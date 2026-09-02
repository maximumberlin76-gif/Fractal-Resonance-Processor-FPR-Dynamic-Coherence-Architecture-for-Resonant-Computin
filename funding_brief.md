# Funding Brief — Fractal Resonance Processor (FRP)

## Current Funding and Engineering Brief — FRP v3.3.0 / M31

This section defines the current funding-facing technical boundary for the Fractal Resonance Processor. The complete funding brief through M16, including its version-specific engineering scopes and archival DOI record, remains preserved below this section.

| Control field | Current value |
|---|---|
| Repository release | FRP v3.3.0 |
| Current milestone | M31 |
| Qualification state | PASS |
| Balanced ternary domain | `-1/0/1` |
| Neutral-state role | active mediation, routing, retention, and controlled transition staging |
| Focused M31 qualification | 60 / 60 PASS |
| Current validation index | [FRP_VALIDATION_INDEX_v3_3_0.md](FRP_VALIDATION_INDEX_v3_3_0.md) |
| Current release notes | [RELEASE_NOTES_v3_3_0.md](RELEASE_NOTES_v3_3_0.md) |
| Current test report | [TEST_REPORT_v3_3_0.md](TEST_REPORT_v3_3_0.md) |

## Current Technical Baseline

The current public repository records a connected processor, implementation, evidence, benchmark, and release history through M31. The active M31 boundary adds executable phase-interference and active-zero thermal evidence to the preserved earlier semantic, fixed-point, SystemVerilog, FPGA-preparation, interface, archival, and qualification layers.

The current M31 publication set consists of:

- executable source: [frp_m31_phase_interference_thermal_evidence.py](frp_m31_phase_interference_thermal_evidence.py);
- focused qualification: [tests/test_frp_m31_phase_interference_thermal_evidence.py](tests/test_frp_m31_phase_interference_thermal_evidence.py);
- validation schema: [schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json);
- evidence record: [artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json);
- manifest: [artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json);
- qualification record: [artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json);
- completion workflow: [.github/workflows/frp-m31-complete.yml](.github/workflows/frp-m31-complete.yml).

