#!/usr/bin/env python3
"""Run, generate, and verify FRP M27 long-run telemetry qualification."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from frp_prototype_v1_7_0 import (
    Q16_SCALE,
    Q30_SCALE,
    TERNARY_STATES,
    QuantizedReferenceShadowProcessor,
    expected_scheduler_counts,
)


VERSION = "2.9.0"
MILESTONE = "M27"
MILESTONE_TITLE = "M27 - Long-Run Stability and Telemetry Qualification"
EXPECTED_M26_COMMIT = "67e9cc6d3e5dd2e96380b7cadb16b66f5e7d2427"
EXPECTED_M26_SUBJECT = "Add M26 declared-target implementation evidence"
WORKFLOW_PATH = ".github/workflows/frp-m27-long-run-stability-telemetry-qualification-workflow.yml"

CELLS = 16
TRANSITION_FRACTION_NUMERATOR = 1
TRANSITION_FRACTION_DENOMINATOR = 4
TRANSITION_FRACTION = TRANSITION_FRACTION_NUMERATOR / TRANSITION_FRACTION_DENOMINATOR
REQUEST_LANES = 4
RUN_TICKS = 16_384
CHECKPOINT_INTERVAL = 512
PHASE_PERIOD_TICKS = 256
ACTIVE_TICKS = 192
SETTLE_TICKS = 32
IDLE_TICKS = 32
ZERO_EVENT_MIN_TICKS = 8
CANONICAL_FILE_MAX_BYTES = 524_288
CANONICAL_PRIMARY_SET_MAX_BYTES = 2_097_152
RAW_RETENTION_DAYS = 30

PROFILE_SPECS = (
    {"profile_id": "free-long-run", "scheduler_mode": "free", "seed": 27001, "workload_offset": 0},
    {"profile_id": "seven-one-long-run", "scheduler_mode": "7/1", "seed": 27002, "workload_offset": 5},
    {"profile_id": "one-seven-long-run", "scheduler_mode": "1/7", "seed": 27003, "workload_offset": 10},
)

CONTRACT_ARTIFACT = "artifacts/m27/contracts/m27-long-run-telemetry-contract.json"
WORKLOAD_ARTIFACT = "artifacts/m27/workloads/m27-long-run-workload-catalog.json"
CHECKPOINT_ARTIFACT = "artifacts/m27/checkpoints/m27-long-run-checkpoint-evidence.json"
TELEMETRY_ARTIFACT = "artifacts/m27/telemetry/m27-telemetry-semantics.json"
REPORT_ARTIFACT = "artifacts/m27/reports/m27-long-run-stability-report.json"
MANIFEST_ARTIFACT = "artifacts/m27/manifests/m27-long-run-stability-manifest.json"
QUALIFICATION_ARTIFACT = "artifacts/m27/manifests/m27-long-run-stability-qualification.json"

CONTRACT_SCHEMA = "schemas/m27/frp_m27_long_run_telemetry_contract.v2.9.0.schema.json"
WORKLOAD_SCHEMA = "schemas/m27/frp_m27_long_run_workload_catalog.v2.9.0.schema.json"
CHECKPOINT_SCHEMA = "schemas/m27/frp_m27_long_run_checkpoint_evidence.v2.9.0.schema.json"
TELEMETRY_SCHEMA = "schemas/m27/frp_m27_telemetry_semantics.v2.9.0.schema.json"
REPORT_SCHEMA = "schemas/m27/frp_m27_long_run_stability_report.v2.9.0.schema.json"
MANIFEST_SCHEMA = "schemas/m27/frp_m27_long_run_stability_manifest.v2.9.0.schema.json"
QUALIFICATION_SCHEMA = "schemas/m27/frp_m27_long_run_stability_qualification.v2.9.0.schema.json"
REGISTRY_PATH = "schemas/m27/frp_m27_schema_registry.json"

SCHEMA_PATHS = {
    "m27-long-run-telemetry-contract-v2.9.0": CONTRACT_SCHEMA,
    "m27-long-run-workload-catalog-v2.9.0": WORKLOAD_SCHEMA,
    "m27-long-run-checkpoint-evidence-v2.9.0": CHECKPOINT_SCHEMA,
    "m27-telemetry-semantics-v2.9.0": TELEMETRY_SCHEMA,
    "m27-long-run-stability-report-v2.9.0": REPORT_SCHEMA,
    "m27-long-run-stability-manifest-v2.9.0": MANIFEST_SCHEMA,
    "m27-long-run-stability-qualification-v2.9.0": QUALIFICATION_SCHEMA,
}

PRIMARY_ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    WORKLOAD_ARTIFACT,
    CHECKPOINT_ARTIFACT,
    TELEMETRY_ARTIFACT,
    REPORT_ARTIFACT,
)

ARTIFACT_PATHS = (
    *PRIMARY_ARTIFACT_PATHS,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

TECHNICAL_SOURCE_PATHS = (
    "frp_m27_long_run_stability_telemetry_qualification.py",
    *SCHEMA_PATHS.values(),
    REGISTRY_PATH,
    "tests/test_frp_m27_long_run_stability_telemetry_qualification.py",
)

UPSTREAM_SOURCE_PATHS = (
    "frp_prototype_v1_7_0.py",
    "artifacts/m21/matrix/m21-parameter-dimensions.json",
    "artifacts/m26/contracts/m26-declared-target-implementation-contract.json",
    "artifacts/m26/reports/m26-declared-target-implementation-report.json",
    "artifacts/m26/manifests/m26-declared-target-implementation-manifest.json",
    "artifacts/m26/manifests/m26-declared-target-implementation-qualification.json",
)

REQUIRED_SCOPE = (
    "long_run_scheduler_execution",
    "long_run_pending_route_behavior",
    "long_run_transition_capacity_behavior",
    "switching_load_telemetry",
    "thermal_state_proxy_telemetry",
    "transition_pressure_telemetry",
    "coherence_telemetry",
    "stability_boundary_records",
    "zero_event_intervals",
    "deterministic_checkpoint_digests",
    "bounded_artifact_size_and_retention_policy",
    "exact_workload_identity",
)

TELEMETRY_DEFINITIONS = (
    {
        "telemetry_id": "switching_load_q16",
        "storage_type": "signed_integer_s32q16",
        "domain": {"minimum": 0, "maximum": Q16_SCALE},
        "relation": "round(changes * 65536 / cells)",
        "classification": "dimensionless_model_derived_event_fraction_proxy",
    },
    {
        "telemetry_id": "thermal_state_proxy_q16",
        "storage_type": "signed_integer_s32q16",
        "domain": {"minimum": 0, "maximum": 2_147_483_647},
        "relation": "integer mean of per-cell model heat state",
        "classification": "dimensionless_model_state_proxy",
    },
    {
        "telemetry_id": "transition_pressure_q16",
        "storage_type": "signed_integer_s32q16",
        "domain": {"minimum": 0, "maximum": 2_147_483_647},
        "relation": "thermal_state_proxy_q16 + switching_load_q16",
        "classification": "dimensionless_model_derived_pressure_proxy",
    },
    {
        "telemetry_id": "global_phase_coherence_q30",
        "storage_type": "signed_integer_s32q30",
        "domain": {"minimum": 0, "maximum": Q30_SCALE},
        "relation": "quantized global phase-order metric",
        "classification": "dimensionless_model_coherence_metric",
    },
    {
        "telemetry_id": "coherence_capacity_q16",
        "storage_type": "signed_integer_s32q16",
        "domain": {"minimum": -2_147_483_648, "maximum": 2_147_483_647},
        "relation": "canonical fixed-point model coherence capacity C",
        "classification": "dimensionless_model_capacity_proxy",
    },
    {
        "telemetry_id": "stability_margin_q16",
        "storage_type": "signed_integer_s32q16",
        "domain": {"minimum": -2_147_483_648, "maximum": 2_147_483_647},
        "relation": "coherence_capacity_q16 - transition_pressure_q16",
        "classification": "dimensionless_model_stability_margin",
    },
)


class ContractError(ValueError):
    """Raised when an M27 invariant is violated."""


class SafetyError(ValueError):
    """Raised when an M27 path leaves its declared repository boundary."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    return path


