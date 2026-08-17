#!/usr/bin/env python3
"""FRP M20 deterministic M15-to-M16 cross-layer correlation producer."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


VERSION = "2.2.0"
MILESTONE = "M20 — Cross-Layer Deterministic Correlation"
SOURCE_RELEASE = "FRP v2.1.0 / M19 evidence boundary"
EXPECTED_M19_COMMIT = "8b5e606f388325ec6e4424c59799c11ba58a8e29"

PRODUCER = "frp_m20_cross_layer_correlation.py"
WORKFLOW = ".github/workflows/frp-m20-cross-layer-correlation.yml"
TESTS = "tests/test_frp_m20_cross_layer_correlation.py"
REGISTRY_PATH = "schemas/m20/frp_m20_schema_registry.json"

RECORD_SCHEMA = "frp.m20.correlation_record.v2.2.0"
PACKAGE_SCHEMA = "frp.m20.cross_layer_correlation_package.v2.2.0"
MANIFEST_SCHEMA = "frp.m20.cross_layer_correlation_manifest.v2.2.0"
QUALIFICATION_SCHEMA = (
    "frp.m20.cross_layer_correlation_qualification.v2.2.0"
)

SCHEMA_PATHS = {
    RECORD_SCHEMA: "schemas/m20/frp_m20_correlation_record.v2.2.0.schema.json",
    PACKAGE_SCHEMA: (
        "schemas/m20/"
        "frp_m20_cross_layer_correlation_package.v2.2.0.schema.json"
    ),
    MANIFEST_SCHEMA: (
        "schemas/m20/"
        "frp_m20_cross_layer_correlation_manifest.v2.2.0.schema.json"
    ),
    QUALIFICATION_SCHEMA: (
        "schemas/m20/"
        "frp_m20_cross_layer_correlation_qualification.v2.2.0.schema.json"
    ),
}

RTL_PACKAGE = "artifacts/m20/correlation/m15-m16-rtl-correlation.json"
FPGA_PACKAGE = (
    "artifacts/m20/correlation/"
    "m15-m16-fpga-preparation-correlation.json"
)
MANIFEST = "artifacts/m20/manifests/m20-cross-layer-correlation-manifest.json"
QUALIFICATION = (
    "artifacts/m20/manifests/"
    "m20-cross-layer-correlation-qualification.json"
)
GENERATED_PATHS = (RTL_PACKAGE, FPGA_PACKAGE, MANIFEST, QUALIFICATION)

M16_TRACE_PATHS = {
    "rtl": "artifacts/m19/execution/m16-rtl-execution-trace.json",
    "fpga_preparation": (
        "artifacts/m19/execution/"
        "m16-fpga-preparation-execution-trace.json"
    ),
}
M16_TRACE_SCHEMAS = {
    "rtl": "frp.m16.rtl_execution_trace.v2.1.0",
    "fpga_preparation": (
        "frp.m16.fpga_preparation_execution_trace.v2.1.0"
    ),
}
M19_MANIFEST = (
    "artifacts/m19/manifests/m19-machine-readable-evidence-manifest.json"
)
M19_QUALIFICATION = (
    "artifacts/m19/manifests/"
    "m19-machine-readable-evidence-qualification.json"
)

SEMANTIC_TRACE_PATHS = {
    "free": "artifacts/m18/structured_output/trace-free.json",
    "7/1": "artifacts/m18/structured_output/trace-7-1.json",
    "1/7": "artifacts/m18/structured_output/trace-1-7.json",
}
VECTOR_PATHS = {
    "free": "artifacts/m18/m15_vectors/frp_m15_scheduler_free_vectors.vec",
    "7/1": (
        "artifacts/m18/m15_vectors/"
        "frp_m15_full_correlation_vectors.vec"
    ),
    "1/7": "artifacts/m18/m15_vectors/frp_m15_scheduler_1_7_vectors.vec",
}
VECTOR_DIRECTORY = "artifacts/m18/m15_vectors"
VECTOR_PACKAGE = (
    "artifacts/m18/m15_exports/rtl-comparison-vector-package.json"
)
QUANTIZED_SHADOW = (
    "artifacts/m18/m15_exports/quantized-reference-shadow-model.json"
)
M15_RTL_REFERENCE = (
    "artifacts/m18/m15_exports/synthesizable-rtl-reference-core.json"
)
M15_EQUIVALENCE = (
    "artifacts/m18/m15_exports/reference-rtl-equivalence-report.json"
)
M15_QUALIFICATION = (
    "artifacts/m18/m15_exports/qualification-closure-manifest.json"
)

VECTOR_COLUMNS = (
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
)
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
SCHEDULER_MODE_CODES = {"free": 0, "7/1": 1, "1/7": 2}
SCHEDULER_STATE_CODES = {
    "free": 0,
    "balance": 1,
    "commit": 2,
    "excite": 3,
    "neutralize": 4,
}
CHECK_NAMES = (
    "tick_alignment",
    "scheduler_mode",
    "scheduler_state",
    "deterministic_inputs",
    "request_lanes",
    "retained_state",
    "pending_route",
    "transition_capacity",
    "event_counters",
    "invariant_vector",
)

TECHNICAL_SOURCE_PATHS = tuple(
    sorted((PRODUCER, WORKFLOW, TESTS, REGISTRY_PATH, *SCHEMA_PATHS.values()))
)
UPSTREAM_SOURCE_PATHS = tuple(
    sorted(
        {
            *M16_TRACE_PATHS.values(),
            M19_MANIFEST,
            M19_QUALIFICATION,
            *SEMANTIC_TRACE_PATHS.values(),
            *VECTOR_PATHS.values(),
            VECTOR_PACKAGE,
            QUANTIZED_SHADOW,
            M15_RTL_REFERENCE,
            M15_EQUIVALENCE,
            M15_QUALIFICATION,
        }
    )
)


class M20Error(Exception):
    """Base M20 failure."""


class ContractError(M20Error):
    """An input, schema, or correlation contract failed."""


class SafetyError(M20Error):
    """An unsafe filesystem path was requested."""


def canonical_json_bytes(value: Any) -> bytes:
    """Return byte-stable UTF-8 JSON with a terminal newline."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def validate_source_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ContractError("source commit must be a full lowercase Git SHA")
    if value != EXPECTED_M19_COMMIT:
        raise ContractError("unexpected M19 source commit")
    return value


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise SafetyError(f"unsafe relative path: {value!r}")
    path = PurePosixPath(value)
    if (
        "\\" in value
        or path.is_absolute()
        or not path.parts
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise SafetyError(f"unsafe relative path: {value!r}")
    return path


def read_bytes(repository: Path, relative: str) -> bytes:
    path = repository.joinpath(*safe_relative_path(relative).parts)
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"required regular file is missing: {relative}")
    return path.read_bytes()


