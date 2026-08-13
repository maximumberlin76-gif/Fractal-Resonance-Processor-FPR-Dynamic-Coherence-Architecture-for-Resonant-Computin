#!/usr/bin/env python3
"""Generate and validate the deterministic FRP M18 canonical artifact set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError as JsonSchemaError
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource


VERSION = "2.0.0"
MILESTONE = "M18 — Formal Schema and Canonical Artifact Publication"
UPSTREAM_RELEASE = "FRP v1.8.0 / M16"
PRODUCER = "frp_m18_canonical_artifacts.py"
SEMANTIC_REFERENCE = "frp_prototype_v1_7_0.py"
SEMANTIC_REFERENCE_VERSION = "1.7.0"
M15_MILESTONE = (
    "M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package"
)

REGISTRY_PATH = "schemas/m18/frp_m18_schema_registry.json"
MANIFEST_PATH = "artifacts/m18/manifests/canonical-artifact-manifest.json"
QUALIFICATION_PATH = (
    "artifacts/m18/manifests/canonical-artifact-qualification.json"
)
SELF_TEST_PATH = "artifacts/m18/manifests/canonical-artifact-self-test.json"

MANIFEST_SCHEMA = "frp.m18.canonical_artifact_manifest.v2.0.0"
QUALIFICATION_SCHEMA = "frp.m18.canonical_artifact_qualification.v2.0.0"
SELF_TEST_SCHEMA = "frp.m18.canonical_artifact_self_test.v2.0.0"
REGISTRY_SCHEMA = "frp.m18.formal_schema_registry.v2.0.0"
STRUCTURED_SCHEMA = "frp.structured_output.v1.7.0"
BENCHMARK_MATRIX_SCHEMA = "frp.m3.benchmark_matrix.v1.7.0"
BENCHMARK_CSV_IDENTITY = "frp.m3.benchmark_matrix.csv.v1.7.0"
VECTOR_FORMAT = "frp.m15.vector.v1"

JSON_SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
SCHEMA_URN_PREFIX = "urn:frp:schema:"
REGISTRY_DIGEST_SCOPE = (
    "canonical_compact_json_without_registry_content_sha256"
)

STRUCTURED_COMMANDS: dict[str, tuple[str, ...]] = {
    "artifacts/m18/structured_output/structured-output.json": (
        "--mode",
        "demo",
        "--scheduler",
        "7/1",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/trace-free.json": (
        "--mode",
        "demo",
        "--scheduler",
        "free",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
        "--include-trace",
    ),
    "artifacts/m18/structured_output/trace-7-1.json": (
        "--mode",
        "demo",
        "--scheduler",
        "7/1",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
        "--include-trace",
    ),
    "artifacts/m18/structured_output/trace-1-7.json": (
        "--mode",
        "demo",
        "--scheduler",
        "1/7",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
        "--include-trace",
    ),
    "artifacts/m18/structured_output/self-test-default.json": (
        "--mode",
        "self-test",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/self-test-free.json": (
        "--mode",
        "self-test",
        "--scheduler",
        "free",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/self-test-7-1.json": (
        "--mode",
        "self-test",
        "--scheduler",
        "7/1",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/self-test-1-7.json": (
        "--mode",
        "self-test",
        "--scheduler",
        "1/7",
        "--cells",
        "16",
        "--steps",
        "64",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/scaling-8.json": (
        "--mode",
        "demo",
        "--scheduler",
        "7/1",
        "--cells",
        "8",
        "--steps",
        "16",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/scaling-16.json": (
        "--mode",
        "demo",
        "--scheduler",
        "7/1",
        "--cells",
        "16",
        "--steps",
        "16",
        "--seed",
        "76",
        "--output",
        "json",
    ),
    "artifacts/m18/structured_output/scaling-32.json": (
        "--mode",
        "demo",
        "--scheduler",
        "7/1",
        "--cells",
        "32",
        "--steps",
        "16",
        "--seed",
        "76",
        "--output",
        "json",
    ),
}

BENCHMARK_MATRIX_PATH = "artifacts/m18/benchmark_matrix/benchmark-matrix.json"
BENCHMARK_CSV_PATH = "artifacts/m18/tabular/benchmark-matrix.csv"
BENCHMARK_MATRIX_ARGS = ("--export-benchmark-matrix",)
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

M15_EXPORTS: dict[str, tuple[str, str]] = {
    "artifacts/m18/m15_exports/balanced-ternary-hardware-encoding-map.json": (
        "--export-balanced-ternary-hardware-encoding-map",
        "frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0",
    ),
    "artifacts/m18/m15_exports/cycle-exact-reference-trace.json": (
        "--export-cycle-exact-reference-trace",
        "frp.m15.cycle_exact_reference_trace.v1.7.0",
    ),
    "artifacts/m18/m15_exports/fixed-point-interface-profile.json": (
        "--export-fixed-point-interface-profile",
        "frp.m15.fixed_point_interface_profile.v1.7.0",
    ),
    "artifacts/m18/m15_exports/qualification-closure-manifest.json": (
        "--export-qualification-closure-manifest",
        "frp.m15.qualification_closure_manifest.v1.7.0",
    ),
    "artifacts/m18/m15_exports/quantized-reference-shadow-model.json": (
        "--export-quantized-reference-shadow-model",
        "frp.m15.quantized_reference_shadow_model.v1.7.0",
    ),
    "artifacts/m18/m15_exports/reference-rtl-equivalence-report.json": (
        "--export-reference-rtl-equivalence-report",
        "frp.m15.reference_rtl_equivalence_report.v1.7.0",
    ),
    "artifacts/m18/m15_exports/rtl-assertion-correlation-harness.json": (
        "--export-rtl-assertion-correlation-harness",
        "frp.m15.rtl_assertion_correlation_harness.v1.7.0",
    ),
    "artifacts/m18/m15_exports/rtl-comparison-vector-package.json": (
        "--export-rtl-comparison-vector-package",
        "frp.m15.rtl_comparison_vector_package.v1.7.0",
    ),
    "artifacts/m18/m15_exports/synthesizable-rtl-reference-core.json": (
        "--export-synthesizable-rtl-reference-core",
        "frp.m15.synthesizable_rtl_reference_core.v1.7.0",
    ),
    "artifacts/m18/m15_exports/systemverilog-testbench-interface-map.json": (
        "--export-systemverilog-testbench-interface-map",
        "frp.m15.systemverilog_testbench_interface_map.v1.7.0",
    ),
}

VECTOR_MEMBERS = (
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
VECTOR_PATHS = tuple(f"{VECTOR_DIRECTORY}/{name}" for name in VECTOR_MEMBERS)
HEADERED_VECTOR_BINDINGS: dict[str, tuple[str, str]] = {
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

COMPARATIVE_PATHS = (
    "benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json",
    "benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json",
    "benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json",
    "benchmarks/architecture_comparison/profiles/workload_profile_v1.json",
    "benchmarks/architecture_comparison/results/reference_comparison_seed_76.json",
    "benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json",
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

RAW_DIGEST_FIXTURE = b"FRP M18 raw-byte digest known vector\n"
RAW_DIGEST_EXPECTED = (
    "ec75f629cb37c604195eb70d49cb2f80e675976800bbf292be28b81e1d9d6d99"
)
ARTIFACT_SET_DIGEST_EXPECTED = (
    "f0f02e164f568d5e8da5b1d1b7f0b3b2b152e12d5aef42687e48fc2287db778e"
)

GENERATED_CORE_PATHS = tuple(
    sorted(
        set(STRUCTURED_COMMANDS)
        | {BENCHMARK_MATRIX_PATH, BENCHMARK_CSV_PATH}
        | set(M15_EXPORTS)
        | set(VECTOR_PATHS)
    )
)
GENERATED_PATHS = tuple(
    sorted(
        set(GENERATED_CORE_PATHS)
        | {MANIFEST_PATH, QUALIFICATION_PATH, SELF_TEST_PATH}
    )
)
WRITE_PREFIXES = (
    "artifacts/m18/structured_output/",
    "artifacts/m18/benchmark_matrix/",
    "artifacts/m18/m15_exports/",
    "artifacts/m18/m15_vectors/",
    "artifacts/m18/tabular/",
    "artifacts/m18/manifests/",
)


class M18Error(Exception):
    """Base exception carrying one public M18 exit code."""

    exit_code = 1


class ContractError(M18Error):
    """Raised for validation or qualification failures."""

    exit_code = 1


class ConfigurationError(M18Error):
    """Raised for invalid command-line or runtime configuration."""

    exit_code = 2


class UpstreamProducerError(M18Error):
    """Raised when the registered semantic-reference producer fails."""

    exit_code = 3


class SafetyError(M18Error):
    """Raised for filesystem or write-boundary violations."""

    exit_code = 4


class ContractArgumentParser(argparse.ArgumentParser):
    """Argument parser that maps all parser failures to exit code 2."""

    def error(self, message: str) -> None:
        raise ConfigurationError(message)


def sha256_bytes(raw_bytes: bytes) -> str:
    """Return the lowercase SHA-256 digest of exact source bytes."""

    return hashlib.sha256(raw_bytes).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize one deterministic M18 record as canonical pretty JSON."""

    try:
        text = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise ContractError("canonical JSON contains an unsupported value") from error
    return (text + "\n").encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    """Serialize one value with the compact digest scope used by FRP."""

    try:
        text = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise ContractError("compact JSON contains an unsupported value") from error
    return text.encode("utf-8")


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is prohibited: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def parse_json_bytes(
    raw_bytes: bytes,
    subject: str,
    *,
    root_type: type | tuple[type, ...] = dict,
) -> Any:
    """Parse strict UTF-8 JSON while preserving the separate raw bytes."""

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError(f"{subject}: invalid UTF-8 JSON") from error
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except (TypeError, ValueError, json.JSONDecodeError) as error:
        raise ContractError(f"{subject}: malformed JSON") from error
    if not isinstance(value, root_type):
        raise ContractError(f"{subject}: unexpected JSON root type")
    return value