def path_for(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative_path(relative).parts)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def document_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def validate_source_commit(value: str) -> str:
    if value != EXPECTED_M26_COMMIT:
        raise ContractError(f"unexpected M26 source commit: {value}")
    return value


def require_file(root: Path, relative: str) -> Path:
    target = path_for(root, relative)
    if target.is_symlink() or not target.is_file():
        raise ContractError(f"required source missing: {relative}")
    return target


def source_record(root: Path, relative: str) -> dict[str, Any]:
    raw = require_file(root, relative).read_bytes()
    return {"path": relative, "bytes": len(raw), "raw_sha256": raw_digest(raw)}


def add_digest(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = dict(value)
    result[field] = object_digest(result)
    return result


def verify_digest(value: Mapping[str, Any], field: str, label: str) -> None:
    payload = dict(value)
    observed = payload.pop(field, None)
    expected = object_digest(payload)
    if observed != expected:
        raise ContractError(f"{label} digest mismatch")


class SchemaContext:
    """Load and validate the closed M27 Draft 2020-12 schema set."""

    def __init__(self, root: Path) -> None:
        self.schemas: dict[str, Mapping[str, Any]] = {}
        for relative in SCHEMA_PATHS.values():
            schema = json.loads(require_file(root, relative).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self.schemas[relative] = schema

    def validate(self, schema_path: str, instance: Any, label: str) -> None:
        errors = sorted(
            Draft202012Validator(self.schemas[schema_path]).iter_errors(instance),
            key=lambda item: list(item.absolute_path),
        )
        if errors:
            detail = "; ".join(error.message for error in errors[:5])
            raise ContractError(f"schema validation failed for {label}: {detail}")


def profile_identity(spec: Mapping[str, Any]) -> dict[str, Any]:
    identity = {
        "profile_id": spec["profile_id"],
        "scheduler_mode": spec["scheduler_mode"],
        "seed": spec["seed"],
        "workload_offset": spec["workload_offset"],
        "cells": CELLS,
        "request_lanes": REQUEST_LANES,
        "transition_fraction": {
            "numerator": TRANSITION_FRACTION_NUMERATOR,
            "denominator": TRANSITION_FRACTION_DENOMINATOR,
        },
        "ticks": RUN_TICKS,
        "checkpoint_interval_ticks": CHECKPOINT_INTERVAL,
        "phase_period_ticks": PHASE_PERIOD_TICKS,
        "phase_partition": {
            "active_ticks": ACTIVE_TICKS,
            "settle_ticks": SETTLE_TICKS,
            "idle_ticks": IDLE_TICKS,
        },
        "request_generator": "m27-deterministic-lane-pattern-v1",
        "target_state_domain": list(TERNARY_STATES),
    }
    return add_digest(identity, "workload_identity_digest")


def workload_phase(tick: int) -> str:
    phase_tick = tick % PHASE_PERIOD_TICKS
    if phase_tick < ACTIVE_TICKS:
        return "active"
    if phase_tick < ACTIVE_TICKS + SETTLE_TICKS:
        return "settle"
    return "idle"


def workload_requests(tick: int, offset: int) -> list[tuple[bool, int, int]]:
    if workload_phase(tick) != "active":
        return []
    requests: list[tuple[bool, int, int]] = []
    for lane in range(REQUEST_LANES):
        valid = ((tick + lane * 5 + offset) % 7) != 0
        cell_id = (tick * 5 + lane * 3 + offset) % CELLS
        target = TERNARY_STATES[(tick + lane * 2 + offset) % len(TERNARY_STATES)]
        requests.append((valid, cell_id, target))
    return requests


def request_rows(requests: Sequence[tuple[bool, int, int]]) -> list[dict[str, Any]]:
    return [
        {"lane": lane, "valid": valid, "cell_id": cell_id, "target_state": target}
        for lane, (valid, cell_id, target) in enumerate(requests)
    ]


def margin_class(value: int) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def checkpoint_record(
    profile_id: str,
    record: Mapping[str, Any],
    processor: QuantizedReferenceShadowProcessor,
    chain_digest: str,
) -> dict[str, Any]:
    value = {
        "profile_id": profile_id,
        "tick": record["tick"],
        "chain_digest": chain_digest,
        "scheduler_state": record["scheduler_state_name"],
        "scheduler_counts": dict(sorted(processor.scheduler_counts.items())),
        "states": list(processor.states),
        "states_packed_hex": record["states_packed_hex"],
        "pending_route_count": record["pending_route_count"],
        "changes": record["changes"],
        "transition_capacity_remaining": REQUEST_LANES - record["changes"],
        "switching_load_q16": record["switch_load_q16"],
        "thermal_state_proxy_q16": record["heat_global_q16"],
        "global_phase_coherence_q30": record["global_phase_coherence_q30"],
        "coherence_capacity_q16": record["C_q16"],
        "transition_pressure_q16": record["P_q16"],
        "stability_margin_q16": record["C_minus_P_q16"],
        "stability_margin_class": margin_class(record["C_minus_P_q16"]),
        "requested_direct_events": record["requested_direct_events"],
        "prevented_direct_events": record["prevented_direct_events"],
        "neutral_routed_events": record["neutral_routed_events"],
        "neutralized_conflicts": record["neutralized_conflicts"],
        "actual_direct_events": record["actual_direct_events"],
        "reserved_state_events": record["reserved_state_events"],
        "queue_overflow_events": record["queue_overflow_events"],
    }
    return add_digest(value, "checkpoint_digest")


def _update_range(ranges: dict[str, dict[str, int]], key: str, value: int) -> None:
    if key not in ranges:
        ranges[key] = {"minimum": value, "maximum": value}
    else:
        ranges[key]["minimum"] = min(ranges[key]["minimum"], value)
        ranges[key]["maximum"] = max(ranges[key]["maximum"], value)


def run_profile(spec: Mapping[str, Any]) -> dict[str, Any]:
    identity = profile_identity(spec)
    processor = QuantizedReferenceShadowProcessor(
        cells=CELLS,
        transition_fraction=TRANSITION_FRACTION,
        scheduler=spec["scheduler_mode"],
        seed=spec["seed"],
    )
    if processor.request_lanes != REQUEST_LANES:
        raise ContractError("canonical transition capacity is not four lanes")

    chain_digest = object_digest({
        "domain": "frp-m27-long-run-checkpoint-chain-v1",
        "workload_identity_digest": identity["workload_identity_digest"],
    })
    checkpoints: list[dict[str, Any]] = []
    zero_intervals: list[dict[str, int]] = []
    boundary_crossings: list[dict[str, Any]] = []
    metric_ranges: dict[str, dict[str, int]] = {}
    previous_margin: int | None = None
    minimum_margin = 2_147_483_647
    minimum_margin_tick = -1
    zero_start: int | None = None
    zero_event_ticks = 0
    valid_request_count = 0
    max_pending_routes = 0
    max_changes = 0
    retained_trace_peak = 0
    retained_cell_trace_peak = 0
    retained_route_event_peak = 0

    for tick in range(RUN_TICKS):
        phase = workload_phase(tick)
        requests = workload_requests(tick, spec["workload_offset"])
        valid_request_count += sum(1 for valid, _, _ in requests if valid)
        record = processor.tick(
            tick,
            requests=requests,
            auto_targets_enable=phase != "idle",
        )

        if record["P_q16"] != record["heat_global_q16"] + record["switch_load_q16"]:
            raise ContractError(f"transition-pressure relation failed at tick {tick}")
        if record["changes"] < 0 or record["changes"] > REQUEST_LANES:
            raise ContractError(f"transition capacity failed at tick {tick}")
        if record["pending_route_count"] > processor.neutral_route_queue_capacity:
            raise ContractError(f"pending-route capacity failed at tick {tick}")
        if any(state not in TERNARY_STATES for state in processor.states):
            raise ContractError(f"ternary state domain failed at tick {tick}")

        tick_payload = {
            "tick": tick,
            "phase": phase,
            "requests": request_rows(requests),
            "auto_targets_enable": phase != "idle",
            "scheduler_state": record["scheduler_state_name"],
            "states": list(processor.states),
            "states_packed_hex": record["states_packed_hex"],
            "pending_route_count": record["pending_route_count"],
            "changes": record["changes"],
            "switching_load_q16": record["switch_load_q16"],
            "thermal_state_proxy_q16": record["heat_global_q16"],
            "global_phase_coherence_q30": record["global_phase_coherence_q30"],
            "coherence_capacity_q16": record["C_q16"],
            "transition_pressure_q16": record["P_q16"],
            "stability_margin_q16": record["C_minus_P_q16"],
            "counters": {
                "requested_direct_events": record["requested_direct_events"],
                "prevented_direct_events": record["prevented_direct_events"],
                "neutral_routed_events": record["neutral_routed_events"],
                "neutralized_conflicts": record["neutralized_conflicts"],
                "actual_direct_events": record["actual_direct_events"],
                "reserved_state_events": record["reserved_state_events"],
                "queue_overflow_events": record["queue_overflow_events"],
            },
        }
        chain_digest = hashlib.sha256(
            bytes.fromhex(chain_digest) + canonical_json_bytes(tick_payload)
        ).hexdigest()

        for key, value in (
            ("switching_load_q16", record["switch_load_q16"]),
            ("thermal_state_proxy_q16", record["heat_global_q16"]),
            ("transition_pressure_q16", record["P_q16"]),
            ("global_phase_coherence_q30", record["global_phase_coherence_q30"]),
            ("coherence_capacity_q16", record["C_q16"]),
            ("stability_margin_q16", record["C_minus_P_q16"]),
            ("pending_route_count", record["pending_route_count"]),
            ("changes", record["changes"]),
        ):
            _update_range(metric_ranges, key, value)

        margin = record["C_minus_P_q16"]
        if margin < minimum_margin:
            minimum_margin = margin
            minimum_margin_tick = tick
        if previous_margin is not None and margin_class(previous_margin) != margin_class(margin):
            if previous_margin == 0 or margin == 0 or (previous_margin < 0) != (margin < 0):
                boundary_crossings.append({
                    "tick": tick,
                    "previous_margin_q16": previous_margin,
                    "current_margin_q16": margin,
                    "direction": "toward_nonpositive" if previous_margin > margin else "toward_positive",
                })
        previous_margin = margin

        zero_event = (
            record["switch_load_q16"] == 0
            and record["pending_route_count"] == 0
            and record["changes"] == 0
        )
        if zero_event:
            zero_event_ticks += 1
            if zero_start is None:
                zero_start = tick
        elif zero_start is not None:
            length = tick - zero_start
            if length >= ZERO_EVENT_MIN_TICKS:
                zero_intervals.append({"start_tick": zero_start, "end_tick": tick - 1, "tick_count": length})
            zero_start = None

        max_pending_routes = max(max_pending_routes, record["pending_route_count"])
        max_changes = max(max_changes, record["changes"])
        retained_trace_peak = max(retained_trace_peak, len(processor.trace))
        retained_cell_trace_peak = max(retained_cell_trace_peak, len(processor.cell_trace))
        retained_route_event_peak = max(retained_route_event_peak, len(processor.route_events))

        if (tick + 1) % CHECKPOINT_INTERVAL == 0:
            checkpoints.append(checkpoint_record(spec["profile_id"], record, processor, chain_digest))

        processor.trace.clear()
        processor.cell_trace.clear()
        processor.route_events.clear()

    if zero_start is not None:
        length = RUN_TICKS - zero_start
        if length >= ZERO_EVENT_MIN_TICKS:
            zero_intervals.append({"start_tick": zero_start, "end_tick": RUN_TICKS - 1, "tick_count": length})

    counters = {
        "requested_direct_events": processor.requested_direct_events,
        "prevented_direct_events": processor.prevented_direct_events,
        "neutral_routed_events": processor.neutral_routed_events,
        "neutralized_conflicts": processor.neutralized_conflicts,
        "actual_direct_events": processor.actual_direct_events,
        "reserved_state_events": processor.reserved_state_events,
        "queue_overflow_events": processor.queue_overflow_events,
    }
    profile = {
        "profile_id": spec["profile_id"],
        "status": "PASS",
        "workload_identity": identity,
        "scheduler_mode": spec["scheduler_mode"],
        "ticks": RUN_TICKS,
        "scheduler_counts": dict(sorted(processor.scheduler_counts.items())),
        "expected_scheduler_counts": dict(sorted(expected_scheduler_counts(spec["scheduler_mode"], RUN_TICKS).items())),
        "valid_request_count": valid_request_count,
        "transition_capacity": {
            "request_lanes": REQUEST_LANES,
            "maximum_changes_observed": max_changes,
            "capacity_relation_valid": max_changes <= REQUEST_LANES,
        },
        "pending_routes": {
            "queue_capacity": processor.neutral_route_queue_capacity,
            "maximum_pending_observed": max_pending_routes,
            "final_pending_count": len(processor.pending_neutral_routes),
            "capacity_relation_valid": max_pending_routes <= processor.neutral_route_queue_capacity,
        },
        "counter_relations": {
            **counters,
            "prevented_covers_requested": counters["prevented_direct_events"] >= counters["requested_direct_events"],
            "neutral_route_relation_valid": counters["neutral_routed_events"] == counters["neutralized_conflicts"],
            "safety_counters_zero": counters["actual_direct_events"] == counters["reserved_state_events"] == counters["queue_overflow_events"] == 0,
        },
        "metric_ranges": metric_ranges,
        "stability_boundary_record": {
            "observation_status": "crossed" if boundary_crossings else "not_crossed",
            "crossing_count": len(boundary_crossings),
            "crossings": boundary_crossings,
            "minimum_margin_q16": minimum_margin,
            "minimum_margin_tick": minimum_margin_tick,
            "final_margin_q16": processor.C_minus_P_q16,
            "final_margin_class": margin_class(processor.C_minus_P_q16),
        },
        "zero_event_record": {
            "minimum_interval_ticks": ZERO_EVENT_MIN_TICKS,
            "zero_event_tick_count": zero_event_ticks,
            "retained_interval_count": len(zero_intervals),
            "intervals": zero_intervals,
        },
        "checkpoint_count": len(checkpoints),
        "checkpoints": checkpoints,
        "final_chain_digest": chain_digest,
        "final_states": list(processor.states),
        "bounded_runtime_retention": {
            "per_tick_trace_cleared": True,
            "per_cell_trace_cleared": True,
            "route_event_trace_cleared": True,
            "retained_trace_peak_records": retained_trace_peak,
            "retained_cell_trace_peak_records": retained_cell_trace_peak,
            "retained_route_event_peak_records": retained_route_event_peak,
        },
    }
    return add_digest(profile, "profile_result_digest")


def run_long_run(source_commit: str) -> dict[str, Any]:
    source_commit = validate_source_commit(source_commit)
    profiles = [run_profile(spec) for spec in PROFILE_SPECS]
    result = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-checkpoint-evidence",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": source_commit,
        "profile_count": len(profiles),
        "total_ticks": sum(profile["ticks"] for profile in profiles),
        "checkpoint_interval_ticks": CHECKPOINT_INTERVAL,
        "checkpoint_count": sum(profile["checkpoint_count"] for profile in profiles),
        "profiles": profiles,
        "checkpoint_set_digest": object_digest([
            checkpoint
            for profile in profiles
            for checkpoint in profile["checkpoints"]
        ]),
    }
    result = add_digest(result, "evidence_digest")
    validate_long_run_result(result, source_commit)
    return result


def validate_long_run_result(value: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    result = dict(value)
    if result.get("source_commit") != source_commit:
        raise ContractError("long-run source commit mismatch")
    if result.get("status") != "PASS" or result.get("profile_count") != len(PROFILE_SPECS):
        raise ContractError("long-run status or profile count mismatch")
    if result.get("total_ticks") != RUN_TICKS * len(PROFILE_SPECS):
        raise ContractError("long-run total tick count mismatch")
    verify_digest(result, "evidence_digest", "long-run evidence")
    profiles = result.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != len(PROFILE_SPECS):
        raise ContractError("long-run profiles are incomplete")
    all_checkpoints: list[Mapping[str, Any]] = []
    for spec, profile in zip(PROFILE_SPECS, profiles):
        verify_digest(profile, "profile_result_digest", str(profile.get("profile_id")))
        if profile.get("profile_id") != spec["profile_id"] or profile.get("scheduler_mode") != spec["scheduler_mode"]:
            raise ContractError("long-run profile identity mismatch")
        identity = profile.get("workload_identity")
        if identity != profile_identity(spec):
            raise ContractError(f"workload identity mismatch for {spec['profile_id']}")
        if profile.get("scheduler_counts") != profile.get("expected_scheduler_counts"):
            raise ContractError(f"scheduler counts mismatch for {spec['profile_id']}")
        transition = profile.get("transition_capacity", {})
        pending = profile.get("pending_routes", {})
        counters = profile.get("counter_relations", {})
        if transition.get("request_lanes") != REQUEST_LANES or transition.get("capacity_relation_valid") is not True:
            raise ContractError(f"transition capacity mismatch for {spec['profile_id']}")
        if pending.get("queue_capacity") != CELLS or pending.get("capacity_relation_valid") is not True:
            raise ContractError(f"pending-route capacity mismatch for {spec['profile_id']}")
        if counters.get("prevented_covers_requested") is not True:
            raise ContractError(f"direct-event counter relation mismatch for {spec['profile_id']}")
        if counters.get("neutral_route_relation_valid") is not True or counters.get("safety_counters_zero") is not True:
            raise ContractError(f"neutral-route safety relation mismatch for {spec['profile_id']}")
        checkpoints = profile.get("checkpoints")
        if not isinstance(checkpoints, list) or len(checkpoints) != RUN_TICKS // CHECKPOINT_INTERVAL:
            raise ContractError(f"checkpoint count mismatch for {spec['profile_id']}")
        expected_ticks = list(range(CHECKPOINT_INTERVAL - 1, RUN_TICKS, CHECKPOINT_INTERVAL))
        if [checkpoint.get("tick") for checkpoint in checkpoints] != expected_ticks:
            raise ContractError(f"checkpoint order mismatch for {spec['profile_id']}")
        for checkpoint in checkpoints:
            verify_digest(checkpoint, "checkpoint_digest", f"checkpoint {spec['profile_id']}/{checkpoint.get('tick')}")
            if checkpoint.get("transition_pressure_q16") != checkpoint.get("thermal_state_proxy_q16") + checkpoint.get("switching_load_q16"):
                raise ContractError(f"checkpoint pressure relation mismatch for {spec['profile_id']}")
            if checkpoint.get("stability_margin_q16") != checkpoint.get("coherence_capacity_q16") - checkpoint.get("transition_pressure_q16"):
                raise ContractError(f"checkpoint margin relation mismatch for {spec['profile_id']}")
            if any(state not in TERNARY_STATES for state in checkpoint.get("states", [])):
                raise ContractError(f"checkpoint state domain mismatch for {spec['profile_id']}")
        if profile.get("final_chain_digest") != checkpoints[-1].get("chain_digest"):
            raise ContractError(f"final chain mismatch for {spec['profile_id']}")
        if not profile.get("zero_event_record", {}).get("intervals"):
            raise ContractError(f"zero-event intervals missing for {spec['profile_id']}")
        all_checkpoints.extend(checkpoints)
    if result.get("checkpoint_count") != len(all_checkpoints):
        raise ContractError("aggregate checkpoint count mismatch")
    if result.get("checkpoint_set_digest") != object_digest(all_checkpoints):
        raise ContractError("checkpoint set digest mismatch")
    return result


def build_contract(source_commit: str) -> dict[str, Any]:
    contract = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-telemetry-contract",
        "milestone": MILESTONE,
        "milestone_title": MILESTONE_TITLE,
        "release": "FRP v2.9.0",
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "objective": "qualify deterministic long-run execution and published telemetry relations",
        "required_scope": list(REQUIRED_SCOPE),
        "immutable_core": {
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": list(TERNARY_STATES),
            "active_neutral_state": 0,
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
            "opposite_transition_route": ["source", "0", "target"],
        },
        "long_run_boundary": {
            "profile_count": len(PROFILE_SPECS),
            "ticks_per_profile": RUN_TICKS,
            "total_ticks": RUN_TICKS * len(PROFILE_SPECS),
            "cells": CELLS,
            "request_lanes": REQUEST_LANES,
            "checkpoint_interval_ticks": CHECKPOINT_INTERVAL,
            "full_tick_trace_committed": False,
        },
        "retention_policy": {
            "canonical_artifacts": "committed",
            "raw_workflow_runs": "github_actions_artifact",
            "raw_workflow_retention_days": RAW_RETENTION_DAYS,
            "canonical_file_max_bytes": CANONICAL_FILE_MAX_BYTES,
            "canonical_primary_set_max_bytes": CANONICAL_PRIMARY_SET_MAX_BYTES,
            "per_tick_records": "reduced_to_ordered_checkpoints_and_zero_event_intervals",
        },
        "interpretation_boundary": {
            "telemetry_is_model_derived": True,
            "telemetry_is_dimensionless": True,
            "physical_measurement_status": "not_a_physical_measurement",
            "proxy_to_physical_conversion": "prohibited",
            "universal_physical_chip_claim": "not_made",
        },
    }
    return add_digest(contract, "contract_digest")


def build_workload_catalog(source_commit: str) -> dict[str, Any]:
    catalog = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-workload-catalog",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "generator": {
            "generator_id": "m27-deterministic-lane-pattern-v1",
            "phase_order": ["active", "settle", "idle"],
            "phase_period_ticks": PHASE_PERIOD_TICKS,
            "active_ticks": ACTIVE_TICKS,
            "settle_ticks": SETTLE_TICKS,
            "idle_ticks": IDLE_TICKS,
            "target_state_domain": list(TERNARY_STATES),
            "external_requests_during_active_only": True,
            "auto_targets_enabled_during_active_and_settle": True,
        },
        "profile_count": len(PROFILE_SPECS),
        "profiles": [profile_identity(spec) for spec in PROFILE_SPECS],
    }
    return add_digest(catalog, "catalog_digest")


