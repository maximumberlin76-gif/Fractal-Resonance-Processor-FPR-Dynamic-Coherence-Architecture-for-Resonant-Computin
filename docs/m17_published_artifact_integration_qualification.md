# FRP M17 Published Artifact Integration Qualification

## Status

`PASS`

Qualified boundary:

`M17 PUBLISHED ARTIFACT INTEGRATION QUALIFICATION`

Recorded inventory milestone state:

`planned`

## Baseline

| Field | Recorded value |
|---|---|
| Baseline release | `FRP v1.8.0` |
| Baseline milestone | `M16 — RTL Core Realization and Execution Semantics Package` |
| M17 inventory version | `1.9.0` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| Source authority | `FRP` |

## Purpose

This document records the qualified execution of the M17 published-artifact
inventory and one-way integration boundary.

The qualified integration direction is:

`FRP → published artifacts → downstream consumers`

FRP remains the source authority for processor semantics, schemas, producer
commands, published values, traces, manifests, and qualification records.

The M17 inventory reads and identifies upstream publication surfaces without
redefining processor semantics, changing source artifacts, executing recorded
producer commands, or merging measurement contours.

## Qualified Source Boundary

| Path | Role |
|---|---|
| `docs/m17_published_artifact_integration_contract.md` | one-way integration and publication contract |
| `frp_m17_publication_inventory.py` | deterministic machine-readable inventory generator |
| `tests/test_frp_m17_publication_inventory.py` | dependency-free M17 qualification tests |
| `.github/workflows/frp-m17-published-artifact-integration.yml` | executable qualification workflow |

This document is the post-execution qualification record for that boundary.

## Workflow Execution Record

| Field | Recorded value |
|---|---|
| Workflow | `FRP M17 Published Artifact Integration` |
| Workflow file | `.github/workflows/frp-m17-published-artifact-integration.yml` |
| Job | `M17 Published Artifact Integration Qualification` |
| Workflow run | `#1` |
| Qualified commit | `08e5714` |
| Branch | `main` |
| Event | `push` |
| Result | `SUCCESS` |
| Duration | `16s` |
| Python | `3.12` |
| Repository permission | `contents: read` |
| Evidence retention | `30 days` |

## Qualification Results

| Qualification item | Result |
|---|---|
| workflow syntax and GitHub Actions execution | `PASS` |
| M17 generator source syntax | `PASS` |
| M17 test source syntax | `PASS` |
| built-in inventory self-test | `25 / 25 PASS` |
| dependency-free unit-test suite | `30 / 30 PASS` |
| deterministic inventory generation | `2 / 2 byte-identical` |
| inventory identity validation | `PASS` |
| inventory summary validation | `PASS` |
| publication-state count validation | `PASS` |
| record ordering validation | `PASS` |
| record-identifier uniqueness validation | `PASS` |
| canonical ternary domain validation | `PASS` |
| opposite-polarity route validation | `PASS` |
| inventory content-digest recomputation | `PASS` |
| self-test and inventory digest correlation | `PASS` |
| source hash recording | `PASS` |
| repository unchanged validation | `PASS` |
| qualification evidence generation | `PASS` |

## Machine-Readable Inventory Identity

| Field | Exact value |
|---|---|
| Schema | `frp.m17.published_artifact_inventory.v1.9.0` |
| Kind | `published_artifact_inventory` |
| Version | `1.9.0` |
| Milestone | `M17 — Published Artifact Integration Contract` |
| Milestone state | `planned` |
| Baseline release | `FRP v1.8.0` |
| Semantic reference | `frp_prototype_v1_7_0.py` |
| Source authority | `frp` |
| Integration direction | `frp_to_published_artifacts_to_downstream_consumers` |
| Record order | `record_id_lexicographic` |
| Raw digest algorithm | `sha256` |
| Inventory digest scope | `canonical_compact_json_without_inventory_content_sha256` |

Self-test identity:

| Field | Exact value |
|---|---|
| Schema | `frp.m17.published_artifact_inventory.self_test.v1.9.0` |
| Kind | `published_artifact_inventory_self_test` |
| Version | `1.9.0` |
| Status | `PASS` |
| Check count | `25` |

## Inventory Summary

| Record | Value |
|---|---:|
| Total inventory records | `63` |
| Exact schema identifiers | `17` |
| Repository-committed canonical JSON artifacts | `6` |
| M15 export schemas | `10` |
| M15 deterministic vector package members | `10` |
| M16 workflow-retained evidence members | `11` |
| Documentation-only records | `13` |
| Planned-unavailable records | `4` |

## Publication-State Counts

