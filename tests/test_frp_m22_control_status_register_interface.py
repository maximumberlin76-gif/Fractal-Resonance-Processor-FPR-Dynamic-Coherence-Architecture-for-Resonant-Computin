"""Tests for FRP M22 deterministic control/status/register realization."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import frp_m22_control_status_register_interface as M22


ROOT = Path(__file__).resolve().parents[1]


class M22ControlStatusRegisterTests(unittest.TestCase):
    """Exercise the complete register contract, traces, schemas, and closure."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.interface = M22.build_interface(ROOT, M22.EXPECTED_M21_COMMIT)
        cls.traces = M22.build_traces(cls.interface, M22.EXPECTED_M21_COMMIT)
        cls.outputs = M22.build_outputs(ROOT, M22.EXPECTED_M21_COMMIT)
        cls.manifest = json.loads(cls.outputs[M22.MANIFEST_ARTIFACT])
        cls.qualification = json.loads(cls.outputs[M22.QUALIFICATION_ARTIFACT])
        cls.schemas = M22.SchemaContext(ROOT)

    @staticmethod
    def stage(model: M22.CsrModel, lane: int, cell: int, target: int) -> None:
        for address, data in (
            (M22.ADDR["REQUEST_LANE_SELECT"], lane),
            (M22.ADDR["REQUEST_CELL_INDEX"], cell),
            (M22.ADDR["REQUEST_TARGET"], M22.semantic_to_encoding(target)),
            (M22.ADDR["REQUEST_VALID"], 1),
        ):
            result = model.transact("write", address, data)
            if result["error"]:
                raise AssertionError(result)

    def test_release_and_source_commit_are_exact(self) -> None:
        self.assertEqual(M22.VERSION, "2.4.0")
        self.assertEqual(
            M22.EXPECTED_M21_COMMIT,
            "759ee446adf028ca135c75ca38388c26e911aa68",
        )
        self.assertEqual(
            self.interface["source_release"],
            "FRP v2.3.0 / M21 parameterized qualification boundary",
        )

    def test_upstream_source_digests_are_exact(self) -> None:
        self.assertEqual(
            self.interface["source_digests"] | {},
            {
                "m16_core_sha256": "3b94f5caa5ee28da0060a38dd9b4ba4605ef5f86ac93f5425967e515ff1ebd23",
                "m16_package_sha256": "c20fe071e7c91b60ca0411b75d4cf762112d51abbd49dc2a5667d1d8c5d49152",
                "m21_dimensions_sha256": "fcfac50848deedd6ef90bc0f4184e325931e0070960cbe61fd2175b2f6d0b348",
                "m21_matrix_sha256": "0a2ebfe3fe2372727e46e7070af14fbee95a1abf26bae97d47c8f2f6f1b9f9f1",
                "m21_qualification_sha256": "cd98499a63d84c9fb3970cf12c7828f9ebe584986cd076829de94905ba11aba0",
                "rtl_interface_sha256": M22.sha256_bytes((ROOT / M22.RTL_INTERFACE).read_bytes()),
                "rtl_package_sha256": M22.sha256_bytes((ROOT / M22.RTL_PACKAGE).read_bytes()),
                "rtl_testbench_sha256": M22.sha256_bytes((ROOT / M22.RTL_TESTBENCH).read_bytes()),
            },
        )

    def test_parameter_profiles_are_exact_and_ordered(self) -> None:
        self.assertEqual(
            self.interface["parameter_profiles"],
            [
                {"profile_id": "cells-8-lanes-2", "cell_count": 8, "request_lanes": 2, "capacity_limit": 2, "transition_fraction_denominator": 4, "transition_fraction_numerator": 1},
                {"profile_id": "cells-16-lanes-4", "cell_count": 16, "request_lanes": 4, "capacity_limit": 4, "transition_fraction_denominator": 4, "transition_fraction_numerator": 1},
                {"profile_id": "cells-32-lanes-8", "cell_count": 32, "request_lanes": 8, "capacity_limit": 8, "transition_fraction_denominator": 4, "transition_fraction_numerator": 1},
            ],
        )

    def test_register_names_offsets_and_count_are_exact(self) -> None:
        registers = self.interface["registers"]
        self.assertEqual(self.interface["register_count"], 26)
        self.assertEqual([item["name"] for item in registers], list(M22.ADDR))
        self.assertEqual([item["offset"] for item in registers], list(M22.ADDR.values()))
        self.assertEqual([item["address"] for item in registers], [f"0x{value:02X}" for value in M22.ADDR.values()])

    def test_register_offsets_are_unique_aligned_and_dense(self) -> None:
        offsets = [item["offset"] for item in self.interface["registers"]]
        self.assertEqual(len(offsets), len(set(offsets)))
        self.assertTrue(all(offset % 4 == 0 for offset in offsets))
        self.assertEqual(offsets, list(range(0, 0x68, 4)))

    def test_register_access_partition_is_exact(self) -> None:
        actual = {item["name"]: item["access"] for item in self.interface["registers"]}
        self.assertEqual(actual, M22.ACCESS)
        self.assertEqual([name for name, access in actual.items() if access == "WO"], ["CONTROL"])
        self.assertEqual(sum(access == "RW" for access in actual.values()), 6)
        self.assertEqual(sum(access == "RO" for access in actual.values()), 19)

    def test_register_resets_and_widths_are_complete(self) -> None:
        for register in self.interface["registers"]:
            self.assertEqual(register["reset_value"], 0)
            self.assertEqual(register["reset_value_hex"], "0x00000000")
            self.assertEqual(register["width_bits"], 32)
            self.assertGreaterEqual(len(register["fields"]), 1)

    def test_control_commands_and_fields_are_exact(self) -> None:
        self.assertEqual(
            [(item["command"], item["mask"]) for item in self.interface["control_commands"]],
            [("tick", 1), ("clear_counters", 2), ("clear_requests", 4)],
        )
        control = self.interface["registers"][0]
        self.assertEqual([(item["name"], item["lsb"], item["access"]) for item in control["fields"]], [("tick", 0, "W1P"), ("clear_counters", 1, "W1P"), ("clear_requests", 2, "W1P")])

    def test_status_field_layout_is_exact(self) -> None:
        status = next(item for item in self.interface["registers"] if item["name"] == "STATUS")
        self.assertEqual(
            [(field["name"], field["lsb"]) for field in status["fields"]],
            [("ready", 0), ("capacity_exhausted", 1), ("request_accepted", 2), ("request_rejected", 3), ("pending_active", 4), ("invariant_failure", 5), ("actual_direct_nonzero", 6), ("reserved_state_nonzero", 7), ("queue_overflow_nonzero", 8)],
        )

    def test_invariant_field_layout_is_exact(self) -> None:
        flags = next(item for item in self.interface["registers"] if item["name"] == "INVARIANT_FLAGS")
        self.assertEqual([item["name"] for item in flags["fields"]], list(M22.INVARIANT_NAMES))
        self.assertEqual([item["lsb"] for item in flags["fields"]], list(range(10)))

    def test_balanced_ternary_encoding_is_exact(self) -> None:
        encodings = self.interface["encodings"]
        self.assertEqual(encodings["active_neutral_state"], 0)
        self.assertEqual(encodings["reserved_ternary_encoding"], 2)
        self.assertEqual(encodings["balanced_ternary"], list(M22.TERNARY_ENCODINGS))
        self.assertEqual([item["semantic_value"] for item in encodings["balanced_ternary"]], [-1, 0, 1])

    def test_scheduler_encoding_is_exact(self) -> None:
        encodings = self.interface["encodings"]
        self.assertEqual(encodings["reserved_scheduler_encoding"], 3)
        self.assertEqual(encodings["scheduler_modes"], list(M22.SCHEDULER_ENCODINGS))

    def test_bus_timing_and_signals_are_exact(self) -> None:
        bus = self.interface["bus"]
        self.assertEqual((bus["address_bits"], bus["data_bits"], bus["alignment_bytes"]), (8, 32, 4))
        self.assertEqual(bus["byte_order"], "little-endian")
        self.assertEqual(bus["request_signals"], ["csr_valid", "csr_write", "csr_addr", "csr_wdata"])
        self.assertEqual(bus["response_signals"], ["csr_ready", "csr_error", "csr_rdata"])

    def test_invalid_access_policy_is_complete_and_exact(self) -> None:
        policy = self.interface["invalid_access_policy"]
        self.assertTrue(policy["no_side_effects"])
        self.assertEqual(policy["invalid_read_data"], 0)
        self.assertEqual(
            policy["rejected_classes"],
            ["misaligned_address", "unmapped_address", "read_from_WO", "write_to_RO", "invalid_control_command", "reserved_scheduler_encoding", "out_of_range_lane", "out_of_range_cell", "reserved_ternary_encoding", "invalid_boolean_payload"],
        )

    def test_rtl_sources_are_bound_and_have_required_contract_tokens(self) -> None:
        self.assertEqual(self.interface["rtl"]["interface_module"], "frp_m22_control_status_register_interface")
        M22.validate_rtl_interface(ROOT)
        package = (ROOT / M22.RTL_PACKAGE).read_text()
        self.assertIn("FRP_M22_REGISTER_COUNT = 26", package)
        self.assertIn("FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS = 8'h64", package)

    def test_model_reset_state_is_exact(self) -> None:
        model = M22.CsrModel(16, 4)
        snapshot = model.snapshot()
        self.assertEqual(snapshot["state"], [0] * 16)
        self.assertEqual(snapshot["pending"], [0] * 16)
        self.assertEqual(snapshot["request_valid"], [0] * 4)
        self.assertEqual(snapshot["ticks_recorded"], 0)
        self.assertEqual(model.transact("read", M22.ADDR["STATUS"])["read_data"], 1)

    def test_model_scheduler_read_write_is_deterministic(self) -> None:
        model = M22.CsrModel(16, 4)
        for mode in (1, 2, 0):
            self.assertFalse(model.transact("write", M22.ADDR["SCHEDULER_MODE"], mode)["error"])
            self.assertEqual(model.transact("read", M22.ADDR["SCHEDULER_MODE"])["read_data"], mode)
            self.assertEqual(model.transact("read", M22.ADDR["SCHEDULER_MODE_ACTIVE"])["read_data"], mode)

    def test_model_selected_lane_staging_is_isolated(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 3, 11, -1)
        self.stage(model, 0, 2, 1)
        self.assertEqual(model.request_cells, [2, 0, 0, 11])
        self.assertEqual(model.request_targets, [1, 0, 0, -1])
        self.assertEqual(model.request_valid, [1, 0, 0, 1])

    def test_clear_requests_command_clears_only_valid_bits(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 2, 7, -1)
        before = (list(model.request_cells), list(model.request_targets))
        self.assertFalse(model.transact("write", M22.ADDR["CONTROL"], 4)["error"])
        self.assertEqual(model.request_valid, [0] * 4)
        self.assertEqual((model.request_cells, model.request_targets), before)

    def test_tick_accepts_request_and_auto_clears_valid(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 0, 0, 1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual(model.state[0], 1)
        self.assertEqual(model.request_valid, [0] * 4)
        self.assertEqual(model.request_accept, 1)
        self.assertEqual(model.ticks_recorded, 1)

    def test_positive_to_negative_transition_routes_through_zero(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 0, 0, 1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.stage(model, 0, 0, -1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual((model.state[0], model.pending[0]), (0, -1))
        self.assertEqual((model.requested_direct_events, model.prevented_direct_events, model.neutral_routed_events), (1, 1, 1))
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual((model.state[0], model.pending[0]), (-1, 0))

    def test_negative_to_positive_transition_routes_through_zero(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 0, 0, -1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.stage(model, 0, 0, 1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual((model.state[0], model.pending[0]), (0, 1))
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual((model.state[0], model.pending[0]), (1, 0))

    def test_transition_capacity_is_exact_for_every_profile(self) -> None:
        for spec in M22.PROFILE_SPECS:
            model = M22.CsrModel(spec["cell_count"], spec["request_lanes"])
            for lane in range(spec["request_lanes"]):
                self.stage(model, lane, lane, 1)
            model.transact("write", M22.ADDR["CONTROL"], 1)
            self.assertEqual(model.accepted_changes, spec["request_lanes"])
            self.assertEqual(model.capacity_remaining, 0)
            self.assertEqual(model.capacity_exhausted, 1)

    def test_duplicate_cell_request_is_rejected_deterministically(self) -> None:
        model = M22.CsrModel(16, 4)
        self.stage(model, 0, 4, 1)
        self.stage(model, 1, 4, -1)
        model.transact("write", M22.ADDR["CONTROL"], 1)
        self.assertEqual(model.request_accept, 0b0001)
        self.assertEqual(model.request_reject, 0b0010)
        self.assertEqual(model.state[4], 1)

    def test_all_invalid_access_classes_are_rejected_without_side_effects(self) -> None:
        model = M22.CsrModel(16, 4)
        accesses = [("read", M22.ADDR["CONTROL"], 0), ("read", 1, 0), ("read", 0x68, 0), ("write", M22.ADDR["STATUS"], 0), ("write", M22.ADDR["CONTROL"], 0), ("write", M22.ADDR["CONTROL"], 3), ("write", M22.ADDR["SCHEDULER_MODE"], 3), ("write", M22.ADDR["REQUEST_LANE_SELECT"], 4), ("write", M22.ADDR["REQUEST_CELL_INDEX"], 16), ("write", M22.ADDR["REQUEST_TARGET"], 2), ("write", M22.ADDR["REQUEST_VALID"], 2), ("write", M22.ADDR["OBSERVE_CELL_INDEX"], 16)]
        before = model.snapshot()
        for operation, address, data in accesses:
            self.assertTrue(model.transact(operation, address, data)["error"])
            self.assertEqual(model.snapshot(), before)

    def test_invalid_reads_return_zero_and_ready_with_error(self) -> None:
        model = M22.CsrModel(8, 2)
        for address in (M22.ADDR["CONTROL"], 1, 0x68):
            result = model.transact("read", address)
            self.assertTrue(result["ready"])
            self.assertTrue(result["error"])
            self.assertEqual(result["read_data"], 0)

    def test_trace_profiles_counts_and_negative_coverage_are_exact(self) -> None:
        self.assertEqual(self.traces["profile_count"], 3)
        self.assertEqual(self.traces["invalid_access_count"], 36)
        self.assertEqual([item["profile_id"] for item in self.traces["profiles"]], [item["profile_id"] for item in M22.PROFILE_SPECS])
        for profile in self.traces["profiles"]:
            self.assertEqual(profile["invalid_access_count"], 12)
            self.assertEqual(profile["transaction_count"], len(profile["transactions"]))

    def test_trace_sequences_and_all_nested_digests_are_exact(self) -> None:
        for profile in self.traces["profiles"]:
            self.assertEqual([item["sequence"] for item in profile["transactions"]], list(range(profile["transaction_count"])))
            for transaction in profile["transactions"]:
                candidate = {key: value for key, value in transaction.items() if key != "transaction_digest"}
                self.assertEqual(transaction["transaction_digest"], M22.object_digest(candidate))
            candidate = {key: value for key, value in profile.items() if key != "trace_digest"}
            self.assertEqual(profile["trace_digest"], M22.object_digest(candidate))
        candidate = {key: value for key, value in self.traces.items() if key != "trace_set_digest"}
        self.assertEqual(self.traces["trace_set_digest"], M22.object_digest(candidate))

    def test_trace_forbidden_event_registers_are_always_zero(self) -> None:
        forbidden = {"ACTUAL_DIRECT_EVENTS", "RESERVED_STATE_EVENTS", "QUEUE_OVERFLOW_EVENTS"}
        for profile in self.traces["profiles"]:
            reads = [item for item in profile["transactions"] if item["operation"] == "read" and item["register"] in forbidden]
            self.assertEqual({item["read_data"] for item in reads}, {0})
            invariant_reads = [item for item in profile["transactions"] if item["operation"] == "read" and item["register"] == "INVARIANT_FLAGS"]
            self.assertEqual({item["read_data"] for item in invariant_reads}, {0x3FF})

    def test_generation_is_byte_stable(self) -> None:
        first = M22.build_outputs(ROOT, M22.EXPECTED_M21_COMMIT)
        second = M22.build_outputs(ROOT, M22.EXPECTED_M21_COMMIT)
        self.assertEqual(first, second)
        self.assertEqual(first, self.outputs)

    def test_all_outputs_validate_against_formal_schemas(self) -> None:
        mapping = {M22.INTERFACE_ARTIFACT: M22.INTERFACE_SCHEMA, M22.TRACE_ARTIFACT: M22.TRACE_SCHEMA, M22.MANIFEST_ARTIFACT: M22.MANIFEST_SCHEMA, M22.QUALIFICATION_ARTIFACT: M22.QUALIFICATION_SCHEMA}
        for path, schema in mapping.items():
            self.schemas.validate(schema, json.loads(self.outputs[path]), path)

    def test_schema_registry_is_complete_and_exact(self) -> None:
        registry = json.loads((ROOT / M22.REGISTRY_PATH).read_text())
        self.assertEqual(registry["version"], "2.4.0")
        self.assertEqual([item["schema"] for item in registry["records"]], list(M22.SCHEMA_PATHS))
        self.assertEqual([item["path"] for item in registry["records"]], list(M22.SCHEMA_PATHS.values()))
        self.assertEqual({item["urn"] for item in registry["records"]}, {f"urn:frp:schema:{name}" for name in M22.SCHEMA_PATHS})

    def test_manifest_covers_every_source_and_generated_evidence_file(self) -> None:
        source_paths = [item["path"] for item in self.manifest["sources"]]
        self.assertEqual(source_paths, sorted((*M22.TECHNICAL_SOURCE_PATHS, *M22.UPSTREAM_SOURCE_PATHS)))
        self.assertEqual([item["path"] for item in self.manifest["artifacts"]], [M22.INTERFACE_ARTIFACT, M22.TRACE_ARTIFACT])
        for source in self.manifest["sources"]:
            self.assertEqual(source["raw_sha256"], M22.sha256_bytes((ROOT / source["path"]).read_bytes()))

    def test_qualification_is_exact_complete_and_unique(self) -> None:
        record = self.qualification
        self.assertEqual((record["check_count"], record["passed_count"], record["failed_count"]), (60, 60, 0))
        self.assertEqual(record["overall_status"], "PASS")
        self.assertEqual(len({item["check_id"] for item in record["checks"]}), 60)
        self.assertEqual({item["status"] for item in record["checks"]}, {"PASS"})
        self.assertEqual(record["manifest_digest"], M22.object_digest(self.manifest))

    def test_wrong_commit_and_unsafe_paths_are_rejected(self) -> None:
        with self.assertRaises(M22.ContractError):
            M22.validate_source_commit("0" * 40)
        for value in ("/absolute", "../escape", "a/../b", "a\\b"):
            with self.assertRaises(M22.SafetyError):
                M22.safe_relative_path(value)

    def test_committed_artifacts_are_byte_exact_and_complete_verification_passes(self) -> None:
        for path, raw in self.outputs.items():
            self.assertEqual((ROOT / path).read_bytes(), raw)
        result = M22.verify(ROOT, M22.EXPECTED_M21_COMMIT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["artifact_count"], 4)


if __name__ == "__main__":
    unittest.main()
