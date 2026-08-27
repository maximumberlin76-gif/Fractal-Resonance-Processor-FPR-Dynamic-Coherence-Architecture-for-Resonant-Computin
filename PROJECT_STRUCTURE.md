# Repository Structure — Fractal Resonance Processor (FRP)

**Ternary Resonant Coherence Processor — Structured Output Prototype**

This document describes the current public repository structure of the Fractal Resonance Processor (FRP).

Current version:

`FRP v3.2.0`

Current milestone:

`M30 — Reproducibility, Qualification, and Archival Release Closure`

Main executable semantic reference file:

`frp_prototype_v1_7_0.py`

Current test report:

`TEST_REPORT_v3_2_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v3_2_0.md`

Current release notes:

`RELEASE_NOTES_v3_2_0.md`

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current M16 RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Current M16 FPGA preparation workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Current M17 published-artifact integration qualification workflow:

`.github/workflows/frp-m17-published-artifact-integration.yml`

Current validation status:

`PASS`

Inherited validated M15 self-test result:

`41/41 PASS`

Current M16 RTL status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation status:

`M16 FPGA PREPARATION LAYER CLOSED`

Current M17 qualification boundary status:

`M17 QUALIFICATION BOUNDARY CLOSED`

Current M17 qualification result:

`PASS`

Current M17 machine-readable inventory milestone state:

`planned`

Current published release boundary:

`FRP v3.2.0 / M30`

## 1. Repository Role

The repository preserves the complete published FRP architecture progression.

The progression begins with the resonant phase-coherence computational mechanism and the balanced ternary state and retained-result domain.

It continues through structured executable validation, hardware-facing signal mapping, HDL and RTL preparation, FPGA and silicon implementation layers, production qualification, deterministic fixed-point implementation mapping, cycle-exact reference execution, RTL correlation, reference equivalence, and qualification closure.

