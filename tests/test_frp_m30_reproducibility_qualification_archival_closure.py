from __future__ import annotations

import copy
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

import frp_m30_reproducibility_qualification_archival_closure as m30


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class M30ConstantBoundaryTests(unittest.TestCase):
    def test_version_is_exact(self):
        self.assertEqual(m30.VERSION, "3.2.0")

    def test_release_is_exact(self):
        self.assertEqual(m30.RELEASE, "FRP v3.2.0")

    def test_milestone_is_exact(self):
        self.assertEqual(m30.MILESTONE, "M30")

    def test_objective_closes_the_planned_progression(self):
        self.assertEqual(
            m30.OBJECTIVE,
            "close the planned M17 through M30 architecture progression with "
            "reproducible qualification and archival evidence",
        )

    def test_source_commit_is_the_complete_m29_closure(self):
        self.assertEqual(
            m30.EXPECTED_M29_COMMIT,
            "ff3dd434da5dcbd9e8fa62444f658ed4c495b540",
        )

    def test_source_subject_is_exact(self):
        self.assertEqual(
            m30.EXPECTED_M29_SUBJECT,
            "Add M29 system integration and downstream compatibility closure",
        )

    def test_balanced_ternary_notation_is_exact(self):
        self.assertEqual(m30.CORE["balanced_ternary_notation"], "-1/0/1")

    def test_semantic_values_are_exact(self):
        self.assertEqual(m30.CORE["semantic_values"], [-1, 0, 1])

    def test_active_neutral_state_is_exact(self):
        self.assertEqual(m30.CORE["active_neutral_state"], 0)

    def test_temporal_scheduler_modes_are_exact(self):
        self.assertEqual(m30.CORE["temporal_scheduler_modes"], ["1/7", "7/1"])

    def test_free_service_mode_is_separate(self):
        self.assertEqual(m30.CORE["service_scheduler_mode"], "free")

    def test_opposite_routes_are_neutral_mediated(self):
        self.assertEqual(
            m30.CORE["opposite_polarity_routes"],
            [[-1, 0, 1], [1, 0, -1]],
        )

    def test_observatory_repository_is_preserved(self):
        self.assertEqual(
            m30.OBSERVATORY_BOUNDARY["repository"],
            "FRP-Trace-Observatory",
        )

    def test_observatory_direction_is_one_way(self):
        self.assertEqual(
            m30.OBSERVATORY_BOUNDARY["integration_direction"],
            "upstream_to_downstream_only",
        )

    def test_observatory_writeback_is_forbidden(self):
        self.assertEqual(
            m30.OBSERVATORY_BOUNDARY["downstream_writeback"], "forbidden"
        )

    def test_observatory_semantic_reimplementation_is_forbidden(self):
        self.assertEqual(
            m30.OBSERVATORY_BOUNDARY["downstream_semantic_reimplementation"],
            "forbidden",
        )

    def test_upstream_has_no_downstream_code_dependency(self):
        self.assertFalse(
            m30.OBSERVATORY_BOUNDARY["upstream_dependency_on_downstream_code"]
        )

    def test_m30_modifies_no_downstream_file(self):
        self.assertFalse(
            m30.OBSERVATORY_BOUNDARY["downstream_files_modified_by_m30"]
        )

    def test_workflow_filename_explicitly_says_workflow(self):
        self.assertEqual(len(m30.M30_WORKFLOWS), 3)
        for workflow in m30.M30_WORKFLOWS:
            with self.subTest(workflow=workflow):
                self.assertIn("workflow", Path(workflow).name)
                self.assertTrue(workflow.startswith(".github/workflows/"))


