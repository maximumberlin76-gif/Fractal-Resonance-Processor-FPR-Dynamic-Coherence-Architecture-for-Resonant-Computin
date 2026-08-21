from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import frp_m28_trace_observatory_upstream_interchange as m28


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def refresh_digest(value: dict, field: str) -> dict:
    result = copy.deepcopy(value)
    result.pop(field, None)
    result[field] = m28.object_digest(result)
    return result


class M28ConstantBoundaryTests(unittest.TestCase):
    def test_version_and_milestone_are_exact(self):
        self.assertEqual(m28.VERSION, "3.0.0")
        self.assertEqual(m28.MILESTONE, "M28")

    def test_source_commit_is_exact_m27_closure(self):
        self.assertEqual(
            m28.EXPECTED_M27_COMMIT,
            "23e464206f85cd9473101d9221027ee33d9dd094",
        )
        self.assertEqual(
            m28.EXPECTED_M27_SUBJECT,
            "Add M27 long-run stability and telemetry qualification",
        )

    def test_existing_observatory_baseline_is_pinned(self):
        self.assertEqual(m28.OBSERVATORY_REPOSITORY, "FRP-Trace-Observatory")
        self.assertEqual(
            m28.OBSERVATORY_AUDITED_COMMIT,
            "a9d71657c56221d0d9b72fb6e954e0028f096a9e",
        )
        self.assertEqual(m28.OBSERVATORY_TEST_COUNT, 275)

    def test_existing_observatory_modes_are_exact(self):
        self.assertEqual(
            m28.OBSERVATORY_MODES,
            (
                "artifact_auditor",
                "ternary_transition_visualizer",
                "trace_explorer",
            ),
        )

    def test_workflow_filename_declares_workflow(self):
        self.assertIn("workflow", Path(m28.WORKFLOW_PATH).name)
        self.assertTrue(m28.WORKFLOW_PATH.startswith(".github/workflows/"))


class M28PathSafetyTests(unittest.TestCase):
    def test_safe_relative_paths_are_preserved(self):
        path = m28.safe_relative_path("artifacts/m28/example.json")
        self.assertEqual(path.as_posix(), "artifacts/m28/example.json")

    def test_unsafe_paths_are_rejected(self):
        for value in (
            "",
            "/absolute",
            "../escape",
            "a/../b",
            "a//b",
            "a\\b",
            "a\x00b",
        ):
            with self.subTest(value=value), self.assertRaises(m28.SafetyError):
                m28.safe_relative_path(value)

    def test_wrong_source_commit_is_rejected(self):
        with self.assertRaises(m28.ContractError):
            m28.validate_source_commit("0" * 40)


