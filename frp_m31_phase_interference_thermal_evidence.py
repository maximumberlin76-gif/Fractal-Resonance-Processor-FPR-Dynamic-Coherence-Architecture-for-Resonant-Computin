#!/usr/bin/env python3
"""FRP M31 phase-interference, active-zero, and thermal evidence producer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA_ID = "frp.m31.phase_interference_active_zero_thermal_evidence.v1"
MANIFEST_SCHEMA_ID = (
    "frp.m31.phase_interference_active_zero_thermal_evidence_manifest.v1"
)
QUALIFICATION_SCHEMA_ID = (
    "frp.m31.phase_interference_active_zero_thermal_evidence_qualification.v1"
)
MILESTONE = "M31"
ARCHIVE_ROOT = "Fractal-Resonance-Processor-FRP-v3.2.0"
ARCHIVE_PATH = "artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz"
ARCHIVE_SHA256 = "05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa"

SCHEMA_PATH = (
    "schemas/m31/"
    "frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json"
)
EVIDENCE_PATH = (
    "artifacts/m31/evidence/"
    "m31-phase-interference-active-zero-thermal-evidence.json"
)
MANIFEST_PATH = (
    "artifacts/m31/manifests/"
    "m31-phase-interference-active-zero-thermal-evidence-manifest.json"
)
QUALIFICATION_PATH = (
    "artifacts/m31/qualification/"
    "m31-phase-interference-active-zero-thermal-evidence-qualification.json"
)

INPUT_DIGESTS = {
    "frp_prototype_v0_9_3_mobile.py": (
        "48361714bb815f362a30a5a884a0fb782cb97349e9a18f9b607af7bf54c02e52"
    ),
    "TEST_REPORT_v0_9_3.md": (
        "c6fe86f2c0c922243a8bd001742e9fcbfd3c31cdedf40a6a728b989dbd01679e"
    ),
    "docs/physical_foundation.md": (
        "e9bacd13ebe7a7058e698a80dc4f677476e3ed2eab4b9d41f58fd9cdbcf68a7e"
    ),
    "docs/resonance_computation.md": (
        "1149cbd0aeb90d0a6133db5ecc1e5b4d45268815b70a75cb7a347a5e44a9b615"
    ),
    "artifacts/m19/execution/m16-rtl-execution-trace.json": (
        "d7945e0d2b5aaa05c5fff2e4e60d3b984017f7e4ae1984c55920368a110020bd"
    ),
    "artifacts/m19/execution/m16-fpga-preparation-execution-trace.json": (
        "7d58b6741bdcadbfb9acb9049ed0e956305f49b9ad36946e719a4121b5caf22f"
    ),
    "benchmarks/architecture_comparison/results/"
    "reference_comparison_seed_76.json": (
        "5ba86d26dc62db36ae14ac2c1167e71dd5c06c00bbd5aa3dc21c6d11b38db064"
    ),
    "benchmarks/architecture_comparison/results/"
    "reference_comparison_seed_76_hardware_sensitivity_v1.json": (
        "e4785aa4c234cc7dd8e5377e5e0b41a8ec401f962400975e0cef7a88cc494680"
    ),
    "benchmarks/architecture_comparison/profiles/"
    "thermal_proxy_profile_v1.json": (
        "aeafebc3e71d1311a3445bd1528cbe7322546f79d6a5099dfed3a9590fc4a25b"
    ),
    "artifacts/m29/contracts/m29-system-integration-contract.json": (
        "6e14d93abe5646b4e094f27b07217d9e4dcd833d8af0d5afb30da21b904c4642"
    ),
}

CURRENT_WORKFLOW_DIGESTS = {
    ".github/workflows/"
    "frp-m30-observatory-full-core-trace-qualification-workflow.yml": (
        "01ca22bc98f63d9d4ea4a58299d53ff58b410f3f2db94b81097d7cef3ad4dee7"
    )
}

TRACE_PATHS = (
    "artifacts/m19/execution/m16-rtl-execution-trace.json",
    "artifacts/m19/execution/m16-fpga-preparation-execution-trace.json",
)

EXPECTED_ARCHITECTURE_ORDER = [
    "binary_synchronous_reference",
    "binary_clock_gated_reference",
    "direct_ternary_reference",
    "frp_v1_7_0_quantized_shadow",
]

EXPECTED_HISTORICAL_ROWS = {
    "binary_style_forced_switch": {
        "architecture_id": "binary_style_forced_switch",
        "cases": 300,
        "match": "1.000",
        "C_minus_P_min": "-0.551000",
        "heat_peak": "0.051000",
        "switch_load_peak": "1.000000",
        "actual_direct_events": 2052,
        "prevented_direct_events": 0,
        "neutralized_conflicts": 0,
    },
    "direct_ternary_commit": {
        "architecture_id": "direct_ternary_commit",
        "cases": 300,
        "match": "1.000",
        "C_minus_P_min": "-0.551000",
        "heat_peak": "0.051000",
        "switch_load_peak": "1.000000",
        "actual_direct_events": 2052,
        "prevented_direct_events": 0,
        "neutralized_conflicts": 0,
    },
    "distributed_neutral_ternary": {
        "architecture_id": "distributed_neutral_ternary",
        "cases": 300,
        "match": "1.000",
        "C_minus_P_min": "0.174750",
        "heat_peak": "0.003250",
        "switch_load_peak": "0.250000",
        "actual_direct_events": 0,
        "prevented_direct_events": 0,
        "neutralized_conflicts": 2052,
    },
    "frp_distributed_resonant": {
        "architecture_id": "frp_distributed_resonant",
        "cases": 300,
        "match": "1.000",
        "C_minus_P_min": "0.144750",
        "heat_peak": "0.107000",
        "switch_load_peak": "0.250000",
        "actual_direct_events": 0,
        "prevented_direct_events": 3820,
        "neutralized_conflicts": 2392,
    },
}

EXPECTED_HISTORICAL_STDOUT_SHA256 = (
    "b18e1affec6dec8029086e923b907c9ae3cb0c50131e4291b31fbd2a4d97cbb6"
)


class EvidenceError(RuntimeError):
    """Raised when a published evidence boundary is violated."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def read_regular(root: Path, relative_path: str) -> bytes:
    target = root / relative_path
    if target.is_symlink() or not target.is_file():
        raise EvidenceError(f"required regular file is missing: {relative_path}")
    return target.read_bytes()