| Publication state | Count |
|---|---:|
| `documentation_only` | `13` |
| `planned_unavailable` | `4` |
| `producer_defined` | `29` |
| `release_archived` | `0` |
| `repository_committed` | `6` |
| `workflow_retained` | `11` |

## Measurement-Contour Separation

The inventory records the following measurement-contour assignments without
combining their values:

| Measurement contour | Inventory records |
|---|---:|
| `comparative_architecture_benchmark_suite` | `4` |
| `hardware_informed_sensitivity_qualification` | `2` |
| `m15_implementation_mapping_matrix` | `29` |
| `m16_fpga_preparation_qualification` | `6` |
| `m16_rtl_qualification` | `5` |
| `structured_output_benchmark` | `0` |

These counts identify inventory records assigned to each contour. They do not
combine operation count, thermal proxy, transition pressure, scheduler timing,
latency, throughput, RTL execution, FPGA preparation, or physical measurement
fields.

## Canonical Balanced Ternary Contract

Canonical processor domain:

`-1/0/1`

Active neutral state:

`0`

Canonical opposite-polarity routes:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

The workflow validates the exact domain, both routes, and canonical positive
state notation.

## Recorded Publication Gaps

The inventory preserves four explicit absence records from the qualified
baseline:

| Record identifier | Recorded count |
|---|---:|
| `missing.formal_json_schemas` | `0` committed formal JSON Schema files |
| `missing.committed_m15_canonical_artifacts` | `0` committed M15 canonical vector members |
| `missing.canonical_csv_tsv_artifacts` | `0` committed canonical CSV or TSV artifacts |
| `missing.machine_readable_m16_artifacts` | `0` machine-readable FRP M16 schema identifiers |

These records remain distinct from committed, producer-defined,
documentation-only, and workflow-retained publication states.

## Provenance and Digest Validation

For each repository-committed canonical JSON artifact, the inventory records:

- exact repository path;
- source filename;
- schema identifier when embedded by the source artifact;
- byte length;
- raw SHA-256 digest;
- measurement contour;
- upstream release and milestone.

The generated inventory records its own content digest under:

`inventory_content_sha256`

The workflow removes that field from the digest input, renders the remaining
payload as canonical compact JSON, recomputes SHA-256, and requires an exact
match with the declared inventory digest.

The built-in self-test records the same inventory digest and requires exact
correlation with the generated inventory.

## Deterministic Evidence Set

The workflow generates the following evidence under the isolated directory:

`/tmp/frp_m17_publication_evidence`

| Evidence member | Function |
|---|---|
| `frp_m17_inventory_a.json` | first deterministic inventory rendering |
| `frp_m17_inventory_b.json` | second deterministic inventory rendering |
| `frp_m17_self_test.json` | 25-check machine-readable self-test result |
| `frp_m17_unittest.log` | 30-test execution log |
| `frp_m17_sources.sha256` | qualification-source SHA-256 records |
| `frp_m17_qualification.txt` | workflow, commit, result, counts, and digest record |

The two inventory renderings are required to be byte-identical.

Retained workflow artifact:

`frp-m17-published-artifact-integration-1`

Retention period:

`30 days`

## Repository Immutability Result

All generated qualification evidence is written outside the repository under
`/tmp`.

The workflow executes both:

- `git diff --exit-code`;
- `git status --porcelain --untracked-files=all`.

Repository unchanged result:

`PASS`

## Synchronized Workflow Surface

The qualified commit completed the following repository workflows with
`SUCCESS`:

| Workflow | Run | Commit | Branch | Result | Duration |
|---|---:|---|---|---|---:|
| `FRP M17 Published Artifact Integration` | `#1` | `08e5714` | `main` | `SUCCESS` | `16s` |
| `FRP Self Test` | `#563` | `08e5714` | `main` | `SUCCESS` | `29s` |
| `FRP Benchmark Smoke Test` | `#560` | `08e5714` | `main` | `SUCCESS` | `30s` |
| `FRP Structured Output` | `#521` | `08e5714` | `main` | `SUCCESS` | `54s` |

## Qualification Conclusion

| Qualified boundary | Result |
|---|---|
| M17 published-artifact inventory | `PASS` |
| one-way FRP publication integration direction | `PASS` |
| deterministic inventory rendering | `PASS` |
| provenance and digest verification | `PASS` |
| measurement-contour separation | `PASS` |
| canonical balanced ternary contract | `PASS` |
| repository immutability | `PASS` |
| retained qualification evidence | `PASS` |

Recorded qualification status:

`M17 PUBLISHED ARTIFACT INTEGRATION QUALIFICATION — PASS`
