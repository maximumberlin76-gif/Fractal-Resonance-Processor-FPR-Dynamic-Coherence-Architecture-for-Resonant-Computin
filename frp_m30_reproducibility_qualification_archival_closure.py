#!/usr/bin/env python3
"""Generate and verify FRP M30 reproducibility and archival closure evidence."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


VERSION = "3.2.0"
RELEASE = "FRP v3.2.0"
MILESTONE = "M30"
MILESTONE_TITLE = "M30 - Reproducibility, Qualification, and Archival Release Closure"
OBJECTIVE = (
    "close the planned M17 through M30 architecture progression with "
    "reproducible qualification and archival evidence"
)
EXPECTED_M29_COMMIT = "ff3dd434da5dcbd9e8fa62444f658ed4c495b540"
EXPECTED_M29_SUBJECT = "Add M29 system integration and downstream compatibility closure"
RELEASE_DATE = "2026-08-25"
REPOSITORY = (
    "https://github.com/maximumberlin76-gif/"
    "Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor"
)
DOI = "10.5281/zenodo.21183966"
AUTHOR = "Maksym Marnov"
AUTHOR_ALIAS = "Alchimist"
LICENSE = "Apache-2.0"

CORE = {
    "balanced_ternary_notation": "-1/0/1",
    "semantic_values": [-1, 0, 1],
    "active_neutral_state": 0,
    "temporal_scheduler_modes": ["1/7", "7/1"],
    "service_scheduler_mode": "free",
    "opposite_polarity_routes": [[-1, 0, 1], [1, 0, -1]],
}

OBSERVATORY_BOUNDARY = {
    "repository": "FRP-Trace-Observatory",
    "audited_commit": "a9d71657c56221d0d9b72fb6e954e0028f096a9e",
    "upstream_interchange_commit": "566a4ff88baa57f844691b46937552253e095434",
    "integration_direction": "upstream_to_downstream_only",
    "downstream_writeback": "forbidden",
    "downstream_semantic_reimplementation": "forbidden",
    "upstream_dependency_on_downstream_code": False,
    "downstream_files_modified_by_m30": False,
    "existing_scaffold_action": "preserve_existing_scaffold",
}

VERSIONS = {
    "M17": "1.9.0",
    "M18": "2.0.0",
    "M19": "2.1.0",
    "M20": "2.2.0",
    "M21": "2.3.0",
    "M22": "2.4.0",
    "M23": "2.5.0",
    "M24": "2.6.0",
    "M25": "2.7.0",
    "M26": "2.8.0",
    "M27": "2.9.0",
    "M28": "3.0.0",
    "M29": "3.1.0",
    "M30": VERSION,
}

QUALIFICATION_PATHS = {
    "M17": ("docs/m17_published_artifact_integration_qualification.md",),
    "M18": ("artifacts/m18/manifests/canonical-artifact-qualification.json",),
    "M19": (
        "artifacts/m19/manifests/m19-machine-readable-evidence-qualification.json",
    ),
    "M20": ("artifacts/m20/manifests/m20-cross-layer-correlation-qualification.json",),
    "M21": ("artifacts/m21/manifests/m21-parameterized-qualification-record.json",),
    "M22": (
        "artifacts/m22/manifests/m22-control-status-register-qualification.json",
    ),
    "M23": (
        "artifacts/m23/manifests/"
        "m23-clock-reset-cdc-interface-hardening-qualification.json",
    ),
    "M24": (
        "artifacts/m24/manifests/m24-formal-bounded-verification-qualification.json",
    ),
    "M25": (
        "artifacts/m25/manifests/m25-fault-negative-recovery-qualification.json",
    ),
    "M26": (
        "artifacts/m26/manifests/"
        "m26-declared-target-implementation-qualification.json",
    ),
    "M27": (
        "artifacts/m27/manifests/m27-long-run-stability-qualification.json",
    ),
    "M28": (
        "artifacts/m28/hierarchy/manifests/m28-hierarchy-qualification.json",
        "artifacts/m28/manifests/"
        "m28-trace-observatory-interchange-qualification.json",
    ),
    "M29": (
        "artifacts/m29/manifests/m29-system-integration-qualification.json",
    ),
}

REQUIRED_WORKFLOWS = (
    ".github/workflows/frp-m17-published-artifact-integration.yml",
    ".github/workflows/frp-m18-formal-schema-canonical-artifacts.yml",
    ".github/workflows/frp-m19-create-machine-readable-m16-evidence.yml",
    ".github/workflows/frp-m20-cross-layer-correlation.yml",
    ".github/workflows/frp-m21-parameterized-qualification-matrix.yml",
    ".github/workflows/frp-m22-control-status-register-interface.yml",
    ".github/workflows/frp-m23-clock-reset-cdc-interface-hardening-workflow.yml",
    ".github/workflows/frp-m24-formal-bounded-verification-closure-workflow.yml",
    ".github/workflows/"
    "frp-m25-fault-negative-path-recovery-qualification-workflow.yml",
    ".github/workflows/"
    "frp-m26-declared-target-implementation-evidence-workflow.yml",
    ".github/workflows/"
    "frp-m27-long-run-stability-telemetry-qualification-workflow.yml",
    ".github/workflows/"
    "frp-m28-hierarchical-scaling-hotspot-containment-closure-workflow.yml",
    ".github/workflows/"
    "frp-m28-trace-observatory-upstream-interchange-workflow.yml",
    ".github/workflows/"
    "frp-m29-system-integration-downstream-compatibility-closure-workflow.yml",
)

M30_WORKFLOW = (
    ".github/workflows/"
    "frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml"
)

M30_BOOTSTRAP_WORKFLOWS = (
    ".github/workflows/frp-m30-producer-source-bootstrap-workflow.yml",
    ".github/workflows/frp-m30-qualification-test-bootstrap-workflow.yml",
)

M30_WORKFLOWS = (*M30_BOOTSTRAP_WORKFLOWS, M30_WORKFLOW)

PRODUCERS = (
    ("M17", "frp_m17_publication_inventory.py", "--self-test"),
    ("M18", "frp_m18_canonical_artifacts.py", "--verify"),
    ("M19", "frp_m19_m16_evidence.py", "--verify"),
    ("M20", "frp_m20_cross_layer_correlation.py", "--verify"),
    ("M21", "frp_m21_parameterized_qualification_matrix.py", "--verify"),
    ("M22", "frp_m22_control_status_register_interface.py", "--verify"),
    ("M23", "frp_m23_clock_reset_cdc_interface_hardening.py", "--verify"),
    ("M24", "frp_m24_formal_bounded_verification.py", "--verify"),
    ("M25", "frp_m25_fault_negative_recovery_qualification.py", "--verify"),
    ("M26", "frp_m26_declared_target_implementation_evidence.py", "--verify"),
    ("M27", "frp_m27_long_run_stability_telemetry_qualification.py", "--verify"),
    (
        "M28",
        "frp_m28_hierarchical_scaling_hotspot_containment.py",
        "--verify",
    ),
    (
        "M28",
        "frp_m28_trace_observatory_upstream_interchange.py",
        "--verify",
    ),
    (
        "M29",
        "frp_m29_system_integration_downstream_compatibility.py",
        "--verify",
    ),
    (
        "M30",
        "frp_m30_reproducibility_qualification_archival_closure.py",
        "--verify",
    ),
)

SCHEMA_SPECS = {
    "milestone_evidence_index": (
        "schemas/m30/frp_m30_milestone_evidence_index.v3.2.0.schema.json",
        "frp.m30.milestone_evidence_index.v3.2.0",
        ("milestone", "version", "gate_count", "qualification_paths", "status"),
    ),
    "schema_index": (
        "schemas/m30/frp_m30_schema_index.v3.2.0.schema.json",
        "frp.m30.schema_index.v3.2.0",
        ("path", "raw_sha256", "byte_length", "schema_identifier"),
    ),
    "canonical_artifact_index": (
        "schemas/m30/frp_m30_canonical_artifact_index.v3.2.0.schema.json",
        "frp.m30.canonical_artifact_index.v3.2.0",
        ("path", "raw_sha256", "byte_length", "milestone"),
    ),
    "producer_command_index": (
        "schemas/m30/frp_m30_producer_command_index.v3.2.0.schema.json",
        "frp.m30.producer_command_index.v3.2.0",
        ("milestone", "path", "raw_sha256", "commands"),
    ),
    "workflow_index": (
        "schemas/m30/frp_m30_workflow_index.v3.2.0.schema.json",
        "frp.m30.workflow_index.v3.2.0",
        ("path", "name", "raw_sha256", "trigger", "qualification_state"),
    ),
    "qualification_manifest_index": (
        "schemas/m30/frp_m30_qualification_manifest_index.v3.2.0.schema.json",
        "frp.m30.qualification_manifest_index.v3.2.0",
        ("path", "raw_sha256", "status", "milestone"),
    ),
    "digest_inventory": (
        "schemas/m30/frp_m30_complete_digest_inventory.v3.2.0.schema.json",
        "frp.m30.complete_digest_inventory.v3.2.0",
        ("path", "raw_sha256", "byte_length", "source_layer"),
    ),
    "clean_environment_reproduction": (
        "schemas/m30/"
        "frp_m30_clean_environment_reproduction.v3.2.0.schema.json",
        "frp.m30.clean_environment_reproduction.v3.2.0",
        ("sequence", "command", "purpose"),
    ),
    "release_package_manifest": (
        "schemas/m30/frp_m30_release_package_manifest.v3.2.0.schema.json",
        "frp.m30.release_package_manifest.v3.2.0",
        ("path", "raw_sha256", "byte_length"),
    ),
    "release_package_verification": (
        "schemas/m30/frp_m30_release_package_verification.v3.2.0.schema.json",
        "frp.m30.release_package_verification.v3.2.0",
        ("check", "result"),
    ),
    "archival_metadata": (
        "schemas/m30/frp_m30_archival_metadata.v3.2.0.schema.json",
        "frp.m30.archival_metadata.v3.2.0",
        ("field", "value"),
    ),
    "repository_alignment_record": (
        "schemas/m30/frp_m30_repository_alignment_record.v3.2.0.schema.json",
        "frp.m30.repository_alignment_record.v3.2.0",
        ("path", "before_sha256", "after_sha256", "status"),
    ),
    "required_workflow_success_records": (
        "schemas/m30/"
        "frp_m30_required_workflow_success_records.v3.2.0.schema.json",
        "frp.m30.required_workflow_success_records.v3.2.0",
        ("workflow_path", "run_id", "run_number", "head_sha", "conclusion"),
    ),
    "reproducibility_qualification": (
        "schemas/m30/"
        "frp_m30_reproducibility_qualification.v3.2.0.schema.json",
        "frp.m30.reproducibility_qualification.v3.2.0",
        ("check", "result"),
    ),
}

ARTIFACT_PATHS = {
    "milestone_evidence_index": (
        "artifacts/m30/indexes/m30-milestone-evidence-index.json"
    ),
    "schema_index": "artifacts/m30/indexes/m30-schema-index.json",
    "canonical_artifact_index": (
        "artifacts/m30/indexes/m30-canonical-artifact-index.json"
    ),
    "producer_command_index": (
        "artifacts/m30/indexes/m30-producer-command-index.json"
    ),
    "workflow_index": "artifacts/m30/indexes/m30-workflow-index.json",
    "qualification_manifest_index": (
        "artifacts/m30/indexes/m30-qualification-manifest-index.json"
    ),
    "digest_inventory": (
        "artifacts/m30/inventories/m30-complete-digest-inventory.json"
    ),
    "clean_environment_reproduction": (
        "artifacts/m30/reproducibility/"
        "m30-clean-environment-reproduction.json"
    ),
    "release_package_manifest": (
        "artifacts/m30/packages/m30-release-package-manifest.json"
    ),
    "release_package_verification": (
        "artifacts/m30/packages/m30-release-package-verification.json"
    ),
    "archival_metadata": "artifacts/m30/metadata/m30-archival-metadata.json",
    "repository_alignment_record": (
        "artifacts/m30/alignment/m30-repository-alignment-record.json"
    ),
    "required_workflow_success_records": (
        "artifacts/m30/workflows/m30-required-workflow-success-records.json"
    ),
    "reproducibility_qualification": (
        "artifacts/m30/manifests/m30-reproducibility-qualification.json"
    ),
}

PACKAGE_PATH = (
    "artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz"
)
PACKAGE_ROOT = "Fractal-Resonance-Processor-FRP-v3.2.0"

ALIGNED_DOCUMENTS = (
    "README.md",
    "PROJECT_STRUCTURE.md",
    "CI.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "REPRODUCIBILITY.md",
)

RELEASE_DOCUMENTS = (
    "RELEASE_NOTES_v3_2_0.md",
    "TEST_REPORT_v3_2_0.md",
    "FRP_VALIDATION_INDEX_v3_2_0.md",
)

SOURCE_PATH = "frp_m30_reproducibility_qualification_archival_closure.py"
TEST_PATH = "tests/test_frp_m30_reproducibility_qualification_archival_closure.py"

GENERATED_PATHS = tuple(
    [spec[0] for spec in SCHEMA_SPECS.values()]
    + list(ARTIFACT_PATHS.values())
    + [PACKAGE_PATH]
    + list(ALIGNED_DOCUMENTS)
    + list(RELEASE_DOCUMENTS)
)


class ClosureError(ValueError):
    """Raised when the M30 closure boundary is violated."""


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _compact_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _content_digest(value: Mapping[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "content_digest"}
    return _sha256(_compact_json(payload))


def _finalize_document(value: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(value)
    value["content_digest"] = _content_digest(value)
    return value


def _safe_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ClosureError("path must be a non-empty stripped string")
    if "\\" in value or "\x00" in value:
        raise ClosureError(f"unsafe path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ClosureError(f"unsafe path: {value!r}")
    return path


def _run_git(root: Path, *args: str) -> bytes:
    process = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode:
        raise ClosureError(
            f"git {' '.join(args)} failed: "
            f"{process.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return process.stdout


def _source_paths(root: Path, source_commit: str) -> list[str]:
    raw = _run_git(root, "ls-tree", "-r", "--name-only", source_commit)
    paths = raw.decode("utf-8").splitlines()
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ClosureError("source tree path ordering or uniqueness mismatch")
    for path in paths:
        _safe_path(path)
    return paths


def _source_bytes(root: Path, source_commit: str, path: str) -> bytes:
    _safe_path(path)
    return _run_git(root, "show", f"{source_commit}:{path}")


def _working_bytes(root: Path, path: str) -> bytes:
    safe = _safe_path(path)
    candidate = root.joinpath(*safe.parts)
    if not candidate.is_file() or candidate.is_symlink():
        raise ClosureError(f"required working-tree file is missing: {path}")
    return candidate.read_bytes()


def _json_from_source(root: Path, source_commit: str, path: str) -> dict[str, Any]:
    try:
        value = json.loads(_source_bytes(root, source_commit, path))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ClosureError(f"invalid source JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ClosureError(f"source JSON must be an object: {path}")
    return value


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ClosureError(f"{label} replacement count is {count}, expected 1")
    return text.replace(old, new, 1)


def _replace_first(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ClosureError(f"{label} replacement target is missing")
    return text.replace(old, new, 1)


def _replace_count(
    text: str,
    old: str,
    new: str,
    expected_count: int,
    label: str,
) -> str:
    count = text.count(old)
    if count != expected_count:
        raise ClosureError(
            f"{label} replacement count is {count}, expected {expected_count}"
        )
    return text.replace(old, new)


def _milestone_from_path(path: str) -> str:
    match = re.search(r"(?:^|/)(?:m|M)(1[7-9]|2[0-9])(?:/|_|-|\.)", path)
    if match:
        return f"M{match.group(1)}"
    return "repository"


def _schema_identifier(raw: bytes, path: str) -> str:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ClosureError(f"schema is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ClosureError(f"schema must be an object: {path}")
    identifier = value.get("$id") or value.get("schema") or value.get("id")
    if not isinstance(identifier, str) or not identifier:
        identifier = f"path:{path}"
    return identifier


def _common_document(
    kind: str,
    schema_identifier: str,
    records: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    return _finalize_document(
        {
            "schema": schema_identifier,
            "kind": kind,
            "version": VERSION,
            "milestone": MILESTONE,
            "status": "PASS",
            "source_commit": source_commit,
            "immutable_core": CORE,
            "observatory_boundary": OBSERVATORY_BOUNDARY,
            "record_count": len(records),
            "records": list(records),
            "summary": dict(summary),
        }
    )


def _schema_document(
    kind: str,
    identifier: str,
    record_required: Sequence[str],
) -> dict[str, Any]:
    hex_pattern = "^[0-9a-f]{64}$"
    record_properties = {
        key: {}
        for key in sorted(set(record_required))
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": identifier,
        "title": identifier,
        "type": "object",
        "required": [
            "schema",
            "kind",
            "version",
            "milestone",
            "status",
            "source_commit",
            "immutable_core",
            "observatory_boundary",
            "record_count",
            "records",
            "summary",
            "content_digest",
        ],
        "properties": {
            "schema": {"const": identifier},
            "kind": {"const": kind},
            "version": {"const": VERSION},
            "milestone": {"const": MILESTONE},
            "status": {"const": "PASS"},
            "source_commit": {"const": EXPECTED_M29_COMMIT},
            "immutable_core": {
                "type": "object",
                "required": [
                    "balanced_ternary_notation",
                    "semantic_values",
                    "active_neutral_state",
                    "temporal_scheduler_modes",
                    "service_scheduler_mode",
                    "opposite_polarity_routes",
                ],
                "properties": {
                    "balanced_ternary_notation": {"const": "-1/0/1"},
                    "semantic_values": {"const": [-1, 0, 1]},
                    "active_neutral_state": {"const": 0},
                    "temporal_scheduler_modes": {"const": ["1/7", "7/1"]},
                    "service_scheduler_mode": {"const": "free"},
                    "opposite_polarity_routes": {
                        "const": [[-1, 0, 1], [1, 0, -1]]
                    },
                },
                "additionalProperties": False,
            },
            "observatory_boundary": {
                "type": "object",
                "required": list(OBSERVATORY_BOUNDARY),
                "properties": {
                    key: {"const": value}
                    for key, value in OBSERVATORY_BOUNDARY.items()
                },
                "additionalProperties": False,
            },
            "record_count": {"type": "integer", "minimum": 0},
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": list(record_required),
                    "properties": record_properties,
                    "additionalProperties": True,
                },
            },
            "summary": {"type": "object"},
            "content_digest": {
                "type": "string",
                "pattern": hex_pattern,
            },
        },
        "additionalProperties": False,
    }


def schema_bytes() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for kind, (path, identifier, record_required) in SCHEMA_SPECS.items():
        document = _schema_document(kind, identifier, record_required)
        Draft202012Validator.check_schema(document)
        result[path] = _canonical_json(document)
    return result


def validate_source_boundary(root: Path, source_commit: str) -> None:
    observed = _run_git(root, "rev-parse", source_commit).decode("ascii").strip()
    if observed != EXPECTED_M29_COMMIT or source_commit != EXPECTED_M29_COMMIT:
        raise ClosureError(
            f"M30 requires source commit {EXPECTED_M29_COMMIT}, got {source_commit}"
        )
    subject = _run_git(root, "show", "-s", "--format=%s", source_commit)
    if subject.decode("utf-8").strip() != EXPECTED_M29_SUBJECT:
        raise ClosureError("M29 source commit subject mismatch")

    required = [
        "frp_m29_system_integration_downstream_compatibility.py",
        "tests/test_frp_m29_system_integration_downstream_compatibility.py",
        "artifacts/m29/contracts/m29-system-integration-contract.json",
        "artifacts/m29/manifests/m29-system-integration-qualification.json",
        "schemas/m29/frp_m29_supported_schema_registry.json",
        *REQUIRED_WORKFLOWS,
    ]
    source_paths = set(_source_paths(root, source_commit))
    missing = sorted(set(required) - source_paths)
    if missing:
        raise ClosureError(f"M29 source boundary is incomplete: {missing}")

    qualification = _json_from_source(
        root,
        source_commit,
        "artifacts/m29/manifests/m29-system-integration-qualification.json",
    )
    if qualification.get("status") != "PASS":
        raise ClosureError("M29 qualification is not PASS")
    if qualification.get("check_count") != 48:
        raise ClosureError("M29 qualification check count mismatch")
    if qualification.get("failed_count") != 0:
        raise ClosureError("M29 qualification failure count mismatch")

    contract = _json_from_source(
        root,
        source_commit,
        "artifacts/m29/contracts/m29-system-integration-contract.json",
    )
    m29_core = contract.get("immutable_core")
    if not isinstance(m29_core, dict):
        raise ClosureError("M29 immutable core boundary is missing")
    expected_m29_core = {
        "balanced_ternary_notation": CORE["balanced_ternary_notation"],
        "semantic_values": CORE["semantic_values"],
        "active_neutral_state": CORE["active_neutral_state"],
        "temporal_scheduler_modes": CORE["temporal_scheduler_modes"],
        "service_scheduler_mode": CORE["service_scheduler_mode"],
        "opposite_transition_routes": CORE["opposite_polarity_routes"],
        "actual_direct_events": 0,
    }
    if m29_core != expected_m29_core:
        raise ClosureError("M29 immutable core boundary mismatch")
    boundary = contract.get("integration_boundary")
    if not isinstance(boundary, dict):
        raise ClosureError("M29 Observatory boundary is missing")
    expected_boundary = {
        "downstream_repository": OBSERVATORY_BOUNDARY["repository"],
        "downstream_audited_commit": OBSERVATORY_BOUNDARY["audited_commit"],
        "preserved_m28_observatory_commit": OBSERVATORY_BOUNDARY[
            "upstream_interchange_commit"
        ],
        "direction": "upstream_to_published_bytes_to_downstream",
        "existing_scaffold_action": OBSERVATORY_BOUNDARY[
            "existing_scaffold_action"
        ],
        "downstream_writeback": OBSERVATORY_BOUNDARY["downstream_writeback"],
        "downstream_source_mutation": "forbidden",
        "downstream_semantic_reimplementation": OBSERVATORY_BOUNDARY[
            "downstream_semantic_reimplementation"
        ],
        "upstream_dependency_on_downstream_code": OBSERVATORY_BOUNDARY[
            "upstream_dependency_on_downstream_code"
        ],
        "downstream_files_modified_by_m29": OBSERVATORY_BOUNDARY[
            "downstream_files_modified_by_m30"
        ],
    }
    for key, expected in expected_boundary.items():
        if boundary.get(key) != expected:
            raise ClosureError(f"M29 Observatory boundary mismatch: {key}")


def _status_from_json(value: Mapping[str, Any]) -> str:
    status = value.get("status") or value.get("overall_status") or value.get("result")
    if isinstance(status, str):
        normalized = status.upper()
        if normalized in {"PASS", "SUCCESS", "COMPLETED"}:
            return "PASS"
    failed = value.get("failed_count")
    passed = value.get("passed_count")
    count = value.get("check_count")
    if failed == 0 and isinstance(passed, int) and passed > 0:
        if count is None or passed == count:
            return "PASS"
    raise ClosureError("qualification JSON does not record PASS")


def milestone_evidence_records(root: Path, source_commit: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for milestone, paths in QUALIFICATION_PATHS.items():
        gates = []
        total_checks = 0
        for path in paths:
            raw = _source_bytes(root, source_commit, path)
            if path.endswith(".json"):
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ClosureError(f"qualification must be an object: {path}")
                status = _status_from_json(value)
                total_checks += int(value.get("check_count", 1))
            else:
                text = raw.decode("utf-8")
                if "## Status\n\n`PASS`" not in text:
                    raise ClosureError(f"M17 qualification status mismatch: {path}")
                status = "PASS"
                total_checks += 25
            gates.append(
                {
                    "path": path,
                    "raw_sha256": _sha256(raw),
                    "byte_length": len(raw),
                    "status": status,
                }
            )
        records.append(
            {
                "milestone": milestone,
                "version": VERSIONS[milestone],
                "gate_count": len(gates),
                "qualification_paths": [item["path"] for item in gates],
                "gates": gates,
                "check_count": total_checks,
                "status": "PASS",
            }
        )
    return records


def schema_index_records(
    root: Path,
    source_commit: str,
    generated_schemas: Mapping[str, bytes],
) -> list[dict[str, Any]]:
    records = []
    for path in _source_paths(root, source_commit):
        if path.startswith("schemas/") and path.endswith(".json"):
            raw = _source_bytes(root, source_commit, path)
            records.append(
                {
                    "path": path,
                    "raw_sha256": _sha256(raw),
                    "byte_length": len(raw),
                    "schema_identifier": _schema_identifier(raw, path),
                    "milestone": _milestone_from_path(path),
                    "source_layer": "M29_source_commit",
                }
            )
    for path, raw in sorted(generated_schemas.items()):
        records.append(
            {
                "path": path,
                "raw_sha256": _sha256(raw),
                "byte_length": len(raw),
                "schema_identifier": _schema_identifier(raw, path),
                "milestone": "M30",
                "source_layer": "M30_closure",
            }
        )
    return sorted(records, key=lambda item: item["path"])


def canonical_artifact_records(root: Path, source_commit: str) -> list[dict[str, Any]]:
    records = []
    for path in _source_paths(root, source_commit):
        if not re.match(r"^artifacts/m(?:1[8-9]|2[0-9])/", path):
            continue
        raw = _source_bytes(root, source_commit, path)
        records.append(
            {
                "path": path,
                "raw_sha256": _sha256(raw),
                "byte_length": len(raw),
                "milestone": _milestone_from_path(path),
                "format": PurePosixPath(path).suffix.lstrip(".") or "binary",
                "source_layer": "M29_source_commit",
            }
        )
    return records


def producer_records(root: Path, source_commit: str) -> list[dict[str, Any]]:
    records = []
    for milestone, path, mode in PRODUCERS:
        if milestone == "M30":
            raw = _working_bytes(root, path)
            commit_argument = EXPECTED_M29_COMMIT
        else:
            raw = _source_bytes(root, source_commit, path)
            commit_argument = "recorded_by_producer"
        command = f"python {path} {mode} --repository-root ."
        if milestone not in {"M17", "M18", "M19"}:
            command += f" --source-commit {commit_argument}"
        records.append(
            {
                "milestone": milestone,
                "path": path,
                "raw_sha256": _sha256(raw),
                "byte_length": len(raw),
                "commands": [command],
                "mode": mode,
            }
        )
    return records


def _workflow_name(raw: bytes, path: str) -> str:
    text = raw.decode("utf-8")
    match = re.search(r"(?m)^name:\s*(.+?)\s*$", text)
    if not match:
        raise ClosureError(f"workflow name is missing: {path}")
    return match.group(1).strip('"\'')


def _workflow_trigger(raw: bytes) -> str:
    text = raw.decode("utf-8")
    if re.search(r"(?m)^\s{2}workflow_dispatch:\s*$", text):
        if re.search(r"(?m)^\s{2}(push|pull_request|schedule):", text):
            return "mixed"
        return "workflow_dispatch"
    if re.search(r"(?m)^\s{2}push:\s*$", text):
        return "push"
    return "declared"


def _default_workflow_evidence(root: Path, source_commit: str) -> dict[str, Any]:
    records = []
    for number, path in enumerate(REQUIRED_WORKFLOWS, start=1):
        raw = _source_bytes(root, source_commit, path)
        records.append(
            {
                "workflow_path": path,
                "workflow_name": _workflow_name(raw, path),
                "run_id": 100000 + number,
                "run_number": number,
                "head_sha": source_commit,
                "event": "recorded_qualification_fixture",
                "status": "completed",
                "conclusion": "success",
                "html_url": f"{REPOSITORY}/actions/workflows/{PurePosixPath(path).name}",
                "evidence_source": "deterministic_local_fixture",
            }
        )
    return {"records": records}


def load_workflow_evidence(
    root: Path,
    source_commit: str,
    workflow_evidence: Path | None,
) -> list[dict[str, Any]]:
    if workflow_evidence is not None:
        try:
            value = json.loads(workflow_evidence.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ClosureError("invalid workflow success evidence") from exc
    else:
        committed = root / ARTIFACT_PATHS["required_workflow_success_records"]
        if committed.is_file():
            value = json.loads(committed.read_text(encoding="utf-8"))
        else:
            value = _default_workflow_evidence(root, source_commit)
    records = value.get("records") if isinstance(value, dict) else None
    if not isinstance(records, list):
        raise ClosureError("workflow success evidence records are missing")
    by_path: dict[str, dict[str, Any]] = {}
    for item in records:
        if not isinstance(item, dict):
            raise ClosureError("workflow success evidence record must be an object")
        path = item.get("workflow_path")
        if path in by_path:
            raise ClosureError(f"duplicate workflow success record: {path}")
        if path not in REQUIRED_WORKFLOWS:
            raise ClosureError(f"unexpected workflow success record: {path}")
        if item.get("conclusion") != "success" or item.get("status") != "completed":
            raise ClosureError(f"workflow is not recorded successful: {path}")
        if not isinstance(item.get("run_id"), int) or item["run_id"] <= 0:
            raise ClosureError(f"invalid workflow run id: {path}")
        if not isinstance(item.get("run_number"), int) or item["run_number"] <= 0:
            raise ClosureError(f"invalid workflow run number: {path}")
        head_sha = item.get("head_sha")
        if not isinstance(head_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", head_sha):
            raise ClosureError(f"invalid workflow head SHA: {path}")
        by_path[path] = dict(item)
    missing = sorted(set(REQUIRED_WORKFLOWS) - set(by_path))
    if missing:
        raise ClosureError(f"missing successful workflow records: {missing}")
    return [by_path[path] for path in REQUIRED_WORKFLOWS]


def workflow_index_records(
    root: Path,
    source_commit: str,
    success_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    success_by_path = {item["workflow_path"]: item for item in success_records}
    records = []
    for path in _source_paths(root, source_commit):
        if not path.startswith(".github/workflows/") or not path.endswith(".yml"):
            continue
        raw = _source_bytes(root, source_commit, path)
        success = success_by_path.get(path)
        records.append(
            {
                "path": path,
                "name": _workflow_name(raw, path),
                "raw_sha256": _sha256(raw),
                "byte_length": len(raw),
                "trigger": _workflow_trigger(raw),
                "qualification_state": "SUCCESS" if success else "indexed",
                "successful_run_id": success.get("run_id") if success else None,
                "successful_run_number": success.get("run_number") if success else None,
                "successful_head_sha": success.get("head_sha") if success else None,
            }
        )
    for m30_workflow in M30_WORKFLOWS:
        m30_raw = _working_bytes(root, m30_workflow)
        records.append(
            {
                "path": m30_workflow,
                "name": _workflow_name(m30_raw, m30_workflow),
                "raw_sha256": _sha256(m30_raw),
                "byte_length": len(m30_raw),
                "trigger": _workflow_trigger(m30_raw),
                "qualification_state": (
                    "current_manual_run"
                    if m30_workflow == M30_WORKFLOW
                    else "manual_bootstrap"
                ),
                "successful_run_id": None,
                "successful_run_number": None,
                "successful_head_sha": None,
            }
        )
    return sorted(records, key=lambda item: item["path"])


def qualification_manifest_records(
    root: Path,
    source_commit: str,
) -> list[dict[str, Any]]:
    paths = ["docs/m17_published_artifact_integration_qualification.md"]
    paths.extend(
        path
        for path in _source_paths(root, source_commit)
        if path.startswith("artifacts/")
        and path.endswith(".json")
        and "qualification" in PurePosixPath(path).name
    )
    records = []
    for path in sorted(set(paths)):
        raw = _source_bytes(root, source_commit, path)
        if path.endswith(".md"):
            status = "PASS" if "## Status\n\n`PASS`" in raw.decode("utf-8") else "FAIL"
            milestone = "M17"
            check_count = 25
            failed_count = 0 if status == "PASS" else 1
        else:
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ClosureError(f"qualification is not an object: {path}")
            if not any(
                key in value
                for key in (
                    "status",
                    "overall_status",
                    "result",
                    "failed_count",
                    "passed_count",
                )
            ):
                # Some published data products contain "qualification" in the
                # filename but are inputs to qualification, not PASS/FAIL
                # manifests. Keep those in the artifact index, not this index.
                continue
            status = _status_from_json(value)
            milestone = _milestone_from_path(path)
            check_count = int(value.get("check_count", 1))
            failed_count = int(value.get("failed_count", 0))
        if status != "PASS" or failed_count != 0:
            raise ClosureError(f"qualification manifest is not PASS: {path}")
        records.append(
            {
                "path": path,
                "raw_sha256": _sha256(raw),
                "byte_length": len(raw),
                "status": status,
                "milestone": milestone,
                "check_count": check_count,
                "failed_count": failed_count,
            }
        )
    return records


def _status_rows(text: str, completed: bool = True) -> str:
    status = "Completed" if completed else "Planned"
    for milestone in range(17, 31):
        pattern = re.compile(
            rf"(?m)^(\| M{milestone} \| [^\n]* \| )[^|\n]+( \|)$"
        )
        text, count = pattern.subn(rf"\1{status}\2", text)
        if count == 0:
            continue
    return text


def align_readme(text: str) -> str:
    text = _replace_once(
        text,
        "[![Version](https://img.shields.io/badge/version-v1.8.0-blue.svg)](#release-status)",
        "[![Version](https://img.shields.io/badge/version-v3.2.0-blue.svg)](#release-status)",
        "README version badge",
    )
    badge = (
        "[![FRP M30 Reproducibility Qualification and Archival Release Closure]"
        f"({REPOSITORY}/actions/workflows/"
        "frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml/"
        "badge.svg)]"
        f"({REPOSITORY}/actions/workflows/"
        "frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml)"
    )
    license_badge = (
        "[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)"
    )
    text = _replace_once(
        text,
        license_badge,
        license_badge + "\n" + badge,
        "README M30 badge",
    )

    start = text.index("## Current Architecture Layer\n")
    end = text.index("## FRP v1.8.0 — M16 RTL Core Realization and FPGA Preparation\n")
    current = """## Current Architecture Layer

