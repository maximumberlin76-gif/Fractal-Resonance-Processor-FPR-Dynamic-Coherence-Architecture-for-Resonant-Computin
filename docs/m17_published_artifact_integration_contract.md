# FRP M17 — Published Artifact Integration Contract

- **Milestone:** M17 — Published Artifact Integration Contract
- **Provisional release target:** v1.9.0
- **Milestone state:** Planned
- **Current qualified upstream boundary:** FRP v1.8.0 / M16
- **Current executable semantic reference:** `frp_prototype_v1_7_0.py`
- **Integration direction:** FRP → published artifacts → downstream consumers

## Purpose

This document defines the upstream publication contract for machine-readable Fractal Resonance Processor artifacts.

The contract establishes:

- the authority of the FRP repository;
- the one-way integration boundary;
- artifact publication states;
- exact artifact and schema identity rules;
- producer association;
- source-byte immutability;
- provenance requirements;
- digest requirements;
- deterministic package requirements;
- measurement-contour separation;
- qualification-evidence handling;
- downstream compatibility requirements;
- M17 closure conditions.

This contract does not change processor semantics, published metric values, scheduler behavior, transition behavior, RTL behavior, FPGA preparation behavior, or existing qualification results.

## Current Qualification Boundary

The current qualified repository boundary remains:

`FRP v1.8.0 / M16`

The current semantic and implementation-mapping foundation remains:

`FRP v1.7.0 / M15`

The current executable semantic reference remains:

`frp_prototype_v1_7_0.py`

The current structured-output schema remains:

`frp.structured_output.v1.7.0`

The current benchmark-matrix schema remains:

`frp.m3.benchmark_matrix.v1.7.0`

M17 must not be represented as completed until its implementation, tests, workflows, qualification evidence, validation index, test report, and release records exist.

## Integration Direction

The integration direction is strictly one-way:

`Fractal-Resonance-Processor`

↓

`published JSON, traces, vectors, schemas, manifests, digests, and qualification records`

↓

`downstream consumers`

Downstream-generated data is not written back into FRP under this contract.

A downstream consumer may:

- capture published source bytes;
- calculate a source-byte digest;
- identify an artifact;
- parse a supported non-executable format;
- validate fields, values, order, relations, and digests;
- construct a separate normalized representation;
- construct explicitly labeled derived views;
- display recorded qualification evidence.

A downstream consumer must not:

- redefine FRP processor semantics;
- replace the executable semantic reference;
- reproduce internal processor execution as an alternative authority;
- modify a published source artifact;
- change a published metric value;
- replace a declared digest;
- invent a missing field or event;
- silently migrate a schema version;
- merge distinct measurement contours;
- convert target-independent FPGA preparation evidence into physical-chip evidence.

## Repository Boundary

The FRP repository contains:

- processor architecture;
- executable semantic references;
- benchmark contours;
- structured output;
- deterministic traces;
- mathematical and physical foundations;
- implementation-mapping artifacts;
- RTL;
- target-independent FPGA preparation;
- qualification evidence;
- artifact producers;
- release-specific records.

Downstream repositories contain their own:

- parsers;
- validators;
- normalized data models;
- visualizations;
- user interfaces;
- downstream tests;
- downstream workflows;
- independent release cycles.

Parser dependencies, UI dependencies, visualization dependencies, and downstream release dependencies must remain outside the qualified FRP repository boundary.

FRP qualification must not import, execute, or depend on downstream implementation code.

## Source Authority

FRP is the sole source of truth for FRP processor semantics.

For a published artifact, authority remains bound to:

- its upstream producer;
- its exact producer version;
- its schema or registered format identity;
- its release or milestone scope;
- its source bytes;
- its declared and calculated digests;
- its qualification evidence.

A downstream interpretation does not replace an upstream value.

A conflict between source bytes, embedded identity, registered producer, declared digest, manifest, or qualification record must be reported. It must not be silently repaired or resolved through substitution.

## Normative Vocabulary

The terms `must`, `must not`, `required`, `shall`, and `shall not` define mandatory contract requirements.

The terms `may` and `optional` define permitted behavior that does not replace a mandatory requirement.

The term `published` applies only to an artifact instance that satisfies one of the publication states defined by this contract.

The term `canonical` applies only when the repository explicitly designates the artifact instance, producer inputs, ordering, serialization, and digest scope.

The term `derived` identifies data calculated outside the published upstream artifact. Derived data must retain its source identity and must not be presented as an upstream value.

