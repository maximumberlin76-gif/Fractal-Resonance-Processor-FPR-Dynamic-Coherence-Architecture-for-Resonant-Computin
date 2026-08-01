#!/usr/bin/env python3
"""Deterministic FRP M17 published-artifact inventory generator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


VERSION = "1.9.0"
MILESTONE = "M17 — Published Artifact Integration Contract"
INVENTORY_SCHEMA = "frp.m17.published_artifact_inventory.v1.9.0"
SELF_TEST_SCHEMA = "frp.m17.published_artifact_inventory.self_test.v1.9.0"
BASELINE_RELEASE = "FRP v1.8.0"
BASELINE_MILESTONE = "M16 — RTL Core Realization and Execution Semantics Package"
SEMANTIC_REFERENCE = "frp_prototype_v1_7_0.py"
PRODUCER_VERSION = "1.7.0"
PRODUCER_MILESTONE = (
    "M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package"
)

PUBLICATION_STATES = (
    "documentation_only",
    "planned_unavailable",
    "producer_defined",
    "release_archived",
    "repository_committed",
    "workflow_retained",
)

MEASUREMENT_CONTOURS = (
    "comparative_architecture_benchmark_suite",
    "hardware_informed_sensitivity_qualification",
    "m15_implementation_mapping_matrix",
    "m16_fpga_preparation_qualification",
    "m16_rtl_qualification",
    "structured_output_benchmark",
)

M15_WORKFLOW = (
    ".github/workflows/frp-m15-implementation-mapping-qualification.yml"
)
M15_WORKFLOW_ARTIFACT = "frp-v1.7.0-m15-qualification-artifacts"
M16_RTL_WORKFLOW = ".github/workflows/frp-m16-rtl-artifact-boundary.yml"
M16_RTL_WORKFLOW_ARTIFACT = (
    "frp-m16-rtl-qualification-${{ github.run_number }}"
)
M16_FPGA_WORKFLOW = ".github/workflows/frp-m16-fpga-preparation.yml"
M16_FPGA_WORKFLOW_ARTIFACT = (
    "frp-m16-fpga-preparation-${{ github.run_number }}"
)


class InventoryError(ValueError):
    """Raised when an inventory record violates the M17 contract."""


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """One immutable publication-inventory record."""

    record_id: str
    artifact_role: str
    publication_state: str
    artifact_format: str
    identity_basis: str
    upstream_release: str
    upstream_milestone: str
    measurement_contour: str | None = None
    repository_path: str | None = None
    schema_identifier: str | None = None
    format_identifier: str | None = None
    artifact_kind: str | None = None
    trace_kind: str | None = None
    producer_path: str | None = None
    producer_version: str | None = None
    producer_commands: tuple[str, ...] = ()
    workflow_path: str | None = None
    workflow_artifact_name: str | None = None
    workflow_member_path: str | None = None
    package_name: str | None = None
    package_member_order: int | None = None
    required: bool = True
    canonical: bool = False
    note: str | None = None


def _sha256(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def _safe_relative_path(value: str, field_name: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or value != value.strip():
        raise InventoryError(f"{field_name} must be a non-empty stripped string")
    if "\\" in value or "\x00" in value:
        raise InventoryError(f"{field_name} must use a safe POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise InventoryError(f"{field_name} must use a safe POSIX relative path")
    return path


def _recorded_file(
    root: Path,
    relative_path: str,
    field_name: str = "repository_path",
) -> Path:
    path = _safe_relative_path(relative_path, field_name)
    repository_root = root.resolve()
    candidate = repository_root.joinpath(*path.parts)
    if not candidate.is_file():
        raise InventoryError(f"required repository file is missing: {relative_path}")
    try:
        candidate.resolve().relative_to(repository_root)
    except ValueError as error:
        raise InventoryError(
            f"{field_name} must resolve inside the repository root"
        ) from error
    return candidate


def _record_mapping(record: ArtifactRecord, root: Path) -> dict[str, Any]:
    mapping: dict[str, Any] = {
        "record_id": record.record_id,
        "artifact_role": record.artifact_role,
        "publication_state": record.publication_state,
        "artifact_format": record.artifact_format,
        "identity_basis": record.identity_basis,
        "upstream_release": record.upstream_release,
        "upstream_milestone": record.upstream_milestone,
        "required": record.required,
        "canonical": record.canonical,
    }

    optional_values = {
        "measurement_contour": record.measurement_contour,
        "repository_path": record.repository_path,
        "schema_identifier": record.schema_identifier,
        "format_identifier": record.format_identifier,
        "artifact_kind": record.artifact_kind,
        "trace_kind": record.trace_kind,
        "producer_path": record.producer_path,
        "producer_version": record.producer_version,
        "workflow_path": record.workflow_path,
        "workflow_artifact_name": record.workflow_artifact_name,
        "workflow_member_path": record.workflow_member_path,
        "package_name": record.package_name,
        "package_member_order": record.package_member_order,
        "note": record.note,
    }
    mapping.update(
        {
            key: value
            for key, value in optional_values.items()
            if value is not None
        }
    )

    if record.producer_commands:
        mapping["producer_commands"] = list(record.producer_commands)

    if record.repository_path is not None:
        source = _recorded_file(root, record.repository_path)
        raw_bytes = source.read_bytes()
        mapping["source_filename"] = source.name
        mapping["byte_length"] = len(raw_bytes)
        mapping["raw_sha256"] = _sha256(raw_bytes)

    return mapping


def _repo_json(
    record_id: str,
    role: str,
    path: str,
    contour: str,
    *,
    schema: str | None,
    identity_basis: str = "embedded_schema",
    producer_path: str | None = None,
    producer_commands: tuple[str, ...] = (),
    note: str | None = None,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=record_id,
        artifact_role=role,
        publication_state="repository_committed",
        artifact_format="json",
        identity_basis=identity_basis,
        upstream_release=BASELINE_RELEASE,
        upstream_milestone=BASELINE_MILESTONE,
        measurement_contour=contour,
        repository_path=path,
        schema_identifier=schema,
        producer_path=producer_path,
        producer_commands=producer_commands,
        canonical=True,
        note=note,
    )


def _m15_output(
    record_id: str,
    role: str,
    output_name: str,
    command: str,
    schema: str,
    kind: str,
    *,
    note: str | None = None,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=record_id,
        artifact_role=role,
        publication_state="producer_defined",
        artifact_format="json",
        identity_basis="schema_and_kind",
        upstream_release="FRP v1.7.0",
        upstream_milestone=PRODUCER_MILESTONE,
        measurement_contour="m15_implementation_mapping_matrix",
        schema_identifier=schema,
        artifact_kind=kind,
        producer_path=SEMANTIC_REFERENCE,
        producer_version=PRODUCER_VERSION,
        producer_commands=(command,),
        workflow_path=M15_WORKFLOW,
        workflow_artifact_name=M15_WORKFLOW_ARTIFACT,
        workflow_member_path=f"artifacts/m15/{output_name}",
        note=note,
    )


def _m15_vector_member(
    order: int,
    filename: str,
    role: str,
    artifact_format: str,
    *,
    trace_kind: str | None = None,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=f"m15.vector_member.{order:02d}.{role}",
        artifact_role=role,
        publication_state="producer_defined",
        artifact_format=artifact_format,
        identity_basis=(
            "format_and_trace_kind"
            if trace_kind
            else "verified_package_role"
        ),
        upstream_release="FRP v1.7.0",
        upstream_milestone=PRODUCER_MILESTONE,
        measurement_contour="m15_implementation_mapping_matrix",
        format_identifier=("frp.m15.vector.v1" if trace_kind else None),
        trace_kind=trace_kind,
        producer_path=SEMANTIC_REFERENCE,
        producer_version=PRODUCER_VERSION,
        producer_commands=(
            "python frp_prototype_v1_7_0.py "
            "--export-rtl-comparison-vector-package "
            "--vector-output-dir <directory>",
        ),
        workflow_path=M15_WORKFLOW,
        workflow_artifact_name=M15_WORKFLOW_ARTIFACT,
        workflow_member_path=f"artifacts/m15/vectors_a/{filename}",
        package_name="frp_m15_deterministic_vector_package",
        package_member_order=order,
    )


def _workflow_member(
    record_id: str,
    role: str,
    artifact_format: str,
    contour: str,
    workflow_path: str,
    workflow_artifact_name: str,
    member_name: str,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=record_id,
        artifact_role=role,
        publication_state="workflow_retained",
        artifact_format=artifact_format,
        identity_basis="workflow_artifact_and_member",
        upstream_release=BASELINE_RELEASE,
        upstream_milestone=BASELINE_MILESTONE,
        measurement_contour=contour,
        workflow_path=workflow_path,
        workflow_artifact_name=workflow_artifact_name,
        workflow_member_path=member_name,
        note=(
            "Workflow-retained for 30 days; exact instance requires "
            "a workflow run identity."
        ),
    )


def _documentation(
    record_id: str,
    role: str,
    path: str,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=record_id,
        artifact_role=role,
        publication_state="documentation_only",
        artifact_format="markdown",
        identity_basis="exact_repository_path",
        upstream_release=BASELINE_RELEASE,
        upstream_milestone=BASELINE_MILESTONE,
        repository_path=path,
    )


def _missing(
    record_id: str,
    role: str,
    artifact_format: str,
    note: str,
) -> ArtifactRecord:
    return ArtifactRecord(
        record_id=record_id,
        artifact_role=role,
        publication_state="planned_unavailable",
        artifact_format=artifact_format,
        identity_basis="absence_record",
        upstream_release=BASELINE_RELEASE,
        upstream_milestone=BASELINE_MILESTONE,
        required=False,
        note=note,
    )


def _records() -> tuple[ArtifactRecord, ...]:
    records: list[ArtifactRecord] = [
        _repo_json(
            "comparative.profile.workload.v1",
            "deterministic_workload_profile",
            "benchmarks/architecture_comparison/profiles/"
            "workload_profile_v1.json",
            "comparative_architecture_benchmark_suite",
            schema=None,
            identity_basis="exact_path_and_role",
            note="Schema-free committed profile input.",
        ),
        _repo_json(
            "comparative.profile.normalized_cost.v1",
            "normalized_activity_cost_profile",
            "benchmarks/architecture_comparison/profiles/"
            "normalized_cost_profile_v1.json",
            "comparative_architecture_benchmark_suite",
            schema="frp.benchmark.normalized_cost_profile.v1",
        ),
        _repo_json(
            "comparative.profile.thermal_proxy.v1",
            "common_thermal_proxy_profile",
            "benchmarks/architecture_comparison/profiles/"
            "thermal_proxy_profile_v1.json",
            "comparative_architecture_benchmark_suite",
            schema="frp.benchmark.thermal_proxy_profile.v1",
        ),
        _repo_json(
            "hardware_sensitivity.profile.cost.v1",
            "hardware_informed_sensitivity_profile",
            "benchmarks/architecture_comparison/profiles/"
            "hardware_sensitivity_cost_profile_v1.json",
            "hardware_informed_sensitivity_qualification",
            schema=(
                "frp.benchmark.hardware_sensitivity_cost_profile.v1"
            ),
            note=(
                "Validated by "
                "validate_hardware_sensitivity_profile.py."
            ),
        ),
        _repo_json(
            "comparative.result.reference_seed_76.v1",
            "canonical_comparative_architecture_result",
            "benchmarks/architecture_comparison/results/"
            "reference_comparison_seed_76.json",
            "comparative_architecture_benchmark_suite",
            schema="frp.benchmark.architecture_comparison.v1",
            producer_path=(
                "benchmarks/architecture_comparison/"
                "run_architecture_comparison.py"
            ),
            producer_commands=(
                "python run_architecture_comparison.py "
                "--workload-profile profiles/workload_profile_v1.json "
                "--cost-profile profiles/normalized_cost_profile_v1.json "
                "--thermal-profile profiles/thermal_proxy_profile_v1.json "
                "--frp-scheduler 7/1 "
                "--write results/reference_comparison_seed_76.json "
                "--output text",
            ),
        ),
        _repo_json(
            "hardware_sensitivity.result.reference_seed_76.v1",
            "canonical_hardware_sensitivity_result",
            "benchmarks/architecture_comparison/results/"
            "reference_comparison_seed_76_hardware_sensitivity_v1.json",
            "hardware_informed_sensitivity_qualification",
            schema=(
                "frp.benchmark.hardware_sensitivity_comparison.v1"
            ),
            producer_path=(
                "benchmarks/architecture_comparison/"
                "run_hardware_sensitivity_comparison.py"
            ),
            producer_commands=(
                "python run_hardware_sensitivity_comparison.py "
                "--workload-profile profiles/workload_profile_v1.json "
                "--hardware-sensitivity-profile "
                "profiles/hardware_sensitivity_cost_profile_v1.json "
                "--thermal-profile profiles/thermal_proxy_profile_v1.json "
                "--frp-scheduler 7/1 "
                "--write results/"
                "reference_comparison_seed_76_hardware_sensitivity_v1.json "
                "--output text",
            ),
        ),
    ]

    structured_schema = "frp.structured_output.v1.7.0"
    benchmark_schema = "frp.m3.benchmark_matrix.v1.7.0"

    records.extend(
        (
            _m15_output(
                "m15.structured_output.default",
                "structured_output",
                "structured-output.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--mode demo --output json"
                ),
                structured_schema,
                "demo",
                note=(
                    "The --include-trace option produces "
                    "the full-trace variant."
                ),
            ),
            _m15_output(
                "m15.self_test.default",
                "self_test_default_scheduler",
                "self-test.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--mode self-test --output json"
                ),
                structured_schema,
                "self_test",
            ),
            _m15_output(
                "m15.self_test.free",
                "self_test_free_scheduler",
                "self-test-free.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--mode self-test --scheduler free --output json"
                ),
                structured_schema,
                "self_test",
            ),
            _m15_output(
                "m15.self_test.7_1",
                "self_test_7_1_scheduler",
                "self-test-7-1.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--mode self-test --scheduler 7/1 --output json"
                ),
                structured_schema,
                "self_test",
            ),
            _m15_output(
                "m15.self_test.1_7",
                "self_test_1_7_scheduler",
                "self-test-1-7.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--mode self-test --scheduler 1/7 --output json"
                ),
                structured_schema,
                "self_test",
            ),
            _m15_output(
                "m15.benchmark_matrix",
                "benchmark_matrix",
                "benchmark-matrix.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    "--export-benchmark-matrix"
                ),
                benchmark_schema,
                "benchmark_matrix",
            ),
        )
    )

    for cells in (8, 16, 32):
        records.append(
            _m15_output(
                f"m15.scaling.{cells}",
                f"structured_scaling_{cells}_cells",
                f"scaling-{cells}.json",
                (
                    "python frp_prototype_v1_7_0.py "
                    f"--cells {cells} --steps 16 "
                    "--mode demo --output json"
                ),
                structured_schema,
                "demo",
            )
        )

    export_specs = (
        (
            "fixed_point_interface_profile",
            "fixed-point-interface-profile.json",
            "frp.m15.fixed_point_interface_profile.v1.7.0",
        ),
        (
            "balanced_ternary_hardware_encoding_map",
            "balanced-ternary-hardware-encoding-map.json",
            (
                "frp.m15."
                "balanced_ternary_hardware_encoding_map.v1.7.0"
            ),
        ),
        (
            "quantized_reference_shadow_model",
            "quantized-reference-shadow-model.json",
            "frp.m15.quantized_reference_shadow_model.v1.7.0",
        ),
        (
            "cycle_exact_reference_trace",
            "cycle-exact-reference-trace.json",
            "frp.m15.cycle_exact_reference_trace.v1.7.0",
        ),
        (
            "rtl_comparison_vector_package",
            "rtl-comparison-vector-package.json",
            "frp.m15.rtl_comparison_vector_package.v1.7.0",
        ),
        (
            "systemverilog_testbench_interface_map",
            "systemverilog-testbench-interface-map.json",
            (
                "frp.m15."
                "systemverilog_testbench_interface_map.v1.7.0"
            ),
        ),
        (
            "synthesizable_rtl_reference_core",
            "synthesizable-rtl-reference-core.json",
            "frp.m15.synthesizable_rtl_reference_core.v1.7.0",
        ),
        (
            "rtl_assertion_correlation_harness",
            "rtl-assertion-correlation-harness.json",
            (
                "frp.m15."
                "rtl_assertion_correlation_harness.v1.7.0"
            ),
        ),
        (
            "reference_rtl_equivalence_report",
            "reference-rtl-equivalence-report.json",
            (
                "frp.m15."
                "reference_rtl_equivalence_report.v1.7.0"
            ),
        ),
        (
            "qualification_closure_manifest",
            "qualification-closure-manifest.json",
            "frp.m15.qualification_closure_manifest.v1.7.0",
        ),
    )

    for kind, filename, schema in export_specs:
        option = "--export-" + kind.replace("_", "-")
        records.append(
            _m15_output(
                f"m15.export.{kind}",
                kind,
                filename,
                f"python frp_prototype_v1_7_0.py {option}",
                schema,
                kind,
            )
        )

    vector_specs = (
        (
            "frp_m15_cell_trace.vec",
            "cell_trace",
            "headered_vector",
            "cell_trace",
        ),
        (
            "frp_m15_full_correlation_vectors.vec",
            "full_correlation_vectors",
            "headered_vector",
            "full_correlation_vectors",
        ),
        (
            "frp_m15_kernel_vectors.vec",
            "kernel_transition_vectors",
            "headered_vector",
            "kernel_transition_vectors",
        ),
        (
            "frp_m15_pending_routes.trace",
            "pending_routes",
            "headered_trace",
            "pending_routes",
        ),
        (
            "frp_m15_reference_preload.json",
            "reference_preload",
            "json",
            None,
        ),
        (
            "frp_m15_scheduler_1_7_vectors.vec",
            "scheduler_1_7_vectors",
            "headered_vector",
            "scheduler_1_7_vectors",
        ),
        (
            "frp_m15_scheduler_7_1_vectors.vec",
            "scheduler_7_1_vectors",
            "headered_vector",
            "scheduler_7_1_vectors",
        ),
        (
            "frp_m15_scheduler_free_vectors.vec",
            "scheduler_free_vectors",
            "headered_vector",
            "scheduler_free_vectors",
        ),
        (
            "frp_m15_sha256_manifest.json",
            "sha256_manifest",
            "json",
            None,
        ),
        (
            "frp_m15_trig_lut_q30.vec",
            "trigonometric_lookup_table",
            "vector_text",
            None,
        ),
    )

    records.extend(
        _m15_vector_member(
            order,
            filename,
            role,
            artifact_format,
            trace_kind=trace_kind,
        )
        for order, (
            filename,
            role,
            artifact_format,
            trace_kind,
        ) in enumerate(vector_specs)
    )

    rtl_members = (
        (
            "toolchain_log",
            "text",
            "frp_m16_toolchain.log",
        ),
        (
            "source_sha256_manifest",
            "sha256_manifest",
            "frp_m16_sources.sha256",
        ),
        (
            "build_log",
            "text",
            "frp_m16_build.log",
        ),
        (
            "execution_log",
            "text",
            "frp_m16_execution.log",
        ),
        (
            "qualification_record",
            "text",
            "frp_m16_qualification.txt",
        ),
    )

    records.extend(
        _workflow_member(
            f"m16.rtl.workflow.{role}",
            role,
            artifact_format,
            "m16_rtl_qualification",
            M16_RTL_WORKFLOW,
            M16_RTL_WORKFLOW_ARTIFACT,
            filename,
        )
        for role, artifact_format, filename in rtl_members
    )

    fpga_members = (
        (
            "toolchain_log",
            "text",
            "frp_m16_fpga_toolchain.log",
        ),
        (
            "source_sha256_manifest",
            "sha256_manifest",
            "frp_m16_fpga_sources.sha256",
        ),
        (
            "top_lint_log",
            "text",
            "frp_m16_fpga_top_lint.log",
        ),
        (
            "build_log",
            "text",
            "frp_m16_fpga_build.log",
        ),
        (
            "execution_log",
            "text",
            "frp_m16_fpga_execution.log",
        ),
        (
            "qualification_record",
            "text",
            "frp_m16_fpga_qualification.txt",
        ),
    )

    records.extend(
        _workflow_member(
            f"m16.fpga.workflow.{role}",
            role,
            artifact_format,
            "m16_fpga_preparation_qualification",
            M16_FPGA_WORKFLOW,
            M16_FPGA_WORKFLOW_ARTIFACT,
            filename,
        )
        for role, artifact_format, filename in fpga_members
    )

    documentation_specs = (
        (
            "m17.integration_contract",
            "published_artifact_integration_contract",
            "docs/m17_published_artifact_integration_contract.md",
        ),
        (
            "output_schema",
            "output_schema_documentation",
            "docs/output_schema.md",
        ),
        (
            "benchmark_matrix",
            "benchmark_matrix_documentation",
            "docs/benchmark_matrix.md",
        ),
        (
            "m15.architecture",
            "m15_architecture_documentation",
            "docs/"
            "m15_implementation_mapping_domain_interface_"
            "qualification_closure.md",
        ),
        (
            "v1_8_0.validation_index",
            "release_validation_index",
            "FRP_VALIDATION_INDEX_v1_8_0.md",
        ),
        (
            "m16.qualification_manifest",
            "m16_qualification_manifest",
            "docs/m16_qualification_manifest.md",
        ),
        (
            "m16.qualification_index",
            "m16_qualification_index",
            "docs/m16_qualification_index.md",
        ),
        (
            "m16.public_status_snapshot",
            "m16_public_status_snapshot",
            "docs/m16_public_status_snapshot.md",
        ),
        (
            "m16.rtl.artifacts",
            "m16_rtl_artifact_index",
            "rtl/m16/ARTIFACTS.md",
        ),
        (
            "m16.rtl.simulation_transcript",
            "m16_rtl_simulation_transcript",
            "rtl/m16/SIMULATION_TRANSCRIPT.md",
        ),
        (
            "m16.rtl.closure",
            "m16_rtl_closure",
            "rtl/m16/CLOSURE.md",
        ),
        (
            "m16.fpga.simulation_transcript",
            "m16_fpga_simulation_transcript",
            "fpga/m16/SIMULATION_TRANSCRIPT.md",
        ),
        (
            "m16.fpga.closure",
            "m16_fpga_closure",
            "fpga/m16/CLOSURE.md",
        ),
    )

    records.extend(
        _documentation(*spec)
        for spec in documentation_specs
    )

    records.extend(
        (
            _missing(
                "missing.formal_json_schemas",
                "formal_json_schema_files",
                "json_schema_set",
                (
                    "No formal JSON Schema files are committed "
                    "in the audited baseline."
                ),
            ),
            _missing(
                "missing.committed_m15_canonical_artifacts",
                "committed_m15_canonical_artifact_set",
                "artifact_set",
                (
                    "M15 JSON exports and vector members are not "
                    "committed canonical fixtures."
                ),
            ),
            _missing(
                "missing.canonical_csv_tsv_artifacts",
                "canonical_csv_tsv_artifact_set",
                "tabular_artifact_set",
                (
                    "No canonical CSV or TSV artifacts are committed "
                    "in the audited baseline."
                ),
            ),
            _missing(
                "missing.machine_readable_m16_artifacts",
                (
                    "machine_readable_m16_schema_trace_"
                    "and_qualification_set"
                ),
                "artifact_set",
                (
                    "No frp.m16.* schema or committed machine-readable "
                    "M16 trace is present."
                ),
            ),
        )
    )

    return tuple(
        sorted(
            records,
            key=lambda record: record.record_id,
        )
    )


def _validate_record(
    record: ArtifactRecord,
    root: Path,
) -> None:
    for field_name in (
        "record_id",
        "artifact_role",
        "publication_state",
        "artifact_format",
        "identity_basis",
        "upstream_release",
        "upstream_milestone",
    ):
        value = getattr(record, field_name)
        if (
            not isinstance(value, str)
            or not value
            or value != value.strip()
            or "\x00" in value
        ):
            raise InventoryError(
                f"{field_name} must be a non-empty stripped string"
            )

    if record.publication_state not in PUBLICATION_STATES:
        raise InventoryError(
            "unsupported publication_state: "
            f"{record.publication_state}"
        )

    if record.measurement_contour not in {
        None,
        *MEASUREMENT_CONTOURS,
    }:
        raise InventoryError(
            "unsupported measurement_contour: "
            f"{record.measurement_contour}"
        )

    if (
        record.schema_identifier is not None
        and not record.schema_identifier.startswith("frp.")
    ):
        raise InventoryError(
            "schema_identifier must use an exact frp.* identity"
        )

    if (
        record.format_identifier is not None
        and not record.format_identifier.startswith("frp.")
    ):
        raise InventoryError(
            "format_identifier must use an exact frp.* identity"
        )

    for field_name in (
        "repository_path",
        "producer_path",
        "workflow_path",
        "workflow_member_path",
    ):
        value = getattr(record, field_name)
        if value is not None:
            _safe_relative_path(value, field_name)

    if record.repository_path is not None:
        _recorded_file(
            root,
            record.repository_path,
        )

    if record.producer_path is not None:
        _recorded_file(
            root,
            record.producer_path,
            "producer_path",
        )

    if record.workflow_path is not None:
        _recorded_file(
            root,
            record.workflow_path,
            "workflow_path",
        )

    if record.publication_state in {
        "repository_committed",
        "documentation_only",
    }:
        if record.repository_path is None:
            raise InventoryError(
                f"{record.publication_state} requires repository_path"
            )

    elif record.publication_state == "producer_defined":
        if (
            record.producer_path is None
            or not record.producer_commands
        ):
            raise InventoryError(
                "producer_defined requires producer path and command"
            )

    elif record.publication_state == "workflow_retained":
        if not all(
            (
                record.workflow_path,
                record.workflow_artifact_name,
                record.workflow_member_path,
            )
        ):
            raise InventoryError(
                "workflow_retained requires workflow "
                "and member identity"
            )

    elif record.publication_state == "planned_unavailable":
        if (
            record.repository_path
            or record.workflow_member_path
            or record.canonical
        ):
            raise InventoryError(
                "planned_unavailable cannot claim "
                "available source bytes"
            )

    if record.package_member_order is not None:
        if (
            record.package_name is None
            or record.package_member_order < 0
        ):
            raise InventoryError(
                "package member order requires a package "
                "and nonnegative order"
            )


def _validate_record_set(
    records: Sequence[ArtifactRecord],
    root: Path,
) -> None:
    record_ids = [
        record.record_id
        for record in records
    ]

    if record_ids != sorted(record_ids):
        raise InventoryError(
            "records must be ordered lexicographically by record_id"
        )

    if len(record_ids) != len(set(record_ids)):
        raise InventoryError(
            "record_id values must be unique"
        )

    for record in records:
        _validate_record(
            record,
            root,
        )

    vector_orders = [
        record.package_member_order
        for record in records
        if (
            record.package_name
            == "frp_m15_deterministic_vector_package"
        )
    ]

    if vector_orders != list(range(10)):
        raise InventoryError(
            "M15 vector package order must contain "
            "exactly 0 through 9"
        )


def _canonical_compact_json(
    value: Any,
) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def build_inventory(
    repository_root: Path,
) -> dict[str, Any]:
    root = repository_root.resolve()
    records = _records()

    _validate_record_set(
        records,
        root,
    )

    record_mappings = [
        _record_mapping(
            record,
            root,
        )
        for record in records
    ]

    state_counts = {
        state: sum(
            record.publication_state == state
            for record in records
        )
        for state in PUBLICATION_STATES
    }

    contour_counts = {
        contour: sum(
            record.measurement_contour == contour
            for record in records
        )
        for contour in MEASUREMENT_CONTOURS
    }

    schema_identifiers = sorted(
        {
            record.schema_identifier
            for record in records
            if record.schema_identifier
        }
    )

    summary = {
        "total_records": len(records),
        "publication_state_counts": state_counts,
        "measurement_contour_counts": contour_counts,
        "schema_identifier_count": len(schema_identifiers),
        "repository_committed_json_count": sum(
            (
                record.publication_state
                == "repository_committed"
            )
            and record.artifact_format == "json"
            for record in records
        ),
        "m15_export_schema_count": sum(
            record.record_id.startswith("m15.export.")
            for record in records
        ),
        "m15_vector_package_member_count": sum(
            (
                record.package_name
                == "frp_m15_deterministic_vector_package"
            )
            for record in records
        ),
        "m16_workflow_member_count": sum(
            record.record_id.startswith("m16.")
            and record.publication_state == "workflow_retained"
            for record in records
        ),
        "documentation_only_count": (
            state_counts["documentation_only"]
        ),
        "planned_unavailable_count": (
            state_counts["planned_unavailable"]
        ),
        "formal_json_schema_files_committed": 0,
        "committed_m15_canonical_vector_members": 0,
        "canonical_csv_tsv_artifacts_committed": 0,
        "machine_readable_frp_m16_schema_count": 0,
    }

    payload: dict[str, Any] = {
        "schema": INVENTORY_SCHEMA,
        "kind": "published_artifact_inventory",
        "version": VERSION,
        "milestone": MILESTONE,
        "milestone_state": "planned",
        "baseline_release": BASELINE_RELEASE,
        "baseline_milestone": BASELINE_MILESTONE,
        "semantic_reference": SEMANTIC_REFERENCE,
        "integration_direction": (
            "frp_to_published_artifacts_to_downstream_consumers"
        ),
        "source_authority": "frp",
        "canonical_ternary_domain": [-1, 0, 1],
        "canonical_opposite_polarity_routes": [
            [-1, 0, 1],
            [1, 0, -1],
        ],
        "record_order": "record_id_lexicographic",
        "raw_digest_algorithm": "sha256",
        "publication_states": list(PUBLICATION_STATES),
        "schema_identifiers": schema_identifiers,
        "summary": summary,
        "records": record_mappings,
        "inventory_digest_scope": (
            "canonical_compact_json_without_"
            "inventory_content_sha256"
        ),
    }

    payload["inventory_content_sha256"] = _sha256(
        _canonical_compact_json(payload)
    )

    return payload


def inventory_json(
    payload: dict[str, Any],
) -> str:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def inventory_text(
    payload: dict[str, Any],
) -> str:
    summary = payload["summary"]

    lines = [
        f"schema: {payload['schema']}",
        f"kind: {payload['kind']}",
        f"version: {payload['version']}",
        f"milestone: {payload['milestone']}",
        f"milestone_state: {payload['milestone_state']}",
        f"baseline_release: {payload['baseline_release']}",
        f"total_records: {summary['total_records']}",
        (
            "repository_committed_json_count: "
            f"{summary['repository_committed_json_count']}"
        ),
        (
            "m15_export_schema_count: "
            f"{summary['m15_export_schema_count']}"
        ),
        (
            "m15_vector_package_member_count: "
            f"{summary['m15_vector_package_member_count']}"
        ),
        (
            "m16_workflow_member_count: "
            f"{summary['m16_workflow_member_count']}"
        ),
        (
            "planned_unavailable_count: "
            f"{summary['planned_unavailable_count']}"
        ),
        (
            "inventory_content_sha256: "
            f"{payload['inventory_content_sha256']}"
        ),
    ]

    return "\n".join(lines)


def _expect_inventory_error(
    action: Any,
) -> bool:
    try:
        action()
    except InventoryError:
        return True

    return False


def run_self_test(
    repository_root: Path,
) -> dict[str, Any]:
    root = repository_root.resolve()
    records = _records()
    payload_a = build_inventory(root)
    payload_b = build_inventory(root)

    unsafe_record = replace(
        records[0],
        repository_path="../outside.json",
    )
    invalid_state_record = replace(
        records[0],
        publication_state="invented_state",
    )
    missing_record = replace(
        records[0],
        repository_path="missing/artifact.json",
    )

    checks = {
        "schema_exact": (
            payload_a["schema"]
            == INVENTORY_SCHEMA
        ),
        "kind_exact": (
            payload_a["kind"]
            == "published_artifact_inventory"
        ),
        "version_exact": (
            payload_a["version"]
            == VERSION
        ),
        "milestone_exact": (
            payload_a["milestone"]
            == MILESTONE
        ),
        "baseline_release_exact": (
            payload_a["baseline_release"]
            == BASELINE_RELEASE
        ),
        "semantic_reference_exact": (
            payload_a["semantic_reference"]
            == SEMANTIC_REFERENCE
        ),
        "canonical_ternary_domain_exact": (
            payload_a["canonical_ternary_domain"]
            == [-1, 0, 1]
        ),
        "canonical_routes_exact": (
            payload_a["canonical_opposite_polarity_routes"]
            == [
                [-1, 0, 1],
                [1, 0, -1],
            ]
        ),
        "record_order_deterministic": (
            [
                row["record_id"]
                for row in payload_a["records"]
            ]
            == sorted(
                row["record_id"]
                for row in payload_a["records"]
            )
        ),
        "record_ids_unique": (
            len(
                {
                    row["record_id"]
                    for row in payload_a["records"]
                }
            )
            == len(payload_a["records"])
        ),
        "inventory_repeat_byte_identical": (
            inventory_json(payload_a)
            == inventory_json(payload_b)
        ),
        "inventory_digest_repeat_exact": (
            payload_a["inventory_content_sha256"]
            == payload_b["inventory_content_sha256"]
        ),
        "repository_committed_json_count_6": (
            payload_a["summary"][
                "repository_committed_json_count"
            ]
            == 6
        ),
        "m15_export_schema_count_10": (
            payload_a["summary"][
                "m15_export_schema_count"
            ]
            == 10
        ),
        "m15_vector_package_member_count_10": (
            payload_a["summary"][
                "m15_vector_package_member_count"
            ]
            == 10
        ),
        "m16_workflow_member_count_11": (
            payload_a["summary"][
                "m16_workflow_member_count"
            ]
            == 11
        ),
        "formal_json_schema_count_0": (
            payload_a["summary"][
                "formal_json_schema_files_committed"
            ]
            == 0
        ),
        "machine_readable_m16_schema_count_0": (
            payload_a["summary"][
                "machine_readable_frp_m16_schema_count"
            ]
            == 0
        ),
        "no_invented_m16_schema_identifier": all(
            not schema.startswith("frp.m16.")
            for schema in payload_a["schema_identifiers"]
        ),
        "repository_digests_are_sha256": all(
            len(row["raw_sha256"]) == 64
            for row in payload_a["records"]
            if "repository_path" in row
        ),
        "duplicate_record_rejected": (
            _expect_inventory_error(
                lambda: _validate_record_set(
                    tuple(
                        sorted(
                            (
                                records[0],
                                records[0],
                            ),
                            key=lambda item: item.record_id,
                        )
                    ),
                    root,
                )
            )
        ),
        "unsafe_path_rejected": (
            _expect_inventory_error(
                lambda: _validate_record(
                    unsafe_record,
                    root,
                )
            )
        ),
        "invalid_state_rejected": (
            _expect_inventory_error(
                lambda: _validate_record(
                    invalid_state_record,
                    root,
                )
            )
        ),
        "missing_committed_file_rejected": (
            _expect_inventory_error(
                lambda: _validate_record(
                    missing_record,
                    root,
                )
            )
        ),
        "canonical_positive_state_has_no_added_sign": (
            '"+1"' not in inventory_json(payload_a)
        ),
    }

    status = (
        "PASS"
        if all(checks.values())
        else "FAIL"
    )

    return {
        "schema": SELF_TEST_SCHEMA,
        "kind": "published_artifact_inventory_self_test",
        "version": VERSION,
        "milestone": MILESTONE,
        "status": status,
        "check_count": len(checks),
        "checks": checks,
        "inventory_content_sha256": (
            payload_a["inventory_content_sha256"]
        ),
    }


def _atomic_write(
    path: Path,
    raw_bytes: bytes,
) -> None:
    target = path.resolve()
    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
    )

    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(
            descriptor,
            "wb",
        ) as handle:
            handle.write(raw_bytes)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(
            temporary_path,
            target,
        )
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the deterministic FRP M17 "
            "published-artifact inventory."
        )
    )

    parser.add_argument(
        "--output",
        choices=(
            "text",
            "json",
        ),
        default="text",
    )
    parser.add_argument(
        "--write",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
    )
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parent,
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if (
        args.self_test
        and args.write is not None
    ):
        parser.error(
            "--write cannot be combined with --self-test"
        )

    try:
        if args.self_test:
            payload = run_self_test(
                args.repository_root
            )

            rendered = (
                inventory_json(payload)
                if args.output == "json"
                else "\n".join(
                    (
                        f"schema: {payload['schema']}",
                        f"status: {payload['status']}",
                        (
                            "check_count: "
                            f"{payload['check_count']}"
                        ),
                        *(
                            f"{name}: {value}"
                            for name, value
                            in payload["checks"].items()
                        ),
                    )
                )
            )

            print(rendered)

            return (
                0
                if payload["status"] == "PASS"
                else 1
            )

        payload = build_inventory(
            args.repository_root
        )
        json_output = inventory_json(payload)

        if args.write is not None:
            _atomic_write(
                args.write,
                json_output.encode("utf-8"),
            )

        print(
            json_output
            if args.output == "json"
            else inventory_text(payload)
        )

        return 0

    except (
        InventoryError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        print(
            f"inventory error: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
