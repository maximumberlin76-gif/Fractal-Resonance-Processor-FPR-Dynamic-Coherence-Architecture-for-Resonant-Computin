#!/usr/bin/env python3
import argparse
import json
import math
import random
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "1.7.0"
MILESTONE = "M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package"

STRUCTURED_SCHEMA = "frp.structured_output.v1.7.0"
BENCHMARK_SCHEMA = "frp.m3.benchmark_matrix.v1.7.0"

M14_HIERARCHICAL_ULTRAMETRIC_TOPOLOGY_MODEL_SCHEMA = (
    "frp.m14.hierarchical_ultrametric_topology_model.v1.6.0"
)
M14_FRACTAL_COUPLING_WEIGHT_MAP_SCHEMA = (
    "frp.m14.fractal_coupling_weight_map.v1.6.0"
)
M14_MULTISCALE_PHASE_COHERENCE_MAP_SCHEMA = (
    "frp.m14.multiscale_phase_coherence_map.v1.6.0"
)
M14_CLUSTER_LOCAL_THERMAL_FIELD_SCHEMA = (
    "frp.m14.cluster_local_thermal_field.v1.6.0"
)
M14_CROSS_CLUSTER_PROPAGATION_MAP_SCHEMA = (
    "frp.m14.cross_cluster_propagation_map.v1.6.0"
)
M14_LOCALIZED_HOTSPOT_CONTAINMENT_HARNESS_SCHEMA = (
    "frp.m14.localized_hotspot_containment_harness.v1.6.0"
)
M14_DENSE_HIERARCHICAL_EQUIVALENCE_MAP_SCHEMA = (
    "frp.m14.dense_hierarchical_equivalence_map.v1.6.0"
)
M14_PHYSICAL_DOMAIN_CORRELATION_PACKAGE_SCHEMA = (
    "frp.m14.physical_domain_correlation_package.v1.6.0"
)

SCHEDULER_MODES = ("free", "7/1", "1/7")
TERNARY_STATES = (-1, 0, 1)

DEFAULT_CELLS = 16
DEFAULT_STEPS = 64
DEFAULT_SEED = 76
DEFAULT_TRANSITION_FRACTION = 0.25
DEFAULT_GAMMA = 0.30 * math.pi
DEFAULT_FRACTAL_ALPHA = 0.70
DEFAULT_THERMAL_BETA = 1.20
DEFAULT_AMBIENT_HEAT = 0.05
DEFAULT_THERMAL_TIME_CONSTANT = 14.0
DEFAULT_THERMAL_SOFT_LIMIT = 0.22
DEFAULT_THERMAL_HARD_LIMIT = 0.90
DEFAULT_COUPLING_NOMINAL = 0.28
DEFAULT_DELAY_ALPHA = 0.30
DEFAULT_THERMAL_DIFFUSION_GAIN = 0.035
DEFAULT_EQUIVALENCE_TOLERANCE = 1e-12


def q16(value: float) -> int:
    return int(round(value * 65536.0))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def is_power_of_two(value: int) -> bool:
    return value > 0 and (value & (value - 1)) == 0


def phase_order(phases: Sequence[float]) -> float:
    if not phases:
        return 0.0
    c = sum(math.cos(p) for p in phases) / len(phases)
    s = sum(math.sin(p) for p in phases) / len(phases)
    return math.sqrt(c * c + s * s)


def scheduler_state(mode: str, tick: int) -> str:
    if mode == "7/1":
        return "commit" if (tick + 1) % 8 == 0 else "balance"
    if mode == "1/7":
        return "excite" if tick % 8 == 0 else "neutralize"
    return "free"


def expected_scheduler_counts(mode: str, steps: int) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for tick in range(steps):
        state = scheduler_state(mode, tick)
        counts[state] = counts.get(state, 0) + 1
    return counts


def target_state(phase: float) -> int:
    x = math.sin(phase)
    if x > 0.33:
        return 1
    if x < -0.33:
        return -1
    return 0


def round_list(values: Iterable[float], digits: int = 6) -> List[float]:
    return [round(value, digits) for value in values]