## Audited Upstream Baseline

This contract is based on the FRP v1.8.0 / M16 repository boundary and the following existing evidence paths:

- `frp_prototype_v1_7_0.py`;
- `docs/output_schema.md`;
- `docs/benchmark_matrix.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `docs/m16_qualification_manifest.md`;
- `docs/m16_qualification_index.md`;
- `docs/m16_public_status_snapshot.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`;
- `benchmarks/architecture_comparison/`.

The audited baseline contains:

- committed comparative benchmark JSON profiles and results;
- executable structured-output producers;
- executable benchmark-matrix producers;
- executable M15 export producers;
- executable M15 deterministic-vector producers;
- workflow-generated M15 qualification outputs;
- human-readable M16 qualification documents;
- workflow-retained M16 text, log, and SHA-256 evidence.

The audited baseline does not contain:

- formal JSON Schema files;
- committed canonical M15 export JSON files;
- committed canonical M15 vector-package members;
- committed canonical CSV or TSV artifacts;
- machine-readable `frp.m16.*` schema identifiers;
- committed machine-readable M16 per-tick qualification artifacts.

Absence must remain explicit. Missing artifacts must not be reconstructed and represented as published upstream evidence.

## Semantic Invariance

This contract must preserve:

- the canonical processor state domain;
- active neutral state `0`;
- opposite-polarity routing through `0`;
- retained pending-route behavior;
- scheduler modes;
- request-lane behavior;
- transition-capacity behavior;
- retained-state writeback;
- published counters;
- published invariant meanings;
- published metric definitions;
- release-specific schema identities.

M17 introduces a publication contract. It does not introduce a new processor execution model.

## Canonical Processor Domain

The canonical balanced ternary processor domain is:

`-1, 0, 1`

State `0` is the active neutral state.

Canonical opposite-polarity routes are:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

Direct opposite-polarity transitions remain prohibited.

Packed hardware codes, vector encodings, and interface representations are not interchangeable with canonical processor-state values. They require their exact published mapping contract.

## Artifact Publication States

Every artifact instance must have one explicit publication state.

### Repository-Committed

A repository-committed artifact:

- is tracked at an exact repository path;
- is bound to a Git commit;
- has retrievable source bytes;
- may be assigned a canonical role when the repository explicitly declares that role;
- remains independently digestible from its raw bytes.

A generated local file is not repository-committed until its exact bytes are committed.

### Workflow-Retained

A workflow-retained artifact:

- is generated or collected by a named workflow;
- is bound to a workflow run;
- is available only while the workflow artifact remains retained;
- requires the workflow name, run identity, artifact name, member path, and digest for durable provenance.

Workflow retention is not equivalent to repository commitment or archival release storage.

### Release-Archived

A release-archived artifact:

- is attached to an identified FRP release or archival record;
- is bound to an exact release version;
- has a stable asset name;
- has an exact digest;
- remains associated with its source commit and producer.

No M15 or M16 machine-readable artifact may be assigned this state without a recorded asset inventory and digest.

### Producer-Defined

A producer-defined artifact:

- has an executable upstream producer;
- has a known producer version;
- may have an embedded schema or format identifier;
- can be generated from declared inputs;
- does not yet have a contractually published artifact instance.

Producer existence is not publication evidence.

### Documentation-Only

Documentation-only evidence:

- is committed as human-readable text or Markdown;
- may record commands, results, workflow runs, commits, PASS states, or SUCCESS states;
- does not become a typed machine-readable trace solely because values are written in text.

### Planned or Unavailable

A planned or unavailable artifact:

- is absent from the audited repository boundary;
- has no contractually available source bytes;
- must not be reconstructed;
- must not receive an invented schema identifier;
- must not be represented as published evidence.

### State Transition Rule

Publication state changes require explicit repository evidence.

Local generation, parsing, copying, normalization, visualization, or downstream fixture creation must not promote an artifact to a stronger publication state.

## Current Repository-Committed JSON Artifacts

The audited repository contains the following committed JSON artifacts under `benchmarks/architecture_comparison/`.

| Exact repository path | Embedded identity | Role | Producer association |
|---|---|---|---|
| `benchmarks/architecture_comparison/profiles/workload_profile_v1.json` | No embedded schema identifier | Deterministic workload profile | Repository-maintained profile input |
| `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json` | `frp.benchmark.normalized_cost_profile.v1` | Normalized activity-cost profile | Repository-maintained profile input |
| `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json` | `frp.benchmark.thermal_proxy_profile.v1` | Common thermal-proxy profile | Repository-maintained profile input |
| `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json` | `frp.benchmark.hardware_sensitivity_cost_profile.v1` | Hardware-informed sensitivity profile | Validated by `validate_hardware_sensitivity_profile.py` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json` | `frp.benchmark.architecture_comparison.v1` | Canonical comparative architecture result | Produced by `run_architecture_comparison.py` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json` | `frp.benchmark.hardware_sensitivity_comparison.v1` | Canonical hardware-sensitivity result | Produced by `run_hardware_sensitivity_comparison.py` |

The schema-free workload profile is identified by its exact path and its role inside the registered comparative benchmark package. A filename alone is insufficient for external identification.

The four profile files are inputs. The two result files are outputs. Inputs and outputs must not be presented as the same artifact class.

## Comparative Result Producer Commands

The canonical comparative architecture result is generated from:

`benchmarks/architecture_comparison/`

using:

    python run_architecture_comparison.py \
      --workload-profile profiles/workload_profile_v1.json \
      --cost-profile profiles/normalized_cost_profile_v1.json \
      --thermal-profile profiles/thermal_proxy_profile_v1.json \
      --frp-scheduler "7/1" \
      --write results/reference_comparison_seed_76.json \
      --output text

The canonical hardware-sensitivity result is generated from:

`benchmarks/architecture_comparison/`

using:

    python run_hardware_sensitivity_comparison.py \
      --workload-profile profiles/workload_profile_v1.json \
      --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json \
      --thermal-profile profiles/thermal_proxy_profile_v1.json \
      --frp-scheduler "7/1" \
      --write results/reference_comparison_seed_76_hardware_sensitivity_v1.json \
      --output text

Both workflows independently regenerate their result and compare the regenerated bytes with the committed result.

## Current Structured and Benchmark Producers

The current executable producer is:

`frp_prototype_v1_7_0.py`

Current producer version:

`1.7.0`

Current producer milestone:

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

The standard structured output is generated with:

    python frp_prototype_v1_7_0.py --mode demo --output json

Embedded schema identifier:

`frp.structured_output.v1.7.0`

The full structured trace is generated with:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace

Embedded schema identifier:

`frp.structured_output.v1.7.0`

The benchmark matrix is generated with:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix

Embedded schema identifier:

`frp.m3.benchmark_matrix.v1.7.0`

These producers exist in the audited baseline. Their default generated output files are not committed canonical artifacts in that baseline.

## Current M15 Export Producers

The M15 workflow defines the following JSON outputs.

| Workflow output name | Exact schema identifier | Producer option |
|---|---|---|
| `fixed-point-interface-profile.json` | `frp.m15.fixed_point_interface_profile.v1.7.0` | `--export-fixed-point-interface-profile` |
| `balanced-ternary-hardware-encoding-map.json` | `frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0` | `--export-balanced-ternary-hardware-encoding-map` |
| `quantized-reference-shadow-model.json` | `frp.m15.quantized_reference_shadow_model.v1.7.0` | `--export-quantized-reference-shadow-model` |
| `cycle-exact-reference-trace.json` | `frp.m15.cycle_exact_reference_trace.v1.7.0` | `--export-cycle-exact-reference-trace` |
| `rtl-comparison-vector-package.json` | `frp.m15.rtl_comparison_vector_package.v1.7.0` | `--export-rtl-comparison-vector-package` |
| `systemverilog-testbench-interface-map.json` | `frp.m15.systemverilog_testbench_interface_map.v1.7.0` | `--export-systemverilog-testbench-interface-map` |
| `synthesizable-rtl-reference-core.json` | `frp.m15.synthesizable_rtl_reference_core.v1.7.0` | `--export-synthesizable-rtl-reference-core` |
| `rtl-assertion-correlation-harness.json` | `frp.m15.rtl_assertion_correlation_harness.v1.7.0` | `--export-rtl-assertion-correlation-harness` |
| `reference-rtl-equivalence-report.json` | `frp.m15.reference_rtl_equivalence_report.v1.7.0` | `--export-reference-rtl-equivalence-report` |
| `qualification-closure-manifest.json` | `frp.m15.qualification_closure_manifest.v1.7.0` | `--export-qualification-closure-manifest` |

The exact producer form is:

    python frp_prototype_v1_7_0.py <producer-option>

The workflow writes these files under:

`artifacts/m15/`

The workflow uploads the generated directory under the artifact name:

`frp-v1.7.0-m15-qualification-artifacts`

These outputs are producer-defined and workflow-retained. They are not repository-committed canonical artifact instances in the audited baseline.

## Additional M15 Workflow Outputs

The M15 workflow also generates:

- `structured-output.json`;
- `self-test.json`;
- `self-test-free.json`;
- `self-test-7-1.json`;
- `self-test-1-7.json`;
- `benchmark-matrix.json`;
- `scaling-8.json`;
- `scaling-16.json`;
- `scaling-32.json`;
- `vector-package-a.json`;
- `vector-package-b.json`.

The two vector-package generations use separate output directories:

- `artifacts/m15/vectors_a/`;
- `artifacts/m15/vectors_b/`.

The workflow compares these directories recursively for deterministic equality.

These workflow outputs must retain their exact producer arguments. Default-output, scheduler-specific, scaling, and repeat-generation records must not be silently treated as interchangeable fixtures.

## Current M15 Deterministic Vector Package

The producer option:

`--export-rtl-comparison-vector-package`

accepts:

`--vector-output-dir`

and writes the following ten-member package.

| Package member | Format identity or role |
|---|---|
| `frp_m15_kernel_vectors.vec` | `frp.m15.vector.v1`, `kernel_transition_vectors` |
| `frp_m15_pending_routes.trace` | `frp.m15.vector.v1`, `pending_routes` |
| `frp_m15_scheduler_free_vectors.vec` | `frp.m15.vector.v1`, `scheduler_free_vectors` |
| `frp_m15_scheduler_7_1_vectors.vec` | `frp.m15.vector.v1`, `scheduler_7_1_vectors` |
| `frp_m15_scheduler_1_7_vectors.vec` | `frp.m15.vector.v1`, `scheduler_1_7_vectors` |
| `frp_m15_full_correlation_vectors.vec` | `frp.m15.vector.v1`, `full_correlation_vectors` |
| `frp_m15_cell_trace.vec` | `frp.m15.vector.v1`, `cell_trace` |
| `frp_m15_reference_preload.json` | Schema-free package member with exact preload role |
| `frp_m15_trig_lut_q30.vec` | Schema-free package member with exact trigonometric lookup-table role |
| `frp_m15_sha256_manifest.json` | Schema-free package manifest |

The seven headered vector and trace files declare:

- `format_version`;
- `frp_version`;
- `milestone`;
- `trace_kind`.

The SHA-256 manifest records digests for the nine non-manifest members.

The JSON vector-package record declares a deterministic package digest and a ten-file manifest.

A schema-free package member is identifiable only through:

- its exact package role;
- the verified manifest;
- the registered producer;
- the exact package contract.

The ten vector-package members are producer-defined and workflow-retained. They are not repository-committed canonical fixtures in the audited baseline.

## Current M16 Evidence State

The M16 RTL workflow is:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Its workflow artifact name is:

`frp-m16-rtl-qualification-${github.run_number}`

Its retained members are:

- `frp_m16_toolchain.log`;
- `frp_m16_sources.sha256`;
- `frp_m16_build.log`;
- `frp_m16_execution.log`;
- `frp_m16_qualification.txt`.

The M16 FPGA preparation workflow is:

`.github/workflows/frp-m16-fpga-preparation.yml`

Its workflow artifact name is:

`frp-m16-fpga-preparation-${github.run_number}`

Its retained members are:

- `frp_m16_fpga_toolchain.log`;
- `frp_m16_fpga_sources.sha256`;
- `frp_m16_fpga_top_lint.log`;
- `frp_m16_fpga_build.log`;
- `frp_m16_fpga_execution.log`;
- `frp_m16_fpga_qualification.txt`.

Both workflows retain their uploaded qualification artifacts for 30 days.

The repository also contains human-readable M16 qualification evidence, including:

- `docs/m16_qualification_manifest.md`;
- `docs/m16_qualification_index.md`;
- `docs/m16_public_status_snapshot.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

