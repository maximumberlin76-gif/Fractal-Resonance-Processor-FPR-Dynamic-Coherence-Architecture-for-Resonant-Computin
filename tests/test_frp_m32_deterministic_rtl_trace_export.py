"""Independent tests for the FRP M32 deterministic RTL trace exporter."""

from __future__ import annotations

import copy
import hashlib
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator

import frp_m32_deterministic_rtl_trace_export as m32


ROOT = Path(__file__).resolve().parents[1]
PRODUCER_PATH = ROOT / "frp_m32_deterministic_rtl_trace_export.py"
PRODUCER_BYTES = 64267
PRODUCER_SHA256 = (
    "1a575482d0c62f977afc72f25c8d8eacb0daa35981f39cb64b7f85069e5c43cd"
)
SCHEMA_BYTES = 34066
SCHEMA_SHA256 = (
    "534db8227218184cac5d1cabb461dd63b1b61a99e0269c98535539ad3f7d7da2"
)

SAMPLE_7_1 = (
    "M32_TRACE_SAMPLE source_tick=0 tick_enable=1 clear_counters=0 "
    "phase_load_valid=0 auto_target_enable=1 scheduler_mode=1 "
    "scheduler_state=1 balance_tick=1 commit_tick=0 excite_tick=0 "
    "neutralize_tick=0 registered_target_valid=0 "
    "phase_target_domain_valid=1 registered_target_domain_valid=1 "
    "capture_accepted=1 capture_rejected=0 registered_request_enable=0 "
    "accepted_capture_events=1 rejected_capture_events=0 ticks_recorded=1 "
    "scheduler_free=0 scheduler_balance=1 scheduler_commit=0 "
    "scheduler_excite=0 scheduler_neutralize=0 accepted_changes=0 "
    "capacity_remaining=2 capacity_exhausted=0 switch_load_numerator=0 "
    "requested_direct_events=0 prevented_direct_events=0 "
    "neutral_routed_events=0 actual_direct_events=0 reserved_state_events=0 "
    "queue_overflow_events=0 invariant_flags=3ff invariant_all_valid=1 "
    "pair_phase_order_q30=1006673667 cluster_phase_order_q30=965643034 "
    "global_phase_order_q30=946840355 organization_dispersion_q30=108098790 "
    "normalized_cycle_cost_q16=0 temperature_proxy_q16=0 "
    "peak_temperature_proxy_q16=0 thermal_sample_count=1 "
    "coherence_capacity_q16=88062 pressure_q16=0 "
    "stability_margin_q16=88062 stable=1"
)

SAMPLE_1_7 = SAMPLE_7_1.replace(
    "scheduler_mode=1 scheduler_state=1 balance_tick=1 commit_tick=0 "
    "excite_tick=0 neutralize_tick=0",
    "scheduler_mode=2 scheduler_state=3 balance_tick=0 commit_tick=0 "
    "excite_tick=1 neutralize_tick=0",
).replace(
    "scheduler_balance=1 scheduler_commit=0 scheduler_excite=0",
    "scheduler_balance=0 scheduler_commit=0 scheduler_excite=1",
)

BANK = (
    "M32_TRACE_BANK source_tick=0 phase_target_source=1 "
    "registered_target=0 execution_target=0 retained_state=0 pending_route=0 "
    "accepted_cell_mask=0 neutral_routed_cell_mask=0 accepted_change_mask=0 "
    "first_route_leg_mask=0 second_route_leg_mask=0"
)

CELL = (
    "M32_TRACE_CELL source_tick=0 source_cell=0 phase_word=40000000 "
    "frequency_current_q16=65536 gamma_effective_word=26666666 "
    "thermal_node_factor_q30=1073741824 coupling_field_q16=-10772 "
    "phase_projection_q30=1073741824 source_target_code=1 "
    "source_target_value=1 registered_target_code=0 "
    "registered_target_value=0 execution_target_code=0 "
    "execution_target_value=0 retained_state_code=0 retained_state_value=0 "
    "active_zero=1 pending_target_code=0 pending_target_value=0 "
    "pending_active=0 accepted_cell=0 neutral_routed=0 state_changed=0 "
    "first_route_leg=0 second_route_leg=0"
)

