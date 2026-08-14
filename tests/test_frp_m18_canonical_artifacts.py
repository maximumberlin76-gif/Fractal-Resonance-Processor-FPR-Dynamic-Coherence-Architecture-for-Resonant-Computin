# SPDX-License-Identifier: Apache-2.0
"""Independent qualification tests for FRP M18 canonical artifacts."""

from __future__ import annotations

import ast
import copy
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from unittest import mock

from jsonschema import Draft202012Validator


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCER_PATH = REPO_ROOT / "frp_m18_canonical_artifacts.py"
REGISTRY_PATH = "schemas/m18/frp_m18_schema_registry.json"
MANIFEST_PATH = "artifacts/m18/manifests/canonical-artifact-manifest.json"
QUALIFICATION_PATH = (
    "artifacts/m18/manifests/canonical-artifact-qualification.json"
)
SELF_TEST_PATH = "artifacts/m18/manifests/canonical-artifact-self-test.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import frp_m18_canonical_artifacts as producer


JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_URN_PREFIX = "urn:frp:schema:"
M18_MILESTONE = "M18 — Formal Schema and Canonical Artifact Publication"
M15_MILESTONE = (
    "M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package"
)
M18_VERSION = "2.0.0"
M15_VERSION = "1.7.0"
SEMANTIC_REFERENCE = "frp_prototype_v1_7_0.py"
M18_PRODUCER = "frp_m18_canonical_artifacts.py"
CANONICAL_STATES = (-1, 0, 1)
STATE_CODES = {-1: ("11", 3), 0: ("00", 0), 1: ("01", 1)}
RESERVED_STATE_CODE = ("10", 2)
SCHEDULER_MODES = ("free", "7/1", "1/7")
OBSERVATORY_MODES = (
    "artifact_auditor",
    "ternary_transition_visualizer",
    "trace_explorer",
)

EXPECTED_SCHEMA_IDENTIFIERS = (
    "frp.benchmark.architecture_comparison.v1",
    "frp.benchmark.hardware_sensitivity_comparison.v1",
    "frp.benchmark.hardware_sensitivity_cost_profile.v1",
    "frp.benchmark.normalized_cost_profile.v1",
    "frp.benchmark.thermal_proxy_profile.v1",
    "frp.benchmark.workload_profile.v1",
    "frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0",
    "frp.m15.cycle_exact_reference_trace.v1.7.0",
    "frp.m15.fixed_point_interface_profile.v1.7.0",
    "frp.m15.qualification_closure_manifest.v1.7.0",
    "frp.m15.quantized_reference_shadow_model.v1.7.0",
    "frp.m15.reference_preload.v1.7.0",
    "frp.m15.reference_rtl_equivalence_report.v1.7.0",
    "frp.m15.rtl_assertion_correlation_harness.v1.7.0",
    "frp.m15.rtl_comparison_vector_package.v1.7.0",
    "frp.m15.sha256_manifest.v1.7.0",
    "frp.m15.synthesizable_rtl_reference_core.v1.7.0",
    "frp.m15.systemverilog_testbench_interface_map.v1.7.0",
    "frp.m18.canonical_artifact_manifest.v2.0.0",
    "frp.m18.canonical_artifact_qualification.v2.0.0",
    "frp.m18.canonical_artifact_self_test.v2.0.0",
    "frp.m18.formal_schema_registry.v2.0.0",
    "frp.m3.benchmark_matrix.v1.7.0",
    "frp.structured_output.v1.7.0",
)

EXPECTED_SCHEMA_PATHS = tuple(
    f"schemas/m18/{identifier}.schema.json"
    for identifier in EXPECTED_SCHEMA_IDENTIFIERS
)

STRUCTURED_SPECS = {
    "artifacts/m18/structured_output/scaling-16.json": (
        "demo",
        "7/1",
        16,
        16,
        False,
    ),
    "artifacts/m18/structured_output/scaling-32.json": (
        "demo",
        "7/1",
        32,
        16,
        False,
    ),
    "artifacts/m18/structured_output/scaling-8.json": (
        "demo",
        "7/1",
        8,
        16,
        False,
    ),
    "artifacts/m18/structured_output/self-test-1-7.json": (
        "self-test",
        "1/7",
        16,
        64,
        False,
    ),
    "artifacts/m18/structured_output/self-test-7-1.json": (
        "self-test",
        "7/1",
        16,
        64,
        False,
    ),
    "artifacts/m18/structured_output/self-test-default.json": (
        "self-test",
        "7/1",
        16,
        64,
        False,
    ),
    "artifacts/m18/structured_output/self-test-free.json": (
        "self-test",
        "free",
        16,
        64,
        False,
    ),
    "artifacts/m18/structured_output/structured-output.json": (
        "demo",
        "7/1",
        16,
        64,
        False,
    ),
    "artifacts/m18/structured_output/trace-1-7.json": (
        "demo",
        "1/7",
        16,
        64,
        True,
    ),
    "artifacts/m18/structured_output/trace-7-1.json": (
        "demo",
        "7/1",
        16,
        64,
        True,
    ),
    "artifacts/m18/structured_output/trace-free.json": (
        "demo",
        "free",
        16,
        64,
        True,
    ),
}

BENCHMARK_JSON_PATH = "artifacts/m18/benchmark_matrix/benchmark-matrix.json"
BENCHMARK_CSV_PATH = "artifacts/m18/tabular/benchmark-matrix.csv"
BENCHMARK_PATHS = (BENCHMARK_JSON_PATH, BENCHMARK_CSV_PATH)
BENCHMARK_COLUMNS = (
    "architecture",
    "numeric_domain",
    "interaction_scaling",
    "cycle_exact_integer_trace",
    "hardware_facing_encoding",
    "C_minus_P_sign_match",
    "scheduler_sequence_match",
    "state_sequence_match",
    "vector_repeat_match",
    "comparison_rule",
    "artifact_layers",
)
BENCHMARK_ARCHITECTURES = (
    "frp_v1_6_0_m14_floating_semantic_reference",
    "frp_v1_7_0_quantized_hardware_shadow",
    "frp_v1_7_0_cycle_exact_vector_package",
    "frp_v1_7_0_systemverilog_correlation_contract",
    "frp_v1_7_0_qualification_closure",
)

M15_EXPORT_SPECS = {
    "artifacts/m18/m15_exports/balanced-ternary-hardware-encoding-map.json": (
        "frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0",
        "balanced_ternary_hardware_encoding_map",
        "--export-balanced-ternary-hardware-encoding-map",
    ),
    "artifacts/m18/m15_exports/cycle-exact-reference-trace.json": (
        "frp.m15.cycle_exact_reference_trace.v1.7.0",
        "cycle_exact_reference_trace",
        "--export-cycle-exact-reference-trace",
    ),
    "artifacts/m18/m15_exports/fixed-point-interface-profile.json": (
        "frp.m15.fixed_point_interface_profile.v1.7.0",
        "fixed_point_interface_profile",
        "--export-fixed-point-interface-profile",
    ),
    "artifacts/m18/m15_exports/qualification-closure-manifest.json": (
        "frp.m15.qualification_closure_manifest.v1.7.0",
        "qualification_closure_manifest",
        "--export-qualification-closure-manifest",
    ),
    "artifacts/m18/m15_exports/quantized-reference-shadow-model.json": (
        "frp.m15.quantized_reference_shadow_model.v1.7.0",
        "quantized_reference_shadow_model",
        "--export-quantized-reference-shadow-model",
    ),
    "artifacts/m18/m15_exports/reference-rtl-equivalence-report.json": (
        "frp.m15.reference_rtl_equivalence_report.v1.7.0",
        "reference_rtl_equivalence_report",
        "--export-reference-rtl-equivalence-report",
    ),
    "artifacts/m18/m15_exports/rtl-assertion-correlation-harness.json": (
        "frp.m15.rtl_assertion_correlation_harness.v1.7.0",
        "rtl_assertion_correlation_harness",
        "--export-rtl-assertion-correlation-harness",
    ),
    "artifacts/m18/m15_exports/rtl-comparison-vector-package.json": (
        "frp.m15.rtl_comparison_vector_package.v1.7.0",
        "rtl_comparison_vector_package",
        "--export-rtl-comparison-vector-package",
    ),
    "artifacts/m18/m15_exports/synthesizable-rtl-reference-core.json": (
        "frp.m15.synthesizable_rtl_reference_core.v1.7.0",
        "synthesizable_rtl_reference_core",
        "--export-synthesizable-rtl-reference-core",
    ),
    "artifacts/m18/m15_exports/systemverilog-testbench-interface-map.json": (
        "frp.m15.systemverilog_testbench_interface_map.v1.7.0",
        "systemverilog_testbench_interface_map",
        "--export-systemverilog-testbench-interface-map",
    ),
}

VECTOR_MEMBER_NAMES = (
    "frp_m15_cell_trace.vec",
    "frp_m15_full_correlation_vectors.vec",
    "frp_m15_kernel_vectors.vec",
    "frp_m15_pending_routes.trace",
    "frp_m15_reference_preload.json",
    "frp_m15_scheduler_1_7_vectors.vec",
    "frp_m15_scheduler_7_1_vectors.vec",
    "frp_m15_scheduler_free_vectors.vec",
    "frp_m15_sha256_manifest.json",
    "frp_m15_trig_lut_q30.vec",
)
VECTOR_DIRECTORY = "artifacts/m18/m15_vectors"
VECTOR_PATHS = tuple(f"{VECTOR_DIRECTORY}/{name}" for name in VECTOR_MEMBER_NAMES)
HEADERED_VECTOR_SPECS = {
    "frp_m15_cell_trace.vec": ("cell_trace", "7/1"),
    "frp_m15_full_correlation_vectors.vec": (
        "full_correlation_vectors",
        "7/1",
    ),
    "frp_m15_kernel_vectors.vec": ("kernel_transition_vectors", "free"),
    "frp_m15_pending_routes.trace": ("pending_routes", "free"),
    "frp_m15_scheduler_1_7_vectors.vec": ("scheduler_1_7_vectors", "1/7"),
    "frp_m15_scheduler_7_1_vectors.vec": ("scheduler_7_1_vectors", "7/1"),
    "frp_m15_scheduler_free_vectors.vec": ("scheduler_free_vectors", "free"),
}
VECTOR_PACKAGE_DIGEST = (
    "703dd4b56f4b34289a2c5bc5521ad4ddc3113bdec8c38238c3244c69cb4d58df"
)

