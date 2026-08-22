from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import frp_m28_hierarchical_scaling_hotspot_containment as m28h


ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class M28HierarchyConstantTests(unittest.TestCase):
    def test_version_and_milestone_are_exact(self):
        self.assertEqual(m28h.VERSION, "3.0.0")
        self.assertEqual(m28h.MILESTONE, "M28")

    def test_title_is_canonical(self):
        self.assertEqual(
            m28h.MILESTONE_TITLE,
            "M28 - Hierarchical Scaling and Hotspot-Containment Realization",
        )

    def test_source_commit_is_exact_m27_closure(self):
        self.assertEqual(
            m28h.EXPECTED_M27_COMMIT,
            "23e464206f85cd9473101d9221027ee33d9dd094",
        )

    def test_observatory_interchange_is_preserved_as_supplement(self):
        self.assertEqual(
            m28h.M28_OBSERVATORY_COMMIT,
            "566a4ff88baa57f844691b46937552253e095434",
        )

    def test_workflow_filename_declares_workflow(self):
        path = Path(m28h.WORKFLOW_PATH)
        self.assertIn("workflow", path.name)
        self.assertTrue(m28h.WORKFLOW_PATH.startswith(".github/workflows/"))

    def test_scheduler_classes_are_separate(self):
        self.assertEqual(m28h.TEMPORAL_SCHEDULERS, ("1/7", "7/1"))
        self.assertEqual(m28h.SERVICE_SCHEDULER, "free")


class M28HierarchyPathSafetyTests(unittest.TestCase):
    def test_safe_path_is_preserved(self):
        self.assertEqual(
            m28h.safe_relative_path("artifacts/m28/hierarchy/example.json").as_posix(),
            "artifacts/m28/hierarchy/example.json",
        )

    def test_unsafe_paths_are_rejected(self):
        for value in ("", "/absolute", "../escape", "a/../b", "a//b", "a\\b"):
            with self.subTest(value=value), self.assertRaises(m28h.SafetyError):
                m28h.safe_relative_path(value)

    def test_wrong_source_commit_is_rejected(self):
        with self.assertRaises(m28h.ContractError):
            m28h.validate_source_commit("0" * 40)


