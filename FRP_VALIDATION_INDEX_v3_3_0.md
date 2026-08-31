# FRP v3.3.0 Validation Index

## Release boundary

| Field | Value |
|---|---|
| Project | Fractal Resonance Processor (FRP) |
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification status | `PASS` |
| Focused qualification | `60 / 60 PASS` |
| Prior archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| RTL and FPGA implementation anchor | `M16 — PASS` |

M31 adds a deterministic, read-only publication layer over already committed
FRP evidence. It does not replace the M30 archival baseline, rename the M15
semantic reference, redefine M16 execution semantics, or alter historical
benchmark and release records.

## Preservation guarantee

This validation index is additive. Its publication creates exactly one new
file:

`FRP_VALIDATION_INDEX_v3_3_0.md`

No existing evidence, benchmark, schema, workflow, release note, test report,
validation index, release checklist, source file, or test file is deleted,
renamed, regenerated, or rewritten by the publication workflow.

The protected pre-publication inventories are:

| Protected record set | Files | Sorted digest-inventory SHA-256 |
|---|---:|---|
| `artifacts/` | `127` | `0d86a8c50c86ba0196f635903cb8cc8d635dd1399787625f7619ad4dd8121f2b` |
| `benchmarks/` | `19` | `54dc4ae9aa858ccd60f577367be909abf1266b76fcefe10c8223e1f22cc78670` |
| `schemas/` | `125` | `384cede6b31eea78b9e85804405d7d8bb3bec42e0ce8489d3f9ed20d36f213d9` |
| historical root release records | `48` | `7903e5b9e7b404770a434fa22c9bd6ae76fb062136f6e0b7fa2233dc0b3127f5` |

Each aggregate is the SHA-256 of a lexicographically sorted list containing
the SHA-256 and repository-relative path of every protected regular file. The
publication workflow computes the inventories before and after creating this
index and requires byte identity for every pre-existing protected file.

## Immutable processor identity

| Contract | Preserved value |
|---|---|
| Balanced ternary notation | `-1/0/1` |
| Semantic values | `-1`, `0`, `1` |
| Active neutral state | `0` |
| Opposite-polarity routes | `-1 → 0 → 1`, `1 → 0 → -1` |
| Temporal scheduler modes | `1/7`, `7/1` |
| Separate service scheduler mode | `free` |
| Primary organization | retained relative-phase interference and resonant selection |
| Classical bit addition as primary mechanism | `false` |

The balanced ternary layer remains the discrete state, target, transition, and
retained-result boundary. Active neutral state `0` remains an executable
computational state.

## Canonical M31 source and outputs

| Path | Bytes | SHA-256 |
|---|---:|---|
| `frp_m31_phase_interference_thermal_evidence.py` | `42092` | `1e4ccfd7b157cd2bac609c34dfec9da791653a31af7b29b75502c755807b9c62` |
| `tests/test_frp_m31_phase_interference_thermal_evidence.py` | `22370` | `f64214a9c785d8cf579e3a6a5afa6e364772d8972775cc010a3dba89d852c1ed` |
| `schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json` | `1468` | `53d79d45d70753ccd24c3dc4c97af6fee481f86a9d7cdca7ef78b486c76479f7` |
| `artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json` | `39993` | `bdaa676acbfb09d86d848070e8a2673c5ce6902657a0b13b2e4293383bec8b42` |
| `artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json` | `828` | `80f0841d0041cd22c2f76175b6139e601aede7b69823356ae1fefbce5f793e7c` |
| `artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json` | `1512` | `4c2446f954e01ec0aa37cc6c0fc70cf4a87ec565c450628e31b0efcac9160224` |

Evidence schema identity:

`frp.m31.phase_interference_active_zero_thermal_evidence.v1`

The M31 manifest binds two generated records, and the qualification record
binds all three generated evidence records. Together with the formal schema,
the complete publication contains four canonical outputs.

## M31 workflow history

The complete functional workflow history remains committed:

| Workflow | Bytes | SHA-256 |
|---|---:|---|
| `.github/workflows/frp-m31a1-phase-interference-thermal-evidence-source-part-1-workflow.yml` | `14081` | `e24f8de99c1a93c454f3180e133a20c6d495f11c221bd7c3c59930ada844ba27` |
| `.github/workflows/frp-m31a2-phase-interference-thermal-evidence-source-part-2-workflow.yml` | `16053` | `7dd5e6702e02427354db80ab1cc11dc98e67d40e69c3745174ec7cba2a962e6d` |
| `.github/workflows/frp-m31a3-phase-interference-thermal-evidence-source-assembly-workflow.yml` | `15191` | `4f9c95b6411a5c7ae47a46df2c980feca91039d71f46ee3e014355cfd58a7649` |
| `.github/workflows/frp-m31b1-phase-interference-thermal-evidence-test-part-1-workflow.yml` | `13304` | `387270d58a29889bfcca1c41c6f460d958858092ae60748de0e9005dc65a1dfd` |
| `.github/workflows/frp-m31b2-phase-interference-thermal-evidence-test-part-2-workflow.yml` | `19735` | `b8ad399a8aef858aa18028e7519a7d336f10f5984ca84808852c9e21ec4af85a` |
| `.github/workflows/frp-m31b3-phase-interference-thermal-evidence-test-assembly-workflow.yml` | `12763` | `04c21e9d003ab27f1285e0cbe65cc7f10ff91509c945ad215273e5aff7afc597` |
| `.github/workflows/frp-m31c-phase-interference-thermal-evidence-publication-workflow.yml` | `25808` | `16bd797c84a966852a1e9859ac2610b9082b998bae82f9dbe94975d9e6baf250` |
| `.github/workflows/frp-m31-complete.yml` | `11762` | `eed979a2b7e795b73facd628d49bf76993ed1fc7e37a8e0dd613d92fae4e751b` |

The final `FRP M31 Complete` workflow validates exact source bytes, runs all
60 focused tests, reproduces the M31 evidence twice, requires byte identity,
verifies all committed digests, and publishes only the four canonical M31
outputs.

## M31 qualification checks

All checks recorded in the committed qualification document are `true`:

| Check | Result |
|---|---|
| `active_zero_trace_evidence_exact` | `PASS` |
| `current_comparative_contours_integrity_pass` | `PASS` |
| `direct_opposite_transitions_zero` | `PASS` |
| `historical_experiment_reproduced` | `PASS` |
| `historical_rows_exact` | `PASS` |
| `m30_archive_members_byte_identical` | `PASS` |
| `observatory_boundary_read_only` | `PASS` |
| `physical_temperature_claim_absent` | `PASS` |
| `scheduler_modes_exact` | `PASS` |
| `source_digests_exact` | `PASS` |
| `ternary_notation_exact` | `PASS` |
| `thermal_measurement_contours_separate` | `PASS` |
| `winner_assertions_absent` | `PASS` |

Focused test command:

`python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v`

Recorded result:

`Ran 60 tests — OK`

## Published active-zero execution evidence

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

The evidence contains two cycle-exact execution contours, 100 execution
records, 800 cell observations, and no direct opposite-polarity transition.

## Thermal and benchmark evidence continuity

M31 preserves the historical and current benchmark contours as separate
measurement classes.

### Historical reproduced contour

The FRP v0.9.3 benchmark is preserved by:

- `frp_prototype_v0_9_3_mobile.py`;
- `TEST_REPORT_v0_9_3.md`;
- the exact command recorded in the M31 evidence;
- the recorded stdout SHA-256
  `b18e1affec6dec8029086e923b907c9ae3cb0c50131e4291b31fbd2a4d97cbb6`.

Under that exact historical model workload, the focused record contains:

| Historical model value | Recorded value |
|---|---:|
| binary-style forced-switch `heat_peak` | `0.051000` |
| distributed active-neutral ternary `heat_peak` | `0.003250` |
| ratio | `15.6923076923` |
| relative reduction | `93.63%` |
| physical temperature measurement | `false` |

These are release-specific model thermal-load values. They are not physical
temperature measurements and do not establish a universal architecture
winner.

### Current comparative contours

The current benchmark sources remain unchanged:

| Path | SHA-256 |
|---|---|
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json` | `5ba86d26dc62db36ae14ac2c1167e71dd5c06c00bbd5aa3dc21c6d11b38db064` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json` | `e4785aa4c234cc7dd8e5377e5e0b41a8ec401f962400975e0cef7a88cc494680` |
| `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json` | `aeafebc3e71d1311a3445bd1528cbe7322546f79d6a5099dfed3a9590fc4a25b` |

The current RC temperature proxy is not the historical `heat_peak`, is not a
physical temperature, and must not be normalized or merged with the historical
contour. Normalized activity cost is not physical energy. Operation count is
not thermal load.

## M31 provenance

The evidence binds 12 existing sources:

| Path | SHA-256 |
|---|---|
| `TEST_REPORT_v0_9_3.md` | `c6fe86f2c0c922243a8bd001742e9fcbfd3c31cdedf40a6a728b989dbd01679e` |
| `artifacts/m19/execution/m16-fpga-preparation-execution-trace.json` | `7d58b6741bdcadbfb9acb9049ed0e956305f49b9ad36946e719a4121b5caf22f` |
| `artifacts/m19/execution/m16-rtl-execution-trace.json` | `d7945e0d2b5aaa05c5fff2e4e60d3b984017f7e4ae1984c55920368a110020bd` |
| `artifacts/m29/contracts/m29-system-integration-contract.json` | `6e14d93abe5646b4e094f27b07217d9e4dcd833d8af0d5afb30da21b904c4642` |
| `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json` | `aeafebc3e71d1311a3445bd1528cbe7322546f79d6a5099dfed3a9590fc4a25b` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json` | `5ba86d26dc62db36ae14ac2c1167e71dd5c06c00bbd5aa3dc21c6d11b38db064` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json` | `e4785aa4c234cc7dd8e5377e5e0b41a8ec401f962400975e0cef7a88cc494680` |
| `docs/physical_foundation.md` | `e9bacd13ebe7a7058e698a80dc4f677476e3ed2eab4b9d41f58fd9cdbcf68a7e` |
| `docs/resonance_computation.md` | `1149cbd0aeb90d0a6133db5ecc1e5b4d45268815b70a75cb7a347a5e44a9b615` |
| `frp_prototype_v0_9_3_mobile.py` | `48361714bb815f362a30a5a884a0fb782cb97349e9a18f9b607af7bf54c02e52` |
| `artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz` | `05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa` |
| `.github/workflows/frp-m30-observatory-full-core-trace-qualification-workflow.yml` | `01ca22bc98f63d9d4ea4a58299d53ff58b410f3f2db94b81097d7cef3ad4dee7` |

## M30 archival continuity

The M31 producer verifies the preserved M30 archive:

| Field | Value |
|---|---|
| Path | `artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz` |
| Bytes | `10189989` |
| SHA-256 | `05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa` |
| Archive root | `Fractal-Resonance-Processor-FRP-v3.2.0` |
| Member verification | byte-identical |

M31 is an additive publication over this immutable archive. The archive is not
rebuilt or replaced.

## FRP Trace Observatory boundary

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

The downstream role is read-only validation and visualization. The contract
forbids:

- downstream metric normalization;
- downstream semantic reimplementation;
- downstream FRP source mutation;
- downstream writeback.

Published contours must remain separate. Observatory processing cannot modify
FRP source, schemas, evidence, manifests, benchmarks, workflows, or historical
release records.

## Historical release continuity

All pre-existing release-specific records remain present:

- `RELEASE_NOTES_v0_9_3.md` through `RELEASE_NOTES_v1_8_0.md`;
- `RELEASE_NOTES_v3_2_0.md`;
- `TEST_REPORT_v0_9_3.md` through `TEST_REPORT_v1_8_0.md`;
- `TEST_REPORT_v3_2_0.md`;
- `FRP_VALIDATION_INDEX_v0_9_9.md` through
  `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v3_2_0.md`;
- all existing release checklists;
- `FRP_PRODUCTION_RELEASE_MANIFEST_v1_0_0.md`;
- the complete committed `artifacts/`, `benchmarks/`, and `schemas/`
  histories.

This v3.3.0 index supplements those records. It does not supersede their
release-specific measurements, checksums, scope, or conclusions.

## Result

`FRP v3.3.0 / M31 VALIDATION INDEX — PASS`