COMPARATIVE_SPECS = {
    "benchmarks/architecture_comparison/profiles/"
    "hardware_sensitivity_cost_profile_v1.json": (
        "frp.benchmark.hardware_sensitivity_cost_profile.v1",
        "embedded_schema",
        None,
        "hardware_informed_sensitivity_qualification",
    ),
    "benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json": (
        "frp.benchmark.normalized_cost_profile.v1",
        "embedded_schema",
        None,
        "comparative_architecture_benchmark_suite",
    ),
    "benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json": (
        "frp.benchmark.thermal_proxy_profile.v1",
        "embedded_schema",
        None,
        "comparative_architecture_benchmark_suite",
    ),
    "benchmarks/architecture_comparison/profiles/workload_profile_v1.json": (
        "frp.benchmark.workload_profile.v1",
        "registry_bound_exact_path_and_role",
        None,
        "comparative_architecture_benchmark_suite",
    ),
    "benchmarks/architecture_comparison/results/reference_comparison_seed_76.json": (
        "frp.benchmark.architecture_comparison.v1",
        "embedded_schema",
        "benchmarks/architecture_comparison/run_architecture_comparison.py",
        "comparative_architecture_benchmark_suite",
    ),
    "benchmarks/architecture_comparison/results/"
    "reference_comparison_seed_76_hardware_sensitivity_v1.json": (
        "frp.benchmark.hardware_sensitivity_comparison.v1",
        "embedded_schema",
        "benchmarks/architecture_comparison/"
        "run_hardware_sensitivity_comparison.py",
        "hardware_informed_sensitivity_qualification",
    ),
}

GENERATED_CORE_PATHS = tuple(
    sorted(
        set(STRUCTURED_SPECS)
        | set(BENCHMARK_PATHS)
        | set(M15_EXPORT_SPECS)
        | set(VECTOR_PATHS)
    )
)
GENERATED_PATHS = tuple(
    sorted(
        set(GENERATED_CORE_PATHS)
        | {MANIFEST_PATH, QUALIFICATION_PATH, SELF_TEST_PATH}
    )
)
MANIFEST_BOUND_PATHS = tuple(
    sorted(
        set(GENERATED_CORE_PATHS)
        | set(COMPARATIVE_SPECS)
        | set(EXPECTED_SCHEMA_PATHS)
        | {REGISTRY_PATH}
    )
)

SELF_TEST_CASE_IDS = (
    "artifact_set_digest_known_vector",
    "canonical_json_serialization_stable",
    "canonical_ternary_domain_accept",
    "canonical_ternary_domain_reject",
    "deterministic_regeneration_byte_identical",
    "embedded_schema_identity_accept",
    "environment_dependent_field_reject",
    "formal_schema_id_match_accept",
    "formal_schema_id_mismatch_reject",
    "internal_manifest_digest_mismatch_reject",
    "manifest_aggregate_status_accept",
    "manifest_aggregate_status_reject",
    "manifest_order_accept",
    "manifest_order_reject",
    "manifest_self_binding_reject",
    "opposite_transition_direct_reject",
    "opposite_transition_via_zero_accept",
    "path_absolute_reject",
    "path_duplicate_reject",
    "path_parent_component_reject",
    "path_relative_accept",
    "path_symlink_reject",
    "preload_packed_state_mapping_accept",
    "raw_byte_sha256_known_vector",
    "registry_bound_identity_accept",
    "registry_duplicate_identifier_reject",
    "registry_exact_identifier_set_accept",
    "registry_unknown_identifier_reject",
    "scheduler_1_7_sequence_accept",
    "scheduler_7_1_sequence_accept",
    "scheduler_free_sequence_accept",
    "source_mutation_detected",
    "state_notation_plus_prefix_reject",
    "vector_package_member_set_accept",
)

QUALIFICATION_CATEGORIES = (
    "determinism",
    "digest",
    "formal_schema",
    "identity",
    "immutability",
    "manifest",
    "measurement_contour",
    "publication_boundary",
    "registry",
    "structure",
    "ternary_domain",
)
QUALIFICATION_CHECK_IDS = (
    "canonical_artifact_relations_valid",
    "canonical_processor_domain_preserved",
    "draft_2020_12_schema_valid",
    "exact_supported_schema_set",
    "formal_schema_identity_exact",
    "generated_path_set_exact",
    "independent_regeneration_byte_identical",
    "m16_and_physical_claim_boundary_preserved",
    "manifest_artifact_set_digest_valid",
    "manifest_regeneration_byte_identical",
    "measurement_contours_remain_separate",
    "publication_matches_regeneration",
    "registry_content_digest_valid",
    "source_bytes_unchanged",
)
MEASUREMENT_CONTOURS = (
    "comparative_architecture_benchmark_suite",
    "hardware_informed_sensitivity_qualification",
    "m15_implementation_mapping_matrix",
    "m18_canonical_artifact_publication",
)

REGISTRY_ROOT_FIELDS = {
    "json_schema_dialect",
    "kind",
    "milestone",
    "record_order",
    "records",
    "registry_content_sha256",
    "registry_digest_scope",
    "schema",
    "schema_count",
    "version",
}
REGISTRY_RECORD_FIELDS = {
    "artifact_format",
    "artifact_role",
    "canonical_artifact_paths",
    "identity_basis",
    "identity_class",
    "measurement_contour",
    "producer_path",
    "producer_version",
    "required",
    "schema_identifier",
    "schema_path",
    "schema_urn",
    "schema_version",
    "supported",
    "upstream_milestone",
    "upstream_release",
    "validation_mode",
}

MANIFEST_ROOT_FIELDS = {
    "artifact_count",
    "artifact_order",
    "artifact_set_sha256",
    "artifacts",
    "digest_algorithm",
    "digest_scope",
    "kind",
    "milestone",
    "producer",
    "producer_version",
    "schema",
    "upstream_release",
    "version",
}

SELF_TEST_ROOT_FIELDS = {
    "case_count",
    "case_order",
    "cases",
    "failed_count",
    "kind",
    "milestone",
    "overall_status",
    "passed_count",
    "producer",
    "producer_version",
    "profile",
    "schema",
    "upstream_release",
    "version",
}


def sha256_bytes(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite number: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def strict_json_bytes(raw_bytes: bytes, root_type: type = dict) -> Any:
    value = json.loads(
        raw_bytes.decode("utf-8"),
        object_pairs_hook=_unique_object,
        parse_constant=_reject_nonfinite,
    )
    if not isinstance(value, root_type):
        raise ValueError("unexpected JSON root type")
    return value


def repository_file(relative_path: str) -> Path:
    return REPO_ROOT.joinpath(*PurePosixPath(relative_path).parts)


def independent_safe_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if "\\" in value or "\x00" in value or value.endswith("/"):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(
        part not in {"", ".", ".."} for part in path.parts
    )


def observatory_modes_valid(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) for item in value)
        and tuple(value) == tuple(sorted(set(value)))
        and set(value).issubset(OBSERVATORY_MODES)
    )


def snapshot(paths: Sequence[str]) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for relative_path in paths:
        raw_bytes = repository_file(relative_path).read_bytes()
        result[relative_path] = (len(raw_bytes), sha256_bytes(raw_bytes))
    return result


def recursive_file_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


_CACHE_DIRECTORY = tempfile.TemporaryDirectory(prefix="frp-m18-test-cache-")
_CACHE_ROOT = Path(_CACHE_DIRECTORY.name)


