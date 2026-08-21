"""Tests for FRP M24 formal and bounded verification closure."""

from __future__ import annotations

import copy
import json
import unittest
from collections import Counter
from pathlib import Path

import frp_m24_formal_bounded_verification as M24


ROOT = Path(__file__).resolve().parents[1]


class M24FormalBoundedVerificationTests(unittest.TestCase):
    """Exercise the complete M24 proof contract and evidence closure."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = M24.build_outputs(ROOT, M24.EXPECTED_M23_COMMIT)
        cls.contract = json.loads(cls.outputs[M24.CONTRACT_ARTIFACT])
        cls.inventory = json.loads(cls.outputs[M24.INVENTORY_ARTIFACT])
        cls.evidence = json.loads(cls.outputs[M24.EVIDENCE_ARTIFACT])
        cls.manifest = json.loads(cls.outputs[M24.MANIFEST_ARTIFACT])
        cls.qualification = json.loads(cls.outputs[M24.QUALIFICATION_ARTIFACT])
        cls.schemas = M24.SchemaContext(ROOT)

    def test_release_milestone_and_source_commit_are_exact(self) -> None:
        self.assertEqual((M24.VERSION, M24.MILESTONE), ("2.6.0", "M24"))
        self.assertEqual(self.contract["release"], "FRP v2.6.0")
        self.assertEqual(
            M24.EXPECTED_M23_COMMIT,
            "1dcc4e4d47135cdf1e38192cc96f0d928066b13e",
        )
        self.assertEqual(self.contract["source_commit"], M24.EXPECTED_M23_COMMIT)

    def test_real_core_is_the_authoritative_qualified_boundary(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["primary_rtl"], "rtl/m16/frp_m16_core.sv")
        self.assertEqual(
            boundary["integration_rtl"],
            "rtl/m23/frp_m23_hardened_integration_boundary.sv",
        )
        core_harness = (ROOT / M24.CORE_HARNESS).read_text(encoding="utf-8")
        liveness_harness = (ROOT / M24.LIVENESS_HARNESS).read_text(encoding="utf-8")
        self.assertIn("frp_m16_core", core_harness)
        self.assertIn("frp_m16_core", liveness_harness)

    def test_core_ternary_contract_is_exact_and_immutable(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(boundary["balanced_ternary_semantic_values"], [-1, 0, 1])
        self.assertEqual(boundary["active_neutral_state"], 0)
        self.assertEqual(boundary["direct_opposite_polarity_transition"], "forbidden")

    def test_scheduler_contract_is_exact(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(boundary["service_scheduler_mode"], "free")

    def test_property_inventory_is_dense_and_complete(self) -> None:
        expected = [f"M24-P{index:02d}" for index in range(1, 37)]
        self.assertEqual(self.inventory["property_count"], 36)
        self.assertEqual(self.inventory["passed_count"], 36)
        self.assertEqual(self.inventory["failed_count"], 0)
        self.assertEqual(
            [item["property_id"] for item in self.inventory["properties"]],
            expected,
        )
        self.assertEqual({item["status"] for item in self.inventory["properties"]}, {"PASS"})

    def test_property_domains_cover_the_complete_m24_boundary(self) -> None:
        domains = {item["domain"] for item in self.inventory["properties"]}
        self.assertEqual(domains, set(self.contract["required_domains"]))
        counts = Counter(item["domain"] for item in self.inventory["properties"])
        self.assertGreaterEqual(counts["canonical_ternary"], 1)
        self.assertGreaterEqual(counts["scheduler_counter"], 1)
        self.assertGreaterEqual(counts["bounded_liveness"], 1)
        self.assertGreaterEqual(counts["reset_readiness"], 1)

    def test_every_property_token_is_bound_to_a_formal_harness(self) -> None:
        text = "\n".join(
            (ROOT / path).read_text(encoding="utf-8")
            for path in M24.FORMAL_HARNESSES
        )
        for index in range(1, 37):
            self.assertIn(f"M24_P{index:02d}", text)
        self.assertEqual(text.count("assume("), 6)

    def test_assumption_inventory_is_closed(self) -> None:
        expected = [f"M24-A{index:02d}" for index in range(1, 12)]
        self.assertEqual(self.evidence["assumption_count"], 11)
        self.assertEqual(
            [item["assumption_id"] for item in self.evidence["assumptions"]],
            expected,
        )
        self.assertEqual(self.evidence["unrecorded_assumption_count"], 0)
        self.assertEqual({item["status"] for item in self.evidence["assumptions"]}, {"DECLARED"})

    def test_bounds_are_exact_and_explicit(self) -> None:
        self.assertEqual(self.evidence["bound_count"], 5)
        self.assertEqual(
            [item["bound_id"] for item in self.evidence["bounds"]],
            [f"M24-B{index:02d}" for index in range(1, 6)],
        )
        self.assertEqual([item["depth"] for item in self.evidence["bounds"]], [1, 8, 3, 4, 7])
        self.assertEqual({item["status"] for item in self.evidence["bounds"]}, {"PASS"})

    def test_formal_runs_cover_every_property_once(self) -> None:
        self.assertEqual(self.evidence["proof_run_count"], 7)
        runs = self.evidence["proof_runs"]
        self.assertEqual([item["run_id"] for item in runs], [f"M24-R{index:02d}" for index in range(1, 8)])
        property_ids = [
            property_id
            for run in runs
            for property_id in run.get("property_ids", [])
        ]
        self.assertEqual(property_ids, [f"M24-P{index:02d}" for index in range(1, 37)])
        self.assertEqual(
            Counter(item["status"] for item in runs),
            {"PASS": 5, "EXPECTED_COUNTEREXAMPLE": 2},
        )

    def test_formal_tool_provenance_is_exact(self) -> None:
        tool = self.evidence["tool"]
        self.assertEqual(tool["package"], "yowasp-yosys")
        self.assertEqual(tool["package_version"], "0.68.0.0.post1208")
        self.assertEqual(tool["engine_version"], "0.68")
        self.assertEqual(tool["engine_git_sha"], "38e001a6f")
        self.assertEqual(tool["solver"], "minisat")

    def test_prepared_sources_preserve_real_module_bodies(self) -> None:
        prepared = M24.prepared_source_bytes(ROOT)
        scheduler = prepared["prepared/m16/frp_m16_scheduler.sv"].decode()
        core = prepared["prepared/m16/frp_m16_core.sv"].decode()
        boundary = prepared["prepared/m23/frp_m23_hardened_integration_boundary.sv"].decode()
        self.assertIn("module frp_m16_scheduler", scheduler)
        self.assertIn("module frp_m16_core", core)
        self.assertIn("module frp_m23_hardened_integration_boundary", boundary)
        self.assertNotIn("frp_m16_pkg::", "\n".join(raw.decode() for raw in prepared.values()))
        self.assertEqual(len(self.evidence["prepared_rtl_digest"]), 64)

    def test_retained_expected_counterexamples_are_exact(self) -> None:
        self.assertEqual(self.evidence["expected_counterexample_count"], 2)
        counterexamples = self.evidence["retained_counterexamples"]
        self.assertEqual(
            [item["counterexample_id"] for item in counterexamples],
            ["M24-N01", "M24-N02"],
        )
        self.assertEqual(
            counterexamples[0]["witness"],
            {"state_value": "10", "M24_N01_FALSE_CLAIM": "0"},
        )
        self.assertEqual(
            counterexamples[1]["witness"],
            {"state_candidate_d": "00", "M24_N02_FALSE_CLAIM": "0"},
        )

    def test_nested_digests_are_exact(self) -> None:
        for item in self.inventory["properties"]:
            candidate = {key: value for key, value in item.items() if key != "property_digest"}
            self.assertEqual(item["property_digest"], M24.object_digest(candidate))
        for item in self.evidence["assumptions"]:
            candidate = {key: value for key, value in item.items() if key != "assumption_digest"}
            self.assertEqual(item["assumption_digest"], M24.object_digest(candidate))
        for item in self.evidence["bounds"]:
            candidate = {key: value for key, value in item.items() if key != "bound_digest"}
            self.assertEqual(item["bound_digest"], M24.object_digest(candidate))

    def test_manifest_cardinalities_and_source_boundaries_are_exact(self) -> None:
        self.assertEqual(
            (
                self.manifest["source_count"],
                self.manifest["upstream_dependency_count"],
                self.manifest["artifact_count"],
            ),
            (15, 13, 3),
        )
        self.assertEqual(
            [item["path"] for item in self.manifest["sources"]],
            sorted((M24.WORKFLOW_PATH, *M24.TECHNICAL_SOURCE_PATHS)),
        )
        self.assertEqual(
            [item["path"] for item in self.manifest["upstream_dependencies"]],
            sorted(M24.UPSTREAM_SOURCE_PATHS),
        )
        for item in (*self.manifest["sources"], *self.manifest["upstream_dependencies"]):
            self.assertEqual(item["raw_sha256"], M24.sha256_bytes((ROOT / item["path"]).read_bytes()))

    def test_qualification_is_dense_and_complete(self) -> None:
        self.assertEqual(
            (
                self.qualification["check_count"],
                self.qualification["passed_count"],
                self.qualification["failed_count"],
            ),
            (76, 76, 0),
        )
        self.assertEqual(
            [item["check_id"] for item in self.qualification["checks"]],
            [f"Q{index:03d}" for index in range(1, 77)],
        )
        self.assertEqual(self.qualification["overall_status"], "PASS")

    def test_registry_and_all_schemas_are_complete(self) -> None:
        registry = json.loads((ROOT / M24.REGISTRY_PATH).read_text(encoding="utf-8"))
        self.assertEqual((registry["schema_version"], registry["record_count"]), ("2.6.0", 5))
        self.assertEqual([item["path"] for item in registry["records"]], list(M24.SCHEMA_PATHS.values()))
        mapping = {
            M24.CONTRACT_ARTIFACT: M24.CONTRACT_SCHEMA,
            M24.INVENTORY_ARTIFACT: M24.INVENTORY_SCHEMA,
            M24.EVIDENCE_ARTIFACT: M24.EVIDENCE_SCHEMA,
            M24.MANIFEST_ARTIFACT: M24.MANIFEST_SCHEMA,
            M24.QUALIFICATION_ARTIFACT: M24.QUALIFICATION_SCHEMA,
        }
        for artifact, schema in mapping.items():
            self.schemas.validate(schema, json.loads(self.outputs[artifact]), artifact)
        invalid = copy.deepcopy(self.contract)
        invalid["qualified_boundary"]["balanced_ternary_notation"] = "1/0/-1"
        with self.assertRaises(M24.ContractError):
            self.schemas.validate(M24.CONTRACT_SCHEMA, invalid, "invalid-ternary-contract")
        invalid = copy.deepcopy(self.contract)
        invalid["qualified_boundary"]["temporal_scheduler_modes"] = ["7/1", "1/7"]
        with self.assertRaises(M24.ContractError):
            self.schemas.validate(M24.CONTRACT_SCHEMA, invalid, "invalid-scheduler-contract")

    def test_generation_is_byte_stable(self) -> None:
        self.assertEqual(M24.build_outputs(ROOT, M24.EXPECTED_M23_COMMIT), self.outputs)

    def test_committed_verification_self_test_and_safety_boundaries_pass(self) -> None:
        verification = M24.verify(ROOT, M24.EXPECTED_M23_COMMIT)
        self.assertEqual((verification["status"], verification["artifact_count"]), ("PASS", 5))
        result = M24.self_test(ROOT, M24.EXPECTED_M23_COMMIT)
        self.assertEqual((result["check_count"], result["passed_count"]), (17, 17))
        with self.assertRaises(M24.ContractError):
            M24.validate_source_commit("0" * 40)
        for value in ("/absolute", "../escape", "a/../b", "a\\b"):
            with self.assertRaises(M24.SafetyError):
                M24.safe_relative_path(value)


if __name__ == "__main__":
    unittest.main()