def load_json(root: Path, relative_path: str) -> dict[str, Any]:
    try:
        value = json.loads(read_regular(root, relative_path))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"invalid JSON source: {relative_path}") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON object required: {relative_path}")
    return value


def write_json(root: Path, relative_path: str, value: Any) -> dict[str, Any]:
    target = root / relative_path
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise EvidenceError(f"refusing non-regular output: {relative_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.parent.is_symlink():
        raise EvidenceError(f"refusing symlink output directory: {relative_path}")
    payload = canonical_json_bytes(value)
    target.write_bytes(payload)
    return {
        "path": relative_path,
        "raw_sha256": sha256_bytes(payload),
        "byte_count": len(payload),
    }


def validate_source_provenance(repository_root: Path) -> list[dict[str, Any]]:
    archive_raw = read_regular(repository_root, ARCHIVE_PATH)
    if sha256_bytes(archive_raw) != ARCHIVE_SHA256:
        raise EvidenceError("M30 archival release digest mismatch")

    source_raw: dict[str, bytes] = {}
    for path, expected_digest in INPUT_DIGESTS.items():
        value = read_regular(repository_root, path)
        if sha256_bytes(value) != expected_digest:
            raise EvidenceError(f"published input digest mismatch: {path}")
        source_raw[path] = value

    for path, expected_digest in CURRENT_WORKFLOW_DIGESTS.items():
        value = read_regular(repository_root, path)
        if sha256_bytes(value) != expected_digest:
            raise EvidenceError(f"current workflow digest mismatch: {path}")

    with tarfile.open(repository_root / ARCHIVE_PATH, mode="r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise EvidenceError("duplicate M30 archive member")
        for member in members:
            pure = PurePosixPath(member.name)
            if pure.is_absolute() or ".." in pure.parts:
                raise EvidenceError(f"unsafe M30 archive member: {member.name}")
        for path, value in source_raw.items():
            member_name = f"{ARCHIVE_ROOT}/{path}"
            try:
                member = archive.getmember(member_name)
            except KeyError as exc:
                raise EvidenceError(
                    f"published M30 archive member is missing: {path}"
                ) from exc
            if not member.isfile() or member.issym() or member.islnk():
                raise EvidenceError(f"non-regular M30 archive member: {path}")
            stream = archive.extractfile(member)
            if stream is None or stream.read() != value:
                raise EvidenceError(f"M30 archive byte mismatch: {path}")

    provenance = [
        {
            "path": path,
            "raw_sha256": INPUT_DIGESTS[path],
            "byte_count": len(source_raw[path]),
            "m30_archive_member_verified": True,
        }
        for path in sorted(INPUT_DIGESTS)
    ]
    provenance.append(
        {
            "path": ARCHIVE_PATH,
            "raw_sha256": ARCHIVE_SHA256,
            "byte_count": len(archive_raw),
            "m30_archive_member_verified": False,
            "role": "immutable_archive_container",
        }
    )
    for path in sorted(CURRENT_WORKFLOW_DIGESTS):
        provenance.append(
            {
                "path": path,
                "raw_sha256": CURRENT_WORKFLOW_DIGESTS[path],
                "byte_count": len(read_regular(repository_root, path)),
                "m30_archive_member_verified": False,
                "role": "post_archive_full_core_qualification",
            }
        )
    return provenance


def run_historical_experiment(
    repository_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    command = [
        sys.executable,
        "frp_prototype_v0_9_3_mobile.py",
        "--mode",
        "bench",
        "--steps",
        "128",
        "--seeds",
        "5",
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUTF8": "1",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
        }
    )
    completed = subprocess.run(
        command,
        cwd=repository_root,
        env=environment,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise EvidenceError(
            "historical benchmark execution failed: "
            + completed.stderr.decode("utf-8", errors="replace")
        )
    if completed.stderr:
        raise EvidenceError("historical benchmark emitted stderr")
    stdout_digest = sha256_bytes(completed.stdout)
    if stdout_digest != EXPECTED_HISTORICAL_STDOUT_SHA256:
        raise EvidenceError("historical benchmark stdout digest mismatch")

    rows: dict[str, dict[str, Any]] = {}
    text = completed.stdout.decode("utf-8")
    for line in text.splitlines():
        if " | " not in line:
            continue
        columns = [column.strip() for column in line.split("|")]
        if len(columns) != 9 or columns[0] not in EXPECTED_HISTORICAL_ROWS:
            continue
        row = {
            "architecture_id": columns[0],
            "cases": int(columns[1]),
            "match": columns[2],
            "C_minus_P_min": columns[3],
            "heat_peak": columns[4],
            "switch_load_peak": columns[5],
            "actual_direct_events": int(columns[6]),
            "prevented_direct_events": int(columns[7]),
            "neutralized_conflicts": int(columns[8]),
        }
        rows[row["architecture_id"]] = row
    if rows != EXPECTED_HISTORICAL_ROWS:
        raise EvidenceError("historical benchmark row mismatch")

    ordered = [rows[name] for name in EXPECTED_HISTORICAL_ROWS]
    execution = {
        "command": [
            "python3",
            "frp_prototype_v0_9_3_mobile.py",
            "--mode",
            "bench",
            "--steps",
            "128",
            "--seeds",
            "5",
        ],
        "python_requirement": "3.12",
        "stdout_sha256": stdout_digest,
        "stdout_byte_count": len(completed.stdout),
        "exit_code": completed.returncode,
    }
    return ordered, execution


def build_active_zero_trace_evidence(repository_root: Path) -> dict[str, Any]:
    mode_counts: Counter[str] = Counter()
    state_counts: Counter[str] = Counter()
    transition_counts: Counter[str] = Counter()
    event_totals: Counter[str] = Counter()
    observed_values: set[int] = set()
    record_count = 0
    cell_observations = 0
    active_zero_after_observations = 0
    invariant_pass_records = 0
    contour_records: list[dict[str, Any]] = []

    for path in TRACE_PATHS:
        trace = load_json(repository_root, path)
        records = trace.get("records")
        summary = trace.get("summary")
        if not isinstance(records, list) or not isinstance(summary, dict):
            raise EvidenceError(f"trace record boundary is missing: {path}")
        if summary.get("record_count") != len(records):
            raise EvidenceError(f"trace record count mismatch: {path}")
        if [record.get("sequence") for record in records] != list(
            range(len(records))
        ):
            raise EvidenceError(f"trace sequence mismatch: {path}")
        summary_events = summary.get("event_totals")
        if not isinstance(summary_events, dict):
            raise EvidenceError(f"trace event summary is missing: {path}")
        event_totals.update(summary_events)
        contour_records.append(
            {
                "path": path,
                "raw_sha256": INPUT_DIGESTS[path],
                "record_count": len(records),
                "execution_epochs": trace.get("execution_epochs"),
            }
        )

        for record in records:
            record_count += 1
            scheduler = record.get("scheduler")
            invariants = record.get("invariants")
            if not isinstance(scheduler, dict):
                raise EvidenceError(f"scheduler record missing: {path}")
            mode_counts[scheduler.get("mode")] += 1
            state_counts[scheduler.get("state")] += 1
            if not isinstance(invariants, dict) or not invariants.get("all_pass"):
                raise EvidenceError(f"trace invariant failure: {path}")
            invariant_pass_records += 1

            before = record.get("retained_state_before")
            after = record.get("retained_state_after")
            if (
                not isinstance(before, list)
                or not isinstance(after, list)
                or len(before) != 8
                or len(after) != 8
            ):
                raise EvidenceError(f"retained-state vector mismatch: {path}")
            cell_observations += len(after)
            active_zero_after_observations += after.count(0)
            observed_values.update(before)
            observed_values.update(after)
            for previous, current in zip(before, after):
                if previous == current:
                    transition_counts["retained_same"] += 1
                elif previous in (-1, 1) and current == 0:
                    transition_counts["polarity_to_active_zero"] += 1
                elif previous == 0 and current in (-1, 1):
                    transition_counts["active_zero_to_polarity"] += 1
                elif (previous, current) in ((-1, 1), (1, -1)):
                    transition_counts["direct_opposite"] += 1
                else:
                    transition_counts["invalid"] += 1

    expected_modes = Counter({"free": 19, "1/7": 17, "7/1": 64})
    expected_states = Counter(
        {"free": 19, "excite": 3, "neutralize": 14, "balance": 56, "commit": 8}
    )
    expected_transitions = Counter(
        {
            "retained_same": 783,
            "polarity_to_active_zero": 5,
            "active_zero_to_polarity": 12,
        }
    )
    expected_events = Counter(
        {
            "requested_direct_events": 5,
            "prevented_direct_events": 5,
            "neutral_routed_events": 5,
            "actual_direct_events": 0,
            "reserved_state_events": 0,
            "queue_overflow_events": 0,
        }
    )
    if mode_counts != expected_modes:
        raise EvidenceError("full-core scheduler-mode evidence mismatch")
    if state_counts != expected_states:
        raise EvidenceError("full-core scheduler-state evidence mismatch")
    if transition_counts != expected_transitions:
        raise EvidenceError("full-core retained-transition evidence mismatch")
    if event_totals != expected_events:
        raise EvidenceError("full-core active-zero event evidence mismatch")
    if observed_values != {-1, 0, 1}:
        raise EvidenceError("full-core ternary domain evidence mismatch")
    if record_count != 100 or cell_observations != 800:
        raise EvidenceError("full-core observation count mismatch")
    if active_zero_after_observations != 702:
        raise EvidenceError("full-core active-zero observation mismatch")

    return {
        "evidence_class": "published_cycle_exact_execution_trace",
        "contours": contour_records,
        "record_count": record_count,
        "cell_observation_count": cell_observations,
        "active_zero_after_observation_count": active_zero_after_observations,
        "invariant_pass_records": invariant_pass_records,
        "observed_ternary_domain": [-1, 0, 1],
        "scheduler_mode_counts": {
            "free": mode_counts["free"],
            "1/7": mode_counts["1/7"],
            "7/1": mode_counts["7/1"],
        },
        "scheduler_state_counts": {
            name: state_counts[name]
            for name in ("free", "excite", "neutralize", "balance", "commit")
        },
        "retained_transition_counts": {
            "retained_same": transition_counts["retained_same"],
            "polarity_to_active_zero": transition_counts[
                "polarity_to_active_zero"
            ],
            "active_zero_to_polarity": transition_counts[
                "active_zero_to_polarity"
            ],
            "direct_opposite": transition_counts["direct_opposite"],
        },
        "event_totals": {
            name: event_totals[name]
            for name in (
                "requested_direct_events",
                "prevented_direct_events",
                "neutral_routed_events",
                "actual_direct_events",
                "reserved_state_events",
                "queue_overflow_events",
            )
        },
        "active_zero_roles": [
            "conflict_neutralization",
            "temporal_separation",
            "balancing",
            "damping",
            "transition_buffering",
            "switching_load_distribution",
            "retained_transition_continuity",
            "pending_route_completion_preparation",
            "stabilization",
        ],
    }


def build_current_comparative_contours(repository_root: Path) -> dict[str, Any]:
    baseline_path = (
        "benchmarks/architecture_comparison/results/"
        "reference_comparison_seed_76.json"
    )
    sensitivity_path = (
        "benchmarks/architecture_comparison/results/"
        "reference_comparison_seed_76_hardware_sensitivity_v1.json"
    )
    profile_path = (
        "benchmarks/architecture_comparison/profiles/"
        "thermal_proxy_profile_v1.json"
    )
    baseline = load_json(repository_root, baseline_path)
    sensitivity = load_json(repository_root, sensitivity_path)
    profile = load_json(repository_root, profile_path)

    if baseline.get("schema") != "frp.benchmark.architecture_comparison.v1":
        raise EvidenceError("comparative baseline schema mismatch")
    if baseline.get("architecture_order") != EXPECTED_ARCHITECTURE_ORDER:
        raise EvidenceError("comparative baseline architecture order mismatch")
    if baseline.get("frp_scheduler") != "7/1":
        raise EvidenceError("comparative baseline FRP scheduler mismatch")
    if baseline.get("integrity", {}).get("status") != "PASS":
        raise EvidenceError("comparative baseline integrity failed")
    if baseline.get("qualification", {}).get("status") != "PASS":
        raise EvidenceError("comparative baseline qualification failed")
    if baseline.get("qualification", {}).get("winner_assertions") != []:
        raise EvidenceError("comparative baseline winner assertion detected")

    if sensitivity.get("schema") != (
        "frp.benchmark.hardware_sensitivity_comparison.v1"
    ):
        raise EvidenceError("hardware-sensitivity schema mismatch")
    if sensitivity.get("architecture_order") != EXPECTED_ARCHITECTURE_ORDER:
        raise EvidenceError("hardware-sensitivity architecture order mismatch")
    if sensitivity.get("integrity", {}).get("status") != "PASS":
        raise EvidenceError("hardware-sensitivity integrity failed")
    if sensitivity.get("qualification", {}).get("status") != "PASS":
        raise EvidenceError("hardware-sensitivity qualification failed")
    if sensitivity.get("qualification", {}).get("winner_assertions") != []:
        raise EvidenceError("hardware-sensitivity winner assertion detected")

    embedded_profile = baseline.get("thermal_profile")
    if not isinstance(embedded_profile, dict):
        raise EvidenceError("shared thermal profile embedding is missing")
    for name in (
        "profile_name",
        "temperature_unit",
        "ambient_temperature_proxy",
        "thermal_decay",
        "thermal_gain",
    ):
        if embedded_profile.get(name) != profile.get(name):
            raise EvidenceError(
                f"shared thermal profile embedding mismatch: {name}"
            )
    if profile.get("temperature_unit") != "normalized_temperature_proxy":
        raise EvidenceError("shared thermal proxy unit mismatch")

    scenarios = sensitivity.get("scenarios")
    if not isinstance(scenarios, list):
        raise EvidenceError("hardware-sensitivity scenarios are missing")
    if [item.get("scenario_id") for item in scenarios] != [
        "lower_bound",
        "nominal",
        "upper_bound",
    ]:
        raise EvidenceError("hardware-sensitivity scenario order mismatch")
    scenario_summaries = []
    for scenario in scenarios:
        if scenario.get("integrity", {}).get("status") != "PASS":
            raise EvidenceError("hardware-sensitivity scenario failed")
        scenario_summaries.append(
            {
                "scenario_id": scenario["scenario_id"],
                "scenario_cost_profile_sha256": scenario[
                    "scenario_cost_profile_sha256"
                ],
                "comparison_matrix": scenario["comparison_matrix"],
                "ranking": scenario["ranking"],
            }
        )

    return {
        "measurement_class": "shared_model_comparative_benchmark",
        "physical_temperature_measurement": False,
        "historical_heat_peak_interchangeable": False,
        "baseline": {
            "source_path": baseline_path,
            "raw_sha256": INPUT_DIGESTS[baseline_path],
            "schema": baseline["schema"],
            "benchmark_kind": baseline["benchmark_kind"],
            "comparison_package_sha256": baseline[
                "comparison_package_sha256"
            ],
            "workload_sha256": baseline["workload_sha256"],
            "frp_scheduler": baseline["frp_scheduler"],
            "comparison_matrix": baseline["comparison_matrix"],
            "qualification_status": baseline["qualification"]["status"],
            "winner_assertions": [],
        },
        "thermal_profile": {
            "source_path": profile_path,
            "raw_sha256": INPUT_DIGESTS[profile_path],
            "profile_name": profile["profile_name"],
            "temperature_unit": profile["temperature_unit"],
            "ambient_temperature_proxy": profile[
                "ambient_temperature_proxy"
            ],
            "thermal_decay": profile["thermal_decay"],
            "thermal_gain": profile["thermal_gain"],
            "update_equation": profile["update_equation"],
            "thermal_profile_sha256": profile["thermal_profile_sha256"],
        },
        "hardware_sensitivity": {
            "source_path": sensitivity_path,
            "raw_sha256": INPUT_DIGESTS[sensitivity_path],
            "schema": sensitivity["schema"],
            "hardware_sensitivity_package_sha256": sensitivity[
                "hardware_sensitivity_package_sha256"
            ],
            "scenario_order": ["lower_bound", "nominal", "upper_bound"],
            "scenario_summaries": scenario_summaries,
            "ranking_stability": sensitivity["ranking_stability"],
            "qualification_status": sensitivity["qualification"]["status"],
            "winner_assertions": [],
        },
    }


def build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": (
            "https://frp.example/schemas/m31/"
            "frp.m31.phase_interference_active_zero_thermal_evidence.v1"
            ".schema.json"
        ),
        "title": "FRP M31 Phase-Interference Active-Zero Thermal Evidence",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema",
            "version",
            "milestone",
            "kind",
            "status",
            "core",
            "active_zero_execution_evidence",
            "historical_thermal_experiment",
            "current_comparative_thermal_contours",
            "evidence_boundaries",
            "observatory_publication_contract",
            "provenance",
        ],
        "properties": {
            "schema": {"const": SCHEMA_ID},
            "version": {"const": "1.0.0"},
            "milestone": {"const": MILESTONE},
            "kind": {
                "const": "phase_interference_active_zero_thermal_evidence"
            },
            "status": {"const": "PASS"},
            "core": {"type": "object"},
            "active_zero_execution_evidence": {"type": "object"},
            "historical_thermal_experiment": {"type": "object"},
            "current_comparative_thermal_contours": {"type": "object"},
            "evidence_boundaries": {"type": "object"},
            "observatory_publication_contract": {"type": "object"},
            "provenance": {
                "type": "array",
                "minItems": len(INPUT_DIGESTS) + 2,
                "items": {"type": "object"},
            },
        },
    }


