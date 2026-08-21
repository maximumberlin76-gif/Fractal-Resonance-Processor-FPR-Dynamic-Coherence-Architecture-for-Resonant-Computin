#!/usr/bin/env python3
"""Generate and verify FRP M26 declared-target implementation evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator


VERSION = "2.8.0"
MILESTONE = "M26"
EXPECTED_M25_COMMIT = "d83e23785d292adaaf419c31e51abb294ddf98f9"
WORKFLOW_PATH = ".github/workflows/frp-m26-declared-target-implementation-evidence-workflow.yml"

TARGET_TOP = "frp_m26_declared_target_top"
TARGET_TOP_PATH = "rtl/m26/frp_m26_declared_target_top.sv"
SYNTHESIS_STUB_PATH = "rtl/m26/frp_m26_protocol_monitor_synthesis_stub.sv"
CONSTRAINT_PATH = "constraints/m26/frp_m26_ice40_hx8k_ct256.sdc"

CONTRACT_ARTIFACT = "artifacts/m26/contracts/m26-declared-target-implementation-contract.json"
PROVENANCE_ARTIFACT = "artifacts/m26/provenance/m26-tool-command-provenance.json"
REPORT_ARTIFACT = "artifacts/m26/reports/m26-declared-target-implementation-report.json"
REPRODUCIBILITY_ARTIFACT = "artifacts/m26/reproducibility/m26-reproducibility-record.json"
MANIFEST_ARTIFACT = "artifacts/m26/manifests/m26-declared-target-implementation-manifest.json"
QUALIFICATION_ARTIFACT = "artifacts/m26/manifests/m26-declared-target-implementation-qualification.json"

CONTRACT_SCHEMA = "schemas/m26/frp_m26_declared_target_implementation_contract.v2.8.0.schema.json"
PROVENANCE_SCHEMA = "schemas/m26/frp_m26_tool_command_provenance.v2.8.0.schema.json"
REPORT_SCHEMA = "schemas/m26/frp_m26_declared_target_implementation_report.v2.8.0.schema.json"
REPRODUCIBILITY_SCHEMA = "schemas/m26/frp_m26_reproducibility_record.v2.8.0.schema.json"
MANIFEST_SCHEMA = "schemas/m26/frp_m26_declared_target_implementation_manifest.v2.8.0.schema.json"
QUALIFICATION_SCHEMA = "schemas/m26/frp_m26_declared_target_implementation_qualification.v2.8.0.schema.json"
REGISTRY_PATH = "schemas/m26/frp_m26_schema_registry.json"

SCHEMA_PATHS = {
    "m26-declared-target-implementation-contract-v2.8.0": CONTRACT_SCHEMA,
    "m26-tool-command-provenance-v2.8.0": PROVENANCE_SCHEMA,
    "m26-declared-target-implementation-report-v2.8.0": REPORT_SCHEMA,
    "m26-reproducibility-record-v2.8.0": REPRODUCIBILITY_SCHEMA,
    "m26-declared-target-implementation-manifest-v2.8.0": MANIFEST_SCHEMA,
    "m26-declared-target-implementation-qualification-v2.8.0": QUALIFICATION_SCHEMA,
}

ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    PROVENANCE_ARTIFACT,
    REPORT_ARTIFACT,
    REPRODUCIBILITY_ARTIFACT,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

M16_PATHS = (
    "rtl/m16/frp_m16_pkg.sv",
    "rtl/m16/frp_m16_scheduler.sv",
    "rtl/m16/frp_m16_request_lanes.sv",
    "rtl/m16/frp_m16_pending_routes.sv",
    "rtl/m16/frp_m16_active_neutral.sv",
    "rtl/m16/frp_m16_capacity_guard.sv",
    "rtl/m16/frp_m16_state_update.sv",
    "rtl/m16/frp_m16_core.sv",
)

M22_PATHS = (
    "rtl/m22/frp_m22_csr_pkg.sv",
    "rtl/m22/frp_m22_control_status_register_interface.sv",
)

M23_PATHS = (
    "rtl/m23/frp_m23_reset_release_sync.sv",
    "rtl/m23/frp_m23_csr_cdc_bridge.sv",
    "rtl/m23/frp_m23_interface_protocol_assertions.sv",
    "rtl/m23/frp_m23_hardened_integration_boundary.sv",
)

IMPLEMENTATION_SOURCE_PATHS = (
    *M16_PATHS,
    *M22_PATHS,
    *M23_PATHS,
    SYNTHESIS_STUB_PATH,
    TARGET_TOP_PATH,
    CONSTRAINT_PATH,
)

TECHNICAL_SOURCE_PATHS = (
    "frp_m26_declared_target_implementation_evidence.py",
    SYNTHESIS_STUB_PATH,
    TARGET_TOP_PATH,
    CONSTRAINT_PATH,
    *SCHEMA_PATHS.values(),
    REGISTRY_PATH,
    "tests/test_frp_m26_declared_target_implementation_evidence.py",
)

UPSTREAM_SOURCE_PATHS = (
    *M16_PATHS,
    *M22_PATHS,
    *M23_PATHS,
    "artifacts/m25/contracts/m25-fault-negative-recovery-contract.json",
    "artifacts/m25/evidence/m25-negative-path-recovery-evidence.json",
    "artifacts/m25/manifests/m25-fault-negative-recovery-manifest.json",
    "artifacts/m25/manifests/m25-fault-negative-recovery-qualification.json",
)

YOSYS_PACKAGE = "yowasp-yosys"
YOSYS_PACKAGE_VERSION = "0.68.0.0.post1208"
YOSYS_ENGINE_VERSION = "0.68"
YOSYS_GIT_SHA = "38e001a6f"
NEXTPNR_PACKAGE = "yowasp-nextpnr-ice40"
NEXTPNR_PACKAGE_VERSION = "0.11.1.0.post826"
NEXTPNR_ENGINE_VERSION = "nextpnr-0.11.1"

TARGET_ID = "ice40-hx8k-ct256-cells8"
TARGET_FAMILY = "Lattice iCE40 HX"
TARGET_DEVICE = "iCE40HX8K"
TARGET_PACKAGE = "CT256"
TARGET_CELLS = 8
TARGET_REQUEST_LANES = 2
HOST_CLOCK_MHZ = 10
CORE_CLOCK_MHZ = 8
HOST_PERIOD_NS = 100.0
CORE_PERIOD_NS = 125.0
SEED = 26

RAW_OUTPUT_NAMES = (
    "design.json",
    "stat.json",
    "design.asc",
    "routed.json",
    "nextpnr_report.json",
)

EXPECTED_SYNTHESIS = {
    "num_ports": 18,
    "num_port_bits": 87,
    "num_cells": 2164,
    "SB_CARRY": 291,
    "SB_DFFER": 269,
    "SB_DFFR": 215,
    "SB_LUT4": 1389,
}

EXPECTED_UTILIZATION = {
    "ICESTORM_LC": {"used": 1693, "available": 7680},
    "ICESTORM_RAM": {"used": 0, "available": 32},
    "SB_IO": {"used": 87, "available": 206},
    "SB_GB": {"used": 7, "available": 8},
    "ICESTORM_PLL": {"used": 0, "available": 2},
    "SB_WARMBOOT": {"used": 0, "available": 1},
}

EXPECTED_WARNING = "Warning: No PCF file specified; IO pins will be placed automatically"

REQUIRED_SCOPE = (
    "declared_implementation_target",
    "declared_tool_and_version",
    "declared_constraints",
    "synthesis_command_provenance",
    "timing_command_provenance",
    "resource_report_provenance",
    "implementation_warnings",
    "result_digests",
    "reproducibility_records",
    "target_independent_fpga_preparation_separation",
    "physical_measurement_separation",
)


class ContractError(ValueError):
    """Raised when an M26 contract or evidence invariant is violated."""


class SafetyError(ValueError):
    """Raised when an M26 filesystem boundary is unsafe."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise SafetyError(f"unsafe repository-relative path: {value!r}")
    return path


