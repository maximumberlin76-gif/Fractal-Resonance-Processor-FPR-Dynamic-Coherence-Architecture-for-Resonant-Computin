"""Tests for FRP M21 deterministic parameterized qualification matrix."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

import frp_m21_parameterized_qualification_matrix as M21


ROOT = Path(__file__).resolve().parents[1]


class M21ParameterizedMatrixTests(unittest.TestCase):
    """Exercise dimensions, complete coverage, contours, and failures."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.context = M21.build_context(ROOT, M21.EXPECTED_M20_COMMIT)
        cls.schemas = M21.SchemaContext(ROOT)
        cls.dimensions = M21.build_dimensions(cls.context)
        cls.matrix = M21.build_matrix(cls.context, cls.dimensions)
        cls.supported = [
            case
            for case in cls.matrix["cases"]
            if case["qualification_status"] == "PASS"
        ]
        cls.skipped = [
            case
            for case in cls.matrix["cases"]
            if case["qualification_status"] == "SKIPPED"
        ]

    def test_exact_source_commit_and_upstream_boundaries(self) -> None:
        self.assertEqual(self.context.source_commit, M21.EXPECTED_M20_COMMIT)
        self.assertEqual(self.context.m20_boundary["qualification_check_count"], 39)
        self.assertEqual(
            self.context.m20_boundary["rtl_record_counts"],
            {"free": 16, "7/1": 64, "1/7": 16},
        )
        self.assertEqual(
            self.context.m20_boundary["fpga_record_counts"],
            {"free": 3, "7/1": 0, "1/7": 1},
        )

    def test_workload_catalog_is_exact_ordered_and_qualified(self) -> None:
        self.assertEqual(
            [item["workload_id"] for item in self.context.workloads],
            [
                "scaling-16",
                "scaling-32",
                "scaling-8",
                "trace-1-7",
                "trace-7-1",
                "trace-free",
            ],
        )
        self.assertTrue(
            all(item["qualification_status"] == "PASS" for item in self.context.workloads)
        )
        for item in self.context.workloads:
            self.assertEqual(
                item["raw_sha256"],
                M21.sha256_bytes((ROOT / item["path"]).read_bytes()),
            )

    def test_dimension_order_cardinalities_and_cartesian_count_are_exact(self) -> None:
        self.assertEqual(self.dimensions["dimension_order"], list(M21.DIMENSION_ORDER))
        self.assertEqual(
            self.dimensions["dimension_cardinalities"],
            {
                "cell_count": 3,
                "request_lanes": 3,
                "scheduler_mode": 3,
                "scheduler_parameter_profile": 3,
                "transition_capacity_profile": 3,
                "retained_route_profile": 2,
            },
        )
        self.assertEqual(self.dimensions["declared_cartesian_case_count"], 486)

    def test_declared_scalar_dimensions_are_exact(self) -> None:
        values = self.dimensions["dimensions"]
        self.assertEqual(values["cell_count"], [8, 16, 32])
        self.assertEqual(values["request_lanes"], [2, 4, 8])
        self.assertEqual(values["scheduler_mode"], ["free", "7/1", "1/7"])

    def test_scheduler_parameter_profiles_are_exact(self) -> None:
        self.assertEqual(
            self.dimensions["dimensions"]["scheduler_parameter_profile"],
            list(M21.SCHEDULER_PROFILES),
        )
        profiles = {
            item["scheduler_mode"]: item["state_pattern"]
            for item in M21.SCHEDULER_PROFILES
        }
        self.assertEqual(profiles["free"], ["free"] * 8)
        self.assertEqual(profiles["7/1"], ["balance"] * 7 + ["commit"])
        self.assertEqual(profiles["1/7"], ["excite"] + ["neutralize"] * 7)

    def test_transition_capacity_profiles_are_exact(self) -> None:
        profiles = self.dimensions["dimensions"]["transition_capacity_profile"]
        self.assertEqual(profiles, list(M21.TRANSITION_CAPACITY_PROFILES))
        for profile in profiles:
            self.assertEqual(profile["fraction_numerator"], 1)
            self.assertEqual(profile["fraction_denominator"], 4)
            self.assertEqual(profile["capacity_limit"], profile["cell_count"] // 4)

    def test_retained_route_profiles_preserve_active_zero_boundary(self) -> None:
        canonical, forbidden = self.dimensions["dimensions"]["retained_route_profile"]
        self.assertTrue(canonical["supported"])
        self.assertTrue(canonical["pending_route_retention"])
        self.assertEqual(canonical["active_neutral_state"], 0)
        self.assertEqual(canonical["canonical_ternary_states"], [-1, 0, 1])
        self.assertEqual(
            canonical["neutral_routes"],
            ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
        )
        self.assertFalse(forbidden["supported"])
        self.assertFalse(forbidden["pending_route_retention"])
        self.assertEqual(forbidden["neutral_routes"], ["-1 -> 1", "1 -> -1"])

    def test_matrix_has_complete_unique_ordered_coverage(self) -> None:
        cases = self.matrix["cases"]
        self.assertEqual(len(cases), 486)
        self.assertEqual([case["sequence"] for case in cases], list(range(486)))
        self.assertEqual(
            [case["case_id"] for case in cases],
            [f"m21-case-{index:06d}" for index in range(486)],
        )
        self.assertEqual(
            len({M21.object_digest(case["coordinates"]) for case in cases}),
            486,
        )

    def test_supported_and_skipped_counts_are_exact(self) -> None:
        self.assertEqual(len(self.supported), 5)
        self.assertEqual(len(self.skipped), 481)
        self.assertEqual(self.matrix["summary"]["supported_case_count"], 5)
        self.assertEqual(self.matrix["summary"]["skipped_case_count"], 481)
        self.assertEqual(self.matrix["summary"]["failed_case_count"], 0)
        self.assertEqual(self.matrix["summary"]["overall_status"], "PASS")

    def test_skip_reason_counts_are_complete_and_exact(self) -> None:
        self.assertEqual(
            self.matrix["summary"]["skip_reason_counts"],
            M21.SKIP_REASON_COUNTS,
        )
        self.assertEqual(
            sum(M21.SKIP_REASON_COUNTS.values()),
            len(self.skipped),
        )
        self.assertTrue(
            all(case["support"]["reason_detail"] for case in self.skipped)
        )

    def test_supported_coordinates_and_workloads_are_exact(self) -> None:
        actual = {
            (
                case["coordinates"]["cell_count"],
                case["coordinates"]["request_lanes"],
                case["coordinates"]["scheduler_mode"],
            ): [item["workload_id"] for item in case["workloads"]]
            for case in self.supported
        }
        self.assertEqual(
            actual,
            {
                (8, 2, "7/1"): ["scaling-8"],
                (16, 4, "free"): ["trace-free"],
                (16, 4, "7/1"): ["scaling-16", "trace-7-1"],
                (16, 4, "1/7"): ["trace-1-7"],
                (32, 8, "7/1"): ["scaling-32"],
            },
        )

    def test_supported_cases_preserve_exact_parameters_and_invariants(self) -> None:
        for case in self.supported:
            coordinates = case["coordinates"]
            resolved = case["resolved_parameters"]
            self.assertEqual(resolved["canonical_ternary_states"], [-1, 0, 1])
            self.assertEqual(resolved["active_neutral_state"], 0)
            self.assertEqual(
                resolved["neutral_routes"],
                ["-1 -> 0 -> 1", "1 -> 0 -> -1"],
            )
            self.assertEqual(
                resolved["transition_capacity_limit"],
                coordinates["request_lanes"],
            )
            self.assertEqual(
                resolved["pending_route_queue_capacity"],
                coordinates["cell_count"],
            )
            self.assertEqual(resolved["transition_fraction"], {"numerator": 1, "denominator": 4})

    def test_case_checks_are_exact_and_never_fail(self) -> None:
        for case in self.matrix["cases"]:
            self.assertEqual(
                tuple(item["check_id"] for item in case["checks"]),
                M21.CHECK_IDS,
            )
            self.assertNotIn("FAIL", {item["status"] for item in case["checks"]})
            self.assertEqual(case["checks"][-2]["status"], "PASS")
            self.assertEqual(case["checks"][-1]["status"], "PASS")

    def test_measurement_contours_are_separate_in_every_case(self) -> None:
        expected = [
            "rtl_static_parameter_contract",
            "m15_quantized_semantic_reference",
            "m20_cross_layer_correlation",
        ]
        for case in self.matrix["cases"]:
            evidence = case["contour_evidence"]
            self.assertEqual([item["contour"] for item in evidence], expected)
            for item in evidence:
                self.assertEqual(
                    item["evidence_digest"],
                    M21.object_digest(
                        {
                            key: value
                            for key, value in item.items()
                            if key != "evidence_digest"
                        }
                    ),
                )

    def test_cross_layer_contour_is_pass_only_for_supported_16_cell_cases(self) -> None:
        for case in self.supported:
            evidence = case["contour_evidence"][2]
            expected = (
                "PASS"
                if case["coordinates"]["cell_count"] == 16
                else "NOT_APPLICABLE"
            )
            self.assertEqual(evidence["status"], expected)
        self.assertTrue(
            all(
                case["contour_evidence"][2]["status"] == "NOT_APPLICABLE"
                for case in self.skipped
            )
        )

    def test_provenance_is_per_case_and_digest_bound(self) -> None:
        for case in self.matrix["cases"]:
            self.assertGreaterEqual(len(case["provenance"]), 1)
            for item in case["provenance"]:
                self.assertEqual(
                    item["raw_sha256"],
                    M21.sha256_bytes((ROOT / item["path"]).read_bytes()),
                )

    def test_case_and_matrix_digests_are_exact(self) -> None:
        for case in self.matrix["cases"]:
            self.assertEqual(
                case["case_digest"],
                M21.object_digest(
                    {
                        key: value
                        for key, value in case.items()
                        if key != "case_digest"
                    }
                ),
            )
        self.assertEqual(
            self.matrix["matrix_digest"],
            M21.object_digest(self.matrix["cases"]),
        )
        self.assertEqual(
            self.dimensions["dimensions_digest"],
            M21.object_digest(
                {
                    key: value
                    for key, value in self.dimensions.items()
                    if key != "dimensions_digest"
                }
            ),
        )

    def test_dimensions_and_matrix_validate_against_formal_schemas(self) -> None:
        self.schemas.validate(M21.DIMENSIONS_SCHEMA, self.dimensions, "dimensions")
        self.schemas.validate(M21.MATRIX_SCHEMA, self.matrix, "matrix")

    def test_generation_is_byte_stable(self) -> None:
        second_dimensions = M21.build_dimensions(self.context)
        second_matrix = M21.build_matrix(self.context, second_dimensions)
        self.assertEqual(
            M21.canonical_json_bytes(self.dimensions),
            M21.canonical_json_bytes(second_dimensions),
        )
        self.assertEqual(
            M21.canonical_json_bytes(self.matrix),
            M21.canonical_json_bytes(second_matrix),
        )

    def test_deliberate_case_digest_change_is_detected(self) -> None:
        self.assertTrue(
            M21.altered_case_digest_probe(
                self.context,
                self.dimensions,
                self.matrix,
            )
        )

    def test_deliberate_parameter_change_is_detected(self) -> None:
        self.assertTrue(
            M21.altered_parameter_probe(
                self.context,
                self.dimensions,
                self.matrix,
            )
        )

    def test_deliberate_workload_digest_change_is_detected(self) -> None:
        self.assertTrue(
            M21.altered_workload_digest_probe(
                self.context,
                self.dimensions,
                self.matrix,
            )
        )

    def test_deliberate_contour_substitution_is_detected(self) -> None:
        self.assertTrue(
            M21.contour_substitution_probe(
                self.context,
                self.dimensions,
                self.matrix,
            )
        )

    def test_schema_rejects_reserved_ternary_state(self) -> None:
        altered = copy.deepcopy(self.supported[0])
        altered["resolved_parameters"]["canonical_ternary_states"] = [-1, 2, 1]
        with self.assertRaises(M21.ContractError):
            self.schemas.validate(M21.CASE_SCHEMA, altered, "reserved-state")

    def test_schema_rejects_missing_required_field(self) -> None:
        altered = copy.deepcopy(self.supported[0])
        del altered["provenance"]
        with self.assertRaises(M21.ContractError):
            self.schemas.validate(M21.CASE_SCHEMA, altered, "missing-field")

    def test_schema_rejects_additional_field(self) -> None:
        altered = copy.deepcopy(self.supported[0])
        altered["unregistered"] = True
        with self.assertRaises(M21.ContractError):
            self.schemas.validate(M21.CASE_SCHEMA, altered, "additional-field")

    def test_wrong_source_commit_is_rejected(self) -> None:
        with self.assertRaises(M21.ContractError):
            M21.build_context(ROOT, "0" * 40)

    def test_unsafe_relative_paths_are_rejected(self) -> None:
        for value in ("../escape.json", "/absolute.json", "a/./b.json", "a\\b"):
            with self.subTest(value=value):
                with self.assertRaises(M21.SafetyError):
                    M21.safe_relative_path(value)


class M21CommittedOutputTests(unittest.TestCase):
    """Exercise the complete generated and committed M21 package."""

    @classmethod
    def setUpClass(cls) -> None:
        if not all((ROOT / path).is_file() for path in M21.GENERATED_PATHS):
            raise unittest.SkipTest("committed M21 outputs not installed yet")
        cls.outputs = M21.build_outputs(ROOT, M21.EXPECTED_M20_COMMIT)

    def test_committed_outputs_are_byte_identical(self) -> None:
        for relative, expected in self.outputs.items():
            with self.subTest(path=relative):
                self.assertEqual((ROOT / relative).read_bytes(), expected)

    def test_complete_verification_passes(self) -> None:
        result = M21.verify(ROOT, M21.EXPECTED_M20_COMMIT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["artifact_count"], 4)
        self.assertTrue(all(item["match"] for item in result["artifacts"]))

    def test_qualification_record_is_complete(self) -> None:
        qualification = M21.read_json(ROOT, M21.QUALIFICATION_ARTIFACT)
        self.assertEqual(qualification["overall_status"], "PASS")
        self.assertEqual(qualification["failed_count"], 0)
        self.assertEqual(
            qualification["passed_count"],
            qualification["check_count"],
        )


if __name__ == "__main__":
    unittest.main()