The audited baseline contains no machine-readable `frp.m16.*` schema identifier and no committed machine-readable M16 per-tick trace.

Human-readable M16 qualification evidence must not be represented as a machine-readable processor-tick trace.

Unavailable workflow artifact bytes must not be reconstructed from documentation.

## Published Artifact Identity

Every published artifact must have an exact identity contract.

Identity may be established through one of the following registered mechanisms:

1. an embedded schema identifier;
2. an embedded schema identifier combined with a required artifact kind;
3. an embedded format identifier combined with a required trace kind;
4. an exact role inside a verified deterministic package;
5. an exact path-and-digest contract for a schema-free repository artifact;
6. an exact release-asset name-and-digest contract;
7. an exact workflow-run artifact and member-path contract.

A filename alone is not sufficient identity.

A file extension alone is not sufficient identity.

A repository path must not override conflicting embedded content.

An embedded schema identifier must match exactly. Prefix matching, alias substitution, implicit migration, and automatic version promotion are prohibited.

Historical schema identifiers remain independent versioned identities. They must not be renamed as current identifiers.

An artifact with conflicting identity evidence must fail publication validation until the conflict is resolved upstream.

## Publication Registry Requirements

M17 requires a machine-readable publication inventory.

Each registry entry must record, where applicable:

- artifact role;
- publication state;
- exact repository path;
- release-asset identity;
- workflow identity;
- workflow artifact name;
- workflow member path;
- container format;
- exact schema identifier;
- exact format identifier;
- required artifact kind;
- required trace kind;
- producer path;
- producer version;
- producer command;
- declared producer parameters;
- upstream milestone;
- upstream release;
- source commit;
- measurement contour;
- canonical status;
- required or optional status;
- digest algorithm;
- digest scope;
- declared digest;
- byte length;
- deterministic package identity;
- package-member role;
- package-member order;
- qualification-evidence references.

