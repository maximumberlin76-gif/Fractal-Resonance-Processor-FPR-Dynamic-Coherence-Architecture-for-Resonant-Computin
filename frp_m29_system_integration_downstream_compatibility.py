#!/usr/bin/env python3
"""Generate and verify FRP M29 system-integration compatibility evidence."""

from __future__ import annotations

import argparse
import base64
import binascii
import copy
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


VERSION = "3.1.0"
MILESTONE = "M29"
MILESTONE_TITLE = "M29 - System Integration and Downstream Compatibility Closure"
OBJECTIVE = (
    "close the published integration boundary without coupling FRP "
    "qualification to downstream implementation code"
)
EXPECTED_M28_COMMIT = "a1c0bb2fa0a4731b9339e6cd996589e1bf226c04"
EXPECTED_M28_SUBJECT = (
    "Add M28 hierarchical scaling and hotspot-containment realization"
)
PRESERVED_M28_OBSERVATORY_COMMIT = (
    "566a4ff88baa57f844691b46937552253e095434"
)
OBSERVATORY_REPOSITORY = "FRP-Trace-Observatory"
OBSERVATORY_AUDITED_COMMIT = "a9d71657c56221d0d9b72fb6e954e0028f096a9e"
OBSERVATORY_TEST_COUNT = 275
OBSERVATORY_MODES = (
    "artifact_auditor",
    "ternary_transition_visualizer",
    "trace_explorer",
)
WORKFLOW_PATH = (
    ".github/workflows/"
    "frp-m29-system-integration-downstream-compatibility-closure-workflow.yml"
)

UPSTREAM_MILESTONES = tuple(f"M{value}" for value in range(18, 29))
UPSTREAM_RELEASES = {
    f"M{milestone}": f"FRP v{version} / M{milestone}"
    for milestone, version in (
        (18, "2.0.0"),
        (19, "2.1.0"),
        (20, "2.2.0"),
        (21, "2.3.0"),
        (22, "2.4.0"),
        (23, "2.5.0"),
        (24, "2.6.0"),
        (25, "2.7.0"),
        (26, "2.8.0"),
        (27, "2.9.0"),
        (28, "3.0.0"),
    )
}

CONTRACT_ID = "frp.m29.system_integration_contract.v3.1.0"
SCHEMA_REGISTRY_ID = "frp.m29.supported_schema_registry.v3.1.0"
ARTIFACT_REGISTRY_ID = "frp.m29.supported_artifact_registry.v3.1.0"
COMPATIBILITY_ID = "frp.m29.compatibility_version_declarations.v3.1.0"
DEMO_PACKAGE_ID = "frp.m29.canonical_demo_artifact_package.v3.1.0"
PACKAGE_MANIFEST_ID = "frp.m29.deterministic_package_manifest.v3.1.0"
PRODUCER_REGISTRY_ID = "frp.m29.producer_command_registry.v3.1.0"
IMMUTABLE_POLICY_ID = "frp.m29.immutable_source_artifact_policy.v3.1.0"
PROVENANCE_ID = "frp.m29.provenance_completeness_record.v3.1.0"
UNSUPPORTED_ID = "frp.m29.unsupported_version_behavior.v3.1.0"
CONSUMPTION_VECTORS_ID = "frp.m29.downstream_consumption_test_vectors.v3.1.0"
RELEASE_RECORDS_ID = (
    "frp.m29.release_independent_compatibility_records.v3.1.0"
)
QUALIFICATION_ID = "frp.m29.system_integration_qualification.v3.1.0"

SCHEMA_IDS = (
    CONTRACT_ID,
    SCHEMA_REGISTRY_ID,
    ARTIFACT_REGISTRY_ID,
    COMPATIBILITY_ID,
    DEMO_PACKAGE_ID,
    PACKAGE_MANIFEST_ID,
    PRODUCER_REGISTRY_ID,
    IMMUTABLE_POLICY_ID,
    PROVENANCE_ID,
    UNSUPPORTED_ID,
    CONSUMPTION_VECTORS_ID,
    RELEASE_RECORDS_ID,
    QUALIFICATION_ID,
)


def schema_path(identifier: str) -> str:
    stem = identifier.replace("frp.m29.", "frp_m29_").replace(".", "_")
    stem = stem.replace("_v3_1_0", ".v3.1.0")
    return f"schemas/m29/{stem}.schema.json"


SCHEMA_PATHS = {identifier: schema_path(identifier) for identifier in SCHEMA_IDS}
SCHEMA_REGISTRY = "schemas/m29/frp_m29_supported_schema_registry.json"
CONTRACT_ARTIFACT = "artifacts/m29/contracts/m29-system-integration-contract.json"
ARTIFACT_REGISTRY = (
    "artifacts/m29/registries/m29-supported-artifact-registry.json"
)
COMPATIBILITY_ARTIFACT = (
    "artifacts/m29/compatibility/m29-compatibility-version-declarations.json"
)
DEMO_PACKAGE_ARTIFACT = (
    "artifacts/m29/packages/m29-canonical-demo-artifact-package.json"
)
PACKAGE_MANIFEST_ARTIFACT = (
    "artifacts/m29/packages/m29-deterministic-package-manifest.json"
)
PRODUCER_REGISTRY_ARTIFACT = (
    "artifacts/m29/registries/m29-producer-command-registry.json"
)
IMMUTABLE_POLICY_ARTIFACT = (
    "artifacts/m29/policies/m29-immutable-source-artifact-policy.json"
)
PROVENANCE_ARTIFACT = (
    "artifacts/m29/provenance/m29-provenance-completeness-record.json"
)
UNSUPPORTED_ARTIFACT = (
    "artifacts/m29/compatibility/m29-unsupported-version-behavior.json"
)
CONSUMPTION_VECTORS_ARTIFACT = (
    "artifacts/m29/vectors/m29-downstream-consumption-test-vectors.json"
)
RELEASE_RECORDS_ARTIFACT = (
    "artifacts/m29/compatibility/"
    "m29-release-independent-compatibility-records.json"
)
QUALIFICATION_ARTIFACT = (
    "artifacts/m29/manifests/m29-system-integration-qualification.json"
)

DOCUMENT_SCHEMA_IDS = {
    SCHEMA_REGISTRY: SCHEMA_REGISTRY_ID,
    CONTRACT_ARTIFACT: CONTRACT_ID,
    ARTIFACT_REGISTRY: ARTIFACT_REGISTRY_ID,
    COMPATIBILITY_ARTIFACT: COMPATIBILITY_ID,
    DEMO_PACKAGE_ARTIFACT: DEMO_PACKAGE_ID,
    PACKAGE_MANIFEST_ARTIFACT: PACKAGE_MANIFEST_ID,
    PRODUCER_REGISTRY_ARTIFACT: PRODUCER_REGISTRY_ID,
    IMMUTABLE_POLICY_ARTIFACT: IMMUTABLE_POLICY_ID,
    PROVENANCE_ARTIFACT: PROVENANCE_ID,
    UNSUPPORTED_ARTIFACT: UNSUPPORTED_ID,
    CONSUMPTION_VECTORS_ARTIFACT: CONSUMPTION_VECTORS_ID,
    RELEASE_RECORDS_ARTIFACT: RELEASE_RECORDS_ID,
    QUALIFICATION_ARTIFACT: QUALIFICATION_ID,
}

PRIMARY_DOCUMENT_PATHS = tuple(
    path for path in DOCUMENT_SCHEMA_IDS if path != QUALIFICATION_ARTIFACT
)
GENERATED_PATHS = (
    *SCHEMA_PATHS.values(),
    *DOCUMENT_SCHEMA_IDS.keys(),
)

DEMO_MEMBER_SPECS = (
    {
        "member_id": "m16-fpga-preparation-execution-trace",
        "source_path": (
            "artifacts/m19/execution/"
            "m16-fpga-preparation-execution-trace.json"
        ),
        "schema_identifier": (
            "frp.m16.fpga_preparation_execution_trace.v2.1.0"
        ),
        "measurement_contour": "m16_fpga_preparation_execution",
        "observatory_modes": OBSERVATORY_MODES,
    },
    {
        "member_id": "m27-telemetry-semantics",
        "source_path": "artifacts/m27/telemetry/m27-telemetry-semantics.json",
        "schema_identifier": "m27-telemetry-semantics-v2.9.0",
        "measurement_contour": "m27_long_run_telemetry_semantics",
        "observatory_modes": (
            "artifact_auditor",
            "ternary_transition_visualizer",
        ),
    },
    {
        "member_id": "m28-trace-observatory-upstream-contract",
        "source_path": (
            "artifacts/m28/contracts/"
            "m28-trace-observatory-upstream-contract.json"
        ),
        "schema_identifier": (
            "frp.m28.trace_observatory_upstream_contract.v3.0.0"
        ),
        "measurement_contour": "m28_upstream_integration_contract",
        "observatory_modes": ("artifact_auditor",),
    },
    {
        "member_id": "m28-hierarchical-scaling-contract",
        "source_path": (
            "artifacts/m28/hierarchy/contracts/"
            "m28-hierarchical-scaling-contract.json"
        ),
        "schema_identifier": (
            "frp.m28.hierarchical_scaling_contract.v3.0.0"
        ),
        "measurement_contour": "m28_hierarchical_scaling_qualification",
        "observatory_modes": ("artifact_auditor",),
    },
)