def validate_evidence_document(document: dict[str, Any]) -> None:
    if set(document) != set(build_schema()["required"]):
        raise EvidenceError("M31 evidence top-level key mismatch")
    if document.get("schema") != SCHEMA_ID:
        raise EvidenceError("M31 evidence schema mismatch")
    if document.get("status") != "PASS":
        raise EvidenceError("M31 evidence status mismatch")
    core = document.get("core", {})
    if core.get("balanced_ternary_notation") != "-1/0/1":
        raise EvidenceError("M31 immutable ternary notation mismatch")
    if core.get("semantic_values") != [-1, 0, 1]:
        raise EvidenceError("M31 immutable ternary domain mismatch")
    if core.get("active_neutral_state") != 0:
        raise EvidenceError("M31 active neutral state mismatch")
    if core.get("temporal_scheduler_modes") != ["1/7", "7/1"]:
        raise EvidenceError("M31 temporal scheduler modes mismatch")
    if core.get("service_scheduler_mode") != "free":
        raise EvidenceError("M31 service scheduler mode mismatch")
    if core.get("classical_bit_addition_primary_mechanism") is not False:
        raise EvidenceError("M31 computation mechanism boundary mismatch")
    traces = document.get("active_zero_execution_evidence", {})
    if traces.get("retained_transition_counts", {}).get(
        "direct_opposite"
    ) != 0:
        raise EvidenceError("M31 direct opposite transition detected")
    experiment = document.get("historical_thermal_experiment", {})
    if experiment.get("physical_temperature_measurement") is not False:
        raise EvidenceError("M31 historical measurement boundary mismatch")
    focused = experiment.get("focused_binary_ternary_comparison", {})
    if focused.get("heat_peak_ratio_binary_over_active_neutral_ternary") != (
        "15.6923076923"
    ):
        raise EvidenceError("M31 historical heat ratio mismatch")
    if focused.get("heat_peak_relative_reduction_percent") != "93.63":
        raise EvidenceError("M31 historical heat reduction mismatch")
    boundary = document.get("observatory_publication_contract", {})
    if boundary.get("downstream_writeback") != "forbidden":
        raise EvidenceError("M31 Observatory writeback boundary mismatch")