The primary architecture chain is:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`cell phase and frequency state`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric Sakaguchi phase lag gamma`

↓

`hierarchical fractal coupling`

↓

`phase evolution`

↓

`resonance selection`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`stateful delay dynamics`

↓

`local thermal-phase interaction`

↓

`local correlated gamma drift`

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

`structured machine-readable validation`

↓

`benchmark export and hardware signal mapping`

↓

`HDL trace and testbench preparation`

↓

`RTL interface and assertion contracts`

↓

`formal verification and equivalence scaffolds`

↓

`FPGA synthesis and timing structures`

↓

`production release and stable interface freeze`

↓

`silicon and heterogeneous implementation architecture`

↓

`silicon production and tapeout readiness`

↓

`production integration and external implementation handoff`

↓

`external implementation feedback and production iteration`

↓

`production scaling and implementation stabilization`

↓

`physical implementation correlation and production qualification`

↓

`fixed-point implementation mapping`

↓

`stateful quantized hardware shadow execution`

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

`floating-to-quantized reference correlation`

↓

`exact quantized deterministic replay`

↓

`qualification closure`

↓

`M16 integrated SystemVerilog RTL execution`

↓

`M16 executable architectural testbench and invariant evaluation`

↓

`M16 target-independent FPGA integration, reset synchronization, readiness, and execution-input gating`

↓

`M16 RTL and FPGA preparation qualification closure`

The Comparative Architecture Benchmark Suite adds a supporting deterministic comparison and hardware-sensitivity validation contour alongside the primary architecture progression.

## 2. Complete Computational Core

The current FRP architecture contains two connected computational domains.

### 2.1 Resonant dynamic domain

The resonant dynamic domain contains:

- cell phase;
- base frequency;
- target frequency;
- current frequency;
- Kuramoto-Sakaguchi phase interaction;
- asymmetric phase lag gamma;
- hierarchical fractal coupling;
- scheduler-dependent phase contribution;
- delayed frequency response;
- distributed thermal state;
- thermal coupling-factor evolution;
- local correlated gamma drift;
- phase evolution;
- global Kuramoto order parameter `R`;
- pair-domain phase coherence;
- cluster phase coherence;
- supercluster phase coherence;
- global phase coherence;
- nonlinear coherence compression;
- dynamic stability evaluation.

### 2.2 Balanced ternary state and retained-result domain

The balanced ternary domain contains:

- states `{-1, 0, 1}`;
- active neutral state `0`;
- phase-derived ternary targets;
- transition requests;
- distributed commit;
- transition-fraction limits;
- request lanes;
- pending neutral routes;
- mandatory tick separation;
- scheduler-controlled execution;
- retained ternary state.

The resonant dynamic domain drives the evolving computation.

The balanced ternary domain provides the state, target, transition, and retained-result layer.

### 2.3 Tick-by-tick execution chain

The current Python executable semantic reference preserves the following operational sequence:

`scheduler-state selection`

↓

`pending neutral-route processing`

↓

`transition-request processing`

↓

`phase-derived ternary target processing`

↓

`distributed transition-limit enforcement`

↓

`frequency-target formation`

↓

`stateful delayed frequency response`

↓

`local generated power`

↓

`distributed thermal update`

↓

`local thermal overload`

↓

`correlated gamma-noise update`

↓

`local effective Sakaguchi phase lag`

↓

`thermal coupling-factor update`

↓

`hierarchical Kuramoto-Sakaguchi coupling field`

↓

`phase velocity`

↓

`phase evolution`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`nonlinear coherence compression`

↓

`C(t), P(t), and C(t) - P(t)`

↓

`structured telemetry and trace capture`

Across successive ticks:

`evolved phase field`

↓

`next phase-derived ternary target`

↓

`distributed transition`

↓

`active neutral routing`

↓

`retained coherent ternary state`

## 3. Resonant Phase and Coherence Architecture

### 3.1 Kuramoto-Sakaguchi phase interaction

The current phase interaction uses:

`sin(phase_j - phase_i - gamma_effective_i)`

The interaction combines:

- hierarchical coupling weights;
- local thermal coupling factors;
- nominal coupling strength;
- local effective gamma.

Current default nominal phase lag:

`gamma = 0.30 × pi`

Current default nominal coupling strength:

`coupling_nominal = 0.28`

Current default fractal coupling exponent:

`fractal_alpha = 0.70`

### 3.2 Phase evolution

The current floating reference phase velocity combines:

`0.060 × current frequency`

+

`scheduler push`

+

`coupling field`

The phase update is:

`phase_i = (phase_i + phase_velocity_i) mod 2π`

### 3.3 Kuramoto order parameter R

The current global phase order is:

`R = sqrt(mean(cos(phase))² + mean(sin(phase))²)`

The same phase-order relation is evaluated across hierarchical coherence domains.

### 3.4 Multiscale phase coherence

Current coherence domains include:

- pair domain;
- cluster domain;
- supercluster domain;
- global domain.

Current outputs include:

- pair-domain coherence mean;
- pair-domain coherence minimum;
- cluster coherence mean;
- cluster coherence minimum;
- supercluster coherence mean;
- supercluster coherence minimum;
- global phase coherence;
- coherence dispersion across clusters.

## 4. Delay, Thermal, Gamma, and Stability Architecture

### 4.1 Stateful delay dynamics

Current default delay coefficient:

`delay_alpha = 0.30`

Each cell preserves:

- base frequency;
- frequency target;
- current frequency.

The delayed response is:

`frequency_next = frequency_current + delay_alpha × (frequency_target - frequency_current)`

Frequency lag contributes to:

- phase velocity;
- generated power;
- operational coherence;
- dynamic stability.

### 4.2 Local thermal-phase interaction

Each cell tracks:

- generated power;
- thermal dissipation;
- thermal diffusion;
- local heat;
- thermal overload.

The thermal field feeds into:

- effective resonant coupling;
- local gamma drift;
- nonlinear coherence compression.

Required fixed-point thermal marker:

`fixed_point_thermal_sum_exact = True`

### 4.3 Local correlated gamma drift

The current processor tracks:

- nominal gamma;
- deterministic gamma-noise targets;
- correlated gamma-noise state;
- local thermal overload;
- effective local gamma;
- gamma drift.

The M15 verification path maps this domain through:

- `GAMMA_S32`;
- `gamma_noise_update_valid`;
- `gamma_noise_target_q`;
- deterministic cycle-exact gamma stimulus;
- floating-to-quantized gamma correlation.

### 4.4 Nonlinear coherence compression and dynamic stability

The current processor applies:

`effective coherence = raw phase coherence × coherence compression`

The dynamic stability layer tracks:

`C(t)`

`P(t)`

`C(t) - P(t)`

Current destabilizing load:

`P(t) = heat + switch_load`

Required validated condition:

`C_minus_P_min > 0.0`

## 5. Balanced Ternary State and Retained-Result Architecture

Balanced ternary state domain:

`{-1, 0, 1}`

Active neutral state:

`0`

The active neutral state provides:

- balancing;
- damping;
- transition;
- stabilization;
- conflict neutralization;
- switching-load control.

Current phase-derived ternary target mapping:

`sin(phase) > 0.33 → 1`

`sin(phase) < -0.33 → -1`

`otherwise → 0`

Mandatory opposite-polarity routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Execution relation:

`tick N: active polarity → 0`

↓

`pending neutral route retained`

↓

`tick N+1 or later: 0 → target polarity`

Core validated invariants:

`balanced_ternary_state_domain = True`

`actual_direct_events = 0`

`reserved_state_events = 0`

`queue_overflow_events = 0`

Preserved scheduler modes:

- `free`;
- `7/1`;
- `1/7`.

Current default transition fraction:

`0.25`

Current default 16-cell request-lane count:

`4`

Current validated relation:

`switch_load_peak <= transition_fraction`

## 6. Current Semantic Reference and M16 Execution Layers

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Qualified semantic and implementation-mapping foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Current architecture layer:

`FRP v1.8.0 — M16 RTL Core Realization and Execution Semantics Package`

The Python executable semantic reference preserves the complete resonant phase-coherence computational mechanism and balanced ternary state-retention mechanism.

It extends the M14 floating semantic reference into deterministic hardware-facing representation and qualification layers.

The M15 bridge is:

`M14 floating semantic reference`

↓

`hardware-facing numeric types`

↓

`balanced ternary hardware encoding`

↓

`deterministic fixed-point arithmetic`

↓

`M15 quantized hardware shadow model`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`verification preload and deterministic stimulus`

↓

`SystemVerilog interface mapping`

↓

`synthesizable RTL reference-core mapping`

↓

`RTL assertion correlation mapping`

↓

`floating semantic reference correlation`

↓

`exact quantized deterministic replay`

↓

`qualification closure`

### M16 RTL Core Realization Layer

Path:

`rtl/m16/`

Purpose:

Concrete SystemVerilog RTL realization layer for the FRP v1.8.0 M16 execution boundary.

The M16 RTL layer preserves the M15-qualified retained-state execution contract and exposes the processor boundary as explicit RTL artifacts.

Primary preserved invariants:

`actual_direct_events = 0`

`reserved_state_events = 0`

`queue_overflow_events = 0`

Primary execution chain:

`scheduler execution`

→ `phase-derived ternary target and request input`

→ `request-lane arbitration`

→ `pending-route eligibility`

→ `active-neutral routing through 0`

→ `transition-capacity guard`

→ `retained-state and pending-route writeback`

### M16 RTL Files

| Path | Purpose |
|---|---|
| `rtl/m16/frp_m16_pkg.sv` | constants, encodings, helper functions, scheduler decoding, transition classification |
| `rtl/m16/frp_m16_scheduler.sv` | `free`, `7/1`, and `1/7` scheduler-state realization |
| `rtl/m16/frp_m16_request_lanes.sv` | deterministic request-lane arbitration |
| `rtl/m16/frp_m16_pending_routes.sv` | pending-route register layer |
| `rtl/m16/frp_m16_active_neutral.sv` | active-neutral transition generation |
| `rtl/m16/frp_m16_capacity_guard.sv` | transition-capacity enforcement |
| `rtl/m16/frp_m16_state_update.sv` | retained-state writeback |
| `rtl/m16/frp_m16_core.sv` | integrated M16 RTL core |
| `rtl/m16/frp_m16_assertions.sv` | assertion binding layer |
| `rtl/m16/frp_m16_tb.sv` | deterministic executable RTL testbench |

### M16 RTL Documentation

| Path | Purpose |
|---|---|
| `rtl/m16/README.md` | M16 RTL layer overview |
| `rtl/m16/ARTIFACTS.md` | RTL artifact manifest |
| `rtl/m16/SIMULATION.md` | simulator execution instructions |
| `rtl/m16/SIMULATION_TRANSCRIPT.md` | qualified simulation transcript |
| `rtl/m16/CLOSURE.md` | RTL closure report |

### M16 Closure Status

Current M16 RTL status:

`M16 RTL EXECUTION LAYER CLOSED`

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

M16 RTL execution and invariant records:

| Record | Result |
|---|---:|
| cells | `8` |
| request lanes | `2` |
| `ticks_recorded` | `16` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

### M16 FPGA Preparation Layer

Path:

`fpga/m16/`

Purpose:

Target-independent FPGA integration, reset synchronization, readiness generation, execution-input gating, and executable integration-testbench boundary for FRP v1.8.0 M16.

The FPGA preparation layer integrates the qualified M16 RTL core through a target-independent boundary.

### M16 FPGA Files

| Path | Purpose |
|---|---|
| `fpga/m16/frp_m16_fpga_top.sv` | target-independent FPGA integration top |
| `fpga/m16/frp_m16_fpga_tb.sv` | executable FPGA integration testbench |

### M16 FPGA Documentation

| Path | Purpose |
|---|---|
| `fpga/m16/SIMULATION_TRANSCRIPT.md` | FPGA integration simulation transcript |
| `fpga/m16/CLOSURE.md` | FPGA preparation closure record |

M16 FPGA preparation domains:

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

Current M16 FPGA preparation status:

`M16 FPGA PREPARATION LAYER CLOSED`

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

## 7. Balanced Ternary Hardware Encoding

FRP v1.7.0 defines the canonical two-bit balanced ternary encoding:

`-1 → 2'b11`