def path_for(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative_path(relative).parts)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def document_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def raw_digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def validate_source_commit(value: str) -> str:
    if value != EXPECTED_M25_COMMIT:
        raise ContractError(f"unexpected M25 source commit: {value}")
    return value


def require_file(root: Path, relative: str) -> Path:
    target = path_for(root, relative)
    if target.is_symlink() or not target.is_file():
        raise ContractError(f"required source missing: {relative}")
    return target


def source_record(root: Path, relative: str) -> dict[str, Any]:
    raw = require_file(root, relative).read_bytes()
    return {"path": relative, "bytes": len(raw), "raw_sha256": raw_digest(raw)}


def file_record(path: Path, output_id: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContractError(f"implementation output missing: {path}")
    raw = path.read_bytes()
    return {"output_id": output_id, "bytes": len(raw), "raw_sha256": raw_digest(raw)}


class SchemaContext:
    """Load and validate the closed M26 Draft 2020-12 schema set."""

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


def yosys_script(run_id: str) -> str:
    run_dir = run_id.lower()
    commands = [
        "read_slang -j 1 --ignore-assertions --ignore-initial "
        f"--top {TARGET_TOP} -I rtl/m16 -I rtl/m22 -I rtl/m23 -I rtl/m26 {TARGET_TOP_PATH}",
        f"hierarchy -check -top {TARGET_TOP}",
        f"synth_ice40 -top {TARGET_TOP} -json {run_dir}/design.json",
        f"tee -o {run_dir}/stat.json stat -json",
    ]
    return "; ".join(commands)


def yosys_argv(run_id: str, executable: str = "yowasp-yosys") -> list[str]:
    run_dir = run_id.lower()
    return [executable, "-ql", f"{run_dir}/yosys.log", "-p", yosys_script(run_id)]


def nextpnr_argv(run_id: str, executable: str = "yowasp-nextpnr-ice40") -> list[str]:
    run_dir = run_id.lower()
    return [
        executable,
        "--hx8k",
        "--package",
        "ct256",
        "--json",
        f"{run_dir}/design.json",
        "--asc",
        f"{run_dir}/design.asc",
        "--write",
        f"{run_dir}/routed.json",
        "--report",
        f"{run_dir}/nextpnr_report.json",
        "--sdc",
        CONSTRAINT_PATH,
        "--pcf-allow-unconstrained",
        "--seed",
        str(SEED),
        "--threads",
        "1",
        "--placer",
        "heap",
        "--router",
        "router1",
        "--ignore-rel-clk",
        "--log",
        f"{run_dir}/nextpnr.log",
    ]


def _check_work_root(repository_root: Path, work_root: Path) -> None:
    resolved = work_root.resolve()
    forbidden = {Path("/").resolve(), Path.home().resolve(), repository_root.resolve()}
    if resolved in forbidden or len(resolved.parts) < 3:
        raise SafetyError(f"unsafe M26 work root: {resolved}")
    if work_root.is_symlink():
        raise SafetyError(f"M26 work root is a symlink: {work_root}")


def prepare_work_root(repository_root: Path, work_root: Path) -> None:
    _check_work_root(repository_root, work_root)
    if work_root.exists():
        if not work_root.is_dir():
            raise SafetyError(f"M26 work root is not a directory: {work_root}")
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True, mode=0o700)
    for relative in IMPLEMENTATION_SOURCE_PATHS:
        source = require_file(repository_root, relative)
        destination = path_for(work_root, relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())