def build_telemetry_semantics(source_commit: str) -> dict[str, Any]:
    semantics = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-telemetry-semantics",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "telemetry_count": len(TELEMETRY_DEFINITIONS),
        "telemetry": list(TELEMETRY_DEFINITIONS),
        "validated_relations": [
            "transition_pressure_q16 equals thermal_state_proxy_q16 plus switching_load_q16",
            "stability_margin_q16 equals coherence_capacity_q16 minus transition_pressure_q16",
            "changes never exceeds request_lanes",
            "pending_route_count never exceeds queue_capacity",
        ],
        "interpretation_boundary": {
            "all_values_are_model_derived": True,
            "all_values_are_dimensionless": True,
            "physical_units_published": False,
            "physical_measurements_published": False,
            "unsupported_physical_interpretation": "prohibited",
        },
    }
    return add_digest(semantics, "semantics_digest")


def build_report(
    contract: Mapping[str, Any],
    workload: Mapping[str, Any],
    evidence: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    profile_summaries = []
    for profile in evidence["profiles"]:
        profile_summaries.append({
            "profile_id": profile["profile_id"],
            "scheduler_mode": profile["scheduler_mode"],
            "ticks": profile["ticks"],
            "checkpoint_count": profile["checkpoint_count"],
            "zero_event_interval_count": profile["zero_event_record"]["retained_interval_count"],
            "boundary_observation_status": profile["stability_boundary_record"]["observation_status"],
            "minimum_margin_q16": profile["stability_boundary_record"]["minimum_margin_q16"],
            "maximum_pending_routes": profile["pending_routes"]["maximum_pending_observed"],
            "maximum_changes": profile["transition_capacity"]["maximum_changes_observed"],
            "final_chain_digest": profile["final_chain_digest"],
            "status": "PASS",
        })
    report = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-stability-report",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "workload_catalog_digest": workload["catalog_digest"],
        "checkpoint_evidence_digest": evidence["evidence_digest"],
        "telemetry_semantics_digest": telemetry["semantics_digest"],
        "deterministic_rerun_requirement": {
            "required_run_count": 2,
            "comparison": "byte_identical_canonical_json",
            "workflow_enforced": True,
        },
        "aggregate": {
            "profile_count": evidence["profile_count"],
            "total_ticks": evidence["total_ticks"],
            "checkpoint_count": evidence["checkpoint_count"],
            "scheduler_modes": [spec["scheduler_mode"] for spec in PROFILE_SPECS],
            "all_profiles_passed": all(profile["status"] == "PASS" for profile in evidence["profiles"]),
            "all_safety_counters_zero": all(profile["counter_relations"]["safety_counters_zero"] for profile in evidence["profiles"]),
            "all_counter_relations_valid": all(
                profile["counter_relations"]["prevented_covers_requested"]
                and profile["counter_relations"]["neutral_route_relation_valid"]
                for profile in evidence["profiles"]
            ),
            "all_capacity_relations_valid": all(
                profile["transition_capacity"]["capacity_relation_valid"]
                and profile["pending_routes"]["capacity_relation_valid"]
                for profile in evidence["profiles"]
            ),
        },
        "profiles": profile_summaries,
        "evidence_classification": {
            "deterministic_model_evidence": True,
            "physical_measurements": False,
            "physical_units": False,
            "universal_chip_claim": False,
            "proxy_labels_explicit": True,
        },
    }
    return add_digest(report, "report_digest")