def run_cli(
    *arguments: str,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = str(_CACHE_ROOT / "pycache")
    return subprocess.run(
        [sys.executable, str(PRODUCER_PATH), *arguments],
        cwd=REPO_ROOT if cwd is None else cwd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=environment,
    )


def scheduler_sequence(mode: str, length: int) -> tuple[str, ...]:
    if mode == "free":
        return ("free",) * length
    if mode == "7/1":
        return tuple(
            "commit" if index % 8 == 7 else "balance"
            for index in range(length)
        )
    if mode == "1/7":
        return tuple(
            "excite" if index % 8 == 0 else "neutralize"
            for index in range(length)
        )
    raise ValueError("unknown scheduler mode")


def state_vector_from_human(value: str) -> tuple[int, ...]:
    mapping = {"M": -1, "N": 0, "P": 1}
    return tuple(mapping[character] for character in value)


def packed_states_match(states: Sequence[Any], packed_hex: Any) -> bool:
    if not isinstance(packed_hex, str) or re.fullmatch(r"[0-9A-F]+", packed_hex) is None:
        return False
    if any(type(state) is not int or state not in CANONICAL_STATES for state in states):
        return False
    packed = int(packed_hex, 16)
    if packed >> (2 * len(states)):
        return False
    return all(
        ((packed >> (2 * index)) & 3) == STATE_CODES[state][1]
        for index, state in enumerate(states)
    )


def parse_vector_header(raw_bytes: bytes) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    for line in raw_bytes.decode("utf-8").splitlines():
        if not line.startswith("#"):
            break
        content = line[1:].strip()
        if "=" not in content:
            continue
        key, raw_value = content.split("=", 1)
        key = key.strip()
        if key in headers:
            raise ValueError("duplicate header")
        headers[key] = json.loads(raw_value)
    return headers


def expected_package_digest(member_bytes: Mapping[str, bytes]) -> str:
    material = b"".join(
        name.encode("utf-8") + b"\0" + member_bytes[name]
        for name in VECTOR_MEMBER_NAMES
    )
    return sha256_bytes(material)


def independent_vector_package_valid(core: Mapping[str, bytes]) -> bool:
    try:
        observed_paths = tuple(
            sorted(path for path in core if path.startswith(VECTOR_DIRECTORY + "/"))
        )
        if observed_paths != VECTOR_PATHS:
            return False
        members = {
            PurePosixPath(path).name: core[path]
            for path in observed_paths
        }
        if tuple(sorted(members)) != VECTOR_MEMBER_NAMES:
            return False

        for name, (trace_kind, scheduler) in HEADERED_VECTOR_SPECS.items():
            headers = parse_vector_header(members[name])
            expected = {
                "format_version": "frp.m15.vector.v1",
                "frp_version": "1.7.0",
                "milestone": M15_MILESTONE,
                "trace_kind": trace_kind,
                "cells": 16,
                "hierarchy_depth": 4,
                "request_lanes": 4,
                "transition_fraction": 0.25,
                "scheduler_mode": scheduler,
                "scalar_format": "S32Q16",
            }
            if any(headers.get(key) != value for key, value in expected.items()):
                return False

        preload = strict_json_bytes(members["frp_m15_reference_preload.json"])
        if set(preload) != {
            "cells",
            "frequency_current_q16",
            "frequency_target_q16",
            "gamma_noise_state_q16",
            "gamma_noise_target_q16",
            "heat_q16",
            "phase_words",
            "scheduler",
            "seed",
            "states",
            "states_packed_hex",
        }:
            return False
        if (
            preload["cells"] != 16
            or preload["seed"] != 76
            or preload["scheduler"] != "7/1"
            or not packed_states_match(preload["states"], preload["states_packed_hex"])
        ):
            return False
        for field in (
            "frequency_current_q16",
            "frequency_target_q16",
            "gamma_noise_state_q16",
            "gamma_noise_target_q16",
            "heat_q16",
            "phase_words",
            "states",
        ):
            if not isinstance(preload[field], list) or len(preload[field]) != 16:
                return False

        internal = strict_json_bytes(members["frp_m15_sha256_manifest.json"])
        expected_internal = {
            name: sha256_bytes(raw_bytes)
            for name, raw_bytes in sorted(members.items())
            if name != "frp_m15_sha256_manifest.json"
        }
        if internal != expected_internal:
            return False

        lookup_lines = members["frp_m15_trig_lut_q30.vec"].decode("utf-8").splitlines()
        if lookup_lines[:3] != [
            "# FRP v1.7.0 M15 deterministic trigonometric lookup table",
            "# entries=4096",
            "# format=index | sin_q30",
        ]:
            return False
        if len(lookup_lines[3:]) != 4096:
            return False
        for index, line in enumerate(lookup_lines[3:]):
            match = re.fullmatch(r"([0-9A-F]{4}) \| (-?[0-9]+)", line)
            if match is None or int(match.group(1), 16) != index:
                return False

        descriptor = strict_json_bytes(
            core[
                "artifacts/m18/m15_exports/rtl-comparison-vector-package.json"
            ]
        )
        expected_files = [
            {
                "name": name,
                "sha256": sha256_bytes(members[name]),
                "size_bytes": len(members[name]),
            }
            for name in VECTOR_MEMBER_NAMES
        ]
        package_digest = expected_package_digest(members)
        return (
            descriptor.get("manifest")
            == {"file_count": 10, "files": expected_files}
            and descriptor.get("deterministic_package_digest") == package_digest
            and package_digest == VECTOR_PACKAGE_DIGEST
        )
    except (KeyError, TypeError, UnicodeError, ValueError, json.JSONDecodeError):
        return False


def artifact_set_digest(records: Sequence[Mapping[str, Any]]) -> str:
    material = b"".join(
        record["repository_path"].encode("utf-8")
        + b"\0"
        + record["sha256"].encode("ascii")
        + b"\0"
        + str(record["byte_length"]).encode("ascii")
        + b"\n"
        for record in sorted(records, key=lambda item: item["repository_path"])
    )
    return sha256_bytes(material)


def environment_fields_absent(value: Any) -> bool:
    prohibited = {
        "timestamp",
        "generated_at",
        "hostname",
        "username",
        "pid",
        "process_id",
        "workflow_run_number",
        "environment",
    }
    if isinstance(value, dict):
        for key, child in value.items():
            if key in prohibited:
                return False
            if "path" in key and isinstance(child, str) and Path(child).is_absolute():
                return False
            if not environment_fields_absent(child):
                return False
    elif isinstance(value, list):
        return all(environment_fields_absent(child) for child in value)
    return True


def aggregate_valid(
    checks: Sequence[Mapping[str, Any]],
    aggregate: Mapping[str, Any],
) -> bool:
    expected = {
        "check_count": len(checks),
        "passed_count": sum(check.get("outcome") == "PASS" for check in checks),
        "failed_count": sum(check.get("outcome") == "FAIL" for check in checks),
        "warning_count": sum(check.get("outcome") == "WARNING" for check in checks),
        "not_evaluated_count": sum(
            check.get("outcome") == "NOT_EVALUATED" for check in checks
        ),
    }
    expected["overall_status"] = (
        "PASS"
        if expected["check_count"] > 0
        and expected["passed_count"] == expected["check_count"]
        else "FAIL"
    )
    return all(aggregate.get(key) == value for key, value in expected.items())


def manifest_relations_valid(manifest: Mapping[str, Any], root: Path) -> bool:
    try:
        if set(manifest) != MANIFEST_ROOT_FIELDS:
            return False
        records = manifest["artifacts"]
        if not isinstance(records, list) or len(records) != 64:
            return False
        paths = [record["repository_path"] for record in records]
        if paths != list(MANIFEST_BOUND_PATHS) or paths != sorted(paths):
            return False
        if len(paths) != len(set(paths)) or any(
            not independent_safe_path(path) for path in paths
        ):
            return False
        if {MANIFEST_PATH, QUALIFICATION_PATH, SELF_TEST_PATH}.intersection(paths):
            return False
        for record in records:
            path = record["repository_path"]
            target = root.joinpath(*PurePosixPath(path).parts)
            if target.is_symlink() or not target.is_file():
                return False
            raw_bytes = target.read_bytes()
            if record.get("filename") != PurePosixPath(path).name:
                return False
            if record.get("byte_length") != len(raw_bytes):
                return False
            if record.get("sha256") != sha256_bytes(raw_bytes):
                return False
            if record.get("canonical") is not True or record.get("mutable") is not False:
                return False
            if record.get("measurement_contour") not in MEASUREMENT_CONTOURS:
                return False
            if record.get("producer") not in {
                None,
                M18_PRODUCER,
                SEMANTIC_REFERENCE,
                "benchmarks/architecture_comparison/run_architecture_comparison.py",
                "benchmarks/architecture_comparison/"
                "run_hardware_sensitivity_comparison.py",
            }:
                return False
            identifier = record.get("schema_identifier")
            if identifier is not None and identifier not in set(EXPECTED_SCHEMA_IDENTIFIERS) | {
                "frp.m3.benchmark_matrix.csv.v1.7.0",
                "frp.m15.vector.v1",
            }:
                return False
        if manifest.get("artifact_count") != 64:
            return False
        if manifest.get("artifact_set_sha256") != artifact_set_digest(records):
            return False
        return environment_fields_absent(manifest)
    except (KeyError, OSError, TypeError, UnicodeError, ValueError):
        return False


_BOUNDARY_PATHS = tuple(
    sorted(
        set(MANIFEST_BOUND_PATHS)
        | set(GENERATED_PATHS)
        | {"frp_m18_canonical_artifacts.py", SEMANTIC_REFERENCE}
    )
)
_INITIAL_BOUNDARY_SNAPSHOT = snapshot(_BOUNDARY_PATHS)
_DETERMINISM_CACHE: dict[str, Any] | None = None


def determinism_cache() -> dict[str, Any]:
    global _DETERMINISM_CACHE
    if _DETERMINISM_CACHE is not None:
        return _DETERMINISM_CACHE

    first_root = _CACHE_ROOT / "generation-a"
    second_root = _CACHE_ROOT / "generation-b"
    first = run_cli(
        "--generate",
        "--repository-root",
        str(REPO_ROOT),
        "--output-root",
        str(first_root),
        "--output",
        "json",
    )
    second = run_cli(
        "--generate",
        "--repository-root",
        str(REPO_ROOT),
        "--output-root",
        str(second_root),
        "--output",
        "json",
    )
    qualification_a = run_cli(
        "--qualify",
        "--repository-root",
        str(REPO_ROOT),
        "--output",
        "json",
    )
    qualification_b = run_cli(
        "--qualify",
        "--repository-root",
        str(REPO_ROOT),
        "--output",
        "json",
    )
    verification = run_cli(
        "--verify",
        "--repository-root",
        str(REPO_ROOT),
        "--output",
        "json",
    )
    self_test_a = run_cli("--self-test", "--output", "json", cwd=_CACHE_ROOT)
    self_test_b = run_cli("--self-test", "--output", "json", cwd=_CACHE_ROOT)
    commands = {
        "generation_a": first,
        "generation_b": second,
        "qualification_a": qualification_a,
        "qualification_b": qualification_b,
        "verification": verification,
        "self_test_a": self_test_a,
        "self_test_b": self_test_b,
    }
    failures = {
        name: (
            result.returncode,
            result.stdout.decode("utf-8", errors="replace"),
            result.stderr.decode("utf-8", errors="replace"),
        )
        for name, result in commands.items()
        if result.returncode != 0
    }
    if failures:
        raise AssertionError(f"M18 deterministic command failure: {failures}")
    _DETERMINISM_CACHE = {
        "first_root": first_root,
        "second_root": second_root,
        "first_files": recursive_file_bytes(first_root),
        "second_files": recursive_file_bytes(second_root),
        **commands,
    }
    return _DETERMINISM_CACHE


def tearDownModule() -> None:
    try:
        if snapshot(_BOUNDARY_PATHS) != _INITIAL_BOUNDARY_SNAPSHOT:
            raise AssertionError("M18 tests changed committed boundary bytes")
    finally:
        _CACHE_DIRECTORY.cleanup()


class M18ProducerInterfaceTests(unittest.TestCase):
    """Validate the producer import, CLI, subprocess, and exit-code contract."""

    def test_module_import_and_execution_modes_are_exact(self) -> None:
        self.assertTrue(PRODUCER_PATH.is_file())
        self.assertIs(producer.main, producer.main)
        parser = producer._parser()
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        self.assertTrue(
            {
                "--generate",
                "--verify",
                "--qualify",
                "--self-test",
                "--repository-root",
                "--output",
                "--output-root",
                "--replace",
            }.issubset(option_strings)
        )

    def test_cli_requires_exactly_one_mode_and_generate_output_root(self) -> None:
        cases = (
            (),
            ("--verify", "--qualify"),
            ("--generate",),
            ("--self-test", "--output", "yaml"),
            ("--verify", "--output-root", "unused"),
            ("--qualify", "--replace"),
        )
        before = snapshot(_BOUNDARY_PATHS)
        for arguments in cases:
            with self.subTest(arguments=arguments):
                completed = run_cli(*arguments)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, b"")
                self.assertTrue(completed.stderr.startswith(b"error: "))
        self.assertEqual(snapshot(_BOUNDARY_PATHS), before)

    def test_all_public_exit_codes_are_exercised(self) -> None:
        success = run_cli("--self-test", "--output", "json", cwd=_CACHE_ROOT)
        invalid = run_cli()
        with tempfile.TemporaryDirectory(prefix="frp-m18-empty-") as temporary:
            validation = run_cli(
                "--verify",
                "--repository-root",
                temporary,
                "--output",
                "json",
            )
        write_boundary = run_cli(
            "--generate",
            "--repository-root",
            str(REPO_ROOT),
            "--output-root",
            str(REPO_ROOT),
        )
        with tempfile.TemporaryDirectory(prefix="frp-m18-upstream-") as temporary:
            with mock.patch.object(
                producer,
                "_run_producer",
                side_effect=producer.UpstreamProducerError("fixture failure"),
            ), mock.patch.object(sys, "stderr", io.StringIO()) as diagnostic:
                upstream = producer.main(
                    [
                        "--generate",
                        "--repository-root",
                        str(REPO_ROOT),
                        "--output-root",
                        temporary,
                    ]
                )
        self.assertEqual(diagnostic.getvalue(), "error: fixture failure\n")
        self.assertEqual(
            (success.returncode, validation.returncode, invalid.returncode, upstream),
            (0, 1, 2, 3),
        )
        self.assertEqual(write_boundary.returncode, 4)

    def test_verify_and_qualify_are_read_only(self) -> None:
        before = snapshot(_BOUNDARY_PATHS)
        cache = determinism_cache()
        self.assertEqual(cache["verification"].returncode, 0)
        self.assertEqual(cache["qualification_a"].returncode, 0)
        self.assertEqual(cache["qualification_b"].returncode, 0)
        self.assertEqual(snapshot(_BOUNDARY_PATHS), before)

    def test_self_test_requires_no_repository_state_and_json_is_clean(self) -> None:
        with tempfile.TemporaryDirectory(prefix="frp-m18-self-test-") as temporary:
            missing_root = Path(temporary) / "absent"
            completed = run_cli(
                "--self-test",
                "--repository-root",
                str(missing_root),
                "--output",
                "json",
                cwd=Path(temporary),
            )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr, b"")
        payload = strict_json_bytes(completed.stdout)
        self.assertEqual(payload["overall_status"], "PASS")
        self.assertEqual(completed.stdout, canonical_json_bytes(payload))

    def test_upstream_invocation_uses_fixed_executable_and_argument_list(self) -> None:
        literal_argument = "--value;touch /tmp/not-executed"
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"{}\n",
            stderr=b"",
        )
        with mock.patch.object(producer.subprocess, "run", return_value=completed) as called:
            observed = producer._run_producer(REPO_ROOT, (literal_argument,))
        self.assertEqual(observed, b"{}\n")
        positional, keywords = called.call_args
        command = positional[0]
        self.assertIsInstance(command, list)
        self.assertEqual(command[0], sys.executable)
        self.assertEqual(command[1], str(REPO_ROOT / SEMANTIC_REFERENCE))
        self.assertEqual(command[2], literal_argument)
        self.assertIs(keywords["shell"], False)
        self.assertEqual(keywords["stdout"], subprocess.PIPE)
        self.assertEqual(keywords["stderr"], subprocess.PIPE)


