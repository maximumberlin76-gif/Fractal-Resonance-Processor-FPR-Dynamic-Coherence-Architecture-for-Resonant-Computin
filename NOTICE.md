# Notice

## Project identity

**Fractal Resonance Processor (FRP)**  
**Ternary Fractal Resonant Coherence Processor**

Copyright 2026 Maksym Marnov

Licensed under the Apache License, Version 2.0. The complete license text is
provided in `LICENSE`.

## Current publication record

| Field | Value |
|---|---|
| Current version | `FRP v3.3.0` |
| Current milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification status | `PASS` |
| Focused M31 qualification | `60 / 60 PASS` |
| M31 qualification checks | `13 / 13 PASS` |
| Canonical M31 outputs | `4 / 4 exact` |
| Prior archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Current validation index | `FRP_VALIDATION_INDEX_v3_3_0.md` |
| Current test report | `TEST_REPORT_v3_3_0.md` |
| Current release notes | `RELEASE_NOTES_v3_3_0.md` |

The executable semantic reference remains
`frp_prototype_v1_7_0.py`. The qualified RTL and target-independent FPGA
implementation anchor remains M16.

## Processor identity

FRP organizes computation through retained relative-phase interference,
resonant selection, phase-derived ternary targets, scheduler-controlled
request handling, active-zero mediation, and retained-state writeback.

| Contract | Preserved value |
|---|---|
| Balanced ternary notation | `-1/0/1` |
| Semantic states | `-1`, `0`, `1` |
| Active neutral state | `0` |
| Negative-to-positive route | `-1 → 0 → 1` |
| Positive-to-negative route | `1 → 0 → -1` |
| Temporal scheduler modes | `1/7`, `7/1` |
| Separate service scheduler mode | `free` |

State `0` is an active computational state used for mediation, routing,
retention, balancing, transition staging, and controlled neutralization.

## Qualified milestone continuity

| Milestone boundary | Qualification record |
|---|---|
| M15 semantic and implementation mapping | `41 / 41 PASS`; deterministic vector and replay records preserved |
| M16 RTL execution and FPGA preparation | qualified implementation anchor; invariant records preserved |
| M17–M29 progression | all 13 milestone gates recorded as `PASS` by the M30 closure |
| M30 reproducibility and archival release | `55 / 55 PASS`; archival package verified |
| M31 evidence publication | `60 / 60 PASS`; 13 qualification checks; four exact canonical outputs |

The M30 archival package remains:

`artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz`

SHA-256:

`05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa`

## M31 canonical publication

The current M31 publication consists of:

- `frp_m31_phase_interference_thermal_evidence.py`;
- `tests/test_frp_m31_phase_interference_thermal_evidence.py`;
- `schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`;
- `artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`;
- `artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`;
- `artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`.

The schema, evidence, manifest, and qualification record are deterministic
canonical outputs. M31 retains the M30 archive, historical benchmark records,
current comparison contours, schemas, workflows, release records, and prior
qualification evidence.

## Repository scope

The repository contains the public executable processor reference,
machine-readable schemas, canonical artifacts, deterministic traces,
benchmarks, comparison profiles, hardware-facing mappings, RTL and FPGA
integration layers, verification records, qualification manifests,
documentation, governance records, and release evidence.

Historical release notes, test reports, validation indexes, release
checklists, benchmark results, schemas, and milestone evidence remain bound to
their original versions, measurements, digests, and qualification results.

## FRP Trace Observatory boundary

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

FRP is the source and semantic authority. The Observatory consumes immutable
published artifacts through a one-way read-only boundary for validation and
visualization. Published schemas, evidence, manifests, qualification records,
and measurement contours retain their FRP identities.

## Redistribution and attribution

Redistribution and derivative works are governed by the Apache License,
Version 2.0. Distributed copies must retain the applicable copyright,
license, and attribution notices required by that license. Modified files
must carry prominent notices identifying the changes.

Third-party software, tools, and dependencies retain their respective
copyright and license terms. The Apache License for FRP does not replace those
independent terms.

## License

See `LICENSE` for the complete Apache License 2.0 terms.
