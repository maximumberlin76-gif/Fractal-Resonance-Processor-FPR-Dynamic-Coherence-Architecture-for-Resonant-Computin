"""Tests for FRP M20 deterministic cross-layer correlation."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

import frp_m20_cross_layer_correlation as M20


ROOT = Path(__file__).resolve().parents[1]


class M20CorrelationTests(unittest.TestCase):
    """Exercise canonical correlation, schemas, digests, and failures."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = M20.build_context(ROOT, M20.EXPECTED_M19_COMMIT)
        cls.schemas = M20.SchemaContext(ROOT)
        cls.rtl = M20.build_layer_package(cls.context, "rtl")
        cls.fpga = M20.build_layer_package(cls.context, "fpga_preparation")

    def test_exact_source_commit_and_vector_inventory(self) -> None:
        self.assertEqual(self.context.source_commit, M20.EXPECTED_M19_COMMIT)
        self.assertEqual(len(self.context.vector_identities), 10)
        self.assertEqual(
            [item["name"] for item in self.context.vector_identities],
            sorted(item["name"] for item in self.context.vector_identities),
        )

    def test_semantic_and_vector_scheduler_sources_are_exact(self) -> None:
        self.assertEqual(set(self.context.semantic_traces), {"free", "7/1", "1/7"})
        self.assertEqual(len(self.context.vector_rows["free"]), 16)
        self.assertEqual(len(self.context.vector_rows["7/1"]), 64)
        self.assertEqual(len(self.context.vector_rows["1/7"]), 16)
        for mode in ("free", "7/1", "1/7"):
            trace = self.context.semantic_traces[mode]["trace"]
            for tick, vector in enumerate(self.context.vector_rows[mode]):
                self.assertEqual(trace[tick]["scheduler_mode"], vector["scheduler_mode"])
                self.assertEqual(trace[tick]["scheduler_state"], vector["scheduler_state"])

    def test_rtl_package_has_96_zero_mismatch_records(self) -> None:
        summary = self.rtl["summary"]
        self.assertEqual(summary["record_count"], 96)
        self.assertEqual(summary["check_count"], 960)
        self.assertEqual(summary["passed_check_count"], 960)
        self.assertEqual(summary["failed_check_count"], 0)
        self.assertEqual(summary["mismatch_count"], 0)
        self.assertEqual(summary["overall_status"], "PASS")

    def test_fpga_package_has_four_zero_mismatch_records(self) -> None:
        summary = self.fpga["summary"]
        self.assertEqual(summary["record_count"], 4)
        self.assertEqual(summary["check_count"], 40)
        self.assertEqual(summary["passed_check_count"], 40)
        self.assertEqual(summary["failed_check_count"], 0)
        self.assertEqual(summary["mismatch_count"], 0)
        self.assertEqual(summary["overall_status"], "PASS")

    def test_all_record_level_checks_pass(self) -> None:
        for package in (self.rtl, self.fpga):
            for sequence, record in enumerate(package["records"]):
                self.assertEqual(record["sequence"], sequence)
                self.assertEqual(tuple(record["checks"]), M20.CHECK_NAMES)
                self.assertTrue(all(record["checks"].values()))
                self.assertEqual(record["mismatch_count"], 0)
                self.assertEqual(record["mismatches"], [])
                self.assertEqual(record["record_status"], "PASS")

    def test_canonical_ternary_domain_and_active_zero_are_preserved(self) -> None:
        for package in (self.rtl, self.fpga):
            mapping = package["interface_mapping"]
            self.assertEqual(mapping["canonical_ternary_states"], [-1, 0, 1])
            self.assertEqual(mapping["active_neutral_state"], 0)
            self.assertEqual(
                mapping["neutral_routes"],
                ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
            )
            for record in package["records"]:
                for field in (
                    "retained_state_before",
                    "retained_state_after",
                    "pending_route_before",
                    "pending_route_after",
                ):
                    self.assertTrue(
                        set(record["m16_observed"][field]).issubset({-1, 0, 1})
                    )

    def test_transition_fraction_scales_request_lanes_exactly(self) -> None:
        for package in (self.rtl, self.fpga):
            m15 = package["interface_mapping"]["m15_profile"]
            m16 = package["interface_mapping"]["m16_profile"]
            self.assertEqual(m15["request_lanes"], m15["cells"] // 4)
            self.assertEqual(m16["request_lanes"], m16["cells"] // 4)

    def test_record_and_mismatch_digests_are_exact(self) -> None:
        for package in (self.rtl, self.fpga):
            self.assertEqual(
                package["summary"]["record_digest"],
                M20.object_digest(package["records"]),
            )
            self.assertEqual(
                package["summary"]["mismatch_digest"],
                M20.object_digest(package["mismatch_records"]),
            )

    def test_packages_validate_against_formal_schemas(self) -> None:
        self.schemas.validate(M20.PACKAGE_SCHEMA, self.rtl, M20.RTL_PACKAGE)
        self.schemas.validate(M20.PACKAGE_SCHEMA, self.fpga, M20.FPGA_PACKAGE)

    def test_generation_is_byte_stable(self) -> None:
        second_rtl = M20.build_layer_package(self.context, "rtl")
        second_fpga = M20.build_layer_package(self.context, "fpga_preparation")
        self.assertEqual(M20.canonical_json_bytes(self.rtl), M20.canonical_json_bytes(second_rtl))
        self.assertEqual(M20.canonical_json_bytes(self.fpga), M20.canonical_json_bytes(second_fpga))

    def test_altered_observed_record_is_detected(self) -> None:
        self.assertTrue(M20.altered_record_probe(self.context))

    def test_altered_m15_vector_is_detected(self) -> None:
        self.assertTrue(M20.altered_vector_probe(self.context))

    def test_altered_vector_digest_is_detected(self) -> None:
        self.assertTrue(M20.altered_digest_probe(self.context))

    def test_schema_rejects_reserved_ternary_state(self) -> None:
        altered = copy.deepcopy(self.rtl["records"][0])
        altered["m16_observed"]["retained_state_after"][0] = 2
        with self.assertRaises(M20.ContractError):
            self.schemas.validate(M20.RECORD_SCHEMA, altered, "reserved-state")

    def test_schema_rejects_missing_required_field(self) -> None:
        altered = copy.deepcopy(self.rtl["records"][0])
        del altered["m16_observed"]
        with self.assertRaises(M20.ContractError):
            self.schemas.validate(M20.RECORD_SCHEMA, altered, "missing-field")

    def test_schema_rejects_additional_field(self) -> None:
        altered = copy.deepcopy(self.rtl["records"][0])
        altered["unregistered"] = True
        with self.assertRaises(M20.ContractError):
            self.schemas.validate(M20.RECORD_SCHEMA, altered, "additional-field")

    def test_wrong_source_commit_is_rejected(self) -> None:
        with self.assertRaises(M20.ContractError):
            M20.build_context(ROOT, "0" * 40)

    def test_unsafe_output_path_is_rejected(self) -> None:
        for value in ("../escape.json", "/absolute.json", "a/./b.json"):
            with self.subTest(value=value):
                with self.assertRaises(M20.SafetyError):
                    M20.safe_relative_path(value)


class M20CommittedOutputTests(unittest.TestCase):
    """Exercise the complete generated and committed M20 package."""

    @classmethod
    def setUpClass(cls) -> None:
        if not all((ROOT / path).is_file() for path in M20.GENERATED_PATHS):
            raise unittest.SkipTest("committed M20 outputs not installed yet")
        cls.outputs = M20.build_outputs(ROOT, M20.EXPECTED_M19_COMMIT)

    def test_committed_outputs_are_byte_identical(self) -> None:
        for relative, expected in self.outputs.items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), expected)

    def test_complete_verification_passes(self) -> None:
        result = M20.verify(ROOT, M20.EXPECTED_M19_COMMIT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["artifact_count"], 4)
        self.assertTrue(all(item["match"] for item in result["artifacts"]))

    def test_qualification_is_complete(self) -> None:
        qualification = M20.read_json(ROOT, M20.QUALIFICATION)
        self.assertEqual(qualification["overall_status"], "PASS")
        self.assertEqual(qualification["failed_count"], 0)
        self.assertEqual(
            qualification["passed_count"], qualification["check_count"]
        )


if __name__ == "__main__":
    unittest.main()