class M30SafetyAndSourceTests(unittest.TestCase):
    def test_safe_path_is_preserved(self):
        value = "artifacts/m30/example/example.json"
        self.assertEqual(m30._safe_path(value).as_posix(), value)

    def test_unsafe_paths_are_rejected(self):
        for value in (
            "",
            " /trimmed",
            "/absolute",
            "../escape",
            "a/../b",
            "a\\b",
            "a\x00b",
        ):
            with self.subTest(value=value), self.assertRaises(m30.ClosureError):
                m30._safe_path(value)

    def test_wrong_source_commit_is_rejected(self):
        with self.assertRaises(m30.ClosureError):
            m30.validate_source_boundary(ROOT, "0" * 40)

    def test_complete_source_boundary_passes(self):
        self.assertIsNone(
            m30.validate_source_boundary(ROOT, m30.EXPECTED_M29_COMMIT)
        )

    def test_milestone_path_detection_is_exact(self):
        self.assertEqual(m30._milestone_from_path("artifacts/m17/a.json"), "M17")
        self.assertEqual(m30._milestone_from_path("schemas/m29/a.json"), "M29")
        self.assertEqual(m30._milestone_from_path("README.md"), "repository")

    def test_generated_paths_are_exact_and_unique(self):
        self.assertEqual(len(m30.GENERATED_PATHS), 38)
        self.assertEqual(len(m30.GENERATED_PATHS), len(set(m30.GENERATED_PATHS)))

    def test_declared_schema_and_artifact_counts_are_exact(self):
        self.assertEqual(len(m30.SCHEMA_SPECS), 14)
        self.assertEqual(len(m30.ARTIFACT_PATHS), 14)

    def test_required_workflow_count_is_exact(self):
        self.assertEqual(len(m30.REQUIRED_WORKFLOWS), 14)

    def test_producer_count_is_exact(self):
        self.assertEqual(len(m30.PRODUCERS), 15)

    def test_canonical_json_has_one_terminal_newline(self):
        raw = m30._canonical_json({"b": 2, "a": 1})
        self.assertTrue(raw.endswith(b"\n"))
        self.assertFalse(raw.endswith(b"\n\n"))
        self.assertLess(raw.index(b'"a"'), raw.index(b'"b"'))

    def test_content_digest_ignores_only_the_digest_field(self):
        value = {"value": 1}
        digest = m30._content_digest(value)
        with_digest = {"value": 1, "content_digest": "0" * 64}
        self.assertEqual(digest, m30._content_digest(with_digest))
        self.assertNotEqual(digest, m30._content_digest({"value": 2}))

    def test_missing_workflow_success_record_is_rejected(self):
        fixture = m30._default_workflow_evidence(ROOT, m30.EXPECTED_M29_COMMIT)
        fixture["records"].pop()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            with self.assertRaises(m30.ClosureError):
                m30.load_workflow_evidence(
                    ROOT, m30.EXPECTED_M29_COMMIT, path
                )

    def test_failed_workflow_success_record_is_rejected(self):
        fixture = m30._default_workflow_evidence(ROOT, m30.EXPECTED_M29_COMMIT)
        fixture["records"][0]["conclusion"] = "failure"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            with self.assertRaises(m30.ClosureError):
                m30.load_workflow_evidence(
                    ROOT, m30.EXPECTED_M29_COMMIT, path
                )


