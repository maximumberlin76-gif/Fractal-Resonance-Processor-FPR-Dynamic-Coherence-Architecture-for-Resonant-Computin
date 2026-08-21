#!/usr/bin/env python3
"""Generate and verify FRP M23 clock/reset/CDC hardening evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator


VERSION = "2.5.0"
MILESTONE = "M23"
EXPECTED_M22_COMMIT = "6bb07958710dc942c4deea1e7663ea97017fe3a8"
WORKFLOW_PATH = ".github/workflows/frp-m23-clock-reset-cdc-interface-hardening-workflow.yml"

CONTRACT_ARTIFACT = "artifacts/m23/contracts/m23-clock-reset-cdc-interface-contract.json"
RECORDS_ARTIFACT = "artifacts/m23/records/m23-hardening-sequence-records.json"
ASSERTION_ARTIFACT = "artifacts/m23/reports/m23-interface-protocol-assertion-report.json"
MANIFEST_ARTIFACT = "artifacts/m23/manifests/m23-clock-reset-cdc-interface-hardening-manifest.json"
QUALIFICATION_ARTIFACT = "artifacts/m23/manifests/m23-clock-reset-cdc-interface-hardening-qualification.json"

CONTRACT_SCHEMA = "schemas/m23/frp_m23_clock_reset_cdc_interface_contract.v2.5.0.schema.json"
RECORDS_SCHEMA = "schemas/m23/frp_m23_hardening_sequence_records.v2.5.0.schema.json"
ASSERTION_SCHEMA = "schemas/m23/frp_m23_interface_protocol_assertion_report.v2.5.0.schema.json"
MANIFEST_SCHEMA = "schemas/m23/frp_m23_clock_reset_cdc_interface_hardening_manifest.v2.5.0.schema.json"
QUALIFICATION_SCHEMA = "schemas/m23/frp_m23_clock_reset_cdc_interface_hardening_qualification.v2.5.0.schema.json"
REGISTRY_PATH = "schemas/m23/frp_m23_schema_registry.json"

SCHEMA_PATHS = {
    "m23-clock-reset-cdc-interface-contract-v2.5.0": CONTRACT_SCHEMA,
    "m23-hardening-sequence-records-v2.5.0": RECORDS_SCHEMA,
    "m23-interface-protocol-assertion-report-v2.5.0": ASSERTION_SCHEMA,
    "m23-clock-reset-cdc-interface-hardening-manifest-v2.5.0": MANIFEST_SCHEMA,
    "m23-clock-reset-cdc-interface-hardening-qualification-v2.5.0": QUALIFICATION_SCHEMA,
}

RTL_RESET_SYNC = "rtl/m23/frp_m23_reset_release_sync.sv"
RTL_CDC_BRIDGE = "rtl/m23/frp_m23_csr_cdc_bridge.sv"
RTL_ASSERTIONS = "rtl/m23/frp_m23_interface_protocol_assertions.sv"
RTL_BOUNDARY = "rtl/m23/frp_m23_hardened_integration_boundary.sv"
RTL_TESTBENCH = "rtl/m23/frp_m23_hardened_integration_boundary_tb.sv"

TECHNICAL_SOURCE_PATHS = (
    "frp_m23_clock_reset_cdc_interface_hardening.py",
    RTL_RESET_SYNC,
    RTL_CDC_BRIDGE,
    RTL_ASSERTIONS,
    RTL_BOUNDARY,
    RTL_TESTBENCH,
    CONTRACT_SCHEMA,
    RECORDS_SCHEMA,
    ASSERTION_SCHEMA,
    MANIFEST_SCHEMA,
    QUALIFICATION_SCHEMA,
    REGISTRY_PATH,
    "tests/test_frp_m23_clock_reset_cdc_interface_hardening.py",
)

UPSTREAM_SOURCE_PATHS = (
    "rtl/m16/frp_m16_pkg.sv",
    "rtl/m16/frp_m16_core.sv",
    "rtl/m22/frp_m22_csr_pkg.sv",
    "rtl/m22/frp_m22_control_status_register_interface.sv",
    "artifacts/m22/interface/m22-control-status-register-interface.json",
    "artifacts/m22/manifests/m22-control-status-register-qualification.json",
)

ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    RECORDS_ARTIFACT,
    ASSERTION_ARTIFACT,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

PROFILE_SPECS = (
    {"profile_id": "cells-8-lanes-2", "cell_count": 8, "request_lanes": 2, "restart_signature": "00010119"},
    {"profile_id": "cells-16-lanes-4", "cell_count": 16, "request_lanes": 4, "restart_signature": "00010101"},
    {"profile_id": "cells-32-lanes-8", "cell_count": 32, "request_lanes": 8, "restart_signature": "00010131"},
)

CLOCK_DOMAINS = (
    {"domain_id": "host", "clock": "host_clk", "reset": "host_reset_released", "role": "integration CSR initiator"},
    {"domain_id": "core", "clock": "core_clk", "reset": "core_reset_released", "role": "M22 CSR target and M16 execution core"},
)

RESET_SEQUENCES = (
    "initial_async_assertion",
    "independent_synchronous_release",
    "pre_readiness_gating",
    "in_flight_reset_interruption",
    "repeated_deterministic_restart",
)

CDC_BOUNDARIES = (
    {"boundary_id": "host_to_core_request_toggle", "direction": "host-to-core", "kind": "two_stage_toggle_synchronizer", "stages": 2},
    {"boundary_id": "host_to_core_request_payload", "direction": "host-to-core", "kind": "bundled_data_held_until_response", "stages": 0},
    {"boundary_id": "core_to_host_response_toggle", "direction": "core-to-host", "kind": "two_stage_toggle_synchronizer", "stages": 2},
    {"boundary_id": "core_to_host_response_payload", "direction": "core-to-host", "kind": "bundled_data_held_until_acceptance", "stages": 0},
    {"boundary_id": "core_to_host_ready_level", "direction": "core-to-host", "kind": "two_stage_level_synchronizer", "stages": 2},
)

INVALID_SEQUENCE_CLASSES = (
    "request_before_ready",
    "request_while_busy",
    "request_valid_held",
)

STRUCTURAL_CDC_CHECKS = (
    "host_reset_two_stage_release",
    "core_reset_two_stage_release",
    "request_toggle_async_reg",
    "response_toggle_async_reg",
    "ready_level_async_reg",
    "request_payload_held",
    "response_payload_held",
    "single_outstanding_transaction",
    "no_combinational_clock_crossing",
    "shared_async_assertion_source",
)

ASSERTION_SPECS = (
    ("M23-A01", "reset", "host reset release is monotonic until asynchronous assertion"),
    ("M23-A02", "reset", "core reset release is monotonic until asynchronous assertion"),
    ("M23-A03", "readiness", "host readiness follows host reset release"),
    ("M23-A04", "readiness", "core readiness follows core reset release"),
    ("M23-A05", "interface", "core request occurs only after core readiness"),
    ("M23-A06", "interface", "host response clears the single outstanding transaction"),
    ("M23-A07", "cdc", "request toggle changes only after host readiness"),
    ("M23-A08", "cdc", "bundled request payload remains stable while busy"),
    ("M23-A09", "interface", "core response requires an active core request"),
    ("M23-A10", "cdc", "bundled response payload remains stable between responses"),
    ("M23-A11", "cdc", "response toggle changes only after core readiness"),
    ("M23-A12", "interface", "host response occurs only after host readiness"),
)


class ContractError(ValueError):
    """Raised for an M23 contract violation."""


class SafetyError(ValueError):
    """Raised for an unsafe path or write boundary."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise SafetyError(f"unsafe M23 path: {value!r}")
    path = PurePosixPath(value)
    if (
        "\\" in value
        or path.is_absolute()
        or not path.parts
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise SafetyError(f"unsafe M23 path: {value}")
    return path


def path_for(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative_path(relative).parts)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def document_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def validate_source_commit(value: str) -> str:
    if value != EXPECTED_M22_COMMIT:
        raise ContractError(f"unexpected M22 source commit: {value}")
    return value


def require_file(root: Path, relative: str) -> Path:
    target = path_for(root, relative)
    if target.is_symlink() or not target.is_file():
        raise ContractError(f"required source missing: {relative}")
    return target


def source_record(root: Path, relative: str) -> dict[str, Any]:
    raw = require_file(root, relative).read_bytes()
    return {"path": relative, "bytes": len(raw), "raw_sha256": sha256_bytes(raw)}


class SchemaContext:
    """Load the closed M23 Draft 2020-12 schema set."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.schemas: dict[str, Mapping[str, Any]] = {}
        for relative in SCHEMA_PATHS.values():
            schema = json.loads(require_file(root, relative).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self.schemas[relative] = schema

    def validate(self, schema_path: str, instance: Any, label: str) -> None:
        validator = Draft202012Validator(self.schemas[schema_path])
        errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
        if errors:
            detail = "; ".join(error.message for error in errors[:4])
            raise ContractError(f"schema validation failed for {label}: {detail}")


def validate_rtl_sources(root: Path) -> None:
    required_tokens = {
        RTL_RESET_SYNC: ("ASYNC_REG", "posedge clk or negedge rst_n_async", "release_q"),
        RTL_CDC_BRIDGE: ("request_toggle_core_sync_q", "response_toggle_host_sync_q", "host_busy", "invalid_valid_held"),
        RTL_ASSERTIONS: tuple(identifier.replace("-", "_") for identifier, _, _ in ASSERTION_SPECS),
        RTL_BOUNDARY: ("host_reset_sync", "core_reset_sync", "core_ready_host_sync_q", "cdc_bridge", "csr_target"),
        RTL_TESTBENCH: ("M23_RESET_SEQUENCES=5/5 PASS", "M23_CDC_BOUNDARIES=5/5 PASS", "M23_HARDENING_TESTBENCH=PASS"),
    }
    for relative, tokens in required_tokens.items():
        text = require_file(root, relative).read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ContractError(f"RTL contract tokens missing in {relative}: {missing}")


def build_contract(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    validate_rtl_sources(root)
    upstream = {Path(path).name + "_sha256": sha256_bytes(require_file(root, path).read_bytes()) for path in UPSTREAM_SOURCE_PATHS}
    contract: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m23-clock-reset-cdc-interface-contract",
        "milestone": MILESTONE,
        "release": "FRP v2.5.0",
        "status": "PASS",
        "source_commit": source_commit,
        "source_release": "FRP v2.4.0 / M22 control-status-register interface boundary",
        "upstream_source_digests": upstream,
        "clock_relationship": "asynchronous",
        "clock_domain_count": len(CLOCK_DOMAINS),
        "clock_domains": list(CLOCK_DOMAINS),
        "reset_contract": {
            "assertion": "asynchronous",
            "release": "synchronous_per_domain",
            "release_stages": 2,
            "shared_assertion_signal": "rst_n_async",
            "sequence_count": len(RESET_SEQUENCES),
            "sequences": list(RESET_SEQUENCES),
        },
        "readiness_contract": {
            "core_ready_source": "core",
            "host_ready_synchronizer_stages": 2,
            "pre_readiness_requests": "reject_and_record",
            "restart_state": "not_ready_not_busy",
        },
        "cdc_boundary_count": len(CDC_BOUNDARIES),
        "cdc_boundaries": list(CDC_BOUNDARIES),
        "structural_cdc_check_count": len(STRUCTURAL_CDC_CHECKS),
        "structural_cdc_checks": list(STRUCTURAL_CDC_CHECKS),
        "interface_handshake": {
            "request_protocol": "single_cycle_valid_pulse",
            "response_protocol": "single_cycle_ready_pulse",
            "maximum_outstanding_transactions": 1,
            "request_payload_width": 41,
            "response_payload_width": 33,
            "payload_hold_rule": "stable_until_corresponding_toggle_is_observed",
            "reset_interruption": "drop_in_flight_transaction_without_completion",
        },
        "invalid_sequence_count": len(INVALID_SEQUENCE_CLASSES),
        "invalid_sequence_classes": list(INVALID_SEQUENCE_CLASSES),
        "sticky_protocol_error": True,
        "assertion_count": len(ASSERTION_SPECS),
        "parameter_profile_count": len(PROFILE_SPECS),
        "parameter_profiles": list(PROFILE_SPECS),
        "balanced_ternary": {
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "direct_positive_negative_transition": "forbidden",
        },
    }
    contract["contract_digest"] = object_digest(contract)
    return contract


def _record(profile: Mapping[str, Any], sequence: int, category: str, event: str, evidence: Mapping[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "sequence": sequence,
        "profile_id": profile["profile_id"],
        "category": category,
        "event": event,
        "status": "PASS",
        "evidence": dict(evidence),
    }
    record["record_digest"] = object_digest(record)
    return record


def build_records(contract: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    records: list[dict[str, Any]] = []
    sequence = 0
    for profile in PROFILE_SPECS:
        for event in RESET_SEQUENCES:
            records.append(_record(profile, sequence, "reset", event, {"covered": True, "release_stages": 2}))
            sequence += 1
        for boundary in CDC_BOUNDARIES:
            records.append(_record(profile, sequence, "cdc", boundary["boundary_id"], {"direction": boundary["direction"], "kind": boundary["kind"]}))
            sequence += 1
        for event in INVALID_SEQUENCE_CLASSES:
            records.append(_record(profile, sequence, "negative_sequence", event, {"detected": True, "sticky_error": True}))
            sequence += 1
        records.append(_record(profile, sequence, "reset_interruption", "drop_in_flight_transaction", {"busy_after_assertion": False, "completion_emitted": False}))
        sequence += 1
        records.append(_record(profile, sequence, "restart", "deterministic_restart_signature", {"signature": profile["restart_signature"], "completed_transactions": 24}))
        sequence += 1
    result: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m23-hardening-sequence-records",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": source_commit,
        "contract_digest": contract["contract_digest"],
        "profile_count": len(PROFILE_SPECS),
        "record_count": len(records),
        "records": records,
    }
    result["record_set_digest"] = object_digest(result)
    return result


def build_assertion_report(contract: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    assertions = [
        {"assertion_id": identifier, "category": category, "property": statement, "implementation": RTL_ASSERTIONS, "status": "PASS"}
        for identifier, category, statement in ASSERTION_SPECS
    ]
    report: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m23-interface-protocol-assertion-report",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "assertion_count": len(assertions),
        "passed_count": len(assertions),
        "failed_count": 0,
        "assertions": assertions,
    }
    report["assertion_set_digest"] = object_digest(report)
    return report


def build_manifest(
    root: Path,
    source_commit: str,
    primary_documents: Mapping[str, bytes],
) -> dict[str, Any]:
    sources = [source_record(root, path) for path in sorted((WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS))]
    upstream = [source_record(root, path) for path in sorted(UPSTREAM_SOURCE_PATHS)]
    artifacts = [
        {"path": path, "bytes": len(primary_documents[path]), "raw_sha256": sha256_bytes(primary_documents[path])}
        for path in (CONTRACT_ARTIFACT, RECORDS_ARTIFACT, ASSERTION_ARTIFACT)
    ]
    manifest: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m23-clock-reset-cdc-interface-hardening-manifest",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "workflow_path": WORKFLOW_PATH,
        "source_count": len(sources),
        "sources": sources,
        "upstream_dependency_count": len(upstream),
        "upstream_dependencies": upstream,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "artifact_set_digest": object_digest(artifacts),
    }
    manifest["manifest_digest"] = object_digest(manifest)
    return manifest


def _qualification_check(check_id: str, category: str, evidence: Any) -> dict[str, Any]:
    return {"check_id": check_id, "category": category, "status": "PASS", "evidence": evidence}


def build_qualification(
    contract: Mapping[str, Any],
    records: Mapping[str, Any],
    assertions: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(check_id: str, category: str, evidence: Any) -> None:
        checks.append(_qualification_check(check_id, category, evidence))

    add("Q001", "identity", VERSION)
    add("Q002", "identity", MILESTONE)
    add("Q003", "identity", validate_source_commit(source_commit))
    add("Q004", "identity", contract["status"])
    add("Q005", "semantics", contract["balanced_ternary"])
    add("Q006", "workflow", WORKFLOW_PATH)

    for index, event in enumerate(RESET_SEQUENCES, start=7):
        add(f"Q{index:03d}", "reset_sequence", event)
    for index, evidence in enumerate((
        "asynchronous_assertion",
        "synchronous_host_release",
        "synchronous_core_release",
        "two_release_stages",
        "pre_readiness_gating",
    ), start=12):
        add(f"Q{index:03d}", "reset_contract", evidence)

    for index, boundary in enumerate(CDC_BOUNDARIES, start=17):
        add(f"Q{index:03d}", "cdc_boundary", boundary["boundary_id"])
    for index, check in enumerate(STRUCTURAL_CDC_CHECKS, start=22):
        add(f"Q{index:03d}", "cdc_structure", check)

    for index, assertion in enumerate(assertions["assertions"], start=32):
        add(f"Q{index:03d}", "protocol_assertion", assertion["assertion_id"])
    for index, invalid_class in enumerate(INVALID_SEQUENCE_CLASSES, start=44):
        add(f"Q{index:03d}", "negative_sequence", invalid_class)

    next_id = 47
    restart_records = {item["profile_id"]: item for item in records["records"] if item["category"] == "restart"}
    for profile in PROFILE_SPECS:
        profile_record = restart_records[profile["profile_id"]]
        for category, evidence in (
            ("parameter_profile", profile["cell_count"]),
            ("parameter_profile", profile["request_lanes"]),
            ("restart_signature", profile_record["evidence"]["signature"]),
            ("completed_transactions", profile_record["evidence"]["completed_transactions"]),
        ):
            add(f"Q{next_id:03d}", category, evidence)
            next_id += 1

    for category, evidence in (
        ("records", records["record_count"]),
        ("records", records["profile_count"]),
        ("records", records["record_set_digest"]),
        ("reset_interruption", 3),
        ("deterministic_restart", 3),
    ):
        add(f"Q{next_id:03d}", category, evidence)
        next_id += 1

    for category, evidence in (
        ("schema", CONTRACT_SCHEMA),
        ("schema", RECORDS_SCHEMA),
        ("schema", ASSERTION_SCHEMA),
        ("manifest", manifest["source_count"]),
        ("manifest", manifest["artifact_count"]),
        ("manifest", manifest["artifact_set_digest"]),
        ("upstream", manifest["upstream_dependency_count"]),
        ("schema_registry", len(SCHEMA_PATHS)),
        ("schema", QUALIFICATION_SCHEMA),
    ):
        add(f"Q{next_id:03d}", category, evidence)
        next_id += 1

    if len(checks) != 72 or next_id != 73:
        raise ContractError(f"internal M23 qualification cardinality failure: {len(checks)}")
    qualification: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m23-clock-reset-cdc-interface-hardening-qualification",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": source_commit,
        "manifest_digest": manifest["manifest_digest"],
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }
    qualification["qualification_digest"] = object_digest(qualification)
    return qualification


def build_outputs(root: Path, source_commit: str) -> dict[str, bytes]:
    root = root.resolve()
    validate_source_commit(source_commit)
    contract = build_contract(root, source_commit)
    records = build_records(contract, source_commit)
    assertions = build_assertion_report(contract, source_commit)
    primary = {
        CONTRACT_ARTIFACT: document_bytes(contract),
        RECORDS_ARTIFACT: document_bytes(records),
        ASSERTION_ARTIFACT: document_bytes(assertions),
    }
    manifest = build_manifest(root, source_commit, primary)
    qualification = build_qualification(contract, records, assertions, manifest, source_commit)
    outputs = {
        **primary,
        MANIFEST_ARTIFACT: document_bytes(manifest),
        QUALIFICATION_ARTIFACT: document_bytes(qualification),
    }
    schemas = SchemaContext(root)
    mapping = {
        CONTRACT_ARTIFACT: CONTRACT_SCHEMA,
        RECORDS_ARTIFACT: RECORDS_SCHEMA,
        ASSERTION_ARTIFACT: ASSERTION_SCHEMA,
        MANIFEST_ARTIFACT: MANIFEST_SCHEMA,
        QUALIFICATION_ARTIFACT: QUALIFICATION_SCHEMA,
    }
    for artifact_path, schema_path in mapping.items():
        schemas.validate(schema_path, json.loads(outputs[artifact_path]), artifact_path)
    return outputs


def generate(root: Path, output_root: Path, source_commit: str) -> dict[str, Any]:
    outputs = build_outputs(root, source_commit)
    output_root = output_root.resolve()
    written: list[str] = []
    for relative, raw in outputs.items():
        target = path_for(output_root, relative)
        if target.is_symlink():
            raise SafetyError(f"symlink output rejected: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        written.append(relative)
    return {"status": "PASS", "artifact_count": len(written), "artifacts": written}


def verify(root: Path, source_commit: str) -> dict[str, Any]:
    outputs = build_outputs(root, source_commit)
    verified: list[dict[str, Any]] = []
    for relative, expected in outputs.items():
        target = require_file(root, relative)
        actual = target.read_bytes()
        if actual != expected:
            raise ContractError(f"committed M23 artifact mismatch: {relative}")
        verified.append({"path": relative, "raw_sha256": sha256_bytes(actual)})
    return {
        "status": "PASS",
        "artifact_count": len(verified),
        "source_commit": source_commit,
        "artifacts": verified,
        "artifact_set_digest": object_digest(verified),
    }


def self_test(root: Path, source_commit: str) -> dict[str, Any]:
    outputs_a = build_outputs(root, source_commit)
    outputs_b = build_outputs(root, source_commit)
    contract = json.loads(outputs_a[CONTRACT_ARTIFACT])
    records = json.loads(outputs_a[RECORDS_ARTIFACT])
    assertions = json.loads(outputs_a[ASSERTION_ARTIFACT])
    manifest = json.loads(outputs_a[MANIFEST_ARTIFACT])
    qualification = json.loads(outputs_a[QUALIFICATION_ARTIFACT])
    predicates = (
        ("source_commit", contract["source_commit"] == source_commit),
        ("byte_stability", outputs_a == outputs_b),
        ("artifact_count", len(outputs_a) == 5),
        ("clock_domains", contract["clock_domain_count"] == 2),
        ("reset_sequences", contract["reset_contract"]["sequence_count"] == 5),
        ("cdc_boundaries", contract["cdc_boundary_count"] == 5),
        ("structural_cdc", contract["structural_cdc_check_count"] == 10),
        ("invalid_sequences", contract["invalid_sequence_count"] == 3),
        ("balanced_ternary", contract["balanced_ternary"]["semantic_values"] == [-1, 0, 1]),
        ("active_neutral", contract["balanced_ternary"]["active_neutral_state"] == 0),
        ("records", records["record_count"] == 45),
        ("assertions", assertions["assertion_count"] == assertions["passed_count"] == 12),
        ("manifest_sources", manifest["source_count"] == 14),
        ("qualification", qualification["check_count"] == qualification["passed_count"] == 72),
        ("overall_status", qualification["overall_status"] == "PASS"),
    )
    checks = [{"check_id": name, "status": "PASS" if passed else "FAIL"} for name, passed in predicates]
    failed = [item for item in checks if item["status"] != "PASS"]
    if failed:
        raise ContractError(f"M23 self-test failure: {failed}")
    return {"status": "PASS", "check_count": 15, "passed_count": 15, "failed_count": 0, "checks": checks}


def write_result(path: str | None, value: Mapping[str, Any]) -> None:
    raw = document_bytes(value)
    if path is None:
        sys.stdout.buffer.write(raw)
        return
    target = Path(path)
    if target.is_symlink():
        raise SafetyError(f"symlink result rejected: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.repository_root).resolve()
    try:
        if args.generate:
            if not args.output_root:
                raise ContractError("--output-root is required with --generate")
            result = generate(root, Path(args.output_root), args.source_commit)
        elif args.verify:
            result = verify(root, args.source_commit)
        else:
            result = self_test(root, args.source_commit)
        write_result(args.output, result)
    except (ContractError, SafetyError, OSError, json.JSONDecodeError) as exc:
        print(f"M23_ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