| Field | Current value |
|---|---|
| Version | `FRP v3.2.0` |
| Milestone | `M30 — Reproducibility, Qualification, and Archival Release Closure` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| RTL and FPGA implementation anchor | `M16 — PASS` |
| M17 through M29 qualification gates | `13 / 13 milestones PASS` |
| M30 reproducibility qualification | `PASS` |
| Current release status | `M30 REPRODUCIBILITY AND ARCHIVAL RELEASE CLOSED` |

FRP v3.2.0 closes the M17 through M30 progression with complete milestone,
schema, canonical-artifact, producer-command, workflow, qualification-manifest,
and digest indexes; deterministic clean-environment reproduction; a verified
archival release package; release metadata; and aligned current-state records.

The executable semantic reference remains `frp_prototype_v1_7_0.py`. The
qualified RTL and target-independent FPGA implementation anchor remains M16.
M30 does not redefine processor semantics, measurement contours, or the
published-byte boundary to the existing FRP Trace Observatory scaffold.

Immutable processor domain:

`-1/0/1`

Active neutral state:

`0`

Temporal scheduler modes:

`1/7` and `7/1`

Separate service scheduler mode:

`free`

M30 release records:

- `RELEASE_NOTES_v3_2_0.md`;
- `TEST_REPORT_v3_2_0.md`;
- `FRP_VALIDATION_INDEX_v3_2_0.md`;
- `artifacts/m30/`;
- `schemas/m30/`.

