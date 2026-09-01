# Roadmap — Fractal Resonance Processor (FRP)

## Current Roadmap State — FRP v3.3.0 / M31

Current repository release:

`FRP v3.3.0 / M31 — PASS`

Current milestone:

`M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication`

Current execution environment:

`Python 3.12+`

Current balanced ternary domain:

`-1/0/1`

Current release records:

- [`FRP_VALIDATION_INDEX_v3_3_0.md`](FRP_VALIDATION_INDEX_v3_3_0.md);
- [`RELEASE_NOTES_v3_3_0.md`](RELEASE_NOTES_v3_3_0.md);
- [`TEST_REPORT_v3_3_0.md`](TEST_REPORT_v3_3_0.md).

Current M31 publication boundary:

- source: [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py);
- tests: [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py);
- schema: [`schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json);
- evidence: [`artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json);
- manifest: [`artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json);
- qualification: [`artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json);
- complete qualification workflow: [`.github/workflows/frp-m31-complete.yml`](.github/workflows/frp-m31-complete.yml).

Current M31 focused qualification result:

`60 / 60 PASS`

The M31 publication extends the completed M30 archival-release boundary while retaining every historical evidence record, benchmark contour, schema, manifest, qualification record, and release document in its original release context.

## Completed Architecture Progression

| Milestone | Release | Architecture layer | Primary traceability | State |
|---|---:|---|---|---|
| M0 | v0.9.3-mobile | Repository Stabilization | [`frp_prototype_v0_9_3_mobile.py`](frp_prototype_v0_9_3_mobile.py) | Complete |
| M1 | v0.9.3 | Archival Release and DOI | [`RELEASE_NOTES_v0_9_3.md`](RELEASE_NOTES_v0_9_3.md) | Complete |
| M2 | v0.9.4 | Structured Output and Machine-Readable Validation | [`frp_prototype_v0_9_4.py`](frp_prototype_v0_9_4.py) | Complete |
| M3 | v0.9.5 | Benchmark Export and Hardware Signal Mapping | [`docs/m3_validation_targets.md`](docs/m3_validation_targets.md) | Complete |
| M4 | v0.9.6 | HDL Trace Export and Testbench Scaffold | [`docs/m4_hdl_trace_testbench.md`](docs/m4_hdl_trace_testbench.md) | Complete |
| M5 | v0.9.7 | RTL Interface Contract and Assertion Harness | [`docs/m5_rtl_interface_assertion_harness.md`](docs/m5_rtl_interface_assertion_harness.md) | Complete |
| M6 | v0.9.8 | Formal Verification Hooks and Equivalence Scaffold | [`docs/m6_formal_verification_equivalence.md`](docs/m6_formal_verification_equivalence.md) | Complete |
| M7 | v0.9.9 | FPGA Synthesis Package and Timing Constraint Scaffold | [`docs/m7_fpga_synthesis_timing.md`](docs/m7_fpga_synthesis_timing.md) | Complete |
| M8 | v1.0.0 | Production Release Package and Stable Interface Freeze | [`docs/m8_production_release_package.md`](docs/m8_production_release_package.md) | Complete |
| M9 | v1.1.0 | Silicon and Heterogeneous Implementation Architecture | [`docs/m9_silicon_heterogeneous_architecture.md`](docs/m9_silicon_heterogeneous_architecture.md) | Complete |
| M10 | v1.2.0 | Silicon Production and Tapeout Readiness | [`docs/m10_silicon_production_tapeout_readiness.md`](docs/m10_silicon_production_tapeout_readiness.md) | Complete |
| M11 | v1.3.0 | Production Integration and External Implementation Handoff | [`docs/m11_production_integration_external_handoff.md`](docs/m11_production_integration_external_handoff.md) | Complete |
| M12 | v1.4.0 | External Implementation Feedback and Production Iteration | [`docs/m12_external_implementation_feedback_iteration.md`](docs/m12_external_implementation_feedback_iteration.md) | Complete |
| M13 | v1.5.0 | Production Scaling and Implementation Stabilization | [`docs/m13_production_scaling_implementation_stabilization.md`](docs/m13_production_scaling_implementation_stabilization.md) | Complete |
| M14 | v1.6.0 | Physical Implementation Correlation and Production Qualification | [`docs/m14_physical_implementation_correlation_production_qualification.md`](docs/m14_physical_implementation_correlation_production_qualification.md) | Complete |
| M15 | v1.7.0 | Implementation Mapping, Domain Interface, and Qualification Closure | [`docs/m15_implementation_mapping_domain_interface_qualification_closure.md`](docs/m15_implementation_mapping_domain_interface_qualification_closure.md) | Complete |
| M16 | v1.8.0 | RTL Core Realization and Execution Semantics | [`docs/m16_qualification_index.md`](docs/m16_qualification_index.md) | Complete |
| M17 | v1.9.0 | Published Artifact Integration Contract | [`docs/m17_published_artifact_integration_closure.md`](docs/m17_published_artifact_integration_closure.md) | Complete |
| M18 | v2.0.0 | Formal Schema and Canonical Artifact Publication | [`docs/m18_formal_schema_canonical_artifact_publication_qualification.md`](docs/m18_formal_schema_canonical_artifact_publication_qualification.md) | Complete |
| M19 | v2.1.0 | Machine-Readable M16 Execution and Qualification Evidence | [`frp_m19_m16_evidence.py`](frp_m19_m16_evidence.py) | Complete |
| M20 | v2.2.0 | Cross-Layer Deterministic Correlation | [`frp_m20_cross_layer_correlation.py`](frp_m20_cross_layer_correlation.py) | Complete |
| M21 | v2.3.0 | Parameterized Qualification Matrix | [`frp_m21_parameterized_qualification_matrix.py`](frp_m21_parameterized_qualification_matrix.py) | Complete |
| M22 | v2.4.0 | Control, Status, and Register Interface Realization | [`frp_m22_control_status_register_interface.py`](frp_m22_control_status_register_interface.py) | Complete |
| M23 | v2.5.0 | Clock, Reset, CDC, and Interface Hardening | [`frp_m23_clock_reset_cdc_interface_hardening.py`](frp_m23_clock_reset_cdc_interface_hardening.py) | Complete |
| M24 | v2.6.0 | Formal and Bounded Verification Closure | [`frp_m24_formal_bounded_verification.py`](frp_m24_formal_bounded_verification.py) | Complete |
| M25 | v2.7.0 | Fault, Negative-Path, and Recovery Qualification | [`frp_m25_fault_negative_recovery_qualification.py`](frp_m25_fault_negative_recovery_qualification.py) | Complete |
| M26 | v2.8.0 | Declared-Target Implementation Evidence | [`frp_m26_declared_target_implementation_evidence.py`](frp_m26_declared_target_implementation_evidence.py) | Complete |
| M27 | v2.9.0 | Long-Run Stability and Telemetry Qualification | [`frp_m27_long_run_stability_telemetry_qualification.py`](frp_m27_long_run_stability_telemetry_qualification.py) | Complete |
| M28 | v3.0.0 | Hierarchical Scaling and Hotspot-Containment Realization | [`frp_m28_hierarchical_scaling_hotspot_containment.py`](frp_m28_hierarchical_scaling_hotspot_containment.py) | Complete |
| M29 | v3.1.0 | System Integration and Downstream Compatibility Closure | [`frp_m29_system_integration_downstream_compatibility.py`](frp_m29_system_integration_downstream_compatibility.py) | Complete |
| M30 | v3.2.0 | Reproducibility, Qualification, and Archival Release Closure | [`frp_m30_reproducibility_qualification_archival_closure.py`](frp_m30_reproducibility_qualification_archival_closure.py) | Complete |
| M31 | v3.3.0 | Phase-Interference, Active-Zero, and Thermal-Evidence Publication | [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py) | Current complete release |

