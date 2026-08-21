"""Tests for FRP M23 clock, reset, CDC, and interface hardening."""

from __future__ import annotations

import copy
import json
import unittest
from collections import Counter
from pathlib import Path

import frp_m23_clock_reset_cdc_interface_hardening as M23


ROOT = Path(__file__).resolve().parents[1]


class M23ClockResetCdcInterfaceHardeningTests(unittest.TestCase):
    """Exercise the complete M23 contract and machine-readable closure."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = M23.build_outputs(ROOT, M23.EXPECTED_M22_COMMIT)
        cls.contract = json.loads(cls.outputs[M23.CONTRACT_ARTIFACT])
        cls.records = json.loads(cls.outputs[M23.RECORDS_ARTIFACT])
        cls.assertions = json.loads(cls.outputs[M23.ASSERTION_ARTIFACT])
        cls.manifest = json.loads(cls.outputs[M23.MANIFEST_ARTIFACT])
        cls.qualification = json.loads(cls.outputs[M23.QUALIFICATION_ARTIFACT])
        cls.schemas = M23.SchemaContext(ROOT)

    def test_release_and_milestone_are_exact(self) -> None:
        self.assertEqual((M23.VERSION, M23.MILESTONE), ("2.5.0", "M23"))
        self.assertEqual(self.contract["release"], "FRP v2.5.0")

    def test_m22_source_commit_and_release_are_exact(self) -> None:
        self.assertEqual(M23.EXPECTED_M22_COMMIT, "6bb07958710dc942c4deea1e7663ea97017fe3a8")
        self.assertEqual(self.contract["source_commit"], M23.EXPECTED_M22_COMMIT)
        self.assertIn("M22", self.contract["source_release"])

    def test_parameter_profiles_and_signatures_are_exact(self) -> None:
        self.assertEqual(self.contract["parameter_profiles"], list(M23.PROFILE_SPECS))
        self.assertEqual([item["restart_signature"] for item in M23.PROFILE_SPECS], ["00010119", "00010101", "00010131"])

    def test_clock_domains_are_exact(self) -> None:
        self.assertEqual(self.contract["clock_domain_count"], 2)
        self.assertEqual([item["clock"] for item in self.contract["clock_domains"]], ["host_clk", "core_clk"])
        self.assertEqual(self.contract["clock_relationship"], "asynchronous")

    def test_reset_contract_is_complete(self) -> None:
        reset = self.contract["reset_contract"]
        self.assertEqual((reset["assertion"], reset["release"], reset["release_stages"]), ("asynchronous", "synchronous_per_domain", 2))
        self.assertEqual(reset["sequences"], list(M23.RESET_SEQUENCES))

    def test_readiness_contract_is_exact(self) -> None:
        readiness = self.contract["readiness_contract"]
        self.assertEqual(readiness["host_ready_synchronizer_stages"], 2)
        self.assertEqual(readiness["pre_readiness_requests"], "reject_and_record")
        self.assertEqual(readiness["restart_state"], "not_ready_not_busy")

    def test_cdc_boundary_count_and_order_are_exact(self) -> None:
        self.assertEqual(self.contract["cdc_boundary_count"], 5)
        self.assertEqual([item["boundary_id"] for item in self.contract["cdc_boundaries"]], [item["boundary_id"] for item in M23.CDC_BOUNDARIES])

    def test_cdc_boundary_directions_are_complete(self) -> None:
        directions = Counter(item["direction"] for item in self.contract["cdc_boundaries"])
        self.assertEqual(directions, {"host-to-core": 2, "core-to-host": 3})
        self.assertEqual([item["stages"] for item in self.contract["cdc_boundaries"]], [2, 0, 2, 0, 2])

    def test_structural_cdc_checks_are_exact(self) -> None:
        self.assertEqual(self.contract["structural_cdc_check_count"], 10)
        self.assertEqual(self.contract["structural_cdc_checks"], list(M23.STRUCTURAL_CDC_CHECKS))

    def test_handshake_contract_is_exact(self) -> None:
        handshake = self.contract["interface_handshake"]
        self.assertEqual(handshake["maximum_outstanding_transactions"], 1)
        self.assertEqual((handshake["request_payload_width"], handshake["response_payload_width"]), (41, 33))
        self.assertEqual(handshake["reset_interruption"], "drop_in_flight_transaction_without_completion")

    def test_invalid_sequence_classes_are_exact(self) -> None:
        self.assertEqual(self.contract["invalid_sequence_count"], 3)
        self.assertEqual(self.contract["invalid_sequence_classes"], list(M23.INVALID_SEQUENCE_CLASSES))
        self.assertTrue(self.contract["sticky_protocol_error"])

    def test_balanced_ternary_semantics_are_preserved(self) -> None:
        semantics = self.contract["balanced_ternary"]
        self.assertEqual(semantics["semantic_values"], [-1, 0, 1])
        self.assertEqual(semantics["active_neutral_state"], 0)
        self.assertEqual(semantics["direct_positive_negative_transition"], "forbidden")

    def test_reset_rtl_declares_async_assert_and_sync_release(self) -> None:
        text = (ROOT / M23.RTL_RESET_SYNC).read_text()
        self.assertIn("posedge clk or negedge rst_n_async", text)
        self.assertIn("ASYNC_REG", text)
        self.assertIn("2'b00", text)

    def test_bridge_rtl_declares_toggle_and_payload_boundaries(self) -> None:
        text = (ROOT / M23.RTL_CDC_BRIDGE).read_text()
        for token in ("request_toggle_core_sync_q", "response_toggle_host_sync_q", "request_wdata_hold_q", "response_rdata_hold_q"):
            self.assertIn(token, text)

    def test_assertion_rtl_contains_all_twelve_identifiers(self) -> None:
        text = (ROOT / M23.RTL_ASSERTIONS).read_text()
        for identifier, _, _ in M23.ASSERTION_SPECS:
            self.assertIn(identifier.replace("-", "_"), text)

    def test_boundary_rtl_instantiates_all_hardening_blocks(self) -> None:
        text = (ROOT / M23.RTL_BOUNDARY).read_text()
        for token in ("host_reset_sync", "core_reset_sync", "cdc_bridge", "csr_target", "protocol_assertions"):
            self.assertIn(token, text)

    def test_testbench_declares_all_terminal_markers(self) -> None:
        text = (ROOT / M23.RTL_TESTBENCH).read_text()
        for marker in ("M23_RESET_SEQUENCES=5/5 PASS", "M23_CDC_BOUNDARIES=5/5 PASS", "M23_INTERFACE_ASSERTIONS=12/12 PASS", "M23_INVALID_SEQUENCE_CLASSES=3/3 DETECTED", "M23_COMPLETED_TRANSACTIONS=%0d", "M23_RESTART_DETERMINISM=PASS", "M23_HARDENING_TESTBENCH=PASS"):
            self.assertIn(marker, text)

    def test_record_count_and_profile_count_are_exact(self) -> None:
        self.assertEqual((self.records["record_count"], self.records["profile_count"]), (45, 3))
        self.assertEqual(len(self.records["records"]), 45)

    def test_record_sequences_are_dense_and_ordered(self) -> None:
        self.assertEqual([item["sequence"] for item in self.records["records"]], list(range(45)))

    def test_record_category_counts_are_exact(self) -> None:
        counts = Counter(item["category"] for item in self.records["records"])
        self.assertEqual(counts, {"reset": 15, "cdc": 15, "negative_sequence": 9, "reset_interruption": 3, "restart": 3})

    def test_all_nested_record_digests_are_exact(self) -> None:
        for record in self.records["records"]:
            candidate = {key: value for key, value in record.items() if key != "record_digest"}
            self.assertEqual(record["record_digest"], M23.object_digest(candidate))
        candidate = {key: value for key, value in self.records.items() if key != "record_set_digest"}
        self.assertEqual(self.records["record_set_digest"], M23.object_digest(candidate))

    def test_restart_records_match_every_profile(self) -> None:
        restart = [item for item in self.records["records"] if item["category"] == "restart"]
        self.assertEqual([item["evidence"]["signature"] for item in restart], [item["restart_signature"] for item in M23.PROFILE_SPECS])

    def test_completed_transaction_evidence_is_exact(self) -> None:
        restart = [item for item in self.records["records"] if item["category"] == "restart"]
        self.assertEqual({item["evidence"]["completed_transactions"] for item in restart}, {24})

    def test_assertion_report_cardinality_is_exact(self) -> None:
        self.assertEqual((self.assertions["assertion_count"], self.assertions["passed_count"], self.assertions["failed_count"]), (12, 12, 0))

    def test_assertion_identifiers_are_unique_and_ordered(self) -> None:
        expected = [f"M23-A{index:02d}" for index in range(1, 13)]
        self.assertEqual([item["assertion_id"] for item in self.assertions["assertions"]], expected)

    def test_assertion_report_has_only_pass_status(self) -> None:
        self.assertEqual({item["status"] for item in self.assertions["assertions"]}, {"PASS"})
        self.assertEqual(self.assertions["status"], "PASS")

    def test_manifest_cardinalities_are_exact(self) -> None:
        self.assertEqual((self.manifest["source_count"], self.manifest["upstream_dependency_count"], self.manifest["artifact_count"]), (14, 6, 3))

    def test_manifest_source_paths_cover_workflow_and_sources(self) -> None:
        expected = sorted((M23.WORKFLOW_PATH, *M23.TECHNICAL_SOURCE_PATHS))
        self.assertEqual([item["path"] for item in self.manifest["sources"]], expected)
        for item in self.manifest["sources"]:
            self.assertEqual(item["raw_sha256"], M23.sha256_bytes((ROOT / item["path"]).read_bytes()))

    def test_manifest_upstream_dependencies_are_exact(self) -> None:
        self.assertEqual([item["path"] for item in self.manifest["upstream_dependencies"]], sorted(M23.UPSTREAM_SOURCE_PATHS))
        self.assertTrue(all(len(item["raw_sha256"]) == 64 for item in self.manifest["upstream_dependencies"]))

    def test_manifest_primary_artifact_set_is_exact(self) -> None:
        expected = [M23.CONTRACT_ARTIFACT, M23.RECORDS_ARTIFACT, M23.ASSERTION_ARTIFACT]
        self.assertEqual([item["path"] for item in self.manifest["artifacts"]], expected)
        self.assertEqual(self.manifest["artifact_set_digest"], M23.object_digest(self.manifest["artifacts"]))

    def test_qualification_cardinality_and_status_are_exact(self) -> None:
        self.assertEqual((self.qualification["check_count"], self.qualification["passed_count"], self.qualification["failed_count"]), (72, 72, 0))
        self.assertEqual(self.qualification["overall_status"], "PASS")

    def test_qualification_check_identifiers_are_dense(self) -> None:
        self.assertEqual([item["check_id"] for item in self.qualification["checks"]], [f"Q{index:03d}" for index in range(1, 73)])

    def test_qualification_covers_required_categories(self) -> None:
        categories = {item["category"] for item in self.qualification["checks"]}
        self.assertTrue({"reset_sequence", "cdc_boundary", "protocol_assertion", "negative_sequence", "restart_signature", "schema", "manifest"}.issubset(categories))

    def test_generation_is_byte_stable(self) -> None:
        self.assertEqual(M23.build_outputs(ROOT, M23.EXPECTED_M22_COMMIT), self.outputs)

    def test_registry_and_all_formal_schemas_are_complete(self) -> None:
        registry = json.loads((ROOT / M23.REGISTRY_PATH).read_text())
        self.assertEqual((registry["schema_version"], registry["record_count"]), ("2.5.0", 5))
        self.assertEqual([item["path"] for item in registry["records"]], list(M23.SCHEMA_PATHS.values()))
        mapping = {M23.CONTRACT_ARTIFACT: M23.CONTRACT_SCHEMA, M23.RECORDS_ARTIFACT: M23.RECORDS_SCHEMA, M23.ASSERTION_ARTIFACT: M23.ASSERTION_SCHEMA, M23.MANIFEST_ARTIFACT: M23.MANIFEST_SCHEMA, M23.QUALIFICATION_ARTIFACT: M23.QUALIFICATION_SCHEMA}
        for artifact, schema in mapping.items():
            self.schemas.validate(schema, json.loads(self.outputs[artifact]), artifact)
        invalid = copy.deepcopy(self.contract)
        invalid["balanced_ternary"]["semantic_values"] = [-1, 1]
        with self.assertRaises(M23.ContractError):
            self.schemas.validate(M23.CONTRACT_SCHEMA, invalid, "invalid-contract")

    def test_committed_verification_self_test_and_safety_boundaries_pass(self) -> None:
        verification = M23.verify(ROOT, M23.EXPECTED_M22_COMMIT)
        self.assertEqual((verification["status"], verification["artifact_count"]), ("PASS", 5))
        result = M23.self_test(ROOT, M23.EXPECTED_M22_COMMIT)
        self.assertEqual((result["check_count"], result["passed_count"]), (15, 15))
        with self.assertRaises(M23.ContractError):
            M23.validate_source_commit("0" * 40)
        for value in ("/absolute", "../escape", "a/../b", "a\\b"):
            with self.assertRaises(M23.SafetyError):
                M23.safe_relative_path(value)


if __name__ == "__main__":
    unittest.main()