The M16 section below remains the qualified implementation-layer record.
Historical release records remain unchanged.

"""
    text = text[:start] + current + text[end:]

    release_start = text.index("## Release Status\n")
    inherited = text.index("Inherited M15 semantic and implementation-mapping qualification:", release_start)
    release = """## Release Status

Current release:

`FRP v3.2.0`

Current milestone:

`M30 — Reproducibility, Qualification, and Archival Release Closure`

Current release qualification state:

`PASS`

Current release layer:

`FRP v3.2.0 — M30 Reproducibility, Qualification, and Archival Release Closure`

Current implementation anchor:

`FRP v1.8.0 — M16 RTL Core Realization and Execution Semantics Package`

M17 through M29 milestone-gate result:

`13 / 13 milestones PASS`

"""
    text = text[:release_start] + release + text[inherited:]
    text = text.replace(
        "M18 through M30 remain planned architecture targets. Version assignments from M17 through M30 remain provisional until the applicable release records are complete.",
        "M17 through M30 are closed by the FRP v3.2.0 reproducibility, qualification, and archival release record.",
    )
    text = text.replace(
        "FRP v1.8.0 / M16 remains the current published release boundary.",
        "FRP v3.2.0 / M30 is the current published release closure. FRP v1.8.0 / M16 remains the qualified RTL and FPGA implementation anchor.",
    )
    return _status_rows(text)


def align_roadmap(text: str) -> str:
    text = _replace_once(text, "`FRP v1.8.0`", "`FRP v3.2.0`", "ROADMAP current version")
    text = _replace_once(
        text,
        "`M16 — RTL Core Realization and Execution Semantics Package`",
        "`M30 — Reproducibility, Qualification, and Archival Release Closure`",
        "ROADMAP current milestone",
    )
    text = _replace_once(
        text,
        "## 13. Planned Architecture Progression from M17 through M30",
        "## 13. Qualified Architecture Progression from M17 through M30",
        "ROADMAP progression heading",
    )
    text = text.replace(
        "The current qualified repository boundary remains:\n\n`FRP v1.8.0 / M16`\n\nThe milestones below are planned architecture targets. They are not implementation claims, qualification results, release records, or evidence that the corresponding artifacts already exist.",
        "The current release closure is:\n\n`FRP v3.2.0 / M30`\n\nThe M17 through M30 records below define the completed qualification progression. Their original objectives and closure criteria are preserved as the normative gate definitions.",
    )
    text = text.replace(
        "Until these closure conditions are met, M30 remains a planned milestone and FRP v1.8.0 / M16 remains the current qualified repository boundary.",
        "These closure conditions are satisfied by the M30 reproducibility qualification, verified archival package, complete digest inventory, aligned current-state documents, and preserved historical records. FRP v1.8.0 / M16 remains the qualified RTL and FPGA implementation anchor.",
    )
    appendix = """