## M17–M31 Qualification Chain

The completed upper milestone chain is implemented and qualified by these source/test/workflow boundaries:

| Milestone | Source | Test | Qualification workflow |
|---|---|---|---|
| M17 | [`frp_m17_publication_inventory.py`](frp_m17_publication_inventory.py) | [`tests/test_frp_m17_publication_inventory.py`](tests/test_frp_m17_publication_inventory.py) | [`.github/workflows/frp-m17-published-artifact-integration.yml`](.github/workflows/frp-m17-published-artifact-integration.yml) |
| M18 | [`frp_m18_canonical_artifacts.py`](frp_m18_canonical_artifacts.py) | [`tests/test_frp_m18_canonical_artifacts.py`](tests/test_frp_m18_canonical_artifacts.py) | [`.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml`](.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml) |
| M19 | [`frp_m19_m16_evidence.py`](frp_m19_m16_evidence.py) | [`tests/test_frp_m19_m16_evidence.py`](tests/test_frp_m19_m16_evidence.py) | [`.github/workflows/frp-m19-create-machine-readable-m16-evidence.yml`](.github/workflows/frp-m19-create-machine-readable-m16-evidence.yml) |
| M20 | [`frp_m20_cross_layer_correlation.py`](frp_m20_cross_layer_correlation.py) | [`tests/test_frp_m20_cross_layer_correlation.py`](tests/test_frp_m20_cross_layer_correlation.py) | [`.github/workflows/frp-m20-cross-layer-correlation.yml`](.github/workflows/frp-m20-cross-layer-correlation.yml) |
| M21 | [`frp_m21_parameterized_qualification_matrix.py`](frp_m21_parameterized_qualification_matrix.py) | [`tests/test_frp_m21_parameterized_qualification_matrix.py`](tests/test_frp_m21_parameterized_qualification_matrix.py) | [`.github/workflows/frp-m21-parameterized-qualification-matrix.yml`](.github/workflows/frp-m21-parameterized-qualification-matrix.yml) |
| M22 | [`frp_m22_control_status_register_interface.py`](frp_m22_control_status_register_interface.py) | [`tests/test_frp_m22_control_status_register_interface.py`](tests/test_frp_m22_control_status_register_interface.py) | [`.github/workflows/frp-m22-control-status-register-interface.yml`](.github/workflows/frp-m22-control-status-register-interface.yml) |
| M23 | [`frp_m23_clock_reset_cdc_interface_hardening.py`](frp_m23_clock_reset_cdc_interface_hardening.py) | [`tests/test_frp_m23_clock_reset_cdc_interface_hardening.py`](tests/test_frp_m23_clock_reset_cdc_interface_hardening.py) | [`.github/workflows/frp-m23-clock-reset-cdc-interface-hardening-workflow.yml`](.github/workflows/frp-m23-clock-reset-cdc-interface-hardening-workflow.yml) |
| M24 | [`frp_m24_formal_bounded_verification.py`](frp_m24_formal_bounded_verification.py) | [`tests/test_frp_m24_formal_bounded_verification.py`](tests/test_frp_m24_formal_bounded_verification.py) | [`.github/workflows/frp-m24-formal-bounded-verification-closure-workflow.yml`](.github/workflows/frp-m24-formal-bounded-verification-closure-workflow.yml) |
| M25 | [`frp_m25_fault_negative_recovery_qualification.py`](frp_m25_fault_negative_recovery_qualification.py) | [`tests/test_frp_m25_fault_negative_recovery_qualification.py`](tests/test_frp_m25_fault_negative_recovery_qualification.py) | [`.github/workflows/frp-m25-fault-negative-path-recovery-qualification-workflow.yml`](.github/workflows/frp-m25-fault-negative-path-recovery-qualification-workflow.yml) |
| M26 | [`frp_m26_declared_target_implementation_evidence.py`](frp_m26_declared_target_implementation_evidence.py) | [`tests/test_frp_m26_declared_target_implementation_evidence.py`](tests/test_frp_m26_declared_target_implementation_evidence.py) | [`.github/workflows/frp-m26-declared-target-implementation-evidence-workflow.yml`](.github/workflows/frp-m26-declared-target-implementation-evidence-workflow.yml) |
| M27 | [`frp_m27_long_run_stability_telemetry_qualification.py`](frp_m27_long_run_stability_telemetry_qualification.py) | [`tests/test_frp_m27_long_run_stability_telemetry_qualification.py`](tests/test_frp_m27_long_run_stability_telemetry_qualification.py) | [`.github/workflows/frp-m27-long-run-stability-telemetry-qualification-workflow.yml`](.github/workflows/frp-m27-long-run-stability-telemetry-qualification-workflow.yml) |
| M28 | [`frp_m28_hierarchical_scaling_hotspot_containment.py`](frp_m28_hierarchical_scaling_hotspot_containment.py) | [`tests/test_frp_m28_hierarchical_scaling_hotspot_containment.py`](tests/test_frp_m28_hierarchical_scaling_hotspot_containment.py) | [`.github/workflows/frp-m28-hierarchical-scaling-hotspot-containment-closure-workflow.yml`](.github/workflows/frp-m28-hierarchical-scaling-hotspot-containment-closure-workflow.yml) |
| M29 | [`frp_m29_system_integration_downstream_compatibility.py`](frp_m29_system_integration_downstream_compatibility.py) | [`tests/test_frp_m29_system_integration_downstream_compatibility.py`](tests/test_frp_m29_system_integration_downstream_compatibility.py) | [`.github/workflows/frp-m29-system-integration-downstream-compatibility-closure-workflow.yml`](.github/workflows/frp-m29-system-integration-downstream-compatibility-closure-workflow.yml) |
| M30 | [`frp_m30_reproducibility_qualification_archival_closure.py`](frp_m30_reproducibility_qualification_archival_closure.py) | [`tests/test_frp_m30_reproducibility_qualification_archival_closure.py`](tests/test_frp_m30_reproducibility_qualification_archival_closure.py) | [`.github/workflows/frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml`](.github/workflows/frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml) |
| M31 | [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py) | [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py) | [`.github/workflows/frp-m31-complete.yml`](.github/workflows/frp-m31-complete.yml) |

