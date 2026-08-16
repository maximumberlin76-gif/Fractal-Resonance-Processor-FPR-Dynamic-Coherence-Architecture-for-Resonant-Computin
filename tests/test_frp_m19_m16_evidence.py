from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "frp_m19_m16_evidence.py"
SPEC = importlib.util.spec_from_file_location("frp_m19_m16_evidence", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load M19 producer module")
M19 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M19)


class M19StaticBoundaryTests(unittest.TestCase):
    def test_identity_and_generated_path_set_are_exact(self) -> None:
        self.assertEqual(M19.VERSION, "2.1.0")
        self.assertEqual(
            M19.MILESTONE,
            "M19 — Machine-Readable M16 Execution and Qualification Evidence",
        )
        self.assertEqual(len(M19.GENERATED_PATHS), 10)
        self.assertEqual(len(set(M19.GENERATED_PATHS)), 10)
        self.assertEqual(tuple(sorted(M19.GENERATED_PATHS)), tuple(sorted(set(M19.GENERATED_PATHS))))

    def test_schema_registry_and_formal_schemas_are_exact(self) -> None:
        context = M19.SchemaContext(ROOT)
        self.assertEqual(set(context.schemas), set(M19.SCHEMA_PATHS))
        self.assertEqual(len(context.schemas), 8)

    def test_technical_source_set_is_exact_and_present(self) -> None:
        self.assertEqual(len(M19.TECHNICAL_SOURCE_PATHS), 28)
        self.assertEqual(tuple(sorted(M19.TECHNICAL_SOURCE_PATHS)), M19.TECHNICAL_SOURCE_PATHS)
        for relative in M19.TECHNICAL_SOURCE_PATHS:
            path = M19.source_file(ROOT, relative)
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 0)

    def test_monitor_observes_original_testbenches_without_modification(self) -> None:
        source = (ROOT / M19.MONITOR).read_text(encoding="utf-8")
        self.assertIn('`include "frp_m16_tb.sv"', source)
        self.assertIn('`include "frp_m16_fpga_tb.sv"', source)
        self.assertIn("frp_m16_tb source();", source)
        self.assertIn("frp_m16_fpga_tb source();", source)
        self.assertNotIn("$fopen", source)
        self.assertNotIn("$fwrite", source)

    def test_monitor_raw_record_width_and_terminal_counts_are_exact(self) -> None:
        source = (ROOT / M19.MONITOR).read_text(encoding="utf-8")
        marker_lines = [line for line in source.splitlines() if '"FRP_M19|1|' in line]
        self.assertEqual(len(marker_lines), 2)
        for line in marker_lines:
            self.assertEqual(line.count("%0"), 35)
        self.assertIn('"FRP M19 RTL evidence records=96"', source)
        self.assertIn('"FRP M19 FPGA evidence records=4"', source)

    def test_qualified_m16_source_hashes_are_unchanged(self) -> None:
        expected = {
            "rtl/m16/frp_m16_tb.sv": "36a9b0a326a3ff9fb87f9df8f7fb0c8daeaaeef74fe374bd41307fa7409b8885",
            "rtl/m16/frp_m16_core.sv": "3b94f5caa5ee28da0060a38dd9b4ba4605ef5f86ac93f5425967e515ff1ebd23",
            "fpga/m16/frp_m16_fpga_top.sv": "de2d23ed8921de2daad49bad17c290f38ecadf074641c702b759d511edee35dc",
            "fpga/m16/frp_m16_fpga_tb.sv": "95aac48eb4e23b663db187e0e2a7ba4396023221c653b7d4a75967d3ba230719",
        }
        for relative, digest in expected.items():
            self.assertEqual(M19.sha256_bytes(M19.read_source(ROOT, relative)), digest)

    def test_self_test_is_deterministic_and_complete(self) -> None:
        first = M19.build_self_test()
        second = M19.build_self_test()
        self.assertEqual(M19.canonical_json_bytes(first), M19.canonical_json_bytes(second))
        self.assertEqual(first["case_count"], 20)
        self.assertEqual(first["passed_count"], 20)
        self.assertEqual(first["failed_count"], 0)
        self.assertEqual(first["overall_status"], "PASS")

    def test_upstream_telemetry_contour_is_reference_only(self) -> None:
        context = M19._upstream_telemetry_context(ROOT)
        upstream = context["m15_semantic_reference"]
        self.assertEqual(upstream["correlation_status"], "not_evaluated_in_m19")
        self.assertEqual(upstream["availability"], "external_upstream_canonical_artifacts")
        self.assertEqual(len(upstream["artifacts"]), 3)
        self.assertEqual(context["physical_measurement"]["availability"], "not_in_scope")


