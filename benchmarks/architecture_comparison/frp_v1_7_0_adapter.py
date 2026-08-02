#!/usr/bin/env python3
"""FRP v1.7.0 M15 quantized shadow adapter for architecture comparisons."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from common_cost_model import (
    CostModelError,
    EVENT_FIELDS,
    empty_event_counts,
    validate_event_counts,
)
from common_workload import (
    ISSUE_POLICY_TRANSACTION_SERIAL,
    NEGATIVE_TARGET,
    POSITIVE_TARGET,
    WorkloadError,
    WorkloadProfile,
    build_workload_package,
    validate_workload_package,
)

ARCHITECTURE_RESULT_SCHEMA = "frp.benchmark.architecture_reference_result.v1"
ARCHITECTURE_SELF_TEST_SCHEMA = (
    "frp.benchmark.frp_v1_7_0_adapter.self_test.v1"
)
SUITE_NAME = "FRP Comparative Architecture Benchmark Suite"
ARCHITECTURE_ID = "frp_v1_7_0_quantized_shadow"
ARCHITECTURE_NAME = "FRP v1.7.0 Quantized Hardware Shadow Reference"
EVENT_ACCOUNTING_PROFILE = "m15_shadow_algorithmic_event_accounting_v1"
DEFAULT_FRP_SCHEDULER = "7/1"
STATE_BITS_PER_CELL = 2

EXPECTED_FRP_SOURCE_SHA256 = (
    "9de085915aa0fb8a73705c0927cc875b106480ef8a75a76f599be04440c0f099"
)

SEMANTIC_TO_FRP_STATE = {
    NEGATIVE_TARGET: -1,
    POSITIVE_TARGET: 1,
}

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FRP_SOURCE_PATH = REPOSITORY_ROOT / "frp_prototype_v1_7_0.py"


class FRPAdapterError(ValueError):
    """Raised when FRP adapter integration or execution is invalid."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON deterministically for hashing and byte comparison."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_frp_source() -> str:
    """Verify that the adapter is bound to the exact M15 reference source."""

    try:
        source_bytes = FRP_SOURCE_PATH.read_bytes()
    except OSError as exc:
        raise FRPAdapterError(
            f"unable to read FRP source: {FRP_SOURCE_PATH}"
        ) from exc

    digest = sha256_hex(source_bytes)

    if digest != EXPECTED_FRP_SOURCE_SHA256:
        raise FRPAdapterError(
            "frp_prototype_v1_7_0.py SHA-256 mismatch: "
            f"expected {EXPECTED_FRP_SOURCE_SHA256}, got {digest}"
        )

    return digest


FRP_SOURCE_SHA256 = verify_frp_source()

if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from frp_prototype_v1_7_0 import (  # noqa: E402
    DEFAULT_AMBIENT_HEAT,
    DEFAULT_COUPLING_NOMINAL,
    DEFAULT_DELAY_ALPHA,
    DEFAULT_FRACTAL_ALPHA,
    DEFAULT_GAMMA,
    DEFAULT_SEED,
    DEFAULT_THERMAL_BETA,
    DEFAULT_THERMAL_DIFFUSION_GAIN,
    DEFAULT_THERMAL_HARD_LIMIT,
    DEFAULT_THERMAL_SOFT_LIMIT,
    DEFAULT_THERMAL_TIME_CONSTANT,
    DEFAULT_TRANSITION_FRACTION,
    MILESTONE,
    Q30_SCALE,
    TERNARY_STATES,
    VERSION,
    QuantizedReferenceShadowProcessor,
    dequantize_q16,
    dequantize_q30,
    state_to_code,
)


if VERSION != "1.7.0":
    raise FRPAdapterError(
        f"unexpected FRP reference version: {VERSION}"
    )


def _percentile_nearest_rank(
    values: Sequence[int],
    percentile: float,
) -> float:
    if not values:
        return 0.0

    if not 0.0 < percentile <= 1.0:
        raise FRPAdapterError(
            "percentile must satisfy 0 < percentile <= 1"
        )

    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return float(ordered[rank - 1])


def _load_workload_package(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8")
        )
    except OSError as exc:
        raise FRPAdapterError(
            f"unable to read workload package: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise FRPAdapterError(
            f"invalid workload package JSON: {path}"
        ) from exc

    if not isinstance(value, dict):
        raise FRPAdapterError(
            "workload package JSON must contain an object"
        )

    validate_workload_package(value)
    return value


def _write_json(
    path: Path,
    value: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    )

    path.write_text(
        text + "\n",
        encoding="utf-8",
    )


def _encoded_bit_toggle_count(
    state_before: int,
    state_after: int,
) -> int:
    before_code = state_to_code(state_before)
    after_code = state_to_code(state_after)
    return (before_code ^ after_code).bit_count()


