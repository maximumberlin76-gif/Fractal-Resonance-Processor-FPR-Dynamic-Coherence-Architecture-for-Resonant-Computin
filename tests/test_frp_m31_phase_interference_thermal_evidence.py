"""Qualification tests for FRP M31 phase-interference thermal evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import shutil
import tempfile
import unittest
from pathlib import Path

import jsonschema

import frp_m31_phase_interference_thermal_evidence as m31


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "frp_m31_phase_interference_thermal_evidence.py"
SOURCE_BYTES = 42092
SOURCE_SHA256 = (
    "1e4ccfd7b157cd2bac609c34dfec9da791653a31af7b29b75502c755807b9c62"
)
EXPECTED_OUTPUTS = {
    m31.SCHEMA_PATH: (
        1468,
        "53d79d45d70753ccd24c3dc4c97af6fee481f86a9d7cdca7ef78b486c76479f7",
    ),
    m31.EVIDENCE_PATH: (
        39993,
        "bdaa676acbfb09d86d848070e8a2673c5ce6902657a0b13b2e4293383bec8b42",
    ),
    m31.MANIFEST_PATH: (
        828,
        "80f0841d0041cd22c2f76175b6139e601aede7b69823356ae1fefbce5f793e7c",
    ),
    m31.QUALIFICATION_PATH: (
        1512,
        "4c2446f954e01ec0aa37cc6c0fc70cf4a87ec565c450628e31b0efcac9160224",
    ),
}


class M31PhaseInterferenceThermalEvidenceTests(unittest.TestCase):
    """Exercise exact evidence, output, safety, and downstream boundaries."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory()
        cls.output_root = Path(cls._temporary.name)
        cls.generation = m31.generate(ROOT, cls.output_root)
        cls.evidence = json.loads(
            (cls.output_root / m31.EVIDENCE_PATH).read_text(encoding="utf-8")
        )
        cls.schema = json.loads(
            (cls.output_root / m31.SCHEMA_PATH).read_text(encoding="utf-8")
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def fresh_evidence(self) -> dict:
        return copy.deepcopy(self.evidence)

    def test_01_producer_source_identity_is_exact(self) -> None:
        raw = SOURCE_PATH.read_bytes()
        self.assertEqual(len(raw), SOURCE_BYTES)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_SHA256)

    def test_02_published_constants_are_exact(self) -> None:
        self.assertEqual(m31.MILESTONE, "M31")
        self.assertEqual(
            m31.SCHEMA_ID,
            "frp.m31.phase_interference_active_zero_thermal_evidence.v1",
        )
        self.assertEqual(
            m31.ARCHIVE_SHA256,
            "05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa",
        )

    def test_03_canonical_json_is_sorted_and_newline_terminated(self) -> None:
        raw = m31.canonical_json_bytes({"z": 1, "a": [-1, 0, 1]})
        self.assertTrue(raw.endswith(b"\n"))
        self.assertLess(raw.index(b'"a"'), raw.index(b'"z"'))
        self.assertEqual(raw, m31.canonical_json_bytes({"a": [-1, 0, 1], "z": 1}))

    def test_04_canonical_json_rejects_nonfinite_values(self) -> None:
        with self.assertRaises(ValueError):
            m31.canonical_json_bytes({"invalid": math.nan})

    def test_05_schema_identity_is_exact(self) -> None:
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertTrue(self.schema["$id"].endswith(".v1.schema.json"))
        self.assertEqual(self.schema["additionalProperties"], False)

    def test_06_schema_required_fields_match_evidence(self) -> None:
        self.assertEqual(set(self.schema["required"]), set(self.evidence))

    def test_07_schema_is_valid_and_accepts_published_evidence(self) -> None:
        jsonschema.Draft202012Validator.check_schema(self.schema)
        jsonschema.Draft202012Validator(self.schema).validate(self.evidence)

    def test_08_evidence_identity_and_status_are_exact(self) -> None:
        self.assertEqual(self.evidence["schema"], m31.SCHEMA_ID)
        self.assertEqual(self.evidence["version"], "1.0.0")
        self.assertEqual(self.evidence["milestone"], "M31")
        self.assertEqual(self.evidence["status"], "PASS")

    def test_09_balanced_ternary_notation_is_exact(self) -> None:
        self.assertEqual(self.evidence["core"]["balanced_ternary_notation"], "-1/0/1")

    def test_10_semantic_domain_is_exact(self) -> None:
        self.assertEqual(self.evidence["core"]["semantic_values"], [-1, 0, 1])

    def test_11_zero_is_an_active_computational_state(self) -> None:
        core = self.evidence["core"]
        self.assertEqual(core["active_neutral_state"], 0)
        self.assertEqual(core["zero_role"], "active_computational_state")

    def test_12_opposite_transitions_are_neutral_mediated(self) -> None:
        self.assertEqual(
            self.evidence["core"]["opposite_transition_routes"],
            [[-1, 0, 1], [1, 0, -1]],
        )

    def test_13_temporal_and_service_scheduler_modes_remain_separate(self) -> None:
        core = self.evidence["core"]
        self.assertEqual(core["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(core["service_scheduler_mode"], "free")

    def test_14_primary_mechanism_is_not_classical_bit_addition(self) -> None:
        core = self.evidence["core"]
        self.assertIs(core["classical_bit_addition_primary_mechanism"], False)
        self.assertEqual(
            core["primary_computational_organization"],
            "retained_relative_phase_interference_and_resonant_selection",
        )

    def test_15_computation_chain_preserves_phase_to_retained_state_order(self) -> None:
        chain = self.evidence["core"]["computation_chain"]
        self.assertEqual(chain[0], "retained phase and frequency state")
        self.assertEqual(chain[3], "resonance selection")
        self.assertEqual(chain[-1], "retained coherent ternary state")

    def test_16_full_core_record_and_cell_counts_are_exact(self) -> None:
        trace = self.evidence["active_zero_execution_evidence"]
        self.assertEqual(trace["record_count"], 100)
        self.assertEqual(trace["cell_observation_count"], 800)

    def test_17_active_zero_observation_count_is_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]
            ["active_zero_after_observation_count"],
            702,
        )

    def test_18_scheduler_mode_counts_are_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["scheduler_mode_counts"],
            {"free": 19, "1/7": 17, "7/1": 64},
        )

    def test_19_scheduler_state_counts_are_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["scheduler_state_counts"],
            {"free": 19, "excite": 3, "neutralize": 14, "balance": 56, "commit": 8},
        )

    def test_20_retained_transition_counts_are_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["retained_transition_counts"],
            {
                "retained_same": 783,
                "polarity_to_active_zero": 5,
                "active_zero_to_polarity": 12,
                "direct_opposite": 0,
            },
        )

    def test_21_full_core_event_totals_are_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["event_totals"],
            {
                "requested_direct_events": 5,
                "prevented_direct_events": 5,
                "neutral_routed_events": 5,
                "actual_direct_events": 0,
                "reserved_state_events": 0,
                "queue_overflow_events": 0,
            },
        )

    def test_22_observed_trace_domain_is_exact(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["observed_ternary_domain"],
            [-1, 0, 1],
        )

    def test_23_all_full_core_records_pass_invariants(self) -> None:
        self.assertEqual(
            self.evidence["active_zero_execution_evidence"]["invariant_pass_records"],
            100,
        )

    def test_24_active_zero_roles_are_explicit_and_unique(self) -> None:
        roles = self.evidence["active_zero_execution_evidence"]["active_zero_roles"]
        self.assertEqual(len(roles), len(set(roles)))
        self.assertIn("balancing", roles)
        self.assertIn("transition_buffering", roles)
        self.assertIn("pending_route_completion_preparation", roles)

    def test_25_trace_contours_preserve_exact_source_identities(self) -> None:
        contours = self.evidence["active_zero_execution_evidence"]["contours"]
        self.assertEqual([item["record_count"] for item in contours], [96, 4])
        self.assertEqual([item["path"] for item in contours], list(m31.TRACE_PATHS))
        self.assertEqual(
            [item["raw_sha256"] for item in contours],
            [m31.INPUT_DIGESTS[path] for path in m31.TRACE_PATHS],
        )

    def test_26_historical_experiment_boundary_is_explicit(self) -> None:
        experiment = self.evidence["historical_thermal_experiment"]
        self.assertEqual(experiment["release"], "FRP v0.9.3")
        self.assertEqual(experiment["measurement_class"], "release_specific_model_thermal_load")
        self.assertIs(experiment["physical_temperature_measurement"], False)

    def test_27_historical_execution_identity_is_exact(self) -> None:
        execution = self.evidence["historical_thermal_experiment"]["execution"]
        self.assertEqual(execution["stdout_byte_count"], 640)
        self.assertEqual(execution["stdout_sha256"], m31.EXPECTED_HISTORICAL_STDOUT_SHA256)
        self.assertEqual(execution["exit_code"], 0)

    def test_28_historical_rows_are_exact_and_ordered(self) -> None:
        experiment = self.evidence["historical_thermal_experiment"]
        self.assertEqual(experiment["architecture_order"], list(m31.EXPECTED_HISTORICAL_ROWS))
        self.assertEqual(
            experiment["rows"],
            [m31.EXPECTED_HISTORICAL_ROWS[name] for name in m31.EXPECTED_HISTORICAL_ROWS],
        )

    def test_29_historical_heat_peak_ratio_is_exact(self) -> None:
        focused = self.evidence["historical_thermal_experiment"]["focused_binary_ternary_comparison"]
        self.assertEqual(focused["heat_peak_ratio_binary_over_active_neutral_ternary"], "15.6923076923")

    def test_30_historical_heat_peak_reduction_is_exact(self) -> None:
        focused = self.evidence["historical_thermal_experiment"]["focused_binary_ternary_comparison"]
        self.assertEqual(focused["heat_peak_relative_reduction_percent_exact"], "93.6274509804")
        self.assertEqual(focused["heat_peak_relative_reduction_percent"], "93.63")

    def test_31_historical_switch_load_ratio_is_exact(self) -> None:
        focused = self.evidence["historical_thermal_experiment"]["focused_binary_ternary_comparison"]
        self.assertEqual(focused["switch_load_ratio_binary_over_active_neutral_ternary"], "4.0")

    def test_32_advantage_is_topology_specific_not_third_symbol_universal(self) -> None:
        relations = self.evidence["historical_thermal_experiment"]["observed_relations"]
        self.assertIs(relations["direct_ternary_heat_peak_equals_binary"], True)
        self.assertIs(relations["advantage_attached_to_distributed_active_neutral_topology"], True)
        self.assertIs(relations["advantage_attached_to_third_symbol_alone"], False)

    def test_33_historical_winner_assertions_are_absent(self) -> None:
        self.assertEqual(self.evidence["historical_thermal_experiment"]["winner_assertions"], [])

    def test_34_current_contour_is_not_physical_temperature(self) -> None:
        current = self.evidence["current_comparative_thermal_contours"]
        self.assertEqual(current["measurement_class"], "shared_model_comparative_benchmark")
        self.assertIs(current["physical_temperature_measurement"], False)
        self.assertIs(current["historical_heat_peak_interchangeable"], False)

    def test_35_current_baseline_identity_is_exact(self) -> None:
        baseline = self.evidence["current_comparative_thermal_contours"]["baseline"]
        self.assertEqual(baseline["schema"], "frp.benchmark.architecture_comparison.v1")
        self.assertEqual(baseline["frp_scheduler"], "7/1")
        self.assertEqual(baseline["raw_sha256"], m31.INPUT_DIGESTS[baseline["source_path"]])

    def test_36_current_baseline_architecture_order_is_exact(self) -> None:
        matrix = self.evidence["current_comparative_thermal_contours"]["baseline"]["comparison_matrix"]
        self.assertEqual([row["architecture_id"] for row in matrix], m31.EXPECTED_ARCHITECTURE_ORDER)

    def test_37_current_baseline_is_pass_without_winner_assertion(self) -> None:
        baseline = self.evidence["current_comparative_thermal_contours"]["baseline"]
        self.assertEqual(baseline["qualification_status"], "PASS")
        self.assertEqual(baseline["winner_assertions"], [])

    def test_38_hardware_sensitivity_scenario_order_is_exact(self) -> None:
        sensitivity = self.evidence["current_comparative_thermal_contours"]["hardware_sensitivity"]
        self.assertEqual(sensitivity["scenario_order"], ["lower_bound", "nominal", "upper_bound"])
        self.assertEqual(
            [item["scenario_id"] for item in sensitivity["scenario_summaries"]],
            sensitivity["scenario_order"],
        )

    def test_39_hardware_sensitivity_ranking_stability_is_preserved(self) -> None:
        ranking = self.evidence["current_comparative_thermal_contours"]["hardware_sensitivity"]["ranking_stability"]
        self.assertIs(ranking["ranking_stable"], True)
        self.assertIs(ranking["ranking_sensitive"], False)

    def test_40_hardware_sensitivity_is_pass_without_winner_assertion(self) -> None:
        sensitivity = self.evidence["current_comparative_thermal_contours"]["hardware_sensitivity"]
        self.assertEqual(sensitivity["qualification_status"], "PASS")
        self.assertEqual(sensitivity["winner_assertions"], [])

    def test_41_thermal_proxy_profile_identity_is_exact(self) -> None:
        profile = self.evidence["current_comparative_thermal_contours"]["thermal_profile"]
        self.assertEqual(profile["temperature_unit"], "normalized_temperature_proxy")
        self.assertEqual(profile["raw_sha256"], m31.INPUT_DIGESTS[profile["source_path"]])

    def test_42_all_evidence_boundary_flags_are_true(self) -> None:
        self.assertTrue(all(self.evidence["evidence_boundaries"].values()))

    def test_43_observatory_contract_is_strictly_read_only(self) -> None:
        contract = self.evidence["observatory_publication_contract"]
        self.assertEqual(contract["direction"], "upstream_published_bytes_to_downstream")
        self.assertEqual(contract["downstream_writeback"], "forbidden")
        self.assertEqual(contract["downstream_source_mutation"], "forbidden")
        self.assertEqual(contract["downstream_semantic_reimplementation"], "forbidden")
        self.assertIs(contract["m29_boundary_confirmed"], True)

    def test_44_provenance_is_complete_and_digest_bound(self) -> None:
        provenance = self.evidence["provenance"]
        self.assertEqual(len(provenance), len(m31.INPUT_DIGESTS) + 2)
        indexed = {item["path"]: item for item in provenance}
        for path, digest in m31.INPUT_DIGESTS.items():
            self.assertEqual(indexed[path]["raw_sha256"], digest)
            self.assertIs(indexed[path]["m30_archive_member_verified"], True)
        self.assertEqual(indexed[m31.ARCHIVE_PATH]["raw_sha256"], m31.ARCHIVE_SHA256)

    def test_45_generation_returns_only_the_four_exact_outputs(self) -> None:
        self.assertEqual(self.generation["status"], "PASS")
        self.assertEqual(
            [item["path"] for item in self.generation["outputs"]],
            list(EXPECTED_OUTPUTS),
        )

    def test_46_generated_output_byte_counts_are_exact(self) -> None:
        observed = {item["path"]: item["byte_count"] for item in self.generation["outputs"]}
        self.assertEqual(observed, {path: values[0] for path, values in EXPECTED_OUTPUTS.items()})

    def test_47_generated_output_digests_are_exact(self) -> None:
        observed = {item["path"]: item["raw_sha256"] for item in self.generation["outputs"]}
        self.assertEqual(observed, {path: values[1] for path, values in EXPECTED_OUTPUTS.items()})
        for path, (_, digest) in EXPECTED_OUTPUTS.items():
            self.assertEqual(hashlib.sha256((self.output_root / path).read_bytes()).hexdigest(), digest)

    def test_48_independent_verification_accepts_exact_outputs(self) -> None:
        result = m31.verify(ROOT, self.output_root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual([item["path"] for item in result["verified_outputs"]], list(EXPECTED_OUTPUTS))

    def test_49_self_test_is_deterministic_and_exact(self) -> None:
        result = m31.self_test(ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["evidence_sha256"], EXPECTED_OUTPUTS[m31.EVIDENCE_PATH][1])
        self.assertTrue(all(value is True for value in result["checks"].values() if isinstance(value, bool) and value))
        self.assertIs(result["checks"]["classical_bit_addition_primary_mechanism"], False)

    def test_50_invalid_ternary_notation_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["core"]["balanced_ternary_notation"] = "invalid"
        with self.assertRaisesRegex(m31.EvidenceError, "ternary notation"):
            m31.validate_evidence_document(evidence)

    def test_51_invalid_ternary_domain_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["core"]["semantic_values"] = [-1, 1]
        with self.assertRaisesRegex(m31.EvidenceError, "ternary domain"):
            m31.validate_evidence_document(evidence)

    def test_52_direct_opposite_transition_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["active_zero_execution_evidence"]["retained_transition_counts"]["direct_opposite"] = 1
        with self.assertRaisesRegex(m31.EvidenceError, "direct opposite"):
            m31.validate_evidence_document(evidence)

    def test_53_physical_temperature_claim_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["historical_thermal_experiment"]["physical_temperature_measurement"] = True
        with self.assertRaisesRegex(m31.EvidenceError, "measurement boundary"):
            m31.validate_evidence_document(evidence)

    def test_54_historical_ratio_tamper_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["historical_thermal_experiment"]["focused_binary_ternary_comparison"][
            "heat_peak_ratio_binary_over_active_neutral_ternary"
        ] = "1"
        with self.assertRaisesRegex(m31.EvidenceError, "heat ratio"):
            m31.validate_evidence_document(evidence)

    def test_55_observatory_writeback_permission_is_rejected(self) -> None:
        evidence = self.fresh_evidence()
        evidence["observatory_publication_contract"]["downstream_writeback"] = "allowed"
        with self.assertRaisesRegex(m31.EvidenceError, "writeback"):
            m31.validate_evidence_document(evidence)

    def test_56_load_json_rejects_nonobject_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "value.json").write_text("[]\n", encoding="utf-8")
            with self.assertRaisesRegex(m31.EvidenceError, "JSON object required"):
                m31.load_json(root, "value.json")

    def test_57_read_regular_rejects_missing_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(m31.EvidenceError, "regular file is missing"):
                m31.read_regular(Path(temporary), "missing.json")

    def test_58_write_json_is_canonical_and_refuses_directory_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            record = m31.write_json(root, "safe/value.json", {"z": 1, "a": 2})
            raw = (root / "safe/value.json").read_bytes()
            self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(raw, m31.canonical_json_bytes({"z": 1, "a": 2}))
            (root / "blocked").mkdir()
            with self.assertRaisesRegex(m31.EvidenceError, "non-regular output"):
                m31.write_json(root, "blocked", {})

    def test_59_tampered_trace_direct_transition_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in m31.TRACE_PATHS:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            first = root / m31.TRACE_PATHS[0]
            trace = json.loads(first.read_text(encoding="utf-8"))
            trace["records"][0]["retained_state_before"][0] = -1
            trace["records"][0]["retained_state_after"][0] = 1
            first.write_text(json.dumps(trace), encoding="utf-8")
            with self.assertRaisesRegex(m31.EvidenceError, "retained-transition"):
                m31.build_active_zero_trace_evidence(root)

    def test_60_current_winner_assertion_tamper_is_rejected(self) -> None:
        paths = [
            "benchmarks/architecture_comparison/results/reference_comparison_seed_76.json",
            "benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json",
            "benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in paths:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
            baseline = root / paths[0]
            value = json.loads(baseline.read_text(encoding="utf-8"))
            value["qualification"]["winner_assertions"] = ["forbidden"]
            baseline.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(m31.EvidenceError, "winner assertion"):
                m31.build_current_comparative_contours(root)


if __name__ == "__main__":
    unittest.main()