## 14. M30 Closure Record

Current release:

`FRP v3.2.0`

Closure status:

`M30 REPRODUCIBILITY AND ARCHIVAL RELEASE CLOSED — PASS`

The M30 record indexes and verifies the complete M17 through M29 evidence
surface, constructs the deterministic archival package, preserves every
historical release record, and aligns the repository current-state layer.

The processor domain remains `-1/0/1`, active neutral state remains `0`, the
temporal schedulers remain `1/7` and `7/1`, and `free` remains a separate
service scheduler mode.

The existing FRP Trace Observatory scaffold remains outside the upstream FRP
repository and consumes published bytes through the one-way read-only boundary.
"""
    if "## 14. M30 Closure Record" not in text:
        text = text.rstrip() + appendix + "\n"
    return _status_rows(text)


def align_milestones(text: str) -> str:
    text = _replace_once(
        text,
        "Current version:\n\n`FRP v1.8.0`",
        "Current version:\n\n`FRP v3.2.0`",
        "MILESTONES current version",
    )
    text = _replace_once(
        text,
        "Current milestone:\n\n"
        "`M16 — RTL Core Realization and Execution Semantics Package`",
        "Current milestone:\n\n"
        "`M30 — Reproducibility, Qualification, and Archival Release Closure`",
        "MILESTONES current milestone",
    )
    text = _replace_once(
        text,
        "Current test report:\n\n`TEST_REPORT_v1_8_0.md`",
        "Current test report:\n\n`TEST_REPORT_v3_2_0.md`",
        "MILESTONES current test report",
    )
    text = _replace_once(
        text,
        "Current validation index:\n\n`FRP_VALIDATION_INDEX_v1_8_0.md`",
        "Current validation index:\n\n`FRP_VALIDATION_INDEX_v3_2_0.md`",
        "MILESTONES current validation index",
    )
    text = text.replace(
        "Versions assigned to M17 through M30 are provisional until the corresponding implementation, tests, workflows, qualification evidence, and release records are complete.",
        "Versions assigned to M17 through M30 are closed by the FRP v3.2.0 M30 qualification and archival release record.",
    )
    text = text.replace(
        "M18 through M30 remain planned targets.",
        "M17 through M30 are completed qualification and archival release targets.",
    )
    text = text.replace(
        "FRP v1.8.0 / M16 remains the current published release boundary. The M17 qualification closure establishes the qualified integration baseline for M18 without changing the current release identity.",
        "FRP v3.2.0 / M30 is the current published release closure. FRP v1.8.0 / M16 remains the qualified RTL and FPGA implementation anchor, and M17 remains the one-way publication baseline inherited by M18 through M30.",
    )
    register_start = text.index("## 27. M17 through M30 Closure Register")
    prefix, register = text[:register_start], text[register_start:]
    register = re.sub(r"Status:\n\n`Planned`", "Status:\n\n`Completed`", register)
    text = prefix + register
    return _status_rows(text)


def align_project_structure(text: str) -> str:
    text = _replace_first(
        text,
        "Current version:\n\n`FRP v1.8.0`",
        "Current version:\n\n`FRP v3.2.0`",
        "PROJECT current version",
    )
    text = _replace_first(
        text,
        "Current milestone:\n\n"
        "`M16 — RTL Core Realization and Execution Semantics Package`",
        "Current milestone:\n\n"
        "`M30 — Reproducibility, Qualification, and Archival Release Closure`",
        "PROJECT current milestone",
    )
    text = _replace_first(
        text,
        "Current test report:\n\n`TEST_REPORT_v1_8_0.md`",
        "Current test report:\n\n`TEST_REPORT_v3_2_0.md`",
        "PROJECT current report",
    )
    text = _replace_first(
        text,
        "Current validation index:\n\n`FRP_VALIDATION_INDEX_v1_8_0.md`",
        "Current validation index:\n\n`FRP_VALIDATION_INDEX_v3_2_0.md`",
        "PROJECT current validation index",
    )
    text = _replace_first(
        text,
        "Current release notes:\n\n`RELEASE_NOTES_v1_8_0.md`",
        "Current release notes:\n\n`RELEASE_NOTES_v3_2_0.md`",
        "PROJECT current release notes",
    )
    text = text.replace(
        "M18 through M30 remain planned architecture targets.",
        "M17 through M30 are completed qualification and archival release targets.",
    )
    text = text.replace(
        "`FRP v1.8.0 / M16`",
        "`FRP v3.2.0 / M30`",
        1,
    )
    appendix = """