class FractalResonanceProcessor:
    def __init__(
        self,
        cells: int,
        transition_fraction: float,
        gamma_nominal: float,
        scheduler: str,
        seed: int,
        fractal_alpha: float = DEFAULT_FRACTAL_ALPHA,
        thermal_beta: float = DEFAULT_THERMAL_BETA,
        ambient_heat: float = DEFAULT_AMBIENT_HEAT,
        thermal_time_constant: float = DEFAULT_THERMAL_TIME_CONSTANT,
        thermal_soft_limit: float = DEFAULT_THERMAL_SOFT_LIMIT,
        thermal_hard_limit: float = DEFAULT_THERMAL_HARD_LIMIT,
        coupling_nominal: float = DEFAULT_COUPLING_NOMINAL,
        delay_alpha: float = DEFAULT_DELAY_ALPHA,
        thermal_diffusion_gain: float = DEFAULT_THERMAL_DIFFUSION_GAIN,
        equivalence_tolerance: float = DEFAULT_EQUIVALENCE_TOLERANCE,
        coupling_path: str = "hierarchical",
    ) -> None:
        if not is_power_of_two(cells):
            raise ValueError("M14 exact dyadic topology requires cells to be a power of two")
        if cells < 2:
            raise ValueError("M14 requires at least two cells")
        if scheduler not in SCHEDULER_MODES:
            raise ValueError(f"Unsupported scheduler mode: {scheduler}")
        if fractal_alpha <= 0:
            raise ValueError("fractal_alpha must be greater than zero")
        if thermal_beta <= 0:
            raise ValueError("thermal_beta must be greater than zero")
        if coupling_path not in ("dense", "hierarchical"):
            raise ValueError("coupling_path must be 'dense' or 'hierarchical'")

        self.cells = cells
        self.hierarchy_depth = cells.bit_length() - 1
        self.transition_fraction = clamp(transition_fraction, 0.01, 1.0)
        self.gamma_nominal = gamma_nominal
        self.scheduler = scheduler
        self.seed = seed
        self.random = random.Random(seed)
        self.fractal_alpha = fractal_alpha
        self.thermal_beta = thermal_beta
        self.coupling_path = coupling_path
        self.equivalence_tolerance = equivalence_tolerance

        self.states = [self.random.choice(TERNARY_STATES) for _ in range(cells)]
        self.phases = [self.random.random() * math.tau for _ in range(cells)]
        self.base_frequencies = [1.0 for _ in range(cells)]
        self.frequency_targets = [1.0 for _ in range(cells)]
        self.frequencies = [1.0 for _ in range(cells)]

        self.actual_direct_events = 0
        self.requested_direct_events = 0
        self.prevented_direct_events = 0
        self.neutral_routed_events = 0
        self.neutralized_conflicts = 0

        self.transition_requests: List[Tuple[int, int]] = []
        self.pending_neutral_routes: List[Tuple[int, int, int]] = []

        self.scheduler_counts: Dict[str, int] = {}
        self.telemetry: List[Dict[str, Any]] = []

        self.current_switch_changes = 0
        self.cell_switch_activity = [0 for _ in range(cells)]
        self.switch_load = 0.0
        self.switch_load_peak = 0.0

        self.ambient_heat = ambient_heat
        self.heat_cells = [ambient_heat for _ in range(cells)]
        self.local_heat_peaks = [ambient_heat for _ in range(cells)]
        self.heat = ambient_heat
        self.heat_peak = ambient_heat
        self.local_heat_peak = ambient_heat
        self.thermal_time_constant = thermal_time_constant
        self.thermal_soft_limit = thermal_soft_limit
        self.thermal_hard_limit = thermal_hard_limit

        self.base_power_cell = 0.0018
        self.switch_power_gain = 0.052
        self.lag_power_gain = 0.018
        self.thermal_diffusion_gain = thermal_diffusion_gain
        self.generated_power_cells = [0.0 for _ in range(cells)]
        self.thermal_dissipation_cells = [0.0 for _ in range(cells)]
        self.thermal_diffusion_cells = [0.0 for _ in range(cells)]
        self.thermal_overload_cells = [0.0 for _ in range(cells)]

        self.coupling_nominal = coupling_nominal
        self.thermal_coupling_gain = 2.50
        self.thermal_node_factors = [1.0 for _ in range(cells)]
        self.effective_coupling_min = coupling_nominal

        self.delay_alpha = delay_alpha
        self.state_frequency_gain = 0.06
        self.switching_frequency_gain = 0.12

        self.gamma_noise_states = [0.0 for _ in range(cells)]
        self.gamma_noise_targets = [0.0 for _ in range(cells)]
        self.gamma_correlation_alpha = 0.15
        self.gamma_thermal_gain = 0.08
        self.gamma_effective = [gamma_nominal for _ in range(cells)]
        self.gamma_drift = [0.0 for _ in range(cells)]
        self.gamma_drift_peak = 0.0

        self.thermal_compression_gain = 3.0
        self.margin_compression_gain = 1.5
        self.stability_soft_margin = 0.25
        self.previous_C_minus_P = 0.60
        self.first_C_minus_P_crossing: Optional[Dict[str, Any]] = None

        self.raw_phase_coherence = phase_order(self.phases)
        self.coherence_compression = 1.0
        self.effective_coherence = self.raw_phase_coherence
        self.C_value = 1.0
        self.P_value = self.heat
        self.C_minus_P = self.C_value - self.P_value

        self.coupling_matrix = self._generate_hierarchical_matrix(self.fractal_alpha)
        self.thermal_matrix = self._generate_hierarchical_matrix(self.thermal_beta)
        self.coupling_pair_weights_by_level = self._pair_weights_by_level(self.fractal_alpha)
        self.thermal_pair_weights_by_level = self._pair_weights_by_level(self.thermal_beta)

    def hierarchical_distance(self, i: int, j: int) -> int:
        if i == j:
            return 0
        return (i ^ j).bit_length()

    def shell_population(self, distance: int) -> int:
        if distance < 1 or distance > self.hierarchy_depth:
            raise ValueError("distance outside hierarchy depth")
        return 2 ** (distance - 1)

    def _pair_weights_by_level(self, exponent: float) -> Dict[int, float]:
        shell_normalizer = sum(1.0 / (d ** exponent) for d in range(1, self.hierarchy_depth + 1))
        return {
            d: 1.0 / (self.shell_population(d) * (d ** exponent) * shell_normalizer)
            for d in range(1, self.hierarchy_depth + 1)
        }

    def _generate_hierarchical_matrix(self, exponent: float) -> List[List[float]]:
        pair_weights = self._pair_weights_by_level(exponent)
        matrix = [[0.0 for _ in range(self.cells)] for _ in range(self.cells)]
        for i in range(self.cells):
            for j in range(self.cells):
                if i == j:
                    continue
                distance = self.hierarchical_distance(i, j)
                matrix[i][j] = pair_weights[distance]
        return matrix

    def topology_metrics(self, matrix: Sequence[Sequence[float]], exponent: float) -> Dict[str, Any]:
        row_sum_errors = [abs(sum(row) - 1.0) for row in matrix]
        symmetry_error_max = 0.0
        diagonal_error_max = 0.0
        for i in range(self.cells):
            diagonal_error_max = max(diagonal_error_max, abs(matrix[i][i]))
            for j in range(self.cells):
                symmetry_error_max = max(symmetry_error_max, abs(matrix[i][j] - matrix[j][i]))

        pair_weights = self._pair_weights_by_level(exponent)
        shell_profile = []
        for distance in range(1, self.hierarchy_depth + 1):
            shell_profile.append({
                "distance": distance,
                "shell_population": self.shell_population(distance),
                "normalized_pair_weight": pair_weights[distance],
                "aggregate_shell_influence": self.shell_population(distance) * pair_weights[distance],
            })

        shell_influences = [row["aggregate_shell_influence"] for row in shell_profile]
        monotonic = all(
            shell_influences[index] > shell_influences[index + 1]
            for index in range(len(shell_influences) - 1)
        )

        return {
            "hierarchy_depth": self.hierarchy_depth,
            "row_sum_error_max": max(row_sum_errors),
            "symmetry_error_max": symmetry_error_max,
            "diagonal_error_max": diagonal_error_max,
            "shell_influence_profile": shell_profile,
            "shell_influence_monotonic": monotonic,
            "row_sum_match": max(row_sum_errors) <= 1e-12,
            "symmetry_match": symmetry_error_max <= 1e-12,
            "diagonal_zero": diagonal_error_max <= 1e-15,
        }

    def request_transition(self, cell_idx: int, target: int) -> None:
        if target not in TERNARY_STATES:
            raise ValueError("FRP transition target must be one of -1, 0, 1")
        if cell_idx < 0 or cell_idx >= self.cells:
            raise IndexError("FRP transition cell index out of range")
        self.transition_requests.append((cell_idx, target))

    def _apply_state(self, cell_idx: int, next_state: int) -> bool:
        if next_state not in TERNARY_STATES:
            raise ValueError("FRP state must remain in -1, 0, 1")
        current = self.states[cell_idx]
        if current == next_state:
            return False
        if current * next_state == -1:
            self.actual_direct_events += 1
        self.states[cell_idx] = next_state
        self.current_switch_changes += 1
        self.cell_switch_activity[cell_idx] = 1
        return True

    def process_pending_neutral_routes(self, tick_index: int, max_changes: int) -> int:
        changes = 0
        still_pending: List[Tuple[int, int, int]] = []
        for cell_idx, target, ready_tick in self.pending_neutral_routes:
            if tick_index < ready_tick or changes >= max_changes:
                still_pending.append((cell_idx, target, ready_tick))
                continue
            if self.states[cell_idx] == 0:
                if self._apply_state(cell_idx, target):
                    changes += 1
            elif self.states[cell_idx] != target:
                still_pending.append((cell_idx, target, ready_tick))
        self.pending_neutral_routes = still_pending
        return changes

    def process_transition_requests(self, tick_index: int, max_changes: int, changes_used: int) -> int:
        changes = changes_used
        remaining_requests: List[Tuple[int, int]] = []

        for cell_idx, target in self.transition_requests:
            if changes >= max_changes:
                remaining_requests.append((cell_idx, target))
                continue

            current = self.states[cell_idx]
            if current == target:
                continue

            if current * target == -1:
                self.requested_direct_events += 1
                self.prevented_direct_events += 1
                self.neutralized_conflicts += 1
                if self._apply_state(cell_idx, 0):
                    changes += 1
                    self.neutral_routed_events += 1
                    self.pending_neutral_routes.append((cell_idx, target, tick_index + 1))
                continue

            if self._apply_state(cell_idx, target):
                changes += 1

        self.transition_requests = remaining_requests
        return changes

    def update_reference_state_targets(self, tick_index: int, max_changes: int, changes_used: int) -> int:
        changes = changes_used
        for i in range(self.cells):
            if changes >= max_changes:
                break
            desired = target_state(self.phases[i])
            current = self.states[i]
            if current == desired:
                continue
            if current * desired == -1:
                self.prevented_direct_events += 1
                self.neutralized_conflicts += 1
                if self._apply_state(i, 0):
                    changes += 1
                    self.neutral_routed_events += 1
                    self.pending_neutral_routes.append((i, desired, tick_index + 1))
                continue
            if self._apply_state(i, desired):
                changes += 1
        return changes

    def update_delay_dynamics(self) -> Dict[str, Any]:
        lags: List[float] = []
        for i in range(self.cells):
            self.frequency_targets[i] = (
                self.base_frequencies[i]
                + self.state_frequency_gain * abs(self.states[i])
                + self.switching_frequency_gain * self.cell_switch_activity[i]
            )
            self.frequencies[i] += self.delay_alpha * (
                self.frequency_targets[i] - self.frequencies[i]
            )
            lags.append(abs(self.frequency_targets[i] - self.frequencies[i]))

        return {
            "frequency_lags": lags,
            "mean_frequency_lag": sum(lags) / self.cells,
            "frequency_lag_peak_tick": max(lags),
        }

    def update_local_thermal_field(self, frequency_lags: Sequence[float]) -> Dict[str, Any]:
        previous_heat = list(self.heat_cells)

        for i in range(self.cells):
            self.generated_power_cells[i] = (
                self.base_power_cell
                + self.switch_power_gain * self.cell_switch_activity[i]
                + self.lag_power_gain * frequency_lags[i]
            )
            self.thermal_dissipation_cells[i] = (
                previous_heat[i] - self.ambient_heat
            ) / self.thermal_time_constant
            self.thermal_diffusion_cells[i] = self.thermal_diffusion_gain * sum(
                self.thermal_matrix[i][j] * (previous_heat[j] - previous_heat[i])
                for j in range(self.cells)
            )

        for i in range(self.cells):
            self.heat_cells[i] = max(
                self.ambient_heat,
                previous_heat[i]
                + self.generated_power_cells[i]
                - self.thermal_dissipation_cells[i]
                + self.thermal_diffusion_cells[i],
            )
            self.local_heat_peaks[i] = max(self.local_heat_peaks[i], self.heat_cells[i])
            self.thermal_overload_cells[i] = max(
                0.0,
                self.heat_cells[i] - self.thermal_soft_limit,
            )

        self.heat = sum(self.heat_cells) / self.cells
        self.heat_peak = max(self.heat_peak, self.heat)
        self.local_heat_peak = max(self.local_heat_peak, max(self.heat_cells))

        return {
            "heat": self.heat,
            "heat_cells": list(self.heat_cells),
            "local_heat_peak_tick": max(self.heat_cells),
            "generated_power_mean": sum(self.generated_power_cells) / self.cells,
            "generated_power_peak_tick": max(self.generated_power_cells),
            "thermal_dissipation_mean": sum(self.thermal_dissipation_cells) / self.cells,
            "thermal_diffusion_abs_mean": sum(abs(x) for x in self.thermal_diffusion_cells) / self.cells,
            "thermal_overload_mean": sum(self.thermal_overload_cells) / self.cells,
            "thermal_overload_peak_tick": max(self.thermal_overload_cells),
        }

    def update_local_gamma_drift(self, tick_index: int) -> None:
        if tick_index % 8 == 0:
            self.gamma_noise_targets = [self.random.uniform(-1.0, 1.0) for _ in range(self.cells)]

        for i in range(self.cells):
            self.gamma_noise_states[i] += self.gamma_correlation_alpha * (
                self.gamma_noise_targets[i] - self.gamma_noise_states[i]
            )
            self.gamma_effective[i] = (
                self.gamma_nominal
                + self.gamma_thermal_gain
                * self.thermal_overload_cells[i]
                * self.gamma_noise_states[i]
            )
            self.gamma_drift[i] = self.gamma_effective[i] - self.gamma_nominal
            self.gamma_drift_peak = max(self.gamma_drift_peak, abs(self.gamma_drift[i]))

    def update_thermal_node_factors(self) -> None:
        self.thermal_node_factors = [
            math.exp(-0.5 * self.thermal_coupling_gain * overload)
            for overload in self.thermal_overload_cells
        ]
        self.effective_coupling_min = min(
            self.effective_coupling_min,
            self.coupling_nominal
            * min(self.thermal_node_factors)
            * min(self.thermal_node_factors),
        )

    def dense_coupling_field(self) -> List[float]:
        field = [0.0 for _ in range(self.cells)]
        for i in range(self.cells):
            weighted_sum = 0.0
            for j in range(self.cells):
                if i == j:
                    continue
                thermal_pair_factor = self.thermal_node_factors[i] * self.thermal_node_factors[j]
                weighted_sum += (
                    self.coupling_matrix[i][j]
                    * thermal_pair_factor
                    * math.sin(self.phases[j] - self.phases[i] - self.gamma_effective[i])
                )
            field[i] = self.coupling_nominal * weighted_sum
        return field

    def _weighted_phase_prefix(self) -> Tuple[List[float], List[float]]:
        prefix_real = [0.0]
        prefix_imag = [0.0]
        for factor, phase in zip(self.thermal_node_factors, self.phases):
            prefix_real.append(prefix_real[-1] + factor * math.cos(phase))
            prefix_imag.append(prefix_imag[-1] + factor * math.sin(phase))
        return prefix_real, prefix_imag

    @staticmethod
    def _prefix_range(prefix: Sequence[float], start: int, end: int) -> float:
        return prefix[end] - prefix[start]

    def sibling_shell_bounds(self, cell_idx: int, distance: int) -> Tuple[int, int]:
        half_block_size = 2 ** (distance - 1)
        half_index = cell_idx // half_block_size
        sibling_half_index = half_index ^ 1
        start = sibling_half_index * half_block_size
        end = start + half_block_size
        return start, end

    def hierarchical_coupling_field(self) -> List[float]:
        prefix_real, prefix_imag = self._weighted_phase_prefix()
        field = [0.0 for _ in range(self.cells)]

        for i in range(self.cells):
            phase_offset = self.phases[i] + self.gamma_effective[i]
            cos_offset = math.cos(phase_offset)
            sin_offset = math.sin(phase_offset)
            shell_sum = 0.0

            for distance in range(1, self.hierarchy_depth + 1):
                start, end = self.sibling_shell_bounds(i, distance)
                shell_real = self._prefix_range(prefix_real, start, end)
                shell_imag = self._prefix_range(prefix_imag, start, end)
                imaginary_projection = cos_offset * shell_imag - sin_offset * shell_real
                shell_sum += self.coupling_pair_weights_by_level[distance] * imaginary_projection

            field[i] = (
                self.coupling_nominal
                * self.thermal_node_factors[i]
                * shell_sum
            )

        return field

    def scheduler_push(self, scheduler_mode: str) -> float:
        if scheduler_mode == "commit":
            return 0.010
        if scheduler_mode == "excite":
            return 0.006
        return 0.003

    def phase_velocities(self, coupling_field: Sequence[float], scheduler_mode: str) -> List[float]:
        push = self.scheduler_push(scheduler_mode)
        return [
            0.060 * self.frequencies[i] + push + coupling_field[i]
            for i in range(self.cells)
        ]

    def update_phase_field(self, scheduler_mode: str) -> Dict[str, Any]:
        if self.coupling_path == "dense":
            coupling_field = self.dense_coupling_field()
        else:
            coupling_field = self.hierarchical_coupling_field()

        velocities = self.phase_velocities(coupling_field, scheduler_mode)
        self.phases = [
            (self.phases[i] + velocities[i]) % math.tau
            for i in range(self.cells)
        ]
        self.raw_phase_coherence = phase_order(self.phases)

        return {
            "coupling_field": coupling_field,
            "phase_velocities": velocities,
            "raw_phase_coherence": self.raw_phase_coherence,
        }

    def multiscale_phase_coherence(self) -> Dict[str, Any]:
        levels: List[Dict[str, Any]] = []
        for level in range(1, self.hierarchy_depth + 1):
            group_size = 2 ** level
            coherences = [
                phase_order(self.phases[start : start + group_size])
                for start in range(0, self.cells, group_size)
            ]
            mean_value = sum(coherences) / len(coherences)
            variance = sum((value - mean_value) ** 2 for value in coherences) / len(coherences)
            levels.append({
                "level": level,
                "group_size": group_size,
                "group_count": len(coherences),
                "group_phase_coherence": coherences,
                "level_mean_phase_coherence": mean_value,
                "level_min_phase_coherence": min(coherences),
                "level_max_phase_coherence": max(coherences),
                "level_coherence_dispersion": math.sqrt(variance),
            })

        pair_level = levels[0]
        cluster_level = levels[min(1, len(levels) - 1)]
        supercluster_level = levels[max(0, len(levels) - 2)]
        global_level = levels[-1]

        return {
            "levels": levels,
            "pair_domain_coherence_mean": pair_level["level_mean_phase_coherence"],
            "pair_domain_coherence_min": pair_level["level_min_phase_coherence"],
            "cluster_coherence_mean": cluster_level["level_mean_phase_coherence"],
            "cluster_coherence_min": cluster_level["level_min_phase_coherence"],
            "supercluster_coherence_mean": supercluster_level["level_mean_phase_coherence"],
            "supercluster_coherence_min": supercluster_level["level_min_phase_coherence"],
            "global_phase_coherence": global_level["level_mean_phase_coherence"],
            "coherence_dispersion_across_clusters": cluster_level["level_coherence_dispersion"],
        }

    def cluster_metrics(self, cluster_size: int = 4) -> List[Dict[str, Any]]:
        if self.cells % cluster_size != 0:
            raise ValueError("cluster_size must divide cells")
        metrics: List[Dict[str, Any]] = []
        for cluster_index, start in enumerate(range(0, self.cells, cluster_size)):
            end = start + cluster_size
            cluster_heat = self.heat_cells[start:end]
            cluster_states = self.states[start:end]
            cluster_switch_activity = self.cell_switch_activity[start:end]
            cluster_phase_coherence = phase_order(self.phases[start:end])
            cluster_switch_load = sum(cluster_switch_activity) / cluster_size
            cluster_heat_mean = sum(cluster_heat) / cluster_size
            cluster_pressure = cluster_heat_mean + cluster_switch_load
            metrics.append({
                "cluster_index": cluster_index,
                "cell_start": start,
                "cell_end": end - 1,
                "heat_mean": cluster_heat_mean,
                "heat_peak": max(cluster_heat),
                "switch_load": cluster_switch_load,
                "phase_coherence": cluster_phase_coherence,
                "pressure": cluster_pressure,
                "coherence_margin": cluster_phase_coherence - cluster_pressure,
                "state_counts": {
                    "-1": cluster_states.count(-1),
                    "0": cluster_states.count(0),
                    "1": cluster_states.count(1),
                },
            })
        return metrics

    def update_global_stability(self, multiscale: Dict[str, Any]) -> Dict[str, float]:
        thermal_overload_mean = sum(self.thermal_overload_cells) / self.cells
        margin_pressure = max(0.0, self.stability_soft_margin - self.previous_C_minus_P)
        self.coherence_compression = math.exp(
            -(
                self.thermal_compression_gain * thermal_overload_mean * thermal_overload_mean
                + self.margin_compression_gain * margin_pressure * margin_pressure
            )
        )
        self.effective_coherence = self.raw_phase_coherence * self.coherence_compression
        neutral_fraction = self.states.count(0) / self.cells
        mean_frequency_lag = sum(
            abs(self.frequency_targets[i] - self.frequencies[i])
            for i in range(self.cells)
        ) / self.cells

        self.C_value = (
            0.82
            + 0.34 * self.effective_coherence
            + 0.16 * multiscale["cluster_coherence_mean"]
            + 0.08 * neutral_fraction
            - 0.10 * mean_frequency_lag
        )
        self.P_value = self.heat + self.switch_load
        self.C_minus_P = self.C_value - self.P_value
        return {
            "C": self.C_value,
            "P": self.P_value,
            "C_minus_P": self.C_minus_P,
            "coherence_compression": self.coherence_compression,
            "effective_coherence": self.effective_coherence,
        }

    def tick(
        self,
        tick_index: int,
        auto_targets: bool = True,
        pressure_level: Optional[float] = None,
    ) -> None:
        sched = scheduler_state(self.scheduler, tick_index)
        self.scheduler_counts[sched] = self.scheduler_counts.get(sched, 0) + 1

        self.current_switch_changes = 0
        self.cell_switch_activity = [0 for _ in range(self.cells)]

        max_changes = max(1, int(round(self.cells * self.transition_fraction)))
        changes = self.process_pending_neutral_routes(tick_index, max_changes)
        changes = self.process_transition_requests(tick_index, max_changes, changes)
        if auto_targets:
            changes = self.update_reference_state_targets(tick_index, max_changes, changes)

        self.switch_load = self.current_switch_changes / self.cells
        self.switch_load_peak = max(self.switch_load_peak, self.switch_load)

        delay = self.update_delay_dynamics()
        thermal = self.update_local_thermal_field(delay["frequency_lags"])
        self.update_local_gamma_drift(tick_index)
        self.update_thermal_node_factors()
        phase = self.update_phase_field(sched)
        multiscale = self.multiscale_phase_coherence()
        cluster_data = self.cluster_metrics(4 if self.cells >= 4 else 2)
        stability = self.update_global_stability(multiscale)

        previous_margin = self.previous_C_minus_P
        self.previous_C_minus_P = self.C_minus_P

        if (
            self.first_C_minus_P_crossing is None
            and previous_margin > 0.0
            and self.C_minus_P <= 0.0
        ):
            self.first_C_minus_P_crossing = {
                "boundary_tick": tick_index,
                "boundary_pressure_level": pressure_level,
                "heat_at_boundary": self.heat,
                "local_heat_peak_at_boundary": max(self.heat_cells),
                "gamma_drift_peak_at_boundary": max(abs(x) for x in self.gamma_drift),
                "frequency_lag_at_boundary": delay["mean_frequency_lag"],
                "raw_phase_coherence_at_boundary": self.raw_phase_coherence,
                "effective_coherence_at_boundary": self.effective_coherence,
                "coherence_compression_at_boundary": self.coherence_compression,
                "C_minus_P_at_boundary": self.C_minus_P,
            }

        self.telemetry.append({
            "tick": tick_index,
            "scheduler_state": sched,
            "pressure_level": pressure_level,
            "cell_state": list(self.states),
            "phase": round_list(self.phases),
            "frequency_target": round_list(self.frequency_targets),
            "frequency_current": round_list(self.frequencies),
            "mean_frequency_lag": round(delay["mean_frequency_lag"], 6),
            "frequency_lag_peak_tick": round(delay["frequency_lag_peak_tick"], 6),
            "switch_load": round(self.switch_load, 6),
            "generated_power_mean": round(thermal["generated_power_mean"], 6),
            "generated_power_peak_tick": round(thermal["generated_power_peak_tick"], 6),
            "thermal_dissipation_mean": round(thermal["thermal_dissipation_mean"], 6),
            "thermal_diffusion_abs_mean": round(thermal["thermal_diffusion_abs_mean"], 6),
            "heat": round(self.heat, 6),
            "heat_cells": round_list(self.heat_cells),
            "local_heat_peak_tick": round(max(self.heat_cells), 6),
            "thermal_overload_mean": round(thermal["thermal_overload_mean"], 6),
            "thermal_overload_peak_tick": round(thermal["thermal_overload_peak_tick"], 6),
            "gamma_effective_mean": round(sum(self.gamma_effective) / self.cells, 6),
            "gamma_drift_peak_tick": round(max(abs(x) for x in self.gamma_drift), 6),
            "thermal_node_factor_min": round(min(self.thermal_node_factors), 6),
            "coupling_field": round_list(phase["coupling_field"]),
            "raw_phase_coherence": round(self.raw_phase_coherence, 6),
            "coherence_compression": round(self.coherence_compression, 6),
            "effective_coherence": round(self.effective_coherence, 6),
            "pair_domain_coherence_mean": round(multiscale["pair_domain_coherence_mean"], 6),
            "pair_domain_coherence_min": round(multiscale["pair_domain_coherence_min"], 6),
            "cluster_coherence_mean": round(multiscale["cluster_coherence_mean"], 6),
            "cluster_coherence_min": round(multiscale["cluster_coherence_min"], 6),
            "supercluster_coherence_mean": round(multiscale["supercluster_coherence_mean"], 6),
            "supercluster_coherence_min": round(multiscale["supercluster_coherence_min"], 6),
            "global_phase_coherence": round(multiscale["global_phase_coherence"], 6),
            "coherence_dispersion_across_clusters": round(multiscale["coherence_dispersion_across_clusters"], 6),
            "cluster_metrics": [
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                }
                for row in cluster_data
            ],
            "C": round(stability["C"], 6),
            "P": round(stability["P"], 6),
            "C_minus_P": round(stability["C_minus_P"], 6),
            "actual_direct_events": self.actual_direct_events,
            "requested_direct_events": self.requested_direct_events,
            "prevented_direct_events": self.prevented_direct_events,
            "neutral_routed_events": self.neutral_routed_events,
            "neutralized_conflicts": self.neutralized_conflicts,
            "changes": changes,
            "pending_neutral_routes": len(self.pending_neutral_routes),
            "balanced_ternary_state_domain": all(state in TERNARY_STATES for state in self.states),
        })

    def summarize(self, steps: int) -> Dict[str, Any]:
        if not self.telemetry:
            return {
                "version": VERSION,
                "milestone": MILESTONE,
                "cells": self.cells,
                "steps": steps,
                "ticks_recorded": 0,
                "scheduler": self.scheduler,
                "scheduler_counts": dict(self.scheduler_counts),
                "transition_fraction": self.transition_fraction,
                "actual_direct_events": self.actual_direct_events,
                "requested_direct_events": self.requested_direct_events,
                "prevented_direct_events": self.prevented_direct_events,
                "neutral_routed_events": self.neutral_routed_events,
                "neutralized_conflicts": self.neutralized_conflicts,
            }

        c_minus_p_values = [x["C_minus_P"] for x in self.telemetry]
        switch_values = [x["switch_load"] for x in self.telemetry]
        heat_values = [x["heat"] for x in self.telemetry]
        local_heat_values = [x["local_heat_peak_tick"] for x in self.telemetry]
        generated_power_values = [x["generated_power_peak_tick"] for x in self.telemetry]
        thermal_overload_values = [x["thermal_overload_peak_tick"] for x in self.telemetry]
        gamma_values = [x["gamma_drift_peak_tick"] for x in self.telemetry]
        lag_values = [x["mean_frequency_lag"] for x in self.telemetry]
        lag_peak_values = [x["frequency_lag_peak_tick"] for x in self.telemetry]
        raw_coherence_values = [x["raw_phase_coherence"] for x in self.telemetry]
        compression_values = [x["coherence_compression"] for x in self.telemetry]
        effective_coherence_values = [x["effective_coherence"] for x in self.telemetry]
        cluster_mean_values = [x["cluster_coherence_mean"] for x in self.telemetry]
        cluster_min_values = [x["cluster_coherence_min"] for x in self.telemetry]
        pair_mean_values = [x["pair_domain_coherence_mean"] for x in self.telemetry]
        pair_min_values = [x["pair_domain_coherence_min"] for x in self.telemetry]
        supercluster_mean_values = [x["supercluster_coherence_mean"] for x in self.telemetry]
        supercluster_min_values = [x["supercluster_coherence_min"] for x in self.telemetry]
        dispersion_values = [x["coherence_dispersion_across_clusters"] for x in self.telemetry]

        match = 1.0 if self.actual_direct_events == 0 else 0.0
        scheduler_counts_valid = self.scheduler_counts == expected_scheduler_counts(self.scheduler, steps)

        return {
            "version": VERSION,
            "milestone": MILESTONE,
            "cells": self.cells,
            "hierarchy_depth": self.hierarchy_depth,
            "steps": steps,
            "ticks_recorded": len(self.telemetry),
            "scheduler": self.scheduler,
            "scheduler_counts": dict(self.scheduler_counts),
            "scheduler_counts_valid": scheduler_counts_valid,
            "transition_fraction": self.transition_fraction,
            "transition_fraction_q16": q16(self.transition_fraction),
            "gamma_nominal": self.gamma_nominal,
            "gamma_nominal_q16": q16(self.gamma_nominal),
            "fractal_alpha": self.fractal_alpha,
            "thermal_beta": self.thermal_beta,
            "coupling_path": self.coupling_path,
            "actual_direct_events": self.actual_direct_events,
            "requested_direct_events": self.requested_direct_events,
            "prevented_direct_events": self.prevented_direct_events,
            "neutral_routed_events": self.neutral_routed_events,
            "neutralized_conflicts": self.neutralized_conflicts,
            "match": match,
            "match_q16": q16(match),
            "balanced_ternary_state_domain": all(
                state in TERNARY_STATES for record in self.telemetry for state in record["cell_state"]
            ),
            "switch_load_peak": round(max(switch_values), 6),
            "heat_final": round(heat_values[-1], 6),
            "heat_peak": round(max(heat_values), 6),
            "local_heat_peak": round(max(local_heat_values), 6),
            "thermal_overload_peak": round(max(thermal_overload_values), 6),
            "generated_power_peak": round(max(generated_power_values), 6),
            "effective_coupling_min": round(self.effective_coupling_min, 6),
            "gamma_drift_peak": round(max(gamma_values), 6),
            "mean_frequency_lag_final": round(lag_values[-1], 6),
            "mean_frequency_lag_peak": round(max(lag_values), 6),
            "frequency_lag_peak": round(max(lag_peak_values), 6),
            "raw_phase_coherence_final": round(raw_coherence_values[-1], 6),
            "raw_phase_coherence_min": round(min(raw_coherence_values), 6),
            "coherence_compression_final": round(compression_values[-1], 6),
            "coherence_compression_min": round(min(compression_values), 6),
            "effective_coherence_final": round(effective_coherence_values[-1], 6),
            "effective_coherence_min": round(min(effective_coherence_values), 6),
            "pair_domain_coherence_mean_final": round(pair_mean_values[-1], 6),
            "pair_domain_coherence_min": round(min(pair_min_values), 6),
            "cluster_coherence_mean_final": round(cluster_mean_values[-1], 6),
            "cluster_coherence_min": round(min(cluster_min_values), 6),
            "supercluster_coherence_mean_final": round(supercluster_mean_values[-1], 6),
            "supercluster_coherence_min": round(min(supercluster_min_values), 6),
            "coherence_dispersion_across_clusters_peak": round(max(dispersion_values), 6),
            "global_phase_coherence_final": round(self.telemetry[-1]["global_phase_coherence"], 6),
            "C_minus_P_final": round(c_minus_p_values[-1], 6),
            "C_minus_P_min": round(min(c_minus_p_values), 6),
            "boundary_detected": self.first_C_minus_P_crossing is not None,
            "first_C_minus_P_crossing": self.first_C_minus_P_crossing,
            "pending_neutral_routes_final": len(self.pending_neutral_routes),
        }

    def run(self, steps: int, auto_targets: bool = True) -> Dict[str, Any]:
        for tick_index in range(steps):
            self.tick(tick_index, auto_targets=auto_targets)
        return {
            "summary": self.summarize(steps),
            "telemetry": self.telemetry,
        }