The current documentation and review surface is recorded in [README.md](README.md), [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md), [MILESTONES.md](MILESTONES.md), [CI.md](CI.md), and [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Current Validated Asset Classes

| Asset class | Current repository record |
|---|---|
| Processor semantics | executable Python references, focused tests, structured records, and preserved qualification history |
| Balanced ternary execution | `-1/0/1`, active state `0`, pending-route state, and tick-separated opposite-polarity transition paths |
| Phase and coherence execution | phase evolution, resonance selection, phase order, multiscale coherence, retained state, and scheduler-controlled execution |
| Thermal evidence | M31 phase-interference and active-zero thermal-evidence source, schema, evidence, manifest, and qualification record |
| Reproducibility | declared dependencies, deterministic commands, schema validation, digests, manifests, and GitHub Actions records |
| SystemVerilog | versioned RTL, testbench, assertion, interface, reset, CDC, integration, and declared-target contours |
| FPGA preparation | versioned target-independent integration and execution-gating records |
| Benchmarks | preserved definitions, structured results, metric domains, workload identities, and qualification records |
| Release engineering | validation indices, release notes, test reports, archival packages, workflow records, and historical digests |
| Downstream observability | published FRP contracts consumed through a one-way read-only Observatory boundary |

Versioned SystemVerilog assets are currently recorded under [rtl/m16/](rtl/m16/), [fpga/m16/](fpga/m16/), [rtl/m22/](rtl/m22/), [rtl/m23/](rtl/m23/), and [rtl/m26/](rtl/m26/). Their version-local source, test, interface, simulation, and closure records define the implementation evidence available for engineering review.

## Funding Objective

Funding supports the conversion of the current qualified repository baseline into additional complete engineering, verification, target-integration, measurement, observability, and release contours while preserving correlation with published processor semantics and evidence.

The current funding objective covers:

- complete M31 SystemVerilog realization, testbench, assertion, simulation, and qualification packaging;
- target-specific FPGA integration, synthesis, placement, routing, timing, and telemetry capture;
- cycle-exact comparison between executable references, RTL, and selected target execution;
- physical timing, energy, thermal, and transition-event measurement;
- independent reproduction and engineering audit of published evidence;
- ASIC-oriented datapath, storage, clocking, control, interface, and implementation studies;
- read-only FRP Trace Observatory contract integration and downstream visualization qualification;
- archival packaging, release metadata, citation metadata, and partner-review documentation.

Each funded contour is represented by explicit source, tests, configuration, generated records, schemas, manifests, qualification evidence, and acceptance criteria.

## Engineering Work Packages

### Work Package 1 — M31 SystemVerilog Realization and Qualification

Deliverables:

- versioned M31 RTL package and interfaces;
- synthesizable execution modules connected to the M31 semantic boundary;
- explicit retained-state, pending-route, active-zero, and transition-capacity handling;
- assertions covering direct opposite-polarity transitions, reserved states, queue conditions, and interface invariants;
- deterministic testbench stimuli and expected results;
- simulator command record and complete transcript;
- source-to-reference comparison record;
- qualification manifest, test report, closure record, and manual GitHub Actions workflow.

Acceptance is tied to exact source identities, deterministic simulator output, passing assertions, declared test counts, and a green qualification workflow on `main`.

### Work Package 2 — Target-Specific FPGA Integration

Deliverables:

- selected device and development-board record;
- versioned clock, reset, pin, constraint, and memory-interface mapping;
- synthesis, placement-and-routing, utilization, and timing reports;
- target image and reproducible build procedure;
- telemetry transport and capture configuration;
- retained-state and transition-event correlation against the qualified reference boundary;
- target-specific qualification manifest and closure report.

### Work Package 3 — Physical Correlation and Measurement

Deliverables:

- controlled workload and parameter registry;
- calibrated timing, power, energy, and thermal measurement setup;
- raw measurement records and processing procedure;
- binary and ternary comparison records with explicit metric-domain separation;
- repeatability and uncertainty records;
- phase, coherence, retained-state, switching-load, and thermal correlation report;
- independently reviewable evidence package.

### Work Package 4 — Trace Observatory Integration

Deliverables:

- versioned FRP publication contract and schema registry;
- deterministic downstream intake fixtures;
- Trace Explorer integration;
- Ternary Transition Visualizer integration;
- Artifact Auditor integration;
- schema, digest, manifest, and qualification checks;
- downstream test and release package.

FRP remains the authoritative producer. Observatory consumes published artifacts through a one-way read-only boundary and does not alter canonical FRP source, schema, evidence, manifest, qualification, or benchmark records.

### Work Package 5 — Independent Reproduction and Technical Audit

Deliverables:

- clean-environment reproduction record;
- dependency and toolchain inventory;
- source and artifact digest verification;
- focused and repository-level test execution;
- schema-validation report;
- benchmark and evidence provenance audit;
- SystemVerilog and FPGA contour review;
- discrepancy register and traceable resolution records.

### Work Package 6 — ASIC-Oriented Engineering Study

Deliverables:

- datapath and state-storage partitioning;
- fixed-point and lookup implementation analysis;
- phase-coupling, coherence, thermal, and retained-state mapping;
- scheduler, request-lane, pending-route, and capacity-control mapping;
- clock, reset, CDC, observability, and test architecture;
- power, performance, area, and implementation-risk study;
- reference-equivalence and verification plan.

### Work Package 7 — Release and Archival Closure

Deliverables:

- final repository audit;
- validation index, release notes, test report, and release checklist;
- deterministic archival package and manifest;
- GitHub release and tag;
- archival repository submission and metadata synchronization;
- citation record and public review package.

Release and citation metadata are finalized after the technical, documentation, and qualification identities are stable.

## Resource Categories

| Resource category | Technical function |
|---|---|
| RTL engineering | M31 module realization, interface definition, synthesis discipline, and semantic correlation |
| Verification engineering | assertions, deterministic tests, simulator execution, coverage, and closure |
| FPGA engineering | device integration, synthesis, timing, constraints, telemetry, and target qualification |
| ASIC architecture | datapath, storage, control, clocking, reset, interfaces, test, and implementation study |
| Numerical implementation | fixed-point mapping, lookup methods, coupling, coherence, thermal, and retained-state execution |
| Measurement engineering | calibrated timing, power, energy, thermal, and signal capture |
| Software engineering | executable references, schemas, export tooling, reproducibility, and automated validation |
| Observatory engineering | read-only intake, trace exploration, transition visualization, and artifact audit |
| Independent review | clean reproduction, provenance audit, discrepancy analysis, and technical verification |
| Release engineering | archival packages, manifests, metadata, workflow records, and publication closure |
| Legal and IP support | licensing, collaboration scope, background-IP records, and partner agreements |

## Partner and Review Interface

Relevant review and collaboration domains include:

- balanced ternary processor architecture and active-zero execution;
- phase-interference, resonance, coherence, retention, and thermal-evidence analysis;
- SystemVerilog RTL and assertion-based verification;
- FPGA and ASIC engineering;
- physical measurement and laboratory correlation;
- reproducible scientific software and schema validation;
- benchmark design and metric-domain audit;
- downstream trace exploration, visualization, and artifact auditing;
- archival publication, research infrastructure, and technical due diligence.

Partner review uses repository paths, exact versions, declared workloads, measured quantities, workflow results, manifests, and digests. Proposed deliverables and qualified results remain separately identified throughout review.

The public repository license is defined in [LICENSE](LICENSE). Project-specific funding, engineering, confidentiality, background-IP, jointly developed IP, manufacturing, and publication terms are recorded in the corresponding external agreement.

## Evidence and History Protection

Funding-supported changes preserve all existing evidence, benchmark, schema, RTL, FPGA, workflow, and release histories. New results are added as separately named and versioned records with explicit provenance.

Protected repository classes include:

- [artifacts/](artifacts/);
- [benchmarks/](benchmarks/);
- [schemas/](schemas/);
- versioned [RTL](rtl/) and [FPGA](fpga/) contours;
- validation indices, release notes, test reports, and release checklists;
- current governance records in [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

Acceptance records identify the exact files changed and confirm the byte identity of protected histories outside the funded contour.

## Current Funding Review Package

The current technical review package consists of:

- [USAGE.md](USAGE.md);
- [INSTALL.md](INSTALL.md);
- [ROADMAP.md](ROADMAP.md);
- [CHANGELOG.md](CHANGELOG.md);
- [NOTICE.md](NOTICE.md);
- the M31 validation index, release notes, and test report;
- the M31 executable source, focused tests, schema, evidence, manifest, and qualification record;
- preserved benchmark, SystemVerilog, FPGA, archival, and release histories.

This package provides the current repository evidence for engineering scope definition, partner review, independent reproduction, funding evaluation, and subsequent statement-of-work preparation.

## Preserved Funding Brief Through M16

**Ternary Fractal Resonant Coherence Processor**

**Ternary Resonant Coherence Processor — Structured Output Prototype**

This document defines the funding and partner-facing brief for the Fractal Resonance Processor (FRP) project.

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Qualified semantic and implementation-mapping foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Current public repository package:

`executable semantic reference, structured output, reproducibility, verification, benchmark, comparative architecture, hardware-sensitivity, deterministic implementation mapping, executable SystemVerilog RTL, target-independent FPGA preparation, qualification, documentation, governance, and release-evidence layers`

Current executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Current test report:

`TEST_REPORT_v1_8_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

Current release checklist:

`RELEASE_CHECKLIST_v1_8_0.md`

Current primary qualification workflows:

- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`.

Current published validation result:

`PASS`

Qualified M15 self-test result:

`41/41 PASS`

Current M16 RTL status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation status:

`M16 FPGA PREPARATION LAYER CLOSED`

Current DOI:

`10.5281/zenodo.21183966`

## 1. Executive Summary

Fractal Resonance Processor (FRP) is a Ternary Fractal Resonant Coherence Processor architecture.

The current public repository establishes the FRP v1.8.0 M16 RTL Core Realization and Execution Semantics Package.

M15 remains the qualified semantic and implementation-mapping foundation of M16.

The current computational chain is:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`cell phase and frequency state`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric Sakaguchi phase lag gamma`

↓

`dyadic hierarchical fractal coupling`

↓

`phase velocity and phase evolution`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`stateful delay dynamics`

↓

`distributed local thermal dynamics`

↓

`correlated local gamma drift`

↓

`nonlinear coherence compression`

↓

`dynamic stability C(t) - P(t)`

↓

`phase-derived ternary target`

↓

`distributed ternary commit`

↓

`mandatory tick-separated routing through active neutral state 0`

↓

`retained coherent ternary state`

↓

`M15 deterministic fixed-point implementation mapping`

↓

`M15 cycle-exact trace and RTL comparison-vector qualification`

↓

`M16 executable SystemVerilog RTL core`

↓

`M16 target-independent FPGA integration boundary`

↓

`M16 RTL and FPGA preparation qualification closure`

The current public package includes:

- the executable FRP v1.7.0 semantic reference;
- balanced ternary state and retained-result logic;
- active neutral transition routing;
- distributed commit behavior;
- Kuramoto-Sakaguchi resonant phase dynamics;
- hierarchical fractal coupling;
- multiscale phase coherence;
- nonlinear coherence compression;
- delay dynamics;
- distributed local thermal dynamics;
- correlated gamma dynamics;
- scheduler modes;
- structured per-tick and per-cell telemetry;
- deterministic fixed-point interface mapping;
- canonical balanced ternary hardware encoding;
- stateful quantized hardware-shadow execution;
- cycle-exact integer golden traces;
- deterministic RTL comparison vectors;
- SystemVerilog interface mapping;
- synthesizable RTL reference-core mapping;
- RTL assertion correlation;
- floating-to-quantized reference equivalence;
- exact deterministic replay;
- M15 qualification closure;
- ten integrated M16 SystemVerilog RTL artifacts;
- executable Verilator elaboration, build, and architectural simulation;
- deterministic request-lane arbitration;
- retained pending-route execution;
- active-neutral opposite-polarity routing;
- distributed transition-capacity enforcement;
- retained balanced ternary state writeback;
- SystemVerilog assertion execution;
- ten integrated M16 invariant flags;
- a target-independent FPGA integration top;
- an executable FPGA integration testbench;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` execution-input gating;
- M16 RTL qualification closure;
- M16 FPGA preparation qualification closure;
- comparative architecture benchmarking;
- hardware-sensitivity qualification;
- reproducibility commands;
- automated GitHub Actions validation;
- mathematical and physical foundation documents;
- release, governance, security, and partner-facing documentation.

The current M16 package provides the repository baseline for funding scopes that include:

- FRP v1.8.0 archival release and DOI synchronization;
- target-specific FPGA integration;
- FPGA synthesis and timing analysis;
- target-specific clock, reset, pin, and constraint integration;
- cycle-exact FPGA correlation;
- FPGA telemetry capture;
- physical timing, energy, and thermal measurement;
- ASIC-oriented implementation study;
- physical validation protocol execution;
- laboratory collaboration;
- independent engineering review;
- engineering partnership;
- grant review;
- investor-facing technical review;
- release and partner-review package preparation.

## 2. Project Position

FRP v1.8.0 establishes the current M16 RTL Core Realization and Execution Semantics Package.

The current project position is:

`validated floating semantic reference`

↓

`validated quantized hardware shadow`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`SystemVerilog interface mapping`

↓

`synthesizable RTL reference-core mapping`

↓

`RTL assertion correlation`

↓

`reference equivalence`

↓

`M15 qualification closure PASS`

↓

`M16 integrated SystemVerilog execution core`

↓

`M16 executable architectural testbench`

↓

`M16 integrated invariant execution`

↓

`M16 RTL qualification closure PASS`

↓

`M16 target-independent FPGA integration top`

↓

`M16 executable FPGA integration testbench`

↓

`M16 FPGA preparation qualification closure PASS`

The current repository provides the executable semantic reference, deterministic implementation-mapping artifacts, RTL source boundary, FPGA preparation boundary, qualification workflows, and release evidence for staged engineering and partner review.

## 3. Current Validated Assets

Current validated assets include:

| Asset | Status |
|---|---|
| FRP v1.7.0 executable semantic reference | complete |
| Python compilation | PASS |
| structured-output schema `frp.structured_output.v1.7.0` | stable |
| benchmark-matrix schema `frp.m3.benchmark_matrix.v1.7.0` | stable |
| M15 41-check self-test | 41/41 PASS |
| default 64-tick semantic execution | PASS |
| `free` scheduler profile | PASS |
| `7/1` scheduler profile | PASS |
| `1/7` scheduler profile | PASS |
| 8-cell scaling profile | PASS |
| 16-cell scaling profile | PASS |
| 32-cell scaling profile | PASS |
| balanced ternary state domain | PASS |
| active-neutral opposite-polarity routing | PASS |
| fixed-point topology closure | exact |
| fixed-point thermal closure | exact |
| M15 artifact layer count | 10 |
| quantized hardware-shadow model | qualified |
| cycle-exact reference trace | qualified |
| deterministic RTL vector package | qualified |
| independent vector regeneration | 10/10 byte-identical |
| SystemVerilog interface map | qualified |
| synthesizable RTL reference-core map | qualified |
| RTL assertion-correlation harness | 13 domains |
| floating-to-quantized semantic correlation | 5/5 matches = 1.0 |
| exact quantized deterministic replay | 6/6 matches = 1.0 |
| M15 qualification closure manifest | PASS |
| five-row M15 benchmark matrix | qualified |
| M16 SystemVerilog source artifacts | 10 |
| M16 RTL documentation artifacts | 5 |
| M16 artifact-manifest test | PASS |
| Verilator parsing and module elaboration | PASS |
| executable M16 RTL testbench generation | PASS |
| M16 architectural simulation | PASS |
| M16 SystemVerilog assertion execution | PASS |
| inferred latch diagnostics | 0 |
| multidriven diagnostics | 0 |
| M16 scheduler execution | PASS |
| deterministic request-lane arbitration | PASS |
| retained pending-route execution | PASS |
| active-neutral route execution | PASS |
| transition-capacity enforcement | PASS |
| retained-state writeback | PASS |
| M16 integrated invariant flags | 10/10 equal to 1 |
| M16 RTL repository integrity | PASS |
| M16 RTL qualification evidence | PASS |
| M16 FPGA SystemVerilog artifacts | 2 |
| M16 FPGA documentation artifacts | 2 |
| inherited M16 RTL dependencies | 9 |
| FPGA integration-top elaboration | PASS |
| executable FPGA integration testbench | PASS |
| asynchronous external reset assertion | PASS |
| two-stage synchronous reset release | PASS |
| `core_ready` generation | PASS |
| execution-input gating before readiness | PASS |
| FPGA scheduler propagation | PASS |
| FPGA request-interface propagation | PASS |
| FPGA active-neutral first-leg execution | PASS |
| FPGA retained pending-route completion | PASS |
| FPGA integrated invariant flags | 10/10 equal to 1 |
| M16 FPGA repository integrity | PASS |
| M16 FPGA qualification evidence | PASS |
| Comparative Architecture Benchmark Suite | qualified |
| hardware-sensitivity profile | PASS |
| hardware-sensitivity comparison | PASS |
| mathematical foundation | present |
| physical foundation | present |
| M16 architecture and qualification documents | 17 |
| GitHub Actions workflow files | 23 |
| CI workflow badges | 23 |
| test report | complete |
| validation index | complete |
| release notes | complete |
| release checklist | complete |
| reproducibility guide | complete |
| usage guide | complete |
| installation guide | complete |
| output schema documentation | present |
| CI documentation | complete |
| benchmark interpretation guide | complete |
| architecture documentation | complete |
| implementation layers documentation | complete |
| verification documentation | complete |
| model registry | complete |
| simulation record layer | complete |
| examples layer | complete |
| Code of Conduct | current |
| security policy | current |
| citation metadata | present |
| Apache-2.0 license | present |

Current repository validation context:

`1 linked README architecture image`

`23 CI workflow badges`

`23 GitHub Actions workflow files`

## 4. Current Validation Evidence

Current executable semantic reference:

`frp_prototype_v1_7_0.py`

Current test report:

`TEST_REPORT_v1_8_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

Current release checklist:

`RELEASE_CHECKLIST_v1_8_0.md`

Current validation environment:

- `GitHub Actions`;
- `ubuntu-latest`;
- Verilator SystemVerilog parsing;
- Verilator module elaboration;
- executable compiled RTL testbench generation;
- executable compiled FPGA integration testbench generation;
- SystemVerilog assertion execution.

Qualified M15 validation record:

| Record | Value |
|---|---|
| validated release | `FRP v1.7.0` |
| milestone | `M15` |
| validated processor-evidence commit | `5fd9a4f` |
| self-test | `41/41 PASS` |
| vector regeneration | `10/10 byte-identical` |
| semantic correlation | `5/5 = 1.0` |
| deterministic replay | `6/6 = 1.0` |
| result | `PASS` |

Recorded M15 workflow stack:

- `FRP Structured Output #113 — PASS`;
- `FRP M15 Implementation Mapping and Qualification Closure #1 — PASS`;
- `FRP Self Test #154 — PASS`;
- `FRP Benchmark Smoke Test #152 — PASS`.

M16 RTL qualification records:

| Qualification record | Workflow run | Qualified source commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |

M16 FPGA preparation qualification records:

| Qualification record | Workflow run | Qualified repository commit | Branch | Result | Duration | Artifact count | Status |
|---|---:|---|---|---|---:|---:|---|
| Initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1m 7s` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `36s` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

Current result:

`PASS`

## 5. Current Processor Invariants

The current FRP v1.8.0 package retains the following qualified M15 invariants:

| Invariant | Required result |
|---|---|
| balanced ternary state domain | `{-1, 0, 1}` |
| opposite-polarity routing | `-1 → 0 → 1` and `1 → 0 → -1` |
| direct opposite-polarity execution | `actual_direct_events = 0` |
| reserved hardware state | `reserved_state_events = 0` |
| pending-route queue | `queue_overflow_events = 0` |
| dynamic stability | `C_minus_P_min > 0.0` |
| transition load | `switch_load_peak <= transition_fraction` |
| telemetry | `ticks_recorded = steps` |
| scheduler | counts match selected cycle mode |
| topology closure | `fixed_point_topology_sum_exact = True` |
| thermal closure | `fixed_point_thermal_sum_exact = True` |
| semantic state sequence | match `1.0` |
| semantic scheduler sequence | match `1.0` |
| semantic neutral-route sequence | match `1.0` |
| semantic C_minus_P sign | match `1.0` |
| semantic boundary order | match `1.0` |
| exact shadow state replay | match `1.0` |
| exact shadow scheduler replay | match `1.0` |
| exact pending-route replay | match `1.0` |
| exact counter replay | match `1.0` |
| exact trace replay | match `1.0` |
| exact cell-trace replay | match `1.0` |

The M16 integrated invariant set is:

| Invariant flag | RTL result | FPGA preparation result |
|---|---:|---:|
| `FRP_INV_STATE_DOMAIN_VALID` | `PASS` | `PASS` |
| `FRP_INV_SCHEDULER_COUNTS_VALID` | `PASS` | `PASS` |
| `FRP_INV_REQUEST_LANE_ORDER_VALID` | `PASS` | `PASS` |
| `FRP_INV_PENDING_POLARITY_VALID` | `PASS` | `PASS` |
| `FRP_INV_ACTIVE_NEUTRAL_VALID` | `PASS` | `PASS` |
| `FRP_INV_TRANSITION_CAPACITY_VALID` | `PASS` | `PASS` |
| `FRP_INV_STATE_UPDATE_VALID` | `PASS` | `PASS` |
| `FRP_INV_NO_ACTUAL_DIRECT_EVENTS` | `PASS` | `PASS` |
| `FRP_INV_NO_RESERVED_STATE` | `PASS` | `PASS` |
| `FRP_INV_NO_QUEUE_OVERFLOW` | `PASS` | `PASS` |

Integrated invariant vector:

`1111111111`

## 6. Current Default Semantic Reference Execution Summary

Command:

    python frp_prototype_v1_7_0.py --mode demo --output json

Current default profile:

| Parameter | Value |
|---|---:|
| cells | `16` |
| steps | `64` |
| seed | `76` |
| scheduler | `7/1` |
| transition fraction | `0.25` |
| hierarchy depth | `4` |
| request lanes | `4` |
| packed state width | `32 bits` |

Current verified summary:

| Metric | Value |
|---|---:|
| ticks recorded | `64` |
| scheduler balance ticks | `56` |
| scheduler commit ticks | `8` |
| `C_minus_P_min` | `0.6142730712890625` |
| `C_minus_P_final` | `0.88287353515625` |
| `switch_load_peak` | `0.25` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |
| result | `PASS` |

## 7. Qualified M15 41-Check Self-Test Summary

Command:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Qualified result:

`41/41 PASS`

The M15 self-test registry validates:

- `free` scheduler behavior;
- `7/1` scheduler behavior;
- `1/7` scheduler behavior;
- balanced ternary encoding;
- opposite-polarity active-neutral routing;
- request-lane order;
- transition-fraction enforcement;
- queue behavior;
- reserved-state exclusion;
- fixed-point boundaries;
- exact topology closure;
- exact thermal closure;
- trigonometric lookup behavior;
- quantized-shadow state invariants;
- semantic sequence correlation;
- exact deterministic replay;
- vector determinism;
- 8-cell scaling;
- 16-cell scaling;
- 32-cell scaling;
- qualification closure.

Qualified status:

`PASS`

## 8. Qualified M15 Benchmark Summary

Command:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix

Schema:

`frp.m3.benchmark_matrix.v1.7.0`

Validated benchmark rows:

1. `frp_v1_6_0_m14_floating_semantic_reference`;
2. `frp_v1_7_0_quantized_hardware_shadow`;
3. `frp_v1_7_0_cycle_exact_vector_package`;
4. `frp_v1_7_0_systemverilog_correlation_contract`;
5. `frp_v1_7_0_qualification_closure`.

Row count:

`5`

Qualification result:

`PASS`

## 9. Historical Standard Self-Test Summary

The repository preserves the historical v0.9.3 standard self-test as a separate release-specific evidence contour.

Historical command:

    python3 frp_prototype_v0_9_3_mobile.py --mode test --steps 128 --seeds 5

Recorded historical summary:

| Metric | Value |
|---|---:|
| runs | `300` |
| `C_minus_P_min` | `0.14475` |
| `heat_peak` | `0.10700` |
| `switch_load_peak` | `0.25` |
| `actual_direct_events` | `0` |
| `prevented_direct_events` | `3820` |
| `neutralized_conflicts` | `2392` |
| failures | `0` |
| result | `PASS` |

These values remain attached to the historical `frp_distributed_resonant` architecture and the v0.9.3 benchmark model.

## 10. Historical Heavy Self-Test Summary

The repository preserves the historical heavy self-test as a separate release-specific evidence contour.

Historical command:

    python3 frp_prototype_v0_9_3_mobile.py --mode test --steps 256 --seeds 10

Recorded historical summary:

| Metric | Value |
|---|---:|
| runs | `600` |
| `C_minus_P_min` | `0.14475` |
| `heat_peak` | `0.10700` |
| `switch_load_peak` | `0.25` |
| `actual_direct_events` | `0` |
| `prevented_direct_events` | `7913` |
| `neutralized_conflicts` | `4921` |
| failures | `0` |
| result | `PASS` |

These values remain attached to the historical v0.9.3 transition-model contour.

## 11. Historical Transition Benchmark Summary

Historical evidence source:

`TEST_REPORT_v0_9_3.md`

Historical benchmark parameters:

| Parameter | Value |
|---|---|
| `N` | `8, 16, 32, 64` |
| seeds | `0..4` |
| cycle modes | `free`, `7/1`, `1/7` |
| operations | `neg`, `add`, `sub`, `compare`, `consensus` |
| steps | `128` |

Historical architecture set:

- `binary_style_forced_switch`;
- `direct_ternary_commit`;
- `distributed_neutral_ternary`;
- `frp_distributed_resonant`.

Recorded historical benchmark:

| Architecture | Match | C-P_min | Heat Peak | Switch Peak | Actual Direct | Prevented Direct | Neutralized |
|---|---:|---:|---:|---:|---:|---:|---:|
| `binary_style_forced_switch` | `1.000` | `-0.551000` | `0.051000` | `1.000000` | `2052` | `0` | `0` |
| `direct_ternary_commit` | `1.000` | `-0.551000` | `0.051000` | `1.000000` | `2052` | `0` | `0` |
| `distributed_neutral_ternary` | `1.000` | `0.174750` | `0.003250` | `0.250000` | `0` | `0` | `2052` |
| `frp_distributed_resonant` | `1.000` | `0.144750` | `0.107000` | `0.250000` | `0` | `3820` | `2392` |

Recorded heat-peak values:

`binary_style_forced_switch heat_peak = 0.051000`

`distributed_neutral_ternary heat_peak = 0.003250`

Exact ratio:

`0.051000 / 0.003250 = 15.6923076923`

Recorded numerical representations:

`15.69× lower heat_peak`

`93.63% lower heat_peak`

Recorded transition values:

`distributed_neutral_ternary actual_direct_events = 0`

`binary_style_forced_switch actual_direct_events = 2052`

`distributed_neutral_ternary switch_load_peak = 0.25`

`binary_style_forced_switch switch_load_peak = 1.0`

Measurement contour:

`FRP v0.9.3 transition benchmark model and defined workload`

## 12. Comparative Architecture Benchmark Suite

Benchmark directory:

`benchmarks/architecture_comparison/`

Schema:

`frp.benchmark.architecture_comparison.v1`

Architecture order:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

Canonical workload:

- `256 commands`;
- `16 cells`;
- `seed 76`;
- `transaction_serial` execution;
- maximum `64` completion cycles per command;
- final cooldown `32` cycles.

Canonical unit-event profile:

`unit_event_cost_v1`

Canonical result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`

Canonical comparison-package digest:

`5a4be61ce7fd6bc680bbd8bc28bfe7cc9d2ad35adddf642cecff111fbd503d6a`

Integrity status:

`PASS`

Qualification status:

`PASS`

Recorded semantic results for every architecture row:

`semantic_completion_ratio = 1.0`

`semantic_output_match = 1.0`

Canonical unit-event baseline results:

| Architecture | Total normalized energy | Peak temperature proxy |
|---|---:|---:|
| `binary_synchronous_reference` | `5412.0` | `3.8474206768140564` |
| `binary_clock_gated_reference` | `934.0` | `0.771273768299779` |
| `direct_ternary_reference` | `1242.0` | `1.119499710224827` |
| `frp_v1_7_0_quantized_shadow` | `1393509.0` | `675.0796999541329` |

Tick-level record:

| Architecture | Completion ticks | Mean latency ticks | Maximum latency ticks | Throughput commands per tick |
|---|---:|---:|---:|---:|
| `binary_synchronous_reference` | `288` | `1.0` | `1` | `0.8888888888888888` |
| `binary_clock_gated_reference` | `288` | `1.0` | `1` | `0.8888888888888888` |
| `direct_ternary_reference` | `288` | `1.0` | `1` | `0.8888888888888888` |
| `frp_v1_7_0_quantized_shadow` | `413` | `1.48828125` | `2` | `0.6198547215496368` |

The canonical unit-event comparison records identical completion ticks, mean latency ticks, maximum latency ticks, and throughput per tick for:

- `binary_synchronous_reference`;
- `binary_clock_gated_reference`;
- `direct_ternary_reference`.

Canonical FRP workload record:

| Metric | Value |
|---|---:|
| `semantic_completion_ratio` | `1.0` |
| `semantic_output_match` | `1.0` |
| `requested_direct_events` | `125` |
| `prevented_direct_events` | `125` |
| `neutral_insertions` | `125` |
| `neutral_routed_events` | `125` |
| `actual_direct_events` | `0` |
| `pending_route_count_final` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |
| `global_phase_coherence_final` | `0.9999997103586793` |
| `C_minus_P_min` | `0.856201171875` |
| `C_minus_P_final` | `1.2415313720703125` |

FRP v1.7.0 quantized-shadow arithmetic record:

| Event | Total |
|---|---:|
| `fixed_point_multiplies_32x32` | `518728` |
| `fixed_point_accumulates_64` | `296534` |
| `fixed_point_adds_32` | `339899` |
| `fixed_point_compares_32` | `45430` |
| `lut_reads_32` | `172221` |

Measurement contour:

`FRP v1.7.0 M15 quantized hardware shadow under the canonical comparative workload`

## 13. Hardware-Sensitivity Qualification

Schema:

`frp.benchmark.hardware_sensitivity_comparison.v1`

Canonical result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`

Profile:

`literature_anchored_cmos45_sensitivity_v1`

Normalization:

`32-bit integer addition = 1.0`

Reference energy:

`0.1 pJ`

Technology context:

`45 nm CMOS`

Validated scenarios:

1. `lower_bound`;
2. `nominal`;
3. `upper_bound`.

Recorded total normalized energy:

| Scenario | Binary synchronous | Binary clock gated | Direct ternary | FRP v1.7.0 quantized shadow |
|---|---:|---:|---:|---:|
| `lower_bound` | `181.078125` | `111.109375` | `118.078125` | `14457825.125` |
| `nominal` | `724.3125` | `444.4375` | `472.3125` | `25157118.0` |
| `upper_bound` | `4049.25` | `2929.75` | `3041.25` | `39955490.0` |

Ranking basis:

`ascending_total_normalized_energy`

Recorded ranking for all three scenarios:

`binary_clock_gated_reference`

↓

`direct_ternary_reference`

↓

`binary_synchronous_reference`

↓

`frp_v1_7_0_quantized_shadow`

Recorded ranking state:

`ranking_stable = true`

`ranking_sensitive = false`

Hardware-sensitivity package digest:

`a44cf392d946e3b5c21dffbaa1d726d31da326a007e2908914f6477215261ea0`

Profile qualification status:

`PASS`

Comparison qualification status:

`PASS`

Qualification policy:

`integrity_only_no_winner_assertions`

Winner assertions:

`[]`

## 14. General-Purpose Execution and Qualification Environment

The FRP repository has been executed through:

- local Python execution;
- reproducibility commands;
- structured-output workflows;
- benchmark workflows;
- self-test workflows;
- GitHub Actions hardware-backed CI execution;
- deterministic M15 artifact generation;
- independent vector-package regeneration;
- exact quantized replay;
- Verilator SystemVerilog parsing;
- Verilator module elaboration;
- compiled M16 RTL testbench execution;
- SystemVerilog assertion execution;
- compiled FPGA integration testbench execution;
- repository-integrity validation;
- qualification-evidence generation.

Current executable semantic layer:

`frp_prototype_v1_7_0.py`

Current RTL execution layer:

`rtl/m16/`

Current FPGA preparation layer:

`fpga/m16/`

## 15. Qualified M15 Hardware-Facing Foundation

The qualified M15 hardware-facing package contains ten artifact layers:

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

The M15 implementation-mapping chain is:

`floating semantic reference`

↓

`hardware-facing numeric types`

↓

`balanced ternary hardware encoding`

↓

`deterministic fixed-point arithmetic`

↓

`stateful quantized hardware shadow`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`SystemVerilog interface mapping`

↓

`synthesizable RTL reference-core mapping`

↓

`RTL assertion correlation`

↓

`reference equivalence`

↓

`qualification closure`

M15 qualification closure result:

`PASS`

M15 qualification records:

| Record | Result |
|---|---:|
| self-test | `41/41 PASS` |
| deterministic vector files | `10/10 byte-identical` |
| semantic correlation matches | `5/5 = 1.0` |
| deterministic replay matches | `6/6 = 1.0` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |

## 16. Current M16 RTL Execution Package

M16 RTL source boundary:

`rtl/m16/`

Qualified M16 SystemVerilog artifact count:

`10`

| SystemVerilog artifact | Function |
|---|---|
| `rtl/m16/frp_m16_pkg.sv` | canonical balanced ternary encoding, scheduler types, transition classes, invariant indexes, and shared functions |
| `rtl/m16/frp_m16_scheduler.sv` | `free`, `7/1`, and `1/7` temporal scheduler execution |
| `rtl/m16/frp_m16_request_lanes.sv` | deterministic request-lane arbitration |
| `rtl/m16/frp_m16_pending_routes.sv` | retained pending-polarity creation, retention, completion, and clearing |
| `rtl/m16/frp_m16_active_neutral.sv` | active-neutral transition generation |
| `rtl/m16/frp_m16_capacity_guard.sv` | distributed transition-capacity admission |
| `rtl/m16/frp_m16_state_update.sv` | retained balanced ternary state writeback |
| `rtl/m16/frp_m16_core.sv` | integrated M16 RTL execution boundary |
| `rtl/m16/frp_m16_assertions.sv` | temporal and architectural assertion layer |
| `rtl/m16/frp_m16_tb.sv` | deterministic executable testbench |

Qualified M16 RTL documentation count:

`5`

| Documentation artifact | Function |
|---|---|
| `rtl/m16/README.md` | M16 RTL architecture and execution semantics |
| `rtl/m16/ARTIFACTS.md` | exact RTL artifact manifest |
| `rtl/m16/SIMULATION.md` | build and execution procedure |
| `rtl/m16/SIMULATION_TRANSCRIPT.md` | executable qualification record |
| `rtl/m16/CLOSURE.md` | M16 RTL closure record |

RTL testbench configuration:

| Parameter | Value |
|---|---:|
| `CELLS` | `8` |
| `STATE_BITS` | `2` |
| `REQUEST_LANES` | `2` |
| `COUNTER_BITS` | `32` |

Transition-capacity relation:

`REQUEST_LANES = max(1, round(CELLS × 0.25))`

Qualified configuration:

`8 cells → 2 request lanes`

M16 RTL execution domains:

- `free` scheduler execution;
- `7/1` scheduler execution;
- `1/7` scheduler execution;
- deterministic request-lane arbitration;
- retained pending-route ownership;
- retained pending-route priority;
- retained pending-route completion from state `0`;
- active-neutral first-leg execution;
- distributed transition-capacity enforcement;
- retained balanced ternary state writeback;
- counter clearing with retained state preserved;
- architectural telemetry;
- SystemVerilog assertion execution;
- ten integrated invariant flags.

Balanced ternary retained-state domain:

`{-1, 0, 1}`

Active neutral state:

`0`

Mandatory opposite-polarity routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Qualified opposite-polarity event record:

| Event | Recorded value |
|---|---:|
| `requested_direct_events` | `1` |
| `prevented_direct_events` | `1` |
| `neutral_routed_events` | `1` |
| `actual_direct_events` | `0` |

RTL terminal record:

| Record | Value |
|---|---:|
| `CELLS` | `8` |
| `REQUEST_LANES` | `2` |
| `ticks_recorded` | `16` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

RTL diagnostic record:

| Diagnostic boundary | Result |
|---|---:|
| inferred latch diagnostics | `0` |
| multidriven diagnostics | `0` |
| latch-diagnostic rejection | `PASS` |
| multidriven-diagnostic rejection | `PASS` |

RTL repository-integrity record:

| Record | Result |
|---|---|
| build directory and logs | `/tmp` |
| repository-local simulator directories after qualification | `ABSENT` |
| repository source modification during qualification | `NONE` |
| repository-integrity result | `PASS` |

RTL qualification evidence contains:

- toolchain record;
- SystemVerilog source hashes;
- Verilator build log;
- architectural execution log;
- qualification result record.

RTL qualification records:

| Qualification record | Workflow run | Qualified source commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |

RTL qualification rerun duration:

`52s`

RTL qualification result:

`PASS`

## 17. Current M16 FPGA Preparation Package

M16 FPGA preparation source boundary:

`fpga/m16/`

Qualified FPGA SystemVerilog artifact count:

`2`

| FPGA SystemVerilog artifact | Function |
|---|---|
| `fpga/m16/frp_m16_fpga_top.sv` | target-independent FPGA integration boundary |
| `fpga/m16/frp_m16_fpga_tb.sv` | executable FPGA integration qualification testbench |

Qualified FPGA documentation count:

`2`

| FPGA documentation artifact | Function |
|---|---|
| `fpga/m16/SIMULATION_TRANSCRIPT.md` | FPGA preparation simulation and qualification record |
| `fpga/m16/CLOSURE.md` | FPGA preparation closure record |

Qualified inherited RTL dependency count:

`9`

| Inherited RTL dependency | Status |
|---|---|
| `rtl/m16/frp_m16_pkg.sv` | qualified |
| `rtl/m16/frp_m16_scheduler.sv` | qualified |
| `rtl/m16/frp_m16_request_lanes.sv` | qualified |
| `rtl/m16/frp_m16_pending_routes.sv` | qualified |
| `rtl/m16/frp_m16_active_neutral.sv` | qualified |
| `rtl/m16/frp_m16_capacity_guard.sv` | qualified |
| `rtl/m16/frp_m16_state_update.sv` | qualified |
| `rtl/m16/frp_m16_core.sv` | qualified |
| `rtl/m16/frp_m16_assertions.sv` | qualified |

FPGA integration top:

`frp_m16_fpga_top`

FPGA integration testbench:

`frp_m16_fpga_tb`

Instantiated execution core:

`frp_m16_core`

FPGA preparation configuration:

| Parameter | Value |
|---|---:|
| `CELLS` | `8` |
| `STATE_BITS` | `2` |
| `REQUEST_LANES` | `2` |
| `CELL_INDEX_BITS` | `3` |
| `COUNTER_BITS` | `32` |

FPGA preparation execution domains:

- target-independent FPGA integration;
- FPGA top parsing and elaboration;
- executable FPGA integration testbench generation;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- tick blocking before readiness;
- counter-clear blocking before readiness;
- request blocking before readiness;
- scheduler-mode propagation;
- request-interface propagation;
- active-neutral opposite-polarity routing;
- retained pending-route completion;
- transition-capacity enforcement;
- retained balanced ternary state writeback;
- architectural telemetry;
- all ten M16 invariant flags.

External reset input:

`rst_n_async`

Internal core reset:

`rst_n_core`

Validated reset sequence:

1. external reset asserts asynchronously;
2. the synchronization register clears;
3. the first release edge remains blocked;
4. the second release edge activates `rst_n_core` and `core_ready`.

Validated input-gating relations:

`core_ready = rst_n_core`

`tick_enable_core = tick_enable && core_ready`

`clear_counters_core = clear_counters && core_ready`

`request_valid_core = request_valid & {REQUEST_LANES{core_ready}}`

Qualified FPGA opposite-polarity transition:

`1 → -1`

Executed route:

`1 → 0 → -1`

FPGA terminal record:

| Record | Value |
|---|---:|
| `CELLS` | `8` |
| `REQUEST_LANES` | `2` |
| `core_ready` | `1` |
| `ticks_recorded` | `1` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `invariant_flags` | `1111111111` |

FPGA diagnostic record:

| Diagnostic boundary | Result |
|---|---:|
| inferred latch diagnostics | `0` |
| multidriven diagnostics | `0` |
| latch-diagnostic rejection | `PASS` |
| multidriven-diagnostic rejection | `PASS` |

FPGA repository-integrity record:

| Record | Result |
|---|---|
| isolated build directory | `/tmp/frp_m16_fpga_obj` |
| repository-local simulator directories after qualification | `ABSENT` |
| repository source modification during qualification | `NONE` |
| repository-integrity result | `PASS` |

FPGA qualification evidence contains:

- Verilator and compiler toolchain record;
- FPGA and inherited RTL source hashes;
- FPGA top lint and elaboration log;
- FPGA testbench build log;
- FPGA execution log;
- qualification result record.

FPGA preparation qualification records:

| Qualification record | Workflow run | Qualified repository commit | Branch | Result | Duration | Artifact count | Status |
|---|---:|---|---|---|---:|---:|---|
| Initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1m 7s` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `36s` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

FPGA preparation qualification result:

`PASS`

## 18. Current Hardware-Facing Numeric Profile

Primary numeric representations:

| Domain | Representation |
|---|---|
| general dynamic scalar | `S32Q16` |
| normalized coefficient | `S32Q30` |
| phase | `PHASE_U32` |
| Sakaguchi gamma | `GAMMA_S32` |

Deterministic trigonometric profile:

`4096-entry full-cycle lookup table`

Canonical balanced ternary hardware encoding:

| Ternary state | Two-bit encoding |
|---|---|
| `-1` | `2'b11` |
| `0` | `2'b00` |
| `1` | `2'b01` |
| reserved | `2'b10` |

The same canonical encoding is used for:

- retained processor state;
- phase-derived target state;
- request target state;
- transition candidates;
- pending-route polarity.

Qualified reserved-state record:

`reserved_state_events = 0`

Qualified fixed-point closure records:

`fixed_point_topology_sum_exact = True`

`fixed_point_thermal_sum_exact = True`

## 19. Current Hardware-Facing Documents

Foundation documents:

| File | Role |
|---|---|
| `docs/mathematical_foundation.md` | FRP mathematical relations |
| `docs/physical_foundation.md` | FRP physical implementation relations |

Implementation and physical-path documents:

| File | Role |
|---|---|
| `docs/hardware_pathway.md` | hardware-facing development path |
| `docs/implementation_layers.md` | staged FRP implementation layers |
| `docs/fpga_mapping_study.md` | FPGA-oriented mapping study |
| `docs/asic_mapping_study.md` | ASIC-oriented mapping study |
| `docs/physical_validation_plan.md` | physical validation planning structure |
| `docs/m15_implementation_mapping_domain_interface_qualification_closure.md` | qualified M15 implementation-mapping architecture |
| `verification/README.md` | verification registry |
| `verification/coherence_metrics.md` | coherence and stability metrics |

Current M16 architecture and qualification documents:

| File | Role |
|---|---|
| `docs/m16_rtl_core_realization_execution_semantics.md` | M16 RTL core realization and execution-semantics package |
| `docs/m16_rtl_core_interface_contract.md` | M16 RTL interface contract |
| `docs/m16_scheduler_state_rtl_realization.md` | scheduler-state RTL realization |
| `docs/m16_request_lane_arbitration_module.md` | request-lane arbitration module |
| `docs/m16_pending_route_register_module.md` | pending-route register module |
| `docs/m16_active_neutral_transition_module.md` | active-neutral transition module |
| `docs/m16_transition_capacity_guard_module.md` | transition-capacity guard module |
| `docs/m16_retained_state_update_module.md` | retained-state update module |
| `docs/m16_balanced_ternary_state_register_map.md` | balanced ternary state-register map |
| `docs/m16_invariant_assertion_set.md` | M16 invariant and assertion set |
| `docs/m16_external_simulator_execution_plan.md` | external simulator execution plan |
| `docs/m16_m15_vector_replay_compatibility_report.md` | M15 vector replay compatibility report |
| `docs/m16_rtl_artifact_boundary_qualification.md` | M16 RTL artifact-boundary qualification |
| `docs/m16_artifact_boundary_test_stability_policy.md` | artifact-boundary test stability policy |
| `docs/m16_qualification_manifest.md` | M16 qualification manifest |
| `docs/m16_qualification_index.md` | M16 qualification index |
| `docs/m16_public_status_snapshot.md` | M16 public status snapshot |

M16 architecture and qualification document count:

`17`

Closed RTL documentation:

- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`.

Closed FPGA preparation documentation:

- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

## 20. Funding Objective

The funding objective is to advance FRP from the qualified M15 semantic and implementation-mapping foundation and the closed M16 RTL execution and FPGA preparation layers into target-specific implementation and physical-correlation stages while preserving correlation with the current processor semantics.

Funding can support:

- FRP v1.8.0 archival release and DOI synchronization;
- target-specific FPGA top integration;
- target-specific clock-generation resources;
- target-specific reset-source integration;
- pin assignments;
- device constraints;
- physical timing constraints;
- board-level input and output routing;
- FPGA synthesis;
- FPGA placement and routing;
- resource-utilization reporting;
- timing reporting;
- cycle-exact FPGA correlation;
- M15 vector replay through the M16 execution boundary;
- FPGA telemetry capture;
- physical timing measurement;
- physical energy measurement;
- physical thermal measurement;
- ASIC-oriented implementation study;
- arithmetic and lookup implementation study;
- hierarchical coupling implementation study;
- thermal and coherence datapath implementation study;
- physical validation protocol execution;
- laboratory collaboration;
- independent engineering review;
- partner review package preparation;
- technical diagrams and implementation documentation;
- release engineering;
- legal and intellectual-property support.

## 21. Proposed Funding Milestones

Completed technical baseline:

- `FRP v1.7.0 M15 — 41/41 PASS`;
- `M16 RTL EXECUTION LAYER CLOSED`;
- `M16 FPGA PREPARATION LAYER CLOSED`.

### Milestone 1 — FRP v1.8.0 Archival Release and Partner Review Package

Objective:

`publish the current FRP v1.8.0 M16 package as an archival and partner-review reference`

Deliverables:

- final repository audit;
- GitHub release tag;
- release description;
- archival package;
- Zenodo release;
- DOI metadata synchronization;
- citation metadata synchronization;
- README DOI integration;
- M15 and M16 release-evidence finalization;
- partner-facing technical review package.

### Milestone 2 — Target-Specific FPGA Integration and Synthesis

Objective:

`connect the closed target-independent M16 FPGA preparation boundary to a selected FPGA target and execute the target-specific synthesis flow`

Deliverables:

- selected FPGA target record;
- target-specific top-level integration;
- clock-generation resource mapping;
- reset-source mapping;
- pin assignments;
- device constraints;
- physical timing constraints;
- board-level input and output routing;
- synthesis project;
- synthesis report;
- resource-utilization report;
- placement-and-routing report;
- timing report;
- target-specific implementation record.

### Milestone 3 — FPGA Execution and Physical Correlation

Objective:

`execute the M16 retained-state semantics on the selected FPGA target and correlate recorded execution with the M15 and M16 reference domains`

Deliverables:

- FPGA execution image;
- clock and reset execution record;
- M15 deterministic vector replay;
- cycle-exact RTL-to-FPGA comparison;
- scheduler-state capture;
- request-lane capture;
- pending-route capture;
- active-neutral route capture;
- transition-capacity telemetry;
- invariant-flag capture;
- timing measurement record;
- energy measurement record;
- thermal measurement record;
- workload-identity record;
- FPGA correlation report.

### Milestone 4 — ASIC-Oriented Implementation and Cost Study

Objective:

`translate the qualified M16 execution boundary into an ASIC-oriented implementation study with explicit event, arithmetic, storage, control, and interface records`

Deliverables:

- datapath partitioning;
- state-storage architecture;
- fixed-point arithmetic study;
- trigonometric approximation study;
- hierarchical coupling implementation study;
- thermal and coherence datapath study;
- clocking and control study;
- reset architecture study;
- request-lane and pending-route storage study;
- power, performance, and area estimation plan;
- raw event-total mapping;
- sensitivity-model refinement;
- reference-equivalence plan;
- ASIC-oriented engineering report.

### Milestone 5 — Physical Validation Protocol

Objective:

`execute a measurement protocol that compares future physical execution against the qualified FRP semantic, implementation-mapping, RTL, and FPGA preparation references`

Deliverables:

- validation protocol;
- measurement setup;
- benchmark repeatability record;
- timing measurement procedure;
- energy measurement procedure;
- thermal measurement procedure;
- telemetry comparison procedure;
- cycle-exact reference comparison structure;
- workload identity controls;
- result schema;
- independent review procedure;
- physical-correlation report.

### Milestone 6 — Laboratory, Engineering, and Funding Partnership Package

Objective:

`prepare the current FRP v1.8.0 package and proposed target-specific work for laboratory collaboration, engineering partnership, grant review, and investor-facing technical evaluation`

Deliverables:

- executive summary;
- technical architecture overview;
- current validated asset registry;
- M15 qualification summary;
- M16 RTL qualification summary;
- M16 FPGA preparation qualification summary;
- historical transition benchmark record;
- comparative architecture benchmark record;
- hardware-sensitivity qualification record;
- target-specific FPGA work package;
- ASIC-oriented study package;
- physical validation package;
- resource request outline;
- project timeline;
- partner collaboration model.

## 22. Resource Needs

Potential resource categories:

| Resource category | Purpose |
|---|---|
| RTL engineering | M16 maintenance, target-specific integration, interface extension, and execution-semantics preservation |
| verification engineering | cycle-exact correlation, vector replay, assertion execution, and invariant closure |
| FPGA engineering | target selection, synthesis, placement and routing, timing, memory mapping, and telemetry integration |
| ASIC architecture | datapath partitioning, control, state storage, clocking, reset, and PPA study |
| numerical implementation engineering | fixed-point arithmetic, lookup, coupling, thermal, and coherence implementation |
| measurement engineering | timing, energy, thermal, and telemetry measurement |
| software engineering | semantic-reference maintenance, export tooling, reproducibility, and benchmark automation |
| documentation engineering | architecture diagrams, technical briefs, release records, and partner packaging |
| research collaboration | independent review and laboratory validation |
| legal and intellectual-property support | licensing review, patent strategy, and collaboration agreements |
| archival support | DOI release, citation metadata, and public research packaging |

Target-specific FPGA resource records:

| Resource | Required record |
|---|---|
| FPGA family and device | selected target |
| development board | selected target |
| synthesis toolchain | versioned tool record |
| placement-and-routing toolchain | versioned tool record |
| timing constraints | repository artifact |
| pin constraints | repository artifact |
| clock source | recorded frequency and source |
| reset source | recorded assertion and release path |
| telemetry interface | recorded transport |
| power measurement equipment | model and calibration record |
| thermal measurement equipment | model and calibration record |
| logic analyzer or embedded trace | capture configuration |
| host execution environment | versioned software record |

## 23. Partner Profile

Relevant partner types:

- RTL development teams;
- FPGA development teams;
- ASIC architecture teams;
- semiconductor research groups;
- university laboratories;
- applied computing research laboratories;
- grant programs;
- early-stage hardware incubators;
- scientific computing partners;
- verification specialists;
- measurement laboratories;
- technical investors;
- prototype engineering partners;
- archival publication partners;
- intellectual-property counsel.

Partner review domains:

- validated processor semantics;
- balanced ternary state and retained-result domain;
- active-neutral route behavior;
- Kuramoto-Sakaguchi resonant phase dynamics;
- hierarchical fractal coupling;
- multiscale phase coherence;
- stateful delay dynamics;
- distributed local thermal dynamics;
- processor-specific operational quantities;
- reproducibility and CI evidence;
- deterministic fixed-point mapping;
- cycle-exact traces;
- RTL comparison vectors;
- reference equivalence;
- M15 qualification closure;
- M16 RTL source and execution boundary;
- deterministic scheduler execution;
- request-lane arbitration;
- retained pending-route completion;
- transition-capacity enforcement;
- retained-state writeback;
- SystemVerilog assertions;
- integrated invariant flags;
- target-independent FPGA integration;
- reset synchronization and `core_ready` gating;
- comparative benchmark records;
- hardware-sensitivity qualification;
- target-specific FPGA work package;
- physical validation protocol.

## 24. Technical Value Proposition

FRP currently provides:

- a defined Ternary Fractal Resonant Coherence Processor architecture;
- an executable floating semantic reference;
- a balanced ternary state and retained-result domain;
- active neutral transition routing;
- distributed transition commit;
- Kuramoto-Sakaguchi resonant phase dynamics;
- hierarchical fractal coupling;
- multiscale phase coherence;
- stateful delay dynamics;
- distributed local thermal dynamics;
- correlated gamma drift;
- nonlinear coherence compression;
- operational coherence tracking;
- dynamic stability tracking;
- stable structured-output schemas;
- a deterministic fixed-point interface;
- canonical balanced ternary hardware encoding;
- a stateful quantized hardware shadow;
- cycle-exact integer traces;
- deterministic RTL comparison vectors;
- a SystemVerilog interface map;
- a synthesizable RTL reference-core map;
- an assertion-correlation harness;
- floating-to-quantized reference equivalence;
- exact deterministic replay;
- M15 qualification closure;
- an executable ten-file SystemVerilog RTL boundary;
- deterministic temporal scheduler execution;
- deterministic request-lane arbitration;
- retained pending-route execution;
- active-neutral transition execution;
- distributed transition-capacity enforcement;
- retained balanced ternary writeback;
- integrated SystemVerilog assertions;
- ten integrated invariant flags;
- an executable RTL architectural testbench;
- a target-independent FPGA integration top;
- an executable FPGA integration testbench;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` execution gating;
- M16 RTL qualification closure;
- M16 FPGA preparation qualification closure;
- comparative architecture benchmarks;
- hardware-sensitivity qualification;
- historical transition benchmark evidence;
- CI-backed reproducibility;
- mathematical and physical foundation documents;
- a defined target-specific FPGA work package;
- a defined physical validation package.

The current engineering value is the combination of:

`defined processor semantics`

+

`measured execution behavior`

+

`deterministic implementation mapping`

+

`executable RTL realization`

+

`target-independent FPGA preparation`

+

`exact correlation artifacts`

+

`qualification evidence`

+

`staged physical validation planning`

## 25. Current Engineering Work Package

The current repository records the following completed boundaries:

- M15 semantic and implementation-mapping qualification;
- ten M15 artifact layers;
- `41/41 PASS`;
- `10/10` byte-identical deterministic vector regeneration;
- `5/5` semantic correlation matches equal to `1.0`;
- `6/6` deterministic replay matches equal to `1.0`;
- ten M16 SystemVerilog RTL source artifacts;
- five M16 RTL documentation artifacts;
- executable Verilator architectural simulation;
- SystemVerilog assertion execution;
- ten integrated invariant flags equal to `1`;
- two M16 FPGA preparation SystemVerilog artifacts;
- two M16 FPGA preparation documentation artifacts;
- nine inherited M16 RTL dependencies;
- executable FPGA integration simulation;
- M16 RTL qualification closure;
- M16 FPGA preparation qualification closure.

The historical v0.9.3 distributed-neutral transition contour records:

`0.051000 / 0.003250 = 15.6923076923`

`15.69× lower heat_peak`

`93.63% lower heat_peak`

The canonical comparative architecture package records the following FRP v1.7.0 quantized-shadow arithmetic totals:

| Event | Total |
|---|---:|
| `fixed_point_multiplies_32x32` | `518728` |
| `fixed_point_accumulates_64` | `296534` |
| `fixed_point_adds_32` | `339899` |
| `fixed_point_compares_32` | `45430` |
| `lut_reads_32` | `172221` |

The proposed engineering work package contains:

- target-specific FPGA top integration;
- target-specific clock and reset mapping;
- device and pin constraints;
- physical timing constraints;
- FPGA synthesis;
- placement and routing;
- utilization reporting;
- timing reporting;
- deterministic vector replay;
- cycle-exact execution correlation;
- invariant telemetry capture;
- timing measurement;
- energy measurement;
- thermal measurement;
- ASIC-oriented datapath study;
- physical validation reporting.

The proposed work preserves:

- balanced ternary state semantics;
- active-neutral route invariants;
- scheduler behavior;
- deterministic request-lane order;
- retained pending-route behavior;
- transition-capacity enforcement;
- retained-state writeback;
- phase evolution;
- multiscale coherence behavior;
- dynamic-stability sign behavior;
- cycle-exact deterministic correlation.

## 26. Review Package

A current partner or funding review package includes:

Release-facing root records:

- `README.md`;
- `funding_brief.md`;
- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `RELEASE_CHECKLIST_v1_8_0.md`;
- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`;
- `RELEASE_CHECKLIST_v1_7_0.md`;
- `CHANGELOG.md`;
- `ROADMAP.md`;
- `MILESTONES.md`;
- `PROJECT_STRUCTURE.md`;
- `CI.md`;
- `REPRODUCIBILITY.md`;
- `USAGE.md`;
- `INSTALL.md`;
- `CONTRIBUTING.md`;
- `CODE_OF_CONDUCT.md`;
- `SECURITY.md`;
- `NOTICE.md`;
- `CITATION.cff`;
- `LICENSE`.

Foundation and architecture records:

- `docs/README.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `docs/core_principles.md`;
- `docs/resonance_computation.md`;
- `docs/architecture.md`;
- `docs/implementation_layers.md`;
- `docs/hardware_pathway.md`;
- `docs/fpga_mapping_study.md`;
- `docs/asic_mapping_study.md`;
- `docs/physical_validation_plan.md`;
- `docs/benchmark_interpretation.md`;
- `docs/output_schema.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `docs/m16_rtl_core_realization_execution_semantics.md`;
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

M16 RTL records:

- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`;
- `rtl/m16/frp_m16_pkg.sv`;
- `rtl/m16/frp_m16_scheduler.sv`;
- `rtl/m16/frp_m16_request_lanes.sv`;
- `rtl/m16/frp_m16_pending_routes.sv`;
- `rtl/m16/frp_m16_active_neutral.sv`;
- `rtl/m16/frp_m16_capacity_guard.sv`;
- `rtl/m16/frp_m16_state_update.sv`;
- `rtl/m16/frp_m16_core.sv`;
- `rtl/m16/frp_m16_assertions.sv`;
- `rtl/m16/frp_m16_tb.sv`.

M16 FPGA preparation records:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

Verification, benchmark, model, simulation, and example records:

- `verification/README.md`;
- `verification/coherence_metrics.md`;
- `benchmarks/architecture_comparison/README.md`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`;
- `models/README.md`;
- `simulations/README.md`;
- `examples/README.md`.

Historical v0.9.3 benchmark review records:

- `TEST_REPORT_v0_9_3.md`;
- `frp_prototype_v0_9_3_mobile.py`.

## 27. Funding-Facing Technical Message

Core message:

`FRP v1.8.0 records a qualified Ternary Fractal Resonant Coherence Processor semantic reference, deterministic M15 implementation-mapping package, executable M16 SystemVerilog RTL core, target-independent FPGA preparation layer, benchmark evidence, and qualification closure.`

Engineering message:

`The current repository contains the semantic source, quantized hardware shadow, cycle-exact traces, deterministic vectors, interface maps, assertion domains, equivalence evidence, integrated RTL execution modules, FPGA integration top, executable testbenches, invariant outputs, and qualification records used by the M15-to-M16 implementation chain.`

Benchmark message:

`The repository preserves the historical distributed-neutral transition record of 15.69× lower heat_peak than binary_style_forced_switch inside the historical v0.9.3 benchmark model, the canonical Comparative Architecture Benchmark Suite, and the Hardware-Informed Sensitivity Qualification as separate evidence contours.`

Partner message:

`The current FRP v1.8.0 package contains the records for technical review, target-specific FPGA integration planning, FPGA synthesis and measurement planning, ASIC-oriented study, physical validation planning, laboratory collaboration, archival publication, and funding milestone definition.`

Research-direction message:

`The balanced ternary {-1, 0, 1} state domain, active neutral state 0, and resonant phase dynamics define a future research direction for qutrit-oriented resonant computation.`

## 28. Evidence-Domain Separation

The funding brief preserves the following distinct evidence contours.

### Preliminary Kuramoto Contour

Measured subject:

`simplified oscillator phase synchronization under external driving`

Primary records:

- `models/kuramoto_frp_background_model.md`;
- `simulations/initial_kuramoto_result.md`.

### Historical v0.9.3 Transition Contour

Measured subject:

`route activity, switching load, historical heat_peak, and historical dynamic stability`

Primary evidence:

`TEST_REPORT_v0_9_3.md`

### FRP v1.7.0 Semantic Contour

Measured subject:

`resonant phase dynamics, hierarchical coherence, delay, distributed thermal state, gamma drift, ternary routing, and C(t) - P(t)`

Primary executable:

`frp_prototype_v1_7_0.py`

Structured-output schema:

`frp.structured_output.v1.7.0`

### M15 Implementation-Mapping Contour

Measured subject:

`fixed-point mapping, quantized execution, cycle-exact traces, RTL vectors, interface mapping, equivalence, deterministic replay, and qualification closure`

Primary architecture document:

`docs/m15_implementation_mapping_domain_interface_qualification_closure.md`

Primary workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

### Comparative Architecture Benchmark Contour

Measured subject:

`semantic completion, tick-level execution, raw event totals, normalized activity cost, and thermal proxy under the canonical comparative workload`

Primary result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`

Schema:

`frp.benchmark.architecture_comparison.v1`

### Hardware-Sensitivity Contour

Measured subject:

`common-coefficient normalized energy under lower-bound, nominal, and upper-bound hardware-sensitivity scenarios`

Primary result:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`

Schema:

`frp.benchmark.hardware_sensitivity_comparison.v1`

### M16 RTL Execution Contour

Measured subject:

`SystemVerilog parsing, module elaboration, executable testbench generation, scheduler execution, request arbitration, active-neutral routing, pending-route completion, transition-capacity enforcement, retained-state writeback, assertions, invariant flags, diagnostics, repository integrity, and qualification evidence`

Primary source boundary:

`rtl/m16/`

Primary workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Qualification records:

- `#82 — a68a2af — SUCCESS`;
- `#84 — ede53cf — SUCCESS`.

Status:

`M16 RTL EXECUTION LAYER CLOSED`

### M16 FPGA Preparation Contour

Measured subject:

`target-independent FPGA top elaboration, executable integration testbench, asynchronous reset assertion, two-stage synchronous reset release, core-ready gating, scheduler propagation, request propagation, active-neutral execution, pending-route completion, invariant flags, diagnostics, repository integrity, and qualification evidence`

Primary source boundary:

`fpga/m16/`

Primary workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Qualification records:

- `#1 — 326b69e — SUCCESS`;
- `#2 — ede53cf — SUCCESS`.

Status:

`M16 FPGA PREPARATION LAYER CLOSED`

Each contour retains its own architecture identifiers, workload, metric definitions, source boundaries, and evidence records.

## 29. Current Semantic-Reference Reproduction Commands

Compile the executable semantic reference:

    python -m py_compile frp_prototype_v1_7_0.py

Run the default execution:

    python frp_prototype_v1_7_0.py --mode demo --output json

Run the full trace:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace

Run the 41-check self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Run the `free` scheduler profile:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

Run the `7/1` scheduler profile:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

Run the `1/7` scheduler profile:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Export the M15 benchmark matrix:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix

Export the reference-equivalence report:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report

Export the qualification-closure manifest:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

## 30. Qualified M15 Export Package

Export the fixed-point interface profile:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile

Export the balanced ternary hardware encoding map:

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map

Export the quantized reference shadow model:

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model

Export the cycle-exact reference trace:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace

Export the RTL comparison vector package:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package

Export the SystemVerilog testbench interface map:

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map

Export the synthesizable RTL reference-core map:

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core

Export the RTL assertion correlation harness:

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness

Export the reference RTL equivalence report:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report

Export the qualification closure manifest:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

## 31. Current M16 RTL Reproduction Commands

Simulation source:

`rtl/m16/frp_m16_tb.sv`

Top-level simulation module:

`frp_m16_tb`

Top-level synthesis boundary:

`frp_m16_core`

Remove previous isolated build outputs:

    rm -rf /tmp/frp_m16_obj
    rm -f /tmp/frp_m16_build.log
    rm -f /tmp/frp_m16_execution.log

Create the isolated build directory:

    mkdir -p /tmp/frp_m16_obj

Build the integrated M16 RTL testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_tb -Irtl/m16 --Mdir /tmp/frp_m16_obj rtl/m16/frp_m16_tb.sv 2>&1 | tee /tmp/frp_m16_build.log

Check the generated executable:

    test -x /tmp/frp_m16_obj/Vfrp_m16_tb

Run the integrated M16 RTL testbench:

    /tmp/frp_m16_obj/Vfrp_m16_tb 2>&1 | tee /tmp/frp_m16_execution.log

Expected terminal markers:

`FRP M16 deterministic RTL testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`ticks_recorded=16`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

## 32. Current M16 FPGA Preparation Reproduction Commands

FPGA integration top:

`frp_m16_fpga_top`

FPGA integration testbench:

`frp_m16_fpga_tb`

Remove previous isolated build outputs:

    rm -rf /tmp/frp_m16_fpga_obj
    rm -f /tmp/frp_m16_fpga_top_lint.log
    rm -f /tmp/frp_m16_fpga_build.log
    rm -f /tmp/frp_m16_fpga_execution.log

Create the isolated build directory:

    mkdir -p /tmp/frp_m16_fpga_obj

Elaborate the FPGA integration top:

    verilator --sv --lint-only --top-module frp_m16_fpga_top -Irtl/m16 -Ifpga/m16 fpga/m16/frp_m16_fpga_top.sv 2>&1 | tee /tmp/frp_m16_fpga_top_lint.log

Build the FPGA integration testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_fpga_tb -Irtl/m16 -Ifpga/m16 --Mdir /tmp/frp_m16_fpga_obj fpga/m16/frp_m16_fpga_tb.sv 2>&1 | tee /tmp/frp_m16_fpga_build.log

Check the generated executable:

    test -x /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Run the FPGA integration testbench:

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb 2>&1 | tee /tmp/frp_m16_fpga_execution.log

Expected terminal markers:

`FRP M16 FPGA integration testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`core_ready=1`

`ticks_recorded=1`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

`invariant_flags=1111111111`

## 33. Current Status

Processor:

`Fractal Resonance Processor (FRP)`

Processor class:

`Ternary Fractal Resonant Coherence Processor`

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Qualified M15 self-test result:

`41/41 PASS`

Qualified M15 vector-regeneration result:

`10/10 byte-identical`

Qualified M15 semantic-correlation result:

`5/5 = 1.0`

Qualified M15 deterministic-replay result:

`6/6 = 1.0`

Current default semantic-reference execution result:

`PASS`

Qualified M15 artifact layer count:

`10`

Current M16 RTL SystemVerilog artifact count:

`10`

Current M16 RTL documentation artifact count:

`5`

Current M16 RTL qualification record:

| Field | Value |
|---|---|
| Workflow | `FRP M16 RTL Artifact Boundary` |
| Workflow file | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#84` |
| Qualified source commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation artifact count:

`2 SystemVerilog artifacts + 2 documentation artifacts`

Current M16 FPGA preparation qualification record:

| Field | Value |
|---|---|
| Workflow | `FRP M16 FPGA Preparation` |
| Workflow file | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#2` |
| Qualified repository commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Workflow duration | `36s` |
| Artifact count | `1` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

Current integrated invariant record:

`1111111111`

Current zero-event records:

`actual_direct_events = 0`

`reserved_state_events = 0`

`queue_overflow_events = 0`

Historical archived ternary-to-binary thermal relation:

`0.051000 / 0.003250 = 15.6923076923`

Historical archived numerical representation:

`15.69× lower heat_peak`

Comparative architecture qualification policy:

`integrity_only_no_winner_assertions`

Comparative architecture winner assertions:

`[]`

Current foundation documents:

- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`.

Current release records:

- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `RELEASE_CHECKLIST_v1_8_0.md`.

Current DOI:

`10.5281/zenodo.21183966`

Current published validation result:

`PASS`

Current RTL status:

`M16 RTL EXECUTION LAYER CLOSED`

Current FPGA preparation status:

`M16 FPGA PREPARATION LAYER CLOSED`

Current funding position:

`qualified M15 semantic and implementation-mapping foundation + executable M16 SystemVerilog RTL core + target-independent FPGA preparation + benchmark records + qualification evidence + target-specific FPGA and physical-correlation work package`