REQUEST = (
    "M32_TRACE_REQUEST source_tick=0 request_lane=0 phase_valid=0 "
    "phase_cell=0 phase_target_code=0 phase_target_value=0 "
    "execution_valid=0 execution_cell=0 execution_target_code=0 "
    "execution_target_value=0 accepted=0 rejected=0"
)

LEGACY_7_1 = (
    "M32_MODE_7_1_TRACE tick=0 scheduler_state=1 balance_tick=1 "
    "commit_tick=0 source_target=1 registered_target=0 registered_valid=0 "
    "capture_accepted=1 execution_target=0 request_valid=0 first_leg=0 "
    "second_leg=0 executed_state=0 active_zero=1 pending_target=0"
)

LEGACY_1_7 = (
    "M32_MODE_1_7_TRACE tick=0 scheduler_state=3 excite_tick=1 "
    "neutralize_tick=0 source_target=1 registered_target=0 "
    "registered_valid=0 capture_accepted=1 execution_target=0 "
    "request_valid=0 first_leg=0 second_leg=0 executed_state=0 "
    "active_zero=1 pending_target=0"
)


def scheduler_states(profile: m32.TraceProfile) -> list[str]:
    if profile.mode == "7/1":
        return ["commit" if tick in {7, 15} else "balance" for tick in range(16)]
    return ["excite" if tick in {0, 8, 16} else "neutralize" for tick in range(17)]


def make_sample(
    profile: m32.TraceProfile,
    source_tick: int,
    scheduler_state: str,
) -> dict:
    result = {}
    for key in m32.SAMPLE_KEYS:
        if key in m32.SAMPLE_BOOLEAN_KEYS:
            result[key] = False
        elif key == "invariant_flags":
            result["invariant_flags_hex"] = m32.INVARIANT_FLAGS_HEX
        elif key == "scheduler_mode":
            result["scheduler_mode_code"] = profile.mode_code
            result["scheduler_mode"] = profile.mode
        elif key == "scheduler_state":
            state_code = {
                value: code
                for code, value in m32.SCHEDULER_STATE_LABELS.items()
            }
            result["scheduler_state_code"] = state_code[scheduler_state]
            result["scheduler_state"] = scheduler_state
        else:
            result[key] = 0

    result.update(
        {
            "source_tick": source_tick,
            "tick_enable": True,
            "phase_target_domain_valid": True,
            "registered_target_domain_valid": True,
            "invariant_all_valid": True,
            "thermal_sample_count": source_tick + 1,
            "pair_phase_order_q30": 1000 + source_tick,
            "cluster_phase_order_q30": 900 + source_tick,
            "global_phase_order_q30": 800 + source_tick,
            "coherence_capacity_q16": 700 + source_tick,
            "stability_margin_q16": 600 + source_tick,
            "stable": True,
        }
    )
    result[f"{scheduler_state}_tick"] = True
    return result


def make_cell(
    source_tick: int,
    source_cell: int,
    *,
    retained_nonzero: bool,
    first_route_leg: bool,
    second_route_leg: bool,
) -> dict:
    result = {}
    for key in m32.CELL_KEYS:
        if key in m32.CELL_BOOLEAN_KEYS:
            result[key] = False
        elif key in m32.CELL_HEX_KEYS:
            result[f"{key}_hex"] = "00000000"
        else:
            result[key] = 0

    retained_code = 1 if retained_nonzero else 0
    result.update(
        {
            "source_tick": source_tick,
            "source_cell": source_cell,
            "phase_word_hex": f"{((source_tick + 1) << 12) + source_cell:08x}",
            "frequency_current_q16": 65536 + source_tick,
            "gamma_effective_word_hex": "26666666",
            "thermal_node_factor_q30": 1073741824,
            "coupling_field_q16": -1000 + source_tick * 8 + source_cell,
            "phase_projection_q30": 1000000 + source_tick * 8 + source_cell,
            "source_target_code": 1,
            "source_target_value": 1,
            "registered_target_code": 1,
            "registered_target_value": 1,
            "retained_state_code": retained_code,
            "retained_state_value": retained_code,
            "active_zero": not retained_nonzero,
            "first_route_leg": first_route_leg,
            "second_route_leg": second_route_leg,
        }
    )
    return result


def pack_codes(cells: list[dict], key: str) -> str:
    value = sum(cell[key] << (cell["source_cell"] * 2) for cell in cells)
    return f"{value:x}"


def pack_mask(cells: list[dict], key: str) -> str:
    value = sum(int(cell[key]) << cell["source_cell"] for cell in cells)
    return f"{value:x}"