`0 → 2'b00`

`+1 → 2'b01`

Reserved encoding:

`2'b10`

Canonical integer encoding:

`-1 → 3`

`0 → 0`

`+1 → 1`

Reserved integer code:

`2`

Validated invariant:

`reserved_state_events = 0`

## 8. Qualified M15 Artifact Layers

The qualified M15 executable semantic reference defines ten implementation-mapping and qualification layers:

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

Qualified M15 primary numeric representations:

| Domain | Representation |
|---|---|
| general dynamic scalar | `S32Q16` |
| normalized coefficient | `S32Q30` |
| phase | `PHASE_U32` |
| Sakaguchi gamma | `GAMMA_S32` |

Qualified M15 deterministic trigonometric profile:

`4096-entry full-cycle lookup table`

Required exactness markers:

`fixed_point_topology_sum_exact = True`

`fixed_point_thermal_sum_exact = True`

## 9. Repository Root

The repository root contains:

- the current Python executable semantic reference file;
- the complete historical executable reference chain;
- the deterministic M17 published-artifact inventory generator;
- current and historical validation records;
- current and historical release notes;
- validation indices;
- architecture tracking documents;
- installation and usage documentation;
- reproducibility documentation;
- Continuous Integration documentation;
- contribution and security policies;
- citation and licensing metadata.

Current primary files:

| File | Purpose |
|---|---|
| `README.md` | main public processor overview, current M16 release boundary, and M17 qualification boundary |
| `frp_prototype_v1_7_0.py` | M15-qualified Python executable semantic reference retained by M16 |
| `frp_m17_publication_inventory.py` | deterministic read-only M17 published-artifact inventory generator |
| `TEST_REPORT_v1_8_0.md` | current M16 validation record |
| `FRP_VALIDATION_INDEX_v1_8_0.md` | current M16 validation index |
| `RELEASE_NOTES_v1_8_0.md` | current release notes |
| `ROADMAP.md` | architecture progression through M30 and M17 qualification status |
| `MILESTONES.md` | milestone chain from M0 through M30 and M17 qualification evidence |
| `PROJECT_STRUCTURE.md` | repository structure guide |
| `CHANGELOG.md` | version history and release chronology |
| `INSTALL.md` | installation and first-run path |
| `USAGE.md` | execution, command, export, and validation reference |
| `REPRODUCIBILITY.md` | M15 semantic-reference and M16 RTL/FPGA reproducibility path |
| `CI.md` | Continuous Integration and qualification documentation |
| `CONTRIBUTING.md` | contribution and validation guide |
| `SECURITY.md` | security policy |
| `CODE_OF_CONDUCT.md` | participation and conduct policy |
| `funding_brief.md` | partner and funding-facing technical brief |
| `requirements.txt` | Python dependency list |
| `CITATION.cff` | citation metadata |
| `LICENSE` | Apache License 2.0 |
| `NOTICE.md` | repository notice |
| `.gitignore` | ignored local files |

## 10. Executable Version Chain

The repository preserves the complete executable architecture chain.

| File | Architecture layer |
|---|---|
| `frp_prototype_v0_9_3_mobile.py` | original stabilized executable resonant reference layer |
| `frp_prototype_v0_9_4.py` | structured output and machine-readable validation |
| `frp_prototype_v0_9_5.py` | benchmark export and hardware signal mapping |
| `frp_prototype_v0_9_6.py` | HDL trace export and testbench scaffold |
| `frp_prototype_v0_9_7.py` | RTL interface contract and assertion harness |
| `frp_prototype_v0_9_8.py` | formal verification hooks and equivalence scaffold |
| `frp_prototype_v0_9_9.py` | FPGA synthesis and timing constraint scaffold |
| `frp_prototype_v1_0_0.py` | production release and stable interface freeze |
| `frp_prototype_v1_1_0.py` | silicon and heterogeneous implementation architecture |
| `frp_prototype_v1_2_0.py` | silicon production and tapeout readiness |
| `frp_prototype_v1_3_0.py` | production integration and external implementation handoff |
| `frp_prototype_v1_4_0.py` | external implementation feedback and production iteration |
| `frp_prototype_v1_5_0.py` | production scaling and implementation stabilization |
| `frp_prototype_v1_6_0.py` | physical implementation correlation and production qualification |
| `frp_prototype_v1_7_0.py` | implementation mapping, domain interface, and qualification closure |

Each executable file preserves its release-specific architecture state.

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

## 11. Validation Record Chain

The repository preserves release-specific test reports from the initial validated layer through the current M16 release.

Test reports:

- `TEST_REPORT_v0_9_3.md`;
- `TEST_REPORT_v0_9_4.md`;
- `TEST_REPORT_v0_9_5.md`;
- `TEST_REPORT_v0_9_6.md`;
- `TEST_REPORT_v0_9_7.md`;
- `TEST_REPORT_v0_9_8.md`;
- `TEST_REPORT_v0_9_9.md`;
- `TEST_REPORT_v1_0_0.md`;
- `TEST_REPORT_v1_1_0.md`;
- `TEST_REPORT_v1_2_0.md`;
- `TEST_REPORT_v1_3_0.md`;
- `TEST_REPORT_v1_4_0.md`;
- `TEST_REPORT_v1_5_0.md`;
- `TEST_REPORT_v1_6_0.md`;
- `TEST_REPORT_v1_7_0.md`;
- `TEST_REPORT_v1_8_0.md`.

Current validation record:

`TEST_REPORT_v1_8_0.md`

Current validation status:

`PASS`

Inherited validated M15 self-test result:

`41/41 PASS`

## 12. Validation Index Chain

Validation indices are preserved for the architecture layers from M7 through M16.

Files:

- `FRP_VALIDATION_INDEX_v0_9_9.md`;
- `FRP_VALIDATION_INDEX_v1_0_0.md`;
- `FRP_VALIDATION_INDEX_v1_1_0.md`;
- `FRP_VALIDATION_INDEX_v1_2_0.md`;
- `FRP_VALIDATION_INDEX_v1_3_0.md`;
- `FRP_VALIDATION_INDEX_v1_4_0.md`;
- `FRP_VALIDATION_INDEX_v1_5_0.md`;
- `FRP_VALIDATION_INDEX_v1_6_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`.

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Each validation index preserves its release-specific qualification record.

## 13. Release Record Chain

The repository preserves release notes for every published architecture layer.

Files:

- `RELEASE_NOTES_v0_9_3.md`;
- `RELEASE_NOTES_v0_9_4.md`;
- `RELEASE_NOTES_v0_9_5.md`;
- `RELEASE_NOTES_v0_9_6.md`;
- `RELEASE_NOTES_v0_9_7.md`;
- `RELEASE_NOTES_v0_9_8.md`;
- `RELEASE_NOTES_v0_9_9.md`;
- `RELEASE_NOTES_v1_0_0.md`;
- `RELEASE_NOTES_v1_1_0.md`;
- `RELEASE_NOTES_v1_2_0.md`;
- `RELEASE_NOTES_v1_3_0.md`;
- `RELEASE_NOTES_v1_4_0.md`;
- `RELEASE_NOTES_v1_5_0.md`;
- `RELEASE_NOTES_v1_6_0.md`;
- `RELEASE_NOTES_v1_7_0.md`;
- `RELEASE_NOTES_v1_8_0.md`.

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