def build_manifest(root: Path, primary: Mapping[str, bytes], source_commit: str) -> dict[str, Any]:
    sources = [source_record(root, path) for path in (WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS)]
    upstream = [source_record(root, path) for path in UPSTREAM_SOURCE_PATHS]
    artifacts = [
        {"path": path, "bytes": len(primary[path]), "raw_sha256": raw_digest(primary[path])}
        for path in PRIMARY_ARTIFACT_PATHS
    ]
    total_bytes = sum(item["bytes"] for item in artifacts)
    if any(item["bytes"] > CANONICAL_FILE_MAX_BYTES for item in artifacts):
        raise ContractError("canonical M27 artifact exceeds the per-file size bound")
    if total_bytes > CANONICAL_PRIMARY_SET_MAX_BYTES:
        raise ContractError("canonical M27 primary artifact set exceeds the size bound")
    manifest = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-stability-manifest",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "source_count": len(sources),
        "sources": sources,
        "upstream_dependency_count": len(upstream),
        "upstream_dependencies": upstream,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "artifact_set_digest": object_digest(artifacts),
        "retention_validation": {
            "canonical_file_max_bytes": CANONICAL_FILE_MAX_BYTES,
            "canonical_primary_set_max_bytes": CANONICAL_PRIMARY_SET_MAX_BYTES,
            "observed_primary_set_bytes": total_bytes,
            "all_primary_files_within_limit": True,
            "primary_set_within_limit": True,
            "raw_workflow_retention_days": RAW_RETENTION_DAYS,
            "recursive_metadata_exclusions": [MANIFEST_ARTIFACT, QUALIFICATION_ARTIFACT],
        },
    }
    return add_digest(manifest, "manifest_digest")