def make_bank(source_tick: int, cells: list[dict]) -> dict:
    return {
        "source_tick": source_tick,
        "phase_target_source_hex": pack_codes(cells, "source_target_code"),
        "registered_target_hex": pack_codes(cells, "registered_target_code"),
        "execution_target_hex": pack_codes(cells, "execution_target_code"),
        "retained_state_hex": pack_codes(cells, "retained_state_code"),
        "pending_route_hex": pack_codes(cells, "pending_target_code"),
        "accepted_cell_mask_hex": pack_mask(cells, "accepted_cell"),
        "neutral_routed_cell_mask_hex": pack_mask(cells, "neutral_routed"),
        "accepted_change_mask_hex": pack_mask(cells, "state_changed"),
        "first_route_leg_mask_hex": pack_mask(cells, "first_route_leg"),
        "second_route_leg_mask_hex": pack_mask(cells, "second_route_leg"),
    }


def make_request(source_tick: int, lane: int) -> dict:
    result = {}
    for key in m32.REQUEST_KEYS:
        if key in m32.REQUEST_BOOLEAN_KEYS:
            result[key] = False
        else:
            result[key] = 0
    result.update(
        {
            "source_tick": source_tick,
            "request_lane": lane,
            "phase_cell": lane,
            "execution_cell": lane,
        }
    )
    return result


def make_trace(profile: m32.TraceProfile) -> dict:
    route_coordinates = {
        "7/1": {"first": (9, 0), "second": (15, 0)},
        "1/7": {"first": (10, 0), "second": (16, 0)},
    }[profile.mode]
    nonzero_coordinates = {
        (tick, cell)
        for tick, width in ((0, 8), (1, 5))
        for cell in range(width)
    }
    records = []
    for source_tick, state in enumerate(scheduler_states(profile)):
        cells = [
            make_cell(
                source_tick,
                source_cell,
                retained_nonzero=(source_tick, source_cell) in nonzero_coordinates,
                first_route_leg=(source_tick, source_cell)
                == route_coordinates["first"],
                second_route_leg=(source_tick, source_cell)
                == route_coordinates["second"],
            )
            for source_cell in range(m32.CELLS)
        ]
        records.append(
            {
                "source_tick": source_tick,
                "sample": make_sample(profile, source_tick, state),
                "bank": make_bank(source_tick, cells),
                "cells": cells,
                "requests": [
                    make_request(source_tick, lane)
                    for lane in range(m32.REQUEST_LANES)
                ],
            }
        )

    trace = {
        "scheduler_mode": profile.mode,
        "scheduler_mode_code": profile.mode_code,
        "source_tick_count": profile.samples,
        "sample_record_count": profile.samples,
        "bank_record_count": profile.bank_records,
        "cell_record_count": profile.cell_records,
        "request_record_count": profile.request_records,
        "record_count": profile.total_records,
        "records": records,
    }
    m32.validate_trace_records(trace, profile)
    trace["records_sha256"] = m32.sha256_bytes(m32.canonical_json_bytes(records))
    return trace