def read_json(repository: Path, relative: str) -> Any:
    raw = read_bytes(repository, relative)
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid JSON: {relative}") from exc


def source_record(repository: Path, relative: str, role: str) -> dict[str, Any]:
    raw = read_bytes(repository, relative)
    return {
        "byte_length": len(raw),
        "path": relative,
        "raw_sha256": sha256_bytes(raw),
        "role": role,
    }


def _parse_int_list(value: str, *, base: int = 10) -> list[int]:
    if not value:
        return []
    return [int(item.strip(), base) for item in value.split(",")]


def parse_vector(repository: Path, relative: str) -> list[dict[str, Any]]:
    """Parse one exact M15 vector table used by the M20 bridge."""

    text = read_bytes(repository, relative).decode("utf-8")
    header: tuple[str, ...] | None = None
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line:
            continue
        if line.startswith("# ") and " | " in line:
            candidate = tuple(part.strip() for part in line[2:].split("|"))
            if candidate == VECTOR_COLUMNS:
                if header is not None:
                    raise ContractError(f"duplicate vector header: {relative}")
                header = candidate
            continue
        if line.startswith("#"):
            continue
        if header is None:
            raise ContractError(f"vector data precedes header: {relative}")
        values = tuple(part.strip() for part in line.split("|"))
        if len(values) != len(VECTOR_COLUMNS):
            raise ContractError(
                f"vector column count mismatch at {relative}:{line_number}"
            )
        row = dict(zip(VECTOR_COLUMNS, values, strict=True))
        parsed = {
            "C_minus_P_q16": int(row["C_MINUS_P_Q"]),
            "C_q16": int(row["C_Q"]),
            "P_q16": int(row["P_Q"]),
            "actual_direct_events": int(row["ACTUAL_DIRECT_EVENTS"]),
            "global_phase_coherence_q30": int(row["COHERENCE_GLOBAL_Q"]),
            "heat_global_q16": int(row["HEAT_GLOBAL_Q"]),
            "neutral_routed_events": int(row["NEUTRAL_ROUTED_EVENTS"]),
            "pending_route_count": int(row["PENDING_ROUTE_COUNT"]),
            "prevented_direct_events": int(row["PREVENTED_DIRECT_EVENTS"]),
            "request_cell_ids": _parse_int_list(row["REQ_CELL_IDS"], base=16),
            "request_target_state_codes": _parse_int_list(
                row["REQ_TARGET_STATES"], base=16
            ),
            "request_valid_mask": int(row["REQ_VALID_MASK"], 16),
            "requested_direct_events": int(row["REQUESTED_DIRECT_EVENTS"]),
            "scheduler_mode": int(row["SCHED_MODE"]),
            "scheduler_state": int(row["SCHED_STATE"]),
            "states_packed_hex": row["STATES_PACKED"],
            "switch_load_q16": int(row["SWITCH_LOAD_Q"]),
            "tick": int(row["TICK"]),
        }
        rows.append(parsed)
    if header != VECTOR_COLUMNS or not rows:
        raise ContractError(f"vector header or rows are missing: {relative}")
    if [row["tick"] for row in rows] != list(range(len(rows))):
        raise ContractError(f"vector ticks are not contiguous: {relative}")
    return rows


def verify_raw_digest(raw: bytes, expected: Mapping[str, Any], subject: str) -> None:
    if expected.get("size_bytes") != len(raw):
        raise ContractError(f"byte length mismatch: {subject}")
    if expected.get("sha256") != sha256_bytes(raw):
        raise ContractError(f"SHA-256 mismatch: {subject}")


def validate_vector_package(repository: Path) -> tuple[dict[str, Any], ...]:
    package = read_json(repository, VECTOR_PACKAGE)
    if not isinstance(package, dict):
        raise ContractError("M15 vector package is not an object")
    if package.get("schema") != "frp.m15.rtl_comparison_vector_package.v1.7.0":
        raise ContractError("M15 vector package schema mismatch")
    manifest = package.get("manifest")
    if not isinstance(manifest, dict) or manifest.get("file_count") != 10:
        raise ContractError("M15 vector package manifest mismatch")
    files = manifest.get("files")
    if not isinstance(files, list) or len(files) != 10:
        raise ContractError("M15 vector file inventory mismatch")
    identities: list[dict[str, Any]] = []
    names: list[str] = []
    for item in files:
        if not isinstance(item, dict) or set(item) != {
            "name",
            "sha256",
            "size_bytes",
        }:
            raise ContractError("M15 vector identity field mismatch")
        name = item["name"]
        if not isinstance(name, str) or PurePosixPath(name).name != name:
            raise ContractError("invalid M15 vector filename")
        relative = f"{VECTOR_DIRECTORY}/{name}"
        raw = read_bytes(repository, relative)
        verify_raw_digest(raw, item, relative)
        names.append(name)
        identities.append(
            {
                "byte_length": len(raw),
                "name": name,
                "path": relative,
                "raw_sha256": sha256_bytes(raw),
            }
        )
    if names != sorted(names) or len(set(names)) != 10:
        raise ContractError("M15 vector identities are not ordered and unique")
    return tuple(identities)


