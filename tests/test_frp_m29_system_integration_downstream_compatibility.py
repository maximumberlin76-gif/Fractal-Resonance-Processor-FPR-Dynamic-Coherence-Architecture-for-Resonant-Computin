from __future__ import annotations

import base64
import copy
import json
import unittest
from pathlib import Path

import frp_m29_system_integration_downstream_compatibility as m29


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def refresh(value: dict, field: str) -> dict:
    return m29.with_digest(copy.deepcopy(value), field)


class M29ConstantBoundaryTests(unittest.TestCase):
    def test_version_and_milestone_are_exact(self):
        self.assertEqual(m29.VERSION, "3.1.0")
        self.assertEqual(m29.MILESTONE, "M29")

    def test_objective_matches_the_roadmap(self):
        self.assertEqual(
            m29.OBJECTIVE,
            "close the published integration boundary without coupling FRP "
            "qualification to downstream implementation code",
        )

    def test_source_commit_is_the_complete_m28_closure(self):
        self.assertEqual(
            m29.EXPECTED_M28_COMMIT,
            "a1c0bb2fa0a4731b9339e6cd996589e1bf226c04",
        )
        self.assertEqual(
            m29.EXPECTED_M28_SUBJECT,
            "Add M28 hierarchical scaling and hotspot-containment realization",
        )

    def test_preserved_m28_observatory_commit_is_exact(self):
        self.assertEqual(
            m29.PRESERVED_M28_OBSERVATORY_COMMIT,
            "566a4ff88baa57f844691b46937552253e095434",
        )

    def test_existing_observatory_baseline_is_pinned(self):
        self.assertEqual(m29.OBSERVATORY_REPOSITORY, "FRP-Trace-Observatory")
        self.assertEqual(
            m29.OBSERVATORY_AUDITED_COMMIT,
            "a9d71657c56221d0d9b72fb6e954e0028f096a9e",
        )
        self.assertEqual(m29.OBSERVATORY_TEST_COUNT, 275)

    def test_existing_observatory_modes_are_exact(self):
        self.assertEqual(
            m29.OBSERVATORY_MODES,
            (
                "artifact_auditor",
                "ternary_transition_visualizer",
                "trace_explorer",
            ),
        )

    def test_workflow_filename_explicitly_declares_workflow(self):
        self.assertIn("workflow", Path(m29.WORKFLOW_PATH).name)
        self.assertTrue(m29.WORKFLOW_PATH.startswith(".github/workflows/"))

    def test_generated_path_set_is_exact_and_unique(self):
        self.assertEqual(len(m29.SCHEMA_PATHS), 13)
        self.assertEqual(len(m29.DOCUMENT_SCHEMA_IDS), 13)
        self.assertEqual(len(m29.GENERATED_PATHS), 26)
        self.assertEqual(len(m29.GENERATED_PATHS), len(set(m29.GENERATED_PATHS)))


class M29PathAndSourceSafetyTests(unittest.TestCase):
    def test_safe_relative_path_is_preserved(self):
        value = "artifacts/m29/example/example.json"
        self.assertEqual(m29.safe_relative_path(value).as_posix(), value)

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
            with self.subTest(value=value), self.assertRaises(m29.SafetyError):
                m29.safe_relative_path(value)

    def test_wrong_source_commit_is_rejected(self):
        with self.assertRaises(m29.ContractError):
            m29.validate_source_commit("0" * 40)

    def test_milestone_path_boundary_is_exact(self):
        self.assertEqual(m29.milestone_from_path("artifacts/m18/a.json"), "M18")
        self.assertEqual(m29.milestone_from_path("schemas/m28/a.json"), "M28")
        with self.assertRaises(m29.ContractError):
            m29.milestone_from_path("artifacts/m29/a.json")