Unknown values must remain absent or explicitly unavailable.

The registry must not invent a producer, version, schema, digest, package role, workflow run, or qualification result.

Registry membership does not by itself establish qualification, canonical status, or downstream support.

## Provenance Requirements

Every published artifact instance must preserve its own provenance.

Required provenance includes, where applicable:

- source filename;
- exact repository path;
- release-asset name;
- workflow artifact name;
- workflow member path;
- schema or format identifier;
- artifact kind or trace kind;
- producer path;
- producer version;
- producer command;
- producer parameters;
- source commit;
- release version;
- milestone;
- measurement contour;
- raw-byte digest;
- raw-byte length;
- package identity;
- package-member identity;
- qualification record;
- validation status;
- validation messages.

A copied artifact must retain the provenance of its upstream source instance.

A downstream load timestamp is downstream metadata. It is not an upstream generation timestamp and must not replace upstream provenance.

A missing provenance value must remain missing. It must not be derived from a filename unless the exact filename rule is part of the registered contract.

## Source-Byte Immutability

Published source bytes are immutable artifact evidence.

Before parsing or normalization, a consumer must be able to:

1. capture the original bytes;
2. record the byte length;
3. calculate the registered raw-byte digest;
4. retain the original bytes or an exact retrievable source reference.

The following operations are prohibited before raw-byte digest calculation:

- whitespace normalization;
- line-ending normalization;
- character replacement;
- field insertion;
- field deletion;
- field renaming;
- array reordering;
- numeric conversion;
- default insertion;
- schema migration;
- manifest repair.

Parsing must produce a separate representation.

Normalization must produce a separate representation.

Derived calculations must produce a separate representation.

No parsed, normalized, filtered, sorted, correlated, or visualized representation may replace the original artifact bytes.

## Digest Contract

The contract distinguishes the following digest scopes:

- raw source bytes;
- canonical JSON substructure;
- processor-tick trace;
- per-cell trace;
- profile content;
- package member;
- deterministic package;
- source-file set;
- qualification evidence set.

Digest values from different scopes are not interchangeable.

The current repository uses SHA-256 for published integrity records.

A SHA-256 value must be represented as:

- 64 lowercase hexadecimal characters;
- bound to an explicit byte or serialization scope;
- associated with an explicit artifact or package identity.

A digest field embedded inside a JSON profile is not automatically the raw-byte digest of the complete JSON file.

A canonical-substructure digest requires an exact serialization rule.

A trace digest requires an exact trace ordering and serialization rule.

A package digest requires an exact member set and ordering rule.

A source-file-set digest requires exact paths and ordering.

A digest must not be validated using an inferred serialization rule.

If the required algorithm, scope, ordering, or serialization rule is unavailable, digest validation must report that the check cannot be evaluated.

A mismatch must retain:

- the declared digest;
- the calculated digest;
- the digest scope;
- the affected artifact identity;
- the validation failure.

A consumer must not replace the declared value with the calculated value.

## Deterministic Artifact Packages

A deterministic package contract must define:

- package identity;
- producer;
- producer version;
- producer parameters;
- exact member count;
- exact member names;
- exact member roles;
- exact member formats;
- member ordering;
- per-member digest rules;
- package-digest rules;
- required cross-file relations;
- missing-member behavior;
- unexpected-member behavior.