class M32TraceExportBoundaryTests(unittest.TestCase):
    def test_01_producer_source_identity_is_exact(self) -> None:
        raw = PRODUCER_PATH.read_bytes()
        self.assertEqual(len(raw), PRODUCER_BYTES)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), PRODUCER_SHA256)

    def test_02_publication_constants_are_exact(self) -> None:
        self.assertEqual(m32.MILESTONE, "M32")
        self.assertEqual(m32.VERSION, "1.0.0")
        self.assertEqual(
            m32.SOURCE_COMMIT,
            "c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941",
        )
        self.assertEqual(m32.CANONICAL_TERNARY_NOTATION, "-1/0/1")
        self.assertEqual(m32.CANONICAL_TERNARY_DOMAIN, [-1, 0, 1])

    def test_03_output_paths_are_exact_and_unique(self) -> None:
        paths = [
            m32.SCHEMA_PATH,
            m32.BUNDLE_PATH,
            m32.MANIFEST_PATH,
            m32.QUALIFICATION_PATH,
        ]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(
            all(
                path.startswith(("schemas/m32/", "artifacts/m32/"))
                for path in paths
            )
        )

    def test_04_source_identities_are_exact(self) -> None:
        identities = m32.validate_source_identities(ROOT)
        self.assertEqual(len(identities), 29)
        self.assertEqual(
            [item["path"] for item in identities],
            list(m32.SOURCE_IDENTITIES),
        )

    def test_05_source_identity_classes_remain_separate(self) -> None:
        paths = list(m32.SOURCE_IDENTITIES)
        self.assertEqual(sum(path.startswith("rtl/m31/") for path in paths), 16)
        self.assertEqual(sum(path.startswith("rtl/m32/") for path in paths), 11)
        self.assertEqual(sum(path.startswith("formal/m32/") for path in paths), 1)
        self.assertIn(m32.WORKFLOW_PATH, paths)

    def test_06_scheduler_profiles_are_exact_and_separate(self) -> None:
        self.assertEqual(list(m32.TRACE_PROFILES), ["7/1", "1/7"])
        seven = m32.TRACE_PROFILES["7/1"]
        one = m32.TRACE_PROFILES["1/7"]
        self.assertEqual((seven.samples, seven.total_records), (16, 192))
        self.assertEqual((one.samples, one.total_records), (17, 204))
        self.assertEqual(seven.scheduler_counts, {"balance": 14, "commit": 2})
        self.assertEqual(one.scheduler_counts, {"excite": 3, "neutralize": 14})

    def test_07_transcript_identities_are_exact(self) -> None:
        expected = {
            "7/1": (
                105702,
                "9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915",
            ),
            "1/7": (
                112364,
                "41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89",
            ),
        }
        for mode, profile in m32.TRACE_PROFILES.items():
            with self.subTest(mode=mode):
                self.assertEqual(
                    (profile.transcript_bytes, profile.transcript_sha256),
                    expected[mode],
                )

    def test_08_schema_identity_is_exact(self) -> None:
        raw = m32.canonical_json_bytes(m32.build_schema())
        self.assertEqual(len(raw), SCHEMA_BYTES)
        self.assertEqual(m32.sha256_bytes(raw), SCHEMA_SHA256)

    def test_09_schema_is_valid_draft_2020_12(self) -> None:
        schema = m32.build_schema()
        self.assertEqual(
            schema["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )
        Draft202012Validator.check_schema(schema)

    def test_10_schema_preserves_exact_route_coordinates(self) -> None:
        definitions = m32.build_schema()["$defs"]
        seven = definitions["trace_7_1"]["allOf"][1]["properties"]
        one = definitions["trace_1_7"]["allOf"][1]["properties"]
        self.assertEqual(
            seven["first_route_leg_coordinates"]["const"],
            [{"source_tick": 9, "source_cell": 0}],
        )
        self.assertEqual(
            seven["second_route_leg_coordinates"]["const"],
            [{"source_tick": 15, "source_cell": 0}],
        )
        self.assertEqual(
            one["first_route_leg_coordinates"]["const"],
            [{"source_tick": 10, "source_cell": 0}],
        )
        self.assertEqual(
            one["second_route_leg_coordinates"]["const"],
            [{"source_tick": 16, "source_cell": 0}],
        )

    def test_11_schema_preserves_execution_contract(self) -> None:
        contract = m32.build_schema()["properties"]["execution_contract"]["properties"]
        self.assertEqual(
            contract["opposite_polarity_routes"]["const"],
            [[-1, 0, 1], [1, 0, -1]],
        )
        self.assertIs(contract["direct_opposite_transitions_allowed"]["const"], False)
        self.assertEqual(contract["effective_gamma_scope"]["const"], "local_per_cell")
        self.assertIs(
            contract["phase_order_and_coherence_capacity_interchangeable"][
                "const"
            ],
            False,
        )

    def test_12_qualification_check_identifiers_are_unique(self) -> None:
        checks = m32.qualification_checks()
        identifiers = [item["check_id"] for item in checks]
        self.assertEqual(len(checks), 38)
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(item["status"] == "PASS" for item in checks))

    def test_13_canonical_json_is_stable_and_newline_terminated(self) -> None:
        first = m32.canonical_json_bytes({"z": 1, "a": [-1, 0, 1]})
        second = m32.canonical_json_bytes({"a": [-1, 0, 1], "z": 1})
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertLess(first.index(b'"a"'), first.index(b'"z"'))

    def test_14_canonical_json_rejects_nonfinite_values(self) -> None:
        with self.assertRaises(ValueError):
            m32.canonical_json_bytes({"invalid": math.nan})

    def test_15_payload_digest_scope_ignores_only_digest_field(self) -> None:
        bundle = {"value": 1, "bundle_sha256": "0" * 64}
        self.assertEqual(m32.payload_for_bundle_digest(bundle), {"value": 1})
        self.assertEqual(bundle["bundle_sha256"], "0" * 64)


class M32TraceParsingTests(unittest.TestCase):
    def test_01_mode_7_1_sample_is_parsed_exactly(self) -> None:
        sample = m32.parse_sample(SAMPLE_7_1)
        self.assertEqual(sample["scheduler_mode"], "7/1")
        self.assertEqual(sample["scheduler_state"], "balance")
        self.assertTrue(sample["balance_tick"])
        self.assertEqual(sample["invariant_flags_hex"], "3ff")
        self.assertEqual(sample["pair_phase_order_q30"], 1006673667)
        self.assertEqual(sample["coherence_capacity_q16"], 88062)

    def test_02_mode_1_7_sample_is_parsed_separately(self) -> None:
        sample = m32.parse_sample(SAMPLE_1_7)
        self.assertEqual(sample["scheduler_mode"], "1/7")
        self.assertEqual(sample["scheduler_state"], "excite")
        self.assertTrue(sample["excite_tick"])
        self.assertFalse(sample["balance_tick"])

    def test_03_bank_record_is_parsed_without_repacking(self) -> None:
        bank = m32.parse_bank(BANK)
        self.assertEqual(bank["source_tick"], 0)
        self.assertEqual(bank["phase_target_source_hex"], "1")
        self.assertEqual(bank["retained_state_hex"], "0")

    def test_04_cell_record_preserves_phase_gamma_and_active_zero(self) -> None:
        cell = m32.parse_cell(CELL)
        self.assertEqual(cell["phase_word_hex"], "40000000")
        self.assertEqual(cell["gamma_effective_word_hex"], "26666666")
        self.assertEqual(cell["coupling_field_q16"], -10772)
        self.assertEqual(cell["retained_state_value"], 0)
        self.assertTrue(cell["active_zero"])

    def test_05_request_record_preserves_source_coordinates(self) -> None:
        request = m32.parse_request(REQUEST)
        self.assertEqual(request["source_tick"], 0)
        self.assertEqual(request["request_lane"], 0)
        self.assertEqual(request["phase_cell"], 0)
        self.assertEqual(request["execution_cell"], 0)

    def test_06_legacy_records_remain_mode_specific(self) -> None:
        seven = m32.parse_legacy(LEGACY_7_1, m32.TRACE_PROFILES["7/1"])
        one = m32.parse_legacy(LEGACY_1_7, m32.TRACE_PROFILES["1/7"])
        self.assertEqual(
            set(seven) - m32.LEGACY_COMMON_KEYS,
            {"balance_tick", "commit_tick"},
        )
        self.assertEqual(
            set(one) - m32.LEGACY_COMMON_KEYS,
            {"excite_tick", "neutralize_tick"},
        )

    def test_07_legacy_and_full_records_cross_check(self) -> None:
        legacy = m32.parse_legacy(LEGACY_7_1, m32.TRACE_PROFILES["7/1"])
        m32.cross_check_legacy_record(
            legacy,
            m32.parse_sample(SAMPLE_7_1),
            m32.parse_cell(CELL),
        )

    def test_08_legacy_mismatch_is_rejected(self) -> None:
        legacy = m32.parse_legacy(LEGACY_7_1, m32.TRACE_PROFILES["7/1"])
        legacy["executed_state"] = 1
        with self.assertRaisesRegex(m32.TraceExportError, "legacy/full trace mismatch"):
            m32.cross_check_legacy_record(
                legacy,
                m32.parse_sample(SAMPLE_7_1),
                m32.parse_cell(CELL),
            )

    def test_09_noncanonical_decimal_values_are_rejected(self) -> None:
        for value in ("", "+1", "01", "1.0"):
            with self.subTest(value=value), self.assertRaises(m32.TraceExportError):
                m32.parse_decimal(value, "fixture")

    def test_10_nonbinary_flags_are_rejected(self) -> None:
        for value in ("-1", "2"):
            with self.subTest(value=value), self.assertRaises(m32.TraceExportError):
                m32.parse_boolean(value, "fixture")

    def test_11_noncanonical_hexadecimal_values_are_rejected(self) -> None:
        for value in ("", "0x1", "A", "ab-cd"):
            with self.subTest(value=value), self.assertRaises(m32.TraceExportError):
                m32.parse_hex(value, "fixture")
        with self.assertRaises(m32.TraceExportError):
            m32.parse_hex("1234567", "fixture", width=8)

    def test_12_reserved_ternary_code_is_rejected(self) -> None:
        with self.assertRaisesRegex(m32.TraceExportError, "reserved or invalid"):
            m32.parse_ternary_code("2", "fixture")

    def test_13_duplicate_trace_field_is_rejected(self) -> None:
        with self.assertRaisesRegex(m32.TraceExportError, "duplicate trace field"):
            m32.parse_fields("PREFIX value=1 value=1", "PREFIX", ("value",))

    def test_14_missing_and_extra_trace_fields_are_rejected(self) -> None:
        with self.assertRaisesRegex(m32.TraceExportError, "trace field mismatch"):
            m32.parse_fields("PREFIX value=1 extra=2", "PREFIX", ("value",))
        with self.assertRaisesRegex(m32.TraceExportError, "trace field mismatch"):
            m32.parse_fields("PREFIX value=1", "PREFIX", ("value", "missing"))

    def test_15_unsupported_scheduler_mode_is_rejected(self) -> None:
        mutated = SAMPLE_7_1.replace("scheduler_mode=1", "scheduler_mode=3")
        with self.assertRaisesRegex(m32.TraceExportError, "unsupported scheduler mode"):
            m32.parse_sample(mutated)

    def test_16_reserved_cell_code_is_rejected(self) -> None:
        mutated = CELL.replace("retained_state_code=0", "retained_state_code=2")
        with self.assertRaisesRegex(m32.TraceExportError, "reserved or invalid"):
            m32.parse_cell(mutated)

    def test_17_nonbinary_request_flag_is_rejected(self) -> None:
        mutated = REQUEST.replace("accepted=0", "accepted=2")
        with self.assertRaisesRegex(m32.TraceExportError, "binary flag required"):
            m32.parse_request(mutated)

    def test_18_incomplete_transcript_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "source tick coverage mismatch",
        ):
            m32.parse_transcript(
                (SAMPLE_7_1 + "\n").encode("utf-8"),
                m32.TRACE_PROFILES["7/1"],
            )