class M18SchemaRegistryTests(unittest.TestCase):
    """Validate the exact supported-schema registry independently."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = repository_file(REGISTRY_PATH).read_bytes()
        cls.registry = strict_json_bytes(cls.raw)
        cls.records = cls.registry["records"]
        cls.context = producer.RepositoryContext(REPO_ROOT)

    def test_registry_path_utf8_root_identity_and_digest_are_exact(self) -> None:
        self.assertEqual(repository_file(REGISTRY_PATH).relative_to(REPO_ROOT).as_posix(), REGISTRY_PATH)
        self.raw.decode("utf-8")
        self.assertEqual(set(self.registry), REGISTRY_ROOT_FIELDS)
        expected = {
            "schema": "frp.m18.formal_schema_registry.v2.0.0",
            "kind": "formal_schema_registry",
            "version": M18_VERSION,
            "milestone": M18_MILESTONE,
            "json_schema_dialect": JSON_SCHEMA_DIALECT,
            "record_order": "schema_identifier_lexicographic",
            "schema_count": 24,
            "registry_digest_scope": (
                "canonical_compact_json_without_registry_content_sha256"
            ),
        }
        for field, value in expected.items():
            self.assertEqual(self.registry[field], value)
        digest_source = dict(self.registry)
        declared = digest_source.pop("registry_content_sha256")
        self.assertEqual(
            declared,
            "6d2d0077b00c9f3da04429a8a690256fe7b4de585c7257804471a3d3d4992c0c",
        )
        self.assertEqual(declared, sha256_bytes(compact_json_bytes(digest_source)))

    def test_exact_twenty_four_records_identifiers_paths_and_urns(self) -> None:
        identifiers = tuple(record["schema_identifier"] for record in self.records)
        paths = tuple(record["schema_path"] for record in self.records)
        urns = tuple(record["schema_urn"] for record in self.records)
        self.assertEqual(len(self.records), 24)
        self.assertEqual(identifiers, EXPECTED_SCHEMA_IDENTIFIERS)
        self.assertEqual(paths, EXPECTED_SCHEMA_PATHS)
        self.assertEqual(
            urns,
            tuple(SCHEMA_URN_PREFIX + identifier for identifier in EXPECTED_SCHEMA_IDENTIFIERS),
        )
        self.assertEqual(identifiers, tuple(sorted(identifiers)))
        self.assertEqual(len(set(identifiers)), 24)
        self.assertEqual(len(set(paths)), 24)
        self.assertEqual(len(set(urns)), 24)

    def test_record_fields_and_registered_value_domains_are_exact(self) -> None:
        self.assertTrue(all(set(record) == REGISTRY_RECORD_FIELDS for record in self.records))
        self.assertEqual({record["artifact_format"] for record in self.records}, {"json"})
        self.assertEqual(
            {record["identity_basis"] for record in self.records},
            {"embedded_schema", "registry_bound_exact_path_and_role", "schema_and_kind"},
        )
        self.assertEqual(
            {record["measurement_contour"] for record in self.records},
            set(MEASUREMENT_CONTOURS),
        )
        self.assertEqual(
            {record["producer_version"] for record in self.records},
            {None, "1.7.0", "2.0.0"},
        )
        self.assertEqual(
            {record["validation_mode"] for record in self.records},
            {"json_schema_draft_2020_12"},
        )
        self.assertTrue(all(record["required"] is True for record in self.records))
        self.assertTrue(all(record["supported"] is True for record in self.records))
        for record in self.records:
            modes = record.get("observatory_modes")
            if modes is not None:
                self.assertTrue(observatory_modes_valid(modes))

    def test_observatory_mode_vocabulary_validation_is_closed(self) -> None:
        self.assertTrue(observatory_modes_valid(list(OBSERVATORY_MODES)))
        for fixture in (
            [],
            ["trace_explorer", "artifact_auditor"],
            ["artifact_auditor", "artifact_auditor"],
            ["unknown_mode"],
        ):
            with self.subTest(fixture=fixture):
                self.assertFalse(observatory_modes_valid(fixture))

    def test_producer_bindings_and_referenced_files_exist(self) -> None:
        allowed_producers = {
            None,
            M18_PRODUCER,
            SEMANTIC_REFERENCE,
            "benchmarks/architecture_comparison/run_architecture_comparison.py",
            "benchmarks/architecture_comparison/"
            "run_hardware_sensitivity_comparison.py",
        }
        for record in self.records:
            with self.subTest(identifier=record["schema_identifier"]):
                self.assertIn(record["producer_path"], allowed_producers)
                self.assertTrue(repository_file(record["schema_path"]).is_file())
                if record["producer_path"] is not None:
                    self.assertTrue(repository_file(record["producer_path"]).is_file())
                for path in record["canonical_artifact_paths"]:
                    self.assertTrue(independent_safe_path(path))
                    self.assertTrue(repository_file(path).is_file())

    def test_corrected_structured_output_bindings_are_present(self) -> None:
        record = next(
            item
            for item in self.records
            if item["schema_identifier"] == "frp.structured_output.v1.7.0"
        )
        paths = record["canonical_artifact_paths"]
        self.assertEqual(set(paths), set(STRUCTURED_SPECS))
        self.assertIn("artifacts/m18/structured_output/trace-free.json", paths)
        self.assertIn("artifacts/m18/structured_output/trace-7-1.json", paths)
        self.assertIn("artifacts/m18/structured_output/trace-1-7.json", paths)
        self.assertIn("artifacts/m18/structured_output/self-test-default.json", paths)

    def test_malformed_registry_records_are_rejected(self) -> None:
        cases: list[tuple[str, dict[str, Any]]] = []
        duplicate = copy.deepcopy(self.registry)
        duplicate["records"][1] = copy.deepcopy(duplicate["records"][0])
        cases.append(("duplicate", duplicate))
        unknown = copy.deepcopy(self.registry)
        unknown["records"][0]["schema_identifier"] = "frp.unknown.v1"
        cases.append(("unknown", unknown))
        parent = copy.deepcopy(self.registry)
        parent["records"][0]["schema_path"] = "schemas/m18/../escape.schema.json"
        cases.append(("parent", parent))
        absolute = copy.deepcopy(self.registry)
        absolute["records"][0]["schema_path"] = "/schemas/m18/value.schema.json"
        cases.append(("absolute", absolute))
        for label, fixture in cases:
            with self.subTest(label=label):
                with self.assertRaises(producer.ContractError):
                    self.context.validate(
                        "frp.m18.formal_schema_registry.v2.0.0",
                        fixture,
                        label,
                    )


class M18FormalSchemaTests(unittest.TestCase):
    """Validate all registered Draft 2020-12 schemas and representative data."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = producer.RepositoryContext(REPO_ROOT)

    def test_all_schemas_are_valid_unique_offline_draft_2020_12(self) -> None:
        observed_ids: list[str] = []
        for identifier, expected_path in zip(
            EXPECTED_SCHEMA_IDENTIFIERS,
            EXPECTED_SCHEMA_PATHS,
            strict=True,
        ):
            with self.subTest(identifier=identifier):
                schema = strict_json_bytes(repository_file(expected_path).read_bytes())
                Draft202012Validator.check_schema(schema)
                self.assertEqual(schema["$schema"], JSON_SCHEMA_DIALECT)
                self.assertEqual(schema["$id"], SCHEMA_URN_PREFIX + identifier)
                self.assertEqual(schema["x-frp-schema-identifier"], identifier)
                observed_ids.append(schema["$id"])
                stack = [schema]
                while stack:
                    value = stack.pop()
                    if isinstance(value, dict):
                        reference = value.get("$ref")
                        if reference is not None:
                            self.assertTrue(reference.startswith("#"))
                        stack.extend(value.values())
                    elif isinstance(value, list):
                        stack.extend(value)
        self.assertEqual(len(observed_ids), 24)
        self.assertEqual(len(set(observed_ids)), 24)

    def test_required_and_additional_field_behavior_is_explicit(self) -> None:
        for identifier in EXPECTED_SCHEMA_IDENTIFIERS:
            schema = self.context.schemas[identifier]
            with self.subTest(identifier=identifier):
                if identifier == "frp.structured_output.v1.7.0":
                    self.assertEqual(len(schema.get("oneOf", [])), 2)
                else:
                    self.assertEqual(schema.get("type"), "object")
                    self.assertTrue(schema.get("required"))
                    self.assertIs(schema.get("additionalProperties"), False)

    def test_canonical_ternary_enums_are_exact_and_boolean_safe(self) -> None:
        ternary_nodes: list[dict[str, Any]] = []
        schema_text = ""
        for identifier in EXPECTED_SCHEMA_IDENTIFIERS:
            schema = self.context.schemas[identifier]
            schema_text += json.dumps(schema, ensure_ascii=False, sort_keys=True)
            stack = [schema]
            while stack:
                value = stack.pop()
                if isinstance(value, dict):
                    if value.get("enum") == [-1, 0, 1]:
                        ternary_nodes.append(value)
                    stack.extend(value.values())
                elif isinstance(value, list):
                    stack.extend(value)
        self.assertGreaterEqual(len(ternary_nodes), 1)
        self.assertNotIn('"+1"', schema_text)
        for node in ternary_nodes:
            validator = Draft202012Validator(node)
            for state in CANONICAL_STATES:
                self.assertTrue(validator.is_valid(state))
            self.assertFalse(validator.is_valid(True))
            self.assertFalse(validator.is_valid(False))
            self.assertFalse(validator.is_valid(2))

    def test_all_registered_canonical_json_instances_validate(self) -> None:
        registry = strict_json_bytes(repository_file(REGISTRY_PATH).read_bytes())
        for record in registry["records"]:
            identifier = record["schema_identifier"]
            for path in record["canonical_artifact_paths"]:
                if PurePosixPath(path).suffix != ".json":
                    continue
                payload = strict_json_bytes(repository_file(path).read_bytes())
                with self.subTest(identifier=identifier, path=path):
                    self.context.validate(identifier, payload, path)

    def test_optional_structured_trace_and_matrix_fields_remain_optional(self) -> None:
        trace_free = strict_json_bytes(
            repository_file(
                "artifacts/m18/structured_output/structured-output.json"
            ).read_bytes()
        )
        self.context.validate(
            "frp.structured_output.v1.7.0",
            trace_free,
            "trace-free fixture",
        )
        self.assertFalse({"trace", "cell_trace", "route_events"}.intersection(trace_free))
        matrix = strict_json_bytes(repository_file(BENCHMARK_JSON_PATH).read_bytes())
        self.assertNotIn("comparison_rule", matrix["rows"][0])
        self.context.validate(
            "frp.m3.benchmark_matrix.v1.7.0",
            matrix,
            "optional matrix fixture",
        )

    def test_malformed_representative_instances_are_rejected(self) -> None:
        preload_path = f"{VECTOR_DIRECTORY}/frp_m15_reference_preload.json"
        preload = strict_json_bytes(repository_file(preload_path).read_bytes())
        malformed_preload = copy.deepcopy(preload)
        malformed_preload.pop("cells")
        with self.assertRaises(producer.ContractError):
            self.context.validate(
                "frp.m15.reference_preload.v1.7.0",
                malformed_preload,
                "missing cells",
            )
        structured = strict_json_bytes(
            repository_file("artifacts/m18/structured_output/trace-7-1.json").read_bytes()
        )
        malformed_structured = copy.deepcopy(structured)
        malformed_structured["summary"]["actual_direct_events"] = 1
        with self.assertRaises(producer.ContractError):
            self.context.validate(
                "frp.structured_output.v1.7.0",
                malformed_structured,
                "direct transition",
            )

    def test_remote_reference_is_rejected_before_resolution(self) -> None:
        with self.assertRaises(producer.ContractError):
            producer.RepositoryContext._validate_refs(
                {"$ref": "https://example.invalid/schema.json"},
                "remote fixture",
            )


