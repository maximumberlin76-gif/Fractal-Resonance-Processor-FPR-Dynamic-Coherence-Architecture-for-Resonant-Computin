# FRP v3.3.0 Release Notes

## Release identity

| Field | Value |
|---|---|
| Project | Fractal Resonance Processor (FRP) |
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification status | `PASS` |
| Focused qualification | `60 / 60 PASS` |
| Prior archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Validation record | `FRP_VALIDATION_INDEX_v3_3_0.md` |

FRP v3.3.0 publishes the M31 evidence boundary over the preserved M30
archival release. M31 records phase-interference execution, active-neutral
state participation, neutral-mediated opposite-polarity routing, separated
thermal evidence contours, deterministic provenance, and the one-way
read-only FRP Trace Observatory contract.

## Processor semantics preserved by M31

| Contract | Value |
|---|---|
| Balanced ternary notation | `-1/0/1` |
| Semantic values | `-1`, `0`, `1` |
| Active neutral state | `0` |
| Negative-to-positive route | `-1 → 0 → 1` |
| Positive-to-negative route | `1 → 0 → -1` |
| Temporal scheduler modes | `1/7`, `7/1` |
| Separate service scheduler mode | `free` |
| Primary organization | retained relative-phase interference and resonant selection |
| Classical bit addition as primary mechanism | `false` |

The balanced ternary layer remains the discrete state, target, transition,
and retained-result boundary. Neutral state `0` is an active computational
state used for mediation, routing, retention, balancing, and controlled
neutralization.

## Canonical M31 publication

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

The producer emits the schema, evidence record, manifest, and qualification
record as four deterministic canonical outputs. The committed manifest binds
the generated publication records, and the qualification record binds the
complete M31 output set.

## Active-zero execution evidence

| Record | Value |
|---|---:|
| execution records | `100` |
| cell observations | `800` |
| active-zero observations | `702` |
| requested direct events | `5` |
| prevented direct events | `5` |
| neutral-routed events | `5` |
| actual direct events | `0` |
| reserved-state events | `0` |
| queue-overflow events | `0` |
| polarity-to-active-zero transitions | `5` |
| active-zero-to-polarity transitions | `12` |
| direct opposite-polarity transitions | `0` |
| retained-same observations | `783` |

The published trace contains two cycle-exact execution contours. Every
opposite-polarity request is routed through active neutral state `0`; the
published evidence contains no direct opposite-polarity transition.

## Phase-interference computation boundary

M31 preserves the computation chain:

`phase dynamics → relative-phase organization → ternary target → scheduler → request handling → neutral-mediated routing → retained state`

The phase layer supplies the target organization. The balanced ternary layer
supplies the discrete transition and retained-state semantics. Target state
and executed retained state remain distinct. Scheduler modes, pending-route
state, capacity checks, active-neutral mediation, and retained writeback
remain explicit execution stages.

## Thermal-evidence boundary

M31 keeps historical and current contours separate.

### Historical reproduced contour

The preserved FRP v0.9.3 model workload records:

| Historical model value | Recorded value |
|---|---:|
| binary-style forced-switch `heat_peak` | `0.051000` |
| distributed active-neutral ternary `heat_peak` | `0.003250` |
| ratio | `15.6923076923` |
| relative reduction | `93.63%` |
| physical temperature measurement | `false` |

These values belong to the exact historical model and workload recorded in
the evidence. They are not physical temperature measurements and do not
establish a universal architecture winner.

### Current comparative contours

The current architecture-comparison records and RC temperature-proxy profile
remain separate from the historical `heat_peak` contour. Normalized activity
cost is not physical energy. Operation count is not thermal load. The M31
publication does not merge, normalize, or reinterpret these measurement
classes.

## Qualification

Focused command:

`python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v`

Recorded result:

`Ran 60 tests — OK`

The committed qualification record contains 13 checks, all `true`:

- active-zero trace evidence exact;
- current comparative-contour integrity;
- zero direct opposite transitions;
- historical experiment reproduced;
- historical rows exact;
- M30 archive members byte-identical;
- Observatory boundary read-only;
- physical-temperature claim absent;
- scheduler modes exact;
- source digests exact;
- ternary notation exact;
- thermal measurement contours separate;
- winner assertions absent.

## M30 archival continuity

| Field | Value |
|---|---|
| Archive | `artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz` |
| Bytes | `10189989` |
| SHA-256 | `05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa` |
| Archive root | `Fractal-Resonance-Processor-FRP-v3.2.0` |
| Member verification | byte-identical |

The M30 archive remains the preserved archival baseline. M31 is an additive
publication and does not rebuild or replace that archive.

## FRP Trace Observatory contract

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

The downstream repository receives immutable published records for validation
and visualization. The contract forbids:

- downstream metric normalization;
- downstream semantic reimplementation;
- downstream FRP source mutation;
- downstream writeback.

The Observatory does not execute FRP producer source and does not modify FRP
source, schemas, evidence, manifests, qualification records, benchmarks,
workflows, or release history.

## Preservation record

The additive M31 validation workflow recorded the following protected
pre-publication inventories:

| Protected record set | Files | Sorted digest-inventory SHA-256 |
|---|---:|---|
| `artifacts/` | `127` | `0d86a8c50c86ba0196f635903cb8cc8d635dd1399787625f7619ad4dd8121f2b` |
| `benchmarks/` | `19` | `54dc4ae9aa858ccd60f577367be909abf1266b76fcefe10c8223e1f22cc78670` |
| `schemas/` | `125` | `384cede6b31eea78b9e85804405d7d8bb3bec42e0ce8489d3f9ed20d36f213d9` |
| historical root release records | `48` | `7903e5b9e7b404770a434fa22c9bd6ae76fb062136f6e0b7fa2233dc0b3127f5` |

The validation-index publication verified these inventories before and after
creating `FRP_VALIDATION_INDEX_v3_3_0.md`. Every pre-existing protected file
remained byte-identical.

## Historical release continuity

FRP v3.3.0 retains all earlier release-specific notes, test reports,
validation indexes, release checklists, milestone artifacts, schemas,
benchmarks, workflows, and archival packages. Historical measurements,
digests, scope statements, and qualification conclusions remain bound to their
original releases.

No historical release record is deleted, renamed, shortened, regenerated, or
rewritten by the M31 release-notes publication.

## Release result

`FRP v3.3.0 / M31 RELEASE NOTES — QUALIFIED`