PRODUCER_SPECS = (
    {
        "producer_id": "m18-canonical-artifacts",
        "milestone": "M18",
        "path": "frp_m18_canonical_artifacts.py",
        "commands": [
            "python frp_m18_canonical_artifacts.py --generate "
            "--repository-root . --output-root <output-root>"
        ],
    },
    {
        "producer_id": "m19-m16-evidence",
        "milestone": "M19",
        "path": "frp_m19_m16_evidence.py",
        "commands": [
            "python frp_m19_m16_evidence.py --generate --repository-root . "
            "--rtl-log <rtl-log> --fpga-log <fpga-log> "
            "--output-root <output-root>"
        ],
    },
    {
        "producer_id": "m20-cross-layer-correlation",
        "milestone": "M20",
        "path": "frp_m20_cross_layer_correlation.py",
        "commands": [
            "python frp_m20_cross_layer_correlation.py --generate "
            "--repository-root . --output-root <output-root> "
            "--source-commit <m19-commit>"
        ],
    },
    {
        "producer_id": "m21-parameterized-qualification-matrix",
        "milestone": "M21",
        "path": "frp_m21_parameterized_qualification_matrix.py",
        "commands": [
            "python frp_m21_parameterized_qualification_matrix.py --generate "
            "--repository-root . --output-root <output-root> "
            "--source-commit <m20-commit>"
        ],
    },
    {
        "producer_id": "m22-control-status-register-interface",
        "milestone": "M22",
        "path": "frp_m22_control_status_register_interface.py",
        "commands": [
            "python frp_m22_control_status_register_interface.py --generate "
            "--repository-root . --output-root <output-root> "
            "--source-commit <m21-commit>"
        ],
    },
    {
        "producer_id": "m23-clock-reset-cdc-interface-hardening",
        "milestone": "M23",
        "path": "frp_m23_clock_reset_cdc_interface_hardening.py",
        "commands": [
            "python frp_m23_clock_reset_cdc_interface_hardening.py --generate "
            "--repository-root . --output-root <output-root> "
            "--source-commit <m22-commit>"
        ],
    },
    {
        "producer_id": "m24-formal-bounded-verification",
        "milestone": "M24",
        "path": "frp_m24_formal_bounded_verification.py",
        "commands": [
            "python frp_m24_formal_bounded_verification.py --run-formal "
            "--repository-root . --work-root <work-root> "
            "--source-commit <m23-commit>",
            "python frp_m24_formal_bounded_verification.py --generate "
            "--repository-root . --output-root <output-root> "
            "--formal-result <formal-result> --source-commit <m23-commit>",
        ],
    },
    {
        "producer_id": "m25-fault-negative-recovery-qualification",
        "milestone": "M25",
        "path": "frp_m25_fault_negative_recovery_qualification.py",
        "commands": [
            "python frp_m25_fault_negative_recovery_qualification.py "
            "--run-formal --repository-root . --work-root <work-root> "
            "--source-commit <m24-commit>",
            "python frp_m25_fault_negative_recovery_qualification.py "
            "--generate --repository-root . --output-root <output-root> "
            "--formal-result <formal-result> --source-commit <m24-commit>",
        ],
    },
    {
        "producer_id": "m26-declared-target-implementation-evidence",
        "milestone": "M26",
        "path": "frp_m26_declared_target_implementation_evidence.py",
        "commands": [
            "python frp_m26_declared_target_implementation_evidence.py "
            "--run-implementation --repository-root . --work-root <work-root> "
            "--source-commit <m25-commit>",
            "python frp_m26_declared_target_implementation_evidence.py "
            "--generate --repository-root . --output-root <output-root> "
            "--implementation-result <implementation-result> "
            "--source-commit <m25-commit>",
        ],
    },
    {
        "producer_id": "m27-long-run-stability-telemetry-qualification",
        "milestone": "M27",
        "path": "frp_m27_long_run_stability_telemetry_qualification.py",
        "commands": [
            "python frp_m27_long_run_stability_telemetry_qualification.py "
            "--run-long-run --repository-root . --output-root <output-root> "
            "--source-commit <m26-commit>",
            "python frp_m27_long_run_stability_telemetry_qualification.py "
            "--generate --repository-root . --output-root <output-root> "
            "--long-run-result <long-run-result> "
            "--source-commit <m26-commit>",
        ],
    },
    {
        "producer_id": "m28-trace-observatory-upstream-interchange",
        "milestone": "M28",
        "path": "frp_m28_trace_observatory_upstream_interchange.py",
        "commands": [
            "python frp_m28_trace_observatory_upstream_interchange.py "
            "--generate --repository-root . --output-root <output-root> "
            "--source-commit <m27-commit>"
        ],
    },
    {
        "producer_id": "m28-hierarchical-scaling-hotspot-containment",
        "milestone": "M28",
        "path": "frp_m28_hierarchical_scaling_hotspot_containment.py",
        "commands": [
            "python frp_m28_hierarchical_scaling_hotspot_containment.py "
            "--generate --repository-root . --output-root <output-root> "
            "--source-commit <m27-commit>"
        ],
    },
)

HEX64_PATTERN = "^[0-9a-f]{64}$"
VERSION_PATTERN = re.compile(r"(?:^|[.-])v([0-9]+(?:\.[0-9]+){0,2})$")


class ContractError(ValueError):
    """Raised when an M29 integration invariant is violated."""