class M18CanonicalArtifactTests(unittest.TestCase):
    """Validate exact canonical artifact sets and cross-artifact relations."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = producer.RepositoryContext(REPO_ROOT)
        cls.core = {
            path: repository_file(path).read_bytes()
            for path in GENERATED_CORE_PATHS
        }
        cls.manifest = strict_json_bytes(repository_file(MANIFEST_PATH).read_bytes())
        cls.manifest_by_path = {
            record["repository_path"]: record
            for record in cls.manifest["artifacts"]
        }

    def test_exact_committed_publication_sets_are_present(self) -> None:
        observed_m18 = tuple(
            sorted(
                path.relative_to(REPO_ROOT).as_posix()
                for path in (REPO_ROOT / "artifacts/m18").rglob("*")
                if path.is_file() and not path.is_symlink()
            )
        )
        self.assertEqual(len(STRUCTURED_SPECS), 11)
        self.assertEqual(len(BENCHMARK_PATHS), 2)
        self.assertEqual(len(COMPARATIVE_SPECS), 6)
        self.assertEqual(len(M15_EXPORT_SPECS), 10)
        self.assertEqual(len(VECTOR_PATHS), 10)
        self.assertEqual(len(GENERATED_PATHS), 36)
        self.assertEqual(observed_m18, GENERATED_PATHS)

    def test_all_canonical_artifacts_are_regular_nonempty_and_strict(self) -> None:
        for path in tuple(GENERATED_PATHS) + tuple(COMPARATIVE_SPECS):
            target = repository_file(path)
            with self.subTest(path=path):
                self.assertTrue(target.is_file())
                self.assertFalse(target.is_symlink())
                raw_bytes = target.read_bytes()
                self.assertGreater(len(raw_bytes), 0)
                if target.suffix == ".json":
                    strict_json_bytes(raw_bytes)

    def test_registered_schema_identity_format_producer_and_contour_bindings(self) -> None:
        for path in MANIFEST_BOUND_PATHS:
            record = self.manifest_by_path[path]
            with self.subTest(path=path):
                self.assertEqual(record["filename"], PurePosixPath(path).name)
                self.assertTrue(record["canonical"])
                self.assertFalse(record["mutable"])
                self.assertEqual(record["byte_length"], repository_file(path).stat().st_size)
                self.assertEqual(record["sha256"], sha256_bytes(repository_file(path).read_bytes()))
                self.assertIn(record["measurement_contour"], MEASUREMENT_CONTOURS)
                if (
                    record["format"] == "json"
                    and record["artifact_class"] != "formal_schema"
                    and record["schema_identifier"] in EXPECTED_SCHEMA_IDENTIFIERS
                ):
                    payload = strict_json_bytes(repository_file(path).read_bytes())
                    self.context.validate(record["schema_identifier"], payload, path)

        for path, (identifier, identity, source, contour) in COMPARATIVE_SPECS.items():
            record = self.manifest_by_path[path]
            expected_basis = (
                "registry_binding"
                if identity == "registry_bound_exact_path_and_role"
                else "embedded_schema"
            )
            self.assertEqual(record["schema_identifier"], identifier)
            self.assertEqual(record["identification_basis"], expected_basis)
            self.assertEqual(record["producer"], source)
            self.assertEqual(record["measurement_contour"], contour)

    def test_structured_outputs_preserve_exact_identity_and_invariants(self) -> None:
        for path, (mode, scheduler, cells, steps, include_trace) in STRUCTURED_SPECS.items():
            payload = strict_json_bytes(repository_file(path).read_bytes())
            with self.subTest(path=path):
                self.assertEqual(payload["schema"], "frp.structured_output.v1.7.0")
                self.assertEqual(payload["version"], M15_VERSION)
                self.assertEqual(payload["milestone"], M15_MILESTONE)
                producer._validate_structured(path, payload)
                if mode == "self-test":
                    self.assertEqual(payload["kind"], "self_test")
                    self.assertEqual(payload["status"], "PASS")
                    self.assertEqual(payload["check_count"], 41)
                    self.assertEqual(len(payload["checks"]), 41)
                    self.assertTrue(all(value is True for value in payload["checks"].values()))
                    negative_to_positive = payload["neutral_route_validation"]["-1_to_0_to_1"]
                    positive_to_negative = payload["neutral_route_validation"]["1_to_0_to_-1"]
                    self.assertEqual(negative_to_positive["status"], "PASS")
                    self.assertEqual(positive_to_negative["status"], "PASS")
                    self.assertTrue(all(negative_to_positive["checks"].values()))
                    self.assertTrue(all(positive_to_negative["checks"].values()))
                    continue
                configuration = payload["configuration"]
                summary = payload["summary"]
                self.assertEqual(
                    (configuration["scheduler"], configuration["cells"], configuration["steps"], configuration["seed"]),
                    (scheduler, cells, steps, 76),
                )
                self.assertEqual(summary["actual_direct_events"], 0)
                self.assertEqual(summary["reserved_state_events"], 0)
                self.assertEqual(summary["queue_overflow_events"], 0)
                self.assertTrue(summary["balanced_ternary_state_domain"])
                self.assertTrue(summary["scheduler_counts_valid"])
                self.assertLessEqual(summary["pending_route_count_final"], summary["neutral_route_queue_capacity"])
                self.assertLessEqual(summary["switch_load_peak"], summary["transition_fraction"])
                self.assertEqual(summary["ticks_recorded"], steps)
                kernel_text = json.dumps(payload["kernel"], ensure_ascii=False, sort_keys=True)
                self.assertIn("-1", kernel_text)
                self.assertNotIn('"+1"', kernel_text)
                trace_fields = {"trace", "cell_trace", "route_events"}
                self.assertEqual(trace_fields.issubset(payload), include_trace)

    def test_trace_order_scheduler_routes_and_retained_state_relations(self) -> None:
        for path in (
            "artifacts/m18/structured_output/trace-free.json",
            "artifacts/m18/structured_output/trace-7-1.json",
            "artifacts/m18/structured_output/trace-1-7.json",
        ):
            payload = strict_json_bytes(repository_file(path).read_bytes())
            scheduler = payload["configuration"]["scheduler"]
            trace = payload["trace"]
            cells = payload["configuration"]["cells"]
            steps = payload["configuration"]["steps"]
            with self.subTest(path=path):
                self.assertEqual([row["tick"] for row in trace], list(range(steps)))
                self.assertEqual(
                    tuple(row["scheduler_state_name"] for row in trace),
                    scheduler_sequence(scheduler, steps),
                )
                self.assertEqual(
                    [(row["tick"], row["cell_id"]) for row in payload["cell_trace"]],
                    [(tick, cell) for tick in range(steps) for cell in range(cells)],
                )
                vectors = [state_vector_from_human(row["states_human"]) for row in trace]
                self.assertTrue(all(set(vector).issubset(CANONICAL_STATES) for vector in vectors))
                for previous, current in zip(vectors, vectors[1:]):
                    self.assertTrue(
                        all(not (left == -right and left != 0) for left, right in zip(previous, current))
                    )
                for row in trace:
                    self.assertEqual(row["actual_direct_events"], 0)
                    self.assertEqual(row["reserved_state_events"], 0)
                    self.assertEqual(row["queue_overflow_events"], 0)
                    self.assertLessEqual(row["pending_route_count"], cells)
                    self.assertLessEqual(row["changes"], cells // 4)
                routes = payload["route_events"]
                self.assertTrue(all(route["target_state"] in CANONICAL_STATES for route in routes))
                self.assertTrue(all(route["route_status"] in {"pending", "applied"} for route in routes))
                pending = [route for route in routes if route["route_status"] == "pending"]
                applied = [route for route in routes if route["route_status"] == "applied"]
                self.assertTrue(all(route["ready_tick"] > route["tick"] for route in pending))
                self.assertTrue(all(route["tick"] >= route["ready_tick"] for route in applied))

    def test_benchmark_matrix_json_csv_relation_is_exact(self) -> None:
        matrix_raw = repository_file(BENCHMARK_JSON_PATH).read_bytes()
        csv_raw = repository_file(BENCHMARK_CSV_PATH).read_bytes()
        matrix = strict_json_bytes(matrix_raw)
        self.context.validate("frp.m3.benchmark_matrix.v1.7.0", matrix, BENCHMARK_JSON_PATH)
        rows = matrix["rows"]
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(row["architecture"] for row in rows), BENCHMARK_ARCHITECTURES)
        self.assertEqual(rows[1]["C_minus_P_sign_match"], 1.0)
        self.assertEqual(rows[1]["scheduler_sequence_match"], 1.0)
        self.assertEqual(rows[1]["state_sequence_match"], 1.0)
        self.assertEqual(rows[2]["vector_repeat_match"], 1.0)
        self.assertEqual(rows[3]["comparison_rule"], "actual == expected")
        self.assertEqual(rows[4]["artifact_layers"], 10)
        parsed_csv = list(csv.reader(io.StringIO(csv_raw.decode("utf-8"), newline="")))
        self.assertEqual(tuple(parsed_csv[0]), BENCHMARK_COLUMNS)
        self.assertEqual(len(parsed_csv), 6)
        self.assertTrue(all(len(row) == len(BENCHMARK_COLUMNS) for row in parsed_csv))
        self.assertEqual(tuple(row[0] for row in parsed_csv[1:]), BENCHMARK_ARCHITECTURES)
        for json_row, csv_row in zip(rows, parsed_csv[1:], strict=True):
            expected = []
            for column in BENCHMARK_COLUMNS:
                value = json_row.get(column, "")
                if isinstance(value, bool):
                    expected.append("true" if value else "false")
                else:
                    expected.append(str(value))
            self.assertEqual(csv_row, expected)
        self.assertEqual(csv_raw, producer.benchmark_csv_bytes(matrix))
        self.assertTrue(csv_raw.endswith(b"\n"))
        self.assertFalse(csv_raw.endswith(b"\n\n"))

    def test_comparative_profiles_results_digests_order_and_contours(self) -> None:
        payloads = {
            path: strict_json_bytes(repository_file(path).read_bytes())
            for path in COMPARATIVE_SPECS
        }
        producer._validate_comparative(self.context)
        workload_path = "benchmarks/architecture_comparison/profiles/workload_profile_v1.json"
        cost_path = "benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json"
        thermal_path = "benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json"
        sensitivity_path = (
            "benchmarks/architecture_comparison/profiles/"
            "hardware_sensitivity_cost_profile_v1.json"
        )
        baseline_path = "benchmarks/architecture_comparison/results/reference_comparison_seed_76.json"
        hardware_path = (
            "benchmarks/architecture_comparison/results/"
            "reference_comparison_seed_76_hardware_sensitivity_v1.json"
        )
        baseline = payloads[baseline_path]
        hardware = payloads[hardware_path]
        architecture_order = (
            "binary_synchronous_reference",
            "binary_clock_gated_reference",
            "direct_ternary_reference",
            "frp_v1_7_0_quantized_shadow",
        )
        self.assertEqual(tuple(baseline["architecture_order"]), architecture_order)
        self.assertEqual(tuple(hardware["architecture_order"]), architecture_order)
        self.assertEqual(baseline["workload_profile"], payloads[workload_path])
        self.assertEqual(
            baseline["cost_profile"],
            {
                key: payloads[cost_path][key]
                for key in baseline["cost_profile"]
            },
        )
        self.assertEqual(
            baseline["thermal_profile"],
            {
                key: payloads[thermal_path][key]
                for key in baseline["thermal_profile"]
            },
        )
        self.assertEqual(
            baseline["cost_profile_sha256"],
            payloads[cost_path]["cost_profile_sha256"],
        )
        self.assertEqual(
            baseline["thermal_profile_sha256"],
            payloads[thermal_path]["thermal_profile_sha256"],
        )
        self.assertEqual(hardware["workload_profile"], payloads[workload_path])
        self.assertEqual(
            hardware["thermal_profile"],
            {
                key: payloads[thermal_path][key]
                for key in hardware["thermal_profile"]
            },
        )
        self.assertEqual(
            hardware["hardware_sensitivity_profile"],
            {
                key: payloads[sensitivity_path][key]
                for key in hardware["hardware_sensitivity_profile"]
            },
        )
        scenario_order = ("lower_bound", "nominal", "upper_bound")
        self.assertEqual(tuple(payloads[sensitivity_path]["scenario_order"]), scenario_order)
        self.assertEqual(tuple(item["scenario_id"] for item in hardware["scenarios"]), scenario_order)
        expected_ranking = (
            "binary_clock_gated_reference",
            "direct_ternary_reference",
            "binary_synchronous_reference",
            "frp_v1_7_0_quantized_shadow",
        )
        for scenario in hardware["scenarios"]:
            self.assertEqual(tuple(scenario["ranking"]["architecture_order"]), expected_ranking)
            self.assertEqual(
                tuple(item["architecture_id"] for item in scenario["architectures"]),
                architecture_order,
            )
            for architecture in scenario["architectures"]:
                identifier = architecture["architecture_id"]
                self.assertEqual(
                    architecture["architecture_result_sha256"],
                    hardware["baseline_binding"]["architecture_result_sha256"][identifier],
                )
        self.assertEqual(baseline["qualification"]["status"], "PASS")
        self.assertEqual(baseline["integrity"]["status"], "PASS")
        self.assertEqual(hardware["qualification"]["status"], "PASS")
        self.assertEqual(hardware["integrity"]["status"], "PASS")
        self.assertEqual(
            {
                self.manifest_by_path[path]["measurement_contour"]
                for path in COMPARATIVE_SPECS
            },
            {
                "comparative_architecture_benchmark_suite",
                "hardware_informed_sensitivity_qualification",
            },
        )

    def test_m15_exports_have_exact_identity_commands_and_encodings(self) -> None:
        for path, (identifier, kind, option) in M15_EXPORT_SPECS.items():
            payload = strict_json_bytes(repository_file(path).read_bytes())
            record = self.manifest_by_path[path]
            with self.subTest(path=path):
                self.assertEqual(payload["schema"], identifier)
                self.assertEqual(payload["kind"], kind)
                self.assertEqual(payload["version"], M15_VERSION)
                self.assertEqual(payload["milestone"], M15_MILESTONE)
                self.context.validate(identifier, payload, path)
                self.assertEqual(record["producer"], SEMANTIC_REFERENCE)
                self.assertEqual(record["producer_version"], M15_VERSION)
                self.assertEqual(
                    record["producer_command"],
                    f"python {SEMANTIC_REFERENCE} {option}",
                )
        encoding_path = (
            "artifacts/m18/m15_exports/"
            "balanced-ternary-hardware-encoding-map.json"
        )
        encoding = strict_json_bytes(repository_file(encoding_path).read_bytes())
        self.assertEqual(
            tuple(
                (item["state"], item["code"], item["integer_code"])
                for item in encoding["state_encoding"]
            ),
            tuple((state, *STATE_CODES[state]) for state in CANONICAL_STATES),
        )
        reserved = encoding["reserved_state_code"]
        self.assertEqual((reserved["code"], reserved["integer_code"]), RESERVED_STATE_CODE)
        self.assertNotIn(reserved["integer_code"], CANONICAL_STATES)
        self.assertEqual(
            tuple((item["name"], item["code"]) for item in encoding["scheduler_mode_encoding"]),
            (("free", 0), ("7/1", 1), ("1/7", 2)),
        )

    def test_m15_vector_package_exact_members_headers_preload_and_digests(self) -> None:
        self.assertTrue(independent_vector_package_valid(self.core))
        producer._validate_vector_package(self.core)
        members = {
            PurePosixPath(path).name: self.core[path]
            for path in VECTOR_PATHS
        }
        self.assertEqual(tuple(sorted(members)), VECTOR_MEMBER_NAMES)
        internal = strict_json_bytes(members["frp_m15_sha256_manifest.json"])
        self.assertEqual(len(internal), 9)
        self.assertNotIn("frp_m15_sha256_manifest.json", internal)
        for name, digest in internal.items():
            self.assertEqual(digest, sha256_bytes(members[name]))
        descriptor = strict_json_bytes(
            repository_file(
                "artifacts/m18/m15_exports/rtl-comparison-vector-package.json"
            ).read_bytes()
        )
        self.assertEqual(descriptor["manifest"]["file_count"], 10)
        self.assertEqual(
            tuple(item["name"] for item in descriptor["manifest"]["files"]),
            VECTOR_MEMBER_NAMES,
        )
        for item in descriptor["manifest"]["files"]:
            self.assertEqual(item["size_bytes"], len(members[item["name"]]))
            self.assertEqual(item["sha256"], sha256_bytes(members[item["name"]]))
        self.assertEqual(descriptor["deterministic_package_digest"], VECTOR_PACKAGE_DIGEST)

    def test_vector_package_negative_fixtures_are_rejected(self) -> None:
        fixtures: dict[str, dict[str, bytes]] = {}

        missing = dict(self.core)
        missing.pop(VECTOR_PATHS[0])
        fixtures["missing"] = missing

        unexpected = dict(self.core)
        unexpected[f"{VECTOR_DIRECTORY}/unexpected.vec"] = b"unexpected\n"
        fixtures["unexpected"] = unexpected

        renamed = dict(self.core)
        renamed[f"{VECTOR_DIRECTORY}/renamed.vec"] = renamed.pop(VECTOR_PATHS[0])
        fixtures["renamed"] = renamed

        duplicate = dict(self.core)
        internal_path = f"{VECTOR_DIRECTORY}/frp_m15_sha256_manifest.json"
        duplicate[internal_path] = b'{"x":"a","x":"b"}\n'
        fixtures["duplicate_record"] = duplicate

        altered = dict(self.core)
        altered[VECTOR_PATHS[0]] += b"altered\n"
        fixtures["altered_member"] = altered

        incorrect_digest = dict(self.core)
        internal = strict_json_bytes(incorrect_digest[internal_path])
        internal[VECTOR_MEMBER_NAMES[0]] = "0" * 64
        incorrect_digest[internal_path] = canonical_json_bytes(internal)
        fixtures["incorrect_digest"] = incorrect_digest

        self_entry = dict(self.core)
        internal = strict_json_bytes(self_entry[internal_path])
        internal["frp_m15_sha256_manifest.json"] = "0" * 64
        self_entry[internal_path] = canonical_json_bytes(internal)
        fixtures["internal_self_entry"] = self_entry

        invalid_state = dict(self.core)
        preload_path = f"{VECTOR_DIRECTORY}/frp_m15_reference_preload.json"
        preload = strict_json_bytes(invalid_state[preload_path])
        preload["states"][0] = 2
        invalid_state[preload_path] = canonical_json_bytes(preload)
        fixtures["invalid_state_code"] = invalid_state

        scheduler_mismatch = dict(self.core)
        scheduler_path = f"{VECTOR_DIRECTORY}/frp_m15_scheduler_7_1_vectors.vec"
        scheduler_mismatch[scheduler_path] = scheduler_mismatch[scheduler_path].replace(
            b'# scheduler_mode="7/1"',
            b'# scheduler_mode="1/7"',
            1,
        )
        fixtures["scheduler_mismatch"] = scheduler_mismatch

        lookup_order = dict(self.core)
        lookup_path = f"{VECTOR_DIRECTORY}/frp_m15_trig_lut_q30.vec"
        lines = lookup_order[lookup_path].splitlines(keepends=True)
        lines[3], lines[4] = lines[4], lines[3]
        lookup_order[lookup_path] = b"".join(lines)
        fixtures["lookup_order"] = lookup_order

        self.assertEqual(len(fixtures), 10)
        for label, fixture in fixtures.items():
            with self.subTest(label=label):
                self.assertFalse(independent_vector_package_valid(fixture))


class M18ManifestTests(unittest.TestCase):
    """Validate the exact 64-record canonical manifest and negative fixtures."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = producer.RepositoryContext(REPO_ROOT)
        cls.raw = repository_file(MANIFEST_PATH).read_bytes()
        cls.manifest = strict_json_bytes(cls.raw)

    def test_manifest_identity_scope_order_count_and_schema_are_exact(self) -> None:
        self.context.validate(
            "frp.m18.canonical_artifact_manifest.v2.0.0",
            self.manifest,
            MANIFEST_PATH,
        )
        self.assertEqual(set(self.manifest), MANIFEST_ROOT_FIELDS)
        expected = {
            "schema": "frp.m18.canonical_artifact_manifest.v2.0.0",
            "kind": "canonical_artifact_manifest",
            "version": M18_VERSION,
            "milestone": M18_MILESTONE,
            "producer": M18_PRODUCER,
            "producer_version": M18_VERSION,
            "upstream_release": "FRP v1.8.0 / M16",
            "artifact_order": "repository_path_lexicographic",
            "digest_algorithm": "sha256",
            "digest_scope": "raw_bytes",
            "artifact_count": 64,
        }
        for field, value in expected.items():
            self.assertEqual(self.manifest[field], value)
        paths = tuple(record["repository_path"] for record in self.manifest["artifacts"])
        self.assertEqual(paths, MANIFEST_BOUND_PATHS)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertFalse({MANIFEST_PATH, QUALIFICATION_PATH, SELF_TEST_PATH}.intersection(paths))

    def test_manifest_records_bind_exact_files_metadata_and_raw_digests(self) -> None:
        records = self.manifest["artifacts"]
        self.assertTrue(manifest_relations_valid(self.manifest, REPO_ROOT))
        self.assertEqual(
            {record["artifact_class"] for record in records},
            {
                "benchmark_matrix_csv",
                "benchmark_matrix_json",
                "comparative_benchmark",
                "formal_schema",
                "m15_export",
                "m15_vector_member",
                "schema_registry",
                "structured_output",
            },
        )
        self.assertEqual(
            {record["format"] for record in records},
            {"csv", "headered_trace", "headered_vector", "json", "vector_text"},
        )
        self.assertEqual(
            {record["identification_basis"] for record in records},
            {
                "embedded_schema",
                "format_header",
                "package_role",
                "registry_binding",
            },
        )
        self.assertEqual(
            {record["measurement_contour"] for record in records},
            set(MEASUREMENT_CONTOURS),
        )
        for record in records:
            path = record["repository_path"]
            self.assertTrue(independent_safe_path(path))
            self.assertEqual(record["filename"], PurePosixPath(path).name)
            self.assertTrue(repository_file(path).is_file())
            self.assertFalse(repository_file(path).is_symlink())
            raw_bytes = repository_file(path).read_bytes()
            self.assertEqual(record["byte_length"], len(raw_bytes))
            self.assertEqual(record["sha256"], sha256_bytes(raw_bytes))
            self.assertTrue(record["canonical"])
            self.assertFalse(record["mutable"])

    def test_manifest_artifact_set_digest_and_serialization_are_deterministic(self) -> None:
        observed = artifact_set_digest(self.manifest["artifacts"])
        self.assertEqual(self.manifest["artifact_set_sha256"], observed)
        self.assertEqual(
            observed,
            "c190ffeee11ac44a5f89efa85e54fc656cac23f0f66f625cf303419b967a9f83",
        )
        self.assertEqual(self.raw, canonical_json_bytes(self.manifest))
        context = producer.RepositoryContext(REPO_ROOT)
        core = {
            path: repository_file(path).read_bytes()
            for path in GENERATED_CORE_PATHS
        }
        rebuilt = producer.build_manifest(context, core)
        self.assertEqual(canonical_json_bytes(rebuilt), self.raw)

    def test_negative_manifest_fixtures_are_rejected(self) -> None:
        fixtures: dict[str, dict[str, Any]] = {}

        def changed(label: str, field: str, value: Any) -> None:
            fixture = copy.deepcopy(self.manifest)
            fixture["artifacts"][0][field] = value
            fixtures[label] = fixture

        changed("absolute_path", "repository_path", "/absolute.json")
        changed("parent_component", "repository_path", "artifacts/../escape.json")
        changed("backslash", "repository_path", "artifacts\\escape.json")
        duplicate = copy.deepcopy(self.manifest)
        duplicate["artifacts"][1]["repository_path"] = duplicate["artifacts"][0]["repository_path"]
        fixtures["duplicate_path"] = duplicate
        changed("unknown_schema", "schema_identifier", "frp.unknown.v1")
        changed("wrong_producer", "producer", "unknown.py")
        changed("wrong_contour", "measurement_contour", "unknown_contour")
        changed("incorrect_length", "byte_length", 0)
        changed("incorrect_digest", "sha256", "0" * 64)
        incorrect_order = copy.deepcopy(self.manifest)
        incorrect_order["artifacts"][0], incorrect_order["artifacts"][1] = (
            incorrect_order["artifacts"][1],
            incorrect_order["artifacts"][0],
        )
        fixtures["incorrect_order"] = incorrect_order
        changed("self_binding", "repository_path", MANIFEST_PATH)
        timestamp = copy.deepcopy(self.manifest)
        timestamp["timestamp"] = "2026-01-01T00:00:00Z"
        fixtures["environment_field"] = timestamp

        self.assertEqual(len(fixtures), 12)
        for label, fixture in fixtures.items():
            with self.subTest(label=label):
                self.assertFalse(manifest_relations_valid(fixture, REPO_ROOT))

    def test_symbolic_link_manifest_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="frp-m18-manifest-link-") as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "link.json"
            link.symlink_to(target.name)
            fixture = copy.deepcopy(self.manifest)
            fixture["artifacts"][0]["repository_path"] = "link.json"
            self.assertFalse(manifest_relations_valid(fixture, root))