class M32TraceInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.traces = {
            mode: make_trace(profile)
            for mode, profile in m32.TRACE_PROFILES.items()
        }

    def fresh_trace(self, mode: str = "7/1") -> dict:
        return copy.deepcopy(self.traces[mode])

    def test_01_mode_7_1_trace_contract_is_accepted(self) -> None:
        trace = self.fresh_trace("7/1")
        m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])
        self.assertEqual(trace["scheduler_state_counts"], {"balance": 14, "commit": 2})
        self.assertEqual(trace["active_zero_cell_observation_count"], 115)
        self.assertEqual(
            trace["first_route_leg_coordinates"],
            [{"source_tick": 9, "source_cell": 0}],
        )
        self.assertEqual(
            trace["second_route_leg_coordinates"],
            [{"source_tick": 15, "source_cell": 0}],
        )

    def test_02_mode_1_7_trace_contract_is_accepted(self) -> None:
        trace = self.fresh_trace("1/7")
        m32.validate_trace_records(trace, m32.TRACE_PROFILES["1/7"])
        self.assertEqual(
            trace["scheduler_state_counts"],
            {"excite": 3, "neutralize": 14},
        )
        self.assertEqual(trace["active_zero_cell_observation_count"], 123)
        self.assertEqual(
            trace["first_route_leg_coordinates"],
            [{"source_tick": 10, "source_cell": 0}],
        )
        self.assertEqual(
            trace["second_route_leg_coordinates"],
            [{"source_tick": 16, "source_cell": 0}],
        )

    def test_03_reserved_ternary_code_mutation_is_rejected(self) -> None:
        trace = self.fresh_trace()
        trace["records"][0]["cells"][0]["retained_state_code"] = 2
        with self.assertRaisesRegex(m32.TraceExportError, "invalid ternary code"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_04_active_zero_marker_mutation_is_rejected(self) -> None:
        trace = self.fresh_trace()
        trace["records"][2]["cells"][0]["active_zero"] = False
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "active state 0 marker mismatch",
        ):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_05_packed_bank_mutation_is_rejected(self) -> None:
        trace = self.fresh_trace()
        trace["records"][2]["bank"]["retained_state_hex"] = "1"
        with self.assertRaisesRegex(m32.TraceExportError, "packed bank mismatch"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_06_merged_route_legs_are_rejected(self) -> None:
        trace = self.fresh_trace()
        cell = trace["records"][9]["cells"][0]
        cell["second_route_leg"] = True
        trace["records"][9]["bank"]["second_route_leg_mask_hex"] = "1"
        with self.assertRaisesRegex(m32.TraceExportError, "route legs merged"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_07_direct_opposite_transition_is_rejected(self) -> None:
        trace = self.fresh_trace()
        cell = trace["records"][0]["cells"][0]
        cell["retained_state_code"] = 3
        cell["retained_state_value"] = -1
        trace["records"][0]["bank"]["retained_state_hex"] = pack_codes(
            trace["records"][0]["cells"], "retained_state_code"
        )
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "direct opposite-polarity transition",
        ):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_08_scheduler_cadence_mutation_is_rejected(self) -> None:
        trace = self.fresh_trace()
        sample = trace["records"][0]["sample"]
        sample["scheduler_state"] = "commit"
        sample["scheduler_state_code"] = 2
        sample["balance_tick"] = False
        sample["commit_tick"] = True
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "scheduler cadence count mismatch",
        ):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_09_active_zero_count_mutation_is_rejected(self) -> None:
        trace = self.fresh_trace()
        cell = trace["records"][2]["cells"][0]
        cell["retained_state_code"] = 1
        cell["retained_state_value"] = 1
        cell["active_zero"] = False
        trace["records"][2]["bank"]["retained_state_hex"] = pack_codes(
            trace["records"][2]["cells"], "retained_state_code"
        )
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "active state 0 observation count mismatch",
        ):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_10_nonconsecutive_source_ticks_are_rejected(self) -> None:
        trace = self.fresh_trace()
        trace["records"][1]["source_tick"] = 20
        with self.assertRaisesRegex(m32.TraceExportError, "consecutive and zero-based"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_11_request_accept_reject_collision_is_rejected(self) -> None:
        trace = self.fresh_trace()
        request = trace["records"][0]["requests"][0]
        request["accepted"] = True
        request["rejected"] = True
        with self.assertRaisesRegex(m32.TraceExportError, "accepted and rejected"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_12_request_coordinate_out_of_range_is_rejected(self) -> None:
        trace = self.fresh_trace()
        trace["records"][0]["requests"][0]["phase_cell"] = m32.CELLS
        with self.assertRaisesRegex(m32.TraceExportError, "coordinate out of range"):
            m32.validate_trace_records(trace, m32.TRACE_PROFILES["7/1"])

    def test_13_transcript_identity_mutation_is_rejected(self) -> None:
        profile = m32.TRACE_PROFILES["7/1"]
        raw = b"x" * (profile.transcript_bytes - 1) + b"\n"
        with self.assertRaisesRegex(
            m32.TraceExportError,
            "transcript SHA-256 mismatch",
        ):
            m32.verify_trace_identity(raw, profile)

    def test_14_source_identity_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "source.bin"
            path.write_bytes(b"abc")
            expected = {"source.bin": (3, hashlib.sha256(b"abc").hexdigest())}
            with mock.patch.object(m32, "SOURCE_IDENTITIES", expected):
                path.write_bytes(b"abd")
                with self.assertRaisesRegex(
                    m32.TraceExportError,
                    "source SHA-256 mismatch",
                ):
                    m32.validate_source_identities(root)

    def test_15_symlink_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.bin"
            target.write_bytes(b"abc")
            link = root / "source.bin"
            link.symlink_to(target)
            expected = {"source.bin": (3, hashlib.sha256(b"abc").hexdigest())}
            with mock.patch.object(m32, "SOURCE_IDENTITIES", expected):
                with self.assertRaisesRegex(
                    m32.TraceExportError,
                    "regular file is missing",
                ):
                    m32.validate_source_identities(root)

    def test_16_symlink_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.json"
            target.write_bytes(b"{}\n")
            link = root / "output.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(
                m32.TraceExportError,
                "refusing non-regular output",
            ):
                m32.write_json(root, "output.json", {"value": 1})


if __name__ == "__main__":
    unittest.main()