class M28HierarchyGeneratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verification = m28h.verify(ROOT, m28h.EXPECTED_M27_COMMIT)
        cls.contract = load(m28h.CONTRACT_ARTIFACT)
        cls.topology = load(m28h.TOPOLOGY_ARTIFACT)
        cls.scaling = load(m28h.SCALING_ARTIFACT)
        cls.hotspot = load(m28h.HOTSPOT_ARTIFACT)
        cls.qualification = load(m28h.QUALIFICATION_ARTIFACT)
        cls.registry = load(m28h.SCHEMA_REGISTRY_PATH)

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
        self.assertEqual(core["service_scheduler_mode"], "free")

    def test_contract_scope_is_complete_and_ordered(self):
        self.assertEqual(self.contract["required_scope"], list(m28h.REQUIRED_SCOPE))
        self.assertEqual(len(self.contract["required_scope"]), 11)

    def test_observatory_interchange_is_not_deleted_or_redefined(self):
        provenance = self.contract["provenance_boundary"]
        self.assertEqual(
            provenance["observatory_interchange_role"],
            "additional_publication_layer",
        )
        self.assertEqual(provenance["hierarchy_role"], "primary_M28_realization")

    def test_aggregation_equations_are_explicit(self):
        equations = self.contract["aggregation_equations"]
        self.assertTrue(equations["no_undeclared_metric_aggregation"])
        self.assertIn("sum", equations["cluster_heat_mean"])
        self.assertIn("max", equations["cluster_heat_peak"])

    def test_measurement_contours_remain_separate(self):
        boundary = self.contract["measurement_boundary"]
        self.assertTrue(boundary["measurement_contours_remain_separate"])
        self.assertEqual(
            boundary["cluster_telemetry"],
            "model_derived_dimensionless_proxy",
        )

    def test_topology_has_exact_profiles(self):
        self.assertEqual(self.topology["profile_count"], 3)
        self.assertEqual(
            [item["cells"] for item in self.topology["profiles"]],
            [8, 16, 32],
        )
        self.assertEqual(
            [item["hierarchy_depth"] for item in self.topology["profiles"]],
            [3, 4, 5],
        )

    def test_cluster_identities_are_complete_and_nonoverlapping(self):
        for profile in self.topology["profiles"]:
            observed = [
                cell_id
                for cluster in profile["clusters"]
                for cell_id in cluster["cell_ids"]
            ]
            self.assertEqual(observed, list(range(profile["cells"])))
            self.assertEqual(len(set(observed)), profile["cells"])

    def test_cell_to_cluster_mapping_is_exact(self):
        for profile in self.topology["profiles"]:
            for record in profile["cell_to_cluster"]:
                self.assertEqual(
                    record["cluster_index"],
                    record["cell_id"] // m28h.CLUSTER_SIZE,
                )
                self.assertEqual(
                    record["cluster_offset"],
                    record["cell_id"] % m28h.CLUSTER_SIZE,
                )

    def test_dyadic_levels_end_in_global_domain(self):
        for profile in self.topology["profiles"]:
            self.assertEqual(profile["levels"][0]["role"], "individual_cell")
            self.assertEqual(profile["levels"][1]["role"], "pair_domain")
            self.assertEqual(profile["levels"][2]["role"], "local_cluster")
            self.assertEqual(profile["levels"][-1]["role"], "global_cell_domain")
            self.assertEqual(profile["levels"][-1]["domain_count"], 1)

    def test_topology_metrics_pass(self):
        for profile in self.topology["profiles"]:
            for name in ("coupling_topology_metrics", "thermal_topology_metrics"):
                metrics = profile[name]
                self.assertTrue(metrics["row_sum_match"])
                self.assertTrue(metrics["symmetry_match"])
                self.assertTrue(metrics["diagonal_zero"])
            self.assertEqual(profile["fixed_point_validation"]["status"], "PASS")

    def test_source_provenance_uses_raw_bytes(self):
        for record in self.topology["source_records"]:
            path = ROOT / record["path"]
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(m28h.raw_sha256(path), record["raw_sha256"])

    def test_scaling_matrix_has_six_profiles(self):
        self.assertEqual(self.scaling["profile_count"], 6)
        self.assertEqual(
            [(item["cells"], item["scheduler"]) for item in self.scaling["cell_profiles"]],
            [
                (8, "1/7"),
                (8, "7/1"),
                (16, "1/7"),
                (16, "7/1"),
                (32, "1/7"),
                (32, "7/1"),
            ],
        )

    def test_scaling_profiles_pass_every_check(self):
        for profile in self.scaling["cell_profiles"]:
            self.assertEqual(profile["status"], "PASS")
            self.assertTrue(all(profile["checks"].values()))
            self.assertEqual(profile["checkpoint_count"], 8)

    def test_cluster_counts_reconstruct_global_cell_count(self):
        for profile in self.scaling["cell_profiles"]:
            for observation in profile["observations"]:
                self.assertEqual(
                    sum(observation["cluster_state_count_sums"].values()),
                    profile["cells"],
                )

    def test_scaling_profiles_preserve_zero_safety_counters(self):
        for profile in self.scaling["cell_profiles"]:
            self.assertEqual(profile["fixed_point_validation_scheduler"], "7/1")
            summary = profile["fixed_point_profile"]["summary"]
            self.assertEqual(summary["scheduler"], "7/1")
            self.assertEqual(summary["actual_direct_events"], 0)
            self.assertEqual(summary["reserved_state_events"], 0)
            self.assertEqual(summary["queue_overflow_events"], 0)

    def test_hotspot_evidence_covers_service_and_temporal_modes(self):
        self.assertEqual(self.hotspot["profile_count"], 3)
        self.assertEqual(
            [item["scheduler"] for item in self.hotspot["profiles"]],
            ["free", "1/7", "7/1"],
        )
        self.assertEqual(
            [item["scheduler_class"] for item in self.hotspot["profiles"]],
            ["service", "temporal", "temporal"],
        )

    def test_hotspot_profiles_pass_all_checks(self):
        for profile in self.hotspot["profiles"]:
            self.assertEqual(profile["status"], "PASS")
            self.assertTrue(all(profile["checks"].values()))
            self.assertTrue(
                profile["containment_markers"]["localized_hotspot_containment_pass"]
            )
            self.assertTrue(profile["recovery"]["completed"])

    def test_hotspot_ratios_are_below_declared_limits(self):
        for profile in self.hotspot["profiles"]:
            markers = profile["containment_markers"]
            ratio = markers["cross_cluster_thermal_propagation_ratio_q30"] / (1 << 30)
            remote = markers["remote_thermal_propagation_ratio_q30"] / (1 << 30)
            self.assertLess(ratio, m28h.HOTSPOT_PROPAGATION_LIMIT)
            self.assertLess(remote, m28h.HOTSPOT_REMOTE_PROPAGATION_LIMIT)

    def test_qualification_is_closed(self):
        self.assertEqual(self.qualification["status"], "PASS")
        self.assertEqual(self.qualification["failed_count"], 0)
        self.assertEqual(
            self.qualification["check_count"],
            self.qualification["passed_count"],
        )
        self.assertTrue(
            all(item["status"] == "PASS" for item in self.qualification["checks"])
        )

    def test_schema_registry_has_exact_identifiers(self):
        self.assertEqual(self.registry["record_count"], 5)
        self.assertEqual(
            [item["identifier"] for item in self.registry["records"]],
            list(m28h.SCHEMA_PATHS),
        )

    def test_all_generated_documents_end_with_one_newline(self):
        for relative in m28h.GENERATED_PATHS:
            raw = (ROOT / relative).read_bytes()
            self.assertTrue(raw.endswith(b"\n"), relative)
            self.assertFalse(raw.endswith(b"\n\n"), relative)

    def test_no_forbidden_positive_sign_notation(self):
        forbidden = "-1/0/" + "+1"
        paths = [
            ROOT / "frp_m28_hierarchical_scaling_hotspot_containment.py",
            ROOT / "tests/test_frp_m28_hierarchical_scaling_hotspot_containment.py",
        ]
        paths.extend(ROOT / relative for relative in m28h.GENERATED_PATHS)
        for path in paths:
            self.assertNotIn(forbidden, path.read_text(encoding="utf-8"), str(path))