The repository also preserves:

- `RELEASE_CHECKLIST_v0_9_3.md`;
- `FRP_PRODUCTION_RELEASE_MANIFEST_v1_0_0.md`.

## 14. Documentation Directory

Directory:

`docs/`

The `docs/` directory contains the public technical documentation layer.

### Core documentation

| File | Purpose |
|---|---|
| `docs/README.md` | documentation architecture index |
| `docs/core_principles.md` | foundational FRP operating principles |
| `docs/resonance_computation.md` | resonance-based computational interpretation |
| `docs/architecture.md` | architecture documentation |
| `docs/benchmark_interpretation.md` | benchmark interpretation and evidence scope |
| `docs/limitations.md` | version-specific evidence and scope record |
| `docs/output_schema.md` | output and machine-readable validation structure |
| `docs/mathematical_foundation.md` | FRP mathematical foundation |
| `docs/physical_foundation.md` | FRP physical foundation |
| `docs/frp_v1_8_0_m16_architecture-1.gif` | README M16 architecture image |
| `docs/frp_v1_8_0_m16_architecture-1-1.gif` | M16 architecture image asset |

### Hardware-facing pathway documentation

| File | Purpose |
|---|---|
| `docs/hardware_pathway.md` | hardware-facing development pathway |
| `docs/implementation_layers.md` | staged implementation layers |
| `docs/fpga_mapping_study.md` | FPGA-oriented mapping study |
| `docs/asic_mapping_study.md` | ASIC-oriented mapping study |
| `docs/physical_validation_plan.md` | physical validation planning |

### M3 documentation

| File | Purpose |
|---|---|
| `docs/m3_validation_targets.md` | M3 validation targets |
| `docs/benchmark_matrix.md` | benchmark export structure |
| `docs/hardware_signal_mapping.md` | hardware-facing signal mapping |
| `docs/fpga_register_map_draft.md` | FPGA register-map draft |
| `docs/testbench_comparison_plan.md` | testbench comparison plan |

### M4 through M16 architecture documents

| File | Architecture layer |
|---|---|
| `docs/m4_hdl_trace_testbench.md` | M4 HDL Trace Export and Testbench Scaffold |
| `docs/m5_rtl_interface_assertion_harness.md` | M5 RTL Interface Contract and Assertion Harness |
| `docs/m6_formal_verification_equivalence.md` | M6 Formal Verification Hooks and Equivalence Scaffold |
| `docs/m7_fpga_synthesis_timing.md` | M7 FPGA Synthesis Package and Timing Constraint Scaffold |
| `docs/m8_production_release_package.md` | M8 Production Release Package and Stable Interface Freeze |
| `docs/m9_silicon_heterogeneous_architecture.md` | M9 Silicon and Heterogeneous Implementation Architecture |
| `docs/m10_silicon_production_tapeout_readiness.md` | M10 Silicon Production and Tapeout Readiness Package |
| `docs/m11_production_integration_external_handoff.md` | M11 Production Integration and External Implementation Handoff |
| `docs/m12_external_implementation_feedback_iteration.md` | M12 External Implementation Feedback and Production Iteration Loop |
| `docs/m13_production_scaling_implementation_stabilization.md` | M13 Production Scaling and Implementation Stabilization Package |
| `docs/m14_physical_implementation_correlation_production_qualification.md` | M14 Physical Implementation Correlation and Production Qualification Package |
| `docs/m15_implementation_mapping_domain_interface_qualification_closure.md` | qualified M15 Implementation Mapping, Domain Interface, and Qualification Closure Package foundation |
| `docs/m16_rtl_core_realization_execution_semantics.md` | M16 RTL Core Realization and Execution Semantics Package |
| `docs/m16_rtl_core_interface_contract.md` | M16 RTL core interface contract |
| `docs/m16_scheduler_state_rtl_realization.md` | M16 scheduler-state RTL realization |
| `docs/m16_request_lane_arbitration_module.md` | M16 request-lane arbitration module |
| `docs/m16_pending_route_register_module.md` | M16 pending-route register module |
| `docs/m16_active_neutral_transition_module.md` | M16 active-neutral transition module |
| `docs/m16_transition_capacity_guard_module.md` | M16 transition-capacity guard module |
| `docs/m16_retained_state_update_module.md` | M16 retained-state update module |
| `docs/m16_balanced_ternary_state_register_map.md` | M16 balanced ternary state register map |
| `docs/m16_invariant_assertion_set.md` | M16 invariant assertion set |
| `docs/m16_external_simulator_execution_plan.md` | M16 external simulator execution plan |
| `docs/m16_m15_vector_replay_compatibility_report.md` | M15 vector replay compatibility record for M16 |
| `docs/m16_rtl_artifact_boundary_qualification.md` | M16 RTL artifact-boundary qualification record |
| `docs/m16_artifact_boundary_test_stability_policy.md` | M16 artifact-boundary test stability policy |
| `docs/m16_qualification_manifest.md` | M16 qualification manifest |
| `docs/m16_qualification_index.md` | M16 qualification index |
| `docs/m16_public_status_snapshot.md` | M16 public status snapshot |

### M17 published-artifact integration documents

| File | Purpose |
|---|---|
| `docs/m17_published_artifact_integration_contract.md` | normative one-way FRP publication and downstream integration contract |
| `docs/m17_published_artifact_integration_qualification.md` | M17 post-execution qualification record |
| `docs/m17_published_artifact_integration_closure.md` | M17 qualification-boundary closure record |

Current architecture document:

`docs/m16_rtl_core_realization_execution_semantics.md`

The repository also preserves the root-level M5 companion document:

`m5_rtl_interface_assertion_harness.md`

## 15. Verification Directory

Directory:

`verification/`

Files:

| File | Purpose |
|---|---|
| `verification/README.md` | verification layer overview |
| `verification/coherence_metrics.md` | coherence and operational metric definitions |

The verification layer documents:

- phase coherence;
- operational coherence;
- dynamic stability;
- execution telemetry.

## 16. Examples Directory

Directory:

`examples/`

Files:

| File | Purpose |
|---|---|
| `examples/README.md` | examples overview |
| `examples/resonance_convergence_example.md` | resonance-convergence example |

The examples layer provides practical interpretation material for repository review.

## 17. Simulations Directory

Directory:

`simulations/`

Files:

| File | Purpose |
|---|---|
| `simulations/README.md` | simulation background index |
| `simulations/initial_kuramoto_result.md` | preliminary Kuramoto background result |

The simulation directory preserves supporting historical background material for the processor architecture.

Current release qualification is recorded through the M15 executable semantic reference, M16 RTL and FPGA preparation artifacts, GitHub Actions workflows, test reports, validation indices, release notes, and qualification artifacts.

