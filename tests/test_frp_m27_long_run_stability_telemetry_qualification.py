"""Tests for FRP M27 long-run stability and telemetry qualification."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import frp_m27_long_run_stability_telemetry_qualification as M27


ROOT = Path(__file__).resolve().parents[1]


class M27LongRunStabilityTelemetryQualificationTests(unittest.TestCase):
    """Exercise M27 identities, checkpoints, relations, schemas, and closure."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads((ROOT / M27.CONTRACT_ARTIFACT).read_text(encoding="utf-8"))
        cls.workload = json.loads((ROOT / M27.WORKLOAD_ARTIFACT).read_text(encoding="utf-8"))
        cls.evidence = json.loads((ROOT / M27.CHECKPOINT_ARTIFACT).read_text(encoding="utf-8"))
        cls.telemetry = json.loads((ROOT / M27.TELEMETRY_ARTIFACT).read_text(encoding="utf-8"))
        cls.report = json.loads((ROOT / M27.REPORT_ARTIFACT).read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / M27.MANIFEST_ARTIFACT).read_text(encoding="utf-8"))
        cls.qualification = json.loads((ROOT / M27.QUALIFICATION_ARTIFACT).read_text(encoding="utf-8"))

    def test_release_milestone_and_source_boundary_are_exact(self) -> None:
        self.assertEqual((M27.VERSION, M27.MILESTONE), ("2.9.0", "M27"))
        self.assertEqual(self.contract["release"], "FRP v2.9.0")
        self.assertEqual(self.contract["source_commit"], M27.EXPECTED_M26_COMMIT)
        with self.assertRaises(M27.ContractError):
            M27.validate_source_commit("0" * 40)

    def test_immutable_core_vocabulary_is_exact(self) -> None:
        core = self.contract["immutable_core"]
        self.assertEqual(core["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(core["semantic_values"], [-1, 0, 1])
        self.assertEqual(core["active_neutral_state"], 0)
        self.assertEqual(core["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(core["service_scheduler_mode"], "free")
        text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in M27.TECHNICAL_SOURCE_PATHS)
        self.assertNotIn("-1/0/" + "+1", text)

    def test_required_scope_is_complete_and_ordered(self) -> None:
        self.assertEqual(tuple(self.contract["required_scope"]), M27.REQUIRED_SCOPE)
        self.assertEqual(len(self.contract["required_scope"]), 12)

    def test_long_run_boundary_is_exact(self) -> None:
        boundary = self.contract["long_run_boundary"]
        self.assertEqual(boundary["profile_count"], 3)
        self.assertEqual(boundary["ticks_per_profile"], 16384)
        self.assertEqual(boundary["total_ticks"], 49152)
        self.assertEqual((boundary["cells"], boundary["request_lanes"]), (16, 4))
        self.assertFalse(boundary["full_tick_trace_committed"])

    def test_workload_phase_partition_is_total(self) -> None:
        self.assertEqual(M27.ACTIVE_TICKS + M27.SETTLE_TICKS + M27.IDLE_TICKS, M27.PHASE_PERIOD_TICKS)
        counts = {phase: 0 for phase in ("active", "settle", "idle")}
        for tick in range(M27.PHASE_PERIOD_TICKS):
            counts[M27.workload_phase(tick)] += 1
        self.assertEqual(counts, {"active": 192, "settle": 32, "idle": 32})

    def test_workload_requests_are_deterministic_and_core_bounded(self) -> None:
        first = [M27.workload_requests(tick, 5) for tick in range(512)]
        second = [M27.workload_requests(tick, 5) for tick in range(512)]
        self.assertEqual(first, second)
        for tick, requests in enumerate(first):
            self.assertLessEqual(len(requests), M27.REQUEST_LANES)
            if M27.workload_phase(tick) != "active":
                self.assertEqual(requests, [])
            for valid, cell_id, target in requests:
                self.assertIsInstance(valid, bool)
                self.assertIn(cell_id, range(M27.CELLS))
                self.assertIn(target, (-1, 0, 1))

    def test_workload_catalog_profiles_have_exact_identities(self) -> None:
        self.assertEqual(self.workload["profile_count"], len(M27.PROFILE_SPECS))
        self.assertEqual(self.workload["profiles"], [M27.profile_identity(spec) for spec in M27.PROFILE_SPECS])
        for identity in self.workload["profiles"]:
            M27.verify_digest(identity, "workload_identity_digest", identity["profile_id"])
        M27.verify_digest(self.workload, "catalog_digest", "workload catalog")

    def test_long_run_profile_and_checkpoint_counts_are_exact(self) -> None:
        self.assertEqual(self.evidence["profile_count"], 3)
        self.assertEqual(self.evidence["total_ticks"], 49152)
        self.assertEqual(self.evidence["checkpoint_count"], 96)
        self.assertEqual([profile["checkpoint_count"] for profile in self.evidence["profiles"]], [32, 32, 32])

    def test_scheduler_counts_match_the_canonical_scheduler(self) -> None:
        for profile in self.evidence["profiles"]:
            expected = dict(sorted(M27.expected_scheduler_counts(profile["scheduler_mode"], M27.RUN_TICKS).items()))
            self.assertEqual(profile["scheduler_counts"], expected)
            self.assertEqual(profile["expected_scheduler_counts"], expected)

    def test_checkpoints_are_strictly_ordered_and_digest_bound(self) -> None:
        expected_ticks = list(range(M27.CHECKPOINT_INTERVAL - 1, M27.RUN_TICKS, M27.CHECKPOINT_INTERVAL))
        all_checkpoints = []
        for profile in self.evidence["profiles"]:
            checkpoints = profile["checkpoints"]
            self.assertEqual([item["tick"] for item in checkpoints], expected_ticks)
            for checkpoint in checkpoints:
                M27.verify_digest(checkpoint, "checkpoint_digest", "checkpoint")
                self.assertRegex(checkpoint["chain_digest"], r"^[0-9a-f]{64}$")
            self.assertEqual(profile["final_chain_digest"], checkpoints[-1]["chain_digest"])
            all_checkpoints.extend(checkpoints)
        self.assertEqual(self.evidence["checkpoint_set_digest"], M27.object_digest(all_checkpoints))

    def test_checkpoint_telemetry_relations_are_exact(self) -> None:
        for profile in self.evidence["profiles"]:
            for checkpoint in profile["checkpoints"]:
                self.assertEqual(
                    checkpoint["transition_pressure_q16"],
                    checkpoint["thermal_state_proxy_q16"] + checkpoint["switching_load_q16"],
                )
                self.assertEqual(
                    checkpoint["stability_margin_q16"],
                    checkpoint["coherence_capacity_q16"] - checkpoint["transition_pressure_q16"],
                )
                self.assertEqual(
                    checkpoint["transition_capacity_remaining"],
                    M27.REQUEST_LANES - checkpoint["changes"],
                )

    def test_checkpoint_state_domain_and_capacity_are_exact(self) -> None:
        for profile in self.evidence["profiles"]:
            for checkpoint in profile["checkpoints"]:
                self.assertEqual(len(checkpoint["states"]), M27.CELLS)
                self.assertTrue(all(state in (-1, 0, 1) for state in checkpoint["states"]))
                self.assertLessEqual(checkpoint["changes"], M27.REQUEST_LANES)
                self.assertLessEqual(checkpoint["pending_route_count"], M27.CELLS)

    def test_counter_relations_and_safety_counters_are_exact(self) -> None:
        for profile in self.evidence["profiles"]:
            counters = profile["counter_relations"]
            self.assertGreaterEqual(counters["prevented_direct_events"], counters["requested_direct_events"])
            self.assertEqual(counters["neutral_routed_events"], counters["neutralized_conflicts"])
            self.assertEqual(
                (counters["actual_direct_events"], counters["reserved_state_events"], counters["queue_overflow_events"]),
                (0, 0, 0),
            )
            self.assertTrue(counters["safety_counters_zero"])

    def test_zero_event_intervals_are_ordered_and_bounded(self) -> None:
        for profile in self.evidence["profiles"]:
            record = profile["zero_event_record"]
            intervals = record["intervals"]
            self.assertEqual(record["retained_interval_count"], len(intervals))
            self.assertGreater(len(intervals), 0)
            previous_end = -1
            for interval in intervals:
                self.assertGreater(interval["start_tick"], previous_end)
                self.assertEqual(interval["tick_count"], interval["end_tick"] - interval["start_tick"] + 1)
                self.assertGreaterEqual(interval["tick_count"], M27.ZERO_EVENT_MIN_TICKS)
                previous_end = interval["end_tick"]

    def test_stability_boundary_records_are_explicit(self) -> None:
        for profile in self.evidence["profiles"]:
            boundary = profile["stability_boundary_record"]
            self.assertIn(boundary["observation_status"], ("crossed", "not_crossed"))
            self.assertEqual(boundary["crossing_count"], len(boundary["crossings"]))
            self.assertIn(boundary["minimum_margin_tick"], range(M27.RUN_TICKS))
            self.assertEqual(boundary["final_margin_class"], M27.margin_class(boundary["final_margin_q16"]))

    def test_runtime_retention_is_bounded_per_tick(self) -> None:
        for profile in self.evidence["profiles"]:
            retention = profile["bounded_runtime_retention"]
            self.assertTrue(retention["per_tick_trace_cleared"])
            self.assertTrue(retention["per_cell_trace_cleared"])
            self.assertTrue(retention["route_event_trace_cleared"])
            self.assertEqual(retention["retained_trace_peak_records"], 1)
            self.assertEqual(retention["retained_cell_trace_peak_records"], M27.CELLS)

    def test_telemetry_types_domains_and_proxy_labels_are_explicit(self) -> None:
        self.assertEqual(self.telemetry["telemetry_count"], 6)
        for item in self.telemetry["telemetry"]:
            self.assertTrue(item["storage_type"].startswith("signed_integer_s32q"))
            self.assertLessEqual(item["domain"]["minimum"], item["domain"]["maximum"])
            self.assertTrue(item["classification"].startswith("dimensionless_model_"))
        boundary = self.telemetry["interpretation_boundary"]
        self.assertTrue(boundary["all_values_are_model_derived"])
        self.assertTrue(boundary["all_values_are_dimensionless"])
        self.assertFalse(boundary["physical_units_published"])
        self.assertFalse(boundary["physical_measurements_published"])

    def test_report_closure_relations_are_all_true(self) -> None:
        aggregate = self.report["aggregate"]
        self.assertTrue(aggregate["all_profiles_passed"])
        self.assertTrue(aggregate["all_safety_counters_zero"])
        self.assertTrue(aggregate["all_counter_relations_valid"])
        self.assertTrue(aggregate["all_capacity_relations_valid"])
        self.assertTrue(self.report["deterministic_rerun_requirement"]["workflow_enforced"])

    def test_all_nested_and_top_level_digests_are_exact(self) -> None:
        for profile in self.evidence["profiles"]:
            M27.verify_digest(profile, "profile_result_digest", profile["profile_id"])
        for document, field in (
            (self.contract, "contract_digest"),
            (self.workload, "catalog_digest"),
            (self.evidence, "evidence_digest"),
            (self.telemetry, "semantics_digest"),
            (self.report, "report_digest"),
            (self.manifest, "manifest_digest"),
            (self.qualification, "qualification_digest"),
        ):
            M27.verify_digest(document, field, field)

    def test_schema_registry_and_artifacts_validate(self) -> None:
        registry = json.loads((ROOT / M27.REGISTRY_PATH).read_text(encoding="utf-8"))
        self.assertEqual([item["schema_id"] for item in registry["records"]], list(M27.SCHEMA_PATHS))
        self.assertEqual([item["path"] for item in registry["records"]], list(M27.SCHEMA_PATHS.values()))
        schemas = M27.SchemaContext(ROOT)
        mapping = {
            M27.CONTRACT_ARTIFACT: M27.CONTRACT_SCHEMA,
            M27.WORKLOAD_ARTIFACT: M27.WORKLOAD_SCHEMA,
            M27.CHECKPOINT_ARTIFACT: M27.CHECKPOINT_SCHEMA,
            M27.TELEMETRY_ARTIFACT: M27.TELEMETRY_SCHEMA,
            M27.REPORT_ARTIFACT: M27.REPORT_SCHEMA,
            M27.MANIFEST_ARTIFACT: M27.MANIFEST_SCHEMA,
            M27.QUALIFICATION_ARTIFACT: M27.QUALIFICATION_SCHEMA,
        }
        for artifact, schema in mapping.items():
            schemas.validate(schema, json.loads((ROOT / artifact).read_text(encoding="utf-8")), artifact)
        invalid = copy.deepcopy(self.contract)
        invalid["immutable_core"]["balanced_ternary_notation"] = "invalid"
        with self.assertRaises(M27.ContractError):
            schemas.validate(M27.CONTRACT_SCHEMA, invalid, "invalid-core")

    def test_manifest_source_and_artifact_digests_are_exact(self) -> None:
        self.assertEqual(self.manifest["source_count"], len((M27.WORKFLOW_PATH, *M27.TECHNICAL_SOURCE_PATHS)))
        self.assertEqual(self.manifest["upstream_dependency_count"], len(M27.UPSTREAM_SOURCE_PATHS))
        self.assertEqual(self.manifest["artifact_count"], len(M27.PRIMARY_ARTIFACT_PATHS))
        for collection in (self.manifest["sources"], self.manifest["upstream_dependencies"], self.manifest["artifacts"]):
            for record in collection:
                raw = (ROOT / record["path"]).read_bytes()
                self.assertEqual(record["bytes"], len(raw))
                self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())

    def test_artifact_size_and_retention_policy_are_enforced(self) -> None:
        retention = self.manifest["retention_validation"]
        self.assertTrue(retention["all_primary_files_within_limit"])
        self.assertTrue(retention["primary_set_within_limit"])
        self.assertLessEqual(retention["observed_primary_set_bytes"], M27.CANONICAL_PRIMARY_SET_MAX_BYTES)
        self.assertEqual(retention["raw_workflow_retention_days"], 30)
        for record in self.manifest["artifacts"]:
            self.assertLessEqual(record["bytes"], M27.CANONICAL_FILE_MAX_BYTES)

    def test_workflow_is_manual_only_and_filename_is_explicit(self) -> None:
        self.assertIn("workflow", Path(M27.WORKFLOW_PATH).name)
        workflow = (ROOT / M27.WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertIn("  workflow_dispatch:", workflow)
        self.assertNotIn("  push:", workflow)
        self.assertNotIn("  pull_request:", workflow)
        self.assertIn("cmp --silent", workflow)

    def test_safe_paths_reject_escape_forms(self) -> None:
        for value in ("", "/absolute", "../escape", "a/../b", "a\\b"):
            with self.subTest(value=value), self.assertRaises(M27.SafetyError):
                M27.safe_relative_path(value)

    def test_validate_long_run_rejects_modified_evidence(self) -> None:
        invalid = copy.deepcopy(self.evidence)
        invalid["profiles"][0]["checkpoints"][0]["changes"] = 5
        with self.assertRaises(M27.ContractError):
            M27.validate_long_run_result(invalid, M27.EXPECTED_M26_COMMIT)

    def test_qualification_is_complete_and_closed(self) -> None:
        self.assertEqual(self.qualification["overall_status"], "PASS")
        self.assertEqual(self.qualification["check_count"], len(self.qualification["checks"]))
        self.assertEqual(self.qualification["passed_count"], self.qualification["check_count"])
        self.assertEqual(self.qualification["failed_count"], 0)
        self.assertEqual(self.qualification["checks"][-1]["evidence"], "long-run stability and telemetry qualification is closed")

    def test_committed_verification_and_self_test_pass(self) -> None:
        verification = M27.verify(ROOT, M27.EXPECTED_M26_COMMIT)
        self.assertEqual((verification["status"], verification["artifact_count"]), ("PASS", 7))
        result = M27.self_test(ROOT, M27.EXPECTED_M26_COMMIT)
        self.assertEqual((result["check_count"], result["passed_count"], result["failed_count"]), (12, 12, 0))


if __name__ == "__main__":
    unittest.main()