class M18QualificationRecordTests(unittest.TestCase):
    """Validate exact qualification checks, bindings, aggregates, and bytes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = producer.RepositoryContext(REPO_ROOT)
        cls.raw = repository_file(QUALIFICATION_PATH).read_bytes()
        cls.qualification = strict_json_bytes(cls.raw)

    def test_qualification_identity_schema_and_bindings_are_exact(self) -> None:
        self.context.validate(
            "frp.m18.canonical_artifact_qualification.v2.0.0",
            self.qualification,
            QUALIFICATION_PATH,
        )
        expected = {
            "schema": "frp.m18.canonical_artifact_qualification.v2.0.0",
            "kind": "canonical_artifact_qualification",
            "version": M18_VERSION,
            "milestone": M18_MILESTONE,
            "producer": M18_PRODUCER,
            "producer_version": M18_VERSION,
            "upstream_release": "FRP v1.8.0 / M16",
            "registry_path": REGISTRY_PATH,
            "manifest_path": MANIFEST_PATH,
            "check_order": "category_check_id_subject_path",
            "check_count": 187,
            "passed_count": 187,
            "failed_count": 0,
            "warning_count": 0,
            "not_evaluated_count": 0,
            "overall_status": "PASS",
        }
        for field, value in expected.items():
            self.assertEqual(self.qualification[field], value)
        self.assertEqual(
            self.qualification["registry_sha256"],
            sha256_bytes(repository_file(REGISTRY_PATH).read_bytes()),
        )
        self.assertEqual(
            self.qualification["manifest_sha256"],
            sha256_bytes(repository_file(MANIFEST_PATH).read_bytes()),
        )
        manifest = strict_json_bytes(repository_file(MANIFEST_PATH).read_bytes())
        self.assertEqual(
            self.qualification["artifact_set_sha256"],
            manifest["artifact_set_sha256"],
        )

    def test_qualification_check_ids_categories_order_and_aggregates_are_exact(self) -> None:
        checks = self.qualification["checks"]
        keys = [
            (
                check["category"],
                check["check_id"],
                "" if check["subject_path"] is None else check["subject_path"],
            )
            for check in checks
        ]
        pairs = [(check["check_id"], check["subject_path"]) for check in checks]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(tuple(sorted({check["category"] for check in checks})), QUALIFICATION_CATEGORIES)
        self.assertEqual(tuple(sorted({check["check_id"] for check in checks})), QUALIFICATION_CHECK_IDS)
        self.assertTrue(all(check["outcome"] == "PASS" for check in checks))
        self.assertTrue(all(check["severity"] == "INFO" for check in checks))
        self.assertTrue(aggregate_valid(checks, self.qualification))

    def test_qualification_serialization_and_repeated_output_are_identical(self) -> None:
        self.assertEqual(self.raw, canonical_json_bytes(self.qualification))
        cache = determinism_cache()
        self.assertEqual(cache["qualification_a"].stderr, b"")
        self.assertEqual(cache["qualification_b"].stderr, b"")
        self.assertEqual(cache["qualification_a"].stdout, cache["qualification_b"].stdout)
        self.assertEqual(cache["qualification_a"].stdout, self.raw)
        self.assertEqual(cache["verification"].stdout, self.raw)

    def test_inconsistent_check_vector_and_aggregate_are_rejected(self) -> None:
        fixture = copy.deepcopy(self.qualification)
        fixture["checks"][0]["outcome"] = "FAIL"
        fixture["checks"][0]["severity"] = "ERROR"
        self.assertFalse(aggregate_valid(fixture["checks"], fixture))
        fixture = copy.deepcopy(self.qualification)
        fixture["passed_count"] = 186
        fixture["failed_count"] = 1
        self.assertFalse(aggregate_valid(fixture["checks"], fixture))


class M18SelfTestRecordTests(unittest.TestCase):
    """Validate the independent 34-case self-test CLI record."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = producer.RepositoryContext(REPO_ROOT)
        cls.committed_raw = repository_file(SELF_TEST_PATH).read_bytes()
        cls.committed = strict_json_bytes(cls.committed_raw)

    def test_self_test_cli_json_matches_committed_record_byte_for_byte(self) -> None:
        completed = determinism_cache()["self_test_a"]
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr, b"")
        self.assertEqual(completed.stdout, self.committed_raw)
        payload = strict_json_bytes(completed.stdout)
        self.context.validate(
            "frp.m18.canonical_artifact_self_test.v2.0.0",
            payload,
            SELF_TEST_PATH,
        )

    def test_self_test_root_cases_order_counts_and_statuses_are_exact(self) -> None:
        payload = self.committed
        self.assertEqual(set(payload), SELF_TEST_ROOT_FIELDS)
        expected = {
            "schema": "frp.m18.canonical_artifact_self_test.v2.0.0",
            "kind": "canonical_artifact_self_test",
            "version": M18_VERSION,
            "milestone": M18_MILESTONE,
            "producer": M18_PRODUCER,
            "producer_version": M18_VERSION,
            "upstream_release": "FRP v1.8.0 / M16",
            "profile": "m18_canonical_artifact_publication",
            "case_order": "case_id_lexicographic",
            "case_count": 34,
            "passed_count": 34,
            "failed_count": 0,
            "overall_status": "PASS",
        }
        for field, value in expected.items():
            self.assertEqual(payload[field], value)
        identifiers = tuple(case["case_id"] for case in payload["cases"])
        self.assertEqual(identifiers, SELF_TEST_CASE_IDS)
        self.assertEqual(identifiers, tuple(sorted(identifiers)))
        self.assertEqual(len(set(identifiers)), 34)
        self.assertTrue(all(case["status"] == "PASS" for case in payload["cases"]))
        self.assertEqual(self.committed_raw, canonical_json_bytes(payload))

    def test_repeated_self_test_output_is_byte_identical(self) -> None:
        cache = determinism_cache()
        self.assertEqual(cache["self_test_a"].stdout, cache["self_test_b"].stdout)
        self.assertEqual(cache["self_test_b"].stdout, self.committed_raw)