Package validation must reject:

- missing required members;
- unexpected members when the package is closed;
- duplicate member roles;
- duplicate member names;
- invalid member digests;
- invalid package digests;
- conflicting identifiers;
- incorrect member ordering when ordering is normative.

A missing member must not be regenerated and inserted during validation.

A schema-free member may be identified only through its verified package role and exact package contract.

The M15 deterministic vector package remains a ten-member package.

The M15 SHA-256 manifest binds the nine non-manifest members. The manifest does not contain a digest for itself.

The manifest and the JSON vector-package record must remain distinct artifacts with distinct digest scopes.

## Required Validation Layers

Publication qualification must evaluate independent validation layers.

### Container and Encoding

Checks include:

- supported container format;
- valid encoding;
- complete parse;
- no trailing executable payload;
- resource-bound processing.

### Identity

Checks include:

- exact schema identifier;
- exact format identifier;
- required artifact kind;
- required trace kind;
- exact producer association;
- exact version association;
- exact package role.

### Structure

Checks include:

- required fields;
- optional fields;
- field types;
- array and object structure;
- allowed null behavior;
- allowed value domains.

### Processor Domain

Checks include:

- canonical processor states restricted to `-1`, `0`, and `1`;
- active neutral state preserved;
- opposite-polarity routing through `0`;
- packed encodings checked only against their exact mapping contract.

### Ordering

Checks include:

- source record order;
- trace order;
- tick order;
- package-member order;
- deterministic-set order;
- invariant-vector bit order.

### Relations

Checks include, where published:

- scheduler-counter relations;
- transition-capacity relations;
- pending-route relations;
- retained-state relations;
- accepted and rejected request-lane relations;
- zero-event relations;
- invariant relations.

### Digests

Checks include:

- declared digest syntax;
- registered algorithm;
- registered scope;
- registered serialization;
- calculated equality;
- manifest consistency;
- package consistency.

### Qualification

Checks include:

- release identity;
- milestone identity;
- workflow identity;
- workflow run;
- qualified commit;
- recorded result;
- artifact-set identity;
- evidence digest.

A success at one layer does not imply success at another layer.

A mandatory failure must not be converted into a warning.

## Trace and Event Ordering

Published source order must be preserved.

A validator must not silently sort an invalid trace and present the sorted result as source order.

A separately sorted view must be labeled as derived and must retain the original source-order result.

Tick monotonicity, uniqueness, and continuity must be evaluated only under the exact registered artifact contract.

An absent event is not equivalent to a zero-valued event.

An absent field is not equivalent to a field containing `0`.

Aggregate counters must not be expanded into invented per-tick or per-cell events.

Published event records may include:

- first-leg neutralization;
- retained pending polarity;
- pending-route completion;
- scheduler deferral;
- transition-capacity deferral;
- accepted request lanes;
- rejected request lanes;
- actual direct events;
- reserved-state events;
- queue-overflow events;
- invariant flags.

Event acceptance, rejection, or deferral reasons must not be inferred from unrelated aggregate counters.

Scheduler mode, scheduler state, request-lane state, pending-route state, retained processor state, transition capacity, switching load, and thermal-state proxy remain distinct fields.

## Measurement-Contour Separation

The following measurement contours remain separate:

- historical transition benchmark;
- structured-output benchmark;
- M3 benchmark matrices;
- transition-pressure and feedback-stress matrix;
- thermal-survival and stability-boundary matrix;
- hierarchical scaling and hotspot-containment matrix;
- M15 implementation-mapping matrix;
- Comparative Architecture Benchmark Suite;
- Hardware-Informed Sensitivity Qualification;
- M16 RTL qualification;
- M16 FPGA preparation qualification.

Every published artifact must retain its measurement contour.

The following quantities must not be represented as interchangeable:

- operation count;
- normalized activity cost;
- thermal proxy;
- transition pressure;
- `heat_peak`;
- switching load;
- scheduler timing;
- latency;
- throughput;
- RTL execution;
- FPGA preparation evidence;
- implementation-tool evidence;
- physical measurement.

Identical field names across contours do not establish identical definitions, units, scopes, or methods.

Cross-contour correlation is a separate derived operation. It must retain every source contour and must not replace the published source values.

Comparative aggregate results are not processor-tick traces.

Target-independent FPGA preparation evidence is not physical-chip evidence.