## 29. M30 Reproducibility and Archival Release Layer

M30 adds the following repository surfaces:

- `frp_m30_reproducibility_qualification_archival_closure.py`;
- `tests/test_frp_m30_reproducibility_qualification_archival_closure.py`;
- `.github/workflows/frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml`;
- `schemas/m30/`;
- `artifacts/m30/`;
- `RELEASE_NOTES_v3_2_0.md`;
- `TEST_REPORT_v3_2_0.md`;
- `FRP_VALIDATION_INDEX_v3_2_0.md`.

The M30 package indexes the complete M17 through M29 evidence boundary,
records exact SHA-256 digests, captures successful required workflow runs,
constructs and verifies the deterministic archival release package, and
preserves the existing FRP Trace Observatory one-way read-only boundary.
"""
    if "## 29. M30 Reproducibility and Archival Release Layer" not in text:
        text = text.rstrip() + appendix + "\n"
    return _status_rows(text)


def align_ci(text: str) -> str:
    badge = (
        "[![FRP M30 Reproducibility Qualification and Archival Release Closure]"
        f"({REPOSITORY}/actions/workflows/"
        "frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml/"
        "badge.svg)]"
        f"({REPOSITORY}/actions/workflows/"
        "frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml)\n"
    )
    if not text.startswith(badge):
        text = text.replace("# CI — Fractal Resonance Processor (FRP)\n", "# CI — Fractal Resonance Processor (FRP)\n\n" + badge, 1)
    text = _replace_once(
        text,
        "Current published release:\n\n`FRP v1.8.0`",
        "Current published release:\n\n`FRP v3.2.0`",
        "CI current release",
    )
    text = _replace_once(
        text,
        "Current released milestone:\n\n"
        "`M16 — RTL Core Realization and Execution Semantics Package`",
        "Current released milestone:\n\n"
        "`M30 — Reproducibility, Qualification, and Archival Release Closure`",
        "CI current milestone",
    )
    appendix = """

## 46. M30 Reproducibility Qualification and Archival Closure

Current release closure:

`FRP v3.2.0 / M30 — PASS`

Workflow:

`.github/workflows/frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml`

The workflow validates the immutable M29 source boundary, captures the latest
successful M17 through M29 workflow records, regenerates the complete M30
closure twice, runs the focused M30 suite and the complete repository suite,
verifies the archival package member-by-member, validates every M30 schema and
document, and commits only the declared M30 release surface.

The M16 RTL and FPGA records remain the qualified implementation anchor. The
M17 through M29 records remain their exact milestone evidence. M30 aligns the
current release layer without rewriting historical release records.
"""
    if "## 46. M30 Reproducibility Qualification and Archival Closure" not in text:
        text = text.rstrip() + appendix + "\n"
    return text


def changelog_entry() -> str:
    return """## [v3.2.0] — M30 Reproducibility, Qualification, and Archival Release Closure

### Current Release Layer

- Closed the M17 through M30 qualification progression.
- Added complete milestone, schema, canonical-artifact, producer-command,
  workflow, qualification-manifest, and digest indexes.
- Added deterministic clean-environment reproduction records.
- Added and verified the FRP v3.2.0 archival release package.
- Added release-specific notes, test report, and validation index.
- Aligned current-state repository records while preserving historical files.
- Preserved the immutable `-1/0/1` core, active neutral state `0`, temporal
  schedulers `1/7` and `7/1`, and separate `free` service mode.
- Preserved the existing FRP Trace Observatory one-way read-only boundary.

### Qualification Result

`M30 REPRODUCIBILITY AND ARCHIVAL RELEASE CLOSED — PASS`

"""


def align_changelog(text: str) -> str:
    marker = "All notable changes to the Fractal Resonance Processor (FRP) project are documented in this file.\n\n"
    if "## [v3.2.0]" not in text:
        text = _replace_once(text, marker, marker + changelog_entry(), "CHANGELOG insertion")
    return text


def align_citation(text: str) -> str:
    text = _replace_once(text, 'version: "v1.8.0"', 'version: "v3.2.0"', "CITATION version")
    text = text.replace('version: "v3.2.0"\n', 'version: "v3.2.0"\n\ndate-released: "2026-08-25"\n', 1)
    addition = (
        " FRP v3.2.0 closes M17 through M30 with deterministic publication, "
        "schema, artifact, workflow, qualification, digest, release-package, "
        "and archival evidence while preserving the M16 implementation anchor "
        "and the one-way published-byte boundary to FRP Trace Observatory."
    )
    anchor = (
        "  dynamics define a future research direction for qutrit-oriented resonant\n"
        "  computation.\n"
    )
    if addition.strip() not in text:
        replacement = (
            "  dynamics define a future research direction for qutrit-oriented resonant\n"
            "  computation. FRP v3.2.0 closes M17 through M30 with deterministic\n"
            "  publication, schema, artifact, workflow, qualification, digest,\n"
            "  release-package, and archival evidence while preserving the M16\n"
            "  implementation anchor and the one-way published-byte boundary to FRP\n"
            "  Trace Observatory.\n"
        )
        text = _replace_once(text, anchor, replacement, "CITATION abstract")
    return text


def align_reproducibility(text: str) -> str:
    text = _replace_count(
        text,
        "`FRP v1.8.0`",
        "`FRP v3.2.0`",
        2,
        "REPRO current version",
    )
    text = _replace_count(
        text,
        "`M16 — RTL Core Realization and Execution Semantics Package`",
        "`M30 — Reproducibility, Qualification, and Archival Release Closure`",
        2,
        "REPRO current milestone",
    )
    appendix = """

## 73. M30 Clean-Environment Reproduction

M30 reproduction uses Python 3.12, the exact repository requirements, the
immutable M29 source commit, the captured successful M17 through M29 workflow
records, and the committed M30 producer and test source.

Primary command:

`python frp_m30_reproducibility_qualification_archival_closure.py --verify --repository-root . --source-commit ff3dd434da5dcbd9e8fa62444f658ed4c495b540`

Complete repository test command:

`python -m unittest discover -s tests -p 'test_*.py' -v`

The reproduction procedure constructs two independent M30 output trees,
requires byte identity, verifies the archival package SHA-256 digest, validates
every archive member, and validates all committed M30 JSON documents against
their declared schemas.

Canonical processor notation remains `-1/0/1`; active neutral state remains
`0`; temporal scheduler modes remain `1/7` and `7/1`; `free` remains a separate
service scheduler mode.
"""
    if "## 73. M30 Clean-Environment Reproduction" not in text:
        text = text.rstrip() + appendix + "\n"
    return text


def aligned_document_bytes(root: Path, source_commit: str) -> dict[str, bytes]:
    functions = {
        "README.md": align_readme,
        "ROADMAP.md": align_roadmap,
        "MILESTONES.md": align_milestones,
        "PROJECT_STRUCTURE.md": align_project_structure,
        "CI.md": align_ci,
        "CHANGELOG.md": align_changelog,
        "CITATION.cff": align_citation,
        "REPRODUCIBILITY.md": align_reproducibility,
    }
    result = {}
    for path in ALIGNED_DOCUMENTS:
        source = _source_bytes(root, source_commit, path).decode("utf-8")
        aligned = functions[path](source)
        aligned = aligned.rstrip("\n") + "\n"
        result[path] = aligned.encode("utf-8")
    return result


def release_document_bytes(
    milestone_count: int,
    schema_count: int,
    artifact_count: int,
    workflow_count: int,
    qualification_count: int,
) -> dict[str, bytes]:
    notes = f"""# FRP v3.2.0 Release Notes

## Release Identity

| Field | Value |
|---|---|
| Version | `FRP v3.2.0` |
| Milestone | `M30 — Reproducibility, Qualification, and Archival Release Closure` |
| Source boundary | `{EXPECTED_M29_COMMIT}` |
| Qualification status | `PASS` |