class M28HierarchyNegativeTests(unittest.TestCase):
    def setUp(self):
        self.contract = load(m28h.CONTRACT_ARTIFACT)
        self.topology = load(m28h.TOPOLOGY_ARTIFACT)
        self.scaling = load(m28h.SCALING_ARTIFACT)
        self.hotspot = load(m28h.HOTSPOT_ARTIFACT)

    def test_ternary_notation_change_is_rejected(self):
        value = copy.deepcopy(self.contract)
        value["immutable_core"]["balanced_ternary_notation"] = "ternary"
        with self.assertRaises(m28h.ContractError):
            m28h.validate_contract(m28h.attach_digest(value, "contract_digest"))

    def test_cluster_overlap_is_rejected(self):
        value = copy.deepcopy(self.topology)
        value["profiles"][0]["clusters"][0]["cell_ids"][0] = 7
        value["topology_set_digest"] = m28h.object_digest(value["profiles"])
        with self.assertRaises(m28h.ContractError):
            m28h.validate_topology(m28h.attach_digest(value, "manifest_digest"), ROOT)

    def test_scaling_check_failure_is_rejected(self):
        value = copy.deepcopy(self.scaling)
        value["cell_profiles"][0]["checks"]["actual_direct_events_zero"] = False
        value["profile_set_digest"] = m28h.object_digest(value["cell_profiles"])
        with self.assertRaises(m28h.ContractError):
            m28h.validate_scaling(m28h.attach_digest(value, "matrix_digest"))

    def test_hotspot_failure_is_rejected(self):
        value = copy.deepcopy(self.hotspot)
        value["profiles"][0]["checks"][
            "cross_cluster_thermal_propagation_bounded"
        ] = False
        value["profile_set_digest"] = m28h.object_digest(value["profiles"])
        with self.assertRaises(m28h.ContractError):
            m28h.validate_hotspot(m28h.attach_digest(value, "evidence_digest"))


class M28HierarchyDeterminismTests(unittest.TestCase):
    def test_two_complete_generations_are_byte_identical(self):
        with tempfile.TemporaryDirectory(prefix="m28-hierarchy-a-") as first_dir:
            with tempfile.TemporaryDirectory(prefix="m28-hierarchy-b-") as second_dir:
                first = Path(first_dir)
                second = Path(second_dir)
                m28h.generate(ROOT, first, m28h.EXPECTED_M27_COMMIT)
                m28h.generate(ROOT, second, m28h.EXPECTED_M27_COMMIT)
                for relative in m28h.GENERATED_PATHS:
                    self.assertEqual(
                        (first / relative).read_bytes(),
                        (second / relative).read_bytes(),
                        relative,
                    )

    def test_self_test_passes_all_negative_controls(self):
        result = m28h.self_test(ROOT, m28h.EXPECTED_M27_COMMIT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["check_count"], 7)
        self.assertTrue(all(item["status"] == "PASS" for item in result["checks"]))


if __name__ == "__main__":
    unittest.main()
