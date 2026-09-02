# Code of Conduct

## Current Conduct Boundary — FRP v3.3.0 / M31

This section defines the current participation boundary for the Fractal Resonance Processor repository. The complete code-of-conduct record through M16 remains preserved below this section.

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

## Scope of Participation

This code applies to participation connected to the FRP project, including:

- issues, pull requests, reviews, and repository discussions;
- commits, documentation, tests, schemas, evidence, benchmarks, and release records;
- GitHub Actions qualification and publication runs;
- SystemVerilog RTL, testbench, assertion, simulation, FPGA, and closure work;
- public statements that attribute technical behavior, measurements, or validation status to FRP;
- FRP interchange work consumed by FRP Trace Observatory;
- project communication conducted through public or private channels under maintainer control.

The current repository boundaries are recorded in [README.md](README.md), [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md), and [MILESTONES.md](MILESTONES.md).

## Technical Discussion Standard

Participation shall keep technical statements connected to verifiable repository records. Contributors and reviewers shall:

1. Distinguish implemented behavior, measured result, qualified result, proposed change, and open question.
2. Cite the source, test, schema, artifact, benchmark, workflow, or release record supporting a technical claim.
3. State the applicable release, milestone, workload, parameters, metric domain, and execution boundary.
4. Use `-1/0/1` exactly when naming the balanced ternary domain.
5. Treat state `0` as an active computational state in descriptions of FRP semantics.
6. Preserve the distinction between phase-derived targets and executed retained states.
7. Preserve the distinction between phase order, coherence, stability, switching load, and thermal evidence.
8. Correct factual or provenance errors with the corresponding evidence and replacement record.
9. Keep review focused on the submitted technical boundary and its testable consequences.

The current executable M31 boundary is [frp_m31_phase_interference_thermal_evidence.py](frp_m31_phase_interference_thermal_evidence.py), with focused tests in [tests/test_frp_m31_phase_interference_thermal_evidence.py](tests/test_frp_m31_phase_interference_thermal_evidence.py).

## Evidence and Provenance Conduct

Repository evidence is part of the public technical record. Participants shall preserve its identity and provenance.

Acceptable conduct includes:

- adding a separately named and versioned result when declared inputs change;
- recording exact source paths, parameters, schemas, environments, tests, and digests;
- reporting failed and successful qualification results with their actual status;
- correcting an error through a traceable commit and a new current record;
- keeping historical evidence, benchmark, schema, and release records available for audit.

Unacceptable conduct includes:

- altering published evidence while presenting it as the original record;
- deleting historical benchmark or qualification records to conceal a result;
- reporting an Actions run as green when a required job or step failed;
- detaching a measurement from its workload, parameters, release, or metric definition;
- presenting proposed, inferred, or downstream behavior as a qualified FRP result;
- fabricating digests, test counts, simulator output, benchmark values, workflow runs, or release status.

Protected technical histories reside under [artifacts/](artifacts/), [benchmarks/](benchmarks/), and [schemas/](schemas/), together with versioned validation indices, release notes, test reports, and release checklists at the repository root.

## M31 Publication Conduct

The current M31 publication boundary consists of:

- [M31 schema](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json);
- [M31 evidence](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json);
- [M31 manifest](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json);
- [M31 qualification record](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json);
- [M31 completion workflow](.github/workflows/frp-m31-complete.yml).

Review of this boundary shall use the published bytes, declared schema, focused 60-test qualification set, and recorded workflow result. Disagreement about interpretation remains separate from the identity of the published record.

## SystemVerilog Review Conduct

SystemVerilog work is reviewed within its versioned implementation boundary. Current repository contours are recorded under [rtl/m16/](rtl/m16/), [fpga/m16/](fpga/m16/), [rtl/m22/](rtl/m22/), [rtl/m23/](rtl/m23/), and [rtl/m26/](rtl/m26/).

Technical claims about an RTL contour shall identify its version and linked package, synthesizable modules, interfaces, assertions, testbench, simulator invocation, transcript, manifest, and closure evidence. Review comments shall distinguish source inspection, simulation result, synthesis result, target preparation, and published qualification status.

Existing versioned RTL and FPGA histories remain part of the audit record. A later contour does not retroactively replace the evidence identity of an earlier contour.

## GitHub Actions Conduct

Current documentation-alignment workflows are committed as complete files and executed manually through `workflow_dispatch` on `main`. Participants shall:

- review the workflow source before execution;
- confirm the selected branch and declared target;
- preserve source-identity and protected-history checks;
- keep credentials and tokens out of workflow source, logs, artifacts, and discussion;
- report the complete job result rather than an isolated successful step;
- identify and correct the exact failing boundary before rerunning;
- verify that publication changed only the workflow's declared target.

The current workflow and qualification record is summarized in [CI.md](CI.md). Contribution procedures are recorded in [CONTRIBUTING.md](CONTRIBUTING.md).

## FRP and Trace Observatory Conduct Boundary

FRP is the authoritative producer of processor sources, schemas, traces, structured evidence, manifests, qualification records, and benchmark records. FRP Trace Observatory consumes published FRP boundaries for intake, exploration, visualization, and audit.

The interchange is one-way and read-only:

`FRP published artifacts → Observatory intake, exploration, visualization, and audit`

