# FRP M18 Formal Schema and Canonical Artifact Publication Qualification

## Status

`PASS`

Qualified boundary:

`M18 FORMAL SCHEMA AND CANONICAL ARTIFACT PUBLICATION`

Recorded milestone state:

`QUALIFIED`

## Baseline

| Field | Recorded value |
|---|---|
| Current published FRP release | `FRP v1.8.0 / M16` |
| M18 version target | `v2.0.0` |
| M18 milestone | `M18 — Formal Schema and Canonical Artifact Publication` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| Canonical artifact producer | `frp_m18_canonical_artifacts.py` |
| Source authority | `FRP` |

The `v2.0.0` value is the M18 version target. This qualification record does
not create a tag, create a release, or replace the current published release.

## Purpose

This document records the successful qualification of the M18 formal schema
registry, canonical artifact publication, deterministic producer, tests, and
permanent qualification workflow for one exact implementation commit.

The qualified publication direction remains:

`FRP → published artifacts → downstream consumers`

FRP remains the sole authority for processor semantics. M18 formalizes and
publishes existing FRP outputs without redefining processor behavior, changing
published values, combining measurement contours, or introducing physical-chip
claims.

## Qualified Implementation Boundary

| Path | Role |
|---|---|
| `docs/m18_formal_schema_canonical_artifact_publication_contract.md` | M18 technical contract |
| `schemas/m18/` | 24 formal JSON Schema documents and the formal schema registry |
| `frp_m18_canonical_artifacts.py` | deterministic canonical artifact producer |
| `artifacts/m18/` | committed canonical publication set |
| `tests/test_frp_m18_canonical_artifacts.py` | M18 contract, schema, registry, producer, artifact, and safety tests |
| `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml` | permanent read-only M18 qualification workflow |

## Workflow Execution Record

| Field | Recorded value |
|---|---|
| Workflow | `FRP M18 Formal Schema and Canonical Artifacts` |
| Workflow file | `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml` |
| Job | `M18 Formal Schema and Canonical Artifact Qualification` |
| Workflow run number | `1` |
| Workflow run identifier | `31817350461` |
| Workflow run attempt | `1` |
| Qualified commit | `5264c7dbfc0c23a96816635faadb3af74d57ae10` |
| Branch | `main` |
| Event | `push` |
| Conclusion | `success` |
| Workflow duration | `8m 59s` |
| Job duration | `8m 55s` |
| Python | `3.12` |
| `jsonschema` | `4.25.1` |
| Validator | `Draft202012Validator` |
| Repository permission | `contents: read` |
| Evidence artifact | `frp-m18-formal-schema-canonical-artifacts` |
| Evidence retention | `30 days` |

Workflow run URL:

`https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/runs/31817350461`

## Workflow Step Results

Every mandatory job step completed with conclusion `success`:

| Step | Result |
|---|---|
| checkout repository | `PASS` |
| set up Python 3.12 | `PASS` |
| install exact M18 dependencies | `PASS` |
| prepare isolated M18 directories | `PASS` |
| compile M18 Python sources | `PASS` |
| generate independent self-test pair | `PASS` |
| validate self-test pair | `PASS` |
| generate independent canonical artifact pair | `PASS` |
| compare generated and committed artifact trees | `PASS` |
| validate formal schema registry offline | `PASS` |
| verify committed M18 publication | `PASS` |
| generate independent qualification pair | `PASS` |
| validate qualification pair | `PASS` |
| run isolated M18 test suite | `PASS` |
| run complete repository test suite | `PASS` |
| verify repository immutability | `PASS` |
| upload M18 qualification evidence | `PASS` |

## Formal Schema Registry Qualification

