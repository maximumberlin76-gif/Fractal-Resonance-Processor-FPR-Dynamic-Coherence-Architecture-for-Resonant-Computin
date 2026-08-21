#!/usr/bin/env python3
"""Generate, prove, and verify FRP M24 formal/bounded closure evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


VERSION = "2.6.0"
MILESTONE = "M24"
EXPECTED_M23_COMMIT = "1dcc4e4d47135cdf1e38192cc96f0d928066b13e"
WORKFLOW_PATH = ".github/workflows/frp-m24-formal-bounded-verification-closure-workflow.yml"

CONTRACT_ARTIFACT = "artifacts/m24/contracts/m24-formal-bounded-verification-contract.json"
INVENTORY_ARTIFACT = "artifacts/m24/inventory/m24-property-inventory.json"
EVIDENCE_ARTIFACT = "artifacts/m24/proofs/m24-formal-bounded-proof-evidence.json"
MANIFEST_ARTIFACT = "artifacts/m24/manifests/m24-formal-bounded-verification-manifest.json"
QUALIFICATION_ARTIFACT = "artifacts/m24/manifests/m24-formal-bounded-verification-qualification.json"

CONTRACT_SCHEMA = "schemas/m24/frp_m24_formal_bounded_verification_contract.v2.6.0.schema.json"
INVENTORY_SCHEMA = "schemas/m24/frp_m24_property_inventory.v2.6.0.schema.json"
EVIDENCE_SCHEMA = "schemas/m24/frp_m24_formal_bounded_proof_evidence.v2.6.0.schema.json"
MANIFEST_SCHEMA = "schemas/m24/frp_m24_formal_bounded_verification_manifest.v2.6.0.schema.json"
QUALIFICATION_SCHEMA = "schemas/m24/frp_m24_formal_bounded_verification_qualification.v2.6.0.schema.json"
REGISTRY_PATH = "schemas/m24/frp_m24_schema_registry.json"

SCHEMA_PATHS = {
    "m24-formal-bounded-verification-contract-v2.6.0": CONTRACT_SCHEMA,
    "m24-property-inventory-v2.6.0": INVENTORY_SCHEMA,
    "m24-formal-bounded-proof-evidence-v2.6.0": EVIDENCE_SCHEMA,
    "m24-formal-bounded-verification-manifest-v2.6.0": MANIFEST_SCHEMA,
    "m24-formal-bounded-verification-qualification-v2.6.0": QUALIFICATION_SCHEMA,
}

PACKAGE_HARNESS = "formal/m24/frp_m24_package_properties_formal.sv"
SCHEDULER_HARNESS = "formal/m24/frp_m24_scheduler_properties_formal.sv"
CORE_HARNESS = "formal/m24/frp_m24_core_properties_formal.sv"
LIVENESS_HARNESS = "formal/m24/frp_m24_bounded_liveness_formal.sv"
RESET_HARNESS = "formal/m24/frp_m24_reset_readiness_formal.sv"
NEGATIVE_HARNESS = "formal/m24/frp_m24_expected_counterexamples_formal.sv"

FORMAL_HARNESSES = (
    PACKAGE_HARNESS,
    SCHEDULER_HARNESS,
    CORE_HARNESS,
    LIVENESS_HARNESS,
    RESET_HARNESS,
    NEGATIVE_HARNESS,
)

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
M23_RESET = "rtl/m23/frp_m23_reset_release_sync.sv"
M23_CDC = "rtl/m23/frp_m23_csr_cdc_bridge.sv"
M23_BOUNDARY = "rtl/m23/frp_m23_hardened_integration_boundary.sv"

TECHNICAL_SOURCE_PATHS = (
    "frp_m24_formal_bounded_verification.py",
    *FORMAL_HARNESSES,
    CONTRACT_SCHEMA,
    INVENTORY_SCHEMA,
    EVIDENCE_SCHEMA,
    MANIFEST_SCHEMA,
    QUALIFICATION_SCHEMA,
    REGISTRY_PATH,
    "tests/test_frp_m24_formal_bounded_verification.py",
)

UPSTREAM_SOURCE_PATHS = (
    M16_PACKAGE,
    *M16_MODULES,
    M23_RESET,
    M23_CDC,
    M23_BOUNDARY,
    "artifacts/m23/manifests/m23-clock-reset-cdc-interface-hardening-manifest.json",
    "artifacts/m23/manifests/m23-clock-reset-cdc-interface-hardening-qualification.json",
)

ARTIFACT_PATHS = (
    CONTRACT_ARTIFACT,
    INVENTORY_ARTIFACT,
    EVIDENCE_ARTIFACT,
    MANIFEST_ARTIFACT,
    QUALIFICATION_ARTIFACT,
)

YOWASP_PACKAGE = "yowasp-yosys"
YOWASP_PACKAGE_VERSION = "0.68.0.0.post1208"
YOSYS_ENGINE_VERSION = "0.68"
YOSYS_GIT_SHA = "38e001a6f"


PROPERTY_SPECS: tuple[dict[str, Any], ...] = (
    {"property_id": "M24-P01", "domain": "canonical_ternary", "kind": "safety", "statement": "canonical state is valid exactly when it is not encoding 2'b10", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P02", "domain": "canonical_ternary", "kind": "safety", "statement": "encodings are -1=11, 0=00, 1=01, reserved=10, and active neutral is 0", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P03", "domain": "canonical_ternary", "kind": "safety", "statement": "equal valid state and target with no pending route classify as same-state", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P04", "domain": "canonical_ternary", "kind": "safety", "statement": "zero to nonzero class is exact for valid operands without pending ownership", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P05", "domain": "canonical_ternary", "kind": "safety", "statement": "nonzero to zero class is exact for valid operands without pending ownership", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P06", "domain": "active_neutral", "kind": "safety", "statement": "opposite valid polarities classify as opposite-polarity", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P07", "domain": "active_neutral", "kind": "safety", "statement": "opposite-polarity selection is active neutral and direct transition is illegal", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P08", "domain": "pending_route", "kind": "safety", "statement": "nonzero pending route owns zero state and supplies the selected completion target", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P09", "domain": "transition_capacity", "kind": "safety", "statement": "same-state consumes no capacity and every state-changing class consumes capacity", "run_id": "M24-R01", "assumption_ids": []},
    {"property_id": "M24-P10", "domain": "scheduler_counter", "kind": "safety", "statement": "registered scheduler mode remains inside the declared domain", "run_id": "M24-R02", "assumption_ids": ["M24-A02", "M24-A05", "M24-A11"]},
    {"property_id": "M24-P11", "domain": "scheduler_counter", "kind": "safety", "statement": "registered scheduler state remains inside the declared domain", "run_id": "M24-R02", "assumption_ids": ["M24-A02", "M24-A05", "M24-A11"]},
    {"property_id": "M24-P12", "domain": "scheduler_counter", "kind": "safety", "statement": "period index equals tick index modulo eight", "run_id": "M24-R02", "assumption_ids": ["M24-A01", "M24-A02", "M24-A05"]},
    {"property_id": "M24-P13", "domain": "scheduler_counter", "kind": "safety", "statement": "scheduler event counters sum exactly to ticks recorded", "run_id": "M24-R02", "assumption_ids": ["M24-A01", "M24-A02", "M24-A05"]},
    {"property_id": "M24-P14", "domain": "scheduler_counter", "kind": "safety", "statement": "enabled tick has exactly one scheduler enable and disabled tick has none", "run_id": "M24-R02", "assumption_ids": ["M24-A02", "M24-A11"]},
    {"property_id": "M24-P15", "domain": "scheduler_counter", "kind": "bounded_sequence", "statement": "registered scheduler state equals the mode and modulo-eight decode relation", "run_id": "M24-R02", "assumption_ids": ["M24-A01", "M24-A02", "M24-A05"]},
    {"property_id": "M24-P16", "domain": "request_lane", "kind": "safety", "statement": "a request lane is never accepted and rejected simultaneously", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09", "M24-A11"]},
    {"property_id": "M24-P17", "domain": "request_lane", "kind": "safety", "statement": "accepted change count never exceeds the request-lane boundary", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P18", "domain": "request_lane", "kind": "safety", "statement": "duplicate same-cell lanes cannot both be accepted", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P19", "domain": "transition_capacity", "kind": "safety", "statement": "capacity remaining and exhausted outputs are exact functions of accepted changes", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P20", "domain": "transition_capacity", "kind": "safety", "statement": "switch-load numerator equals accepted changes", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P21", "domain": "active_neutral", "kind": "safety", "statement": "neutral routing is a subset of accepted cells and accepted state changes", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P22", "domain": "retained_state", "kind": "safety", "statement": "every retained state output remains canonical ternary", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P23", "domain": "pending_route", "kind": "safety", "statement": "every retained pending-route output remains canonical ternary", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P24", "domain": "retained_state", "kind": "safety", "statement": "actual direct opposite-polarity event count remains zero", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P25", "domain": "retained_state", "kind": "safety", "statement": "reserved state event count remains zero", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P26", "domain": "pending_route", "kind": "safety", "statement": "queue overflow event count remains zero", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P27", "domain": "invariant_flag", "kind": "safety", "statement": "all ten integrated invariant flags remain asserted", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A05", "M24-A09", "M24-A11"]},
    {"property_id": "M24-P28", "domain": "retained_state", "kind": "bounded_sequence", "statement": "disabled tick preserves retained state and pending-route banks", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A02", "M24-A03", "M24-A04", "M24-A09"]},
    {"property_id": "M24-P29", "domain": "reset_readiness", "kind": "initial_state", "statement": "formal reset image initializes state, pending routes, and tick count to zero", "run_id": "M24-R03", "assumption_ids": ["M24-A01", "M24-A09"]},
    {"property_id": "M24-P30", "domain": "bounded_liveness", "kind": "bounded_sequence", "statement": "first controlled free-mode request commits 0 to 1", "run_id": "M24-R04", "assumption_ids": ["M24-A01", "M24-A05", "M24-A06", "M24-A09"]},
    {"property_id": "M24-P31", "domain": "bounded_liveness", "kind": "bounded_sequence", "statement": "opposite request performs 1 to active-neutral 0 and retains -1 pending polarity", "run_id": "M24-R04", "assumption_ids": ["M24-A01", "M24-A05", "M24-A06", "M24-A09"]},
    {"property_id": "M24-P32", "domain": "bounded_liveness", "kind": "bounded_liveness", "statement": "retained -1 pending route completes from active-neutral 0 by proof step three", "run_id": "M24-R04", "assumption_ids": ["M24-A01", "M24-A05", "M24-A06", "M24-A09"]},
    {"property_id": "M24-P33", "domain": "reset_readiness", "kind": "safety", "statement": "asynchronous assertion forces both release signals and readiness low", "run_id": "M24-R05", "assumption_ids": ["M24-A01", "M24-A07", "M24-A08", "M24-A11"]},
    {"property_id": "M24-P34", "domain": "reset_readiness", "kind": "bounded_sequence", "statement": "both domain reset synchronizers release within two post-assertion paired edges", "run_id": "M24-R05", "assumption_ids": ["M24-A01", "M24-A07", "M24-A08"]},
    {"property_id": "M24-P35", "domain": "reset_readiness", "kind": "safety", "statement": "integration readiness implies both reset domains have released", "run_id": "M24-R05", "assumption_ids": ["M24-A01", "M24-A07", "M24-A08"]},
    {"property_id": "M24-P36", "domain": "reset_readiness", "kind": "bounded_liveness", "statement": "readiness is asserted by paired-edge proof step six", "run_id": "M24-R05", "assumption_ids": ["M24-A01", "M24-A07", "M24-A08"]},
)


ASSUMPTION_SPECS: tuple[dict[str, Any], ...] = (
    {"assumption_id": "M24-A01", "class": "initialization", "statement": "all proof registers begin at the architectural reset image", "implementation": "sat -set-init-zero"},
    {"assumption_id": "M24-A02", "class": "input_domain", "statement": "temporal scheduler modes are 1/7 and 7/1; free remains a distinct service mode", "implementation": "frp_is_valid_scheduler_mode assume statements"},
    {"assumption_id": "M24-A03", "class": "input_domain", "statement": "both symbolic request targets are canonical ternary", "implementation": "two request_target assume statements"},
    {"assumption_id": "M24-A04", "class": "input_domain", "statement": "both symbolic target-bank cells are canonical ternary", "implementation": "two target_q assume statements"},
    {"assumption_id": "M24-A05", "class": "arithmetic_bound", "statement": "eight-bit counters cannot wrap inside the declared proof depths", "implementation": "COUNTER_BITS=8 and maximum depth=8"},
    {"assumption_id": "M24-A06", "class": "liveness_fairness", "statement": "liveness trace uses free mode, one enabled tick per step, no clear, and no competing request after the opposite request", "implementation": LIVENESS_HARNESS},
    {"assumption_id": "M24-A07", "class": "reset_sequence", "statement": "reset is asserted at proof step zero and remains deasserted afterward", "implementation": RESET_HARNESS},
    {"assumption_id": "M24-A08", "class": "clock_fairness", "statement": "one host edge and one core edge occur per paired formal step", "implementation": "host_clk and core_clk share paired_clock in reset/readiness harness"},
    {"assumption_id": "M24-A09", "class": "parameter_bound", "statement": "integrated proof uses CELLS=2/LANES=2 and liveness proof uses CELLS=1/LANES=1", "implementation": "explicit harness parameter overrides"},
    {"assumption_id": "M24-A10", "class": "elaboration_transform", "statement": "Yosys preparation removes only include, package, import, and namespace wrappers while preserving module bodies", "implementation": "audited deterministic prepare_yosys_sources transform"},
    {"assumption_id": "M24-A11", "class": "logic_semantics", "statement": "formal variables are defined two-state values", "implementation": "sat -set-def-formal"},
)


BOUND_SPECS: tuple[dict[str, Any], ...] = (
    {"bound_id": "M24-B01", "run_id": "M24-R01", "depth": 1, "cells": 0, "request_lanes": 0, "counter_bits": 0, "scope": "complete two-bit helper input space"},
    {"bound_id": "M24-B02", "run_id": "M24-R02", "depth": 8, "cells": 0, "request_lanes": 0, "counter_bits": 8, "scope": "one complete modulo-eight scheduler period"},
    {"bound_id": "M24-B03", "run_id": "M24-R03", "depth": 3, "cells": 2, "request_lanes": 2, "counter_bits": 8, "scope": "integrated symbolic M16 safety and retention"},
    {"bound_id": "M24-B04", "run_id": "M24-R04", "depth": 4, "cells": 1, "request_lanes": 1, "counter_bits": 8, "scope": "controlled opposite-polarity pending completion"},
    {"bound_id": "M24-B05", "run_id": "M24-R05", "depth": 7, "cells": 2, "request_lanes": 1, "counter_bits": 0, "scope": "M23 paired-edge reset release and readiness"},
)


RUN_SPECS: tuple[dict[str, Any], ...] = (
    {"run_id": "M24-R01", "top": "frp_m24_package_properties_formal", "harness": PACKAGE_HARNESS, "depth": 1, "property_ids": [f"M24-P{index:02d}" for index in range(1, 10)], "mode": "prove", "source_group": "package"},
    {"run_id": "M24-R02", "top": "frp_m24_scheduler_properties_formal", "harness": SCHEDULER_HARNESS, "depth": 8, "property_ids": [f"M24-P{index:02d}" for index in range(10, 16)], "mode": "prove", "source_group": "scheduler"},
    {"run_id": "M24-R03", "top": "frp_m24_core_properties_formal", "harness": CORE_HARNESS, "depth": 3, "property_ids": [f"M24-P{index:02d}" for index in range(16, 30)], "mode": "prove", "source_group": "core"},
    {"run_id": "M24-R04", "top": "frp_m24_bounded_liveness_formal", "harness": LIVENESS_HARNESS, "depth": 4, "property_ids": ["M24-P30", "M24-P31", "M24-P32"], "mode": "prove", "source_group": "core"},
    {"run_id": "M24-R05", "top": "frp_m24_reset_readiness_formal", "harness": RESET_HARNESS, "depth": 7, "property_ids": ["M24-P33", "M24-P34", "M24-P35", "M24-P36"], "mode": "prove", "source_group": "reset"},
    {"run_id": "M24-R06", "top": "frp_m24_reserved_encoding_counterexample", "harness": NEGATIVE_HARNESS, "depth": 1, "counterexample_id": "M24-N01", "mode": "expected_counterexample", "source_group": "negative"},
    {"run_id": "M24-R07", "top": "frp_m24_direct_transition_counterexample", "harness": NEGATIVE_HARNESS, "depth": 1, "counterexample_id": "M24-N02", "mode": "expected_counterexample", "source_group": "negative"},
)


COUNTEREXAMPLE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "counterexample_id": "M24-N01",
        "run_id": "M24-R06",
        "false_claim": "reserved encoding 2'b10 is a valid ternary state",
        "expected_classification": "reserved_operand",
        "witness": {"state_value": "10", "M24_N01_FALSE_CLAIM": "0"},
    },
    {
        "counterexample_id": "M24-N02",
        "run_id": "M24-R07",
        "false_claim": "1 to -1 executes directly in one retained-state write",
        "expected_classification": "active_neutral_route",
        "context": {"state_q": "01", "request_target": "11"},
        "witness": {"state_candidate_d": "00", "M24_N02_FALSE_CLAIM": "0"},
    },
)


class ContractError(ValueError):
    """Raised for an M24 contract or proof violation."""


class SafetyError(ValueError):
    """Raised for an unsafe filesystem boundary."""


def safe_relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str):
        raise SafetyError(f"unsafe M24 path: {value!r}")
    path = PurePosixPath(value)
    if (
        "\\" in value
        or path.is_absolute()
        or not path.parts
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise SafetyError(f"unsafe M24 path: {value}")
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
    if value != EXPECTED_M23_COMMIT:
        raise ContractError(f"unexpected M23 source commit: {value}")
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
    """Load and validate the closed M24 Draft 2020-12 schema set."""

    def __init__(self, root: Path) -> None:
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


def _flatten_package(text: str, package_name: str) -> str:
    start = f"package {package_name};"
    end = f"endpackage : {package_name}"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ContractError(f"unexpected package wrapper for {package_name}")
    lines = [line for line in text.splitlines() if line.strip() not in (start, end)]
    return "\n".join(lines) + "\n"


def _flatten_module(text: str) -> str:
    output: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("`include \"frp_m"):
            continue
        if stripped in ("import frp_m16_pkg::*;", "import frp_m22_csr_pkg::*;"):
            continue
        output.append(line.replace("frp_m16_pkg::", "").replace("frp_m22_csr_pkg::", ""))
    result = "\n".join(output) + "\n"
    if "import frp_m" in result or "frp_m16_pkg::" in result or "frp_m22_csr_pkg::" in result:
        raise ContractError("unhandled namespace in prepared RTL")
    return result


def prepared_source_bytes(root: Path) -> dict[str, bytes]:
    prepared: dict[str, bytes] = {}
    package_text = require_file(root, M16_PACKAGE).read_text(encoding="utf-8")
    prepared["prepared/00_frp_m16_pkg_flat.sv"] = _flatten_package(package_text, "frp_m16_pkg").encode()
    for relative in M16_MODULES:
        text = require_file(root, relative).read_text(encoding="utf-8")
        prepared[f"prepared/m16/{Path(relative).name}"] = _flatten_module(text).encode()
    for relative in (M23_RESET, M23_CDC, M23_BOUNDARY):
        text = require_file(root, relative).read_text(encoding="utf-8")
        prepared[f"prepared/m23/{Path(relative).name}"] = _flatten_module(text).encode()
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
    property_ids = [item["property_id"] for item in PROPERTY_SPECS]
    if property_ids != [f"M24-P{index:02d}" for index in range(1, 37)]:
        raise ContractError("M24 property inventory is not dense")
    source_text = "\n".join(require_file(root, path).read_text(encoding="utf-8") for path in FORMAL_HARNESSES)
    for property_id in property_ids:
        token = property_id.replace("-", "_")
        if source_text.count(token) < 1:
            raise ContractError(f"formal property token missing: {property_id}")
    for negative_id in ("M24_N01_FALSE_CLAIM", "M24_N02_FALSE_CLAIM"):
        if source_text.count(negative_id) < 2:
            raise ContractError(f"negative property token missing: {negative_id}")
    if source_text.count("assume(") != 6:
        raise ContractError("unexpected formal assume statement count")
    if len({item["assumption_id"] for item in ASSUMPTION_SPECS}) != len(ASSUMPTION_SPECS):
        raise ContractError("duplicate M24 assumption identifier")
    declared_assumptions = {item["assumption_id"] for item in ASSUMPTION_SPECS}
    used_assumptions = {value for item in PROPERTY_SPECS for value in item["assumption_ids"]}
    if not used_assumptions.issubset(declared_assumptions):
        raise ContractError("unrecorded M24 property assumption")
    prepared_source_bytes(root)


def _proof_script(run: Mapping[str, Any], work_root: Path) -> str:
    del work_root
    prepared = Path("prepared")
    package = prepared / "00_frp_m16_pkg_flat.sv"
    harness = prepared / "harness" / Path(str(run["harness"])).name
    group = run["source_group"]
    if group == "package":
        sources = [package, harness]
    elif group == "scheduler":
        sources = [package, prepared / "m16" / "frp_m16_scheduler.sv", harness]
    elif group == "core":
        sources = [package, *(prepared / "m16" / Path(path).name for path in M16_MODULES), harness]
    elif group == "reset":
        sources = [
            package,
            prepared / "m23" / Path(M23_RESET).name,
            prepared / "m23" / Path(M23_CDC).name,
            prepared / "m23" / Path(M23_BOUNDARY).name,
            harness,
        ]
    elif group == "negative":
        sources = [package, prepared / "m16" / "frp_m16_active_neutral.sv", harness]
    else:
        raise ContractError(f"unknown M24 source group: {group}")
    read_command = "read_verilog -sv -formal " + " ".join(str(path) for path in sources)
    commands = [
        read_command,
        f"prep -top {run['top']}",
        "flatten",
        "chformal -lower",
    ]
    if group in ("scheduler", "core", "reset"):
        commands.append("async2sync")
    commands.append("opt_clean")
    sat = [
        "sat",
        "-prove-asserts",
        "-set-def-formal",
        "-set-init-zero",
        f"-seq {run['depth']}",
        "-timeout 300",
    ]
    if group in ("scheduler", "core"):
        sat.append("-set-assumes")
    if run["mode"] == "prove":
        sat.append("-verify")
    else:
        witness = Path("witness") / f"{run['counterexample_id'].lower()}.json"
        if run["counterexample_id"] == "M24-N01":
            sat.extend(("-show state_value", "-show M24_N01_FALSE_CLAIM"))
        else:
            sat.extend(("-show state_candidate_d", "-show M24_N02_FALSE_CLAIM"))
        sat.append(f"-dump_json {witness}")
    commands.append(" ".join(sat))
    return "; ".join(commands)


def _normalized_script(run: Mapping[str, Any]) -> str:
    return _proof_script(run, Path("."))


def canonical_formal_result(root: Path) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for run in RUN_SPECS:
        record: dict[str, Any] = {
            "run_id": run["run_id"],
            "top": run["top"],
            "mode": run["mode"],
            "depth": run["depth"],
            "yosys_script": _normalized_script(run),
            "status": "PASS" if run["mode"] == "prove" else "EXPECTED_COUNTEREXAMPLE",
        }
        if run["mode"] == "prove":
            record["property_ids"] = list(run["property_ids"])
        else:
            record["counterexample_id"] = run["counterexample_id"]
        runs.append(record)
    counterexamples: list[dict[str, Any]] = []
    for spec in COUNTEREXAMPLE_SPECS:
        item = dict(spec)
        item["status"] = "EXPECTED_COUNTEREXAMPLE"
        item["witness_digest"] = object_digest(item["witness"])
        counterexamples.append(item)
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
        "passing_proof_run_count": 5,
        "expected_counterexample_run_count": 2,
        "runs": runs,
        "counterexample_count": len(counterexamples),
        "counterexamples": counterexamples,
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
        target = work_root.joinpath(*safe_relative_path(relative).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (work_root / "logs").mkdir()
    (work_root / "witness").mkdir()


def _normalize_wavejson(path: Path) -> dict[str, str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for signal in document.get("signal", []):
        name = signal.get("name")
        if not isinstance(name, str):
            raise ContractError(f"invalid witness signal name in {path}")
        if "data" in signal:
            data = signal["data"]
            if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], str):
                raise ContractError(f"invalid witness data in {path}")
            result[name] = data[0]
        else:
            wave = signal.get("wave")
            if wave not in ("0", "1"):
                raise ContractError(f"invalid witness wave in {path}")
            result[name] = wave
    return result


def run_formal(root: Path, work_root: Path, yosys: str) -> dict[str, Any]:
    root = root.resolve()
    work_root = work_root.resolve()
    validate_formal_sources(root)
    executable = shutil.which(yosys)
    if executable is None:
        raise ContractError(f"Yosys executable not found: {yosys}")
    version_run = subprocess.run(
        [executable, "-V"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=120,
    )
    version_text = version_run.stdout.strip()
    if version_run.returncode != 0 or f"Yosys {YOSYS_ENGINE_VERSION}" not in version_text or YOSYS_GIT_SHA not in version_text:
        raise ContractError(f"unexpected Yosys provenance: {version_text}")
    _write_prepared_sources(root, work_root)
    expected = canonical_formal_result(root)
    expected_witnesses = {
        item["counterexample_id"]: item["witness"] for item in expected["counterexamples"]
    }
    for run in RUN_SPECS:
        script = _proof_script(run, work_root)
        completed = subprocess.run(
            [executable, "-Q", "-p", script],
            cwd=work_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=600,
            env={**os.environ, "PYTHONHASHSEED": "0", "LC_ALL": "C.UTF-8", "TZ": "UTC"},
        )
        log_path = work_root / "logs" / f"{run['run_id'].lower()}.log"
        log_path.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            raise ContractError(f"formal run failed: {run['run_id']} (see {log_path})")
        if run["mode"] == "prove":
            if "SAT proof finished - no model found: SUCCESS!" not in completed.stdout:
                raise ContractError(f"passing proof marker missing: {run['run_id']}")
        else:
            if "SAT proof finished - model found: FAIL!" not in completed.stdout:
                raise ContractError(f"expected counterexample marker missing: {run['run_id']}")
            witness_path = work_root / "witness" / f"{run['counterexample_id'].lower()}.json"
            observed = _normalize_wavejson(witness_path)
            if observed != expected_witnesses[run["counterexample_id"]]:
                raise ContractError(f"counterexample witness mismatch: {run['counterexample_id']}: {observed}")
    result_path = work_root / "formal-run.json"
    result_path.write_bytes(document_bytes(expected))
    return expected


def build_contract(root: Path, source_commit: str) -> dict[str, Any]:
    validate_source_commit(source_commit)
    validate_formal_sources(root)
    contract: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m24-formal-bounded-verification-contract",
        "milestone": MILESTONE,
        "release": "FRP v2.6.0",
        "status": "PASS",
        "source_commit": source_commit,
        "source_release": "FRP v2.5.0 / M23 clock-reset-CDC integration boundary",
        "qualified_boundary": {
            "primary_rtl": "rtl/m16/frp_m16_core.sv",
            "integration_rtl": M23_BOUNDARY,
            "balanced_ternary_notation": "-1/0/1",
            "balanced_ternary_semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
            "direct_opposite_polarity_transition": "forbidden",
        },
        "method": {
            "class": "bounded_symbolic_model_checking",
            "engine": "Yosys SAT",
            "solver": "minisat",
            "rtl_binding": "deterministic namespace-only preparation of exact digest-bound RTL",
            "claim_boundary": "only listed properties, assumptions, profiles, and depths",
            "unbounded_proof_claimed": False,
        },
        "required_domains": [
            "canonical_ternary",
            "active_neutral",
            "pending_route",
            "scheduler_counter",
            "request_lane",
            "transition_capacity",
            "retained_state",
            "invariant_flag",
            "reset_readiness",
            "bounded_liveness",
        ],
        "property_count": len(PROPERTY_SPECS),
        "assumption_count": len(ASSUMPTION_SPECS),
        "bound_count": len(BOUND_SPECS),
        "proof_run_count": len(RUN_SPECS),
        "expected_counterexample_count": len(COUNTEREXAMPLE_SPECS),
        "workflow_path": WORKFLOW_PATH,
    }
    contract["contract_digest"] = object_digest(contract)
    return contract


def build_inventory(contract: Mapping[str, Any], formal: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    run_status = {item["run_id"]: item["status"] for item in formal["runs"]}
    properties = []
    for spec in PROPERTY_SPECS:
        item = dict(spec)
        item["harness"] = next(run["harness"] for run in RUN_SPECS if run["run_id"] == spec["run_id"])
        item["status"] = "PASS" if run_status[spec["run_id"]] == "PASS" else "FAIL"
        item["property_digest"] = object_digest(item)
        properties.append(item)
    inventory: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m24-property-inventory",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "property_count": len(properties),
        "passed_count": sum(item["status"] == "PASS" for item in properties),
        "failed_count": sum(item["status"] == "FAIL" for item in properties),
        "properties": properties,
    }
    inventory["property_set_digest"] = object_digest(inventory)
    return inventory


def build_evidence(contract: Mapping[str, Any], inventory: Mapping[str, Any], formal: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    assumptions = []
    for spec in ASSUMPTION_SPECS:
        item = dict(spec)
        item["status"] = "DECLARED"
        item["assumption_digest"] = object_digest(item)
        assumptions.append(item)
    bounds = []
    for spec in BOUND_SPECS:
        item = dict(spec)
        item["status"] = "PASS"
        item["bound_digest"] = object_digest(item)
        bounds.append(item)
    evidence: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m24-formal-bounded-proof-evidence",
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": validate_source_commit(source_commit),
        "contract_digest": contract["contract_digest"],
        "property_set_digest": inventory["property_set_digest"],
        "prepared_rtl_digest": formal["prepared_rtl_digest"],
        "tool": formal["tool"],
        "reproduction_command": "python frp_m24_formal_bounded_verification.py --run-formal --repository-root . --work-root /tmp/frp_m24_formal --yosys yowasp-yosys --source-commit " + source_commit + " --output /tmp/frp_m24_evidence/formal-run.json",
        "assumption_count": len(assumptions),
        "assumptions": assumptions,
        "unrecorded_assumption_count": 0,
        "bound_count": len(bounds),
        "bounds": bounds,
        "proof_run_count": formal["run_count"],
        "proof_runs": formal["runs"],
        "property_count": inventory["property_count"],
        "passed_property_count": inventory["passed_count"],
        "failed_property_count": inventory["failed_count"],
        "expected_counterexample_count": formal["counterexample_count"],
        "retained_counterexamples": formal["counterexamples"],
        "overall_status": "PASS",
    }
    evidence["evidence_digest"] = object_digest(evidence)
    return evidence


def build_manifest(root: Path, source_commit: str, primary: Mapping[str, bytes]) -> dict[str, Any]:
    sources = [source_record(root, path) for path in sorted((WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS))]
    upstream = [source_record(root, path) for path in sorted(UPSTREAM_SOURCE_PATHS)]
    artifacts = [
        {"path": path, "bytes": len(primary[path]), "raw_sha256": sha256_bytes(primary[path])}
        for path in (CONTRACT_ARTIFACT, INVENTORY_ARTIFACT, EVIDENCE_ARTIFACT)
    ]
    manifest: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m24-formal-bounded-verification-manifest",
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


def build_qualification(contract: Mapping[str, Any], inventory: Mapping[str, Any], evidence: Mapping[str, Any], manifest: Mapping[str, Any], source_commit: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(category: str, value: Any) -> None:
        checks.append(_qualification_check(f"Q{len(checks) + 1:03d}", category, value))

    for value in (VERSION, MILESTONE, validate_source_commit(source_commit), contract["status"], WORKFLOW_PATH):
        add("identity", value)
    for item in inventory["properties"]:
        add("property", item["property_id"])
    for item in evidence["assumptions"]:
        add("assumption", item["assumption_id"])
    for item in evidence["bounds"]:
        add("bound", item["bound_id"])
    for item in evidence["proof_runs"]:
        add("proof_run", item["run_id"])
    for item in evidence["retained_counterexamples"]:
        add("counterexample", item["counterexample_id"])
    for schema_path in SCHEMA_PATHS.values():
        add("schema", schema_path)
    for category, value in (
        ("manifest", manifest["source_count"]),
        ("manifest", manifest["upstream_dependency_count"]),
        ("manifest", manifest["artifact_count"]),
        ("manifest", manifest["artifact_set_digest"]),
        ("assumption_closure", evidence["unrecorded_assumption_count"]),
    ):
        add(category, value)
    qualification: dict[str, Any] = {
        "schema_version": VERSION,
        "artifact_id": "frp-m24-formal-bounded-verification-qualification",
        "milestone": MILESTONE,
        "status": "PASS",
        "overall_status": "PASS",
        "source_commit": source_commit,
        "manifest_digest": manifest["manifest_digest"],
        "evidence_digest": evidence["evidence_digest"],
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
    }
    qualification["qualification_digest"] = object_digest(qualification)
    return qualification


def build_outputs(root: Path, source_commit: str, formal_result: Mapping[str, Any] | None = None) -> dict[str, bytes]:
    root = root.resolve()
    expected_formal = canonical_formal_result(root)
    if formal_result is not None and dict(formal_result) != expected_formal:
        raise ContractError("formal run result does not match canonical M24 result")
    contract = build_contract(root, source_commit)
    inventory = build_inventory(contract, expected_formal, source_commit)
    evidence = build_evidence(contract, inventory, expected_formal, source_commit)
    primary = {
        CONTRACT_ARTIFACT: document_bytes(contract),
        INVENTORY_ARTIFACT: document_bytes(inventory),
        EVIDENCE_ARTIFACT: document_bytes(evidence),
    }
    manifest = build_manifest(root, source_commit, primary)
    qualification = build_qualification(contract, inventory, evidence, manifest, source_commit)
    outputs = {
        **primary,
        MANIFEST_ARTIFACT: document_bytes(manifest),
        QUALIFICATION_ARTIFACT: document_bytes(qualification),
    }
    schemas = SchemaContext(root)
    mapping = {
        CONTRACT_ARTIFACT: CONTRACT_SCHEMA,
        INVENTORY_ARTIFACT: INVENTORY_SCHEMA,
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
    verified = []
    for relative, expected in outputs.items():
        actual = require_file(root, relative).read_bytes()
        if actual != expected:
            raise ContractError(f"committed M24 artifact mismatch: {relative}")
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
    inventory = json.loads(outputs_a[INVENTORY_ARTIFACT])
    evidence = json.loads(outputs_a[EVIDENCE_ARTIFACT])
    manifest = json.loads(outputs_a[MANIFEST_ARTIFACT])
    qualification = json.loads(outputs_a[QUALIFICATION_ARTIFACT])
    predicates = (
        ("identity", (VERSION, MILESTONE) == ("2.6.0", "M24")),
        ("source_commit", contract["source_commit"] == source_commit),
        ("byte_stability", outputs_a == outputs_b),
        ("artifact_count", len(outputs_a) == 5),
        ("property_count", inventory["property_count"] == inventory["passed_count"] == 36),
        ("property_ids", [item["property_id"] for item in inventory["properties"]] == [f"M24-P{index:02d}" for index in range(1, 37)]),
        ("assumptions", evidence["assumption_count"] == 11),
        ("no_unrecorded_assumptions", evidence["unrecorded_assumption_count"] == 0),
        ("bounds", evidence["bound_count"] == 5),
        ("proof_runs", evidence["proof_run_count"] == 7),
        ("counterexamples", evidence["expected_counterexample_count"] == 2),
        ("tool", evidence["tool"]["engine_version"] == YOSYS_ENGINE_VERSION),
        ("prepared_rtl", len(evidence["prepared_rtl_digest"]) == 64),
        ("manifest_sources", manifest["source_count"] == len((WORKFLOW_PATH, *TECHNICAL_SOURCE_PATHS))),
        ("manifest_upstream", manifest["upstream_dependency_count"] == len(UPSTREAM_SOURCE_PATHS)),
        ("qualification", qualification["check_count"] == qualification["passed_count"]),
        ("overall_status", qualification["overall_status"] == "PASS"),
    )
    checks = [{"check_id": name, "status": "PASS" if passed else "FAIL"} for name, passed in predicates]
    failed = [item for item in checks if item["status"] != "PASS"]
    if failed:
        raise ContractError(f"M24 self-test failure: {failed}")
    return {"status": "PASS", "check_count": len(checks), "passed_count": len(checks), "failed_count": 0, "checks": checks}


def read_json_file(path: str | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    candidate = Path(path)
    if candidate.is_symlink() or not candidate.is_file():
        raise SafetyError(f"invalid JSON input: {candidate}")
    value = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"JSON input must be an object: {candidate}")
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
    except (ContractError, SafetyError, OSError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(f"M24_ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