def make_processor(
    args: argparse.Namespace,
    cells: Optional[int] = None,
    transition_fraction: Optional[float] = None,
    scheduler: Optional[str] = None,
    seed_offset: int = 0,
    coupling_path: str = "hierarchical",
) -> FractalResonanceProcessor:
    return FractalResonanceProcessor(
        cells=cells if cells is not None else args.cells,
        transition_fraction=(
            transition_fraction if transition_fraction is not None else args.transition_fraction
        ),
        gamma_nominal=args.gamma,
        scheduler=scheduler if scheduler is not None else args.scheduler,
        seed=args.seed + seed_offset,
        fractal_alpha=args.fractal_alpha,
        thermal_beta=args.thermal_beta,
        ambient_heat=args.ambient_heat,
        thermal_time_constant=args.thermal_time_constant,
        thermal_soft_limit=args.thermal_soft_limit,
        thermal_hard_limit=args.thermal_hard_limit,
        coupling_nominal=args.coupling_nominal,
        delay_alpha=args.delay_alpha,
        thermal_diffusion_gain=args.thermal_diffusion_gain,
        equivalence_tolerance=args.equivalence_tolerance,
        coupling_path=coupling_path,
    )


def run_reference(args: argparse.Namespace) -> Dict[str, Any]:
    return make_processor(args).run(args.steps, auto_targets=True)


def inject_hostile_requests(
    processor: FractalResonanceProcessor,
    cell_indices: Sequence[int],
    count: int,
    tick_index: int,
) -> None:
    nonzero_cells = [index for index in cell_indices if processor.states[index] != 0]
    if not nonzero_cells:
        return
    for offset in range(min(count, len(nonzero_cells))):
        cell_idx = nonzero_cells[(tick_index * max(1, count) + offset) % len(nonzero_cells)]
        processor.request_transition(cell_idx, -processor.states[cell_idx])


# -----------------------------------------------------------------------------
# M15 hardware-facing schemas and fixed-point contract
# -----------------------------------------------------------------------------

M15_FIXED_POINT_INTERFACE_PROFILE_SCHEMA = (
    "frp.m15.fixed_point_interface_profile.v1.7.0"
)
M15_BALANCED_TERNARY_HARDWARE_ENCODING_MAP_SCHEMA = (
    "frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0"
)
M15_QUANTIZED_REFERENCE_SHADOW_MODEL_SCHEMA = (
    "frp.m15.quantized_reference_shadow_model.v1.7.0"
)
M15_CYCLE_EXACT_REFERENCE_TRACE_SCHEMA = (
    "frp.m15.cycle_exact_reference_trace.v1.7.0"
)
M15_RTL_COMPARISON_VECTOR_PACKAGE_SCHEMA = (
    "frp.m15.rtl_comparison_vector_package.v1.7.0"
)
M15_SYSTEMVERILOG_TESTBENCH_INTERFACE_MAP_SCHEMA = (
    "frp.m15.systemverilog_testbench_interface_map.v1.7.0"
)
M15_SYNTHESIZABLE_RTL_REFERENCE_CORE_SCHEMA = (
    "frp.m15.synthesizable_rtl_reference_core.v1.7.0"
)
M15_RTL_ASSERTION_CORRELATION_HARNESS_SCHEMA = (
    "frp.m15.rtl_assertion_correlation_harness.v1.7.0"
)
M15_REFERENCE_RTL_EQUIVALENCE_REPORT_SCHEMA = (
    "frp.m15.reference_rtl_equivalence_report.v1.7.0"
)
M15_QUALIFICATION_CLOSURE_MANIFEST_SCHEMA = (
    "frp.m15.qualification_closure_manifest.v1.7.0"
)

Q16_FRAC = 16
Q30_FRAC = 30
Q16_SCALE = 1 << Q16_FRAC
Q30_SCALE = 1 << Q30_FRAC
S32_MIN = -(1 << 31)
S32_MAX = (1 << 31) - 1
PHASE_MOD = 1 << 32
PHASE_MASK = PHASE_MOD - 1
TRIG_LUT_BITS = 12
TRIG_LUT_SIZE = 1 << TRIG_LUT_BITS
TRIG_LUT_SHIFT = 32 - TRIG_LUT_BITS
EXP_LUT_SIZE = 4096
EXP_INPUT_MAX_Q16 = 8 * Q16_SCALE

STATE_TO_CODE = {-1: 0b11, 0: 0b00, 1: 0b01}
CODE_TO_STATE = {0b11: -1, 0b00: 0, 0b01: 1}
RESERVED_STATE_CODE = 0b10

SCHEDULER_MODE_TO_CODE = {"free": 0b00, "7/1": 0b01, "1/7": 0b10}
SCHEDULER_CODE_TO_MODE = {value: key for key, value in SCHEDULER_MODE_TO_CODE.items()}
SCHEDULER_STATE_TO_CODE = {
    "free": 0b000,
    "balance": 0b001,
    "commit": 0b010,
    "excite": 0b011,
    "neutralize": 0b100,
}
SCHEDULER_CODE_TO_STATE = {
    value: key for key, value in SCHEDULER_STATE_TO_CODE.items()
}

M15_ARTIFACT_LAYERS = [
    "fixed_point_interface_profile",
    "balanced_ternary_hardware_encoding_map",
    "quantized_reference_shadow_model",
    "cycle_exact_reference_trace",
    "rtl_comparison_vector_package",
    "systemverilog_testbench_interface_map",
    "synthesizable_rtl_reference_core",
    "rtl_assertion_correlation_harness",
    "reference_rtl_equivalence_report",
    "qualification_closure_manifest",
]

M15_EXPORT_SCHEMAS = [
    M15_FIXED_POINT_INTERFACE_PROFILE_SCHEMA,
    M15_BALANCED_TERNARY_HARDWARE_ENCODING_MAP_SCHEMA,
    M15_QUANTIZED_REFERENCE_SHADOW_MODEL_SCHEMA,
    M15_CYCLE_EXACT_REFERENCE_TRACE_SCHEMA,
    M15_RTL_COMPARISON_VECTOR_PACKAGE_SCHEMA,
    M15_SYSTEMVERILOG_TESTBENCH_INTERFACE_MAP_SCHEMA,
    M15_SYNTHESIZABLE_RTL_REFERENCE_CORE_SCHEMA,
    M15_RTL_ASSERTION_CORRELATION_HARNESS_SCHEMA,
    M15_REFERENCE_RTL_EQUIVALENCE_REPORT_SCHEMA,
    M15_QUALIFICATION_CLOSURE_MANIFEST_SCHEMA,
]


def round_half_away_from_zero(value: float) -> int:
    if value >= 0.0:
        return math.floor(value + 0.5)
    return math.ceil(value - 0.5)