def _run_command(argv: Sequence[str], cwd: Path, label: str, timeout: int) -> str:
    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
        env={**os.environ, "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8", "TZ": "UTC"},
    )
    if completed.returncode != 0:
        tail = "\n".join(completed.stdout.splitlines()[-80:])
        raise ContractError(f"{label} failed with exit {completed.returncode}:\n{tail}")
    return completed.stdout


def _probe_toolchain(yosys: str, nextpnr: str) -> dict[str, Any]:
    yosys_executable = shutil.which(yosys)
    nextpnr_executable = shutil.which(nextpnr)
    if yosys_executable is None:
        raise ContractError(f"Yosys executable not found: {yosys}")
    if nextpnr_executable is None:
        raise ContractError(f"nextpnr executable not found: {nextpnr}")

    yosys_package = importlib.metadata.version(YOSYS_PACKAGE)
    nextpnr_package = importlib.metadata.version(NEXTPNR_PACKAGE)
    if yosys_package != YOSYS_PACKAGE_VERSION:
        raise ContractError(f"unexpected Yosys package version: {yosys_package}")
    if nextpnr_package != NEXTPNR_PACKAGE_VERSION:
        raise ContractError(f"unexpected nextpnr package version: {nextpnr_package}")

    yosys_version = _run_command([yosys_executable, "-V"], Path.cwd(), "Yosys version probe", 120).strip()
    nextpnr_version = _run_command([nextpnr_executable, "--version"], Path.cwd(), "nextpnr version probe", 120).strip()
    if f"Yosys {YOSYS_ENGINE_VERSION}" not in yosys_version or YOSYS_GIT_SHA not in yosys_version:
        raise ContractError(f"unexpected Yosys engine provenance: {yosys_version}")
    if NEXTPNR_ENGINE_VERSION not in nextpnr_version:
        raise ContractError(f"unexpected nextpnr engine provenance: {nextpnr_version}")

    return {
        "yosys": {
            "package": YOSYS_PACKAGE,
            "package_version": yosys_package,
            "engine": "Yosys",
            "engine_version": YOSYS_ENGINE_VERSION,
            "engine_git_sha": YOSYS_GIT_SHA,
            "version_output": yosys_version,
        },
        "nextpnr": {
            "package": NEXTPNR_PACKAGE,
            "package_version": nextpnr_package,
            "engine": "nextpnr-ice40",
            "engine_version": NEXTPNR_ENGINE_VERSION,
            "version_output": nextpnr_version,
        },
    }


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid {label}: {exc}") from None
    if not isinstance(value, dict):
        raise ContractError(f"{label} is not a JSON object")
    return value


