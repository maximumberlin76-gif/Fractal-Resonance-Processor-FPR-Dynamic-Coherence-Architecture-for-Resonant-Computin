# FRP v3.3.0 Test Report

## Result

`PASS`

## Qualification identity

| Field | Value |
|---|---|
| Project | Fractal Resonance Processor (FRP) |
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Focused test module | `tests.test_frp_m31_phase_interference_thermal_evidence` |
| Focused result | `60 / 60 PASS` |
| Qualification checks | `13 / 13 PASS` |
| Canonical M31 outputs | `4 / 4 exact` |
| Prior archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Validation record | `FRP_VALIDATION_INDEX_v3_3_0.md` |
| Release notes | `RELEASE_NOTES_v3_3_0.md` |

This report records the focused M31 qualification boundary. It does not
replace or rewrite test reports from prior releases.

## Execution command

`python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v`

Recorded result:

`Ran 60 tests — OK`

The M31D1, M31D2, and M31D3 publication workflows execute this command from a
clean checkout of `main` after verifying the exact committed M31 source,
test, schema, evidence, manifest, qualification, and M30 archive identities.

## Tested files

| Path | Bytes | SHA-256 |
|---|---:|---|
| `frp_m31_phase_interference_thermal_evidence.py` | `42092` | `1e4ccfd7b157cd2bac609c34dfec9da791653a31af7b29b75502c755807b9c62` |
| `tests/test_frp_m31_phase_interference_thermal_evidence.py` | `22370` | `f64214a9c785d8cf579e3a6a5afa6e364772d8972775cc010a3dba89d852c1ed` |
| `schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json` | `1468` | `53d79d45d70753ccd24c3dc4c97af6fee481f86a9d7cdca7ef78b486c76479f7` |
| `artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json` | `39993` | `bdaa676acbfb09d86d848070e8a2673c5ce6902657a0b13b2e4293383bec8b42` |
| `artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json` | `828` | `80f0841d0041cd22c2f76175b6139e601aede7b69823356ae1fefbce5f793e7c` |
| `artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json` | `1512` | `4c2446f954e01ec0aa37cc6c0fc70cf4a87ec565c450628e31b0efcac9160224` |

Schema identity:

`frp.m31.phase_interference_active_zero_thermal_evidence.v1`

## Test distribution

| Test range | Qualification surface | Tests | Result |
|---|---|---:|---|
| `01–10` | source identity, constants, canonical JSON, schema, evidence identity, ternary domain | `10` | `PASS` |
| `11–25` | active zero, neutral-mediated routing, scheduler separation, computation order, trace counts and invariants | `15` | `PASS` |
| `26–33` | historical experiment boundary, exact rows, thermal-load ratios, scoped interpretation | `8` | `PASS` |
| `34–41` | current comparative contours, architecture ordering, hardware sensitivity, thermal-proxy identity | `8` | `PASS` |
| `42–49` | evidence boundaries, read-only Observatory contract, provenance, deterministic generation and replay | `8` | `PASS` |
| `50–60` | invalid-input, forbidden-transition, claim-tamper, writeback, path, JSON, and trace negative paths | `11` | `PASS` |
| Total | focused M31 qualification | `60` | `PASS` |

## Processor-semantic assertions

| Assertion | Expected | Result |
|---|---|---|
| balanced ternary notation | `-1/0/1` | `PASS` |
| semantic domain | `-1`, `0`, `1` | `PASS` |
| neutral state `0` is active | `true` | `PASS` |
| direct `-1 → 1` transition | forbidden | `PASS` |
| direct `1 → -1` transition | forbidden | `PASS` |
| negative-to-positive route | `-1 → 0 → 1` | `PASS` |
| positive-to-negative route | `1 → 0 → -1` | `PASS` |
| temporal scheduler modes | `1/7`, `7/1` | `PASS` |
| service scheduler mode | `free` | `PASS` |
| target and retained state | distinct | `PASS` |
| classical bit addition as primary mechanism | `false` | `PASS` |

## Active-zero execution assertions

| Record | Expected | Result |
|---|---:|---|
| execution records | `100` | `PASS` |
| cell observations | `800` | `PASS` |
| active-zero observations | `702` | `PASS` |
| requested direct events | `5` | `PASS` |
| prevented direct events | `5` | `PASS` |
| neutral-routed events | `5` | `PASS` |
| actual direct events | `0` | `PASS` |
| reserved-state events | `0` | `PASS` |
| queue-overflow events | `0` | `PASS` |
| polarity-to-active-zero transitions | `5` | `PASS` |
| active-zero-to-polarity transitions | `12` | `PASS` |
| direct opposite-polarity transitions | `0` | `PASS` |
| retained-same observations | `783` | `PASS` |

The trace-count tests bind these totals to the committed evidence. The
invariant tests require every full-core record to pass and require all direct
opposite-polarity requests to be prevented and neutral-routed.