class M19CommittedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_context = M19.SchemaContext(ROOT)
        cls.committed = M19.records_from_committed(ROOT)
        cls.payloads = {
            path: M19.parse_json_bytes(raw, path)
            for path, raw in cls.committed.items()
            if path.endswith(".json")
        }

    def test_exact_committed_artifact_set_is_present(self) -> None:
        observed = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "artifacts/m19").rglob("*")
            if path.is_file()
        }
        self.assertEqual(observed, set(M19.GENERATED_PATHS))

    def test_committed_json_is_canonical(self) -> None:
        for path, payload in self.payloads.items():
            self.assertEqual(M19.canonical_json_bytes(payload), self.committed[path], path)

    def test_committed_instances_validate_against_registered_schemas(self) -> None:
        bindings = {
            M19.RTL_TRACE: M19.RTL_TRACE_SCHEMA,
            M19.FPGA_TRACE: M19.FPGA_TRACE_SCHEMA,
            M19.RTL_ZERO: M19.ZERO_SCHEMA,
            M19.FPGA_ZERO: M19.ZERO_SCHEMA,
            M19.RTL_MANIFEST: M19.LAYER_MANIFEST_SCHEMA,
            M19.FPGA_MANIFEST: M19.LAYER_MANIFEST_SCHEMA,
            M19.MANIFEST: M19.MANIFEST_SCHEMA,
            M19.QUALIFICATION: M19.QUALIFICATION_SCHEMA,
        }
        for path, identifier in bindings.items():
            self.schema_context.validate(identifier, self.payloads[path], path)

    def test_rtl_and_fpga_record_counts_and_epochs_are_exact(self) -> None:
        rtl = self.payloads[M19.RTL_TRACE]
        fpga = self.payloads[M19.FPGA_TRACE]
        self.assertEqual(len(rtl["records"]), 96)
        self.assertEqual(len(fpga["records"]), 4)
        self.assertEqual(
            [(item["mode"], item["record_count"]) for item in rtl["execution_epochs"]],
            [("free", 16), ("7/1", 64), ("1/7", 16)],
        )
        self.assertEqual(
            [(item["mode"], item["record_count"]) for item in fpga["execution_epochs"]],
            [("free", 3), ("1/7", 1)],
        )

    def test_tick_sequence_and_scheduler_relations_are_exact(self) -> None:
        for path in (M19.RTL_TRACE, M19.FPGA_TRACE):
            trace = self.payloads[path]
            for sequence, record in enumerate(trace["records"]):
                scheduler = record["scheduler"]
                self.assertEqual(record["sequence"], sequence)
                self.assertEqual(scheduler["ticks_after"], scheduler["ticks_before"] + 1)
                self.assertEqual(sum(scheduler["counters_after"].values()), scheduler["ticks_after"])
                self.assertEqual(
                    scheduler["state"],
                    M19._expected_scheduler_state(scheduler["mode"], scheduler["ticks_before"]),
                )

    def test_ternary_domain_and_active_neutral_routes_are_exact(self) -> None:
        for path in (M19.RTL_TRACE, M19.FPGA_TRACE):
            for record in self.payloads[path]["records"]:
                for field in (
                    "retained_state_before",
                    "retained_state_after",
                    "pending_route_before",
                    "pending_route_after",
                    "phase_derived_targets",
                ):
                    self.assertTrue(set(record[field]).issubset({-1, 0, 1}))
                for left, right in zip(
                    record["retained_state_before"],
                    record["retained_state_after"],
                    strict=True,
                ):
                    self.assertNotIn((left, right), {(-1, 1), (1, -1)})

    def test_request_lane_dispositions_are_complete(self) -> None:
        for path in (M19.RTL_TRACE, M19.FPGA_TRACE):
            for record in self.payloads[path]["records"]:
                self.assertEqual([item["lane"] for item in record["requests"]], [0, 1])
                for lane in record["requests"]:
                    self.assertFalse(lane["accepted"] and lane["rejected"])
                    self.assertEqual(lane["valid"], lane["accepted"] or lane["rejected"])

    def test_capacity_and_switch_load_relations_are_exact(self) -> None:
        for path in (M19.RTL_TRACE, M19.FPGA_TRACE):
            for record in self.payloads[path]["records"]:
                capacity = record["transition_capacity"]
                telemetry = record["telemetry"]
                self.assertEqual(capacity["capacity_limit"], 2)
                self.assertEqual(
                    capacity["capacity_remaining"],
                    2 - capacity["accepted_changes"],
                )
                self.assertEqual(telemetry["switch_load_numerator"], capacity["accepted_changes"])
                self.assertEqual(telemetry["switch_load_q16"], capacity["accepted_changes"] * 8192)

    def test_zero_event_and_invariant_records_are_complete(self) -> None:
        for path in (M19.RTL_TRACE, M19.FPGA_TRACE):
            for record in self.payloads[path]["records"]:
                self.assertEqual(record["events"]["actual_direct_events"], 0)
                self.assertEqual(record["events"]["reserved_state_events"], 0)
                self.assertEqual(record["events"]["queue_overflow_events"], 0)
                self.assertTrue(record["invariants"]["all_pass"])
                self.assertEqual(len(record["invariants"]["flags"]), 10)

    def test_raw_trace_digests_and_record_digests_are_exact(self) -> None:
        for layer in ("rtl", "fpga_preparation"):
            config = M19.LAYER_CONFIG[layer]
            trace = self.payloads[config["trace_path"]]
            self.assertEqual(trace["raw_trace"]["raw_sha256"], M19.sha256_bytes(self.committed[config["raw_path"]]))
            self.assertEqual(
                trace["summary"]["record_digest"],
                M19.sha256_bytes(M19.canonical_json_bytes(trace["records"])),
            )

    def test_manifests_bind_current_sources_and_artifacts(self) -> None:
        manifest = self.payloads[M19.MANIFEST]
        self.assertEqual(manifest["artifact_count"], 8)
        self.assertEqual(manifest["source_count"], 28)
        self.assertEqual(manifest["artifact_set_digest"], M19._artifact_set_digest(manifest["artifacts"]))
        self.assertEqual(manifest["source_set_digest"], M19._artifact_set_digest(manifest["sources"]))
        for record in manifest["sources"]:
            self.assertEqual(M19.file_record(ROOT, record["path"], record["role"]), record)

    def test_qualification_record_is_complete(self) -> None:
        qualification = self.payloads[M19.QUALIFICATION]
        self.assertEqual(qualification["check_count"], 37)
        self.assertEqual(qualification["passed_count"], 37)
        self.assertEqual(qualification["failed_count"], 0)
        self.assertEqual(qualification["overall_status"], "PASS")
        self.assertEqual(len({item["check_id"] for item in qualification["checks"]}), 37)

    def test_reconstruction_is_byte_identical(self) -> None:
        reconstructed = M19.reconstruct_from_committed(ROOT)
        self.assertEqual(set(reconstructed), set(self.committed))
        for path in M19.GENERATED_PATHS:
            self.assertEqual(reconstructed[path], self.committed[path], path)

    def test_verify_reports_complete_pass(self) -> None:
        result = M19.verify_committed(ROOT)
        self.assertEqual(result["check_count"], 12)
        self.assertEqual(result["passed_count"], 12)
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["overall_status"], "PASS")
        self.assertTrue(result["qualification_record_match"])


