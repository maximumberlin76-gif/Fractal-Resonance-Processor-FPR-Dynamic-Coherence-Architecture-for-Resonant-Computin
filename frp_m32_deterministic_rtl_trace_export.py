#!/usr/bin/env python3
"""Produce the FRP M32 deterministic RTL trace publication boundary."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "frp.m32.deterministic_rtl_trace_bundle.v1"
MANIFEST_SCHEMA_ID = "frp.m32.deterministic_rtl_trace_manifest.v1"
QUALIFICATION_SCHEMA_ID = "frp.m32.deterministic_rtl_trace_qualification.v1"
MILESTONE = "M32"
VERSION = "1.0.0"
SOURCE_COMMIT = "c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941"
WORKFLOW_PATH = (
    ".github/workflows/"
    "frp-m32-registered-target-boundary-workflow.yml"
)
WORKFLOW_NAME = "FRP M32 Registered Target Core"
REPOSITORY_NAME = (
    "Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor"
)

SCHEMA_PATH = (
    "schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json"
)
BUNDLE_PATH = "artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json"
MANIFEST_PATH = (
    "artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json"
)
QUALIFICATION_PATH = (
    "artifacts/m32/qualification/"
    "m32-deterministic-rtl-trace-qualification.json"
)

CANONICAL_TERNARY_NOTATION = "-1/0/1"
CANONICAL_TERNARY_DOMAIN = [-1, 0, 1]
TERNARY_CODE_TO_VALUE = {0: 0, 1: 1, 3: -1}
SCHEDULER_MODE_LABELS = {1: "7/1", 2: "1/7"}
SCHEDULER_STATE_LABELS = {
    1: "balance",
    2: "commit",
    3: "excite",
    4: "neutralize",
}
CELLS = 8
REQUEST_LANES = 2
INVARIANT_FLAGS_HEX = "3ff"

SOURCE_IDENTITIES: dict[str, tuple[int, str]] = {
    "rtl/m31/frp_m31_pkg.sv": (
        18531,
        "762302f1c7a7f7f40cb029f5ada6a111fc8c3e3f6be9920e9b2401b95e179c94",
    ),
    "rtl/m31/frp_m31_fixed_point_pkg.sv": (
        7278,
        "6b2afb8d1583c93d95d2386ba25dd1eaef6bb5bd9a4e1c9e9abff1dd004cbf24",
    ),
    "rtl/m31/frp_m31_scheduler.sv": (
        10560,
        "fc9de24b41736e5c5a9f9e464318c80adbfda9dc8cc4362c0c55bfed403bf97f",
    ),
    "rtl/m31/frp_m31_request_lanes.sv": (
        18290,
        "32f75cc70df5dba3f4fbb511397be9a5921236c2afd16cfeb1350eca3f6e8109",
    ),
    "rtl/m31/frp_m31_pending_routes.sv": (
        17005,
        "18889d85e78b23b844f1db4c46a35a6b7d01e609e3f1f0e6263a39a6c5729411",
    ),
    "rtl/m31/frp_m31_active_neutral.sv": (
        25909,
        "765429b33df3f843626bdc411ad8371fd963738a58ab10201abef75dcdafcaf0",
    ),
    "rtl/m31/frp_m31_capacity_guard.sv": (
        20787,
        "d0587897f955ce49923aca807b5d3e0c637383c88e5d5e0dfa8405f47917c123",
    ),
    "rtl/m31/frp_m31_state_update.sv": (
        18147,
        "ebad1f7ee952a577239445d33d99cae799afaaff5c181c7162514bbcea6eab90",
    ),
    "rtl/m31/frp_m31_execution_core.sv": (
        33724,
        "e516a5cd378bd2ddecdadc5abb13ddef26c63fafe5bda65b47a6bd859ca66f92",
    ),
    "rtl/m31/frp_m31_phase_interference.sv": (
        11245,
        "e8ceb80feb0b30db5e28d70bc4d68d51506da4d596b46a73c0137465d1455fe0",
    ),
    "rtl/m31/frp_m31_phase_request_adapter.sv": (
        2251,
        "fa78bcfe965270cc74855908aa392989d857575a2097a126539aabb1aab8990d",
    ),
    "rtl/m31/frp_m31_thermal_proxy.sv": (
        1883,
        "34df4ebfc5dfad8e3e5e454e560404585de5c881e6f75abaae367d3bd9fb11bd",
    ),
    "rtl/m31/frp_m31_stability.sv": (
        2203,
        "69c06833e6dfbb28e25b74a5787dcd03756dddf0f66726de3ea47c1ad2931931",
    ),
    "rtl/m31/frp_m31_assertions.sv": (
        24366,
        "16a6abea57d2161a58ad5660c62f86cf057e65dbb1d9ae76e355e912a378077b",
    ),
    "rtl/m31/frp_m31_phase_thermal_assertions.sv": (
        3783,
        "fe7b06073e65fc64acf7232038911230db27fe3a5ce000d0e1d421e2f49b1b3b",
    ),
    "rtl/m31/frp_m31_sin_q30.mem": (
        36864,
        "adbb4b94fcf8fa0bfc981d654679fd7518a5c4c9c97b611a35cd8accaf28233d",
    ),
    "rtl/m32/frp_m32_registered_target_boundary.sv": (
        3947,
        "9626474b49d32b411e107d7ccc8ee5aa7f42728e9a6f70d634d16d3f2a414c5e",
    ),
    "rtl/m32/frp_m32_registered_target_boundary_tb.sv": (
        6748,
        "0824e781f276f325aa86bb9a6a136f1d4da910920b64d15fafe5d7d017e5288a",
    ),
    "rtl/m32/frp_m32_registered_target_request_path.sv": (
        3244,
        "02250069a68737f055a419cd67bf2d439b3f63b3f6a7a245f40e9bf29d1958eb",
    ),
    "rtl/m32/frp_m32_registered_target_request_path_tb.sv": (
        12135,
        "a615d9b3bd456f60b37715433862830a4f3f8170859a2b12415d4b4b071faea5",
    ),
    "rtl/m32/frp_m32_core.sv": (
        10564,
        "925342326b7ad555a1382e8ee3bc5754ed3012ba60e0eabf512113731e0ee6c9",
    ),
    "rtl/m32/frp_m32_core_tb.sv": (
        19348,
        "4a2ac2778192199d02700c324da7d0cfba4a2f83730ea148497099e1a640d800",
    ),
    "rtl/m32/frp_m32_mode_7_1_tb.sv": (
        22207,
        "7a6d610435bbd3f11441cb518bb64ab05b3748f5bb866092b1a734eab99c08f8",
    ),
    "rtl/m32/frp_m32_mode_1_7_tb.sv": (
        22388,
        "3dcd66dbd8edc6989294298adb14d4e3b314e0af62512b5a1398b789cb510b97",
    ),
    "rtl/m32/frp_m32_trace_monitor.sv": (
        13827,
        "556dd0759d91188b1947ae3abf61a0606cec238b67ff268f243eab370b01fc7c",
    ),
    "rtl/m32/frp_m32_mode_7_1_trace_tb.sv": (
        13136,
        "4d02db27a3ae080c7c2a029e27d1b2c66bdbd2ad35c64ad3e020792c0bb841ca",
    ),
    "rtl/m32/frp_m32_mode_1_7_trace_tb.sv": (
        13136,
        "bfb4b58f95f09e2fcbb81df3fae1c452a2e83111da7a9076dfaaefd2d76ab6cb",
    ),
    "formal/m32/frp_m32_registered_target_boundary_formal.sv": (
        7698,
        "b4880df9c8ca6a3f220a26d4937c14b63e3b97277cdff16ce50de725c7f840d2",
    ),
    WORKFLOW_PATH: (
        41712,
        "c0e3a9d134201d1d4d855f43d5740138155291d2074663207456841a08470afe",
    ),
}


@dataclass(frozen=True)
class TraceProfile:
    mode: str
    mode_code: int
    source_prefix: str
    samples: int
    scheduler_counts: dict[str, int]
    active_zero_observations: int
    transcript_bytes: int
    transcript_sha256: str
    pass_record: str
    base_pass_record: str
    run_names: tuple[str, str]

    @property
    def bank_records(self) -> int:
        return self.samples

    @property
    def cell_records(self) -> int:
        return self.samples * CELLS

    @property
    def request_records(self) -> int:
        return self.samples * REQUEST_LANES

    @property
    def total_records(self) -> int:
        return (
            self.samples
            + self.bank_records
            + self.cell_records
            + self.request_records
        )


TRACE_PROFILES: dict[str, TraceProfile] = {
    "7/1": TraceProfile(
        mode="7/1",
        mode_code=1,
        source_prefix="M32_MODE_7_1_TRACE",
        samples=16,
        scheduler_counts={"balance": 14, "commit": 2},
        active_zero_observations=115,
        transcript_bytes=105702,
        transcript_sha256=(
            "9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915"
        ),
        pass_record="FRP_M32_MODE_7_1_TRACE_TB: PASS samples=16",
        base_pass_record="FRP_M32_REGISTERED_TARGET_MODE_7_1_TB: PASS",
        run_names=(
            "m32-mode-7-1-full-trace-run-1.log",
            "m32-mode-7-1-full-trace-run-2.log",
        ),
    ),
    "1/7": TraceProfile(
        mode="1/7",
        mode_code=2,
        source_prefix="M32_MODE_1_7_TRACE",
        samples=17,
        scheduler_counts={"excite": 3, "neutralize": 14},
        active_zero_observations=123,
        transcript_bytes=112364,
        transcript_sha256=(
            "41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89"
        ),
        pass_record="FRP_M32_MODE_1_7_TRACE_TB: PASS samples=17",
        base_pass_record="FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS",
        run_names=(
            "m32-mode-1-7-full-trace-run-1.log",
            "m32-mode-1-7-full-trace-run-2.log",
        ),
    ),
}

SAMPLE_KEYS = (
    "source_tick",
    "tick_enable",
    "clear_counters",
    "phase_load_valid",
    "auto_target_enable",
    "scheduler_mode",
    "scheduler_state",
    "balance_tick",
    "commit_tick",
    "excite_tick",
    "neutralize_tick",
    "registered_target_valid",
    "phase_target_domain_valid",
    "registered_target_domain_valid",
    "capture_accepted",
    "capture_rejected",
    "registered_request_enable",
    "accepted_capture_events",
    "rejected_capture_events",
    "ticks_recorded",
    "scheduler_free",
    "scheduler_balance",
    "scheduler_commit",
    "scheduler_excite",
    "scheduler_neutralize",
    "accepted_changes",
    "capacity_remaining",
    "capacity_exhausted",
    "switch_load_numerator",
    "requested_direct_events",
    "prevented_direct_events",
    "neutral_routed_events",
    "actual_direct_events",
    "reserved_state_events",
    "queue_overflow_events",
    "invariant_flags",
    "invariant_all_valid",
    "pair_phase_order_q30",
    "cluster_phase_order_q30",
    "global_phase_order_q30",
    "organization_dispersion_q30",
    "normalized_cycle_cost_q16",
    "temperature_proxy_q16",
    "peak_temperature_proxy_q16",
    "thermal_sample_count",
    "coherence_capacity_q16",
    "pressure_q16",
    "stability_margin_q16",
    "stable",
)

SAMPLE_BOOLEAN_KEYS = {
    "tick_enable",
    "clear_counters",
    "phase_load_valid",
    "auto_target_enable",
    "balance_tick",
    "commit_tick",
    "excite_tick",
    "neutralize_tick",
    "registered_target_valid",
    "phase_target_domain_valid",
    "registered_target_domain_valid",
    "capture_accepted",
    "capture_rejected",
    "registered_request_enable",
    "capacity_exhausted",
    "invariant_all_valid",
    "stable",
}

BANK_KEYS = (
    "source_tick",
    "phase_target_source",
    "registered_target",
    "execution_target",
    "retained_state",
    "pending_route",
    "accepted_cell_mask",
    "neutral_routed_cell_mask",
    "accepted_change_mask",
    "first_route_leg_mask",
    "second_route_leg_mask",
)

CELL_KEYS = (
    "source_tick",
    "source_cell",
    "phase_word",
    "frequency_current_q16",
    "gamma_effective_word",
    "thermal_node_factor_q30",
    "coupling_field_q16",
    "phase_projection_q30",
    "source_target_code",
    "source_target_value",
    "registered_target_code",
    "registered_target_value",
    "execution_target_code",
    "execution_target_value",
    "retained_state_code",
    "retained_state_value",
    "active_zero",
    "pending_target_code",
    "pending_target_value",
    "pending_active",
    "accepted_cell",
    "neutral_routed",
    "state_changed",
    "first_route_leg",
    "second_route_leg",
)

CELL_BOOLEAN_KEYS = {
    "active_zero",
    "pending_active",
    "accepted_cell",
    "neutral_routed",
    "state_changed",
    "first_route_leg",
    "second_route_leg",
}

CELL_HEX_KEYS = {"phase_word", "gamma_effective_word"}

CELL_TERNARY_CODE_KEYS = {
    "source_target_code",
    "registered_target_code",
    "execution_target_code",
    "retained_state_code",
    "pending_target_code",
}

REQUEST_KEYS = (
    "source_tick",
    "request_lane",
    "phase_valid",
    "phase_cell",
    "phase_target_code",
    "phase_target_value",
    "execution_valid",
    "execution_cell",
    "execution_target_code",
    "execution_target_value",
    "accepted",
    "rejected",
)

REQUEST_BOOLEAN_KEYS = {
    "phase_valid",
    "execution_valid",
    "accepted",
    "rejected",
}

REQUEST_TERNARY_CODE_KEYS = {
    "phase_target_code",
    "execution_target_code",
}

LEGACY_COMMON_KEYS = {
    "tick",
    "scheduler_state",
    "source_target",
    "registered_target",
    "registered_valid",
    "capture_accepted",
    "execution_target",
    "request_valid",
    "first_leg",
    "second_leg",
    "executed_state",
    "active_zero",
    "pending_target",
}

HEX_PATTERN = re.compile(r"^[0-9a-f]+$")
HEX_32_PATTERN = re.compile(r"^[0-9a-f]{8}$")
FIELD_PATTERN = re.compile(r"^(?P<key>[a-z0-9_]+)=(?P<value>\S+)$")


class TraceExportError(RuntimeError):
    """Raised when an M32 trace publication invariant is violated."""


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


def read_regular(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise TraceExportError(f"required regular file is missing: {path}")
    return path.read_bytes()


def write_json(root: Path, relative_path: str, value: Any) -> dict[str, Any]:
    target = root / relative_path
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise TraceExportError(f"refusing non-regular output: {relative_path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.parent.is_symlink():
        raise TraceExportError(f"refusing symlink output directory: {relative_path}")
    payload = canonical_json_bytes(value)
    target.write_bytes(payload)
    return {
        "path": relative_path,
        "byte_count": len(payload),
        "raw_sha256": sha256_bytes(payload),
    }


def parse_decimal(value: str, field: str) -> int:
    if not re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
        raise TraceExportError(f"invalid decimal value for {field}: {value}")
    return int(value, 10)


def parse_boolean(value: str, field: str) -> bool:
    parsed = parse_decimal(value, field)
    if parsed not in (0, 1):
        raise TraceExportError(f"binary flag required for {field}: {value}")
    return bool(parsed)


def parse_hex(value: str, field: str, *, width: int | None = None) -> str:
    if not HEX_PATTERN.fullmatch(value):
        raise TraceExportError(f"lowercase hexadecimal value required for {field}")
    if width is not None and len(value) != width:
        raise TraceExportError(f"{field} must contain exactly {width} hex digits")
    return value


def parse_ternary_code(value: str, field: str) -> int:
    code_text = parse_hex(value, field)
    code = int(code_text, 16)
    if code not in TERNARY_CODE_TO_VALUE:
        raise TraceExportError(f"reserved or invalid ternary code in {field}")
    return code


def parse_fields(line: str, prefix: str, expected_keys: Iterable[str]) -> dict[str, str]:
    marker = f"{prefix} "
    if not line.startswith(marker):
        raise TraceExportError(f"trace prefix mismatch: {prefix}")

    fields: dict[str, str] = {}
    for token in line[len(marker) :].split(" "):
        match = FIELD_PATTERN.fullmatch(token)
        if match is None:
            raise TraceExportError(f"invalid trace token: {token}")
        key = match.group("key")
        if key in fields:
            raise TraceExportError(f"duplicate trace field: {key}")
        fields[key] = match.group("value")

    expected = set(expected_keys)
    if set(fields) != expected:
        missing = sorted(expected - set(fields))
        extra = sorted(set(fields) - expected)
        raise TraceExportError(
            f"trace field mismatch for {prefix}: missing={missing}, extra={extra}"
        )
    return fields


def parse_sample(line: str) -> dict[str, Any]:
    raw = parse_fields(line, "M32_TRACE_SAMPLE", SAMPLE_KEYS)
    record: dict[str, Any] = {}
    for key in SAMPLE_KEYS:
        if key in SAMPLE_BOOLEAN_KEYS:
            record[key] = parse_boolean(raw[key], key)
        elif key == "invariant_flags":
            record["invariant_flags_hex"] = parse_hex(raw[key], key)
        elif key == "scheduler_mode":
            mode_code = parse_decimal(raw[key], key)
            if mode_code not in SCHEDULER_MODE_LABELS:
                raise TraceExportError("unsupported scheduler mode code")
            record["scheduler_mode_code"] = mode_code
            record["scheduler_mode"] = SCHEDULER_MODE_LABELS[mode_code]
        elif key == "scheduler_state":
            state_code = parse_decimal(raw[key], key)
            if state_code not in SCHEDULER_STATE_LABELS:
                raise TraceExportError("unsupported scheduler state code")
            record["scheduler_state_code"] = state_code
            record["scheduler_state"] = SCHEDULER_STATE_LABELS[state_code]
        else:
            record[key] = parse_decimal(raw[key], key)
    return record


def parse_bank(line: str) -> dict[str, Any]:
    raw = parse_fields(line, "M32_TRACE_BANK", BANK_KEYS)
    record: dict[str, Any] = {"source_tick": parse_decimal(raw["source_tick"], "source_tick")}
    for key in BANK_KEYS[1:]:
        record[f"{key}_hex"] = parse_hex(raw[key], key)
    return record


def parse_cell(line: str) -> dict[str, Any]:
    raw = parse_fields(line, "M32_TRACE_CELL", CELL_KEYS)
    record: dict[str, Any] = {}
    for key in CELL_KEYS:
        if key in CELL_BOOLEAN_KEYS:
            record[key] = parse_boolean(raw[key], key)
        elif key in CELL_HEX_KEYS:
            record[f"{key}_hex"] = parse_hex(raw[key], key, width=8)
        elif key in CELL_TERNARY_CODE_KEYS:
            record[key] = parse_ternary_code(raw[key], key)
        else:
            record[key] = parse_decimal(raw[key], key)
    return record


def parse_request(line: str) -> dict[str, Any]:
    raw = parse_fields(line, "M32_TRACE_REQUEST", REQUEST_KEYS)
    record: dict[str, Any] = {}
    for key in REQUEST_KEYS:
        if key in REQUEST_BOOLEAN_KEYS:
            record[key] = parse_boolean(raw[key], key)
        elif key in REQUEST_TERNARY_CODE_KEYS:
            record[key] = parse_ternary_code(raw[key], key)
        else:
            record[key] = parse_decimal(raw[key], key)
    return record


def legacy_expected_keys(profile: TraceProfile) -> set[str]:
    cadence = {"balance_tick", "commit_tick"}
    if profile.mode == "1/7":
        cadence = {"excite_tick", "neutralize_tick"}
    return LEGACY_COMMON_KEYS | cadence


def parse_legacy(line: str, profile: TraceProfile) -> dict[str, Any]:
    raw = parse_fields(line, profile.source_prefix, legacy_expected_keys(profile))
    result: dict[str, Any] = {}
    for key, value in raw.items():
        if key.endswith("_tick") or key in {
            "registered_valid",
            "capture_accepted",
            "request_valid",
            "first_leg",
            "second_leg",
            "active_zero",
        }:
            result[key] = parse_boolean(value, key)
        else:
            result[key] = parse_decimal(value, key)
    return result


def verify_trace_identity(raw: bytes, profile: TraceProfile) -> None:
    if len(raw) != profile.transcript_bytes:
        raise TraceExportError(f"{profile.mode} transcript byte count mismatch")
    if sha256_bytes(raw) != profile.transcript_sha256:
        raise TraceExportError(f"{profile.mode} transcript SHA-256 mismatch")
    if not raw.endswith(b"\n") or b"\r" in raw or b"\x00" in raw:
        raise TraceExportError(f"{profile.mode} transcript byte format mismatch")


def transcript_identity(profile: TraceProfile, run_index: int) -> dict[str, Any]:
    return {
        "scheduler_mode": profile.mode,
        "replay": run_index,
        "artifact_member_path": profile.run_names[run_index - 1],
        "byte_count": profile.transcript_bytes,
        "raw_sha256": profile.transcript_sha256,
    }


def cross_check_legacy_record(
    legacy: dict[str, Any],
    sample: dict[str, Any],
    cell_zero: dict[str, Any],
) -> None:
    checks = {
        "tick": sample["source_tick"],
        "scheduler_state": sample["scheduler_state_code"],
        "source_target": cell_zero["source_target_value"],
        "registered_target": cell_zero["registered_target_value"],
        "registered_valid": sample["registered_target_valid"],
        "capture_accepted": sample["capture_accepted"],
        "execution_target": cell_zero["execution_target_value"],
        "first_leg": cell_zero["first_route_leg"],
        "second_leg": cell_zero["second_route_leg"],
        "executed_state": cell_zero["retained_state_value"],
        "active_zero": cell_zero["active_zero"],
        "pending_target": cell_zero["pending_target_value"],
    }
    for key, expected in checks.items():
        if legacy[key] != expected:
            raise TraceExportError(f"legacy/full trace mismatch: {key}")


def unpack_code(packed_hex: str, cell_index: int) -> int:
    return (int(packed_hex, 16) >> (cell_index * 2)) & 0b11


def unpack_mask(packed_hex: str, cell_index: int) -> bool:
    return bool((int(packed_hex, 16) >> cell_index) & 1)


def validate_code_value(record: dict[str, Any], code_key: str, value_key: str) -> None:
    code = record[code_key]
    if code not in TERNARY_CODE_TO_VALUE:
        raise TraceExportError(f"invalid ternary code: {code_key}")
    if record[value_key] != TERNARY_CODE_TO_VALUE[code]:
        raise TraceExportError(f"ternary code/value mismatch: {value_key}")


def validate_tick_record(record: dict[str, Any], profile: TraceProfile) -> None:
    tick = record["source_tick"]
    sample = record["sample"]
    bank = record["bank"]
    cells = record["cells"]
    requests = record["requests"]

    if sample["source_tick"] != tick or bank["source_tick"] != tick:
        raise TraceExportError("sample/bank source coordinate mismatch")
    if sample["scheduler_mode"] != profile.mode:
        raise TraceExportError("scheduler mode label mismatch")
    if sample["scheduler_mode_code"] != profile.mode_code:
        raise TraceExportError("scheduler mode code mismatch")
    if not sample["tick_enable"]:
        raise TraceExportError("published trace requires an enabled source tick")
    if sample["invariant_flags_hex"] != INVARIANT_FLAGS_HEX:
        raise TraceExportError("invariant flag vector mismatch")
    if not sample["invariant_all_valid"]:
        raise TraceExportError("trace contains an invalid invariant state")
    if sample["actual_direct_events"] != 0:
        raise TraceExportError("direct opposite-polarity execution observed")
    if sample["reserved_state_events"] != 0:
        raise TraceExportError("reserved ternary state event observed")
    if sample["queue_overflow_events"] != 0:
        raise TraceExportError("request queue overflow observed")

    expected_flags = {
        "balance_tick": sample["scheduler_state"] == "balance",
        "commit_tick": sample["scheduler_state"] == "commit",
        "excite_tick": sample["scheduler_state"] == "excite",
        "neutralize_tick": sample["scheduler_state"] == "neutralize",
    }
    for key, expected in expected_flags.items():
        if sample[key] is not expected:
            raise TraceExportError(f"scheduler state flag mismatch: {key}")

    if len(cells) != CELLS:
        raise TraceExportError("cell record count mismatch")
    if [cell["source_cell"] for cell in cells] != list(range(CELLS)):
        raise TraceExportError("cell source coordinate order mismatch")
    if len(requests) != REQUEST_LANES:
        raise TraceExportError("request record count mismatch")
    if [item["request_lane"] for item in requests] != list(range(REQUEST_LANES)):
        raise TraceExportError("request source coordinate order mismatch")

    bank_code_fields = {
        "phase_target_source_hex": "source_target_code",
        "registered_target_hex": "registered_target_code",
        "execution_target_hex": "execution_target_code",
        "retained_state_hex": "retained_state_code",
        "pending_route_hex": "pending_target_code",
    }
    bank_mask_fields = {
        "accepted_cell_mask_hex": "accepted_cell",
        "neutral_routed_cell_mask_hex": "neutral_routed",
        "accepted_change_mask_hex": "state_changed",
        "first_route_leg_mask_hex": "first_route_leg",
        "second_route_leg_mask_hex": "second_route_leg",
    }

    for cell in cells:
        if cell["source_tick"] != tick:
            raise TraceExportError("cell source tick mismatch")
        if not HEX_32_PATTERN.fullmatch(cell["phase_word_hex"]):
            raise TraceExportError("phase word width mismatch")
        if not HEX_32_PATTERN.fullmatch(cell["gamma_effective_word_hex"]):
            raise TraceExportError("effective gamma word width mismatch")

        for prefix in (
            "source_target",
            "registered_target",
            "execution_target",
            "retained_state",
            "pending_target",
        ):
            validate_code_value(cell, f"{prefix}_code", f"{prefix}_value")

        if cell["active_zero"] is not (cell["retained_state_value"] == 0):
            raise TraceExportError("active state 0 marker mismatch")
        if cell["pending_active"] is not (cell["pending_target_value"] != 0):
            raise TraceExportError("pending route marker mismatch")
        if cell["first_route_leg"] and cell["second_route_leg"]:
            raise TraceExportError("route legs merged into one source tick")

        cell_index = cell["source_cell"]
        for bank_key, cell_key in bank_code_fields.items():
            if unpack_code(bank[bank_key], cell_index) != cell[cell_key]:
                raise TraceExportError(f"packed bank mismatch: {bank_key}")
        for bank_key, cell_key in bank_mask_fields.items():
            if unpack_mask(bank[bank_key], cell_index) is not cell[cell_key]:
                raise TraceExportError(f"packed mask mismatch: {bank_key}")

    for request in requests:
        if request["source_tick"] != tick:
            raise TraceExportError("request source tick mismatch")
        if not 0 <= request["phase_cell"] < CELLS:
            raise TraceExportError("phase request cell coordinate out of range")
        if not 0 <= request["execution_cell"] < CELLS:
            raise TraceExportError("execution request cell coordinate out of range")
        validate_code_value(request, "phase_target_code", "phase_target_value")
        validate_code_value(request, "execution_target_code", "execution_target_value")
        if request["accepted"] and request["rejected"]:
            raise TraceExportError("request cannot be accepted and rejected together")


def validate_trace_records(trace: dict[str, Any], profile: TraceProfile) -> None:
    records = trace["records"]
    if len(records) != profile.samples:
        raise TraceExportError("source tick count mismatch")
    if [record["source_tick"] for record in records] != list(range(profile.samples)):
        raise TraceExportError("source ticks must be consecutive and zero-based")

    for record in records:
        validate_tick_record(record, profile)

    scheduler_counts: dict[str, int] = {}
    active_zero_count = 0
    first_leg_coordinates: list[tuple[int, int]] = []
    second_leg_coordinates: list[tuple[int, int]] = []
    frequency_values: set[int] = set()
    interference_values: set[int] = set()
    phase_values: set[str] = set()
    phase_target_execution_difference = False
    registered_target_execution_difference = False

    previous_states: list[int] | None = None
    for record in records:
        state = record["sample"]["scheduler_state"]
        scheduler_counts[state] = scheduler_counts.get(state, 0) + 1
        current_states = []
        for cell in record["cells"]:
            current_states.append(cell["retained_state_value"])
            phase_values.add(cell["phase_word_hex"])
            frequency_values.add(cell["frequency_current_q16"])
            interference_values.add(cell["coupling_field_q16"])
            if cell["source_target_value"] != cell["retained_state_value"]:
                phase_target_execution_difference = True
            if cell["registered_target_value"] != cell["retained_state_value"]:
                registered_target_execution_difference = True
            if cell["active_zero"]:
                active_zero_count += 1
            coordinate = (record["source_tick"], cell["source_cell"])
            if cell["first_route_leg"]:
                first_leg_coordinates.append(coordinate)
            if cell["second_route_leg"]:
                second_leg_coordinates.append(coordinate)

        if previous_states is not None:
            for before, after in zip(previous_states, current_states, strict=True):
                if (before, after) in {(-1, 1), (1, -1)}:
                    raise TraceExportError("direct opposite-polarity transition observed")
        previous_states = current_states

    if scheduler_counts != profile.scheduler_counts:
        raise TraceExportError("scheduler cadence count mismatch")
    if active_zero_count != profile.active_zero_observations:
        raise TraceExportError("active state 0 observation count mismatch")
    if len(first_leg_coordinates) != 1 or len(second_leg_coordinates) != 1:
        raise TraceExportError("expected one observation of each route leg")
    if first_leg_coordinates[0] == second_leg_coordinates[0]:
        raise TraceExportError("route legs are not separately observable")
    if len(phase_values) <= CELLS:
        raise TraceExportError("phase evolution is not observable")
    if len(frequency_values) < 2:
        raise TraceExportError("retained-frequency dynamics are not observable")
    if len(interference_values) < 2:
        raise TraceExportError("relative-phase interference is not observable")
    if not phase_target_execution_difference:
        raise TraceExportError("phase-derived target and execution are not distinguishable")
    if not registered_target_execution_difference:
        raise TraceExportError("registered target and execution are not distinguishable")

    trace["scheduler_state_counts"] = scheduler_counts
    trace["active_zero_cell_observation_count"] = active_zero_count
    trace["first_route_leg_coordinates"] = [
        {"source_tick": tick, "source_cell": cell}
        for tick, cell in first_leg_coordinates
    ]
    trace["second_route_leg_coordinates"] = [
        {"source_tick": tick, "source_cell": cell}
        for tick, cell in second_leg_coordinates
    ]


def parse_transcript(raw: bytes, profile: TraceProfile) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TraceExportError("trace transcript is not UTF-8") from exc

    samples: dict[int, dict[str, Any]] = {}
    banks: dict[int, dict[str, Any]] = {}
    cells: dict[int, list[dict[str, Any]]] = {}
    requests: dict[int, list[dict[str, Any]]] = {}
    legacy: dict[int, dict[str, Any]] = {}
    pass_count = 0
    base_pass_count = 0

    for line in text.splitlines():
        if line.startswith("M32_TRACE_SAMPLE "):
            record = parse_sample(line)
            tick = record["source_tick"]
            if tick in samples:
                raise TraceExportError("duplicate sample record")
            samples[tick] = record
        elif line.startswith("M32_TRACE_BANK "):
            record = parse_bank(line)
            tick = record["source_tick"]
            if tick in banks:
                raise TraceExportError("duplicate bank record")
            banks[tick] = record
        elif line.startswith("M32_TRACE_CELL "):
            record = parse_cell(line)
            cells.setdefault(record["source_tick"], []).append(record)
        elif line.startswith("M32_TRACE_REQUEST "):
            record = parse_request(line)
            requests.setdefault(record["source_tick"], []).append(record)
        elif line.startswith(f"{profile.source_prefix} "):
            record = parse_legacy(line, profile)
            tick = record["tick"]
            if tick in legacy:
                raise TraceExportError("duplicate scheduler trace record")
            legacy[tick] = record
        elif line == profile.pass_record:
            pass_count += 1
        elif line == profile.base_pass_record:
            base_pass_count += 1
        elif line.startswith("- rtl/m32/") and line.endswith("Verilog $finish"):
            continue
        elif line.startswith("M32_") or "PASS" in line:
            raise TraceExportError(f"unexpected M32 transcript record: {line}")

    expected_ticks = set(range(profile.samples))
    for name, records in (
        ("sample", samples),
        ("bank", banks),
        ("cell", cells),
        ("request", requests),
        ("scheduler", legacy),
    ):
        if set(records) != expected_ticks:
            raise TraceExportError(f"{name} source tick coverage mismatch")
    if pass_count != 1 or base_pass_count != 1:
        raise TraceExportError("testbench pass record count mismatch")

    tick_records: list[dict[str, Any]] = []
    for tick in range(profile.samples):
        cell_records = sorted(cells[tick], key=lambda item: item["source_cell"])
        request_records = sorted(
            requests[tick], key=lambda item: item["request_lane"]
        )
        record = {
            "source_tick": tick,
            "sample": samples[tick],
            "bank": banks[tick],
            "cells": cell_records,
            "requests": request_records,
        }
        if not cell_records:
            raise TraceExportError("missing cell records")
        cross_check_legacy_record(legacy[tick], samples[tick], cell_records[0])
        tick_records.append(record)

    trace: dict[str, Any] = {
        "scheduler_mode": profile.mode,
        "scheduler_mode_code": profile.mode_code,
        "source_tick_count": profile.samples,
        "sample_record_count": profile.samples,
        "bank_record_count": profile.bank_records,
        "cell_record_count": profile.cell_records,
        "request_record_count": profile.request_records,
        "record_count": profile.total_records,
        "records": tick_records,
    }
    validate_trace_records(trace, profile)
    trace["records_sha256"] = sha256_bytes(canonical_json_bytes(tick_records))
    return trace


def validate_source_identities(repository_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for relative_path, (expected_bytes, expected_digest) in SOURCE_IDENTITIES.items():
        raw = read_regular(repository_root / relative_path)
        if len(raw) != expected_bytes:
            raise TraceExportError(f"source byte count mismatch: {relative_path}")
        digest = sha256_bytes(raw)
        if digest != expected_digest:
            raise TraceExportError(f"source SHA-256 mismatch: {relative_path}")
        records.append(
            {
                "path": relative_path,
                "byte_count": expected_bytes,
                "raw_sha256": expected_digest,
            }
        )
    return records


def load_replay_pair(
    profile: TraceProfile,
    primary_path: Path,
    replay_path: Path,
) -> tuple[bytes, list[dict[str, Any]]]:
    primary = read_regular(primary_path)
    replay = read_regular(replay_path)
    verify_trace_identity(primary, profile)
    verify_trace_identity(replay, profile)
    if primary != replay:
        raise TraceExportError(f"{profile.mode} deterministic replay mismatch")
    return primary, [
        transcript_identity(profile, 1),
        transcript_identity(profile, 2),
    ]


def payload_for_bundle_digest(bundle: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(bundle)
    payload.pop("bundle_sha256", None)
    return payload


def payload_for_manifest_digest(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(manifest)
    payload.pop("manifest_sha256", None)
    return payload


def payload_for_qualification_digest(qualification: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(qualification)
    payload.pop("qualification_sha256", None)
    return payload


def build_bundle(
    source_identities: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    transcript_identities: list[dict[str, Any]],
) -> dict[str, Any]:
    bundle: dict[str, Any] = {
        "schema": SCHEMA_ID,
        "version": VERSION,
        "milestone": MILESTONE,
        "kind": "deterministic_rtl_trace_bundle",
        "status": "PASS",
        "source_boundary": {
            "repository": REPOSITORY_NAME,
            "provenance_class": "upstream_frp_systemverilog_rtl",
            "source_commit": SOURCE_COMMIT,
            "workflow_name": WORKFLOW_NAME,
            "workflow_path": WORKFLOW_PATH,
            "source_identity_count": len(source_identities),
            "source_identities": source_identities,
            "transcript_identity_count": len(transcript_identities),
            "transcript_identities": transcript_identities,
        },
        "execution_contract": {
            "canonical_ternary_notation": CANONICAL_TERNARY_NOTATION,
            "canonical_ternary_domain": CANONICAL_TERNARY_DOMAIN,
            "active_zero_roles": [
                "mediation",
                "balancing",
                "routing",
                "damping",
                "transition_staging",
                "retained_state_participation",
                "pending_route_handling",
                "controlled_neutralization",
            ],
            "direct_opposite_transitions_allowed": False,
            "opposite_polarity_routes": [[-1, 0, 1], [1, 0, -1]],
            "route_legs_separately_observable": True,
            "phase_derived_target_is_executed_state": False,
            "registered_target_is_final_executed_state": False,
            "scheduler_modes": ["7/1", "1/7"],
            "phase_term": "sin(θ_j - θ_i - γ_effective_i)",
            "effective_gamma_scope": "local_per_cell",
            "phase_word_format": "unsigned_modulo_2^32",
            "phase_projection_format": "signed_q30",
            "retained_frequency_format": "signed_q16",
            "interference_field_format": "signed_q16",
            "phase_order_formats": {
                "pair": "signed_q30",
                "cluster": "signed_q30",
                "global": "signed_q30",
            },
            "coherence_capacity_format": "signed_q16",
            "phase_order_and_coherence_capacity_interchangeable": False,
            "thermal_telemetry_format": "signed_q16",
            "stability_telemetry_format": "signed_q16",
            "packed_cell_order": "cell_0_least_significant",
            "execution_chain": [
                "upstream_phase_dynamics",
                "registered_boundary",
                "scheduler",
                "request_handling",
                "pending_routing",
                "active_state_0",
                "capacity_control",
                "retained_writeback",
                "invariants",
            ],
        },
        "trace_count": len(traces),
        "source_tick_count": sum(trace["source_tick_count"] for trace in traces),
        "record_count": sum(trace["record_count"] for trace in traces),
        "traces": traces,
        "bundle_digest_scope": "canonical_json_without_bundle_sha256",
    }
    bundle["bundle_sha256"] = sha256_bytes(
        canonical_json_bytes(payload_for_bundle_digest(bundle))
    )
    return bundle


def strict_object(
    properties: dict[str, Any],
    required: Iterable[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties if required is None else required),
    }


def build_schema() -> dict[str, Any]:
    boolean = {"type": "boolean"}
    integer = {"type": "integer"}
    nonnegative = {"type": "integer", "minimum": 0}
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    hex_value = {"type": "string", "pattern": "^[0-9a-f]+$"}
    hex_32 = {"type": "string", "pattern": "^[0-9a-f]{8}$"}
    ternary_code = {"type": "integer", "enum": [0, 1, 3]}
    ternary_value = {"type": "integer", "enum": CANONICAL_TERNARY_DOMAIN}

    sample_properties: dict[str, Any] = {}
    for key in SAMPLE_KEYS:
        if key in SAMPLE_BOOLEAN_KEYS:
            sample_properties[key] = boolean
        elif key == "invariant_flags":
            sample_properties["invariant_flags_hex"] = hex_value
        elif key == "scheduler_mode":
            sample_properties["scheduler_mode_code"] = {
                "type": "integer",
                "enum": [1, 2],
            }
            sample_properties["scheduler_mode"] = {
                "type": "string",
                "enum": ["7/1", "1/7"],
            }
        elif key == "scheduler_state":
            sample_properties["scheduler_state_code"] = {
                "type": "integer",
                "enum": [1, 2, 3, 4],
            }
            sample_properties["scheduler_state"] = {
                "type": "string",
                "enum": ["balance", "commit", "excite", "neutralize"],
            }
        else:
            sample_properties[key] = integer

    bank_properties = {"source_tick": nonnegative}
    for key in BANK_KEYS[1:]:
        bank_properties[f"{key}_hex"] = hex_value

    cell_properties: dict[str, Any] = {}
    for key in CELL_KEYS:
        if key in CELL_BOOLEAN_KEYS:
            cell_properties[key] = boolean
        elif key in CELL_HEX_KEYS:
            cell_properties[f"{key}_hex"] = hex_32
        elif key in CELL_TERNARY_CODE_KEYS:
            cell_properties[key] = ternary_code
        elif key.endswith("_value"):
            cell_properties[key] = ternary_value
        elif key in {"source_tick", "source_cell"}:
            cell_properties[key] = nonnegative
        else:
            cell_properties[key] = integer

    request_properties: dict[str, Any] = {}
    for key in REQUEST_KEYS:
        if key in REQUEST_BOOLEAN_KEYS:
            request_properties[key] = boolean
        elif key in REQUEST_TERNARY_CODE_KEYS:
            request_properties[key] = ternary_code
        elif key.endswith("_value"):
            request_properties[key] = ternary_value
        elif key in {"source_tick", "request_lane", "phase_cell", "execution_cell"}:
            request_properties[key] = nonnegative
        else:
            request_properties[key] = integer

    coordinate_schema = strict_object(
        {"source_tick": nonnegative, "source_cell": nonnegative}
    )
    tick_schema = strict_object(
        {
            "source_tick": nonnegative,
            "sample": {"$ref": "#/$defs/sample_record"},
            "bank": {"$ref": "#/$defs/bank_record"},
            "cells": {
                "type": "array",
                "minItems": CELLS,
                "maxItems": CELLS,
                "items": {"$ref": "#/$defs/cell_record"},
            },
            "requests": {
                "type": "array",
                "minItems": REQUEST_LANES,
                "maxItems": REQUEST_LANES,
                "items": {"$ref": "#/$defs/request_record"},
            },
        }
    )
    trace_schema = strict_object(
        {
            "scheduler_mode": {"type": "string", "enum": ["7/1", "1/7"]},
            "scheduler_mode_code": {"type": "integer", "enum": [1, 2]},
            "source_tick_count": {"type": "integer", "enum": [16, 17]},
            "sample_record_count": {"type": "integer", "enum": [16, 17]},
            "bank_record_count": {"type": "integer", "enum": [16, 17]},
            "cell_record_count": {"type": "integer", "enum": [128, 136]},
            "request_record_count": {"type": "integer", "enum": [32, 34]},
            "record_count": {"type": "integer", "enum": [192, 204]},
            "records": {
                "type": "array",
                "minItems": 16,
                "maxItems": 17,
                "items": {"$ref": "#/$defs/tick_record"},
            },
            "scheduler_state_counts": {
                "type": "object",
                "additionalProperties": {"type": "integer", "minimum": 1},
                "minProperties": 2,
                "maxProperties": 2,
            },
            "active_zero_cell_observation_count": {
                "type": "integer",
                "enum": [115, 123],
            },
            "first_route_leg_coordinates": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1,
                "items": coordinate_schema,
            },
            "second_route_leg_coordinates": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1,
                "items": coordinate_schema,
            },
            "records_sha256": digest,
        }
    )
    exact_source_identities = [
        {
            "path": path,
            "byte_count": byte_count,
            "raw_sha256": raw_sha256,
        }
        for path, (byte_count, raw_sha256) in SOURCE_IDENTITIES.items()
    ]
    exact_transcript_identities = [
        transcript_identity(TRACE_PROFILES[mode], replay)
        for mode in ("7/1", "1/7")
        for replay in (1, 2)
    ]
    source_boundary_schema = strict_object(
        {
            "repository": {"const": REPOSITORY_NAME},
            "provenance_class": {"const": "upstream_frp_systemverilog_rtl"},
            "source_commit": {"const": SOURCE_COMMIT},
            "workflow_name": {"const": WORKFLOW_NAME},
            "workflow_path": {"const": WORKFLOW_PATH},
            "source_identity_count": {"const": len(SOURCE_IDENTITIES)},
            "source_identities": {"const": exact_source_identities},
            "transcript_identity_count": {"const": 4},
            "transcript_identities": {"const": exact_transcript_identities},
        }
    )
    execution_contract_schema = strict_object(
        {
            "canonical_ternary_notation": {"const": CANONICAL_TERNARY_NOTATION},
            "canonical_ternary_domain": {"const": CANONICAL_TERNARY_DOMAIN},
            "active_zero_roles": {
                "const": [
                    "mediation",
                    "balancing",
                    "routing",
                    "damping",
                    "transition_staging",
                    "retained_state_participation",
                    "pending_route_handling",
                    "controlled_neutralization",
                ]
            },
            "direct_opposite_transitions_allowed": {"const": False},
            "opposite_polarity_routes": {"const": [[-1, 0, 1], [1, 0, -1]]},
            "route_legs_separately_observable": {"const": True},
            "phase_derived_target_is_executed_state": {"const": False},
            "registered_target_is_final_executed_state": {"const": False},
            "scheduler_modes": {"const": ["7/1", "1/7"]},
            "phase_term": {
                "const": "sin(θ_j - θ_i - γ_effective_i)"
            },
            "effective_gamma_scope": {"const": "local_per_cell"},
            "phase_word_format": {"const": "unsigned_modulo_2^32"},
            "phase_projection_format": {"const": "signed_q30"},
            "retained_frequency_format": {"const": "signed_q16"},
            "interference_field_format": {"const": "signed_q16"},
            "phase_order_formats": {
                "const": {
                    "pair": "signed_q30",
                    "cluster": "signed_q30",
                    "global": "signed_q30",
                }
            },
            "coherence_capacity_format": {"const": "signed_q16"},
            "phase_order_and_coherence_capacity_interchangeable": {
                "const": False
            },
            "thermal_telemetry_format": {"const": "signed_q16"},
            "stability_telemetry_format": {"const": "signed_q16"},
            "packed_cell_order": {"const": "cell_0_least_significant"},
            "execution_chain": {
                "const": [
                    "upstream_phase_dynamics",
                    "registered_boundary",
                    "scheduler",
                    "request_handling",
                    "pending_routing",
                    "active_state_0",
                    "capacity_control",
                    "retained_writeback",
                    "invariants",
                ]
            },
        }
    )

    return {
        "$id": (
            "https://frp.example/schemas/m32/"
            "frp.m32.deterministic_rtl_trace_bundle.v1.schema.json"
        ),
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "FRP M32 Deterministic RTL Trace Bundle",
        "type": "object",
        "additionalProperties": False,
        "$defs": {
            "sample_record": strict_object(sample_properties),
            "bank_record": strict_object(bank_properties),
            "cell_record": strict_object(cell_properties),
            "request_record": strict_object(request_properties),
            "tick_record": tick_schema,
            "trace": trace_schema,
            "trace_7_1": {
                "allOf": [
                    {"$ref": "#/$defs/trace"},
                    {
                        "properties": {
                            "scheduler_mode": {"const": "7/1"},
                            "scheduler_mode_code": {"const": 1},
                            "source_tick_count": {"const": 16},
                            "sample_record_count": {"const": 16},
                            "bank_record_count": {"const": 16},
                            "cell_record_count": {"const": 128},
                            "request_record_count": {"const": 32},
                            "record_count": {"const": 192},
                            "records": {"minItems": 16, "maxItems": 16},
                            "scheduler_state_counts": {
                                "const": {"balance": 14, "commit": 2}
                            },
                            "active_zero_cell_observation_count": {"const": 115},
                            "first_route_leg_coordinates": {
                                "const": [{"source_tick": 9, "source_cell": 0}]
                            },
                            "second_route_leg_coordinates": {
                                "const": [{"source_tick": 15, "source_cell": 0}]
                            },
                        }
                    },
                ]
            },
            "trace_1_7": {
                "allOf": [
                    {"$ref": "#/$defs/trace"},
                    {
                        "properties": {
                            "scheduler_mode": {"const": "1/7"},
                            "scheduler_mode_code": {"const": 2},
                            "source_tick_count": {"const": 17},
                            "sample_record_count": {"const": 17},
                            "bank_record_count": {"const": 17},
                            "cell_record_count": {"const": 136},
                            "request_record_count": {"const": 34},
                            "record_count": {"const": 204},
                            "records": {"minItems": 17, "maxItems": 17},
                            "scheduler_state_counts": {
                                "const": {"excite": 3, "neutralize": 14}
                            },
                            "active_zero_cell_observation_count": {"const": 123},
                            "first_route_leg_coordinates": {
                                "const": [{"source_tick": 10, "source_cell": 0}]
                            },
                            "second_route_leg_coordinates": {
                                "const": [{"source_tick": 16, "source_cell": 0}]
                            },
                        }
                    },
                ]
            },
        },
        "properties": {
            "schema": {"const": SCHEMA_ID},
            "version": {"const": VERSION},
            "milestone": {"const": MILESTONE},
            "kind": {"const": "deterministic_rtl_trace_bundle"},
            "status": {"const": "PASS"},
            "source_boundary": source_boundary_schema,
            "execution_contract": execution_contract_schema,
            "trace_count": {"const": 2},
            "source_tick_count": {"const": 33},
            "record_count": {"const": 396},
            "traces": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "prefixItems": [
                    {"$ref": "#/$defs/trace_7_1"},
                    {"$ref": "#/$defs/trace_1_7"},
                ],
                "items": False,
            },
            "bundle_digest_scope": {
                "const": "canonical_json_without_bundle_sha256"
            },
            "bundle_sha256": digest,
        },
        "required": [
            "schema",
            "version",
            "milestone",
            "kind",
            "status",
            "source_boundary",
            "execution_contract",
            "trace_count",
            "source_tick_count",
            "record_count",
            "traces",
            "bundle_digest_scope",
            "bundle_sha256",
        ],
    }


def validate_bundle(bundle: dict[str, Any], schema: dict[str, Any]) -> None:
    if bundle["schema"] != SCHEMA_ID:
        raise TraceExportError("bundle schema identifier mismatch")
    if [trace["scheduler_mode"] for trace in bundle["traces"]] != ["7/1", "1/7"]:
        raise TraceExportError("scheduler traces must remain separate and ordered")
    if bundle["source_tick_count"] != 33 or bundle["record_count"] != 396:
        raise TraceExportError("bundle record totals mismatch")
    expected_digest = sha256_bytes(
        canonical_json_bytes(payload_for_bundle_digest(bundle))
    )
    if bundle["bundle_sha256"] != expected_digest:
        raise TraceExportError("bundle payload digest mismatch")

    try:
        import jsonschema
    except ImportError as exc:
        raise TraceExportError("jsonschema is required for bundle validation") from exc

    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(bundle),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise TraceExportError(f"bundle schema validation failed: {errors[0].message}")


def qualification_checks() -> list[dict[str, str]]:
    identifiers = [
        "source_identities_exact",
        "workflow_identity_exact",
        "mode_7_1_primary_transcript_identity_exact",
        "mode_7_1_replay_transcript_identity_exact",
        "mode_7_1_replays_byte_identical",
        "mode_1_7_primary_transcript_identity_exact",
        "mode_1_7_replay_transcript_identity_exact",
        "mode_1_7_replays_byte_identical",
        "mode_7_1_scheduler_cadence_exact",
        "mode_1_7_scheduler_cadence_exact",
        "source_tick_coordinates_complete",
        "cell_coordinates_complete",
        "request_lane_coordinates_complete",
        "packed_bank_matches_cell_records",
        "packed_masks_match_cell_records",
        "ternary_code_value_pairs_valid",
        "active_zero_markers_exact",
        "pending_route_markers_exact",
        "phase_derived_target_separate_from_execution",
        "registered_target_separate_from_execution",
        "source_boundary_and_execution_fields_separate",
        "first_route_legs_observed",
        "second_route_legs_observed",
        "route_legs_separately_observable",
        "direct_opposite_transitions_absent",
        "reserved_state_events_zero",
        "queue_overflow_events_zero",
        "invariant_flags_all_valid",
        "phase_evolution_records_present",
        "local_effective_gamma_records_present",
        "relative_phase_interference_records_present",
        "retained_frequency_dynamics_observed",
        "phase_order_scales_separate",
        "coherence_capacity_separate_from_phase_order",
        "thermal_telemetry_present",
        "stability_telemetry_present",
        "canonical_bundle_schema_valid",
        "canonical_bundle_digest_reproduced",
    ]
    return [{"check_id": value, "status": "PASS"} for value in identifiers]


def generate(
    repository_root: Path,
    output_root: Path,
    trace_paths: dict[str, tuple[Path, Path]],
) -> dict[str, Any]:
    source_identities = validate_source_identities(repository_root)
    traces: list[dict[str, Any]] = []
    all_transcript_identities: list[dict[str, Any]] = []

    for mode in ("7/1", "1/7"):
        profile = TRACE_PROFILES[mode]
        primary, identities = load_replay_pair(
            profile,
            trace_paths[mode][0],
            trace_paths[mode][1],
        )
        traces.append(parse_transcript(primary, profile))
        all_transcript_identities.extend(identities)

    bundle = build_bundle(source_identities, traces, all_transcript_identities)
    schema = build_schema()
    validate_bundle(bundle, schema)

    schema_record = write_json(output_root, SCHEMA_PATH, schema)
    bundle_record = write_json(output_root, BUNDLE_PATH, bundle)

    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA_ID,
        "version": VERSION,
        "milestone": MILESTONE,
        "kind": "deterministic_rtl_trace_manifest",
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "generated_file_count": 2,
        "generated_files": [schema_record, bundle_record],
        "source_identity_count": len(source_identities),
        "source_identities": source_identities,
        "transcript_identity_count": len(all_transcript_identities),
        "transcript_identities": all_transcript_identities,
        "manifest_digest_scope": "canonical_json_without_manifest_sha256",
    }
    manifest["manifest_sha256"] = sha256_bytes(
        canonical_json_bytes(payload_for_manifest_digest(manifest))
    )
    manifest_record = write_json(output_root, MANIFEST_PATH, manifest)

    checks = qualification_checks()
    qualification: dict[str, Any] = {
        "schema": QUALIFICATION_SCHEMA_ID,
        "version": VERSION,
        "milestone": MILESTONE,
        "kind": "deterministic_rtl_trace_qualification",
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "check_count": len(checks),
        "passed_count": len(checks),
        "failed_count": 0,
        "checks": checks,
        "qualified_artifact_count": 3,
        "qualified_artifacts": [schema_record, bundle_record, manifest_record],
        "qualification_digest_scope": (
            "canonical_json_without_qualification_sha256"
        ),
    }
    qualification["qualification_sha256"] = sha256_bytes(
        canonical_json_bytes(payload_for_qualification_digest(qualification))
    )
    qualification_record = write_json(
        output_root, QUALIFICATION_PATH, qualification
    )

    return {
        "schema": SCHEMA_ID,
        "milestone": MILESTONE,
        "status": "PASS",
        "source_commit": SOURCE_COMMIT,
        "source_identity_count": len(source_identities),
        "transcript_identity_count": len(all_transcript_identities),
        "source_tick_count": bundle["source_tick_count"],
        "record_count": bundle["record_count"],
        "bundle_sha256": bundle["bundle_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "qualification_sha256": qualification["qualification_sha256"],
        "generated_files": [
            schema_record,
            bundle_record,
            manifest_record,
            qualification_record,
        ],
    }


def compare_outputs(left_root: Path, right_root: Path) -> None:
    for relative_path in (SCHEMA_PATH, BUNDLE_PATH, MANIFEST_PATH, QUALIFICATION_PATH):
        left = read_regular(left_root / relative_path)
        right = read_regular(right_root / relative_path)
        if left != right:
            raise TraceExportError(f"generated output mismatch: {relative_path}")


def verify(
    repository_root: Path,
    output_root: Path,
    trace_paths: dict[str, tuple[Path, Path]],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temporary:
        expected_root = Path(temporary)
        result = generate(repository_root, expected_root, trace_paths)
        compare_outputs(expected_root, output_root)
    return result | {"verification": "EXACT"}


def self_test(
    repository_root: Path,
    trace_paths: dict[str, tuple[Path, Path]],
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        first_root = Path(first)
        second_root = Path(second)
        first_result = generate(repository_root, first_root, trace_paths)
        second_result = generate(repository_root, second_root, trace_paths)
        compare_outputs(first_root, second_root)

        bundle = json.loads(read_regular(first_root / BUNDLE_PATH))
        schema = json.loads(read_regular(first_root / SCHEMA_PATH))

        digest_mutation = copy.deepcopy(bundle)
        digest_mutation["traces"][0]["records"][0]["cells"][0][
            "frequency_current_q16"
        ] += 1
        try:
            validate_bundle(digest_mutation, schema)
        except TraceExportError:
            pass
        else:
            raise TraceExportError("bundle payload mutation was not rejected")

        reserved_mutation = copy.deepcopy(bundle["traces"][0])
        reserved_mutation["records"][0]["cells"][0]["retained_state_code"] = 2
        try:
            validate_trace_records(reserved_mutation, TRACE_PROFILES["7/1"])
        except TraceExportError:
            pass
        else:
            raise TraceExportError("reserved ternary code mutation was not rejected")

        route_mutation = copy.deepcopy(bundle["traces"][0])
        route_mutation["records"][9]["cells"][0]["second_route_leg"] = True
        try:
            validate_trace_records(route_mutation, TRACE_PROFILES["7/1"])
        except TraceExportError:
            pass
        else:
            raise TraceExportError("merged route-leg mutation was not rejected")

        primary = read_regular(trace_paths["7/1"][0])
        transcript_mutation = bytearray(primary)
        transcript_mutation[0] ^= 1
        try:
            verify_trace_identity(bytes(transcript_mutation), TRACE_PROFILES["7/1"])
        except TraceExportError:
            pass
        else:
            raise TraceExportError("transcript byte mutation was not rejected")

    return first_result | {
        "deterministic_generation_replays": 2,
        "mutation_rejections": 4,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Produce and verify the FRP M32 deterministic RTL trace boundary."
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--mode-7-1-primary", type=Path, required=True)
    parser.add_argument("--mode-7-1-replay", type=Path, required=True)
    parser.add_argument("--mode-1-7-primary", type=Path, required=True)
    parser.add_argument("--mode-1-7-replay", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--generate", action="store_true")
    action.add_argument("--verify", action="store_true")
    action.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repository_root = args.repository_root.resolve()
    trace_paths = {
        "7/1": (
            args.mode_7_1_primary.resolve(),
            args.mode_7_1_replay.resolve(),
        ),
        "1/7": (
            args.mode_1_7_primary.resolve(),
            args.mode_1_7_replay.resolve(),
        ),
    }

    try:
        if args.self_test:
            result = self_test(repository_root, trace_paths)
        else:
            if args.output_root is None:
                raise TraceExportError("--output-root is required")
            output_root = args.output_root.resolve()
            if args.generate:
                result = generate(repository_root, output_root, trace_paths)
            else:
                result = verify(repository_root, output_root, trace_paths)
    except TraceExportError as exc:
        print(f"FRP M32 deterministic RTL trace export: FAIL: {exc}", file=sys.stderr)
        return 1

    print(canonical_json_bytes(result).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