def _static_algorithmic_operation_counts(
    *,
    cells: int,
    hierarchy_depth: int,
) -> dict[str, int]:
    """Return declared per-cycle M15 algorithmic primitive counts.

    The profile counts architecture-level operations in the current M15
    quantized shadow path. It does not count Python interpreter instructions,
    helper-internal saturation branches, memory allocation, or host runtime
    overhead.
    """

    pair_count = cells * (cells - 1)

    return {
        "lut_reads_32": (
            pair_count
            + 2 * cells * (1 + hierarchy_depth)
            + cells
            + 1
        ),
        "fixed_point_multiplies_32x32": (
            4 * pair_count
            + 18 * cells
            + 8
        ),
        "fixed_point_accumulates_64": (
            2 * pair_count
            + 2 * cells * hierarchy_depth
            + 7 * cells
            - 2
        ),
        "fixed_point_adds_32": (
            2 * pair_count
            + 21 * cells
            + 7
        ),
        "fixed_point_compares_32": (
            7 * cells
            + 2
            - hierarchy_depth
        ),
    }


def _event_accounting_contract(
    *,
    cells: int,
    hierarchy_depth: int,
    request_lanes: int,
) -> dict[str, Any]:
    static_counts = _static_algorithmic_operation_counts(
        cells=cells,
        hierarchy_depth=hierarchy_depth,
    )

    return {
        "profile_name": EVENT_ACCOUNTING_PROFILE,
        "granularity": "M15 architecture-level algorithmic primitives",
        "excluded_from_counting": [
            "Python interpreter instructions",
            "helper-internal saturation branches",
            "host memory allocation",
            "host serialization",
            "host runtime overhead",
        ],
        "state_clock_model": "synchronous 2-bit ternary state domain",
        "clocked_state_bits_per_cycle": cells * STATE_BITS_PER_CELL,
        "state_register_write_bits_per_logical_change": STATE_BITS_PER_CELL,
        "request_lanes": request_lanes,
        "static_per_cycle_operation_counts": static_counts,
        "dynamic_event_rules": {
            "encoded_bit_toggles": (
                "2-bit Hamming distance between pre-tick and post-tick "
                "FRP state encodings"
            ),
            "logical_state_changes": (
                "count of cells whose ternary state changes during the tick"
            ),
            "queue_reads": (
                "pending neutral-route entries present at tick entry"
            ),
            "queue_writes": (
                "new M15 route_events with route_status=pending"
            ),
            "comparison_events": (
                "scheduler selection, request-lane normalization, valid "
                "request routing, pending-route control, queue-capacity "
                "control, and semantic completion checks"
            ),
            "control_events": "one M15 processor-cycle control event",
        },
    }