## 18. Models Directory

Directory:

`models/`

Files:

| File | Purpose |
|---|---|
| `models/README.md` | model background index |
| `models/kuramoto_frp_background_model.md` | Kuramoto-type background model context |

The model directory preserves conceptual and mathematical background for the resonant phase layer.

The current Python executable semantic reference is:

`frp_prototype_v1_7_0.py`

## 19. Comparative Architecture Benchmark Directory

Directory:

`benchmarks/architecture_comparison/`

The Comparative Architecture Benchmark Suite provides a supporting validation contour aligned with the qualified M15 semantic and implementation-mapping foundation retained by M16:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

The suite compares:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The comparison chain is:

`one deterministic semantic workload`

↓

`architecture-specific execution`

↓

`raw architecture event counters`

↓

`one common normalized cost model`

↓

`one common thermal proxy model`

↓

`machine-readable comparison matrix`

The suite extends the repository validation surface with deterministic architecture-level comparison and hardware-sensitivity analysis.

### Benchmark execution files

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/run_architecture_comparison.py` | canonical comparative architecture benchmark runner |
| `benchmarks/architecture_comparison/run_hardware_sensitivity_comparison.py` | hardware-informed sensitivity comparison runner |
| `benchmarks/architecture_comparison/validate_hardware_sensitivity_profile.py` | hardware-sensitivity profile validator |

### Architecture reference files

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/binary_synchronous_reference.py` | binary synchronous reference |
| `benchmarks/architecture_comparison/binary_clock_gated_reference.py` | binary clock-gated reference |
| `benchmarks/architecture_comparison/direct_ternary_reference.py` | direct ternary reference |
| `benchmarks/architecture_comparison/frp_v1_7_0_adapter.py` | FRP v1.7.0 benchmark adapter |

### Shared benchmark model files

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/common_workload.py` | shared deterministic semantic workload |
| `benchmarks/architecture_comparison/common_cost_model.py` | common normalized cost model |
| `benchmarks/architecture_comparison/common_thermal_model.py` | common thermal proxy model |

### Benchmark profiles

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/profiles/workload_profile_v1.json` | deterministic workload profile |
| `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json` | normalized cost profile |
| `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json` | common thermal proxy profile |
| `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json` | hardware-sensitivity cost profile |

### Calibration and coefficient provenance

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/calibration/hardware_cost_calibration_v1.md` | hardware-cost calibration layer |
| `benchmarks/architecture_comparison/calibration/coefficient_provenance_map_v1.md` | coefficient provenance map |

### Machine-readable comparison results

| File | Purpose |
|---|---|
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json` | canonical comparative architecture result |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json` | hardware-sensitivity comparison result |

Current qualification policy:

`integrity_only_no_winner_assertions`

Current winner assertions:

`[]`

## 20. Tests Directory

Directory:

`tests/`

Files:

| File | Purpose |
|---|---|
| `tests/test_m16_rtl_artifact_manifest.py` | M16 RTL artifact-set, module-structure, execution-mode, active-neutral routing, pending-route, capacity, assertion, and simulation-command validation |
| `tests/test_frp_m17_publication_inventory.py` | dependency-free M17 publication-inventory, provenance, ordering, digest, schema-identity, publication-state, and CLI validation |

The M16 test layer validates:

- the exact ten-file M16 SystemVerilog source boundary;
- the five M16 RTL documentation artifacts;
- canonical ternary encodings;
- `free`, `7/1`, and `1/7` temporal execution modes;
- deterministic request-lane order;
- retained pending polarity;
- active-neutral routing through state `0`;
- bounded transition capacity;
- retained-state writeback;
- assertion coverage;
- simulator build and execution commands;
- zero-event relations.

The M17 test layer validates:

- exact inventory and self-test schema identities;
- one-way FRP publication integration direction;
- canonical `-1/0/1` domain;
- both active-neutral opposite-polarity routes;
- lexicographic record ordering;
- unique record identifiers;
- exact inventory summary and publication-state counts;
- exact schema-identifier registry;
- exact M15 export-schema set;
- exact M15 producer and workflow bindings;
- exact M15 vector-package member order and names;
- distinct `free`, `7/1`, and `1/7` scheduler vector-member identities;
- exact M16 RTL and FPGA workflow-member sets;
- committed-artifact raw-byte provenance;
- measurement-contour separation;
- four explicit `planned_unavailable` records;
- deterministic inventory content digest;
- byte-identical inventory rendering;
- source immutability during inventory generation;
- CLI write and self-test behavior;
- unsafe relative-path rejection.

M17 test result:

`30 / 30 PASS`

## 21. GitHub Actions Directory

Directory:

`.github/workflows/`

The repository contains 24 GitHub Actions workflow files.

The workflow structure covers:

- foundational executable validation;
- foundational resonant benchmark validation;
- structured output validation;
- architecture milestone qualification from M3 through M17;
- M16 canonical-domain and repository-maintenance validation;
- M17 published-artifact integration qualification;
- comparative architecture qualification;
- hardware-sensitivity comparison qualification;
- hardware-sensitivity profile qualification.

### Foundational validation workflows

| Workflow | Purpose |
|---|---|
| `frp-self-test.yml` | standard FRP self-test |
| `frp-benchmark-smoke.yml` | resonant benchmark smoke test |
| `frp-structured-output.yml` | structured output validation |

### M3 through M15 architecture milestone workflows

| Workflow | Architecture layer |
|---|---|
| `frp-m3-benchmark-signal-map.yml` | M3 Benchmark Export and Hardware Signal Mapping |
| `frp-m4-hdl-trace.yml` | M4 HDL Trace and Testbench |
| `frp-m5-rtl-assertion-harness.yml` | M5 RTL Interface and Assertion Harness |
| `frp-m6-formal-verification.yml` | M6 Formal Verification and Equivalence |
| `frp-m7-fpga-synthesis.yml` | M7 FPGA Synthesis and Timing |
| `frp-m8-production-release.yml` | M8 Production Release Package |
| `frp-m9-silicon-architecture.yml` | M9 Silicon and Heterogeneous Architecture |
| `frp-m10-silicon-production-tapeout.yml` | M10 Silicon Production and Tapeout Readiness |
| `frp-m11-production-integration-handoff.yml` | M11 Production Integration and External Handoff |
| `frp-m12-feedback-iteration.yml` | M12 External Implementation Feedback and Production Iteration |
| `frp-m13-production-scaling-stabilization.yml` | M13 Production Scaling and Implementation Stabilization |
| `frp-m14-physical-implementation-qualification.yml` | M14 Physical Implementation Correlation and Production Qualification |
| `frp-m15-implementation-mapping-qualification.yml` | qualified M15 Implementation Mapping and Qualification Closure foundation |

### M16 qualification and maintenance workflows

| Workflow | Purpose |
|---|---|
| `frp-m16-rtl-artifact-boundary.yml` | M16 RTL artifact-boundary qualification |
| `frp-m16-fpga-preparation.yml` | M16 FPGA preparation qualification |
| `frp-m16-canonical-core-domain.yml` | M16 canonical `{-1, 0, 1}` core-domain validation |
| `frp-m16-reserved-cell-cleanup.yml` | M16 reserved-cell cleanup validation |

### M17 qualification workflow

| Workflow | Purpose |
|---|---|
| `frp-m17-published-artifact-integration.yml` | deterministic M17 publication-inventory and one-way integration-boundary qualification |

### Supporting comparative workflows

| Workflow | Purpose |
|---|---|
| `frp-architecture-comparison.yml` | comparative architecture benchmark qualification |
| `frp-hardware-sensitivity-comparison.yml` | hardware-sensitivity comparison qualification |
| `frp-hardware-sensitivity-profile.yml` | hardware-sensitivity profile qualification |

Current qualification workflow layers:

- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`;
- `.github/workflows/frp-m17-published-artifact-integration.yml`.