| Qualification item | Result |
|---|---|
| registry schema | `frp.m18.formal_schema_registry.v2.0.0` |
| registry kind | `formal_schema_registry` |
| registry version | `2.0.0` |
| registered formal schema documents | `24 / 24 PASS` |
| schema dialect | `JSON Schema Draft 2020-12` |
| validator implementation | `Draft202012Validator` |
| schema resolution | `offline repository-local PASS` |
| unique registry identifiers | `24 / 24 PASS` |
| unique schema `$id` values | `24 / 24 PASS` |
| registry-to-document correspondence | `24 / 24 PASS` |
| document-to-registry correspondence | `24 / 24 PASS` |
| duplicate registry paths | `0` |
| duplicate schema identifiers | `0` |
| unresolved or external `$ref` values | `0` |
| registry raw-file SHA-256 | `35dbce174597da749d95cc8cdbc41f1b67a3d042296ae84e61915ee09c5fdea6` |
| registry content SHA-256 | `6d2d0077b00c9f3da04429a8a690256fe7b4de585c7257804471a3d3d4992c0c` |

The registry records the corrected structured-output publication paths:

- `artifacts/m18/structured_output/trace-free.json`;
- `artifacts/m18/structured_output/trace-7-1.json`;
- `artifacts/m18/structured_output/trace-1-7.json`;
- `artifacts/m18/structured_output/self-test-default.json`.

## Canonical Artifact Publication Qualification

| Publication member class | Count | Result |
|---|---:|---|
| structured-output JSON artifacts | `11` | `PASS` |
| benchmark-matrix JSON artifacts | `1` | `PASS` |
| benchmark-matrix CSV artifacts | `1` | `PASS` |
| M15 JSON exports | `10` | `PASS` |
| M15 deterministic vector-package members | `10` | `PASS` |
| canonical artifact manifest | `1` | `PASS` |
| canonical artifact qualification record | `1` | `PASS` |
| canonical artifact self-test record | `1` | `PASS` |
| total committed M18 publication files | `36` | `36 / 36 PASS` |

The canonical artifact manifest contains exactly `64` source and generated
object records. It does not include itself, the canonical qualification record,
or the canonical self-test record.

| Canonical record | Schema | Raw-file SHA-256 | Result |
|---|---|---|---|
| `artifacts/m18/manifests/canonical-artifact-manifest.json` | `frp.m18.canonical_artifact_manifest.v2.0.0` | `bdf034303e9557a87ff53fce9193b9480360202e5ece8247d35f44678a871710` | `PASS` |
| `artifacts/m18/manifests/canonical-artifact-qualification.json` | `frp.m18.canonical_artifact_qualification.v2.0.0` | `432fef4d9a96e1181a6dc5b96dab64ac5726b1aeccb92702d02bce0721c87c13` | `PASS` |
| `artifacts/m18/manifests/canonical-artifact-self-test.json` | `frp.m18.canonical_artifact_self_test.v2.0.0` | `0c05d34d1a550086248e8b95b8ecbc00fd056081bf77ad9b88e65eaa9995950a` | `PASS` |

The M15 deterministic vector package retains the exact package digest:

`703dd4b56f4b34289a2c5bc5521ad4ddc3113bdec8c38238c3244c69cb4d58df`

## Producer Qualification

| Qualification item | Result |
|---|---|
| producer path | `frp_m18_canonical_artifacts.py` |
| producer source SHA-256 | `4562e0d6b5a0611ce7623d66b563aea7e90afb98e9f534a581a64d59e47c11b1` |
| `--generate` | `PASS` |
| `--verify` | `187 / 187 PASS` |
| `--qualify` | `187 / 187 PASS` |
| `--self-test` | `34 / 34 PASS` |
| CLI and configuration failure exit code | `2` |
| upstream producer failure exit code | `3` |
| filesystem or safety-boundary failure exit code | `4` |
| validation, qualification, or self-test failure exit code | `1` |
| success exit code | `0` |

The producer invokes the FRP semantic reference through `sys.executable` with
an argument list, `shell=False`, and captured standard output and standard
error. It performs no network access, arbitrary code execution, SystemVerilog
execution, or shell interpolation.

## Determinism Results