## Historical thermal-contour assertions

| Historical model value | Expected | Result |
|---|---:|---|
| binary-style forced-switch `heat_peak` | `0.051000` | `PASS` |
| distributed active-neutral ternary `heat_peak` | `0.003250` | `PASS` |
| ratio | `15.6923076923` | `PASS` |
| relative reduction | `93.63%` | `PASS` |
| physical temperature measurement | `false` | `PASS` |
| universal winner assertion | absent | `PASS` |

The historical tests reproduce the exact FRP v0.9.3 command boundary, verify
the ordered rows and derived values, and reject changes to the recorded ratio.

## Current comparative-contour assertions

| Assertion | Result |
|---|---|
| current baseline identity exact | `PASS` |
| architecture order exact | `PASS` |
| baseline status without winner assertion | `PASS` |
| hardware-sensitivity scenario order exact | `PASS` |
| ranking stability preserved across recorded scenarios | `PASS` |
| hardware-sensitivity status without winner assertion | `PASS` |
| thermal-proxy profile identity exact | `PASS` |
| historical and current contours remain separate | `PASS` |

The current RC temperature proxy is not the historical `heat_peak` and is not
a physical temperature measurement. Normalized activity cost is not physical
energy. Operation count is not thermal load.

## Canonical-output and replay assertions

| Assertion | Expected | Result |
|---|---|---|
| generated output inventory | exactly four paths | `PASS` |
| generated byte counts | exact | `PASS` |
| generated SHA-256 digests | exact | `PASS` |
| independent verification | accepts exact outputs | `PASS` |
| self-test evidence digest | exact | `PASS` |
| repeated generation | byte-identical | `PASS` |
| canonical JSON key order | sorted | `PASS` |
| canonical JSON termination | one final newline | `PASS` |
| non-finite JSON values | rejected | `PASS` |

## Negative-path assertions

The focused suite verifies rejection of:

- invalid ternary notation;
- values outside the `-1/0/1` domain;
- direct opposite-polarity transitions;
- physical-temperature claims on model contours;
- tampered historical ratios;
- downstream Observatory writeback permission;
- non-object JSON input;
- missing required paths;
- directory targets for canonical JSON output;
- tampered traces containing a direct opposite transition;
- current-contour winner assertions.

All 11 negative-path tests pass.

## FRP Trace Observatory boundary assertions

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

| Downstream operation | Expected | Result |
|---|---|---|
| metric normalization | forbidden | `PASS` |
| semantic reimplementation | forbidden | `PASS` |
| FRP source mutation | forbidden | `PASS` |
| writeback | forbidden | `PASS` |
| producer-source execution by Observatory | absent | `PASS` |

## M30 archival-continuity assertion

| Field | Value |
|---|---|
| Archive | `artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz` |
| Bytes | `10189989` |
| SHA-256 | `05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa` |
| Archive root | `Fractal-Resonance-Processor-FRP-v3.2.0` |
| Member verification | byte-identical |
| Result | `PASS` |

M31 verifies the preserved M30 archive and does not rebuild or replace it.

## Documentation-publication assertions

| Record | Expected SHA-256 | Result |
|---|---|---|
| `FRP_VALIDATION_INDEX_v3_3_0.md` | `d9cc92a9a51797d536875710933109a42f24120739c8e2960d82205dbb785d3b` | `PASS` |
| `RELEASE_NOTES_v3_3_0.md` | `16bb207b2b254ba980272b23e448ad737cd7e2de5da3bdfc005ea9ca2010b648` | `PASS` |

Each documentation publication is additive and idempotent. The first manual
run creates exactly its declared target. A repeated run verifies the exact
target and produces no additional commit.

## Protected-history assertions

| Protected record set | Files before M31 documentation | Result |
|---|---:|---|
| `artifacts/` | `127` | byte-identical |
| `benchmarks/` | `19` | byte-identical |
| `schemas/` | `125` | byte-identical |
| historical root release records before D1 | `48` | byte-identical |

The D1 and D2 workflows snapshot protected records before publication,
compare them after publication, and require byte identity for every existing
file. No evidence, benchmark, schema, source, test, workflow, release note,
test report, validation index, release checklist, or archive is deleted,
renamed, regenerated, shortened, or rewritten.

## Final qualification

| Gate | Result |
|---|---|
| focused M31 suite | `60 / 60 PASS` |
| qualification record | `13 / 13 PASS` |
| canonical outputs | `4 / 4 exact` |
| active-zero invariants | `PASS` |
| thermal-contour separation | `PASS` |
| deterministic replay | `PASS` |
| M30 archival continuity | `PASS` |
| Observatory read-only boundary | `PASS` |
| prior-history preservation | `PASS` |

`FRP v3.3.0 / M31 TEST REPORT — PASS`