## 22. README Architecture Image and CI Workflow Badge Chain

The root `README.md` contains one clickable M16 architecture image.

Image source:

`docs/frp_v1_8_0_m16_architecture-1.gif`

Image link target:

`#current-architecture-layer`

Image label:

`FRP v1.8.0 — M16 — RTL Core Realization and Execution Semantics Package`

The complete GitHub Actions workflow badge chain is recorded in `CI.md`.

`CI.md` contains 24 workflow status badges for the 24 repository workflow files:

| Workflow badge | Workflow file |
|---|---|
| `FRP M17 Published Artifact Integration` | `frp-m17-published-artifact-integration.yml` |
| `FRP M16 RTL Artifact Boundary` | `frp-m16-rtl-artifact-boundary.yml` |
| `FRP M16 FPGA Preparation` | `frp-m16-fpga-preparation.yml` |
| `FRP M16 Canonical Core Domain` | `frp-m16-canonical-core-domain.yml` |
| `FRP M16 Reserved Cell Cleanup` | `frp-m16-reserved-cell-cleanup.yml` |
| `FRP M15 Implementation Mapping and Qualification Closure` | `frp-m15-implementation-mapping-qualification.yml` |
| `FRP M14 Physical Implementation Correlation and Production Qualification` | `frp-m14-physical-implementation-qualification.yml` |
| `FRP M13 Production Scaling and Implementation Stabilization` | `frp-m13-production-scaling-stabilization.yml` |
| `FRP M12 External Implementation Feedback and Production Iteration` | `frp-m12-feedback-iteration.yml` |
| `FRP M11 Production Integration and External Handoff` | `frp-m11-production-integration-handoff.yml` |
| `FRP M10 Silicon Production and Tapeout Readiness` | `frp-m10-silicon-production-tapeout.yml` |
| `FRP M9 Silicon and Heterogeneous Architecture` | `frp-m9-silicon-architecture.yml` |
| `FRP M8 Production Release Package` | `frp-m8-production-release.yml` |
| `FRP M7 FPGA Synthesis and Timing Scaffold` | `frp-m7-fpga-synthesis.yml` |
| `FRP M6 Formal Verification and Equivalence Scaffold` | `frp-m6-formal-verification.yml` |
| `FRP M5 RTL Interface and Assertion Harness` | `frp-m5-rtl-assertion-harness.yml` |
| `FRP M4 HDL Trace and Testbench` | `frp-m4-hdl-trace.yml` |
| `FRP M3 Benchmark and Signal Map` | `frp-m3-benchmark-signal-map.yml` |
| `FRP Self Test` | `frp-self-test.yml` |
| `FRP Benchmark Smoke Test` | `frp-benchmark-smoke.yml` |
| `FRP Structured Output` | `frp-structured-output.yml` |
| `FRP Comparative Architecture Benchmark` | `frp-architecture-comparison.yml` |
| `FRP Hardware Sensitivity Profile Qualification` | `frp-hardware-sensitivity-profile.yml` |
| `FRP Hardware Sensitivity Comparison` | `frp-hardware-sensitivity-comparison.yml` |

## 23. M15 Foundation, M16 Validation, and M17 Qualification Evidence

Qualified M15 foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

M15 validation environment:

`GitHub Actions`

M15 release-record validated commit:

`5fd9a4f`

Validated workflow stack recorded in `TEST_REPORT_v1_7_0.md`:

- `FRP Structured Output #113`;
- `FRP M15 Implementation Mapping and Qualification Closure #1`;
- `FRP Self Test #154`;
- `FRP Benchmark Smoke Test #152`.

M15 validation result:

`PASS`

M15 self-test result:

`41/41 PASS`

M15 deterministic results:

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

M15 validation records:

- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`.

The release-record commit and workflow-run identifiers preserve the published v1.7.0 validation evidence.

Current validated release layer:

`FRP v1.8.0 — M16 RTL Core Realization and Execution Semantics Package`

M16 validation environment:

- `GitHub Actions`;
- Verilator SystemVerilog parsing and elaboration;
- executable compiled RTL and FPGA integration testbenches;
- SystemVerilog assertion execution.

M16 RTL qualification records:

| Qualification record | Workflow run | Qualified commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Current qualification record | `#88` | `975222b` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |

M16 FPGA preparation qualification records:

| Qualification record | Workflow run | Qualified commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Current qualification record | `#6` | `975222b` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

Current M16 validation result:

`PASS`

Current M16 validation records:

- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`.

Qualified M17 published-artifact integration boundary:

`M17 QUALIFICATION BOUNDARY CLOSED`

M17 provisional version:

`v1.9.0`

M17 machine-readable inventory milestone state:

`planned`

M17 qualification workflow record:

| Record | Value |
|---|---|
| Workflow | `FRP M17 Published Artifact Integration` |
| Workflow file | `.github/workflows/frp-m17-published-artifact-integration.yml` |
| Workflow run | `#1` |
| Qualified commit | `08e5714` |
| Branch | `main` |
| Result | `SUCCESS` |
| Duration | `16s` |
| Evidence retention | `30 days` |
| Status | `M17 QUALIFICATION BOUNDARY CLOSED` |

M17 deterministic qualification results:

| Qualification record | Result |
|---|---:|
| inventory records | `63` |
| exact schema identifiers | `17` |
| built-in inventory self-test | `25 / 25 PASS` |
| dependency-free unit-test suite | `30 / 30 PASS` |
| deterministic inventory renderings | `2 / 2 byte-identical` |
| deterministic record ordering | `PASS` |
| inventory content-digest validation | `PASS` |
| repository-committed raw SHA-256 validation | `PASS` |
| measurement-contour separation | `PASS` |
| repository immutability | `PASS` |

M17 scheduler-mode identities:

- `free`;
- `7/1`: seven `balance` ticks followed by one `commit` tick;
- `1/7`: one `excite` tick followed by seven `neutralize` ticks.

M17 qualification records:

- `docs/m17_published_artifact_integration_contract.md`;
- `docs/m17_published_artifact_integration_qualification.md`;
- `docs/m17_published_artifact_integration_closure.md`.

Current published release boundary:

`FRP v1.8.0 / M16`

