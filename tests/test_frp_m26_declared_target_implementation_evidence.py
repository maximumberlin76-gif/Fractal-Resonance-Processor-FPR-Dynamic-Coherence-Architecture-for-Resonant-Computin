"""Tests for FRP M26 declared-target implementation evidence."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import frp_m26_declared_target_implementation_evidence as M26


ROOT = Path(__file__).resolve().parents[1]


class M26DeclaredTargetImplementationEvidenceTests(unittest.TestCase):
    """Exercise the complete M26 target, provenance, reports, and closure."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads((ROOT / M26.CONTRACT_ARTIFACT).read_text(encoding="utf-8"))
        cls.provenance = json.loads((ROOT / M26.PROVENANCE_ARTIFACT).read_text(encoding="utf-8"))
        cls.report = json.loads((ROOT / M26.REPORT_ARTIFACT).read_text(encoding="utf-8"))
        cls.reproducibility = json.loads((ROOT / M26.REPRODUCIBILITY_ARTIFACT).read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / M26.MANIFEST_ARTIFACT).read_text(encoding="utf-8"))
        cls.qualification = json.loads((ROOT / M26.QUALIFICATION_ARTIFACT).read_text(encoding="utf-8"))
        cls.implementation = cls.report["implementation_result"]

    def test_release_milestone_and_source_commit_are_exact(self) -> None:
        self.assertEqual((M26.VERSION, M26.MILESTONE), ("2.8.0", "M26"))
        self.assertEqual(self.contract["release"], "FRP v2.8.0")
        self.assertEqual(self.contract["source_commit"], M26.EXPECTED_M25_COMMIT)
        with self.assertRaises(M26.ContractError):
            M26.validate_source_commit("0" * 40)

    def test_immutable_core_vocabulary_is_exact(self) -> None:
        core = self.contract["immutable_core"]
        self.assertEqual(core["balanced_ternary_notation"], "-1/0/1")
        self.assertEqual(core["semantic_values"], [-1, 0, 1])
        self.assertEqual(core["active_neutral_state"], 0)
        self.assertEqual(core["temporal_scheduler_modes"], ["1/7", "7/1"])
        self.assertEqual(core["service_scheduler_mode"], "free")
        text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in M26.TECHNICAL_SOURCE_PATHS)
        self.assertNotIn("-1/0/" + "+1", text)

    def test_required_scope_is_complete_and_ordered(self) -> None:
        self.assertEqual(tuple(self.contract["required_scope"]), M26.REQUIRED_SCOPE)
        self.assertEqual(len(self.contract["required_scope"]), 11)

    def test_declared_target_is_exact(self) -> None:
        target = self.contract["declared_target"]
        self.assertEqual(target["target_id"], "ice40-hx8k-ct256-cells8")
        self.assertEqual((target["device"], target["package"]), ("iCE40HX8K", "CT256"))
        self.assertEqual((target["cells"], target["request_lanes"]), (8, 2))
        self.assertEqual(target["top_module"], M26.TARGET_TOP)

    def test_target_top_binds_the_hardened_boundary(self) -> None:
        source = (ROOT / M26.TARGET_TOP_PATH).read_text(encoding="utf-8")
        self.assertIn("frp_m23_hardened_integration_boundary", source)
        self.assertIn("localparam int M26_CELLS = 8;", source)
        self.assertIn("localparam int M26_REQUEST_LANES = 2;", source)
        stub = (ROOT / M26.SYNTHESIS_STUB_PATH).read_text(encoding="utf-8")
        self.assertIn("module frp_m23_interface_protocol_assertions", stub)
        self.assertNotIn("always_ff", stub)

    def test_constraints_are_exact_and_bound_to_both_clocks(self) -> None:
        constraints = self.contract["declared_constraints"]
        self.assertEqual((constraints["host_clock_mhz"], constraints["host_period_ns"]), (10, 100.0))
        self.assertEqual((constraints["core_clock_mhz"], constraints["core_period_ns"]), (8, 125.0))
        self.assertEqual(constraints["board_pinout"], "unbound")
        lines = (ROOT / M26.CONSTRAINT_PATH).read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines, [
            "create_clock -name host_clk -period 100.000 [get_ports host_clk]",
            "create_clock -name core_clk -period 125.000 [get_ports core_clk]",
        ])

    def test_toolchain_versions_are_exact(self) -> None:
        tools = self.provenance["toolchain"]
        self.assertEqual(tools["yosys"]["package_version"], "0.68.0.0.post1208")
        self.assertEqual(tools["yosys"]["engine_version"], "0.68")
        self.assertEqual(tools["yosys"]["engine_git_sha"], "38e001a6f")
        self.assertEqual(tools["nextpnr"]["package_version"], "0.11.1.0.post826")
        self.assertEqual(tools["nextpnr"]["engine_version"], "nextpnr-0.11.1")

    def test_command_provenance_is_complete(self) -> None:
        commands = self.provenance["commands"]
        self.assertEqual(len(commands), 4)
        self.assertEqual({item["run_id"] for item in commands}, {"RUN_A", "RUN_B"})
        self.assertEqual({item["stage"] for item in commands}, {"synthesis", "place_route_timing_resource"})
        joined = "\n".join(" ".join(item["argv"]) for item in commands)
        for token in ("--hx8k", "ct256", "--seed 26", "--threads 1", "--ignore-rel-clk", "synth_ice40"):
            self.assertIn(token, joined)

    def test_synthesis_report_is_exact(self) -> None:
        synthesis = self.report["synthesis"]
        self.assertEqual((synthesis["num_ports"], synthesis["num_port_bits"], synthesis["num_cells"]), (18, 87, 2164))
        self.assertEqual(synthesis["cell_types"], {"SB_CARRY": 291, "SB_DFFER": 269, "SB_DFFR": 215, "SB_LUT4": 1389})

    def test_resource_report_is_exact(self) -> None:
        self.assertEqual(self.report["implementation"]["utilization"], M26.EXPECTED_UTILIZATION)
        self.assertEqual(self.report["implementation"]["timing_status"], "PASS")

    def test_timing_constraints_pass(self) -> None:
        clocks = {item["clock"]: item for item in self.report["implementation"]["clocks"]}
        self.assertEqual(clocks["host_clk"]["constraint_mhz"], 10)
        self.assertEqual(clocks["core_clk"]["constraint_mhz"], 8)
        for item in clocks.values():
            self.assertGreaterEqual(item["achieved_mhz"], item["constraint_mhz"])
            self.assertEqual(item["status"], "PASS")

    def test_implementation_warning_is_retained_and_classified(self) -> None:
        diagnostics = self.report["diagnostics"]
        self.assertEqual((diagnostics["warning_count"], diagnostics["error_count"]), (1, 0))
        warning = diagnostics["warnings"][0]
        self.assertEqual(warning["message"], M26.EXPECTED_WARNING)
        self.assertEqual(warning["classification"], "declared_target_package_with_unbound_board_pinout")
        self.assertTrue(warning["retained"])

    def test_two_runs_are_byte_reproducible(self) -> None:
        self.assertEqual(self.implementation["run_count"], 2)
        self.assertEqual(self.reproducibility["compared_output_count"], 5)
        self.assertEqual(self.reproducibility["matching_output_count"], 5)
        self.assertEqual(self.reproducibility["mismatching_output_count"], 0)
        self.assertTrue(self.reproducibility["canonical_metrics_identical"])
        for record in self.reproducibility["outputs"]:
            self.assertEqual(record["run_a_bytes"], record["run_b_bytes"])
            self.assertEqual(record["run_a_sha256"], record["run_b_sha256"])
            self.assertTrue(record["byte_identical"])

    def test_all_nested_and_top_level_digests_are_exact(self) -> None:
        implementation = dict(self.implementation)
        self.assertEqual(implementation.pop("implementation_result_digest"), M26.object_digest(implementation))
        for run in self.implementation["runs"]:
            payload = dict(run)
            self.assertEqual(payload.pop("run_digest"), M26.object_digest(payload))
        for document, field in (
            (self.contract, "contract_digest"),
            (self.provenance, "provenance_digest"),
            (self.report, "report_digest"),
            (self.reproducibility, "reproducibility_digest"),
            (self.manifest, "manifest_digest"),
            (self.qualification, "qualification_digest"),
        ):
            payload = dict(document)
            self.assertEqual(payload.pop(field), M26.object_digest(payload))

    def test_schema_registry_and_artifacts_validate(self) -> None:
        registry = json.loads((ROOT / M26.REGISTRY_PATH).read_text(encoding="utf-8"))
        self.assertEqual([item["schema_id"] for item in registry["records"]], list(M26.SCHEMA_PATHS))
        self.assertEqual([item["path"] for item in registry["records"]], list(M26.SCHEMA_PATHS.values()))
        schemas = M26.SchemaContext(ROOT)
        mapping = {
            M26.CONTRACT_ARTIFACT: M26.CONTRACT_SCHEMA,
            M26.PROVENANCE_ARTIFACT: M26.PROVENANCE_SCHEMA,
            M26.REPORT_ARTIFACT: M26.REPORT_SCHEMA,
            M26.REPRODUCIBILITY_ARTIFACT: M26.REPRODUCIBILITY_SCHEMA,
            M26.MANIFEST_ARTIFACT: M26.MANIFEST_SCHEMA,
            M26.QUALIFICATION_ARTIFACT: M26.QUALIFICATION_SCHEMA,
        }
        for artifact, schema in mapping.items():
            schemas.validate(schema, json.loads((ROOT / artifact).read_text(encoding="utf-8")), artifact)
        invalid = copy.deepcopy(self.contract)
        invalid["immutable_core"]["balanced_ternary_notation"] = "invalid"
        with self.assertRaises(M26.ContractError):
            schemas.validate(M26.CONTRACT_SCHEMA, invalid, "invalid-core")

    def test_manifest_boundaries_and_raw_digests_are_exact(self) -> None:
        self.assertEqual(self.manifest["source_count"], len((M26.WORKFLOW_PATH, *M26.TECHNICAL_SOURCE_PATHS)))
        self.assertEqual(self.manifest["upstream_dependency_count"], len(M26.UPSTREAM_SOURCE_PATHS))
        self.assertEqual(self.manifest["artifact_count"], 4)
        for collection in (self.manifest["sources"], self.manifest["upstream_dependencies"]):
            for record in collection:
                raw = (ROOT / record["path"]).read_bytes()
                self.assertEqual(record["bytes"], len(raw))
                self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())

    def test_evidence_boundary_does_not_claim_physical_measurement(self) -> None:
        boundary = self.contract["evidence_boundary"]
        classification = self.report["evidence_classification"]
        self.assertEqual(boundary["physical_measurement_status"], "not_a_physical_measurement")
        self.assertEqual(boundary["universal_physical_chip_claim"], "not_made")
        self.assertEqual(boundary["proxy_to_physical_conversion"], "prohibited")
        self.assertFalse(classification["physical_measurements"])
        self.assertFalse(classification["board_pinout_bound"])
        self.assertFalse(classification["universal_chip_claim"])

    def test_qualification_is_complete(self) -> None:
        self.assertEqual(self.qualification["overall_status"], "PASS")
        self.assertEqual(self.qualification["check_count"], self.qualification["passed_count"])
        self.assertEqual(self.qualification["failed_count"], 0)
        self.assertGreaterEqual(self.qualification["check_count"], 55)

    def test_generation_is_byte_stable(self) -> None:
        outputs_a = M26.build_outputs(ROOT, self.implementation, M26.EXPECTED_M25_COMMIT)
        outputs_b = M26.build_outputs(ROOT, self.implementation, M26.EXPECTED_M25_COMMIT)
        self.assertEqual(outputs_a, outputs_b)
        for path, raw in outputs_a.items():
            self.assertEqual(raw, (ROOT / path).read_bytes())

    def test_workflow_is_manual_only_and_named_as_workflow(self) -> None:
        self.assertIn("workflow", Path(M26.WORKFLOW_PATH).name)
        workflow = (ROOT / M26.WORKFLOW_PATH).read_text(encoding="utf-8")
        self.assertIn("  workflow_dispatch:", workflow)
        self.assertNotIn("  push:", workflow)
        self.assertNotIn("  pull_request:", workflow)

    def test_safe_paths_reject_escape_forms(self) -> None:
        for value in ("", "/absolute", "../escape", "a/../b", "a\\b"):
            with self.subTest(value=value), self.assertRaises(M26.SafetyError):
                M26.safe_relative_path(value)

    def test_committed_verification_and_self_test_pass(self) -> None:
        verification = M26.verify(ROOT, M26.EXPECTED_M25_COMMIT)
        self.assertEqual((verification["status"], verification["artifact_count"]), ("PASS", 6))
        result = M26.self_test(ROOT, M26.EXPECTED_M25_COMMIT)
        self.assertEqual((result["check_count"], result["passed_count"], result["failed_count"]), (12, 12, 0))


if __name__ == "__main__":
    unittest.main()