class M18DeterminismTests(unittest.TestCase):
    """Validate two independent generated trees and committed byte equality."""

    def test_two_generated_trees_have_exact_identical_path_sets(self) -> None:
        cache = determinism_cache()
        first = cache["first_files"]
        second = cache["second_files"]
        self.assertEqual(tuple(sorted(first)), GENERATED_PATHS)
        self.assertEqual(tuple(sorted(second)), GENERATED_PATHS)
        self.assertEqual(len(first), 36)
        self.assertEqual(len(second), 36)
        self.assertEqual(set(first), set(second))

    def test_two_generated_trees_are_byte_and_digest_identical(self) -> None:
        cache = determinism_cache()
        first = cache["first_files"]
        second = cache["second_files"]
        for path in GENERATED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(len(first[path]), len(second[path]))
                self.assertEqual(first[path], second[path])
                self.assertEqual(sha256_bytes(first[path]), sha256_bytes(second[path]))

    def test_every_generated_file_matches_committed_bytes(self) -> None:
        first = determinism_cache()["first_files"]
        for path in GENERATED_PATHS:
            with self.subTest(path=path):
                committed = repository_file(path).read_bytes()
                self.assertEqual(first[path], committed)
                self.assertEqual(sha256_bytes(first[path]), sha256_bytes(committed))

    def test_generation_reports_exact_thirty_six_paths(self) -> None:
        cache = determinism_cache()
        for key in ("generation_a", "generation_b"):
            completed = cache[key]
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, b"")
            report = strict_json_bytes(completed.stdout)
            self.assertEqual(report["overall_status"], "PASS")
            self.assertEqual(report["generated_file_count"], 36)
            self.assertEqual(tuple(report["paths"]), GENERATED_PATHS)

    def test_repository_boundary_bytes_remain_unchanged(self) -> None:
        determinism_cache()
        self.assertEqual(snapshot(_BOUNDARY_PATHS), _INITIAL_BOUNDARY_SNAPSHOT)