The qualified M17 contract, deterministic inventory, provenance records, publication-state records, and one-way integration boundary form the baseline for M18.

## 24. Architecture Milestone Chain

The repository structure records the published and planned architecture progression from M0 through M30.

Current published release boundary:

`FRP v1.8.0 / M16`

Qualified M17 integration boundary:

`M17 QUALIFICATION BOUNDARY CLOSED`

M17 release target:

`v1.9.0 — provisional`

M17 through M30 are completed qualification and archival release targets.

| Milestone | Version | Architecture layer | Status |
|---|---|---|---|
| M0 | v0.9.3-mobile | Repository Stabilization | Completed |
| M1 | v0.9.3 | Archival Release and DOI | Completed |
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
| M17 | v1.9.0 | Published Artifact Integration Contract | Completed |
| M18 | v2.0.0 | Formal Schema and Canonical Artifact Publication | Completed |
| M19 | v2.1.0 | Machine-Readable M16 Execution and Qualification Evidence | Completed |
| M20 | v2.2.0 | Cross-Layer Deterministic Correlation | Completed |
| M21 | v2.3.0 | Parameterized Qualification Matrix | Completed |
| M22 | v2.4.0 | Control, Status, and Register Interface Realization | Completed |
| M23 | v2.5.0 | Clock, Reset, CDC, and Interface Hardening | Completed |
| M24 | v2.6.0 | Formal and Bounded Verification Closure | Completed |
| M25 | v2.7.0 | Fault, Negative-Path, and Recovery Qualification | Completed |
| M26 | v2.8.0 | Declared-Target Implementation Evidence | Completed |
| M27 | v2.9.0 | Long-Run Stability and Telemetry Qualification | Completed |
| M28 | v3.0.0 | Hierarchical Scaling and Hotspot-Containment Realization | Completed |
| M29 | v3.1.0 | System Integration and Downstream Compatibility Closure | Completed |
| M30 | v3.2.0 | Reproducibility, Qualification, and Archival Release Closure | Completed |

Architecture tracking is maintained in:

- `ROADMAP.md`;
- `MILESTONES.md`.

## 25. Reproducibility Layer

The current reproducibility chain is:

`INSTALL.md`

↓

`USAGE.md`

↓

`REPRODUCIBILITY.md`

↓

`CI.md`

↓

`current Python executable semantic reference`

↓

`current qualification workflows`

↓

`Run Job result`

↓

`current test report`

↓

`current validation index`

↓

`current release notes`

The current Python executable semantic reference is:

`frp_prototype_v1_7_0.py`

Current validation records:

- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`.

## 26. Release and Metadata Layer

Release and repository metadata files include:

| File | Purpose |
|---|---|
| `CHANGELOG.md` | version chronology |
| `ROADMAP.md` | architecture progression |
| `MILESTONES.md` | milestone structure |
| `CITATION.cff` | citation metadata |
| `LICENSE` | Apache License 2.0 |
| `NOTICE.md` | repository notice |
| `SECURITY.md` | security policy |
| `CONTRIBUTING.md` | contribution and validation guide |
| `CODE_OF_CONDUCT.md` | participation and conduct policy |
| `funding_brief.md` | partner and funding-facing technical brief |

Release-specific test reports, release notes, validation indices, and release manifests preserve architecture traceability.

## 27. Repository Naming Discipline

Processor name:

`FRP — Fractal Resonance Processor`

Processor class:

`Ternary Resonant Coherence Processor`

Current Python executable semantic-reference form:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Current test report:

`TEST_REPORT_v1_8_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Qualified semantic and implementation-mapping foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Each release-specific file retains its release-specific version identity.

## 28. Repository Alignment Rule

When the current release boundary, qualification boundary, or planned architecture progression changes, review:

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
- `docs/m17_published_artifact_integration_contract.md`;
- `docs/m17_published_artifact_integration_qualification.md`;
- `docs/m17_published_artifact_integration_closure.md`;
- `frp_m17_publication_inventory.py`;
- `.github/workflows/frp-m17-published-artifact-integration.yml`;
- `rtl/m16/`;
- `fpga/m16/`;
- `tests/`;
- current executable semantic reference;
- current `TEST_REPORT`;
- current `RELEASE_NOTES`;
- current `FRP_VALIDATION_INDEX`;
- current architecture document;
- current qualification workflows.

The alignment review checks:

- current published release version and milestone;
- current qualification-boundary status;
- provisional milestone and version identities;
- current executable semantic-reference filename;
- current validation result;
- exact schema identifiers;
- exact inventory and self-test identities;
- current workflow paths;
- qualified workflow runs and commits;
- deterministic evidence counts;
- publication-state counts;
- repository-committed raw SHA-256 bindings;
- complete computational core;
- canonical `-1/0/1` state domain;
- active neutral state `0`;
- distinct `free`, `7/1`, and `1/7` scheduler-mode identities;
- exact `7/1` balance-to-commit sequence;
- exact `1/7` excite-to-neutralize sequence;
- measurement-contour separation;
- one-way FRP publication boundary;
- README architecture image path and link target;
- `CI.md` GitHub Actions badge chain;
- release-specific and qualification-specific architecture traceability.

Historical release and qualification records remain bound to their recorded versions, workflow runs, commits, schemas, and evidence.

## 29. Current Public Repository Structure

The current public repository contains:

- the complete executable FRP version chain from v0.9.3-mobile through v1.7.0;
- the M15-qualified `frp_prototype_v1_7_0.py` Python executable semantic reference retained by M16;
- the current FRP v1.8.0 M16 RTL execution and FPGA preparation layer;
- the qualified M17 published-artifact integration boundary;
- the deterministic `frp_m17_publication_inventory.py` inventory generator;
- the dependency-free `tests/test_frp_m17_publication_inventory.py` qualification suite;
- the M17 published-artifact integration workflow;
- three M17 integration, qualification, and closure documents;
- Kuramoto-Sakaguchi resonant phase coupling;
- asymmetric phase lag gamma;
- hierarchical fractal phase interaction;
- phase evolution;
- resonance selection;
- Kuramoto order parameter `R`;
- multiscale phase coherence;
- stateful delay dynamics;
- distributed local thermal dynamics;
- thermal coupling-factor evolution;
- local correlated gamma drift;
- nonlinear coherence compression;
- dynamic stability evaluation;
- phase-derived balanced ternary target formation;
- canonical balanced ternary state domain `-1/0/1`;
- active neutral state `0`;
- mandatory tick-separated neutral routing;
- `-1 → 0 → 1` and `1 → 0 → -1` routes;
- distinct `free`, `7/1`, and `1/7` scheduler modes;
- seven `balance` ticks followed by one `commit` tick in `7/1` mode;
- one `excite` tick followed by seven `neutralize` ticks in `1/7` mode;
- distributed commit;
- retained coherent ternary state;
- release-specific test reports;
- release-specific release notes;
- validation indices through M16;
- M3 through M16 architecture documentation;
- M17 publication-boundary documentation;
- structured output validation;
- hardware-facing signal mapping;
- HDL and testbench preparation;
- RTL interface and assertion layers;
- formal verification and equivalence scaffolds;
- FPGA synthesis and timing structures;
- production release and stable interface structures;
- silicon and heterogeneous implementation architecture;
- tapeout-readiness structures;
- external implementation handoff structures;
- production iteration and stabilization layers;
- physical implementation correlation and qualification;
- fixed-point implementation mapping;
- balanced ternary hardware encoding;
- stateful quantized hardware shadow execution;
- cycle-exact integer golden traces;
- deterministic RTL comparison vectors;
- SystemVerilog interface mapping;
- synthesizable RTL reference-core mapping;
- RTL assertion correlation;
- floating-to-quantized reference correlation;
- exact quantized deterministic replay;
- M15 qualification closure;
- ten M16 SystemVerilog RTL source files;
- five M16 RTL documentation artifacts;
- executable M16 RTL architectural simulation;
- M16 SystemVerilog assertion execution;
- ten integrated M16 invariant flags;
- target-independent M16 FPGA integration top;
- executable M16 FPGA integration testbench;
- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` and execution-input gating;
- two M16 FPGA preparation documentation artifacts;
- M16 RTL artifact-manifest tests;
- M17 deterministic publication-inventory tests;
- 63 M17 published-artifact inventory records;
- 17 exact M17 inventory schema identifiers;
- four explicit M17 `planned_unavailable` records;
- repository-committed raw SHA-256 provenance bindings;
- deterministic M17 inventory content-digest validation;
- independent measurement-contour assignments;
- one-way `FRP → published artifacts → downstream consumers` integration direction;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- reproducibility documentation;
- 24 GitHub Actions workflow files;
- one clickable M16 architecture image in the root README;
- 24 GitHub Actions workflow badges recorded in `CI.md`;
- Comparative Architecture Benchmark Suite support;
- hardware-sensitivity qualification;
- documentation, verification, examples, simulations, and model layers;
- citation and licensing metadata.

## 30. Current Status

Processor:

`Fractal Resonance Processor (FRP)`

Processor class:

`Ternary Resonant Coherence Processor`

Computational mechanism:

`Kuramoto-Sakaguchi resonant phase dynamics with asymmetric phase lag, hierarchical fractal coupling, phase evolution, resonance selection, Kuramoto order parameter R, multiscale phase coherence, stateful delay dynamics, local thermal-phase interaction, local correlated gamma drift, nonlinear coherence compression, dynamic stability evaluation, phase-derived ternary targets, distributed commit, mandatory active-neutral routing, and retained coherent ternary state`

State and retained-result domain:

`-1/0/1`

Active neutral state:

`0`

Mandatory opposite-polarity routes:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

Scheduler modes:

- `free`;
- `7/1`: seven `balance` ticks followed by one `commit` tick;
- `1/7`: one `excite` tick followed by seven `neutralize` ticks.

Current Python executable semantic-reference form:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

Current published release version:

`FRP v1.8.0`

Current published release milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current Python executable semantic reference:

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

Current release validation result:

`PASS`

Inherited validated M15 self-test result:

`41/41 PASS`

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current M16 canonical-domain and repository-maintenance workflows:

- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`.

Current M16 RTL qualification record:

| Record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#88` |
| Qualified source commit | `975222b` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation qualification record:

| Record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#6` |
| Qualified repository commit | `975222b` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

Current M16 RTL execution and invariant records:

| Record | Result |
|---|---:|
| `ticks_recorded` | `16` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

Current M16 FPGA preparation terminal execution records:

| Record | Result |
|---|---:|
| `core_ready` | `1` |
| `ticks_recorded` | `1` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| invariant flags | `1111111111` |

Current M17 qualification boundary:

`M17 QUALIFICATION BOUNDARY CLOSED`

M17 qualification result:

`PASS`

M17 provisional release target:

`v1.9.0`

M17 machine-readable inventory milestone state:

`planned`

M17 inventory schema:

`frp.m17.published_artifact_inventory.v1.9.0`

M17 self-test schema:

`frp.m17.published_artifact_inventory.self_test.v1.9.0`

M17 qualification workflow record:

| Record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m17-published-artifact-integration.yml` |
| Workflow run | `#1` |
| Qualified commit | `08e5714` |
| Branch | `main` |
| Result | `SUCCESS` |
| Duration | `16s` |
| Evidence retention | `30 days` |
| Status | `M17 QUALIFICATION BOUNDARY CLOSED` |

M17 qualification results:

| Record | Result |
|---|---:|
| inventory records | `63` |
| exact schema identifiers | `17` |
| built-in inventory self-test | `25 / 25 PASS` |
| dependency-free unit-test suite | `30 / 30 PASS` |
| deterministic inventory renderings | `2 / 2 byte-identical` |
| deterministic record ordering | `PASS` |
| inventory content-digest validation | `PASS` |
| repository-committed raw SHA-256 validation | `PASS` |
| measurement-contour separation | `PASS` |
| repository immutability | `PASS` |

M17 qualification source set:

- `docs/m17_published_artifact_integration_contract.md`;
- `frp_m17_publication_inventory.py`;
- `tests/test_frp_m17_publication_inventory.py`;
- `.github/workflows/frp-m17-published-artifact-integration.yml`;
- `docs/m17_published_artifact_integration_qualification.md`;
- `docs/m17_published_artifact_integration_closure.md`.

Current mathematical foundation:

`docs/mathematical_foundation.md`

Current physical foundation:

`docs/physical_foundation.md`

Next planned milestone:

`M18 — Formal Schema and Canonical Artifact Publication`

Next provisional version:

`v2.0.0`

Current repository role:

`preserve the complete published Fractal Resonance Processor architecture from Kuramoto-Sakaguchi resonant phase evolution, hierarchical fractal coupling, resonance selection, multiscale phase coherence, delay and thermal-phase dynamics, nonlinear coherence compression, phase-derived balanced ternary state formation, distributed active-neutral routing, and retained coherent state through structured validation, hardware-facing implementation mapping, cycle-exact execution, RTL correlation, reference equivalence, M15 qualification closure, M16 SystemVerilog RTL execution, target-independent FPGA preparation, and the qualified M17 one-way published-artifact integration boundary`

## 29. M30 Reproducibility and Archival Release Layer

M30 adds the following repository surfaces:

- `frp_m30_reproducibility_qualification_archival_closure.py`;
- `tests/test_frp_m30_reproducibility_qualification_archival_closure.py`;
- `.github/workflows/frp-m30-reproducibility-qualification-archival-release-closure-workflow.yml`;
- `schemas/m30/`;
- `artifacts/m30/`;
- `RELEASE_NOTES_v3_2_0.md`;
- `TEST_REPORT_v3_2_0.md`;
- `FRP_VALIDATION_INDEX_v3_2_0.md`.

The M30 package indexes the complete M17 through M29 evidence boundary,
records exact SHA-256 digests, captures successful required workflow runs,
constructs and verifies the deterministic archival release package, and
preserves the existing FRP Trace Observatory one-way read-only boundary.