def round_div_away_from_zero(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if numerator >= 0:
        return (numerator + denominator // 2) // denominator
    return -((-numerator + denominator // 2) // denominator)


def round_shift_away_from_zero(value: int, shift: int) -> int:
    if shift < 0:
        return value << (-shift)
    if shift == 0:
        return value
    return round_div_away_from_zero(value, 1 << shift)


def sat_s32(value: int) -> int:
    return max(S32_MIN, min(S32_MAX, int(value)))


def quantize_q16(value: float) -> int:
    return sat_s32(round_half_away_from_zero(value * Q16_SCALE))


def quantize_q30(value: float) -> int:
    return sat_s32(round_half_away_from_zero(value * Q30_SCALE))


def dequantize_q16(value: int) -> float:
    return value / Q16_SCALE


def dequantize_q30(value: int) -> float:
    return value / Q30_SCALE


def mul_q16(a: int, b: int) -> int:
    return sat_s32(round_shift_away_from_zero(a * b, Q16_FRAC))


def mul_q30(a: int, b: int) -> int:
    return sat_s32(round_shift_away_from_zero(a * b, Q30_FRAC))


def mul_q16_q30(a_q16: int, b_q30: int) -> int:
    return sat_s32(round_shift_away_from_zero(a_q16 * b_q30, Q30_FRAC))


def q30_to_q16(value_q30: int) -> int:
    return sat_s32(round_shift_away_from_zero(value_q30, Q30_FRAC - Q16_FRAC))


def q16_to_q30(value_q16: int) -> int:
    return sat_s32(value_q16 << (Q30_FRAC - Q16_FRAC))


PHASE_PER_RAD_Q16 = round_half_away_from_zero((PHASE_MOD / math.tau) * Q16_SCALE)


def phase_from_radians(value: float) -> int:
    normalized = (value % math.tau) / math.tau
    return round_half_away_from_zero(normalized * PHASE_MOD) & PHASE_MASK


def signed_phase_from_radians(value: float) -> int:
    raw = round_half_away_from_zero((value / math.tau) * PHASE_MOD)
    raw &= PHASE_MASK
    if raw >= (1 << 31):
        raw -= PHASE_MOD
    return raw


def signed_phase_delta(a: int, b: int) -> int:
    delta = (a - b) & PHASE_MASK
    if delta >= (1 << 31):
        delta -= PHASE_MOD
    return delta


def state_to_code(state: int) -> int:
    if state not in STATE_TO_CODE:
        raise ValueError("FRP state must be -1, 0, or 1")
    return STATE_TO_CODE[state]


def code_to_state(code: int) -> int:
    if code == RESERVED_STATE_CODE:
        raise ValueError("reserved balanced ternary state code 2'b10")
    if code not in CODE_TO_STATE:
        raise ValueError(f"invalid balanced ternary hardware code: {code}")
    return CODE_TO_STATE[code]


def pack_states(states: Sequence[int]) -> int:
    packed = 0
    for index, state in enumerate(states):
        packed |= state_to_code(state) << (2 * index)
    return packed


def unpack_states(packed: int, cells: int) -> List[int]:
    states: List[int] = []
    for index in range(cells):
        code = (packed >> (2 * index)) & 0b11
        states.append(code_to_state(code))
    return states


def packed_state_hex(states: Sequence[int]) -> str:
    width_nibbles = max(1, (2 * len(states) + 3) // 4)
    return f"{pack_states(states):0{width_nibbles}X}"


def ternary_human_string(states: Sequence[int]) -> str:
    mapping = {-1: "M", 0: "N", 1: "P"}
    return "".join(mapping[state] for state in states)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def request_lanes_for_profile(cells: int, transition_fraction: float) -> int:
    return max(1, int(round(cells * transition_fraction)))


def cell_id_width(cells: int) -> int:
    return max(1, (cells - 1).bit_length())


def hierarchy_depth_for_cells(cells: int) -> int:
    if not is_power_of_two(cells) or cells < 2:
        raise ValueError("M15 exact dyadic topology requires cells to be a power of two")
    return cells.bit_length() - 1


def hierarchical_distance(i: int, j: int) -> int:
    if i == j:
        return 0
    return (i ^ j).bit_length()


def shell_population(distance: int) -> int:
    if distance < 1:
        raise ValueError("distance must be positive")
    return 1 << (distance - 1)


def quantized_level_weights(cells: int, exponent: float) -> Dict[int, int]:
    depth = hierarchy_depth_for_cells(cells)
    normalizer = sum(1.0 / (distance ** exponent) for distance in range(1, depth + 1))
    weights: Dict[int, int] = {}
    for distance in range(1, depth + 1):
        pair_weight = 1.0 / (
            shell_population(distance) * (distance ** exponent) * normalizer
        )
        weights[distance] = quantize_q30(pair_weight)

    aggregate = sum(shell_population(d) * weights[d] for d in weights)
    residual = Q30_SCALE - aggregate
    weights[1] += residual
    exact = sum(shell_population(d) * weights[d] for d in weights)
    if exact != Q30_SCALE:
        raise AssertionError("fixed-point topology residual closure failed")
    return weights


def level_weight_profile(cells: int, exponent: float) -> List[Dict[str, Any]]:
    weights = quantized_level_weights(cells, exponent)
    return [
        {
            "distance": distance,
            "shell_population": shell_population(distance),
            "pair_weight_q30": weights[distance],
            "pair_weight_real": dequantize_q30(weights[distance]),
            "aggregate_weight_q30": shell_population(distance) * weights[distance],
        }
        for distance in range(1, hierarchy_depth_for_cells(cells) + 1)
    ]


TRIG_SIN_Q30 = tuple(
    quantize_q30(math.sin(math.tau * index / TRIG_LUT_SIZE))
    for index in range(TRIG_LUT_SIZE)
)


def sin_phase_q30(phase_word: int) -> int:
    return TRIG_SIN_Q30[(phase_word & PHASE_MASK) >> TRIG_LUT_SHIFT]


def cos_phase_q30(phase_word: int) -> int:
    index = ((phase_word & PHASE_MASK) >> TRIG_LUT_SHIFT) + TRIG_LUT_SIZE // 4
    return TRIG_SIN_Q30[index % TRIG_LUT_SIZE]


EXP_NEG_Q30 = tuple(
    quantize_q30(
        math.exp(-((index * EXP_INPUT_MAX_Q16) / (EXP_LUT_SIZE - 1)) / Q16_SCALE)
    )
    for index in range(EXP_LUT_SIZE)
)


def exp_neg_q30(x_q16: int) -> int:
    clipped = max(0, min(EXP_INPUT_MAX_Q16, x_q16))
    index = round_div_away_from_zero(clipped * (EXP_LUT_SIZE - 1), EXP_INPUT_MAX_Q16)
    return EXP_NEG_Q30[index]


def phase_order_q30(phase_words: Sequence[int]) -> int:
    if not phase_words:
        return 0
    sum_cos = sum(cos_phase_q30(phase) for phase in phase_words)
    sum_sin = sum(sin_phase_q30(phase) for phase in phase_words)
    mean_cos = round_div_away_from_zero(sum_cos, len(phase_words))
    mean_sin = round_div_away_from_zero(sum_sin, len(phase_words))
    magnitude_sq_q60 = mean_cos * mean_cos + mean_sin * mean_sin
    magnitude_q30 = math.isqrt(max(0, magnitude_sq_q60))
    return min(Q30_SCALE, magnitude_q30)


def phase_error_radians(phase_a: int, phase_b: int) -> float:
    delta = abs(signed_phase_delta(phase_a, phase_b))
    return (delta / PHASE_MOD) * math.tau


def inherited_v1_6_0_boundary() -> Dict[str, Any]:
    return {
        "release": "FRP v1.6.0",
        "layer": "M14 — Physical Implementation Correlation and Production Qualification Package",
        "main_executable_reference_file": "frp_prototype_v1_6_0.py",
        "validation_index": "FRP_VALIDATION_INDEX_v1_6_0.md",
        "release_notes": "RELEASE_NOTES_v1_6_0.md",
        "test_report": "TEST_REPORT_v1_6_0.md",
        "validated_commit": "09141fc",
        "release_status": "PUBLISHED",
        "preserved_kernel": {
            "balanced_ternary_states": [-1, 0, 1],
            "active_neutral_state": 0,
            "tick_separated_neutral_routing": True,
            "scheduler_modes": list(SCHEDULER_MODES),
            "stability_relation": "C(t) > P(t)",
            "pressure_relation": "P(t) = heat + switch_load",
        },
        "m14_artifact_layers": [
            "hierarchical_ultrametric_topology_model",
            "fractal_coupling_weight_map",
            "multiscale_phase_coherence_map",
            "cluster_local_thermal_field",
            "cross_cluster_propagation_map",
            "localized_hotspot_containment_harness",
            "dense_hierarchical_equivalence_map",
            "physical_domain_correlation_package",
        ],
    }


class QuantizedReferenceShadowProcessor:
    def __init__(
        self,
        cells: int = DEFAULT_CELLS,
        transition_fraction: float = DEFAULT_TRANSITION_FRACTION,
        gamma_nominal: float = DEFAULT_GAMMA,
        scheduler: str = "7/1",
        seed: int = DEFAULT_SEED,
        fractal_alpha: float = DEFAULT_FRACTAL_ALPHA,
        thermal_beta: float = DEFAULT_THERMAL_BETA,
        ambient_heat: float = DEFAULT_AMBIENT_HEAT,
        thermal_time_constant: float = DEFAULT_THERMAL_TIME_CONSTANT,
        thermal_soft_limit: float = DEFAULT_THERMAL_SOFT_LIMIT,
        thermal_hard_limit: float = DEFAULT_THERMAL_HARD_LIMIT,
        coupling_nominal: float = DEFAULT_COUPLING_NOMINAL,
        delay_alpha: float = DEFAULT_DELAY_ALPHA,
        thermal_diffusion_gain: float = DEFAULT_THERMAL_DIFFUSION_GAIN,
    ) -> None:
        if not is_power_of_two(cells) or cells < 2:
            raise ValueError("M15 exact dyadic topology requires cells to be a power of two")
        if scheduler not in SCHEDULER_MODES:
            raise ValueError(f"unsupported scheduler mode: {scheduler}")

        self.cells = cells
        self.hierarchy_depth = hierarchy_depth_for_cells(cells)
        self.transition_fraction = clamp(transition_fraction, 0.01, 1.0)
        self.request_lanes = request_lanes_for_profile(cells, self.transition_fraction)
        self.scheduler = scheduler
        self.seed = seed
        self.random = random.Random(seed)
        self.fractal_alpha = fractal_alpha
        self.thermal_beta = thermal_beta

        self.states = [self.random.choice(TERNARY_STATES) for _ in range(cells)]
        initial_phases = [self.random.random() * math.tau for _ in range(cells)]
        self.phase_words = [phase_from_radians(value) for value in initial_phases]

        self.base_frequency_q16 = [quantize_q16(1.0) for _ in range(cells)]
        self.frequency_target_q16 = list(self.base_frequency_q16)
        self.frequency_current_q16 = list(self.base_frequency_q16)
        self.frequency_lag_q16 = [0 for _ in range(cells)]

        self.ambient_heat_q16 = quantize_q16(ambient_heat)
        self.heat_q16 = [self.ambient_heat_q16 for _ in range(cells)]
        self.local_heat_peak_q16 = list(self.heat_q16)
        self.generated_power_q16 = [0 for _ in range(cells)]
        self.thermal_dissipation_q16 = [0 for _ in range(cells)]
        self.thermal_diffusion_q16 = [0 for _ in range(cells)]
        self.thermal_overload_q16 = [0 for _ in range(cells)]

        self.thermal_time_constant_q16 = quantize_q16(thermal_time_constant)
        self.thermal_soft_limit_q16 = quantize_q16(thermal_soft_limit)
        self.thermal_hard_limit_q16 = quantize_q16(thermal_hard_limit)
        self.base_power_cell_q16 = quantize_q16(0.0018)
        self.switch_power_gain_q16 = quantize_q16(0.052)
        self.lag_power_gain_q16 = quantize_q16(0.018)
        self.thermal_diffusion_gain_q16 = quantize_q16(thermal_diffusion_gain)

        self.coupling_nominal_q16 = quantize_q16(coupling_nominal)
        self.thermal_coupling_gain_q16 = quantize_q16(2.50)
        self.delay_alpha_q16 = quantize_q16(delay_alpha)
        self.state_frequency_gain_q16 = quantize_q16(0.06)
        self.switching_frequency_gain_q16 = quantize_q16(0.12)

        self.gamma_nominal_word = signed_phase_from_radians(gamma_nominal)
        self.gamma_noise_state_q16 = [0 for _ in range(cells)]
        self.gamma_noise_target_q16 = [0 for _ in range(cells)]
        self.gamma_correlation_alpha_q16 = quantize_q16(0.15)
        self.gamma_thermal_gain_q16 = quantize_q16(0.08)
        self.gamma_effective_word = [self.gamma_nominal_word for _ in range(cells)]
        self.gamma_drift_word = [0 for _ in range(cells)]

        self.thermal_node_factor_q30 = [Q30_SCALE for _ in range(cells)]
        self.coupling_field_q16 = [0 for _ in range(cells)]
        self.phase_velocity_word = [0 for _ in range(cells)]

        self.thermal_compression_gain_q16 = quantize_q16(3.0)
        self.margin_compression_gain_q16 = quantize_q16(1.5)
        self.stability_soft_margin_q16 = quantize_q16(0.25)
        self.previous_C_minus_P_q16 = quantize_q16(0.60)

        self.raw_phase_coherence_q30 = phase_order_q30(self.phase_words)
        self.coherence_compression_q30 = Q30_SCALE
        self.effective_coherence_q30 = self.raw_phase_coherence_q30
        self.C_q16 = quantize_q16(1.0)
        self.P_q16 = self.ambient_heat_q16
        self.C_minus_P_q16 = self.C_q16 - self.P_q16
        self.first_boundary_crossing: Optional[Dict[str, Any]] = None

        self.phase_pair_weights_q30 = quantized_level_weights(cells, fractal_alpha)
        self.thermal_pair_weights_q30 = quantized_level_weights(cells, thermal_beta)

        self.transition_requests: List[Tuple[int, int]] = []
        self.pending_neutral_routes: List[Tuple[int, int, int]] = []
        self.neutral_route_queue_capacity = cells
        self.route_events: List[Dict[str, Any]] = []
        self.actual_direct_events = 0
        self.requested_direct_events = 0
        self.prevented_direct_events = 0
        self.neutral_routed_events = 0
        self.neutralized_conflicts = 0
        self.reserved_state_events = 0
        self.queue_overflow_events = 0

        self.scheduler_counts: Dict[str, int] = {}
        self.cell_switch_activity = [0 for _ in range(cells)]
        self.current_switch_changes = 0
        self.switch_load_q16 = 0
        self.switch_load_peak_q16 = 0
        self.tick_count = 0
        self.trace: List[Dict[str, Any]] = []
        self.cell_trace: List[Dict[str, Any]] = []

    def snapshot_preload(self) -> Dict[str, Any]:
        return {
            "cells": self.cells,
            "scheduler": self.scheduler,
            "seed": self.seed,
            "states": list(self.states),
            "states_packed_hex": packed_state_hex(self.states),
            "phase_words": list(self.phase_words),
            "frequency_target_q16": list(self.frequency_target_q16),
            "frequency_current_q16": list(self.frequency_current_q16),
            "heat_q16": list(self.heat_q16),
            "gamma_noise_state_q16": list(self.gamma_noise_state_q16),
            "gamma_noise_target_q16": list(self.gamma_noise_target_q16),
        }

    def request_transition(self, cell_idx: int, target: int) -> None:
        if target not in TERNARY_STATES:
            raise ValueError("FRP transition target must be one of -1, 0, 1")
        if cell_idx < 0 or cell_idx >= self.cells:
            raise IndexError("FRP transition cell index out of range")
        self.transition_requests.append((cell_idx, target))

    def _apply_state(self, cell_idx: int, next_state: int) -> bool:
        if next_state not in TERNARY_STATES:
            self.reserved_state_events += 1
            raise ValueError("FRP state must remain in -1, 0, 1")
        current = self.states[cell_idx]
        if current == next_state:
            return False
        if current * next_state == -1:
            self.actual_direct_events += 1
        self.states[cell_idx] = next_state
        self.current_switch_changes += 1
        self.cell_switch_activity[cell_idx] = 1
        return True

    def _enqueue_neutral_route(
        self,
        cell_idx: int,
        target: int,
        ready_tick: int,
        tick_index: int,
    ) -> bool:
        if len(self.pending_neutral_routes) >= self.neutral_route_queue_capacity:
            self.queue_overflow_events += 1
            return False
        self.pending_neutral_routes.append((cell_idx, target, ready_tick))
        self.route_events.append(
            {
                "tick": tick_index,
                "cell_id": cell_idx,
                "target_state": target,
                "ready_tick": ready_tick,
                "route_status": "pending",
            }
        )
        return True

    def process_pending_neutral_routes(self, tick_index: int, max_changes: int) -> int:
        changes = 0
        still_pending: List[Tuple[int, int, int]] = []
        for cell_idx, target, ready_tick in self.pending_neutral_routes:
            if tick_index < ready_tick or changes >= max_changes:
                still_pending.append((cell_idx, target, ready_tick))
                continue
            if self.states[cell_idx] == 0:
                if self._apply_state(cell_idx, target):
                    changes += 1
                    self.route_events.append(
                        {
                            "tick": tick_index,
                            "cell_id": cell_idx,
                            "target_state": target,
                            "ready_tick": ready_tick,
                            "route_status": "applied",
                        }
                    )
            elif self.states[cell_idx] != target:
                still_pending.append((cell_idx, target, ready_tick))
        self.pending_neutral_routes = still_pending
        return changes

    def process_transition_requests(
        self, tick_index: int, max_changes: int, changes_used: int
    ) -> int:
        changes = changes_used
        remaining: List[Tuple[int, int]] = []
        for cell_idx, target in self.transition_requests:
            if changes >= max_changes:
                remaining.append((cell_idx, target))
                continue
            current = self.states[cell_idx]
            if current == target:
                continue
            if current * target == -1:
                self.requested_direct_events += 1
                self.prevented_direct_events += 1
                self.neutralized_conflicts += 1
                if self._apply_state(cell_idx, 0):
                    changes += 1
                    self.neutral_routed_events += 1
                    ready_tick = tick_index + 1
                    self._enqueue_neutral_route(
                        cell_idx, target, ready_tick, tick_index
                    )
                continue
            if self._apply_state(cell_idx, target):
                changes += 1
        self.transition_requests = remaining
        return changes

    def target_state_from_phase(self, phase_word: int) -> int:
        sine_q30 = sin_phase_q30(phase_word)
        threshold_q30 = quantize_q30(0.33)
        if sine_q30 > threshold_q30:
            return 1
        if sine_q30 < -threshold_q30:
            return -1
        return 0

    def update_reference_state_targets(
        self, tick_index: int, max_changes: int, changes_used: int
    ) -> int:
        changes = changes_used
        for cell_idx in range(self.cells):
            if changes >= max_changes:
                break
            desired = self.target_state_from_phase(self.phase_words[cell_idx])
            current = self.states[cell_idx]
            if current == desired:
                continue
            if current * desired == -1:
                self.prevented_direct_events += 1
                self.neutralized_conflicts += 1
                if self._apply_state(cell_idx, 0):
                    changes += 1
                    self.neutral_routed_events += 1
                    ready_tick = tick_index + 1
                    self._enqueue_neutral_route(
                        cell_idx, desired, ready_tick, tick_index
                    )
                continue
            if self._apply_state(cell_idx, desired):
                changes += 1
        return changes

    def update_delay_dynamics(self) -> None:
        for cell_idx in range(self.cells):
            target = self.base_frequency_q16[cell_idx]
            target += self.state_frequency_gain_q16 * abs(self.states[cell_idx])
            target += self.switching_frequency_gain_q16 * self.cell_switch_activity[cell_idx]
            self.frequency_target_q16[cell_idx] = sat_s32(target)
            delta = self.frequency_target_q16[cell_idx] - self.frequency_current_q16[cell_idx]
            self.frequency_current_q16[cell_idx] = sat_s32(
                self.frequency_current_q16[cell_idx]
                + mul_q16(self.delay_alpha_q16, delta)
            )
            self.frequency_lag_q16[cell_idx] = abs(
                self.frequency_target_q16[cell_idx] - self.frequency_current_q16[cell_idx]
            )

    def thermal_weighted_sum_q16(self, cell_idx: int) -> int:
        total = 0
        current_heat = self.heat_q16[cell_idx]
        for other in range(self.cells):
            if other == cell_idx:
                continue
            distance = hierarchical_distance(cell_idx, other)
            weight_q30 = self.thermal_pair_weights_q30[distance]
            total += mul_q16_q30(self.heat_q16[other] - current_heat, weight_q30)
        return sat_s32(total)

    def update_local_thermal_field(self) -> None:
        previous_heat = list(self.heat_q16)
        weighted_differences = [self.thermal_weighted_sum_q16(i) for i in range(self.cells)]

        for cell_idx in range(self.cells):
            power = self.base_power_cell_q16
            power += self.switch_power_gain_q16 * self.cell_switch_activity[cell_idx]
            power += mul_q16(self.lag_power_gain_q16, self.frequency_lag_q16[cell_idx])
            self.generated_power_q16[cell_idx] = sat_s32(power)

            numerator = previous_heat[cell_idx] - self.ambient_heat_q16
            self.thermal_dissipation_q16[cell_idx] = round_div_away_from_zero(
                numerator * Q16_SCALE,
                self.thermal_time_constant_q16,
            )
            self.thermal_diffusion_q16[cell_idx] = mul_q16(
                self.thermal_diffusion_gain_q16,
                weighted_differences[cell_idx],
            )

        for cell_idx in range(self.cells):
            next_heat = (
                previous_heat[cell_idx]
                + self.generated_power_q16[cell_idx]
                - self.thermal_dissipation_q16[cell_idx]
                + self.thermal_diffusion_q16[cell_idx]
            )
            self.heat_q16[cell_idx] = max(self.ambient_heat_q16, sat_s32(next_heat))
            self.local_heat_peak_q16[cell_idx] = max(
                self.local_heat_peak_q16[cell_idx], self.heat_q16[cell_idx]
            )
            self.thermal_overload_q16[cell_idx] = max(
                0, self.heat_q16[cell_idx] - self.thermal_soft_limit_q16
            )

    def generate_gamma_noise_targets(self, tick_index: int) -> Tuple[bool, List[int]]:
        if tick_index % 8 != 0:
            return False, list(self.gamma_noise_target_q16)
        targets = [quantize_q16(self.random.uniform(-1.0, 1.0)) for _ in range(self.cells)]
        return True, targets

    def update_local_gamma_drift(
        self,
        gamma_update_valid: bool,
        gamma_targets_q16: Optional[Sequence[int]],
    ) -> None:
        if gamma_update_valid:
            if gamma_targets_q16 is None or len(gamma_targets_q16) != self.cells:
                raise ValueError("gamma target vector length mismatch")
            self.gamma_noise_target_q16 = [sat_s32(value) for value in gamma_targets_q16]

        for cell_idx in range(self.cells):
            delta = self.gamma_noise_target_q16[cell_idx] - self.gamma_noise_state_q16[cell_idx]
            self.gamma_noise_state_q16[cell_idx] = sat_s32(
                self.gamma_noise_state_q16[cell_idx]
                + mul_q16(self.gamma_correlation_alpha_q16, delta)
            )
            drift_rad_q16 = mul_q16(
                mul_q16(self.gamma_thermal_gain_q16, self.thermal_overload_q16[cell_idx]),
                self.gamma_noise_state_q16[cell_idx],
            )
            drift_word = round_shift_away_from_zero(
                drift_rad_q16 * PHASE_PER_RAD_Q16, 32
            )
            drift_word &= PHASE_MASK
            if drift_word >= (1 << 31):
                drift_word -= PHASE_MOD
            self.gamma_drift_word[cell_idx] = drift_word
            effective = (self.gamma_nominal_word + drift_word) & PHASE_MASK
            if effective >= (1 << 31):
                effective -= PHASE_MOD
            self.gamma_effective_word[cell_idx] = effective

    def update_thermal_node_factors(self) -> None:
        half_gain_q16 = round_shift_away_from_zero(self.thermal_coupling_gain_q16, 1)
        for cell_idx in range(self.cells):
            exponent_arg_q16 = mul_q16(
                half_gain_q16,
                self.thermal_overload_q16[cell_idx],
            )
            self.thermal_node_factor_q30[cell_idx] = exp_neg_q30(exponent_arg_q16)

    def hierarchical_coupling_field(self) -> None:
        for cell_idx in range(self.cells):
            phase_plus_gamma = (
                self.phase_words[cell_idx] + self.gamma_effective_word[cell_idx]
            ) & PHASE_MASK
            total_q16 = 0
            own_factor_q30 = self.thermal_node_factor_q30[cell_idx]

            for other in range(self.cells):
                if other == cell_idx:
                    continue
                distance = hierarchical_distance(cell_idx, other)
                pair_weight_q30 = self.phase_pair_weights_q30[distance]
                pair_factor_q30 = mul_q30(
                    own_factor_q30,
                    self.thermal_node_factor_q30[other],
                )
                weighted_pair_q30 = mul_q30(pair_weight_q30, pair_factor_q30)
                phase_delta = (
                    self.phase_words[other] - phase_plus_gamma
                ) & PHASE_MASK
                sine_q30 = sin_phase_q30(phase_delta)
                pair_term_q30 = mul_q30(weighted_pair_q30, sine_q30)
                pair_term_q16 = q30_to_q16(pair_term_q30)
                total_q16 = sat_s32(total_q16 + pair_term_q16)

            self.coupling_field_q16[cell_idx] = mul_q16(
                self.coupling_nominal_q16,
                total_q16,
            )

    def scheduler_push_q16(self, scheduler_mode: str) -> int:
        if scheduler_mode == "commit":
            return quantize_q16(0.010)
        if scheduler_mode == "excite":
            return quantize_q16(0.006)
        return quantize_q16(0.003)

    def update_phase_field(self, scheduler_mode: str) -> None:
        self.hierarchical_coupling_field()
        push_q16 = self.scheduler_push_q16(scheduler_mode)
        for cell_idx in range(self.cells):
            velocity_turns_q16 = (
                mul_q16(quantize_q16(0.060), self.frequency_current_q16[cell_idx])
                + push_q16
                + self.coupling_field_q16[cell_idx]
            )
            velocity_word = round_shift_away_from_zero(
                velocity_turns_q16 * PHASE_PER_RAD_Q16, 32
            )
            self.phase_velocity_word[cell_idx] = velocity_word
            self.phase_words[cell_idx] = (
                self.phase_words[cell_idx] + velocity_word
            ) & PHASE_MASK
        self.raw_phase_coherence_q30 = phase_order_q30(self.phase_words)

    def multiscale_phase_coherence(self) -> Dict[str, Any]:
        levels: List[Dict[str, Any]] = []
        for level in range(1, self.hierarchy_depth + 1):
            group_size = 1 << level
            values = [
                phase_order_q30(self.phase_words[start : start + group_size])
                for start in range(0, self.cells, group_size)
            ]
            mean_value = round_div_away_from_zero(sum(values), len(values))
            dispersion_sq = sum((value - mean_value) ** 2 for value in values) // len(values)
            levels.append(
                {
                    "level": level,
                    "group_size": group_size,
                    "group_count": len(values),
                    "group_phase_coherence_q30": values,
                    "level_mean_phase_coherence_q30": mean_value,
                    "level_min_phase_coherence_q30": min(values),
                    "level_max_phase_coherence_q30": max(values),
                    "level_coherence_dispersion_q30": math.isqrt(max(0, dispersion_sq)),
                }
            )

        pair_level = levels[0]
        cluster_level = levels[min(1, len(levels) - 1)]
        supercluster_level = levels[max(0, len(levels) - 2)]
        global_level = levels[-1]
        return {
            "levels": levels,
            "pair_domain_coherence_mean_q30": pair_level[
                "level_mean_phase_coherence_q30"
            ],
            "pair_domain_coherence_min_q30": pair_level[
                "level_min_phase_coherence_q30"
            ],
            "cluster_coherence_mean_q30": cluster_level[
                "level_mean_phase_coherence_q30"
            ],
            "cluster_coherence_min_q30": cluster_level[
                "level_min_phase_coherence_q30"
            ],
            "supercluster_coherence_mean_q30": supercluster_level[
                "level_mean_phase_coherence_q30"
            ],
            "supercluster_coherence_min_q30": supercluster_level[
                "level_min_phase_coherence_q30"
            ],
            "global_phase_coherence_q30": global_level[
                "level_mean_phase_coherence_q30"
            ],
            "coherence_dispersion_across_clusters_q30": cluster_level[
                "level_coherence_dispersion_q30"
            ],
        }

    def update_global_stability(self, multiscale: Dict[str, Any]) -> None:
        thermal_overload_mean_q16 = round_div_away_from_zero(
            sum(self.thermal_overload_q16), self.cells
        )
        margin_pressure_q16 = max(
            0,
            self.stability_soft_margin_q16 - self.previous_C_minus_P_q16,
        )
        thermal_sq_q16 = mul_q16(thermal_overload_mean_q16, thermal_overload_mean_q16)
        margin_sq_q16 = mul_q16(margin_pressure_q16, margin_pressure_q16)
        compression_arg_q16 = sat_s32(
            mul_q16(self.thermal_compression_gain_q16, thermal_sq_q16)
            + mul_q16(self.margin_compression_gain_q16, margin_sq_q16)
        )
        self.coherence_compression_q30 = exp_neg_q30(compression_arg_q16)
        self.effective_coherence_q30 = mul_q30(
            self.raw_phase_coherence_q30,
            self.coherence_compression_q30,
        )

        neutral_fraction_q30 = round_div_away_from_zero(
            self.states.count(0) * Q30_SCALE,
            self.cells,
        )
        mean_lag_q16 = round_div_away_from_zero(
            sum(self.frequency_lag_q16), self.cells
        )

        C_q16 = quantize_q16(0.82)
        C_q16 += mul_q16_q30(quantize_q16(0.34), self.effective_coherence_q30)
        C_q16 += mul_q16_q30(
            quantize_q16(0.16), multiscale["cluster_coherence_mean_q30"]
        )
        C_q16 += mul_q16_q30(quantize_q16(0.08), neutral_fraction_q30)
        C_q16 -= mul_q16(quantize_q16(0.10), mean_lag_q16)
        self.C_q16 = sat_s32(C_q16)

        heat_global_q16 = round_div_away_from_zero(sum(self.heat_q16), self.cells)
        self.P_q16 = sat_s32(heat_global_q16 + self.switch_load_q16)
        self.C_minus_P_q16 = sat_s32(self.C_q16 - self.P_q16)

    def pending_route_rows(self, tick_index: int) -> List[Dict[str, Any]]:
        return [
            {
                "tick": tick_index,
                "route_index": route_index,
                "cell_id": cell_idx,
                "target_state_code": state_to_code(target),
                "ready_tick": ready_tick,
                "route_status": "pending",
            }
            for route_index, (cell_idx, target, ready_tick) in enumerate(
                self.pending_neutral_routes
            )
        ]

    def tick(
        self,
        tick_index: int,
        requests: Optional[Sequence[Tuple[bool, int, int]]] = None,
        auto_targets_enable: bool = True,
        gamma_update_valid: Optional[bool] = None,
        gamma_targets_q16: Optional[Sequence[int]] = None,
    ) -> Dict[str, Any]:
        sched_state = scheduler_state(self.scheduler, tick_index)
        self.scheduler_counts[sched_state] = self.scheduler_counts.get(sched_state, 0) + 1

        self.current_switch_changes = 0
        self.cell_switch_activity = [0 for _ in range(self.cells)]
        max_changes = self.request_lanes

        changes = self.process_pending_neutral_routes(tick_index, max_changes)

        normalized_requests: List[Tuple[bool, int, int]] = []
        incoming = list(requests or [])
        for lane in range(self.request_lanes):
            if lane < len(incoming):
                valid, cell_idx, target = incoming[lane]
            else:
                valid, cell_idx, target = False, 0, 0
            if valid:
                self.request_transition(cell_idx, target)
            normalized_requests.append((bool(valid), int(cell_idx), int(target)))

        changes = self.process_transition_requests(tick_index, max_changes, changes)
        if auto_targets_enable:
            changes = self.update_reference_state_targets(tick_index, max_changes, changes)

        self.switch_load_q16 = round_div_away_from_zero(
            self.current_switch_changes * Q16_SCALE,
            self.cells,
        )
        self.switch_load_peak_q16 = max(self.switch_load_peak_q16, self.switch_load_q16)

        self.update_delay_dynamics()
        self.update_local_thermal_field()

        if gamma_update_valid is None:
            gamma_update_valid, generated_targets = self.generate_gamma_noise_targets(tick_index)
            gamma_targets_q16 = generated_targets
        self.update_local_gamma_drift(bool(gamma_update_valid), gamma_targets_q16)
        self.update_thermal_node_factors()
        self.update_phase_field(sched_state)
        multiscale = self.multiscale_phase_coherence()
        previous_margin = self.previous_C_minus_P_q16
        self.update_global_stability(multiscale)
        self.previous_C_minus_P_q16 = self.C_minus_P_q16

        if (
            self.first_boundary_crossing is None
            and previous_margin > 0
            and self.C_minus_P_q16 <= 0
        ):
            self.first_boundary_crossing = {
                "boundary_tick": tick_index,
                "C_minus_P_q16": self.C_minus_P_q16,
                "heat_global_q16": round_div_away_from_zero(sum(self.heat_q16), self.cells),
            }

        request_valid_mask = 0
        request_cell_ids: List[int] = []
        request_target_codes: List[int] = []
        for lane, (valid, cell_idx, target) in enumerate(normalized_requests):
            if valid:
                request_valid_mask |= 1 << lane
            request_cell_ids.append(cell_idx)
            request_target_codes.append(state_to_code(target))

        heat_global_q16 = round_div_away_from_zero(sum(self.heat_q16), self.cells)
        record = {
            "tick": tick_index,
            "reset_n": 1,
            "scheduler_mode": SCHEDULER_MODE_TO_CODE[self.scheduler],
            "scheduler_state": SCHEDULER_STATE_TO_CODE[sched_state],
            "scheduler_state_name": sched_state,
            "auto_targets_enable": 1 if auto_targets_enable else 0,
            "request_valid_mask": request_valid_mask,
            "request_cell_ids": request_cell_ids,
            "request_target_states": request_target_codes,
            "gamma_noise_update_valid": 1 if gamma_update_valid else 0,
            "gamma_noise_target_q16": list(self.gamma_noise_target_q16),
            "states_packed": pack_states(self.states),
            "states_packed_hex": packed_state_hex(self.states),
            "states_human": ternary_human_string(self.states),
            "pending_route_count": len(self.pending_neutral_routes),
            "switch_load_q16": self.switch_load_q16,
            "heat_global_q16": heat_global_q16,
            "global_phase_coherence_q30": multiscale["global_phase_coherence_q30"],
            "C_q16": self.C_q16,
            "P_q16": self.P_q16,
            "C_minus_P_q16": self.C_minus_P_q16,
            "requested_direct_events": self.requested_direct_events,
            "prevented_direct_events": self.prevented_direct_events,
            "neutral_routed_events": self.neutral_routed_events,
            "neutralized_conflicts": self.neutralized_conflicts,
            "actual_direct_events": self.actual_direct_events,
            "reserved_state_events": self.reserved_state_events,
            "queue_overflow_events": self.queue_overflow_events,
            "changes": changes,
        }
        self.trace.append(record)

        for cell_idx in range(self.cells):
            self.cell_trace.append(
                {
                    "tick": tick_index,
                    "cell_id": cell_idx,
                    "state_code": state_to_code(self.states[cell_idx]),
                    "phase_word": self.phase_words[cell_idx],
                    "frequency_target_q16": self.frequency_target_q16[cell_idx],
                    "frequency_current_q16": self.frequency_current_q16[cell_idx],
                    "frequency_lag_q16": self.frequency_lag_q16[cell_idx],
                    "generated_power_q16": self.generated_power_q16[cell_idx],
                    "heat_q16": self.heat_q16[cell_idx],
                    "thermal_overload_q16": self.thermal_overload_q16[cell_idx],
                    "gamma_noise_state_q16": self.gamma_noise_state_q16[cell_idx],
                    "gamma_effective_word": self.gamma_effective_word[cell_idx],
                    "thermal_node_factor_q30": self.thermal_node_factor_q30[cell_idx],
                    "coupling_field_q16": self.coupling_field_q16[cell_idx],
                }
            )

        self.tick_count += 1
        return record

    def run(
        self,
        steps: int,
        auto_targets_enable: bool = True,
        request_plan: Optional[Dict[int, Sequence[Tuple[bool, int, int]]]] = None,
    ) -> Dict[str, Any]:
        for tick_index in range(steps):
            requests = None if request_plan is None else request_plan.get(tick_index, [])
            self.tick(
                tick_index,
                requests=requests,
                auto_targets_enable=auto_targets_enable,
            )
        return {"summary": self.summarize(steps), "trace": self.trace, "cell_trace": self.cell_trace}

    def summarize(self, steps: int) -> Dict[str, Any]:
        c_minus_p_values = [row["C_minus_P_q16"] for row in self.trace] or [self.C_minus_P_q16]
        return {
            "version": VERSION,
            "milestone": MILESTONE,
            "cells": self.cells,
            "hierarchy_depth": self.hierarchy_depth,
            "request_lanes": self.request_lanes,
            "steps": steps,
            "ticks_recorded": len(self.trace),
            "scheduler": self.scheduler,
            "scheduler_counts": dict(self.scheduler_counts),
            "scheduler_counts_valid": self.scheduler_counts
            == expected_scheduler_counts(self.scheduler, steps),
            "transition_fraction": self.transition_fraction,
            "balanced_ternary_state_domain": all(state in TERNARY_STATES for state in self.states),
            "reserved_state_events": self.reserved_state_events,
            "actual_direct_events": self.actual_direct_events,
            "requested_direct_events": self.requested_direct_events,
            "prevented_direct_events": self.prevented_direct_events,
            "neutral_routed_events": self.neutral_routed_events,
            "neutralized_conflicts": self.neutralized_conflicts,
            "pending_route_count_final": len(self.pending_neutral_routes),
            "neutral_route_queue_capacity": self.neutral_route_queue_capacity,
            "queue_overflow_events": self.queue_overflow_events,
            "switch_load_peak_q16": self.switch_load_peak_q16,
            "switch_load_peak": dequantize_q16(self.switch_load_peak_q16),
            "C_minus_P_final_q16": self.C_minus_P_q16,
            "C_minus_P_final": dequantize_q16(self.C_minus_P_q16),
            "C_minus_P_min_q16": min(c_minus_p_values),
            "C_minus_P_min": dequantize_q16(min(c_minus_p_values)),
            "boundary_detected": self.first_boundary_crossing is not None,
            "fixed_point_topology_sum_exact": sum(
                shell_population(d) * self.phase_pair_weights_q30[d]
                for d in self.phase_pair_weights_q30
            )
            == Q30_SCALE,
            "fixed_point_thermal_sum_exact": sum(
                shell_population(d) * self.thermal_pair_weights_q30[d]
                for d in self.thermal_pair_weights_q30
            )
            == Q30_SCALE,
        }


def make_shadow_processor(
    args: argparse.Namespace,
    cells: Optional[int] = None,
    scheduler: Optional[str] = None,
    seed_offset: int = 0,
) -> QuantizedReferenceShadowProcessor:
    return QuantizedReferenceShadowProcessor(
        cells=cells if cells is not None else args.cells,
        transition_fraction=args.transition_fraction,
        gamma_nominal=args.gamma,
        scheduler=scheduler if scheduler is not None else args.scheduler,
        seed=args.seed + seed_offset,
        fractal_alpha=args.fractal_alpha,
        thermal_beta=args.thermal_beta,
        ambient_heat=args.ambient_heat,
        thermal_time_constant=args.thermal_time_constant,
        thermal_soft_limit=args.thermal_soft_limit,
        thermal_hard_limit=args.thermal_hard_limit,
        coupling_nominal=args.coupling_nominal,
        delay_alpha=args.delay_alpha,
        thermal_diffusion_gain=args.thermal_diffusion_gain,
    )


def fixed_point_interface_profile(args: argparse.Namespace) -> Dict[str, Any]:
    coupling_profile = level_weight_profile(args.cells, args.fractal_alpha)
    thermal_profile = level_weight_profile(args.cells, args.thermal_beta)
    return {
        "schema": M15_FIXED_POINT_INTERFACE_PROFILE_SCHEMA,
        "kind": "fixed_point_interface_profile",
        "version": VERSION,
        "milestone": MILESTONE,
        "inherited_boundary": inherited_v1_6_0_boundary(),
        "profile": {
            "general_scalar": {
                "name": "S32Q16",
                "width": 32,
                "fraction_bits": 16,
                "signed": True,
                "scale": Q16_SCALE,
            },
            "normalized_coefficient": {
                "name": "S32Q30",
                "width": 32,
                "fraction_bits": 30,
                "signed": True,
                "scale": Q30_SCALE,
            },
            "phase": {
                "name": "PHASE_U32",
                "width": 32,
                "signed": False,
                "modulus": PHASE_MOD,
                "full_cycle_relation": "2^32 phase units = 2 pi",
            },
            "gamma": {
                "name": "GAMMA_S32",
                "width": 32,
                "signed": True,
                "phase_scale": "PHASE_U32 scale",
                "nominal_gamma_word": signed_phase_from_radians(args.gamma),
            },
            "rounding": "round-to-nearest, half cases away from zero",
            "saturation": "signed destination saturation",
            "phase_overflow": "modulo 2^32 wrap",
            "multiply_rules": {
                "mul_q30": "round_shift(a * b, 30)",
                "mul_q16": "round_shift(a * b, 16)",
                "mul_q16_q30": "round_shift(a * b, 30)",
            },
            "trigonometric_profile": {
                "table_entries": TRIG_LUT_SIZE,
                "address_bits": TRIG_LUT_BITS,
                "index_relation": "phase_word >> 20",
                "output_type": "S32Q30",
                "sin_lut_sha256": sha256_bytes(
                    b"".join(int(value).to_bytes(4, "little", signed=True) for value in TRIG_SIN_Q30)
                ),
            },
            "exponential_profile": {
                "table_entries": EXP_LUT_SIZE,
                "input_domain_q16": [0, EXP_INPUT_MAX_Q16],
                "output_type": "S32Q30",
                "exp_lut_sha256": sha256_bytes(
                    b"".join(int(value).to_bytes(4, "little", signed=True) for value in EXP_NEG_Q30)
                ),
            },
        },
        "topology_fixed_point_profile": coupling_profile,
        "thermal_fixed_point_profile": thermal_profile,
        "fixed_point_topology_sum_exact": sum(
            row["aggregate_weight_q30"] for row in coupling_profile
        )
        == Q30_SCALE,
        "fixed_point_thermal_sum_exact": sum(
            row["aggregate_weight_q30"] for row in thermal_profile
        )
        == Q30_SCALE,
    }


def balanced_ternary_hardware_encoding_map(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "schema": M15_BALANCED_TERNARY_HARDWARE_ENCODING_MAP_SCHEMA,
        "kind": "balanced_ternary_hardware_encoding_map",
        "version": VERSION,
        "milestone": MILESTONE,
        "inherited_boundary": inherited_v1_6_0_boundary(),
        "state_encoding": [
            {"state": -1, "code": "11", "integer_code": 3},
            {"state": 0, "code": "00", "integer_code": 0},
            {"state": 1, "code": "01", "integer_code": 1},
        ],
        "reserved_state_code": {"code": "10", "integer_code": RESERVED_STATE_CODE},
        "packed_state_vector": {
            "bits_per_cell": 2,
            "cell_zero_bits": "[1:0]",
            "cell_i_bits": "[2i+1:2i]",
            "configured_cells": args.cells,
            "configured_width_bits": 2 * args.cells,
        },
        "scheduler_mode_encoding": [
            {"name": name, "code": code} for name, code in SCHEDULER_MODE_TO_CODE.items()
        ],
        "scheduler_state_encoding": [
            {"name": name, "code": code} for name, code in SCHEDULER_STATE_TO_CODE.items()
        ],
        "request_interface": {
            "request_lanes": request_lanes_for_profile(args.cells, args.transition_fraction),
            "cell_id_width": cell_id_width(args.cells),
            "request_valid_bits_per_lane": 1,
            "request_target_state_bits_per_lane": 2,
            "lane_order": "ascending lane index",
        },
    }


def deterministic_request_plan(
    cells: int,
    transition_fraction: float,
    steps: int,
    seed: int,
    density: int = 4,
) -> Dict[int, List[Tuple[bool, int, int]]]:
    rng = random.Random(seed + 15000)
    lanes = request_lanes_for_profile(cells, transition_fraction)
    plan: Dict[int, List[Tuple[bool, int, int]]] = {}
    for tick in range(steps):
        rows: List[Tuple[bool, int, int]] = []
        if tick % density == 0:
            active_count = min(lanes, 1 + ((tick // density) % max(1, lanes)))
            chosen = list(range(cells))
            rng.shuffle(chosen)
            for lane in range(active_count):
                cell_idx = chosen[lane]
                target = rng.choice(TERNARY_STATES)
                rows.append((True, cell_idx, target))
        plan[tick] = rows
    return plan


def kernel_request_plan(
    initial_states: Sequence[int],
    cells: int,
    transition_fraction: float,
    steps: int,
) -> Dict[int, List[Tuple[bool, int, int]]]:
    lanes = request_lanes_for_profile(cells, transition_fraction)
    plan: Dict[int, List[Tuple[bool, int, int]]] = {tick: [] for tick in range(steps)}
    nonzero = [index for index, state in enumerate(initial_states) if state != 0]
    if len(nonzero) < 2:
        nonzero = list(range(min(2, cells)))
    first = nonzero[0]
    second = nonzero[1] if len(nonzero) > 1 else (first + 1) % cells
    first_target = -initial_states[first] if initial_states[first] != 0 else 1
    second_target = -initial_states[second] if initial_states[second] != 0 else -1
    plan[0] = [(True, first, first_target)]
    if lanes > 1:
        plan[3] = [(True, second, second_target), (True, (second + 1) % cells, 0)]
    else:
        plan[3] = [(True, second, second_target)]
    if steps > 8:
        plan[8] = [
            (True, index % cells, 1 if index % 2 == 0 else -1)
            for index in range(min(lanes, cells))
        ]
    return plan


def execute_shadow_trace(
    args: argparse.Namespace,
    scheduler: Optional[str] = None,
    cells: Optional[int] = None,
    steps: Optional[int] = None,
    auto_targets_enable: bool = True,
    request_plan: Optional[Dict[int, Sequence[Tuple[bool, int, int]]]] = None,
) -> Dict[str, Any]:
    processor = make_shadow_processor(args, cells=cells, scheduler=scheduler)
    preload = processor.snapshot_preload()
    run_steps = args.steps if steps is None else steps
    result = processor.run(
        run_steps,
        auto_targets_enable=auto_targets_enable,
        request_plan=request_plan,
    )
    result["preload"] = preload
    result["route_events"] = processor.route_events
    result["processor"] = processor
    return result


def quantized_reference_shadow_model(args: argparse.Namespace) -> Dict[str, Any]:
    result = execute_shadow_trace(args)
    processor: QuantizedReferenceShadowProcessor = result["processor"]
    return {
        "schema": M15_QUANTIZED_REFERENCE_SHADOW_MODEL_SCHEMA,
        "kind": "quantized_reference_shadow_model",
        "version": VERSION,
        "milestone": MILESTONE,
        "inherited_boundary": inherited_v1_6_0_boundary(),
        "execution_model": "stateful fixed-point feedback",
        "numeric_profile": {
            "scalar": "S32Q16",
            "unit": "S32Q30",
            "phase": "PHASE_U32",
            "gamma": "GAMMA_S32",
        },
        "configuration": {
            "cells": processor.cells,
            "hierarchy_depth": processor.hierarchy_depth,
            "request_lanes": processor.request_lanes,
            "scheduler": processor.scheduler,
            "seed": processor.seed,
            "steps": args.steps,
        },
        "preload": result["preload"],
        "summary": result["summary"],
        "trace_digest": sha256_bytes(canonical_json_bytes(result["trace"])),
        "cell_trace_digest": sha256_bytes(canonical_json_bytes(result["cell_trace"])),
    }


PRIMARY_VECTOR_COLUMNS = [
    "TICK",
    "RESET_N",
    "SCHED_MODE",
    "SCHED_STATE",
    "AUTO_TARGETS_ENABLE",
    "REQ_VALID_MASK",
    "REQ_CELL_IDS",
    "REQ_TARGET_STATES",
    "GAMMA_UPDATE_VALID",
    "GAMMA_NOISE_TARGETS_Q",
    "STATES_PACKED",
    "PENDING_ROUTE_COUNT",
    "SWITCH_LOAD_Q",
    "HEAT_GLOBAL_Q",
    "COHERENCE_GLOBAL_Q",
    "C_Q",
    "P_Q",
    "C_MINUS_P_Q",
    "REQUESTED_DIRECT_EVENTS",
    "PREVENTED_DIRECT_EVENTS",
    "NEUTRAL_ROUTED_EVENTS",
    "NEUTRALIZED_CONFLICTS",
    "ACTUAL_DIRECT_EVENTS",
]

CELL_TRACE_COLUMNS = [
    "TICK",
    "CELL_ID",
    "STATE_CODE",
    "PHASE_WORD",
    "FREQUENCY_TARGET_Q",
    "FREQUENCY_CURRENT_Q",
    "FREQUENCY_LAG_Q",
    "GENERATED_POWER_Q",
    "HEAT_Q",
    "THERMAL_OVERLOAD_Q",
    "GAMMA_NOISE_STATE_Q",
    "GAMMA_EFFECTIVE_WORD",
    "THERMAL_NODE_FACTOR_Q",
    "COUPLING_FIELD_Q",
]

ROUTE_TRACE_COLUMNS = [
    "TICK",
    "ROUTE_INDEX",
    "CELL_ID",
    "TARGET_STATE_CODE",
    "READY_TICK",
    "ROUTE_STATUS",
]


def vector_header(
    args: argparse.Namespace,
    trace_kind: str,
    cells: int,
    scheduler: str,
    steps: int,
    columns: Sequence[str],
) -> List[str]:
    depth = hierarchy_depth_for_cells(cells)
    lanes = request_lanes_for_profile(cells, args.transition_fraction)
    metadata = {
        "format_version": "frp.m15.vector.v1",
        "frp_version": VERSION,
        "milestone": MILESTONE,
        "trace_kind": trace_kind,
        "cells": cells,
        "hierarchy_depth": depth,
        "request_lanes": lanes,
        "transition_fraction": args.transition_fraction,
        "scheduler_mode": scheduler,
        "fractal_alpha": args.fractal_alpha,
        "thermal_beta": args.thermal_beta,
        "scalar_format": "S32Q16",
        "unit_format": "S32Q30",
        "phase_format": "PHASE_U32",
        "seed": args.seed,
        "trace_steps": steps,
        "column_definition": list(columns),
    }
    return [f"# {key}={json.dumps(value, ensure_ascii=False, separators=(',', ':'))}" for key, value in metadata.items()]


def primary_vector_text(
    args: argparse.Namespace,
    trace_kind: str,
    result: Dict[str, Any],
    scheduler: str,
) -> str:
    processor: QuantizedReferenceShadowProcessor = result["processor"]
    lines = vector_header(
        args,
        trace_kind,
        processor.cells,
        scheduler,
        len(result["trace"]),
        PRIMARY_VECTOR_COLUMNS,
    )
    lines.append("# " + " | ".join(PRIMARY_VECTOR_COLUMNS))
    width_nibbles = max(1, (2 * processor.cells + 3) // 4)
    lane_hex_width = max(1, (processor.request_lanes + 3) // 4)
    cell_hex_width = max(1, (cell_id_width(processor.cells) + 3) // 4)
    for row in result["trace"]:
        req_cell_ids = ",".join(f"{value:0{cell_hex_width}X}" for value in row["request_cell_ids"])
        req_targets = ",".join(f"{value:X}" for value in row["request_target_states"])
        fields = [
            f"{row['tick']:08d}",
            str(row["reset_n"]),
            f"{row['scheduler_mode']:X}",
            f"{row['scheduler_state']:X}",
            str(row["auto_targets_enable"]),
            f"{row['request_valid_mask']:0{lane_hex_width}X}",
            req_cell_ids,
            req_targets,
            str(row["gamma_noise_update_valid"]),
            ",".join(str(value) for value in row["gamma_noise_target_q16"]),
            f"{row['states_packed']:0{width_nibbles}X}",
            str(row["pending_route_count"]),
            str(row["switch_load_q16"]),
            str(row["heat_global_q16"]),
            str(row["global_phase_coherence_q30"]),
            str(row["C_q16"]),
            str(row["P_q16"]),
            str(row["C_minus_P_q16"]),
            str(row["requested_direct_events"]),
            str(row["prevented_direct_events"]),
            str(row["neutral_routed_events"]),
            str(row["neutralized_conflicts"]),
            str(row["actual_direct_events"]),
        ]
        lines.append(" | ".join(fields))
    return "\n".join(lines) + "\n"


def cell_trace_text(args: argparse.Namespace, result: Dict[str, Any], scheduler: str) -> str:
    processor: QuantizedReferenceShadowProcessor = result["processor"]
    lines = vector_header(
        args,
        "cell_trace",
        processor.cells,
        scheduler,
        len(result["trace"]),
        CELL_TRACE_COLUMNS,
    )
    lines.append("# " + " | ".join(CELL_TRACE_COLUMNS))
    for row in result["cell_trace"]:
        fields = [
            f"{row['tick']:08d}",
            str(row["cell_id"]),
            f"{row['state_code']:X}",
            f"{row['phase_word'] & PHASE_MASK:08X}",
            str(row["frequency_target_q16"]),
            str(row["frequency_current_q16"]),
            str(row["frequency_lag_q16"]),
            str(row["generated_power_q16"]),
            str(row["heat_q16"]),
            str(row["thermal_overload_q16"]),
            str(row["gamma_noise_state_q16"]),
            str(row["gamma_effective_word"]),
            str(row["thermal_node_factor_q30"]),
            str(row["coupling_field_q16"]),
        ]
        lines.append(" | ".join(fields))
    return "\n".join(lines) + "\n"


def route_trace_text(args: argparse.Namespace, result: Dict[str, Any], scheduler: str) -> str:
    processor: QuantizedReferenceShadowProcessor = result["processor"]
    lines = vector_header(
        args,
        "pending_routes",
        processor.cells,
        scheduler,
        len(result["trace"]),
        ROUTE_TRACE_COLUMNS,
    )
    lines.append("# " + " | ".join(ROUTE_TRACE_COLUMNS))
    events = sorted(
        result["route_events"],
        key=lambda row: (row["tick"], row["cell_id"], row["ready_tick"], row["route_status"]),
    )
    for index, row in enumerate(events):
        fields = [
            f"{row['tick']:08d}",
            str(index),
            str(row["cell_id"]),
            f"{state_to_code(row['target_state']):X}",
            str(row["ready_tick"]),
            row["route_status"],
        ]
        lines.append(" | ".join(fields))
    return "\n".join(lines) + "\n"


def preload_manifest_text(result: Dict[str, Any]) -> str:
    return json.dumps(result["preload"], indent=2, sort_keys=True) + "\n"


def trig_lut_text() -> str:
    lines = [
        "# FRP v1.7.0 M15 deterministic trigonometric lookup table",
        f"# entries={TRIG_LUT_SIZE}",
        "# format=index | sin_q30",
    ]
    lines.extend(f"{index:04X} | {value}" for index, value in enumerate(TRIG_SIN_Q30))
    return "\n".join(lines) + "\n"


def build_vector_package_contents(args: argparse.Namespace) -> Dict[str, bytes]:
    kernel_processor = make_shadow_processor(args, scheduler="free")
    kernel_plan = kernel_request_plan(
        kernel_processor.states,
        kernel_processor.cells,
        kernel_processor.transition_fraction,
        max(16, args.steps // 2),
    )
    kernel_result = execute_shadow_trace(
        args,
        scheduler="free",
        steps=max(16, args.steps // 2),
        auto_targets_enable=False,
        request_plan=kernel_plan,
    )

    scheduler_results: Dict[str, Dict[str, Any]] = {}
    for mode in SCHEDULER_MODES:
        processor = make_shadow_processor(args, scheduler=mode)
        plan = deterministic_request_plan(
            processor.cells,
            processor.transition_fraction,
            16,
            args.seed + SCHEDULER_MODE_TO_CODE[mode],
            density=4,
        )
        scheduler_results[mode] = execute_shadow_trace(
            args,
            scheduler=mode,
            steps=16,
            auto_targets_enable=False,
            request_plan=plan,
        )

    full_plan = deterministic_request_plan(
        args.cells,
        args.transition_fraction,
        args.steps,
        args.seed,
        density=5,
    )
    full_result = execute_shadow_trace(
        args,
        scheduler=args.scheduler,
        steps=args.steps,
        auto_targets_enable=True,
        request_plan=full_plan,
    )

    contents: Dict[str, bytes] = {
        "frp_m15_kernel_vectors.vec": primary_vector_text(
            args, "kernel_transition_vectors", kernel_result, "free"
        ).encode("utf-8"),
        "frp_m15_pending_routes.trace": route_trace_text(
            args, kernel_result, "free"
        ).encode("utf-8"),
        "frp_m15_scheduler_free_vectors.vec": primary_vector_text(
            args, "scheduler_free_vectors", scheduler_results["free"], "free"
        ).encode("utf-8"),
        "frp_m15_scheduler_7_1_vectors.vec": primary_vector_text(
            args, "scheduler_7_1_vectors", scheduler_results["7/1"], "7/1"
        ).encode("utf-8"),
        "frp_m15_scheduler_1_7_vectors.vec": primary_vector_text(
            args, "scheduler_1_7_vectors", scheduler_results["1/7"], "1/7"
        ).encode("utf-8"),
        "frp_m15_full_correlation_vectors.vec": primary_vector_text(
            args, "full_correlation_vectors", full_result, args.scheduler
        ).encode("utf-8"),
        "frp_m15_cell_trace.vec": cell_trace_text(
            args, full_result, args.scheduler
        ).encode("utf-8"),
        "frp_m15_reference_preload.json": preload_manifest_text(full_result).encode("utf-8"),
        "frp_m15_trig_lut_q30.vec": trig_lut_text().encode("utf-8"),
    }
    digest_manifest = {
        name: sha256_bytes(data) for name, data in sorted(contents.items())
    }
    contents["frp_m15_sha256_manifest.json"] = (
        json.dumps(digest_manifest, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return contents


def vector_package_manifest(contents: Dict[str, bytes]) -> Dict[str, Any]:
    return {
        "file_count": len(contents),
        "files": [
            {
                "name": name,
                "size_bytes": len(data),
                "sha256": sha256_bytes(data),
            }
            for name, data in sorted(contents.items())
        ],
    }


def write_vector_package(output_dir: Path, contents: Dict[str, bytes]) -> List[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    for name, data in sorted(contents.items()):
        path = output_dir / name
        path.write_bytes(data)
        written.append(str(path))
    return written


def cycle_exact_reference_trace(args: argparse.Namespace) -> Dict[str, Any]:
    request_plan = deterministic_request_plan(
        args.cells,
        args.transition_fraction,
        args.steps,
        args.seed,
        density=5,
    )
    result = execute_shadow_trace(
        args,
        auto_targets_enable=True,
        request_plan=request_plan,
    )
    return {
        "schema": M15_CYCLE_EXACT_REFERENCE_TRACE_SCHEMA,
        "kind": "cycle_exact_reference_trace",
        "version": VERSION,
        "milestone": MILESTONE,
        "configuration": {
            "cells": args.cells,
            "steps": args.steps,
            "scheduler": args.scheduler,
            "request_lanes": request_lanes_for_profile(
                args.cells, args.transition_fraction
            ),
        },
        "preload": result["preload"],
        "summary": result["summary"],
        "trace": result["trace"],
        "route_events": result["route_events"],
    }


def rtl_comparison_vector_package(args: argparse.Namespace) -> Dict[str, Any]:
    contents = build_vector_package_contents(args)
    payload = {
        "schema": M15_RTL_COMPARISON_VECTOR_PACKAGE_SCHEMA,
        "kind": "rtl_comparison_vector_package",
        "version": VERSION,
        "milestone": MILESTONE,
        "vector_classes": [
            "kernel_transition_vectors",
            "scheduler_vectors",
            "full_correlation_vectors",
        ],
        "manifest": vector_package_manifest(contents),
        "deterministic_package_digest": sha256_bytes(
            b"".join(name.encode("utf-8") + b"\0" + contents[name] for name in sorted(contents))
        ),
    }
    if args.vector_output_dir:
        payload["written_files"] = write_vector_package(Path(args.vector_output_dir), contents)
    return payload


def systemverilog_testbench_interface_map(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "schema": M15_SYSTEMVERILOG_TESTBENCH_INTERFACE_MAP_SCHEMA,
        "kind": "systemverilog_testbench_interface_map",
        "version": VERSION,
        "milestone": MILESTONE,
        "parameters": {
            "NUM_CELLS": args.cells,
            "HIERARCHY_DEPTH": hierarchy_depth_for_cells(args.cells),
            "REQUEST_LANES": request_lanes_for_profile(
                args.cells, args.transition_fraction
            ),
            "CELL_ID_WIDTH": cell_id_width(args.cells),
            "STATE_VECTOR_WIDTH": 2 * args.cells,
            "SCALAR_WIDTH": 32,
            "PHASE_WIDTH": 32,
        },
        "execution_inputs": [
            "clk",
            "reset_n",
            "scheduler_mode",
            "auto_targets_enable",
            "request_valid",
            "request_cell_id",
            "request_target_state",
        ],
        "verification_stimulus_inputs": [
            "preload_valid",
            "gamma_noise_update_valid",
            "gamma_noise_target_q",
        ],
        "comparison_outputs": [
            "states_packed",
            "scheduler_state",
            "pending_route_count",
            "switch_load_q",
            "heat_global_q",
            "global_phase_coherence_q",
            "C_q",
            "P_q",
            "C_minus_P_q",
            "requested_direct_events",
            "prevented_direct_events",
            "neutral_routed_events",
            "neutralized_conflicts",
            "actual_direct_events",
        ],
        "vector_replay_order": [
            "parse vector row",
            "drive input signals before active clock edge",
            "apply verification sideband stimulus",
            "execute one processor clock edge",
            "allow registered outputs to settle",
            "sample post-tick outputs",
            "compare sampled outputs against expected integer values",
            "execute invariant assertions",
            "stop immediately on mismatch",
        ],
    }


def synthesizable_rtl_reference_core(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "schema": M15_SYNTHESIZABLE_RTL_REFERENCE_CORE_SCHEMA,
        "kind": "synthesizable_rtl_reference_core",
        "version": VERSION,
        "milestone": MILESTONE,
        "exact_tick_execution_order": [
            "resolve scheduler state",
            "clear current-tick switch-change counters",
            "clear current-tick per-cell switch activity",
            "process ready pending neutral routes",
            "process external request lanes in ascending order",
            "process phase-derived targets when enabled",
            "calculate switch load",
            "update frequency targets",
            "update lagged frequencies",
            "calculate local generated power",
            "calculate local thermal dissipation",
            "calculate hierarchical thermal diffusion",
            "update local heat",
            "calculate local thermal overload",
            "update gamma-noise correlation states",
            "update local gamma-effective values",
            "update thermal node factors",
            "calculate hierarchical phase-coupling field",
            "update phase velocities",
            "update wrapped phase words",
            "calculate multiscale phase coherence",
            "calculate C(t)",
            "calculate P(t)",
            "calculate C_minus_P",
            "detect first stability crossing",
            "capture post-tick outputs",
        ],
        "planned_rtl_files": [
            "rtl/m15/frp_m15_types_pkg.sv",
            "rtl/m15/frp_m15_fixed_point_pkg.sv",
            "rtl/m15/frp_m15_trig_lut_pkg.sv",
            "rtl/m15/frp_m15_scheduler.sv",
            "rtl/m15/frp_m15_transition_core.sv",
            "rtl/m15/frp_m15_neutral_route_queue.sv",
            "rtl/m15/frp_m15_delay_dynamics.sv",
            "rtl/m15/frp_m15_thermal_field.sv",
            "rtl/m15/frp_m15_gamma_drift.sv",
            "rtl/m15/frp_m15_hierarchical_coupling.sv",
            "rtl/m15/frp_m15_multiscale_coherence.sv",
            "rtl/m15/frp_m15_stability_telemetry.sv",
            "rtl/m15/frp_m15_top.sv",
        ],
        "kernel_requirements": {
            "balanced_ternary_states": [-1, 0, 1],
            "reserved_state_code": "2'b10",
            "actual_direct_events": 0,
            "tick_separated_neutral_routing": True,
            "scheduler_modes": list(SCHEDULER_MODES),
        },
    }


def rtl_assertion_correlation_harness(args: argparse.Namespace) -> Dict[str, Any]:
    assertions = [
        "valid balanced ternary encoding",
        "reserved-state exclusion",
        "direct polarity transition exclusion",
        "active neutral route insertion",
        "target application after ready tick",
        "actual_direct_events = 0",
        "transition-limit enforcement",
        "scheduler sequence",
        "scheduler count consistency",
        "phase topology fixed-point normalization",
        "thermal topology fixed-point normalization",
        "deterministic trace tick count",
        "exact cycle-output match",
    ]
    return {
        "schema": M15_RTL_ASSERTION_CORRELATION_HARNESS_SCHEMA,
        "kind": "rtl_assertion_correlation_harness",
        "version": VERSION,
        "milestone": MILESTONE,
        "assertion_count": len(assertions),
        "assertions": assertions,
               "direct_transition_rules": [
            "previous_state = -1 and current_state = 1 is a failure",
            "previous_state = 1 and current_state = -1 is a failure",
            "valid opposite-polarity migration requires intermediate state 0",
        ],
        "exact_comparison_rule": "actual integer field == expected integer field",
        "scheduler_modes": list(SCHEDULER_MODES),
    }


def run_float_and_shadow_correlation(
    args: argparse.Namespace,
    steps: Optional[int] = None,
) -> Dict[str, Any]:
    run_steps = args.steps if steps is None else steps
    float_processor = make_processor(args)
    shadow_processor = make_shadow_processor(args)

    request_plan = deterministic_request_plan(
        args.cells,
        args.transition_fraction,
        run_steps,
        args.seed,
        density=5,
    )

    state_sequence_match = True
    scheduler_sequence_match = True
    neutral_route_sequence_match = True
    C_minus_P_sign_match = True
    boundary_order_match = True

    max_phase_error = 0.0
    max_frequency_error = 0.0
    max_heat_error = 0.0
    max_gamma_error = 0.0
    max_coherence_error = 0.0
    max_C_error = 0.0
    max_P_error = 0.0
    max_C_minus_P_error = 0.0

    float_boundary_tick: Optional[int] = None
    shadow_boundary_tick: Optional[int] = None

    for tick_index in range(run_steps):
        requests = request_plan.get(tick_index, [])
        for valid, cell_idx, target in requests:
            if valid:
                float_processor.request_transition(cell_idx, target)

        float_processor.tick(
            tick_index,
            auto_targets=False,
        )
        shadow_row = shadow_processor.tick(
            tick_index,
            requests=requests,
            auto_targets_enable=False,
        )
        float_row = float_processor.telemetry[-1]

        state_sequence_match = state_sequence_match and (
            float_processor.states == shadow_processor.states
        )
        scheduler_sequence_match = scheduler_sequence_match and (
            float_row["scheduler_state"] == shadow_row["scheduler_state_name"]
        )
        neutral_route_sequence_match = neutral_route_sequence_match and (
            len(float_processor.pending_neutral_routes)
            == shadow_row["pending_route_count"]
        )

        float_sign = 1 if float_processor.C_minus_P > 0 else (0 if float_processor.C_minus_P == 0 else -1)
        shadow_sign = 1 if shadow_processor.C_minus_P_q16 > 0 else (
            0 if shadow_processor.C_minus_P_q16 == 0 else -1
        )
        C_minus_P_sign_match = C_minus_P_sign_match and (float_sign == shadow_sign)

        if float_boundary_tick is None and float_processor.first_C_minus_P_crossing is not None:
            float_boundary_tick = int(float_processor.first_C_minus_P_crossing["boundary_tick"])
        if shadow_boundary_tick is None and shadow_processor.first_boundary_crossing is not None:
            shadow_boundary_tick = int(shadow_processor.first_boundary_crossing["boundary_tick"])

        for cell_idx in range(args.cells):
            float_phase_word = phase_from_radians(float_processor.phases[cell_idx])
            max_phase_error = max(
                max_phase_error,
                phase_error_radians(float_phase_word, shadow_processor.phase_words[cell_idx]),
            )
            max_frequency_error = max(
                max_frequency_error,
                abs(
                    float_processor.frequencies[cell_idx]
                    - dequantize_q16(shadow_processor.frequency_current_q16[cell_idx])
                ),
            )
            max_heat_error = max(
                max_heat_error,
                abs(
                    float_processor.heat_cells[cell_idx]
                    - dequantize_q16(shadow_processor.heat_q16[cell_idx])
                ),
            )
            float_gamma = float_processor.gamma_effective[cell_idx]
            shadow_gamma_word = shadow_processor.gamma_effective_word[cell_idx] & PHASE_MASK
            float_gamma_word = phase_from_radians(float_gamma)
            max_gamma_error = max(
                max_gamma_error,
                phase_error_radians(float_gamma_word, shadow_gamma_word),
            )

        max_coherence_error = max(
            max_coherence_error,
            abs(
                float_processor.raw_phase_coherence
                - dequantize_q30(shadow_processor.raw_phase_coherence_q30)
            ),
        )
        max_C_error = max(
            max_C_error,
            abs(float_processor.C_value - dequantize_q16(shadow_processor.C_q16)),
        )
        max_P_error = max(
            max_P_error,
            abs(float_processor.P_value - dequantize_q16(shadow_processor.P_q16)),
        )
        max_C_minus_P_error = max(
            max_C_minus_P_error,
            abs(
                float_processor.C_minus_P
                - dequantize_q16(shadow_processor.C_minus_P_q16)
            ),
        )

    if float_boundary_tick is None and shadow_boundary_tick is None:
        boundary_order_match = True
    elif float_boundary_tick is None or shadow_boundary_tick is None:
        boundary_order_match = False
    else:
        boundary_order_match = abs(float_boundary_tick - shadow_boundary_tick) <= 1

    return {
        "state_sequence_match": 1.0 if state_sequence_match else 0.0,
        "scheduler_sequence_match": 1.0 if scheduler_sequence_match else 0.0,
        "neutral_route_sequence_match": 1.0 if neutral_route_sequence_match else 0.0,
        "C_minus_P_sign_match": 1.0 if C_minus_P_sign_match else 0.0,
        "boundary_order_match": 1.0 if boundary_order_match else 0.0,
        "max_phase_error": max_phase_error,
        "max_frequency_error": max_frequency_error,
        "max_heat_error": max_heat_error,
        "max_gamma_error": max_gamma_error,
        "max_coherence_error": max_coherence_error,
        "max_C_error": max_C_error,
        "max_P_error": max_P_error,
        "max_C_minus_P_error": max_C_minus_P_error,
        "float_boundary_tick": float_boundary_tick,
        "shadow_boundary_tick": shadow_boundary_tick,
        "float_summary": float_processor.summarize(run_steps),
        "shadow_summary": shadow_processor.summarize(run_steps),
    }


def exact_shadow_replay_report(args: argparse.Namespace) -> Dict[str, Any]:
    request_plan = deterministic_request_plan(
        args.cells,
        args.transition_fraction,
        args.steps,
        args.seed,
        density=5,
    )
    first = execute_shadow_trace(
        args,
        request_plan=request_plan,
        auto_targets_enable=True,
    )
    second = execute_shadow_trace(
        args,
        request_plan=request_plan,
        auto_targets_enable=True,
    )
    first_trace = canonical_json_bytes(first["trace"])
    second_trace = canonical_json_bytes(second["trace"])
    first_cells = canonical_json_bytes(first["cell_trace"])
    second_cells = canonical_json_bytes(second["cell_trace"])
    return {
        "shadow_replay_state_match": 1.0 if [row["states_packed"] for row in first["trace"]]
        == [row["states_packed"] for row in second["trace"]] else 0.0,
        "shadow_replay_scheduler_match": 1.0 if [row["scheduler_state"] for row in first["trace"]]
        == [row["scheduler_state"] for row in second["trace"]] else 0.0,
        "shadow_replay_pending_route_match": 1.0 if [row["pending_route_count"] for row in first["trace"]]
        == [row["pending_route_count"] for row in second["trace"]] else 0.0,
        "shadow_replay_counter_match": 1.0 if [
            (
                row["requested_direct_events"],
                row["prevented_direct_events"],
                row["neutral_routed_events"],
                row["neutralized_conflicts"],
                row["actual_direct_events"],
            )
            for row in first["trace"]
        ] == [
            (
                row["requested_direct_events"],
                row["prevented_direct_events"],
                row["neutral_routed_events"],
                row["neutralized_conflicts"],
                row["actual_direct_events"],
            )
            for row in second["trace"]
        ] else 0.0,
        "shadow_replay_trace_match": 1.0 if first_trace == second_trace else 0.0,
        "shadow_replay_cell_trace_match": 1.0 if first_cells == second_cells else 0.0,
        "trace_digest": sha256_bytes(first_trace),
        "cell_trace_digest": sha256_bytes(first_cells),
    }


def reference_rtl_equivalence_report(args: argparse.Namespace) -> Dict[str, Any]:
    semantic = run_float_and_shadow_correlation(args)
    exact_replay = exact_shadow_replay_report(args)
    return {
        "schema": M15_REFERENCE_RTL_EQUIVALENCE_REPORT_SCHEMA,
        "kind": "reference_rtl_equivalence_report",
        "version": VERSION,
        "milestone": MILESTONE,
        "floating_reference_to_quantized_shadow": semantic,
        "quantized_shadow_deterministic_replay": exact_replay,
        "rtl_exact_integer_comparison_contract": {
            "comparison_rule": "actual == expected",
            "required_domains": [
                "packed ternary states",
                "scheduler state",
                "pending route count",
                "fixed-point scalar outputs",
                "phase words",
                "transition counters",
                "per-cell thermal values",
                "per-cell gamma values",
                "coupling-field values",
            ],
        },
    }


def qualification_closure_manifest(args: argparse.Namespace) -> Dict[str, Any]:
    fixed = fixed_point_interface_profile(args)
    vectors = rtl_comparison_vector_package(args)
    correlation = reference_rtl_equivalence_report(args)
    exact = correlation["quantized_shadow_deterministic_replay"]
    semantic = correlation["floating_reference_to_quantized_shadow"]
    checks = {
        "balanced_ternary_state_sequence_match": semantic["state_sequence_match"] == 1.0,
        "scheduler_sequence_match": semantic["scheduler_sequence_match"] == 1.0,
        "neutral_route_sequence_match": semantic["neutral_route_sequence_match"] == 1.0,
        "C_minus_P_sign_match": semantic["C_minus_P_sign_match"] == 1.0,
        "boundary_order_match": semantic["boundary_order_match"] == 1.0,
        "fixed_point_topology_sum_exact": fixed["fixed_point_topology_sum_exact"],
        "fixed_point_thermal_sum_exact": fixed["fixed_point_thermal_sum_exact"],
        "shadow_replay_trace_match": exact["shadow_replay_trace_match"] == 1.0,
        "shadow_replay_cell_trace_match": exact[
            "shadow_replay_cell_trace_match"
        ] == 1.0,
        "vector_package_present": vectors["manifest"]["file_count"] >= 10,
    }
    return {
        "schema": M15_QUALIFICATION_CLOSURE_MANIFEST_SCHEMA,
        "kind": "qualification_closure_manifest",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "artifact_layers": list(M15_ARTIFACT_LAYERS),
        "vector_manifest": vectors["manifest"],
        "semantic_correlation": semantic,
        "exact_shadow_replay": exact,
    }


def neutral_route_direction_validation(
    args: argparse.Namespace,
    start_state: int,
    target_state_value: int,
) -> Dict[str, Any]:
    processor = make_shadow_processor(args, cells=8, scheduler="free")
    processor.states = [0 for _ in range(8)]
    processor.states[0] = start_state
    processor.tick(
        0,
        requests=[(True, 0, target_state_value)],
        auto_targets_enable=False,
    )
    state_tick_0 = processor.states[0]
    pending_tick_0 = list(processor.pending_neutral_routes)
    processor.tick(1, requests=[], auto_targets_enable=False)
    state_tick_1 = processor.states[0]
    checks = {
        "start_is_active_polarity": start_state in (-1, 1),
        "target_is_opposite_polarity": target_state_value == -start_state,
        "tick_0_reaches_neutral": state_tick_0 == 0,
        "tick_0_pending_route_present": len(pending_tick_0) == 1,
        "tick_0_target_not_applied": state_tick_0 != target_state_value,
        "tick_1_reaches_target": state_tick_1 == target_state_value,
        "requested_direct_events_one": processor.requested_direct_events == 1,
        "prevented_direct_events_one": processor.prevented_direct_events == 1,
        "neutral_routed_events_one": processor.neutral_routed_events == 1,
        "actual_direct_events_zero": processor.actual_direct_events == 0,
    }
    return {
        "direction": f"{start_state} -> 0 -> {target_state_value}",
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "state_tick_0": state_tick_0,
        "state_tick_1": state_tick_1,
        "summary": processor.summarize(2),
    }


def queue_exhaustion_validation(args: argparse.Namespace) -> Dict[str, Any]:
    processor = make_shadow_processor(args, cells=8, scheduler="free")
    processor.states = [0 for _ in range(8)]
    processor.states[0] = -1
    processor.pending_neutral_routes = [
        (index, 1 if index % 2 == 0 else -1, 100 + index)
        for index in range(processor.neutral_route_queue_capacity)
    ]
    processor.tick(
        0,
        requests=[(True, 0, 1)],
        auto_targets_enable=False,
    )
    checks = {
        "queue_capacity_equals_cells": processor.neutral_route_queue_capacity == 8,
        "overflow_detected": processor.queue_overflow_events == 1,
        "queue_length_bounded": len(processor.pending_neutral_routes)
        == processor.neutral_route_queue_capacity,
        "same_tick_result_neutral": processor.states[0] == 0,
        "actual_direct_events_zero": processor.actual_direct_events == 0,
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "summary": processor.summarize(1),
    }


def scheduler_shadow_validation(args: argparse.Namespace, mode: str) -> Dict[str, Any]:
    processor = make_shadow_processor(args, scheduler=mode)
    plan = deterministic_request_plan(
        processor.cells,
        processor.transition_fraction,
        16,
        args.seed + SCHEDULER_MODE_TO_CODE[mode],
        density=4,
    )
    processor.run(16, auto_targets_enable=False, request_plan=plan)
    summary = processor.summarize(16)
    checks = {
        "balanced_ternary_state_domain": summary["balanced_ternary_state_domain"],
        "reserved_state_events_zero": summary["reserved_state_events"] == 0,
        "actual_direct_events_zero": summary["actual_direct_events"] == 0,
        "scheduler_counts_match": summary["scheduler_counts"]
        == expected_scheduler_counts(mode, 16),
        "scheduler_counts_valid": summary["scheduler_counts_valid"],
        "ticks_recorded_equals_steps": summary["ticks_recorded"] == 16,
        "switch_load_within_transition_fraction": summary["switch_load_peak"]
        <= processor.transition_fraction + 1e-12,
    }
    return {
        "scheduler": mode,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "summary": summary,
    }


def request_lane_order_validation(args: argparse.Namespace) -> Dict[str, Any]:
    processor = make_shadow_processor(args, cells=8, scheduler="free")
    processor.states = [0 for _ in range(8)]
    processor.tick(
        0,
        requests=[
            (True, 0, 1),
            (True, 0, -1),
        ],
        auto_targets_enable=False,
    )
    checks = {
        "request_lanes_at_least_two": processor.request_lanes >= 2,
        "lane_zero_applied_first": processor.requested_direct_events == 1,
        "lane_one_opposite_request_intercepted": processor.prevented_direct_events == 1,
        "same_tick_result_neutral": processor.states[0] == 0,
        "pending_target_is_minus_one": bool(processor.pending_neutral_routes)
        and processor.pending_neutral_routes[0][1] == -1,
        "actual_direct_events_zero": processor.actual_direct_events == 0,
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "summary": processor.summarize(1),
    }


def fixed_point_boundary_validation() -> Dict[str, Any]:
    checks = {
        "positive_half_rounds_away": round_half_away_from_zero(1.5) == 2,
        "negative_half_rounds_away": round_half_away_from_zero(-1.5) == -2,
        "positive_q16_half_lsb_rounds_up": round_div_away_from_zero(1, 2) == 1,
        "negative_q16_half_lsb_rounds_down": round_div_away_from_zero(-1, 2) == -1,
        "positive_saturation": sat_s32(S32_MAX + 100) == S32_MAX,
        "negative_saturation": sat_s32(S32_MIN - 100) == S32_MIN,
        "q16_one_exact": quantize_q16(1.0) == Q16_SCALE,
        "q30_one_exact": quantize_q30(1.0) == Q30_SCALE,
        "mul_q16_identity": mul_q16(quantize_q16(0.375), quantize_q16(1.0))
        == quantize_q16(0.375),
        "mul_q30_identity": mul_q30(quantize_q30(0.375), quantize_q30(1.0))
        == quantize_q30(0.375),
        "phase_zero": phase_from_radians(0.0) == 0,
        "phase_quarter_cycle": phase_from_radians(math.pi / 2) == 0x40000000,
        "phase_half_cycle": phase_from_radians(math.pi) == 0x80000000,
        "phase_wrap": phase_from_radians(math.tau) == 0,
        "phase_negative_wrap": phase_from_radians(-math.pi / 2) == 0xC0000000,
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
    }


def encoding_validation() -> Dict[str, Any]:
    sample = [-1, 0, 1, 0, -1, 1, 0, 0]
    packed = pack_states(sample)
    reserved_rejected = False
    try:
        code_to_state(RESERVED_STATE_CODE)
    except ValueError:
        reserved_rejected = True
    checks = {
        "minus_one_code": state_to_code(-1) == 0b11,
        "neutral_code": state_to_code(0) == 0b00,
        "plus_one_code": state_to_code(1) == 0b01,
        "reserved_code_is_10": RESERVED_STATE_CODE == 0b10,
        "reserved_state_rejected": reserved_rejected,
        "packed_roundtrip": unpack_states(packed, len(sample)) == sample,
        "cell_zero_occupies_low_bits": (packed & 0b11) == state_to_code(sample[0]),
        "scheduler_mode_free": SCHEDULER_MODE_TO_CODE["free"] == 0b00,
        "scheduler_mode_7_1": SCHEDULER_MODE_TO_CODE["7/1"] == 0b01,
        "scheduler_mode_1_7": SCHEDULER_MODE_TO_CODE["1/7"] == 0b10,
        "scheduler_state_encodings_unique": len(set(SCHEDULER_STATE_TO_CODE.values()))
        == len(SCHEDULER_STATE_TO_CODE),
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "sample_states": sample,
        "packed_hex": packed_state_hex(sample),
    }


def topology_fixed_point_validation(args: argparse.Namespace, cells: int) -> Dict[str, Any]:
    coupling = quantized_level_weights(cells, args.fractal_alpha)
    thermal = quantized_level_weights(cells, args.thermal_beta)
    coupling_sum = sum(shell_population(d) * coupling[d] for d in coupling)
    thermal_sum = sum(shell_population(d) * thermal[d] for d in thermal)
    coupling_aggregate = [shell_population(d) * coupling[d] for d in sorted(coupling)]
    thermal_aggregate = [shell_population(d) * thermal[d] for d in sorted(thermal)]
    checks = {
        "cells_power_of_two": is_power_of_two(cells),
        "hierarchy_depth_exact": hierarchy_depth_for_cells(cells) == cells.bit_length() - 1,
        "coupling_sum_exact": coupling_sum == Q30_SCALE,
        "thermal_sum_exact": thermal_sum == Q30_SCALE,
        "coupling_shell_influence_monotonic": all(
            coupling_aggregate[i] > coupling_aggregate[i + 1]
            for i in range(len(coupling_aggregate) - 1)
        ),
        "thermal_shell_influence_monotonic": all(
            thermal_aggregate[i] > thermal_aggregate[i + 1]
            for i in range(len(thermal_aggregate) - 1)
        ),
        "shell_populations_exact": [
            shell_population(d) for d in range(1, hierarchy_depth_for_cells(cells) + 1)
        ] == [1 << (d - 1) for d in range(1, hierarchy_depth_for_cells(cells) + 1)],
    }
    return {
        "cells": cells,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "coupling_sum_q30": coupling_sum,
        "thermal_sum_q30": thermal_sum,
    }


def trig_lut_validation() -> Dict[str, Any]:
    second = tuple(
        quantize_q30(math.sin(math.tau * index / TRIG_LUT_SIZE))
        for index in range(TRIG_LUT_SIZE)
    )
    checks = {
        "entry_count": len(TRIG_SIN_Q30) == TRIG_LUT_SIZE,
        "deterministic_rebuild": second == TRIG_SIN_Q30,
        "sin_zero": TRIG_SIN_Q30[0] == 0,
        "sin_quarter_cycle": abs(TRIG_SIN_Q30[TRIG_LUT_SIZE // 4] - Q30_SCALE) <= 1,
        "sin_half_cycle": abs(TRIG_SIN_Q30[TRIG_LUT_SIZE // 2]) <= 1,
        "cos_relation": cos_phase_q30(0) == TRIG_SIN_Q30[TRIG_LUT_SIZE // 4],
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "sha256": sha256_bytes(
            b"".join(int(value).to_bytes(4, "little", signed=True) for value in TRIG_SIN_Q30)
        ),
    }


def vector_determinism_validation(args: argparse.Namespace) -> Dict[str, Any]:
    first = build_vector_package_contents(args)
    second = build_vector_package_contents(args)
    same_names = sorted(first) == sorted(second)
    byte_matches = {
        name: first[name] == second[name]
        for name in sorted(set(first) & set(second))
    }
    checks = {
        "same_file_set": same_names,
        "all_files_byte_identical": all(byte_matches.values()),
        "sha256_manifest_present": "frp_m15_sha256_manifest.json" in first,
        "kernel_vectors_present": "frp_m15_kernel_vectors.vec" in first,
        "free_scheduler_vectors_present": "frp_m15_scheduler_free_vectors.vec" in first,
        "scheduler_7_1_vectors_present": "frp_m15_scheduler_7_1_vectors.vec" in first,
        "scheduler_1_7_vectors_present": "frp_m15_scheduler_1_7_vectors.vec" in first,
        "full_correlation_vectors_present": "frp_m15_full_correlation_vectors.vec" in first,
        "cell_trace_present": "frp_m15_cell_trace.vec" in first,
        "preload_manifest_present": "frp_m15_reference_preload.json" in first,
        "trig_lut_present": "frp_m15_trig_lut_q30.vec" in first,
    }
    return {
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "byte_matches": byte_matches,
        "package_digest": sha256_bytes(
            b"".join(name.encode("utf-8") + b"\0" + first[name] for name in sorted(first))
        ),
        "manifest": vector_package_manifest(first),
    }


def scaling_profile_validation(args: argparse.Namespace, cells: int) -> Dict[str, Any]:
    processor = make_shadow_processor(args, cells=cells, scheduler="7/1")
    plan = deterministic_request_plan(
        cells,
        args.transition_fraction,
        16,
        args.seed + cells,
        density=4,
    )
    processor.run(16, auto_targets_enable=False, request_plan=plan)
    summary = processor.summarize(16)
    topology = topology_fixed_point_validation(args, cells)
    expected_lanes = max(1, int(round(cells * args.transition_fraction)))
    checks = {
        "hierarchy_depth": summary["hierarchy_depth"] == cells.bit_length() - 1,
        "request_lanes": summary["request_lanes"] == expected_lanes,
        "packed_state_width": 2 * cells == 2 * summary["cells"],
        "balanced_ternary_state_domain": summary["balanced_ternary_state_domain"],
        "reserved_state_events_zero": summary["reserved_state_events"] == 0,
        "actual_direct_events_zero": summary["actual_direct_events"] == 0,
        "queue_overflow_events_zero": summary["queue_overflow_events"] == 0,
        "switch_load_within_transition_fraction": summary["switch_load_peak"]
        <= args.transition_fraction + 1e-12,
        "scheduler_counts_valid": summary["scheduler_counts_valid"],
        "fixed_point_topology_sum_exact": summary["fixed_point_topology_sum_exact"],
        "fixed_point_thermal_sum_exact": summary["fixed_point_thermal_sum_exact"],
        "topology_validation_pass": topology["status"] == "PASS",
    }
    return {
        "cells": cells,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "checks": checks,
        "summary": summary,
        "topology": topology,
    }


def benchmark_matrix(args: argparse.Namespace) -> Dict[str, Any]:
    semantic = run_float_and_shadow_correlation(args, steps=min(args.steps, 64))
    exact = exact_shadow_replay_report(args)
    rows = [
        {
            "architecture": "frp_v1_6_0_m14_floating_semantic_reference",
            "numeric_domain": "floating semantic reference",
            "cycle_exact_integer_trace": False,
            "hardware_facing_encoding": False,
            "interaction_scaling": "O(N log N) hierarchical reference path",
        },
        {
            "architecture": "frp_v1_7_0_quantized_hardware_shadow",
            "numeric_domain": "S32Q16 / S32Q30 / PHASE_U32 / GAMMA_S32",
            "cycle_exact_integer_trace": True,
            "hardware_facing_encoding": True,
            "interaction_scaling": "O(N^2) shadow evaluation with exact dyadic weights",
            "state_sequence_match": semantic["state_sequence_match"],
            "scheduler_sequence_match": semantic["scheduler_sequence_match"],
            "C_minus_P_sign_match": semantic["C_minus_P_sign_match"],
        },
        {
            "architecture": "frp_v1_7_0_cycle_exact_vector_package",
            "numeric_domain": "integer and hexadecimal vectors",
            "cycle_exact_integer_trace": True,
            "hardware_facing_encoding": True,
            "vector_repeat_match": exact["shadow_replay_trace_match"],
        },
        {
            "architecture": "frp_v1_7_0_systemverilog_correlation_contract",
            "numeric_domain": "exact integer comparison",
            "cycle_exact_integer_trace": True,
            "hardware_facing_encoding": True,
            "comparison_rule": "actual == expected",
        },
        {
            "architecture": "frp_v1_7_0_qualification_closure",
            "numeric_domain": "semantic correlation plus exact integer replay",
            "cycle_exact_integer_trace": True,
            "hardware_facing_encoding": True,
            "artifact_layers": len(M15_ARTIFACT_LAYERS),
        },
    ]
    return {
        "schema": BENCHMARK_SCHEMA,
        "kind": "benchmark_matrix",
        "version": VERSION,
        "milestone": MILESTONE,
        "rows": rows,
    }


def m15_self_test(args: argparse.Namespace) -> Dict[str, Any]:
    route_minus_to_plus = neutral_route_direction_validation(args, -1, 1)
    route_plus_to_minus = neutral_route_direction_validation(args, 1, -1)
    scheduler_free = scheduler_shadow_validation(args, "free")
    scheduler_7_1 = scheduler_shadow_validation(args, "7/1")
    scheduler_1_7 = scheduler_shadow_validation(args, "1/7")
    lane_order = request_lane_order_validation(args)
    queue_exhaustion = queue_exhaustion_validation(args)
    fixed = fixed_point_boundary_validation()
    encoding = encoding_validation()
    topology_8 = topology_fixed_point_validation(args, 8)
    topology_16 = topology_fixed_point_validation(args, 16)
    topology_32 = topology_fixed_point_validation(args, 32)
    trig = trig_lut_validation()
    semantic = run_float_and_shadow_correlation(args)
    exact = exact_shadow_replay_report(args)
    vectors = vector_determinism_validation(args)
    scale_8 = scaling_profile_validation(args, 8)
    scale_16 = scaling_profile_validation(args, 16)
    scale_32 = scaling_profile_validation(args, 32)

    exports = {
        "fixed_point": fixed_point_interface_profile(args),
        "encoding": balanced_ternary_hardware_encoding_map(args),
        "shadow": quantized_reference_shadow_model(args),
        "trace": cycle_exact_reference_trace(args),
        "vectors": rtl_comparison_vector_package(args),
        "sv_interface": systemverilog_testbench_interface_map(args),
        "rtl_core": synthesizable_rtl_reference_core(args),
        "assertions": rtl_assertion_correlation_harness(args),
        "equivalence": reference_rtl_equivalence_report(args),
        "closure": qualification_closure_manifest(args),
    }

    checks = {
        "route_minus_to_plus_pass": route_minus_to_plus["status"] == "PASS",
        "route_plus_to_minus_pass": route_plus_to_minus["status"] == "PASS",
        "free_scheduler_pass": scheduler_free["status"] == "PASS",
        "7_1_scheduler_pass": scheduler_7_1["status"] == "PASS",
        "1_7_scheduler_pass": scheduler_1_7["status"] == "PASS",
        "request_lane_order_pass": lane_order["status"] == "PASS",
        "queue_exhaustion_detection_pass": queue_exhaustion["status"] == "PASS",
        "fixed_point_boundary_pass": fixed["status"] == "PASS",
        "encoding_pass": encoding["status"] == "PASS",
        "topology_8_pass": topology_8["status"] == "PASS",
        "topology_16_pass": topology_16["status"] == "PASS",
        "topology_32_pass": topology_32["status"] == "PASS",
        "trig_lut_pass": trig["status"] == "PASS",
        "semantic_state_sequence_match": semantic["state_sequence_match"] == 1.0,
        "semantic_scheduler_sequence_match": semantic["scheduler_sequence_match"] == 1.0,
        "semantic_neutral_route_sequence_match": semantic["neutral_route_sequence_match"] == 1.0,
        "semantic_C_minus_P_sign_match": semantic["C_minus_P_sign_match"] == 1.0,
        "semantic_boundary_order_match": semantic["boundary_order_match"] == 1.0,
        "exact_shadow_state_match": exact["shadow_replay_state_match"] == 1.0,
        "exact_shadow_scheduler_match": exact["shadow_replay_scheduler_match"] == 1.0,
        "exact_shadow_pending_route_match": exact["shadow_replay_pending_route_match"] == 1.0,
        "exact_shadow_counter_match": exact["shadow_replay_counter_match"] == 1.0,
        "exact_reference_vector_replay_match": exact["shadow_replay_trace_match"] == 1.0,
        "exact_reference_cell_trace_replay_match": exact[
            "shadow_replay_cell_trace_match"
        ] == 1.0,
        "vector_determinism_pass": vectors["status"] == "PASS",
        "scale_8_pass": scale_8["status"] == "PASS",
        "scale_16_pass": scale_16["status"] == "PASS",
        "scale_32_pass": scale_32["status"] == "PASS",
        "artifact_layer_count_10": len(M15_ARTIFACT_LAYERS) == 10,
        "export_schema_count_10": len(M15_EXPORT_SCHEMAS) == 10,
        "fixed_point_topology_sum_exact": exports["fixed_point"][
            "fixed_point_topology_sum_exact"
        ],
        "fixed_point_thermal_sum_exact": exports["fixed_point"][
            "fixed_point_thermal_sum_exact"
        ],
        "shadow_actual_direct_events_zero": exports["shadow"]["summary"][
            "actual_direct_events"
        ] == 0,
        "shadow_reserved_state_events_zero": exports["shadow"]["summary"][
            "reserved_state_events"
        ] == 0,
        "shadow_queue_overflow_events_zero": exports["shadow"]["summary"][
            "queue_overflow_events"
        ] == 0,
        "shadow_balanced_ternary_domain": exports["shadow"]["summary"][
            "balanced_ternary_state_domain"
        ],
        "shadow_scheduler_counts_valid": exports["shadow"]["summary"][
            "scheduler_counts_valid"
        ],
        "shadow_ticks_recorded_equals_steps": exports["shadow"]["summary"][
            "ticks_recorded"
        ] == args.steps,
        "shadow_switch_load_within_transition_fraction": exports["shadow"]["summary"][
            "switch_load_peak"
        ] <= args.transition_fraction + 1e-12,
        "all_export_schemas_exact": [
            exports["fixed_point"]["schema"],
            exports["encoding"]["schema"],
            exports["shadow"]["schema"],
            exports["trace"]["schema"],
            exports["vectors"]["schema"],
            exports["sv_interface"]["schema"],
            exports["rtl_core"]["schema"],
            exports["assertions"]["schema"],
            exports["equivalence"]["schema"],
            exports["closure"]["schema"],
        ] == M15_EXPORT_SCHEMAS,
        "qualification_closure_pass": exports["closure"]["status"] == "PASS",
    }

    return {
        "schema": STRUCTURED_SCHEMA,
        "kind": "self_test",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "check_count": len(checks),
        "checks": checks,
        "neutral_route_validation": {
            "-1_to_0_to_1": route_minus_to_plus,
            "1_to_0_to_-1": route_plus_to_minus,
        },
        "scheduler_validation": {
            "free": scheduler_free,
            "7/1": scheduler_7_1,
            "1/7": scheduler_1_7,
        },
        "request_lane_order_validation": lane_order,
        "queue_exhaustion_validation": queue_exhaustion,
        "fixed_point_validation": fixed,
        "encoding_validation": encoding,
        "topology_validation": {
            "8": topology_8,
            "16": topology_16,
            "32": topology_32,
        },
        "trigonometric_lut_validation": trig,
        "semantic_correlation": semantic,
        "exact_shadow_replay": exact,
        "vector_determinism": vectors,
        "scaling_validation": {
            "8": scale_8,
            "16": scale_16,
            "32": scale_32,
        },
    }


def structured_output(
    kind: str,
    args: argparse.Namespace,
    include_trace: bool = False,
) -> Dict[str, Any]:
    request_plan = deterministic_request_plan(
        args.cells,
        args.transition_fraction,
        args.steps,
        args.seed,
        density=5,
    )
    result = execute_shadow_trace(
        args,
        request_plan=request_plan,
        auto_targets_enable=True,
    )
    payload: Dict[str, Any] = {
        "schema": STRUCTURED_SCHEMA,
        "kind": kind,
        "version": VERSION,
        "milestone": MILESTONE,
        "configuration": {
            "cells": args.cells,
            "steps": args.steps,
            "seed": args.seed,
            "scheduler": args.scheduler,
            "transition_fraction": args.transition_fraction,
            "request_lanes": request_lanes_for_profile(
                args.cells, args.transition_fraction
            ),
            "gamma_nominal": args.gamma,
            "fractal_alpha": args.fractal_alpha,
            "thermal_beta": args.thermal_beta,
            "ambient_heat": args.ambient_heat,
            "thermal_time_constant": args.thermal_time_constant,
            "thermal_soft_limit": args.thermal_soft_limit,
            "thermal_hard_limit": args.thermal_hard_limit,
            "coupling_nominal": args.coupling_nominal,
            "delay_alpha": args.delay_alpha,
            "thermal_diffusion_gain": args.thermal_diffusion_gain,
        },
        "kernel": {
            "balanced_ternary_states": [-1, 0, 1],
            "active_neutral_state": 0,
            "neutral_routes": ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
            "scheduler_modes": list(SCHEDULER_MODES),
            "actual_direct_events_target": 0,
        },
        "hardware_profile": {
            "scalar": "S32Q16",
            "unit": "S32Q30",
            "phase": "PHASE_U32",
            "gamma": "GAMMA_S32",
            "state_encoding": {
                "-1": "11",
                "0": "00",
                "1": "01",
                "reserved": "10",
            },
        },
        "summary": result["summary"],
        "preload_digest": sha256_bytes(canonical_json_bytes(result["preload"])),
        "trace_digest": sha256_bytes(canonical_json_bytes(result["trace"])),
        "cell_trace_digest": sha256_bytes(canonical_json_bytes(result["cell_trace"])),
    }
    if include_trace:
        payload["trace"] = result["trace"]
        payload["cell_trace"] = result["cell_trace"]
        payload["route_events"] = result["route_events"]
    return payload


def text_report(payload: Dict[str, Any]) -> str:
    lines = [
        f"FRP v{VERSION}",
        MILESTONE,
        f"kind: {payload.get('kind')}",
    ]
    if payload.get("status"):
        lines.append(f"status: {payload.get('status')}")
    summary = payload.get("summary")
    if summary:
        for key in [
            "balanced_ternary_state_domain",
            "reserved_state_events",
            "actual_direct_events",
            "scheduler",
            "scheduler_counts",
            "switch_load_peak",
            "C_minus_P_min",
            "fixed_point_topology_sum_exact",
            "fixed_point_thermal_sum_exact",
        ]:
            if key in summary:
                lines.append(f"{key}: {summary[key]}")
    if payload.get("check_count") is not None:
        lines.append(f"check_count: {payload['check_count']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "FRP v1.7.0 M15 Implementation Mapping, Domain Interface, "
            "and Qualification Closure Package"
        )
    )
    parser.add_argument(
        "--mode",
        choices=("demo", "self-test", "benchmark"),
        default="demo",
    )
    parser.add_argument(
        "--output",
        choices=("text", "json"),
        default="text",
    )
    parser.add_argument("--include-trace", action="store_true")
    parser.add_argument("--scheduler", choices=SCHEDULER_MODES, default="7/1")
    parser.add_argument("--cells", type=int, default=DEFAULT_CELLS)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--transition-fraction", type=float, default=DEFAULT_TRANSITION_FRACTION
    )
    parser.add_argument("--gamma", type=float, default=DEFAULT_GAMMA)
    parser.add_argument("--fractal-alpha", type=float, default=DEFAULT_FRACTAL_ALPHA)
    parser.add_argument("--thermal-beta", type=float, default=DEFAULT_THERMAL_BETA)
    parser.add_argument("--ambient-heat", type=float, default=DEFAULT_AMBIENT_HEAT)
    parser.add_argument(
        "--thermal-time-constant", type=float, default=DEFAULT_THERMAL_TIME_CONSTANT
    )
    parser.add_argument(
        "--thermal-soft-limit", type=float, default=DEFAULT_THERMAL_SOFT_LIMIT
    )
    parser.add_argument(
        "--thermal-hard-limit", type=float, default=DEFAULT_THERMAL_HARD_LIMIT
    )
    parser.add_argument(
        "--coupling-nominal", type=float, default=DEFAULT_COUPLING_NOMINAL
    )
    parser.add_argument("--delay-alpha", type=float, default=DEFAULT_DELAY_ALPHA)
    parser.add_argument(
        "--thermal-diffusion-gain",
        type=float,
        default=DEFAULT_THERMAL_DIFFUSION_GAIN,
    )
    parser.add_argument(
        "--equivalence-tolerance",
        type=float,
        default=DEFAULT_EQUIVALENCE_TOLERANCE,
    )
    parser.add_argument(
        "--vector-output-dir",
        type=str,
        default=None,
        help="Optional directory for writing the deterministic M15 vector package",
    )

    parser.add_argument("--export-fixed-point-interface-profile", action="store_true")
    parser.add_argument(
        "--export-balanced-ternary-hardware-encoding-map", action="store_true"
    )
    parser.add_argument("--export-quantized-reference-shadow-model", action="store_true")
    parser.add_argument("--export-cycle-exact-reference-trace", action="store_true")
    parser.add_argument("--export-rtl-comparison-vector-package", action="store_true")
    parser.add_argument(
        "--export-systemverilog-testbench-interface-map", action="store_true"
    )
    parser.add_argument("--export-synthesizable-rtl-reference-core", action="store_true")
    parser.add_argument(
        "--export-rtl-assertion-correlation-harness", action="store_true"
    )
    parser.add_argument("--export-reference-rtl-equivalence-report", action="store_true")
    parser.add_argument("--export-qualification-closure-manifest", action="store_true")
    parser.add_argument("--export-benchmark-matrix", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not is_power_of_two(args.cells) or args.cells < 2:
        parser.error("--cells must be a power of two and at least 2")

    if args.export_fixed_point_interface_profile:
        payload = fixed_point_interface_profile(args)
    elif args.export_balanced_ternary_hardware_encoding_map:
        payload = balanced_ternary_hardware_encoding_map(args)
    elif args.export_quantized_reference_shadow_model:
        payload = quantized_reference_shadow_model(args)
    elif args.export_cycle_exact_reference_trace:
        payload = cycle_exact_reference_trace(args)
    elif args.export_rtl_comparison_vector_package:
        payload = rtl_comparison_vector_package(args)
    elif args.export_systemverilog_testbench_interface_map:
        payload = systemverilog_testbench_interface_map(args)
    elif args.export_synthesizable_rtl_reference_core:
        payload = synthesizable_rtl_reference_core(args)
    elif args.export_rtl_assertion_correlation_harness:
        payload = rtl_assertion_correlation_harness(args)
    elif args.export_reference_rtl_equivalence_report:
        payload = reference_rtl_equivalence_report(args)
    elif args.export_qualification_closure_manifest:
        payload = qualification_closure_manifest(args)
    elif args.export_benchmark_matrix:
        payload = benchmark_matrix(args)
    elif args.mode == "self-test":
        payload = m15_self_test(args)
    elif args.mode == "benchmark":
        payload = benchmark_matrix(args)
    else:
        payload = structured_output("demo", args, include_trace=args.include_trace)

    export_requested = any(
        [
            args.export_fixed_point_interface_profile,
            args.export_balanced_ternary_hardware_encoding_map,
            args.export_quantized_reference_shadow_model,
            args.export_cycle_exact_reference_trace,
            args.export_rtl_comparison_vector_package,
            args.export_systemverilog_testbench_interface_map,
            args.export_synthesizable_rtl_reference_core,
            args.export_rtl_assertion_correlation_harness,
            args.export_reference_rtl_equivalence_report,
            args.export_qualification_closure_manifest,
            args.export_benchmark_matrix,
        ]
    )

    if args.output == "json" or export_requested or args.mode == "benchmark":
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(text_report(payload))


if __name__ == "__main__":
    main()