def build_evidence(repository_root: Path) -> dict[str, Any]:
    provenance = validate_source_provenance(repository_root)
    historical_rows, execution = run_historical_experiment(repository_root)
    active_zero = build_active_zero_trace_evidence(repository_root)
    current = build_current_comparative_contours(repository_root)
    contract = load_json(
        repository_root,
        "artifacts/m29/contracts/m29-system-integration-contract.json",
    )
    integration = contract.get("integration_boundary")
    if not isinstance(integration, dict):
        raise EvidenceError("M29 integration boundary is missing")

    binary = EXPECTED_HISTORICAL_ROWS["binary_style_forced_switch"]
    neutral = EXPECTED_HISTORICAL_ROWS["distributed_neutral_ternary"]
    direct_ternary = EXPECTED_HISTORICAL_ROWS["direct_ternary_commit"]
    binary_heat = Decimal(binary["heat_peak"])
    neutral_heat = Decimal(neutral["heat_peak"])
    ratio = binary_heat / neutral_heat
    reduction = (binary_heat - neutral_heat) / binary_heat * Decimal("100")

    evidence = {
        "schema": SCHEMA_ID,
        "version": "1.0.0",
        "milestone": MILESTONE,
        "kind": "phase_interference_active_zero_thermal_evidence",
        "status": "PASS",
        "core": {
            "processor": "Fractal Resonance Processor",
            "balanced_ternary_notation": "-1/0/1",
            "semantic_values": [-1, 0, 1],
            "active_neutral_state": 0,
            "opposite_transition_routes": [[-1, 0, 1], [1, 0, -1]],
            "temporal_scheduler_modes": ["1/7", "7/1"],
            "service_scheduler_mode": "free",
            "classical_bit_addition_primary_mechanism": False,
            "primary_computational_organization": (
                "retained_relative_phase_interference_and_resonant_selection"
            ),
            "computation_chain": [
                "retained phase and frequency state",
                "relative-phase interaction",
                "phase organization and dispersion",
                "resonance selection",
                "multiscale coherence evaluation",
                "dynamic stability evaluation",
                "phase-derived ternary target",
                "distributed active-neutral commit",
                "retained coherent ternary state",
            ],
            "ternary_layer_role": (
                "discrete_state_target_transition_and_retained_result_boundary"
            ),
            "zero_role": "active_computational_state",
        },
        "active_zero_execution_evidence": active_zero,
        "historical_thermal_experiment": {
            "evidence_class": "reproduced_release_benchmark",
            "release": "FRP v0.9.3",
            "measurement_class": "release_specific_model_thermal_load",
            "physical_temperature_measurement": False,
            "metric_unit": "historical_model_heat_peak",
            "source_executable": "frp_prototype_v0_9_3_mobile.py",
            "source_report": "TEST_REPORT_v0_9_3.md",
            "execution": execution,
            "workload": {
                "cell_counts": [8, 16, 32, 64],
                "seeds": [0, 1, 2, 3, 4],
                "cycle_modes": ["free", "7/1", "1/7"],
                "operations": [
                    "neg",
                    "add",
                    "sub",
                    "compare",
                    "consensus",
                ],
                "steps": 128,
                "cases_per_architecture": 300,
            },
            "architecture_order": list(EXPECTED_HISTORICAL_ROWS),
            "rows": historical_rows,
            "focused_binary_ternary_comparison": {
                "binary_architecture_id": binary["architecture_id"],
                "active_neutral_ternary_architecture_id": neutral[
                    "architecture_id"
                ],
                "binary_heat_peak": binary["heat_peak"],
                "active_neutral_ternary_heat_peak": neutral["heat_peak"],
                "heat_peak_ratio_binary_over_active_neutral_ternary": (
                    str(ratio.quantize(Decimal("0.0000000001")))
                ),
                "heat_peak_relative_reduction_percent_exact": (
                    str(reduction.quantize(Decimal("0.0000000001")))
                ),
                "heat_peak_relative_reduction_percent": (
                    str(
                        reduction.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    )
                ),
                "binary_switch_load_peak": binary["switch_load_peak"],
                "active_neutral_ternary_switch_load_peak": neutral[
                    "switch_load_peak"
                ],
                "switch_load_ratio_binary_over_active_neutral_ternary": "4.0",
                "binary_actual_direct_events": binary[
                    "actual_direct_events"
                ],
                "active_neutral_ternary_actual_direct_events": neutral[
                    "actual_direct_events"
                ],
            },
            "observed_relations": {
                "direct_ternary_heat_peak_equals_binary": (
                    direct_ternary["heat_peak"] == binary["heat_peak"]
                ),
                "distributed_active_neutral_heat_peak_below_binary": (
                    neutral_heat < binary_heat
                ),
                "advantage_attached_to_distributed_active_neutral_topology": True,
                "advantage_attached_to_third_symbol_alone": False,
            },
            "winner_assertions": [],
        },
        "current_comparative_thermal_contours": current,
        "evidence_boundaries": {
            "historical_and_current_contours_separate": True,
            "historical_heat_peak_is_not_current_rc_temperature_proxy": True,
            "thermal_proxy_is_not_physical_temperature": True,
            "normalized_activity_cost_is_not_physical_energy": True,
            "operation_count_is_not_thermal_load": True,
            "scope_limited_relations_are_not_universal_winner_claims": True,
            "physical_measurement_required_for_silicon_temperature_claim": True,
        },
        "observatory_publication_contract": {
            "direction": "upstream_published_bytes_to_downstream",
            "upstream_repository": "FRP",
            "downstream_repository": "FRP-Trace-Observatory",
            "downstream_role": "read_only_validation_and_visualization",
            "downstream_writeback": "forbidden",
            "downstream_source_mutation": "forbidden",
            "downstream_semantic_reimplementation": "forbidden",
            "downstream_metric_normalization": "forbidden",
            "published_contours_must_remain_separate": True,
            "m29_boundary_confirmed": all(
                (
                    integration.get("downstream_writeback") == "forbidden",
                    integration.get("downstream_source_mutation") == "forbidden",
                    integration.get("downstream_semantic_reimplementation")
                    == "forbidden",
                )
            ),
        },
        "provenance": provenance,
    }
    validate_evidence_document(evidence)
    return evidence