class M29GeneratedBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verification = m29.verify(ROOT, m29.EXPECTED_M28_COMMIT)
        cls.contract = load(m29.CONTRACT_ARTIFACT)
        cls.schemas = load(m29.SCHEMA_REGISTRY)
        cls.artifacts = load(m29.ARTIFACT_REGISTRY)
        cls.compatibility = load(m29.COMPATIBILITY_ARTIFACT)
        cls.package = load(m29.DEMO_PACKAGE_ARTIFACT)
        cls.manifest = load(m29.PACKAGE_MANIFEST_ARTIFACT)
        cls.producers = load(m29.PRODUCER_REGISTRY_ARTIFACT)
        cls.policy = load(m29.IMMUTABLE_POLICY_ARTIFACT)
        cls.provenance = load(m29.PROVENANCE_ARTIFACT)
        cls.unsupported = load(m29.UNSUPPORTED_ARTIFACT)
        cls.vectors = load(m29.CONSUMPTION_VECTORS_ARTIFACT)
        cls.releases = load(m29.RELEASE_RECORDS_ARTIFACT)
        cls.qualification = load(m29.QUALIFICATION_ARTIFACT)

    def test_complete_verification_passes(self):
        self.assertEqual(self.verification["status"], "PASS")
        self.assertEqual(self.verification["generated_path_count"], 26)
        self.assertEqual(self.verification["schema_definition_count"], 13)
        self.assertEqual(self.verification["document_count"], 13)

    def test_complete_upstream_schema_inventory_is_exact(self):
        self.assertEqual(self.schemas["upstream_schema_count"], 84)
        self.assertEqual(self.schemas["m29_schema_count"], 13)
        self.assertEqual(self.schemas["record_count"], 97)
        self.assertEqual(self.schemas["source_registry_count"], 12)

    def test_supported_schema_identifiers_and_paths_are_unique(self):
        identifiers = [record["schema_identifier"] for record in self.schemas["records"]]
        paths = [record["schema_path"] for record in self.schemas["records"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(len(paths), len(set(paths)))

    def test_upstream_schema_raw_digests_are_exact(self):
        for record in self.schemas["records"]:
            if record["origin"] != "upstream_publication":
                continue
            raw = (ROOT / record["schema_path"]).read_bytes()
            self.assertEqual(record["byte_length"], len(raw))
            self.assertEqual(record["raw_sha256"], m29.raw_digest(raw))

    def test_m29_schema_raw_digests_are_exact(self):
        for record in self.schemas["records"]:
            if record["origin"] != "m29_closure":
                continue
            raw = (ROOT / record["schema_path"]).read_bytes()
            self.assertEqual(record["byte_length"], len(raw))
            self.assertEqual(record["raw_sha256"], m29.raw_digest(raw))

    def test_source_schema_registry_inventory_is_exact(self):
        self.assertEqual(
            [record["path"] for record in self.schemas["source_registries"]],
            m29.source_schema_registry_paths(ROOT),
        )
        for record in self.schemas["source_registries"]:
            raw = (ROOT / record["path"]).read_bytes()
            self.assertEqual(record["raw_sha256"], m29.raw_digest(raw))

    def test_complete_upstream_artifact_inventory_is_exact(self):
        self.assertEqual(self.artifacts["record_count"], 97)
        self.assertEqual(self.artifacts["json_artifact_count"], 86)
        self.assertEqual(self.artifacts["byte_artifact_count"], 11)
        self.assertEqual(
            self.artifacts["identity_policy"]["validated_json_artifact_count"],
            86,
        )

    def test_artifact_milestone_counts_are_exact(self):
        self.assertEqual(
            self.artifacts["milestone_counts"],
            {
                "M18": 36,
                "M19": 10,
                "M20": 4,
                "M21": 4,
                "M22": 4,
                "M23": 5,
                "M24": 5,
                "M25": 6,
                "M26": 6,
                "M27": 7,
                "M28": 10,
            },
        )

    def test_artifact_identifiers_and_paths_are_unique(self):
        identifiers = [record["artifact_identifier"] for record in self.artifacts["records"]]
        paths = [record["artifact_path"] for record in self.artifacts["records"]]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(len(paths), len(set(paths)))

    def test_artifact_raw_digests_are_exact(self):
        for record in self.artifacts["records"]:
            raw = (ROOT / record["artifact_path"]).read_bytes()
            self.assertEqual(record["byte_length"], len(raw))
            self.assertEqual(record["raw_sha256"], m29.raw_digest(raw))

    def test_all_json_artifacts_have_exact_schema_validation(self):
        json_records = [
            record
            for record in self.artifacts["records"]
            if record["artifact_format"] == "json"
        ]
        self.assertEqual(len(json_records), 86)
        self.assertTrue(
            all(record["schema_validation_status"] == "PASS" for record in json_records)
        )
        self.assertTrue(all(record["schema_identifier"] for record in json_records))

    def test_non_json_artifacts_use_raw_digest_identity(self):
        records = [
            record
            for record in self.artifacts["records"]
            if record["artifact_format"] != "json"
        ]
        self.assertEqual(len(records), 11)
        self.assertTrue(all(record["schema_identifier"] is None for record in records))
        self.assertTrue(
            all(record["schema_validation_status"] == "NOT_APPLICABLE" for record in records)
        )

    def test_provenance_covers_every_upstream_publication_file(self):
        counts = self.provenance["inventory_counts"]
        self.assertEqual(counts["upstream_schema_definitions"], 84)
        self.assertEqual(counts["upstream_schema_registries"], 12)
        self.assertEqual(counts["upstream_artifacts"], 97)
        self.assertEqual(counts["complete_upstream_publication_files"], 193)

    def test_provenance_is_complete_and_non_mutating(self):
        coverage = self.provenance["coverage"]
        self.assertTrue(coverage["required_fields_present"])
        self.assertEqual(coverage["missing_schema_identifiers"], 0)
        self.assertEqual(coverage["missing_artifact_identifiers"], 0)
        self.assertEqual(coverage["missing_raw_digests"], 0)
        self.assertEqual(coverage["source_bytes_rewritten"], 0)
        self.assertEqual(coverage["measurement_contours_merged"], 0)

    def test_producer_command_registry_is_complete(self):
        self.assertEqual(self.producers["record_count"], 12)
        self.assertEqual(
            [record["producer_id"] for record in self.producers["records"]],
            [spec["producer_id"] for spec in m29.PRODUCER_SPECS],
        )
        self.assertTrue(
            all(record["downstream_execution"] == "forbidden" for record in self.producers["records"])
        )

    def test_producer_source_digests_are_exact(self):
        for record in self.producers["records"]:
            raw = (ROOT / record["producer_path"]).read_bytes()
            self.assertEqual(record["producer_bytes"], len(raw))
            self.assertEqual(record["producer_raw_sha256"], m29.raw_digest(raw))
            self.assertEqual(record["command_count"], len(record["commands"]))

    def test_contract_preserves_the_immutable_core(self):
        core = self.contract["immutable_core"]
        self.assertEqual(core["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(core["semantic_values"], [-1, 0, 1])
        self.assertEqual(core["active_neutral_state"], 0)
        self.assertEqual(core["opposite_transition_routes"], [[-1, 0, 1], [1, 0, -1]])
        self.assertEqual(core["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(core["service_scheduler_mode"], "free")
        self.assertEqual(core["actual_direct_events"], 0)

    def test_contract_preserves_existing_observatory_scaffold(self):
        boundary = self.contract["integration_boundary"]
        self.assertEqual(boundary["downstream_repository"], m29.OBSERVATORY_REPOSITORY)
        self.assertEqual(boundary["existing_scaffold_action"], "preserve_existing_scaffold")
        self.assertEqual(boundary["downstream_audited_commit"], m29.OBSERVATORY_AUDITED_COMMIT)
        self.assertEqual(boundary["downstream_modes"], list(m29.OBSERVATORY_MODES))
        self.assertFalse(boundary["downstream_files_modified_by_m29"])

    def test_contract_is_strictly_one_way(self):
        boundary = self.contract["integration_boundary"]
        self.assertEqual(
            boundary["direction"],
            "upstream_to_published_bytes_to_downstream",
        )
        self.assertEqual(boundary["downstream_writeback"], "forbidden")
        self.assertEqual(boundary["downstream_source_mutation"], "forbidden")
        self.assertEqual(boundary["downstream_semantic_reimplementation"], "forbidden")
        self.assertFalse(boundary["upstream_dependency_on_downstream_code"])

    def test_contract_lists_all_required_roadmap_deliverables(self):
        self.assertEqual(len(self.contract["required_deliverables"]), 11)
        self.assertEqual(
            [item["deliverable"] for item in self.contract["required_deliverables"]],
            [
                "supported_schema_registry",
                "supported_artifact_registry",
                "compatibility_version_declarations",
                "canonical_demo_artifact_package",
                "deterministic_package_manifest",
                "producer_command_registry",
                "immutable_source_artifact_policy",
                "provenance_completeness",
                "unsupported_version_behavior",
                "downstream_consumption_test_vectors",
                "release_independent_compatibility_records",
            ],
        )
        for item in self.contract["required_deliverables"]:
            self.assertTrue((ROOT / item["path"]).is_file(), item["path"])

    def test_immutable_policy_is_pre_parse_and_byte_exact(self):
        identity = self.policy["byte_identity"]
        self.assertEqual(identity["algorithm"], "sha256")
        self.assertEqual(identity["digest_scope"], "raw_source_bytes")
        self.assertTrue(identity["digest_before_parse"])
        self.assertEqual(identity["copy_mode"], "byte_exact")
        self.assertEqual(identity["source_mutation"], "forbidden")

    def test_immutable_policy_keeps_absence_distinct_from_zero(self):
        rules = self.policy["consumer_rules"]
        self.assertEqual(rules["absent_field_policy"], "remain_absent")
        self.assertFalse(rules["absent_is_zero"])
        self.assertEqual(rules["source_execution"], "forbidden")
        self.assertEqual(rules["producer_execution"], "forbidden")

    def test_compatibility_versions_are_exact_declarations(self):
        self.assertEqual(
            [item["schema_version"] for item in self.compatibility["declarations"]],
            [
                "1",
                "1.7.0",
                "2.0.0",
                "2.1.0",
                "2.2.0",
                "2.3.0",
                "2.4.0",
                "2.5.0",
                "2.6.0",
                "2.7.0",
                "2.8.0",
                "2.9.0",
                "3.0.0",
                "3.1.0",
            ],
        )
        self.assertTrue(
            all(
                item["compatibility_state"] == "supported_by_exact_identifier"
                for item in self.compatibility["declarations"]
            )
        )

    def test_unsupported_version_behavior_fails_closed(self):
        resolution = self.unsupported["resolution"]
        self.assertTrue(resolution["fail_closed"])
        self.assertEqual(resolution["key"], "exact_schema_identifier")
        self.assertEqual(resolution["aliases"], "forbidden")
        self.assertEqual(resolution["automatic_migration"], "forbidden")
        self.assertEqual(self.unsupported["case_count"], 6)

    def test_canonical_demo_package_uses_exact_source_bytes(self):
        m29.validate_demo_package(self.package, ROOT)
        self.assertEqual(self.package["member_count"], 4)
        for member in self.package["members"]:
            raw = base64.b64decode(member["payload_base64"], validate=True)
            self.assertEqual(raw, (ROOT / member["source_path"]).read_bytes())
            self.assertEqual(member["raw_sha256"], m29.raw_digest(raw))

    def test_canonical_demo_package_member_order_is_exact(self):
        self.assertEqual(
            [member["member_id"] for member in self.package["members"]],
            [spec["member_id"] for spec in m29.DEMO_MEMBER_SPECS],
        )

    def test_demo_package_only_routes_to_existing_modes(self):
        allowed = set(m29.OBSERVATORY_MODES)
        for member in self.package["members"]:
            self.assertTrue(set(member["observatory_modes"]) <= allowed)

    def test_package_manifest_matches_the_exact_package_bytes(self):
        raw = (ROOT / m29.DEMO_PACKAGE_ARTIFACT).read_bytes()
        self.assertEqual(self.manifest["package_path"], m29.DEMO_PACKAGE_ARTIFACT)
        self.assertEqual(self.manifest["package_bytes"], len(raw))
        self.assertEqual(self.manifest["package_raw_sha256"], m29.raw_digest(raw))
        self.assertEqual(self.manifest["member_count"], self.package["member_count"])

    def test_downstream_consumption_vectors_are_complete(self):
        self.assertEqual(self.vectors["vector_count"], 12)
        self.assertEqual(self.vectors["accepted_count"], 4)
        self.assertEqual(self.vectors["rejected_count"], 8)
        self.assertEqual(self.vectors["status"], "PASS")
        self.assertTrue(all(vector["status"] == "PASS" for vector in self.vectors["vectors"]))

    def test_release_independent_records_use_only_published_identity(self):
        contract = self.releases["compatibility_key_contract"]
        self.assertEqual(
            contract["included_fields"],
            ["member_id", "schema_identifier", "raw_sha256"],
        )
        self.assertIn("upstream_release_label", contract["excluded_fields"])
        self.assertIn("consumer_version", contract["excluded_fields"])
        self.assertEqual(self.releases["record_count"], 4)

    def test_release_independent_compatibility_keys_are_exact(self):
        members = {member["member_id"]: member for member in self.package["members"]}
        for record in self.releases["records"]:
            self.assertEqual(
                record["compatibility_key"],
                m29.compatibility_key(members[record["member_id"]]),
            )
            self.assertFalse(record["release_label_in_key"])
            self.assertFalse(record["consumer_version_in_key"])

    def test_qualification_has_only_passing_checks(self):
        self.assertEqual(self.qualification["status"], "PASS")
        self.assertEqual(self.qualification["check_count"], 48)
        self.assertEqual(self.qualification["passed_count"], 48)
        self.assertEqual(self.qualification["failed_count"], 0)
        self.assertTrue(
            all(check["status"] == "PASS" for check in self.qualification["checks"])
        )

    def test_qualification_covers_every_m29_schema_and_primary_document(self):
        self.assertEqual(self.qualification["schema_count"], 13)
        self.assertEqual(self.qualification["document_count"], 12)
        for record in self.qualification["schemas"] + self.qualification["documents"]:
            raw = (ROOT / record["path"]).read_bytes()
            self.assertEqual(record["byte_length"], len(raw))
            self.assertEqual(record["raw_sha256"], m29.raw_digest(raw))

    def test_all_generated_documents_end_with_one_newline(self):
        for relative in m29.GENERATED_PATHS:
            raw = (ROOT / relative).read_bytes()
            self.assertTrue(raw.endswith(b"\n"), relative)
            self.assertFalse(raw.endswith(b"\n\n"), relative)

    def test_no_forbidden_positive_sign_notation(self):
        forbidden = "-1/0/" + "+1"
        paths = [
            ROOT / "frp_m29_system_integration_downstream_compatibility.py",
            ROOT / "tests/test_frp_m29_system_integration_downstream_compatibility.py",
        ]
        paths.extend(ROOT / relative for relative in m29.GENERATED_PATHS)
        for path in paths:
            self.assertNotIn(forbidden, path.read_text(encoding="utf-8"), str(path))


class M29NegativeValidationTests(unittest.TestCase):
    def setUp(self):
        self.contract = load(m29.CONTRACT_ARTIFACT)
        self.package = load(m29.DEMO_PACKAGE_ARTIFACT)
        self.schema_registry = load(m29.SCHEMA_REGISTRY)

    def test_contract_rejects_ternary_notation_change(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["balanced_ternary_notation"] = "ternary"
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_contract_rejects_active_neutral_change(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["active_neutral_state"] = 1
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_contract_rejects_scheduler_change(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["temporal_scheduler_modes"] = ["7/1"]
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_contract_rejects_observatory_writeback(self):
        value = copy.deepcopy(self.contract)
        value["integration_boundary"]["downstream_writeback"] = "allowed"
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_contract_rejects_downstream_semantic_reimplementation(self):
        value = copy.deepcopy(self.contract)
        value["integration_boundary"]["downstream_semantic_reimplementation"] = "allowed"
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_contract_rejects_upstream_dependency_on_observatory(self):
        value = copy.deepcopy(self.contract)
        value["integration_boundary"]["upstream_dependency_on_downstream_code"] = True
        with self.assertRaises(m29.ContractError):
            m29._validate_contract(refresh(value, "contract_digest"))

    def test_demo_package_rejects_invalid_base64(self):
        value = copy.deepcopy(self.package)
        value["members"][0]["payload_base64"] = value["members"][0]["payload_base64"][:-1]
        with self.assertRaises(m29.ContractError):
            m29.validate_demo_package(refresh(value, "package_digest"), ROOT)

    def test_demo_package_rejects_source_byte_mutation(self):
        value = copy.deepcopy(self.package)
        raw = base64.b64decode(value["members"][0]["payload_base64"]) + b"\n"
        value["members"][0]["payload_base64"] = base64.b64encode(raw).decode("ascii")
        value["members"][0]["byte_length"] = len(raw)
        value["members"][0]["raw_sha256"] = m29.raw_digest(raw)
        with self.assertRaises(m29.ContractError):
            m29.validate_demo_package(refresh(value, "package_digest"), ROOT)

    def test_demo_package_rejects_schema_identifier_change(self):
        value = copy.deepcopy(self.package)
        value["members"][0]["schema_identifier"] = "frp.unknown.schema.v9.0.0"
        with self.assertRaises(m29.ContractError):
            m29.validate_demo_package(refresh(value, "package_digest"), ROOT)

    def test_vector_consumer_rejects_unknown_artifact(self):
        members = {member["member_id"]: member for member in self.package["members"]}
        supported = {
            record["schema_identifier"] for record in self.schema_registry["records"]
        }
        outcome = m29._evaluate_vector(
            {
                "member_id": "unknown",
                "schema_identifier": self.package["members"][0]["schema_identifier"],
                "raw_sha256": self.package["members"][0]["raw_sha256"],
            },
            members,
            supported,
        )
        self.assertEqual(outcome, ("rejected", "UNKNOWN_ARTIFACT_IDENTIFIER"))

    def test_vector_consumer_rejects_unknown_schema(self):
        member = self.package["members"][0]
        members = {item["member_id"]: item for item in self.package["members"]}
        supported = {
            record["schema_identifier"] for record in self.schema_registry["records"]
        }
        outcome = m29._evaluate_vector(
            {
                "member_id": member["member_id"],
                "schema_identifier": "frp.unknown.schema.v9.0.0",
                "raw_sha256": member["raw_sha256"],
            },
            members,
            supported,
        )
        self.assertEqual(outcome, ("rejected", "UNSUPPORTED_SCHEMA_IDENTIFIER"))

    def test_vector_consumer_rejects_digest_mismatch(self):
        member = self.package["members"][0]
        members = {item["member_id"]: item for item in self.package["members"]}
        supported = {
            record["schema_identifier"] for record in self.schema_registry["records"]
        }
        outcome = m29._evaluate_vector(
            {
                "member_id": member["member_id"],
                "schema_identifier": member["schema_identifier"],
                "raw_sha256": "0" * 64,
            },
            members,
            supported,
        )
        self.assertEqual(outcome, ("rejected", "SOURCE_DIGEST_MISMATCH"))


if __name__ == "__main__":
    unittest.main()