class M28GeneratedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verification = m28.verify(ROOT, m28.EXPECTED_M27_COMMIT)
        cls.contract = load(m28.CONTRACT_ARTIFACT)
        cls.trace = load(m28.TRACE_ARTIFACT)
        cls.fixtures = load(m28.FIXTURE_ARTIFACT)
        cls.registry = load(m28.REGISTRY_ARTIFACT)
        cls.qualification = load(m28.QUALIFICATION_ARTIFACT)

    def test_complete_verification_passes(self):
        self.assertEqual(self.verification["status"], "PASS")
        self.assertEqual(self.verification["schema_count"], 5)
        self.assertEqual(self.verification["artifact_count"], 5)

    def test_contract_preserves_immutable_core(self):
        core = self.contract["immutable_core"]
        self.assertEqual(core["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(core["semantic_values"], [-1, 0, 1])
        self.assertEqual(core["active_neutral_state"], 0)
        self.assertEqual(core["temporal_scheduler_modes"], ["1/7", "7/1"])

    def test_contract_extends_existing_scaffold(self):
        baseline = self.contract["consumer_scaffold_baseline"]
        self.assertEqual(baseline["repository"], "FRP-Trace-Observatory")
        self.assertEqual(baseline["implementation_action"], "extend_existing_scaffold")
        self.assertEqual(baseline["verified_test_count"], 275)
        self.assertEqual(
            {item["mode"] for item in baseline["implemented_layers"]},
            set(m28.OBSERVATORY_MODES),
        )

    def test_contract_is_strictly_one_way(self):
        direction = self.contract["integration_direction"]
        self.assertEqual(direction["direction"], "upstream_to_downstream_only")
        self.assertTrue(direction["upstream_semantic_authority"])
        self.assertEqual(direction["downstream_writeback"], "forbidden")
        self.assertEqual(direction["downstream_source_mutation"], "forbidden")

    def test_contract_keeps_ui_outside_upstream(self):
        scope = self.contract["export_scope"]
        self.assertFalse(scope["ui_dependencies_in_upstream"])
        self.assertFalse(scope["downstream_repository_files_modified"])

    def test_contract_separates_absence_from_zero(self):
        data_contract = self.contract["data_contract"]
        self.assertEqual(data_contract["missing_field_policy"], "remain_absent")
        self.assertFalse(data_contract["absent_is_zero"])

    def test_trace_bundle_has_exact_dataset_order(self):
        self.assertEqual(
            [dataset["dataset_id"] for dataset in self.trace["datasets"]],
            [
                "m16-rtl-execution",
                "m16-fpga-preparation-execution",
                "m27-long-run-checkpoints",
            ],
        )

    def test_trace_bundle_has_exact_record_counts(self):
        self.assertEqual(self.trace["dataset_count"], 3)
        self.assertEqual(
            [dataset["record_count"] for dataset in self.trace["datasets"]],
            [96, 4, 96],
        )
        self.assertEqual(self.trace["record_count"], 196)

    def test_trace_bundle_preserves_source_records(self):
        rtl = load(m28.M19_RTL_TRACE)["records"]
        fpga = load(m28.M19_FPGA_TRACE)["records"]
        long_run = load(m28.M27_CHECKPOINTS)
        checkpoints = [
            checkpoint
            for profile in long_run["profiles"]
            for checkpoint in profile["checkpoints"]
        ]
        self.assertEqual(self.trace["datasets"][0]["records"], rtl)
        self.assertEqual(self.trace["datasets"][1]["records"], fpga)
        self.assertEqual(self.trace["datasets"][2]["records"], checkpoints)

    def test_trace_bundle_preserves_canonical_states(self):
        self.assertEqual(self.trace["canonical_ternary_domain"], [-1, 0, 1])
        for record in self.trace["datasets"][0]["records"]:
            self.assertTrue(set(record["retained_state_after"]) <= {-1, 0, 1})
        for record in self.trace["datasets"][2]["records"]:
            self.assertTrue(set(record["states"]) <= {-1, 0, 1})

    def test_trace_bundle_preserves_zero_safety_counters(self):
        for dataset in self.trace["datasets"][:2]:
            for record in dataset["records"]:
                events = record["events"]
                self.assertEqual(events["actual_direct_events"], 0)
                self.assertEqual(events["reserved_state_events"], 0)
                self.assertEqual(events["queue_overflow_events"], 0)
        for record in self.trace["datasets"][2]["records"]:
            self.assertEqual(record["actual_direct_events"], 0)
            self.assertEqual(record["reserved_state_events"], 0)
            self.assertEqual(record["queue_overflow_events"], 0)

    def test_trace_bundle_covers_all_existing_modes(self):
        for dataset in self.trace["datasets"]:
            self.assertEqual(
                dataset["observatory_modes"], list(m28.OBSERVATORY_MODES)
            )

    def test_trace_dataset_digests_are_exact(self):
        for dataset in self.trace["datasets"]:
            self.assertEqual(
                dataset["records_digest"],
                m28.object_digest(dataset["records"]),
            )

    def test_fixture_manifest_covers_exact_sources(self):
        self.assertEqual(self.fixtures["fixture_count"], 6)
        self.assertEqual(
            [fixture["fixture_id"] for fixture in self.fixtures["fixtures"]],
            [spec["fixture_id"] for spec in m28.SOURCE_FIXTURE_SPECS],
        )

    def test_fixture_manifest_uses_raw_byte_digests(self):
        self.assertEqual(self.fixtures["digest_contract"]["algorithm"], "sha256")
        self.assertEqual(
            self.fixtures["digest_contract"]["scope"], "raw_source_bytes"
        )
        self.assertEqual(
            self.fixtures["copy_requirement"], "unchanged_upstream_bytes"
        )

    def test_compatibility_registry_has_exact_identifiers(self):
        self.assertEqual(self.registry["record_count"], 5)
        self.assertEqual(
            [record["identifier"] for record in self.registry["records"]],
            list(m28.SCHEMA_PATHS),
        )
        self.assertEqual(
            self.registry["consumer_registration_state"],
            "upstream_published_downstream_registration_required",
        )

    def test_trace_compatibility_record_routes_to_all_modes(self):
        trace_record = self.registry["records"][1]
        self.assertEqual(trace_record["identifier"], m28.TRACE_SCHEMA_ID)
        self.assertEqual(
            trace_record["observatory_modes"], list(m28.OBSERVATORY_MODES)
        )
        self.assertEqual(
            trace_record["downstream_registration_state"],
            "registration_required",
        )

    def test_qualification_has_only_passing_checks(self):
        self.assertEqual(self.qualification["status"], "PASS")
        self.assertEqual(self.qualification["check_count"], 30)
        self.assertEqual(self.qualification["passed_count"], 30)
        self.assertEqual(self.qualification["failed_count"], 0)
        self.assertTrue(
            all(check["status"] == "PASS" for check in self.qualification["checks"])
        )

    def test_all_documents_end_with_one_newline(self):
        for relative in m28.GENERATED_PATHS:
            raw = (ROOT / relative).read_bytes()
            self.assertTrue(raw.endswith(b"\n"), relative)
            self.assertFalse(raw.endswith(b"\n\n"), relative)

    def test_no_forbidden_positive_sign_notation(self):
        forbidden = "-1/0/" + "+1"
        paths = [
            ROOT / "frp_m28_trace_observatory_upstream_interchange.py",
            ROOT / "tests/test_frp_m28_trace_observatory_upstream_interchange.py",
        ]
        paths.extend(ROOT / relative for relative in m28.GENERATED_PATHS)
        for path in paths:
            self.assertNotIn(forbidden, path.read_text(encoding="utf-8"), str(path))


class M28NegativeValidationTests(unittest.TestCase):
    def setUp(self):
        self.contract = load(m28.CONTRACT_ARTIFACT)
        self.trace = load(m28.TRACE_ARTIFACT)
        self.fixtures = load(m28.FIXTURE_ARTIFACT)
        self.registry = load(m28.REGISTRY_ARTIFACT)

    def test_contract_rejects_ternary_notation_change(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["balanced_ternary_notation"] = "ternary"
        value = refresh_digest(value, "contract_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_contract(value, m28.EXPECTED_M27_COMMIT)

    def test_contract_rejects_scheduler_change(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["temporal_scheduler_modes"] = ["7/1"]
        value = refresh_digest(value, "contract_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_contract(value, m28.EXPECTED_M27_COMMIT)

    def test_contract_rejects_writeback(self):
        value = copy.deepcopy(self.contract)
        value["integration_direction"]["downstream_writeback"] = "allowed"
        value = refresh_digest(value, "contract_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_contract(value, m28.EXPECTED_M27_COMMIT)

    def test_trace_rejects_source_record_mutation(self):
        value = copy.deepcopy(self.trace)
        value["datasets"][0]["records"][0]["core_ready"] = False
        value["datasets"][0]["records_digest"] = m28.object_digest(
            value["datasets"][0]["records"]
        )
        value = refresh_digest(value, "bundle_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_trace_bundle(value, ROOT, m28.EXPECTED_M27_COMMIT)

    def test_trace_rejects_nonzero_safety_event(self):
        value = copy.deepcopy(self.trace)
        value["datasets"][0]["records"][0]["events"][
            "actual_direct_events"
        ] = 1
        value["datasets"][0]["records_digest"] = m28.object_digest(
            value["datasets"][0]["records"]
        )
        value = refresh_digest(value, "bundle_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_trace_bundle(value, ROOT, m28.EXPECTED_M27_COMMIT)

    def test_fixture_rejects_digest_change(self):
        value = copy.deepcopy(self.fixtures)
        value["fixtures"][0]["artifact_raw_sha256"] = "0" * 64
        value["fixture_set_digest"] = m28.object_digest(value["fixtures"])
        value = refresh_digest(value, "manifest_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_fixture_manifest(value, ROOT, m28.EXPECTED_M27_COMMIT)

    def test_registry_rejects_mode_loss(self):
        value = copy.deepcopy(self.registry)
        value["records"][1]["observatory_modes"] = ["artifact_auditor"]
        value = refresh_digest(value, "registry_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_compatibility_registry(value, m28.EXPECTED_M27_COMMIT)

    def test_registry_rejects_identifier_alias(self):
        value = copy.deepcopy(self.registry)
        value["records"][0]["identifier"] = "frp.m28.alias.v3.0.0"
        value = refresh_digest(value, "registry_digest")
        with self.assertRaises(m28.ContractError):
            m28.validate_compatibility_registry(value, m28.EXPECTED_M27_COMMIT)


class M28DeterminismTests(unittest.TestCase):
    def test_two_complete_generations_are_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="m28-a-") as first_dir:
            with tempfile.TemporaryDirectory(prefix="m28-b-") as second_dir:
                first_root = Path(first_dir)
                second_root = Path(second_dir)
                first = m28.generate(ROOT, first_root, m28.EXPECTED_M27_COMMIT)
                second = m28.generate(ROOT, second_root, m28.EXPECTED_M27_COMMIT)
                self.assertEqual(first, second)
                for relative in m28.GENERATED_PATHS:
                    self.assertEqual(
                        (first_root / relative).read_bytes(),
                        (second_root / relative).read_bytes(),
                        relative,
                    )

    def test_self_test_passes_all_negative_controls(self):
        result = m28.self_test(ROOT, m28.EXPECTED_M27_COMMIT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["check_count"], 6)
        self.assertTrue(all(check["status"] == "PASS" for check in result["checks"]))


if __name__ == "__main__":
    unittest.main()