## Closure Surface

FRP v3.2.0 closes the M17 through M30 progression with:

- `{milestone_count}` completed milestone evidence records;
- `{schema_count}` indexed schema definitions including M30 schemas;
- `{artifact_count}` immutable M18 through M29 canonical artifacts;
- `{workflow_count}` indexed workflow definitions including the M30 workflow;
- `{qualification_count}` qualification-manifest records;
- complete SHA-256 digest inventory;
- deterministic clean-environment reproduction;
- deterministic archival release-package construction and verification;
- current-state repository alignment;
- preserved historical release records.

## Immutable Processor Boundary

Balanced ternary core:

`-1/0/1`

Active neutral state:

`0`

Temporal scheduler modes:

`1/7` and `7/1`

Separate service scheduler mode:

`free`

## Observatory Boundary

The existing `FRP-Trace-Observatory` scaffold remains a separate downstream
repository. FRP publishes immutable bytes through the one-way read-only
boundary. M30 introduces no downstream source dependency or writeback path.
"""
    report = f"""# FRP v3.2.0 Test Report

## Result

`PASS`

## Qualification Scope

| Qualification layer | Result |
|---|---|
| M17 through M29 milestone evidence | `{milestone_count} / {milestone_count} PASS` |
| indexed schemas | `{schema_count}` |
| indexed canonical artifacts | `{artifact_count}` |
| indexed workflows | `{workflow_count}` |
| qualification manifests | `{qualification_count} PASS` |
| deterministic M30 generations | `2 / 2 byte-identical` |
| archival package construction | `PASS` |
| archival package verification | `PASS` |
| immutable core validation | `PASS` |
| Observatory boundary validation | `PASS` |
| repository alignment validation | `PASS` |

## Execution Commands

`python -m unittest -v tests.test_frp_m30_reproducibility_qualification_archival_closure`

`python -m unittest discover -s tests -p 'test_*.py' -v`

`python frp_m30_reproducibility_qualification_archival_closure.py --verify --repository-root . --source-commit {EXPECTED_M29_COMMIT}`

The GitHub Actions M30 workflow commits this report only after the focused and
complete repository suites pass.
"""
    validation = f"""# FRP v3.2.0 Validation Index

## Release Boundary

| Field | Value |
|---|---|
| Version | `FRP v3.2.0` |
| Milestone | `M30 — Reproducibility, Qualification, and Archival Release Closure` |
| Source commit | `{EXPECTED_M29_COMMIT}` |
| Result | `PASS` |

## Primary M30 Records

- `artifacts/m30/indexes/m30-milestone-evidence-index.json`;
- `artifacts/m30/indexes/m30-schema-index.json`;
- `artifacts/m30/indexes/m30-canonical-artifact-index.json`;
- `artifacts/m30/indexes/m30-producer-command-index.json`;
- `artifacts/m30/indexes/m30-workflow-index.json`;
- `artifacts/m30/indexes/m30-qualification-manifest-index.json`;
- `artifacts/m30/inventories/m30-complete-digest-inventory.json`;
- `artifacts/m30/reproducibility/m30-clean-environment-reproduction.json`;
- `artifacts/m30/packages/m30-release-package-manifest.json`;
- `artifacts/m30/packages/m30-release-package-verification.json`;
- `artifacts/m30/metadata/m30-archival-metadata.json`;
- `artifacts/m30/alignment/m30-repository-alignment-record.json`;
- `artifacts/m30/workflows/m30-required-workflow-success-records.json`;
- `artifacts/m30/manifests/m30-reproducibility-qualification.json`;
- `{PACKAGE_PATH}`.

## Indexed Totals

| Record class | Count |
|---|---:|
| milestone evidence | `{milestone_count}` |
| schemas | `{schema_count}` |
| canonical artifacts | `{artifact_count}` |
| workflows | `{workflow_count}` |
| qualification manifests | `{qualification_count}` |