def _synthesis_summary(stat: Mapping[str, Any]) -> dict[str, Any]:
    modules = stat.get("modules")
    if not isinstance(modules, dict) or len(modules) != 1:
        raise ContractError("unexpected Yosys module statistics")
    module = next(iter(modules.values()))
    if not isinstance(module, dict):
        raise ContractError("invalid Yosys module statistics")
    by_type = module.get("num_cells_by_type")
    if not isinstance(by_type, dict):
        raise ContractError("missing Yosys cell-type statistics")
    summary = {
        "num_ports": module.get("num_ports"),
        "num_port_bits": module.get("num_port_bits"),
        "num_cells": module.get("num_cells"),
        "cell_types": {name: by_type.get(name, 0) for name in ("SB_CARRY", "SB_DFFER", "SB_DFFR", "SB_LUT4")},
    }
    flattened = {**{key: summary[key] for key in ("num_ports", "num_port_bits", "num_cells")}, **summary["cell_types"]}
    if flattened != EXPECTED_SYNTHESIS:
        raise ContractError(f"unexpected synthesis result: {flattened}")
    return summary


def _clock_record(name: str, value: Mapping[str, Any], expected_mhz: int) -> dict[str, Any]:
    achieved = value.get("achieved")
    constraint = value.get("constraint")
    if not isinstance(achieved, (int, float)) or not isinstance(constraint, (int, float)):
        raise ContractError(f"invalid nextpnr clock record: {name}")
    if float(constraint) != float(expected_mhz) or float(achieved) < float(constraint):
        raise ContractError(f"timing constraint failed for {name}: {value}")
    return {
        "clock": name,
        "constraint_mhz": constraint,
        "achieved_mhz": achieved,
        "margin_mhz": achieved - constraint,
        "status": "PASS",
    }


def _nextpnr_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    utilization = report.get("utilization")
    fmax = report.get("fmax")
    if not isinstance(utilization, dict) or not isinstance(fmax, dict):
        raise ContractError("invalid nextpnr report structure")
    observed_utilization = {
        name: {"used": value.get("used"), "available": value.get("available")}
        for name, value in utilization.items()
        if isinstance(value, dict)
    }
    if observed_utilization != EXPECTED_UTILIZATION:
        raise ContractError(f"unexpected target utilization: {observed_utilization}")

    host = next((value for key, value in fmax.items() if key.startswith("host_clk")), None)
    core = next((value for key, value in fmax.items() if key.startswith("core_clk")), None)
    if not isinstance(host, dict) or not isinstance(core, dict):
        raise ContractError("declared clocks missing from nextpnr report")
    clocks = [
        _clock_record("host_clk", host, HOST_CLOCK_MHZ),
        _clock_record("core_clk", core, CORE_CLOCK_MHZ),
    ]
    return {"utilization": observed_utilization, "clocks": clocks, "timing_status": "PASS"}


def _warning_summary(yosys_log: str, nextpnr_log: str) -> dict[str, Any]:
    warnings = [
        line.strip()
        for line in (yosys_log + "\n" + nextpnr_log).splitlines()
        if line.startswith("Warning:")
    ]
    errors = [
        line.strip()
        for line in (yosys_log + "\n" + nextpnr_log).splitlines()
        if re.match(r"^(?:ERROR|Error):", line)
    ]
    if warnings != [EXPECTED_WARNING] or errors:
        raise ContractError(f"unexpected implementation diagnostics: warnings={warnings}, errors={errors}")
    return {
        "warning_count": 1,
        "error_count": 0,
        "warnings": [
            {
                "code": "M26-W01-UNBOUND-BOARD-PINOUT",
                "severity": "warning",
                "message": EXPECTED_WARNING,
                "classification": "declared_target_package_with_unbound_board_pinout",
                "retained": True,
            }
        ],
    }