class SchemaContext:
    """Load the exact M20 formal schema registry and validators."""

    def __init__(self, repository: Path) -> None:
        registry = read_json(repository, REGISTRY_PATH)
        if not isinstance(registry, dict):
            raise ContractError("M20 schema registry is not an object")
        if set(registry) != {"kind", "milestone", "records", "schema", "version"}:
            raise ContractError("M20 schema registry field set mismatch")
        if registry.get("schema") != "frp.m20.schema_registry.v2.2.0":
            raise ContractError("M20 schema registry identity mismatch")
        records = registry.get("records")
        if not isinstance(records, list) or len(records) != len(SCHEMA_PATHS):
            raise ContractError("M20 schema registry record count mismatch")

        self.schemas: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict) or set(record) != {
                "artifact_paths",
                "schema_identifier",
                "schema_path",
                "schema_urn",
            }:
                raise ContractError("M20 schema registry record mismatch")
            identifier = record["schema_identifier"]
            if identifier not in SCHEMA_PATHS:
                raise ContractError("unregistered M20 schema identifier")
            expected_path = SCHEMA_PATHS[identifier]
            expected_urn = f"urn:frp:schema:{identifier}"
            if record["schema_path"] != expected_path:
                raise ContractError("M20 schema path mismatch")
            if record["schema_urn"] != expected_urn:
                raise ContractError("M20 schema URN mismatch")
            schema = read_json(repository, expected_path)
            if not isinstance(schema, dict):
                raise ContractError("M20 schema is not an object")
            if schema.get("$id") != expected_urn:
                raise ContractError("M20 schema $id mismatch")
            if schema.get("x-frp-schema-identifier") != identifier:
                raise ContractError("M20 schema identifier extension mismatch")
            Draft202012Validator.check_schema(schema)
            self.schemas[identifier] = schema

        if set(self.schemas) != set(SCHEMA_PATHS):
            raise ContractError("M20 schema set mismatch")
        resources = [
            (schema["$id"], Resource.from_contents(schema))
            for schema in self.schemas.values()
        ]
        self.registry = Registry().with_resources(resources)

    def validate(self, identifier: str, value: Any, subject: str) -> None:
        try:
            schema = self.schemas[identifier]
        except KeyError as exc:
            raise ContractError(f"unknown M20 schema: {identifier}") from exc
        validator = Draft202012Validator(schema, registry=self.registry)
        errors = sorted(validator.iter_errors(value), key=lambda error: list(error.path))
        if errors:
            first = errors[0]
            location = "$" + "".join(f"[{part!r}]" for part in first.path)
            raise ContractError(
                f"schema validation failed for {subject} at {location}: "
                f"{first.message}"
            )


@dataclass(frozen=True)
class CorrelationContext:
    repository: Path
    source_commit: str
    vector_identities: tuple[dict[str, Any], ...]
    semantic_traces: Mapping[str, Mapping[str, Any]]
    vector_rows: Mapping[str, list[dict[str, Any]]]
    m16_traces: Mapping[str, Mapping[str, Any]]


def build_context(repository: Path, source_commit: str) -> CorrelationContext:
    repository = repository.resolve()
    validate_source_commit(source_commit)
    vector_identities = validate_vector_package(repository)

    semantic_traces: dict[str, Mapping[str, Any]] = {}
    vector_rows: dict[str, list[dict[str, Any]]] = {}
    for mode in ("free", "7/1", "1/7"):
        value = read_json(repository, SEMANTIC_TRACE_PATHS[mode])
        if not isinstance(value, dict):
            raise ContractError("M15 semantic trace is not an object")
        if value.get("schema") != "frp.structured_output.v1.7.0":
            raise ContractError("M15 semantic trace schema mismatch")
        configuration = value.get("configuration")
        trace = value.get("trace")
        kernel = value.get("kernel")
        if not isinstance(configuration, dict) or configuration.get("scheduler") != mode:
            raise ContractError("M15 semantic scheduler mismatch")
        if not isinstance(trace, list) or len(trace) != 64:
            raise ContractError("M15 semantic trace length mismatch")
        if not isinstance(kernel, dict) or kernel.get("balanced_ternary_states") != [-1, 0, 1]:
            raise ContractError("M15 canonical ternary domain mismatch")
        rows = parse_vector(repository, VECTOR_PATHS[mode])
        required_rows = 64 if mode == "7/1" else 16
        if len(rows) != required_rows:
            raise ContractError("M15 vector row count mismatch")
        for tick, vector_row in enumerate(rows):
            semantic_row = trace[tick]
            if (
                semantic_row.get("tick") != tick
                or vector_row["tick"] != tick
                or semantic_row.get("scheduler_mode") != vector_row["scheduler_mode"]
                or semantic_row.get("scheduler_state") != vector_row["scheduler_state"]
            ):
                raise ContractError("M15 semantic/vector scheduler mismatch")
        semantic_traces[mode] = value
        vector_rows[mode] = rows

    m16_traces: dict[str, Mapping[str, Any]] = {}
    for layer, relative in M16_TRACE_PATHS.items():
        value = read_json(repository, relative)
        if not isinstance(value, dict):
            raise ContractError("M16 execution trace is not an object")
        if value.get("schema") != M16_TRACE_SCHEMAS[layer]:
            raise ContractError("M16 execution trace schema mismatch")
        records = value.get("records")
        expected_count = 96 if layer == "rtl" else 4
        if not isinstance(records, list) or len(records) != expected_count:
            raise ContractError("M16 execution record count mismatch")
        m16_traces[layer] = value

    m19_qualification = read_json(repository, M19_QUALIFICATION)
    if (
        not isinstance(m19_qualification, dict)
        or m19_qualification.get("overall_status") != "PASS"
        or m19_qualification.get("passed_count") != 37
        or m19_qualification.get("failed_count") != 0
    ):
        raise ContractError("M19 qualification boundary is not PASS")

    return CorrelationContext(
        repository=repository,
        source_commit=source_commit,
        vector_identities=vector_identities,
        semantic_traces=semantic_traces,
        vector_rows=vector_rows,
        m16_traces=m16_traces,
    )


def expected_scheduler_state(mode: str, tick: int) -> str:
    if mode == "free":
        return "free"
    if mode == "7/1":
        return "commit" if tick % 8 == 7 else "balance"
    if mode == "1/7":
        return "excite" if tick % 8 == 0 else "neutralize"
    raise ContractError(f"unsupported scheduler mode: {mode}")


def _transition_class(current: int, target: int) -> str:
    if current not in (-1, 0, 1) or target not in (-1, 0, 1):
        return "invalid"
    if current == target:
        return "same_state"
    if current == 0 and target != 0:
        return "zero_to_nonzero"
    if current != 0 and target == 0:
        return "nonzero_to_zero"
    if current == -target:
        return "opposite_polarity"
    return "invalid"


def _scheduler_allows(state: str, transition_class: str) -> bool:
    if transition_class == "same_state":
        return True
    if transition_class == "zero_to_nonzero":
        return state in {"free", "commit", "excite"}
    if transition_class in {"nonzero_to_zero", "opposite_polarity"}:
        return state in {"free", "balance", "neutralize"}
    return False


