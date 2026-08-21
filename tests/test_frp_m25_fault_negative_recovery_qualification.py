"""Tests for FRP M25 fault, negative-path, and recovery qualification."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

import frp_m25_fault_negative_recovery_qualification as M25
import frp_m25_safe_artifact_validator as SAFE


ROOT = Path(__file__).resolve().parents[1]


class M25FaultNegativeRecoveryTests(unittest.TestCase):
    """Exercise the complete M25 contract, fixtures, evidence, and safety."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = M25.build_outputs(ROOT, M25.EXPECTED_M24_COMMIT)
        cls.contract = json.loads(cls.outputs[M25.CONTRACT_ARTIFACT])
        cls.classifications = json.loads(cls.outputs[M25.CLASSIFICATION_ARTIFACT])
        cls.fixtures = json.loads(cls.outputs[M25.FIXTURE_ARTIFACT])
        cls.evidence = json.loads(cls.outputs[M25.EVIDENCE_ARTIFACT])
        cls.manifest = json.loads(cls.outputs[M25.MANIFEST_ARTIFACT])
        cls.qualification = json.loads(cls.outputs[M25.QUALIFICATION_ARTIFACT])

    def test_release_milestone_and_source_commit_are_exact(self) -> None:
        self.assertEqual((M25.VERSION, M25.MILESTONE), ("2.7.0", "M25"))
        self.assertEqual(self.contract["source_commit"], "a01fb687fd1e4f0159f0d8cd885863afb8b87a1e")
        self.assertEqual(self.contract["release"], "FRP v2.7.0")
        with self.assertRaises(M25.ContractError):
            M25.validate_source_commit("0" * 40)

    def test_actual_core_is_the_authoritative_boundary(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["authoritative_rtl"], "rtl/m16/frp_m16_core.sv")
        for relative in (M25.M16_PACKAGE, *M25.M16_MODULES):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_core_ternary_contract_is_exact_and_immutable(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(boundary["semantic_values"], [-1, 0, 1])
        self.assertEqual(boundary["reserved_encoding"], "2'b10")
        self.assertEqual(boundary["active_neutral_state"], 0)
        self.assertEqual(boundary["direct_opposite_polarity_transition"], "forbidden")
        technical_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in M25.TECHNICAL_SOURCE_PATHS)
        self.assertNotIn("-1/0/" + "+1", technical_text)

    def test_scheduler_contract_is_exact(self) -> None:
        boundary = self.contract["qualified_boundary"]
        self.assertEqual(boundary["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(boundary["service_scheduler_mode"], "free")

    def test_required_scope_is_complete_and_ordered(self) -> None:
        self.assertEqual(tuple(self.contract["required_scope"]), M25.REQUIRED_SCOPE)
        self.assertEqual(len(self.contract["required_scope"]), 13)
        self.assertEqual(self.fixtures["scope_count"], 13)
        self.assertEqual({item["scope"] for item in self.fixtures["fixtures"]}, set(M25.REQUIRED_SCOPE))

    def test_fixture_inventory_is_dense_and_deterministic(self) -> None:
        fixtures = self.fixtures["fixtures"]
        self.assertEqual([item["fixture_id"] for item in fixtures], [f"M25-F{i:02d}" for i in range(1, 14)])
        self.assertTrue(all(item["deterministic"] for item in fixtures))
        for item in fixtures:
            payload = dict(item)
            digest = payload.pop("fixture_digest")
            self.assertEqual(digest, M25.object_digest(payload))
            self.assertEqual(M25.execute_fixture(item["fixture_id"]), M25.execute_fixture(item["fixture_id"]))

    def test_machine_failure_registry_is_dense_unique_and_complete(self) -> None:
        records = self.classifications["records"]
        self.assertEqual([item["classification_id"] for item in records], [f"M25-C{i:02d}" for i in range(1, 20)])
        self.assertEqual(len({item["code"] for item in records}), 19)
        fixture_codes = {item["classification"] for item in self.fixtures["fixtures"]}
        self.assertTrue(fixture_codes.issubset({item["code"] for item in records}))
        for item in records:
            payload = dict(item)
            digest = payload.pop("classification_digest")
            self.assertEqual(digest, M25.object_digest(payload))

    def test_formal_inventory_is_dense_and_every_property_is_bound_once(self) -> None:
        formal = self.evidence["formal"]
        expected = [f"M25-P{i:02d}" for i in range(1, 26)]
        self.assertEqual([item["property_id"] for item in M25.PROPERTY_SPECS], expected)
        observed = [value for run in formal["runs"] for value in run["property_ids"]]
        self.assertEqual(observed, expected)
        self.assertEqual((formal["property_count"], formal["passed_property_count"], formal["failed_property_count"]), (25, 25, 0))

    def test_formal_tool_provenance_and_bounds_are_exact(self) -> None:
        formal = self.evidence["formal"]
        self.assertEqual(formal["tool"]["package_version"], "0.68.0.0.post1208")
        self.assertEqual(formal["tool"]["engine_version"], "0.68")
        self.assertEqual(formal["tool"]["engine_git_sha"], "38e001a6f")
        self.assertEqual([(run["run_id"], run["depth"]) for run in formal["runs"]], [("M25-R01", 1), ("M25-R02", 3), ("M25-R03", 6)])
        self.assertTrue(all(run["status"] == "PASS" for run in formal["runs"]))

    def test_every_formal_property_token_is_present(self) -> None:
        source = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in M25.FORMAL_HARNESSES)
        for index in range(1, 26):
            self.assertGreaterEqual(source.count(f"M25_P{index:02d}"), 2)

    def test_recovery_evidence_is_exact(self) -> None:
        recovery = self.evidence["recovery_state"]
        self.assertEqual(recovery["final_state"], [1])
        self.assertEqual(recovery["final_pending"], [0])
        self.assertEqual(recovery["active_neutral"], 0)
        self.assertEqual(recovery["actual_direct_events"], 0)
        self.assertEqual(recovery["qualified_queue_overflow_events"], 0)
        self.assertEqual(self.evidence["fixture_result_count"], self.evidence["passed_fixture_count"])
        self.assertEqual(self.evidence["failed_fixture_count"], 0)

    def test_digest_mismatch_is_classified_and_rejected(self) -> None:
        raw = b'{"artifact_id":"x"}\n'
        with self.assertRaises(SAFE.ValidationFailure) as caught:
            SAFE.validate_package_bytes({"a.json": raw + b" "}, ("a.json",), {"a.json": SAFE.sha256_bytes(raw)})
        self.assertEqual(caught.exception.code, SAFE.FailureCode.DIGEST_MISMATCH)

    def test_malformed_duplicate_key_and_non_object_json_are_rejected(self) -> None:
        cases = (
            (b'{"a":', SAFE.FailureCode.MALFORMED_JSON),
            (b'{"a":1,"a":2}', SAFE.FailureCode.DUPLICATE_JSON_KEY),
            (b'[1,2,3]', SAFE.FailureCode.INVALID_DOCUMENT),
        )
        for raw, code in cases:
            with self.subTest(code=code), self.assertRaises(SAFE.ValidationFailure) as caught:
                SAFE.decode_json_object(raw, "fixture")
            self.assertEqual(caught.exception.code, code)

    def test_incomplete_and_unexpected_packages_are_rejected(self) -> None:
        raw = b'{"artifact_id":"x"}\n'
        digest = SAFE.sha256_bytes(raw)
        with self.assertRaises(SAFE.ValidationFailure) as caught:
            SAFE.validate_package_bytes({"a.json": raw}, ("a.json", "b.json"), {"a.json": digest, "b.json": digest})
        self.assertEqual(caught.exception.code, SAFE.FailureCode.INCOMPLETE_PACKAGE)
        with self.assertRaises(SAFE.ValidationFailure) as caught:
            SAFE.validate_package_bytes({"a.json": raw, "b.json": raw}, ("a.json",), {"a.json": digest})
        self.assertEqual(caught.exception.code, SAFE.FailureCode.UNEXPECTED_ARTIFACT)

    def test_unsafe_paths_and_oversized_artifacts_are_rejected(self) -> None:
        for value in ("/absolute", "../escape", "a/../b", "a\\b", ""):
            with self.subTest(value=value), self.assertRaises(SAFE.ValidationFailure) as caught:
                SAFE.safe_relative_path(value)
            self.assertEqual(caught.exception.code, SAFE.FailureCode.UNSAFE_PATH)
        with self.assertRaises(SAFE.ValidationFailure) as caught:
            SAFE.decode_json_object(b" " * (SAFE.MAX_ARTIFACT_BYTES + 1), "oversized")
        self.assertEqual(caught.exception.code, SAFE.FailureCode.OVERSIZED_ARTIFACT)

    def test_artifact_validator_has_no_code_execution_surface(self) -> None:
        source = (ROOT / "frp_m25_safe_artifact_validator.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_modules = {"subprocess", "pickle", "marshal", "shelve", "importlib", "yaml"}
        forbidden_calls = {"eval", "exec", "compile", "__import__", "system", "popen", "Popen", "run", "call", "check_call", "check_output"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(alias.name.split(".")[0] not in forbidden_modules for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0], forbidden_modules)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, forbidden_calls)
                elif isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, forbidden_calls)

    def test_schema_registry_and_all_artifacts_validate(self) -> None:
        registry = json.loads((ROOT / M25.REGISTRY_PATH).read_text(encoding="utf-8"))
        self.assertEqual([item["schema_id"] for item in registry["records"]], list(M25.SCHEMA_PATHS))
        self.assertEqual([item["path"] for item in registry["records"]], list(M25.SCHEMA_PATHS.values()))
        schemas = M25.SchemaContext(ROOT)
        mapping = {
            M25.CONTRACT_ARTIFACT: M25.CONTRACT_SCHEMA,
            M25.CLASSIFICATION_ARTIFACT: M25.CLASSIFICATION_SCHEMA,
            M25.FIXTURE_ARTIFACT: M25.FIXTURE_SCHEMA,
            M25.EVIDENCE_ARTIFACT: M25.EVIDENCE_SCHEMA,
            M25.MANIFEST_ARTIFACT: M25.MANIFEST_SCHEMA,
            M25.QUALIFICATION_ARTIFACT: M25.QUALIFICATION_SCHEMA,
        }
        for artifact, schema in mapping.items():
            schemas.validate(schema, json.loads(self.outputs[artifact]), artifact)
        invalid = copy.deepcopy(self.contract)
        invalid["qualified_boundary"]["balanced_ternary_notation"] = "-1/0/" + "+1"
        with self.assertRaises(M25.ContractError):
            schemas.validate(M25.CONTRACT_SCHEMA, invalid, "invalid-core-notation")

    def test_nested_and_top_level_digests_are_exact(self) -> None:
        for document, field in (
            (self.contract, "contract_digest"),
            (self.classifications, "classification_set_digest"),
            (self.fixtures, "fixture_set_digest"),
            (self.evidence, "evidence_digest"),
            (self.manifest, "manifest_digest"),
            (self.qualification, "qualification_digest"),
        ):
            payload = dict(document)
            digest = payload.pop(field)
            self.assertEqual(digest, M25.object_digest(payload))

    def test_manifest_boundaries_and_raw_digests_are_exact(self) -> None:
        self.assertEqual(self.manifest["source_count"], len((M25.WORKFLOW_PATH, *M25.TECHNICAL_SOURCE_PATHS)))
        self.assertEqual(self.manifest["upstream_dependency_count"], len(M25.UPSTREAM_SOURCE_PATHS))
        self.assertEqual(self.manifest["artifact_count"], 4)
        for collection in (self.manifest["sources"], self.manifest["upstream_dependencies"]):
            for record in collection:
                raw = (ROOT / record["path"]).read_bytes()
                self.assertEqual(record["bytes"], len(raw))
                self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())

    def test_qualification_is_complete(self) -> None:
        self.assertEqual(self.qualification["overall_status"], "PASS")
        self.assertEqual(self.qualification["check_count"], self.qualification["passed_count"])
        self.assertEqual(self.qualification["failed_count"], 0)
        categories = {item["category"] for item in self.qualification["checks"]}
        self.assertEqual(categories, {"identity", "scope", "fixture", "fixture_result", "formal_property", "formal_run", "classification", "schema", "closure", "manifest", "recovery"})

    def test_generation_is_byte_stable(self) -> None:
        self.assertEqual(M25.build_outputs(ROOT, M25.EXPECTED_M24_COMMIT), self.outputs)

    def test_committed_verification_and_self_test_pass(self) -> None:
        verification = M25.verify(ROOT, M25.EXPECTED_M24_COMMIT)
        self.assertEqual((verification["status"], verification["artifact_count"]), ("PASS", 6))
        result = M25.self_test(ROOT, M25.EXPECTED_M24_COMMIT)
        self.assertEqual((result["check_count"], result["passed_count"], result["failed_count"]), (17, 17, 0))


if __name__ == "__main__":
    unittest.main()