def _run_one(work_root: Path, run_id: str, yosys_executable: str, nextpnr_executable: str) -> dict[str, Any]:
    run_dir = work_root / run_id.lower()
    run_dir.mkdir(parents=True, exist_ok=False)
    yargv = yosys_argv(run_id, yosys_executable)
    nargv = nextpnr_argv(run_id, nextpnr_executable)
    _run_command(yargv, work_root, f"{run_id} synthesis", 600)
    _run_command(nargv, work_root, f"{run_id} place-and-route", 600)

    stat = _read_json_object(run_dir / "stat.json", f"{run_id} Yosys statistics")
    report = _read_json_object(run_dir / "nextpnr_report.json", f"{run_id} nextpnr report")
    yosys_log = (run_dir / "yosys.log").read_text(encoding="utf-8")
    nextpnr_log = (run_dir / "nextpnr.log").read_text(encoding="utf-8")
    raw_outputs = [file_record(run_dir / name, name) for name in RAW_OUTPUT_NAMES]
    result = {
        "run_id": run_id,
        "status": "PASS",
        "seed": SEED,
        "synthesis": _synthesis_summary(stat),
        "implementation": _nextpnr_summary(report),
        "diagnostics": _warning_summary(yosys_log, nextpnr_log),
        "raw_output_count": len(raw_outputs),
        "raw_outputs": raw_outputs,
    }
    result["run_digest"] = object_digest(result)
    return result


def run_implementation(
    repository_root: Path,
    work_root: Path,
    yosys: str,
    nextpnr: str,
    source_commit: str,
) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    work_root = work_root.resolve()
    validate_source_commit(source_commit)
    for relative in IMPLEMENTATION_SOURCE_PATHS:
        require_file(repository_root, relative)
    toolchain = _probe_toolchain(yosys, nextpnr)
    prepare_work_root(repository_root, work_root)
    yosys_executable = shutil.which(yosys)
    nextpnr_executable = shutil.which(nextpnr)
    assert yosys_executable is not None and nextpnr_executable is not None

    runs = [
        _run_one(work_root, "RUN_A", yosys_executable, nextpnr_executable),
        _run_one(work_root, "RUN_B", yosys_executable, nextpnr_executable),
    ]
    a_outputs = {item["output_id"]: item for item in runs[0]["raw_outputs"]}
    b_outputs = {item["output_id"]: item for item in runs[1]["raw_outputs"]}
    compared = []
    for output_id in RAW_OUTPUT_NAMES:
        a = a_outputs[output_id]
        b = b_outputs[output_id]
        match = a["bytes"] == b["bytes"] and a["raw_sha256"] == b["raw_sha256"]
        if not match:
            raise ContractError(f"non-reproducible implementation output: {output_id}")
        compared.append({
            "output_id": output_id,
            "run_a_bytes": a["bytes"],
            "run_b_bytes": b["bytes"],
            "run_a_sha256": a["raw_sha256"],
            "run_b_sha256": b["raw_sha256"],
            "byte_identical": True,
        })
    if runs[0]["synthesis"] != runs[1]["synthesis"] or runs[0]["implementation"] != runs[1]["implementation"]:
        raise ContractError("non-reproducible canonical implementation metrics")

    result = {
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "toolchain": toolchain,
        "target": {
            "target_id": TARGET_ID,
            "family": TARGET_FAMILY,
            "device": TARGET_DEVICE,
            "package": TARGET_PACKAGE,
            "top_module": TARGET_TOP,
            "cells": TARGET_CELLS,
            "request_lanes": TARGET_REQUEST_LANES,
        },
        "constraints": {
            "sdc_path": CONSTRAINT_PATH,
            "host_clock_mhz": HOST_CLOCK_MHZ,
            "host_period_ns": HOST_PERIOD_NS,
            "core_clock_mhz": CORE_CLOCK_MHZ,
            "core_period_ns": CORE_PERIOD_NS,
            "board_pinout": "unbound",
            "io_placement": "automatic_with_explicit_warning",
            "inter_clock_timing_policy": "ignore_rel_clk_for_declared_asynchronous_cdc",
        },
        "run_count": 2,
        "runs": runs,
        "reproducibility": {
            "status": "PASS",
            "seed": SEED,
            "single_threaded": True,
            "compared_output_count": len(compared),
            "matching_output_count": len(compared),
            "mismatching_output_count": 0,
            "outputs": compared,
        },
    }
    result["implementation_result_digest"] = object_digest(result)
    return result