class M30GeneratedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.summary = m30.build_outputs(
            ROOT, m30.EXPECTED_M29_COMMIT
        )
        cls.documents = {
            kind: load(path) for kind, path in m30.ARTIFACT_PATHS.items()
        }
        cls.schemas = {
            kind: load(spec[0]) for kind, spec in m30.SCHEMA_SPECS.items()
        }

    def test_complete_build_passes(self):
        self.assertEqual(self.summary["status"], "PASS")
        self.assertEqual(self.summary["generated_path_count"], 38)
        self.assertEqual(set(self.outputs), set(m30.GENERATED_PATHS))

    def test_committed_outputs_are_byte_exact(self):
        for relative, expected in self.outputs.items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), expected)

    def test_all_generated_json_schemas_are_valid(self):
        for kind, schema in self.schemas.items():
            with self.subTest(kind=kind):
                Draft202012Validator.check_schema(schema)

    def test_all_documents_validate_against_declared_schemas(self):
        for kind, document in self.documents.items():
            with self.subTest(kind=kind):
                errors = list(
                    Draft202012Validator(self.schemas[kind]).iter_errors(document)
                )
                self.assertEqual(errors, [])

    def test_all_document_content_digests_are_exact(self):
        for kind, document in self.documents.items():
            with self.subTest(kind=kind):
                self.assertEqual(
                    document["content_digest"], m30._content_digest(document)
                )

    def test_all_document_record_counts_are_exact(self):
        for kind, document in self.documents.items():
            with self.subTest(kind=kind):
                self.assertEqual(document["record_count"], len(document["records"]))

    def test_all_documents_repeat_the_exact_core(self):
        for kind, document in self.documents.items():
            with self.subTest(kind=kind):
                self.assertEqual(document["immutable_core"], m30.CORE)

    def test_all_documents_repeat_the_observatory_boundary(self):
        for kind, document in self.documents.items():
            with self.subTest(kind=kind):
                self.assertEqual(
                    document["observatory_boundary"], m30.OBSERVATORY_BOUNDARY
                )

    def test_milestone_evidence_index_is_complete(self):
        value = self.documents["milestone_evidence_index"]
        self.assertEqual(value["record_count"], 13)
        self.assertEqual(
            [item["milestone"] for item in value["records"]],
            [f"M{number}" for number in range(17, 30)],
        )
        self.assertTrue(all(item["status"] == "PASS" for item in value["records"]))

    def test_schema_index_count_is_exact(self):
        value = self.documents["schema_index"]
        self.assertEqual(value["record_count"], 124)
        self.assertEqual(value["summary"]["m30_schema_count"], 14)

    def test_canonical_artifact_index_count_is_exact(self):
        value = self.documents["canonical_artifact_index"]
        self.assertEqual(value["record_count"], 109)

    def test_producer_command_index_count_is_exact(self):
        value = self.documents["producer_command_index"]
        self.assertEqual(value["record_count"], 15)
        self.assertEqual(value["records"][-1]["milestone"], "M30")

    def test_workflow_index_count_is_exact(self):
        value = self.documents["workflow_index"]
        self.assertEqual(value["record_count"], 40)
        record = next(
            item for item in value["records"] if item["path"] == m30.M30_WORKFLOW
        )
        self.assertEqual(record["trigger"], "workflow_dispatch")
        self.assertIn("M30", record["name"])

    def test_required_successful_workflow_records_are_complete(self):
        value = self.documents["required_workflow_success_records"]
        self.assertEqual(value["record_count"], 14)
        self.assertEqual(
            [item["workflow_path"] for item in value["records"]],
            list(m30.REQUIRED_WORKFLOWS),
        )
        self.assertTrue(
            all(item["conclusion"] == "success" for item in value["records"])
        )

    def test_qualification_manifest_index_is_all_pass(self):
        value = self.documents["qualification_manifest_index"]
        self.assertGreaterEqual(value["record_count"], 20)
        self.assertTrue(all(item["status"] == "PASS" for item in value["records"]))

    def test_digest_inventory_is_complete_and_unique(self):
        value = self.documents["digest_inventory"]
        self.assertGreater(value["record_count"], 500)
        paths = [item["path"] for item in value["records"]]
        self.assertEqual(len(paths), len(set(paths)))

    def test_repository_alignment_has_six_documents(self):
        value = self.documents["repository_alignment_record"]
        self.assertEqual(value["record_count"], 6)
        self.assertTrue(all(item["status"] == "aligned" for item in value["records"]))

    def test_clean_environment_sequence_is_complete(self):
        value = self.documents["clean_environment_reproduction"]
        self.assertEqual(value["record_count"], 6)
        self.assertEqual(
            [item["sequence"] for item in value["records"]], list(range(1, 7))
        )

    def test_archival_metadata_is_complete(self):
        value = self.documents["archival_metadata"]
        self.assertEqual(value["record_count"], 12)
        fields = {item["field"]: item["value"] for item in value["records"]}
        self.assertEqual(fields["version"], "FRP v3.2.0")
        self.assertEqual(fields["source_commit"], m30.EXPECTED_M29_COMMIT)

    def test_reproducibility_qualification_is_all_pass(self):
        value = self.documents["reproducibility_qualification"]
        self.assertEqual(value["summary"]["failed_count"], 0)
        self.assertEqual(
            value["summary"]["check_count"], value["record_count"]
        )
        self.assertTrue(all(item["result"] == "PASS" for item in value["records"]))

    def test_release_package_digest_matches_manifest(self):
        raw = (ROOT / m30.PACKAGE_PATH).read_bytes()
        value = self.documents["release_package_manifest"]
        self.assertEqual(value["summary"]["package_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(value["summary"]["package_byte_length"], len(raw))

    def test_release_package_gzip_stream_is_valid(self):
        raw = (ROOT / m30.PACKAGE_PATH).read_bytes()
        self.assertTrue(gzip.decompress(raw))

    def test_release_package_verifies_member_by_member(self):
        expected = m30._package_expected_from_output(
            ROOT, m30.EXPECTED_M29_COMMIT, self.outputs
        )
        observed = m30.verify_archive(self.outputs[m30.PACKAGE_PATH], expected)
        self.assertGreater(len(observed), 500)

    def test_tampered_release_package_is_rejected(self):
        raw = bytearray(self.outputs[m30.PACKAGE_PATH])
        raw[-1] ^= 1
        with self.assertRaises(m30.ClosureError):
            m30.verify_archive(bytes(raw), {})

    def test_release_documents_are_complete(self):
        for relative in m30.RELEASE_DOCUMENTS:
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("FRP v3.2.0", text)
                self.assertIn("M30", text)
                self.assertIn("PASS", text)

    def test_current_documents_are_aligned_to_v3_2_0(self):
        for relative in m30.ALIGNED_DOCUMENTS:
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("3.2.0", text)

    def test_readme_preserves_the_m16_historical_anchor(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("M16 RTL Core Realization", text)
        self.assertIn("M16", text)

    def test_no_forbidden_positive_sign_notation(self):
        forbidden = "-1/0/" + "+1"
        paths = [ROOT / m30.SOURCE_PATH, ROOT / m30.TEST_PATH]
        paths.extend(ROOT / relative for relative in m30.GENERATED_PATHS if relative != m30.PACKAGE_PATH)
        paths.extend(ROOT / workflow for workflow in m30.M30_WORKFLOWS)
        for path in paths:
            with self.subTest(path=str(path)):
                self.assertNotIn(forbidden, path.read_text(encoding="utf-8"))

    def test_all_text_outputs_end_with_one_newline(self):
        for relative in m30.GENERATED_PATHS:
            if relative == m30.PACKAGE_PATH:
                continue
            raw = (ROOT / relative).read_bytes()
            with self.subTest(path=relative):
                self.assertTrue(raw.endswith(b"\n"))
                self.assertFalse(raw.endswith(b"\n\n"))


if __name__ == "__main__":
    unittest.main()