M28 also publishes the one-way Observatory interchange through [`frp_m28_trace_observatory_upstream_interchange.py`](frp_m28_trace_observatory_upstream_interchange.py) and [`.github/workflows/frp-m28-trace-observatory-upstream-interchange-workflow.yml`](.github/workflows/frp-m28-trace-observatory-upstream-interchange-workflow.yml).

## Publication and Observatory Boundary

FRP is the source of canonical published bytes. FRP-Trace-Observatory consumes those bytes through a one-way, read-only boundary.

The boundary preserves:

- exact source bytes and digests;
- schema and artifact identifiers;
- release and milestone provenance;
- measurement-contour labels;
- deterministic ordering;
- upstream semantic authority in FRP.

The Observatory presents and qualifies the published boundary while FRP remains the owner of processor semantics, canonical artifacts, qualification evidence, and release records.

## Roadmap Maintenance Rule

Each future roadmap change carries its own versioned source, schema, canonical artifact, test, workflow, qualification record, validation index, release notes, and test report. Repository-facing documents are aligned only after the technical boundary is green.

Historical release records remain attached to the milestone that produced them. Evidence, benchmarks, schemas, manifests, qualification records, and archived packages retain their original bytes and provenance.

## Preserved Roadmap History Through M30

This roadmap defines the staged architecture progression of the Fractal Resonance Processor (FRP) project.

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Current validation status:

`PASS`

Qualified semantic and implementation-mapping foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Current RTL closure status:

`M16 RTL EXECUTION LAYER CLOSED`

Current FPGA preparation closure status:

`M16 FPGA PREPARATION LAYER CLOSED`

## 1. Purpose

The purpose of this roadmap is to preserve the FRP architecture trajectory from the executable balanced ternary reference layer through implementation mapping, domain interfaces, deterministic quantized execution, RTL correlation, qualification closure, executable SystemVerilog RTL realization, and target-independent FPGA preparation.

The primary project path is:

`balanced ternary computational kernel`

↓

`structured executable validation`

↓

`hardware-facing signal and trace layers`

↓

`RTL, formal, and FPGA-facing contracts`

↓

`production release and stable interface freeze`

↓

`silicon and heterogeneous implementation architecture`

↓

`tapeout, production integration, and external implementation handoff`

↓

`production iteration and stabilization`

↓

`physical implementation correlation and qualification`

↓

`fixed-point implementation mapping and qualification closure`

↓

`SystemVerilog RTL core realization and execution semantics`

↓

`target-independent FPGA integration and preparation qualification`

Comparative benchmark work remains a supporting validation contour. It does not replace or redefine the FRP architecture progression.

## 2. Current Architecture Layer

FRP v1.8.0 establishes the M16 RTL Core Realization and Execution Semantics Package layer of the Fractal Resonance Processor architecture.

M16 realizes the qualified M15 semantic and implementation-mapping boundary as:

`M15-qualified Python executable semantic reference`

↓

`M15 fixed-point and balanced ternary implementation map`

↓

`M16 SystemVerilog package and module realization`

↓

`temporal scheduler execution`

↓

`deterministic request-lane arbitration`

↓

`retained pending-route execution`

↓

`active-neutral transition routing`

↓

`distributed transition-capacity enforcement`

↓

`retained-state writeback`

↓

`SystemVerilog assertion execution`

↓

`executable RTL architectural simulation`

↓

`target-independent FPGA integration top`

↓

`asynchronous external reset assertion and two-stage synchronous reset release`

↓

`core-ready execution-input gating`

↓

`executable FPGA integration simulation`

M16 does not rename the Python executable semantic reference.

The retained semantic reference is:

`frp_prototype_v1_7_0.py`

## 3. Preserved Computational Kernel

FRP v1.8.0 retains the M15-qualified computational kernel.

Resonant phase model:

`Kuramoto-Sakaguchi resonant phase dynamics`

Preserved resonant and structural quantities include:

- oscillator phase;
- asymmetric phase lag gamma;
- hierarchical fractal coupling;
- phase evolution;
- resonance selection;
- Kuramoto order parameter `R(t)`;
- multiscale phase coherence;
- endogenous structural coherence `C(t)`;
- operational pressure `P(t)`;
- state-dependent delay dynamics;
- distributed local thermal dynamics;
- thermal coupling-factor evolution;
- local correlated gamma drift;
- nonlinear coherence compression;
- dynamic stability evaluation;
- phase-derived balanced ternary target formation.

Phase synchronization and phase coherence are not interchangeable.

`R(t)` is not identical to general endogenous structural coherence `C(t)`.

FRP operational `C(t)` and `P(t)` are processor-specific quantities.

Operational stability relation:

`C(t) > P(t)`

Thermal state participates in endogenous processor feedback.

Balanced ternary state and retained-result domain:

`{-1, 0, 1}`

Active neutral state:

`0`

Mandatory opposite-polarity routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Execution relation:

`tick N: active polarity → 0`

↓

`pending neutral route retained`

↓

`tick N+1 or later: 0 → target polarity`

Preserved scheduler modes:

- `free`;
- `7/1`;
- `1/7`.

Preserved transition control:

- transition-fraction control;
- deterministic request-lane ordering;
- bounded pending-neutral-route queue handling;
- reserved-state rejection.

Core validated invariant:

`actual_direct_events = 0`

Additional retained invariants:

`reserved_state_events = 0`

`queue_overflow_events = 0`

## 4. Qualified M15 Foundation

FRP v1.7.0 defines the qualified M15 semantic and implementation-mapping foundation retained by M16.

The M15 bridge is:

`M14 floating semantic reference`

↓

`M15 quantized hardware shadow model`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`SystemVerilog interface mapping`

↓

`RTL assertion correlation mapping`

↓

`qualification closure`

M15 defines ten artifact layers:

1. `fixed_point_interface_profile`;
2. `balanced_ternary_hardware_encoding_map`;
3. `quantized_reference_shadow_model`;
4. `cycle_exact_reference_trace`;
5. `rtl_comparison_vector_package`;
6. `systemverilog_testbench_interface_map`;
7. `synthesizable_rtl_reference_core`;
8. `rtl_assertion_correlation_harness`;
9. `reference_rtl_equivalence_report`;
10. `qualification_closure_manifest`.

M15 qualification result:

`41/41 PASS`

M15 deterministic qualification records:

| Qualification record | Result |
|---|---:|
| deterministic vector files | `10 / 10 byte-identical` |
| required semantic correlation matches | `5 / 5 = 1.0` |
| deterministic replay matches | `6 / 6 = 1.0` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |

M15 release-record validated commit:

`5fd9a4f`

M15 validated workflow stack recorded in `TEST_REPORT_v1_7_0.md`:

- `FRP Structured Output #113`;
- `FRP M15 Implementation Mapping and Qualification Closure #1`;
- `FRP Self Test #154`;
- `FRP Benchmark Smoke Test #152`.

M15 validation records:

- `TEST_REPORT_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`.

## 5. Current M16 RTL and FPGA Preparation Layers

M16 RTL source boundary:

1. `rtl/m16/frp_m16_pkg.sv`;
2. `rtl/m16/frp_m16_scheduler.sv`;
3. `rtl/m16/frp_m16_request_lanes.sv`;
4. `rtl/m16/frp_m16_pending_routes.sv`;
5. `rtl/m16/frp_m16_active_neutral.sv`;
6. `rtl/m16/frp_m16_capacity_guard.sv`;
7. `rtl/m16/frp_m16_state_update.sv`;
8. `rtl/m16/frp_m16_core.sv`;
9. `rtl/m16/frp_m16_assertions.sv`;
10. `rtl/m16/frp_m16_tb.sv`.

M16 RTL documentation boundary:

- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`.

M16 RTL execution domains:

- scheduler modes `free`, `7/1`, and `1/7`;
- deterministic request-lane arbitration;
- retained pending-route eligibility;
- active-neutral first-leg execution;
- pending-route completion from state `0`;
- distributed transition-capacity enforcement;
- retained-state writeback;
- counter clearing with retained state preserved;
- SystemVerilog assertion execution;
- ten integrated invariant flags.

M16 FPGA preparation boundary:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

M16 FPGA preparation domains:

- target-independent FPGA integration top;
- executable FPGA integration testbench;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- tick, counter-clear, and request-valid gating before readiness;
- scheduler propagation;
- request-interface propagation;
- active-neutral first-leg execution;
- retained pending-route completion;
- transition-capacity enforcement;
- retained-state writeback;
- ten integrated invariant flags.

M16 integrated invariant set:

1. `FRP_INV_STATE_DOMAIN_VALID`;
2. `FRP_INV_SCHEDULER_COUNTS_VALID`;
3. `FRP_INV_REQUEST_LANE_ORDER_VALID`;
4. `FRP_INV_PENDING_POLARITY_VALID`;
5. `FRP_INV_ACTIVE_NEUTRAL_VALID`;
6. `FRP_INV_TRANSITION_CAPACITY_VALID`;
7. `FRP_INV_STATE_UPDATE_VALID`;
8. `FRP_INV_NO_ACTUAL_DIRECT_EVENTS`;
9. `FRP_INV_NO_RESERVED_STATE`;
10. `FRP_INV_NO_QUEUE_OVERFLOW`.

Integrated invariant vector:

`1111111111`

## 6. Current Validation Evidence

Current validated release layer:

`FRP v1.8.0 — M16 RTL Core Realization and Execution Semantics Package`

Validation environment:

- `GitHub Actions`;
- Verilator SystemVerilog parsing and elaboration;
- executable compiled RTL testbench;
- executable compiled FPGA integration testbench;
- SystemVerilog assertion execution.

M16 RTL qualification records:

| Qualification record | Workflow run | Qualified commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |

M16 FPGA preparation qualification records:

| Qualification record | Workflow run | Qualified commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

M16 RTL terminal execution records:

| Record | Result |
|---|---:|
| cells | `8` |
| request lanes | `2` |
| `ticks_recorded` | `16` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

M16 FPGA preparation terminal execution records:

| Record | Result |
|---|---:|
| cells | `8` |
| request lanes | `2` |
| `core_ready` | `1` |
| `ticks_recorded` | `1` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

Current validation result:

`PASS`

Current validation records:

- `TEST_REPORT_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`.

## 7. Completed Architecture Progression

| Milestone | Version | Architecture layer | Status |
|---|---|---|---|
| M0 | v0.9.3-mobile | Repository stabilization | Completed |
| M1 | v0.9.3 release path | Archival release and DOI | Completed |
| M2 | v0.9.4 | Structured Output and Machine-Readable Validation | Completed |
| M3 | v0.9.5 | Benchmark Export and Hardware Signal Mapping | Completed |
| M4 | v0.9.6 | HDL Trace Export and Testbench Scaffold | Completed |
| M5 | v0.9.7 | RTL Interface Contract and Assertion Harness | Completed |
| M6 | v0.9.8 | Formal Verification Hooks and Equivalence Scaffold | Completed |
| M7 | v0.9.9 | FPGA Synthesis Package and Timing Constraint Scaffold | Completed |
| M8 | v1.0.0 | Production Release Package and Stable Interface Freeze | Completed |
| M9 | v1.1.0 | Silicon and Heterogeneous Implementation Architecture | Completed |
| M10 | v1.2.0 | Silicon Production and Tapeout Readiness Package | Completed |
| M11 | v1.3.0 | Production Integration and External Implementation Handoff | Completed |
| M12 | v1.4.0 | External Implementation Feedback and Production Iteration Loop | Completed |
| M13 | v1.5.0 | Production Scaling and Implementation Stabilization Package | Completed |
| M14 | v1.6.0 | Physical Implementation Correlation and Production Qualification Package | Completed |
| M15 | v1.7.0 | Implementation Mapping, Domain Interface, and Qualification Closure Package | Qualified semantic and implementation-mapping foundation |
| M16 | v1.8.0 | RTL Core Realization and Execution Semantics Package | Current RTL execution and FPGA preparation layer |

Historical release notes, test reports, and validation indices remain the release-specific source records for each completed layer.

## 8. Architecture Progression Through M16

The FRP architecture progression includes:

`production reference prototype`

↓

`stable production release package`

↓

`stable interface freeze`

↓

`silicon interface model`

↓

`heterogeneous implementation map`

↓

`compute fabric mapping`

↓

`memory/register interface map`

↓

`clock/reset domain map`

↓

`signal pipeline architecture`

↓

`accelerator integration profile`

↓

`FPGA-to-silicon migration path`

↓

`silicon production readiness manifest`

↓

`tapeout readiness checklist`

↓

`production integration and external implementation handoff`

↓

`external implementation feedback and production iteration`

↓

`production scaling and implementation stabilization`

↓

`hierarchical ultrametric topology model`

↓

`multiscale phase-coherence map`

↓

`cluster-local thermal field`

↓

`physical-domain correlation package`

↓

`fixed-point interface profile`

↓

`balanced ternary hardware encoding map`

↓

`quantized reference shadow model`

↓

`cycle-exact reference trace`

↓

`RTL comparison vector package`

↓

`SystemVerilog testbench interface map`

↓

`synthesizable RTL reference-core map`

↓

`RTL assertion correlation harness`

↓

`reference RTL equivalence report`

↓

`qualification closure manifest`

↓

`SystemVerilog RTL package and scheduler realization`

↓

`request-lane, pending-route, active-neutral, capacity, and state-update realization`

↓

`integrated RTL core and assertion boundary`

↓

`deterministic RTL testbench execution`

↓

`target-independent FPGA integration top`

↓

`FPGA reset synchronization and core-ready gating`

↓

`deterministic FPGA integration testbench execution`

## 9. Comparative Benchmark Role

The comparative architecture benchmark suite is a supporting validation layer.

Its role is to provide reproducible comparison profiles and sensitivity analysis without replacing the FRP architecture chain.

Benchmark contours remain separated:

- the original v0.9.3 transition and thermal benchmark;
- the v0.9.4 text and structured JSON benchmark;
- the v0.9.5–v1.3.0 M3 benchmark matrices;
- the v1.4.0 transition-pressure and feedback-stress matrix;
- the v1.5.0 thermal-survival and stability-boundary matrix;
- the v1.6.0 hierarchical scaling, acceleration, and hotspot-containment matrix;
- the v1.7.0 M15 implementation-mapping matrix;
- the Comparative Architecture Benchmark Suite;
- the Hardware-Informed Sensitivity Qualification;
- M16 RTL qualification;
- M16 FPGA preparation qualification.

The comparative benchmark layer is not an architecture milestone and does not alter the M0–M16 release progression.

Comparative benchmark schema:

`frp.benchmark.architecture_comparison.v1`

Canonical comparative result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`

Hardware-sensitivity schema:

`frp.benchmark.hardware_sensitivity_comparison.v1`

Canonical hardware-sensitivity result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`

Qualification policy:

`integrity_only_no_winner_assertions`

Winner assertions:

`[]`

Related repository paths:

- `benchmarks/architecture_comparison/`;
- `.github/workflows/frp-architecture-comparison.yml`;
- `.github/workflows/frp-hardware-sensitivity-comparison.yml`;
- `.github/workflows/frp-hardware-sensitivity-profile.yml`.

## 10. Current M16 Release Files

Current architecture document:

`docs/m16_rtl_core_realization_execution_semantics.md`

Qualified M15 foundation document:

`docs/m15_implementation_mapping_domain_interface_qualification_closure.md`

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Current foundation documents:

- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`.

Current RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Current FPGA preparation qualification workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Current M16 canonical-domain and repository-maintenance workflows:

- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`.

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current release-facing records:

- `TEST_REPORT_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`.

Current M16 qualification documents:

- `docs/m16_rtl_core_interface_contract.md`;
- `docs/m16_scheduler_state_rtl_realization.md`;
- `docs/m16_request_lane_arbitration_module.md`;
- `docs/m16_pending_route_register_module.md`;
- `docs/m16_active_neutral_transition_module.md`;
- `docs/m16_transition_capacity_guard_module.md`;
- `docs/m16_retained_state_update_module.md`;
- `docs/m16_balanced_ternary_state_register_map.md`;
- `docs/m16_invariant_assertion_set.md`;
- `docs/m16_external_simulator_execution_plan.md`;
- `docs/m16_m15_vector_replay_compatibility_report.md`;
- `docs/m16_rtl_artifact_boundary_qualification.md`;
- `docs/m16_artifact_boundary_test_stability_policy.md`;
- `docs/m16_qualification_manifest.md`;
- `docs/m16_qualification_index.md`;
- `docs/m16_public_status_snapshot.md`.

## 11. Repository Alignment Rule

When the current architecture layer changes, review the following files for version, milestone, validation, and architecture-boundary alignment:

- `README.md`;
- `ROADMAP.md`;
- `MILESTONES.md`;
- `PROJECT_STRUCTURE.md`;
- `CHANGELOG.md`;
- `INSTALL.md`;
- `USAGE.md`;
- `REPRODUCIBILITY.md`;
- `CI.md`;
- `CONTRIBUTING.md`;
- `docs/README.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- current Python executable semantic reference;
- current `TEST_REPORT`;
- current `RELEASE_NOTES`;
- current `FRP_VALIDATION_INDEX`;
- current architecture document;
- current qualification workflows;
- `rtl/m16/`;
- `fpga/m16/`;
- `tests/`.

The alignment review checks:

- current version;
- current milestone;
- current Python executable semantic-reference filename;
- current validation result;
- current structured-output and benchmark-matrix schemas;
- current workflow paths;
- complete computational kernel;
- M15 semantic and implementation-mapping foundation;
- M16 RTL and FPGA preparation boundaries;
- release-specific architecture traceability.

Historical release records must remain historical and must not be rewritten as current-state documents.

## 12. Current Status

FRP v1.8.0 currently records:

- the qualified M15 semantic and implementation-mapping foundation;
- deterministic hardware-facing numeric representations;
- balanced ternary hardware encoding;
- stateful quantized hardware shadow execution;
- cycle-exact reference traces;
- deterministic RTL comparison vectors;
- SystemVerilog testbench interface mapping;
- synthesizable RTL reference-core mapping;
- RTL assertion correlation mapping;
- floating semantic reference-to-quantized shadow correlation;
- exact deterministic quantized shadow replay;
- M15 qualification closure;
- ten M16 SystemVerilog RTL source files;
- five M16 RTL documentation artifacts;
- scheduler execution in `free`, `7/1`, and `1/7` modes;
- deterministic request-lane arbitration;
- retained pending-route execution;
- active-neutral transition routing;
- distributed transition-capacity enforcement;
- retained-state writeback;
- executable RTL architectural simulation;
- SystemVerilog assertion execution;
- ten integrated invariant flags;
- target-independent FPGA integration top;
- executable FPGA integration testbench;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- execution-input gating before readiness;
- scheduler and request-interface propagation;
- retained pending-route completion;
- M16 RTL qualification closure;
- M16 FPGA preparation qualification closure.

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Current M16 RTL qualification record:

| Record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#84` |
| Qualified source commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation qualification record:

| Record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#2` |
| Qualified repository commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

Current repository role:

`preserve the complete published Fractal Resonance Processor architecture from the balanced ternary computational kernel through structured validation, hardware-facing implementation mapping, deterministic quantized execution, RTL correlation, M15 qualification closure, M16 SystemVerilog RTL execution, and target-independent FPGA preparation`

## 13. Planned Architecture Progression from M17 through M30

The current qualified repository boundary remains:

`FRP v1.8.0 / M16`

The milestones below are planned architecture targets. They are not implementation claims, qualification results, release records, or evidence that the corresponding artifacts already exist.

The planned version assignments remain provisional until each milestone has:

- implemented repository artifacts;
- deterministic producer commands;
- canonical machine-readable outputs;
- declared digests;
- validation logic;
- automated tests;
- qualification workflows;
- successful workflow evidence;
- release-specific documentation;
- validation-index alignment.

FRP remains the only source of truth for processor semantics.

Downstream tools may read, validate, correlate, and visualize published FRP artifacts. Upstream FRP qualification must not import, execute, or depend on downstream implementation code.

Published measurement contours must remain separate. Operation count, thermal proxy, transition pressure, `heat_peak`, scheduler timing, latency, throughput, RTL execution, implementation-tool results, and physical measurements must not be represented as interchangeable quantities.

Target-independent FPGA preparation evidence must not be represented as physical-chip evidence.

### M17 — Published Artifact Integration Contract

Provisional release target:

`v1.9.0`

Qualification boundary status:

`M17 QUALIFICATION BOUNDARY CLOSED`

Qualification result:

`PASS`

Machine-readable inventory milestone state:

`planned`

Primary objective:

`define the normative one-way publication boundary between FRP and downstream artifact consumers`

Qualified scope:

- published artifact classes are defined;
- canonical source paths are recorded;
- existing producer commands are identified;
- exact existing schema identifiers are recorded;
- required and optional fields are distinguished where the upstream source defines them;
- immutable source-byte handling is defined;
- digest declaration and verification rules are defined;
- artifact provenance requirements are defined;
- deterministic artifact-set ordering is defined;
- compatibility-registry requirements are defined;
- unsupported and incomplete artifact behavior is defined;
- upstream and downstream responsibility boundaries are defined;
- existing processor semantics remain unchanged;
- `free`, `7/1`, and `1/7` remain distinct scheduler-mode identities;
- the `7/1` sequence remains seven `balance` ticks followed by one `commit` tick;
- the `1/7` sequence remains one `excite` tick followed by seven `neutralize` ticks.

Qualified evidence:

- integration contract: `docs/m17_published_artifact_integration_contract.md`;
- deterministic inventory generator: `frp_m17_publication_inventory.py`;
- inventory schema: `frp.m17.published_artifact_inventory.v1.9.0`;
- self-test schema: `frp.m17.published_artifact_inventory.self_test.v1.9.0`;
- inventory records: `63`;
- exact schema identifiers: `17`;
- built-in inventory self-test: `25 / 25 PASS`;
- dependency-free unit-test suite: `30 / 30 PASS`;
- deterministic inventory renderings: `2 / 2 byte-identical`;
- qualification workflow: `.github/workflows/frp-m17-published-artifact-integration.yml`;
- workflow run: `#1`;
- qualified commit: `08e5714`;
- workflow result: `SUCCESS`;
- repository immutability result: `PASS`;
- qualification record: `docs/m17_published_artifact_integration_qualification.md`;
- closure record: `docs/m17_published_artifact_integration_closure.md`;
- downstream-code independence: `PASS`.

Release boundary:

- the current published release remains `FRP v1.8.0 / M16`;
- `v1.9.0` remains a provisional release target;
- the qualified inventory continues to record `milestone_state` as `planned`;
- M17 qualification closure does not publish an M17 release;
- M18 receives the qualified M17 contract, inventory, provenance, and publication-state records as its baseline.

### M18 — Formal Schema and Canonical Artifact Publication

Provisional release target:

`v2.0.0`

Primary objective:

`publish formally validated canonical machine-readable artifacts for the existing structured-output and M15 layers`

Required scope:

- formal schemas for supported structured JSON outputs;
- formal schemas for supported benchmark matrices;
- canonical structured-output artifacts;
- canonical benchmark-matrix artifacts;
- committed M15 implementation-mapping JSON artifacts;
- committed M15 deterministic vector fixtures;
- committed M15 trace fixtures;
- committed M15 preload and lookup-table fixtures;
- committed digest manifests;
- canonical CSV exports where a stable tabular representation is defined;
- producer-command recording;
- deterministic byte-for-byte regeneration checks;
- canonical fixture provenance.

The canonical ternary processor domain remains:

`-1, 0, 1`

Closure requires:

- formal validation of every published canonical artifact;
- complete committed M15 artifact and vector sets;
- exact digest verification;
- deterministic regeneration evidence;
- negative tests for missing fields, invalid types, invalid values, and non-canonical ternary states;
- qualification workflow success.

### M19 — Machine-Readable M16 Execution and Qualification Evidence

Provisional release target:

`v2.1.0`

Primary objective:

`publish machine-readable M16 RTL and FPGA-preparation execution evidence`

Required scope:

- tick-ordered RTL execution records;
- scheduler mode and scheduler-state records;
- request-lane acceptance and rejection records;
- retained ternary state;
- phase-derived targets;
- pending-route state and completion records;
- transition-capacity telemetry;
- switching-load telemetry;
- thermal-state proxy telemetry;
- coherence and pressure quantities;
- `actual_direct_events`;
- `reserved_state_events`;
- `queue_overflow_events`;
- invariant vectors;
- zero-event qualification records;
- RTL qualification manifests;
- FPGA-preparation qualification manifests;
- producer version and source commit records;
- declared artifact digests.

Closure requires:

- exact machine-readable schema identifiers;
- trace-order and tick-order validation;
- scheduler-counter relation checks;
- transition-capacity relation checks;
- pending-route relation checks;
- invariant-vector validation;
- digest verification;
- deterministic artifact-set validation;
- successful RTL and FPGA-preparation qualification workflows.

### M20 — Cross-Layer Deterministic Correlation

Provisional release target:

`v2.2.0`

Primary objective:

`correlate the M15 semantic and implementation-mapping layers with M16 RTL and FPGA-preparation execution`

Required scope:

- deterministic semantic-reference inputs;
- quantized-shadow expected values;
- M15 vector identities;
- M16 RTL observed values;
- FPGA-preparation observed values;
- tick and lane correlation;
- retained-state correlation;
- pending-route correlation;
- scheduler-state correlation;
- transition-capacity correlation;
- invariant correlation;
- explicit mismatch records;
- exact source and result digests.

Closure requires:

- byte-stable correlation packages;
- zero unexplained comparison mismatches;
- machine-readable PASS or failure records;
- tests for deliberately altered vectors and digests;
- independent rerun evidence;
- successful correlation workflow execution.

### M21 — Parameterized Qualification Matrix

Provisional release target:

`v2.3.0`

Primary objective:

`qualify declared parameter combinations without mixing measurement contours`

Required scope:

- cell-count configurations;
- request-lane configurations;
- scheduler modes;
- scheduler parameters;
- transition-capacity configurations;
- retained-route configurations;
- deterministic workload identities;
- explicit matrix dimensions;
- explicit unsupported combinations;
- per-case provenance;
- per-case digests;
- per-case qualification status.

Closure requires:

- deterministic matrix generation;
- complete declared-case coverage;
- explicit skipped-case reasons;
- no silent parameter substitution;
- no cross-contour metric substitution;
- successful matrix qualification workflows.

### M22 — Control, Status, and Register Interface Realization

Provisional release target:

`v2.4.0`

Primary objective:

`realize a deterministic integration-facing control and status boundary around the qualified execution core`

Required scope:

- control-field definitions;
- status-field definitions;
- register-address mapping;
- reset values;
- access permissions;
- scheduler configuration exposure;
- request submission exposure;
- retained-state observation;
- pending-route observation;
- transition-capacity observation;
- invariant-status observation;
- deterministic read and write behavior;
- invalid-access behavior;
- machine-readable interface description.

Closure requires:

- executable interface tests;
- reset-value verification;
- access-policy verification;
- deterministic transaction traces;
- invalid-access qualification;
- schema and digest coverage for published interface artifacts;
- successful interface qualification workflow.

### M23 — Clock, Reset, CDC, and Interface Hardening

Provisional release target:

`v2.5.0`

Primary objective:

`qualify declared clock, reset, and interface behavior at the integration boundary`

Required scope:

- asynchronous reset assertion behavior;
- synchronous reset release behavior;
- `core_ready` sequencing;
- input gating before readiness;
- declared clock-domain boundaries;
- declared synchronization boundaries;
- stable interface handshakes;
- reset interruption behavior;
- deterministic restart behavior;
- interface protocol assertions;
- machine-readable qualification records.

Closure requires:

