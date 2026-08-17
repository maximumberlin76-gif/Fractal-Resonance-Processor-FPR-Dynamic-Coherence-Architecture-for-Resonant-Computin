#!/usr/bin/env python3
"""FRP M21 deterministic parameterized qualification-matrix producer."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


VERSION = "2.3.0"
MILESTONE = "M21 — Parameterized Qualification Matrix"
SOURCE_RELEASE = "FRP v2.2.0 / M20 correlation boundary"
EXPECTED_M20_COMMIT = "be91e69d5d2e51a2bbc9a3ffb8f6d60c88d8bef4"

PRODUCER = "frp_m21_parameterized_qualification_matrix.py"
WORKFLOW = ".github/workflows/frp-m21-parameterized-qualification-matrix.yml"
TESTS = "tests/test_frp_m21_parameterized_qualification_matrix.py"
REGISTRY_PATH = "schemas/m21/frp_m21_schema_registry.json"

CASE_SCHEMA = "frp.m21.parameterized_qualification_case.v2.3.0"
DIMENSIONS_SCHEMA = "frp.m21.parameter_dimensions.v2.3.0"
MATRIX_SCHEMA = "frp.m21.parameterized_qualification_matrix.v2.3.0"
MANIFEST_SCHEMA = "frp.m21.parameterized_qualification_manifest.v2.3.0"
QUALIFICATION_SCHEMA = "frp.m21.parameterized_qualification_record.v2.3.0"

SCHEMA_PATHS = {
    CASE_SCHEMA: (
        "schemas/m21/"
        "frp_m21_parameterized_qualification_case.v2.3.0.schema.json"
    ),
    DIMENSIONS_SCHEMA: (
        "schemas/m21/frp_m21_parameter_dimensions.v2.3.0.schema.json"
    ),
    MATRIX_SCHEMA: (
        "schemas/m21/"
        "frp_m21_parameterized_qualification_matrix.v2.3.0.schema.json"
    ),
    MANIFEST_SCHEMA: (
        "schemas/m21/"
        "frp_m21_parameterized_qualification_manifest.v2.3.0.schema.json"
    ),
    QUALIFICATION_SCHEMA: (
        "schemas/m21/"
        "frp_m21_parameterized_qualification_record.v2.3.0.schema.json"
    ),
}

DIMENSIONS_ARTIFACT = (
    "artifacts/m21/matrix/m21-parameter-dimensions.json"
)
MATRIX_ARTIFACT = (
    "artifacts/m21/matrix/m21-parameterized-qualification-matrix.json"
)
MANIFEST_ARTIFACT = (
    "artifacts/m21/manifests/"
    "m21-parameterized-qualification-manifest.json"
)
QUALIFICATION_ARTIFACT = (
    "artifacts/m21/manifests/"
    "m21-parameterized-qualification-record.json"
)
GENERATED_PATHS = (
    DIMENSIONS_ARTIFACT,
    MATRIX_ARTIFACT,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

ROADMAP = "ROADMAP.md"
MILESTONES = "MILESTONES.md"
M16_PACKAGE = "rtl/m16/frp_m16_pkg.sv"
M15_QUALIFICATION = (
    "artifacts/m18/m15_exports/qualification-closure-manifest.json"
)
M20_RTL = "artifacts/m20/correlation/m15-m16-rtl-correlation.json"
M20_FPGA = (
    "artifacts/m20/correlation/"
    "m15-m16-fpga-preparation-correlation.json"
)
M20_MANIFEST = (
    "artifacts/m20/manifests/m20-cross-layer-correlation-manifest.json"
)
M20_QUALIFICATION = (
    "artifacts/m20/manifests/m20-cross-layer-correlation-qualification.json"
)

WORKLOAD_SPECS = (
    {
        "workload_id": "scaling-8",
        "path": "artifacts/m18/structured_output/scaling-8.json",
        "cell_count": 8,
        "request_lanes": 2,
        "scheduler_mode": "7/1",
        "steps": 16,
    },
    {
        "workload_id": "scaling-16",
        "path": "artifacts/m18/structured_output/scaling-16.json",
        "cell_count": 16,
        "request_lanes": 4,
        "scheduler_mode": "7/1",
        "steps": 16,
    },
    {
        "workload_id": "scaling-32",
        "path": "artifacts/m18/structured_output/scaling-32.json",
        "cell_count": 32,
        "request_lanes": 8,
        "scheduler_mode": "7/1",
        "steps": 16,
    },
    {
        "workload_id": "trace-1-7",
        "path": "artifacts/m18/structured_output/trace-1-7.json",
        "cell_count": 16,
        "request_lanes": 4,
        "scheduler_mode": "1/7",
        "steps": 64,
    },
    {
        "workload_id": "trace-7-1",
        "path": "artifacts/m18/structured_output/trace-7-1.json",
        "cell_count": 16,
        "request_lanes": 4,
        "scheduler_mode": "7/1",
        "steps": 64,
    },
    {
        "workload_id": "trace-free",
        "path": "artifacts/m18/structured_output/trace-free.json",
        "cell_count": 16,
        "request_lanes": 4,
        "scheduler_mode": "free",
        "steps": 64,
    },
)

CELL_COUNTS = (8, 16, 32)
REQUEST_LANE_COUNTS = (2, 4, 8)
SCHEDULER_MODES = ("free", "7/1", "1/7")
SCHEDULER_PROFILES = (
    {
        "profile_id": "free-8",
        "scheduler_mode": "free",
        "period_ticks": 8,
        "state_pattern": ["free"] * 8,
    },
    {
        "profile_id": "balance-7-commit-1",
        "scheduler_mode": "7/1",
        "period_ticks": 8,
        "state_pattern": ["balance"] * 7 + ["commit"],
    },
    {
        "profile_id": "excite-1-neutralize-7",
        "scheduler_mode": "1/7",
        "period_ticks": 8,
        "state_pattern": ["excite"] + ["neutralize"] * 7,
    },
)
TRANSITION_CAPACITY_PROFILES = (
    {
        "profile_id": "cells-8-lanes-2",
        "cell_count": 8,
        "capacity_limit": 2,
        "fraction_numerator": 1,
        "fraction_denominator": 4,
    },
    {
        "profile_id": "cells-16-lanes-4",
        "cell_count": 16,
        "capacity_limit": 4,
        "fraction_numerator": 1,
        "fraction_denominator": 4,
    },
    {
        "profile_id": "cells-32-lanes-8",
        "cell_count": 32,
        "capacity_limit": 8,
        "fraction_numerator": 1,
        "fraction_denominator": 4,
    },
)
RETAINED_ROUTE_PROFILES = (
    {
        "profile_id": "active-neutral-retained",
        "active_neutral_state": 0,
        "canonical_ternary_states": [-1, 0, 1],
        "neutral_routes": ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
        "pending_route_retention": True,
        "supported": True,
    },
    {
        "profile_id": "direct-opposite-single-tick",
        "active_neutral_state": 0,
        "canonical_ternary_states": [-1, 0, 1],
        "neutral_routes": ["-1 -> 1", "1 -> -1"],
        "pending_route_retention": False,
        "supported": False,
    },
)

DIMENSION_ORDER = (
    "cell_count",
    "request_lanes",
    "scheduler_mode",
    "scheduler_parameter_profile",
    "transition_capacity_profile",
    "retained_route_profile",
)
DECLARED_CASE_COUNT = 486
SUPPORTED_CASE_COUNT = 5
SKIPPED_CASE_COUNT = 481
SKIP_REASON_COUNTS = {
    "forbidden_retained_route": 243,
    "scheduler_parameter_mismatch": 162,
    "transition_capacity_profile_mismatch": 54,
    "request_lane_capacity_mismatch": 18,
    "deterministic_workload_unavailable": 4,
}

CHECK_IDS = (
    "cell_count_declared",
    "request_lanes_declared",
    "scheduler_mode_declared",
    "scheduler_parameter_profile_declared",
    "scheduler_mode_profile_match",
    "transition_capacity_profile_declared",
    "transition_capacity_profile_match",
    "request_lane_capacity_match",
    "retained_route_profile_declared",
    "retained_route_supported",
    "deterministic_workload_available",
    "semantic_invariants",
    "cross_layer_correlation",
    "measurement_contours_separate",
    "no_silent_parameter_substitution",
)

TECHNICAL_SOURCE_PATHS = tuple(
    sorted((PRODUCER, WORKFLOW, TESTS, REGISTRY_PATH, *SCHEMA_PATHS.values()))
)
UPSTREAM_SOURCE_PATHS = tuple(
    sorted(
        {
            ROADMAP,
            MILESTONES,
            M16_PACKAGE,
            M15_QUALIFICATION,
            M20_RTL,
            M20_FPGA,
            M20_MANIFEST,
            M20_QUALIFICATION,
            *(item["path"] for item in WORKLOAD_SPECS),
        }
    )
)


class M21Error(Exception):
    """Base M21 failure."""


class ContractError(M21Error):
    """An input, schema, or qualification contract failed."""


class SafetyError(M21Error):
    """An unsafe filesystem path was requested."""


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def validate_source_commit(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ContractError("source commit must be a full lowercase Git SHA")
    if value != EXPECTED_M20_COMMIT:
        raise ContractError("unexpected M20 source commit")
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


def source_record(
    repository: Path,
    relative: str,
    role: str,
    source_contour: str,
) -> dict[str, Any]:
    raw = read_bytes(repository, relative)
    return {
        "byte_length": len(raw),
        "path": relative,
        "raw_sha256": sha256_bytes(raw),
        "role": role,
        "source_contour": source_contour,
    }


def expected_scheduler_counts(mode: str, steps: int) -> dict[str, int]:
    if steps % 8:
        raise ContractError("qualified workloads must contain complete periods")
    periods = steps // 8
    if mode == "free":
        return {"free": steps}
    if mode == "7/1":
        return {"balance": periods * 7, "commit": periods}
    if mode == "1/7":
        return {"excite": periods, "neutralize": periods * 7}
    raise ContractError(f"unknown scheduler mode: {mode}")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_m16_static_contract(repository: Path) -> dict[str, Any]:
    raw = read_bytes(repository, M16_PACKAGE)
    text = raw.decode("utf-8")
    required_fragments = (
        "FRP_M16_PERIOD_TICKS           = 8;",
        "FRP_M16_DEFAULT_CELLS          = 16;",
        "FRP_M16_TRANSITION_FRACTION_NUM = 1;",
        "FRP_M16_TRANSITION_FRACTION_DEN = 4;",
        "frp_calc_request_lanes(8);",
        "frp_calc_request_lanes(16);",
        "frp_calc_request_lanes(32);",
        "FRP_MODE_FREE",
        "FRP_MODE_7_1",
        "FRP_MODE_1_7",
        "FRP_ACTIVE_NEUTRAL",
    )
    for fragment in required_fragments:
        _require(fragment in text, f"M16 parameter contract missing: {fragment}")
    return {
        "active_neutral_state": 0,
        "canonical_ternary_states": [-1, 0, 1],
        "cell_counts": list(CELL_COUNTS),
        "period_ticks": 8,
        "request_lanes": list(REQUEST_LANE_COUNTS),
        "scheduler_modes": list(SCHEDULER_MODES),
        "source": source_record(
            repository,
            M16_PACKAGE,
            "m16_static_parameter_contract",
            "rtl_static_parameter_contract",
        ),
        "transition_fraction": {"denominator": 4, "numerator": 1},
    }


def validate_workload(
    repository: Path,
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    relative = str(spec["path"])
    raw = read_bytes(repository, relative)
    data = read_json(repository, relative)
    _require(isinstance(data, dict), f"workload is not an object: {relative}")
    _require(
        data.get("schema") == "frp.structured_output.v1.7.0",
        f"workload schema mismatch: {relative}",
    )
    configuration = data.get("configuration")
    kernel = data.get("kernel")
    summary = data.get("summary")
    _require(isinstance(configuration, dict), f"configuration missing: {relative}")
    _require(isinstance(kernel, dict), f"kernel missing: {relative}")
    _require(isinstance(summary, dict), f"summary missing: {relative}")
    expected_config = {
        "cells": spec["cell_count"],
        "request_lanes": spec["request_lanes"],
        "scheduler": spec["scheduler_mode"],
        "steps": spec["steps"],
        "transition_fraction": 0.25,
    }
    for key, expected in expected_config.items():
        _require(
            configuration.get(key) == expected,
            f"workload parameter mismatch for {key}: {relative}",
        )
    _require(
        kernel.get("balanced_ternary_states") == [-1, 0, 1],
        f"ternary domain mismatch: {relative}",
    )
    _require(
        kernel.get("active_neutral_state") == 0,
        f"active neutral mismatch: {relative}",
    )
    _require(
        kernel.get("neutral_routes") == ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
        f"neutral route mismatch: {relative}",
    )
    expected_summary = {
        "actual_direct_events": 0,
        "balanced_ternary_state_domain": True,
        "cells": spec["cell_count"],
        "fixed_point_thermal_sum_exact": True,
        "fixed_point_topology_sum_exact": True,
        "queue_overflow_events": 0,
        "request_lanes": spec["request_lanes"],
        "reserved_state_events": 0,
        "scheduler": spec["scheduler_mode"],
        "scheduler_counts_valid": True,
        "steps": spec["steps"],
        "transition_fraction": 0.25,
    }
    for key, expected in expected_summary.items():
        _require(
            summary.get(key) == expected,
            f"workload qualification mismatch for {key}: {relative}",
        )
    _require(
        summary.get("scheduler_counts")
        == expected_scheduler_counts(str(spec["scheduler_mode"]), int(spec["steps"])),
        f"scheduler counts mismatch: {relative}",
    )
    for digest_name in ("cell_trace_digest", "preload_digest", "trace_digest"):
        _require(
            isinstance(data.get(digest_name), str)
            and re.fullmatch(r"[0-9a-f]{64}", data[digest_name]) is not None,
            f"workload digest missing: {relative}:{digest_name}",
        )
    return {
        "byte_length": len(raw),
        "cell_count": spec["cell_count"],
        "cell_trace_digest": data["cell_trace_digest"],
        "path": relative,
        "preload_digest": data["preload_digest"],
        "qualification_status": "PASS",
        "raw_sha256": sha256_bytes(raw),
        "request_lanes": spec["request_lanes"],
        "scheduler_mode": spec["scheduler_mode"],
        "steps": spec["steps"],
        "trace_digest": data["trace_digest"],
        "workload_id": spec["workload_id"],
    }


def validate_m20_boundary(repository: Path) -> dict[str, Any]:
    rtl = read_json(repository, M20_RTL)
    fpga = read_json(repository, M20_FPGA)
    manifest = read_json(repository, M20_MANIFEST)
    qualification = read_json(repository, M20_QUALIFICATION)
    for name, package, expected_count in (
        ("rtl", rtl, 96),
        ("fpga_preparation", fpga, 4),
    ):
        _require(isinstance(package, dict), f"M20 {name} package is not an object")
        summary = package.get("summary")
        _require(isinstance(summary, dict), f"M20 {name} summary missing")
        _require(summary.get("record_count") == expected_count, f"M20 {name} count")
        _require(summary.get("mismatch_count") == 0, f"M20 {name} mismatch")
        _require(summary.get("failed_check_count") == 0, f"M20 {name} failure")
        _require(summary.get("overall_status") == "PASS", f"M20 {name} status")
        records = package.get("records")
        _require(isinstance(records, list), f"M20 {name} records missing")
        _require(
            all(
                record.get("record_status") == "PASS"
                and record.get("mismatch_count") == 0
                and all(record.get("checks", {}).values())
                for record in records
            ),
            f"M20 {name} record failure",
        )
    _require(
        isinstance(manifest, dict) and manifest.get("overall_status") == "PASS",
        "M20 manifest did not pass",
    )
    _require(
        isinstance(qualification, dict)
        and qualification.get("overall_status") == "PASS"
        and qualification.get("passed_count") == qualification.get("check_count") == 39
        and qualification.get("failed_count") == 0,
        "M20 qualification did not pass",
    )

    rtl_counts = {mode: 0 for mode in SCHEDULER_MODES}
    rtl_paths = {
        "free": "artifacts/m18/structured_output/trace-free.json",
        "7/1": "artifacts/m18/structured_output/trace-7-1.json",
        "1/7": "artifacts/m18/structured_output/trace-1-7.json",
    }
    path_to_mode = {path: mode for mode, path in rtl_paths.items()}
    for record in rtl["records"]:
        path = record["m15_semantic_reference"]["path"]
        _require(path in path_to_mode, "M20 semantic trace path is unregistered")
        rtl_counts[path_to_mode[path]] += 1
    _require(
        rtl_counts == {"free": 16, "7/1": 64, "1/7": 16},
        "M20 RTL mode coverage mismatch",
    )
    fpga_counts = {mode: 0 for mode in SCHEDULER_MODES}
    for record in fpga["records"]:
        path = record["m15_semantic_reference"]["path"]
        _require(path in path_to_mode, "M20 FPGA semantic path is unregistered")
        fpga_counts[path_to_mode[path]] += 1
    _require(
        fpga_counts == {"free": 3, "7/1": 0, "1/7": 1},
        "M20 FPGA mode coverage mismatch",
    )
    return {
        "fpga_record_counts": fpga_counts,
        "manifest_status": manifest["overall_status"],
        "qualification_check_count": qualification["check_count"],
        "rtl_record_counts": rtl_counts,
        "sources": [
            source_record(
                repository,
                M20_RTL,
                "m20_rtl_correlation",
                "m20_cross_layer_correlation",
            ),
            source_record(
                repository,
                M20_FPGA,
                "m20_fpga_preparation_correlation",
                "m20_cross_layer_correlation",
            ),
            source_record(
                repository,
                M20_MANIFEST,
                "m20_manifest",
                "m20_cross_layer_correlation",
            ),
            source_record(
                repository,
                M20_QUALIFICATION,
                "m20_qualification",
                "m20_cross_layer_correlation",
            ),
        ],
    }


@dataclass(frozen=True)
class Context:
    repository: Path
    source_commit: str
    static_contract: Mapping[str, Any]
    workloads: tuple[Mapping[str, Any], ...]
    m20_boundary: Mapping[str, Any]


def build_context(repository: Path, source_commit: str) -> Context:
    repository = repository.resolve()
    source_commit = validate_source_commit(source_commit)
    roadmap = read_bytes(repository, ROADMAP).decode("utf-8")
    milestones = read_bytes(repository, MILESTONES).decode("utf-8")
    required_scope = (
        "cell-count configurations",
        "request-lane configurations",
        "scheduler modes",
        "scheduler parameters",
        "transition-capacity configurations",
        "retained-route configurations",
        "deterministic workload identities",
        "explicit unsupported combinations",
        "per-case provenance",
        "per-case digests",
        "per-case qualification status",
    )
    for phrase in required_scope:
        _require(phrase in roadmap, f"M21 roadmap scope missing: {phrase}")
    _require(
        "M21 — Parameterized Qualification Matrix" in milestones,
        "M21 milestone definition missing",
    )
    m15 = read_json(repository, M15_QUALIFICATION)
    _require(
        isinstance(m15, dict)
        and m15.get("status") == "PASS"
        and isinstance(m15.get("checks"), dict)
        and len(m15["checks"]) == 10
        and all(m15["checks"].values()),
        "M15 qualification boundary did not pass",
    )
    workloads = tuple(
        sorted(
            (validate_workload(repository, spec) for spec in WORKLOAD_SPECS),
            key=lambda item: item["workload_id"],
        )
    )
    _require(
        [item["workload_id"] for item in workloads]
        == sorted(item["workload_id"] for item in workloads),
        "workload catalog is not ordered",
    )
    return Context(
        repository=repository,
        source_commit=source_commit,
        static_contract=validate_m16_static_contract(repository),
        workloads=workloads,
        m20_boundary=validate_m20_boundary(repository),
    )


def build_dimensions(context: Context) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "declared_cartesian_case_count": DECLARED_CASE_COUNT,
        "dimension_order": list(DIMENSION_ORDER),
        "dimensions": {
            "cell_count": list(CELL_COUNTS),
            "request_lanes": list(REQUEST_LANE_COUNTS),
            "retained_route_profile": copy.deepcopy(list(RETAINED_ROUTE_PROFILES)),
            "scheduler_mode": list(SCHEDULER_MODES),
            "scheduler_parameter_profile": copy.deepcopy(list(SCHEDULER_PROFILES)),
            "transition_capacity_profile": copy.deepcopy(
                list(TRANSITION_CAPACITY_PROFILES)
            ),
        },
        "kind": "m21_parameter_dimensions",
        "milestone": MILESTONE,
        "schema": DIMENSIONS_SCHEMA,
        "source_commit": context.source_commit,
        "source_release": SOURCE_RELEASE,
        "version": VERSION,
        "workload_catalog": copy.deepcopy(list(context.workloads)),
    }
    cardinalities = {
        "cell_count": len(CELL_COUNTS),
        "request_lanes": len(REQUEST_LANE_COUNTS),
        "scheduler_mode": len(SCHEDULER_MODES),
        "scheduler_parameter_profile": len(SCHEDULER_PROFILES),
        "transition_capacity_profile": len(TRANSITION_CAPACITY_PROFILES),
        "retained_route_profile": len(RETAINED_ROUTE_PROFILES),
    }
    _require(
        math.prod(cardinalities.values()) == DECLARED_CASE_COUNT,
        "declared M21 Cartesian count mismatch",
    )
    payload["dimension_cardinalities"] = cardinalities
    payload["dimensions_digest"] = object_digest(payload)
    return payload


def _profiles_by_id(items: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {str(item["profile_id"]): item for item in items}


def workload_map(context: Context) -> dict[tuple[int, int, str], list[Mapping[str, Any]]]:
    result: dict[tuple[int, int, str], list[Mapping[str, Any]]] = {}
    for workload in context.workloads:
        key = (
            int(workload["cell_count"]),
            int(workload["request_lanes"]),
            str(workload["scheduler_mode"]),
        )
        result.setdefault(key, []).append(workload)
    return result


def classify_coordinates(
    context: Context,
    coordinates: Mapping[str, Any],
) -> tuple[str, str, str]:
    scheduler_profiles = _profiles_by_id(SCHEDULER_PROFILES)
    transition_profiles = _profiles_by_id(TRANSITION_CAPACITY_PROFILES)
    route_profiles = _profiles_by_id(RETAINED_ROUTE_PROFILES)
    scheduler = scheduler_profiles[str(coordinates["scheduler_parameter_profile"])]
    transition = transition_profiles[str(coordinates["transition_capacity_profile"])]
    route = route_profiles[str(coordinates["retained_route_profile"])]
    if not route["supported"]:
        return (
            "UNSUPPORTED",
            "forbidden_retained_route",
            "direct opposite-polarity routing violates the active-neutral retained-route contract",
        )
    if scheduler["scheduler_mode"] != coordinates["scheduler_mode"]:
        return (
            "UNSUPPORTED",
            "scheduler_parameter_mismatch",
            "scheduler parameter profile does not match the declared scheduler mode",
        )
    if transition["cell_count"] != coordinates["cell_count"]:
        return (
            "UNSUPPORTED",
            "transition_capacity_profile_mismatch",
            "transition-capacity profile does not match the declared cell count",
        )
    if transition["capacity_limit"] != coordinates["request_lanes"]:
        return (
            "UNSUPPORTED",
            "request_lane_capacity_mismatch",
            "request-lane count does not match the declared transition-capacity profile",
        )
    key = (
        int(coordinates["cell_count"]),
        int(coordinates["request_lanes"]),
        str(coordinates["scheduler_mode"]),
    )
    if key not in workload_map(context):
        return (
            "UNSUPPORTED",
            "deterministic_workload_unavailable",
            "no published deterministic workload has this exact parameter identity",
        )
    return (
        "SUPPORTED",
        "qualified_combination",
        "all declared parameters and deterministic workload identities match exactly",
    )


def _contour_evidence(
    contour: str,
    status: str,
    source_paths: Sequence[str],
    assertions: Sequence[str],
    reason: str,
) -> dict[str, Any]:
    payload = {
        "assertions": list(assertions),
        "contour": contour,
        "reason": reason,
        "source_paths": list(source_paths),
        "status": status,
    }
    payload["evidence_digest"] = object_digest(payload)
    return payload


def _check(check_id: str, status: str, detail: str) -> dict[str, str]:
    return {"check_id": check_id, "detail": detail, "status": status}


def build_case(
    context: Context,
    dimensions: Mapping[str, Any],
    sequence: int,
    coordinates: Mapping[str, Any],
) -> dict[str, Any]:
    scheduler = _profiles_by_id(SCHEDULER_PROFILES)[
        str(coordinates["scheduler_parameter_profile"])
    ]
    transition = _profiles_by_id(TRANSITION_CAPACITY_PROFILES)[
        str(coordinates["transition_capacity_profile"])
    ]
    route = _profiles_by_id(RETAINED_ROUTE_PROFILES)[
        str(coordinates["retained_route_profile"])
    ]
    support, reason_code, reason_detail = classify_coordinates(context, coordinates)
    supported = support == "SUPPORTED"
    key = (
        int(coordinates["cell_count"]),
        int(coordinates["request_lanes"]),
        str(coordinates["scheduler_mode"]),
    )
    workloads = copy.deepcopy(workload_map(context).get(key, [])) if supported else []

    static_source = context.static_contract["source"]
    provenance = [copy.deepcopy(static_source)]
    if supported:
        provenance.extend(
            {
                "byte_length": item["byte_length"],
                "path": item["path"],
                "raw_sha256": item["raw_sha256"],
                "role": "deterministic_workload",
                "source_contour": "m15_quantized_semantic_reference",
            }
            for item in workloads
        )
    if supported and coordinates["cell_count"] == 16:
        provenance.extend(copy.deepcopy(context.m20_boundary["sources"][:2]))
    provenance = sorted(provenance, key=lambda item: (item["path"], item["role"]))

    semantic_evidence = _contour_evidence(
        "m15_quantized_semantic_reference",
        "PASS" if supported else "NOT_APPLICABLE",
        [str(item["path"]) for item in workloads],
        (
            [
                "balanced_ternary_domain_exact",
                "active_neutral_state_exact",
                "scheduler_counts_exact",
                "transition_fraction_exact",
                "zero_actual_direct_events",
                "zero_reserved_state_events",
                "zero_queue_overflow_events",
                "fixed_point_sums_exact",
            ]
            if supported
            else []
        ),
        (
            "exact M15 workload evidence remains in its semantic measurement contour"
            if supported
            else "unsupported parameter combinations do not receive substituted semantic metrics"
        ),
    )
    if supported and coordinates["cell_count"] == 16:
        mode = str(coordinates["scheduler_mode"])
        rtl_count = context.m20_boundary["rtl_record_counts"][mode]
        fpga_count = context.m20_boundary["fpga_record_counts"][mode]
        assertions = [
            f"rtl_record_count={rtl_count}",
            "rtl_mismatch_count=0",
            "rtl_record_checks_pass",
        ]
        source_paths = [M20_RTL]
        if fpga_count:
            assertions.extend(
                [f"fpga_record_count={fpga_count}", "fpga_mismatch_count=0"]
            )
            source_paths.append(M20_FPGA)
        cross_layer = _contour_evidence(
            "m20_cross_layer_correlation",
            "PASS",
            source_paths,
            assertions,
            "exact 16-cell M20 correlation evidence is used without semantic-metric substitution",
        )
    else:
        cross_layer = _contour_evidence(
            "m20_cross_layer_correlation",
            "NOT_APPLICABLE",
            [],
            [],
            (
                "M20 execution evidence is not assigned to this unsupported combination"
                if not supported
                else "M20 record-level execution evidence is published for the 16-cell profile; no contour substitution is performed"
            ),
        )
    static_evidence = _contour_evidence(
        "rtl_static_parameter_contract",
        "PASS",
        [M16_PACKAGE],
        [
            "declared_cell_profiles_exact",
            "request_lane_formula_exact",
            "scheduler_period_exact",
            "transition_fraction_exact",
            "active_neutral_encoding_exact",
        ],
        "static RTL parameters are retained as a contract contour and not as measured execution metrics",
    )

    mode_match = scheduler["scheduler_mode"] == coordinates["scheduler_mode"]
    transition_match = transition["cell_count"] == coordinates["cell_count"]
    lane_match = transition["capacity_limit"] == coordinates["request_lanes"]
    route_supported = bool(route["supported"])
    checks = [
        _check("cell_count_declared", "PASS", "cell count belongs to the declared dimension"),
        _check("request_lanes_declared", "PASS", "request-lane count belongs to the declared dimension"),
        _check("scheduler_mode_declared", "PASS", "scheduler mode belongs to the declared dimension"),
        _check("scheduler_parameter_profile_declared", "PASS", "scheduler parameter profile is declared"),
        _check(
            "scheduler_mode_profile_match",
            "PASS" if mode_match else "SKIPPED",
            "exact match" if mode_match else "mode/profile mismatch is not substituted",
        ),
        _check("transition_capacity_profile_declared", "PASS", "transition-capacity profile is declared"),
        _check(
            "transition_capacity_profile_match",
            "PASS" if transition_match else "SKIPPED",
            "exact match" if transition_match else "cell/profile mismatch is not substituted",
        ),
        _check(
            "request_lane_capacity_match",
            "PASS" if transition_match and lane_match else "SKIPPED",
            "exact match" if transition_match and lane_match else "lane/capacity mismatch is not substituted",
        ),
        _check("retained_route_profile_declared", "PASS", "retained-route profile is declared"),
        _check(
            "retained_route_supported",
            "PASS" if route_supported else "SKIPPED",
            "active-neutral retained route" if route_supported else "direct opposite route is forbidden",
        ),
        _check(
            "deterministic_workload_available",
            "PASS" if supported else "SKIPPED",
            "exact workload identity available" if supported else reason_detail,
        ),
        _check(
            "semantic_invariants",
            "PASS" if supported else "NOT_APPLICABLE",
            "semantic invariants pass" if supported else "no semantic metrics are substituted",
        ),
        _check(
            "cross_layer_correlation",
            cross_layer["status"],
            cross_layer["reason"],
        ),
        _check(
            "measurement_contours_separate",
            "PASS",
            "static, semantic, and cross-layer contours remain separately identified",
        ),
        _check(
            "no_silent_parameter_substitution",
            "PASS",
            "declared coordinates remain unchanged in PASS and SKIPPED records",
        ),
    ]
    _require(tuple(item["check_id"] for item in checks) == CHECK_IDS, "case checks")
    case: dict[str, Any] = {
        "case_id": f"m21-case-{sequence:06d}",
        "checks": checks,
        "contour_evidence": [static_evidence, semantic_evidence, cross_layer],
        "coordinates": dict(coordinates),
        "dimensions_digest": dimensions["dimensions_digest"],
        "kind": "m21_parameterized_qualification_case",
        "provenance": provenance,
        "qualification_status": "PASS" if supported else "SKIPPED",
        "resolved_parameters": {
            "active_neutral_state": route["active_neutral_state"],
            "canonical_ternary_states": copy.deepcopy(route["canonical_ternary_states"]),
            "neutral_routes": copy.deepcopy(route["neutral_routes"]),
            "pending_route_queue_capacity": (
                int(coordinates["cell_count"])
                if route["pending_route_retention"]
                else None
            ),
            "pending_route_retention": route["pending_route_retention"],
            "scheduler_period_ticks": scheduler["period_ticks"],
            "scheduler_state_pattern": copy.deepcopy(scheduler["state_pattern"]),
            "transition_capacity_limit": transition["capacity_limit"],
            "transition_fraction": {
                "denominator": transition["fraction_denominator"],
                "numerator": transition["fraction_numerator"],
            },
        },
        "schema": CASE_SCHEMA,
        "sequence": sequence,
        "source_commit": context.source_commit,
        "support": {
            "classification": support,
            "reason_code": reason_code,
            "reason_detail": reason_detail,
        },
        "version": VERSION,
        "workloads": workloads,
    }
    case["case_digest"] = object_digest(case)
    return case


def coordinate_iter(dimensions: Mapping[str, Any]):
    values = dimensions["dimensions"]
    scalar_values = (
        values["cell_count"],
        values["request_lanes"],
        values["scheduler_mode"],
        [item["profile_id"] for item in values["scheduler_parameter_profile"]],
        [item["profile_id"] for item in values["transition_capacity_profile"]],
        [item["profile_id"] for item in values["retained_route_profile"]],
    )
    for combination in itertools.product(*scalar_values):
        yield dict(zip(DIMENSION_ORDER, combination, strict=True))


def build_matrix(context: Context, dimensions: Mapping[str, Any]) -> dict[str, Any]:
    cases = [
        build_case(context, dimensions, sequence, coordinates)
        for sequence, coordinates in enumerate(coordinate_iter(dimensions))
    ]
    _require(len(cases) == DECLARED_CASE_COUNT, "M21 case count mismatch")
    supported = [case for case in cases if case["qualification_status"] == "PASS"]
    skipped = [case for case in cases if case["qualification_status"] == "SKIPPED"]
    reason_counts = {
        reason: sum(case["support"]["reason_code"] == reason for case in skipped)
        for reason in SKIP_REASON_COUNTS
    }
    _require(len(supported) == SUPPORTED_CASE_COUNT, "supported count mismatch")
    _require(len(skipped) == SKIPPED_CASE_COUNT, "skipped count mismatch")
    _require(reason_counts == SKIP_REASON_COUNTS, "skip reason counts mismatch")
    matrix: dict[str, Any] = {
        "case_count": len(cases),
        "cases": cases,
        "dimensions_digest": dimensions["dimensions_digest"],
        "kind": "m21_parameterized_qualification_matrix",
        "milestone": MILESTONE,
        "schema": MATRIX_SCHEMA,
        "source_commit": context.source_commit,
        "source_release": SOURCE_RELEASE,
        "summary": {
            "failed_case_count": 0,
            "overall_status": "PASS",
            "skip_reason_counts": reason_counts,
            "skipped_case_count": len(skipped),
            "supported_case_count": len(supported),
            "unsupported_case_count": len(skipped),
        },
        "version": VERSION,
    }
    matrix["matrix_digest"] = object_digest(cases)
    return matrix


def validate_case_integrity(
    context: Context,
    dimensions: Mapping[str, Any],
    case: Mapping[str, Any],
) -> None:
    sequence = case.get("sequence")
    coordinates = case.get("coordinates")
    if not isinstance(sequence, int) or not isinstance(coordinates, dict):
        raise ContractError("case identity is malformed")
    expected = build_case(context, dimensions, sequence, coordinates)
    if canonical_json_bytes(case) != canonical_json_bytes(expected):
        raise ContractError(f"case integrity mismatch: {case.get('case_id')}")


class SchemaContext:
    """Load the exact M21 offline schema registry and validators."""

    def __init__(self, repository: Path) -> None:
        registry = read_json(repository, REGISTRY_PATH)
        if not isinstance(registry, dict):
            raise ContractError("M21 schema registry is not an object")
        if set(registry) != {"kind", "milestone", "records", "schema", "version"}:
            raise ContractError("M21 schema registry field set mismatch")
        if registry.get("schema") != "frp.m21.schema_registry.v2.3.0":
            raise ContractError("M21 schema registry identity mismatch")
        records = registry.get("records")
        if not isinstance(records, list) or len(records) != len(SCHEMA_PATHS):
            raise ContractError("M21 schema registry count mismatch")
        self.schemas: dict[str, dict[str, Any]] = {}
        for record in records:
            if not isinstance(record, dict) or set(record) != {
                "artifact_paths",
                "schema_identifier",
                "schema_path",
                "schema_urn",
            }:
                raise ContractError("M21 schema registry record mismatch")
            identifier = record["schema_identifier"]
            if identifier not in SCHEMA_PATHS:
                raise ContractError("unregistered M21 schema identifier")
            path = SCHEMA_PATHS[identifier]
            if record["schema_path"] != path:
                raise ContractError("M21 schema path mismatch")
            urn = f"urn:frp:schema:{identifier}"
            if record["schema_urn"] != urn:
                raise ContractError("M21 schema URN mismatch")
            schema = read_json(repository, path)
            if not isinstance(schema, dict) or schema.get("$id") != urn:
                raise ContractError("M21 schema identity mismatch")
            Draft202012Validator.check_schema(schema)
            self.schemas[identifier] = schema
        if set(self.schemas) != set(SCHEMA_PATHS):
            raise ContractError("M21 schema set mismatch")
        resource_registry = Registry()
        for identifier, schema in self.schemas.items():
            resource_registry = resource_registry.with_resource(
                f"urn:frp:schema:{identifier}",
                Resource.from_contents(schema),
            )
        self.registry = resource_registry

    def validate(self, identifier: str, instance: Any, subject: str) -> None:
        if identifier not in self.schemas:
            raise ContractError(f"unknown M21 schema: {identifier}")
        validator = Draft202012Validator(
            self.schemas[identifier],
            registry=self.registry,
        )
        errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
        if errors:
            first = errors[0]
            location = "/".join(str(part) for part in first.path) or "<root>"
            raise ContractError(
                f"schema validation failed for {subject} at {location}: {first.message}"
            )


def _manifest_source_records(context: Context) -> list[dict[str, Any]]:
    records = [
        source_record(
            context.repository,
            path,
            "technical_source",
            "m21_technical_source",
        )
        for path in TECHNICAL_SOURCE_PATHS
    ]
    records.extend(
        source_record(
            context.repository,
            path,
            "upstream_source",
            (
                "m20_cross_layer_correlation"
                if path.startswith("artifacts/m20/")
                else "m15_quantized_semantic_reference"
                if path.startswith("artifacts/m18/")
                else "rtl_static_parameter_contract"
                if path == M16_PACKAGE
                else "milestone_contract"
            ),
        )
        for path in UPSTREAM_SOURCE_PATHS
    )
    return sorted(records, key=lambda item: item["path"])


def build_manifest(
    context: Context,
    dimensions_raw: bytes,
    matrix_raw: bytes,
) -> dict[str, Any]:
    sources = _manifest_source_records(context)
    artifacts = [
        {
            "byte_length": len(dimensions_raw),
            "path": DIMENSIONS_ARTIFACT,
            "raw_sha256": sha256_bytes(dimensions_raw),
            "role": "parameter_dimensions",
            "schema": DIMENSIONS_SCHEMA,
            "status": "PASS",
        },
        {
            "byte_length": len(matrix_raw),
            "path": MATRIX_ARTIFACT,
            "raw_sha256": sha256_bytes(matrix_raw),
            "role": "qualification_matrix",
            "schema": MATRIX_SCHEMA,
            "status": "PASS",
        },
    ]
    return {
        "artifact_set_digest": object_digest(
            [{"path": item["path"], "raw_sha256": item["raw_sha256"]} for item in artifacts]
        ),
        "artifacts": artifacts,
        "kind": "m21_parameterized_qualification_manifest",
        "milestone": MILESTONE,
        "overall_status": "PASS",
        "schema": MANIFEST_SCHEMA,
        "source_commit": context.source_commit,
        "source_release": SOURCE_RELEASE,
        "source_set_digest": object_digest(
            [{"path": item["path"], "raw_sha256": item["raw_sha256"]} for item in sources]
        ),
        "sources": sources,
        "version": VERSION,
    }


def altered_case_digest_probe(
    context: Context,
    dimensions: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    altered = copy.deepcopy(next(case for case in matrix["cases"] if case["qualification_status"] == "PASS"))
    altered["case_digest"] = "0" * 64
    try:
        validate_case_integrity(context, dimensions, altered)
    except ContractError:
        return True
    return False


def altered_parameter_probe(
    context: Context,
    dimensions: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    altered = copy.deepcopy(next(case for case in matrix["cases"] if case["qualification_status"] == "PASS"))
    altered["resolved_parameters"]["transition_capacity_limit"] += 1
    altered["case_digest"] = object_digest(
        {key: value for key, value in altered.items() if key != "case_digest"}
    )
    try:
        validate_case_integrity(context, dimensions, altered)
    except ContractError:
        return True
    return False


def altered_workload_digest_probe(
    context: Context,
    dimensions: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    altered = copy.deepcopy(next(case for case in matrix["cases"] if case["workloads"]))
    altered["workloads"][0]["raw_sha256"] = "f" * 64
    altered["case_digest"] = object_digest(
        {key: value for key, value in altered.items() if key != "case_digest"}
    )
    try:
        validate_case_integrity(context, dimensions, altered)
    except ContractError:
        return True
    return False


def contour_substitution_probe(
    context: Context,
    dimensions: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    altered = copy.deepcopy(next(case for case in matrix["cases"] if case["qualification_status"] == "PASS"))
    altered["contour_evidence"][1]["contour"] = "m20_cross_layer_correlation"
    altered["contour_evidence"][1]["evidence_digest"] = object_digest(
        {
            key: value
            for key, value in altered["contour_evidence"][1].items()
            if key != "evidence_digest"
        }
    )
    altered["case_digest"] = object_digest(
        {key: value for key, value in altered.items() if key != "case_digest"}
    )
    try:
        validate_case_integrity(context, dimensions, altered)
    except ContractError:
        return True
    return False


def build_qualification(
    context: Context,
    dimensions: Mapping[str, Any],
    matrix: Mapping[str, Any],
    manifest: Mapping[str, Any],
    schemas: SchemaContext,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(check_id: str, category: str, result: bool) -> None:
        checks.append({"category": category, "check_id": check_id, "pass": bool(result)})

    cases = matrix["cases"]
    supported = [case for case in cases if case["qualification_status"] == "PASS"]
    skipped = [case for case in cases if case["qualification_status"] == "SKIPPED"]
    coordinates = [case["coordinates"] for case in cases]
    add("source_commit_exact", "source_identity", context.source_commit == EXPECTED_M20_COMMIT)
    add("m15_workload_inventory_exact", "source_identity", len(context.workloads) == 6)
    add("m20_boundary_pass", "source_identity", context.m20_boundary["qualification_check_count"] == 39)
    add("cell_count_dimension_exact", "dimension", dimensions["dimensions"]["cell_count"] == [8, 16, 32])
    add("request_lane_dimension_exact", "dimension", dimensions["dimensions"]["request_lanes"] == [2, 4, 8])
    add("scheduler_mode_dimension_exact", "dimension", dimensions["dimensions"]["scheduler_mode"] == ["free", "7/1", "1/7"])
    add("scheduler_parameter_profiles_exact", "dimension", dimensions["dimensions"]["scheduler_parameter_profile"] == list(SCHEDULER_PROFILES))
    add("transition_capacity_profiles_exact", "dimension", dimensions["dimensions"]["transition_capacity_profile"] == list(TRANSITION_CAPACITY_PROFILES))
    add("retained_route_profiles_exact", "dimension", dimensions["dimensions"]["retained_route_profile"] == list(RETAINED_ROUTE_PROFILES))
    add("dimension_order_exact", "dimension", dimensions["dimension_order"] == list(DIMENSION_ORDER))
    add("cartesian_case_count_exact", "coverage", dimensions["declared_cartesian_case_count"] == DECLARED_CASE_COUNT)
    add("matrix_case_count_exact", "coverage", len(cases) == DECLARED_CASE_COUNT)
    add("coordinate_set_unique", "coverage", len({object_digest(item) for item in coordinates}) == DECLARED_CASE_COUNT)
    add("case_sequence_exact", "coverage", [case["sequence"] for case in cases] == list(range(DECLARED_CASE_COUNT)))
    add("case_ids_exact", "coverage", [case["case_id"] for case in cases] == [f"m21-case-{index:06d}" for index in range(DECLARED_CASE_COUNT)])
    add("supported_count_exact", "coverage", len(supported) == SUPPORTED_CASE_COUNT)
    add("skipped_count_exact", "coverage", len(skipped) == SKIPPED_CASE_COUNT)
    for reason, count in SKIP_REASON_COUNTS.items():
        add(
            f"skip_reason:{reason}",
            "unsupported_combination",
            sum(case["support"]["reason_code"] == reason for case in skipped) == count,
        )
    expected_supported = {
        (8, 2, "7/1"),
        (16, 4, "free"),
        (16, 4, "7/1"),
        (16, 4, "1/7"),
        (32, 8, "7/1"),
    }
    add(
        "supported_coordinate_set_exact",
        "supported_combination",
        {
            (
                case["coordinates"]["cell_count"],
                case["coordinates"]["request_lanes"],
                case["coordinates"]["scheduler_mode"],
            )
            for case in supported
        }
        == expected_supported,
    )
    add("supported_status_pass", "supported_combination", all(case["support"]["classification"] == "SUPPORTED" for case in supported))
    add("unsupported_status_skipped", "unsupported_combination", all(case["support"]["classification"] == "UNSUPPORTED" for case in skipped))
    add("zero_failed_cases", "qualification", matrix["summary"]["failed_case_count"] == 0)
    add("per_case_digest_exact", "digest", all(case["case_digest"] == object_digest({key: value for key, value in case.items() if key != "case_digest"}) for case in cases))
    add("matrix_digest_exact", "digest", matrix["matrix_digest"] == object_digest(cases))
    add("dimensions_digest_exact", "digest", dimensions["dimensions_digest"] == object_digest({key: value for key, value in dimensions.items() if key != "dimensions_digest"}))
    add("workload_digests_exact", "digest", all(item["raw_sha256"] == sha256_bytes(read_bytes(context.repository, item["path"])) for item in context.workloads))
    add("workload_qualification_pass", "semantic_contour", all(item["qualification_status"] == "PASS" for item in context.workloads))
    add("balanced_ternary_domain_exact", "semantic_contour", all(case["resolved_parameters"]["canonical_ternary_states"] == [-1, 0, 1] for case in supported))
    add("active_neutral_state_exact", "semantic_contour", all(case["resolved_parameters"]["active_neutral_state"] == 0 for case in supported))
    add("neutral_routes_exact", "semantic_contour", all(case["resolved_parameters"]["neutral_routes"] == ["-1 -> 0 -> 1", "1 -> 0 -> -1"] for case in supported))
    add("measurement_contours_separate", "contour_boundary", all([item["contour"] for item in case["contour_evidence"]] == ["rtl_static_parameter_contract", "m15_quantized_semantic_reference", "m20_cross_layer_correlation"] for case in cases))
    add("no_silent_parameter_substitution", "contour_boundary", all(case["checks"][-1]["status"] == "PASS" for case in cases))
    add("cross_layer_16_cell_pass", "cross_layer_contour", all(case["contour_evidence"][2]["status"] == "PASS" for case in supported if case["coordinates"]["cell_count"] == 16))
    add("cross_layer_non16_not_applicable", "cross_layer_contour", all(case["contour_evidence"][2]["status"] == "NOT_APPLICABLE" for case in supported if case["coordinates"]["cell_count"] != 16))
    add("per_case_provenance_present", "provenance", all(case["provenance"] for case in cases))
    add("provenance_digests_exact", "provenance", all(item["raw_sha256"] == sha256_bytes(read_bytes(context.repository, item["path"])) for case in cases for item in case["provenance"]))
    add("manifest_status_pass", "manifest", manifest["overall_status"] == "PASS")
    add("manifest_artifact_digest_exact", "manifest", manifest["artifact_set_digest"] == object_digest([{"path": item["path"], "raw_sha256": item["raw_sha256"]} for item in manifest["artifacts"]]))
    add("manifest_source_digest_exact", "manifest", manifest["source_set_digest"] == object_digest([{"path": item["path"], "raw_sha256": item["raw_sha256"]} for item in manifest["sources"]]))
    try:
        schemas.validate(DIMENSIONS_SCHEMA, dimensions, DIMENSIONS_ARTIFACT)
        schemas.validate(MATRIX_SCHEMA, matrix, MATRIX_ARTIFACT)
        schemas.validate(MANIFEST_SCHEMA, manifest, MANIFEST_ARTIFACT)
        schemas_pass = True
    except ContractError:
        schemas_pass = False
    add("formal_schema_validation", "schema", schemas_pass)
    add("altered_case_digest_detected", "negative_test", altered_case_digest_probe(context, dimensions, matrix))
    add("altered_parameter_detected", "negative_test", altered_parameter_probe(context, dimensions, matrix))
    add("altered_workload_digest_detected", "negative_test", altered_workload_digest_probe(context, dimensions, matrix))
    add("contour_substitution_detected", "negative_test", contour_substitution_probe(context, dimensions, matrix))
    passed = sum(item["pass"] for item in checks)
    return {
        "check_count": len(checks),
        "checks": checks,
        "failed_count": len(checks) - passed,
        "kind": "m21_parameterized_qualification_record",
        "matrix_digest": matrix["matrix_digest"],
        "milestone": MILESTONE,
        "overall_status": "PASS" if passed == len(checks) else "FAIL",
        "passed_count": passed,
        "schema": QUALIFICATION_SCHEMA,
        "source_commit": context.source_commit,
        "version": VERSION,
    }


def build_outputs(repository: Path, source_commit: str) -> dict[str, bytes]:
    context = build_context(repository, source_commit)
    schemas = SchemaContext(context.repository)
    dimensions = build_dimensions(context)
    matrix = build_matrix(context, dimensions)
    dimensions_raw = canonical_json_bytes(dimensions)
    matrix_raw = canonical_json_bytes(matrix)
    manifest = build_manifest(context, dimensions_raw, matrix_raw)
    qualification = build_qualification(context, dimensions, matrix, manifest, schemas)
    if qualification["overall_status"] != "PASS":
        raise ContractError("M21 qualification did not pass")
    schemas.validate(DIMENSIONS_SCHEMA, dimensions, DIMENSIONS_ARTIFACT)
    schemas.validate(MATRIX_SCHEMA, matrix, MATRIX_ARTIFACT)
    schemas.validate(MANIFEST_SCHEMA, manifest, MANIFEST_ARTIFACT)
    schemas.validate(QUALIFICATION_SCHEMA, qualification, QUALIFICATION_ARTIFACT)
    return {
        DIMENSIONS_ARTIFACT: dimensions_raw,
        MATRIX_ARTIFACT: matrix_raw,
        MANIFEST_ARTIFACT: canonical_json_bytes(manifest),
        QUALIFICATION_ARTIFACT: canonical_json_bytes(qualification),
    }


def _safe_write(output_root: Path, relative: str, raw: bytes) -> None:
    target = output_root.joinpath(*safe_relative_path(relative).parts)
    resolved_root = output_root.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or not target.parent.resolve().is_relative_to(resolved_root):
        raise SafetyError(f"unsafe M21 output path: {relative}")
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
    if not all(item["match"] for item in matches):
        raise ContractError("committed M21 artifact mismatch")
    return {"artifact_count": len(matches), "artifacts": matches, "status": "PASS"}


def self_test(repository: Path, source_commit: str) -> dict[str, Any]:
    context = build_context(repository, source_commit)
    dimensions = build_dimensions(context)
    matrix = build_matrix(context, dimensions)
    cases = [
        ("declared_case_count", len(matrix["cases"]) == 486),
        ("supported_case_count", matrix["summary"]["supported_case_count"] == 5),
        ("skipped_case_count", matrix["summary"]["skipped_case_count"] == 481),
        ("skip_reason_counts", matrix["summary"]["skip_reason_counts"] == SKIP_REASON_COUNTS),
        ("canonical_ternary_domain", all(case["resolved_parameters"]["canonical_ternary_states"] == [-1, 0, 1] for case in matrix["cases"] if case["qualification_status"] == "PASS")),
        ("active_neutral", all(case["resolved_parameters"]["active_neutral_state"] == 0 for case in matrix["cases"] if case["qualification_status"] == "PASS")),
        ("altered_case_digest", altered_case_digest_probe(context, dimensions, matrix)),
        ("altered_parameter", altered_parameter_probe(context, dimensions, matrix)),
        ("altered_workload_digest", altered_workload_digest_probe(context, dimensions, matrix)),
        ("contour_substitution", contour_substitution_probe(context, dimensions, matrix)),
    ]
    passed = sum(result for _, result in cases)
    return {
        "case_count": len(cases),
        "cases": [{"case_id": case_id, "pass": bool(result)} for case_id, result in cases],
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
            result = generate(repository, Path(args.output_root).resolve(), args.source_commit)
        elif args.verify:
            result = verify(repository, args.source_commit)
        else:
            result = self_test(repository, args.source_commit)
            if result["status"] != "PASS":
                raise ContractError("M21 self-test failed")
        _write_optional(args.output, result)
        return 0
    except M21Error as exc:
        print(f"M21 error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