def validate_implementation_result(value: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    result = dict(value)
    digest = result.pop("implementation_result_digest", None)
    if digest != object_digest(result):
        raise ContractError("implementation result digest mismatch")
    result["implementation_result_digest"] = digest
    if result.get("status") != "PASS" or result.get("source_commit") != validate_source_commit(source_commit):
        raise ContractError("implementation result identity mismatch")
    if result.get("run_count") != 2 or len(result.get("runs", [])) != 2:
        raise ContractError("implementation result run count mismatch")
    if result.get("target", {}).get("target_id") != TARGET_ID:
        raise ContractError("implementation target mismatch")
    if result.get("reproducibility", {}).get("status") != "PASS":
        raise ContractError("implementation reproducibility did not pass")
    return result


def build_contract(root: Path, source_commit: str) -> dict[str, Any]:
    contract = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-declared-target-implementation-contract",
        "milestone": MILESTONE,
        "release": "FRP v2.8.0",
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "required_scope": list(REQUIRED_SCOPE),
        "immutable_core": {
            "authoritative_rtl": "rtl/m16/frp_m16_core.sv",
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
        },
        "declared_target": {
            "target_id": TARGET_ID,
            "family": TARGET_FAMILY,
            "device": TARGET_DEVICE,
            "package": TARGET_PACKAGE,
            "top_module": TARGET_TOP,
            "top_source": TARGET_TOP_PATH,
            "cells": TARGET_CELLS,
            "request_lanes": TARGET_REQUEST_LANES,
        },
        "declared_constraints": {
            "sdc_path": CONSTRAINT_PATH,
            "host_clock_mhz": HOST_CLOCK_MHZ,
            "host_period_ns": HOST_PERIOD_NS,
            "core_clock_mhz": CORE_CLOCK_MHZ,
            "core_period_ns": CORE_PERIOD_NS,
            "board_pinout": "unbound",
            "io_placement": "automatic_with_explicit_warning",
        },
        "evidence_boundary": {
            "evidence_type": "reproducible_tool_derived_declared_target_implementation",
            "target_independent_fpga_preparation": "separate_m16_layer",
            "physical_measurement_status": "not_a_physical_measurement",
            "universal_physical_chip_claim": "not_made",
            "board_ready_pinout_claim": "not_made",
            "proxy_to_physical_conversion": "prohibited",
            "protocol_monitor_policy": "nonfunctional_assertion_monitor_replaced_by_synthesis_stub",
            "implementation_warnings_retained": True,
        },
        "workflow_path": WORKFLOW_PATH,
        "source_set_digest": object_digest([source_record(root, path) for path in IMPLEMENTATION_SOURCE_PATHS]),
    }
    contract["contract_digest"] = object_digest(contract)
    return contract


def build_provenance(root: Path, contract: Mapping[str, Any], implementation: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    sources = [source_record(root, path) for path in IMPLEMENTATION_SOURCE_PATHS]
    provenance = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-tool-command-provenance",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "toolchain": implementation["toolchain"],
        "target_id": TARGET_ID,
        "constraint_record": source_record(root, CONSTRAINT_PATH),
        "source_count": len(sources),
        "sources": sources,
        "commands": [
            {
                "command_id": f"M26-CMD-{index:02d}-YOSYS",
                "stage": "synthesis",
                "run_id": run_id,
                "argv": yosys_argv(run_id),
            }
            for index, run_id in enumerate(("RUN_A", "RUN_B"), start=1)
        ] + [
            {
                "command_id": f"M26-CMD-{index + 2:02d}-NEXTPNR",
                "stage": "place_route_timing_resource",
                "run_id": run_id,
                "argv": nextpnr_argv(run_id),
            }
            for index, run_id in enumerate(("RUN_A", "RUN_B"), start=1)
        ],
        "determinism_controls": {
            "seed": SEED,
            "threads": 1,
            "python_hash_seed": 0,
            "locale": "C.UTF-8",
            "timezone": "UTC",
        },
    }
    provenance["provenance_digest"] = object_digest(provenance)
    return provenance


def build_report(contract: Mapping[str, Any], provenance: Mapping[str, Any], implementation: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    run_a = implementation["runs"][0]
    report = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-declared-target-implementation-report",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "provenance_digest": provenance["provenance_digest"],
        "target_id": TARGET_ID,
        "synthesis": run_a["synthesis"],
        "implementation": run_a["implementation"],
        "diagnostics": run_a["diagnostics"],
        "raw_outputs": run_a["raw_outputs"],
        "implementation_result": implementation,
        "evidence_classification": {
            "implementation_tool_evidence": True,
            "timing_values_are_tool_derived": True,
            "resource_values_are_tool_derived": True,
            "physical_measurements": False,
            "board_pinout_bound": False,
            "universal_chip_claim": False,
        },
    }
    report["report_digest"] = object_digest(report)
    return report


def build_reproducibility(contract: Mapping[str, Any], provenance: Mapping[str, Any], report: Mapping[str, Any], implementation: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    reproducibility = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-reproducibility-record",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "provenance_digest": provenance["provenance_digest"],
        "report_digest": report["report_digest"],
        **implementation["reproducibility"],
        "run_a_digest": implementation["runs"][0]["run_digest"],
        "run_b_digest": implementation["runs"][1]["run_digest"],
        "canonical_metrics_identical": (
            implementation["runs"][0]["synthesis"] == implementation["runs"][1]["synthesis"]
            and implementation["runs"][0]["implementation"] == implementation["runs"][1]["implementation"]
        ),
    }
    reproducibility["reproducibility_digest"] = object_digest(reproducibility)
    return reproducibility