class M18SecurityBoundaryTests(unittest.TestCase):
    """Validate path, parsing, schema, execution, and write safety boundaries."""

    def test_parent_absolute_backslash_and_unregistered_targets_are_rejected(self) -> None:
        for value in ("../escape", "a/../escape", "/absolute", "a\\escape"):
            with self.subTest(value=value):
                self.assertFalse(independent_safe_path(value))
                with self.assertRaises(producer.SafetyError):
                    producer.safe_relative_path(value)
        with tempfile.TemporaryDirectory(prefix="frp-m18-target-") as temporary:
            with self.assertRaises(producer.SafetyError):
                producer._preflight_target(Path(temporary), "unregistered/file.json")

    def test_symbolic_link_source_and_output_targets_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="frp-m18-link-") as temporary:
            root = Path(temporary).resolve()
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "link.json"
            link.symlink_to(target.name)
            with self.assertRaises(producer.SafetyError):
                producer.source_file(root, "link.json")
            output = root / "output"
            output.mkdir()
            registered = output / "artifacts"
            registered.symlink_to(root, target_is_directory=True)
            with self.assertRaises(producer.SafetyError):
                producer._preflight_target(
                    output,
                    "artifacts/m18/structured_output/structured-output.json",
                )

    def test_artifact_values_cannot_select_executable_or_command_options(self) -> None:
        source = PRODUCER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        subprocess_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        ]
        self.assertEqual(len(subprocess_calls), 1)
        call = subprocess_calls[0]
        shell_keywords = [keyword for keyword in call.keywords if keyword.arg == "shell"]
        self.assertEqual(len(shell_keywords), 1)
        self.assertIsInstance(shell_keywords[0].value, ast.Constant)
        self.assertIs(shell_keywords[0].value.value, False)
        self.assertIn("command = [sys.executable, str(producer), *arguments]", source)
        self.assertNotIn("shell=True", source.replace(" ", ""))
        self.assertNotIn("os.system", source)

    def test_remote_refs_executable_deserialization_and_nonfinite_json_are_rejected(self) -> None:
        with self.assertRaises(producer.ContractError):
            producer.RepositoryContext._validate_refs(
                {"$ref": "https://example.invalid/remote.schema.json"},
                "remote",
            )
        for raw_bytes in (
            b"cos\nsystem\n(S'echo prohibited'\ntR.",
            b'{"value":NaN}\n',
            b'{"value":Infinity}\n',
            b'{"value":1,"value":2}\n',
        ):
            with self.subTest(raw_bytes=raw_bytes):
                with self.assertRaises(producer.ContractError):
                    producer.parse_json_bytes(raw_bytes, "security fixture")
        imports = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(ast.parse(PRODUCER_PATH.read_text(encoding="utf-8")))
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue({"pickle", "marshal", "yaml"}.isdisjoint(imports))

    def test_environment_dependent_fields_and_absolute_paths_are_rejected(self) -> None:
        valid = {"schema": "frp.example.v1", "repository_path": "a/b.json"}
        self.assertTrue(environment_fields_absent(valid))
        fixtures = (
            {"timestamp": "2026-01-01T00:00:00Z"},
            {"hostname": "runner"},
            {"output_path": "/tmp/environment-dependent"},
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertFalse(environment_fields_absent(fixture))
                self.assertFalse(producer._environment_fields_absent(fixture))

    def test_failure_preserves_repository_and_leaves_no_partial_output(self) -> None:
        before = snapshot(_BOUNDARY_PATHS)
        with tempfile.TemporaryDirectory(prefix="frp-m18-failure-") as temporary:
            output_root = Path(temporary) / "publication"
            sentinel = Path(temporary) / "outside-sentinel"
            sentinel.write_bytes(b"unchanged\n")
            files = {path: b"fixture\n" for path in GENERATED_PATHS}
            files.pop(GENERATED_PATHS[0])
            with self.assertRaises(producer.SafetyError):
                producer.publish_files(output_root, files, replace=False)
            self.assertFalse(output_root.exists())
            self.assertEqual(sentinel.read_bytes(), b"unchanged\n")
        self.assertEqual(snapshot(_BOUNDARY_PATHS), before)

    def test_producer_contains_no_systemverilog_or_network_execution_path(self) -> None:
        source = PRODUCER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_roots = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue(
            {
                "socket",
                "urllib",
                "requests",
                "httpx",
                "aiohttp",
            }.isdisjoint(imported_roots)
        )
        self.assertNotIn(".sv", source)
        self.assertNotIn("iverilog", source)
        self.assertNotIn("verilator", source)


if __name__ == "__main__":
    unittest.main()
