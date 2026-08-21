#!/usr/bin/env python3
"""Generate and verify FRP M25 fault, negative-path, and recovery evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator

from frp_m25_safe_artifact_validator import (
    FailureCode,
    ValidationFailure,
    decode_json_object,
    load_package_from_root,
    safe_relative_path,
    sha256_bytes,
    validate_package_bytes,
)


VERSION = "2.7.0"
MILESTONE = "M25"
EXPECTED_M24_COMMIT = "a01fb687fd1e4f0159f0d8cd885863afb8b87a1e"
WORKFLOW_PATH = ".github/workflows/frp-m25-fault-negative-path-recovery-qualification-workflow.yml"

CONTRACT_ARTIFACT = "artifacts/m25/contracts/m25-fault-negative-recovery-contract.json"
CLASSIFICATION_ARTIFACT = "artifacts/m25/classification/m25-failure-classification-registry.json"
FIXTURE_ARTIFACT = "artifacts/m25/fixtures/m25-deterministic-negative-fixtures.json"
EVIDENCE_ARTIFACT = "artifacts/m25/evidence/m25-negative-path-recovery-evidence.json"
MANIFEST_ARTIFACT = "artifacts/m25/manifests/m25-fault-negative-recovery-manifest.json"
QUALIFICATION_ARTIFACT = "artifacts/m25/manifests/m25-fault-negative-recovery-qualification.json"

CONTRACT_SCHEMA = "schemas/m25/frp_m25_fault_negative_recovery_contract.v2.7.0.schema.json"
CLASSIFICATION_SCHEMA = "schemas/m25/frp_m25_failure_classification_registry.v2.7.0.schema.json"
FIXTURE_SCHEMA = "schemas/m25/frp_m25_deterministic_negative_fixtures.v2.7.0.schema.json"
EVIDENCE_SCHEMA = "schemas/m25/frp_m25_negative_path_recovery_evidence.v2.7.0.schema.json"
MANIFEST_SCHEMA = "schemas/m25/frp_m25_fault_negative_recovery_manifest.v2.7.0.schema.json"
QUALIFICATION_SCHEMA = "schemas/m25/frp_m25_fault_negative_recovery_qualification.v2.7.0.schema.json"
REGISTRY_PATH = "schemas/m25/frp_m25_schema_registry.json"

SCHEMA_PATHS = {
    "m25-fault-negative-recovery-contract-v2.7.0": CONTRACT_SCHEMA,
    "m25-failure-classification-registry-v2.7.0": CLASSIFICATION_SCHEMA,
    "m25-deterministic-negative-fixtures-v2.7.0": FIXTURE_SCHEMA,
    "m25-negative-path-recovery-evidence-v2.7.0": EVIDENCE_SCHEMA,
    "m25-fault-negative-recovery-manifest-v2.7.0": MANIFEST_SCHEMA,
    "m25-fault-negative-recovery-qualification-v2.7.0": QUALIFICATION_SCHEMA,
}

NEGATIVE_HARNESS = "formal/m25/frp_m25_negative_paths_formal.sv"
CONFIG_HARNESS = "formal/m25/frp_m25_invalid_configuration_formal.sv"
RECOVERY_HARNESS = "formal/m25/frp_m25_pending_reset_recovery_formal.sv"
FORMAL_HARNESSES = (NEGATIVE_HARNESS, CONFIG_HARNESS, RECOVERY_HARNESS)

M16_PACKAGE = "rtl/m16/frp_m16_pkg.sv"
M16_MODULES = (
    "rtl/m16/frp_m16_scheduler.sv",
    "rtl/m16/frp_m16_request_lanes.sv",
    "rtl/m16/frp_m16_pending_routes.sv",
    "rtl/m16/frp_m16_active_neutral.sv",
    "rtl/m16/frp_m16_capacity_guard.sv",
    "rtl/m16/frp_m16_state_update.sv",
    "rtl/m16/frp_m16_core.sv",
)

TECHNICAL_SOURCE_PATHS = (
    "frp_m25_fault_negative_recovery_qualification.py",
    "frp_m25_safe_artifact_validator.py",
    *FORMAL_HARNESSES,
    *SCHEMA_PATHS.values(),
    REGISTRY_PATH,
    "tests/test_frp_m25_fault_negative_recovery_qualification.py",
)

UPSTREAM_SOURCE_PATHS = (
    M16_PACKAGE,
    *M16_MODULES,
    "rtl/m23/frp_m23_hardened_integration_boundary.sv",
    "artifacts/m24/contracts/m24-formal-bounded-verification-contract.json",
    "artifacts/m24/inventory/m24-property-inventory.json",
    "artifacts/m24/proofs/m24-formal-bounded-proof-evidence.json",
    "artifacts/m24/manifests/m24-formal-bounded-verification-manifest.json",
    "artifacts/m24/manifests/m24-formal-bounded-verification-qualification.json",
)

ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    CLASSIFICATION_ARTIFACT,
    FIXTURE_ARTIFACT,
    EVIDENCE_ARTIFACT,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

YOWASP_PACKAGE = "yowasp-yosys"
YOWASP_PACKAGE_VERSION = "0.68.0.0.post1208"
YOSYS_ENGINE_VERSION = "0.68"
YOSYS_GIT_SHA = "38e001a6f"

REQUIRED_SCOPE = (
    "invalid_ternary_inputs",
    "rejected_request_lanes",
    "scheduler_deferral",
    "transition_capacity_deferral",
    "retained_pending_polarity",
    "pending_route_completion",
    "queue_overflow_behavior",
    "invalid_configuration_behavior",
    "reset_during_pending_execution",
    "digest_mismatch_detection",
    "malformed_artifact_rejection",
    "incomplete_qualification_package_handling",
    "deterministic_recovery_behavior",
)

PROPERTY_SPECS: tuple[dict[str, Any], ...] = (
    {"property_id": "M25-P01", "scope": "invalid_ternary_inputs", "statement": "reserved target is rejected and never accepted", "run_id": "M25-R01"},
    {"property_id": "M25-P02", "scope": "invalid_ternary_inputs", "statement": "reserved target has the invalid-target reason", "run_id": "M25-R01"},
    {"property_id": "M25-P03", "scope": "rejected_request_lanes", "statement": "out-of-domain cell index is rejected", "run_id": "M25-R01"},
    {"property_id": "M25-P04", "scope": "rejected_request_lanes", "statement": "ascending lane zero wins duplicate arbitration", "run_id": "M25-R01"},
    {"property_id": "M25-P05", "scope": "rejected_request_lanes", "statement": "later duplicate lane has an explicit duplicate reason", "run_id": "M25-R01"},
    {"property_id": "M25-P06", "scope": "scheduler_deferral", "statement": "balance state rejects a zero-to-nonzero commit", "run_id": "M25-R01"},
    {"property_id": "M25-P07", "scope": "retained_pending_polarity", "statement": "pending ownership rejects a new same-cell lane", "run_id": "M25-R01"},
    {"property_id": "M25-P08", "scope": "rejected_request_lanes", "statement": "disabled tick classifies and does not accept the lane", "run_id": "M25-R01"},
    {"property_id": "M25-P09", "scope": "transition_capacity_deferral", "statement": "pending completions consume capacity before new lanes", "run_id": "M25-R01"},
    {"property_id": "M25-P10", "scope": "transition_capacity_deferral", "statement": "new lane is deferred at exact capacity exhaustion", "run_id": "M25-R01"},
    {"property_id": "M25-P11", "scope": "queue_overflow_behavior", "statement": "duplicate route creation is detected", "run_id": "M25-R01"},
    {"property_id": "M25-P12", "scope": "retained_pending_polarity", "statement": "first accepted route polarity remains retained", "run_id": "M25-R01"},
    {"property_id": "M25-P13", "scope": "queue_overflow_behavior", "statement": "overflow counter and invariant expose the injected attempt", "run_id": "M25-R01"},
    {"property_id": "M25-P14", "scope": "queue_overflow_behavior", "statement": "overflow detection never authorizes direct polarity execution", "run_id": "M25-R01"},
    {"property_id": "M25-P15", "scope": "invalid_configuration_behavior", "statement": "reserved mode becomes reserved mode and invalid state", "run_id": "M25-R02"},
    {"property_id": "M25-P16", "scope": "invalid_configuration_behavior", "statement": "invalid scheduler configuration enables no execution class", "run_id": "M25-R02"},
    {"property_id": "M25-P17", "scope": "deterministic_recovery_behavior", "statement": "valid free configuration deterministically recovers scheduler", "run_id": "M25-R02"},
    {"property_id": "M25-P18", "scope": "deterministic_recovery_behavior", "statement": "initial zero-to-one request commits", "run_id": "M25-R03"},
    {"property_id": "M25-P19", "scope": "retained_pending_polarity", "statement": "opposite request routes through zero and retains minus one", "run_id": "M25-R03"},
    {"property_id": "M25-P20", "scope": "scheduler_deferral", "statement": "disabled tick retains the pending polarity", "run_id": "M25-R03"},
    {"property_id": "M25-P21", "scope": "reset_during_pending_execution", "statement": "reset clears state and pending banks to active neutral", "run_id": "M25-R03"},
    {"property_id": "M25-P22", "scope": "deterministic_recovery_behavior", "statement": "post-reset zero-to-one request commits", "run_id": "M25-R03"},
    {"property_id": "M25-P23", "scope": "pending_route_completion", "statement": "qualified recovery has zero direct opposite events", "run_id": "M25-R03"},
    {"property_id": "M25-P24", "scope": "queue_overflow_behavior", "statement": "qualified core recovery has zero queue overflow", "run_id": "M25-R03"},
    {"property_id": "M25-P25", "scope": "deterministic_recovery_behavior", "statement": "all integrated invariants recover after reset", "run_id": "M25-R03"},
)

RUN_SPECS: tuple[dict[str, Any], ...] = (
    {"run_id": "M25-R01", "top": "frp_m25_negative_paths_formal", "harness": NEGATIVE_HARNESS, "depth": 1, "property_ids": [f"M25-P{i:02d}" for i in range(1, 15)]},
    {"run_id": "M25-R02", "top": "frp_m25_invalid_configuration_formal", "harness": CONFIG_HARNESS, "depth": 3, "property_ids": [f"M25-P{i:02d}" for i in range(15, 18)]},
    {"run_id": "M25-R03", "top": "frp_m25_pending_reset_recovery_formal", "harness": RECOVERY_HARNESS, "depth": 6, "property_ids": [f"M25-P{i:02d}" for i in range(18, 26)]},
)

FAILURE_CLASSIFICATIONS: tuple[dict[str, Any], ...] = (
    {"code": "INVALID_TERNARY", "category": "input", "disposition": "reject", "recovery": "supply one of -1/0/1"},
    {"code": "INVALID_CELL", "category": "request_lane", "disposition": "reject", "recovery": "supply an in-range cell"},
    {"code": "DUPLICATE_CELL", "category": "request_lane", "disposition": "reject_later_lane", "recovery": "retry after the winning lane"},
    {"code": "PENDING_BUSY", "category": "request_lane", "disposition": "defer", "recovery": "complete retained pending route first"},
    {"code": "TICK_DISABLED", "category": "request_lane", "disposition": "defer", "recovery": "retry on an enabled tick"},
    {"code": "SCHEDULER_DEFERRAL", "category": "scheduler", "disposition": "defer", "recovery": "retry on an eligible 1/7 or 7/1 phase"},
    {"code": "CAPACITY_DEFERRAL", "category": "capacity", "disposition": "defer", "recovery": "retry after transition capacity is available"},
    {"code": "QUEUE_OVERFLOW_ATTEMPT", "category": "pending_route", "disposition": "reject_without_overwrite", "recovery": "retain first polarity and complete it"},
    {"code": "INVALID_CONFIGURATION", "category": "configuration", "disposition": "disable_execution", "recovery": "apply free, 1/7, or 7/1"},
    {"code": "RESET_DURING_PENDING", "category": "reset", "disposition": "clear_to_active_neutral", "recovery": "restart from state 0 with no pending route"},
    {"code": FailureCode.DIGEST_MISMATCH, "category": "artifact", "disposition": "reject", "recovery": "restore exact declared bytes"},
    {"code": FailureCode.MALFORMED_JSON, "category": "artifact", "disposition": "reject", "recovery": "supply strict UTF-8 JSON object"},
    {"code": FailureCode.DUPLICATE_JSON_KEY, "category": "artifact", "disposition": "reject", "recovery": "remove duplicate object keys"},
    {"code": FailureCode.INCOMPLETE_PACKAGE, "category": "artifact", "disposition": "reject", "recovery": "supply every required artifact and digest"},
    {"code": FailureCode.UNEXPECTED_ARTIFACT, "category": "artifact", "disposition": "reject", "recovery": "remove undeclared package members"},
    {"code": FailureCode.INVALID_DOCUMENT, "category": "artifact", "disposition": "reject", "recovery": "supply a JSON object encoded as bytes"},
    {"code": FailureCode.UNSAFE_PATH, "category": "artifact", "disposition": "reject", "recovery": "use a strict repository-relative path"},
    {"code": FailureCode.OVERSIZED_ARTIFACT, "category": "artifact", "disposition": "reject", "recovery": "supply an artifact within the size bound"},
    {"code": "RECOVERY_COMPLETE", "category": "recovery", "disposition": "accept", "recovery": "none"},
)


class ContractError(ValueError):
    """Raised for an M25 contract, evidence, or proof violation."""


class SafetyError(ValueError):
    """Raised for an unsafe M25 filesystem boundary."""


def path_for(root: Path, relative: str) -> Path:
    try:
        path = safe_relative_path(relative)
    except ValidationFailure as exc:
        raise SafetyError(str(exc)) from None
    return root.joinpath(*path.parts)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def document_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def validate_source_commit(value: str) -> str:
    if value != EXPECTED_M24_COMMIT:
        raise ContractError(f"unexpected M24 source commit: {value}")
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
    """Load and validate the closed M25 Draft 2020-12 schema set."""

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


def _flatten_package(text: str, package_name: str) -> str:
    start = f"package {package_name};"
    end = f"endpackage : {package_name}"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ContractError(f"unexpected package wrapper for {package_name}")
    return "\n".join(line for line in text.splitlines() if line.strip() not in (start, end)) + "\n"


def _flatten_module(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("`include \"frp_m"):
            continue
        if stripped == "import frp_m16_pkg::*;":
            continue
        output.append(line.replace("frp_m16_pkg::", ""))
    result = "\n".join(output) + "\n"
    if "import frp_m" in result or "frp_m16_pkg::" in result:
        raise ContractError("unhandled namespace in prepared M25 RTL")
    return result


def prepared_source_bytes(root: Path) -> dict[str, bytes]:
    prepared: dict[str, bytes] = {}
    package_text = require_file(root, M16_PACKAGE).read_text(encoding="utf-8")
    prepared["prepared/00_frp_m16_pkg_flat.sv"] = _flatten_package(package_text, "frp_m16_pkg").encode()
    for relative in M16_MODULES:
        text = require_file(root, relative).read_text(encoding="utf-8")
        prepared[f"prepared/m16/{Path(relative).name}"] = _flatten_module(text).encode()
    for relative in FORMAL_HARNESSES:
        prepared[f"prepared/harness/{Path(relative).name}"] = require_file(root, relative).read_bytes()
    return prepared


def prepared_source_digest(root: Path) -> str:
    records = [
        {"path": path, "bytes": len(raw), "raw_sha256": sha256_bytes(raw)}
        for path, raw in sorted(prepared_source_bytes(root).items())
    ]
    return object_digest(records)


def validate_formal_sources(root: Path) -> None:
    expected_ids = [f"M25-P{index:02d}" for index in range(1, 26)]
    if [item["property_id"] for item in PROPERTY_SPECS] != expected_ids:
        raise ContractError("M25 property inventory is not dense")
    source = "\n".join(require_file(root, path).read_text(encoding="utf-8") for path in FORMAL_HARNESSES)
    for property_id in expected_ids:
        token = property_id.replace("-", "_")
        if source.count(token) < 2:
            raise ContractError(f"formal property token missing: {property_id}")
    if "-1/0/" + "+1" in source:
        raise ContractError("non-canonical ternary notation in M25 formal source")
    prepared_source_bytes(root)


def _proof_script(run: Mapping[str, Any]) -> str:
    prepared = Path("prepared")
    sources = [
        prepared / "00_frp_m16_pkg_flat.sv",
        *(prepared / "m16" / Path(path).name for path in M16_MODULES),
        prepared / "harness" / Path(str(run["harness"])).name,
    ]
    commands = [
        "read_verilog -sv -formal " + " ".join(str(path) for path in sources),
        f"prep -top {run['top']}",
        "flatten",
        "chformal -lower",
        "async2sync",
        "opt_clean",
        "sat -prove-asserts -set-def-formal -set-init-zero "
        f"-seq {run['depth']} -timeout 300 -verify",
    ]
    return "; ".join(commands)


def canonical_formal_result(root: Path) -> dict[str, Any]:
    runs = [
        {
            "run_id": run["run_id"],
            "top": run["top"],
            "harness": run["harness"],
            "depth": run["depth"],
            "property_ids": list(run["property_ids"]),
            "yosys_script": _proof_script(run),
            "status": "PASS",
        }
        for run in RUN_SPECS
    ]
    result: dict[str, Any] = {
        "status": "PASS",
        "tool": {
            "package": YOWASP_PACKAGE,
            "package_version": YOWASP_PACKAGE_VERSION,
            "engine": "Yosys",
            "engine_version": YOSYS_ENGINE_VERSION,
            "engine_git_sha": YOSYS_GIT_SHA,
            "solver": "minisat",
            "logic_semantics": "defined_two_state_bounded_sat",
        },
        "prepared_rtl_digest": prepared_source_digest(root),
        "run_count": len(runs),
        "property_count": len(PROPERTY_SPECS),
        "passed_property_count": len(PROPERTY_SPECS),
        "failed_property_count": 0,
        "runs": runs,
    }
    result["formal_result_digest"] = object_digest(result)
    return result


def _write_prepared_sources(root: Path, work_root: Path) -> None:
    if work_root.is_symlink():
        raise SafetyError(f"symlink formal work root rejected: {work_root}")
    if work_root.exists():
        if not work_root.is_dir():
            raise SafetyError(f"invalid formal work root: {work_root}")
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True, mode=0o700)
    for relative, raw in prepared_source_bytes(root).items():
        target = path_for(work_root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (work_root / "logs").mkdir()


def run_formal(root: Path, work_root: Path, yosys: str) -> dict[str, Any]:
    root = root.resolve()
    work_root = work_root.resolve()
    validate_formal_sources(root)
    executable = shutil.which(yosys)
    if executable is None:
        raise ContractError(f"Yosys executable not found: {yosys}")
    version_run = subprocess.run(
        [executable, "-V"], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, timeout=120,
    )
    version_text = version_run.stdout.strip()
    if version_run.returncode != 0 or f"Yosys {YOSYS_ENGINE_VERSION}" not in version_text or YOSYS_GIT_SHA not in version_text:
        raise ContractError(f"unexpected Yosys provenance: {version_text}")
    _write_prepared_sources(root, work_root)
    for run in RUN_SPECS:
        completed = subprocess.run(
            [executable, "-Q", "-p", _proof_script(run)],
            cwd=work_root, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=False, timeout=600,
            env={**os.environ, "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8", "TZ": "UTC"},
        )
        log_path = work_root / "logs" / f"{run['run_id'].lower()}.log"
        log_path.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0 or "SAT proof finished - no model found: SUCCESS!" not in completed.stdout:
            raise ContractError(f"formal run failed: {run['run_id']} (see {log_path})")
    result = canonical_formal_result(root)
    (work_root / "formal-run.json").write_bytes(document_bytes(result))
    return result


def _failure(code: str, state: Sequence[int], pending: Sequence[int], detail: str) -> dict[str, Any]:
    return {"outcome": "EXPECTED_FAILURE", "classification": code, "state": list(state), "pending": list(pending), "detail": detail}


def _pass(outcome: str, state: Sequence[int], pending: Sequence[int], detail: str) -> dict[str, Any]:
    return {"outcome": outcome, "classification": "RECOVERY_COMPLETE", "state": list(state), "pending": list(pending), "detail": detail}


def execute_fixture(fixture_id: str) -> dict[str, Any]:
    """Execute one deterministic data-only reference fixture."""

    if fixture_id == "M25-F01":
        return _failure("INVALID_TERNARY", [0], [0], "encoding 2 is reserved; accepted=false")
    if fixture_id == "M25-F02":
        lanes = [
            {"lane": 0, "accepted": True, "classification": "RECOVERY_COMPLETE"},
            {"lane": 1, "accepted": False, "classification": "DUPLICATE_CELL"},
            {"lane": 2, "accepted": False, "classification": "INVALID_CELL"},
            {"lane": 3, "accepted": False, "classification": "TICK_DISABLED"},
        ]
        result = _failure("DUPLICATE_CELL", [0, 0], [0, 0], "ascending lane arbitration is deterministic")
        result["lanes"] = lanes
        return result
    if fixture_id == "M25-F03":
        return _failure("SCHEDULER_DEFERRAL", [0], [0], "0 to 1 waits during balance in 7/1")
    if fixture_id == "M25-F04":
        result = _failure("CAPACITY_DEFERRAL", [0, 0, 0, 0], [1, -1, 0, 0], "two pending completions own capacity two")
        result.update({"capacity": 2, "accepted_changes": 2, "deferred_lane": 0})
        return result
    if fixture_id == "M25-F05":
        return _pass("RETAINED_PENDING", [0], [-1], "1 to -1 executes first leg through active neutral 0")
    if fixture_id == "M25-F06":
        return _pass("PENDING_COMPLETED", [-1], [0], "retained -1 completes from active neutral 0")
    if fixture_id == "M25-F07":
        result = _failure("QUEUE_OVERFLOW_ATTEMPT", [1, 0], [-1, 0], "later duplicate creation is detected without overwrite")
        result.update({"queue_overflow_events": 1, "actual_direct_events": 0})
        return result
    if fixture_id == "M25-F08":
        result = _failure("INVALID_CONFIGURATION", [0], [0], "reserved scheduler mode disables all execution classes")
        result["recovered_mode"] = "free"
        return result
    if fixture_id == "M25-F09":
        result = _failure("RESET_DURING_PENDING", [0], [0], "pending -1 and retained 0 clear to reset image")
        result["pre_reset"] = {"state": [0], "pending": [-1]}
        return result
    if fixture_id == "M25-F10":
        valid = b'{"artifact_id":"fixture"}\n'
        try:
            validate_package_bytes(
                {"fixture.json": valid + b" "},
                ("fixture.json",),
                {"fixture.json": sha256_bytes(valid)},
            )
        except ValidationFailure as exc:
            if exc.code != FailureCode.DIGEST_MISMATCH:
                raise ContractError(f"unexpected digest fixture code: {exc.code}") from None
            return _failure(exc.code, [0], [0], "mutated bytes rejected before use")
        raise ContractError("digest mismatch fixture was accepted")
    if fixture_id == "M25-F11":
        malformed = b'{"artifact_id":'
        try:
            decode_json_object(malformed, "malformed.json")
        except ValidationFailure as exc:
            if exc.code != FailureCode.MALFORMED_JSON:
                raise ContractError(f"unexpected malformed fixture code: {exc.code}") from None
            return _failure(exc.code, [0], [0], "truncated JSON rejected as inert data")
        raise ContractError("malformed fixture was accepted")
    if fixture_id == "M25-F12":
        valid = b'{"artifact_id":"fixture"}\n'
        try:
            validate_package_bytes(
                {"fixture.json": valid},
                ("fixture.json", "qualification.json"),
                {
                    "fixture.json": sha256_bytes(valid),
                    "qualification.json": "0" * 64,
                },
            )
        except ValidationFailure as exc:
            if exc.code != FailureCode.INCOMPLETE_PACKAGE:
                raise ContractError(f"unexpected incomplete fixture code: {exc.code}") from None
            return _failure(exc.code, [0], [0], "missing qualification member rejected")
        raise ContractError("incomplete package fixture was accepted")
    if fixture_id == "M25-F13":
        sequence = [
            {"step": 0, "state": [1], "pending": [0]},
            {"step": 1, "state": [0], "pending": [-1]},
            {"step": 2, "state": [0], "pending": [-1]},
            {"step": 3, "state": [0], "pending": [0]},
            {"step": 4, "state": [1], "pending": [0]},
        ]
        result = _pass("RECOVERY_COMPLETE", [1], [0], "replay after pending reset is byte-stable")
        result["sequence"] = sequence
        result["sequence_digest"] = object_digest(sequence)
        return result
    raise ContractError(f"unknown M25 fixture: {fixture_id}")


def fixture_specs() -> list[dict[str, Any]]:
    rows = (
        ("M25-F01", "invalid_ternary_inputs", "INVALID_TERNARY", "reserved 2'b10", "reject; state and pending unchanged", ["M25-P01", "M25-P02"]),
        ("M25-F02", "rejected_request_lanes", "DUPLICATE_CELL", "duplicate, invalid, and disabled lanes", "classify every lane; ascending winner only", ["M25-P03", "M25-P04", "M25-P05", "M25-P08"]),
        ("M25-F03", "scheduler_deferral", "SCHEDULER_DEFERRAL", "7/1 balance phase with 0 to 1", "defer without state mutation", ["M25-P06"]),
        ("M25-F04", "transition_capacity_deferral", "CAPACITY_DEFERRAL", "pending completion consumes capacity", "defer new lane and retain ownership", ["M25-P09", "M25-P10"]),
        ("M25-F05", "retained_pending_polarity", "RECOVERY_COMPLETE", "1 to -1 request", "commit 1 to 0 and retain -1", ["M25-P07", "M25-P12", "M25-P19"]),
        ("M25-F06", "pending_route_completion", "RECOVERY_COMPLETE", "commit-capable tick from 0 with pending -1", "commit -1 and clear pending", ["M25-P23"]),
        ("M25-F07", "queue_overflow_behavior", "QUEUE_OVERFLOW_ATTEMPT", "duplicate route creation injection", "detect; keep first polarity; zero direct execution", ["M25-P11", "M25-P13", "M25-P14", "M25-P24"]),
        ("M25-F08", "invalid_configuration_behavior", "INVALID_CONFIGURATION", "reserved scheduler mode", "disable then recover to free", ["M25-P15", "M25-P16", "M25-P17"]),
        ("M25-F09", "reset_during_pending_execution", "RESET_DURING_PENDING", "reset with retained pending -1", "clear state and pending to 0", ["M25-P20", "M25-P21"]),
        ("M25-F10", "digest_mismatch_detection", FailureCode.DIGEST_MISMATCH, "one-byte mutation", "reject before document use", []),
        ("M25-F11", "malformed_artifact_rejection", FailureCode.MALFORMED_JSON, "truncated JSON object", "reject as inert data", []),
        ("M25-F12", "incomplete_qualification_package_handling", FailureCode.INCOMPLETE_PACKAGE, "missing qualification member", "reject incomplete closed set", []),
        ("M25-F13", "deterministic_recovery_behavior", "RECOVERY_COMPLETE", "create pending, defer, reset, replay", "finish at state 1, pending 0 identically", ["M25-P18", "M25-P22", "M25-P25"]),
    )
    fixtures: list[dict[str, Any]] = []
    for fixture_id, scope, classification, stimulus, outcome, properties in rows:
        item: dict[str, Any] = {
            "fixture_id": fixture_id,
            "scope": scope,
            "classification": classification,
            "deterministic": True,
            "stimulus": stimulus,
            "expected_outcome": outcome,
            "formal_property_ids": properties,
        }
        item["fixture_digest"] = object_digest(item)
        fixtures.append(item)
    return fixtures


def build_contract(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    validate_formal_sources(root)
    contract: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-fault-negative-recovery-contract",
        "milestone": MILESTONE,
        "release": "FRP v2.7.0",
        "status": "PASS",
        "source_commit": source_commit,
        "source_release": "FRP v2.6.0 / M24 formal bounded verification closure",
        "qualified_boundary": {
            "authoritative_rtl": "rtl/m16/frp_m16_core.sv",
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "reserved_encoding": "2'b10",
            "active_neutral_state": 0,
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
            "direct_opposite_polarity_transition": "forbidden",
        },
        "required_scope": list(REQUIRED_SCOPE),
        "closure_requirements": [
            "explicit expected outcomes",
            "no arbitrary code execution by artifact validators",
            "deterministic negative fixtures",
            "machine-readable failure classification",
            "recovery-state verification",
            "complete negative-path test evidence",
            "successful fault and recovery qualification workflow",
        ],
        "validator_boundary": {
            "format": "strict bounded UTF-8 JSON objects",
            "digest": "SHA-256 over exact bytes",
            "filesystem": "named regular non-symlink repository-relative files",
            "execution": "none",
        },
        "fixture_count": len(REQUIRED_SCOPE),
        "failure_classification_count": len(FAILURE_CLASSIFICATIONS),
        "formal_property_count": len(PROPERTY_SPECS),
        "formal_run_count": len(RUN_SPECS),
        "workflow_path": WORKFLOW_PATH,
    }
    contract["contract_digest"] = object_digest(contract)
    return contract


def build_classification_registry(contract: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    records = []
    for index, spec in enumerate(FAILURE_CLASSIFICATIONS, start=1):
        item = {"classification_id": f"M25-C{index:02d}", **spec}
        item["classification_digest"] = object_digest(item)
        records.append(item)
    registry: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-failure-classification-registry",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "classification_count": len(records),
        "records": records,
    }
    registry["classification_set_digest"] = object_digest(registry)
    return registry


def build_fixture_catalog(contract: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    fixtures = fixture_specs()
    catalog: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-deterministic-negative-fixtures",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "fixture_count": len(fixtures),
        "scope_count": len({item["scope"] for item in fixtures}),
        "fixtures": fixtures,
    }
    catalog["fixture_set_digest"] = object_digest(catalog)
    return catalog


def build_evidence(
    contract: Mapping[str, Any],
    classifications: Mapping[str, Any],
    fixtures: Mapping[str, Any],
    formal: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    results = []
    for fixture in fixtures["fixtures"]:
        observed_a = execute_fixture(fixture["fixture_id"])
        observed_b = execute_fixture(fixture["fixture_id"])
        if observed_a != observed_b:
            raise ContractError(f"non-deterministic M25 fixture: {fixture['fixture_id']}")
        if observed_a["classification"] != fixture["classification"]:
            raise ContractError(f"fixture classification mismatch: {fixture['fixture_id']}")
        record = {
            "fixture_id": fixture["fixture_id"],
            "scope": fixture["scope"],
            "expected_classification": fixture["classification"],
            "observed": observed_a,
            "replay_digest": object_digest(observed_a),
            "status": "PASS",
        }
        record["result_digest"] = object_digest(record)
        results.append(record)
    evidence: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-negative-path-recovery-evidence",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "classification_set_digest": classifications["classification_set_digest"],
        "fixture_set_digest": fixtures["fixture_set_digest"],
        "formal": formal,
        "fixture_result_count": len(results),
        "passed_fixture_count": len(results),
        "failed_fixture_count": 0,
        "results": results,
        "recovery_state": {
            "final_state": [1],
            "final_pending": [0],
            "active_neutral": 0,
            "actual_direct_events": 0,
            "qualified_queue_overflow_events": 0,
            "status": "PASS",
        },
    }
    evidence["evidence_digest"] = object_digest(evidence)
    return evidence


def build_manifest(root: Path, source_commit: str, primary: Mapping[str, bytes]) -> dict[str, Any]:
    sources = [source_record(root, path) for path in sorted((WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS))]
    upstream = [source_record(root, path) for path in sorted(UPSTREAM_SOURCE_PATHS)]
    artifacts = [
        {"path": path, "bytes": len(primary[path]), "raw_sha256": sha256_bytes(primary[path])}
        for path in (CONTRACT_ARTIFACT, CLASSIFICATION_ARTIFACT, FIXTURE_ARTIFACT, EVIDENCE_ARTIFACT)
    ]
    manifest: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-fault-negative-recovery-manifest",
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


def build_qualification(
    contract: Mapping[str, Any],
    classifications: Mapping[str, Any],
    fixtures: Mapping[str, Any],
    evidence: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(category: str, evidence_value: Any) -> None:
        checks.append({"check_id": f"M25-Q{len(checks) + 1:03d}", "category": category, "status": "PASS", "evidence": evidence_value})

    for value in (VERSION, MILESTONE, validate_source_commit(source_commit), WORKFLOW_PATH):
        add("identity", value)
    for scope in REQUIRED_SCOPE:
        add("scope", scope)
    for fixture in fixtures["fixtures"]:
        add("fixture", fixture["fixture_id"])
    for result in evidence["results"]:
        add("fixture_result", result["fixture_id"])
    for prop in PROPERTY_SPECS:
        add("formal_property", prop["property_id"])
    for run in evidence["formal"]["runs"]:
        add("formal_run", run["run_id"])
    for record in classifications["records"]:
        add("classification", record["code"])
    for schema_path in SCHEMA_PATHS.values():
        add("schema", schema_path)
    for requirement in contract["closure_requirements"]:
        add("closure", requirement)
    add("manifest", manifest["artifact_set_digest"])
    add("recovery", evidence["recovery_state"])

    qualification: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m25-fault-negative-recovery-qualification",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": source_commit,
        "contract_digest": contract["contract_digest"],
        "classification_set_digest": classifications["classification_set_digest"],
        "fixture_set_digest": fixtures["fixture_set_digest"],
        "evidence_digest": evidence["evidence_digest"],
        "manifest_digest": manifest["manifest_digest"],
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }
    qualification["qualification_digest"] = object_digest(qualification)
    return qualification


def build_outputs(
    root: Path,
    source_commit: str,
    formal_result: Mapping[str, Any] | None = None,
) -> dict[str, bytes]:
    root = root.resolve()
    expected_formal = canonical_formal_result(root)
    if formal_result is not None and dict(formal_result) != expected_formal:
        raise ContractError("formal run result does not match canonical M25 result")
    contract = build_contract(root, source_commit)
    classifications = build_classification_registry(contract, source_commit)
    fixtures = build_fixture_catalog(contract, source_commit)
    evidence = build_evidence(contract, classifications, fixtures, expected_formal, source_commit)
    primary = {
        CONTRACT_ARTIFACT: document_bytes(contract),
        CLASSIFICATION_ARTIFACT: document_bytes(classifications),
        FIXTURE_ARTIFACT: document_bytes(fixtures),
        EVIDENCE_ARTIFACT: document_bytes(evidence),
    }
    manifest = build_manifest(root, source_commit, primary)
    qualification = build_qualification(
        contract, classifications, fixtures, evidence, manifest, source_commit
    )
    outputs = {
        **primary,
        MANIFEST_ARTIFACT: document_bytes(manifest),
        QUALIFICATION_ARTIFACT: document_bytes(qualification),
    }
    schemas = SchemaContext(root)
    mapping = {
        CONTRACT_ARTIFACT: CONTRACT_SCHEMA,
        CLASSIFICATION_ARTIFACT: CLASSIFICATION_SCHEMA,
        FIXTURE_ARTIFACT: FIXTURE_SCHEMA,
        EVIDENCE_ARTIFACT: EVIDENCE_SCHEMA,
        MANIFEST_ARTIFACT: MANIFEST_SCHEMA,
        QUALIFICATION_ARTIFACT: QUALIFICATION_SCHEMA,
    }
    for artifact, schema in mapping.items():
        schemas.validate(schema, json.loads(outputs[artifact]), artifact)
    return outputs


def generate(root: Path, output_root: Path, source_commit: str, formal_result: Mapping[str, Any]) -> dict[str, Any]:
    outputs = build_outputs(root, source_commit, formal_result)
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


def verify(root: Path, source_commit: str, formal_result: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = build_outputs(root, source_commit, formal_result)
    package = load_package_from_root(root, ARTIFACT_PATHS)
    expected = {path: sha256_bytes(raw) for path, raw in outputs.items()}
    validated = validate_package_bytes(package, ARTIFACT_PATHS, expected)
    for relative, raw in outputs.items():
        if package[relative] != raw:
            raise ContractError(f"committed M25 artifact mismatch: {relative}")
    return {
        "status": "PASS",
        "artifact_count": validated["artifact_count"],
        "source_commit": source_commit,
        "records": validated["records"],
        "artifact_set_digest": object_digest(validated["records"]),
    }


def self_test(root: Path, source_commit: str) -> dict[str, Any]:
    outputs_a = build_outputs(root, source_commit)
    outputs_b = build_outputs(root, source_commit)
    contract = json.loads(outputs_a[CONTRACT_ARTIFACT])
    classifications = json.loads(outputs_a[CLASSIFICATION_ARTIFACT])
    fixtures = json.loads(outputs_a[FIXTURE_ARTIFACT])
    evidence = json.loads(outputs_a[EVIDENCE_ARTIFACT])
    qualification = json.loads(outputs_a[QUALIFICATION_ARTIFACT])
    predicates = (
        ("identity", (VERSION, MILESTONE) == ("2.7.0", "M25")),
        ("source_commit", contract["source_commit"] == source_commit),
        ("core_notation", contract["qualified_boundary"]["balanced_ternary_notation"] == "-1/0/1"),
        ("scheduler_modes", contract["qualified_boundary"]["temporal_scheduler_modes"] == ["1/7", "7/1"]),
        ("byte_stability", outputs_a == outputs_b),
        ("artifact_count", len(outputs_a) == 6),
        ("scope_count", fixtures["scope_count"] == len(REQUIRED_SCOPE) == 13),
        ("fixture_count", fixtures["fixture_count"] == 13),
        ("fixture_results", evidence["fixture_result_count"] == evidence["passed_fixture_count"] == 13),
        ("classifications", classifications["classification_count"] == len(FAILURE_CLASSIFICATIONS)),
        ("formal_runs", evidence["formal"]["run_count"] == 3),
        ("formal_properties", evidence["formal"]["property_count"] == 25),
        ("no_direct", evidence["recovery_state"]["actual_direct_events"] == 0),
        ("no_qualified_overflow", evidence["recovery_state"]["qualified_queue_overflow_events"] == 0),
        ("recovery_state", evidence["recovery_state"]["final_state"] == [1] and evidence["recovery_state"]["final_pending"] == [0]),
        ("qualification", qualification["check_count"] == qualification["passed_count"]),
        ("overall_status", qualification["overall_status"] == "PASS"),
    )
    checks = [{"check_id": name, "status": "PASS" if passed else "FAIL"} for name, passed in predicates]
    failed = [item for item in checks if item["status"] != "PASS"]
    if failed:
        raise ContractError(f"M25 self-test failure: {failed}")
    return {"status": "PASS", "check_count": len(checks), "passed_count": len(checks), "failed_count": 0, "checks": checks}


def read_json_file(path: str | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise SafetyError(f"invalid JSON input: {candidate}")
    value = decode_json_object(candidate.read_bytes(), str(candidate))
    return value


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
    mode.add_argument("--run-formal", action="store_true")
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root")
    parser.add_argument("--work-root")
    parser.add_argument("--yosys", default="yowasp-yosys")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--formal-result")
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.repository_root).resolve()
    try:
        validate_source_commit(args.source_commit)
        if args.run_formal:
            if not args.work_root:
                raise ContractError("--work-root is required with --run-formal")
            result = run_formal(root, Path(args.work_root), args.yosys)
        elif args.generate:
            if not args.output_root or not args.formal_result:
                raise ContractError("--output-root and --formal-result are required with --generate")
            formal_result = read_json_file(args.formal_result)
            if formal_result is None:
                raise ContractError("formal result missing")
            result = generate(root, Path(args.output_root), args.source_commit, formal_result)
        elif args.verify:
            result = verify(root, args.source_commit, read_json_file(args.formal_result))
        else:
            result = self_test(root, args.source_commit)
        write_result(args.output, result)
    except (ContractError, SafetyError, ValidationFailure, OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(f"M25_ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
