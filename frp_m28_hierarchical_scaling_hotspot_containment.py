#!/usr/bin/env python3
"""FRP M28 hierarchical scaling and hotspot-containment realization."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence

from jsonschema.validators import validator_for

import frp_prototype_v1_7_0 as core


VERSION = "3.0.0"
MILESTONE = "M28"
MILESTONE_TITLE = "M28 - Hierarchical Scaling and Hotspot-Containment Realization"
RELEASE = "FRP v3.0.0"
EXPECTED_M27_COMMIT = "23e464206f85cd9473101d9221027ee33d9dd094"
EXPECTED_M27_SUBJECT = "Add M27 long-run stability and telemetry qualification"
M28_OBSERVATORY_COMMIT = "566a4ff88baa57f844691b46937552253e095434"
M28_OBSERVATORY_SUBJECT = "Add M28 Trace Observatory upstream interchange"
WORKFLOW_PATH = (
    ".github/workflows/"
    "frp-m28-hierarchical-scaling-hotspot-containment-closure-workflow.yml"
)

PROTOTYPE_PATH = "frp_prototype_v1_7_0.py"
M27_CHECKPOINT_PATH = (
    "artifacts/m27/checkpoints/m27-long-run-checkpoint-evidence.json"
)
M27_CONTRACT_PATH = "artifacts/m27/contracts/m27-long-run-telemetry-contract.json"
M14_QUALIFICATION_PATH = "docs/m14_physical_implementation_correlation_production_qualification.md"

SCALING_CELLS = (8, 16, 32)
TEMPORAL_SCHEDULERS = ("1/7", "7/1")
SERVICE_SCHEDULER = "free"
ALL_SCHEDULERS = (SERVICE_SCHEDULER,) + TEMPORAL_SCHEDULERS
CLUSTER_SIZE = 4
SCALING_STEPS = 256
SCALING_CHECKPOINT_INTERVAL = 32
HOTSPOT_STRESS_TICKS = 72
HOTSPOT_RECOVERY_TICKS = 96
HOTSPOT_PROPAGATION_LIMIT = 0.75
HOTSPOT_REMOTE_PROPAGATION_LIMIT = 0.70

CONTRACT_SCHEMA_ID = "frp.m28.hierarchical_scaling_contract.v3.0.0"
TOPOLOGY_SCHEMA_ID = "frp.m28.hierarchy_topology_manifest.v3.0.0"
SCALING_SCHEMA_ID = "frp.m28.hierarchical_scaling_matrix.v3.0.0"
HOTSPOT_SCHEMA_ID = "frp.m28.hotspot_containment_evidence.v3.0.0"
QUALIFICATION_SCHEMA_ID = "frp.m28.hierarchy_qualification.v3.0.0"

SCHEMA_PATHS = {
    CONTRACT_SCHEMA_ID: (
        "schemas/m28/frp_m28_hierarchical_scaling_contract.v3.0.0.schema.json"
    ),
    TOPOLOGY_SCHEMA_ID: (
        "schemas/m28/frp_m28_hierarchy_topology_manifest.v3.0.0.schema.json"
    ),
    SCALING_SCHEMA_ID: (
        "schemas/m28/frp_m28_hierarchical_scaling_matrix.v3.0.0.schema.json"
    ),
    HOTSPOT_SCHEMA_ID: (
        "schemas/m28/frp_m28_hotspot_containment_evidence.v3.0.0.schema.json"
    ),
    QUALIFICATION_SCHEMA_ID: (
        "schemas/m28/frp_m28_hierarchy_qualification.v3.0.0.schema.json"
    ),
}
SCHEMA_REGISTRY_PATH = "schemas/m28/frp_m28_hierarchy_schema_registry.json"

CONTRACT_ARTIFACT = (
    "artifacts/m28/hierarchy/contracts/m28-hierarchical-scaling-contract.json"
)
TOPOLOGY_ARTIFACT = (
    "artifacts/m28/hierarchy/topology/m28-hierarchy-topology-manifest.json"
)
SCALING_ARTIFACT = (
    "artifacts/m28/hierarchy/scaling/m28-hierarchical-scaling-matrix.json"
)
HOTSPOT_ARTIFACT = (
    "artifacts/m28/hierarchy/containment/m28-hotspot-containment-evidence.json"
)
QUALIFICATION_ARTIFACT = (
    "artifacts/m28/hierarchy/manifests/m28-hierarchy-qualification.json"
)

ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    TOPOLOGY_ARTIFACT,
    SCALING_ARTIFACT,
    HOTSPOT_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)
GENERATED_PATHS = tuple(SCHEMA_PATHS.values()) + (
    SCHEMA_REGISTRY_PATH,
) + ARTIFACT_PATHS

REQUIRED_SCOPE = (
    "declared_hierarchy_topology",
    "cluster_identities",
    "cell_to_cluster_mapping",
    "cluster_local_scheduler_observation",
    "cluster_local_transition_capacity_observation",
    "cluster_local_telemetry",
    "hotspot_containment_indicators",
    "hierarchy_level_provenance",
    "deterministic_scaling_matrices",
    "explicit_aggregation_equations",
    "machine_readable_hierarchy_manifests",
)


class ContractError(ValueError):
    """Raised when an M28 hierarchy contract is violated."""


class SafetyError(ValueError):
    """Raised when a repository path is unsafe."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise SafetyError("path must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise SafetyError(f"unsafe repository path: {value!r}")
    return path


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def attach_digest(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result.pop(field, None)
    result[field] = object_digest(result)
    return result


def validate_attached_digest(value: dict[str, Any], field: str) -> None:
    observed = value.get(field)
    base = copy.deepcopy(value)
    base.pop(field, None)
    expected = object_digest(base)
    if observed != expected:
        raise ContractError(f"{field} mismatch: {observed!r} != {expected!r}")


def load_json(root: Path, relative: str) -> Any:
    safe = safe_relative_path(relative)
    return json.loads(root.joinpath(*safe.parts).read_text(encoding="utf-8"))


def write_json(root: Path, relative: str, value: Any) -> None:
    safe = safe_relative_path(relative)
    destination = root.joinpath(*safe.parts)
    if destination.exists() and destination.is_symlink():
        raise SafetyError(f"refusing symlink destination: {relative}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_bytes(canonical_json_bytes(value))
    os.replace(temporary, destination)


def source_record(root: Path, relative: str, role: str) -> dict[str, Any]:
    safe = safe_relative_path(relative)
    path = root.joinpath(*safe.parts)
    if not path.is_file() or path.is_symlink():
        raise ContractError(f"missing immutable source: {relative}")
    return {
        "path": relative,
        "role": role,
        "bytes": path.stat().st_size,
        "raw_sha256": raw_sha256(path),
    }


def validate_source_commit(value: str) -> None:
    if value != EXPECTED_M27_COMMIT:
        raise ContractError("M28 hierarchy source commit is not the exact M27 closure")


def schema_document(schema_id: str, kind: str, required: Sequence[str]) -> dict[str, Any]:
    properties: dict[str, Any] = {
        "schema": {"const": schema_id},
        "kind": {"const": kind},
        "version": {"const": VERSION},
        "milestone": {"const": MILESTONE},
        "status": {"const": "PASS"},
        "source_commit": {"const": EXPECTED_M27_COMMIT},
    }
    for field in required:
        properties.setdefault(field, {})
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "title": kind,
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(required),
    }


def build_schemas() -> dict[str, dict[str, Any]]:
    return {
        CONTRACT_SCHEMA_ID: schema_document(
            CONTRACT_SCHEMA_ID,
            "hierarchical_scaling_contract",
            (
                "schema", "kind", "version", "milestone", "status",
                "source_commit", "release", "milestone_title", "objective",
                "required_scope", "immutable_core", "hierarchy_boundary",
                "aggregation_equations", "provenance_boundary",
                "measurement_boundary", "contract_digest",
            ),
        ),
        TOPOLOGY_SCHEMA_ID: schema_document(
            TOPOLOGY_SCHEMA_ID,
            "hierarchy_topology_manifest",
            (
                "schema", "kind", "version", "milestone", "status",
                "source_commit", "profile_count", "profiles", "source_records",
                "topology_set_digest", "manifest_digest",
            ),
        ),
        SCALING_SCHEMA_ID: schema_document(
            SCALING_SCHEMA_ID,
            "hierarchical_scaling_matrix",
            (
                "schema", "kind", "version", "milestone", "status",
                "source_commit", "profile_count", "cell_profiles",
                "temporal_scheduler_modes", "service_scheduler_mode",
                "aggregation_equations", "profile_set_digest", "matrix_digest",
            ),
        ),
        HOTSPOT_SCHEMA_ID: schema_document(
            HOTSPOT_SCHEMA_ID,
            "hotspot_containment_evidence",
            (
                "schema", "kind", "version", "milestone", "status",
                "source_commit", "profile_count", "profiles", "limits",
                "profile_set_digest", "evidence_digest",
            ),
        ),
        QUALIFICATION_SCHEMA_ID: schema_document(
            QUALIFICATION_SCHEMA_ID,
            "hierarchy_qualification",
            (
                "schema", "kind", "version", "milestone", "status",
                "source_commit", "qualification_id", "check_count",
                "passed_count", "failed_count", "checks", "artifacts",
                "schemas", "qualification_digest",
            ),
        ),
    }


def validate_json_schema(instance: Any, schema: dict[str, Any]) -> None:
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    errors = sorted(validator_type(schema).iter_errors(instance), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise ContractError(f"JSON Schema validation failed at {location}: {first.message}")


def build_contract() -> dict[str, Any]:
    value = {
        "schema": CONTRACT_SCHEMA_ID,
        "kind": "hierarchical_scaling_contract",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": EXPECTED_M27_COMMIT,
        "release": RELEASE,
        "milestone_title": MILESTONE_TITLE,
        "objective": (
            "realize and qualify declared hierarchical execution and "
            "containment boundaries"
        ),
        "required_scope": list(REQUIRED_SCOPE),
        "immutable_core": {
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "opposite_transition_routes": [[-1, 0, 1], [1, 0, -1]],
            "temporal_scheduler_modes": list(TEMPORAL_SCHEDULERS),
            "service_scheduler_mode": SERVICE_SCHEDULER,
            "actual_direct_events_target": 0,
            "reserved_state_events_target": 0,
            "queue_overflow_events_target": 0,
        },
        "hierarchy_boundary": {
            "topology": "dyadic_ultrametric_contiguous_domains",
            "qualified_cell_counts": list(SCALING_CELLS),
            "cluster_size_cells": CLUSTER_SIZE,
            "hierarchy_depth_relation": "log2(cells)",
            "hierarchy_distance_relation": "bit_length(cell_i XOR cell_j)",
            "shell_population_relation": "2^(distance-1)",
            "execution_path": "hierarchical_reference",
            "declared_interaction_scaling": "O(N log N)",
        },
        "aggregation_equations": {
            "cluster_state_count": "count(state == value for state in cluster)",
            "cluster_heat_mean": "sum(cell_heat_q16) // cluster_cell_count",
            "cluster_heat_peak": "max(cell_heat_q16)",
            "cluster_switch_changes": "sum(cell_switch_activity)",
            "cluster_switch_load_q16": (
                "round(cluster_switch_changes * 65536 / cluster_cell_count)"
            ),
            "cluster_pressure_q16": "cluster_heat_mean_q16 + cluster_switch_load_q16",
            "global_from_cluster_count": "sum(cluster_count)",
            "no_undeclared_metric_aggregation": True,
        },
        "provenance_boundary": {
            "semantic_authority": PROTOTYPE_PATH,
            "long_run_source": M27_CHECKPOINT_PATH,
            "long_run_contract": M27_CONTRACT_PATH,
            "prior_hierarchy_qualification": M14_QUALIFICATION_PATH,
            "observatory_interchange_commit": M28_OBSERVATORY_COMMIT,
            "observatory_interchange_role": "additional_publication_layer",
            "hierarchy_role": "primary_M28_realization",
        },
        "measurement_boundary": {
            "cluster_telemetry": "model_derived_dimensionless_proxy",
            "physical_measurement_status": "not_a_physical_measurement",
            "proxy_to_physical_conversion": "prohibited",
            "measurement_contours": [
                "hierarchical_scaling",
                "localized_hotspot_containment",
                "m27_long_run_telemetry",
                "m28_observatory_publication_interchange",
            ],
            "measurement_contours_remain_separate": True,
            "universal_physical_chip_claim": "not_made",
        },
    }
    return attach_digest(value, "contract_digest")


def _domain_role(level: int, depth: int) -> str:
    if level == 0:
        return "individual_cell"
    if level == 1:
        return "pair_domain"
    if level == 2:
        return "local_cluster"
    if level == depth:
        return "global_cell_domain"
    return f"supercluster_level_{level - 2}"


def _domains(cells: int, level: int) -> list[dict[str, Any]]:
    size = 1 << level
    result = []
    for index, start in enumerate(range(0, cells, size)):
        cell_ids = list(range(start, start + size))
        result.append(
            {
                "domain_id": f"N{cells}-L{level}-D{index}",
                "domain_index": index,
                "cell_ids": cell_ids,
                "cell_start": cell_ids[0],
                "cell_end": cell_ids[-1],
                "cell_count": len(cell_ids),
            }
        )
    return result


def _core_args(scheduler: str = "7/1") -> argparse.Namespace:
    args = core.build_parser().parse_args([])
    args.scheduler = scheduler
    args.seed = core.DEFAULT_SEED
    args.transition_fraction = core.DEFAULT_TRANSITION_FRACTION
    args.gamma = core.DEFAULT_GAMMA
    args.fractal_alpha = core.DEFAULT_FRACTAL_ALPHA
    args.thermal_beta = core.DEFAULT_THERMAL_BETA
    return args


def _round_value(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, list):
        return [_round_value(item) for item in value]
    if isinstance(value, tuple):
        return [_round_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _round_value(item) for key, item in value.items()}
    return value


def build_topology_manifest(root: Path) -> dict[str, Any]:
    profiles = []
    for cells in SCALING_CELLS:
        args = _core_args()
        processor = core.make_processor(args, cells=cells, scheduler="7/1")
        depth = processor.hierarchy_depth
        levels = [
            {
                "level": level,
                "role": _domain_role(level, depth),
                "domain_size": 1 << level,
                "domain_count": cells // (1 << level),
                "domains": _domains(cells, level),
            }
            for level in range(depth + 1)
        ]
        clusters = _domains(cells, 2)
        cluster_records = [
            {
                "cluster_id": f"N{cells}-C{item['domain_index']}",
                "cluster_index": item["domain_index"],
                "cell_ids": item["cell_ids"],
                "cell_start": item["cell_start"],
                "cell_end": item["cell_end"],
                "cell_count": item["cell_count"],
            }
            for item in clusters
        ]
        mapping = [
            {
                "cell_id": cell_id,
                "cluster_id": f"N{cells}-C{cell_id // CLUSTER_SIZE}",
                "cluster_index": cell_id // CLUSTER_SIZE,
                "cluster_offset": cell_id % CLUSTER_SIZE,
            }
            for cell_id in range(cells)
        ]
        profiles.append(
            {
                "profile_id": f"dyadic-{cells}",
                "cells": cells,
                "hierarchy_depth": depth,
                "cluster_size": CLUSTER_SIZE,
                "cluster_count": cells // CLUSTER_SIZE,
                "clusters": cluster_records,
                "cell_to_cluster": mapping,
                "levels": levels,
                "coupling_topology_metrics": _round_value(
                    processor.topology_metrics(
                        processor.coupling_matrix, processor.fractal_alpha
                    )
                ),
                "thermal_topology_metrics": _round_value(
                    processor.topology_metrics(
                        processor.thermal_matrix, processor.thermal_beta
                    )
                ),
                "fixed_point_validation": core.topology_fixed_point_validation(
                    args, cells
                ),
            }
        )
    value = {
        "schema": TOPOLOGY_SCHEMA_ID,
        "kind": "hierarchy_topology_manifest",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": EXPECTED_M27_COMMIT,
        "profile_count": len(profiles),
        "profiles": profiles,
        "source_records": [
            source_record(root, PROTOTYPE_PATH, "semantic_authority"),
            source_record(root, M27_CHECKPOINT_PATH, "long_run_evidence"),
            source_record(root, M27_CONTRACT_PATH, "long_run_contract"),
            source_record(root, M14_QUALIFICATION_PATH, "prior_hierarchy_evidence"),
        ],
        "topology_set_digest": object_digest(profiles),
    }
    return attach_digest(value, "manifest_digest")


def _q16(value: float) -> int:
    return int(round(value * 65536.0))


def _cluster_observations(processor: core.FractalResonanceProcessor) -> list[dict[str, Any]]:
    result = []
    for row in processor.cluster_metrics(CLUSTER_SIZE):
        cluster_index = row["cluster_index"]
        start = row["cell_start"]
        end = row["cell_end"] + 1
        changes = sum(processor.cell_switch_activity[start:end])
        result.append(
            {
                "cluster_id": f"N{processor.cells}-C{cluster_index}",
                "cluster_index": cluster_index,
                "cell_ids": list(range(start, end)),
                "scheduler_state_observed": core.scheduler_state(
                    processor.scheduler, len(processor.telemetry) - 1
                ),
                "switch_changes_observed": changes,
                "switch_load_q16": _q16(row["switch_load"]),
                "heat_mean_q16": _q16(row["heat_mean"]),
                "heat_peak_q16": _q16(row["heat_peak"]),
                "phase_coherence_q30": int(round(row["phase_coherence"] * (1 << 30))),
                "pressure_q16": _q16(row["pressure"]),
                "coherence_margin_q16": _q16(row["coherence_margin"]),
                "state_counts": row["state_counts"],
            }
        )
    return result


def _run_scaling_profile(cells: int, scheduler: str) -> dict[str, Any]:
    args = _core_args(scheduler)
    seed_offset = cells + (0 if scheduler == "1/7" else 1000)
    processor = core.make_processor(
        args,
        cells=cells,
        scheduler=scheduler,
        seed_offset=seed_offset,
    )
    observations = []
    global_capacity = max(1, int(round(cells * args.transition_fraction)))
    for tick in range(SCALING_STEPS):
        processor.tick(tick, auto_targets=True)
        if (tick + 1) % SCALING_CHECKPOINT_INTERVAL == 0:
            clusters = _cluster_observations(processor)
            total_changes = sum(item["switch_changes_observed"] for item in clusters)
            observations.append(
                {
                    "tick": tick,
                    "scheduler_state": core.scheduler_state(scheduler, tick),
                    "global_transition_capacity": global_capacity,
                    "global_switch_changes_observed": total_changes,
                    "global_transition_capacity_remaining": global_capacity - total_changes,
                    "clusters": clusters,
                    "cluster_state_count_sums": {
                        value: sum(item["state_counts"][value] for item in clusters)
                        for value in ("-1", "0", "1")
                    },
                }
            )
    summary = processor.summarize(SCALING_STEPS)
    exact_profile = core.scaling_profile_validation(args, cells)
    checks = {
        "hierarchy_depth_exact": summary["hierarchy_depth"] == cells.bit_length() - 1,
        "cluster_partition_exact": all(
            sum(item["state_counts"].values()) == CLUSTER_SIZE
            for observation in observations
            for item in observation["clusters"]
        ),
        "cluster_counts_reconstruct_global": all(
            sum(observation["cluster_state_count_sums"].values()) == cells
            for observation in observations
        ),
        "scheduler_counts_valid": summary["scheduler_counts_valid"] is True,
        "balanced_ternary_state_domain": summary["balanced_ternary_state_domain"] is True,
        "actual_direct_events_zero": summary["actual_direct_events"] == 0,
        "reserved_state_events_zero": (
            exact_profile["summary"]["reserved_state_events"] == 0
        ),
        "queue_overflow_events_zero": (
            exact_profile["summary"]["queue_overflow_events"] == 0
        ),
        "switch_load_within_capacity": (
            summary["switch_load_peak"] <= args.transition_fraction + 1e-12
        ),
        "checkpoint_count_exact": (
            len(observations) == SCALING_STEPS // SCALING_CHECKPOINT_INTERVAL
        ),
        "fixed_point_profile_pass": exact_profile["status"] == "PASS",
    }
    return {
        "profile_id": f"N{cells}-{scheduler.replace('/', '_')}",
        "cells": cells,
        "hierarchy_depth": processor.hierarchy_depth,
        "cluster_size": CLUSTER_SIZE,
        "cluster_count": cells // CLUSTER_SIZE,
        "scheduler": scheduler,
        "scheduler_class": "temporal",
        "steps": SCALING_STEPS,
        "checkpoint_interval": SCALING_CHECKPOINT_INTERVAL,
        "checkpoint_count": len(observations),
        "seed": args.seed + seed_offset,
        "transition_fraction": args.transition_fraction,
        "request_lanes": global_capacity,
        "packed_state_width_bits": 2 * cells,
        "declared_execution_scaling": "O(N log N)",
        "checks": checks,
        "summary": summary,
        "fixed_point_validation_scheduler": exact_profile["summary"]["scheduler"],
        "fixed_point_profile": exact_profile,
        "observations": observations,
        "observation_digest": object_digest(observations),
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def build_scaling_matrix() -> dict[str, Any]:
    profiles = [
        _run_scaling_profile(cells, scheduler)
        for cells in SCALING_CELLS
        for scheduler in TEMPORAL_SCHEDULERS
    ]
    value = {
        "schema": SCALING_SCHEMA_ID,
        "kind": "hierarchical_scaling_matrix",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS" if all(item["status"] == "PASS" for item in profiles) else "FAIL",
        "source_commit": EXPECTED_M27_COMMIT,
        "profile_count": len(profiles),
        "cell_profiles": profiles,
        "temporal_scheduler_modes": list(TEMPORAL_SCHEDULERS),
        "service_scheduler_mode": SERVICE_SCHEDULER,
        "aggregation_equations": build_contract()["aggregation_equations"],
        "profile_set_digest": object_digest(profiles),
    }
    return attach_digest(value, "matrix_digest")


def _inject_hostile_requests(
    processor: core.FractalResonanceProcessor,
    cell_indices: Sequence[int],
    count: int,
    tick: int,
) -> None:
    nonzero = [index for index in cell_indices if processor.states[index] != 0]
    for offset in range(min(count, len(nonzero))):
        cell_id = nonzero[(tick * max(1, count) + offset) % len(nonzero)]
        processor.request_transition(cell_id, -processor.states[cell_id])


def _mean(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        raise ContractError("cannot aggregate an empty sequence")
    return sum(items) / len(items)


def _run_hotspot_profile(scheduler: str) -> dict[str, Any]:
    args = _core_args(scheduler)
    processor = core.make_processor(args, cells=16, scheduler=scheduler)
    processor.states = [-1 if index % 2 == 0 else 1 for index in range(16)]
    active = list(range(0, 4))
    adjacent = list(range(4, 8))
    inactive = list(range(4, 16))
    remote = list(range(12, 16))
    total_ticks = HOTSPOT_STRESS_TICKS + HOTSPOT_RECOVERY_TICKS
    active_peak = inactive_peak = adjacent_peak = remote_peak = processor.ambient_heat
    active_coherence_min = remote_coherence_min = 1.0
    snapshots = []

    for tick in range(total_ticks):
        if tick < HOTSPOT_STRESS_TICKS:
            _inject_hostile_requests(processor, active, 2, tick)
        processor.tick(tick, auto_targets=False)
        active_heat = _mean(processor.heat_cells[index] for index in active)
        inactive_heat = _mean(processor.heat_cells[index] for index in inactive)
        adjacent_heat = _mean(processor.heat_cells[index] for index in adjacent)
        remote_heat = _mean(processor.heat_cells[index] for index in remote)
        active_peak = max(active_peak, active_heat)
        inactive_peak = max(inactive_peak, inactive_heat)
        adjacent_peak = max(adjacent_peak, adjacent_heat)
        remote_peak = max(remote_peak, remote_heat)
        active_coherence_min = min(
            active_coherence_min,
            core.phase_order([processor.phases[index] for index in active]),
        )
        remote_coherence_min = min(
            remote_coherence_min,
            core.phase_order([processor.phases[index] for index in remote]),
        )
        if (tick + 1) % 12 == 0:
            snapshots.append(
                {
                    "tick": tick,
                    "phase": "stress" if tick < HOTSPOT_STRESS_TICKS else "recovery",
                    "scheduler_state": core.scheduler_state(scheduler, tick),
                    "active_cluster_heat_mean_q16": _q16(active_heat),
                    "adjacent_cluster_heat_mean_q16": _q16(adjacent_heat),
                    "remote_cluster_heat_mean_q16": _q16(remote_heat),
                    "inactive_cluster_heat_mean_q16": _q16(inactive_heat),
                    "clusters": _cluster_observations(processor),
                }
            )

    summary = processor.summarize(total_ticks)
    propagation_ratio = inactive_peak / active_peak
    remote_ratio = remote_peak / active_peak
    recovery_completion = None
    for record in processor.telemetry[HOTSPOT_STRESS_TICKS:]:
        if (
            record["heat"] <= processor.ambient_heat + 0.08
            and record["mean_frequency_lag"] <= 0.01
            and record["C_minus_P"] >= 0.20
        ):
            recovery_completion = record["tick"]
            break
    checks = {
        "balanced_ternary_state_domain": summary["balanced_ternary_state_domain"] is True,
        "actual_direct_events_zero": summary["actual_direct_events"] == 0,
        "requested_direct_events_present": summary["requested_direct_events"] >= 1,
        "prevented_direct_events_cover_requests": (
            summary["prevented_direct_events"] >= summary["requested_direct_events"]
        ),
        "neutral_routed_events_cover_prevention": (
            summary["neutral_routed_events"] >= summary["prevented_direct_events"]
        ),
        "active_cluster_hotter_than_inactive_mean": active_peak > inactive_peak,
        "remote_cluster_cooler_than_active_cluster": remote_peak < active_peak,
        "cross_cluster_thermal_propagation_bounded": (
            propagation_ratio < HOTSPOT_PROPAGATION_LIMIT
            and remote_ratio < HOTSPOT_REMOTE_PROPAGATION_LIMIT
        ),
        "global_C_minus_P_positive": summary["C_minus_P_min"] > 0,
        "switch_load_within_transition_fraction": (
            summary["switch_load_peak"] <= processor.transition_fraction + 1e-12
        ),
        "scheduler_counts_valid": summary["scheduler_counts_valid"] is True,
        "recovery_completed": recovery_completion is not None,
    }
    markers = {
        "active_cluster_heat_peak_q16": _q16(active_peak),
        "inactive_cluster_heat_mean_peak_q16": _q16(inactive_peak),
        "adjacent_cluster_heat_peak_q16": _q16(adjacent_peak),
        "remote_cluster_heat_peak_q16": _q16(remote_peak),
        "cross_cluster_thermal_propagation_ratio_q30": int(
            round(propagation_ratio * (1 << 30))
        ),
        "remote_thermal_propagation_ratio_q30": int(round(remote_ratio * (1 << 30))),
        "cross_cluster_thermal_propagation_bounded": checks[
            "cross_cluster_thermal_propagation_bounded"
        ],
        "active_cluster_coherence_min_q30": int(
            round(active_coherence_min * (1 << 30))
        ),
        "remote_cluster_coherence_min_q30": int(
            round(remote_coherence_min * (1 << 30))
        ),
        "localized_hotspot_containment_pass": all(checks.values()),
    }
    return {
        "profile_id": f"hotspot-{scheduler.replace('/', '_')}",
        "scheduler": scheduler,
        "scheduler_class": "service" if scheduler == SERVICE_SCHEDULER else "temporal",
        "configuration": {
            "cells": 16,
            "cluster_size": CLUSTER_SIZE,
            "active_cluster_id": "N16-C0",
            "active_cluster_cells": active,
            "adjacent_cluster_id": "N16-C1",
            "adjacent_cluster_cells": adjacent,
            "remote_cluster_id": "N16-C3",
            "remote_cluster_cells": remote,
            "stress_ticks": HOTSPOT_STRESS_TICKS,
            "recovery_ticks": HOTSPOT_RECOVERY_TICKS,
            "total_ticks": total_ticks,
            "hostile_requests_per_stress_tick": 2,
        },
        "limits": {
            "cross_cluster_thermal_propagation_ratio_lt": HOTSPOT_PROPAGATION_LIMIT,
            "remote_thermal_propagation_ratio_lt": HOTSPOT_REMOTE_PROPAGATION_LIMIT,
            "recovery_heat_limit": processor.ambient_heat + 0.08,
            "recovery_lag_limit": 0.01,
            "recovery_margin_min": 0.20,
            "limit_provenance": M14_QUALIFICATION_PATH,
        },
        "checks": checks,
        "containment_markers": markers,
        "recovery": {
            "start_tick": HOTSPOT_STRESS_TICKS,
            "completion_tick": recovery_completion,
            "duration_ticks": (
                recovery_completion - HOTSPOT_STRESS_TICKS
                if recovery_completion is not None
                else None
            ),
            "completed": recovery_completion is not None,
        },
        "summary": summary,
        "snapshots": snapshots,
        "snapshot_digest": object_digest(snapshots),
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def build_hotspot_evidence() -> dict[str, Any]:
    profiles = [_run_hotspot_profile(scheduler) for scheduler in ALL_SCHEDULERS]
    value = {
        "schema": HOTSPOT_SCHEMA_ID,
        "kind": "hotspot_containment_evidence",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS" if all(item["status"] == "PASS" for item in profiles) else "FAIL",
        "source_commit": EXPECTED_M27_COMMIT,
        "profile_count": len(profiles),
        "profiles": profiles,
        "limits": {
            "cross_cluster_thermal_propagation_ratio_lt": HOTSPOT_PROPAGATION_LIMIT,
            "remote_thermal_propagation_ratio_lt": HOTSPOT_REMOTE_PROPAGATION_LIMIT,
            "source": M14_QUALIFICATION_PATH,
        },
        "profile_set_digest": object_digest(profiles),
    }
    return attach_digest(value, "evidence_digest")


def _pass(check_id: str, category: str, evidence: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "category": category,
        "status": "PASS",
        "evidence": evidence,
    }


def build_qualification(root: Path) -> dict[str, Any]:
    contract = load_json(root, CONTRACT_ARTIFACT)
    topology = load_json(root, TOPOLOGY_ARTIFACT)
    scaling = load_json(root, SCALING_ARTIFACT)
    hotspot = load_json(root, HOTSPOT_ARTIFACT)
    checks = [
        _pass("M28-HQ001", "identity", RELEASE),
        _pass("M28-HQ002", "source", EXPECTED_M27_COMMIT),
        _pass("M28-HQ003", "supplement", M28_OBSERVATORY_COMMIT),
        _pass("M28-HQ004", "core", "-1/0/1"),
        _pass("M28-HQ005", "core", 0),
        _pass("M28-HQ006", "scheduler", list(TEMPORAL_SCHEDULERS)),
        _pass("M28-HQ007", "scheduler", SERVICE_SCHEDULER),
        _pass("M28-HQ008", "scope", list(REQUIRED_SCOPE)),
        _pass("M28-HQ009", "topology", topology["profile_count"]),
        _pass(
            "M28-HQ010",
            "topology",
            [item["hierarchy_depth"] for item in topology["profiles"]],
        ),
        _pass(
            "M28-HQ011",
            "topology",
            [item["cluster_count"] for item in topology["profiles"]],
        ),
        _pass("M28-HQ012", "scaling", scaling["profile_count"]),
        _pass(
            "M28-HQ013",
            "scaling",
            [item["status"] for item in scaling["cell_profiles"]],
        ),
        _pass("M28-HQ014", "containment", hotspot["profile_count"]),
        _pass(
            "M28-HQ015",
            "containment",
            [item["status"] for item in hotspot["profiles"]],
        ),
        _pass(
            "M28-HQ016",
            "containment",
            [
                item["containment_markers"]["localized_hotspot_containment_pass"]
                for item in hotspot["profiles"]
            ],
        ),
        _pass("M28-HQ017", "aggregation", contract["aggregation_equations"]),
        _pass("M28-HQ018", "boundary", "measurement_contours_separate"),
        _pass("M28-HQ019", "boundary", "model_derived_dimensionless_proxy"),
        _pass("M28-HQ020", "boundary", "no_universal_physical_chip_claim"),
    ]
    for profile in scaling["cell_profiles"]:
        checks.append(
            _pass(
                f"M28-HQ-S-{profile['cells']}-{profile['scheduler'].replace('/', '_')}",
                "scaling_profile",
                profile["observation_digest"],
            )
        )
    for profile in hotspot["profiles"]:
        checks.append(
            _pass(
                f"M28-HQ-C-{profile['scheduler'].replace('/', '_')}",
                "containment_profile",
                profile["snapshot_digest"],
            )
        )
    artifacts = [
        {
            "path": relative,
            "bytes": root.joinpath(*safe_relative_path(relative).parts).stat().st_size,
            "raw_sha256": raw_sha256(root.joinpath(*safe_relative_path(relative).parts)),
        }
        for relative in ARTIFACT_PATHS[:-1]
    ]
    schemas = [
        {
            "identifier": identifier,
            "path": relative,
            "bytes": root.joinpath(*safe_relative_path(relative).parts).stat().st_size,
            "raw_sha256": raw_sha256(root.joinpath(*safe_relative_path(relative).parts)),
        }
        for identifier, relative in SCHEMA_PATHS.items()
    ]
    value = {
        "schema": QUALIFICATION_SCHEMA_ID,
        "kind": "hierarchy_qualification",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": EXPECTED_M27_COMMIT,
        "qualification_id": "frp-m28-hierarchical-scaling-hotspot-containment",
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
        "artifacts": artifacts,
        "schemas": schemas,
    }
    return attach_digest(value, "qualification_digest")


def build_schema_registry(root: Path) -> dict[str, Any]:
    records = [
        {
            "identifier": identifier,
            "path": relative,
            "raw_sha256": raw_sha256(root.joinpath(*safe_relative_path(relative).parts)),
        }
        for identifier, relative in SCHEMA_PATHS.items()
    ]
    return attach_digest(
        {
            "kind": "m28_hierarchy_schema_registry",
            "milestone": MILESTONE,
            "version": VERSION,
            "source_commit": EXPECTED_M27_COMMIT,
            "record_count": len(records),
            "records": records,
        },
        "registry_digest",
    )


def validate_contract(value: dict[str, Any]) -> None:
    validate_attached_digest(value, "contract_digest")
    if value["required_scope"] != list(REQUIRED_SCOPE):
        raise ContractError("M28 hierarchy required scope mismatch")
    core_boundary = value["immutable_core"]
    if core_boundary["balanced_ternary_notation"] != "-1/0/1":
        raise ContractError("M28 hierarchy ternary notation mismatch")
    if core_boundary["semantic_values"] != [-1, 0, 1]:
        raise ContractError("M28 hierarchy ternary domain mismatch")
    if core_boundary["active_neutral_state"] != 0:
        raise ContractError("M28 hierarchy active neutral state mismatch")
    if core_boundary["temporal_scheduler_modes"] != list(TEMPORAL_SCHEDULERS):
        raise ContractError("M28 hierarchy temporal scheduler mismatch")
    if core_boundary["service_scheduler_mode"] != SERVICE_SCHEDULER:
        raise ContractError("M28 hierarchy service scheduler mismatch")
    if not value["aggregation_equations"]["no_undeclared_metric_aggregation"]:
        raise ContractError("M28 undeclared metric aggregation is not forbidden")


def validate_topology(value: dict[str, Any], root: Path) -> None:
    validate_attached_digest(value, "manifest_digest")
    if value["profile_count"] != len(SCALING_CELLS):
        raise ContractError("M28 topology profile count mismatch")
    if value["topology_set_digest"] != object_digest(value["profiles"]):
        raise ContractError("M28 topology set digest mismatch")
    for expected_cells, profile in zip(SCALING_CELLS, value["profiles"]):
        if profile["cells"] != expected_cells:
            raise ContractError("M28 topology cell profile ordering mismatch")
        if profile["hierarchy_depth"] != expected_cells.bit_length() - 1:
            raise ContractError("M28 hierarchy depth mismatch")
        expected_ids = list(range(expected_cells))
        observed_ids = [
            cell_id for cluster in profile["clusters"] for cell_id in cluster["cell_ids"]
        ]
        if observed_ids != expected_ids or len(set(observed_ids)) != expected_cells:
            raise ContractError("M28 cluster partition mismatch")
        if [item["cell_id"] for item in profile["cell_to_cluster"]] != expected_ids:
            raise ContractError("M28 cell-to-cluster mapping mismatch")
        for metrics_name in ("coupling_topology_metrics", "thermal_topology_metrics"):
            metrics = profile[metrics_name]
            if not all(
                metrics[key]
                for key in ("row_sum_match", "symmetry_match", "diagonal_zero")
            ):
                raise ContractError(f"M28 {metrics_name} failed")
        if profile["fixed_point_validation"]["status"] != "PASS":
            raise ContractError("M28 fixed-point topology validation failed")
    for record in value["source_records"]:
        path = root.joinpath(*safe_relative_path(record["path"]).parts)
        if path.stat().st_size != record["bytes"] or raw_sha256(path) != record["raw_sha256"]:
            raise ContractError(f"M28 hierarchy source provenance mismatch: {record['path']}")


def validate_scaling(value: dict[str, Any]) -> None:
    validate_attached_digest(value, "matrix_digest")
    if value["profile_count"] != len(SCALING_CELLS) * len(TEMPORAL_SCHEDULERS):
        raise ContractError("M28 scaling profile count mismatch")
    if value["profile_set_digest"] != object_digest(value["cell_profiles"]):
        raise ContractError("M28 scaling profile digest mismatch")
    expected_pairs = [
        (cells, scheduler)
        for cells in SCALING_CELLS
        for scheduler in TEMPORAL_SCHEDULERS
    ]
    observed_pairs = [(item["cells"], item["scheduler"]) for item in value["cell_profiles"]]
    if observed_pairs != expected_pairs:
        raise ContractError("M28 scaling profile ordering mismatch")
    for profile in value["cell_profiles"]:
        if profile["status"] != "PASS" or not all(profile["checks"].values()):
            raise ContractError(f"M28 scaling profile failed: {profile['profile_id']}")
        if profile["observation_digest"] != object_digest(profile["observations"]):
            raise ContractError("M28 scaling observation digest mismatch")
        for observation in profile["observations"]:
            if sum(observation["cluster_state_count_sums"].values()) != profile["cells"]:
                raise ContractError("M28 cluster aggregation mismatch")


def validate_hotspot(value: dict[str, Any]) -> None:
    validate_attached_digest(value, "evidence_digest")
    if value["profile_count"] != len(ALL_SCHEDULERS):
        raise ContractError("M28 hotspot profile count mismatch")
    if [item["scheduler"] for item in value["profiles"]] != list(ALL_SCHEDULERS):
        raise ContractError("M28 hotspot scheduler ordering mismatch")
    if value["profile_set_digest"] != object_digest(value["profiles"]):
        raise ContractError("M28 hotspot profile set digest mismatch")
    for profile in value["profiles"]:
        if profile["status"] != "PASS" or not all(profile["checks"].values()):
            raise ContractError(f"M28 hotspot profile failed: {profile['profile_id']}")
        if not profile["containment_markers"]["localized_hotspot_containment_pass"]:
            raise ContractError("M28 hotspot containment marker failed")
        if profile["snapshot_digest"] != object_digest(profile["snapshots"]):
            raise ContractError("M28 hotspot snapshot digest mismatch")


def validate_qualification(value: dict[str, Any], root: Path) -> None:
    validate_attached_digest(value, "qualification_digest")
    if value["status"] != "PASS" or value["failed_count"] != 0:
        raise ContractError("M28 hierarchy qualification failed")
    if value["check_count"] != value["passed_count"] or value["check_count"] != len(value["checks"]):
        raise ContractError("M28 hierarchy qualification count mismatch")
    if any(item["status"] != "PASS" for item in value["checks"]):
        raise ContractError("M28 hierarchy qualification contains a failed check")
    for record in value["artifacts"] + value["schemas"]:
        path = root.joinpath(*safe_relative_path(record["path"]).parts)
        if path.stat().st_size != record["bytes"] or raw_sha256(path) != record["raw_sha256"]:
            raise ContractError(f"M28 qualification inventory mismatch: {record['path']}")


def validate_registry(value: dict[str, Any], root: Path) -> None:
    validate_attached_digest(value, "registry_digest")
    if value["record_count"] != len(SCHEMA_PATHS):
        raise ContractError("M28 hierarchy schema registry count mismatch")
    if [item["identifier"] for item in value["records"]] != list(SCHEMA_PATHS):
        raise ContractError("M28 hierarchy schema registry ordering mismatch")
    for record in value["records"]:
        expected_path = SCHEMA_PATHS[record["identifier"]]
        if record["path"] != expected_path:
            raise ContractError("M28 hierarchy schema registry path mismatch")
        path = root.joinpath(*safe_relative_path(expected_path).parts)
        if raw_sha256(path) != record["raw_sha256"]:
            raise ContractError("M28 hierarchy schema registry digest mismatch")


def generate(repository_root: Path, output_root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    schemas = build_schemas()
    for identifier, schema in schemas.items():
        write_json(output_root, SCHEMA_PATHS[identifier], schema)
    artifacts = {
        CONTRACT_ARTIFACT: build_contract(),
        TOPOLOGY_ARTIFACT: build_topology_manifest(repository_root),
        SCALING_ARTIFACT: build_scaling_matrix(),
        HOTSPOT_ARTIFACT: build_hotspot_evidence(),
    }
    for relative, value in artifacts.items():
        write_json(output_root, relative, value)
    write_json(output_root, QUALIFICATION_ARTIFACT, build_qualification(output_root))
    write_json(output_root, SCHEMA_REGISTRY_PATH, build_schema_registry(output_root))
    return verify(output_root, source_commit, source_root=repository_root)


def verify(
    root: Path,
    source_commit: str,
    source_root: Path | None = None,
) -> dict[str, Any]:
    validate_source_commit(source_commit)
    schemas = {
        identifier: load_json(root, relative)
        for identifier, relative in SCHEMA_PATHS.items()
    }
    contract = load_json(root, CONTRACT_ARTIFACT)
    topology = load_json(root, TOPOLOGY_ARTIFACT)
    scaling = load_json(root, SCALING_ARTIFACT)
    hotspot = load_json(root, HOTSPOT_ARTIFACT)
    qualification = load_json(root, QUALIFICATION_ARTIFACT)
    registry = load_json(root, SCHEMA_REGISTRY_PATH)
    instances = {
        CONTRACT_SCHEMA_ID: contract,
        TOPOLOGY_SCHEMA_ID: topology,
        SCALING_SCHEMA_ID: scaling,
        HOTSPOT_SCHEMA_ID: hotspot,
        QUALIFICATION_SCHEMA_ID: qualification,
    }
    for identifier, instance in instances.items():
        validate_json_schema(instance, schemas[identifier])
    validate_contract(contract)
    validate_topology(topology, source_root.resolve() if source_root else root)
    validate_scaling(scaling)
    validate_hotspot(hotspot)
    validate_qualification(qualification, root)
    validate_registry(registry, root)
    return {
        "status": "PASS",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "schema_count": len(schemas),
        "artifact_count": len(ARTIFACT_PATHS),
        "generated_path_count": len(GENERATED_PATHS),
        "qualification_check_count": qualification["check_count"],
        "scaling_profile_count": scaling["profile_count"],
        "hotspot_profile_count": hotspot["profile_count"],
    }


def self_test(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    checks = []

    def negative(check_id: str, operation) -> None:
        try:
            operation()
        except (ContractError, SafetyError):
            checks.append({"check_id": check_id, "status": "PASS"})
        else:
            checks.append({"check_id": check_id, "status": "FAIL"})

    contract = load_json(root, CONTRACT_ARTIFACT)
    topology = load_json(root, TOPOLOGY_ARTIFACT)
    scaling = load_json(root, SCALING_ARTIFACT)
    hotspot = load_json(root, HOTSPOT_ARTIFACT)

    def changed_contract() -> None:
        value = copy.deepcopy(contract)
        value["immutable_core"]["balanced_ternary_notation"] = "ternary"
        validate_contract(attach_digest(value, "contract_digest"))

    def changed_mapping() -> None:
        value = copy.deepcopy(topology)
        value["profiles"][0]["clusters"][0]["cell_ids"][0] = 7
        value["topology_set_digest"] = object_digest(value["profiles"])
        validate_topology(attach_digest(value, "manifest_digest"), root)

    def changed_scaling() -> None:
        value = copy.deepcopy(scaling)
        value["cell_profiles"][0]["checks"]["actual_direct_events_zero"] = False
        value["profile_set_digest"] = object_digest(value["cell_profiles"])
        validate_scaling(attach_digest(value, "matrix_digest"))

    def changed_hotspot() -> None:
        value = copy.deepcopy(hotspot)
        value["profiles"][0]["checks"]["cross_cluster_thermal_propagation_bounded"] = False
        value["profile_set_digest"] = object_digest(value["profiles"])
        validate_hotspot(attach_digest(value, "evidence_digest"))

    negative("ternary-notation-change-rejected", changed_contract)
    negative("cell-cluster-mapping-change-rejected", changed_mapping)
    negative("scaling-invariant-change-rejected", changed_scaling)
    negative("containment-result-change-rejected", changed_hotspot)
    negative("wrong-source-commit-rejected", lambda: validate_source_commit("0" * 40))
    negative("unsafe-path-rejected", lambda: safe_relative_path("../escape"))

    with tempfile.TemporaryDirectory(prefix="m28-hierarchy-a-") as first_dir:
        with tempfile.TemporaryDirectory(prefix="m28-hierarchy-b-") as second_dir:
            first = Path(first_dir)
            second = Path(second_dir)
            generate(root, first, source_commit)
            generate(root, second, source_commit)
            identical = all(
                first.joinpath(*safe_relative_path(relative).parts).read_bytes()
                == second.joinpath(*safe_relative_path(relative).parts).read_bytes()
                for relative in GENERATED_PATHS
            )
            checks.append(
                {
                    "check_id": "two-complete-generations-byte-identical",
                    "status": "PASS" if identical else "FAIL",
                }
            )
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
    }


def _write_result(path: str | None, value: Any) -> None:
    raw = canonical_json_bytes(value)
    if path is None:
        print(raw.decode("utf-8"), end="")
        return
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=MILESTONE_TITLE)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--generate", action="store_true")
    operation.add_argument("--verify", action="store_true")
    operation.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--source-commit", default=EXPECTED_M27_COMMIT)
    parser.add_argument("--output")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    root = Path(args.repository_root)
    if args.generate:
        result = generate(root, Path(args.output_root), args.source_commit)
    elif args.verify:
        result = verify(root, args.source_commit)
    else:
        result = self_test(root, args.source_commit)
    _write_result(args.output, result)
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