class FRPv170QuantizedShadowAdapter:
    """Benchmark adapter around the exact M15 quantized shadow processor."""

    def __init__(
        self,
        *,
        num_cells: int,
        scheduler: str = DEFAULT_FRP_SCHEDULER,
    ) -> None:
        self.processor = QuantizedReferenceShadowProcessor(
            cells=num_cells,
            transition_fraction=DEFAULT_TRANSITION_FRACTION,
            gamma_nominal=DEFAULT_GAMMA,
            scheduler=scheduler,
            seed=DEFAULT_SEED,
            fractal_alpha=DEFAULT_FRACTAL_ALPHA,
            thermal_beta=DEFAULT_THERMAL_BETA,
            ambient_heat=DEFAULT_AMBIENT_HEAT,
            thermal_time_constant=DEFAULT_THERMAL_TIME_CONSTANT,
            thermal_soft_limit=DEFAULT_THERMAL_SOFT_LIMIT,
            thermal_hard_limit=DEFAULT_THERMAL_HARD_LIMIT,
            coupling_nominal=DEFAULT_COUPLING_NOMINAL,
            delay_alpha=DEFAULT_DELAY_ALPHA,
            thermal_diffusion_gain=DEFAULT_THERMAL_DIFFUSION_GAIN,
        )

        self.num_cells = self.processor.cells
        self.scheduler = self.processor.scheduler
        self.initial_preload = self.processor.snapshot_preload()

        self.semantic_commands_issued = 0
        self.semantic_commands_completed = 0
        self.semantic_commands_matched = 0

        self.processor_cycles = 0
        self.active_clocked_cycles = 0
        self.logical_state_changes = 0
        self.encoded_bit_toggles = 0
        self.neutral_insertions = 0
        self.pending_route_peak = len(
            self.processor.pending_neutral_routes
        )

        self.cost_event_totals = empty_event_counts()
        self.cycle_trace: list[dict[str, Any]] = []
        self.command_trace: list[dict[str, Any]] = []
        self.command_latencies: list[int] = []

        self.static_operation_counts = (
            _static_algorithmic_operation_counts(
                cells=self.processor.cells,
                hierarchy_depth=self.processor.hierarchy_depth,
            )
        )

    def _target_state(
        self,
        semantic_target: str,
    ) -> int:
        try:
            return SEMANTIC_TO_FRP_STATE[
                semantic_target
            ]
        except KeyError as exc:
            raise FRPAdapterError(
                "unsupported semantic target: "
                f"{semantic_target}"
            ) from exc

    def _validate_cell_id(
        self,
        cell_id: int,
    ) -> None:
        if (
            isinstance(cell_id, bool)
            or not isinstance(cell_id, int)
        ):
            raise FRPAdapterError(
                "cell_id must be an integer"
            )

        if not 0 <= cell_id < self.num_cells:
            raise FRPAdapterError(
                "cell_id is outside the configured cell domain"
            )

    def _build_cycle_events(
        self,
        *,
        states_before: Sequence[int],
        states_after: Sequence[int],
        pending_before: int,
        valid_request_count: int,
        new_route_events: Sequence[Mapping[str, Any]],
        semantic_completion_check: bool,
    ) -> tuple[dict[str, int], int, int]:
        events = empty_event_counts()

        logical_changes = 0
        encoded_toggles = 0

        for before, after in zip(
            states_before,
            states_after,
        ):
            if before != after:
                logical_changes += 1
                encoded_toggles += (
                    _encoded_bit_toggle_count(
                        before,
                        after,
                    )
                )

        queue_writes = sum(
            1
            for row in new_route_events
            if row.get("route_status") == "pending"
        )

        events["encoded_bit_toggles"] = encoded_toggles
        events["clocked_state_bits"] = (
            self.num_cells
            * STATE_BITS_PER_CELL
        )
        events["register_write_bits"] = (
            logical_changes
            * STATE_BITS_PER_CELL
        )
        events["comparison_events"] = (
            2
            + 2 * self.processor.request_lanes
            + 4 * pending_before
            + 3 * valid_request_count
            + queue_writes
            + (1 if semantic_completion_check else 0)
        )
        events["control_events"] = 1
        events["queue_reads"] = pending_before
        events["queue_writes"] = queue_writes

        for event_field, count in (
            self.static_operation_counts.items()
        ):
            events[event_field] = count

        return (
            validate_event_counts(events),
            logical_changes,
            encoded_toggles,
        )

    def _execute_cycle(
        self,
        *,
        phase: str,
        requests: Sequence[tuple[bool, int, int]],
        command_index: int | None,
        cell_id: int | None,
        semantic_target: str | None,
        target_state: int | None,
        semantic_completion_check: bool,
    ) -> dict[str, Any]:
        states_before = list(
            self.processor.states
        )
        pending_before = len(
            self.processor.pending_neutral_routes
        )
        route_event_start = len(
            self.processor.route_events
        )
        neutral_routed_before = (
            self.processor.neutral_routed_events
        )

        valid_request_count = sum(
            1
            for valid, _, _ in requests
            if valid
        )

        tick_index = self.processor.tick_count

        m15_row = self.processor.tick(
            tick_index,
            requests=requests,
            auto_targets_enable=False,
        )

        states_after = list(
            self.processor.states
        )
        new_route_events = self.processor.route_events[
            route_event_start:
        ]

        (
            events,
            logical_changes,
            encoded_toggles,
        ) = self._build_cycle_events(
            states_before=states_before,
            states_after=states_after,
            pending_before=pending_before,
            valid_request_count=valid_request_count,
            new_route_events=new_route_events,
            semantic_completion_check=(
                semantic_completion_check
            ),
        )

        self.processor_cycles += 1
        self.active_clocked_cycles += 1
        self.logical_state_changes += (
            logical_changes
        )
        self.encoded_bit_toggles += (
            encoded_toggles
        )
        self.neutral_insertions += (
            self.processor.neutral_routed_events
            - neutral_routed_before
        )
        self.pending_route_peak = max(
            self.pending_route_peak,
            pending_before,
            len(
                self.processor.pending_neutral_routes
            ),
        )

        for event_field in EVENT_FIELDS:
            self.cost_event_totals[event_field] += (
                events[event_field]
            )

        cycle_row = {
            "cycle_index": self.processor_cycles - 1,
            "m15_tick": tick_index,
            "phase": phase,
            "command_index": command_index,
            "cell_id": cell_id,
            "semantic_target": semantic_target,
            "target_state": target_state,
            "states_before": states_before,
            "states_after": states_after,
            "logical_state_changes": logical_changes,
            "encoded_bit_toggles": encoded_toggles,
            "pending_route_count_before": pending_before,
            "pending_route_count_after": len(
                self.processor.pending_neutral_routes
            ),
            "new_route_events": [
                dict(row)
                for row in new_route_events
            ],
            "cost_events": events,
            "m15_trace_row": dict(m15_row),
        }

        self.cycle_trace.append(
            cycle_row
        )

        return cycle_row

    def execute_command(
        self,
        command: Mapping[str, Any],
        *,
        max_completion_cycles: int,
    ) -> None:
        if not isinstance(command, Mapping):
            raise FRPAdapterError(
                "command must be an object"
            )

        command_index = command.get(
            "command_index"
        )
        cell_id = command.get(
            "cell_id"
        )
        semantic_target = command.get(
            "semantic_target"
        )

        if (
            isinstance(command_index, bool)
            or not isinstance(command_index, int)
        ):
            raise FRPAdapterError(
                "command_index must be an integer"
            )

        self._validate_cell_id(
            cell_id
        )

        if (
            semantic_target
            not in SEMANTIC_TO_FRP_STATE
        ):
            raise FRPAdapterError(
                "invalid semantic target"
            )

        if (
            isinstance(
                max_completion_cycles,
                bool,
            )
            or not isinstance(
                max_completion_cycles,
                int,
            )
            or max_completion_cycles <= 0
        ):
            raise FRPAdapterError(
                "max_completion_cycles must be "
                "a positive integer"
            )

        self.semantic_commands_issued += 1

        target_state = self._target_state(
            semantic_target
        )

        start_cycle = self.processor_cycles
        state_before = self.processor.states[
            cell_id
        ]
        first_cycle = True
        semantic_complete = False

        while not semantic_complete:
            requests = (
                [
                    (
                        True,
                        cell_id,
                        target_state,
                    )
                ]
                if first_cycle
                else []
            )

            self._execute_cycle(
                phase="command",
                requests=requests,
                command_index=command_index,
                cell_id=cell_id,
                semantic_target=semantic_target,
                target_state=target_state,
                semantic_completion_check=True,
            )

            semantic_complete = (
                self.processor.states[
                    cell_id
                ]
                == target_state
            )

            latency_ticks = (
                self.processor_cycles
                - start_cycle
            )

            if (
                latency_ticks
                > max_completion_cycles
            ):
                raise FRPAdapterError(
                    "FRP command exceeded "
                    "max_completion_cycles"
                )

            first_cycle = False

        self.semantic_commands_completed += 1
        self.semantic_commands_matched += 1

        latency_ticks = (
            self.processor_cycles
            - start_cycle
        )

        self.command_latencies.append(
            latency_ticks
        )

        self.command_trace.append(
            {
                "command_index": command_index,
                "cell_id": cell_id,
                "semantic_target": semantic_target,
                "target_state": target_state,
                "issue_cycle": start_cycle,
                "completion_cycle": (
                    self.processor_cycles - 1
                ),
                "latency_ticks": latency_ticks,
                "state_before": state_before,
                "state_after": (
                    self.processor.states[
                        cell_id
                    ]
                ),
                "semantic_complete": True,
            }
        )

    def execute_cooldown(
        self,
        cycle_count: int,
    ) -> None:
        if (
            isinstance(cycle_count, bool)
            or not isinstance(cycle_count, int)
        ):
            raise FRPAdapterError(
                "cooldown cycle count must be an integer"
            )

        if cycle_count < 0:
            raise FRPAdapterError(
                "cooldown cycle count must be nonnegative"
            )

        for _ in range(cycle_count):
            self._execute_cycle(
                phase="cooldown",
                requests=[],
                command_index=None,
                cell_id=None,
                semantic_target=None,
                target_state=None,
                semantic_completion_check=False,
            )

    def build_result(
        self,
        *,
        workload_package: Mapping[str, Any],
    ) -> dict[str, Any]:
        issued = self.semantic_commands_issued
        completed = self.semantic_commands_completed

        semantic_completion_ratio = (
            completed / issued
            if issued
            else 0.0
        )

        semantic_output_match = (
            self.semantic_commands_matched
            / issued
            if issued
            else 0.0
        )

        mean_latency_ticks = (
            math.fsum(
                self.command_latencies
            )
            / len(
                self.command_latencies
            )
            if self.command_latencies
            else 0.0
        )

        p95_latency_ticks = (
            _percentile_nearest_rank(
                self.command_latencies,
                0.95,
            )
        )

        maximum_latency_ticks = (
            max(
                self.command_latencies
            )
            if self.command_latencies
            else 0
        )

        throughput_commands_per_tick = (
            completed
            / self.processor_cycles
            if self.processor_cycles
            else 0.0
        )

        active_clock_fraction = (
            self.active_clocked_cycles
            / self.processor_cycles
            if self.processor_cycles
            else 0.0
        )

        c_minus_p_values = [
            row["C_minus_P_q16"]
            for row in self.processor.trace
        ]

        final_m15_row = (
            self.processor.trace[-1]
            if self.processor.trace
            else None
        )

        raw_event_totals = {
            "semantic_commands_issued": issued,
            "semantic_commands_completed": completed,
            "processor_cycles": self.processor_cycles,
            "active_clocked_cycles": (
                self.active_clocked_cycles
            ),
            "logical_state_changes": (
                self.logical_state_changes
            ),
            **self.cost_event_totals,
        }

        digest_payload = {
            "schema": ARCHITECTURE_RESULT_SCHEMA,
            "suite_name": SUITE_NAME,
            "architecture_id": ARCHITECTURE_ID,
            "architecture_name": ARCHITECTURE_NAME,
            "frp_reference": {
                "version": VERSION,
                "milestone": MILESTONE,
                "source_file": "frp_prototype_v1_7_0.py",
                "source_sha256": FRP_SOURCE_SHA256,
                "processor_class": (
                    "QuantizedReferenceShadowProcessor"
                ),
                "execution_model": (
                    "stateful fixed-point feedback"
                ),
            },
            "state_domain": [
                -1,
                0,
                1,
            ],
            "state_encoding": {
                "-1": "2'b11",
                "0": "2'b00",
                "+1": "2'b01",
                "reserved": "2'b10",
            },
            "semantic_mapping": {
                NEGATIVE_TARGET: -1,
                POSITIVE_TARGET: 1,
            },
            "execution_profile": {
                "clock_model": "synchronous",
                "state_bits_per_cell": (
                    STATE_BITS_PER_CELL
                ),
                "scheduler": self.scheduler,
                "transition_fraction": (
                    self.processor.transition_fraction
                ),
                "request_lanes": (
                    self.processor.request_lanes
                ),
                "auto_targets_enable": False,
                "tick_separated_neutral_routing": True,
                "issue_policy": (
                    workload_package[
                        "workload_profile"
                    ]["issue_policy"]
                ),
                "cooldown_processor_cycles": (
                    workload_package[
                        "workload_profile"
                    ]["final_cooldown_cycles"]
                ),
            },
            "event_accounting_contract": (
                _event_accounting_contract(
                    cells=self.processor.cells,
                    hierarchy_depth=(
                        self.processor.hierarchy_depth
                    ),
                    request_lanes=(
                        self.processor.request_lanes
                    ),
                )
            ),
            "workload_sha256": (
                workload_package[
                    "workload_sha256"
                ]
            ),
            "workload_profile": (
                workload_package[
                    "workload_profile"
                ]
            ),
            "initial_preload": (
                self.initial_preload
            ),
            "raw_event_totals": (
                raw_event_totals
            ),
            "architecture_specific_metrics": {
                "requested_direct_events": (
                    self.processor.requested_direct_events
                ),
                "prevented_direct_events": (
                    self.processor.prevented_direct_events
                ),
                "actual_direct_events": (
                    self.processor.actual_direct_events
                ),
                "neutral_routed_events": (
                    self.processor.neutral_routed_events
                ),
                "neutralized_conflicts": (
                    self.processor.neutralized_conflicts
                ),
                "neutral_insertions": (
                    self.neutral_insertions
                ),
                "pending_route_peak": (
                    self.pending_route_peak
                ),
                "pending_route_count_final": len(
                    self.processor.pending_neutral_routes
                ),
                "queue_overflow_events": (
                    self.processor.queue_overflow_events
                ),
                "reserved_state_events": (
                    self.processor.reserved_state_events
                ),
                "C_minus_P_min_q16": (
                    min(c_minus_p_values)
                    if c_minus_p_values
                    else self.processor.C_minus_P_q16
                ),
                "C_minus_P_min": (
                    dequantize_q16(
                        min(c_minus_p_values)
                        if c_minus_p_values
                        else self.processor.C_minus_P_q16
                    )
                ),
                "C_minus_P_final_q16": (
                    self.processor.C_minus_P_q16
                ),
                "C_minus_P_final": (
                    dequantize_q16(
                        self.processor.C_minus_P_q16
                    )
                ),
                "global_phase_coherence_final_q30": (
                    final_m15_row[
                        "global_phase_coherence_q30"
                    ]
                    if final_m15_row
                    else self.processor.raw_phase_coherence_q30
                ),
                "global_phase_coherence_final": (
                    dequantize_q30(
                        final_m15_row[
                            "global_phase_coherence_q30"
                        ]
                        if final_m15_row
                        else self.processor.raw_phase_coherence_q30
                    )
                ),
                "fixed_point_topology_sum_exact": (
                    sum(
                        (1 << (distance - 1))
                        * self.processor.phase_pair_weights_q30[
                            distance
                        ]
                        for distance in (
                            self.processor.phase_pair_weights_q30
                        )
                    )
                    == Q30_SCALE
                ),
                "fixed_point_thermal_sum_exact": (
                    sum(
                        (1 << (distance - 1))
                        * self.processor.thermal_pair_weights_q30[
                            distance
                        ]
                        for distance in (
                            self.processor.thermal_pair_weights_q30
                        )
                    )
                    == Q30_SCALE
                ),
            },
            "comparison_metrics": {
                "semantic_completion_ratio": (
                    semantic_completion_ratio
                ),
                "semantic_output_match": (
                    semantic_output_match
                ),
                "completion_ticks": (
                    self.processor_cycles
                ),
                "mean_latency_ticks": (
                    mean_latency_ticks
                ),
                "p95_latency_ticks": (
                    p95_latency_ticks
                ),
                "maximum_latency_ticks": (
                    maximum_latency_ticks
                ),
                "throughput_commands_per_tick": (
                    throughput_commands_per_tick
                ),
                "logical_state_changes": (
                    self.logical_state_changes
                ),
                "encoded_bit_toggles": (
                    self.encoded_bit_toggles
                ),
                "processor_cycles": (
                    self.processor_cycles
                ),
                "active_clocked_cycles": (
                    self.active_clocked_cycles
                ),
                "active_clock_fraction": (
                    active_clock_fraction
                ),
            },
            "final_state": {
                "ternary_states": list(
                    self.processor.states
                ),
                "states_packed_hex": (
                    final_m15_row[
                        "states_packed_hex"
                    ]
                    if final_m15_row
                    else None
                ),
            },
            "command_trace": (
                self.command_trace
            ),
            "cycle_trace": (
                self.cycle_trace
            ),
        }

        result = dict(
            digest_payload
        )

        result[
            "architecture_result_sha256"
        ] = sha256_hex(
            canonical_json_bytes(
                digest_payload
            )
        )

        return result