## Qualification Evidence

Qualification evidence must retain:

- release;
- milestone;
- evidence contour;
- producer or workflow;
- workflow run when recorded;
- qualified commit when recorded;
- artifact-set identity;
- source paths;
- result;
- qualification status;
- declared digests;
- evidence availability.

Published `PASS` and `SUCCESS` values may be reproduced exactly as recorded.

A zero-event qualification result is valid only when:

- the event field is explicitly present;
- the value is explicitly `0`;
- the execution scope is recorded;
- the artifact or evidence source is identified.

Invariant vectors must retain their source bit order.

A bit position must not receive an inferred meaning without an exact upstream mapping.

Human-readable qualification documents remain human-readable evidence.

Workflow logs remain workflow evidence.

Neither form becomes a machine-readable processor trace without an explicit machine-readable producer and identity contract.

Expired, deleted, or otherwise unavailable workflow artifact bytes must be reported as unavailable.

Qualification evidence must not be reconstructed from summaries.

## Downstream Compatibility

Downstream compatibility requires exact upstream evidence.

A downstream consumer may declare an artifact recognized only when:

- the artifact identity matches an exact upstream registry entry;
- the publication state is preserved;
- the producer association is preserved;
- the source bytes remain unchanged;
- the source-byte digest is recorded;
- required fields and values are validated;
- applicable order and relation checks are performed;
- applicable manifest and digest checks are performed;
- the measurement contour is preserved.

Recognition is not equivalent to full support.

A downstream consumer may declare an artifact supported only when it also has:

- a read-only parser;
- an exact normalized data mapping;
- a validator;
- canonical fixture evidence;
- mandatory-failure fixtures;
- provenance tests;
- immutability tests;
- digest tests;
- mode-integration tests;
- applicable CI evidence.

FRP Trace Observatory has an independent repository and release cycle.

This contract does not assign an Observatory version and does not declare an Observatory release.

An FRP release does not automatically change the supported Observatory release set.

An Observatory release does not change FRP processor semantics or qualification state.

## Safe Consumption Boundary

Published artifacts are data.

A conforming downstream consumer must not:

- execute uploaded scripts;
- execute uploaded expressions;
- invoke producer commands automatically;
- compile uploaded SystemVerilog;
- simulate uploaded SystemVerilog;
- import uploaded Python modules;
- follow uncontrolled external paths;
- fetch external resources automatically;
- write into the upstream repository;
- overwrite captured source bytes.

SystemVerilog source may be handled as opaque evidence for:

- exact filename checks;
- exact path checks;
- byte-length checks;
- raw-byte digest checks;
- package membership checks.

Archive extraction is outside the current contract.

Any future archive handling must reject:

- path traversal;
- absolute-path extraction;
- unsafe symbolic links;
- unsafe hard links;
- external writes;
- decompression beyond declared resource limits.

Rendered artifact strings remain data and must not be executed as markup, commands, or code.

## Versioning and Change Control

FRP version, milestone, schema version, artifact format version, package version, workflow run, and downstream version are separate identities.

A new FRP release does not automatically rename an existing schema.

A new milestone does not automatically change an existing artifact format.

The existing M15 identifiers remain M15 identifiers.

They must not be renamed as M17 identifiers.

A semantic contract change requires a new exact schema or format identity.

A structural change that invalidates an existing parser requires a new exact schema or format identity.

A canonical artifact byte change requires:

- regenerated source-byte digest;
- regenerated manifest records;
- recorded producer inputs;
- recorded source commit;
- repeated deterministic validation;
- updated qualification evidence.

Historical artifacts and identifiers remain historical records.

Automatic migration, aliasing, and version substitution are prohibited.

A registry change requires synchronized review of:

- artifact identity;
- producer;
- version;
- publication state;
- path;
- format;
- schema;
- contour;
- digest scope;
- package relations;
- qualification evidence;
- tests;
- documentation;
- workflows.

## M17 Required Deliverables

M17 requires:

1. this published artifact integration contract;
2. a machine-readable publication inventory;
3. deterministic publication-inventory generation;
4. exact registry entries for committed comparative JSON artifacts;
5. exact registry entries for current structured-output and benchmark producers;
6. exact registry entries for all ten M15 export producers;
7. exact registry entries for the ten-member M15 deterministic vector package;
8. exact registry entries for M16 workflow-retained evidence;
9. explicit records for documentation-only evidence;
10. explicit records for planned or unavailable artifacts;
11. deterministic registry ordering;
12. publication-state validation;
13. identity validation;
14. path validation;
15. producer validation;
16. measurement-contour validation;
17. tests for missing, conflicting, duplicate, and invalid records;
18. a qualification workflow;
19. a release-specific test report;
20. a release-specific validation index;
21. release-specific release notes;
22. repository-wide status alignment after qualification closure.