- reset-sequence coverage;
- restart determinism;
- interface assertion success;
- declared CDC checks;
- negative tests for invalid sequencing;
- workflow-retained logs and reports;
- successful hardening qualification workflows.

### M24 — Formal and Bounded Verification Closure

Provisional release target:

`v2.6.0`

Primary objective:

`close declared formal and bounded properties for the qualified RTL boundary`

Required scope:

- canonical ternary-state properties;
- active-neutral transition properties;
- pending-route preservation properties;
- scheduler-counter properties;
- request-lane arbitration properties;
- transition-capacity properties;
- retained-state update properties;
- invariant-flag properties;
- reset and readiness properties;
- bounded liveness properties where explicitly declared;
- proof assumptions;
- proof bounds;
- tool and version provenance;
- machine-readable proof summaries.

Closure requires:

- explicit property inventory;
- no unrecorded assumptions;
- reproducible proof commands;
- PASS records for every required property;
- retained counterexamples for expected negative tests;
- digest-bound proof reports;
- successful formal qualification workflows.

### M25 — Fault, Negative-Path, and Recovery Qualification

Provisional release target:

`v2.7.0`

Primary objective:

`qualify declared invalid, constrained, deferred, and recovery paths`

Required scope:

- invalid ternary inputs;
- rejected request lanes;
- scheduler deferral;
- transition-capacity deferral;
- retained pending polarity;
- pending-route completion;
- queue-overflow behavior;
- invalid configuration behavior;
- reset during pending execution;
- digest mismatch detection;
- malformed artifact rejection;
- incomplete qualification-package handling;
- deterministic recovery behavior.

Closure requires:

- explicit expected outcomes;
- no arbitrary code execution by artifact validators;
- deterministic negative fixtures;
- machine-readable failure classification;
- recovery-state verification;
- complete negative-path test evidence;
- successful fault and recovery qualification workflows.

### M26 — Declared-Target Implementation Evidence

Provisional release target:

`v2.8.0`

Primary objective:

`produce reproducible implementation-tool evidence bound to explicitly named targets and constraints`

Required scope:

- declared implementation target;
- declared tool and version;
- declared constraints;
- synthesis command provenance;
- timing command provenance;
- resource-report provenance;
- implementation warnings;
- result digests;
- reproducibility records;
- separation from target-independent FPGA preparation;
- separation from physical measurements.

Closure requires:

- reproducible tool execution;
- retained machine-readable reports;
- explicit target and constraint binding;
- no universal physical-chip claim;
- no conversion of proxy values into physical measurements;
- successful declared-target qualification workflows.

### M27 — Long-Run Stability and Telemetry Qualification

Provisional release target:

`v2.9.0`

Primary objective:

`qualify deterministic long-run execution and published telemetry relations`

Required scope:

- long-run scheduler execution;
- long-run pending-route behavior;
- long-run transition-capacity behavior;
- switching-load telemetry;
- thermal-state proxy telemetry;
- transition-pressure telemetry;
- coherence telemetry;
- stability-boundary records;
- zero-event intervals;
- deterministic checkpoint digests;
- bounded artifact size and retention policy;
- exact workload identity.

Closure requires:

- deterministic reruns;
- ordered checkpoint records;
- validated counter relations;
- validated telemetry types and domains;
- explicit proxy labeling;
- no unsupported physical interpretation;
- successful long-run qualification workflows.

### M28 — Hierarchical Scaling and Hotspot-Containment Realization

Provisional release target:

`v3.0.0`

Primary objective:

`realize and qualify declared hierarchical execution and containment boundaries`

Required scope:

- declared hierarchy topology;
- cluster identities;
- cell-to-cluster mapping;
- cluster-local scheduler observation;
- cluster-local transition-capacity observation;
- cluster-local telemetry;
- hotspot-containment indicators;
- hierarchy-level provenance;
- deterministic scaling matrices;
- explicit aggregation equations;
- preserved measurement-contour separation.

Closure requires:

- deterministic hierarchy construction;
- validated aggregation relations;
- no undeclared metric aggregation;
- canonical scaling fixtures;
- machine-readable qualification manifests;
- reproducible workflow evidence;
- no unsupported physical-hardware claim.

### M29 — System Integration and Downstream Compatibility Closure

Provisional release target:

`v3.1.0`

Primary objective:

`close the published integration boundary without coupling FRP qualification to downstream implementation code`

Required scope:

- supported schema registry;
- supported artifact registry;
- compatibility-version declarations;
- canonical demo artifact package;
- deterministic package manifest;
- producer-command registry;
- immutable source-artifact policy;
- provenance completeness;
- unsupported-version behavior;
- downstream-consumption test vectors;
- release-independent compatibility records.

Closure requires:

- complete upstream publication inventory;
- exact schema and artifact identifiers;
- deterministic canonical package generation;
- digest verification;
- compatibility tests using published bytes;
- no downstream semantic reimplementation;
- no upstream dependency on downstream code;
- successful integration-boundary workflows.

### M30 — Reproducibility, Qualification, and Archival Release Closure

Provisional release target:

`v3.2.0`

Primary objective:

`close the planned M17 through M30 architecture progression with reproducible qualification and archival evidence`

Required scope:

- complete milestone evidence index;
- complete schema index;
- complete canonical artifact index;
- complete producer-command index;
- complete workflow index;
- complete qualification-manifest index;
- complete digest inventory;
- deterministic clean-environment reproduction;
- release-package construction;
- release-package verification;
- archival metadata;
- release-specific test report;
- release-specific validation index;
- release-specific release notes;
- repository-wide version and terminology alignment.

Closure requires:

- all required M17 through M29 gates closed;
- all required workflows recorded as successful;
- all canonical artifacts reproduced and digest-verified;
- all supported schemas validated;
- all qualification manifests internally consistent;
- all measurement contours preserved;
- all current-state documents aligned;
- all historical records preserved unchanged;
- no unqualified release claim;
- no unsupported physical-chip claim.

Until these closure conditions are met, M30 remains a planned milestone and FRP v1.8.0 / M16 remains the current qualified repository boundary.