Participants shall keep downstream visualization or interpretation distinct from canonical FRP bytes and qualified processor semantics. Observatory work does not write back into FRP sources, schemas, evidence, manifests, qualification records, or benchmark history. A changed interchange contract is versioned and qualified in FRP before downstream consumption.

## Security, Privacy, and Restricted Material

Credentials, access tokens, private keys, private identity data, embargoed material, and restricted design records are not published in issues, pull requests, workflows, logs, or artifacts. Security-sensitive findings follow the responsible-disclosure procedure in [SECURITY.md](SECURITY.md).

Public discussion begins after the maintainer has had a reasonable opportunity to inspect, reproduce, contain, and document the reported boundary. Conduct reports and security reports remain distinct, even when the same repository interaction involves both.

## Current Review References

Current participation and review shall remain aligned with:

- [INSTALL.md](INSTALL.md);
- [USAGE.md](USAGE.md);
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md);
- [ROADMAP.md](ROADMAP.md);
- [CHANGELOG.md](CHANGELOG.md);
- [NOTICE.md](NOTICE.md).

Maintainer action may include requesting evidence, limiting disclosure of sensitive material, editing or closing off-topic records, rejecting unsupported claims, reverting provenance-breaking changes, or restricting participation after repeated violations. Actions shall be connected to repository scope, evidence integrity, security, reproducibility, or the conduct requirements recorded here.

## Preserved Code-of-Conduct Record Through M16

## 1. Purpose

The Fractal Resonance Processor (FRP) project is a public research, executable semantic reference, implementation-mapping, SystemVerilog RTL execution, target-independent FPGA preparation, verification, benchmark, and documentation repository.

This code of conduct defines the expected standard for participation in issues, pull requests, discussions, and repository collaboration.

## 2. Expected Conduct

Participants are expected to:

- communicate respectfully
- focus on technical content
- provide evidence for technical claims
- attach benchmark and performance statements to their exact metric domain, workload, release, and evidence source
- distinguish historical evidence contours from the current validated architecture
- respect repository scope and documentation boundaries
- avoid personal attacks, harassment, or disruptive behavior
- report security-sensitive issues responsibly

## 3. Unacceptable Conduct

Unacceptable conduct includes:

- harassment, threats, or abusive language
- personal attacks
- repeated off-topic disruption
- intentional misrepresentation of project results or validation evidence
- unsupported technical, implementation, hardware, or performance claims
- publication of private, sensitive, or restricted material
- disclosure of credentials, tokens, keys, secrets, or private access-control material
- attempts to pressure maintainers into accepting unverified claims

## 4. Evidence-Based Discussion

Technical discussion should remain evidence-based.

Claims about FRP behavior should be grounded in:

- repository code
- documented test output
- reproducible benchmark results
- explicit model and workload assumptions
- release-specific metric definitions
- current workflow and qualification evidence

Current project state:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current M15 benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Current published validation result:

`PASS`

Inherited M15 self-test result:

`41/41 PASS`

Current M16 RTL qualification:

| Field | Recorded value |
|---|---|
| Workflow | `FRP M16 RTL Artifact Boundary` |
| Workflow file | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#84` |
| Qualified source commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation qualification:

| Field | Recorded value |
|---|---|
| Workflow | `FRP M16 FPGA Preparation` |
| Workflow file | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#2` |
| Qualified repository commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

## 5. Repository Scope

Discussion and contributions should remain aligned with the public repository scope.

The repository may include:

- public documentation
- executable processor reference code
- structured output and reproducibility instructions
- benchmark interpretation and release-specific evidence
- verification and qualification records
- implementation-mapping artifacts
- hardware-facing interface and correlation documents
- SystemVerilog RTL execution artifacts
- target-independent FPGA preparation artifacts
- mathematical and physical foundation documents
- historical release records

The public repository excludes:

- private access-control material
- credentials, tokens, keys, or secrets
- deployment-sensitive operational details
- unpublished restricted design layers
- private identity or authentication data
- unsafe implementation instructions

## 6. Maintainer Responsibility

Maintainers may:

- edit or close off-topic issues
- reject unsupported claims
- close disruptive discussions
- remove sensitive material
- request additional evidence before accepting changes
- block participants who repeatedly violate this code of conduct

Maintainer decisions should protect project clarity, safety, reproducibility, evidence integrity, and public repository boundaries.

## 7. Reporting

Concerns about conduct or security-sensitive issues should be reported responsibly to the repository maintainer.

Sensitive issues should be reported privately first, with reasonable review time provided before public disclosure.

## 8. Current Status

This code of conduct is aligned with:

- `FRP v1.8.0`
- `M16 — RTL Core Realization and Execution Semantics Package`
- the M15-qualified semantic and implementation-mapping foundation
- `frp_prototype_v1_7_0.py`
- `frp.structured_output.v1.7.0`
- `frp.m3.benchmark_matrix.v1.7.0`
- `README.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `docs/limitations.md`
- `docs/mathematical_foundation.md`
- `docs/physical_foundation.md`
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`
- `docs/m16_rtl_core_realization_execution_semantics.md`
- `TEST_REPORT_v1_8_0.md`
- `FRP_VALIDATION_INDEX_v1_8_0.md`
- `RELEASE_NOTES_v1_8_0.md`
- `rtl/m16/CLOSURE.md`
- `fpga/m16/CLOSURE.md`
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`
- `.github/workflows/frp-m16-fpga-preparation.yml`