def _qualification_checks(
    contract: Mapping[str, Any],
    workload: Mapping[str, Any],
    evidence: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(category: str, evidence_value: Any) -> None:
        checks.append({
            "check_id": f"M27-Q{len(checks) + 1:03d}",
            "category": category,
            "status": "PASS",
            "evidence": evidence_value,
        })

    add("identity", contract["release"])
    add("identity", contract["source_commit"])
    for item in contract["required_scope"]:
        add("scope", item)
    for profile in evidence["profiles"]:
        add("workload", profile["workload_identity"]["workload_identity_digest"])
        add("scheduler", profile["scheduler_counts"])
        add("pending_route", profile["pending_routes"])
        add("transition_capacity", profile["transition_capacity"])
        add("counter_relation", profile["counter_relations"])
        add("boundary", profile["stability_boundary_record"])
        add("zero_event", profile["zero_event_record"]["retained_interval_count"])
        add("checkpoint_chain", profile["final_chain_digest"])
        add("bounded_runtime", profile["bounded_runtime_retention"])
    for definition in telemetry["telemetry"]:
        add("telemetry", definition["telemetry_id"])
    for schema_id in SCHEMA_PATHS:
        add("schema", schema_id)
    for dependency in manifest["upstream_dependencies"]:
        add("upstream_dependency", dependency["path"])
    for artifact in manifest["artifacts"]:
        add("canonical_artifact", artifact["path"])
    add("determinism", report["deterministic_rerun_requirement"])
    add("artifact_retention", manifest["retention_validation"])
    add("workload_catalog", workload["catalog_digest"])
    add("closure", "long-run stability and telemetry qualification is closed")
    return checks


def build_qualification(
    contract: Mapping[str, Any],
    workload: Mapping[str, Any],
    evidence: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    report: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    checks = _qualification_checks(contract, workload, evidence, telemetry, report, manifest)
    qualification = {
        "schema_version": VERSION,
        "artifact_id": "frp-m27-long-run-stability-qualification",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "workload_catalog_digest": workload["catalog_digest"],
        "checkpoint_evidence_digest": evidence["evidence_digest"],
        "telemetry_semantics_digest": telemetry["semantics_digest"],
        "report_digest": report["report_digest"],
        "manifest_digest": manifest["manifest_digest"],
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }
    return add_digest(qualification, "qualification_digest")


def build_outputs(root: Path, evidence_value: Mapping[str, Any], source_commit: str) -> dict[str, bytes]:
    root = root.resolve()
    evidence = validate_long_run_result(evidence_value, source_commit)
    contract = build_contract(source_commit)
    workload = build_workload_catalog(source_commit)
    telemetry = build_telemetry_semantics(source_commit)
    report = build_report(contract, workload, evidence, telemetry, source_commit)
    primary = {
        CONTRACT_ARTIFACT: document_bytes(contract),
        WORKLOAD_ARTIFACT: document_bytes(workload),
        CHECKPOINT_ARTIFACT: document_bytes(evidence),
        TELEMETRY_ARTIFACT: document_bytes(telemetry),
        REPORT_ARTIFACT: document_bytes(report),
    }
    manifest = build_manifest(root, primary, source_commit)
    qualification = build_qualification(contract, workload, evidence, telemetry, report, manifest, source_commit)
    outputs = {
        **primary,
        MANIFEST_ARTIFACT: document_bytes(manifest),
        QUALIFICATION_ARTIFACT: document_bytes(qualification),
    }
    for path, raw in outputs.items():
        if len(raw) > CANONICAL_FILE_MAX_BYTES:
            raise ContractError(f"canonical M27 artifact exceeds size limit: {path}")
    schemas = SchemaContext(root)
    mapping = {
        CONTRACT_ARTIFACT: CONTRACT_SCHEMA,
        WORKLOAD_ARTIFACT: WORKLOAD_SCHEMA,
        CHECKPOINT_ARTIFACT: CHECKPOINT_SCHEMA,
        TELEMETRY_ARTIFACT: TELEMETRY_SCHEMA,
        REPORT_ARTIFACT: REPORT_SCHEMA,
        MANIFEST_ARTIFACT: MANIFEST_SCHEMA,
        QUALIFICATION_ARTIFACT: QUALIFICATION_SCHEMA,
    }
    for artifact, schema in mapping.items():
        schemas.validate(schema, json.loads(outputs[artifact]), artifact)
    return outputs


def write_outputs(output_root: Path, outputs: Mapping[str, bytes]) -> None:
    for relative, raw in outputs.items():
        destination = path_for(output_root, relative)
        if destination.is_symlink():
            raise SafetyError(f"refusing artifact symlink destination: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)


def verify(root: Path, source_commit: str) -> dict[str, Any]:
    root = root.resolve()
    committed = {path: require_file(root, path).read_bytes() for path in ARTIFACT_PATHS}
    evidence = json.loads(committed[CHECKPOINT_ARTIFACT])
    expected = build_outputs(root, evidence, source_commit)
    mismatches = [path for path in ARTIFACT_PATHS if committed[path] != expected[path]]
    if mismatches:
        raise ContractError(f"committed M27 artifact mismatch: {mismatches}")
    return {
        "status": "PASS",
        "milestone": MILESTONE,
        "artifact_count": len(committed),
        "verified_artifacts": list(ARTIFACT_PATHS),
        "artifact_set_digest": object_digest([
            {"path": path, "bytes": len(committed[path]), "raw_sha256": raw_digest(committed[path])}
            for path in ARTIFACT_PATHS
        ]),
    }


def self_test(root: Path, source_commit: str) -> dict[str, Any]:
    verification = verify(root, source_commit)
    contract = json.loads(require_file(root, CONTRACT_ARTIFACT).read_text(encoding="utf-8"))
    evidence = json.loads(require_file(root, CHECKPOINT_ARTIFACT).read_text(encoding="utf-8"))
    telemetry = json.loads(require_file(root, TELEMETRY_ARTIFACT).read_text(encoding="utf-8"))
    report = json.loads(require_file(root, REPORT_ARTIFACT).read_text(encoding="utf-8"))
    manifest = json.loads(require_file(root, MANIFEST_ARTIFACT).read_text(encoding="utf-8"))
    checks = [
        contract["immutable_core"]["balanced_ternary_notation"] == "-1/0/1",
        contract["immutable_core"]["semantic_values"] == [-1, 0, 1],
        contract["immutable_core"]["temporal_scheduler_modes"] == ["1/7", "7/1"],
        [profile["scheduler_mode"] for profile in evidence["profiles"]] == ["free", "7/1", "1/7"],
        evidence["total_ticks"] == RUN_TICKS * len(PROFILE_SPECS),
        evidence["checkpoint_count"] == len(PROFILE_SPECS) * RUN_TICKS // CHECKPOINT_INTERVAL,
        all(profile["counter_relations"]["safety_counters_zero"] for profile in evidence["profiles"]),
        all(profile["zero_event_record"]["retained_interval_count"] > 0 for profile in evidence["profiles"]),
        telemetry["interpretation_boundary"]["physical_measurements_published"] is False,
        report["aggregate"]["all_profiles_passed"] is True,
        manifest["retention_validation"]["all_primary_files_within_limit"] is True,
        verification["artifact_count"] == len(ARTIFACT_PATHS),
    ]
    if not all(checks):
        raise ContractError("M27 self-test failed")
    return {
        "status": "PASS",
        "milestone": MILESTONE,
        "check_count": len(checks),
        "passed_count": sum(checks),
        "failed_count": len(checks) - sum(checks),
    }


def _load_json(path: str, label: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be a JSON object")
    return value


def _write_json_result(path: str | None, value: Mapping[str, Any]) -> None:
    text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run-long-run", action="store_true")
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--long-run-result")
    parser.add_argument("--source-commit", default=EXPECTED_M26_COMMIT)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.repository_root).resolve()
    source_commit = validate_source_commit(args.source_commit)
    if args.run_long_run:
        result = run_long_run(source_commit)
    elif args.generate:
        if not args.long_run_result:
            raise ContractError("--generate requires --long-run-result")
        evidence = _load_json(args.long_run_result, "M27 long-run result")
        outputs = build_outputs(root, evidence, source_commit)
        write_outputs(Path(args.output_root).resolve(), outputs)
        result = {
            "status": "PASS",
            "milestone": MILESTONE,
            "artifact_count": len(outputs),
            "artifacts": [
                {"path": path, "bytes": len(raw), "raw_sha256": raw_digest(raw)}
                for path, raw in outputs.items()
            ],
        }
    elif args.verify:
        result = verify(root, source_commit)
    else:
        result = self_test(root, source_commit)
    _write_json_result(args.output, result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, SafetyError) as exc:
        print(f"M27 qualification failure: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
