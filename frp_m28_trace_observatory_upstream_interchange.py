#!/usr/bin/env python3
"""Generate and verify the FRP M28 Trace Observatory upstream interchange."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator


VERSION = "3.0.0"
MILESTONE = "M28"
MILESTONE_TITLE = "M28 - Trace Observatory Upstream Interchange"
EXPECTED_M27_COMMIT = "23e464206f85cd9473101d9221027ee33d9dd094"
EXPECTED_M27_SUBJECT = "Add M27 long-run stability and telemetry qualification"
WORKFLOW_PATH = (
    ".github/workflows/"
    "frp-m28-trace-observatory-upstream-interchange-workflow.yml"
)

OBSERVATORY_REPOSITORY = "FRP-Trace-Observatory"
OBSERVATORY_AUDITED_COMMIT = "a9d71657c56221d0d9b72fb6e954e0028f096a9e"
OBSERVATORY_CI_WORKFLOW = ".github/workflows/observatory-ci.yml"
OBSERVATORY_REGISTRY_PATH = "schemas/registry.py"
OBSERVATORY_INTEGRATION_CONTRACT = "docs/integration_contract.md"
OBSERVATORY_TEST_COUNT = 275
OBSERVATORY_MODES = (
    "artifact_auditor",
    "ternary_transition_visualizer",
    "trace_explorer",
)

CONTRACT_SCHEMA_ID = "frp.m28.trace_observatory_upstream_contract.v3.0.0"
TRACE_SCHEMA_ID = "frp.m28.trace_observatory_canonical_trace_bundle.v3.0.0"
FIXTURE_SCHEMA_ID = "frp.m28.trace_observatory_fixture_manifest.v3.0.0"
REGISTRY_SCHEMA_ID = "frp.m28.trace_observatory_compatibility_registry.v3.0.0"
QUALIFICATION_SCHEMA_ID = (
    "frp.m28.trace_observatory_interchange_qualification.v3.0.0"
)

CONTRACT_ARTIFACT = (
    "artifacts/m28/contracts/m28-trace-observatory-upstream-contract.json"
)
TRACE_ARTIFACT = (
    "artifacts/m28/exports/m28-observatory-canonical-trace-bundle.json"
)
FIXTURE_ARTIFACT = (
    "artifacts/m28/fixtures/m28-observatory-fixture-manifest.json"
)
REGISTRY_ARTIFACT = (
    "artifacts/m28/registry/m28-observatory-compatibility-registry.json"
)
QUALIFICATION_ARTIFACT = (
    "artifacts/m28/manifests/"
    "m28-trace-observatory-interchange-qualification.json"
)

CONTRACT_SCHEMA = (
    "schemas/m28/"
    "frp_m28_trace_observatory_upstream_contract.v3.0.0.schema.json"
)
TRACE_SCHEMA = (
    "schemas/m28/"
    "frp_m28_trace_observatory_canonical_trace_bundle.v3.0.0.schema.json"
)
FIXTURE_SCHEMA = (
    "schemas/m28/"
    "frp_m28_trace_observatory_fixture_manifest.v3.0.0.schema.json"
)
REGISTRY_SCHEMA = (
    "schemas/m28/"
    "frp_m28_trace_observatory_compatibility_registry.v3.0.0.schema.json"
)
QUALIFICATION_SCHEMA = (
    "schemas/m28/"
    "frp_m28_trace_observatory_interchange_qualification.v3.0.0.schema.json"
)
SCHEMA_REGISTRY = "schemas/m28/frp_m28_schema_registry.json"

SCHEMA_PATHS = {
    CONTRACT_SCHEMA_ID: CONTRACT_SCHEMA,
    TRACE_SCHEMA_ID: TRACE_SCHEMA,
    FIXTURE_SCHEMA_ID: FIXTURE_SCHEMA,
    REGISTRY_SCHEMA_ID: REGISTRY_SCHEMA,
    QUALIFICATION_SCHEMA_ID: QUALIFICATION_SCHEMA,
}

PRIMARY_ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    TRACE_ARTIFACT,
    FIXTURE_ARTIFACT,
    REGISTRY_ARTIFACT,
)
ARTIFACT_PATHS = (*PRIMARY_ARTIFACT_PATHS, QUALIFICATION_ARTIFACT)
GENERATED_PATHS = (*SCHEMA_PATHS.values(), SCHEMA_REGISTRY, *ARTIFACT_PATHS)

M19_RTL_TRACE = "artifacts/m19/execution/m16-rtl-execution-trace.json"
M19_RTL_SCHEMA = "schemas/m19/frp_m16_rtl_execution_trace.v2.1.0.schema.json"
M19_FPGA_TRACE = (
    "artifacts/m19/execution/m16-fpga-preparation-execution-trace.json"
)
M19_FPGA_SCHEMA = (
    "schemas/m19/"
    "frp_m16_fpga_preparation_execution_trace.v2.1.0.schema.json"
)
M27_CHECKPOINTS = (
    "artifacts/m27/checkpoints/m27-long-run-checkpoint-evidence.json"
)
M27_CHECKPOINT_SCHEMA = (
    "schemas/m27/"
    "frp_m27_long_run_checkpoint_evidence.v2.9.0.schema.json"
)
M27_TELEMETRY = "artifacts/m27/telemetry/m27-telemetry-semantics.json"
M27_TELEMETRY_SCHEMA = (
    "schemas/m27/frp_m27_telemetry_semantics.v2.9.0.schema.json"
)
M27_CONTRACT = "artifacts/m27/contracts/m27-long-run-telemetry-contract.json"
M27_CONTRACT_SCHEMA = (
    "schemas/m27/frp_m27_long_run_telemetry_contract.v2.9.0.schema.json"
)
M27_QUALIFICATION = (
    "artifacts/m27/manifests/m27-long-run-stability-qualification.json"
)
M27_QUALIFICATION_SCHEMA = (
    "schemas/m27/"
    "frp_m27_long_run_stability_qualification.v2.9.0.schema.json"
)

SOURCE_FIXTURE_SPECS = (
    {
        "fixture_id": "m16-rtl-execution-trace",
        "artifact_path": M19_RTL_TRACE,
        "schema_path": M19_RTL_SCHEMA,
        "source_identifier": "frp.m16.rtl_execution_trace.v2.1.0",
        "source_kind": "m16_rtl_execution_trace",
        "measurement_contour": "m16_rtl_execution",
        "observatory_modes": OBSERVATORY_MODES,
    },
    {
        "fixture_id": "m16-fpga-preparation-execution-trace",
        "artifact_path": M19_FPGA_TRACE,
        "schema_path": M19_FPGA_SCHEMA,
        "source_identifier": (
            "frp.m16.fpga_preparation_execution_trace.v2.1.0"
        ),
        "source_kind": "m16_fpga_preparation_execution_trace",
        "measurement_contour": "m16_fpga_preparation_execution",
        "observatory_modes": OBSERVATORY_MODES,
    },
    {
        "fixture_id": "m27-long-run-checkpoint-evidence",
        "artifact_path": M27_CHECKPOINTS,
        "schema_path": M27_CHECKPOINT_SCHEMA,
        "source_identifier": "m27-long-run-checkpoint-evidence-v2.9.0",
        "source_kind": "long_run_checkpoint_evidence",
        "measurement_contour": "m27_long_run_checkpoint_qualification",
        "observatory_modes": OBSERVATORY_MODES,
    },
    {
        "fixture_id": "m27-telemetry-semantics",
        "artifact_path": M27_TELEMETRY,
        "schema_path": M27_TELEMETRY_SCHEMA,
        "source_identifier": "m27-telemetry-semantics-v2.9.0",
        "source_kind": "telemetry_semantics",
        "measurement_contour": "m27_long_run_telemetry_semantics",
        "observatory_modes": (
            "artifact_auditor",
            "ternary_transition_visualizer",
        ),
    },
    {
        "fixture_id": "m27-long-run-telemetry-contract",
        "artifact_path": M27_CONTRACT,
        "schema_path": M27_CONTRACT_SCHEMA,
        "source_identifier": "m27-long-run-telemetry-contract-v2.9.0",
        "source_kind": "long_run_telemetry_contract",
        "measurement_contour": "m27_long_run_telemetry_qualification",
        "observatory_modes": ("artifact_auditor",),
    },
    {
        "fixture_id": "m27-long-run-stability-qualification",
        "artifact_path": M27_QUALIFICATION,
        "schema_path": M27_QUALIFICATION_SCHEMA,
        "source_identifier": (
            "m27-long-run-stability-qualification-v2.9.0"
        ),
        "source_kind": "long_run_stability_qualification",
        "measurement_contour": "m27_long_run_telemetry_qualification",
        "observatory_modes": ("artifact_auditor",),
    },
)

HEX64_PATTERN = "^[0-9a-f]{64}$"
SCHEMA_PATTERN = "^frp\\.m28\\.[a-z0-9_.]+\\.v3\\.0\\.0$"


class ContractError(ValueError):
    """Raised when an M28 interchange invariant is violated."""


class SafetyError(ValueError):
    """Raised when a path leaves the declared repository boundary."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
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
        raise ContractError(f"required source missing: {relative}")
    return target