def execute_frp_v1_7_0_adapter(
    workload_package: Mapping[str, Any],
    *,
    scheduler: str = DEFAULT_FRP_SCHEDULER,
) -> dict[str, Any]:
    """Execute one semantic workload through the exact M15 shadow path."""

    validate_workload_package(
        workload_package
    )

    profile = workload_package[
        "workload_profile"
    ]

    if (
        profile["issue_policy"]
        != ISSUE_POLICY_TRANSACTION_SERIAL
    ):
        raise FRPAdapterError(
            "FRP v1.7.0 adapter requires transaction_serial"
        )

    adapter = FRPv170QuantizedShadowAdapter(
        num_cells=profile[
            "num_cells"
        ],
        scheduler=scheduler,
    )

    for command in workload_package[
        "commands"
    ]:
        adapter.execute_command(
            command,
            max_completion_cycles=(
                profile[
                    "max_completion_cycles_per_command"
                ]
            ),
        )

    adapter.execute_cooldown(
        profile[
            "final_cooldown_cycles"
        ]
    )

    if adapter.processor.pending_neutral_routes:
        raise FRPAdapterError(
            "pending neutral routes remain after completed workload"
        )

    return adapter.build_result(
        workload_package=workload_package
    )


def _raises_adapter_error(
    callback: Any,
) -> bool:
    try:
        callback()
    except FRPAdapterError:
        return True

    return False