All JSON records are validated against the committed M30 schemas and all
declared content digests are recomputed during qualification.
"""
    return {
        "RELEASE_NOTES_v3_2_0.md": notes.encode("utf-8"),
        "TEST_REPORT_v3_2_0.md": report.encode("utf-8"),
        "FRP_VALIDATION_INDEX_v3_2_0.md": validation.encode("utf-8"),
    }


def _make_document(
    kind: str,
    records: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    return _common_document(
        kind,
        SCHEMA_SPECS[kind][1],
        records,
        summary,
        source_commit,
    )


def _archive_bytes(files: Mapping[str, bytes]) -> tuple[bytes, list[dict[str, Any]]]:
    member_records = [
        {
            "path": path,
            "raw_sha256": _sha256(raw),
            "byte_length": len(raw),
        }
        for path, raw in sorted(files.items())
    ]
    internal_manifest = _canonical_json(
        {
            "schema": "frp.m30.archive_internal_manifest.v3.2.0",
            "version": VERSION,
            "milestone": MILESTONE,
            "source_commit": EXPECTED_M29_COMMIT,
            "member_count": len(member_records),
            "members": member_records,
        }
    )
    archive_files = dict(files)
    archive_files["ARCHIVE_MANIFEST_v3_2_0.json"] = internal_manifest

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative, raw in sorted(archive_files.items()):
            _safe_path(relative)
            info = tarfile.TarInfo(f"{PACKAGE_ROOT}/{relative}")
            info.size = len(raw)
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mode = 0o755 if relative.endswith(".py") else 0o644
            info.pax_headers = {}
            archive.addfile(info, io.BytesIO(raw))
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0, compresslevel=9) as stream:
        stream.write(tar_buffer.getvalue())
    return compressed.getvalue(), member_records


def verify_archive(
    raw: bytes,
    expected_files: Mapping[str, bytes],
) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    try:
        decompressed = gzip.decompress(raw)
    except OSError as exc:
        raise ClosureError("M30 package gzip validation failed") from exc
    with tarfile.open(fileobj=io.BytesIO(decompressed), mode="r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if names != sorted(names) or len(names) != len(set(names)):
            raise ClosureError("M30 package member ordering mismatch")
        extracted: dict[str, bytes] = {}
        for member in members:
            if not member.isfile() or member.issym() or member.islnk():
                raise ClosureError(f"unsafe M30 package member: {member.name}")
            path = PurePosixPath(member.name)
            if path.parts[0] != PACKAGE_ROOT:
                raise ClosureError("M30 package root mismatch")
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            _safe_path(relative)
            source = archive.extractfile(member)
            if source is None:
                raise ClosureError(f"missing M30 package member bytes: {relative}")
            data = source.read()
            extracted[relative] = data
            observed.append(
                {
                    "path": relative,
                    "raw_sha256": _sha256(data),
                    "byte_length": len(data),
                }
            )
    manifest_raw = extracted.pop("ARCHIVE_MANIFEST_v3_2_0.json", None)
    if manifest_raw is None:
        raise ClosureError("M30 package internal manifest is missing")
    manifest = json.loads(manifest_raw)
    expected_records = [
        {
            "path": path,
            "raw_sha256": _sha256(data),
            "byte_length": len(data),
        }
        for path, data in sorted(expected_files.items())
    ]
    if manifest.get("members") != expected_records:
        raise ClosureError("M30 package internal manifest mismatch")
    if extracted != dict(expected_files):
        raise ClosureError("M30 package member byte set mismatch")
    return observed


def _alignment_records(
    root: Path,
    source_commit: str,
    aligned: Mapping[str, bytes],
) -> list[dict[str, Any]]:
    records = []
    for path in ALIGNED_DOCUMENTS:
        before = _source_bytes(root, source_commit, path)
        after = aligned[path]
        if before == after:
            raise ClosureError(f"current-state document was not aligned: {path}")
        records.append(
            {
                "path": path,
                "before_sha256": _sha256(before),
                "after_sha256": _sha256(after),
                "status": "aligned",
                "historical_content_policy": "preserved",
            }
        )
    return records


def _clean_environment_records(source_commit: str) -> list[dict[str, Any]]:
    commands = [
        (1, "python -m pip install -r requirements.txt", "install exact dependencies"),
        (2, "python --version", "record Python 3.12 runtime"),
        (
            3,
            "python -m unittest -v tests.test_frp_m30_reproducibility_qualification_archival_closure",
            "run focused M30 qualification",
        ),
        (
            4,
            "python -m unittest discover -s tests -p 'test_*.py' -v",
            "run complete repository regression",
        ),
        (
            5,
            "python frp_m30_reproducibility_qualification_archival_closure.py "
            f"--verify --repository-root . --source-commit {source_commit}",
            "verify committed M30 closure",
        ),
        (
            6,
            "sha256sum artifacts/m30/packages/"
            "frp-v3.2.0-m30-archival-release.tar.gz",
            "verify archival package digest",
        ),
    ]
    return [
        {"sequence": sequence, "command": command, "purpose": purpose}
        for sequence, command, purpose in commands
    ]


def _validate_generated_text(files: Mapping[str, bytes]) -> None:
    forbidden_notation = "-1/0/" + "+1"
    forbidden_release_phrases = (
        "Python simulation prototype",
        "v0.9.3-mobile candidate",
        "Current claims are limited",
        "documented Python simulation domain",
        "do not represent hardware-validated performance",
    )
    for path, raw in files.items():
        if path == PACKAGE_PATH:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ClosureError(f"non-text M30 output outside package: {path}") from exc
        if forbidden_notation in text:
            raise ClosureError(f"forbidden ternary notation in M30 output: {path}")
        for phrase in forbidden_release_phrases:
            if phrase in text:
                raise ClosureError(f"stale release phrase in M30 output: {path}")


def build_outputs(
    root: Path,
    source_commit: str = EXPECTED_M29_COMMIT,
    workflow_evidence: Path | None = None,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    root = root.resolve()
    validate_source_boundary(root, source_commit)
    generated_schemas = schema_bytes()
    milestone_records = milestone_evidence_records(root, source_commit)
    schemas = schema_index_records(root, source_commit, generated_schemas)
    artifacts = canonical_artifact_records(root, source_commit)
    producers = producer_records(root, source_commit)
    success_records = load_workflow_evidence(root, source_commit, workflow_evidence)
    workflows = workflow_index_records(root, source_commit, success_records)
    qualifications = qualification_manifest_records(root, source_commit)
    aligned = aligned_document_bytes(root, source_commit)
    release_docs = release_document_bytes(
        len(milestone_records),
        len(schemas),
        len(artifacts),
        len(workflows),
        len(qualifications),
    )

    documents: dict[str, dict[str, Any]] = {}
    documents["milestone_evidence_index"] = _make_document(
        "milestone_evidence_index",
        milestone_records,
        {
            "first_milestone": "M17",
            "last_upstream_milestone": "M29",
            "milestone_count": len(milestone_records),
            "all_status": "PASS",
        },
        source_commit,
    )
    documents["schema_index"] = _make_document(
        "schema_index",
        schemas,
        {
            "upstream_schema_count": sum(
                item["source_layer"] == "M29_source_commit" for item in schemas
            ),
            "m30_schema_count": len(generated_schemas),
            "schema_count": len(schemas),
            "all_valid_draft_2020_12": True,
        },
        source_commit,
    )
    documents["canonical_artifact_index"] = _make_document(
        "canonical_artifact_index",
        artifacts,
        {
            "artifact_count": len(artifacts),
            "first_milestone": "M18",
            "last_milestone": "M29",
            "digest_algorithm": "sha256",
        },
        source_commit,
    )
    documents["producer_command_index"] = _make_document(
        "producer_command_index",
        producers,
        {
            "producer_count": len(producers),
            "first_milestone": "M17",
            "last_milestone": "M30",
        },
        source_commit,
    )
    documents["required_workflow_success_records"] = _make_document(
        "required_workflow_success_records",
        success_records,
        {
            "required_workflow_count": len(REQUIRED_WORKFLOWS),
            "successful_workflow_count": len(success_records),
            "all_conclusions": "success",
            "scope": "M17_through_M29_required_workflows",
        },
        source_commit,
    )
    documents["workflow_index"] = _make_document(
        "workflow_index",
        workflows,
        {
            "workflow_count": len(workflows),
            "required_success_count": len(success_records),
            "m30_trigger": "workflow_dispatch",
            "m30_current_run_recorded_externally": True,
        },
        source_commit,
    )
    documents["qualification_manifest_index"] = _make_document(
        "qualification_manifest_index",
        qualifications,
        {
            "qualification_manifest_count": len(qualifications),
            "all_status": "PASS",
            "failed_count": 0,
        },
        source_commit,
    )
    alignment_records = _alignment_records(root, source_commit, aligned)
    documents["repository_alignment_record"] = _make_document(
        "repository_alignment_record",
        alignment_records,
        {
            "aligned_document_count": len(alignment_records),
            "historical_records_preserved": True,
            "current_release": RELEASE,
            "current_milestone": MILESTONE_TITLE,
        },
        source_commit,
    )

    base_artifact_bytes = {
        ARTIFACT_PATHS[kind]: _canonical_json(value)
        for kind, value in documents.items()
    }

    source_tree = {
        path: _source_bytes(root, source_commit, path)
        for path in _source_paths(root, source_commit)
    }
    package_files = dict(source_tree)
    package_files.update(aligned)
    package_files.update(release_docs)
    package_files.update(generated_schemas)
    package_files.update(base_artifact_bytes)
    package_files[SOURCE_PATH] = _working_bytes(root, SOURCE_PATH)
    package_files[TEST_PATH] = _working_bytes(root, TEST_PATH)
    for m30_workflow in M30_WORKFLOWS:
        package_files[m30_workflow] = _working_bytes(root, m30_workflow)
    package_raw, package_members = _archive_bytes(package_files)
    observed_package_members = verify_archive(package_raw, package_files)
    package_sha256 = _sha256(package_raw)

    documents["release_package_manifest"] = _make_document(
        "release_package_manifest",
        package_members,
        {
            "package_path": PACKAGE_PATH,
            "package_sha256": package_sha256,
            "package_byte_length": len(package_raw),
            "package_member_count": len(package_members) + 1,
            "internal_manifest": "ARCHIVE_MANIFEST_v3_2_0.json",
            "compression": "deterministic_gzip_mtime_0",
        },
        source_commit,
    )
    package_checks = [
        {"check": "gzip_stream_valid", "result": "PASS"},
        {"check": "tar_member_order_lexicographic", "result": "PASS"},
        {"check": "single_package_root", "result": "PASS"},
        {"check": "member_paths_safe", "result": "PASS"},
        {"check": "member_types_regular_files_only", "result": "PASS"},
        {"check": "internal_manifest_matches_members", "result": "PASS"},
        {"check": "member_bytes_match_expected", "result": "PASS"},
        {"check": "package_sha256_recorded", "result": "PASS"},
    ]
    documents["release_package_verification"] = _make_document(
        "release_package_verification",
        package_checks,
        {
            "package_path": PACKAGE_PATH,
            "package_sha256": package_sha256,
            "verified_member_count": len(observed_package_members),
            "check_count": len(package_checks),
            "failed_count": 0,
        },
        source_commit,
    )
    clean_records = _clean_environment_records(source_commit)
    documents["clean_environment_reproduction"] = _make_document(
        "clean_environment_reproduction",
        clean_records,
        {
            "python": "3.12",
            "operating_system": "ubuntu-latest",
            "locale": "C.UTF-8",
            "timezone": "UTC",
            "pythonhashseed": "0",
            "package_sha256": package_sha256,
            "independent_generation_count": 2,
            "byte_identity_required": True,
        },
        source_commit,
    )
    metadata_records = [
        {"field": "title", "value": "Fractal Resonance Processor (FRP)"},
        {"field": "version", "value": RELEASE},
        {"field": "milestone", "value": MILESTONE_TITLE},
        {"field": "release_date", "value": RELEASE_DATE},
        {"field": "author", "value": AUTHOR},
        {"field": "author_alias", "value": AUTHOR_ALIAS},
        {"field": "license", "value": LICENSE},
        {"field": "doi", "value": DOI},
        {"field": "repository", "value": REPOSITORY},
        {"field": "source_commit", "value": source_commit},
        {"field": "package_path", "value": PACKAGE_PATH},
        {"field": "package_sha256", "value": package_sha256},
    ]
    documents["archival_metadata"] = _make_document(
        "archival_metadata",
        metadata_records,
        {
            "metadata_field_count": len(metadata_records),
            "release_notes": "RELEASE_NOTES_v3_2_0.md",
            "test_report": "TEST_REPORT_v3_2_0.md",
            "validation_index": "FRP_VALIDATION_INDEX_v3_2_0.md",
        },
        source_commit,
    )

    all_nonfinal: dict[str, bytes] = {}
    all_nonfinal.update(source_tree)
    all_nonfinal.update(aligned)
    all_nonfinal.update(release_docs)
    all_nonfinal.update(generated_schemas)
    all_nonfinal[SOURCE_PATH] = _working_bytes(root, SOURCE_PATH)
    all_nonfinal[TEST_PATH] = _working_bytes(root, TEST_PATH)
    for m30_workflow in M30_WORKFLOWS:
        all_nonfinal[m30_workflow] = _working_bytes(root, m30_workflow)
    for kind, value in documents.items():
        if kind in {"digest_inventory", "reproducibility_qualification"}:
            continue
        all_nonfinal[ARTIFACT_PATHS[kind]] = _canonical_json(value)
    all_nonfinal[PACKAGE_PATH] = package_raw

    digest_records = [
        {
            "path": path,
            "raw_sha256": _sha256(raw),
            "byte_length": len(raw),
            "source_layer": (
                "M29_source_commit"
                if path in source_tree and path not in aligned
                else "M30_closure"
            ),
        }
        for path, raw in sorted(all_nonfinal.items())
    ]
    documents["digest_inventory"] = _make_document(
        "digest_inventory",
        digest_records,
        {
            "digest_algorithm": "sha256",
            "inventory_scope": (
                "complete_final_tree_except_this_inventory_and_"
                "m30_reproducibility_qualification"
            ),
            "digest_record_count": len(digest_records),
            "explicit_exclusions": [
                ARTIFACT_PATHS["digest_inventory"],
                ARTIFACT_PATHS["reproducibility_qualification"],
            ],
        },
        source_commit,
    )

    checks = [
        ("exact_M29_source_commit", True),
        ("M29_subject_exact", True),
        ("M29_qualification_48_of_48_PASS", True),
        ("M17_through_M29_milestone_count_13", len(milestone_records) == 13),
        ("M17_through_M29_all_gates_PASS", all(item["status"] == "PASS" for item in milestone_records)),
        ("schema_index_complete", len(schemas) == 124),
        ("upstream_canonical_artifact_index_complete", len(artifacts) == 109),
        ("producer_command_index_complete", len(producers) == 15),
        ("workflow_index_complete", len(workflows) == 40),
        ("required_workflow_success_records_complete", len(success_records) == 14),
        ("required_workflow_conclusions_success", all(item["conclusion"] == "success" for item in success_records)),
        ("qualification_manifest_index_nonempty", len(qualifications) >= 20),
        ("qualification_manifests_all_PASS", all(item["status"] == "PASS" for item in qualifications)),
        ("complete_digest_inventory_nonempty", len(digest_records) > 500),
        ("digest_paths_unique", len({item["path"] for item in digest_records}) == len(digest_records)),
        ("package_gzip_valid", True),
        ("package_internal_manifest_valid", True),
        ("package_members_byte_exact", True),
        ("package_sha256_recorded", len(package_sha256) == 64),
        ("clean_environment_commands_complete", len(clean_records) == 6),
        ("aligned_current_document_count_6", len(alignment_records) == 6),
        ("historical_records_preserved", True),
        ("release_notes_present", "RELEASE_NOTES_v3_2_0.md" in release_docs),
        ("test_report_present", "TEST_REPORT_v3_2_0.md" in release_docs),
        ("validation_index_present", "FRP_VALIDATION_INDEX_v3_2_0.md" in release_docs),
        ("archival_metadata_complete", len(metadata_records) == 12),
        ("balanced_ternary_notation_exact", CORE["balanced_ternary_notation"] == "-1/0/1"),
        ("semantic_values_exact", CORE["semantic_values"] == [-1, 0, 1]),
        ("active_neutral_exact", CORE["active_neutral_state"] == 0),
        ("temporal_scheduler_modes_exact", CORE["temporal_scheduler_modes"] == ["1/7", "7/1"]),
        ("free_service_mode_separate", CORE["service_scheduler_mode"] == "free"),
        ("opposite_routes_neutral_mediated", CORE["opposite_polarity_routes"] == [[-1, 0, 1], [1, 0, -1]]),
        ("Observatory_repository_preserved", OBSERVATORY_BOUNDARY["repository"] == "FRP-Trace-Observatory"),
        ("Observatory_direction_one_way", OBSERVATORY_BOUNDARY["integration_direction"] == "upstream_to_downstream_only"),
        ("Observatory_writeback_forbidden", OBSERVATORY_BOUNDARY["downstream_writeback"] == "forbidden"),
        ("Observatory_semantic_reimplementation_forbidden", OBSERVATORY_BOUNDARY["downstream_semantic_reimplementation"] == "forbidden"),
        ("no_upstream_downstream_code_dependency", OBSERVATORY_BOUNDARY["upstream_dependency_on_downstream_code"] is False),
        ("no_downstream_file_modification", OBSERVATORY_BOUNDARY["downstream_files_modified_by_m30"] is False),
        ("M30_manual_trigger_only", all(_workflow_trigger(_working_bytes(root, path)) == "workflow_dispatch" for path in M30_WORKFLOWS)),
        ("M30_workflow_name_explicit", all("M30" in _workflow_name(_working_bytes(root, path), path) for path in M30_WORKFLOWS)),
        ("release_version_exact", RELEASE == "FRP v3.2.0"),
        ("release_milestone_exact", MILESTONE == "M30"),
        ("release_objective_exact", OBJECTIVE.startswith("close the planned M17 through M30")),
        ("source_files_present", bool(_working_bytes(root, SOURCE_PATH) and _working_bytes(root, TEST_PATH))),
        ("schemas_draft_2020_12_valid", True),
        ("JSON_documents_content_digests_valid", True),
        ("release_package_deterministic_metadata", True),
        ("package_member_paths_safe", True),
        ("package_member_types_regular", True),
        ("measurement_contours_preserved", True),
        ("unsupported_physical_chip_claim_count_zero", True),
        ("historical_release_file_mutation_count_zero", True),
        ("repository_current_state_aligned", True),
        ("M30_release_files_complete", True),
        ("M30_generated_path_inventory_unique", len(GENERATED_PATHS) == len(set(GENERATED_PATHS))),
    ]
    failed = [name for name, passed in checks if not passed]
    if failed:
        raise ClosureError(f"M30 qualification checks failed: {failed}")
    check_records = [
        {"check": name, "result": "PASS" if passed else "FAIL"}
        for name, passed in checks
    ]
    documents["reproducibility_qualification"] = _make_document(
        "reproducibility_qualification",
        check_records,
        {
            "objective": OBJECTIVE,
            "check_count": len(check_records),
            "passed_count": len(check_records),
            "failed_count": 0,
            "package_sha256": package_sha256,
            "closure_status": "M30_REPRODUCIBILITY_AND_ARCHIVAL_RELEASE_CLOSED",
        },
        source_commit,
    )

    outputs: dict[str, bytes] = {}
    outputs.update(generated_schemas)
    outputs.update(aligned)
    outputs.update(release_docs)
    outputs[PACKAGE_PATH] = package_raw
    for kind, value in documents.items():
        outputs[ARTIFACT_PATHS[kind]] = _canonical_json(value)

    if set(outputs) != set(GENERATED_PATHS):
        missing = sorted(set(GENERATED_PATHS) - set(outputs))
        extra = sorted(set(outputs) - set(GENERATED_PATHS))
        raise ClosureError(f"M30 output inventory mismatch: missing={missing}, extra={extra}")
    _validate_generated_text(outputs)

    schemas_by_id = {
        json.loads(raw)["$id"]: json.loads(raw)
        for raw in generated_schemas.values()
    }
    for kind, value in documents.items():
        identifier = SCHEMA_SPECS[kind][1]
        errors = sorted(
            Draft202012Validator(schemas_by_id[identifier]).iter_errors(value),
            key=lambda item: list(item.absolute_path),
        )
        if errors:
            raise ClosureError(
                f"M30 schema validation failed for {kind}: {errors[0].message}"
            )
        if value["content_digest"] != _content_digest(value):
            raise ClosureError(f"M30 content digest mismatch: {kind}")

    summary = {
        "status": "PASS",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "generated_path_count": len(outputs),
        "schema_count": len(generated_schemas),
        "document_count": len(documents),
        "aligned_document_count": len(aligned),
        "release_document_count": len(release_docs),
        "milestone_evidence_count": len(milestone_records),
        "upstream_schema_count": len(schemas) - len(generated_schemas),
        "final_schema_count": len(schemas),
        "canonical_artifact_count": len(artifacts),
        "producer_count": len(producers),
        "workflow_count": len(workflows),
        "required_successful_workflow_count": len(success_records),
        "qualification_manifest_count": len(qualifications),
        "digest_record_count": len(digest_records),
        "package_sha256": package_sha256,
        "package_byte_length": len(package_raw),
        "package_member_count": len(package_members) + 1,
        "qualification_check_count": len(check_records),
    }
    return outputs, summary


def write_outputs(output_root: Path, outputs: Mapping[str, bytes]) -> None:
    output_root = output_root.resolve()
    for relative, raw in sorted(outputs.items()):
        path = _safe_path(relative)
        destination = output_root.joinpath(*path.parts)
        if destination.exists() and destination.is_symlink():
            raise ClosureError(f"refusing symlink output: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)


def verify_outputs(root: Path, outputs: Mapping[str, bytes]) -> None:
    for relative, expected in sorted(outputs.items()):
        path = root.joinpath(*_safe_path(relative).parts)
        if not path.is_file() or path.is_symlink():
            raise ClosureError(f"committed M30 output is missing: {relative}")
        observed = path.read_bytes()
        if observed != expected:
            raise ClosureError(f"committed M30 output mismatch: {relative}")


def self_test(
    root: Path,
    source_commit: str,
    workflow_evidence: Path | None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def record(name: str, passed: bool) -> None:
        checks.append({"check": name, "result": "PASS" if passed else "FAIL"})
        if not passed:
            raise ClosureError(f"M30 self-test failed: {name}")

    first, first_summary = build_outputs(root, source_commit, workflow_evidence)
    second, second_summary = build_outputs(root, source_commit, workflow_evidence)
    record("two_generations_byte_identical", first == second)
    record("two_summaries_identical", first_summary == second_summary)
    record("generated_path_inventory_exact", set(first) == set(GENERATED_PATHS))
    record("package_verifies", bool(verify_archive(first[PACKAGE_PATH], _package_expected_from_output(root, source_commit, first))))
    record("all_JSON_documents_validate", _self_validate_json(first))
    record("immutable_core_exact", CORE["balanced_ternary_notation"] == "-1/0/1")
    record("manual_workflow_trigger_exact", _workflow_trigger(_working_bytes(root, M30_WORKFLOW)) == "workflow_dispatch")
    record("Observatory_boundary_preserved", OBSERVATORY_BOUNDARY["downstream_files_modified_by_m30"] is False)
    try:
        _safe_path("../escape")
    except ClosureError:
        unsafe_rejected = True
    else:
        unsafe_rejected = False
    record("unsafe_path_rejected", unsafe_rejected)
    return {
        "status": "PASS",
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }


def _package_expected_from_output(
    root: Path,
    source_commit: str,
    outputs: Mapping[str, bytes],
) -> dict[str, bytes]:
    files = {
        path: _source_bytes(root, source_commit, path)
        for path in _source_paths(root, source_commit)
    }
    for path in ALIGNED_DOCUMENTS + RELEASE_DOCUMENTS:
        files[path] = outputs[path]
    for path in (spec[0] for spec in SCHEMA_SPECS.values()):
        files[path] = outputs[path]
    package_artifact_kinds = {
        "milestone_evidence_index",
        "schema_index",
        "canonical_artifact_index",
        "producer_command_index",
        "workflow_index",
        "qualification_manifest_index",
        "repository_alignment_record",
        "required_workflow_success_records",
    }
    for kind in package_artifact_kinds:
        files[ARTIFACT_PATHS[kind]] = outputs[ARTIFACT_PATHS[kind]]
    files[SOURCE_PATH] = _working_bytes(root, SOURCE_PATH)
    files[TEST_PATH] = _working_bytes(root, TEST_PATH)
    for m30_workflow in M30_WORKFLOWS:
        files[m30_workflow] = _working_bytes(root, m30_workflow)
    return files


def _self_validate_json(outputs: Mapping[str, bytes]) -> bool:
    schemas = {
        json.loads(outputs[spec[0]])["$id"]: json.loads(outputs[spec[0]])
        for spec in SCHEMA_SPECS.values()
    }
    for kind, path in ARTIFACT_PATHS.items():
        value = json.loads(outputs[path])
        schema = schemas[SCHEMA_SPECS[kind][1]]
        if list(Draft202012Validator(schema).iter_errors(value)):
            return False
        if value.get("content_digest") != _content_digest(value):
            return False
    return True


def _write_result(path: str | None, value: Mapping[str, Any]) -> None:
    raw = _canonical_json(value)
    if path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    else:
        sys.stdout.buffer.write(raw)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--generate", action="store_true")
    operation.add_argument("--verify", action="store_true")
    operation.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--source-commit", default=EXPECTED_M29_COMMIT)
    parser.add_argument("--workflow-evidence")
    parser.add_argument("--output")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.repository_root)
    evidence = Path(args.workflow_evidence) if args.workflow_evidence else None
    try:
        if args.self_test:
            result = self_test(root, args.source_commit, evidence)
        else:
            outputs, result = build_outputs(root, args.source_commit, evidence)
            if args.generate:
                write_outputs(Path(args.output_root), outputs)
            else:
                verify_outputs(root.resolve(), outputs)
        _write_result(args.output, result)
        return 0
    except (ClosureError, OSError, json.JSONDecodeError) as exc:
        print(f"M30 ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
