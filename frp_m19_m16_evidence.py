#!/usr/bin/env python3
"""Deterministic M19 publication of machine-readable M16 execution evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


VERSION = "2.1.0"
MILESTONE = "M19 — Machine-Readable M16 Execution and Qualification Evidence"
SOURCE_RELEASE = "FRP v1.8.0 / M16"
PRODUCER = "frp_m19_m16_evidence.py"
MONITOR = "verification/m19/frp_m19_m16_evidence_monitors.sv"
WORKFLOW = ".github/workflows/frp-m19-create-machine-readable-m16-evidence.yml"
TESTS = "tests/test_frp_m19_m16_evidence.py"
REGISTRY = "schemas/m19/frp_m19_schema_registry.json"
RAW_FORMAT = "frp.m19.m16_execution_raw.v1"
JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"

RTL_TRACE_SCHEMA = "frp.m16.rtl_execution_trace.v2.1.0"
FPGA_TRACE_SCHEMA = "frp.m16.fpga_preparation_execution_trace.v2.1.0"
RECORD_SCHEMA = "frp.m16.execution_record.v2.1.0"
TRACE_BASE_SCHEMA = "frp.m16.execution_trace_base.v2.1.0"
ZERO_SCHEMA = "frp.m16.zero_event_qualification.v2.1.0"
LAYER_MANIFEST_SCHEMA = "frp.m16.qualification_manifest.v2.1.0"
MANIFEST_SCHEMA = "frp.m19.machine_readable_evidence_manifest.v2.1.0"
QUALIFICATION_SCHEMA = "frp.m19.machine_readable_evidence_qualification.v2.1.0"

SCHEMA_PATHS = {
    RECORD_SCHEMA: "schemas/m19/frp_m16_execution_record.v2.1.0.schema.json",
    TRACE_BASE_SCHEMA: "schemas/m19/frp_m16_execution_trace_base.v2.1.0.schema.json",
    RTL_TRACE_SCHEMA: "schemas/m19/frp_m16_rtl_execution_trace.v2.1.0.schema.json",
    FPGA_TRACE_SCHEMA: "schemas/m19/frp_m16_fpga_preparation_execution_trace.v2.1.0.schema.json",
    ZERO_SCHEMA: "schemas/m19/frp_m16_zero_event_qualification.v2.1.0.schema.json",
    LAYER_MANIFEST_SCHEMA: "schemas/m19/frp_m16_qualification_manifest.v2.1.0.schema.json",
    MANIFEST_SCHEMA: "schemas/m19/frp_m19_machine_readable_evidence_manifest.v2.1.0.schema.json",
    QUALIFICATION_SCHEMA: "schemas/m19/frp_m19_machine_readable_evidence_qualification.v2.1.0.schema.json",
}

RTL_RAW = "artifacts/m19/raw/m16-rtl-execution.trace"
FPGA_RAW = "artifacts/m19/raw/m16-fpga-preparation-execution.trace"
RTL_TRACE = "artifacts/m19/execution/m16-rtl-execution-trace.json"
FPGA_TRACE = "artifacts/m19/execution/m16-fpga-preparation-execution-trace.json"
RTL_ZERO = "artifacts/m19/qualification/m16-rtl-zero-event-qualification.json"
FPGA_ZERO = "artifacts/m19/qualification/m16-fpga-preparation-zero-event-qualification.json"
RTL_MANIFEST = "artifacts/m19/qualification/m16-rtl-qualification-manifest.json"
FPGA_MANIFEST = "artifacts/m19/qualification/m16-fpga-preparation-qualification-manifest.json"
MANIFEST = "artifacts/m19/manifests/m19-machine-readable-evidence-manifest.json"
QUALIFICATION = "artifacts/m19/manifests/m19-machine-readable-evidence-qualification.json"

GENERATED_CORE_PATHS = (
    RTL_RAW,
    FPGA_RAW,
    RTL_TRACE,
    FPGA_TRACE,
    RTL_ZERO,
    FPGA_ZERO,
    RTL_MANIFEST,
    FPGA_MANIFEST,
)
GENERATED_PATHS = GENERATED_CORE_PATHS + (MANIFEST, QUALIFICATION)

RTL_SOURCES = tuple(
    f"rtl/m16/{name}"
    for name in (
        "frp_m16_pkg.sv",
        "frp_m16_scheduler.sv",
        "frp_m16_request_lanes.sv",
        "frp_m16_pending_routes.sv",
        "frp_m16_active_neutral.sv",
        "frp_m16_capacity_guard.sv",
        "frp_m16_state_update.sv",
        "frp_m16_core.sv",
        "frp_m16_assertions.sv",
        "frp_m16_tb.sv",
    )
)
FPGA_SOURCES = (
    *RTL_SOURCES[:-1],
    "fpga/m16/frp_m16_fpga_top.sv",
    "fpga/m16/frp_m16_fpga_tb.sv",
)
UPSTREAM_TELEMETRY_PATHS = (
    "artifacts/m18/structured_output/trace-free.json",
    "artifacts/m18/structured_output/trace-7-1.json",
    "artifacts/m18/structured_output/trace-1-7.json",
)
TECHNICAL_SOURCE_PATHS = tuple(
    sorted(
        {
            *RTL_SOURCES,
            *FPGA_SOURCES,
            *UPSTREAM_TELEMETRY_PATHS,
            MONITOR,
            PRODUCER,
            WORKFLOW,
            TESTS,
            REGISTRY,
            *SCHEMA_PATHS.values(),
        }
    )
)

LAYER_CONFIG = {
    "rtl": {
        "schema": RTL_TRACE_SCHEMA,
        "kind": "m16_rtl_execution_trace",
        "trace_path": RTL_TRACE,
        "raw_path": RTL_RAW,
        "zero_path": RTL_ZERO,
        "manifest_path": RTL_MANIFEST,
        "source_testbench": "rtl/m16/frp_m16_tb.sv",
        "source_files": RTL_SOURCES,
        "expected_records": 96,
        "expected_epochs": (("free", 16), ("7/1", 64), ("1/7", 16)),
        "qualified_commit": "ede53cf",
        "qualified_workflow": ".github/workflows/frp-m16-rtl-artifact-boundary.yml",
        "qualified_run": 84,
    },
    "fpga_preparation": {
        "schema": FPGA_TRACE_SCHEMA,
        "kind": "m16_fpga_preparation_execution_trace",
        "trace_path": FPGA_TRACE,
        "raw_path": FPGA_RAW,
        "zero_path": FPGA_ZERO,
        "manifest_path": FPGA_MANIFEST,
        "source_testbench": "fpga/m16/frp_m16_fpga_tb.sv",
        "source_files": FPGA_SOURCES,
        "expected_records": 4,
        "expected_epochs": (("free", 3), ("1/7", 1)),
        "qualified_commit": "ede53cf",
        "qualified_workflow": ".github/workflows/frp-m16-fpga-preparation.yml",
        "qualified_run": 2,
    },
}

MODE_NAMES = {0: "free", 1: "7/1", 2: "1/7"}
STATE_NAMES = {0: "free", 1: "balance", 2: "commit", 3: "excite", 4: "neutralize"}
INVARIANT_NAMES = (
    "state_domain_valid",
    "scheduler_counts_valid",
    "request_lane_order_valid",
    "pending_polarity_valid",
    "active_neutral_valid",
    "transition_capacity_valid",
    "state_update_valid",
    "no_actual_direct_events",
    "no_reserved_state",
    "no_queue_overflow",
)
HEX_FIELDS = {
    "scheduler_mode",
    "scheduler_state",
    "request_valid",
    "request_cell_index",
    "request_target",
    "phase_target",
    "state_before",
    "pending_before",
    "request_accept",
    "request_reject",
    "accepted_cell_mask",
    "neutral_routed_cell_mask",
    "accepted_change_mask",
    "invariant_flags",
    "state_after",
    "pending_after",
}
RAW_FIELD_NAMES = (
    "sequence",
    "core_ready",
    "scheduler_mode",
    "scheduler_state",
    "ticks_before",
    "request_valid",
    "request_cell_index",
    "request_target",
    "phase_target",
    "state_before",
    "pending_before",
    "request_accept",
    "request_reject",
    "accepted_cell_mask",
    "neutral_routed_cell_mask",
    "accepted_change_mask",
    "accepted_changes",
    "capacity_remaining",
    "capacity_exhausted",
    "switch_load_numerator",
    "requested_direct_events",
    "prevented_direct_events",
    "neutral_routed_events",
    "actual_direct_events",
    "reserved_state_events",
    "queue_overflow_events",
    "invariant_flags",
    "state_after",
    "pending_after",
    "ticks_after",
    "count_free",
    "count_balance",
    "count_commit",
    "count_excite",
    "count_neutralize",
)

SELF_TEST_CASE_IDS = (
    "canonical_json",
    "raw_sha256",
    "artifact_set_digest",
    "safe_relative_path",
    "unsafe_parent_path",
    "unsafe_absolute_path",
    "ternary_decode_zero",
    "ternary_decode_positive",
    "ternary_decode_negative",
    "ternary_decode_reserved",
    "packed_state_order",
    "mask_cell_order",
    "scheduler_free",
    "scheduler_7_1_balance",
    "scheduler_7_1_commit",
    "scheduler_1_7_excite",
    "scheduler_1_7_neutralize",
    "invariant_vector",
    "counter_relation",
    "raw_record_parser",
)


class M19Error(Exception):
    """Base M19 failure."""


class ContractError(M19Error):
    """Artifact or semantic contract failure."""


class ConfigurationError(M19Error):
    """Command-line or environment failure."""


class SafetyError(M19Error):
    """Filesystem safety-boundary failure."""


class ContractArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ConfigurationError(message)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def parse_json_bytes(raw: bytes, subject: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ContractError(f"non-finite JSON value in {subject}: {value}")

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"duplicate JSON key in {subject}: {key}")
            result[key] = value
        return result

    try:
        return json.loads(
            raw.decode("utf-8"),
            parse_constant=reject_constant,
            object_pairs_hook=unique_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON in {subject}: {exc}") from exc


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise SafetyError("empty repository-relative path")
    if "\\" in value or "\x00" in value:
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    return path


def _reject_symlink_components(path: Path, stop: Path | None = None) -> None:
    current = path
    limit = stop.resolve() if stop is not None else None
    while True:
        if current.exists() and current.is_symlink():
            raise SafetyError(f"symbolic-link component rejected: {current}")
        if limit is not None and current.resolve(strict=False) == limit:
            break
        if current.parent == current:
            break
        current = current.parent


def repository_root(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = Path.cwd() / path
    _reject_symlink_components(path)
    resolved = path.resolve(strict=True)
    if not resolved.is_dir() or resolved.is_symlink():
        raise SafetyError(f"unsafe repository root: {resolved}")
    return resolved


def source_file(root: Path, relative: str) -> Path:
    path = safe_relative_path(relative)
    candidate = root.joinpath(*path.parts)
    _reject_symlink_components(candidate, root)
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ContractError(f"missing source file: {relative}") from exc
    if root not in resolved.parents or resolved.is_symlink():
        raise SafetyError(f"source escapes repository: {relative}")
    mode = resolved.lstat().st_mode
    if not stat.S_ISREG(mode) or resolved.stat().st_size <= 0:
        raise ContractError(f"invalid source file: {relative}")
    return resolved


def read_source(root: Path, relative: str) -> bytes:
    return source_file(root, relative).read_bytes()


def file_record(root: Path, relative: str, role: str) -> dict[str, Any]:
    raw = read_source(root, relative)
    return {
        "byte_length": len(raw),
        "path": relative,
        "raw_sha256": sha256_bytes(raw),
        "role": role,
    }


def output_root(value: str | Path, root: Path, replace: bool) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = Path.cwd() / path
    _reject_symlink_components(path)
    resolved = path.resolve(strict=False)
    if resolved == Path("/") or resolved == Path("/tmp"):
        raise SafetyError(f"unsafe output root: {resolved}")
    if resolved == root or root in resolved.parents or resolved in root.parents:
        raise SafetyError("output root overlaps repository")
    if resolved.exists():
        if resolved.is_symlink() or not resolved.is_dir():
            raise SafetyError(f"unsafe output root: {resolved}")
        if any(resolved.iterdir()) and not replace:
            raise ConfigurationError("output root is not empty; use --replace")
        if replace:
            shutil.rmtree(resolved)
    resolved.mkdir(mode=0o700, parents=True, exist_ok=True)
    return resolved


def _state(code: int) -> int:
    if code == 0:
        return 0
    if code == 1:
        return 1
    if code == 3:
        return -1
    raise ContractError(f"reserved or invalid ternary code: {code}")


def _states(packed: int, count: int = 8) -> list[int]:
    values = [_state((packed >> (2 * index)) & 0b11) for index in range(count)]
    if packed >> (2 * count):
        raise ContractError("packed state exceeds declared cell count")
    return values


def _cells(mask: int, count: int = 8) -> list[int]:
    if mask >> count:
        raise ContractError("cell mask exceeds declared cell count")
    return [index for index in range(count) if (mask >> index) & 1]


def _expected_scheduler_state(mode: str, tick: int) -> str:
    if mode == "free":
        return "free"
    if mode == "7/1":
        return "commit" if tick % 8 == 7 else "balance"
    if mode == "1/7":
        return "excite" if tick % 8 == 0 else "neutralize"
    raise ContractError(f"unsupported scheduler mode: {mode}")


def _parse_unsigned(value: str, base: int, field: str) -> int:
    pattern = r"[0-9a-fA-F]+" if base == 16 else r"[0-9]+"
    if re.fullmatch(pattern, value) is None:
        raise ContractError(f"invalid {field} value in raw record: {value!r}")
    return int(value, base)


def _raw_lines(path: Path, expected_layer: str) -> tuple[list[str], list[dict[str, int]]]:
    _reject_symlink_components(path)
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ContractError(f"missing execution log: {path}") from exc
    if resolved.is_symlink() or not stat.S_ISREG(resolved.lstat().st_mode):
        raise SafetyError(f"unsafe execution log: {resolved}")
    try:
        text = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"execution log is not UTF-8: {resolved}") from exc
    lines = [line for line in text.splitlines() if line.startswith("FRP_M19|")]
    if not lines:
        raise ContractError(f"no FRP M19 records in execution log: {resolved}")
    records: list[dict[str, int]] = []
    for index, line in enumerate(lines):
        parts = line.split("|")
        if len(parts) != 38:
            raise ContractError(f"raw record field count mismatch at line {index}")
        marker, raw_version, layer, *values = parts
        if marker != "FRP_M19" or raw_version != "1" or layer != expected_layer:
            raise ContractError(f"raw record identity mismatch at line {index}")
        record: dict[str, int] = {}
        for name, value in zip(RAW_FIELD_NAMES, values, strict=True):
            record[name] = _parse_unsigned(value, 16 if name in HEX_FIELDS else 10, name)
        records.append(record)
    return lines, records


def _canonical_raw(lines: Sequence[str]) -> bytes:
    if any("\r" in line or "\n" in line for line in lines):
        raise ContractError("embedded line ending in raw record")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _request_lanes(record: Mapping[str, int]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for lane in range(2):
        valid = bool((record["request_valid"] >> lane) & 1)
        accepted = bool((record["request_accept"] >> lane) & 1)
        rejected = bool((record["request_reject"] >> lane) & 1)
        if accepted and rejected:
            raise ContractError(f"lane {lane} is both accepted and rejected")
        if (accepted or rejected) != valid:
            raise ContractError(f"lane {lane} disposition does not match validity")
        cell_index = (record["request_cell_index"] >> (3 * lane)) & 0b111
        target_code = (record["request_target"] >> (2 * lane)) & 0b11
        result.append(
            {
                "accepted": accepted,
                "cell_index": cell_index,
                "lane": lane,
                "rejected": rejected,
                "target_state": _state(target_code),
                "valid": valid,
            }
        )
    if record["request_valid"] >> 2:
        raise ContractError("request-valid mask exceeds declared lane count")
    if record["request_accept"] >> 2 or record["request_reject"] >> 2:
        raise ContractError("request disposition mask exceeds declared lane count")
    if record["request_cell_index"] >> 6 or record["request_target"] >> 4:
        raise ContractError("packed request bus exceeds declared width")
    return result


def _invariant_vector(mask: int) -> dict[str, Any]:
    if mask >> len(INVARIANT_NAMES):
        raise ContractError("invariant mask exceeds declared width")
    flags = [
        {"name": name, "pass": bool((mask >> index) & 1)}
        for index, name in enumerate(INVARIANT_NAMES)
    ]
    return {"all_pass": all(item["pass"] for item in flags), "flags": flags}


def _validate_state_transition(before: Sequence[int], after: Sequence[int]) -> None:
    if len(before) != 8 or len(after) != 8:
        raise ContractError("retained-state vector length mismatch")
    for index, (left, right) in enumerate(zip(before, after, strict=True)):
        if (left, right) in ((-1, 1), (1, -1)):
            raise ContractError(f"direct opposite-polarity transition at cell {index}")


def _upstream_telemetry_context(root: Path) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    for relative in UPSTREAM_TELEMETRY_PATHS:
        raw = read_source(root, relative)
        payload = parse_json_bytes(raw, relative)
        if not isinstance(payload, dict):
            raise ContractError(f"upstream telemetry artifact is not an object: {relative}")
        schema = payload.get("schema")
        trace = payload.get("trace")
        if schema != "frp.structured_output.v1.7.0":
            raise ContractError(f"unexpected upstream telemetry schema: {relative}")
        if not isinstance(trace, list) or len(trace) != 64:
            raise ContractError(f"unexpected upstream telemetry trace length: {relative}")
        required = {
            "C_q16",
            "P_q16",
            "C_minus_P_q16",
            "global_phase_coherence_q30",
            "heat_global_q16",
            "switch_load_q16",
        }
        if any(not isinstance(row, dict) or not required.issubset(row) for row in trace):
            raise ContractError(f"upstream telemetry fields missing: {relative}")
        artifacts.append(
            {
                "path": relative,
                "raw_sha256": sha256_bytes(raw),
                "record_count": len(trace),
                "schema": schema,
            }
        )
    return {
        "m15_semantic_reference": {
            "availability": "external_upstream_canonical_artifacts",
            "artifacts": artifacts,
            "correlation_status": "not_evaluated_in_m19",
            "quantities": [
                "C_q16",
                "P_q16",
                "C_minus_P_q16",
                "global_phase_coherence_q30",
                "heat_global_q16",
            ],
        },
        "m16_execution": {
            "availability": "emitted_by_m16_execution_boundary",
            "quantities": [
                "accepted_changes",
                "capacity_remaining",
                "switch_load_numerator",
                "switch_load_q16",
                "requested_direct_events",
                "prevented_direct_events",
                "neutral_routed_events",
                "actual_direct_events",
                "reserved_state_events",
                "queue_overflow_events",
            ],
        },
        "physical_measurement": {
            "availability": "not_in_scope",
            "correlation_status": "not_evaluated",
        },
    }


def build_trace(
    root: Path,
    layer: str,
    raw_bytes: bytes,
    raw_records: Sequence[Mapping[str, int]],
) -> dict[str, Any]:
    if layer not in LAYER_CONFIG:
        raise ContractError(f"unsupported M16 evidence layer: {layer}")
    config = LAYER_CONFIG[layer]
    expected_records = int(config["expected_records"])
    if len(raw_records) != expected_records:
        raise ContractError(
            f"{layer} record count mismatch: {len(raw_records)} != {expected_records}"
        )

    records: list[dict[str, Any]] = []
    epochs: list[dict[str, Any]] = []
    epoch_index = -1
    epoch_mode = ""
    epoch_length = 0

    for expected_sequence, raw in enumerate(raw_records):
        if raw["sequence"] != expected_sequence:
            raise ContractError(f"{layer} sequence mismatch at {expected_sequence}")
        if raw["core_ready"] != 1:
            raise ContractError(f"{layer} record observed before core readiness")
        try:
            mode = MODE_NAMES[raw["scheduler_mode"]]
            scheduler_state = STATE_NAMES[raw["scheduler_state"]]
        except KeyError as exc:
            raise ContractError(f"reserved scheduler code in {layer} record") from exc

        if raw["ticks_before"] == 0:
            if epoch_index >= 0:
                epochs.append(
                    {
                        "epoch": epoch_index,
                        "mode": epoch_mode,
                        "record_count": epoch_length,
                    }
                )
            epoch_index += 1
            epoch_mode = mode
            epoch_length = 0
        elif epoch_index < 0:
            raise ContractError(f"{layer} first record does not begin at tick zero")

        if mode != epoch_mode:
            raise ContractError(f"{layer} scheduler mode changes inside an epoch")
        if raw["ticks_before"] != epoch_length:
            raise ContractError(f"{layer} tick order mismatch in epoch {epoch_index}")
        if raw["ticks_after"] != raw["ticks_before"] + 1:
            raise ContractError(f"{layer} tick counter did not increment exactly once")
        if scheduler_state != _expected_scheduler_state(mode, raw["ticks_before"]):
            raise ContractError(f"{layer} scheduler-state relation mismatch")

        counters = {
            "balance": raw["count_balance"],
            "commit": raw["count_commit"],
            "excite": raw["count_excite"],
            "free": raw["count_free"],
            "neutralize": raw["count_neutralize"],
        }
        if sum(counters.values()) != raw["ticks_after"]:
            raise ContractError(f"{layer} scheduler-counter sum mismatch")
        if counters[scheduler_state] <= 0:
            raise ContractError(f"{layer} active scheduler counter did not advance")

        requests = _request_lanes(raw)
        state_before = _states(raw["state_before"])
        state_after = _states(raw["state_after"])
        pending_before = _states(raw["pending_before"])
        pending_after = _states(raw["pending_after"])
        phase_targets = _states(raw["phase_target"])
        _validate_state_transition(state_before, state_after)

        accepted_cell_ids = _cells(raw["accepted_cell_mask"])
        neutral_routed_cell_ids = _cells(raw["neutral_routed_cell_mask"])
        accepted_change_cell_ids = _cells(raw["accepted_change_mask"])
        if raw["accepted_changes"] != len(accepted_change_cell_ids):
            raise ContractError(f"{layer} accepted-change mask mismatch")
        if raw["accepted_changes"] > 2:
            raise ContractError(f"{layer} transition capacity exceeded")
        if raw["capacity_remaining"] != 2 - raw["accepted_changes"]:
            raise ContractError(f"{layer} capacity-remaining relation mismatch")
        if bool(raw["capacity_exhausted"]) != (raw["capacity_remaining"] == 0):
            raise ContractError(f"{layer} capacity-exhausted relation mismatch")
        if raw["switch_load_numerator"] != raw["accepted_changes"]:
            raise ContractError(f"{layer} switch-load relation mismatch")
        if any(
            raw[field] != 0
            for field in (
                "actual_direct_events",
                "reserved_state_events",
                "queue_overflow_events",
            )
        ):
            raise ContractError(f"{layer} zero-event invariant failed")
        invariants = _invariant_vector(raw["invariant_flags"])
        if not invariants["all_pass"]:
            raise ContractError(f"{layer} invariant vector is incomplete")

        records.append(
            {
                "accepted_cell_ids": accepted_cell_ids,
                "accepted_change_cell_ids": accepted_change_cell_ids,
                "core_ready": True,
                "events": {
                    "actual_direct_events": raw["actual_direct_events"],
                    "neutral_routed_events": raw["neutral_routed_events"],
                    "prevented_direct_events": raw["prevented_direct_events"],
                    "queue_overflow_events": raw["queue_overflow_events"],
                    "requested_direct_events": raw["requested_direct_events"],
                    "reserved_state_events": raw["reserved_state_events"],
                },
                "execution_epoch": epoch_index,
                "invariants": invariants,
                "neutral_routed_cell_ids": neutral_routed_cell_ids,
                "pending_route_after": pending_after,
                "pending_route_before": pending_before,
                "phase_derived_targets": phase_targets,
                "requests": requests,
                "retained_state_after": state_after,
                "retained_state_before": state_before,
                "scheduler": {
                    "counters_after": counters,
                    "mode": mode,
                    "state": scheduler_state,
                    "ticks_after": raw["ticks_after"],
                    "ticks_before": raw["ticks_before"],
                },
                "sequence": expected_sequence,
                "telemetry": {
                    "switch_load_denominator": 8,
                    "switch_load_numerator": raw["switch_load_numerator"],
                    "switch_load_q16": raw["switch_load_numerator"] * 8192,
                },
                "transition_capacity": {
                    "accepted_changes": raw["accepted_changes"],
                    "capacity_exhausted": bool(raw["capacity_exhausted"]),
                    "capacity_limit": 2,
                    "capacity_remaining": raw["capacity_remaining"],
                },
            }
        )
        epoch_length += 1

    epochs.append(
        {"epoch": epoch_index, "mode": epoch_mode, "record_count": epoch_length}
    )
    expected_epochs = [
        {"epoch": index, "mode": mode, "record_count": count}
        for index, (mode, count) in enumerate(config["expected_epochs"])
    ]
    if epochs != expected_epochs:
        raise ContractError(f"{layer} execution-epoch profile mismatch")

    state_counts = Counter(record["scheduler"]["state"] for record in records)
    event_totals = {
        name: sum(record["events"][name] for record in records)
        for name in records[0]["events"]
    }
    record_digest = sha256_bytes(canonical_json_bytes(records))
    return {
        "configuration": {
            "cells": 8,
            "counter_bits": 32,
            "request_lanes": 2,
            "state_bits": 2,
            "transition_fraction_denominator": 4,
            "transition_fraction_numerator": 1,
        },
        "execution_epochs": epochs,
        "kind": config["kind"],
        "layer": layer,
        "measurement_contours": _upstream_telemetry_context(root),
        "milestone": MILESTONE,
        "monitor": MONITOR,
        "qualified_source": {
            "branch": "main",
            "commit": config["qualified_commit"],
            "commit_identity_format": "short_git_sha",
            "result": "SUCCESS",
            "workflow": config["qualified_workflow"],
            "workflow_run": config["qualified_run"],
        },
        "raw_trace": {
            "byte_length": len(raw_bytes),
            "format": RAW_FORMAT,
            "path": config["raw_path"],
            "raw_sha256": sha256_bytes(raw_bytes),
            "record_count": len(records),
        },
        "records": records,
        "schema": config["schema"],
        "source_release": SOURCE_RELEASE,
        "source_testbench": config["source_testbench"],
        "summary": {
            "event_totals": event_totals,
            "execution_epoch_count": len(epochs),
            "invariant_pass_records": sum(
                1 for record in records if record["invariants"]["all_pass"]
            ),
            "maximum_switch_load_numerator": max(
                record["telemetry"]["switch_load_numerator"] for record in records
            ),
            "record_count": len(records),
            "record_digest": record_digest,
            "scheduler_state_counts": dict(sorted(state_counts.items())),
            "total_accepted_changes": sum(
                record["transition_capacity"]["accepted_changes"]
                for record in records
            ),
            "zero_event_status": "PASS",
        },
        "version": VERSION,
    }


class SchemaContext:
    def __init__(self, root: Path) -> None:
        registry_raw = read_source(root, REGISTRY)
        registry = parse_json_bytes(registry_raw, REGISTRY)
        if not isinstance(registry, dict):
            raise ContractError("M19 schema registry is not an object")
        expected_keys = {"kind", "milestone", "records", "schema", "version"}
        if set(registry) != expected_keys:
            raise ContractError("M19 schema registry field set mismatch")
        if registry.get("schema") != "frp.m19.schema_registry.v2.1.0":
            raise ContractError("M19 schema registry identity mismatch")
        if registry.get("kind") != "m19_schema_registry":
            raise ContractError("M19 schema registry kind mismatch")
        if registry.get("milestone") != MILESTONE or registry.get("version") != VERSION:
            raise ContractError("M19 schema registry version boundary mismatch")
        records = registry.get("records")
        if not isinstance(records, list) or len(records) != len(SCHEMA_PATHS):
            raise ContractError("M19 schema registry record count mismatch")
        identifiers = [record.get("schema_identifier") for record in records if isinstance(record, dict)]
        if identifiers != sorted(SCHEMA_PATHS):
            raise ContractError("M19 schema registry identifier ordering mismatch")

        self.schemas: dict[str, dict[str, Any]] = {}
        for record in records:
            if set(record) != {"artifact_paths", "schema_identifier", "schema_path", "schema_urn"}:
                raise ContractError("M19 schema registry record field mismatch")
            identifier = record["schema_identifier"]
            expected_path = SCHEMA_PATHS.get(identifier)
            if record["schema_path"] != expected_path:
                raise ContractError(f"M19 schema path mismatch: {identifier}")
            expected_urn = f"urn:frp:schema:{identifier}"
            if record["schema_urn"] != expected_urn:
                raise ContractError(f"M19 schema URN mismatch: {identifier}")
            artifact_paths = record["artifact_paths"]
            if not isinstance(artifact_paths, list) or artifact_paths != sorted(artifact_paths):
                raise ContractError(f"M19 schema artifact ordering mismatch: {identifier}")
            raw = read_source(root, expected_path)
            schema = parse_json_bytes(raw, expected_path)
            if not isinstance(schema, dict):
                raise ContractError(f"M19 schema is not an object: {identifier}")
            if schema.get("$schema") != JSON_SCHEMA_DIALECT:
                raise ContractError(f"M19 schema dialect mismatch: {identifier}")
            if schema.get("$id") != expected_urn:
                raise ContractError(f"M19 schema $id mismatch: {identifier}")
            if schema.get("x-frp-schema-identifier") != identifier:
                raise ContractError(f"M19 schema identity extension mismatch: {identifier}")
            Draft202012Validator.check_schema(schema)
            self._validate_refs(schema, identifier)
            self.schemas[identifier] = schema

        resources = [
            (schema["$id"], Resource.from_contents(schema))
            for schema in self.schemas.values()
        ]
        self.registry = Registry().with_resources(resources)

    @staticmethod
    def _validate_refs(node: Any, identifier: str) -> None:
        stack = [node]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                reference = value.get("$ref")
                if isinstance(reference, str) and not (
                    reference.startswith("#")
                    or reference
                    in {f"urn:frp:schema:{item}" for item in SCHEMA_PATHS}
                ):
                    raise ContractError(f"unregistered $ref in M19 schema: {identifier}")
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)

    def validate(self, identifier: str, value: Any, subject: str) -> None:
        try:
            schema = self.schemas[identifier]
        except KeyError as exc:
            raise ContractError(f"unregistered M19 schema: {identifier}") from exc
        validator = Draft202012Validator(
            schema,
            registry=self.registry,
        )
        errors = sorted(validator.iter_errors(value), key=lambda item: list(item.path))
        if errors:
            first = errors[0]
            location = "/".join(str(part) for part in first.absolute_path) or "<root>"
            raise ContractError(f"schema validation failed for {subject} at {location}: {first.message}")


def build_zero_qualification(layer: str, trace: Mapping[str, Any]) -> dict[str, Any]:
    records = trace["records"]
    event_fields = (
        "actual_direct_events",
        "reserved_state_events",
        "queue_overflow_events",
    )
    totals = {
        name: sum(record["events"][name] for record in records)
        for name in event_fields
    }
    maxima = {
        name: max(record["events"][name] for record in records)
        for name in event_fields
    }
    invariant_records = sum(1 for record in records if record["invariants"]["all_pass"])
    status = (
        "PASS"
        if all(value == 0 for value in totals.values())
        and all(value == 0 for value in maxima.values())
        and invariant_records == len(records)
        else "FAIL"
    )
    return {
        "event_maxima": maxima,
        "event_totals": totals,
        "invariant_pass_records": invariant_records,
        "kind": "m16_zero_event_qualification",
        "layer": layer,
        "milestone": MILESTONE,
        "record_count": len(records),
        "record_digest": trace["summary"]["record_digest"],
        "schema": ZERO_SCHEMA,
        "status": status,
        "trace_path": LAYER_CONFIG[layer]["trace_path"],
        "version": VERSION,
    }


def _record_for_bytes(path: str, role: str, raw: bytes, schema: str | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "byte_length": len(raw),
        "path": path,
        "raw_sha256": sha256_bytes(raw),
        "role": role,
    }
    if schema is not None:
        record["schema"] = schema
    return record


def build_layer_manifest(
    root: Path,
    layer: str,
    raw_bytes: bytes,
    trace_bytes: bytes,
    zero_bytes: bytes,
) -> dict[str, Any]:
    config = LAYER_CONFIG[layer]
    sources = tuple(config["source_files"]) + (MONITOR, PRODUCER)
    source_records = [file_record(root, path, "source") for path in sorted(sources)]
    artifact_records = [
        _record_for_bytes(config["raw_path"], "raw_execution_trace", raw_bytes),
        _record_for_bytes(config["trace_path"], "execution_trace", trace_bytes, config["schema"]),
        _record_for_bytes(config["zero_path"], "zero_event_qualification", zero_bytes, ZERO_SCHEMA),
    ]
    digest_input = [
        {"path": record["path"], "raw_sha256": record["raw_sha256"]}
        for record in [*source_records, *artifact_records]
    ]
    return {
        "artifact_set_digest": sha256_bytes(canonical_json_bytes(digest_input)),
        "artifacts": artifact_records,
        "kind": "m16_qualification_manifest",
        "layer": layer,
        "milestone": MILESTONE,
        "qualified_source": {
            "branch": "main",
            "commit": config["qualified_commit"],
            "commit_identity_format": "short_git_sha",
            "result": "SUCCESS",
            "workflow": config["qualified_workflow"],
            "workflow_run": config["qualified_run"],
        },
        "schema": LAYER_MANIFEST_SCHEMA,
        "sources": source_records,
        "status": "PASS",
        "version": VERSION,
    }


def _artifact_set_digest(records: Sequence[Mapping[str, Any]]) -> str:
    digest_input = [
        {
            "byte_length": record["byte_length"],
            "path": record["path"],
            "raw_sha256": record["raw_sha256"],
        }
        for record in records
    ]
    return sha256_bytes(canonical_json_bytes(digest_input))


def build_manifest(root: Path, core: Mapping[str, bytes]) -> dict[str, Any]:
    if set(core) != set(GENERATED_CORE_PATHS):
        raise ContractError("M19 generated core path set mismatch")
    schema_by_path = {
        RTL_TRACE: RTL_TRACE_SCHEMA,
        FPGA_TRACE: FPGA_TRACE_SCHEMA,
        RTL_ZERO: ZERO_SCHEMA,
        FPGA_ZERO: ZERO_SCHEMA,
        RTL_MANIFEST: LAYER_MANIFEST_SCHEMA,
        FPGA_MANIFEST: LAYER_MANIFEST_SCHEMA,
    }
    roles = {
        RTL_RAW: "raw_execution_trace",
        FPGA_RAW: "raw_execution_trace",
        RTL_TRACE: "execution_trace",
        FPGA_TRACE: "execution_trace",
        RTL_ZERO: "zero_event_qualification",
        FPGA_ZERO: "zero_event_qualification",
        RTL_MANIFEST: "layer_qualification_manifest",
        FPGA_MANIFEST: "layer_qualification_manifest",
    }
    artifacts = [
        _record_for_bytes(path, roles[path], core[path], schema_by_path.get(path))
        for path in sorted(core)
    ]
    sources = [file_record(root, path, "technical_source") for path in TECHNICAL_SOURCE_PATHS]
    return {
        "artifact_count": len(artifacts),
        "artifact_set_digest": _artifact_set_digest(artifacts),
        "artifacts": artifacts,
        "kind": "m19_machine_readable_evidence_manifest",
        "milestone": MILESTONE,
        "schema": MANIFEST_SCHEMA,
        "source_count": len(sources),
        "source_set_digest": _artifact_set_digest(sources),
        "sources": sources,
        "version": VERSION,
    }


def _check(checks: list[dict[str, Any]], check_id: str, category: str, passed: bool) -> None:
    checks.append(
        {
            "category": category,
            "check_id": check_id,
            "status": "PASS" if passed else "FAIL",
        }
    )


def build_qualification(
    root: Path,
    schema_context: SchemaContext,
    core: Mapping[str, bytes],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    parsed: dict[str, Any] = {}
    schema_bindings = {
        RTL_TRACE: RTL_TRACE_SCHEMA,
        FPGA_TRACE: FPGA_TRACE_SCHEMA,
        RTL_ZERO: ZERO_SCHEMA,
        FPGA_ZERO: ZERO_SCHEMA,
        RTL_MANIFEST: LAYER_MANIFEST_SCHEMA,
        FPGA_MANIFEST: LAYER_MANIFEST_SCHEMA,
    }
    for path, identifier in schema_bindings.items():
        value = parse_json_bytes(core[path], path)
        schema_context.validate(identifier, value, path)
        parsed[path] = value
        _check(checks, f"schema:{path}", "formal_schema", True)
        _check(
            checks,
            f"canonical:{path}",
            "serialization",
            canonical_json_bytes(value) == core[path],
        )

    schema_context.validate(MANIFEST_SCHEMA, manifest, MANIFEST)
    _check(checks, "schema:manifest", "formal_schema", True)
    _check(checks, "manifest:artifact_count", "manifest", manifest["artifact_count"] == 8)
    _check(
        checks,
        "manifest:artifact_digest",
        "manifest",
        manifest["artifact_set_digest"] == _artifact_set_digest(manifest["artifacts"]),
    )
    _check(
        checks,
        "manifest:source_digest",
        "manifest",
        manifest["source_set_digest"] == _artifact_set_digest(manifest["sources"]),
    )

    for layer in ("rtl", "fpga_preparation"):
        config = LAYER_CONFIG[layer]
        trace = parsed[config["trace_path"]]
        zero = parsed[config["zero_path"]]
        layer_manifest = parsed[config["manifest_path"]]
        prefix = layer.replace("_preparation", "")
        _check(
            checks,
            f"{prefix}:record_count",
            "execution",
            trace["summary"]["record_count"] == config["expected_records"],
        )
        _check(
            checks,
            f"{prefix}:epoch_profile",
            "execution",
            tuple((item["mode"], item["record_count"]) for item in trace["execution_epochs"])
            == tuple(config["expected_epochs"]),
        )
        _check(
            checks,
            f"{prefix}:zero_events",
            "invariant",
            zero["status"] == "PASS"
            and all(value == 0 for value in zero["event_totals"].values()),
        )
        _check(
            checks,
            f"{prefix}:invariant_vectors",
            "invariant",
            zero["invariant_pass_records"] == zero["record_count"],
        )
        _check(
            checks,
            f"{prefix}:raw_digest",
            "digest",
            trace["raw_trace"]["raw_sha256"] == sha256_bytes(core[config["raw_path"]]),
        )
        _check(
            checks,
            f"{prefix}:record_digest",
            "digest",
            trace["summary"]["record_digest"]
            == sha256_bytes(canonical_json_bytes(trace["records"])),
        )
        _check(
            checks,
            f"{prefix}:layer_manifest",
            "manifest",
            layer_manifest["status"] == "PASS" and len(layer_manifest["artifacts"]) == 3,
        )
        _check(
            checks,
            f"{prefix}:qualified_source",
            "provenance",
            trace["qualified_source"] == layer_manifest["qualified_source"],
        )
        _check(
            checks,
            f"{prefix}:measurement_contours",
            "contour",
            trace["measurement_contours"]["m15_semantic_reference"]["correlation_status"]
            == "not_evaluated_in_m19"
            and trace["measurement_contours"]["physical_measurement"]["availability"]
            == "not_in_scope",
        )

    _check(
        checks,
        "ternary:canonical_domain",
        "semantic",
        all(
            value in (-1, 0, 1)
            for path in (RTL_TRACE, FPGA_TRACE)
            for record in parsed[path]["records"]
            for field in (
                "retained_state_before",
                "retained_state_after",
                "pending_route_before",
                "pending_route_after",
                "phase_derived_targets",
            )
            for value in record[field]
        ),
    )
    _check(
        checks,
        "active_neutral:no_direct_transition",
        "semantic",
        all(
            (left, right) not in ((-1, 1), (1, -1))
            for path in (RTL_TRACE, FPGA_TRACE)
            for record in parsed[path]["records"]
            for left, right in zip(
                record["retained_state_before"],
                record["retained_state_after"],
                strict=True,
            )
        ),
    )
    _check(
        checks,
        "sources:current_bytes",
        "provenance",
        all(
            file_record(root, record["path"], record["role"]) == record
            for record in manifest["sources"]
        ),
    )

    failed = sum(check["status"] != "PASS" for check in checks)
    return {
        "check_count": len(checks),
        "checks": checks,
        "failed_count": failed,
        "kind": "m19_machine_readable_evidence_qualification",
        "manifest_path": MANIFEST,
        "manifest_raw_sha256": sha256_bytes(canonical_json_bytes(manifest)),
        "milestone": MILESTONE,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "passed_count": len(checks) - failed,
        "schema": QUALIFICATION_SCHEMA,
        "version": VERSION,
    }


def generate_records(root: Path, rtl_log: Path, fpga_log: Path) -> dict[str, bytes]:
    schema_context = SchemaContext(root)
    logs = {"rtl": rtl_log, "fpga_preparation": fpga_log}
    core: dict[str, bytes] = {}
    for layer, log_path in logs.items():
        config = LAYER_CONFIG[layer]
        lines, raw_records = _raw_lines(log_path, layer)
        raw = _canonical_raw(lines)
        trace = build_trace(root, layer, raw, raw_records)
        schema_context.validate(config["schema"], trace, config["trace_path"])
        trace_raw = canonical_json_bytes(trace)
        zero = build_zero_qualification(layer, trace)
        schema_context.validate(ZERO_SCHEMA, zero, config["zero_path"])
        zero_raw = canonical_json_bytes(zero)
        layer_manifest = build_layer_manifest(root, layer, raw, trace_raw, zero_raw)
        schema_context.validate(
            LAYER_MANIFEST_SCHEMA,
            layer_manifest,
            config["manifest_path"],
        )
        core[config["raw_path"]] = raw
        core[config["trace_path"]] = trace_raw
        core[config["zero_path"]] = zero_raw
        core[config["manifest_path"]] = canonical_json_bytes(layer_manifest)

    manifest = build_manifest(root, core)
    schema_context.validate(MANIFEST_SCHEMA, manifest, MANIFEST)
    manifest_raw = canonical_json_bytes(manifest)
    qualification = build_qualification(root, schema_context, core, manifest)
    schema_context.validate(QUALIFICATION_SCHEMA, qualification, QUALIFICATION)
    if qualification["overall_status"] != "PASS":
        raise ContractError("generated M19 qualification failed")
    return {
        **core,
        MANIFEST: manifest_raw,
        QUALIFICATION: canonical_json_bytes(qualification),
    }


def records_from_committed(root: Path) -> dict[str, bytes]:
    return {path: read_source(root, path) for path in GENERATED_PATHS}


def reconstruct_from_committed(root: Path) -> dict[str, bytes]:
    temp_root = Path(tempfile.mkdtemp(prefix="frp-m19-committed-"))
    try:
        rtl_log = temp_root / "rtl.log"
        fpga_log = temp_root / "fpga.log"
        rtl_log.write_bytes(read_source(root, RTL_RAW))
        fpga_log.write_bytes(read_source(root, FPGA_RAW))
        return generate_records(root, rtl_log, fpga_log)
    finally:
        shutil.rmtree(temp_root)


def verify_committed(root: Path) -> dict[str, Any]:
    committed = records_from_committed(root)
    reconstructed = reconstruct_from_committed(root)
    checks: list[dict[str, Any]] = []
    for path in GENERATED_PATHS:
        _check(
            checks,
            f"committed:{path}",
            "deterministic_regeneration",
            committed[path] == reconstructed[path],
        )
    qualification = parse_json_bytes(committed[QUALIFICATION], QUALIFICATION)
    if not isinstance(qualification, dict):
        raise ContractError("committed M19 qualification is not an object")
    _check(
        checks,
        "qualification:overall_status",
        "qualification",
        qualification.get("overall_status") == "PASS",
    )
    _check(
        checks,
        "qualification:aggregate",
        "qualification",
        qualification.get("passed_count") == qualification.get("check_count")
        and qualification.get("failed_count") == 0,
    )
    failed = sum(check["status"] != "PASS" for check in checks)
    return {
        "check_count": len(checks),
        "checks": checks,
        "failed_count": failed,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "passed_count": len(checks) - failed,
        "qualification_record_match": committed[QUALIFICATION]
        == reconstructed[QUALIFICATION],
    }


def publish_files(files: Mapping[str, bytes], destination: Path) -> None:
    expected = set(GENERATED_PATHS)
    if set(files) != expected:
        raise ContractError("publication path set mismatch")
    for relative in GENERATED_PATHS:
        safe = safe_relative_path(relative)
        target = destination.joinpath(*safe.parts)
        _reject_symlink_components(target, destination)
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if target.exists():
            raise SafetyError(f"publication target already exists: {target}")
        temporary = target.with_name(f".{target.name}.tmp")
        if temporary.exists():
            raise SafetyError(f"temporary publication target exists: {temporary}")
        temporary.write_bytes(files[relative])
        os.chmod(temporary, 0o600)
        temporary.replace(target)


def _artifact_set_known_vector() -> str:
    records = [
        {"byte_length": 3, "path": "a", "raw_sha256": "0" * 64},
        {"byte_length": 4, "path": "b", "raw_sha256": "1" * 64},
    ]
    return _artifact_set_digest(records)


def _synthetic_raw_line() -> str:
    values = {
        "sequence": 0,
        "core_ready": 1,
        "scheduler_mode": 0,
        "scheduler_state": 0,
        "ticks_before": 0,
        "request_valid": 1,
        "request_cell_index": 0,
        "request_target": 1,
        "phase_target": 1,
        "state_before": 0,
        "pending_before": 0,
        "request_accept": 1,
        "request_reject": 0,
        "accepted_cell_mask": 1,
        "neutral_routed_cell_mask": 0,
        "accepted_change_mask": 1,
        "accepted_changes": 1,
        "capacity_remaining": 1,
        "capacity_exhausted": 0,
        "switch_load_numerator": 1,
        "requested_direct_events": 0,
        "prevented_direct_events": 0,
        "neutral_routed_events": 0,
        "actual_direct_events": 0,
        "reserved_state_events": 0,
        "queue_overflow_events": 0,
        "invariant_flags": 0x3FF,
        "state_after": 1,
        "pending_after": 0,
        "ticks_after": 1,
        "count_free": 1,
        "count_balance": 0,
        "count_commit": 0,
        "count_excite": 0,
        "count_neutralize": 0,
    }
    rendered = [
        format(values[name], "x") if name in HEX_FIELDS else str(values[name])
        for name in RAW_FIELD_NAMES
    ]
    return "|".join(("FRP_M19", "1", "rtl", *rendered))


def build_self_test() -> dict[str, Any]:
    expected_artifact_digest = "4e7703efda5fdb2be1bfb40222a72406bcf96cc8a6516ddb31d0ee9e518edf7c"
    known_raw = b"FRP M19 machine-readable M16 evidence\n"
    expected_raw_digest = "d2f014d0dd51ddd747479ee58b635a105ad5c3ea4e5d1a8da752b10182cc3add"
    temporary = Path(tempfile.mkdtemp(prefix="frp-m19-self-test-"))
    cases: list[dict[str, Any]] = []

    def case(case_id: str, passed: bool) -> None:
        cases.append({"case_id": case_id, "status": "PASS" if passed else "FAIL"})

    try:
        synthetic = temporary / "synthetic.log"
        synthetic.write_text(_synthetic_raw_line() + "\n", encoding="utf-8")
        lines, parsed = _raw_lines(synthetic, "rtl")
        case("canonical_json", canonical_json_bytes({"b": 1, "a": 2}) == b'{"a":2,"b":1}\n')
        case("raw_sha256", sha256_bytes(known_raw) == expected_raw_digest)
        case("artifact_set_digest", _artifact_set_known_vector() == expected_artifact_digest)
        case("safe_relative_path", safe_relative_path("a/b.json").as_posix() == "a/b.json")
        for case_id, value in (
            ("unsafe_parent_path", "a/../b"),
            ("unsafe_absolute_path", "/a/b"),
        ):
            try:
                safe_relative_path(value)
            except SafetyError:
                case(case_id, True)
            else:
                case(case_id, False)
        case("ternary_decode_zero", _state(0) == 0)
        case("ternary_decode_positive", _state(1) == 1)
        case("ternary_decode_negative", _state(3) == -1)
        try:
            _state(2)
        except ContractError:
            case("ternary_decode_reserved", True)
        else:
            case("ternary_decode_reserved", False)
        case("packed_state_order", _states(0b110100)[:3] == [0, 1, -1])
        case("mask_cell_order", _cells(0b10000101) == [0, 2, 7])
        case("scheduler_free", _expected_scheduler_state("free", 17) == "free")
        case("scheduler_7_1_balance", _expected_scheduler_state("7/1", 6) == "balance")
        case("scheduler_7_1_commit", _expected_scheduler_state("7/1", 7) == "commit")
        case("scheduler_1_7_excite", _expected_scheduler_state("1/7", 8) == "excite")
        case("scheduler_1_7_neutralize", _expected_scheduler_state("1/7", 9) == "neutralize")
        case("invariant_vector", _invariant_vector(0x3FF)["all_pass"] is True)
        case("counter_relation", sum((1, 0, 0, 0, 0)) == 1)
        case(
            "raw_record_parser",
            lines == [_synthetic_raw_line()]
            and len(parsed) == 1
            and parsed[0]["state_after"] == 1,
        )
    finally:
        shutil.rmtree(temporary)

    if [item["case_id"] for item in cases] != list(SELF_TEST_CASE_IDS):
        raise ContractError("M19 self-test case ordering mismatch")
    failed = sum(item["status"] != "PASS" for item in cases)
    return {
        "case_count": len(cases),
        "cases": cases,
        "failed_count": failed,
        "kind": "m19_machine_readable_evidence_self_test",
        "milestone": MILESTONE,
        "overall_status": "PASS" if failed == 0 else "FAIL",
        "passed_count": len(cases) - failed,
        "version": VERSION,
    }


def _emit_summary(value: Mapping[str, Any]) -> None:
    for key in (
        "overall_status",
        "check_count",
        "passed_count",
        "failed_count",
        "qualification_record_match",
    ):
        if key in value:
            rendered = str(value[key]).lower() if isinstance(value[key], bool) else value[key]
            print(f"{key}: {rendered}")


def _parser() -> ContractArgumentParser:
    parser = ContractArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--generate", action="store_true")
    modes.add_argument("--verify", action="store_true")
    modes.add_argument("--qualify", action="store_true")
    modes.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--rtl-log")
    parser.add_argument("--fpga-log")
    parser.add_argument("--output-root")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--output", choices=("json", "text"), default="text")
    return parser


def _validate_arguments(arguments: argparse.Namespace) -> None:
    generation_only = ("rtl_log", "fpga_log", "output_root", "replace")
    if arguments.generate:
        if not arguments.rtl_log or not arguments.fpga_log or not arguments.output_root:
            raise ConfigurationError("--generate requires --rtl-log, --fpga-log, and --output-root")
    elif any(getattr(arguments, name) for name in generation_only):
        raise ConfigurationError("log, output-root, and replace options are valid only with --generate")


def run(arguments: argparse.Namespace) -> int:
    _validate_arguments(arguments)
    if arguments.self_test:
        result = build_self_test()
        if arguments.output == "json":
            sys.stdout.buffer.write(canonical_json_bytes(result))
        else:
            _emit_summary(result)
        return 0 if result["overall_status"] == "PASS" else 1

    root = repository_root(arguments.repository_root)
    if arguments.generate:
        destination = output_root(arguments.output_root, root, arguments.replace)
        files = generate_records(root, Path(arguments.rtl_log), Path(arguments.fpga_log))
        publish_files(files, destination)
        result = {
            "generated_count": len(files),
            "generated_paths": list(GENERATED_PATHS),
            "overall_status": "PASS",
        }
        if arguments.output == "json":
            sys.stdout.buffer.write(canonical_json_bytes(result))
        else:
            print("overall_status: PASS")
            print(f"generated_count: {len(files)}")
        return 0

    if arguments.verify:
        result = verify_committed(root)
    else:
        raw = read_source(root, QUALIFICATION)
        result = parse_json_bytes(raw, QUALIFICATION)
        if not isinstance(result, dict):
            raise ContractError("committed qualification is not an object")
        reconstructed = reconstruct_from_committed(root)
        result = dict(result)
        result["qualification_record_match"] = reconstructed[QUALIFICATION] == raw

    if arguments.output == "json":
        sys.stdout.buffer.write(canonical_json_bytes(result))
    else:
        _emit_summary(result)
    return 0 if result.get("overall_status") == "PASS" else 1


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return run(_parser().parse_args(argv))
    except ConfigurationError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    except SafetyError as exc:
        print(f"safety error: {exc}", file=sys.stderr)
        return 4
    except (ContractError, OSError) as exc:
        print(f"qualification error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