def build_manifest(root: Path, source_commit: str, primary: Mapping[str, bytes]) -> dict[str, Any]:
    sources = [source_record(root, path) for path in sorted((WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS))]
    upstream = [source_record(root, path) for path in sorted(UPSTREAM_SOURCE_PATHS)]
    artifacts = [
        {"path": path, "bytes": len(primary[path]), "raw_sha256": raw_digest(primary[path])}
        for path in (CONTRACT_ARTIFACT, PROVENANCE_ARTIFACT, REPORT_ARTIFACT, REPRODUCIBILITY_ARTIFACT)
    ]
    manifest = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-declared-target-implementation-manifest",
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


def _qualification_checks(
    contract: Mapping[str, Any],
    provenance: Mapping[str, Any],
    report: Mapping[str, Any],
    reproducibility: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(category: str, evidence: Any) -> None:
        checks.append({
            "check_id": f"M26-Q{len(checks) + 1:03d}",
            "category": category,
            "status": "PASS",
            "evidence": evidence,
        })

    add("identity", contract["release"])
    add("identity", contract["source_commit"])
    for item in contract["required_scope"]:
        add("scope", item)
    for key, value in contract["declared_target"].items():
        add("target", {key: value})
    for key, value in contract["declared_constraints"].items():
        add("constraint", {key: value})
    for key, value in report["synthesis"].items():
        add("synthesis", {key: value})
    for name, value in report["implementation"]["utilization"].items():
        add("resource", {name: value})
    for value in report["implementation"]["clocks"]:
        add("timing", value)
    for key, value in report["diagnostics"].items():
        add("warning", {key: value})
    for output in reproducibility["outputs"]:
        add("reproducibility", output)
    for tool, value in provenance["toolchain"].items():
        add("tool", {tool: value})
    for command in provenance["commands"]:
        add("command", command["command_id"])
    for key, value in contract["evidence_boundary"].items():
        add("boundary", {key: value})
    for schema_id in SCHEMA_PATHS:
        add("schema", schema_id)
    add("manifest", manifest["manifest_digest"])
    add("closure", "declared-target implementation evidence is reproducible and closed")
    return checks


def build_qualification(
    contract: Mapping[str, Any],
    provenance: Mapping[str, Any],
    report: Mapping[str, Any],
    reproducibility: Mapping[str, Any],
    manifest: Mapping[str, Any],
    source_commit: str,
) -> dict[str, Any]:
    checks = _qualification_checks(contract, provenance, report, reproducibility, manifest)
    qualification = {
        "schema_version": VERSION,
        "artifact_id": "frp-m26-declared-target-implementation-qualification",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "provenance_digest": provenance["provenance_digest"],
        "report_digest": report["report_digest"],
        "reproducibility_digest": reproducibility["reproducibility_digest"],
        "manifest_digest": manifest["manifest_digest"],
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }
    qualification["qualification_digest"] = object_digest(qualification)
    return qualification


def build_outputs(root: Path, implementation_value: Mapping[str, Any], source_commit: str) -> dict[str, bytes]:
    root = root.resolve()
    implementation = validate_implementation_result(implementation_value, source_commit)
    contract = build_contract(root, source_commit)
    provenance = build_provenance(root, contract, implementation, source_commit)
    report = build_report(contract, provenance, implementation, source_commit)
    reproducibility = build_reproducibility(contract, provenance, report, implementation, source_commit)
    primary = {
        CONTRACT_ARTIFACT: document_bytes(contract),
        PROVENANCE_ARTIFACT: document_bytes(provenance),
        REPORT_ARTIFACT: document_bytes(report),
        REPRODUCIBILITY_ARTIFACT: document_bytes(reproducibility),
    }
    manifest = build_manifest(root, source_commit, primary)
    qualification = build_qualification(contract, provenance, report, reproducibility, manifest, source_commit)
    outputs = {
        **primary,
        MANIFEST_ARTIFACT: document_bytes(manifest),
        QUALIFICATION_ARTIFACT: document_bytes(qualification),
    }
    schemas = SchemaContext(root)
    mapping = {
        CONTRACT_ARTIFACT: CONTRACT_SCHEMA,
        PROVENANCE_ARTIFACT: PROVENANCE_SCHEMA,
        REPORT_ARTIFACT: REPORT_SCHEMA,
        REPRODUCIBILITY_ARTIFACT: REPRODUCIBILITY_SCHEMA,
        MANIFEST_ARTIFACT: MANIFEST_SCHEMA,
        QUALIFICATION_ARTIFACT: QUALIFICATION_SCHEMA,
    }
    for artifact, schema in mapping.items():
        schemas.validate(schema, json.loads(outputs[artifact]), artifact)
    return outputs


def write_outputs(output_root: Path, outputs: Mapping[str, bytes]) -> None:
    for relative, raw in outputs.items():
        destination = path_for(output_root, relative)
        if destination.is_symlink():
            raise SafetyError(f"refusing artifact symlink destination: {relative}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)


def _load_committed(root: Path) -> dict[str, bytes]:
    return {path: require_file(root, path).read_bytes() for path in ARTIFACT_PATHS}


def verify(root: Path, source_commit: str) -> dict[str, Any]:
    root = root.resolve()
    committed = _load_committed(root)
    report = json.loads(committed[REPORT_ARTIFACT])
    expected = build_outputs(root, report["implementation_result"], source_commit)
    mismatches = [path for path in ARTIFACT_PATHS if committed[path] != expected[path]]
    if mismatches:
        raise ContractError(f"committed M26 artifact mismatch: {mismatches}")
    return {
        "status": "PASS",
        "milestone": MILESTONE,
        "artifact_count": len(committed),
        "verified_artifacts": list(ARTIFACT_PATHS),
        "artifact_set_digest": object_digest([
            {"path": path, "bytes": len(committed[path]), "raw_sha256": raw_digest(committed[path])}
            for path in ARTIFACT_PATHS
        ]),
    }


def self_test(root: Path, source_commit: str) -> dict[str, Any]:
    verification = verify(root, source_commit)
    contract = json.loads(require_file(root, CONTRACT_ARTIFACT).read_text(encoding="utf-8"))
    report = json.loads(require_file(root, REPORT_ARTIFACT).read_text(encoding="utf-8"))
    reproducibility = json.loads(require_file(root, REPRODUCIBILITY_ARTIFACT).read_text(encoding="utf-8"))
    checks = [
        contract["immutable_core"]["balanced_ternary_notation"] == "-1/0/1",
        contract["immutable_core"]["temporal_scheduler_modes"] == ["1/7", "7/1"],
        contract["declared_target"]["target_id"] == TARGET_ID,
        report["implementation"]["timing_status"] == "PASS",
        report["diagnostics"]["warning_count"] == 1,
        report["diagnostics"]["error_count"] == 0,
        reproducibility["matching_output_count"] == len(RAW_OUTPUT_NAMES),
        reproducibility["mismatching_output_count"] == 0,
        reproducibility["canonical_metrics_identical"] is True,
        report["evidence_classification"]["physical_measurements"] is False,
        report["evidence_classification"]["universal_chip_claim"] is False,
        verification["artifact_count"] == len(ARTIFACT_PATHS),
    ]
    if not all(checks):
        raise ContractError("M26 self-test failed")
    return {
        "status": "PASS",
        "milestone": MILESTONE,
        "check_count": len(checks),
        "passed_count": sum(checks),
        "failed_count": len(checks) - sum(checks),
    }


def _write_json_result(path: str | None, value: Mapping[str, Any]) -> None:
    text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def _load_result(path: str) -> dict[str, Any]:
    return _read_json_object(Path(path), "M26 implementation result")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run-implementation", action="store_true")
    mode.add_argument("--generate", action="store_true")
    mode.add_argument("--verify", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--work-root", default="/tmp/frp_m26_implementation")
    parser.add_argument("--yosys", default="yowasp-yosys")
    parser.add_argument("--nextpnr", default="yowasp-nextpnr-ice40")
    parser.add_argument("--implementation-result")
    parser.add_argument("--source-commit", default=EXPECTED_M25_COMMIT)
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(args.repository_root).resolve()
    source_commit = validate_source_commit(args.source_commit)
    if args.run_implementation:
        result = run_implementation(root, Path(args.work_root), args.yosys, args.nextpnr, source_commit)
    elif args.generate:
        if not args.implementation_result:
            raise ContractError("--generate requires --implementation-result")
        implementation = _load_result(args.implementation_result)
        outputs = build_outputs(root, implementation, source_commit)
        write_outputs(Path(args.output_root).resolve(), outputs)
        result = {
            "status": "PASS",
            "milestone": MILESTONE,
            "artifact_count": len(outputs),
            "artifacts": [
                {"path": path, "bytes": len(raw), "raw_sha256": raw_digest(raw)}
                for path, raw in outputs.items()
            ],
        }
    elif args.verify:
        result = verify(root, source_commit)
    else:
        result = self_test(root, source_commit)
    _write_json_result(args.output, result)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, SafetyError) as exc:
        print(f"M26 qualification failure: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