def generate(repository_root: Path, output_root: Path) -> dict[str, Any]:
    evidence = build_evidence(repository_root)
    schema_record = write_json(output_root, SCHEMA_PATH, build_schema())
    evidence_record = write_json(output_root, EVIDENCE_PATH, evidence)
    manifest = {
        "schema": MANIFEST_SCHEMA_ID,
        "version": "1.0.0",
        "milestone": MILESTONE,
        "kind": "phase_interference_active_zero_thermal_evidence_manifest",
        "generated_files": [schema_record, evidence_record],
        "source_count": len(evidence["provenance"]),
        "historical_experiment_stdout_sha256": (
            evidence["historical_thermal_experiment"]["execution"][
                "stdout_sha256"
            ]
        ),
        "status": "PASS",
    }
    manifest_record = write_json(output_root, MANIFEST_PATH, manifest)
    qualification = {
        "schema": QUALIFICATION_SCHEMA_ID,
        "version": "1.0.0",
        "milestone": MILESTONE,
        "kind": "phase_interference_active_zero_thermal_evidence_qualification",
        "checks": {
            "source_digests_exact": True,
            "m30_archive_members_byte_identical": True,
            "historical_experiment_reproduced": True,
            "historical_rows_exact": True,
            "active_zero_trace_evidence_exact": True,
            "direct_opposite_transitions_zero": True,
            "ternary_notation_exact": True,
            "scheduler_modes_exact": True,
            "current_comparative_contours_integrity_pass": True,
            "thermal_measurement_contours_separate": True,
            "physical_temperature_claim_absent": True,
            "winner_assertions_absent": True,
            "observatory_boundary_read_only": True,
        },
        "outputs": [schema_record, evidence_record, manifest_record],
        "status": "PASS",
    }
    qualification_record = write_json(
        output_root, QUALIFICATION_PATH, qualification
    )
    return {
        "schema": "frp.m31.generation_result.v1",
        "milestone": MILESTONE,
        "outputs": [
            schema_record,
            evidence_record,
            manifest_record,
            qualification_record,
        ],
        "status": "PASS",
    }