class M19NegativeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = M19.SchemaContext(ROOT)
        cls.rtl = M19.parse_json_bytes(M19.read_source(ROOT, M19.RTL_TRACE), M19.RTL_TRACE)

    def test_schema_rejects_reserved_ternary_state(self) -> None:
        altered = copy.deepcopy(self.rtl)
        altered["records"][0]["retained_state_after"][0] = 2
        with self.assertRaises(M19.ContractError):
            self.context.validate(M19.RTL_TRACE_SCHEMA, altered, "reserved-state fixture")

    def test_schema_rejects_missing_required_field(self) -> None:
        altered = copy.deepcopy(self.rtl)
        del altered["records"][0]["scheduler"]
        with self.assertRaises(M19.ContractError):
            self.context.validate(M19.RTL_TRACE_SCHEMA, altered, "missing-field fixture")

    def test_schema_rejects_additional_field(self) -> None:
        altered = copy.deepcopy(self.rtl)
        altered["records"][0]["physical_watts"] = 1
        with self.assertRaises(M19.ContractError):
            self.context.validate(M19.RTL_TRACE_SCHEMA, altered, "additional-field fixture")

    def test_schema_rejects_measurement_contour_substitution(self) -> None:
        altered = copy.deepcopy(self.rtl)
        altered["measurement_contours"]["physical_measurement"]["availability"] = "measured"
        with self.assertRaises(M19.ContractError):
            self.context.validate(M19.RTL_TRACE_SCHEMA, altered, "contour fixture")

    def test_raw_parser_rejects_reserved_scheduler_code(self) -> None:
        line = M19._synthetic_raw_line().split("|")
        line[5] = "3"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.log"
            path.write_text("|".join(line) + "\n", encoding="utf-8")
            _, records = M19._raw_lines(path, "rtl")
            raw = M19._canonical_raw(["|".join(line)])
            with self.assertRaises(M19.ContractError):
                M19.build_trace(ROOT, "rtl", raw, records * 96)

    def test_raw_parser_rejects_wrong_field_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.log"
            path.write_text("FRP_M19|1|rtl|0\n", encoding="utf-8")
            with self.assertRaises(M19.ContractError):
                M19._raw_lines(path, "rtl")

    def test_output_root_rejects_repository_overlap(self) -> None:
        with self.assertRaises(M19.SafetyError):
            M19.output_root(ROOT / "artifacts", ROOT, False)

    def test_cli_rejects_incomplete_generation_arguments(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--generate"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("configuration error", completed.stderr)


if __name__ == "__main__":
    unittest.main()