def read_json(root: Path, relative: str) -> Any:
    try:
        return json.loads(require_file(root, relative).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON source: {relative}: {exc}") from exc


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


def raw_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_digest(value: Any) -> str:
    return raw_digest(canonical_json_bytes(value))


def add_digest(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = dict(value)
    result[field] = object_digest(result)
    return result


def verify_digest(value: Mapping[str, Any], field: str, label: str) -> None:
    payload = dict(value)
    observed = payload.pop(field, None)
    if observed != object_digest(payload):
        raise ContractError(f"{label} digest mismatch")


def validate_source_commit(value: str) -> str:
    if value != EXPECTED_M27_COMMIT:
        raise ContractError(f"unexpected M27 source commit: {value}")
    return value


def _schema(
    schema_id: str,
    title: str,
    kind: str,
    required_extra: Sequence[str],
    properties_extra: Mapping[str, Any],
) -> dict[str, Any]:
    properties = {
        "schema": {"const": schema_id},
        "kind": {"const": kind},
        "version": {"const": VERSION},
        "milestone": {"const": MILESTONE},
        "source_commit": {"const": EXPECTED_M27_COMMIT},
        "status": {"const": "PASS"},
    }
    properties.update(properties_extra)
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:frp:schema:{schema_id}",
        "title": title,
        "type": "object",
        "required": [
            "schema",
            "kind",
            "version",
            "milestone",
            "source_commit",
            "status",
            *required_extra,
        ],
        "properties": properties,
        "additionalProperties": False,
    }


def schema_documents() -> dict[str, dict[str, Any]]:
    digest_property = {"type": "string", "pattern": HEX64_PATTERN}
    nonempty_array = {"type": "array", "minItems": 1}
    return {
        CONTRACT_SCHEMA: _schema(
            CONTRACT_SCHEMA_ID,
            "FRP M28 Trace Observatory upstream contract",
            "trace_observatory_upstream_contract",
            (
                "upstream_release",
                "consumer_scaffold_baseline",
                "integration_direction",
                "immutable_core",
                "data_contract",
                "export_scope",
                "contract_digest",
            ),
            {
                "upstream_release": {"const": "FRP v3.0.0 / M28"},
                "consumer_scaffold_baseline": {"type": "object"},
                "integration_direction": {"type": "object"},
                "immutable_core": {"type": "object"},
                "data_contract": {"type": "object"},
                "export_scope": {"type": "object"},
                "contract_digest": digest_property,
            },
        ),
        TRACE_SCHEMA: _schema(
            TRACE_SCHEMA_ID,
            "FRP M28 Observatory canonical trace bundle",
            "trace_observatory_canonical_trace_bundle",
            (
                "bundle_id",
                "ordering_rule",
                "canonical_ternary_domain",
                "scheduler_modes",
                "dataset_count",
                "record_count",
                "datasets",
                "bundle_digest",
            ),
            {
                "bundle_id": {"const": "frp-m28-observatory-canonical-trace-bundle"},
                "ordering_rule": {"const": "source_dataset_order_then_source_record_order"},
                "canonical_ternary_domain": {
                    "const": [-1, 0, 1]
                },
                "scheduler_modes": {"const": ["free", "7/1", "1/7"]},
                "dataset_count": {"const": 3},
                "record_count": {"const": 196},
                "datasets": {**nonempty_array, "minItems": 3, "maxItems": 3},
                "bundle_digest": digest_property,
            },
        ),
        FIXTURE_SCHEMA: _schema(
            FIXTURE_SCHEMA_ID,
            "FRP M28 Observatory fixture manifest",
            "trace_observatory_fixture_manifest",
            (
                "manifest_id",
                "digest_contract",
                "copy_requirement",
                "fixture_count",
                "fixtures",
                "fixture_set_digest",
                "manifest_digest",
            ),
            {
                "manifest_id": {"const": "frp-m28-observatory-fixture-manifest"},
                "digest_contract": {"type": "object"},
                "copy_requirement": {"const": "unchanged_upstream_bytes"},
                "fixture_count": {"const": len(SOURCE_FIXTURE_SPECS)},
                "fixtures": {
                    **nonempty_array,
                    "minItems": len(SOURCE_FIXTURE_SPECS),
                    "maxItems": len(SOURCE_FIXTURE_SPECS),
                },
                "fixture_set_digest": digest_property,
                "manifest_digest": digest_property,
            },
        ),
        REGISTRY_SCHEMA: _schema(
            REGISTRY_SCHEMA_ID,
            "FRP M28 Observatory compatibility registry",
            "trace_observatory_compatibility_registry",
            (
                "registry_revision",
                "consumer_repository",
                "consumer_registry_path",
                "consumer_registration_state",
                "record_count",
                "records",
                "registry_digest",
            ),
            {
                "registry_revision": {"const": "m28-v3.0.0"},
                "consumer_repository": {"const": OBSERVATORY_REPOSITORY},
                "consumer_registry_path": {"const": OBSERVATORY_REGISTRY_PATH},
                "consumer_registration_state": {
                    "const": "upstream_published_downstream_registration_required"
                },
                "record_count": {"const": 5},
                "records": {**nonempty_array, "minItems": 5, "maxItems": 5},
                "registry_digest": digest_property,
            },
        ),
        QUALIFICATION_SCHEMA: _schema(
            QUALIFICATION_SCHEMA_ID,
            "FRP M28 Trace Observatory interchange qualification",
            "trace_observatory_interchange_qualification",
            (
                "qualification_id",
                "check_count",
                "passed_count",
                "failed_count",
                "checks",
                "artifact_count",
                "artifacts",
                "schema_count",
                "schemas",
                "qualification_digest",
            ),
            {
                "qualification_id": {
                    "const": "frp-m28-trace-observatory-interchange-qualification"
                },
                "check_count": {"type": "integer", "minimum": 20},
                "passed_count": {"type": "integer", "minimum": 20},
                "failed_count": {"const": 0},
                "checks": nonempty_array,
                "artifact_count": {"const": 4},
                "artifacts": {"type": "array", "minItems": 4, "maxItems": 4},
                "schema_count": {"const": 5},
                "schemas": {"type": "array", "minItems": 5, "maxItems": 5},
                "qualification_digest": digest_property,
            },
        ),
    }


def schema_registry_document() -> dict[str, Any]:
    return {
        "schema": "frp.m28.schema_registry.v3.0.0",
        "kind": "m28_schema_registry",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": "PASS",
        "records": [
            {
                "schema_identifier": identifier,
                "schema_path": path,
                "schema_urn": f"urn:frp:schema:{identifier}",
            }
            for identifier, path in SCHEMA_PATHS.items()
        ],
    }


def write_document(root: Path, relative: str, value: Any) -> None:
    target = path_for(root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(document_bytes(value))


def source_file_record(root: Path, relative: str) -> dict[str, Any]:
    raw = require_file(root, relative).read_bytes()
    return {
        "path": relative,
        "bytes": len(raw),
        "raw_sha256": raw_digest(raw),
    }


def build_contract(source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    value = {
        "schema": CONTRACT_SCHEMA_ID,
        "kind": "trace_observatory_upstream_contract",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "status": "PASS",
        "upstream_release": "FRP v3.0.0 / M28",
        "consumer_scaffold_baseline": {
            "repository": OBSERVATORY_REPOSITORY,
            "audited_commit": OBSERVATORY_AUDITED_COMMIT,
            "implemented_layers": [
                {"mode": "artifact_auditor", "path": "artifact_auditor/"},
                {"mode": "trace_explorer", "path": "trace_explorer/"},
                {
                    "mode": "ternary_transition_visualizer",
                    "path": "transition_visualizer/",
                },
            ],
            "compatibility_registry_path": OBSERVATORY_REGISTRY_PATH,
            "integration_contract_path": OBSERVATORY_INTEGRATION_CONTRACT,
            "ci_workflow_path": OBSERVATORY_CI_WORKFLOW,
            "verified_test_count": OBSERVATORY_TEST_COUNT,
            "implementation_action": "extend_existing_scaffold",
        },
        "integration_direction": {
            "producer": "Fractal-Resonance-Processor",
            "transport": "published_versioned_artifacts",
            "consumer": OBSERVATORY_REPOSITORY,
            "direction": "upstream_to_downstream_only",
            "upstream_semantic_authority": True,
            "downstream_writeback": "forbidden",
            "downstream_source_mutation": "forbidden",
        },
        "immutable_core": {
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "opposite_transition_routes": [[-1, 0, 1], [1, 0, -1]],
            "service_scheduler_mode": "free",
            "temporal_scheduler_modes": ["1/7", "7/1"],
        },
        "data_contract": {
            "container_format": "json",
            "text_encoding": "utf-8",
            "digest_algorithm": "sha256",
            "digest_scope": "raw_source_bytes",
            "ordering": "preserve_source_order",
            "schema_resolution": "exact_identifier_and_kind",
            "schema_aliases": "forbidden",
            "automatic_schema_migration": "forbidden",
            "missing_field_policy": "remain_absent",
            "absent_is_zero": False,
            "source_execution": "forbidden",
            "producer_command_execution_by_consumer": "forbidden",
        },
        "export_scope": {
            "source_fixture_count": len(SOURCE_FIXTURE_SPECS),
            "trace_dataset_count": 3,
            "published_observatory_modes": list(OBSERVATORY_MODES),
            "measurement_contours_remain_separate": True,
            "ui_dependencies_in_upstream": False,
            "downstream_repository_files_modified": False,
        },
    }
    return add_digest(value, "contract_digest")


def _source_dataset(
    root: Path,
    dataset_id: str,
    source_path: str,
    source_identifier: str,
    source_kind: str,
    contour: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    source = source_file_record(root, source_path)
    copied_records = json.loads(json.dumps(records))
    return {
        "dataset_id": dataset_id,
        "measurement_contour": contour,
        "source_artifact": source,
        "source_identifier": source_identifier,
        "source_kind": source_kind,
        "record_order": "unchanged_source_order",
        "record_count": len(copied_records),
        "records": copied_records,
        "records_digest": object_digest(copied_records),
        "observatory_modes": list(OBSERVATORY_MODES),
    }


def build_trace_bundle(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    rtl = read_json(root, M19_RTL_TRACE)
    fpga = read_json(root, M19_FPGA_TRACE)
    long_run = read_json(root, M27_CHECKPOINTS)
    checkpoints = [
        checkpoint
        for profile in long_run["profiles"]
        for checkpoint in profile["checkpoints"]
    ]
    datasets = [
        _source_dataset(
            root,
            "m16-rtl-execution",
            M19_RTL_TRACE,
            "frp.m16.rtl_execution_trace.v2.1.0",
            "m16_rtl_execution_trace",
            "m16_rtl_execution",
            rtl["records"],
        ),
        _source_dataset(
            root,
            "m16-fpga-preparation-execution",
            M19_FPGA_TRACE,
            "frp.m16.fpga_preparation_execution_trace.v2.1.0",
            "m16_fpga_preparation_execution_trace",
            "m16_fpga_preparation_execution",
            fpga["records"],
        ),
        _source_dataset(
            root,
            "m27-long-run-checkpoints",
            M27_CHECKPOINTS,
            "m27-long-run-checkpoint-evidence-v2.9.0",
            "long_run_checkpoint_evidence",
            "m27_long_run_checkpoint_qualification",
            checkpoints,
        ),
    ]
    value = {
        "schema": TRACE_SCHEMA_ID,
        "kind": "trace_observatory_canonical_trace_bundle",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "status": "PASS",
        "bundle_id": "frp-m28-observatory-canonical-trace-bundle",
        "ordering_rule": "source_dataset_order_then_source_record_order",
        "canonical_ternary_domain": [-1, 0, 1],
        "scheduler_modes": ["free", "7/1", "1/7"],
        "dataset_count": len(datasets),
        "record_count": sum(dataset["record_count"] for dataset in datasets),
        "datasets": datasets,
    }
    return add_digest(value, "bundle_digest")


def build_fixture_manifest(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    fixtures = []
    for spec in SOURCE_FIXTURE_SPECS:
        artifact_record = source_file_record(root, spec["artifact_path"])
        schema_record = source_file_record(root, spec["schema_path"])
        fixtures.append(
            {
                "fixture_id": spec["fixture_id"],
                "artifact_path": spec["artifact_path"],
                "schema_path": spec["schema_path"],
                "source_identifier": spec["source_identifier"],
                "source_kind": spec["source_kind"],
                "measurement_contour": spec["measurement_contour"],
                "observatory_modes": list(spec["observatory_modes"]),
                "artifact_bytes": artifact_record["bytes"],
                "artifact_raw_sha256": artifact_record["raw_sha256"],
                "schema_bytes": schema_record["bytes"],
                "schema_raw_sha256": schema_record["raw_sha256"],
                "copy_requirement": "unchanged_upstream_bytes",
            }
        )
    value = {
        "schema": FIXTURE_SCHEMA_ID,
        "kind": "trace_observatory_fixture_manifest",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "status": "PASS",
        "manifest_id": "frp-m28-observatory-fixture-manifest",
        "digest_contract": {
            "algorithm": "sha256",
            "scope": "raw_source_bytes",
            "pre_parse": True,
        },
        "copy_requirement": "unchanged_upstream_bytes",
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "fixture_set_digest": object_digest(fixtures),
    }
    return add_digest(value, "manifest_digest")


def _compatibility_record(
    identifier: str,
    kind: str,
    contour: str,
    producer_path: str,
    schema_path: str,
    modes: Sequence[str],
) -> dict[str, Any]:
    return {
        "identifier": identifier,
        "identifier_field": "schema",
        "schema_version": VERSION,
        "artifact_format": "json",
        "artifact_kind": kind,
        "measurement_contour": contour,
        "producer_path": "frp_m28_trace_observatory_upstream_interchange.py",
        "producer_version": VERSION,
        "evidence_kind": "committed_artifact",
        "evidence_path": producer_path,
        "schema_path": schema_path,
        "canonical_fixture_source_path": producer_path,
        "observatory_modes": list(modes),
        "upstream_release": "FRP v3.0.0 / M28",
        "downstream_registration_state": "registration_required",
    }


def build_compatibility_registry(source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    records = [
        _compatibility_record(
            CONTRACT_SCHEMA_ID,
            "trace_observatory_upstream_contract",
            "m28_upstream_integration_contract",
            CONTRACT_ARTIFACT,
            CONTRACT_SCHEMA,
            ("artifact_auditor",),
        ),
        _compatibility_record(
            TRACE_SCHEMA_ID,
            "trace_observatory_canonical_trace_bundle",
            "m16_m27_observatory_trace_interchange",
            TRACE_ARTIFACT,
            TRACE_SCHEMA,
            OBSERVATORY_MODES,
        ),
        _compatibility_record(
            FIXTURE_SCHEMA_ID,
            "trace_observatory_fixture_manifest",
            "m28_upstream_fixture_inventory",
            FIXTURE_ARTIFACT,
            FIXTURE_SCHEMA,
            ("artifact_auditor",),
        ),
        _compatibility_record(
            REGISTRY_SCHEMA_ID,
            "trace_observatory_compatibility_registry",
            "m28_upstream_compatibility_registry",
            REGISTRY_ARTIFACT,
            REGISTRY_SCHEMA,
            ("artifact_auditor",),
        ),
        _compatibility_record(
            QUALIFICATION_SCHEMA_ID,
            "trace_observatory_interchange_qualification",
            "m28_upstream_interchange_qualification",
            QUALIFICATION_ARTIFACT,
            QUALIFICATION_SCHEMA,
            ("artifact_auditor",),
        ),
    ]
    value = {
        "schema": REGISTRY_SCHEMA_ID,
        "kind": "trace_observatory_compatibility_registry",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "status": "PASS",
        "registry_revision": "m28-v3.0.0",
        "consumer_repository": OBSERVATORY_REPOSITORY,
        "consumer_registry_path": OBSERVATORY_REGISTRY_PATH,
        "consumer_registration_state": (
            "upstream_published_downstream_registration_required"
        ),
        "record_count": len(records),
        "records": records,
    }
    return add_digest(value, "registry_digest")


def _pass(check_id: str, category: str, evidence: Any) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "category": category,
        "status": "PASS",
        "evidence": evidence,
    }


def validate_contract(value: Mapping[str, Any], source_commit: str) -> None:
    validate_source_commit(source_commit)
    if value.get("source_commit") != source_commit:
        raise ContractError("M28 contract source commit mismatch")
    verify_digest(value, "contract_digest", "M28 upstream contract")
    core = value.get("immutable_core", {})
    if core.get("balanced_ternary_notation") != "-1/0/1":
        raise ContractError("M28 balanced ternary notation mismatch")
    if core.get("semantic_values") != [-1, 0, 1]:
        raise ContractError("M28 ternary domain mismatch")
    if core.get("active_neutral_state") != 0:
        raise ContractError("M28 active neutral state mismatch")
    if core.get("temporal_scheduler_modes") != ["1/7", "7/1"]:
        raise ContractError("M28 temporal scheduler modes mismatch")
    baseline = value.get("consumer_scaffold_baseline", {})
    if baseline.get("repository") != OBSERVATORY_REPOSITORY:
        raise ContractError("M28 Observatory repository mismatch")
    if baseline.get("audited_commit") != OBSERVATORY_AUDITED_COMMIT:
        raise ContractError("M28 Observatory audited commit mismatch")
    modes = [item.get("mode") for item in baseline.get("implemented_layers", [])]
    if set(modes) != set(OBSERVATORY_MODES):
        raise ContractError("M28 Observatory mode boundary mismatch")
    direction = value.get("integration_direction", {})
    if direction.get("direction") != "upstream_to_downstream_only":
        raise ContractError("M28 integration direction mismatch")
    if direction.get("downstream_writeback") != "forbidden":
        raise ContractError("M28 downstream writeback boundary mismatch")


def _validate_m16_records(records: Sequence[Mapping[str, Any]], label: str) -> None:
    previous_sequence = -1
    for record in records:
        sequence = record.get("sequence")
        if not isinstance(sequence, int) or sequence <= previous_sequence:
            raise ContractError(f"{label} source ordering mismatch")
        previous_sequence = sequence
        for field in ("retained_state_before", "retained_state_after"):
            states = record.get(field)
            if not isinstance(states, list) or any(
                state not in (-1, 0, 1) for state in states
            ):
                raise ContractError(f"{label} ternary state mismatch")
        events = record.get("events", {})
        if any(
            events.get(name) != 0
            for name in (
                "actual_direct_events",
                "reserved_state_events",
                "queue_overflow_events",
            )
        ):
            raise ContractError(f"{label} zero-event invariant mismatch")
        if record.get("invariants", {}).get("all_pass") is not True:
            raise ContractError(f"{label} invariant-vector mismatch")


def _validate_m27_checkpoints(records: Sequence[Mapping[str, Any]]) -> None:
    profile_order = [
        "free-long-run",
        "seven-one-long-run",
        "one-seven-long-run",
    ]
    grouped: dict[str, list[int]] = {profile: [] for profile in profile_order}
    for record in records:
        profile = record.get("profile_id")
        if profile not in grouped:
            raise ContractError("M28 M27 checkpoint profile mismatch")
        grouped[profile].append(record.get("tick"))
        states = record.get("states")
        if not isinstance(states, list) or any(
            state not in (-1, 0, 1) for state in states
        ):
            raise ContractError("M28 M27 checkpoint ternary state mismatch")
        if any(
            record.get(name) != 0
            for name in (
                "actual_direct_events",
                "reserved_state_events",
                "queue_overflow_events",
            )
        ):
            raise ContractError("M28 M27 checkpoint zero-event mismatch")
        if record.get("transition_pressure_q16") != (
            record.get("thermal_state_proxy_q16", 0)
            + record.get("switching_load_q16", 0)
        ):
            raise ContractError("M28 M27 telemetry relation mismatch")
        if record.get("stability_margin_q16") != (
            record.get("coherence_capacity_q16", 0)
            - record.get("transition_pressure_q16", 0)
        ):
            raise ContractError("M28 M27 stability relation mismatch")
    if any(len(ticks) != 32 for ticks in grouped.values()):
        raise ContractError("M28 M27 checkpoint count mismatch")
    if any(ticks != sorted(ticks) or len(set(ticks)) != len(ticks) for ticks in grouped.values()):
        raise ContractError("M28 M27 checkpoint order mismatch")


def validate_trace_bundle(
    value: Mapping[str, Any],
    root: Path,
    source_commit: str,
) -> None:
    validate_source_commit(source_commit)
    if value.get("source_commit") != source_commit:
        raise ContractError("M28 trace bundle source commit mismatch")
    verify_digest(value, "bundle_digest", "M28 trace bundle")
    if value.get("canonical_ternary_domain") != [-1, 0, 1]:
        raise ContractError("M28 trace bundle ternary domain mismatch")
    if value.get("scheduler_modes") != ["free", "7/1", "1/7"]:
        raise ContractError("M28 trace bundle scheduler modes mismatch")
    datasets = value.get("datasets")
    if not isinstance(datasets, list) or len(datasets) != 3:
        raise ContractError("M28 trace dataset inventory mismatch")
    expected_ids = [
        "m16-rtl-execution",
        "m16-fpga-preparation-execution",
        "m27-long-run-checkpoints",
    ]
    if [dataset.get("dataset_id") for dataset in datasets] != expected_ids:
        raise ContractError("M28 trace dataset order mismatch")
    if [dataset.get("record_count") for dataset in datasets] != [96, 4, 96]:
        raise ContractError("M28 trace dataset record count mismatch")
    if value.get("record_count") != 196:
        raise ContractError("M28 trace bundle total record count mismatch")
    for dataset in datasets:
        records = dataset.get("records")
        if not isinstance(records, list):
            raise ContractError("M28 trace dataset records missing")
        if dataset.get("record_count") != len(records):
            raise ContractError("M28 trace dataset count relation mismatch")
        if dataset.get("records_digest") != object_digest(records):
            raise ContractError("M28 trace dataset digest mismatch")
        source = dataset.get("source_artifact", {})
        observed = source_file_record(root, source.get("path", ""))
        if source != observed:
            raise ContractError("M28 trace source artifact mismatch")
        if dataset.get("observatory_modes") != list(OBSERVATORY_MODES):
            raise ContractError("M28 trace mode eligibility mismatch")
    rtl_source = read_json(root, M19_RTL_TRACE)["records"]
    fpga_source = read_json(root, M19_FPGA_TRACE)["records"]
    long_run = read_json(root, M27_CHECKPOINTS)
    checkpoint_source = [
        checkpoint
        for profile in long_run["profiles"]
        for checkpoint in profile["checkpoints"]
    ]
    if datasets[0]["records"] != rtl_source:
        raise ContractError("M28 RTL source bytes projection changed")
    if datasets[1]["records"] != fpga_source:
        raise ContractError("M28 FPGA source bytes projection changed")
    if datasets[2]["records"] != checkpoint_source:
        raise ContractError("M28 checkpoint source projection changed")
    _validate_m16_records(datasets[0]["records"], "M28 RTL dataset")
    _validate_m16_records(datasets[1]["records"], "M28 FPGA dataset")
    _validate_m27_checkpoints(datasets[2]["records"])


def validate_fixture_manifest(
    value: Mapping[str, Any],
    root: Path,
    source_commit: str,
) -> None:
    validate_source_commit(source_commit)
    if value.get("source_commit") != source_commit:
        raise ContractError("M28 fixture manifest source commit mismatch")
    verify_digest(value, "manifest_digest", "M28 fixture manifest")
    fixtures = value.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != len(SOURCE_FIXTURE_SPECS):
        raise ContractError("M28 fixture inventory mismatch")
    if value.get("fixture_set_digest") != object_digest(fixtures):
        raise ContractError("M28 fixture set digest mismatch")
    for spec, fixture in zip(SOURCE_FIXTURE_SPECS, fixtures):
        if fixture.get("fixture_id") != spec["fixture_id"]:
            raise ContractError("M28 fixture order mismatch")
        artifact = source_file_record(root, spec["artifact_path"])
        schema = source_file_record(root, spec["schema_path"])
        if fixture.get("artifact_bytes") != artifact["bytes"]:
            raise ContractError("M28 fixture artifact byte count mismatch")
        if fixture.get("artifact_raw_sha256") != artifact["raw_sha256"]:
            raise ContractError("M28 fixture artifact digest mismatch")
        if fixture.get("schema_bytes") != schema["bytes"]:
            raise ContractError("M28 fixture schema byte count mismatch")
        if fixture.get("schema_raw_sha256") != schema["raw_sha256"]:
            raise ContractError("M28 fixture schema digest mismatch")
        if fixture.get("copy_requirement") != "unchanged_upstream_bytes":
            raise ContractError("M28 fixture copy boundary mismatch")


def validate_compatibility_registry(
    value: Mapping[str, Any], source_commit: str
) -> None:
    validate_source_commit(source_commit)
    if value.get("source_commit") != source_commit:
        raise ContractError("M28 compatibility registry source commit mismatch")
    verify_digest(value, "registry_digest", "M28 compatibility registry")
    records = value.get("records")
    if not isinstance(records, list) or len(records) != 5:
        raise ContractError("M28 compatibility record count mismatch")
    identifiers = [record.get("identifier") for record in records]
    if identifiers != list(SCHEMA_PATHS):
        raise ContractError("M28 compatibility identifier order mismatch")
    if len(set(identifiers)) != len(identifiers):
        raise ContractError("M28 compatibility identifiers are not unique")
    for record in records:
        identifier = record.get("identifier")
        if not isinstance(identifier, str) or not identifier.startswith("frp.m28."):
            raise ContractError("M28 compatibility identifier mismatch")
        if record.get("identifier_field") != "schema":
            raise ContractError("M28 compatibility identifier field mismatch")
        if record.get("schema_version") != VERSION:
            raise ContractError("M28 compatibility schema version mismatch")
        modes = record.get("observatory_modes")
        if not isinstance(modes, list) or not modes:
            raise ContractError("M28 compatibility modes missing")
        if any(mode not in OBSERVATORY_MODES for mode in modes):
            raise ContractError("M28 compatibility mode mismatch")
        if record.get("downstream_registration_state") != "registration_required":
            raise ContractError("M28 downstream registration state mismatch")
    if set(records[1]["observatory_modes"]) != set(OBSERVATORY_MODES):
        raise ContractError("M28 trace bundle does not cover all Observatory modes")


def build_checks(
    contract: Mapping[str, Any],
    trace: Mapping[str, Any],
    fixtures: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        _pass("m28-source-boundary", "source", EXPECTED_M27_COMMIT),
        _pass("m28-observatory-repository", "consumer", OBSERVATORY_REPOSITORY),
        _pass("m28-observatory-baseline", "consumer", OBSERVATORY_AUDITED_COMMIT),
        _pass("m28-observatory-ci", "consumer", OBSERVATORY_CI_WORKFLOW),
        _pass("m28-observatory-registry", "consumer", OBSERVATORY_REGISTRY_PATH),
        _pass("m28-observatory-tests", "consumer", OBSERVATORY_TEST_COUNT),
        _pass("m28-existing-scaffold", "boundary", "extend_existing_scaffold"),
        _pass("m28-one-way-integration", "boundary", "upstream_to_downstream_only"),
        _pass("m28-no-writeback", "boundary", "forbidden"),
        _pass("m28-no-source-mutation", "boundary", "forbidden"),
        _pass("m28-ternary-domain", "core", [-1, 0, 1]),
        _pass("m28-active-neutral", "core", 0),
        _pass("m28-temporal-schedulers", "core", ["1/7", "7/1"]),
        _pass("m28-mode-count", "consumer", len(OBSERVATORY_MODES)),
        _pass("m28-dataset-count", "trace", trace["dataset_count"]),
        _pass("m28-record-count", "trace", trace["record_count"]),
        _pass("m28-rtl-records", "trace", trace["datasets"][0]["record_count"]),
        _pass("m28-fpga-records", "trace", trace["datasets"][1]["record_count"]),
        _pass("m28-checkpoint-records", "trace", trace["datasets"][2]["record_count"]),
        _pass("m28-source-order", "trace", trace["ordering_rule"]),
        _pass("m28-fixture-count", "fixture", fixtures["fixture_count"]),
        _pass("m28-raw-byte-digests", "fixture", fixtures["digest_contract"]),
        _pass("m28-unchanged-copy", "fixture", fixtures["copy_requirement"]),
        _pass("m28-registry-record-count", "registry", registry["record_count"]),
        _pass("m28-exact-schema-resolution", "registry", "schema_and_kind"),
        _pass("m28-consumer-registration", "registry", registry["consumer_registration_state"]),
        _pass("m28-contract-digest", "digest", contract["contract_digest"]),
        _pass("m28-trace-digest", "digest", trace["bundle_digest"]),
        _pass("m28-fixture-digest", "digest", fixtures["manifest_digest"]),
        _pass("m28-registry-digest", "digest", registry["registry_digest"]),
    ]


def build_qualification(
    output_root: Path,
    source_commit: str,
    checks: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    validate_source_commit(source_commit)
    artifact_records = [
        source_file_record(output_root, path) for path in PRIMARY_ARTIFACT_PATHS
    ]
    schema_records = [
        source_file_record(output_root, path) for path in SCHEMA_PATHS.values()
    ]
    value = {
        "schema": QUALIFICATION_SCHEMA_ID,
        "kind": "trace_observatory_interchange_qualification",
        "version": VERSION,
        "milestone": MILESTONE,
        "source_commit": source_commit,
        "status": "PASS",
        "qualification_id": "frp-m28-trace-observatory-interchange-qualification",
        "check_count": len(checks),
        "passed_count": sum(check["status"] == "PASS" for check in checks),
        "failed_count": sum(check["status"] != "PASS" for check in checks),
        "checks": list(checks),
        "artifact_count": len(artifact_records),
        "artifacts": artifact_records,
        "schema_count": len(schema_records),
        "schemas": schema_records,
    }
    return add_digest(value, "qualification_digest")


def validate_schema_registry(value: Mapping[str, Any]) -> None:
    if value.get("schema") != "frp.m28.schema_registry.v3.0.0":
        raise ContractError("M28 schema registry identifier mismatch")
    if value.get("version") != VERSION or value.get("milestone") != MILESTONE:
        raise ContractError("M28 schema registry boundary mismatch")
    records = value.get("records")
    if not isinstance(records, list) or len(records) != len(SCHEMA_PATHS):
        raise ContractError("M28 schema registry inventory mismatch")
    for (identifier, path), record in zip(SCHEMA_PATHS.items(), records):
        if record.get("schema_identifier") != identifier:
            raise ContractError("M28 schema registry order mismatch")
        if record.get("schema_path") != path:
            raise ContractError("M28 schema registry path mismatch")


def schema_context(root: Path) -> dict[str, Draft202012Validator]:
    validators = {}
    for identifier, relative in SCHEMA_PATHS.items():
        schema = read_json(root, relative)
        Draft202012Validator.check_schema(schema)
        if schema.get("$id") != f"urn:frp:schema:{identifier}":
            raise ContractError(f"M28 schema identifier mismatch: {relative}")
        validators[relative] = Draft202012Validator(schema)
    return validators


def validate_instance(
    validator: Draft202012Validator,
    instance: Any,
    label: str,
) -> None:
    errors = sorted(
        validator.iter_errors(instance), key=lambda item: list(item.absolute_path)
    )
    if errors:
        detail = "; ".join(error.message for error in errors[:5])
        raise ContractError(f"schema validation failed for {label}: {detail}")


def validate_qualification(
    value: Mapping[str, Any],
    root: Path,
    source_commit: str,
) -> None:
    validate_source_commit(source_commit)
    if value.get("source_commit") != source_commit:
        raise ContractError("M28 qualification source commit mismatch")
    verify_digest(value, "qualification_digest", "M28 qualification")
    checks = value.get("checks")
    if not isinstance(checks, list) or len(checks) < 20:
        raise ContractError("M28 qualification checks incomplete")
    if value.get("check_count") != len(checks):
        raise ContractError("M28 qualification check count mismatch")
    if value.get("passed_count") != len(checks) or value.get("failed_count") != 0:
        raise ContractError("M28 qualification status mismatch")
    if any(check.get("status") != "PASS" for check in checks):
        raise ContractError("M28 qualification contains a failed check")
    expected_artifacts = [
        source_file_record(root, path) for path in PRIMARY_ARTIFACT_PATHS
    ]
    expected_schemas = [
        source_file_record(root, path) for path in SCHEMA_PATHS.values()
    ]
    if value.get("artifacts") != expected_artifacts:
        raise ContractError("M28 qualification artifact inventory mismatch")
    if value.get("schemas") != expected_schemas:
        raise ContractError("M28 qualification schema inventory mismatch")


def generate(
    repository_root: Path,
    output_root: Path,
    source_commit: str,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    validate_source_commit(source_commit)

    schemas = schema_documents()
    for relative, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        write_document(output_root, relative, schema)
    write_document(output_root, SCHEMA_REGISTRY, schema_registry_document())

    contract = build_contract(source_commit)
    trace = build_trace_bundle(repository_root, source_commit)
    fixtures = build_fixture_manifest(repository_root, source_commit)
    registry = build_compatibility_registry(source_commit)

    validate_contract(contract, source_commit)
    validate_trace_bundle(trace, repository_root, source_commit)
    validate_fixture_manifest(fixtures, repository_root, source_commit)
    validate_compatibility_registry(registry, source_commit)

    write_document(output_root, CONTRACT_ARTIFACT, contract)
    write_document(output_root, TRACE_ARTIFACT, trace)
    write_document(output_root, FIXTURE_ARTIFACT, fixtures)
    write_document(output_root, REGISTRY_ARTIFACT, registry)

    checks = build_checks(contract, trace, fixtures, registry)
    qualification = build_qualification(output_root, source_commit, checks)
    write_document(output_root, QUALIFICATION_ARTIFACT, qualification)

    verify(output_root, source_commit, source_root=repository_root)
    return {
        "milestone": MILESTONE,
        "version": VERSION,
        "status": "PASS",
        "generated_file_count": len(GENERATED_PATHS),
        "trace_record_count": trace["record_count"],
        "fixture_count": fixtures["fixture_count"],
        "compatibility_record_count": registry["record_count"],
        "qualification_check_count": qualification["check_count"],
        "qualification_digest": qualification["qualification_digest"],
    }


def verify(
    root: Path,
    source_commit: str,
    *,
    source_root: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    source_root = root if source_root is None else source_root.resolve()
    validate_source_commit(source_commit)
    validators = schema_context(root)
    registry_document = read_json(root, SCHEMA_REGISTRY)
    validate_schema_registry(registry_document)

    contract = read_json(root, CONTRACT_ARTIFACT)
    trace = read_json(root, TRACE_ARTIFACT)
    fixtures = read_json(root, FIXTURE_ARTIFACT)
    registry = read_json(root, REGISTRY_ARTIFACT)
    qualification = read_json(root, QUALIFICATION_ARTIFACT)

    validate_instance(validators[CONTRACT_SCHEMA], contract, CONTRACT_ARTIFACT)
    validate_instance(validators[TRACE_SCHEMA], trace, TRACE_ARTIFACT)
    validate_instance(validators[FIXTURE_SCHEMA], fixtures, FIXTURE_ARTIFACT)
    validate_instance(validators[REGISTRY_SCHEMA], registry, REGISTRY_ARTIFACT)
    validate_instance(
        validators[QUALIFICATION_SCHEMA], qualification, QUALIFICATION_ARTIFACT
    )

    validate_contract(contract, source_commit)
    validate_trace_bundle(trace, source_root, source_commit)
    validate_fixture_manifest(fixtures, source_root, source_commit)
    validate_compatibility_registry(registry, source_commit)
    validate_qualification(qualification, root, source_commit)

    return {
        "milestone": MILESTONE,
        "version": VERSION,
        "status": "PASS",
        "schema_count": len(validators),
        "artifact_count": len(ARTIFACT_PATHS),
        "trace_record_count": trace["record_count"],
        "qualification_check_count": qualification["check_count"],
        "qualification_digest": qualification["qualification_digest"],
    }


def self_test(repository_root: Path, source_commit: str) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    validate_source_commit(source_commit)
    checks: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="frp-m28-self-test-") as temporary:
        output_root = Path(temporary)
        first = generate(repository_root, output_root, source_commit)
        checks.append(_pass("self-generate", "self_test", first["status"]))
        verified = verify(output_root, source_commit, source_root=repository_root)
        checks.append(_pass("self-verify", "self_test", verified["status"]))

        trace = read_json(output_root, TRACE_ARTIFACT)
        tampered_trace = json.loads(json.dumps(trace))
        tampered_trace["canonical_ternary_domain"] = [-1, 0, 2]
        try:
            validate_trace_bundle(tampered_trace, repository_root, source_commit)
        except ContractError:
            checks.append(_pass("self-reject-ternary-tamper", "negative", True))
        else:
            raise ContractError("M28 self-test accepted ternary tampering")

        tampered_trace = json.loads(json.dumps(trace))
        tampered_trace["datasets"][0]["records"][0]["events"][
            "actual_direct_events"
        ] = 1
        tampered_trace["datasets"][0]["records_digest"] = object_digest(
            tampered_trace["datasets"][0]["records"]
        )
        tampered_trace_without_digest = dict(tampered_trace)
        tampered_trace_without_digest.pop("bundle_digest")
        tampered_trace["bundle_digest"] = object_digest(tampered_trace_without_digest)
        try:
            validate_trace_bundle(tampered_trace, repository_root, source_commit)
        except ContractError:
            checks.append(_pass("self-reject-event-tamper", "negative", True))
        else:
            raise ContractError("M28 self-test accepted event tampering")

        fixtures = read_json(output_root, FIXTURE_ARTIFACT)
        tampered_fixtures = json.loads(json.dumps(fixtures))
        tampered_fixtures["fixtures"][0]["artifact_raw_sha256"] = "0" * 64
        try:
            validate_fixture_manifest(
                tampered_fixtures, repository_root, source_commit
            )
        except ContractError:
            checks.append(_pass("self-reject-fixture-tamper", "negative", True))
        else:
            raise ContractError("M28 self-test accepted fixture tampering")

        registry = read_json(output_root, REGISTRY_ARTIFACT)
        tampered_registry = json.loads(json.dumps(registry))
        tampered_registry["records"][1]["observatory_modes"] = [
            "artifact_auditor"
        ]
        tampered_registry_without_digest = dict(tampered_registry)
        tampered_registry_without_digest.pop("registry_digest")
        tampered_registry["registry_digest"] = object_digest(
            tampered_registry_without_digest
        )
        try:
            validate_compatibility_registry(tampered_registry, source_commit)
        except ContractError:
            checks.append(_pass("self-reject-mode-loss", "negative", True))
        else:
            raise ContractError("M28 self-test accepted Observatory mode loss")

    return {
        "milestone": MILESTONE,
        "version": VERSION,
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
    }


def write_result(path: str | None, value: Mapping[str, Any]) -> None:
    raw = document_bytes(value)
    if path is None:
        sys.stdout.buffer.write(raw)
        return
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=MILESTONE_TITLE)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true")
    action.add_argument("--verify", action="store_true")
    action.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--source-commit", default=EXPECTED_M27_COMMIT)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repository_root = Path(args.repository_root)
    output_root = Path(args.output_root)
    if args.generate:
        result = generate(repository_root, output_root, args.source_commit)
    elif args.verify:
        result = verify(repository_root, args.source_commit)
    else:
        result = self_test(repository_root, args.source_commit)
    write_result(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