The machine-readable inventory must describe the audited state. It must not manufacture missing M15 or M16 artifact instances.

## M17 Acceptance Criteria

M17 may close only when all of the following are true:

1. the integration contract is committed;
2. the publication inventory is generated deterministically;
3. all current repository-committed JSON artifacts are registered;
4. the schema-free workload profile has an exact role-based identity contract;
5. `frp.structured_output.v1.7.0` is registered exactly;
6. `frp.m3.benchmark_matrix.v1.7.0` is registered exactly;
7. all ten M15 export schema identifiers are registered exactly;
8. `frp.m15.vector.v1` and every registered trace kind are preserved exactly;
9. all ten M15 vector-package members are registered;
10. M15 producer-defined and workflow-retained states remain distinct from repository commitment;
11. M16 workflow-retained evidence members are registered;
12. documentation-only M16 evidence remains distinct from machine-readable trace evidence;
13. missing formal JSON Schema files remain explicitly absent;
14. missing committed M15 canonical artifacts remain explicitly absent;
15. missing CSV and TSV artifacts remain explicitly absent;
16. missing machine-readable `frp.m16.*` schemas remain explicitly absent;
17. every measurement contour remains separate;
18. registry ordering is deterministic;
19. duplicate and conflicting identities fail validation;
20. missing required registry fields fail validation;
21. publication-state promotion without evidence fails validation;
22. tests pass;
23. the M17 qualification workflow records `SUCCESS`;
24. the release-specific qualification result records `PASS`;
25. upstream qualification executes no downstream code.

Until every criterion is satisfied, M17 remains planned.

## M18 Handoff Boundary

The following work remains outside M17 closure and enters the M18 scope:

- formal JSON Schema publication;
- committed canonical structured-output fixtures;
- committed canonical full-trace fixtures;
- committed canonical benchmark-matrix fixtures;
- committed canonical M15 export JSON artifacts;
- committed canonical M15 vector-package members;
- committed canonical digest manifests;
- canonical CSV publication where a stable upstream tabular contract is defined;
- formal validation of every published canonical artifact.

M17 records the current publication state.

M18 changes eligible producer-defined artifacts into committed canonical artifact instances after their schemas, paths, producer inputs, digests, tests, and workflows are established.

## M19 Handoff Boundary

The following work remains outside M17 and M18 closure and enters the M19 scope:

- machine-readable M16 RTL execution schemas;
- machine-readable M16 FPGA preparation schemas;
- committed M16 processor-tick traces;
- committed M16 request-lane records;
- committed M16 pending-route records;
- committed M16 transition-capacity records;
- committed M16 telemetry records;
- committed M16 invariant vectors;
- committed M16 zero-event qualification records;
- committed M16 qualification manifests;
- deterministic M16 artifact-set digests.

No `frp.m16.*` schema identifier may be declared before its exact structure, producer, version, path, tests, and qualification workflow are implemented.

## Non-Goals

M17 does not authorize:

- changes to FRP processor semantics;
- replacement of `frp_prototype_v1_7_0.py`;
- creation of an alternative executable semantic reference;
- changes to canonical ternary states;
- use of `1` with an added positive sign in the canonical processor-domain notation;
- direct `-1` to `1` transitions;
- direct `1` to `-1` transitions;
- changes to scheduler semantics;
- changes to transition-capacity semantics;
- changes to published metric values;
- mixing of benchmark contours;
- rewriting historical schemas;
- reconstruction of unavailable evidence;
- downstream writeback;
- UI dependencies inside FRP;
- downstream parser dependencies inside FRP;
- AI inference;
- training pipelines;
- autonomous-agent logic;
- RPU integration;
- new physical-chip claims;
- release claims without tests and workflow evidence.

## Contract Completion Rule

This document defines the M17 publication boundary.

It does not by itself close M17.

M17 closure requires the complete implementation and evidence set defined in this contract.

Until that closure exists:

- FRP v1.8.0 remains the current qualified release;
- M16 remains the current qualified milestone;
- M17 remains planned;
- existing M15 schema identities remain unchanged;
- missing upstream artifacts remain explicitly missing.

## Author

Maksym Marnov (Alchimist)
