# SPDX-License-Identifier: Apache-2.0
"""Tests for the FRP M17 published-artifact inventory boundary."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "frp_m17_publication_inventory.py"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import frp_m17_publication_inventory as inventory


EXPECTED_COMMITTED_JSON = {
    "benchmarks/architecture_comparison/profiles/workload_profile_v1.json": None,
    "benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json": (
        "frp.benchmark.normalized_cost_profile.v1"
    ),
    "benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json": (
        "frp.benchmark.thermal_proxy_profile.v1"
    ),
    "benchmarks/architecture_comparison/profiles/"
    "hardware_sensitivity_cost_profile_v1.json": (
        "frp.benchmark.hardware_sensitivity_cost_profile.v1"
    ),
    "benchmarks/architecture_comparison/results/reference_comparison_seed_76.json": (
        "frp.benchmark.architecture_comparison.v1"
    ),
    "benchmarks/architecture_comparison/results/"
    "reference_comparison_seed_76_hardware_sensitivity_v1.json": (
        "frp.benchmark.hardware_sensitivity_comparison.v1"
    ),
}

EXPECTED_M15_EXPORT_SCHEMAS = {
    "frp.m15.fixed_point_interface_profile.v1.7.0",
    "frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0",
    "frp.m15.quantized_reference_shadow_model.v1.7.0",
    "frp.m15.cycle_exact_reference_trace.v1.7.0",
    "frp.m15.rtl_comparison_vector_package.v1.7.0",
    "frp.m15.systemverilog_testbench_interface_map.v1.7.0",
    "frp.m15.synthesizable_rtl_reference_core.v1.7.0",
    "frp.m15.rtl_assertion_correlation_harness.v1.7.0",
    "frp.m15.reference_rtl_equivalence_report.v1.7.0",
    "frp.m15.qualification_closure_manifest.v1.7.0",
}

EXPECTED_SCHEMA_IDENTIFIERS = sorted(
    {
        "frp.structured_output.v1.7.0",
        "frp.m3.benchmark_matrix.v1.7.0",
        "frp.benchmark.normalized_cost_profile.v1",
        "frp.benchmark.thermal_proxy_profile.v1",
        "frp.benchmark.hardware_sensitivity_cost_profile.v1",
        "frp.benchmark.architecture_comparison.v1",
        "frp.benchmark.hardware_sensitivity_comparison.v1",
        *EXPECTED_M15_EXPORT_SCHEMAS,
    }
)

EXPECTED_M15_VECTOR_MEMBERS = (
    "frp_m15_cell_trace.vec",
    "frp_m15_full_correlation_vectors.vec",
    "frp_m15_kernel_vectors.vec",
    "frp_m15_pending_routes.trace",
    "frp_m15_reference_preload.json",
    "frp_m15_scheduler_1_7_vectors.vec",
    "frp_m15_scheduler_7_1_vectors.vec",
    "frp_m15_scheduler_free_vectors.vec",
    "frp_m15_sha256_manifest.json",
    "frp_m15_trig_lut_q30.vec",
)

EXPECTED_M16_RTL_MEMBERS = {
    "frp_m16_toolchain.log",
    "frp_m16_sources.sha256",
    "frp_m16_build.log",
    "frp_m16_execution.log",
    "frp_m16_qualification.txt",
}

EXPECTED_M16_FPGA_MEMBERS = {
    "frp_m16_fpga_toolchain.log",
    "frp_m16_fpga_sources.sha256",
    "frp_m16_fpga_top_lint.log",
    "frp_m16_fpga_build.log",
    "frp_m16_fpga_execution.log",
    "frp_m16_fpga_qualification.txt",
}

EXPECTED_DOCUMENTATION_PATHS = {
    "docs/m17_published_artifact_integration_contract.md",
    "docs/output_schema.md",
    "docs/benchmark_matrix.md",
    "docs/m15_implementation_mapping_domain_interface_qualification_closure.md",
    "FRP_VALIDATION_INDEX_v1_8_0.md",
    "docs/m16_qualification_manifest.md",
    "docs/m16_qualification_index.md",
    "docs/m16_public_status_snapshot.md",
    "rtl/m16/ARTIFACTS.md",
    "rtl/m16/SIMULATION_TRANSCRIPT.md",
    "rtl/m16/CLOSURE.md",
    "fpga/m16/SIMULATION_TRANSCRIPT.md",
    "fpga/m16/CLOSURE.md",
}

EXPECTED_MISSING_RECORDS = {
    "missing.formal_json_schemas",
    "missing.committed_m15_canonical_artifacts",
    "missing.canonical_csv_tsv_artifacts",
    "missing.machine_readable_m16_artifacts",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class M17PublishedArtifactInventoryTests(unittest.TestCase):
    """Validate the M17 inventory without executing artifact producers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = inventory.build_inventory(REPO_ROOT)
        cls.records = cls.payload["records"]

    def test_inventory_source_exists_and_is_nonempty(self) -> None:
        self.assertTrue(SCRIPT_PATH.is_file())
        self.assertGreater(SCRIPT_PATH.stat().st_size, 0)

    def test_inventory_identity_is_exact(self) -> None:
        self.assertEqual(
            self.payload["schema"],
            "frp.m17.published_artifact_inventory.v1.9.0",
        )
        self.assertEqual(
            self.payload["kind"],
            "published_artifact_inventory",
        )
        self.assertEqual(self.payload["version"], "1.9.0")
        self.assertEqual(
            self.payload["milestone"],
            "M17 — Published Artifact Integration Contract",
        )
        self.assertEqual(self.payload["milestone_state"], "planned")
        self.assertEqual(self.payload["baseline_release"], "FRP v1.8.0")
        self.assertEqual(
            self.payload["semantic_reference"],
            "frp_prototype_v1_7_0.py",
        )
        self.assertEqual(self.payload["source_authority"], "frp")

    def test_integration_direction_is_one_way(self) -> None:
        self.assertEqual(
            self.payload["integration_direction"],
            "frp_to_published_artifacts_to_downstream_consumers",
        )

    def test_canonical_ternary_domain_and_routes_are_exact(self) -> None:
        self.assertEqual(
            self.payload["canonical_ternary_domain"],
            [-1, 0, 1],
        )
        self.assertEqual(
            self.payload["canonical_opposite_polarity_routes"],
            [[-1, 0, 1], [1, 0, -1]],
        )
        self.assertNotIn(
            '"+1"',
            inventory.inventory_json(self.payload),
        )

    def test_records_are_lexicographically_ordered_and_unique(self) -> None:
        record_ids = [
            record["record_id"]
            for record in self.records
        ]
        self.assertEqual(record_ids, sorted(record_ids))
        self.assertEqual(len(record_ids), len(set(record_ids)))

    def test_inventory_summary_counts_are_exact(self) -> None:
        summary = self.payload["summary"]
        self.assertEqual(summary["total_records"], 63)
        self.assertEqual(
            summary["repository_committed_json_count"],
            6,
        )
        self.assertEqual(summary["m15_export_schema_count"], 10)
        self.assertEqual(
            summary["m15_vector_package_member_count"],
            10,
        )
        self.assertEqual(summary["m16_workflow_member_count"], 11)
        self.assertEqual(summary["documentation_only_count"], 13)
        self.assertEqual(summary["planned_unavailable_count"], 4)

    def test_publication_state_counts_are_exact(self) -> None:
        self.assertEqual(
            self.payload["summary"]["publication_state_counts"],
            {
                "documentation_only": 13,
                "planned_unavailable": 4,
                "producer_defined": 29,
                "release_archived": 0,
                "repository_committed": 6,
                "workflow_retained": 11,
            },
        )

    def test_committed_json_paths_and_schema_bindings_are_exact(
        self,
    ) -> None:
        committed = {
            record["repository_path"]: record.get(
                "schema_identifier"
            )
            for record in self.records
            if record["publication_state"] == "repository_committed"
        }
        self.assertEqual(committed, EXPECTED_COMMITTED_JSON)

    def test_committed_json_raw_provenance_matches_source_bytes(
        self,
    ) -> None:
        committed = [
            record
            for record in self.records
            if record["publication_state"] == "repository_committed"
        ]

        for record in committed:
            with self.subTest(record_id=record["record_id"]):
                path = REPO_ROOT / record["repository_path"]
                self.assertEqual(
                    record["source_filename"],
                    path.name,
                )
                self.assertEqual(
                    record["byte_length"],
                    path.stat().st_size,
                )
                self.assertEqual(
                    record["raw_sha256"],
                    sha256(path),
                )
                self.assertTrue(record["canonical"])

    def test_schema_free_workload_profile_uses_path_identity(
        self,
    ) -> None:
        workload = next(
            record
            for record in self.records
            if (
                record["record_id"]
                == "comparative.profile.workload.v1"
            )
        )
        self.assertEqual(
            workload["identity_basis"],
            "exact_path_and_role",
        )
        self.assertNotIn("schema_identifier", workload)

    def test_schema_identifier_registry_is_exact(self) -> None:
        self.assertEqual(
            self.payload["schema_identifiers"],
            EXPECTED_SCHEMA_IDENTIFIERS,
        )
        self.assertEqual(
            self.payload["summary"]["schema_identifier_count"],
            17,
        )
        self.assertTrue(
            all(
                not schema.startswith("frp.m16.")
                for schema in self.payload["schema_identifiers"]
            )
        )

    def test_m15_export_schema_set_is_exact(self) -> None:
        exports = [
            record
            for record in self.records
            if record["record_id"].startswith("m15.export.")
        ]
        self.assertEqual(len(exports), 10)
        self.assertEqual(
            {
                record["schema_identifier"]
                for record in exports
            },
            EXPECTED_M15_EXPORT_SCHEMAS,
        )
        self.assertTrue(
            all(
                record["artifact_kind"]
                for record in exports
            )
        )

    def test_m15_producer_and_workflow_bindings_are_exact(
        self,
    ) -> None:
        produced = [
            record
            for record in self.records
            if record["publication_state"] == "producer_defined"
        ]
        self.assertEqual(len(produced), 29)
        self.assertTrue(
            all(
                record["producer_path"]
                == "frp_prototype_v1_7_0.py"
                for record in produced
            )
        )
        self.assertTrue(
            all(
                record["producer_version"] == "1.7.0"
                for record in produced
            )
        )
        self.assertTrue(
            all(
                record["workflow_path"]
                == ".github/workflows/"
                "frp-m15-implementation-mapping-qualification.yml"
                for record in produced
            )
        )
        self.assertTrue(
            all(
                record["workflow_artifact_name"]
                == "frp-v1.7.0-m15-qualification-artifacts"
                for record in produced
            )
        )
        self.assertTrue(
            all(
                record["producer_commands"]
                for record in produced
            )
        )

    def test_m15_vector_package_member_order_and_names_are_exact(
        self,
    ) -> None:
        members = sorted(
            (
                record
                for record in self.records
                if (
                    record.get("package_name")
                    == "frp_m15_deterministic_vector_package"
                )
            ),
            key=lambda record: record["package_member_order"],
        )
        self.assertEqual(
            [
                record["package_member_order"]
                for record in members
            ],
            list(range(10)),
        )
        self.assertEqual(
            tuple(
                Path(
                    record["workflow_member_path"]
                ).name
                for record in members
            ),
            EXPECTED_M15_VECTOR_MEMBERS,
        )

    def test_headered_m15_vector_members_use_exact_format_identity(
        self,
    ) -> None:
        headered = [
            record
            for record in self.records
            if (
                record.get("format_identifier")
                == "frp.m15.vector.v1"
            )
        ]
        self.assertEqual(len(headered), 7)
        self.assertTrue(
            all(
                record.get("trace_kind")
                for record in headered
            )
        )

    def test_m15_manifest_has_exact_package_identity(self) -> None:
        manifest = next(
            record
            for record in self.records
            if (
                record["record_id"]
                == "m15.vector_member.08.sha256_manifest"
            )
        )
        self.assertEqual(manifest["artifact_format"], "json")
        self.assertEqual(manifest["package_member_order"], 8)
        self.assertTrue(
            manifest["workflow_member_path"].endswith(
                "frp_m15_sha256_manifest.json"
            )
        )

    def test_m16_rtl_workflow_member_set_is_exact(self) -> None:
        rtl_records = [
            record
            for record in self.records
            if record["record_id"].startswith(
                "m16.rtl.workflow."
            )
        ]
        self.assertEqual(
            {
                record["workflow_member_path"]
                for record in rtl_records
            },
            EXPECTED_M16_RTL_MEMBERS,
        )
        self.assertTrue(
            all(
                record["workflow_artifact_name"]
                == (
                    "frp-m16-rtl-qualification-"
                    "${{ github.run_number }}"
                )
                for record in rtl_records
            )
        )

    def test_m16_fpga_workflow_member_set_is_exact(self) -> None:
        fpga_records = [
            record
            for record in self.records
            if record["record_id"].startswith(
                "m16.fpga.workflow."
            )
        ]
        self.assertEqual(
            {
                record["workflow_member_path"]
                for record in fpga_records
            },
            EXPECTED_M16_FPGA_MEMBERS,
        )
        self.assertTrue(
            all(
                record["workflow_artifact_name"]
                == (
                    "frp-m16-fpga-preparation-"
                    "${{ github.run_number }}"
                )
                for record in fpga_records
            )
        )

    def test_workflow_records_do_not_claim_committed_source_bytes(
        self,
    ) -> None:
        retained = [
            record
            for record in self.records
            if record["publication_state"] == "workflow_retained"
        ]
        self.assertEqual(len(retained), 11)
        self.assertTrue(
            all(
                not record["canonical"]
                for record in retained
            )
        )
        self.assertTrue(
            all(
                "repository_path" not in record
                for record in retained
            )
        )
        self.assertTrue(
            all(
                "raw_sha256" not in record
                for record in retained
            )
        )
        self.assertTrue(
            all(
                "30 days" in record["note"]
                for record in retained
            )
        )

    def test_documentation_records_are_exact_and_digest_bound(
        self,
    ) -> None:
        documentation = [
            record
            for record in self.records
            if record["publication_state"] == "documentation_only"
        ]
        self.assertEqual(
            {
                record["repository_path"]
                for record in documentation
            },
            EXPECTED_DOCUMENTATION_PATHS,
        )

        for record in documentation:
            with self.subTest(record_id=record["record_id"]):
                path = REPO_ROOT / record["repository_path"]
                self.assertEqual(
                    record["raw_sha256"],
                    sha256(path),
                )
                self.assertEqual(
                    record["byte_length"],
                    path.stat().st_size,
                )

    def test_planned_unavailable_records_are_exact_and_nonclaiming(
        self,
    ) -> None:
        missing = [
            record
            for record in self.records
            if record["publication_state"] == "planned_unavailable"
        ]
        self.assertEqual(
            {
                record["record_id"]
                for record in missing
            },
            EXPECTED_MISSING_RECORDS,
        )

        for record in missing:
            with self.subTest(record_id=record["record_id"]):
                self.assertFalse(record["required"])
                self.assertFalse(record["canonical"])
                self.assertNotIn("repository_path", record)
                self.assertNotIn("workflow_member_path", record)
                self.assertNotIn("raw_sha256", record)
                self.assertNotIn("schema_identifier", record)

    def test_measurement_contours_remain_separate(self) -> None:
        comparative = {
            record.get("measurement_contour")
            for record in self.records
            if record["record_id"].startswith("comparative.")
        }
        sensitivity = {
            record.get("measurement_contour")
            for record in self.records
            if record["record_id"].startswith(
                "hardware_sensitivity."
            )
        }
        rtl = {
            record.get("measurement_contour")
            for record in self.records
            if record["record_id"].startswith(
                "m16.rtl.workflow."
            )
        }
        fpga = {
            record.get("measurement_contour")
            for record in self.records
            if record["record_id"].startswith(
                "m16.fpga.workflow."
            )
        }

        self.assertEqual(
            comparative,
            {"comparative_architecture_benchmark_suite"},
        )
        self.assertEqual(
            sensitivity,
            {"hardware_informed_sensitivity_qualification"},
        )
        self.assertEqual(
            rtl,
            {"m16_rtl_qualification"},
        )
        self.assertEqual(
            fpga,
            {"m16_fpga_preparation_qualification"},
        )

    def test_inventory_content_digest_matches_declared_scope(
        self,
    ) -> None:
        digest_input = dict(self.payload)
        declared = digest_input.pop(
            "inventory_content_sha256"
        )
        calculated = hashlib.sha256(
            json.dumps(
                digest_input,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(declared, calculated)

    def test_inventory_rendering_is_byte_deterministic(
        self,
    ) -> None:
        first = inventory.inventory_json(
            inventory.build_inventory(REPO_ROOT)
        )
        second = inventory.inventory_json(
            inventory.build_inventory(REPO_ROOT)
        )
        self.assertEqual(
            first.encode("utf-8"),
            second.encode("utf-8"),
        )

    def test_build_inventory_does_not_modify_digest_bound_sources(
        self,
    ) -> None:
        paths = [
            REPO_ROOT / record["repository_path"]
            for record in self.records
            if "repository_path" in record
        ]
        before = {
            path: sha256(path)
            for path in paths
        }
        inventory.build_inventory(REPO_ROOT)
        after = {
            path: sha256(path)
            for path in paths
        }
        self.assertEqual(after, before)

    def test_builtin_self_test_passes_all_checks(self) -> None:
        result = inventory.run_self_test(REPO_ROOT)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["check_count"], 25)
        self.assertTrue(
            all(
                result["checks"].values()
            )
        )

    def test_cli_self_test_json_succeeds(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--repository-root",
                str(REPO_ROOT),
                "--self-test",
                "--output",
                "json",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            completed.returncode,
            0,
            completed.stderr,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["check_count"], 25)

    def test_cli_write_produces_exact_json_without_temp_residue(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            target = temporary_root / "inventory.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--repository-root",
                    str(REPO_ROOT),
                    "--output",
                    "json",
                    "--write",
                    str(target),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                completed.returncode,
                0,
                completed.stderr,
            )
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                inventory.inventory_json(
                    inventory.build_inventory(REPO_ROOT)
                ),
            )
            self.assertEqual(
                list(
                    temporary_root.glob(
                        ".inventory.json.*.tmp"
                    )
                ),
                [],
            )

    def test_cli_rejects_write_combined_with_self_test(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "forbidden.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--self-test",
                    "--write",
                    str(target),
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn(
                "--write cannot be combined with --self-test",
                completed.stderr,
            )
            self.assertFalse(target.exists())

    def test_unsafe_relative_paths_are_rejected(self) -> None:
        unsafe_values = (
            "../outside.json",
            "/absolute.json",
            "windows\\path.json",
            "nul\x00path.json",
        )

        for value in unsafe_values:
            with self.subTest(value=value):
                with self.assertRaises(
                    inventory.InventoryError
                ):
                    inventory._safe_relative_path(
                        value,
                        "test_path",
                    )


if __name__ == "__main__":
    unittest.main()