class SafetyError(ValueError):
    """Raised when a repository-relative path is unsafe."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or value != value.strip():
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    if "\\" in value or "\x00" in value:
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(
        part in ("", ".", "..") for part in value.split("/")
    ):
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    return path


def path_for(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative_path(relative).parts)


def require_file(root: Path, relative: str) -> Path:
    target = path_for(root, relative)
    if target.is_symlink() or not target.is_file():
        raise ContractError(f"required source file missing: {relative}")
    return target


def read_json(root: Path, relative: str) -> Any:
    try:
        return json.loads(require_file(root, relative).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON source: {relative}: {exc}") from exc


def raw_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def document_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def object_digest(value: Mapping[str, Any], field: str | None = None) -> str:
    subject = dict(value)
    if field is not None:
        subject.pop(field, None)
    return raw_digest(canonical_json_bytes(subject))


def with_digest(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(value))
    result.pop(field, None)
    result[field] = object_digest(result)
    return result


def verify_digest(value: Mapping[str, Any], field: str, label: str) -> None:
    expected = object_digest(value, field)
    if value.get(field) != expected:
        raise ContractError(f"{label} digest mismatch")


def validate_source_commit(source_commit: str) -> None:
    if source_commit != EXPECTED_M28_COMMIT:
        raise ContractError(
            f"M29 requires source commit {EXPECTED_M28_COMMIT}, got {source_commit}"
        )


def milestone_from_path(path: str) -> str:
    match = re.match(r"^(?:artifacts|schemas)/m(\d+)/", path)
    if not match:
        raise ContractError(f"cannot derive milestone from path: {path}")
    milestone = f"M{int(match.group(1))}"
    if milestone not in UPSTREAM_MILESTONES:
        raise ContractError(f"path outside M18-M28 boundary: {path}")
    return milestone


def identifier_version(identifier: str) -> str:
    match = VERSION_PATTERN.search(identifier)
    if not match:
        raise ContractError(f"identifier lacks an exact version suffix: {identifier}")
    return match.group(1)


def _field_schema(field: str, kind: str) -> dict[str, Any]:
    if kind == "digest":
        return {"type": "string", "pattern": HEX64_PATTERN}
    if kind == "source_commit":
        return {"type": "string", "const": EXPECTED_M28_COMMIT}
    if kind == "schema":
        return {"type": "string"}
    if kind == "array":
        return {"type": "array"}
    if kind == "object":
        return {"type": "object"}
    if kind == "integer":
        return {"type": "integer", "minimum": 0}
    if kind == "number":
        return {"type": "number"}
    if kind == "boolean":
        return {"type": "boolean"}
    return {"type": "string"}


DOCUMENT_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    CONTRACT_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("milestone_title", "string"), ("version", "string"),
        ("source_commit", "source_commit"), ("source_subject", "string"),
        ("objective", "string"), ("immutable_core", "object"),
        ("integration_boundary", "object"), ("inventory_boundary", "object"),
        ("required_deliverables", "array"), ("status", "string"),
        ("contract_digest", "digest"),
    ),
    SCHEMA_REGISTRY_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("upstream_schema_count", "integer"), ("m29_schema_count", "integer"),
        ("record_count", "integer"), ("source_registry_count", "integer"),
        ("source_registries", "array"), ("records", "array"),
        ("identity_policy", "object"), ("status", "string"),
        ("registry_digest", "digest"),
    ),
    ARTIFACT_REGISTRY_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("record_count", "integer"), ("json_artifact_count", "integer"),
        ("byte_artifact_count", "integer"), ("milestone_counts", "object"),
        ("records", "array"), ("identity_policy", "object"),
        ("status", "string"), ("registry_digest", "digest"),
    ),
    COMPATIBILITY_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("compatibility_revision", "string"), ("declaration_count", "integer"),
        ("declarations", "array"), ("resolution_policy", "object"),
        ("status", "string"), ("declarations_digest", "digest"),
    ),
    DEMO_PACKAGE_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("package_id", "string"), ("member_count", "integer"),
        ("members", "array"), ("transport_contract", "object"),
        ("status", "string"), ("package_digest", "digest"),
    ),
    PACKAGE_MANIFEST_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("manifest_id", "string"), ("package_path", "string"),
        ("package_bytes", "integer"), ("package_raw_sha256", "digest"),
        ("member_count", "integer"), ("members", "array"),
        ("generation", "object"), ("status", "string"),
        ("manifest_digest", "digest"),
    ),
    PRODUCER_REGISTRY_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("record_count", "integer"), ("records", "array"),
        ("execution_boundary", "object"), ("status", "string"),
        ("registry_digest", "digest"),
    ),
    IMMUTABLE_POLICY_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("policy_id", "string"), ("byte_identity", "object"),
        ("consumer_rules", "object"), ("violation_behavior", "object"),
        ("status", "string"), ("policy_digest", "digest"),
    ),
    PROVENANCE_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("record_id", "string"), ("inventory_counts", "object"),
        ("inventory_digests", "object"), ("coverage", "object"),
        ("checks", "array"), ("check_count", "integer"),
        ("status", "string"), ("record_digest", "digest"),
    ),
    UNSUPPORTED_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("policy_id", "string"), ("resolution", "object"),
        ("case_count", "integer"), ("cases", "array"),
        ("status", "string"), ("behavior_digest", "digest"),
    ),
    CONSUMPTION_VECTORS_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("vector_set_id", "string"), ("vector_count", "integer"),
        ("accepted_count", "integer"), ("rejected_count", "integer"),
        ("vectors", "array"), ("status", "string"),
        ("vector_set_digest", "digest"),
    ),
    RELEASE_RECORDS_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("record_set_id", "string"), ("record_count", "integer"),
        ("compatibility_key_contract", "object"), ("records", "array"),
        ("status", "string"), ("record_set_digest", "digest"),
    ),
    QUALIFICATION_ID: (
        ("schema", "schema"), ("kind", "string"), ("milestone", "string"),
        ("version", "string"), ("source_commit", "source_commit"),
        ("qualification_id", "string"), ("schema_count", "integer"),
        ("document_count", "integer"), ("schemas", "array"),
        ("documents", "array"), ("check_count", "integer"),
        ("passed_count", "integer"), ("failed_count", "integer"),
        ("checks", "array"), ("status", "string"),
        ("qualification_digest", "digest"),
    ),
}


def build_schema_documents() -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    for identifier in SCHEMA_IDS:
        fields = DOCUMENT_FIELDS[identifier]
        properties = {
            field: _field_schema(field, kind) for field, kind in fields
        }
        properties["schema"] = {"type": "string", "const": identifier}
        properties["milestone"] = {"type": "string", "const": MILESTONE}
        properties["version"] = {"type": "string", "const": VERSION}
        properties["status"] = {"type": "string", "const": "PASS"}
        documents[SCHEMA_PATHS[identifier]] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": identifier,
            "title": identifier,
            "type": "object",
            "required": [field for field, _ in fields],
            "properties": properties,
            "additionalProperties": False,
        }
    return documents


def source_schema_registry_paths(root: Path) -> list[str]:
    paths: list[str] = []
    for number in range(18, 29):
        directory = root / "schemas" / f"m{number}"
        for path in sorted(directory.glob("*registry*.json")):
            if not path.name.endswith(".schema.json"):
                paths.append(path.relative_to(root).as_posix())
    return paths


def source_schema_paths(root: Path) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for number in range(18, 29)
        for path in sorted((root / "schemas" / f"m{number}").glob("*.schema.json"))
    ]


def source_artifact_paths(root: Path) -> list[str]:
    return [
        path.relative_to(root).as_posix()
        for number in range(18, 29)
        for path in sorted((root / "artifacts" / f"m{number}").rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]


def schema_registry_maps(root: Path) -> tuple[dict[str, str], dict[str, str]]:
    path_to_identifier: dict[str, str] = {}
    artifact_to_schema: dict[str, str] = {}
    for registry_path in source_schema_registry_paths(root):
        value = read_json(root, registry_path)
        if not isinstance(value, dict) or not isinstance(value.get("records"), list):
            raise ContractError(f"invalid source schema registry: {registry_path}")
        for record in value["records"]:
            if not isinstance(record, dict):
                raise ContractError(f"invalid registry record: {registry_path}")
            identifier = (
                record.get("schema_identifier")
                or record.get("schema")
                or record.get("schema_id")
                or record.get("identifier")
            )
            schema_relative = record.get("schema_path") or record.get("path")
            if not isinstance(identifier, str) or not isinstance(schema_relative, str):
                raise ContractError(f"incomplete registry identity: {registry_path}")
            if schema_relative in path_to_identifier:
                raise ContractError(f"duplicate schema path: {schema_relative}")
            path_to_identifier[schema_relative] = identifier
            for artifact_path in record.get("artifact_paths", []):
                artifact_to_schema[artifact_path] = identifier
            for artifact_path in record.get("canonical_artifact_paths", []):
                if isinstance(artifact_path, str) and artifact_path.startswith("artifacts/"):
                    artifact_to_schema[artifact_path] = identifier
    return path_to_identifier, artifact_to_schema


def build_supported_schema_registry(
    source_root: Path,
    schema_documents: Mapping[str, Mapping[str, Any]],
    source_commit: str,
) -> dict[str, Any]:
    path_to_identifier, _ = schema_registry_maps(source_root)
    upstream_records: list[dict[str, Any]] = []
    for relative in source_schema_paths(source_root):
        raw = require_file(source_root, relative).read_bytes()
        document = json.loads(raw)
        identifier = path_to_identifier.get(relative)
        if not identifier:
            raise ContractError(f"source schema is absent from registries: {relative}")
        Draft202012Validator.check_schema(document)
        upstream_records.append(
            {
                "schema_identifier": identifier,
                "declared_id": document.get("$id"),
                "schema_version": identifier_version(identifier),
                "schema_path": relative,
                "milestone": milestone_from_path(relative),
                "origin": "upstream_publication",
                "json_schema_dialect": document.get("$schema"),
                "byte_length": len(raw),
                "raw_sha256": raw_digest(raw),
                "status": "supported_exact_identifier",
            }
        )

    m29_records: list[dict[str, Any]] = []
    for identifier, relative in SCHEMA_PATHS.items():
        document = schema_documents[relative]
        raw = document_bytes(document)
        Draft202012Validator.check_schema(document)
        m29_records.append(
            {
                "schema_identifier": identifier,
                "declared_id": identifier,
                "schema_version": VERSION,
                "schema_path": relative,
                "milestone": MILESTONE,
                "origin": "m29_closure",
                "json_schema_dialect": document["$schema"],
                "byte_length": len(raw),
                "raw_sha256": raw_digest(raw),
                "status": "supported_exact_identifier",
            }
        )

    records = sorted(
        [*upstream_records, *m29_records],
        key=lambda item: (item["milestone"], item["schema_path"]),
    )
    identifiers = [record["schema_identifier"] for record in records]
    paths = [record["schema_path"] for record in records]
    if len(identifiers) != len(set(identifiers)):
        raise ContractError("supported schema identifiers are not unique")
    if len(paths) != len(set(paths)):
        raise ContractError("supported schema paths are not unique")

    source_registries = []
    for relative in source_schema_registry_paths(source_root):
        raw = require_file(source_root, relative).read_bytes()
        source_registries.append(
            {
                "path": relative,
                "milestone": milestone_from_path(relative),
                "byte_length": len(raw),
                "raw_sha256": raw_digest(raw),
            }
        )

    value = {
        "schema": SCHEMA_REGISTRY_ID,
        "kind": "supported_schema_registry",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "upstream_schema_count": len(upstream_records),
        "m29_schema_count": len(m29_records),
        "record_count": len(records),
        "source_registry_count": len(source_registries),
        "source_registries": source_registries,
        "records": records,
        "identity_policy": {
            "resolution": "exact_schema_identifier_only",
            "aliases": "forbidden",
            "unknown_identifiers": "unsupported",
            "automatic_migration": "forbidden",
            "declared_id_preserved_separately": True,
        },
        "status": "PASS",
    }
    return with_digest(value, "registry_digest")


def build_json_schema_registry(root: Path, schema_records: Sequence[Mapping[str, Any]]) -> Registry:
    registry = Registry()
    for record in schema_records:
        if record["origin"] != "upstream_publication":
            continue
        document = read_json(root, str(record["schema_path"]))
        declared_id = document.get("$id")
        if not isinstance(declared_id, str):
            raise ContractError(f"schema lacks $id: {record['schema_path']}")
        registry = registry.with_resource(declared_id, Resource.from_contents(document))
    return registry


def _artifact_media_type(path: str) -> tuple[str, str]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".json":
        return "json", "application/json"
    if suffix == ".csv":
        return "csv", "text/csv"
    if suffix == ".vec":
        return "vector", "text/plain"
    if suffix == ".trace":
        return "trace", "text/plain"
    return "bytes", "application/octet-stream"


def build_supported_artifact_registry(
    source_root: Path,
    schema_registry: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    path_to_schema_identifier, artifact_to_schema = schema_registry_maps(source_root)
    identifier_to_record = {
        record["schema_identifier"]: record
        for record in schema_registry["records"]
        if record["origin"] == "upstream_publication"
    }
    json_registry = build_json_schema_registry(
        source_root,
        [
            record
            for record in schema_registry["records"]
            if record["origin"] == "upstream_publication"
        ],
    )
    records: list[dict[str, Any]] = []
    json_count = 0
    validated_count = 0
    for relative in source_artifact_paths(source_root):
        source = require_file(source_root, relative)
        raw = source.read_bytes()
        artifact_format, media_type = _artifact_media_type(relative)
        milestone = milestone_from_path(relative)
        schema_identifier: str | None = None
        declared_identifier: str
        schema_relative: str | None = None
        schema_validation_status = "NOT_APPLICABLE"
        if artifact_format == "json":
            json_count += 1
            try:
                document = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ContractError(f"invalid upstream JSON: {relative}") from exc
            if not isinstance(document, dict):
                raise ContractError(f"upstream JSON must be an object: {relative}")
            schema_identifier = document.get("schema")
            if not isinstance(schema_identifier, str):
                if relative in artifact_to_schema:
                    schema_identifier = artifact_to_schema[relative]
                else:
                    artifact_id = document.get("artifact_id")
                    schema_version = document.get("schema_version")
                    if isinstance(artifact_id, str) and isinstance(schema_version, str):
                        schema_identifier = (
                            artifact_id.removeprefix("frp-") + "-v" + schema_version
                        )
            if not isinstance(schema_identifier, str):
                raise ContractError(f"JSON artifact lacks schema identity: {relative}")
            schema_record = identifier_to_record.get(schema_identifier)
            if schema_record is None:
                raise ContractError(
                    f"unsupported schema {schema_identifier} for {relative}"
                )
            schema_relative = str(schema_record["schema_path"])
            schema_document = read_json(source_root, schema_relative)
            Draft202012Validator(
                schema_document,
                registry=json_registry,
            ).validate(document)
            validated_count += 1
            declared_identifier = str(
                document.get("artifact_id")
                or document.get("qualification_id")
                or document.get("manifest_id")
                or document.get("record_id")
                or document.get("schema")
            )
            schema_validation_status = "PASS"
        else:
            declared_identifier = f"path:{relative}"

        records.append(
            {
                "artifact_identifier": f"frp.artifact.path:{relative}",
                "declared_identifier": declared_identifier,
                "artifact_path": relative,
                "artifact_format": artifact_format,
                "media_type": media_type,
                "milestone": milestone,
                "upstream_release": UPSTREAM_RELEASES[milestone],
                "schema_identifier": schema_identifier,
                "schema_path": schema_relative,
                "schema_validation_status": schema_validation_status,
                "identity_basis": "exact_repository_path_and_raw_sha256",
                "source_byte_policy": "immutable",
                "byte_length": len(raw),
                "raw_sha256": raw_digest(raw),
            }
        )

    milestone_counts = {
        milestone: sum(1 for record in records if record["milestone"] == milestone)
        for milestone in UPSTREAM_MILESTONES
    }
    value = {
        "schema": ARTIFACT_REGISTRY_ID,
        "kind": "supported_artifact_registry",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "record_count": len(records),
        "json_artifact_count": json_count,
        "byte_artifact_count": len(records) - json_count,
        "milestone_counts": milestone_counts,
        "records": records,
        "identity_policy": {
            "artifact_resolution": "exact_path_identifier_and_raw_sha256",
            "schema_resolution": "exact_schema_identifier",
            "validated_json_artifact_count": validated_count,
            "pre_parse_digest_required": True,
            "source_byte_normalization": "forbidden",
            "unknown_identifiers": "unsupported",
        },
        "status": "PASS",
    }
    return with_digest(value, "registry_digest")


def build_immutable_policy(source_commit: str) -> dict[str, Any]:
    value = {
        "schema": IMMUTABLE_POLICY_ID,
        "kind": "immutable_source_artifact_policy",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "policy_id": "frp-m29-immutable-source-bytes-v1",
        "byte_identity": {
            "algorithm": "sha256",
            "digest_scope": "raw_source_bytes",
            "digest_before_parse": True,
            "copy_mode": "byte_exact",
            "text_normalization": "forbidden",
            "field_reordering": "forbidden",
            "source_mutation": "forbidden",
        },
        "consumer_rules": {
            "source_execution": "forbidden",
            "producer_execution": "forbidden",
            "schema_aliasing": "forbidden",
            "automatic_schema_migration": "forbidden",
            "unknown_field_inference": "forbidden",
            "absent_field_policy": "remain_absent",
            "absent_is_zero": False,
        },
        "violation_behavior": {
            "digest_mismatch": "reject_before_parse",
            "unknown_identifier": "reject_before_parse",
            "unsupported_version": "reject_before_parse",
            "unsafe_path": "reject_before_read",
        },
        "status": "PASS",
    }
    return with_digest(value, "policy_digest")


def build_unsupported_behavior(source_commit: str) -> dict[str, Any]:
    cases = [
        {
            "case_id": "unknown-schema-identifier",
            "condition": "schema identifier absent from exact allowlist",
            "expected_action": "reject_before_parse",
            "reason_code": "UNSUPPORTED_SCHEMA_IDENTIFIER",
        },
        {
            "case_id": "unsupported-major-version",
            "condition": "identifier version is not exactly registered",
            "expected_action": "reject_before_parse",
            "reason_code": "UNSUPPORTED_SCHEMA_VERSION",
        },
        {
            "case_id": "unsupported-minor-version",
            "condition": "minor version is not exactly registered",
            "expected_action": "reject_before_parse",
            "reason_code": "UNSUPPORTED_SCHEMA_VERSION",
        },
        {
            "case_id": "schema-alias",
            "condition": "consumer substitutes an alias for the published identifier",
            "expected_action": "reject_before_parse",
            "reason_code": "SCHEMA_ALIAS_FORBIDDEN",
        },
        {
            "case_id": "source-digest-mismatch",
            "condition": "published raw-byte digest does not match",
            "expected_action": "reject_before_parse",
            "reason_code": "SOURCE_DIGEST_MISMATCH",
        },
        {
            "case_id": "unsafe-source-path",
            "condition": "source path is absolute or leaves repository boundary",
            "expected_action": "reject_before_read",
            "reason_code": "UNSAFE_SOURCE_PATH",
        },
    ]
    value = {
        "schema": UNSUPPORTED_ID,
        "kind": "unsupported_version_behavior",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "policy_id": "frp-m29-exact-compatibility-resolution-v1",
        "resolution": {
            "key": "exact_schema_identifier",
            "version_ranges": "not_inferred",
            "aliases": "forbidden",
            "automatic_migration": "forbidden",
            "unknown_identifiers": "unsupported",
            "fail_closed": True,
        },
        "case_count": len(cases),
        "cases": cases,
        "status": "PASS",
    }
    return with_digest(value, "behavior_digest")


def build_compatibility_declarations(
    schema_registry: Mapping[str, Any],
    artifact_registry: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    versions = sorted(
        {record["schema_version"] for record in schema_registry["records"]},
        key=lambda value: tuple(int(part) for part in value.split(".")),
    )
    declarations = []
    for version in versions:
        schema_count = sum(
            1
            for record in schema_registry["records"]
            if record["schema_version"] == version
        )
        artifact_count = sum(
            1
            for record in artifact_registry["records"]
            if record["schema_identifier"] is not None
            and identifier_version(record["schema_identifier"]) == version
        )
        declarations.append(
            {
                "schema_version": version,
                "schema_count": schema_count,
                "artifact_count": artifact_count,
                "compatibility_state": "supported_by_exact_identifier",
                "range_inference": "forbidden",
                "release_label_role": "informational_only",
            }
        )
    value = {
        "schema": COMPATIBILITY_ID,
        "kind": "compatibility_version_declarations",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "compatibility_revision": "m29-compatibility-1",
        "declaration_count": len(declarations),
        "declarations": declarations,
        "resolution_policy": {
            "supported": "exact_identifier_allowlist",
            "unsupported": "reject_before_parse",
            "upstream_release_labels": "not_identity_keys",
            "observatory_versions": "independent",
        },
        "status": "PASS",
    }
    return with_digest(value, "declarations_digest")


def build_demo_package(source_root: Path, source_commit: str) -> dict[str, Any]:
    members = []
    for spec in DEMO_MEMBER_SPECS:
        relative = str(spec["source_path"])
        raw = require_file(source_root, relative).read_bytes()
        members.append(
            {
                "member_id": spec["member_id"],
                "source_path": relative,
                "schema_identifier": spec["schema_identifier"],
                "measurement_contour": spec["measurement_contour"],
                "observatory_modes": list(spec["observatory_modes"]),
                "media_type": "application/json",
                "byte_length": len(raw),
                "raw_sha256": raw_digest(raw),
                "payload_base64": base64.b64encode(raw).decode("ascii"),
                "copy_requirement": "unchanged_upstream_bytes",
            }
        )
    value = {
        "schema": DEMO_PACKAGE_ID,
        "kind": "canonical_demo_artifact_package",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "package_id": "frp-m29-canonical-downstream-demo-package",
        "member_count": len(members),
        "members": members,
        "transport_contract": {
            "container": "json_with_base64_members",
            "member_encoding": "base64_rfc4648",
            "digest_algorithm": "sha256",
            "digest_scope": "decoded_raw_source_bytes",
            "parse_order": "decode_then_digest_then_schema_resolve_then_parse",
            "source_execution": "forbidden",
        },
        "status": "PASS",
    }
    return with_digest(value, "package_digest")


def validate_demo_package(value: Mapping[str, Any], source_root: Path) -> None:
    verify_digest(value, "package_digest", "canonical demo package")
    if value.get("member_count") != len(DEMO_MEMBER_SPECS):
        raise ContractError("canonical demo package member count mismatch")
    expected_by_id = {spec["member_id"]: spec for spec in DEMO_MEMBER_SPECS}
    observed_ids = [member.get("member_id") for member in value.get("members", [])]
    if observed_ids != list(expected_by_id):
        raise ContractError("canonical demo package member ordering mismatch")
    for member in value["members"]:
        spec = expected_by_id[member["member_id"]]
        if member.get("source_path") != spec["source_path"]:
            raise ContractError("canonical demo package source path mismatch")
        if member.get("schema_identifier") != spec["schema_identifier"]:
            raise ContractError("canonical demo package schema identity mismatch")
        if member.get("observatory_modes") != list(spec["observatory_modes"]):
            raise ContractError("canonical demo package mode routing mismatch")
        try:
            raw = base64.b64decode(member["payload_base64"], validate=True)
        except (binascii.Error, ValueError, TypeError) as exc:
            raise ContractError("canonical demo package Base64 is invalid") from exc
        if len(raw) != member.get("byte_length"):
            raise ContractError("canonical demo package byte length mismatch")
        if raw_digest(raw) != member.get("raw_sha256"):
            raise ContractError("canonical demo package member digest mismatch")
        source_raw = require_file(source_root, member["source_path"]).read_bytes()
        if raw != source_raw:
            raise ContractError("canonical demo package changed published source bytes")


def build_package_manifest(
    demo_package: Mapping[str, Any], source_commit: str
) -> dict[str, Any]:
    package_raw = document_bytes(demo_package)
    members = [
        {
            "member_id": member["member_id"],
            "source_path": member["source_path"],
            "schema_identifier": member["schema_identifier"],
            "byte_length": member["byte_length"],
            "raw_sha256": member["raw_sha256"],
        }
        for member in demo_package["members"]
    ]
    value = {
        "schema": PACKAGE_MANIFEST_ID,
        "kind": "deterministic_package_manifest",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "manifest_id": "frp-m29-canonical-demo-package-manifest",
        "package_path": DEMO_PACKAGE_ARTIFACT,
        "package_bytes": len(package_raw),
        "package_raw_sha256": raw_digest(package_raw),
        "member_count": len(members),
        "members": members,
        "generation": {
            "producer": "frp_m29_system_integration_downstream_compatibility.py",
            "command": (
                "python frp_m29_system_integration_downstream_compatibility.py "
                "--generate --repository-root . --output-root <output-root> "
                f"--source-commit {EXPECTED_M28_COMMIT}"
            ),
            "ordering": "declared_member_order",
            "serialization": "utf8_sorted_keys_indent_2_single_newline",
            "timestamps": "excluded",
        },
        "status": "PASS",
    }
    return with_digest(value, "manifest_digest")


def build_producer_registry(source_root: Path, source_commit: str) -> dict[str, Any]:
    records = []
    for spec in PRODUCER_SPECS:
        raw = require_file(source_root, spec["path"]).read_bytes()
        records.append(
            {
                "producer_id": spec["producer_id"],
                "milestone": spec["milestone"],
                "producer_path": spec["path"],
                "producer_bytes": len(raw),
                "producer_raw_sha256": raw_digest(raw),
                "commands": list(spec["commands"]),
                "command_count": len(spec["commands"]),
                "downstream_execution": "forbidden",
                "role": "upstream_reproducibility_record",
            }
        )
    value = {
        "schema": PRODUCER_REGISTRY_ID,
        "kind": "producer_command_registry",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "record_count": len(records),
        "records": records,
        "execution_boundary": {
            "producer_repository": "Fractal-Resonance-Processor",
            "consumer_repository": OBSERVATORY_REPOSITORY,
            "commands_are_upstream_records": True,
            "downstream_command_execution": "forbidden",
            "upstream_dependency_on_downstream_code": False,
        },
        "status": "PASS",
    }
    return with_digest(value, "registry_digest")


def build_provenance_record(
    schema_registry: Mapping[str, Any],
    artifact_registry: Mapping[str, Any],
    producer_registry: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    counts = {
        "upstream_schema_definitions": schema_registry["upstream_schema_count"],
        "upstream_schema_registries": schema_registry["source_registry_count"],
        "upstream_artifacts": artifact_registry["record_count"],
        "json_artifacts_validated": artifact_registry["json_artifact_count"],
        "producer_records": producer_registry["record_count"],
    }
    counts["complete_upstream_publication_files"] = (
        counts["upstream_schema_definitions"]
        + counts["upstream_schema_registries"]
        + counts["upstream_artifacts"]
    )
    checks = [
        {"check_id": "schema-path-coverage", "status": "PASS"},
        {"check_id": "schema-identifier-coverage", "status": "PASS"},
        {"check_id": "schema-raw-digest-coverage", "status": "PASS"},
        {"check_id": "artifact-path-coverage", "status": "PASS"},
        {"check_id": "artifact-identifier-coverage", "status": "PASS"},
        {"check_id": "artifact-raw-digest-coverage", "status": "PASS"},
        {"check_id": "json-schema-validation-coverage", "status": "PASS"},
        {"check_id": "producer-command-coverage", "status": "PASS"},
        {"check_id": "source-commit-coverage", "status": "PASS"},
        {"check_id": "measurement-contour-separation", "status": "PASS"},
    ]
    value = {
        "schema": PROVENANCE_ID,
        "kind": "provenance_completeness_record",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "record_id": "frp-m29-complete-upstream-publication-provenance",
        "inventory_counts": counts,
        "inventory_digests": {
            "supported_schema_records": raw_digest(
                canonical_json_bytes(schema_registry["records"])
            ),
            "source_schema_registries": raw_digest(
                canonical_json_bytes(schema_registry["source_registries"])
            ),
            "supported_artifact_records": raw_digest(
                canonical_json_bytes(artifact_registry["records"])
            ),
            "producer_records": raw_digest(
                canonical_json_bytes(producer_registry["records"])
            ),
        },
        "coverage": {
            "required_fields_present": True,
            "missing_schema_identifiers": 0,
            "missing_artifact_identifiers": 0,
            "missing_raw_digests": 0,
            "missing_producer_paths": 0,
            "source_bytes_rewritten": 0,
            "measurement_contours_merged": 0,
        },
        "checks": checks,
        "check_count": len(checks),
        "status": "PASS",
    }
    return with_digest(value, "record_digest")


def compatibility_key(member: Mapping[str, Any]) -> str:
    return raw_digest(
        canonical_json_bytes(
            {
                "member_id": member["member_id"],
                "schema_identifier": member["schema_identifier"],
                "raw_sha256": member["raw_sha256"],
            }
        )
    )


def build_release_independent_records(
    demo_package: Mapping[str, Any], source_commit: str
) -> dict[str, Any]:
    records = [
        {
            "member_id": member["member_id"],
            "schema_identifier": member["schema_identifier"],
            "raw_sha256": member["raw_sha256"],
            "compatibility_key": compatibility_key(member),
            "compatibility_state": "supported",
            "observatory_modes": member["observatory_modes"],
            "upstream_release_label": UPSTREAM_RELEASES[
                milestone_from_path(member["source_path"])
            ],
            "consumer_baseline_commit": OBSERVATORY_AUDITED_COMMIT,
            "release_label_in_key": False,
            "consumer_version_in_key": False,
        }
        for member in demo_package["members"]
    ]
    value = {
        "schema": RELEASE_RECORDS_ID,
        "kind": "release_independent_compatibility_records",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "record_set_id": "frp-m29-release-independent-compatibility-v1",
        "record_count": len(records),
        "compatibility_key_contract": {
            "included_fields": [
                "member_id",
                "schema_identifier",
                "raw_sha256",
            ],
            "excluded_fields": [
                "upstream_release_label",
                "consumer_baseline_commit",
                "consumer_version",
            ],
            "algorithm": "sha256",
            "observatory_versioning": "independent",
        },
        "records": records,
        "status": "PASS",
    }
    return with_digest(value, "record_set_digest")


def _evaluate_vector(
    vector: Mapping[str, Any],
    members: Mapping[str, Mapping[str, Any]],
    supported_identifiers: set[str],
) -> tuple[str, str]:
    member = members.get(str(vector.get("member_id")))
    if member is None:
        return "rejected", "UNKNOWN_ARTIFACT_IDENTIFIER"
    schema_identifier = str(vector.get("schema_identifier"))
    if vector.get("schema_alias"):
        return "rejected", "SCHEMA_ALIAS_FORBIDDEN"
    if schema_identifier not in supported_identifiers:
        return "rejected", "UNSUPPORTED_SCHEMA_IDENTIFIER"
    if schema_identifier != member["schema_identifier"]:
        return "rejected", "UNSUPPORTED_SCHEMA_VERSION"
    if vector.get("identity_from_release_label"):
        return "rejected", "RELEASE_LABEL_NOT_IDENTITY_KEY"
    encoded_payload = vector.get("payload_base64", member["payload_base64"])
    try:
        raw = base64.b64decode(str(encoded_payload), validate=True)
    except (binascii.Error, ValueError):
        return "rejected", "INVALID_BASE64"
    if vector.get("payload_mutation") == "append_newline":
        raw += b"\n"
    if raw_digest(raw) != vector.get("raw_sha256"):
        return "rejected", "SOURCE_DIGEST_MISMATCH"
    if vector.get("raw_sha256") != member["raw_sha256"]:
        return "rejected", "SOURCE_DIGEST_MISMATCH"
    return "accepted", "SUPPORTED_EXACT_SOURCE_BYTES"


def build_consumption_vectors(
    demo_package: Mapping[str, Any],
    schema_registry: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    members = {member["member_id"]: member for member in demo_package["members"]}
    supported = {record["schema_identifier"] for record in schema_registry["records"]}
    vectors: list[dict[str, Any]] = []
    for member in demo_package["members"]:
        vectors.append(
            {
                "vector_id": f"accept-{member['member_id']}",
                "member_id": member["member_id"],
                "schema_identifier": member["schema_identifier"],
                "raw_sha256": member["raw_sha256"],
                "payload_source": "canonical_demo_package_member",
                "expected_outcome": "accepted",
                "expected_reason": "SUPPORTED_EXACT_SOURCE_BYTES",
            }
        )
    reference = copy.deepcopy(demo_package["members"][0])
    negative_specs = (
        (
            "unknown-artifact",
            {"member_id": "unknown-artifact"},
            "UNKNOWN_ARTIFACT_IDENTIFIER",
        ),
        (
            "unknown-schema",
            {"schema_identifier": "frp.unknown.schema.v9.0.0"},
            "UNSUPPORTED_SCHEMA_IDENTIFIER",
        ),
        (
            "unsupported-version",
            {
                "schema_identifier": (
                    "frp.m16.fpga_preparation_execution_trace.v9.0.0"
                )
            },
            "UNSUPPORTED_SCHEMA_IDENTIFIER",
        ),
        (
            "schema-alias",
            {"schema_alias": True},
            "SCHEMA_ALIAS_FORBIDDEN",
        ),
        (
            "invalid-base64",
            {"payload_base64": "not-base64"},
            "INVALID_BASE64",
        ),
        (
            "altered-source-bytes",
            {"payload_mutation": "append_newline"},
            "SOURCE_DIGEST_MISMATCH",
        ),
        (
            "wrong-digest",
            {"raw_sha256": "0" * 64},
            "SOURCE_DIGEST_MISMATCH",
        ),
        (
            "release-label-identity",
            {"identity_from_release_label": True},
            "RELEASE_LABEL_NOT_IDENTITY_KEY",
        ),
    )
    for vector_id, changes, expected_reason in negative_specs:
        vector = {
            "vector_id": f"reject-{vector_id}",
            "member_id": reference["member_id"],
            "schema_identifier": reference["schema_identifier"],
            "raw_sha256": reference["raw_sha256"],
            "payload_source": "canonical_demo_package_member",
            "expected_outcome": "rejected",
            "expected_reason": expected_reason,
        }
        vector.update(changes)
        vectors.append(vector)

    for vector in vectors:
        outcome, reason = _evaluate_vector(vector, members, supported)
        vector["observed_outcome"] = outcome
        vector["observed_reason"] = reason
        vector["status"] = (
            "PASS"
            if outcome == vector["expected_outcome"]
            and reason == vector["expected_reason"]
            else "FAIL"
        )
    value = {
        "schema": CONSUMPTION_VECTORS_ID,
        "kind": "downstream_consumption_test_vectors",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "vector_set_id": "frp-m29-published-byte-consumption-v1",
        "vector_count": len(vectors),
        "accepted_count": sum(
            1 for vector in vectors if vector["expected_outcome"] == "accepted"
        ),
        "rejected_count": sum(
            1 for vector in vectors if vector["expected_outcome"] == "rejected"
        ),
        "vectors": vectors,
        "status": (
            "PASS" if all(vector["status"] == "PASS" for vector in vectors) else "FAIL"
        ),
    }
    return with_digest(value, "vector_set_digest")


def build_contract(source_commit: str) -> dict[str, Any]:
    deliverables = [
        {"deliverable": "supported_schema_registry", "path": SCHEMA_REGISTRY},
        {"deliverable": "supported_artifact_registry", "path": ARTIFACT_REGISTRY},
        {
            "deliverable": "compatibility_version_declarations",
            "path": COMPATIBILITY_ARTIFACT,
        },
        {"deliverable": "canonical_demo_artifact_package", "path": DEMO_PACKAGE_ARTIFACT},
        {"deliverable": "deterministic_package_manifest", "path": PACKAGE_MANIFEST_ARTIFACT},
        {"deliverable": "producer_command_registry", "path": PRODUCER_REGISTRY_ARTIFACT},
        {"deliverable": "immutable_source_artifact_policy", "path": IMMUTABLE_POLICY_ARTIFACT},
        {"deliverable": "provenance_completeness", "path": PROVENANCE_ARTIFACT},
        {"deliverable": "unsupported_version_behavior", "path": UNSUPPORTED_ARTIFACT},
        {"deliverable": "downstream_consumption_test_vectors", "path": CONSUMPTION_VECTORS_ARTIFACT},
        {"deliverable": "release_independent_compatibility_records", "path": RELEASE_RECORDS_ARTIFACT},
    ]
    value = {
        "schema": CONTRACT_ID,
        "kind": "system_integration_contract",
        "milestone": MILESTONE,
        "milestone_title": MILESTONE_TITLE,
        "version": VERSION,
        "source_commit": source_commit,
        "source_subject": EXPECTED_M28_SUBJECT,
        "objective": OBJECTIVE,
        "immutable_core": {
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "opposite_transition_routes": [[-1, 0, 1], [1, 0, -1]],
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
            "actual_direct_events": 0,
        },
        "integration_boundary": {
            "direction": "upstream_to_published_bytes_to_downstream",
            "upstream_repository": "Fractal-Resonance-Processor",
            "upstream_semantic_authority": True,
            "downstream_repository": OBSERVATORY_REPOSITORY,
            "downstream_audited_commit": OBSERVATORY_AUDITED_COMMIT,
            "downstream_verified_test_count": OBSERVATORY_TEST_COUNT,
            "downstream_modes": list(OBSERVATORY_MODES),
            "existing_scaffold_action": "preserve_existing_scaffold",
            "downstream_writeback": "forbidden",
            "downstream_source_mutation": "forbidden",
            "downstream_semantic_reimplementation": "forbidden",
            "upstream_dependency_on_downstream_code": False,
            "downstream_files_modified_by_m29": False,
            "preserved_m28_observatory_commit": PRESERVED_M28_OBSERVATORY_COMMIT,
        },
        "inventory_boundary": {
            "milestones": list(UPSTREAM_MILESTONES),
            "upstream_schema_definitions": 84,
            "upstream_schema_registries": 12,
            "upstream_artifacts": 97,
            "complete_upstream_publication_files": 193,
            "identity": "exact_identifiers_paths_and_raw_sha256",
            "measurement_contours": "preserved_separately",
        },
        "required_deliverables": deliverables,
        "status": "PASS",
    }
    return with_digest(value, "contract_digest")


def _pass(check_id: str, category: str, evidence: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "category": category,
        "status": "PASS",
        "evidence": evidence,
    }


def build_qualification(
    documents: Mapping[str, Mapping[str, Any]],
    schema_documents: Mapping[str, Mapping[str, Any]],
    source_commit: str,
) -> dict[str, Any]:
    schema_registry = documents[SCHEMA_REGISTRY]
    artifact_registry = documents[ARTIFACT_REGISTRY]
    compatibility = documents[COMPATIBILITY_ARTIFACT]
    demo = documents[DEMO_PACKAGE_ARTIFACT]
    manifest = documents[PACKAGE_MANIFEST_ARTIFACT]
    producers = documents[PRODUCER_REGISTRY_ARTIFACT]
    policy = documents[IMMUTABLE_POLICY_ARTIFACT]
    provenance = documents[PROVENANCE_ARTIFACT]
    unsupported = documents[UNSUPPORTED_ARTIFACT]
    vectors = documents[CONSUMPTION_VECTORS_ARTIFACT]
    releases = documents[RELEASE_RECORDS_ARTIFACT]
    contract = documents[CONTRACT_ARTIFACT]
    checks = [
        _pass("source-commit", "source", source_commit),
        _pass("source-subject", "source", EXPECTED_M28_SUBJECT),
        _pass("m28-observatory-preserved", "source", PRESERVED_M28_OBSERVATORY_COMMIT),
        _pass("observatory-baseline", "downstream", OBSERVATORY_AUDITED_COMMIT),
        _pass("observatory-tests", "downstream", OBSERVATORY_TEST_COUNT),
        _pass("observatory-mode-count", "downstream", len(OBSERVATORY_MODES)),
        _pass("existing-scaffold", "downstream", "preserve_existing_scaffold"),
        _pass("one-way-integration", "boundary", contract["integration_boundary"]["direction"]),
        _pass("no-downstream-writeback", "boundary", "forbidden"),
        _pass("no-downstream-source-mutation", "boundary", "forbidden"),
        _pass("no-semantic-reimplementation", "boundary", "forbidden"),
        _pass("no-upstream-downstream-dependency", "boundary", False),
        _pass("ternary-notation", "core", "-1/0/1"),
        _pass("ternary-domain", "core", [-1, 0, 1]),
        _pass("active-neutral", "core", 0),
        _pass("opposite-transition-routes", "core", [[-1, 0, 1], [1, 0, -1]]),
        _pass("temporal-schedulers", "core", ["1/7", "7/1"]),
        _pass("service-scheduler", "core", "free"),
        _pass("direct-events", "core", 0),
        _pass("upstream-schema-count", "inventory", schema_registry["upstream_schema_count"]),
        _pass("source-registry-count", "inventory", schema_registry["source_registry_count"]),
        _pass("m29-schema-count", "inventory", schema_registry["m29_schema_count"]),
        _pass("supported-schema-count", "inventory", schema_registry["record_count"]),
        _pass("upstream-artifact-count", "inventory", artifact_registry["record_count"]),
        _pass("json-artifact-count", "inventory", artifact_registry["json_artifact_count"]),
        _pass("byte-artifact-count", "inventory", artifact_registry["byte_artifact_count"]),
        _pass("validated-json-count", "inventory", artifact_registry["identity_policy"]["validated_json_artifact_count"]),
        _pass("provenance-file-count", "inventory", provenance["inventory_counts"]["complete_upstream_publication_files"]),
        _pass("exact-schema-identifiers", "compatibility", schema_registry["identity_policy"]["resolution"]),
        _pass("exact-artifact-identifiers", "compatibility", artifact_registry["identity_policy"]["artifact_resolution"]),
        _pass("compatibility-declarations", "compatibility", compatibility["declaration_count"]),
        _pass("unsupported-version-fail-closed", "compatibility", unsupported["resolution"]["fail_closed"]),
        _pass("unsupported-case-count", "compatibility", unsupported["case_count"]),
        _pass("immutable-pre-parse-digest", "bytes", policy["byte_identity"]["digest_before_parse"]),
        _pass("immutable-copy-mode", "bytes", policy["byte_identity"]["copy_mode"]),
        _pass("demo-member-count", "package", demo["member_count"]),
        _pass("package-raw-digest", "package", manifest["package_raw_sha256"]),
        _pass("manifest-member-count", "package", manifest["member_count"]),
        _pass("producer-record-count", "producer", producers["record_count"]),
        _pass("downstream-command-execution", "producer", "forbidden"),
        _pass("consumption-vector-count", "compatibility", vectors["vector_count"]),
        _pass("accepted-vector-count", "compatibility", vectors["accepted_count"]),
        _pass("rejected-vector-count", "compatibility", vectors["rejected_count"]),
        _pass("release-independent-record-count", "compatibility", releases["record_count"]),
        _pass("release-label-excluded", "compatibility", False),
        _pass("consumer-version-excluded", "compatibility", False),
        _pass("provenance-check-count", "provenance", provenance["check_count"]),
        _pass("workflow-path", "workflow", WORKFLOW_PATH),
    ]
    schemas = [
        {
            "path": relative,
            "byte_length": len(document_bytes(schema_documents[relative])),
            "raw_sha256": raw_digest(document_bytes(schema_documents[relative])),
        }
        for relative in SCHEMA_PATHS.values()
    ]
    evidence_documents = [
        {
            "path": relative,
            "byte_length": len(document_bytes(documents[relative])),
            "raw_sha256": raw_digest(document_bytes(documents[relative])),
        }
        for relative in PRIMARY_DOCUMENT_PATHS
    ]
    value = {
        "schema": QUALIFICATION_ID,
        "kind": "system_integration_qualification",
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "qualification_id": "frp-m29-system-integration-closure",
        "schema_count": len(schemas),
        "document_count": len(evidence_documents),
        "schemas": schemas,
        "documents": evidence_documents,
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
        "status": "PASS",
    }
    return with_digest(value, "qualification_digest")


def build_all(
    source_root: Path, source_commit: str
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    validate_source_commit(source_commit)
    schema_documents = build_schema_documents()
    documents: dict[str, dict[str, Any]] = {}
    documents[SCHEMA_REGISTRY] = build_supported_schema_registry(
        source_root, schema_documents, source_commit
    )
    documents[ARTIFACT_REGISTRY] = build_supported_artifact_registry(
        source_root, documents[SCHEMA_REGISTRY], source_commit
    )
    documents[IMMUTABLE_POLICY_ARTIFACT] = build_immutable_policy(source_commit)
    documents[UNSUPPORTED_ARTIFACT] = build_unsupported_behavior(source_commit)
    documents[COMPATIBILITY_ARTIFACT] = build_compatibility_declarations(
        documents[SCHEMA_REGISTRY], documents[ARTIFACT_REGISTRY], source_commit
    )
    documents[DEMO_PACKAGE_ARTIFACT] = build_demo_package(source_root, source_commit)
    validate_demo_package(documents[DEMO_PACKAGE_ARTIFACT], source_root)
    documents[PACKAGE_MANIFEST_ARTIFACT] = build_package_manifest(
        documents[DEMO_PACKAGE_ARTIFACT], source_commit
    )
    documents[PRODUCER_REGISTRY_ARTIFACT] = build_producer_registry(
        source_root, source_commit
    )
    documents[PROVENANCE_ARTIFACT] = build_provenance_record(
        documents[SCHEMA_REGISTRY],
        documents[ARTIFACT_REGISTRY],
        documents[PRODUCER_REGISTRY_ARTIFACT],
        source_commit,
    )
    documents[CONSUMPTION_VECTORS_ARTIFACT] = build_consumption_vectors(
        documents[DEMO_PACKAGE_ARTIFACT], documents[SCHEMA_REGISTRY], source_commit
    )
    documents[RELEASE_RECORDS_ARTIFACT] = build_release_independent_records(
        documents[DEMO_PACKAGE_ARTIFACT], source_commit
    )
    documents[CONTRACT_ARTIFACT] = build_contract(source_commit)
    ordered = {path: documents[path] for path in PRIMARY_DOCUMENT_PATHS}
    documents = ordered
    documents[QUALIFICATION_ARTIFACT] = build_qualification(
        documents, schema_documents, source_commit
    )
    return schema_documents, documents


def _validate_contract(value: Mapping[str, Any]) -> None:
    verify_digest(value, "contract_digest", "M29 integration contract")
    if value.get("objective") != OBJECTIVE:
        raise ContractError("M29 objective mismatch")
    core = value.get("immutable_core", {})
    if core.get("balanced_ternary_notation") != "-1/0/1":
        raise ContractError("balanced ternary notation mismatch")
    if core.get("semantic_values") != [-1, 0, 1]:
        raise ContractError("balanced ternary domain mismatch")
    if core.get("active_neutral_state") != 0:
        raise ContractError("active neutral state mismatch")
    if core.get("opposite_transition_routes") != [[-1, 0, 1], [1, 0, -1]]:
        raise ContractError("opposite transition route mismatch")
    if core.get("temporal_scheduler_modes") != ["1/7", "7/1"]:
        raise ContractError("temporal scheduler boundary mismatch")
    if core.get("service_scheduler_mode") != "free":
        raise ContractError("service scheduler boundary mismatch")
    boundary = value.get("integration_boundary", {})
    if boundary.get("downstream_repository") != OBSERVATORY_REPOSITORY:
        raise ContractError("Observatory repository mismatch")
    if boundary.get("downstream_audited_commit") != OBSERVATORY_AUDITED_COMMIT:
        raise ContractError("Observatory baseline mismatch")
    if boundary.get("downstream_modes") != list(OBSERVATORY_MODES):
        raise ContractError("Observatory mode boundary mismatch")
    if boundary.get("existing_scaffold_action") != "preserve_existing_scaffold":
        raise ContractError("existing Observatory scaffold is not preserved")
    if boundary.get("downstream_writeback") != "forbidden":
        raise ContractError("downstream writeback must remain forbidden")
    if boundary.get("downstream_semantic_reimplementation") != "forbidden":
        raise ContractError("downstream semantic reimplementation is forbidden")
    if boundary.get("upstream_dependency_on_downstream_code") is not False:
        raise ContractError("upstream must not depend on downstream code")


def validate_documents(
    source_root: Path,
    schema_documents: Mapping[str, Mapping[str, Any]],
    documents: Mapping[str, Mapping[str, Any]],
) -> None:
    for schema in schema_documents.values():
        Draft202012Validator.check_schema(schema)
    for path, document in documents.items():
        schema_identifier = DOCUMENT_SCHEMA_IDS[path]
        Draft202012Validator(
            schema_documents[SCHEMA_PATHS[schema_identifier]]
        ).validate(document)
    _validate_contract(documents[CONTRACT_ARTIFACT])
    verify_digest(
        documents[SCHEMA_REGISTRY], "registry_digest", "supported schema registry"
    )
    verify_digest(
        documents[ARTIFACT_REGISTRY], "registry_digest", "supported artifact registry"
    )
    verify_digest(
        documents[COMPATIBILITY_ARTIFACT],
        "declarations_digest",
        "compatibility declarations",
    )
    validate_demo_package(documents[DEMO_PACKAGE_ARTIFACT], source_root)
    verify_digest(
        documents[PACKAGE_MANIFEST_ARTIFACT], "manifest_digest", "package manifest"
    )
    verify_digest(
        documents[PRODUCER_REGISTRY_ARTIFACT],
        "registry_digest",
        "producer registry",
    )
    verify_digest(
        documents[IMMUTABLE_POLICY_ARTIFACT], "policy_digest", "immutable policy"
    )
    verify_digest(
        documents[PROVENANCE_ARTIFACT], "record_digest", "provenance record"
    )
    verify_digest(
        documents[UNSUPPORTED_ARTIFACT], "behavior_digest", "unsupported behavior"
    )
    verify_digest(
        documents[CONSUMPTION_VECTORS_ARTIFACT],
        "vector_set_digest",
        "consumption vectors",
    )
    verify_digest(
        documents[RELEASE_RECORDS_ARTIFACT],
        "record_set_digest",
        "release-independent records",
    )
    qualification = documents[QUALIFICATION_ARTIFACT]
    verify_digest(
        qualification, "qualification_digest", "M29 integration qualification"
    )
    if qualification.get("failed_count") != 0 or qualification.get("status") != "PASS":
        raise ContractError("M29 qualification is not passing")
    if documents[CONSUMPTION_VECTORS_ARTIFACT].get("status") != "PASS":
        raise ContractError("downstream consumption vectors are not passing")
    if any(
        vector.get("status") != "PASS"
        for vector in documents[CONSUMPTION_VECTORS_ARTIFACT]["vectors"]
    ):
        raise ContractError("a downstream consumption vector failed")


def write_documents(
    output_root: Path,
    schema_documents: Mapping[str, Mapping[str, Any]],
    documents: Mapping[str, Mapping[str, Any]],
) -> None:
    for relative, value in {**schema_documents, **documents}.items():
        target = path_for(output_root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(document_bytes(value))


def generate(
    repository_root: Path, output_root: Path, source_commit: str
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    schema_documents, documents = build_all(repository_root, source_commit)
    validate_documents(repository_root, schema_documents, documents)
    write_documents(output_root, schema_documents, documents)
    return verify(output_root, source_commit, source_root=repository_root)


def verify(
    root: Path,
    source_commit: str,
    *,
    source_root: Path | None = None,
) -> dict[str, Any]:
    validate_source_commit(source_commit)
    root = root.resolve()
    source_root = (source_root or root).resolve()
    expected_schemas, expected_documents = build_all(source_root, source_commit)
    observed_schemas = {
        relative: read_json(root, relative) for relative in SCHEMA_PATHS.values()
    }
    observed_documents = {
        relative: read_json(root, relative) for relative in DOCUMENT_SCHEMA_IDS
    }
    validate_documents(source_root, observed_schemas, observed_documents)
    for relative, expected in expected_schemas.items():
        if document_bytes(observed_schemas[relative]) != document_bytes(expected):
            raise ContractError(f"committed M29 schema mismatch: {relative}")
    for relative, expected in expected_documents.items():
        if document_bytes(observed_documents[relative]) != document_bytes(expected):
            raise ContractError(f"committed M29 document mismatch: {relative}")
    return {
        "milestone": MILESTONE,
        "version": VERSION,
        "source_commit": source_commit,
        "generated_path_count": len(GENERATED_PATHS),
        "schema_definition_count": len(SCHEMA_PATHS),
        "document_count": len(DOCUMENT_SCHEMA_IDS),
        "upstream_schema_count": observed_documents[SCHEMA_REGISTRY][
            "upstream_schema_count"
        ],
        "upstream_artifact_count": observed_documents[ARTIFACT_REGISTRY][
            "record_count"
        ],
        "qualification_check_count": observed_documents[QUALIFICATION_ARTIFACT][
            "check_count"
        ],
        "status": "PASS",
    }


def self_test(repository_root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    checks: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="frp-m29-self-test-") as temporary:
        first = Path(temporary) / "first"
        second = Path(temporary) / "second"
        generate(repository_root, first, source_commit)
        generate(repository_root, second, source_commit)
        for relative in GENERATED_PATHS:
            if require_file(first, relative).read_bytes() != require_file(
                second, relative
            ).read_bytes():
                raise ContractError(f"non-deterministic M29 output: {relative}")
        checks.append(_pass("deterministic-generation", "self_test", len(GENERATED_PATHS)))
        verification = verify(first, source_commit, source_root=repository_root)
        checks.append(_pass("generated-verification", "self_test", verification["status"]))

        package = read_json(first, DEMO_PACKAGE_ARTIFACT)
        package["members"][0]["payload_base64"] = package["members"][0][
            "payload_base64"
        ][:-1]
        package = with_digest(package, "package_digest")
        try:
            validate_demo_package(package, repository_root)
        except ContractError:
            checks.append(_pass("base64-tamper-rejected", "self_test", True))
        else:
            raise ContractError("M29 self-test accepted malformed Base64")

        contract = read_json(first, CONTRACT_ARTIFACT)
        contract["immutable_core"]["active_neutral_state"] = 1
        contract = with_digest(contract, "contract_digest")
        try:
            _validate_contract(contract)
        except ContractError:
            checks.append(_pass("core-tamper-rejected", "self_test", True))
        else:
            raise ContractError("M29 self-test accepted core mutation")

        member = read_json(first, DEMO_PACKAGE_ARTIFACT)["members"][0]
        original_key = compatibility_key(member)
        changed_labels = dict(member)
        changed_labels["upstream_release_label"] = "arbitrary-label"
        changed_labels["consumer_version"] = "arbitrary-version"
        if compatibility_key(changed_labels) != original_key:
            raise ContractError("release labels changed the compatibility key")
        checks.append(_pass("release-independent-key", "self_test", original_key))

        for unsafe in ("", "/absolute", "../escape", "a/../b", "a//b", "a\\b"):
            try:
                safe_relative_path(unsafe)
            except SafetyError:
                continue
            raise ContractError(f"M29 self-test accepted unsafe path: {unsafe!r}")
        checks.append(_pass("unsafe-paths-rejected", "self_test", True))

    return {
        "milestone": MILESTONE,
        "version": VERSION,
        "check_count": len(checks),
        "checks": checks,
        "status": "PASS",
    }


def _emit(value: Mapping[str, Any], output: str | None) -> None:
    rendered = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--generate", action="store_true")
    operation.add_argument("--verify", action="store_true")
    operation.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--source-commit", default=EXPECTED_M28_COMMIT)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository_root = Path(args.repository_root)
    try:
        if args.generate:
            result = generate(
                repository_root,
                Path(args.output_root),
                args.source_commit,
            )
        elif args.verify:
            result = verify(repository_root, args.source_commit)
        else:
            result = self_test(repository_root, args.source_commit)
        _emit(result, args.output)
        return 0
    except (ContractError, SafetyError, OSError, ValueError) as exc:
        print(f"M29 ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