def verify(repository_root: Path, output_root: Path) -> dict[str, Any]:
    expected_root = output_root / ".m31-verification-expected"
    if expected_root.exists():
        raise EvidenceError("M31 verification scratch path already exists")
    expected_root.mkdir(parents=True)
    try:
        expected = generate(repository_root, expected_root)
        verified = []
        for record in expected["outputs"]:
            path = record["path"]
            expected_raw = read_regular(expected_root, path)
            observed_raw = read_regular(output_root, path)
            if observed_raw != expected_raw:
                raise EvidenceError(f"M31 output byte mismatch: {path}")
            verified.append(
                {
                    "path": path,
                    "raw_sha256": sha256_bytes(observed_raw),
                    "byte_count": len(observed_raw),
                }
            )
    finally:
        for target in sorted(expected_root.rglob("*"), reverse=True):
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                target.rmdir()
        expected_root.rmdir()
    return {
        "schema": "frp.m31.verification_result.v1",
        "milestone": MILESTONE,
        "verified_outputs": verified,
        "status": "PASS",
    }


def self_test(repository_root: Path) -> dict[str, Any]:
    evidence_a = build_evidence(repository_root)
    evidence_b = build_evidence(repository_root)
    if canonical_json_bytes(evidence_a) != canonical_json_bytes(evidence_b):
        raise EvidenceError("M31 evidence replay is not deterministic")
    return {
        "schema": "frp.m31.self_test_result.v1",
        "milestone": MILESTONE,
        "checks": {
            "replay_byte_identical": True,
            "historical_experiment_reproduced_twice": True,
            "active_zero_is_computational": True,
            "classical_bit_addition_primary_mechanism": False,
            "thermal_contours_separate": True,
        },
        "evidence_sha256": sha256_bytes(canonical_json_bytes(evidence_a)),
        "status": "PASS",
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate or verify FRP M31 phase-interference, active-zero, "
            "and ternary-binary thermal evidence."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true")
    action.add_argument("--verify", action="store_true")
    action.add_argument("--self-test", action="store_true")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--output-root", default=".")
    parser.add_argument("--output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repository_root = Path(args.repository_root).resolve()
    output_root = Path(args.output_root).resolve()
    try:
        if args.generate:
            result = generate(repository_root, output_root)
        elif args.verify:
            result = verify(repository_root, output_root)
        else:
            result = self_test(repository_root)
    except (EvidenceError, OSError, ValueError) as exc:
        print(f"FRP M31 evidence failure: {exc}", file=sys.stderr)
        return 1
    payload = canonical_json_bytes(result)
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