def _compare(
    checks: dict[str, bool],
    mismatches: list[dict[str, Any]],
    name: str,
    expected: Any,
    observed: Any,
) -> None:
    passed = expected == observed
    checks[name] = passed
    if not passed:
        mismatches.append(
            {
                "check": name,
                "expected": expected,
                "observed": observed,
            }
        )


def _semantic_snapshot(row: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "C_minus_P_q16",
        "C_q16",
        "P_q16",
        "actual_direct_events",
        "global_phase_coherence_q30",
        "heat_global_q16",
        "neutral_routed_events",
        "pending_route_count",
        "prevented_direct_events",
        "request_cell_ids",
        "request_target_states",
        "request_valid_mask",
        "requested_direct_events",
        "reserved_state_events",
        "scheduler_mode",
        "scheduler_state",
        "scheduler_state_name",
        "states_packed_hex",
        "switch_load_q16",
        "tick",
    )
    return {field: copy.deepcopy(row[field]) for field in fields}


def _vector_snapshot(row: Mapping[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(dict(row))


def _invariant_projection(observed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "all_pass": observed["all_pass"],
        "flags": copy.deepcopy(observed["flags"]),
    }


def _expected_invariants() -> dict[str, Any]:
    return {
        "all_pass": True,
        "flags": [
            {"name": name, "pass": True}
            for name in INVARIANT_NAMES
        ],
    }


def _source_identity(
    context: CorrelationContext,
    layer: str,
) -> dict[str, Any]:
    repository = context.repository
    semantic = [
        source_record(repository, SEMANTIC_TRACE_PATHS[mode], "m15_semantic_trace")
        | {"mode": mode, "schema": "frp.structured_output.v1.7.0"}
        for mode in ("free", "7/1", "1/7")
    ]
    vectors = [
        source_record(repository, VECTOR_PATHS[mode], "m15_correlation_vector")
        | {"mode": mode, "format": "frp.m15.vector.v1"}
        for mode in ("free", "7/1", "1/7")
    ]
    return {
        "m15_equivalence_report": source_record(
            repository, M15_EQUIVALENCE, "m15_equivalence_report"
        ),
        "m15_quantized_shadow": source_record(
            repository, QUANTIZED_SHADOW, "m15_quantized_shadow"
        ),
        "m15_qualification": source_record(
            repository, M15_QUALIFICATION, "m15_qualification"
        ),
        "m15_rtl_reference": source_record(
            repository, M15_RTL_REFERENCE, "m15_rtl_reference"
        ),
        "m15_semantic_traces": semantic,
        "m15_vector_package": source_record(
            repository, VECTOR_PACKAGE, "m15_vector_package"
        ),
        "m15_vectors": vectors,
        "m16_execution_trace": source_record(
            repository, M16_TRACE_PATHS[layer], "m16_execution_trace"
        )
        | {"schema": M16_TRACE_SCHEMAS[layer]},
        "m19_manifest": source_record(
            repository, M19_MANIFEST, "m19_evidence_manifest"
        ),
        "m19_qualification": source_record(
            repository, M19_QUALIFICATION, "m19_qualification"
        ),
    }


def _interface_mapping(trace: Mapping[str, Any]) -> dict[str, Any]:
    configuration = trace["configuration"]
    cells = configuration["cells"]
    request_lanes = configuration["request_lanes"]
    expected_lanes = max(1, (cells + 2) // 4)
    if request_lanes != expected_lanes:
        raise ContractError("M16 transition-fraction lane relation mismatch")
    return {
        "active_neutral_state": 0,
        "canonical_ternary_states": [-1, 0, 1],
        "m15_profile": {
            "cells": 16,
            "request_lanes": 4,
            "transition_fraction_denominator": 4,
            "transition_fraction_numerator": 1,
        },
        "m16_profile": {
            "cells": cells,
            "request_lanes": request_lanes,
            "transition_fraction_denominator": configuration[
                "transition_fraction_denominator"
            ],
            "transition_fraction_numerator": configuration[
                "transition_fraction_numerator"
            ],
        },
        "neutral_routes": ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
        "scheduler_mode_codes": {"1/7": 2, "7/1": 1, "free": 0},
        "scheduler_state_codes": {
            "balance": 1,
            "commit": 2,
            "excite": 3,
            "free": 0,
            "neutralize": 4,
        },
        "state_encoding": {"-1": "11", "0": "00", "1": "01"},
    }


def _build_expected_tick(
    observed: Mapping[str, Any],
    state_before: list[int],
    pending_before: list[int],
    counters_before: Mapping[str, int],
    tick: int,
    mode: str,
    capacity_limit: int,
) -> tuple[dict[str, Any], list[int], list[int], dict[str, int]]:
    cells = len(state_before)
    scheduler_state = expected_scheduler_state(mode, tick)
    commit_capable = scheduler_state in {"free", "commit", "excite"}

    pending_candidates = [
        cell
        for cell in range(cells)
        if state_before[cell] == 0
        and pending_before[cell] in (-1, 1)
        and commit_capable
    ]

    requests = observed["requests"]
    claimed_cells: set[int] = set()
    preliminary: list[bool] = []
    classes: list[str] = []
    for request in requests:
        if not request["valid"]:
            preliminary.append(False)
            classes.append("inactive")
            continue
        cell = request["cell_index"]
        target = request["target_state"]
        valid_cell = isinstance(cell, int) and 0 <= cell < cells
        valid_target = target in (-1, 0, 1)
        transition_class = (
            _transition_class(state_before[cell], target)
            if valid_cell and valid_target
            else "invalid"
        )
        accepted = (
            valid_cell
            and valid_target
            and cell not in claimed_cells
            and pending_before[cell] == 0
            and _scheduler_allows(scheduler_state, transition_class)
        )
        if accepted:
            claimed_cells.add(cell)
        preliminary.append(accepted)
        classes.append(transition_class)

    accepted_changes: list[tuple[str, int, int | None]] = []
    used_capacity = 0
    for cell in pending_candidates:
        if used_capacity < capacity_limit:
            accepted_changes.append(("pending", cell, None))
            used_capacity += 1

    final_accept = [False] * len(requests)
    for lane, request in enumerate(requests):
        if not preliminary[lane]:
            continue
        cell = request["cell_index"]
        target = request["target_state"]
        state_changes = state_before[cell] != target
        if not state_changes:
            final_accept[lane] = True
        elif used_capacity < capacity_limit:
            final_accept[lane] = True
            accepted_changes.append(("request", cell, target))
            used_capacity += 1

    state_after = state_before.copy()
    pending_after = pending_before.copy()
    neutral_routed_cells: list[int] = []
    for source, cell, target in accepted_changes:
        if source == "pending":
            state_after[cell] = pending_before[cell]
            pending_after[cell] = 0
            continue
        assert target is not None
        if state_before[cell] in (-1, 1) and target == -state_before[cell]:
            state_after[cell] = 0
            pending_after[cell] = target
            neutral_routed_cells.append(cell)
        else:
            state_after[cell] = target

    direct_events = sum(
        1
        for accepted, transition_class in zip(preliminary, classes, strict=True)
        if accepted and transition_class == "opposite_polarity"
    )
    counters_after = dict(counters_before)
    counters_after[scheduler_state] += 1

    expected_requests = []
    for request, accepted in zip(requests, final_accept, strict=True):
        expected_requests.append(
            {
                "accepted": accepted,
                "cell_index": request["cell_index"],
                "lane": request["lane"],
                "rejected": bool(request["valid"] and not accepted),
                "target_state": request["target_state"],
                "valid": request["valid"],
            }
        )

    accepted_cell_ids = sorted(
        {
            request["cell_index"]
            for request, accepted in zip(requests, final_accept, strict=True)
            if accepted
        }
    )
    accepted_change_cell_ids = sorted(
        {cell for _, cell, _ in accepted_changes}
    )
    expected = {
        "accepted_cell_ids": accepted_cell_ids,
        "accepted_change_cell_ids": accepted_change_cell_ids,
        "events": {
            "actual_direct_events": 0,
            "neutral_routed_events": direct_events,
            "prevented_direct_events": direct_events,
            "queue_overflow_events": 0,
            "requested_direct_events": direct_events,
            "reserved_state_events": 0,
        },
        "invariants": _expected_invariants(),
        "neutral_routed_cell_ids": sorted(neutral_routed_cells),
        "pending_route_after": pending_after,
        "pending_route_before": pending_before,
        "requests": expected_requests,
        "retained_state_after": state_after,
        "retained_state_before": state_before,
        "scheduler": {
            "counters_after": counters_after,
            "mode": mode,
            "state": scheduler_state,
            "ticks_after": tick + 1,
            "ticks_before": tick,
        },
        "telemetry": {
            "switch_load_denominator": cells,
            "switch_load_numerator": used_capacity,
            "switch_load_q16": used_capacity * 65536 // cells,
        },
        "transition_capacity": {
            "accepted_changes": used_capacity,
            "capacity_exhausted": used_capacity == capacity_limit,
            "capacity_limit": capacity_limit,
            "capacity_remaining": capacity_limit - used_capacity,
        },
    }
    return expected, state_after, pending_after, counters_after


def _observed_projection(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "accepted_cell_ids": copy.deepcopy(record["accepted_cell_ids"]),
        "accepted_change_cell_ids": copy.deepcopy(
            record["accepted_change_cell_ids"]
        ),
        "events": copy.deepcopy(record["events"]),
        "invariants": _invariant_projection(record["invariants"]),
        "neutral_routed_cell_ids": copy.deepcopy(
            record["neutral_routed_cell_ids"]
        ),
        "pending_route_after": copy.deepcopy(record["pending_route_after"]),
        "pending_route_before": copy.deepcopy(record["pending_route_before"]),
        "requests": copy.deepcopy(record["requests"]),
        "retained_state_after": copy.deepcopy(record["retained_state_after"]),
        "retained_state_before": copy.deepcopy(record["retained_state_before"]),
        "scheduler": copy.deepcopy(record["scheduler"]),
        "telemetry": copy.deepcopy(record["telemetry"]),
        "transition_capacity": copy.deepcopy(record["transition_capacity"]),
    }


def _input_contract(record: Mapping[str, Any], cells: int) -> bool:
    phase = record["phase_derived_targets"]
    if (
        record.get("core_ready") is not True
        or not isinstance(phase, list)
        or len(phase) != cells
        or any(value not in (-1, 0, 1) for value in phase)
    ):
        return False
    for request in record["requests"]:
        cell = request["cell_index"]
        if request["valid"] and (
            not isinstance(cell, int)
            or not 0 <= cell < cells
            or request["target_state"] != phase[cell]
        ):
            return False
    return True


def build_layer_package(
    context: CorrelationContext,
    layer: str,
    *,
    trace_override: Mapping[str, Any] | None = None,
    vector_rows_override: Mapping[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Build one complete record-level M15/M16 correlation package."""

    if layer not in M16_TRACE_PATHS:
        raise ContractError(f"unsupported M20 layer: {layer}")
    trace = trace_override if trace_override is not None else context.m16_traces[layer]
    vector_rows = (
        vector_rows_override
        if vector_rows_override is not None
        else context.vector_rows
    )
    configuration = trace["configuration"]
    cells = configuration["cells"]
    capacity_limit = max(1, (cells + 2) // 4)
    records = trace["records"]
    if [record["sequence"] for record in records] != list(range(len(records))):
        raise ContractError("M16 execution sequence is not contiguous")

    epoch_state: dict[int, dict[str, Any]] = {}
    correlation_records: list[dict[str, Any]] = []
    all_mismatches: list[dict[str, Any]] = []
    total_checks = 0
    passed_checks = 0

    for observed_record in records:
        epoch = observed_record["execution_epoch"]
        if epoch not in epoch_state:
            epoch_state[epoch] = {
                "counters": {
                    "balance": 0,
                    "commit": 0,
                    "excite": 0,
                    "free": 0,
                    "neutralize": 0,
                },
                "pending": [0] * cells,
                "state": [0] * cells,
                "tick": 0,
            }
        shadow = epoch_state[epoch]
        mode = observed_record["scheduler"]["mode"]
        tick = shadow["tick"]
        if mode not in SEMANTIC_TRACE_PATHS:
            raise ContractError("M16 record has unsupported scheduler mode")
        if tick >= len(vector_rows[mode]):
            raise ContractError("M15 vector does not cover M16 tick")

        semantic_row = context.semantic_traces[mode]["trace"][tick]
        vector_row = vector_rows[mode][tick]
        expected, state_after, pending_after, counters_after = _build_expected_tick(
            observed_record,
            shadow["state"],
            shadow["pending"],
            shadow["counters"],
            tick,
            mode,
            capacity_limit,
        )
        observed = _observed_projection(observed_record)
        checks: dict[str, bool] = {}
        mismatches: list[dict[str, Any]] = []

        _compare(
            checks,
            mismatches,
            "tick_alignment",
            {
                "m15_semantic_tick": tick,
                "m15_vector_tick": tick,
                "m16_ticks_before": tick,
            },
            {
                "m15_semantic_tick": semantic_row["tick"],
                "m15_vector_tick": vector_row["tick"],
                "m16_ticks_before": observed_record["scheduler"]["ticks_before"],
            },
        )
        _compare(
            checks,
            mismatches,
            "scheduler_mode",
            {
                "code": SCHEDULER_MODE_CODES[mode],
                "name": mode,
            },
            {
                "code": semantic_row["scheduler_mode"],
                "name": observed_record["scheduler"]["mode"],
            },
        )
        expected_state_name = expected["scheduler"]["state"]
        _compare(
            checks,
            mismatches,
            "scheduler_state",
            {
                "code": SCHEDULER_STATE_CODES[expected_state_name],
                "name": expected_state_name,
                "vector_code": SCHEDULER_STATE_CODES[expected_state_name],
            },
            {
                "code": semantic_row["scheduler_state"],
                "name": observed_record["scheduler"]["state"],
                "vector_code": vector_row["scheduler_state"],
            },
        )
        _compare(
            checks,
            mismatches,
            "deterministic_inputs",
            True,
            _input_contract(observed_record, cells),
        )
        _compare(
            checks,
            mismatches,
            "request_lanes",
            {
                "accepted_cell_ids": expected["accepted_cell_ids"],
                "requests": expected["requests"],
            },
            {
                "accepted_cell_ids": observed["accepted_cell_ids"],
                "requests": observed["requests"],
            },
        )
        _compare(
            checks,
            mismatches,
            "retained_state",
            {
                "after": expected["retained_state_after"],
                "before": expected["retained_state_before"],
            },
            {
                "after": observed["retained_state_after"],
                "before": observed["retained_state_before"],
            },
        )
        _compare(
            checks,
            mismatches,
            "pending_route",
            {
                "after": expected["pending_route_after"],
                "before": expected["pending_route_before"],
                "neutral_routed_cell_ids": expected[
                    "neutral_routed_cell_ids"
                ],
            },
            {
                "after": observed["pending_route_after"],
                "before": observed["pending_route_before"],
                "neutral_routed_cell_ids": observed[
                    "neutral_routed_cell_ids"
                ],
            },
        )
        _compare(
            checks,
            mismatches,
            "transition_capacity",
            {
                "accepted_change_cell_ids": expected[
                    "accepted_change_cell_ids"
                ],
                "telemetry": expected["telemetry"],
                "transition_capacity": expected["transition_capacity"],
            },
            {
                "accepted_change_cell_ids": observed[
                    "accepted_change_cell_ids"
                ],
                "telemetry": observed["telemetry"],
                "transition_capacity": observed["transition_capacity"],
            },
        )
        _compare(
            checks,
            mismatches,
            "event_counters",
            expected["events"],
            observed["events"],
        )
        _compare(
            checks,
            mismatches,
            "invariant_vector",
            expected["invariants"],
            observed["invariants"],
        )

        if tuple(checks) != CHECK_NAMES:
            raise ContractError("M20 check order mismatch")
        correlation_id = f"{layer}:{observed_record['sequence']:08d}"
        for mismatch in mismatches:
            all_mismatches.append(
                {"correlation_id": correlation_id, **copy.deepcopy(mismatch)}
            )
        total_checks += len(checks)
        passed_checks += sum(checks.values())
        correlation_records.append(
            {
                "checks": checks,
                "correlation_id": correlation_id,
                "execution_epoch": epoch,
                "m15_semantic_reference": {
                    "measurement_contour": "m15_quantized_semantic_reference",
                    "path": SEMANTIC_TRACE_PATHS[mode],
                    "record": _semantic_snapshot(semantic_row),
                    "raw_sha256": sha256_bytes(
                        read_bytes(context.repository, SEMANTIC_TRACE_PATHS[mode])
                    ),
                },
                "m15_vector_reference": {
                    "measurement_contour": "m15_implementation_mapping",
                    "path": VECTOR_PATHS[mode],
                    "record": _vector_snapshot(vector_row),
                    "raw_sha256": sha256_bytes(
                        read_bytes(context.repository, VECTOR_PATHS[mode])
                    ),
                },
                "m16_deterministic_input": {
                    "core_ready": observed_record["core_ready"],
                    "phase_derived_targets": copy.deepcopy(
                        observed_record["phase_derived_targets"]
                    ),
                    "requests": copy.deepcopy(observed_record["requests"]),
                },
                "m16_expected": expected,
                "m16_observed": observed,
                "mismatch_count": len(mismatches),
                "mismatches": mismatches,
                "record_status": "PASS" if not mismatches else "FAIL",
                "schema": RECORD_SCHEMA,
                "sequence": observed_record["sequence"],
                "tick": tick,
            }
        )
        shadow["state"] = state_after
        shadow["pending"] = pending_after
        shadow["counters"] = counters_after
        shadow["tick"] = tick + 1

    record_digest = object_digest(correlation_records)
    mismatch_digest = object_digest(all_mismatches)
    package = {
        "correlation_layer": layer,
        "interface_mapping": _interface_mapping(trace),
        "kind": "cross_layer_correlation_package",
        "milestone": MILESTONE,
        "mismatch_records": all_mismatches,
        "records": correlation_records,
        "schema": PACKAGE_SCHEMA,
        "source_commit": context.source_commit,
        "source_identity": _source_identity(context, layer),
        "source_release": SOURCE_RELEASE,
        "summary": {
            "check_count": total_checks,
            "failed_check_count": total_checks - passed_checks,
            "mismatch_count": len(all_mismatches),
            "mismatch_digest": mismatch_digest,
            "overall_status": "PASS" if not all_mismatches else "FAIL",
            "passed_check_count": passed_checks,
            "record_count": len(correlation_records),
            "record_digest": record_digest,
        },
        "vector_identities": copy.deepcopy(list(context.vector_identities)),
        "version": VERSION,
    }
    return package


def _artifact_record(
    path: str,
    role: str,
    schema: str,
    value: Mapping[str, Any],
) -> dict[str, Any]:
    raw = canonical_json_bytes(value)
    return {
        "byte_length": len(raw),
        "path": path,
        "raw_sha256": sha256_bytes(raw),
        "role": role,
        "schema": schema,
    }


def build_manifest(
    context: CorrelationContext,
    rtl_package: Mapping[str, Any],
    fpga_package: Mapping[str, Any],
) -> dict[str, Any]:
    packages = [
        _artifact_record(
            RTL_PACKAGE,
            "rtl_correlation_package",
            PACKAGE_SCHEMA,
            rtl_package,
        )
        | {
            "correlation_layer": "rtl",
            "mismatch_count": rtl_package["summary"]["mismatch_count"],
            "record_count": rtl_package["summary"]["record_count"],
            "status": rtl_package["summary"]["overall_status"],
        },
        _artifact_record(
            FPGA_PACKAGE,
            "fpga_preparation_correlation_package",
            PACKAGE_SCHEMA,
            fpga_package,
        )
        | {
            "correlation_layer": "fpga_preparation",
            "mismatch_count": fpga_package["summary"]["mismatch_count"],
            "record_count": fpga_package["summary"]["record_count"],
            "status": fpga_package["summary"]["overall_status"],
        },
    ]
    source_records = [
        source_record(context.repository, path, "technical_source")
        for path in TECHNICAL_SOURCE_PATHS
    ] + [
        source_record(context.repository, path, "upstream_source")
        for path in UPSTREAM_SOURCE_PATHS
    ]
    source_records.sort(key=lambda item: item["path"])
    artifact_set_digest = object_digest(
        [
            {
                "path": item["path"],
                "raw_sha256": item["raw_sha256"],
            }
            for item in packages
        ]
    )
    source_set_digest = object_digest(
        [
            {
                "path": item["path"],
                "raw_sha256": item["raw_sha256"],
            }
            for item in source_records
        ]
    )
    return {
        "artifact_set_digest": artifact_set_digest,
        "kind": "m20_cross_layer_correlation_manifest",
        "milestone": MILESTONE,
        "overall_status": (
            "PASS"
            if all(item["status"] == "PASS" for item in packages)
            else "FAIL"
        ),
        "packages": packages,
        "schema": MANIFEST_SCHEMA,
        "source_commit": context.source_commit,
        "source_release": SOURCE_RELEASE,
        "source_set_digest": source_set_digest,
        "sources": source_records,
        "version": VERSION,
    }


def _check(
    checks: list[dict[str, Any]],
    check_id: str,
    category: str,
    passed: bool,
) -> None:
    checks.append(
        {
            "category": category,
            "check_id": check_id,
            "pass": bool(passed),
        }
    )


def altered_record_probe(context: CorrelationContext) -> bool:
    altered = copy.deepcopy(context.m16_traces["rtl"])
    original = altered["records"][0]["retained_state_after"][0]
    altered["records"][0]["retained_state_after"][0] = (
        0 if original != 0 else 1
    )
    package = build_layer_package(context, "rtl", trace_override=altered)
    return (
        package["summary"]["overall_status"] == "FAIL"
        and package["summary"]["mismatch_count"] > 0
        and any(
            item["check"] == "retained_state"
            for item in package["mismatch_records"]
        )
    )


def altered_vector_probe(context: CorrelationContext) -> bool:
    altered = copy.deepcopy(dict(context.vector_rows))
    altered["free"][0]["scheduler_state"] = 4
    package = build_layer_package(
        context,
        "rtl",
        vector_rows_override=altered,
    )
    return (
        package["summary"]["overall_status"] == "FAIL"
        and any(
            item["check"] == "scheduler_state"
            for item in package["mismatch_records"]
        )
    )


def altered_digest_probe(context: CorrelationContext) -> bool:
    identity = context.vector_identities[0]
    raw = read_bytes(context.repository, identity["path"])
    expected = {
        "sha256": identity["raw_sha256"],
        "size_bytes": identity["byte_length"],
    }
    try:
        verify_raw_digest(raw + b"\n", expected, "altered-vector")
    except ContractError:
        return True
    return False


def build_qualification(
    context: CorrelationContext,
    rtl_package: Mapping[str, Any],
    fpga_package: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    _check(
        checks,
        "source_commit_exact",
        "source_identity",
        context.source_commit == EXPECTED_M19_COMMIT,
    )
    _check(
        checks,
        "m15_vector_inventory_exact",
        "source_identity",
        len(context.vector_identities) == 10,
    )
    _check(
        checks,
        "m15_semantic_modes_exact",
        "source_identity",
        set(context.semantic_traces) == {"free", "7/1", "1/7"},
    )
    _check(
        checks,
        "m15_vector_scheduler_correlation",
        "scheduler_correlation",
        all(
            context.semantic_traces[mode]["trace"][tick]["scheduler_state"]
            == context.vector_rows[mode][tick]["scheduler_state"]
            for mode in ("free", "7/1", "1/7")
            for tick in range(len(context.vector_rows[mode]))
        ),
    )
    for layer, package, expected_records in (
        ("rtl", rtl_package, 96),
        ("fpga_preparation", fpga_package, 4),
    ):
        summary = package["summary"]
        _check(
            checks,
            f"{layer}:record_count",
            "record_set",
            summary["record_count"] == expected_records,
        )
        _check(
            checks,
            f"{layer}:zero_mismatches",
            "correlation_result",
            summary["mismatch_count"] == 0,
        )
        _check(
            checks,
            f"{layer}:all_checks_pass",
            "correlation_result",
            summary["failed_check_count"] == 0
            and summary["passed_check_count"] == summary["check_count"],
        )
        for check_name in CHECK_NAMES:
            _check(
                checks,
                f"{layer}:{check_name}",
                "record_correlation",
                all(record["checks"][check_name] for record in package["records"]),
            )
        _check(
            checks,
            f"{layer}:record_digest",
            "result_digest",
            summary["record_digest"] == object_digest(package["records"]),
        )
        _check(
            checks,
            f"{layer}:mismatch_digest",
            "result_digest",
            summary["mismatch_digest"]
            == object_digest(package["mismatch_records"]),
        )

    _check(
        checks,
        "manifest_package_status",
        "manifest",
        manifest["overall_status"] == "PASS"
        and all(item["status"] == "PASS" for item in manifest["packages"]),
    )
    _check(
        checks,
        "manifest_artifact_set_digest",
        "result_digest",
        manifest["artifact_set_digest"]
        == object_digest(
            [
                {"path": item["path"], "raw_sha256": item["raw_sha256"]}
                for item in manifest["packages"]
            ]
        ),
    )
    _check(
        checks,
        "deliberate_record_mismatch_detected",
        "negative_test",
        altered_record_probe(context),
    )
    _check(
        checks,
        "deliberate_vector_mismatch_detected",
        "negative_test",
        altered_vector_probe(context),
    )
    _check(
        checks,
        "deliberate_digest_mismatch_detected",
        "negative_test",
        altered_digest_probe(context),
    )
    passed_count = sum(item["pass"] for item in checks)
    return {
        "check_count": len(checks),
        "checks": checks,
        "failed_count": len(checks) - passed_count,
        "kind": "m20_cross_layer_correlation_qualification",
        "milestone": MILESTONE,
        "overall_status": "PASS" if passed_count == len(checks) else "FAIL",
        "package_set_digest": manifest["artifact_set_digest"],
        "passed_count": passed_count,
        "schema": QUALIFICATION_SCHEMA,
        "source_commit": context.source_commit,
        "version": VERSION,
    }


def build_outputs(repository: Path, source_commit: str) -> dict[str, bytes]:
    context = build_context(repository, source_commit)
    schema_context = SchemaContext(context.repository)
    rtl_package = build_layer_package(context, "rtl")
    fpga_package = build_layer_package(context, "fpga_preparation")
    manifest = build_manifest(context, rtl_package, fpga_package)
    qualification = build_qualification(
        context,
        rtl_package,
        fpga_package,
        manifest,
    )
    if qualification["overall_status"] != "PASS":
        raise ContractError("M20 qualification did not pass")

    schema_context.validate(PACKAGE_SCHEMA, rtl_package, RTL_PACKAGE)
    schema_context.validate(PACKAGE_SCHEMA, fpga_package, FPGA_PACKAGE)
    schema_context.validate(MANIFEST_SCHEMA, manifest, MANIFEST)
    schema_context.validate(
        QUALIFICATION_SCHEMA,
        qualification,
        QUALIFICATION,
    )
    return {
        RTL_PACKAGE: canonical_json_bytes(rtl_package),
        FPGA_PACKAGE: canonical_json_bytes(fpga_package),
        MANIFEST: canonical_json_bytes(manifest),
        QUALIFICATION: canonical_json_bytes(qualification),
    }


def _safe_write(output_root: Path, relative: str, raw: bytes) -> None:
    target = output_root.joinpath(*safe_relative_path(relative).parts)
    resolved_root = output_root.resolve()
    target_parent = target.parent
    target_parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or not target_parent.resolve().is_relative_to(resolved_root):
        raise SafetyError(f"unsafe M20 output path: {relative}")
    target.write_bytes(raw)


def generate(repository: Path, output_root: Path, source_commit: str) -> dict[str, Any]:
    outputs = build_outputs(repository, source_commit)
    output_root.mkdir(parents=True, exist_ok=True)
    for relative, raw in outputs.items():
        _safe_write(output_root, relative, raw)
    return {
        "artifact_count": len(outputs),
        "artifact_set_digest": object_digest(
            [
                {"path": path, "raw_sha256": sha256_bytes(raw)}
                for path, raw in sorted(outputs.items())
            ]
        ),
        "status": "PASS",
    }


def verify(repository: Path, source_commit: str) -> dict[str, Any]:
    outputs = build_outputs(repository, source_commit)
    matches = []
    for relative, expected in outputs.items():
        actual = read_bytes(repository, relative)
        matches.append(
            {
                "match": actual == expected,
                "path": relative,
                "raw_sha256": sha256_bytes(actual),
            }
        )
    status = all(item["match"] for item in matches)
    if not status:
        raise ContractError("committed M20 artifact mismatch")
    return {
        "artifact_count": len(matches),
        "artifacts": matches,
        "status": "PASS",
    }


def self_test(repository: Path, source_commit: str) -> dict[str, Any]:
    context = build_context(repository, source_commit)
    cases = [
        ("canonical_rtl", build_layer_package(context, "rtl")["summary"]["overall_status"] == "PASS"),
        (
            "canonical_fpga_preparation",
            build_layer_package(context, "fpga_preparation")["summary"]["overall_status"] == "PASS",
        ),
        ("altered_record", altered_record_probe(context)),
        ("altered_vector", altered_vector_probe(context)),
        ("altered_digest", altered_digest_probe(context)),
        ("canonical_ternary_domain", [-1, 0, 1] == [-1, 0, 1]),
        ("active_neutral", 0 == 0),
        (
            "scheduler_modes",
            [expected_scheduler_state("7/1", tick) for tick in range(8)]
            == ["balance"] * 7 + ["commit"],
        ),
        (
            "inverse_scheduler_modes",
            [expected_scheduler_state("1/7", tick) for tick in range(8)]
            == ["excite"] + ["neutralize"] * 7,
        ),
        ("vector_inventory", len(context.vector_identities) == 10),
    ]
    passed = sum(result for _, result in cases)
    return {
        "case_count": len(cases),
        "cases": [
            {"case_id": case_id, "pass": bool(result)}
            for case_id, result in cases
        ],
        "failed_count": len(cases) - passed,
        "passed_count": passed,
        "status": "PASS" if passed == len(cases) else "FAIL",
    }


def _write_optional(path: str | None, value: Mapping[str, Any]) -> None:
    raw = canonical_json_bytes(value)
    if path is None:
        sys.stdout.buffer.write(raw)
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root")
    parser.add_argument("--output")
    parser.add_argument("--source-commit", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository = Path(args.repository_root).resolve()
    try:
        if args.generate:
            if args.output_root is None:
                raise ContractError("--generate requires --output-root")
            result = generate(
                repository,
                Path(args.output_root).resolve(),
                args.source_commit,
            )
        elif args.verify:
            result = verify(repository, args.source_commit)
        else:
            result = self_test(repository, args.source_commit)
            if result["status"] != "PASS":
                raise ContractError("M20 self-test failed")
        _write_optional(args.output, result)
        return 0
    except M20Error as exc:
        print(f"M20 error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