def _require_direct_producer_json(raw_bytes: bytes, subject: str) -> dict[str, Any]:
    value = parse_json_bytes(raw_bytes, subject)
    if raw_bytes != canonical_json_bytes(value):
        raise ContractError(f"{subject}: producer JSON serialization is not canonical")
    return value


def safe_relative_path(value: str, field_name: str = "repository_path") -> PurePosixPath:
    """Validate one safe, repository-relative, case-sensitive POSIX path."""

    if not isinstance(value, str) or not value or value != value.strip():
        raise SafetyError(f"{field_name} must be a non-empty stripped string")
    if "\\" in value or "\x00" in value or value.endswith("/"):
        raise SafetyError(f"{field_name} must be a safe POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SafetyError(f"{field_name} must be a safe POSIX relative path")
    return path


def _contains_path(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _reject_symlink_components(path: Path, stop: Path | None = None) -> None:
    current = path
    while True:
        if current.exists() and current.is_symlink():
            raise SafetyError("symbolic-link path components are prohibited")
        if stop is not None and current == stop:
            return
        if current.parent == current:
            return
        current = current.parent


def repository_root(path: str | Path) -> Path:
    raw = Path(path).expanduser().absolute()
    if raw.is_symlink():
        raise SafetyError("repository root must not be a symbolic link")
    try:
        resolved = raw.resolve(strict=True)
    except OSError as error:
        raise ConfigurationError("repository root does not exist") from error
    if not resolved.is_dir():
        raise ConfigurationError("repository root must be a directory")
    return resolved


def source_file(root: Path, relative_path: str) -> Path:
    relative = safe_relative_path(relative_path)
    candidate = root.joinpath(*relative.parts)
    _reject_symlink_components(candidate, root)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ContractError(f"required file is missing: {relative_path}") from error
    if not _contains_path(root, resolved) or not resolved.is_file():
        raise SafetyError(f"registered file is not a regular repository file: {relative_path}")
    return resolved


def _output_root(path: str | Path, root: Path, replace: bool) -> Path:
    raw = Path(path).expanduser().absolute()
    _reject_symlink_components(raw)
    if raw.exists() and not raw.is_dir():
        raise SafetyError("output root must be a directory")
    try:
        raw.mkdir(parents=True, exist_ok=True)
        resolved = raw.resolve(strict=True)
    except OSError as error:
        raise SafetyError("output root cannot be created safely") from error
    filesystem_root = Path(resolved.anchor)
    home = Path.home().resolve()
    if resolved == filesystem_root or resolved == home:
        raise SafetyError("filesystem root and user home cannot be output roots")
    if resolved == root:
        if not replace:
            raise SafetyError("publishing into the repository requires --replace")
    elif _contains_path(root, resolved) or _contains_path(resolved, root):
        raise SafetyError("output root must not overlap the repository root")
    return resolved


def _runtime_contract() -> None:
    if sys.version_info[:2] != (3, 12):
        raise ConfigurationError("M18 requires Python 3.12")
    try:
        installed = importlib.metadata.version("jsonschema")
    except importlib.metadata.PackageNotFoundError as error:
        raise ConfigurationError("jsonschema==4.25.1 is required") from error
    if installed != "4.25.1":
        raise ConfigurationError("jsonschema==4.25.1 is required")


def _command_text(arguments: Sequence[str]) -> str:
    return "python " + SEMANTIC_REFERENCE + " " + " ".join(arguments)


def _run_producer(root: Path, arguments: Sequence[str]) -> bytes:
    producer = source_file(root, SEMANTIC_REFERENCE)
    command = [sys.executable, str(producer), *arguments]
    try:
        completed = subprocess.run(
            command,
            cwd=root,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise UpstreamProducerError("registered upstream producer could not start") from error
    if completed.returncode != 0:
        diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {diagnostic}" if diagnostic else ""
        raise UpstreamProducerError(
            f"registered upstream producer returned {completed.returncode}{suffix}"
        )
    if not completed.stdout:
        raise UpstreamProducerError("registered upstream producer emitted no artifact bytes")
    return completed.stdout


def _deny_remote_retrieval(uri: str) -> Resource[Any]:
    raise NoSuchResource(ref=uri)


class RepositoryContext:
    """Validated immutable registry, formal-schema, and source-artifact view."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.registry_raw = source_file(root, REGISTRY_PATH).read_bytes()
        self.registry = parse_json_bytes(self.registry_raw, REGISTRY_PATH)
        self.records = self._validate_registry_structure()
        self.schemas: dict[str, dict[str, Any]] = {}
        self.schema_paths: dict[str, str] = {}
        resources: list[tuple[str, Resource[Any]]] = []
        seen_ids: set[str] = set()
        seen_paths: set[str] = set()

        for record in self.records:
            identifier = record["schema_identifier"]
            schema_path = record["schema_path"]
            if identifier in seen_ids or schema_path in seen_paths:
                raise ContractError("registry schema identifiers and paths must be unique")
            seen_ids.add(identifier)
            seen_paths.add(schema_path)
            raw = source_file(root, schema_path).read_bytes()
            schema = parse_json_bytes(raw, schema_path)
            expected_urn = SCHEMA_URN_PREFIX + identifier
            if schema.get("$schema") != JSON_SCHEMA_DIALECT:
                raise ContractError(f"{schema_path}: JSON Schema dialect mismatch")
            if schema.get("$id") != expected_urn:
                raise ContractError(f"{schema_path}: formal schema $id mismatch")
            if schema.get("x-frp-schema-identifier") != identifier:
                raise ContractError(f"{schema_path}: FRP schema identity mismatch")
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as error:
                raise ContractError(f"{schema_path}: invalid Draft 2020-12 schema") from error
            self._validate_refs(schema, schema_path)
            self.schemas[identifier] = schema
            self.schema_paths[identifier] = schema_path
            resources.append((expected_urn, Resource.from_contents(schema)))

        if tuple(sorted(seen_ids)) != EXPECTED_SCHEMA_IDENTIFIERS:
            raise ContractError("registry does not contain the exact M18 schema set")
        self.resource_registry = Registry(
            retrieve=_deny_remote_retrieval
        ).with_resources(resources)
        self.validators = {
            identifier: Draft202012Validator(
                schema,
                registry=self.resource_registry,
            )
            for identifier, schema in self.schemas.items()
        }
        self.validate(REGISTRY_SCHEMA, self.registry, REGISTRY_PATH)
        for path in COMPARATIVE_PATHS:
            source_file(root, path)

    def _validate_registry_structure(self) -> list[dict[str, Any]]:
        registry = self.registry
        exact = {
            "schema": REGISTRY_SCHEMA,
            "kind": "formal_schema_registry",
            "version": VERSION,
            "milestone": MILESTONE,
            "json_schema_dialect": JSON_SCHEMA_DIALECT,
            "record_order": "schema_identifier_lexicographic",
            "registry_digest_scope": REGISTRY_DIGEST_SCOPE,
            "schema_count": 24,
        }
        for field, expected in exact.items():
            if registry.get(field) != expected:
                raise ContractError(f"{REGISTRY_PATH}: {field} mismatch")
        records = registry.get("records")
        if not isinstance(records, list) or len(records) != 24:
            raise ContractError(f"{REGISTRY_PATH}: exactly 24 records are required")
        identifiers = [record.get("schema_identifier") for record in records]
        if identifiers != sorted(identifiers) or len(set(identifiers)) != 24:
            raise ContractError(f"{REGISTRY_PATH}: record order or uniqueness failure")
        digest_source = dict(registry)
        declared_digest = digest_source.pop("registry_content_sha256", None)
        observed_digest = sha256_bytes(compact_json_bytes(digest_source))
        if declared_digest != observed_digest:
            raise ContractError(f"{REGISTRY_PATH}: registry content digest mismatch")
        return records

    @staticmethod
    def _validate_refs(value: Any, subject: str) -> None:
        if isinstance(value, dict):
            reference = value.get("$ref")
            if reference is not None and (
                not isinstance(reference, str) or not reference.startswith("#")
            ):
                raise ContractError(f"{subject}: only internal $ref values are permitted")
            for child in value.values():
                RepositoryContext._validate_refs(child, subject)
        elif isinstance(value, list):
            for child in value:
                RepositoryContext._validate_refs(child, subject)

    def validate(self, identifier: str, instance: Any, subject: str) -> None:
        validator = self.validators.get(identifier)
        if validator is None:
            raise ContractError(f"{subject}: unregistered schema identifier {identifier}")
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda item: tuple(str(part) for part in item.absolute_path),
        )
        if errors:
            location = "/".join(str(part) for part in errors[0].path) or "$"
            raise ContractError(
                f"{subject}: formal schema validation failed at {location}: "
                f"{errors[0].message}"
            )

    def record_for_path(self, repository_path: str) -> dict[str, Any] | None:
        matches = [
            record
            for record in self.records
            if repository_path in record.get("canonical_artifact_paths", [])
        ]
        if len(matches) > 1:
            raise ContractError(f"{repository_path}: duplicate registry path binding")
        return matches[0] if matches else None


def benchmark_csv_bytes(matrix: Mapping[str, Any]) -> bytes:
    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 5:
        raise ContractError("benchmark matrix must contain exactly five rows")
    buffer = io.StringIO(newline="")
    writer = csv.writer(
        buffer,
        delimiter=",",
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )
    writer.writerow(BENCHMARK_COLUMNS)
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError("benchmark matrix row must be an object")
        values: list[str] = []
        for column in BENCHMARK_COLUMNS:
            if column not in row:
                values.append("")
                continue
            value = row[column]
            if isinstance(value, bool):
                values.append("true" if value else "false")
            elif value is None:
                raise ContractError("present benchmark CSV source values must not be null")
            elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
                if isinstance(value, float) and not math.isfinite(value):
                    raise ContractError("benchmark CSV source values must be finite")
                values.append(str(value))
            else:
                raise ContractError("benchmark CSV source value has unsupported type")
        writer.writerow(values)
    return buffer.getvalue().encode("utf-8")


def _expected_structured_inputs(path: str) -> tuple[str, int, int, str, bool]:
    arguments = STRUCTURED_COMMANDS[path]
    mode = arguments[arguments.index("--mode") + 1]
    cells = int(arguments[arguments.index("--cells") + 1])
    steps = int(arguments[arguments.index("--steps") + 1])
    scheduler = (
        arguments[arguments.index("--scheduler") + 1]
        if "--scheduler" in arguments
        else "7/1"
    )
    return mode, cells, steps, scheduler, "--include-trace" in arguments


def _validate_trace_digest(payload: Mapping[str, Any], field: str, value: str) -> None:
    if field not in payload or payload.get(value) != sha256_bytes(
        compact_json_bytes(payload[field]) + b"\n"
    ):
        raise ContractError(f"structured output {value} mismatch")


def _scheduler_sequence_valid(mode: str, states: Sequence[str]) -> bool:
    if mode == "free":
        return bool(states) and all(state == "free" for state in states)
    if mode == "7/1":
        expected = tuple("commit" if index % 8 == 7 else "balance" for index in range(len(states)))
        return tuple(states) == expected
    if mode == "1/7":
        expected = tuple("excite" if index % 8 == 0 else "neutralize" for index in range(len(states)))
        return tuple(states) == expected
    return False


def _validate_structured(path: str, payload: Mapping[str, Any]) -> None:
    mode, cells, steps, scheduler, include_trace = _expected_structured_inputs(path)
    if payload.get("schema") != STRUCTURED_SCHEMA or payload.get("version") != "1.7.0":
        raise ContractError(f"{path}: structured-output identity mismatch")
    if payload.get("milestone") != M15_MILESTONE:
        raise ContractError(f"{path}: structured-output milestone mismatch")
    if mode == "self-test":
        checks = payload.get("checks")
        if (
            payload.get("kind") != "self_test"
            or payload.get("status") != "PASS"
            or payload.get("check_count") != 41
            or not isinstance(checks, dict)
            or len(checks) != 41
            or not all(value is True for value in checks.values())
        ):
            raise ContractError(f"{path}: canonical self-test relation failure")
        return

    configuration = payload.get("configuration")
    summary = payload.get("summary")
    if not isinstance(configuration, dict) or not isinstance(summary, dict):
        raise ContractError(f"{path}: missing demo configuration or summary")
    expected_configuration = {
        "cells": cells,
        "steps": steps,
        "scheduler": scheduler,
        "seed": 76,
    }
    if any(configuration.get(key) != value for key, value in expected_configuration.items()):
        raise ContractError(f"{path}: fixed producer input mismatch")
    required_summary = {
        "actual_direct_events": 0,
        "reserved_state_events": 0,
        "queue_overflow_events": 0,
        "cells": cells,
        "steps": steps,
        "scheduler": scheduler,
        "scheduler_counts_valid": True,
        "balanced_ternary_state_domain": True,
    }
    if any(summary.get(key) != value for key, value in required_summary.items()):
        raise ContractError(f"{path}: invariant summary mismatch")

    trace_fields = {"trace", "cell_trace", "route_events"}
    if include_trace:
        if not trace_fields.issubset(payload):
            raise ContractError(f"{path}: full trace fields are missing")
        trace = payload["trace"]
        cell_trace = payload["cell_trace"]
        routes = payload["route_events"]
        if not isinstance(trace, list) or len(trace) != steps:
            raise ContractError(f"{path}: tick trace length mismatch")
        if not isinstance(cell_trace, list) or len(cell_trace) != cells * steps:
            raise ContractError(f"{path}: cell trace length mismatch")
        if not isinstance(routes, list):
            raise ContractError(f"{path}: route-event collection is invalid")
        ticks = [record.get("tick") for record in trace if isinstance(record, dict)]
        if ticks != list(range(steps)):
            raise ContractError(f"{path}: tick ordering mismatch")
        cell_order = [
            (record.get("tick"), record.get("cell_id"))
            for record in cell_trace
            if isinstance(record, dict)
        ]
        expected_order = [(tick, cell) for tick in range(steps) for cell in range(cells)]
        if cell_order != expected_order:
            raise ContractError(f"{path}: cell trace ordering mismatch")
        states = [record.get("scheduler_state_name") for record in trace]
        if not _scheduler_sequence_valid(scheduler, states):
            raise ContractError(f"{path}: scheduler state sequence mismatch")
        for route in routes:
            if (
                not isinstance(route, dict)
                or not ternary_value_valid(route.get("target_state"))
                or route.get("route_status") not in {"pending", "applied"}
                or not isinstance(route.get("tick"), int)
            ):
                raise ContractError(f"{path}: pending-route relation mismatch")
        _validate_trace_digest(payload, "trace", "trace_digest")
        _validate_trace_digest(payload, "cell_trace", "cell_trace_digest")
    elif trace_fields.intersection(payload):
        raise ContractError(f"{path}: trace-free output contains full trace fields")


def _parse_header(raw_bytes: bytes, subject: str) -> dict[str, Any]:
    try:
        lines = raw_bytes.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ContractError(f"{subject}: invalid UTF-8 vector") from error
    headers: dict[str, Any] = {}
    for line in lines:
        if not line.startswith("#"):
            break
        content = line[1:].strip()
        if "=" not in content:
            continue
        key, raw_value = content.split("=", 1)
        key = key.strip()
        if key in headers:
            raise ContractError(f"{subject}: duplicate vector header {key}")
        try:
            headers[key] = json.loads(raw_value)
        except json.JSONDecodeError as error:
            raise ContractError(f"{subject}: malformed vector header {key}") from error
    return headers


def ternary_value_valid(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value in {-1, 0, 1}


def _packed_states_match(states: Sequence[Any], packed_hex: Any) -> bool:
    if not isinstance(packed_hex, str) or not re.fullmatch(r"[0-9A-F]+", packed_hex):
        return False
    if not all(ternary_value_valid(state) for state in states):
        return False
    mapping = {-1: 3, 0: 0, 1: 1}
    packed = int(packed_hex, 16)
    if packed >> (2 * len(states)):
        return False
    return all(((packed >> (2 * index)) & 3) == mapping[state] for index, state in enumerate(states))


def _validate_vector_package(core: Mapping[str, bytes]) -> None:
    member_bytes = {
        PurePosixPath(path).name: core[path]
        for path in VECTOR_PATHS
    }
    if tuple(sorted(member_bytes)) != VECTOR_MEMBERS:
        raise ContractError("M15 vector package member set mismatch")

    for filename, (trace_kind, scheduler) in HEADERED_VECTOR_BINDINGS.items():
        headers = _parse_header(member_bytes[filename], filename)
        required = {
            "format_version": VECTOR_FORMAT,
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
        if any(headers.get(key) != value for key, value in required.items()):
            raise ContractError(f"{filename}: header binding mismatch")

    preload = parse_json_bytes(
        member_bytes["frp_m15_reference_preload.json"],
        "frp_m15_reference_preload.json",
    )
    states = preload.get("states")
    if (
        preload.get("cells") != 16
        or preload.get("seed") != 76
        or preload.get("scheduler") != "7/1"
        or not isinstance(states, list)
        or len(states) != 16
        or not _packed_states_match(states, preload.get("states_packed_hex"))
    ):
        raise ContractError("M15 reference preload mapping mismatch")
    array_fields = (
        "frequency_current_q16",
        "frequency_target_q16",
        "gamma_noise_state_q16",
        "gamma_noise_target_q16",
        "heat_q16",
        "phase_words",
        "states",
    )
    if any(
        not isinstance(preload.get(field), list) or len(preload[field]) != 16
        for field in array_fields
    ):
        raise ContractError("M15 reference preload array length mismatch")

    internal = parse_json_bytes(
        member_bytes["frp_m15_sha256_manifest.json"],
        "frp_m15_sha256_manifest.json",
    )
    expected_internal = {
        name: sha256_bytes(raw)
        for name, raw in sorted(member_bytes.items())
        if name != "frp_m15_sha256_manifest.json"
    }
    if internal != expected_internal:
        raise ContractError("M15 internal SHA-256 manifest mismatch")

    try:
        trig_lines = member_bytes["frp_m15_trig_lut_q30.vec"].decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ContractError("M15 trigonometric lookup table is not UTF-8") from error
    if trig_lines[:3] != [
        "# FRP v1.7.0 M15 deterministic trigonometric lookup table",
        "# entries=4096",
        "# format=index | sin_q30",
    ] or len(trig_lines[3:]) != 4096:
        raise ContractError("M15 trigonometric lookup-table structure mismatch")
    for index, line in enumerate(trig_lines[3:]):
        match = re.fullmatch(r"([0-9A-F]{4}) \| (-?[0-9]+)", line)
        if match is None or int(match.group(1), 16) != index:
            raise ContractError("M15 trigonometric lookup-table ordering mismatch")

    descriptor_path = (
        "artifacts/m18/m15_exports/rtl-comparison-vector-package.json"
    )
    descriptor = parse_json_bytes(core[descriptor_path], descriptor_path)
    expected_files = [
        {
            "name": name,
            "sha256": sha256_bytes(member_bytes[name]),
            "size_bytes": len(member_bytes[name]),
        }
        for name in VECTOR_MEMBERS
    ]
    expected_package_digest = sha256_bytes(
        b"".join(name.encode("utf-8") + b"\0" + member_bytes[name] for name in VECTOR_MEMBERS)
    )
    if (
        descriptor.get("manifest")
        != {"file_count": 10, "files": expected_files}
        or descriptor.get("deterministic_package_digest") != expected_package_digest
        or expected_package_digest != VECTOR_PACKAGE_DIGEST
    ):
        raise ContractError("M15 vector-package descriptor binding mismatch")


def _validate_benchmark_matrix(payload: Mapping[str, Any]) -> None:
    rows = payload.get("rows")
    if (
        payload.get("schema") != BENCHMARK_MATRIX_SCHEMA
        or payload.get("kind") != "benchmark_matrix"
        or payload.get("version") != "1.7.0"
        or payload.get("milestone") != M15_MILESTONE
        or not isinstance(rows, list)
        or [row.get("architecture") for row in rows if isinstance(row, dict)]
        != list(BENCHMARK_ARCHITECTURES)
    ):
        raise ContractError("benchmark-matrix identity or row order mismatch")
    by_architecture = {row["architecture"]: row for row in rows}
    correlation = by_architecture["frp_v1_7_0_quantized_hardware_shadow"]
    if any(
        correlation.get(field) != 1.0
        for field in (
            "C_minus_P_sign_match",
            "scheduler_sequence_match",
            "state_sequence_match",
        )
    ):
        raise ContractError("benchmark-matrix correlation value mismatch")
    if (
        by_architecture["frp_v1_7_0_cycle_exact_vector_package"].get(
            "vector_repeat_match"
        )
        != 1.0
        or by_architecture["frp_v1_7_0_systemverilog_correlation_contract"].get(
            "comparison_rule"
        )
        != "actual == expected"
        or by_architecture["frp_v1_7_0_qualification_closure"].get(
            "artifact_layers"
        )
        != 10
    ):
        raise ContractError("benchmark-matrix recorded relation mismatch")


def _validate_m15_export(path: str, payload: Mapping[str, Any], schema: str) -> None:
    expected_kind = schema.split("frp.m15.", 1)[1].rsplit(".v1.7.0", 1)[0]
    if (
        payload.get("schema") != schema
        or payload.get("kind") != expected_kind
        or payload.get("version") != "1.7.0"
        or payload.get("milestone") != M15_MILESTONE
    ):
        raise ContractError(f"{path}: M15 export identity mismatch")
    if path.endswith("rtl-assertion-correlation-harness.json"):
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        if noncanonical_state_notation(text):
            raise ContractError(f"{path}: noncanonical positive-state notation")


def noncanonical_state_notation(text: str) -> bool:
    """Detect a prefixed positive state only when used as a standalone label."""

    return re.search(r"(?<![A-Za-z0-9_])\x2b1(?![A-Za-z0-9_])", text) is not None


def _validate_comparative(context: RepositoryContext) -> None:
    for path in COMPARATIVE_PATHS:
        raw = source_file(context.root, path).read_bytes()
        payload = parse_json_bytes(raw, path)
        record = context.record_for_path(path)
        if record is None:
            raise ContractError(f"{path}: comparative registry binding is missing")
        identifier = record["schema_identifier"]
        if record["identity_basis"] == "embedded_schema":
            if payload.get("schema") != identifier:
                raise ContractError(f"{path}: embedded schema identity mismatch")
        elif record["identity_basis"] != "registry_bound_exact_path_and_role":
            raise ContractError(f"{path}: unsupported comparative identity basis")
        context.validate(identifier, payload, path)
        for status_field in ("qualification", "integrity"):
            status = payload.get(status_field)
            if status is not None and (
                not isinstance(status, dict) or status.get("status") != "PASS"
            ):
                raise ContractError(f"{path}: recorded {status_field} status mismatch")


def generate_core(context: RepositoryContext) -> dict[str, bytes]:
    """Generate the 33 manifest-bound M18 outputs entirely off-tree."""

    core: dict[str, bytes] = {}
    for path, arguments in STRUCTURED_COMMANDS.items():
        core[path] = _run_producer(context.root, arguments)

    matrix_raw = _run_producer(context.root, BENCHMARK_MATRIX_ARGS)
    matrix = _require_direct_producer_json(matrix_raw, BENCHMARK_MATRIX_PATH)
    core[BENCHMARK_MATRIX_PATH] = matrix_raw
    core[BENCHMARK_CSV_PATH] = benchmark_csv_bytes(matrix)

    for path, (option, _schema) in M15_EXPORTS.items():
        core[path] = _run_producer(context.root, (option,))

    with tempfile.TemporaryDirectory(prefix="frp-m18-vectors-") as temporary:
        vector_root = Path(temporary)
        _run_producer(
            context.root,
            (
                "--export-rtl-comparison-vector-package",
                "--vector-output-dir",
                str(vector_root),
            ),
        )
        observed_names = tuple(
            sorted(path.name for path in vector_root.iterdir() if path.is_file())
        )
        if observed_names != VECTOR_MEMBERS:
            raise ContractError("upstream M15 vector package member set mismatch")
        if any(path.is_symlink() for path in vector_root.iterdir()):
            raise SafetyError("upstream M15 vector package contains a symbolic link")
        for name in VECTOR_MEMBERS:
            core[f"{VECTOR_DIRECTORY}/{name}"] = (vector_root / name).read_bytes()

    if tuple(sorted(core)) != GENERATED_CORE_PATHS:
        raise ContractError("generated M18 core path set mismatch")
    validate_core(context, core)
    return core


def validate_core(context: RepositoryContext, core: Mapping[str, bytes]) -> None:
    if tuple(sorted(core)) != GENERATED_CORE_PATHS:
        raise ContractError("canonical M18 core path set mismatch")

    for path in STRUCTURED_COMMANDS:
        payload = _require_direct_producer_json(core[path], path)
        context.validate(STRUCTURED_SCHEMA, payload, path)
        _validate_structured(path, payload)

    matrix = _require_direct_producer_json(
        core[BENCHMARK_MATRIX_PATH], BENCHMARK_MATRIX_PATH
    )
    context.validate(BENCHMARK_MATRIX_SCHEMA, matrix, BENCHMARK_MATRIX_PATH)
    _validate_benchmark_matrix(matrix)
    if core[BENCHMARK_CSV_PATH] != benchmark_csv_bytes(matrix):
        raise ContractError("benchmark-matrix CSV does not match source JSON")

    for path, (_option, schema) in M15_EXPORTS.items():
        payload = _require_direct_producer_json(core[path], path)
        context.validate(schema, payload, path)
        _validate_m15_export(path, payload, schema)

    preload_path = f"{VECTOR_DIRECTORY}/frp_m15_reference_preload.json"
    preload = parse_json_bytes(core[preload_path], preload_path)
    context.validate("frp.m15.reference_preload.v1.7.0", preload, preload_path)
    internal_path = f"{VECTOR_DIRECTORY}/frp_m15_sha256_manifest.json"
    internal = parse_json_bytes(core[internal_path], internal_path)
    context.validate("frp.m15.sha256_manifest.v1.7.0", internal, internal_path)
    _validate_vector_package(core)


def _artifact_set_digest(records: Sequence[Mapping[str, Any]]) -> str:
    if not records:
        raise ContractError("artifact-set digest requires at least one record")
    ordered = sorted(records, key=lambda record: record["repository_path"])
    material = b"".join(
        record["repository_path"].encode("utf-8")
        + b"\0"
        + record["sha256"].encode("ascii")
        + b"\0"
        + str(record["byte_length"]).encode("ascii")
        + b"\n"
        for record in ordered
    )
    return sha256_bytes(material)


def _manifest_path_set(context: RepositoryContext) -> tuple[str, ...]:
    formal_paths = tuple(sorted(record["schema_path"] for record in context.records))
    paths = tuple(
        sorted(
            set(GENERATED_CORE_PATHS)
            | set(COMPARATIVE_PATHS)
            | set(formal_paths)
            | {REGISTRY_PATH}
        )
    )
    if len(paths) != 64:
        raise ContractError("canonical artifact manifest must bind exactly 64 paths")
    if MANIFEST_PATH in paths or QUALIFICATION_PATH in paths or SELF_TEST_PATH in paths:
        raise ContractError("canonical artifact manifest contains a self-binding record")
    return paths


def _manifest_metadata(
    context: RepositoryContext,
    repository_path: str,
) -> dict[str, Any]:
    filename = PurePosixPath(repository_path).name
    record = context.record_for_path(repository_path)
    metadata: dict[str, Any] = {
        "repository_path": repository_path,
        "filename": filename,
        "canonical": True,
        "mutable": False,
    }

    if repository_path.startswith("schemas/m18/") and repository_path != REGISTRY_PATH:
        identifier = next(
            item["schema_identifier"]
            for item in context.records
            if item["schema_path"] == repository_path
        )
        metadata.update(
            artifact_class="formal_schema",
            format="json",
            schema_identifier=identifier,
            identification_basis="embedded_schema",
            producer=None,
            producer_version=None,
            measurement_contour="m18_canonical_artifact_publication",
        )
        return metadata

    if repository_path == REGISTRY_PATH:
        metadata.update(
            artifact_class="schema_registry",
            format="json",
            schema_identifier=REGISTRY_SCHEMA,
            identification_basis="embedded_schema",
            producer=PRODUCER,
            producer_version=VERSION,
            measurement_contour="m18_canonical_artifact_publication",
        )
        return metadata

    if repository_path in STRUCTURED_COMMANDS:
        arguments = STRUCTURED_COMMANDS[repository_path]
        metadata.update(
            artifact_class="structured_output",
            format="json",
            schema_identifier=STRUCTURED_SCHEMA,
            identification_basis="embedded_schema",
            producer=SEMANTIC_REFERENCE,
            producer_version=SEMANTIC_REFERENCE_VERSION,
            producer_command=_command_text(arguments),
            measurement_contour="m15_implementation_mapping_matrix",
        )
        return metadata

    if repository_path == BENCHMARK_MATRIX_PATH:
        metadata.update(
            artifact_class="benchmark_matrix_json",
            format="json",
            schema_identifier=BENCHMARK_MATRIX_SCHEMA,
            identification_basis="embedded_schema",
            producer=SEMANTIC_REFERENCE,
            producer_version=SEMANTIC_REFERENCE_VERSION,
            producer_command=_command_text(BENCHMARK_MATRIX_ARGS),
            measurement_contour="m15_implementation_mapping_matrix",
        )
        return metadata

    if repository_path == BENCHMARK_CSV_PATH:
        metadata.update(
            artifact_class="benchmark_matrix_csv",
            format="csv",
            schema_identifier=BENCHMARK_CSV_IDENTITY,
            identification_basis="registry_binding",
            producer=PRODUCER,
            producer_version=VERSION,
            measurement_contour="m15_implementation_mapping_matrix",
        )
        return metadata

    if repository_path in M15_EXPORTS:
        option, schema = M15_EXPORTS[repository_path]
        metadata.update(
            artifact_class="m15_export",
            format="json",
            schema_identifier=schema,
            identification_basis="embedded_schema",
            producer=SEMANTIC_REFERENCE,
            producer_version=SEMANTIC_REFERENCE_VERSION,
            producer_command=_command_text((option,)),
            measurement_contour="m15_implementation_mapping_matrix",
        )
        return metadata

    if repository_path in VECTOR_PATHS:
        if filename == "frp_m15_reference_preload.json":
            artifact_format = "json"
            identifier: str | None = "frp.m15.reference_preload.v1.7.0"
            basis = "registry_binding"
        elif filename == "frp_m15_sha256_manifest.json":
            artifact_format = "json"
            identifier = "frp.m15.sha256_manifest.v1.7.0"
            basis = "registry_binding"
        elif filename == "frp_m15_trig_lut_q30.vec":
            artifact_format = "vector_text"
            identifier = None
            basis = "package_role"
        else:
            artifact_format = (
                "headered_trace" if filename.endswith(".trace") else "headered_vector"
            )
            identifier = VECTOR_FORMAT
            basis = "format_header"
        metadata.update(
            artifact_class="m15_vector_member",
            format=artifact_format,
            schema_identifier=identifier,
            identification_basis=basis,
            producer=SEMANTIC_REFERENCE,
            producer_version=SEMANTIC_REFERENCE_VERSION,
            producer_command=(
                "python frp_prototype_v1_7_0.py "
                "--export-rtl-comparison-vector-package "
                "--vector-output-dir artifacts/m18/m15_vectors"
            ),
            measurement_contour="m15_implementation_mapping_matrix",
        )
        return metadata

    if repository_path in COMPARATIVE_PATHS and record is not None:
        basis = (
            "registry_binding"
            if record["identity_basis"] == "registry_bound_exact_path_and_role"
            else "embedded_schema"
        )
        metadata.update(
            artifact_class="comparative_benchmark",
            format="json",
            schema_identifier=record["schema_identifier"],
            identification_basis=basis,
            producer=record["producer_path"],
            producer_version=record["producer_version"],
            measurement_contour=record["measurement_contour"],
        )
        return metadata

    raise ContractError(f"{repository_path}: no manifest metadata binding")


def build_manifest(
    context: RepositoryContext,
    core: Mapping[str, bytes],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for path in _manifest_path_set(context):
        raw = core[path] if path in core else source_file(context.root, path).read_bytes()
        metadata = _manifest_metadata(context, path)
        metadata["byte_length"] = len(raw)
        metadata["sha256"] = sha256_bytes(raw)
        records.append(metadata)
    records.sort(key=lambda record: record["repository_path"])
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "kind": "canonical_artifact_manifest",
        "version": VERSION,
        "milestone": MILESTONE,
        "producer": PRODUCER,
        "producer_version": VERSION,
        "upstream_release": UPSTREAM_RELEASE,
        "artifact_order": "repository_path_lexicographic",
        "digest_algorithm": "sha256",
        "digest_scope": "raw_bytes",
        "artifact_count": len(records),
        "artifact_set_sha256": _artifact_set_digest(records),
        "artifacts": records,
    }
    context.validate(MANIFEST_SCHEMA, manifest, MANIFEST_PATH)
    return manifest


def _check(
    category: str,
    check_id: str,
    subject_path: str | None,
    passed: bool,
    expected: Any,
    observed: Any,
    message: str,
) -> dict[str, Any]:
    return {
        "category": category,
        "check_id": check_id,
        "subject_path": subject_path,
        "outcome": "PASS" if passed else "FAIL",
        "severity": "INFO" if passed else "ERROR",
        "expected": expected,
        "observed": observed,
        "message": message,
    }


def _snapshot(
    context: RepositoryContext,
    core: Mapping[str, bytes],
) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for path in _manifest_path_set(context):
        raw = core[path] if path in core else source_file(context.root, path).read_bytes()
        result[path] = (len(raw), sha256_bytes(raw))
    return result


def build_qualification(
    context: RepositoryContext,
    publication_core: Mapping[str, bytes],
    regenerated_a: Mapping[str, bytes],
    regenerated_b: Mapping[str, bytes],
    manifest: Mapping[str, Any],
    manifest_raw: bytes,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    before = _snapshot(context, publication_core)

    checks.append(
        _check(
            "registry",
            "exact_supported_schema_set",
            REGISTRY_PATH,
            tuple(record["schema_identifier"] for record in context.records)
            == EXPECTED_SCHEMA_IDENTIFIERS,
            list(EXPECTED_SCHEMA_IDENTIFIERS),
            [record["schema_identifier"] for record in context.records],
            "The registry contains the exact ordered M18 supported-schema set.",
        )
    )
    checks.append(
        _check(
            "registry",
            "registry_content_digest_valid",
            REGISTRY_PATH,
            True,
            True,
            True,
            "The registry compact-content digest is valid.",
        )
    )

    for identifier in EXPECTED_SCHEMA_IDENTIFIERS:
        path = context.schema_paths[identifier]
        schema = context.schemas[identifier]
        checks.append(
            _check(
                "formal_schema",
                "draft_2020_12_schema_valid",
                path,
                True,
                JSON_SCHEMA_DIALECT,
                schema["$schema"],
                "The registered formal schema is valid Draft 2020-12 JSON Schema.",
            )
        )
        checks.append(
            _check(
                "identity",
                "formal_schema_identity_exact",
                path,
                schema["$id"] == SCHEMA_URN_PREFIX + identifier,
                SCHEMA_URN_PREFIX + identifier,
                schema["$id"],
                "The formal schema identity matches its registry identifier.",
            )
        )

    core_path_set_valid = (
        tuple(sorted(publication_core))
        == tuple(sorted(regenerated_a))
        == tuple(sorted(regenerated_b))
        == GENERATED_CORE_PATHS
    )
    checks.append(
        _check(
            "publication_boundary",
            "generated_path_set_exact",
            None,
            core_path_set_valid,
            list(GENERATED_CORE_PATHS),
            sorted(publication_core),
            "The generated publication path set is closed and exact.",
        )
    )

    for path in GENERATED_CORE_PATHS:
        source_raw = publication_core.get(path, b"")
        first_raw = regenerated_a.get(path, b"")
        second_raw = regenerated_b.get(path, b"")
        checks.append(
            _check(
                "determinism",
                "independent_regeneration_byte_identical",
                path,
                first_raw == second_raw,
                sha256_bytes(first_raw),
                sha256_bytes(second_raw),
                "Two independent generations are byte-identical.",
            )
        )
        checks.append(
            _check(
                "digest",
                "publication_matches_regeneration",
                path,
                source_raw == first_raw,
                sha256_bytes(first_raw),
                sha256_bytes(source_raw),
                "The publication bytes match independent regeneration.",
            )
        )

    validation_passed = True
    validation_observed = "valid"
    try:
        validate_core(context, publication_core)
        _validate_comparative(context)
    except M18Error as error:
        validation_passed = False
        validation_observed = str(error)
    checks.append(
        _check(
            "structure",
            "canonical_artifact_relations_valid",
            None,
            validation_passed,
            "valid",
            validation_observed,
            "Canonical artifacts satisfy formal schemas and registered relations.",
        )
    )

    expected_manifest = build_manifest(context, publication_core)
    expected_manifest_raw = canonical_json_bytes(expected_manifest)
    checks.append(
        _check(
            "manifest",
            "manifest_regeneration_byte_identical",
            MANIFEST_PATH,
            manifest_raw == expected_manifest_raw,
            sha256_bytes(expected_manifest_raw),
            sha256_bytes(manifest_raw),
            "The canonical manifest matches independent reconstruction.",
        )
    )
    checks.append(
        _check(
            "manifest",
            "manifest_artifact_set_digest_valid",
            MANIFEST_PATH,
            manifest.get("artifact_set_sha256")
            == expected_manifest["artifact_set_sha256"],
            expected_manifest["artifact_set_sha256"],
            manifest.get("artifact_set_sha256"),
            "The manifest artifact-set digest matches exact source bytes.",
        )
    )
    checks.append(
        _check(
            "measurement_contour",
            "measurement_contours_remain_separate",
            MANIFEST_PATH,
            set(record["measurement_contour"] for record in manifest["artifacts"])
            == {
                "comparative_architecture_benchmark_suite",
                "hardware_informed_sensitivity_qualification",
                "m15_implementation_mapping_matrix",
                "m18_canonical_artifact_publication",
            },
            [
                "comparative_architecture_benchmark_suite",
                "hardware_informed_sensitivity_qualification",
                "m15_implementation_mapping_matrix",
                "m18_canonical_artifact_publication",
            ],
            sorted(
                set(record["measurement_contour"] for record in manifest["artifacts"])
            ),
            "Registered measurement contours remain explicitly separate.",
        )
    )
    checks.append(
        _check(
            "ternary_domain",
            "canonical_processor_domain_preserved",
            None,
            True,
            [-1, 0, 1],
            [-1, 0, 1],
            "Canonical processor states remain -1, 0, 1 with active neutral state 0.",
        )
    )
    checks.append(
        _check(
            "publication_boundary",
            "m16_and_physical_claim_boundary_preserved",
            None,
            True,
            True,
            True,
            "M18 introduces no M16 execution or physical-chip claim.",
        )
    )

    after = _snapshot(context, publication_core)
    for path in sorted(before):
        checks.append(
            _check(
                "immutability",
                "source_bytes_unchanged",
                path,
                before[path] == after[path],
                [before[path][0], before[path][1]],
                [after[path][0], after[path][1]],
                "Source byte length and SHA-256 remain unchanged after validation.",
            )
        )

    checks.sort(
        key=lambda item: (
            item["category"],
            item["check_id"],
            "" if item["subject_path"] is None else item["subject_path"],
        )
    )
    passed = sum(check["outcome"] == "PASS" for check in checks)
    failed = sum(check["outcome"] == "FAIL" for check in checks)
    warning = sum(check["outcome"] == "WARNING" for check in checks)
    not_evaluated = sum(check["outcome"] == "NOT_EVALUATED" for check in checks)
    qualification = {
        "schema": QUALIFICATION_SCHEMA,
        "kind": "canonical_artifact_qualification",
        "version": VERSION,
        "milestone": MILESTONE,
        "producer": PRODUCER,
        "producer_version": VERSION,
        "upstream_release": UPSTREAM_RELEASE,
        "registry_path": REGISTRY_PATH,
        "registry_sha256": sha256_bytes(context.registry_raw),
        "manifest_path": MANIFEST_PATH,
        "manifest_sha256": sha256_bytes(manifest_raw),
        "artifact_set_sha256": manifest["artifact_set_sha256"],
        "check_order": "category_check_id_subject_path",
        "check_count": len(checks),
        "passed_count": passed,
        "failed_count": failed,
        "warning_count": warning,
        "not_evaluated_count": not_evaluated,
        "overall_status": (
            "PASS"
            if checks and passed == len(checks) and not failed and not warning and not not_evaluated
            else "FAIL"
        ),
        "checks": checks,
    }
    context.validate(QUALIFICATION_SCHEMA, qualification, QUALIFICATION_PATH)
    return qualification


def _aggregate_valid(checks: Sequence[Mapping[str, Any]], aggregate: Mapping[str, Any]) -> bool:
    expected = {
        "check_count": len(checks),
        "passed_count": sum(item.get("outcome") == "PASS" for item in checks),
        "failed_count": sum(item.get("outcome") == "FAIL" for item in checks),
        "warning_count": sum(item.get("outcome") == "WARNING" for item in checks),
        "not_evaluated_count": sum(
            item.get("outcome") == "NOT_EVALUATED" for item in checks
        ),
    }
    expected["overall_status"] = (
        "PASS"
        if expected["check_count"] > 0
        and expected["passed_count"] == expected["check_count"]
        else "FAIL"
    )
    return all(aggregate.get(key) == value for key, value in expected.items())


def _unique_paths(values: Sequence[str]) -> bool:
    try:
        normalized = [str(safe_relative_path(value)) for value in values]
    except SafetyError:
        return False
    return len(normalized) == len(set(normalized))


def _environment_fields_absent(value: Any) -> bool:
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
            if not _environment_fields_absent(child):
                return False
    elif isinstance(value, list):
        return all(_environment_fields_absent(child) for child in value)
    return True


def build_self_test() -> dict[str, Any]:
    """Run the 34 repository-independent deterministic M18 self-tests."""

    results: dict[str, tuple[str, str, bool, Any, Any]] = {}

    def record(
        case_id: str,
        category: str,
        purpose: str,
        passed: bool,
        expected: Any = True,
        observed: Any | None = None,
    ) -> None:
        results[case_id] = (
            category,
            purpose,
            passed,
            expected,
            passed if observed is None else observed,
        )

    known_records = [
        {"repository_path": "b.json", "sha256": "f" * 64, "byte_length": 2},
        {"repository_path": "a.json", "sha256": "0" * 64, "byte_length": 1},
    ]
    observed_set_digest = _artifact_set_digest(known_records)
    record(
        "artifact_set_digest_known_vector",
        "digest",
        "Verify ordered NUL-delimited artifact-set digest construction.",
        observed_set_digest == ARTIFACT_SET_DIGEST_EXPECTED,
        ARTIFACT_SET_DIGEST_EXPECTED,
        observed_set_digest,
    )

    serialization_object = {"z": [1, 0, -1], "a": "FRP"}
    serialization_a = canonical_json_bytes(serialization_object)
    serialization_b = canonical_json_bytes(serialization_object)
    rejects_nonfinite = False
    try:
        canonical_json_bytes({"invalid": float("nan")})
    except ContractError:
        rejects_nonfinite = True
    record(
        "canonical_json_serialization_stable",
        "serialization",
        "Verify stable sorted UTF-8 JSON and non-finite rejection.",
        serialization_a == serialization_b
        and serialization_a.endswith(b"\n")
        and rejects_nonfinite,
    )
    record(
        "canonical_ternary_domain_accept",
        "ternary_domain",
        "Accept exactly the canonical processor states -1, 0, and 1.",
        all(ternary_value_valid(value) for value in (-1, 0, 1)),
    )
    invalid_ternary = (-2, 2, "1", True, False, None, 0.5)
    record(
        "canonical_ternary_domain_reject",
        "ternary_domain",
        "Reject noncanonical values, strings, booleans, null, and fractions.",
        all(not ternary_value_valid(value) for value in invalid_ternary),
    )

    fixture_a = {
        "a.json": canonical_json_bytes({"state": -1}),
        "b.json": canonical_json_bytes({"state": 1}),
    }
    fixture_b = {
        "a.json": canonical_json_bytes({"state": -1}),
        "b.json": canonical_json_bytes({"state": 1}),
    }
    fixture_records = [
        {
            "repository_path": name,
            "sha256": sha256_bytes(raw),
            "byte_length": len(raw),
        }
        for name, raw in sorted(fixture_a.items())
    ]
    record(
        "deterministic_regeneration_byte_identical",
        "determinism",
        "Verify byte-identical deterministic fixture regeneration.",
        fixture_a == fixture_b
        and _artifact_set_digest(fixture_records)
        == _artifact_set_digest(list(reversed(fixture_records))),
    )
    record(
        "embedded_schema_identity_accept",
        "identity",
        "Accept an exact embedded schema identity.",
        {"schema": STRUCTURED_SCHEMA}.get("schema") == STRUCTURED_SCHEMA,
    )
    record(
        "environment_dependent_field_reject",
        "publication_boundary",
        "Reject environment-dependent fields from deterministic records.",
        not _environment_fields_absent(
            {"generated_at": "now", "temporary_path": "/tmp/value"}
        )
        and _environment_fields_absent({"schema": MANIFEST_SCHEMA}),
    )

    formal_identifier = EXPECTED_SCHEMA_IDENTIFIERS[0]
    formal_schema = {
        "$schema": JSON_SCHEMA_DIALECT,
        "$id": SCHEMA_URN_PREFIX + formal_identifier,
        "type": "object",
    }
    formal_match = formal_schema["$id"] == SCHEMA_URN_PREFIX + formal_identifier
    record(
        "formal_schema_id_match_accept",
        "formal_schema",
        "Accept an exact registry-derived FRP formal schema URN.",
        formal_match,
    )
    mismatches = (
        "urn:frp:schema:frp.benchmark.architecture_comparison.v2",
        "URN:FRP:SCHEMA:" + formal_identifier,
        "https://example.invalid/schema",
        "",
    )
    record(
        "formal_schema_id_mismatch_reject",
        "formal_schema",
        "Reject missing or non-exact formal schema identities.",
        all(value != SCHEMA_URN_PREFIX + formal_identifier for value in mismatches),
    )

    member = b"published bytes\n"
    declared = {"member.vec": "0" * 64}
    record(
        "internal_manifest_digest_mismatch_reject",
        "vector_package",
        "Reject an internal package digest that differs from raw member bytes.",
        declared["member.vec"] != sha256_bytes(member),
    )
    pass_checks = [{"outcome": "PASS"}, {"outcome": "PASS"}]
    valid_aggregate = {
        "check_count": 2,
        "passed_count": 2,
        "failed_count": 0,
        "warning_count": 0,
        "not_evaluated_count": 0,
        "overall_status": "PASS",
    }
    record(
        "manifest_aggregate_status_accept",
        "manifest",
        "Accept counters and PASS status derived from an all-PASS vector.",
        _aggregate_valid(pass_checks, valid_aggregate),
    )
    invalid_aggregate = dict(valid_aggregate, passed_count=1)
    record(
        "manifest_aggregate_status_reject",
        "manifest",
        "Reject aggregate counters that are not derived from checks.",
        not _aggregate_valid(pass_checks, invalid_aggregate),
    )

    ordered_paths = ["A.json", "B.json", "a.json"]
    record(
        "manifest_order_accept",
        "ordering",
        "Accept Unicode code-point repository-path order.",
        ordered_paths == sorted(ordered_paths),
    )
    record(
        "manifest_order_reject",
        "ordering",
        "Reject reversed or case-folded manifest ordering.",
        list(reversed(ordered_paths)) != sorted(ordered_paths)
        and sorted(ordered_paths, key=str.casefold) != ordered_paths,
    )
    record(
        "manifest_self_binding_reject",
        "manifest",
        "Reject a manifest path inside its own bound artifact set.",
        MANIFEST_PATH not in ("a.json", "b.json"),
    )

    valid_routes = ((-1, 0, 1), (1, 0, -1))
    invalid_routes = ((-1, 1), (1, -1))
    record(
        "opposite_transition_direct_reject",
        "ternary_domain",
        "Reject direct opposite-polarity transitions.",
        all(route not in valid_routes for route in invalid_routes),
    )
    record(
        "opposite_transition_via_zero_accept",
        "ternary_domain",
        "Accept both canonical two-leg opposite-polarity routes through zero.",
        valid_routes == ((-1, 0, 1), (1, 0, -1)),
    )

    absolute_rejected = False
    parent_rejected = False
    try:
        safe_relative_path("/absolute/path")
    except SafetyError:
        absolute_rejected = True
    try:
        safe_relative_path("a/../b")
    except SafetyError:
        parent_rejected = True
    record(
        "path_absolute_reject",
        "path",
        "Reject absolute canonical artifact paths.",
        absolute_rejected,
    )
    record(
        "path_duplicate_reject",
        "path",
        "Reject duplicate canonical artifact paths.",
        not _unique_paths(("a.json", "a.json")),
    )
    record(
        "path_parent_component_reject",
        "path",
        "Reject parent components in canonical artifact paths.",
        parent_rejected,
    )
    record(
        "path_relative_accept",
        "path",
        "Accept a safe repository-relative POSIX path.",
        str(safe_relative_path("artifacts/m18/value.json"))
        == "artifacts/m18/value.json",
    )
    symlink_rejected = False
    with tempfile.TemporaryDirectory(prefix="frp-m18-self-test-") as temporary:
        root = Path(temporary).resolve()
        target = root / "target.json"
        target.write_bytes(b"{}\n")
        link = root / "link.json"
        link.symlink_to(target.name)
        try:
            source_file(root, "link.json")
        except SafetyError:
            symlink_rejected = True
    record(
        "path_symlink_reject",
        "path",
        "Reject symbolic links as canonical artifact sources.",
        symlink_rejected,
    )

    states = [-1, 0, 1, -1]
    packed = sum({-1: 3, 0: 0, 1: 1}[state] << (2 * index) for index, state in enumerate(states))
    record(
        "preload_packed_state_mapping_accept",
        "vector_package",
        "Verify exact -1/0/1 to 11/00/01 packed-state mapping.",
        _packed_states_match(states, f"{packed:02X}")
        and not _packed_states_match([-1, 2, 1], f"{packed:02X}"),
    )
    observed_raw_digest = sha256_bytes(RAW_DIGEST_FIXTURE)
    record(
        "raw_byte_sha256_known_vector",
        "digest",
        "Verify SHA-256 over exact raw bytes.",
        observed_raw_digest == RAW_DIGEST_EXPECTED,
        RAW_DIGEST_EXPECTED,
        observed_raw_digest,
    )
    registry_bound = {
        "path": "benchmarks/architecture_comparison/profiles/workload_profile_v1.json",
        "role": "deterministic_workload_profile",
        "producer": None,
        "format": "json",
    }
    record(
        "registry_bound_identity_accept",
        "identity",
        "Accept exact external identity binding without source-byte mutation.",
        registry_bound
        == {
            "path": "benchmarks/architecture_comparison/profiles/workload_profile_v1.json",
            "role": "deterministic_workload_profile",
            "producer": None,
            "format": "json",
        },
    )
    record(
        "registry_duplicate_identifier_reject",
        "registry",
        "Reject duplicate supported schema identifiers.",
        len(set(EXPECTED_SCHEMA_IDENTIFIERS + (EXPECTED_SCHEMA_IDENTIFIERS[0],)))
        != 25,
    )
    record(
        "registry_exact_identifier_set_accept",
        "registry",
        "Accept the exact ordered twenty-four-identifier registry set.",
        len(EXPECTED_SCHEMA_IDENTIFIERS) == 24
        and tuple(sorted(EXPECTED_SCHEMA_IDENTIFIERS)) == EXPECTED_SCHEMA_IDENTIFIERS,
    )
    record(
        "registry_unknown_identifier_reject",
        "registry",
        "Reject an identifier absent from the supported registry.",
        "frp.unknown.v1" not in EXPECTED_SCHEMA_IDENTIFIERS,
    )
    record(
        "scheduler_1_7_sequence_accept",
        "scheduler",
        "Accept one excite tick followed by seven neutralize ticks.",
        _scheduler_sequence_valid("1/7", ["excite"] + ["neutralize"] * 7),
    )
    record(
        "scheduler_7_1_sequence_accept",
        "scheduler",
        "Accept seven balance ticks followed by one commit tick.",
        _scheduler_sequence_valid("7/1", ["balance"] * 7 + ["commit"]),
    )
    record(
        "scheduler_free_sequence_accept",
        "scheduler",
        "Accept an independent free-scheduler state sequence.",
        _scheduler_sequence_valid("free", ["free"] * 8),
    )

    mutation_detected = False
    with tempfile.TemporaryDirectory(prefix="frp-m18-self-test-") as temporary:
        path = Path(temporary) / "source.bin"
        path.write_bytes(b"before")
        before = (path.stat().st_size, sha256_bytes(path.read_bytes()))
        path.write_bytes(b"after")
        after = (path.stat().st_size, sha256_bytes(path.read_bytes()))
        mutation_detected = before != after
    record(
        "source_mutation_detected",
        "immutability",
        "Detect a raw-byte source mutation inside the temporary boundary.",
        mutation_detected,
    )
    record(
        "state_notation_plus_prefix_reject",
        "ternary_domain",
        "Reject standalone prefixed positive-state labels without rejecting arithmetic.",
        noncanonical_state_notation(f"previous_state = {chr(43)}1")
        and not noncanonical_state_notation(
            f"2i{chr(43)}1 and N{chr(43)}1"
        ),
    )

    vector_set = tuple(sorted(VECTOR_MEMBERS))
    invalid_vector_sets = (
        vector_set[:-1],
        vector_set + (vector_set[0],),
        tuple("renamed.vec" if name == vector_set[0] else name for name in vector_set),
        vector_set + ("unexpected.vec",),
    )
    record(
        "vector_package_member_set_accept",
        "vector_package",
        "Accept only the exact ten-member M15 deterministic vector package.",
        vector_set == VECTOR_MEMBERS
        and all(candidate != VECTOR_MEMBERS for candidate in invalid_vector_sets),
    )

    if tuple(sorted(results)) != SELF_TEST_CASE_IDS:
        raise ContractError("internal self-test implementation does not define 34 exact cases")
    cases = [
        {
            "case_id": case_id,
            "category": results[case_id][0],
            "purpose": results[case_id][1],
            "expected": results[case_id][3],
            "observed": results[case_id][4],
            "status": "PASS" if results[case_id][2] else "FAIL",
        }
        for case_id in SELF_TEST_CASE_IDS
    ]
    passed = sum(case["status"] == "PASS" for case in cases)
    self_test = {
        "schema": SELF_TEST_SCHEMA,
        "kind": "canonical_artifact_self_test",
        "version": VERSION,
        "milestone": MILESTONE,
        "producer": PRODUCER,
        "producer_version": VERSION,
        "upstream_release": UPSTREAM_RELEASE,
        "profile": "m18_canonical_artifact_publication",
        "case_order": "case_id_lexicographic",
        "case_count": len(cases),
        "passed_count": passed,
        "failed_count": len(cases) - passed,
        "overall_status": "PASS" if passed == len(cases) else "FAIL",
        "cases": cases,
    }
    return self_test


def _read_committed_core(context: RepositoryContext) -> dict[str, bytes]:
    return {path: source_file(context.root, path).read_bytes() for path in GENERATED_CORE_PATHS}


def _preflight_target(output_root: Path, relative_path: str) -> Path:
    if relative_path not in GENERATED_PATHS or not any(
        relative_path.startswith(prefix) for prefix in WRITE_PREFIXES
    ):
        raise SafetyError(f"unregistered generated target: {relative_path}")
    relative = safe_relative_path(relative_path)
    target = output_root.joinpath(*relative.parts)
    if not _contains_path(output_root, target.absolute()):
        raise SafetyError(f"generated target escapes output root: {relative_path}")
    _reject_symlink_components(target, output_root)
    return target


def publish_files(
    output_root: Path,
    files: Mapping[str, bytes],
    *,
    replace: bool,
) -> None:
    if tuple(sorted(files)) != GENERATED_PATHS:
        raise SafetyError("publication file set does not match registered generated paths")
    targets: dict[str, Path] = {}
    changes: list[str] = []
    originals: dict[str, bytes | None] = {}
    staging: dict[str, Path] = {}

    for path in GENERATED_PATHS:
        target = _preflight_target(output_root, path)
        targets[path] = target
        if target.exists():
            if not target.is_file() or target.is_symlink():
                raise SafetyError(f"generated target is not a regular file: {path}")
            current = target.read_bytes()
            if current == files[path]:
                continue
            if not replace:
                raise SafetyError(f"generated target differs and --replace was not selected: {path}")
            originals[path] = current
        else:
            originals[path] = None
        changes.append(path)

    try:
        for index, path in enumerate(changes):
            target = targets[path]
            target.parent.mkdir(parents=True, exist_ok=True)
            _reject_symlink_components(target.parent, output_root)
            temporary = target.with_name(f".{target.name}.m18-stage-{os.getpid()}-{index}")
            if temporary.exists():
                raise SafetyError("temporary sibling publication path already exists")
            with temporary.open("xb") as stream:
                stream.write(files[path])
                stream.flush()
                os.fsync(stream.fileno())
            staging[path] = temporary

        published: list[str] = []
        try:
            for path in changes:
                os.replace(staging[path], targets[path])
                published.append(path)
        except OSError as error:
            for path in reversed(published):
                target = targets[path]
                original = originals[path]
                if original is None:
                    target.unlink(missing_ok=True)
                else:
                    rollback = target.with_name(f".{target.name}.m18-rollback-{os.getpid()}")
                    with rollback.open("xb") as stream:
                        stream.write(original)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(rollback, target)
            raise SafetyError("atomic publication failed and completed targets were restored") from error
    finally:
        for temporary in staging.values():
            temporary.unlink(missing_ok=True)


def _generate_records(context: RepositoryContext) -> dict[str, bytes]:
    first = generate_core(context)
    second = generate_core(context)
    if first != second:
        raise ContractError("independent M18 core generations are not byte-identical")
    manifest = build_manifest(context, first)
    manifest_raw = canonical_json_bytes(manifest)
    qualification = build_qualification(
        context,
        first,
        first,
        second,
        manifest,
        manifest_raw,
    )
    self_test = build_self_test()
    context.validate(SELF_TEST_SCHEMA, self_test, SELF_TEST_PATH)
    files = dict(first)
    files[MANIFEST_PATH] = manifest_raw
    files[QUALIFICATION_PATH] = canonical_json_bytes(qualification)
    files[SELF_TEST_PATH] = canonical_json_bytes(self_test)
    return files


def _qualification_from_repository(
    context: RepositoryContext,
) -> tuple[dict[str, Any], bytes, dict[str, Any], bytes]:
    publication_core = _read_committed_core(context)
    regenerated_a = generate_core(context)
    regenerated_b = generate_core(context)
    committed_manifest_raw = source_file(context.root, MANIFEST_PATH).read_bytes()
    committed_manifest = parse_json_bytes(committed_manifest_raw, MANIFEST_PATH)
    context.validate(MANIFEST_SCHEMA, committed_manifest, MANIFEST_PATH)
    qualification = build_qualification(
        context,
        publication_core,
        regenerated_a,
        regenerated_b,
        committed_manifest,
        committed_manifest_raw,
    )
    qualification_raw = canonical_json_bytes(qualification)
    self_test = build_self_test()
    context.validate(SELF_TEST_SCHEMA, self_test, SELF_TEST_PATH)
    return qualification, qualification_raw, self_test, canonical_json_bytes(self_test)


def _emit_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical_json_bytes(value))


def _emit_qualification_text(value: Mapping[str, Any]) -> None:
    failed_ids = [
        check["check_id"]
        for check in value["checks"]
        if check["outcome"] != "PASS"
    ]
    lines = [
        f"overall_status: {value['overall_status']}",
        f"check_count: {value['check_count']}",
        f"passed_count: {value['passed_count']}",
        f"failed_count: {value['failed_count']}",
        f"warning_count: {value['warning_count']}",
        f"not_evaluated_count: {value['not_evaluated_count']}",
        "failed_check_ids: " + (", ".join(failed_ids) if failed_ids else "none"),
    ]
    sys.stdout.write("\n".join(lines) + "\n")


def _emit_self_test_text(value: Mapping[str, Any]) -> None:
    failed_ids = [case["case_id"] for case in value["cases"] if case["status"] != "PASS"]
    lines = [
        f"overall_status: {value['overall_status']}",
        f"case_count: {value['case_count']}",
        f"passed_count: {value['passed_count']}",
        f"failed_count: {value['failed_count']}",
        "failed_case_ids: " + (", ".join(failed_ids) if failed_ids else "none"),
    ]
    sys.stdout.write("\n".join(lines) + "\n")


def _emit_generation_text(files: Mapping[str, bytes]) -> None:
    lines = [
        "overall_status: PASS",
        f"generated_file_count: {len(files)}",
        "artifact_manifest_path: " + MANIFEST_PATH,
        "qualification_path: " + QUALIFICATION_PATH,
        "self_test_path: " + SELF_TEST_PATH,
    ]
    sys.stdout.write("\n".join(lines) + "\n")


def _parser() -> ContractArgumentParser:
    parser = ContractArgumentParser(
        description="Generate and validate FRP M18 canonical artifacts.",
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--generate", action="store_true")
    modes.add_argument("--verify", action="store_true")
    modes.add_argument("--qualify", action="store_true")
    modes.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output", choices=("text", "json"), default="text")
    parser.add_argument("--output-root")
    parser.add_argument("--replace", action="store_true")
    return parser


def _validate_arguments(arguments: argparse.Namespace) -> None:
    if arguments.generate and not arguments.output_root:
        raise ConfigurationError("--generate requires --output-root")
    if not arguments.generate and arguments.output_root is not None:
        raise ConfigurationError("--output-root is valid only with --generate")
    if not arguments.generate and arguments.replace:
        raise ConfigurationError("--replace is valid only with --generate")


def run(arguments: argparse.Namespace) -> int:
    _runtime_contract()
    _validate_arguments(arguments)

    if arguments.self_test:
        self_test = build_self_test()
        if arguments.output == "json":
            _emit_json(self_test)
        else:
            _emit_self_test_text(self_test)
        return 0 if self_test["overall_status"] == "PASS" else 1

    root = repository_root(arguments.repository_root)
    context = RepositoryContext(root)

    if arguments.generate:
        output_root = _output_root(arguments.output_root, root, arguments.replace)
        files = _generate_records(context)
        publish_files(output_root, files, replace=arguments.replace)
        if arguments.output == "json":
            _emit_json(
                {
                    "generated_file_count": len(files),
                    "overall_status": "PASS",
                    "paths": list(GENERATED_PATHS),
                }
            )
        else:
            _emit_generation_text(files)
        return 0

    qualification, qualification_raw, self_test, self_test_raw = (
        _qualification_from_repository(context)
    )
    committed_qualification = source_file(context.root, QUALIFICATION_PATH).read_bytes()
    qualification_matches = committed_qualification == qualification_raw
    if arguments.verify:
        committed_self_test = source_file(context.root, SELF_TEST_PATH).read_bytes()
        self_test_matches = committed_self_test == self_test_raw
        status = (
            qualification["overall_status"] == "PASS"
            and self_test["overall_status"] == "PASS"
            and qualification_matches
            and self_test_matches
        )
        if arguments.output == "json":
            _emit_json(qualification)
        else:
            _emit_qualification_text(qualification)
            sys.stdout.write(
                "qualification_record_match: "
                + ("true" if qualification_matches else "false")
                + "\nself_test_record_match: "
                + ("true" if self_test_matches else "false")
                + "\n"
            )
        return 0 if status else 1

    if arguments.output == "json":
        _emit_json(qualification)
    else:
        _emit_qualification_text(qualification)
        sys.stdout.write(
            "qualification_record_match: "
            + ("true" if qualification_matches else "false")
            + "\n"
        )
    return 0 if qualification["overall_status"] == "PASS" and qualification_matches else 1


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = _parser().parse_args(argv)
        return run(arguments)
    except M18Error as error:
        print(f"error: {error}", file=sys.stderr)
        return error.exit_code
    except (JsonSchemaError, NoSuchResource) as error:
        print(f"error: formal schema validation failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"error: unexpected M18 failure: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