| Deterministic relation | Result |
|---|---|
| independent self-test render A versus B | `byte-identical PASS` |
| independent generated publication tree A versus B | `36 / 36 byte-identical PASS` |
| generated publication tree versus committed `artifacts/m18/` | `36 / 36 byte-identical PASS` |
| independent qualification record A versus B | `byte-identical PASS` |
| generated self-test record versus committed self-test record | `byte-identical PASS` |
| generated qualification record versus committed qualification record | `byte-identical PASS` |
| manifest ordering and path uniqueness | `PASS` |
| JSON, CSV, and vector serialization stability | `PASS` |
| environment-dependent deterministic fields | `0` |
| timestamps in deterministic published records | `0` |

## Self-Test Results

| Field | Recorded value |
|---|---|
| schema | `frp.m18.canonical_artifact_self_test.v2.0.0` |
| total cases | `34` |
| passed cases | `34` |
| failed cases | `0` |
| overall status | `PASS` |

The self-test is independent of repository state and validates canonical JSON
serialization, digest relations, manifest ordering, path safety, registry
identity, scheduler sequences, and canonical ternary-domain relations.

## Qualification Record Results

| Field | Recorded value |
|---|---|
| schema | `frp.m18.canonical_artifact_qualification.v2.0.0` |
| total checks | `187` |
| passed checks | `187` |
| failed checks | `0` |
| warnings | `0` |
| not evaluated | `0` |
| overall status | `PASS` |

The qualification record closes schema, digest, ordering, provenance,
canonical ternary-domain, scheduler, pending-route, transition-capacity,
retained-state writeback, and deterministic-regeneration relations.

## Semantic Invariance Results

| Invariant | Result |
|---|---|
| canonical retained-state domain `-1, 0, 1` | `PASS` |
| active neutral state `0` | `PASS` |
| route `-1 → 0 → 1` | `PASS` |
| route `1 → 0 → -1` | `PASS` |
| direct transition `-1 → 1` absent | `PASS` |
| direct transition `1 → -1` absent | `PASS` |
| scheduler mode `free` | `PASS` |
| scheduler sequence `7/1` | `PASS` |
| scheduler sequence `1/7` | `PASS` |
| `actual_direct_events = 0` | `PASS` |
| `reserved_state_events = 0` | `PASS` |
| `queue_overflow_events = 0` | `PASS` |
| ten invariant flags | `PASS` |

The workflow keeps structured output, M3 benchmark matrix, M15 implementation
mapping, comparative architecture benchmarking, hardware-informed sensitivity,
M16 RTL qualification, M16 FPGA preparation, and M18 publication evidence in
their separate measurement contours.

## Test Results

| Test boundary | Result |
|---|---|
| M18 Python source compilation | `PASS` |
| isolated `tests/test_frp_m18_canonical_artifacts.py` suite | `54 / 54 PASS` |
| complete `tests/test_*.py` repository suite | `84 / 84 PASS` |
| failures | `0` |
| errors | `0` |

The complete repository suite retains the M15, M16, and M17 regression
coverage present on the qualified commit.

## Repository Immutability Result

Generation and qualification evidence was written only to isolated `/tmp`
directories. The workflow completed both repository checks successfully:

- `git diff --exit-code`;
- `git status --porcelain --untracked-files=all`.

Repository unchanged result:

`PASS`

## Evidence Retention

The workflow retained the following evidence members in the artifact named
`frp-m18-formal-schema-canonical-artifacts`:

- `self-test-a.json`;
- `self-test-b.json`;
- `qualification-a.json`;
- `qualification-b.json`;
- the first independently generated `artifacts/m18/` publication tree.

Retention period:

`30 days`

## Scope Boundary

This qualification does not establish:

- M18 closure;
- an FRP `v2.0.0` tag or release;
- M19 or any later milestone qualification;
- machine-readable M16 execution qualification assigned to M19;
- physical implementation or physical-chip evidence;
- FRP Trace Observatory qualification;
- an AI inference engine;
- a training pipeline;
- autonomous agent logic.

## Final Qualification Status

All mandatory M18 contract, formal schema, canonical artifact, determinism,
semantic invariance, downstream compatibility, self-test, test, workflow, and
repository-immutability gates passed for qualified implementation commit
`5264c7dbfc0c23a96816635faadb3af74d57ae10`.

Final qualification status:

`PASS`

Recorded M18 milestone state:

`QUALIFIED`
