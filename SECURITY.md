# Security Policy

## Current Security Boundary — FRP v3.3.0 / M31

Current repository release:

`FRP v3.3.0 / M31 — PASS`

Current milestone:

`M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication`

Current balanced ternary domain:

`-1/0/1`

Current focused qualification:

`60 / 60 PASS`

## Current Public Security Scope

The public FRP security boundary includes:

- executable semantic-reference and milestone producer source;
- versioned Python tests and SystemVerilog testbenches;
- schemas and canonical artifacts;
- evidence, manifests, qualification records, and archival packages;
- benchmark inputs, outputs, comparison contours, and provenance;
- GitHub Actions workflow definitions and published workflow results;
- architecture, installation, reproducibility, governance, and release documentation.

Current release records:

- [`FRP_VALIDATION_INDEX_v3_3_0.md`](FRP_VALIDATION_INDEX_v3_3_0.md);
- [`RELEASE_NOTES_v3_3_0.md`](RELEASE_NOTES_v3_3_0.md);
- [`TEST_REPORT_v3_3_0.md`](TEST_REPORT_v3_3_0.md).

## Current M31 Publication Boundary

| Role | Path |
|---|---|
| Source | [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py) |
| Test | [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py) |
| Schema | [`schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json) |
| Evidence | [`artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json) |
| Manifest | [`artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json) |
| Qualification | [`artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json) |
| Workflow | [`.github/workflows/frp-m31-complete.yml`](.github/workflows/frp-m31-complete.yml) |

The M31 evidence, manifest, and qualification documents are canonical JSON records tied to their schema identifiers, source provenance, release identity, and recorded digests.

## Versioned SystemVerilog Security Boundary

The current public SystemVerilog files remain attached to their qualified milestone identities:

- M16 RTL core and assertion boundary: [`rtl/m16/`](rtl/m16/);
- M16 FPGA preparation boundary: [`fpga/m16/`](fpga/m16/);
- M22 control/status register interface: [`rtl/m22/`](rtl/m22/);
- M23 reset, CDC, protocol, and hardened integration boundary: [`rtl/m23/`](rtl/m23/);
- M26 declared-target implementation boundary: [`rtl/m26/`](rtl/m26/).

Each hardware-facing statement is evaluated against its versioned source, testbench, assertion, workflow, artifact, and qualification record.

## Integrity and Provenance Controls

Security review covers:

- source and generated-file digest consistency;
- schema identifier and validation consistency;
- canonical JSON ordering and reproducibility;
- artifact and manifest path integrity;
- release and milestone provenance;
- workflow permission scope;
- branch and manual-dispatch boundaries;
- dependency declarations in [`requirements.txt`](requirements.txt);
- preservation of historical evidence and benchmark contours;
- exact separation of measured, modeled, proxy, and historical metric domains.

Credentials, access tokens, private keys, authentication material, and private reports remain outside public artifacts, logs, generated evidence, test fixtures, and workflow summaries.

## FRP-to-Observatory Security Boundary

FRP is the upstream authority for processor semantics and canonical published bytes. FRP-Trace-Observatory consumes the published schemas, artifacts, identifiers, digests, and provenance through a one-way, read-only interchange.

The cross-repository boundary preserves:

- immutable FRP source artifacts;
- exact upstream digests;
- schema and compatibility identifiers;
- release and milestone provenance;
- measurement-contour separation;
- independent downstream presentation and audit logic.

## Responsible Disclosure Procedure

Security-sensitive findings are reported privately to the repository maintainer before public discussion.

A security report records:

- affected path, component, workflow, schema, artifact, or release;
- exact version, milestone, branch, and commit when available;
- reproducible steps or a minimal safe fixture;
- observed behavior and integrity impact;
- logs, traces, hashes, screenshots, or canonical outputs supporting the report;
- any condition required to reproduce the finding.

Public disclosure follows maintainer review and coordinated resolution of the affected boundary.

## Current Security Alignment

This current layer is aligned with:

- [`README.md`](README.md);
- [`INSTALL.md`](INSTALL.md);
- [`USAGE.md`](USAGE.md);
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md);
- [`ROADMAP.md`](ROADMAP.md);
- [`MILESTONES.md`](MILESTONES.md);
- [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md);
- [`CI.md`](CI.md);
- [`CONTRIBUTING.md`](CONTRIBUTING.md);
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Preserved Security Policy History Through M16

The Fractal Resonance Processor (FRP) repository contains the public research, executable semantic reference, documentation, verification, benchmark, implementation-mapping, SystemVerilog RTL execution, target-independent FPGA preparation, and qualification layers of the project.

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

Current published validation result:

`PASS`

Qualified semantic and implementation-mapping foundation:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Inherited validated M15 self-test result:

`41/41 PASS`

Current M16 RTL closure status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation closure status:

`M16 FPGA PREPARATION LAYER CLOSED`

## Public Repository Scope

The public repository may contain:

- public architecture documentation
- executable processor semantic-reference code
- structured output and reproducibility instructions
- benchmark reports and release-specific evidence
- verification and qualification records
- implementation-mapping artifacts
- hardware-facing interface and correlation documents
- SystemVerilog RTL source and executable testbench artifacts
- target-independent FPGA integration and executable testbench artifacts
- GitHub Actions workflow definitions
- historical release records
- public contribution and governance documents

## Excluded Material

The public repository excludes:

- private implementation parameters
- deployment-sensitive operational details
- private access-control material
- credentials, tokens, keys, or secrets
- private identity or authentication data
- unpublished restricted design layers
- private security reports under active review
- material that compromises safety, privacy, repository integrity, or responsible disclosure boundaries

## Repository Security Boundary

Public FRP material is governed by the evidence and release layer that generates it.

Technical, implementation, hardware-facing, benchmark, thermal, and performance statements should remain attached to their exact:

- release
- architecture identifier
- workload
- metric definition
- evidence source
- validation record

Historical benchmark contours remain identified by their original release and measurement domain.

Current FRP v1.8.0 material remains identified by:

- the M15-qualified Python executable semantic reference;
- the M15 semantic and implementation-mapping foundation;
- the M16 SystemVerilog RTL source and documentation boundaries;
- the M16 target-independent FPGA preparation boundary;
- the current M16 qualification workflows;
- the current test report, validation index, and release notes.

Security-sensitive findings remain inside the responsible disclosure process until maintainer review is complete.

## M16 Public Artifact Boundaries

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

M16 FPGA preparation boundary:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

## Current Qualification Records

M16 RTL qualification records:

| Qualification record | Workflow run | Qualified source commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| Qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |

M16 FPGA preparation qualification records:

| Qualification record | Workflow run | Qualified repository commit | Branch | Result | Artifact count | Status |
|---|---:|---|---|---|---:|---|
| Initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| Qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

Current zero-event records:

- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`.

Current integrated invariant vector:

`1111111111`

## Responsible Use

This repository is intended for research, educational, engineering, verification, benchmark, implementation-mapping, RTL execution, and FPGA preparation purposes.

Users are responsible for ensuring that derived work is used safely, ethically, and lawfully.

## Reporting Security Issues

Security-related issues should be reported responsibly to the repository maintainer.

A useful report should include:

- a clear description of the issue
- the affected file, component, workflow, artifact, or release
- reproduction information that can be shared safely
- the observed or potential impact
- supporting logs, traces, screenshots, or other evidence where relevant

Sensitive reports should be shared privately first, with reasonable review time provided before public disclosure.

## Current Status

This security policy is aligned with:

- `FRP v1.8.0`;
- `M16 — RTL Core Realization and Execution Semantics Package`;
- `frp_prototype_v1_7_0.py`;
- `frp.structured_output.v1.7.0`;
- `frp.m3.benchmark_matrix.v1.7.0`;
- `FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`;
- `README.md`;
- `CODE_OF_CONDUCT.md`;
- `CONTRIBUTING.md`;
- `docs/limitations.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`;
- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`;
- `rtl/m16/`;
- `fpga/m16/`;
- `tests/`.