def run_self_test() -> dict[str, Any]:
    workload = build_workload_package(
        WorkloadProfile()
    )

    result_a = execute_frp_v1_7_0_adapter(
        workload
    )

    result_b = execute_frp_v1_7_0_adapter(
        workload
    )

    metrics = result_a[
        "comparison_metrics"
    ]
    raw = result_a[
        "raw_event_totals"
    ]
    specific = result_a[
        "architecture_specific_metrics"
    ]

    command_count = workload[
        "workload_profile"
    ]["command_count"]

    cooldown_cycles = workload[
        "workload_profile"
    ]["final_cooldown_cycles"]

    num_cells = workload[
        "workload_profile"
    ]["num_cells"]

    cycle_event_totals = empty_event_counts()

    for row in result_a[
        "cycle_trace"
    ]:
        for event_field in EVENT_FIELDS:
            cycle_event_totals[event_field] += (
                row[
                    "cost_events"
                ][event_field]
            )

    invalid_target_command = {
        "command_index": 0,
        "cell_id": 0,
        "semantic_target": "INVALID_TARGET",
    }

    invalid_cell_command = {
        "command_index": 0,
        "cell_id": num_cells,
        "semantic_target": NEGATIVE_TARGET,
    }

    probe = FRPv170QuantizedShadowAdapter(
        num_cells=num_cells
    )

    checks = {
        "frp_source_digest_bound": (
            FRP_SOURCE_SHA256
            == EXPECTED_FRP_SOURCE_SHA256
        ),
        "frp_version_correct": (
            result_a[
                "frp_reference"
            ]["version"]
            == "1.7.0"
        ),
        "architecture_id_correct": (
            result_a[
                "architecture_id"
            ]
            == ARCHITECTURE_ID
        ),
        "exact_processor_class_used": (
            result_a[
                "frp_reference"
            ]["processor_class"]
            == "QuantizedReferenceShadowProcessor"
        ),
        "workload_digest_preserved": (
            result_a[
                "workload_sha256"
            ]
            == workload[
                "workload_sha256"
            ]
        ),
        "all_commands_issued": (
            raw[
                "semantic_commands_issued"
            ]
            == command_count
        ),
        "all_commands_completed": (
            raw[
                "semantic_commands_completed"
            ]
            == command_count
        ),
        "semantic_completion_ratio_one": (
            metrics[
                "semantic_completion_ratio"
            ]
            == 1.0
        ),
        "semantic_output_match_one": (
            metrics[
                "semantic_output_match"
            ]
            == 1.0
        ),
        "actual_direct_events_zero": (
            specific[
                "actual_direct_events"
            ]
            == 0
        ),
        "reserved_state_events_zero": (
            specific[
                "reserved_state_events"
            ]
            == 0
        ),
        "queue_overflow_events_zero": (
            specific[
                "queue_overflow_events"
            ]
            == 0
        ),
        "pending_routes_empty_final": (
            specific[
                "pending_route_count_final"
            ]
            == 0
        ),
        "requested_direct_events_prevented": (
            specific[
                "requested_direct_events"
            ]
            == specific[
                "prevented_direct_events"
            ]
        ),
        "neutral_insertions_match_routes": (
            specific[
                "neutral_insertions"
            ]
            == specific[
                "neutral_routed_events"
            ]
        ),
        "tick_separated_latency_visible": (
            metrics[
                "maximum_latency_ticks"
            ]
            == 2
        ),
        "minimum_completion_ticks_respected": (
            metrics[
                "completion_ticks"
            ]
            >= command_count
            + cooldown_cycles
        ),
        "m15_tick_count_matches_adapter": (
            len(
                result_a[
                    "cycle_trace"
                ]
            )
            == raw[
                "processor_cycles"
            ]
        ),
        "globally_active_processor_cycles": (
            raw[
                "active_clocked_cycles"
            ]
            == raw[
                "processor_cycles"
            ]
            and metrics[
                "active_clock_fraction"
            ]
            == 1.0
        ),
        "clocked_state_bits_exact": (
            raw[
                "clocked_state_bits"
            ]
            == raw[
                "processor_cycles"
            ]
            * num_cells
            * STATE_BITS_PER_CELL
        ),
        "register_write_bits_match_changes": (
            raw[
                "register_write_bits"
            ]
            == raw[
                "logical_state_changes"
            ]
            * STATE_BITS_PER_CELL
        ),
        "encoded_toggle_trace_closure": (
            sum(
                row[
                    "encoded_bit_toggles"
                ]
                for row in result_a[
                    "cycle_trace"
                ]
            )
            == raw[
                "encoded_bit_toggles"
            ]
        ),
        "cost_event_trace_closure": (
            cycle_event_totals
            == {
                event_field: raw[
                    event_field
                ]
                for event_field in EVENT_FIELDS
            }
        ),
        "lut_overhead_recorded": (
            raw[
                "lut_reads_32"
            ]
            > 0
        ),
        "fixed_point_multiply_overhead_recorded": (
            raw[
                "fixed_point_multiplies_32x32"
            ]
            > 0
        ),
        "fixed_point_accumulate_overhead_recorded": (
            raw[
                "fixed_point_accumulates_64"
            ]
            > 0
        ),
        "fixed_point_add_overhead_recorded": (
            raw[
                "fixed_point_adds_32"
            ]
            > 0
        ),
        "fixed_point_compare_overhead_recorded": (
            raw[
                "fixed_point_compares_32"
            ]
            > 0
        ),
        "fixed_point_topology_sum_exact": (
            specific[
                "fixed_point_topology_sum_exact"
            ]
        ),
        "fixed_point_thermal_sum_exact": (
            specific[
                "fixed_point_thermal_sum_exact"
            ]
        ),
        "final_state_domain_valid": all(
            state in TERNARY_STATES
            for state in result_a[
                "final_state"
            ]["ternary_states"]
        ),
        "command_trace_length_exact": (
            len(
                result_a[
                    "command_trace"
                ]
            )
            == command_count
        ),
        "deterministic_result_digest_repeat": (
            result_a[
                "architecture_result_sha256"
            ]
            == result_b[
                "architecture_result_sha256"
            ]
        ),
        "deterministic_result_byte_repeat": (
            canonical_json_bytes(
                result_a
            )
            == canonical_json_bytes(
                result_b
            )
        ),
        "invalid_target_rejected": (
            _raises_adapter_error(
                lambda: probe.execute_command(
                    invalid_target_command,
                    max_completion_cycles=64,
                )
            )
        ),
        "invalid_cell_rejected": (
            _raises_adapter_error(
                lambda: probe.execute_command(
                    invalid_cell_command,
                    max_completion_cycles=64,
                )
            )
        ),
    }

    status = (
        "PASS"
        if all(checks.values())
        else "FAIL"
    )

    return {
        "schema": ARCHITECTURE_SELF_TEST_SCHEMA,
        "status": status,
        "check_count": len(checks),
        "checks": checks,
        "workload_sha256": (
            workload[
                "workload_sha256"
            ]
        ),
        "frp_source_sha256": (
            FRP_SOURCE_SHA256
        ),
        "architecture_result_sha256": (
            result_a[
                "architecture_result_sha256"
            ]
        ),
        "summary": {
            "command_count": command_count,
            "completion_ticks": (
                metrics[
                    "completion_ticks"
                ]
            ),
            "mean_latency_ticks": (
                metrics[
                    "mean_latency_ticks"
                ]
            ),
            "p95_latency_ticks": (
                metrics[
                    "p95_latency_ticks"
                ]
            ),
            "maximum_latency_ticks": (
                metrics[
                    "maximum_latency_ticks"
                ]
            ),
            "logical_state_changes": (
                raw[
                    "logical_state_changes"
                ]
            ),
            "encoded_bit_toggles": (
                raw[
                    "encoded_bit_toggles"
                ]
            ),
            "requested_direct_events": (
                specific[
                    "requested_direct_events"
                ]
            ),
            "prevented_direct_events": (
                specific[
                    "prevented_direct_events"
                ]
            ),
            "actual_direct_events": (
                specific[
                    "actual_direct_events"
                ]
            ),
            "neutral_routed_events": (
                specific[
                    "neutral_routed_events"
                ]
            ),
            "neutral_insertions": (
                specific[
                    "neutral_insertions"
                ]
            ),
            "pending_route_peak": (
                specific[
                    "pending_route_peak"
                ]
            ),
            "clocked_state_bits": (
                raw[
                    "clocked_state_bits"
                ]
            ),
            "lut_reads_32": (
                raw[
                    "lut_reads_32"
                ]
            ),
            "fixed_point_multiplies_32x32": (
                raw[
                    "fixed_point_multiplies_32x32"
                ]
            ),
            "C_minus_P_min": (
                specific[
                    "C_minus_P_min"
                ]
            ),
            "C_minus_P_final": (
                specific[
                    "C_minus_P_final"
                ]
            ),
            "global_phase_coherence_final": (
                specific[
                    "global_phase_coherence_final"
                ]
            ),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Execute the FRP v1.7.0 M15 Quantized "
            "Hardware Shadow Reference for the FRP "
            "Comparative Architecture Benchmark Suite."
        )
    )

    parser.add_argument(
        "--workload",
        type=Path,
        help=(
            "Optional validated semantic workload "
            "JSON package. The default workload "
            "profile is used when omitted."
        ),
    )

    parser.add_argument(
        "--scheduler",
        choices=(
            "free",
            "7/1",
            "1/7",
        ),
        default=DEFAULT_FRP_SCHEDULER,
        help="M15 scheduler mode.",
    )

    parser.add_argument(
        "--write",
        type=Path,
        help=(
            "Optional path for the architecture "
            "result JSON."
        ),
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "Run FRP v1.7.0 adapter self-tests."
        ),
    )

    parser.add_argument(
        "--output",
        choices=(
            "json",
            "text",
        ),
        default="json",
        help="Output format.",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.self_test:
            result = run_self_test()

        else:
            workload = (
                _load_workload_package(
                    args.workload
                )
                if args.workload
                else build_workload_package(
                    WorkloadProfile()
                )
            )

            result = execute_frp_v1_7_0_adapter(
                workload,
                scheduler=args.scheduler,
            )

        if args.write:
            _write_json(
                args.write,
                result,
            )

        if args.output == "json":
            print(
                json.dumps(
                    result,
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                    allow_nan=False,
                )
            )

        else:
            if args.self_test:
                print(
                    "FRP COMPARATIVE V1.7.0 M15 "
                    "QUANTIZED SHADOW ADAPTER SELF TEST"
                )

                print(
                    f"status={result['status']}"
                )

                print(
                    f"checks={result['check_count']}"
                )

                print(
                    "workload_sha256="
                    f"{result['workload_sha256']}"
                )

                print(
                    "frp_source_sha256="
                    f"{result['frp_source_sha256']}"
                )

                print(
                    "architecture_result_sha256="
                    f"{result['architecture_result_sha256']}"
                )

            else:
                metrics = result[
                    "comparison_metrics"
                ]
                raw = result[
                    "raw_event_totals"
                ]
                specific = result[
                    "architecture_specific_metrics"
                ]

                print(
                    "FRP COMPARATIVE V1.7.0 M15 "
                    "QUANTIZED SHADOW REFERENCE"
                )

                print(
                    "architecture_id="
                    f"{result['architecture_id']}"
                )

                print(
                    "workload_sha256="
                    f"{result['workload_sha256']}"
                )

                print(
                    "frp_source_sha256="
                    f"{result['frp_reference']['source_sha256']}"
                )

                print(
                    "completion_ticks="
                    f"{metrics['completion_ticks']}"
                )

                print(
                    "semantic_output_match="
                    f"{metrics['semantic_output_match']}"
                )

                print(
                    "actual_direct_events="
                    f"{specific['actual_direct_events']}"
                )

                print(
                    "neutral_routed_events="
                    f"{specific['neutral_routed_events']}"
                )

                print(
                    "C_minus_P_min="
                    f"{specific['C_minus_P_min']}"
                )

                print(
                    "lut_reads_32="
                    f"{raw['lut_reads_32']}"
                )

                print(
                    "fixed_point_multiplies_32x32="
                    f"{raw['fixed_point_multiplies_32x32']}"
                )

        return (
            0
            if (
                not args.self_test
                or result["status"] == "PASS"
            )
            else 1
        )

    except (
        FRPAdapterError,
        CostModelError,
        WorkloadError,
        ValueError,
        IndexError,
    ) as exc:
        raise SystemExit(
            "FRP v1.7.0 adapter error: "
            f"{exc}"
        ) from exc


if __name__ == "__main__":
    raise SystemExit(main())
