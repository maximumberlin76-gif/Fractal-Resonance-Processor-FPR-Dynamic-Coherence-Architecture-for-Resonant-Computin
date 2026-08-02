# FRP M18 — Formal Schema and Canonical Artifact Publication Contract

- **Milestone:** M18 — Formal Schema and Canonical Artifact Publication
- **Provisional release target:** v2.0.0
- **Milestone state:** Planned
- **Current qualified release boundary:** FRP v1.8.0 / M16
- **Qualified integration baseline:** M17 Published Artifact Integration Qualification Closure
- **Current executable semantic reference:** `frp_prototype_v1_7_0.py`
- **Source authority:** FRP
- **Integration direction:** FRP → published artifacts → downstream consumers

## Purpose

This document defines the technical contract for formal schema publication and canonical machine-readable artifact publication at M18.

M18 converts eligible producer-defined publication surfaces recorded by M17 into repository-committed canonical artifacts with:

- exact schema identities;
- formal validation rules;
- exact repository paths;
- exact producer paths and commands;
- fixed producer inputs;
- deterministic serialization;
- raw-byte SHA-256 digests;
- canonical fixture provenance;
- deterministic regeneration checks;
- negative validation tests;
- executable qualification workflow evidence.

This contract does not replace the M17 integration contract.

The M17 contract remains authoritative for:

- FRP source authority;
- one-way downstream integration;
- publication-state meanings;
- source-byte immutability;
- provenance requirements;
- digest requirements;
- measurement-contour separation;
- downstream compatibility;
- safe artifact consumption.

M18 defines the additional requirements that an artifact must satisfy before its publication state may be promoted to a repository-committed canonical artifact.

## Current Qualification Boundary

The current qualified release boundary remains:

`FRP v1.8.0 / M16`

The current executable semantic reference remains:

`frp_prototype_v1_7_0.py`

The current structured-output schema identity remains:

`frp.structured_output.v1.7.0`

The current benchmark-matrix schema identity remains:

`frp.m3.benchmark_matrix.v1.7.0`

The qualified M17 integration direction remains:

`FRP → published artifacts → downstream consumers`

The M17 qualification boundary is closed with result:

`PASS`

The qualified M17 machine-readable inventory records:

- `63` artifact records;
- `17` exact schema identifiers;
- `6` repository-committed canonical JSON artifacts;
- `29` producer-defined records;
- `10` M15 export schema records;
- `10` M15 deterministic vector-package members;
- `11` M16 workflow-retained evidence members;
- `4` explicit planned-unavailable publication records.

The qualified M17 inventory schemas are:

- `frp.m17.published_artifact_inventory.v1.9.0`;
- `frp.m17.published_artifact_inventory.self_test.v1.9.0`.

M17 qualification closure does not create an M17 release.

Until M18 closure is complete:

- FRP v1.8.0 remains the current qualified release;
- M16 remains the current qualified release milestone;
- M18 remains planned;
- producer-defined outputs remain noncanonical unless explicitly committed and qualified;
- missing formal schemas remain missing;
- missing committed M15 artifacts remain missing;
- no M18 release claim may be made.

## Normative Authority

FRP is the sole source of truth for FRP processor semantics.

The authority chain for every M18 canonical artifact is:

`executable upstream producer`

↓

`fixed producer command and fixed producer inputs`

↓

`canonical serialized source bytes`

↓

`formal schema or registered format contract`

↓

`raw-byte SHA-256 digest`

↓

`qualification tests and workflow evidence`

A schema does not create processor semantics.

A canonical fixture does not replace its executable producer.

A digest does not validate semantic correctness by itself.

A downstream consumer does not become an upstream authority by parsing, normalizing, auditing, or visualizing a canonical artifact.

If an artifact, schema, producer, command, input, manifest, digest, or qualification record conflicts with another member of the authority chain, qualification must fail.

The conflict must not be silently repaired, normalized, migrated, or substituted.

## Normative Vocabulary

The terms `must`, `must not`, `required`, `shall`, and `shall not` define mandatory requirements.

The terms `may` and `optional` define permitted behavior that does not replace a mandatory requirement.

The term `formal schema` means a repository-committed machine-readable schema with an exact identifier, exact version, exact path, declared dialect, deterministic bytes, tests, and qualification evidence.

The term `canonical artifact` means one exact repository-committed artifact instance whose producer, command, inputs, ordering, serialization, provenance, digest, and qualification evidence are fixed by this contract.

The term `canonical artifact set` means an ordered collection of canonical artifacts governed by one manifest and one deterministic regeneration procedure.

The term `producer-defined` means that an executable producer and format identity exist but no repository-committed canonical artifact instance has yet been qualified.

The term `derived export` means a deterministic representation generated from an authoritative upstream artifact without changing its recorded values.

A derived export must identify its authoritative source artifact and must not replace that source artifact.

## M18 Objective

The M18 objective is:

`publish formally validated canonical machine-readable artifacts for the existing structured-output and M15 layers`

M18 must close the four publication gaps recorded by the qualified M17 inventory where they belong to the M18 boundary:

- formal JSON Schema files;
- committed canonical M15 JSON artifacts;
- committed canonical M15 deterministic vector-package members;
- canonical tabular exports where a stable upstream representation is explicitly defined.

The M17 record for missing machine-readable M16 artifacts is not closed by M18.

Machine-readable M16 execution and qualification evidence remains assigned to M19.

## Required M18 Deliverables

M18 requires:

1. a formal schema registry;
2. formal schemas for supported structured JSON outputs;
3. formal schemas for supported benchmark matrices;
4. formal schemas for supported comparative benchmark artifacts;
5. formal schemas for supported hardware-sensitivity artifacts;
6. formal schemas for supported M15 export JSON artifacts;
7. canonical structured-output artifacts;
8. canonical structured-output artifacts with full trace data;
9. canonical benchmark-matrix artifacts;
10. committed M15 implementation-mapping JSON artifacts;
11. committed M15 deterministic vector fixtures;
12. committed M15 trace fixtures;
13. committed M15 preload fixtures;
14. committed M15 lookup-table fixtures;
15. committed raw-byte digest manifests;
16. canonical CSV exports only where a stable tabular contract is defined;
17. exact producer-command recording;
18. exact producer-input recording;
19. canonical fixture provenance;
20. deterministic byte-for-byte regeneration checks;
21. formal validation of every canonical JSON artifact;
22. registered-format validation of every canonical non-JSON artifact;
23. negative tests for missing fields;
24. negative tests for invalid types;
25. negative tests for invalid values;
26. negative tests for noncanonical ternary states;
27. negative tests for invalid ordering and relations;
28. exact digest verification;
29. repository-immutability verification;
30. an executable M18 qualification workflow;
31. retained machine-readable qualification evidence;
32. a post-execution M18 qualification record;
33. an M18 qualification closure record.

A deliverable is not complete merely because its file exists.

Every required deliverable must be bound to its tests, workflow, provenance, and qualification evidence.

## Scope Boundary

M18 covers formal publication of existing machine-readable surfaces produced or registered by:

- `frp_prototype_v1_7_0.py`;
- the structured-output interface;
- the benchmark-matrix export interface;
- the M15 implementation-mapping export interfaces;
- the M15 deterministic vector-package interface;
- the Comparative Architecture Benchmark Suite;
- the Hardware-Informed Sensitivity Qualification suite;
- the qualified M17 publication inventory.

M18 may add publication infrastructure, schemas, canonical artifact instances, manifests, validators, tests, and workflows.

M18 must not alter the numerical meaning of an existing published field.

M18 must not alter the execution behavior of an existing producer merely to simplify schema validation.

If an existing producer output exposes a real structural inconsistency, the inconsistency must be recorded and resolved through explicit versioned change control.

No existing schema identifier may be silently assigned new semantics.

No new schema identifier may be declared without:

- an exact structure;
- an exact producer or registered source;
- an exact version;
- an exact repository path;
- required-field rules;
- value-domain rules;
- tests;
- qualification workflow coverage.

## Non-Goals

M18 does not authorize:

- a new processor execution model;
- a replacement executable semantic reference;
- changes to canonical processor semantics;
- changes to scheduler semantics;
- changes to request-lane semantics;
- changes to retained pending-route semantics;
- changes to transition-capacity semantics;
- changes to published metric definitions;
- merging of distinct measurement contours;
- reconstruction of missing upstream evidence;
- downstream writeback into FRP;
- downstream parser dependencies inside FRP;
- user-interface dependencies inside FRP;
- visualization dependencies inside FRP;
- machine-readable M16 RTL execution schemas;
- machine-readable M16 FPGA preparation schemas;
- committed M16 processor-tick traces;
- committed M16 request-lane records;
- committed M16 pending-route records;
- committed M16 transition-capacity records;
- committed M16 telemetry records;
- committed M16 invariant vectors;
- committed M16 zero-event qualification records;
- physical-chip claims derived from target-independent FPGA preparation;
- AI inference;
- training pipelines;
- autonomous-agent logic;
- RPU integration;
- release claims without complete tests and workflow evidence.

The excluded M16 machine-readable publication layer remains assigned to M19.

## Semantic Invariance

M18 is a publication milestone.

M18 must preserve:

- the executable behavior of `frp_prototype_v1_7_0.py`;
- the meaning of every existing schema identifier;
- the canonical balanced ternary state domain;
- active neutral state `0`;
- opposite-polarity routing through `0`;
- first-leg neutralization;
- retained pending polarity;
- pending-route completion;
- scheduler deferral;
- transition-capacity deferral;
- accepted and rejected request-lane meanings;
- `actual_direct_events`;
- `reserved_state_events`;
- `queue_overflow_events`;
- invariant meanings;
- published counter relations;
- published metric values;
- deterministic ordering;
- measurement-contour separation.

Formal schemas must describe existing authoritative values and relations.

Formal schemas must not redefine those values or relations.

Canonical fixtures must record producer output.

Canonical fixtures must not become manually authored substitutes for producer output.

## Canonical Processor Domain

The canonical balanced ternary processor domain is:

`-1/0/1`

State `0` is the active neutral state.

The canonical opposite-polarity routes are:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

The canonical positive processor state must be written as `1`.

The notation `+1` must not be used as the canonical positive processor-state value.

Direct opposite-polarity state transitions remain prohibited.

The scheduler modes remain distinct:

- `free` permits unrestricted scheduler operation;
- `7/1` executes seven `balance` ticks followed by one `commit` tick;
- `1/7` executes one `excite` tick followed by seven `neutralize` ticks.

Packed hardware encodings, fixed-point words, vector encodings, and interface codes are not canonical processor-state values.

Every encoded representation must remain bound to its exact published mapping contract.

## M18 Publication Promotion Rule

M18 promotes an artifact from `producer_defined` to `repository_committed` only when all publication requirements are satisfied.

Promotion requires:

1. an exact artifact role;
2. an exact artifact format;
3. an exact schema identifier or registered non-JSON format identifier;
4. an exact producer path;
5. an exact producer version;
6. an exact producer command;
7. fixed producer inputs;
8. an exact canonical repository path;
9. deterministic ordering;
10. deterministic serialization;
11. byte-for-byte reproducibility;
12. a raw-byte SHA-256 digest;
13. a manifest association;
14. complete provenance;
15. positive validation tests;
16. negative validation tests;
17. qualification workflow coverage;
18. repository-immutability verification.

A locally generated artifact is not canonical.

A workflow-retained artifact is not repository-committed.

A repository-committed artifact is not M18-qualified merely because it is present in the repository.

Canonical status requires an explicit registry record and successful qualification against this contract.

Promotion must preserve the exact source bytes selected for the canonical artifact.

Normalization, reformatting, field insertion, field removal, key renaming, value conversion, or schema migration produces a different artifact instance.

Any such change requires:

- a distinct artifact digest;
- an explicit producer or transformation record;
- an explicit provenance relation;
- independent validation;
- versioned change control.

Existing repository-committed comparative benchmark profiles and results remain at their existing paths.

They must not be duplicated under the M18 artifact directory.

M18 qualification binds those existing source paths to formal schemas, registry records, digests, and qualification evidence without silently replacing their source bytes.

## Canonical Artifact Set Boundary

The M18 canonical artifact set consists of six independent publication groups:

1. existing comparative benchmark artifacts;
2. canonical structured-output artifacts;
3. canonical benchmark-matrix artifacts;
4. canonical M15 export JSON artifacts;
5. canonical M15 deterministic vector-package members;
6. canonical tabular exports.

Each publication group must preserve its own:

- artifact roles;
- schema or format identities;
- producer commands;
- producer inputs;
- ordering rules;
- measurement contour;
- digest scope;
- validation results.

The groups must not be merged into one measurement surface.

The M18 canonical artifact set must not contain machine-readable M16 execution or qualification artifacts.

M16 RTL and FPGA preparation evidence remains referenced only as the current qualified implementation boundary and as input to the M19 handoff.

## Repository Layout

M18 establishes the following repository paths:

| Exact path | Role |
|---|---|
| `docs/m18_formal_schema_canonical_artifact_publication_contract.md` | M18 technical contract |
| `schemas/m18/` | repository-committed formal M18 schema set |
| `schemas/m18/frp_m18_schema_registry.json` | machine-readable schema registry |
| `artifacts/m18/structured_output/` | canonical structured-output artifacts |
| `artifacts/m18/benchmark_matrix/` | canonical benchmark-matrix artifacts |
| `artifacts/m18/m15_exports/` | canonical M15 export JSON artifacts |
| `artifacts/m18/m15_vectors/` | canonical M15 deterministic vector-package members |
| `artifacts/m18/tabular/` | canonical tabular exports |
| `artifacts/m18/manifests/` | canonical artifact and digest manifests |
| `frp_m18_canonical_artifacts.py` | M18 publication, validation, and regeneration entry point |
| `tests/test_frp_m18_canonical_artifacts.py` | dependency-independent M18 contract and artifact tests |
| `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml` | M18 qualification workflow |
| `docs/m18_formal_schema_canonical_artifact_publication_qualification.md` | post-execution qualification record |
| `docs/m18_formal_schema_canonical_artifact_publication_closure.md` | M18 qualification closure record |

The M18 implementation must not add generated caches, temporary files, local qualification outputs, or workflow evidence directories to the repository.

Temporary regeneration and validation outputs must be written outside the repository working tree.

The qualification workflow must regenerate artifacts into an isolated temporary directory and compare those bytes with the committed canonical artifact set.

The workflow must not regenerate directly over committed canonical files.

The existing canonical comparative benchmark artifacts remain at:

- `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/workload_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`.

Their M18 registry records must reference these exact paths.

No M18 copy of those six files may be represented as the authoritative source artifact.

Every path under `artifacts/m18/` must be represented in the canonical artifact manifest.

Every formal schema under `schemas/m18/` must be represented in the schema registry.

Unregistered files must fail M18 qualification.

Missing registered files must fail M18 qualification.

Duplicate schema identifiers, duplicate artifact identifiers, duplicate canonical paths, and duplicate manifest paths must fail M18 qualification.

## Formal Schema Identity Contract

Every M18 formal JSON Schema document must use:

`https://json-schema.org/draft/2020-12/schema`

The required schema-document fields are:

- `$schema`;
- `$id`;
- `title`;
- `description`;
- `type`;
- `x-frp-schema-identifier`;
- `x-frp-artifact-role`;
- `x-frp-schema-version`;
- `x-frp-producer-path`;
- `x-frp-producer-version`.

The `$schema` value must be exactly:

`https://json-schema.org/draft/2020-12/schema`

The `$id` value must use the following absolute URN form:

`urn:frp:schema:<exact-schema-identifier>`

For example:

`urn:frp:schema:frp.structured_output.v1.7.0`

The `x-frp-schema-identifier` value must contain the exact artifact schema identifier without renaming, normalization, or version substitution.

For example:

`frp.structured_output.v1.7.0`

The formal schema filename must be:

`<exact-schema-identifier>.schema.json`

For example:

`schemas/m18/frp.structured_output.v1.7.0.schema.json`

The formal schema `$id`, `x-frp-schema-identifier`, registry identifier, and filename identity must correlate exactly.

The artifact schema identifier and the formal JSON Schema `$id` are different identity fields.

An artifact may contain:

```json
"schema": "frp.structured_output.v1.7.0"
```

The corresponding formal schema must contain:

```json
"$id": "urn:frp:schema:frp.structured_output.v1.7.0",
"x-frp-schema-identifier": "frp.structured_output.v1.7.0"
```

M18 must not replace an artifact’s existing `schema` value with the formal schema `$id`.

M18 must not add the `$id` value to an existing artifact instance.

## Formal Schema Structural Requirements

Every formal schema must:

- declare the exact root JSON type;
- declare every required field;
- declare every optional field;
- distinguish integers from numbers;
- distinguish booleans from integers;
- declare string constraints where defined;
- declare array item schemas;
- declare tuple length where fixed;
- declare object-property rules;
- declare enumerated values where closed;
- declare numeric ranges where authoritative;
- declare canonical ternary values where applicable;
- declare scheduler values where applicable;
- declare digest syntax where applicable;
- declare version and milestone constants where applicable;
- declare cross-field structural prerequisites that JSON Schema can express;
- explicitly declare its additional-property policy.

An object schema must not omit its additional-property policy.

The policy must be expressed through one of:

- `additionalProperties`;
- `unevaluatedProperties`.

A schema must not insert values into an artifact.

The `default` keyword must not be used to compensate for a missing required field.

A schema must not coerce:

- strings into numbers;
- numbers into strings;
- integers into booleans;
- booleans into integers;
- encoded hardware states into canonical ternary states;
- absent values into inferred values.

Schema validation must operate on the parsed representation of the original source bytes.

The validated source artifact must remain unchanged.

## Reference Resolution

M18 schema qualification must operate without network access.

A formal schema must not require a remote schema download during validation.

The JSON Schema dialect URI identifies the dialect and does not authorize network retrieval.

Schema references must be:

- local references within the same schema document; or
- references to another schema registered under `schemas/m18/`.

Every external `$ref` target must resolve through the M18 schema registry.

Absolute filesystem paths are prohibited.

Parent-directory traversal is prohibited.

Unregistered network references are prohibited.

Unresolved references must fail qualification.

Reference cycles that prevent complete validation must fail qualification.

## Formal Schema Validation

Every M18 schema document must pass:

1. strict UTF-8 decoding;
2. strict JSON parsing;
3. JSON Schema Draft 2020-12 meta-schema validation;
4. exact `$id` validation;
5. exact identifier correlation;
6. exact registry-path correlation;
7. local-reference resolution;
8. duplicate-key rejection before schema evaluation;
9. deterministic raw-byte digest verification;
10. positive canonical-artifact validation;
11. required negative validation cases.

A schema that validates itself but does not validate its assigned canonical artifact is incomplete.

A schema that accepts a required negative fixture is invalid for M18 qualification.

A schema that rejects its assigned canonical artifact is invalid for M18 qualification.

## Embedded Artifact Identity

An artifact has embedded schema identity when its root object contains an exact `schema` field.

For an embedded-identity artifact:

- the `schema` field must be required;
- the value must be a constant equal to the registered identifier;
- the formal schema must use the same identifier under `x-frp-schema-identifier`;
- the registry must associate that identifier with one exact formal schema path;
- validation against a different schema version is prohibited.

A missing embedded schema field must fail when that field is part of the producer-defined format.

An unknown embedded schema identifier must fail qualification.

A known but unsupported schema version must fail qualification.

Automatic migration to a newer schema version is prohibited.

## Registry-Bound Artifact Identity

A legacy producer output may lack an embedded `schema` field.

M18 must not modify that artifact merely to insert an identity field.

Such an artifact may receive a registry-bound schema association only when its identity is fixed by:

- exact artifact role;
- exact source filename;
- exact canonical repository path;
- exact producer path;
- exact producer version;
- exact producer command;
- exact package membership where applicable;
- exact formal schema identifier;
- exact raw-byte digest.

The registry record must declare:

`"identity_basis": "registry_bound_exact_path_and_role"`

Registry-bound validation must not be selected from file contents alone.

Filename-only schema selection is prohibited.

Extension-only schema selection is prohibited.

Structural guessing is prohibited.

A registry-bound artifact moved to another path is a different publication instance and must not inherit canonical status automatically.

The following existing schema-free JSON roles require registry-bound treatment at M18:

- the deterministic comparative workload profile;
- the M15 deterministic reference preload;
- the M15 deterministic vector-package SHA-256 manifest.

Their existing source bytes must not be changed merely to add embedded identity.

## Formal Schema Registry

The M18 formal schema registry path is:

`schemas/m18/frp_m18_schema_registry.json`

Its schema identifier is:

`frp.m18.formal_schema_registry.v2.0.0`

Its formal schema path is:

`schemas/m18/frp.m18.formal_schema_registry.v2.0.0.schema.json`

The registry must declare:

- `schema`;
- `kind`;
- `version`;
- `milestone`;
- `json_schema_dialect`;
- `record_order`;
- `schema_count`;
- `records`;
- `registry_digest_scope`;
- `registry_content_sha256`.

The exact root identity is:

| Field | Exact value |
|---|---|
| `schema` | `frp.m18.formal_schema_registry.v2.0.0` |
| `kind` | `formal_schema_registry` |
| `version` | `2.0.0` |
| `milestone` | `M18 — Formal Schema and Canonical Artifact Publication` |
| `json_schema_dialect` | `https://json-schema.org/draft/2020-12/schema` |
| `record_order` | `schema_identifier_lexicographic` |
| `registry_digest_scope` | `canonical_compact_json_without_registry_content_sha256` |

The registry content digest must be calculated over canonical compact JSON with the `registry_content_sha256` field omitted.

The digest algorithm is SHA-256.

## Required Registry Record Fields

Every registry record must contain:

- `schema_identifier`;
- `schema_urn`;
- `schema_path`;
- `schema_version`;
- `artifact_role`;
- `artifact_format`;
- `identity_basis`;
- `identity_class`;
- `producer_path`;
- `producer_version`;
- `upstream_release`;
- `upstream_milestone`;
- `measurement_contour`;
- `canonical_artifact_paths`;
- `validation_mode`;
- `required`;
- `supported`.

The `schema_urn` value must equal:

`urn:frp:schema:<schema_identifier>`

The `schema_path` value must equal:

`schemas/m18/<schema_identifier>.schema.json`

The `canonical_artifact_paths` field must be an ordered array.

An empty `canonical_artifact_paths` array means that the schema is formally published but no repository-committed canonical artifact instance is assigned to that record.

It must not be interpreted as evidence that a canonical artifact exists.

When no executable producer path or producer version is recorded by the qualified upstream baseline:

- `producer_path` must be `null`;
- `producer_version` must be `null`;
- the exact registered source path must remain recorded through `canonical_artifact_paths`;
- producer identity must not be invented.

Registry records must be ordered lexicographically by `schema_identifier`.

Schema identifiers must be unique.

Schema URNs must be unique.

Schema paths must be unique.

A schema path must remain inside `schemas/m18/`.

## M17-Inherited Schema Identifiers

M18 inherits the following `17` exact artifact schema identifiers from the qualified M17 publication inventory.

Their identifier strings must remain unchanged.

| Schema identifier | Artifact role | Identity basis |
|---|---|---|
| `frp.benchmark.architecture_comparison.v1` | canonical comparative architecture result | embedded schema |
| `frp.benchmark.hardware_sensitivity_comparison.v1` | canonical hardware-sensitivity result | embedded schema |
| `frp.benchmark.hardware_sensitivity_cost_profile.v1` | hardware-informed sensitivity profile | embedded schema |
| `frp.benchmark.normalized_cost_profile.v1` | normalized activity-cost profile | embedded schema |
| `frp.benchmark.thermal_proxy_profile.v1` | common thermal-proxy profile | embedded schema |
| `frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0` | balanced ternary hardware-encoding map | embedded schema and kind |
| `frp.m15.cycle_exact_reference_trace.v1.7.0` | cycle-exact reference trace | embedded schema and kind |
| `frp.m15.fixed_point_interface_profile.v1.7.0` | fixed-point interface profile | embedded schema and kind |
| `frp.m15.qualification_closure_manifest.v1.7.0` | M15 qualification-closure manifest | embedded schema and kind |
| `frp.m15.quantized_reference_shadow_model.v1.7.0` | quantized reference shadow model | embedded schema and kind |
| `frp.m15.reference_rtl_equivalence_report.v1.7.0` | reference-to-RTL equivalence report | embedded schema and kind |
| `frp.m15.rtl_assertion_correlation_harness.v1.7.0` | RTL assertion-correlation harness | embedded schema and kind |
| `frp.m15.rtl_comparison_vector_package.v1.7.0` | RTL comparison vector-package descriptor | embedded schema and kind |
| `frp.m15.synthesizable_rtl_reference_core.v1.7.0` | synthesizable RTL reference-core map | embedded schema and kind |
| `frp.m15.systemverilog_testbench_interface_map.v1.7.0` | SystemVerilog testbench-interface map | embedded schema and kind |
| `frp.m3.benchmark_matrix.v1.7.0` | benchmark matrix | embedded schema and kind |
| `frp.structured_output.v1.7.0` | structured processor output | embedded schema and kind |

The M18 formal schema associated with each inherited identifier must describe its existing producer-defined structure.

M18 must not rename an inherited identifier to `v2.0.0`.

M18 publication version and artifact schema version are independent version domains.

## M18 Registry-Bound Schema Identifiers

M18 establishes formal registry-bound identities for three existing schema-free JSON artifact roles.

| Schema identifier | Artifact role | Identity basis |
|---|---|---|
| `frp.benchmark.workload_profile.v1` | deterministic comparative workload profile | registry-bound exact path and role |
| `frp.m15.reference_preload.v1.7.0` | deterministic M15 reference preload | registry-bound exact path and package role |
| `frp.m15.sha256_manifest.v1.7.0` | deterministic M15 vector-package SHA-256 manifest | registry-bound exact path and package role |

These identifiers apply only through exact registry association.

They must not be inserted into the existing source artifacts.

The deterministic comparative workload-profile association is bound to:

`benchmarks/architecture_comparison/profiles/workload_profile_v1.json`

The M15 reference-preload association is bound to:

`artifacts/m18/m15_vectors/frp_m15_reference_preload.json`

The M15 vector-package SHA-256 manifest association is bound to:

`artifacts/m18/m15_vectors/frp_m15_sha256_manifest.json`

## M18-Native Schema Identifiers

M18 establishes four native machine-readable publication and qualification identities.

| Schema identifier | Artifact role |
|---|---|
| `frp.m18.formal_schema_registry.v2.0.0` | formal schema registry |
| `frp.m18.canonical_artifact_manifest.v2.0.0` | canonical artifact manifest |
| `frp.m18.canonical_artifact_qualification.v2.0.0` | machine-readable qualification result |
| `frp.m18.canonical_artifact_self_test.v2.0.0` | deterministic self-test result |

M18-native artifacts must contain their exact schema identifier in the root `schema` field.

Their root `version` field must be:

`2.0.0`

Their root `milestone` field must be:

`M18 — Formal Schema and Canonical Artifact Publication`

## Registry Closure Count

The M18 formal schema registry must contain exactly:

`24`

records at M18 closure.

The count consists of:

- `17` M17-inherited artifact schema identifiers;
- `3` M18 registry-bound schema identifiers;
- `4` M18-native schema identifiers.

Formal non-JSON format contracts are not counted as JSON Schema records.

CSV contracts, headered-vector contracts, headered-trace contracts, and vector-text contracts must be registered separately as artifact-format contracts.

## Registry Qualification Requirements

M18 qualification must verify:

1. exact registry root identity;
2. exact registry schema identity;
3. exact record count;
4. exact record ordering;
5. exact inherited identifier set;
6. exact registry-bound identifier set;
7. exact M18-native identifier set;
8. unique schema identifiers;
9. unique schema URNs;
10. unique schema paths;
11. exact schema-path derivation;
12. exact `$id` correlation;
13. exact `x-frp-schema-identifier` correlation;
14. exact producer association;
15. exact artifact-path association;
16. exact measurement-contour association;
17. existence of every registered formal schema;
18. absence of unregistered formal schemas;
19. successful meta-schema validation;
20. exact registry content-digest recomputation.

Any failed registry requirement must fail M18 qualification.

## Canonical Structured-Output Artifact Set

M18 must commit the canonical structured-output artifact set under:

`artifacts/m18/structured_output/`

Every artifact in this set must be produced by:

`frp_prototype_v1_7_0.py`

The producer version is:

`1.7.0`

The formal schema identifier is:

`frp.structured_output.v1.7.0`

The formal schema path is:

`schemas/m18/frp.structured_output.v1.7.0.schema.json`

The measurement contour is:

`m15_implementation_mapping_matrix`

## Canonical Structured-Output Files

The required canonical structured-output set contains exactly `11` files.

| Canonical path | Artifact role | Scheduler |
|---|---|---|
| `artifacts/m18/structured_output/structured-output.json` | canonical demo structured output | `7/1` |
| `artifacts/m18/structured_output/structured-output-trace-free.json` | canonical full trace | `free` |
| `artifacts/m18/structured_output/structured-output-trace-7-1.json` | canonical full trace | `7/1` |
| `artifacts/m18/structured_output/structured-output-trace-1-7.json` | canonical full trace | `1/7` |
| `artifacts/m18/structured_output/self-test.json` | canonical default-scheduler self-test | `7/1` |
| `artifacts/m18/structured_output/self-test-free.json` | canonical free-scheduler self-test | `free` |
| `artifacts/m18/structured_output/self-test-7-1.json` | canonical 7/1-scheduler self-test | `7/1` |
| `artifacts/m18/structured_output/self-test-1-7.json` | canonical 1/7-scheduler self-test | `1/7` |
| `artifacts/m18/structured_output/scaling-8.json` | canonical 8-cell scaling output | `7/1` |
| `artifacts/m18/structured_output/scaling-16.json` | canonical 16-cell scaling output | `7/1` |
| `artifacts/m18/structured_output/scaling-32.json` | canonical 32-cell scaling output | `7/1` |

No additional file under `artifacts/m18/structured_output/` may be treated as canonical unless it is added through versioned contract and manifest change control.

## Canonical Structured-Output Producer Commands

The exact producer command for `structured-output.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1 --cells 16 --steps 64 --seed 76 --output json`

The exact producer command for `structured-output-trace-free.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler free --cells 16 --steps 64 --seed 76 --output json --include-trace`

The exact producer command for `structured-output-trace-7-1.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1 --cells 16 --steps 64 --seed 76 --output json --include-trace`

The exact producer command for `structured-output-trace-1-7.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 1/7 --cells 16 --steps 64 --seed 76 --output json --include-trace`

The exact producer command for `self-test.json` is:

`python frp_prototype_v1_7_0.py --mode self-test --cells 16 --steps 64 --seed 76 --output json`

The exact producer command for `self-test-free.json` is:

`python frp_prototype_v1_7_0.py --mode self-test --scheduler free --cells 16 --steps 64 --seed 76 --output json`

The exact producer command for `self-test-7-1.json` is:

`python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --cells 16 --steps 64 --seed 76 --output json`

The exact producer command for `self-test-1-7.json` is:

`python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --cells 16 --steps 64 --seed 76 --output json`

The exact producer command for `scaling-8.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1 --cells 8 --steps 16 --seed 76 --output json`

The exact producer command for `scaling-16.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1 --cells 16 --steps 16 --seed 76 --output json`

The exact producer command for `scaling-32.json` is:

`python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1 --cells 32 --steps 16 --seed 76 --output json`

Producer commands must be executed from the repository root.

Standard output must be captured directly as the canonical artifact bytes.

Standard error must not be merged into the canonical artifact.

## Fixed Producer Inputs

The canonical structured-output set fixes:

| Input | Exact value |
|---|---|
| producer | `frp_prototype_v1_7_0.py` |
| producer version | `1.7.0` |
| seed | `76` |
| default cell count | `16` |
| default step count | `64` |
| scaling step count | `16` |
| scheduler set | `free`, `7/1`, `1/7` |
| output format | `json` |
| trace inclusion | exact per registered artifact |

All remaining numerical inputs use the constants embedded in the versioned executable semantic reference.

Their values must be recorded in each produced artifact’s `configuration` object where that object is part of the producer-defined output.

A different seed, cell count, step count, scheduler, numerical parameter, or trace-selection flag produces a different artifact instance.

It must not be substituted for a registered canonical artifact.

## Canonical Serialization

Canonical structured-output bytes must be the direct UTF-8 representation emitted by the producer.

The required serialization properties are:

- UTF-8 encoding;
- no byte-order mark;
- two-space JSON indentation;
- lexicographically sorted object keys;
- unescaped Unicode where emitted by the producer;
- LF line endings;
- one final LF byte;
- no trailing spaces;
- no post-generation formatting;
- no field reordering;
- no value normalization.

A JSON parser and serializer round trip is not an approved regeneration method.

Canonical comparison must use raw bytes.

## Structured-Output Identity Validation

Every canonical structured-output artifact must validate:

- `schema` equals `frp.structured_output.v1.7.0`;
- `version` equals `1.7.0`;
- `milestone` equals `M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`;
- `kind` matches its registered artifact role;
- scheduler identity matches its registered producer command;
- seed, cell count, and step count match its registered producer command;
- required fields are present;
- undeclared fields are rejected according to the formal schema;
- field types are exact;
- closed enumerations contain only supported values.

The formal schema must distinguish at least:

- demo structured output;
- demo structured output with full trace;
- self-test structured output.

The distinction must be selected through existing producer-defined fields.

Structural guessing outside the formal schema is prohibited.

## Full-Trace Validation

Each canonical full-trace artifact must contain:

- `trace`;
- `cell_trace`;
- `route_events`;
- `trace_digest`;
- `cell_trace_digest`;
- `preload_digest`;
- `configuration`;
- `kernel`;
- `summary`.

For the canonical full-trace inputs:

- `trace` must contain exactly `64` tick records;
- tick values must be strictly ordered;
- tick values must not be duplicated;
- `cell_trace` must contain exactly `1024` records;
- `cell_trace` ordering must be deterministic;
- every cell identifier must be within the configured cell range;
- every state value must remain in `-1/0/1`;
- every request target state must remain in `-1/0/1`;
- route-event ordering must be deterministic;
- scheduler state must match the configured scheduler mode;
- recorded trace digests must recompute exactly.

The three full-trace fixtures must remain independent.

The `free`, `7/1`, and `1/7` scheduler traces must not be merged.

## Scheduler Validation

For `free`:

- scheduler operation remains unrestricted;
- no `7/1` or `1/7` phase interpretation may be imposed.

For `7/1`:

- seven `balance` ticks must be followed by one `commit` tick;
- scheduler counters must preserve the producer-defined relation.

For `1/7`:

- one `excite` tick must be followed by seven `neutralize` ticks;
- scheduler counters must preserve the producer-defined relation.

Scheduler names, states, counters, and phase-derived behavior must be validated as separate fields.

A scheduler name must not be inferred from tick count alone.

## Structured-Output Invariant Validation

Every applicable canonical demo and full-trace artifact must preserve:

- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- active neutral state `0`;
- canonical ternary domain `-1/0/1`;
- opposite-polarity routing through `0`;
- retained pending-route behavior;
- deterministic tick ordering;
- deterministic cell ordering;
- deterministic route-event ordering.

Every canonical self-test artifact must record:

- `status = PASS`;
- `check_count = 41`;
- all `41` named checks equal to `true`.

The self-test outputs for `free`, `7/1`, and `1/7` must remain independently generated and independently validated.

## Deterministic Regeneration

The complete `11`-file structured-output set must be generated twice into two distinct temporary directories.

Qualification must verify:

- exact filename equality;
- exact file-count equality;
- exact raw-byte equality for every corresponding file;
- exact SHA-256 equality for every corresponding file;
- exact equality with the committed canonical source bytes.

Any mismatch must fail M18 qualification.

## Canonical Benchmark-Matrix Artifact Set

M18 must commit the canonical benchmark-matrix JSON artifact at:

`artifacts/m18/benchmark_matrix/benchmark-matrix.json`

Its producer is:

`frp_prototype_v1_7_0.py`

Its producer version is:

`1.7.0`

Its exact producer command is:

`python frp_prototype_v1_7_0.py --export-benchmark-matrix`

Its schema identifier is:

`frp.m3.benchmark_matrix.v1.7.0`

Its formal schema path is:

`schemas/m18/frp.m3.benchmark_matrix.v1.7.0.schema.json`

Its measurement contour is:

`m15_implementation_mapping_matrix`

## Benchmark-Matrix Root Identity

The canonical benchmark-matrix root object must contain:

| Field | Exact value |
|---|---|
| `schema` | `frp.m3.benchmark_matrix.v1.7.0` |
| `kind` | `benchmark_matrix` |
| `version` | `1.7.0` |
| `milestone` | `M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package` |

The root `rows` field must be an array containing exactly `5` records.

The row order is authoritative and must remain unchanged.

The exact architecture order is:

1. `frp_v1_6_0_m14_floating_semantic_reference`;
2. `frp_v1_7_0_quantized_hardware_shadow`;
3. `frp_v1_7_0_cycle_exact_vector_package`;
4. `frp_v1_7_0_systemverilog_correlation_contract`;
5. `frp_v1_7_0_qualification_closure`.

Architecture identifiers must be unique.

A row must not be reordered by architecture name, field count, numeric domain, or implementation layer.

## Benchmark-Matrix Row Contracts

Every row must contain:

- `architecture`;
- `cycle_exact_integer_trace`;
- `hardware_facing_encoding`;
- `numeric_domain`.

The `frp_v1_6_0_m14_floating_semantic_reference` row additionally requires:

- `interaction_scaling`.

The `frp_v1_7_0_quantized_hardware_shadow` row additionally requires:

- `interaction_scaling`;
- `C_minus_P_sign_match`;
- `scheduler_sequence_match`;
- `state_sequence_match`.

The `frp_v1_7_0_cycle_exact_vector_package` row additionally requires:

- `vector_repeat_match`.

The `frp_v1_7_0_systemverilog_correlation_contract` row additionally requires:

- `comparison_rule`.

The `frp_v1_7_0_qualification_closure` row additionally requires:

- `artifact_layers`.

Fields belonging to one architecture row must not be inferred for another row.

Missing optional row-specific fields must remain absent in JSON.

They must not be inserted with `null`, zero, `false`, or an empty string.

## Benchmark-Matrix Value Validation

The formal schema and relation validator must verify:

- exact architecture identifiers;
- exact architecture order;
- exact row count;
- exact required fields;
- exact boolean types;
- exact integer types;
- exact numeric types;
- finite numeric values;
- exact closed-string values where defined;
- absence of undeclared fields;
- uniqueness of architecture identifiers.

The following recorded correlation values must remain exact:

- `C_minus_P_sign_match = 1.0`;
- `scheduler_sequence_match = 1.0`;
- `state_sequence_match = 1.0`;
- `vector_repeat_match = 1.0`.

The recorded qualification-closure layer count must remain:

`artifact_layers = 10`

The recorded SystemVerilog correlation rule must remain:

`actual == expected`

These values are published M15 benchmark-matrix values.

M18 must validate them without changing their meaning.

## Benchmark-Matrix Serialization

The canonical JSON bytes must be captured directly from producer standard output.

The required serialization properties are:

- UTF-8 encoding;
- no byte-order mark;
- two-space indentation;
- lexicographically sorted object keys;
- LF line endings;
- one final LF byte;
- no trailing spaces;
- no post-generation formatting.

The producer must be executed from the repository root.

Standard error must not be merged into the artifact.

## Canonical Benchmark-Matrix CSV Export

The stable tabular representation of the canonical benchmark matrix is:

`artifacts/m18/tabular/benchmark-matrix.csv`

Its registered format identifier is:

`frp.m3.benchmark_matrix.csv.v1.7.0`

The CSV is an M18-derived view of:

`artifacts/m18/benchmark_matrix/benchmark-matrix.json`

The JSON artifact remains authoritative.

The CSV must not replace the JSON artifact.

The canonical CSV column order is:

1. `architecture`;
2. `numeric_domain`;
3. `interaction_scaling`;
4. `cycle_exact_integer_trace`;
5. `hardware_facing_encoding`;
6. `C_minus_P_sign_match`;
7. `scheduler_sequence_match`;
8. `state_sequence_match`;
9. `vector_repeat_match`;
10. `comparison_rule`;
11. `artifact_layers`.

The CSV must contain:

- one header row;
- exactly five data rows;
- the same architecture order as the authoritative JSON artifact.

A JSON field absent from a benchmark-matrix row must be represented by an empty CSV field.

An absent value must not be represented as:

- `null`;
- `None`;
- `N/A`;
- `0`;
- `false`.

Boolean values must be encoded as:

- `true`;
- `false`.

Integer values must use base-10 notation.

Floating-point correlation values must preserve their producer-recorded decimal representation.

Strings must preserve their exact Unicode content.

CSV quoting must use deterministic minimal quoting.

A field containing a comma, quotation mark, CR, or LF must be quoted.

A quotation mark inside a quoted field must be doubled.

## Canonical CSV Byte Contract

The benchmark-matrix CSV must use:

- UTF-8 encoding;
- no byte-order mark;
- comma delimiter;
- double-quote quote character;
- LF record terminators;
- one final LF byte;
- no trailing spaces;
- no blank records.

The CSV generator must not depend on locale.

Decimal formatting must not depend on locale.

Column order must not be derived from object-key iteration.

The exact column order defined by this contract must be supplied explicitly.

## Benchmark-Matrix CSV Provenance

The canonical artifact manifest must record for the CSV:

- artifact identifier;
- format identifier;
- canonical path;
- source JSON path;
- source JSON raw SHA-256 digest;
- CSV raw SHA-256 digest;
- generator path;
- generator version;
- generation rule;
- column order;
- row count;
- measurement contour;
- derived-view status.

The derived-view status must be:

`observatory_compatible_upstream_derived_view`

This status identifies a deterministic FRP-published representation.

It does not change the source JSON values.

## Benchmark-Matrix Qualification

M18 qualification must:

1. generate the benchmark-matrix JSON twice;
2. compare both generated JSON files byte for byte;
3. compare the generated JSON with the committed canonical JSON;
4. validate the JSON against its formal schema;
5. validate exact row order;
6. validate exact architecture identifiers;
7. validate row-specific relations;
8. generate the CSV independently from each generated JSON file;
9. compare both generated CSV files byte for byte;
10. compare the generated CSV with the committed canonical CSV;
11. validate the CSV format contract;
12. correlate every CSV value with its source JSON value;
13. verify both raw SHA-256 digests;
14. verify manifest provenance;
15. verify measurement-contour separation.

Any mismatch must fail M18 qualification.

## Canonical Comparative Benchmark Artifact Set

M18 formally validates the six existing repository-committed comparative benchmark artifacts in place.

These artifacts must not be copied into `artifacts/m18/`.

Their existing repository paths remain authoritative.

## Comparative Benchmark Source Set

| Exact repository path | Artifact role | Schema identifier |
|---|---|---|
| `benchmarks/architecture_comparison/profiles/workload_profile_v1.json` | deterministic workload profile | `frp.benchmark.workload_profile.v1` |
| `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json` | normalized activity-cost profile | `frp.benchmark.normalized_cost_profile.v1` |
| `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json` | common thermal-proxy profile | `frp.benchmark.thermal_proxy_profile.v1` |
| `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json` | hardware-informed sensitivity profile | `frp.benchmark.hardware_sensitivity_cost_profile.v1` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json` | canonical comparative architecture result | `frp.benchmark.architecture_comparison.v1` |
| `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json` | canonical hardware-sensitivity result | `frp.benchmark.hardware_sensitivity_comparison.v1` |

The workload profile uses registry-bound identity.

The remaining five artifacts use embedded schema identity.

## Comparative Benchmark Formal Schema Paths

The required formal schema paths are:

- `schemas/m18/frp.benchmark.workload_profile.v1.schema.json`;
- `schemas/m18/frp.benchmark.normalized_cost_profile.v1.schema.json`;
- `schemas/m18/frp.benchmark.thermal_proxy_profile.v1.schema.json`;
- `schemas/m18/frp.benchmark.hardware_sensitivity_cost_profile.v1.schema.json`;
- `schemas/m18/frp.benchmark.architecture_comparison.v1.schema.json`;
- `schemas/m18/frp.benchmark.hardware_sensitivity_comparison.v1.schema.json`.

Each formal schema must validate its assigned source artifact without modifying the source bytes.

## Workload Profile Contract

The deterministic workload profile must contain exactly:

- `num_cells`;
- `command_count`;
- `seed`;
- `issue_policy`;
- `max_completion_cycles_per_command`;
- `final_cooldown_cycles`.

Its exact canonical values are:

| Field | Exact value |
|---|---:|
| `num_cells` | `16` |
| `command_count` | `256` |
| `seed` | `76` |
| `issue_policy` | `transaction_serial` |
| `max_completion_cycles_per_command` | `64` |
| `final_cooldown_cycles` | `32` |

The workload profile must not receive an inserted `schema`, `kind`, or `version` field.

Its identity remains bound to its exact path, role, formal registry association, and raw-byte digest.

## Normalized Cost Profile Contract

The normalized cost profile must preserve:

- `schema`;
- `suite_name`;
- `profile_name`;
- `cost_unit`;
- `costs`;
- `cost_profile_sha256`.

Its embedded schema identity must equal:

`frp.benchmark.normalized_cost_profile.v1`

Its suite name must equal:

`FRP Comparative Architecture Benchmark Suite`

Its profile name must equal:

`unit_event_cost_v1`

Its cost unit must equal:

`normalized_activity_unit`

The formal schema must require the complete producer-defined cost-class set.

Every cost value must be numeric, finite, and nonnegative.

The declared `cost_profile_sha256` must be validated according to its producer-defined digest scope.

## Thermal Proxy Profile Contract

The thermal proxy profile must preserve:

- `schema`;
- `suite_name`;
- `profile_name`;
- `temperature_unit`;
- `ambient_temperature_proxy`;
- `thermal_decay`;
- `thermal_gain`;
- `update_equation`;
- `thermal_profile_sha256`.

Its embedded schema identity must equal:

`frp.benchmark.thermal_proxy_profile.v1`

Its suite name must equal:

`FRP Comparative Architecture Benchmark Suite`

Its profile name must equal:

`common_rc_thermal_proxy_v1`

Its temperature unit must equal:

`normalized_temperature_proxy`

Its recorded update equation must remain:

`ambient + (temperature - ambient) * thermal_decay + normalized_cycle_cost * thermal_gain`

The declared `thermal_profile_sha256` must be validated according to its producer-defined digest scope.

M18 must not interpret the thermal proxy as a physical temperature measurement.

## Hardware-Sensitivity Profile Contract

The hardware-sensitivity profile must preserve:

- its embedded schema identity;
- its profile identity;
- its baseline bindings;
- its normalization reference;
- its reference basis;
- its scenario order;
- its coefficient order;
- its coefficient records;
- its scenario vectors;
- its evaluation contract;
- its validation contract;
- its digest contract;
- its declared profile digest.

Its embedded schema identity must equal:

`frp.benchmark.hardware_sensitivity_cost_profile.v1`

Its profile name must equal:

`literature_anchored_cmos45_sensitivity_v1`

Its scenario order must remain:

1. `lower_bound`;
2. `nominal`;
3. `upper_bound`.

The exact profile-validation command is:

`python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --output json`

The exact validator self-test command is:

`python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --self-test --output json`

Both commands must be executed from:

`benchmarks/architecture_comparison/`

## Comparative Architecture Result Producer

The authoritative producer path is:

`benchmarks/architecture_comparison/run_architecture_comparison.py`

The registered canonical producer command is:

`python run_architecture_comparison.py --workload-profile profiles/workload_profile_v1.json --cost-profile profiles/normalized_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler 7/1 --write results/reference_comparison_seed_76.json --output text`

The command must be executed from:

`benchmarks/architecture_comparison/`

Qualification regeneration must use the same inputs and scheduler while directing `--write` to an isolated temporary path.

The regenerated bytes must equal:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`

The architecture order must remain:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The result must preserve:

- `benchmark_kind = comparative_architecture_matrix`;
- `frp_reference_version = 1.7.0`;
- `frp_scheduler = 7/1`;
- `integrity.status = PASS`;
- `qualification.status = PASS`.

## Hardware-Sensitivity Result Producer

The authoritative producer path is:

`benchmarks/architecture_comparison/run_hardware_sensitivity_comparison.py`

The registered canonical producer command is:

`python run_hardware_sensitivity_comparison.py --workload-profile profiles/workload_profile_v1.json --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler 7/1 --write results/reference_comparison_seed_76_hardware_sensitivity_v1.json --output text`

The command must be executed from:

`benchmarks/architecture_comparison/`

Qualification regeneration must use the same inputs and scheduler while directing `--write` to an isolated temporary path.

The regenerated bytes must equal:

`benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`

The architecture order must remain:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The scenario order must remain:

1. `lower_bound`;
2. `nominal`;
3. `upper_bound`.

The recorded ranking for each scenario must remain:

1. `binary_clock_gated_reference`;
2. `direct_ternary_reference`;
3. `binary_synchronous_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The result must preserve:

- `benchmark_kind = hardware_informed_sensitivity_matrix`;
- `frp_reference_version = 1.7.0`;
- `frp_scheduler = 7/1`;
- `integrity.status = PASS`;
- `qualification.status = PASS`;
- `ranking_stability.ranking_stable = true`.

## Digest-Scope Separation

The comparative benchmark artifacts contain producer-declared content digests.

M18 additionally records raw-byte SHA-256 digests.

These digest classes must remain separate.

A producer-declared content digest may exclude its own digest field and use producer-defined canonical JSON serialization.

A raw-byte digest covers every committed source byte.

The following values must not be assumed equal unless their scopes are explicitly identical:

- workload content digest;
- profile content digest;
- architecture-result digest;
- comparison-package digest;
- raw-trace digest;
- raw artifact-byte digest;
- M18 manifest digest.

Every digest record must declare its scope.

A digest mismatch must fail qualification.

## Measurement-Contour Separation

The following artifacts belong to the Comparative Architecture Benchmark Suite contour:

- deterministic workload profile;
- normalized cost profile;
- thermal proxy profile;
- comparative architecture result.

The following artifacts belong to the Hardware-Informed Sensitivity Qualification contour:

- hardware-sensitivity cost profile;
- hardware-sensitivity result.

Use of the workload and thermal profiles as producer inputs does not merge the two measurement contours.

Operation count, normalized activity cost, thermal proxy, hardware-sensitivity coefficients, scheduler timing, RTL execution, FPGA preparation, and physical measurement fields must remain distinct.

## Comparative CSV Boundary

M18 does not define a flattened CSV representation for either comparative result artifact.

Their nested architecture records, qualification objects, raw-event records, scenario records, rankings, and digest bindings remain authoritative in JSON.

A flattened comparative CSV must not be created without a separately versioned tabular contract.

The canonical benchmark-matrix CSV defined by M18 does not represent the Comparative Architecture Benchmark Suite or the Hardware-Informed Sensitivity Qualification contour.

## Comparative Artifact Qualification

M18 qualification must verify:

1. all six exact source paths exist;
2. all six source files decode as strict UTF-8;
3. all six source files parse as strict JSON;
4. duplicate object keys are rejected;
5. each artifact validates against its assigned formal schema;
6. embedded schema identifiers match exactly where present;
7. registry-bound workload identity matches exactly;
8. declared digests recompute according to their declared scopes;
9. raw-byte SHA-256 digests match the M18 manifest;
10. both result artifacts regenerate byte for byte;
11. producer inputs match their committed source digests;
12. architecture order matches exactly;
13. scenario order matches exactly;
14. recorded qualification statuses remain `PASS`;
15. measurement contours remain separated;
16. repository source bytes remain unchanged.

Any mismatch must fail M18 qualification.

## Canonical M15 Export Artifact Set

M18 must commit the complete canonical M15 JSON export set under:

`artifacts/m18/m15_exports/`

The set contains exactly `10` artifacts.

Every artifact is produced by:

`frp_prototype_v1_7_0.py`

The producer version is:

`1.7.0`

The measurement contour is:

`m15_implementation_mapping_matrix`

## Canonical M15 Export Files

| Canonical path | Schema identifier |
|---|---|
| `artifacts/m18/m15_exports/fixed-point-interface-profile.json` | `frp.m15.fixed_point_interface_profile.v1.7.0` |
| `artifacts/m18/m15_exports/balanced-ternary-hardware-encoding-map.json` | `frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0` |
| `artifacts/m18/m15_exports/quantized-reference-shadow-model.json` | `frp.m15.quantized_reference_shadow_model.v1.7.0` |
| `artifacts/m18/m15_exports/cycle-exact-reference-trace.json` | `frp.m15.cycle_exact_reference_trace.v1.7.0` |
| `artifacts/m18/m15_exports/rtl-comparison-vector-package.json` | `frp.m15.rtl_comparison_vector_package.v1.7.0` |
| `artifacts/m18/m15_exports/systemverilog-testbench-interface-map.json` | `frp.m15.systemverilog_testbench_interface_map.v1.7.0` |
| `artifacts/m18/m15_exports/synthesizable-rtl-reference-core.json` | `frp.m15.synthesizable_rtl_reference_core.v1.7.0` |
| `artifacts/m18/m15_exports/rtl-assertion-correlation-harness.json` | `frp.m15.rtl_assertion_correlation_harness.v1.7.0` |
| `artifacts/m18/m15_exports/reference-rtl-equivalence-report.json` | `frp.m15.reference_rtl_equivalence_report.v1.7.0` |
| `artifacts/m18/m15_exports/qualification-closure-manifest.json` | `frp.m15.qualification_closure_manifest.v1.7.0` |

Every schema identifier must remain at version `v1.7.0`.

M18 must not rename these artifact schemas to `v2.0.0`.

## Canonical M15 Export Producer Commands

The exact producer commands are:

| Canonical filename | Exact producer command |
|---|---|
| `fixed-point-interface-profile.json` | `python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile` |
| `balanced-ternary-hardware-encoding-map.json` | `python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map` |
| `quantized-reference-shadow-model.json` | `python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model` |
| `cycle-exact-reference-trace.json` | `python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace` |
| `rtl-comparison-vector-package.json` | `python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package` |
| `systemverilog-testbench-interface-map.json` | `python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map` |
| `synthesizable-rtl-reference-core.json` | `python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core` |
| `rtl-assertion-correlation-harness.json` | `python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness` |
| `reference-rtl-equivalence-report.json` | `python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report` |
| `qualification-closure-manifest.json` | `python frp_prototype_v1_7_0.py --export-qualification-closure-manifest` |

Every command must be executed from the repository root.

Standard output must be captured directly as the canonical artifact bytes.

Standard error must not be merged into the canonical artifact.

## Canonical M15 Export Root Identity

Every canonical M15 export must contain:

- `schema`;
- `kind`;
- `version`;
- `milestone`.

The root `schema` value must match the schema identifier registered for that exact path.

The root `version` value must equal:

`1.7.0`

The root `milestone` value must equal:

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

The root `kind` value must match the registered artifact role.

A schema, kind, version, or milestone mismatch must fail qualification.

## Formal M15 Export Schema Paths

The required formal schema paths are:

- `schemas/m18/frp.m15.fixed_point_interface_profile.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.quantized_reference_shadow_model.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.cycle_exact_reference_trace.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.rtl_comparison_vector_package.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.systemverilog_testbench_interface_map.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.synthesizable_rtl_reference_core.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.rtl_assertion_correlation_harness.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.reference_rtl_equivalence_report.v1.7.0.schema.json`;
- `schemas/m18/frp.m15.qualification_closure_manifest.v1.7.0.schema.json`.

Each schema must validate only its assigned artifact role.

A structurally similar M15 export must not validate under the wrong schema.

## Fixed-Point Interface Validation

The fixed-point interface profile must preserve:

- `fixed_point_topology_sum_exact = true`;
- `fixed_point_thermal_sum_exact = true`;
- exact scalar formats;
- exact phase format;
- exact gamma format;
- exact state-encoding references;
- exact thermal fixed-point profile;
- exact topology fixed-point profile;
- exact inherited-boundary record.

Fixed-point values must remain distinct from floating-point values.

Fixed-point integer words must not be converted into decimal approximations inside the canonical artifact.

## Balanced Ternary Encoding Validation

The balanced ternary hardware-encoding map must preserve the exact canonical state association:

| Canonical state | Packed code | Integer code |
|---:|---|---:|
| `-1` | `11` | `3` |
| `0` | `00` | `0` |
| `1` | `01` | `1` |

The reserved packed-state code must remain:

| Role | Packed code | Integer code |
|---|---|---:|
| reserved | `10` | `2` |

The reserved code is not a fourth processor state.

The formal schema and relation validator must reject:

- a canonical state outside `-1/0/1`;
- duplicate packed-state codes;
- duplicate integer codes;
- use of the reserved code as a canonical state;
- a missing active neutral state;
- a changed state-to-code association.

Scheduler-mode and scheduler-state encodings must remain separate from processor-state encoding.

## Canonical State-Notation Gate

Canonical processor-state values and state-transition rules must use:

`-1/0/1`

The positive canonical state must be written as:

`1`

Before `rtl-assertion-correlation-harness.json` is promoted to canonical status, its producer-defined direct-transition rule text must use:

- `previous_state = -1 and current_state = 1 is a failure`;
- `previous_state = 1 and current_state = -1 is a failure`;
- `valid opposite-polarity migration requires intermediate state 0`.

This is a notation correction.

It does not change the prohibited-transition relation.

The notation gate applies to processor-state values and processor-state transition rules.

It does not apply to arithmetic expressions such as:

- `2i+1`;
- `N+1`.

A canonical artifact containing noncanonical positive-state notation in a processor-state value or transition rule must fail qualification.

## Quantized Shadow and Cycle-Exact Trace Validation

The quantized reference shadow model and cycle-exact reference trace must preserve:

- exact configuration;
- exact preload;
- exact scheduler identity;
- exact trace ordering;
- exact route-event ordering;
- exact state ordering;
- exact counter values;
- exact fixed-point values;
- exact summary values;
- exact digest relations.

The cycle-exact trace must contain exactly:

- `64` tick records;
- `27` route-event records for the fixed canonical producer inputs.

Every tick value must be strictly ordered.

Every canonical state and request target must remain in `-1/0/1`.

The summary must preserve:

- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- `pending_route_count_final = 0`;
- `fixed_point_topology_sum_exact = true`;
- `fixed_point_thermal_sum_exact = true`;
- `scheduler_counts_valid = true`.

The quantized shadow `trace_digest` and `cell_trace_digest` must recompute exactly.

## RTL Comparison Vector-Package Descriptor Validation

The RTL comparison vector-package descriptor must preserve:

- `vector_classes`;
- `manifest`;
- `deterministic_package_digest`.

The manifest must declare exactly:

`10`

package members.

Every declared package filename, byte length, and SHA-256 digest must correlate with the committed canonical vector-package member.

The deterministic package digest must recompute according to its producer-defined scope.

The descriptor is not a substitute for the committed vector-package members.

## Interface, Core, and Assertion Validation

The SystemVerilog testbench-interface map must preserve:

- exact parameters;
- exact execution inputs;
- exact verification-stimulus inputs;
- exact comparison outputs;
- exact vector-replay order.

The synthesizable RTL reference-core map must preserve:

- exact kernel requirements;
- exact planned RTL file identities;
- exact tick-execution order.

The RTL assertion-correlation harness must preserve:

- `assertion_count = 13`;
- scheduler modes `free`, `7/1`, and `1/7`;
- exact comparison rule;
- direct-transition prohibitions;
- active-neutral routing requirements;
- exact assertion identities.

These JSON artifacts describe M15 mapping and correlation contracts.

They do not replace M16 RTL source files or M16 execution evidence.

## Equivalence and Closure Validation

The reference-to-RTL equivalence report must preserve three independent layers:

- floating reference to quantized shadow;
- quantized shadow deterministic replay;
- RTL exact-integer comparison contract.

The exact RTL comparison rule must remain:

`actual == expected`

The deterministic replay values must remain:

- `shadow_replay_trace_match = 1.0`;
- `shadow_replay_cell_trace_match = 1.0`;
- `shadow_replay_state_match = 1.0`;
- `shadow_replay_scheduler_match = 1.0`;
- `shadow_replay_pending_route_match = 1.0`;
- `shadow_replay_counter_match = 1.0`.

The qualification-closure manifest must preserve:

- `status = PASS`;
- exactly `10` artifact layers;
- all declared checks equal to `true`;
- exact semantic-correlation values;
- exact deterministic-replay values;
- exact vector-manifest membership.

Qualification statuses and correlation values must be validated as recorded upstream values.

M18 must not recalculate them under a different measurement contour.

## Canonical M15 Export Serialization

Every canonical M15 export must use the direct producer serialization:

- UTF-8 encoding;
- no byte-order mark;
- two-space indentation;
- lexicographically sorted object keys;
- LF line endings;
- one final LF byte;
- no trailing spaces;
- no post-generation formatting.

A parsed and reserialized copy is not the canonical producer output.

## Canonical M15 Export Qualification

The complete `10`-file export set must be generated twice into separate temporary directories.

M18 qualification must verify:

1. exact file count;
2. exact canonical filenames;
3. exact root identities;
4. formal schema validation;
5. exact artifact-role association;
6. exact cross-artifact relations;
7. exact declared-digest recomputation;
8. exact raw-byte SHA-256 digests;
9. exact byte equality between both generations;
10. exact byte equality with the committed canonical files;
11. exact manifest association;
12. canonical `-1/0/1` notation;
13. M15 measurement-contour assignment;
14. separation from M16 machine-readable evidence;
15. unchanged repository state after qualification.

Any mismatch must fail M18 qualification.

## Canonical M15 Deterministic Vector Package

M18 promotes one deterministic M15 vector package into the repository-committed canonical artifact set.

The canonical package directory is:

`artifacts/m18/m15_vectors/`

The exact producer command is:

`python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir artifacts/m18/m15_vectors`

The producer invocation uses the inherited deterministic defaults:

- `cells = 16`;
- `steps = 64`;
- `seed = 76`;
- `scheduler = 7/1`;
- `transition_fraction = 0.25`;
- `hierarchy_depth = 4`;
- `request_lanes = 4`.

The committed package must contain exactly ten files and no additional members.

### Exact Package Members

The canonical package-member order is lexicographic by filename.

| Order | Package member | Format identity or registered role |
|---:|---|---|
| 1 | `frp_m15_cell_trace.vec` | `frp.m15.vector.v1`, `cell_trace` |
| 2 | `frp_m15_full_correlation_vectors.vec` | `frp.m15.vector.v1`, `full_correlation_vectors` |
| 3 | `frp_m15_kernel_vectors.vec` | `frp.m15.vector.v1`, `kernel_transition_vectors` |
| 4 | `frp_m15_pending_routes.trace` | `frp.m15.vector.v1`, `pending_routes` |
| 5 | `frp_m15_reference_preload.json` | registry-bound `frp.m15.reference_preload.v1.7.0` |
| 6 | `frp_m15_scheduler_1_7_vectors.vec` | `frp.m15.vector.v1`, `scheduler_1_7_vectors` |
| 7 | `frp_m15_scheduler_7_1_vectors.vec` | `frp.m15.vector.v1`, `scheduler_7_1_vectors` |
| 8 | `frp_m15_scheduler_free_vectors.vec` | `frp.m15.vector.v1`, `scheduler_free_vectors` |
| 9 | `frp_m15_sha256_manifest.json` | registry-bound `frp.m15.sha256_manifest.v1.7.0` |
| 10 | `frp_m15_trig_lut_q30.vec` | deterministic Q30 trigonometric lookup-table role |

The exact member set is closed.

A missing member, duplicate member, unexpected member, renamed member, or member outside the canonical package directory fails M18 qualification.

### Headered Vector and Trace Contract

The following seven members use the inherited headered vector format:

- `frp_m15_cell_trace.vec`;
- `frp_m15_full_correlation_vectors.vec`;
- `frp_m15_kernel_vectors.vec`;
- `frp_m15_pending_routes.trace`;
- `frp_m15_scheduler_1_7_vectors.vec`;
- `frp_m15_scheduler_7_1_vectors.vec`;
- `frp_m15_scheduler_free_vectors.vec`.

Each headered member must declare:

- `format_version = "frp.m15.vector.v1"`;
- `frp_version = "1.7.0"`;
- the exact M15 milestone;
- its exact `trace_kind`;
- `cells = 16`;
- `hierarchy_depth = 4`;
- `request_lanes = 4`;
- `transition_fraction = 0.25`;
- its exact scheduler mode;
- `scalar_format = "S32Q16"`.

The scheduler bindings are:

| Package member | Required scheduler mode |
|---|---|
| `frp_m15_kernel_vectors.vec` | `free` |
| `frp_m15_pending_routes.trace` | `free` |
| `frp_m15_scheduler_free_vectors.vec` | `free` |
| `frp_m15_scheduler_7_1_vectors.vec` | `7/1` |
| `frp_m15_scheduler_1_7_vectors.vec` | `1/7` |
| `frp_m15_full_correlation_vectors.vec` | `7/1` |
| `frp_m15_cell_trace.vec` | `7/1` |

The header parser must reject:

- an unknown format version;
- an unknown trace kind;
- a scheduler mismatch;
- duplicate header fields;
- malformed numeric fields;
- an invalid canonical ternary value;
- an invalid packed-state code;
- malformed data-column counts;
- inconsistent tick or record ordering.

### Canonical Ternary Validation

All decoded processor states must belong to:

`{-1, 0, 1}`

The active neutral state is:

`0`

The only valid two-leg opposite-polarity routes are:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

The canonical positive processor state must be displayed as:

`1`

The notation `+1` must not be introduced as the canonical positive-state label.

Encoded state values must remain bound to the M15 balanced-ternary hardware encoding map and must not be interpreted independently.

### Scheduler Validation

The scheduler-specific vectors must remain distinct.

The required scheduler semantics are:

- `free`: unrestricted scheduler operation;
- `7/1`: seven `balance` ticks followed by one `commit` tick;
- `1/7`: one `excite` tick followed by seven `neutralize` ticks.

The validator must check the declared scheduler mode, scheduler state sequence, scheduler counters, request acceptance, request rejection, pending-route retention, and pending-route completion without redefining processor semantics.

Scheduler-specific members must not be substituted for one another.

### Reference Preload Contract

`frp_m15_reference_preload.json` is identified through its exact filename, package position, producer, enclosing manifests, and registry association.

Its source bytes must not be modified merely to embed a schema identifier.

Its exact root fields are:

- `cells`;
- `frequency_current_q16`;
- `frequency_target_q16`;
- `gamma_noise_state_q16`;
- `gamma_noise_target_q16`;
- `heat_q16`;
- `phase_words`;
- `scheduler`;
- `seed`;
- `states`;
- `states_packed_hex`.

The preload validator must check:

- `cells = 16`;
- `seed = 76`;
- `scheduler = "7/1"`;
- exact array lengths equal to `cells`;
- integer types for all fixed-point and phase values;
- canonical ternary membership for every item in `states`;
- consistency between `states` and `states_packed_hex`;
- valid M15 hardware encoding for every packed state;
- absence of unknown root fields under the registered formal schema.

The preload remains deterministic input evidence.

It is not an independently executable processor definition.

### Trigonometric Lookup-Table Contract

`frp_m15_trig_lut_q30.vec` must preserve the producer-defined text format.

Its header must declare:

- `FRP v1.7.0 M15 deterministic trigonometric lookup table`;
- `entries = 4096`;
- `format = index | sin_q30`.

The data section must contain exactly `4096` ordered entries.

The index sequence must be contiguous from:

`0000`

through:

`0FFF`

Each value must be a signed integer in the declared Q30 representation.

The validator must not replace the published lookup-table values with recomputed floating-point approximations.

A recomputation may be reported only as an Observatory-derived or qualification-derived comparison and must remain separate from the published values.

### Internal SHA-256 Manifest Contract

`frp_m15_sha256_manifest.json` must contain exactly nine entries.

It must bind every non-manifest package member and must not bind itself.

Self-exclusion prevents a circular digest dependency.

The exact manifest keys are:

- `frp_m15_cell_trace.vec`;
- `frp_m15_full_correlation_vectors.vec`;
- `frp_m15_kernel_vectors.vec`;
- `frp_m15_pending_routes.trace`;
- `frp_m15_reference_preload.json`;
- `frp_m15_scheduler_1_7_vectors.vec`;
- `frp_m15_scheduler_7_1_vectors.vec`;
- `frp_m15_scheduler_free_vectors.vec`;
- `frp_m15_trig_lut_q30.vec`.

Each manifest value must be a lowercase 64-character hexadecimal SHA-256 digest.

Every declared digest must equal the SHA-256 digest calculated directly from the committed raw bytes of the corresponding member.

The manifest must not normalize line endings, whitespace, JSON formatting, or text encoding before digest calculation.

### Package-Descriptor Binding

The canonical export:

`artifacts/m18/m15_exports/rtl-comparison-vector-package.json`

must bind the committed vector package.

Its exact schema identifier is:

`frp.m15.rtl_comparison_vector_package.v1.7.0`

Its exact kind is:

`rtl_comparison_vector_package`

Its `manifest.file_count` must equal:

`10`

Its `manifest.files` array must list the ten members in lexicographic filename order.

For every package member, the descriptor must record:

- exact filename;
- exact byte size;
- SHA-256 digest calculated from raw bytes.

The descriptor-level deterministic package digest for the inherited producer configuration is:

`703dd4b56f4b34289a2c5bc5521ad4ddc3113bdec8c38238c3244c69cb4d58df`

The committed package, the internal SHA-256 manifest, and the JSON package descriptor must agree exactly.

### Independent Regeneration

M18 qualification must generate the package twice in separate temporary directories using identical producer arguments.

The qualification process must compare:

- exact filename sets;
- exact file counts;
- exact byte lengths;
- exact raw bytes;
- per-member SHA-256 digests;
- internal manifest contents;
- descriptor manifest contents;
- deterministic package digest.

The two regenerated directories must be byte-identical.

The committed canonical directory must be byte-identical to both regenerated directories.

### Read-Only Publication Boundary

The canonical M15 vector package is published reference evidence.

Consumers may:

- read it;
- parse it;
- validate it;
- replay it through explicitly qualified consumers;
- compare it with independently generated results;
- create clearly labelled derived views.

Consumers must not:

- modify a package member;
- rewrite formatting;
- normalize source bytes;
- replace a published value;
- reinterpret the ternary encoding;
- merge scheduler modes;
- treat the package as new processor semantics;
- infer physical-chip evidence from the package.

### Qualification Requirements

M18 qualification must prove:

1. the exact ten-member package is committed;
2. no unexpected member exists;
3. all headered members use `frp.m15.vector.v1`;
4. all trace kinds match their registered roles;
5. all scheduler bindings are correct;
6. all ternary states belong to `{-1, 0, 1}`;
7. packed states match the registered hardware encoding;
8. preload fields and array lengths are valid;
9. the trigonometric lookup table contains exactly `4096` ordered entries;
10. every internal manifest digest matches raw committed bytes;
11. every descriptor byte size and digest matches raw committed bytes;
12. two independent regenerations are byte-identical;
13. the committed package is byte-identical to both regenerations;
14. the deterministic package digest matches the published descriptor;
15. the original M15 producer semantics remain unchanged.

Any mismatch fails M18 qualification.

## Canonical Artifact Manifest

M18 publishes one deterministic machine-readable manifest for the complete canonical artifact set.

The exact manifest path is:

`artifacts/m18/manifests/canonical-artifact-manifest.json`

The exact schema identifier is:

`frp.m18.canonical_artifact_manifest.v2.0.0`

The exact artifact kind is:

`canonical_artifact_manifest`

The manifest is generated by:

`frp_m18_canonical_artifacts.py`

The manifest records repository-committed artifacts without modifying, normalizing, or replacing their source bytes.

### Manifest Root Contract

The manifest root must contain:

- `schema`;
- `kind`;
- `version`;
- `milestone`;
- `producer`;
- `producer_version`;
- `upstream_release`;
- `artifact_order`;
- `digest_algorithm`;
- `digest_scope`;
- `artifact_count`;
- `artifact_set_sha256`;
- `artifacts`.

The exact root identity values are:

| Field | Required value |
|---|---|
| `schema` | `frp.m18.canonical_artifact_manifest.v2.0.0` |
| `kind` | `canonical_artifact_manifest` |
| `version` | `2.0.0` |
| `milestone` | `M18 — Formal Schema and Canonical Artifact Publication` |
| `producer` | `frp_m18_canonical_artifacts.py` |
| `producer_version` | `2.0.0` |
| `upstream_release` | `FRP v1.8.0 / M16` |
| `artifact_order` | `repository_path_lexicographic` |
| `digest_algorithm` | `sha256` |
| `digest_scope` | `raw_bytes` |

`artifact_count` must equal the exact number of records in `artifacts`.

The manifest must not contain a generation timestamp.

Timestamp exclusion preserves deterministic regeneration.

### Closed Manifest Scope

The manifest must bind exactly these publication classes:

1. the M18 supported-schema registry;
2. every formal JSON Schema referenced by the registry;
3. the eleven canonical structured-output artifacts;
4. the canonical benchmark-matrix JSON artifact;
5. the canonical benchmark-matrix CSV artifact;
6. the six committed comparative benchmark artifacts;
7. the ten canonical M15 JSON exports;
8. the ten canonical M15 deterministic vector-package members.

Qualification reports, workflow logs, temporary files, cache files, generated comparison directories, downstream copies, and Observatory-derived views must not appear in the canonical artifact manifest.

The manifest must not bind itself.

Its own raw-byte digest is recorded by the separate M18 qualification record.

### Schema-Set Inclusion

The manifest must include:

`schemas/m18/frp_m18_schema_registry.json`

It must also include every unique `formal_schema_path` declared by the supported-schema registry.

A registry record without a manifest-bound formal schema fails qualification.

A manifest-bound formal schema without a registry record fails qualification.

The schema registry document and the formal schema that validates that registry are separate files.

The registry must not identify itself as its own formal schema path.

### Structured-Output Inclusion

The manifest must include exactly:

- `artifacts/m18/structured_output/structured-output.json`;
- `artifacts/m18/structured_output/trace-free.json`;
- `artifacts/m18/structured_output/trace-7-1.json`;
- `artifacts/m18/structured_output/trace-1-7.json`;
- `artifacts/m18/structured_output/self-test-default.json`;
- `artifacts/m18/structured_output/self-test-free.json`;
- `artifacts/m18/structured_output/self-test-7-1.json`;
- `artifacts/m18/structured_output/self-test-1-7.json`;
- `artifacts/m18/structured_output/scaling-8.json`;
- `artifacts/m18/structured_output/scaling-16.json`;
- `artifacts/m18/structured_output/scaling-32.json`.

Every structured-output record must bind:

`frp.structured_output.v1.7.0`

### Benchmark-Matrix Inclusion

The manifest must include exactly:

- `artifacts/m18/benchmark_matrix/benchmark-matrix.json`;
- `artifacts/m18/tabular/benchmark-matrix.csv`.

The JSON artifact must bind:

`frp.m3.benchmark_matrix.v1.7.0`

The CSV artifact must bind the registered format identity:

`frp.m3.benchmark_matrix.csv.v1.7.0`

The JSON and CSV records must remain separate manifest entries.

### Comparative Benchmark Inclusion

The manifest must bind the six existing comparative benchmark artifacts at their source repository paths.

The artifacts must not be copied into `artifacts/m18/`.

The exact source artifacts are:

- `benchmarks/architecture_comparison/workload_profile_v1.json`;
- `benchmarks/architecture_comparison/normalized_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/thermal_proxy_profile_v1.json`;
- `benchmarks/architecture_comparison/hardware_sensitivity_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`.

Each comparative record must retain its own exact schema or registry-bound identity.

The comparative measurement contour must remain distinct from structured output, M3 matrices, M15 mapping evidence, RTL execution, FPGA preparation, and physical measurement.

### M15 Export Inclusion

The manifest must include the ten exact files under:

`artifacts/m18/m15_exports/`

Each record must bind the exact M15 schema identifier declared by its source artifact.

The vector-package descriptor and the ten vector-package members must remain separate records.

### M15 Vector-Package Inclusion

The manifest must include the ten exact files under:

`artifacts/m18/m15_vectors/`

The seven headered vector and trace files must bind:

`frp.m15.vector.v1`

The reference preload must use the registry-bound identity:

`frp.m15.reference_preload.v1.7.0`

The internal SHA-256 manifest must use the registry-bound identity:

`frp.m15.sha256_manifest.v1.7.0`

The trigonometric lookup table must use its exact registered package role without an invented embedded schema identifier.

### Artifact Record Contract

Every `artifacts` entry must contain:

- `repository_path`;
- `filename`;
- `artifact_class`;
- `format`;
- `schema_identifier`;
- `identification_basis`;
- `producer`;
- `producer_version`;
- `measurement_contour`;
- `byte_length`;
- `sha256`;
- `canonical`;
- `mutable`.

The optional field is:

- `producer_command`.

No additional record fields are permitted unless the manifest schema is versioned explicitly.

### Repository Path Contract

`repository_path` must:

- be relative to the repository root;
- use `/` as the separator;
- identify one existing regular file;
- contain no empty path component;
- contain no `.` component;
- contain no `..` component;
- contain no backslash;
- contain no leading `/`;
- contain no trailing `/`;
- match the actual case-sensitive repository path.

Symbolic links must not be accepted as canonical manifest targets.

Two records must not resolve to the same repository path.

`filename` must equal the final component of `repository_path`.

### Artifact Class Vocabulary

`artifact_class` must be one of:

- `formal_schema`;
- `schema_registry`;
- `structured_output`;
- `benchmark_matrix_json`;
- `benchmark_matrix_csv`;
- `comparative_benchmark`;
- `m15_export`;
- `m15_vector_member`.

Artifact classes must not be merged or silently renamed.

### Format Vocabulary

`format` must be one of:

- `json`;
- `csv`;
- `headered_vector`;
- `headered_trace`;
- `vector_text`.

The declared format must match the source bytes and registered artifact role.

### Identification Basis Vocabulary

`identification_basis` must be one of:

- `embedded_schema`;
- `registry_binding`;
- `format_header`;
- `package_role`.

An artifact with an embedded `schema` field must use:

`embedded_schema`

A schema-free JSON artifact associated through the registry must use:

`registry_binding`

A headered vector or trace must use:

`format_header`

The trigonometric lookup-table member must use:

`package_role`

### Schema Identifier Rules

`schema_identifier` must contain the exact embedded or registry-bound identifier when one exists.

The value must be `null` only when the artifact is identified solely through a package role that has no formal schema identifier.

A missing known identifier fails qualification.

An invented identifier fails qualification.

An identifier that differs only by capitalization, punctuation, milestone, or version is a different identifier and fails qualification.

### Producer Binding

`producer` must identify the exact repository producer.

`producer_version` must identify the exact producer version.

`producer_command`, when present, must reproduce the corresponding artifact using the contract-defined canonical arguments.

Artifacts generated by different commands must remain separate records even when they share a schema identifier.

### Measurement-Contour Vocabulary

`measurement_contour` must be one of the exact registered contour values established by the M18 schema registry.

The manifest must not merge:

- historical transition benchmark;
- structured-output benchmark;
- M3 benchmark matrix;
- transition-pressure and feedback-stress matrix;
- thermal-survival and stability-boundary matrix;
- hierarchical scaling and hotspot-containment matrix;
- M15 implementation mapping;
- comparative architecture benchmark;
- hardware-informed sensitivity qualification;
- M16 RTL qualification;
- M16 FPGA preparation qualification.

Operation count, thermal proxy, transition pressure, `heat_peak`, scheduler timing, latency, throughput, RTL execution, FPGA preparation, and physical measurements remain distinct quantities.

### Raw-Byte Digest Contract

`byte_length` must equal the exact length of the committed file in bytes.

`sha256` must equal the lowercase hexadecimal SHA-256 digest of those exact raw bytes.

Digest calculation must occur before:

- JSON parsing;
- CSV parsing;
- newline conversion;
- Unicode normalization;
- whitespace normalization;
- numeric conversion;
- field reordering;
- any derived representation.

The source file must remain unchanged after digest calculation.

### Canonical and Mutability Flags

Every manifest record must declare:

`canonical = true`

Every manifest record must declare:

`mutable = false`

These flags describe the committed M18 publication instance.

They do not prevent a future explicitly versioned release from publishing a different artifact set.

A future artifact change requires a new qualified manifest and must not silently alter a released historical manifest.

### Deterministic Artifact-Set Digest

`artifact_set_sha256` binds the ordered manifest records without creating a self-digest cycle.

Records must first be ordered by `repository_path` using Unicode code-point order.

For every ordered record, the producer must append:

`repository_path + NUL + sha256 + NUL + decimal byte_length + LF`

Where:

- `NUL` is the single byte `0x00`;
- `LF` is the single byte `0x0A`;
- `decimal byte_length` contains ASCII decimal digits without leading zeros;
- all text components are encoded as UTF-8.

The SHA-256 digest of the complete concatenated byte sequence is stored as:

`artifact_set_sha256`

The empty record set is invalid.

### Ordering Contract

The `artifacts` array must be ordered lexicographically by `repository_path`.

The order must be deterministic and independent of:

- filesystem enumeration order;
- operating system;
- locale;
- generation time;
- JSON object insertion order.

An unordered or differently ordered array fails qualification.

### Manifest Serialization

The manifest must be serialized as UTF-8 JSON with:

- two-space indentation;
- lexicographically sorted object keys;
- no trailing whitespace;
- one final LF byte;
- no byte-order mark;
- no non-finite numeric values.

Repeated generation from unchanged source bytes must produce a byte-identical manifest.

### Cross-Registry Validation

Every manifest record must be checked against the supported-schema registry.

The validator must confirm:

- schema or format identity;
- identification basis;
- artifact format;
- producer path;
- producer version;
- measurement contour;
- supported artifact role;
- permitted repository path;
- applicable Observatory modes.

A recognized schema with an incompatible artifact role fails qualification.

An unregistered schema or format identity fails qualification.

### Manifest Regeneration

The M18 producer must generate the manifest twice from the same committed artifact set.

The two generated manifests must be byte-identical.

The committed manifest must be byte-identical to both generated manifests.

The validation process must not repair or rewrite an artifact to make it match the manifest.

### Manifest Change Control

Any change to a manifest-bound source file requires regeneration of:

- its byte length;
- its SHA-256 digest;
- `artifact_set_sha256`;
- the committed canonical artifact manifest;
- the M18 qualification record.

Digest values must not be edited manually to conceal source-byte changes.

A source-byte change without corresponding qualification evidence fails M18 closure.

### Manifest Qualification Requirements

M18 qualification must prove:

1. the manifest validates against its formal schema;
2. the exact root identity is present;
3. every required publication class is represented;
4. every required artifact path exists;
5. no unexpected artifact record exists;
6. every path is safe, relative, unique, and case-exact;
7. every target is a regular file;
8. every filename matches its repository path;
9. every schema or format identity is registered;
10. every identification basis is correct;
11. every producer binding is correct;
12. every measurement contour is preserved;
13. every byte length matches the committed raw bytes;
14. every SHA-256 digest matches the committed raw bytes;
15. every record declares `canonical = true`;
16. every record declares `mutable = false`;
17. the record order is lexicographic by repository path;
18. `artifact_count` equals the actual record count;
19. `artifact_set_sha256` is reproduced exactly;
20. two independent manifest generations are byte-identical;
21. the committed manifest is byte-identical to both regenerations;
22. the manifest does not bind itself;
23. no timestamp or environment-dependent value affects serialization;
24. no source artifact is modified during validation.

Any manifest mismatch fails M18 qualification.

## Canonical Artifact Manifest

M18 publishes one deterministic machine-readable manifest for the complete canonical artifact set.

The exact manifest path is:

`artifacts/m18/manifests/canonical-artifact-manifest.json`

The exact schema identifier is:

`frp.m18.canonical_artifact_manifest.v2.0.0`

The exact artifact kind is:

`canonical_artifact_manifest`

The manifest is generated by:

`frp_m18_canonical_artifacts.py`

The manifest records repository-committed artifacts without modifying, normalizing, or replacing their source bytes.

### Manifest Root Contract

The manifest root must contain:

- `schema`;
- `kind`;
- `version`;
- `milestone`;
- `producer`;
- `producer_version`;
- `upstream_release`;
- `artifact_order`;
- `digest_algorithm`;
- `digest_scope`;
- `artifact_count`;
- `artifact_set_sha256`;
- `artifacts`.

The exact root identity values are:

| Field | Required value |
|---|---|
| `schema` | `frp.m18.canonical_artifact_manifest.v2.0.0` |
| `kind` | `canonical_artifact_manifest` |
| `version` | `2.0.0` |
| `milestone` | `M18 — Formal Schema and Canonical Artifact Publication` |
| `producer` | `frp_m18_canonical_artifacts.py` |
| `producer_version` | `2.0.0` |
| `upstream_release` | `FRP v1.8.0 / M16` |
| `artifact_order` | `repository_path_lexicographic` |
| `digest_algorithm` | `sha256` |
| `digest_scope` | `raw_bytes` |

`artifact_count` must equal the exact number of records in `artifacts`.

The manifest must not contain a generation timestamp.

Timestamp exclusion preserves deterministic regeneration.

### Closed Manifest Scope

The manifest must bind exactly these publication classes:

1. the M18 supported-schema registry;
2. every formal JSON Schema referenced by the registry;
3. the eleven canonical structured-output artifacts;
4. the canonical benchmark-matrix JSON artifact;
5. the canonical benchmark-matrix CSV artifact;
6. the six committed comparative benchmark artifacts;
7. the ten canonical M15 JSON exports;
8. the ten canonical M15 deterministic vector-package members.

Qualification reports, workflow logs, temporary files, cache files, generated comparison directories, downstream copies, and Observatory-derived views must not appear in the canonical artifact manifest.

The manifest must not bind itself.

Its own raw-byte digest is recorded by the separate M18 qualification record.

### Schema-Set Inclusion

The manifest must include:

`schemas/m18/frp_m18_schema_registry.json`

It must also include every unique `formal_schema_path` declared by the supported-schema registry.

A registry record without a manifest-bound formal schema fails qualification.

A manifest-bound formal schema without a registry record fails qualification.

The schema registry document and the formal schema that validates that registry are separate files.

The registry must not identify itself as its own formal schema path.

### Structured-Output Inclusion

The manifest must include exactly:

- `artifacts/m18/structured_output/structured-output.json`;
- `artifacts/m18/structured_output/trace-free.json`;
- `artifacts/m18/structured_output/trace-7-1.json`;
- `artifacts/m18/structured_output/trace-1-7.json`;
- `artifacts/m18/structured_output/self-test-default.json`;
- `artifacts/m18/structured_output/self-test-free.json`;
- `artifacts/m18/structured_output/self-test-7-1.json`;
- `artifacts/m18/structured_output/self-test-1-7.json`;
- `artifacts/m18/structured_output/scaling-8.json`;
- `artifacts/m18/structured_output/scaling-16.json`;
- `artifacts/m18/structured_output/scaling-32.json`.

Every structured-output record must bind:

`frp.structured_output.v1.7.0`

### Benchmark-Matrix Inclusion

The manifest must include exactly:

- `artifacts/m18/benchmark_matrix/benchmark-matrix.json`;
- `artifacts/m18/tabular/benchmark-matrix.csv`.

The JSON artifact must bind:

`frp.m3.benchmark_matrix.v1.7.0`

The CSV artifact must bind the registered format identity:

`frp.m3.benchmark_matrix.csv.v1.7.0`

The JSON and CSV records must remain separate manifest entries.

### Comparative Benchmark Inclusion

The manifest must bind the six existing comparative benchmark artifacts at their source repository paths.

The artifacts must not be copied into `artifacts/m18/`.

The exact source artifacts are:

- `benchmarks/architecture_comparison/profiles/workload_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`.

Each comparative record must retain its own exact schema or registry-bound identity.

The comparative measurement contour must remain distinct from structured output, M3 matrices, M15 mapping evidence, RTL execution, FPGA preparation, and physical measurement.

### M15 Export Inclusion

The manifest must include the ten exact files under:

`artifacts/m18/m15_exports/`

Each record must bind the exact M15 schema identifier declared by its source artifact.

The vector-package descriptor and the ten vector-package members must remain separate records.

### M15 Vector-Package Inclusion

The manifest must include the ten exact files under:

`artifacts/m18/m15_vectors/`

The seven headered vector and trace files must bind:

`frp.m15.vector.v1`

The reference preload must use the registry-bound identity:

`frp.m15.reference_preload.v1.7.0`

The internal SHA-256 manifest must use the registry-bound identity:

`frp.m15.sha256_manifest.v1.7.0`

The trigonometric lookup table must use its exact registered package role without an invented embedded schema identifier.

### Artifact Record Contract

Every `artifacts` entry must contain:

- `repository_path`;
- `filename`;
- `artifact_class`;
- `format`;
- `schema_identifier`;
- `identification_basis`;
- `producer`;
- `producer_version`;
- `measurement_contour`;
- `byte_length`;
- `sha256`;
- `canonical`;
- `mutable`.

The optional field is:

- `producer_command`.

No additional record fields are permitted unless the manifest schema is versioned explicitly.

### Repository Path Contract

`repository_path` must:

- be relative to the repository root;
- use `/` as the separator;
- identify one existing regular file;
- contain no empty path component;
- contain no `.` component;
- contain no `..` component;
- contain no backslash;
- contain no leading `/`;
- contain no trailing `/`;
- match the actual case-sensitive repository path.

Symbolic links must not be accepted as canonical manifest targets.

Two records must not resolve to the same repository path.

`filename` must equal the final component of `repository_path`.

### Artifact Class Vocabulary

`artifact_class` must be one of:

- `formal_schema`;
- `schema_registry`;
- `structured_output`;
- `benchmark_matrix_json`;
- `benchmark_matrix_csv`;
- `comparative_benchmark`;
- `m15_export`;
- `m15_vector_member`.

Artifact classes must not be merged or silently renamed.

### Format Vocabulary

`format` must be one of:

- `json`;
- `csv`;
- `headered_vector`;
- `headered_trace`;
- `vector_text`.

The declared format must match the source bytes and registered artifact role.

### Identification Basis Vocabulary

`identification_basis` must be one of:

- `embedded_schema`;
- `registry_binding`;
- `format_header`;
- `package_role`.

An artifact with an embedded `schema` field must use:

`embedded_schema`

A schema-free JSON artifact associated through the registry must use:

`registry_binding`

A headered vector or trace must use:

`format_header`

The trigonometric lookup-table member must use:

`package_role`

### Schema Identifier Rules

`schema_identifier` must contain the exact embedded or registry-bound identifier when one exists.

The value must be `null` only when the artifact is identified solely through a package role that has no formal schema identifier.

A missing known identifier fails qualification.

An invented identifier fails qualification.

An identifier that differs only by capitalization, punctuation, milestone, or version is a different identifier and fails qualification.

### Producer Binding

`producer` must identify the exact repository producer.

`producer_version` must identify the exact producer version.

`producer_command`, when present, must reproduce the corresponding artifact using the contract-defined canonical arguments.

Artifacts generated by different commands must remain separate records even when they share a schema identifier.

### Measurement-Contour Vocabulary

`measurement_contour` must be one of the exact registered contour values established by the M18 schema registry.

The manifest must not merge:

- historical transition benchmark;
- structured-output benchmark;
- M3 benchmark matrix;
- transition-pressure and feedback-stress matrix;
- thermal-survival and stability-boundary matrix;
- hierarchical scaling and hotspot-containment matrix;
- M15 implementation mapping;
- comparative architecture benchmark;
- hardware-informed sensitivity qualification;
- M16 RTL qualification;
- M16 FPGA preparation qualification.

Operation count, thermal proxy, transition pressure, `heat_peak`, scheduler timing, latency, throughput, RTL execution, FPGA preparation, and physical measurements remain distinct quantities.

### Raw-Byte Digest Contract

`byte_length` must equal the exact length of the committed file in bytes.

`sha256` must equal the lowercase hexadecimal SHA-256 digest of those exact raw bytes.

Digest calculation must occur before:

- JSON parsing;
- CSV parsing;
- newline conversion;
- Unicode normalization;
- whitespace normalization;
- numeric conversion;
- field reordering;
- any derived representation.

The source file must remain unchanged after digest calculation.

### Canonical and Mutability Flags

Every manifest record must declare:

`canonical = true`

Every manifest record must declare:

`mutable = false`

These flags describe the committed M18 publication instance.

They do not prevent a future explicitly versioned release from publishing a different artifact set.

A future artifact change requires a new qualified manifest and must not silently alter a released historical manifest.

### Deterministic Artifact-Set Digest

`artifact_set_sha256` binds the ordered manifest records without creating a self-digest cycle.

Records must first be ordered by `repository_path` using Unicode code-point order.

For every ordered record, the producer must append:

`repository_path + NUL + sha256 + NUL + decimal byte_length + LF`

Where:

- `NUL` is the single byte `0x00`;
- `LF` is the single byte `0x0A`;
- `decimal byte_length` contains ASCII decimal digits without leading zeros;
- all text components are encoded as UTF-8.

The SHA-256 digest of the complete concatenated byte sequence is stored as:

`artifact_set_sha256`

The empty record set is invalid.

### Ordering Contract

The `artifacts` array must be ordered lexicographically by `repository_path`.

The order must be deterministic and independent of:

- filesystem enumeration order;
- operating system;
- locale;
- generation time;
- JSON object insertion order.

An unordered or differently ordered array fails qualification.

### Manifest Serialization

The manifest must be serialized as UTF-8 JSON with:

- two-space indentation;
- lexicographically sorted object keys;
- no trailing whitespace;
- one final LF byte;
- no byte-order mark;
- no non-finite numeric values.

Repeated generation from unchanged source bytes must produce a byte-identical manifest.

### Cross-Registry Validation

Every manifest record must be checked against the supported-schema registry.

The validator must confirm:

- schema or format identity;
- identification basis;
- artifact format;
- producer path;
- producer version;
- measurement contour;
- supported artifact role;
- permitted repository path;
- applicable Observatory modes.

A recognized schema with an incompatible artifact role fails qualification.

An unregistered schema or format identity fails qualification.

### Manifest Regeneration

The M18 producer must generate the manifest twice from the same committed artifact set.

The two generated manifests must be byte-identical.

The committed manifest must be byte-identical to both generated manifests.

The validation process must not repair or rewrite an artifact to make it match the manifest.

### Manifest Change Control

Any change to a manifest-bound source file requires regeneration of:

- its byte length;
- its SHA-256 digest;
- `artifact_set_sha256`;
- the committed canonical artifact manifest;
- the M18 qualification record.

Digest values must not be edited manually to conceal source-byte changes.

A source-byte change without corresponding qualification evidence fails M18 closure.

### Manifest Qualification Requirements

M18 qualification must prove:

1. the manifest validates against its formal schema;
2. the exact root identity is present;
3. every required publication class is represented;
4. every required artifact path exists;
5. no unexpected artifact record exists;
6. every path is safe, relative, unique, and case-exact;
7. every target is a regular file;
8. every filename matches its repository path;
9. every schema or format identity is registered;
10. every identification basis is correct;
11. every producer binding is correct;
12. every measurement contour is preserved;
13. every byte length matches the committed raw bytes;
14. every SHA-256 digest matches the committed raw bytes;
15. every record declares `canonical = true`;
16. every record declares `mutable = false`;
17. the record order is lexicographic by repository path;
18. `artifact_count` equals the actual record count;
19. `artifact_set_sha256` is reproduced exactly;
20. two independent manifest generations are byte-identical;
21. the committed manifest is byte-identical to both regenerations;
22. the manifest does not bind itself;
23. no timestamp or environment-dependent value affects serialization;
24. no source artifact is modified during validation.

Any manifest mismatch fails M18 qualification.

## Canonical Artifact Qualification Record

M18 publishes one deterministic machine-readable qualification record for the canonical schema and artifact set.

The exact qualification-record path is:

`artifacts/m18/manifests/canonical-artifact-qualification.json`

The exact schema identifier is:

`frp.m18.canonical_artifact_qualification.v2.0.0`

The exact artifact kind is:

`canonical_artifact_qualification`

The qualification record is produced by:

`frp_m18_canonical_artifacts.py`

### Qualification Root Contract

The qualification root must contain:

- `schema`;
- `kind`;
- `version`;
- `milestone`;
- `producer`;
- `producer_version`;
- `upstream_release`;
- `registry_path`;
- `registry_sha256`;
- `manifest_path`;
- `manifest_sha256`;
- `artifact_set_sha256`;
- `check_order`;
- `check_count`;
- `passed_count`;
- `failed_count`;
- `warning_count`;
- `not_evaluated_count`;
- `overall_status`;
- `checks`.

The exact root identity values are:

| Field | Required value |
|---|---|
| `schema` | `frp.m18.canonical_artifact_qualification.v2.0.0` |
| `kind` | `canonical_artifact_qualification` |
| `version` | `2.0.0` |
| `milestone` | `M18 — Formal Schema and Canonical Artifact Publication` |
| `producer` | `frp_m18_canonical_artifacts.py` |
| `producer_version` | `2.0.0` |
| `upstream_release` | `FRP v1.8.0 / M16` |
| `check_order` | `category_check_id_subject_path` |

The qualification record must not contain a generation timestamp, workflow run number, temporary directory, hostname, username, absolute path, or environment-specific value.

### Registry Binding

`registry_path` must equal:

`schemas/m18/frp_m18_schema_registry.json`

`registry_sha256` must equal the SHA-256 digest calculated from the exact committed registry bytes.

The registry must validate against its registered formal schema before any artifact qualification proceeds.

A missing, invalid, or digest-mismatched registry makes all dependent checks not qualified.

### Manifest Binding

`manifest_path` must equal:

`artifacts/m18/manifests/canonical-artifact-manifest.json`

`manifest_sha256` must equal the SHA-256 digest calculated from the exact committed manifest bytes.

`artifact_set_sha256` must equal the value declared by the canonical artifact manifest and independently recalculated from the manifest-bound source files.

The qualification record must not repair, rewrite, or normalize the manifest.

### Check Record Contract

Every item in `checks` must contain:

- `check_id`;
- `category`;
- `subject_path`;
- `outcome`;
- `severity`;
- `expected`;
- `observed`;
- `message`.

`subject_path` may be `null` only for a qualification-wide aggregate check.

`expected` and `observed` may contain:

- a JSON string;
- a JSON integer;
- a JSON number;
- a JSON boolean;
- `null`;
- an array of permitted JSON values;
- an object containing permitted JSON values.

Non-finite numeric values are prohibited.

### Check Identifier Contract

`check_id` must:

- be a non-empty lowercase ASCII string;
- contain only `a` through `z`, `0` through `9`, and `_`;
- begin with a lowercase letter;
- be unique for the same `subject_path`;
- identify one stable validation relation.

Check identifiers must not contain sequence numbers derived from execution order.

### Qualification Categories

`category` must be one of:

- `registry`;
- `formal_schema`;
- `manifest`;
- `path`;
- `format`;
- `identity`;
- `structure`;
- `ternary_domain`;
- `scheduler`;
- `benchmark_relation`;
- `measurement_contour`;
- `vector_package`;
- `digest`;
- `determinism`;
- `immutability`;
- `publication_boundary`.

Categories must remain distinct in the machine-readable report.

### Check Outcomes

`outcome` must be one of:

- `PASS`;
- `FAIL`;
- `WARNING`;
- `NOT_EVALUATED`.

The meaning of each value is:

| Outcome | Meaning |
|---|---|
| `PASS` | The declared relation was evaluated and satisfied |
| `FAIL` | The declared relation was evaluated and not satisfied |
| `WARNING` | The relation was evaluated and produced a non-closing advisory condition |
| `NOT_EVALUATED` | The relation could not be evaluated |

M18 closure requires every check to have:

`outcome = "PASS"`

### Message Severity

`severity` must be one of:

- `INFO`;
- `WARNING`;
- `ERROR`.

The permitted outcome-to-severity relations are:

| Outcome | Required severity |
|---|---|
| `PASS` | `INFO` |
| `FAIL` | `ERROR` |
| `WARNING` | `WARNING` |
| `NOT_EVALUATED` | `ERROR` |

Any other outcome-to-severity relation is invalid.

### Stable Check Ordering

The `checks` array must be ordered lexicographically by the tuple:

1. `category`;
2. `check_id`;
3. `subject_path`, with `null` ordered before strings.

Ordering must use Unicode code-point order and must not depend on locale or execution order.

### Required Registry Checks

The qualification record must include checks proving:

- the registry file exists;
- the registry is a regular file;
- the registry raw-byte digest matches `registry_sha256`;
- the registry validates against its formal schema;
- the registry root identity is exact;
- registry identifiers are unique;
- formal schema paths are unique;
- every formal schema path exists;
- every formal schema `$id` matches its registry record;
- all local `$ref` values resolve offline;
- the exact twenty-four supported identifiers are present;
- no unregistered identifier is present.

### Required Formal-Schema Checks

For every formal schema, the qualification record must prove:

- the file exists;
- the file is a regular UTF-8 JSON file;
- JSON parsing succeeds;
- `$schema` declares JSON Schema Draft 2020-12;
- `$id` uses the required FRP URN;
- the registered exact schema identifier is preserved;
- required fields are declared;
- additional-field handling is explicit;
- numeric constraints are explicit where upstream values define them;
- enum constraints preserve exact upstream vocabularies;
- local references resolve without network access;
- the canonical positive ternary state is written as `1`, not `+1`.

### Required Manifest Checks

The qualification record must include checks proving:

- the canonical manifest exists;
- the manifest validates against its formal schema;
- the manifest root identity is exact;
- its record set is closed;
- paths are safe and unique;
- record ordering is exact;
- `artifact_count` is exact;
- artifact classes are valid;
- formats are valid;
- identification bases are valid;
- schema bindings match the registry;
- producer bindings match the registry;
- measurement contours match the registry;
- every byte length matches;
- every SHA-256 digest matches;
- `artifact_set_sha256` is independently reproduced;
- the manifest does not bind itself.

### Required Structured-Output Checks

For every canonical structured-output artifact, the qualification record must prove:

- exact schema identity;
- formal schema validity;
- exact producer binding;
- deterministic producer arguments;
- canonical ternary-domain validity;
- tick ordering;
- trace ordering;
- scheduler-state validity;
- scheduler-counter relations;
- pending-route relations;
- transition-capacity relations;
- invariant-vector validity;
- raw-byte digest validity.

The qualification record must distinguish:

- default output;
- `free`;
- `7/1`;
- `1/7`;
- scaling at `8` cells;
- scaling at `16` cells;
- scaling at `32` cells.

### Required Benchmark-Matrix Checks

The qualification record must prove:

- the canonical benchmark-matrix JSON exists;
- the canonical benchmark-matrix CSV exists;
- the JSON validates against `frp.m3.benchmark_matrix.v1.7.0`;
- the CSV header is exact;
- CSV row order is exact;
- CSV field count is exact;
- every CSV row corresponds to the matching JSON row;
- numeric values are preserved without reinterpretation;
- scheduler modes remain distinct;
- measurement fields remain distinct;
- both files reproduce byte-identically.

### Required Comparative Benchmark Checks

The qualification record must prove:

- all six comparative benchmark source artifacts exist;
- their exact source paths are preserved;
- their schema or registry-bound identities are exact;
- their producer bindings are exact;
- their declared workload digests are valid;
- their declared profile digests are valid;
- their architecture order is preserved;
- their hardware-sensitivity scenario order is preserved;
- recorded rankings are preserved;
- operation count and thermal proxy remain separate;
- no comparative value is reinterpreted as physical-chip evidence.

### Required M15 Export Checks

For every canonical M15 JSON export, the qualification record must prove:

- exact filename;
- exact schema identity;
- exact artifact kind;
- formal schema validity;
- exact producer command;
- exact producer version;
- deterministic regeneration;
- raw-byte equality with regenerated output;
- raw-byte digest validity.

The qualification record must also prove that the corrected canonical state notation does not alter processor execution semantics.

### Required M15 Vector-Package Checks

The qualification record must prove:

- the exact ten-member package exists;
- no unexpected package member exists;
- all seven headered members use `frp.m15.vector.v1`;
- all trace kinds are exact;
- all scheduler bindings are exact;
- all canonical ternary states belong to `{-1, 0, 1}`;
- packed states match the registered hardware encoding;
- preload fields and array lengths are valid;
- preload packed states match decoded states;
- the Q30 lookup table contains exactly `4096` ordered entries;
- the internal SHA-256 manifest binds exactly nine non-manifest members;
- every internal digest matches raw bytes;
- the JSON vector-package descriptor binds all ten members;
- descriptor byte lengths match;
- descriptor digests match;
- the deterministic package digest matches;
- two independent regenerations are byte-identical;
- the committed package matches both regenerations.

### Required Measurement-Contour Checks

The qualification record must prove that no artifact record merges distinct measurement contours.

The checks must preserve separate identities for:

- historical transition measurements;
- structured-output measurements;
- M3 benchmark matrices;
- transition-pressure and feedback-stress measurements;
- thermal-survival and stability-boundary measurements;
- hierarchical scaling and hotspot-containment measurements;
- M15 implementation-mapping measurements;
- comparative architecture measurements;
- hardware-informed sensitivity measurements;
- M16 RTL qualification;
- M16 FPGA preparation qualification.

M18 must not publish a physical measurement claim derived from target-independent FPGA preparation evidence.

### Required Immutability Checks

Before parsing, the qualifier must capture for every source file:

- repository path;
- byte length;
- SHA-256 digest.

After all validation and regeneration comparisons, it must capture the same values again.

The before and after values must match exactly.

A source-byte change during qualification fails the immutability check.

### Required Determinism Checks

The qualification process must independently regenerate:

- all canonical structured-output artifacts;
- benchmark-matrix JSON;
- benchmark-matrix CSV;
- all canonical M15 JSON exports;
- both M15 vector-package instances;
- the canonical artifact manifest;
- the qualification record itself.

Each repeated generation must be byte-identical.

The committed artifact must be byte-identical to every corresponding regenerated artifact.

### Aggregate Counters

`check_count` must equal the number of records in `checks`.

`passed_count` must equal the number of `PASS` outcomes.

`failed_count` must equal the number of `FAIL` outcomes.

`warning_count` must equal the number of `WARNING` outcomes.

`not_evaluated_count` must equal the number of `NOT_EVALUATED` outcomes.

The counters must be derived from `checks` and must not be maintained independently.

### Overall Status

`overall_status` must be one of:

- `PASS`;
- `FAIL`.

`overall_status` may equal `PASS` only when:

- `check_count > 0`;
- `passed_count = check_count`;
- `failed_count = 0`;
- `warning_count = 0`;
- `not_evaluated_count = 0`.

Every other valid counter relation requires:

`overall_status = "FAIL"`

### Qualification Serialization

The qualification record must be serialized as UTF-8 JSON with:

- two-space indentation;
- lexicographically sorted object keys;
- no trailing whitespace;
- one final LF byte;
- no byte-order mark;
- no non-finite numeric values.

Stable messages must not contain temporary paths or runtime-specific text.

Two executions over unchanged inputs must produce byte-identical qualification records.

### Qualification Closure Conditions

M18 qualification closes only when:

1. the qualification record validates against its formal schema;
2. all root identity fields are exact;
3. registry and manifest bindings match committed raw bytes;
4. every required check is present;
5. every check has `outcome = "PASS"`;
6. every check has `severity = "INFO"`;
7. all aggregate counters are exact;
8. `overall_status = "PASS"`;
9. repeated qualification is byte-identical;
10. no source artifact is modified;
11. no unsupported schema or artifact claim is introduced;
12. no M16 machine-readable execution evidence is claimed as an M18 deliverable;
13. no physical-chip claim is derived from FPGA preparation evidence.

Any qualification-record mismatch fails M18 closure.

## Canonical Artifact Self-Test Record

M18 publishes one deterministic machine-readable self-test record for the canonical artifact producer and validator.

The exact self-test record path is:

`artifacts/m18/manifests/canonical-artifact-self-test.json`

The exact schema identifier is:

`frp.m18.canonical_artifact_self_test.v2.0.0`

The exact artifact kind is:

`canonical_artifact_self_test`

The exact producer command is:

`python frp_m18_canonical_artifacts.py --self-test --output json`

The committed record must equal the exact UTF-8 JSON emitted by this command.

### Self-Test Root Contract

The self-test root must contain:

- `schema`;
- `kind`;
- `version`;
- `milestone`;
- `producer`;
- `producer_version`;
- `upstream_release`;
- `profile`;
- `case_order`;
- `case_count`;
- `passed_count`;
- `failed_count`;
- `overall_status`;
- `cases`.

The exact root identity values are:

| Field | Required value |
|---|---|
| `schema` | `frp.m18.canonical_artifact_self_test.v2.0.0` |
| `kind` | `canonical_artifact_self_test` |
| `version` | `2.0.0` |
| `milestone` | `M18 — Formal Schema and Canonical Artifact Publication` |
| `producer` | `frp_m18_canonical_artifacts.py` |
| `producer_version` | `2.0.0` |
| `upstream_release` | `FRP v1.8.0 / M16` |
| `profile` | `m18_canonical_artifact_publication` |
| `case_order` | `case_id_lexicographic` |
| `case_count` | `34` |

The self-test record must not contain timestamps or environment-dependent values.

### Self-Test Case Contract

Every item in `cases` must contain:

- `case_id`;
- `category`;
- `purpose`;
- `expected`;
- `observed`;
- `status`.

Every case must be deterministic.

`case_id` must:

- be a non-empty lowercase ASCII string;
- contain only `a` through `z`, `0` through `9`, and `_`;
- begin with a lowercase letter;
- be unique within the self-test record.

### Self-Test Categories

`category` must be one of:

- `serialization`;
- `digest`;
- `path`;
- `registry`;
- `formal_schema`;
- `identity`;
- `ternary_domain`;
- `scheduler`;
- `ordering`;
- `manifest`;
- `vector_package`;
- `immutability`;
- `determinism`;
- `publication_boundary`.

### Self-Test Status

`status` must be one of:

- `PASS`;
- `FAIL`.

A case has `status = "PASS"` only when its exact observed behavior equals its exact expected behavior.

A negative test passes only when the tested invalid input is rejected for the expected reason.

An unexpected exception is a failed case.

### Exact Required Cases

The self-test record must contain exactly these thirty-four case identifiers:

1. `artifact_set_digest_known_vector`;
2. `canonical_json_serialization_stable`;
3. `canonical_ternary_domain_accept`;
4. `canonical_ternary_domain_reject`;
5. `deterministic_regeneration_byte_identical`;
6. `embedded_schema_identity_accept`;
7. `environment_dependent_field_reject`;
8. `formal_schema_id_match_accept`;
9. `formal_schema_id_mismatch_reject`;
10. `internal_manifest_digest_mismatch_reject`;
11. `manifest_aggregate_status_accept`;
12. `manifest_aggregate_status_reject`;
13. `manifest_order_accept`;
14. `manifest_order_reject`;
15. `manifest_self_binding_reject`;
16. `opposite_transition_direct_reject`;
17. `opposite_transition_via_zero_accept`;
18. `path_absolute_reject`;
19. `path_duplicate_reject`;
20. `path_parent_component_reject`;
21. `path_relative_accept`;
22. `path_symlink_reject`;
23. `preload_packed_state_mapping_accept`;
24. `raw_byte_sha256_known_vector`;
25. `registry_bound_identity_accept`;
26. `registry_duplicate_identifier_reject`;
27. `registry_exact_identifier_set_accept`;
28. `registry_unknown_identifier_reject`;
29. `scheduler_1_7_sequence_accept`;
30. `scheduler_7_1_sequence_accept`;
31. `scheduler_free_sequence_accept`;
32. `source_mutation_detected`;
33. `state_notation_plus_prefix_reject`;
34. `vector_package_member_set_accept`.

No additional self-test case may appear without an explicit schema and contract version change.

### Digest Known-Vector Tests

`raw_byte_sha256_known_vector` must validate the SHA-256 implementation against a fixed in-memory byte sequence with a fixed expected digest.

The test must hash raw bytes directly.

It must not hash decoded text or a normalized representation.

`artifact_set_digest_known_vector` must validate:

- lexicographic repository-path ordering;
- UTF-8 path encoding;
- single-byte NUL separators;
- ASCII decimal byte lengths;
- single-byte LF record terminators;
- final SHA-256 calculation.

The expected digest must be stored as a fixed self-test constant independent of repository artifacts.

### Canonical JSON Serialization Test

`canonical_json_serialization_stable` must serialize the same in-memory object twice and prove byte-identical output.

The test must verify:

- two-space indentation;
- sorted object keys;
- UTF-8 encoding;
- one final LF byte;
- no byte-order mark;
- no trailing whitespace;
- rejection of non-finite numeric values.

### Path Tests

`path_relative_accept` must accept a valid repository-relative POSIX path.

`path_absolute_reject` must reject an absolute path.

`path_parent_component_reject` must reject a path containing `..`.

`path_duplicate_reject` must reject two records using the same repository path.

`path_symlink_reject` must reject a symbolic-link target as a canonical artifact.

Path tests must operate only inside a self-test temporary directory.

They must not inspect or modify files outside that directory.

### Registry Tests

`registry_exact_identifier_set_accept` must accept the exact twenty-four-entry M18 registry identity set.

`registry_duplicate_identifier_reject` must reject duplicate exact schema identifiers.

`registry_unknown_identifier_reject` must reject an identifier absent from the supported registry.

The registry tests must distinguish schema identifiers from format identifiers and package roles.

### Formal Schema Tests

`formal_schema_id_match_accept` must accept a formal schema whose `$id` exactly matches the URN derived from its registered schema identifier.

`formal_schema_id_mismatch_reject` must reject:

- a different version;
- a different milestone;
- different capitalization;
- a different punctuation sequence;
- a non-FRP URN;
- a missing `$id`.

Formal schema validation must use the local Draft 2020-12 validator without network access.

### Identity Tests

`embedded_schema_identity_accept` must accept an artifact whose exact embedded `schema` field matches the registered identifier.

`registry_bound_identity_accept` must accept a schema-free artifact only when:

- its exact path is registered;
- its exact role is registered;
- its producer is registered;
- its format is registered;
- its external schema association is registered.

A registry-bound identity must not be inserted into or written over the source artifact.

### Canonical Ternary Tests

`canonical_ternary_domain_accept` must accept only values from:

`{-1, 0, 1}`

`canonical_ternary_domain_reject` must reject values outside that set, including:

- `-2`;
- `2`;
- string values;
- booleans;
- `null`;
- non-integral numbers.

Because JSON booleans are integer-like in Python, the validator must reject booleans before integer-domain validation.

`state_notation_plus_prefix_reject` must reject `+1` as a canonical processor-state label.

It must not reject unrelated arithmetic expressions such as:

- `2i+1`;
- `N+1`;
- signed positive exponents;
- explicitly non-state numeric expressions.

### Transition Tests

`opposite_transition_via_zero_accept` must accept:

- `-1 → 0 → 1`;
- `1 → 0 → -1`.

`opposite_transition_direct_reject` must reject:

- `-1 → 1`;
- `1 → -1`.

The test validates the published transition relation.

It must not implement an alternative processor state machine.

### Scheduler Tests

`scheduler_free_sequence_accept` must validate the registered `free` scheduler sequence.

`scheduler_7_1_sequence_accept` must validate repeating cycles of:

- seven `balance` ticks;
- one `commit` tick.

`scheduler_1_7_sequence_accept` must validate repeating cycles of:

- one `excite` tick;
- seven `neutralize` ticks.

The scheduler tests must verify state sequence, counter progression, and cycle reset.

The three modes must remain independent test cases.

### Ordering Tests

`manifest_order_accept` must accept records ordered lexicographically by repository path.

`manifest_order_reject` must reject:

- reversed order;
- locale-dependent order;
- case-insensitive order when it differs from code-point order;
- filesystem enumeration order that differs from the required order.

### Manifest Self-Binding Test

`manifest_self_binding_reject` must reject a canonical artifact manifest that includes its own repository path.

The test must prove that the validator prevents a circular raw-byte digest dependency.

### Aggregate Status Tests

`manifest_aggregate_status_accept` must accept exact counters derived from an all-PASS check vector.

`manifest_aggregate_status_reject` must reject:

- an incorrect `check_count`;
- an incorrect `passed_count`;
- an incorrect `failed_count`;
- an incorrect `warning_count`;
- an incorrect `not_evaluated_count`;
- `overall_status = "PASS"` when any check is not `PASS`.

### Vector-Package Tests

`vector_package_member_set_accept` must accept exactly these ten filenames:

- `frp_m15_cell_trace.vec`;
- `frp_m15_full_correlation_vectors.vec`;
- `frp_m15_kernel_vectors.vec`;
- `frp_m15_pending_routes.trace`;
- `frp_m15_reference_preload.json`;
- `frp_m15_scheduler_1_7_vectors.vec`;
- `frp_m15_scheduler_7_1_vectors.vec`;
- `frp_m15_scheduler_free_vectors.vec`;
- `frp_m15_sha256_manifest.json`;
- `frp_m15_trig_lut_q30.vec`.

The same test must reject a derived invalid set containing:

- one missing member;
- one duplicate member;
- one renamed member;
- one unexpected member.

### Internal Manifest Digest Test

`internal_manifest_digest_mismatch_reject` must construct an in-memory package whose declared SHA-256 differs from the raw-byte digest of one member.

The validator must reject the package without rewriting either the member or its manifest.

### Preload Mapping Test

`preload_packed_state_mapping_accept` must verify exact consistency between:

- canonical states;
- two-bit hardware codes;
- packed state order;
- `states_packed_hex`.

The exact mapping is:

| State | Two-bit code |
|---:|---|
| `-1` | `11` |
| `0` | `00` |
| `1` | `01` |
| reserved | `10` |

The test must reject the reserved code as a decoded canonical processor state.

### Source-Mutation Test

`source_mutation_detected` must:

1. create one temporary source file;
2. capture its byte length and SHA-256;
3. alter its bytes inside the temporary directory;
4. capture its new byte length and SHA-256;
5. prove that the immutability validator detects the change.

The test must not modify a repository source artifact.

### Deterministic Regeneration Test

`deterministic_regeneration_byte_identical` must generate the same in-memory fixture set twice.

It must prove equality of:

- filenames;
- record order;
- byte lengths;
- raw bytes;
- per-file SHA-256 digests;
- artifact-set digest;
- serialized manifest bytes;
- serialized self-test bytes.

### Environment-Dependent Field Test

`environment_dependent_field_reject` must reject deterministic publication records containing:

- a current timestamp;
- a temporary absolute path;
- a hostname;
- a username;
- a process identifier;
- a workflow run number;
- an unordered environment dump.

This test does not prohibit separate workflow evidence from recording its execution identity.

It prohibits such values from altering deterministic canonical records.

### Self-Test Safety Boundary

The self-test must not:

- execute source artifact contents;
- execute uploaded code;
- invoke SystemVerilog;
- invoke a shell command derived from artifact data;
- access the network;
- alter repository artifacts;
- follow symbolic links;
- write outside its temporary directory;
- introduce processor semantics;
- change published metric values.

All invalid inputs used by negative cases must be constructed internally by the self-test.

### Aggregate Self-Test Counters

`case_count` must equal:

`34`

`passed_count` must equal the number of cases with `status = "PASS"`.

`failed_count` must equal the number of cases with `status = "FAIL"`.

For M18 closure, the required values are:

| Field | Required value |
|---|---:|
| `case_count` | `34` |
| `passed_count` | `34` |
| `failed_count` | `0` |
| `overall_status` | `PASS` |

### Self-Test Serialization

The self-test record must be serialized as UTF-8 JSON with:

- two-space indentation;
- lexicographically sorted object keys;
- cases ordered lexicographically by `case_id`;
- no trailing whitespace;
- one final LF byte;
- no byte-order mark;
- no non-finite numeric values.

Repeated self-test execution must produce byte-identical output.

### Self-Test Closure Conditions

M18 self-test qualification closes only when:

1. the record validates against its formal schema;
2. the exact thirty-four case identifiers are present;
3. no duplicate or additional case exists;
4. every case has `status = "PASS"`;
5. `case_count = 34`;
6. `passed_count = 34`;
7. `failed_count = 0`;
8. `overall_status = "PASS"`;
9. two independent executions are byte-identical;
10. no repository artifact is modified;
11. no network or arbitrary artifact execution occurs.

Any self-test mismatch fails M18 closure.

## M18 Producer Interface

The M18 canonical artifact producer and validator is:

`frp_m18_canonical_artifacts.py`

It is a repository-root Python program.

It coordinates existing FRP producers, formal-schema validation, deterministic artifact generation, raw-byte digest calculation, manifest construction, qualification, and internal self-tests.

It must not implement or replace processor semantics.

### Runtime Contract

The qualified runtime is:

`Python 3.12`

The formal JSON Schema validator is:

`jsonschema==4.25.1`

Formal artifact validation must use:

`Draft202012Validator`

The validator must operate without network access.

The existing FRP numerical dependency remains defined by:

`requirements.txt`

No UI framework, web server, database, notebook runtime, or downstream Observatory dependency belongs to the M18 producer.

### Exact Execution Modes

The producer supports exactly four mutually exclusive execution modes:

- `--generate`;
- `--verify`;
- `--qualify`;
- `--self-test`.

Exactly one execution mode must be selected.

Selecting no mode or more than one mode is a command-line error.

### Common Arguments

The supported common arguments are:

| Argument | Required | Contract |
|---|---:|---|
| `--repository-root PATH` | no | Repository root; default is `.` |
| `--output FORMAT` | no | `text` or `json`; default is `text` |
| `--output-root PATH` | mode-dependent | Generated-artifact staging root |
| `--replace` | no | Permit atomic replacement of registered M18 generated targets |

No unregistered command-line argument may alter processor parameters, schema identities, artifact paths, or qualification rules.

### Repository-Root Resolution

`--repository-root` must resolve to a directory containing:

- `frp_prototype_v1_7_0.py`;
- `requirements.txt`;
- `schemas/m18/frp_m18_schema_registry.json`;
- the registered formal schema files;
- the six registered comparative benchmark artifacts.

The resolved repository root must not be a symbolic link.

All registered repository paths must remain inside the resolved root after canonical path resolution.

A path escape fails before any producer execution.

### Generate Mode

The exact interface is:

`python frp_m18_canonical_artifacts.py --generate --repository-root . --output-root <directory>`

`--output-root` is required in generate mode.

Generate mode writes a mirror of generated repository paths beneath the selected output root.

It generates:

- eleven canonical structured-output artifacts;
- canonical benchmark-matrix JSON;
- canonical benchmark-matrix CSV;
- ten canonical M15 JSON exports;
- ten canonical M15 vector-package members;
- the canonical artifact manifest;
- the canonical artifact qualification record;
- the canonical artifact self-test record.

Generate mode reads but does not copy or modify:

- the M18 schema registry;
- formal JSON Schema files;
- comparative benchmark source artifacts;
- the executable semantic reference;
- existing upstream qualification evidence.

### Overlay Resolution

During staged generation, manifest and qualification input resolution uses two explicit layers.

For registered generated M18 paths, the source is:

`output-root/repository-path`

For registry, formal-schema, and comparative-source paths, the source is:

`repository-root/repository-path`

A missing generated path must not fall back to an older committed artifact under the repository root.

A generated path present in both layers must use the output-root instance.

The overlay rule must be implemented from registered path classes, not from arbitrary filesystem preference.

### Verify Mode

The exact interface is:

`python frp_m18_canonical_artifacts.py --verify --repository-root . --output text`

Verify mode is read-only.

It validates the committed:

- schema registry;
- formal schema set;
- canonical artifact set;
- canonical manifest;
- qualification record;
- self-test record.

Verify mode must not generate replacement files.

Verify mode succeeds only when committed records and independently recalculated values match exactly.

With:

`--output json`

verify mode emits the independently reconstructed qualification record to standard output without writing it to the repository.

### Qualify Mode

The exact machine-readable interface is:

`python frp_m18_canonical_artifacts.py --qualify --repository-root . --output json`

Qualify mode is read-only.

It emits the deterministic record defined by:

`frp.m18.canonical_artifact_qualification.v2.0.0`

The emitted bytes must match:

`artifacts/m18/manifests/canonical-artifact-qualification.json`

With:

`--output text`

qualify mode emits a human-readable projection containing:

- overall status;
- check count;
- passed count;
- failed count;
- warning count;
- not-evaluated count;
- failed check identifiers, if any.

The text projection is not a canonical artifact.

### Self-Test Mode

The exact machine-readable interface is:

`python frp_m18_canonical_artifacts.py --self-test --output json`

Self-test mode does not require repository artifacts.

It may use only:

- in-memory fixtures;
- internally constructed invalid inputs;
- a temporary directory created for the self-test process.

It emits the deterministic record defined by:

`frp.m18.canonical_artifact_self_test.v2.0.0`

The emitted bytes must match:

`artifacts/m18/manifests/canonical-artifact-self-test.json`

With:

`--output text`

self-test mode emits:

- overall status;
- case count;
- passed count;
- failed count;
- failed case identifiers, if any.

### Output Argument Rules

`--output` accepts exactly:

- `text`;
- `json`.

JSON output must be written to standard output.

Diagnostics must be written to standard error.

A successful JSON execution must not mix diagnostic text with standard output.

Text output must use stable English labels.

ANSI color codes are prohibited in canonical or CI-consumed output.

### Output-Root Safety

The output root must:

- resolve to a directory or a creatable directory;
- not be the filesystem root;
- not equal the user home directory;
- not escape through a symbolic link;
- not overlap the repository root unless explicitly selected for publication;
- contain no target path outside registered M18 generated paths.

The producer must never recursively delete the output root.

Temporary files must be removed individually after success or failure.

### Registered Write Boundary

The producer may write only these generated path prefixes:

- `artifacts/m18/structured_output/`;
- `artifacts/m18/benchmark_matrix/`;
- `artifacts/m18/m15_exports/`;
- `artifacts/m18/m15_vectors/`;
- `artifacts/m18/tabular/`;
- `artifacts/m18/manifests/`.

It must not write to:

- `benchmarks/architecture_comparison/`;
- `schemas/m18/`;
- `rtl/`;
- `fpga/`;
- `docs/`;
- `.github/workflows/`;
- the semantic reference;
- test sources;
- dependency files.

Schema and source changes remain separate reviewed repository edits.

### Replacement Rules

Without `--replace`, generation must:

- create a missing registered target;
- leave a byte-identical existing target unchanged;
- fail on an existing target with different bytes.

With `--replace`, generation may atomically replace only registered M18 generated targets.

`--replace` must not authorize writes outside the registered write boundary.

Every replacement must use:

1. a temporary sibling file;
2. complete byte writing;
3. flush and close;
4. atomic path replacement.

A failed generation must not leave a partially written canonical artifact.

### Static Upstream Producer Invocation

The M18 program may invoke only:

`frp_prototype_v1_7_0.py`

The executable path must resolve beneath the repository root.

The invocation must use:

- `sys.executable`;
- an argument list;
- `shell = False`;
- captured standard output;
- captured standard error;
- a checked return code;
- fixed contract-defined arguments.

Artifact data must never supply:

- an executable path;
- a command-line option;
- a shell fragment;
- an environment-variable name;
- an output path.

### Producer Command Table

The M18 program must use the exact producer commands established by this contract.

The required command classes are:

| Output class | Upstream producer option |
|---|---|
| structured output | `--mode benchmark --output json` |
| trace output | `--mode benchmark --output json --include-trace` |
| self-test output | `--mode self-test --output json` |
| benchmark matrix | `--export-benchmark-matrix` |
| M15 fixed-point profile | `--export-fixed-point-interface-profile` |
| M15 encoding map | `--export-balanced-ternary-hardware-encoding-map` |
| M15 quantized shadow | `--export-quantized-reference-shadow-model` |
| M15 cycle-exact trace | `--export-cycle-exact-reference-trace` |
| M15 vector descriptor and members | `--export-rtl-comparison-vector-package` |
| M15 testbench map | `--export-systemverilog-testbench-interface-map` |
| M15 RTL core description | `--export-synthesizable-rtl-reference-core` |
| M15 assertion harness | `--export-rtl-assertion-correlation-harness` |
| M15 equivalence report | `--export-reference-rtl-equivalence-report` |
| M15 closure manifest | `--export-qualification-closure-manifest` |

Scheduler, cell-count, step-count, seed, and output-directory arguments must match the exact artifact-set sections of this contract.

### Canonical State-Notation Gate

Before generating M18 artifacts, the producer must verify the canonical processor-state notation in registered state-label fields and assertion text.

The required processor-domain notation is:

`-1, 0, 1`

The producer must reject `+1` when it denotes the canonical positive processor state.

This gate must not reject unrelated arithmetic expressions.

The notation check must not change numeric execution, state encoding, transition routing, scheduler behavior, or metric values.

### JSON Parsing Boundary

Producer JSON output must be captured as raw bytes.

The raw bytes must first pass:

- successful UTF-8 decoding;
- successful JSON parsing;
- root-type validation;
- exact identity validation;
- formal schema validation.

The M18 producer must not repair malformed upstream JSON.

A producer output with unexpected standard-output text fails generation.

### CSV Construction Boundary

The canonical benchmark CSV is derived only from the validated canonical benchmark-matrix JSON.

CSV construction must use the exact column order and serialization rules defined by this contract.

The CSV producer must not:

- recompute benchmark metrics;
- rename fields;
- merge rows;
- change row order;
- infer missing values;
- convert distinct measurement quantities into one column.

### Formal Schema Loading

Formal schemas must be loaded only from registered repository paths.

The validator must:

- use Draft 2020-12;
- build an offline local resource registry;
- resolve only registered local schema resources;
- reject unresolved references;
- reject duplicate `$id` values;
- reject remote retrieval attempts.

Formal schema validation must not execute format-specific external programs.

### Source-Byte Preservation

Every source artifact must be captured as immutable raw bytes before parsing.

Derived parsed objects must be separate from source bytes.

Digest calculation must use source bytes.

Validation must not replace the source-byte object with reserialized content.

Before and after source digests must match.

### Deterministic Data Structures

Public records must use deterministic ordering.

The implementation must not rely on:

- set iteration order;
- filesystem enumeration order;
- locale sorting;
- process-randomized hashes;
- current time;
- random values without the fixed contract seed.

Where a set is required internally, its public projection must be explicitly sorted.

### Failure Isolation

If one generation or validation operation fails:

- remaining canonical files must not be published;
- the final manifest must not be published;
- the qualification record must report failure when qualification can be completed safely;
- temporary outputs must remain outside committed artifact paths;
- existing committed artifacts must remain unchanged.

### Exit-Code Contract

The producer uses these exact exit codes:

| Exit code | Meaning |
|---:|---|
| `0` | Requested operation completed successfully |
| `1` | Validation, verification, qualification, or self-test failure |
| `2` | Invalid command-line arguments or configuration |
| `3` | Registered upstream producer failed |
| `4` | Filesystem or write-boundary safety failure |

Unhandled exceptions must be converted into one of the defined nonzero exit codes.

A traceback may be written to standard error only when explicitly enabled for development outside canonical CI execution.

### Security Boundary

The M18 producer must not:

- execute uploaded artifacts;
- execute artifact-provided commands;
- execute SystemVerilog;
- import Python modules from artifact paths;
- deserialize executable object formats;
- access the network;
- follow unregistered symbolic links;
- mutate upstream source artifacts;
- evaluate expressions from JSON or CSV;
- use `shell = True`.

JSON, CSV, vector, trace, schema, and manifest files are data only.

### Interface Qualification

M18 qualification must prove:

1. Python 3.12 execution succeeds;
2. the pinned Draft 2020-12 validator is available;
3. exactly one execution mode is required;
4. all registered arguments enforce their mode restrictions;
5. repository-root containment is enforced;
6. output-root containment is enforced;
7. the registered write boundary is enforced;
8. static producer invocation uses `shell = False`;
9. diagnostics remain separate from JSON standard output;
10. generation is deterministic;
11. verification is read-only;
12. qualification is read-only;
13. self-test uses only internal fixtures;
14. replacement is atomic and path-limited;
15. failure leaves committed source artifacts unchanged;
16. all defined exit codes are exercised by tests;
17. no artifact-controlled code execution path exists;
18. processor semantics remain owned by `frp_prototype_v1_7_0.py`.

Any interface-contract violation fails M18 qualification.

## M18 Test Contract

The M18 test module is:

`tests/test_frp_m18_canonical_artifacts.py`

The module uses the Python standard-library `unittest` framework.

It validates the M18 producer independently from the producer's internal self-test.

### Exact Test Commands

The isolated M18 test command is:

`python -m unittest discover -s tests -p 'test_frp_m18_canonical_artifacts.py' -v`

The complete repository test command is:

`python -m unittest discover -s tests -p 'test_*.py' -v`

The source-compilation command is:

`python -m compileall -q frp_m18_canonical_artifacts.py tests/test_frp_m18_canonical_artifacts.py`

All three commands must succeed in the M18 workflow.

### Test Independence

Contract-critical expected values must be declared independently in the test module.

The test module must not import production constants to establish expected values for:

- supported schema identifiers;
- formal schema paths;
- canonical artifact paths;
- canonical ternary states;
- hardware state codes;
- scheduler sequences;
- M15 vector-package members;
- required root fields;
- required self-test case identifiers;
- required status values;
- digest-scope rules.

Production helpers may be invoked as the subject under test.

They must not be used as the authority for their own expected result.

### Read-Only Repository Boundary

Tests may read committed repository files.

Tests must not modify them.

All generated files, malformed fixtures, symbolic links, duplicate records, altered manifests, and negative-case artifacts must exist only under:

`tempfile.TemporaryDirectory()`

Before and after the complete test suite, committed artifact digests must remain identical.

### Required Test Classes

The test module must contain these logical test classes:

- `M18ProducerInterfaceTests`;
- `M18SchemaRegistryTests`;
- `M18FormalSchemaTests`;
- `M18CanonicalArtifactTests`;
- `M18ManifestTests`;
- `M18QualificationRecordTests`;
- `M18SelfTestRecordTests`;
- `M18DeterminismTests`;
- `M18SecurityBoundaryTests`.

Equivalent class splitting is permitted only when every required test relation remains explicit and independently discoverable.

### Producer Interface Tests

`M18ProducerInterfaceTests` must verify:

- the producer module imports successfully;
- the CLI requires exactly one execution mode;
- `--generate` requires `--output-root`;
- `--verify` is read-only;
- `--qualify` is read-only;
- `--self-test` does not require committed artifacts;
- `--output` accepts only `text` and `json`;
- JSON output contains no diagnostic text;
- diagnostics use standard error;
- invalid arguments return exit code `2`;
- upstream producer failure returns exit code `3`;
- write-boundary failure returns exit code `4`;
- validation failure returns exit code `1`;
- successful execution returns exit code `0`;
- upstream producer invocation uses an argument list;
- upstream producer invocation does not use a shell;
- artifact data cannot alter the executable path or arguments.

### Schema Registry Tests

`M18SchemaRegistryTests` must verify:

- the registry path is exact;
- the registry is valid UTF-8 JSON;
- the registry root fields are exact;
- the registry declares exactly twenty-four records;
- the exact twenty-four identifiers are present;
- identifier ordering is deterministic;
- identifiers are unique;
- formal schema paths are unique;
- producer bindings are valid;
- producer versions are valid;
- artifact formats are valid;
- identification bases are valid;
- measurement contours are valid;
- Observatory mode values are valid;
- every referenced formal schema exists;
- an independently constructed duplicate identifier is rejected;
- an independently constructed unknown identifier is rejected;
- a path containing `..` is rejected;
- an absolute schema path is rejected.

### Formal Schema Tests

`M18FormalSchemaTests` must verify every registered formal schema with:

`Draft202012Validator.check_schema`

The tests must also verify:

- `$schema` is exact;
- `$id` is exact;
- every `$id` is unique;
- every `$id` uses the required FRP URN;
- every local reference resolves offline;
- no schema requires network retrieval;
- registered identifiers and formal schema identities match;
- required fields are represented;
- optional fields remain optional;
- additional-field behavior is explicit;
- exact enums preserve upstream values;
- canonical ternary enums use `-1`, `0`, and `1`;
- `+1` is absent from canonical state labels;
- booleans are not accepted as ternary integers;
- malformed representative instances are rejected;
- canonical representative instances are accepted.

The tests must not weaken a formal schema to make a canonical fixture pass.

### Canonical Artifact Tests

`M18CanonicalArtifactTests` must verify the exact committed artifact sets.

The tests must independently declare and compare:

- eleven structured-output paths;
- two benchmark-matrix paths;
- six comparative benchmark paths;
- ten M15 export paths;
- ten M15 vector-package paths.

For every canonical artifact, the tests must verify:

- the exact case-sensitive path;
- regular-file status;
- nonzero byte length;
- registered format;
- exact identity basis;
- exact producer binding;
- exact measurement contour;
- formal schema validity when applicable;
- raw-byte digest relation;
- source-byte preservation.

### Structured-Output Tests

The canonical artifact tests must verify:

- default structured output;
- `free` trace output;
- `7/1` trace output;
- `1/7` trace output;
- default self-test output;
- `free` self-test output;
- `7/1` self-test output;
- `1/7` self-test output;
- scaling output for `8` cells;
- scaling output for `16` cells;
- scaling output for `32` cells.

The tests must verify:

- exact schema identity;
- exact scheduler mode;
- tick ordering;
- trace ordering;
- state-domain membership;
- retained-state relations;
- pending-route relations;
- scheduler-counter relations;
- transition-capacity relations;
- invariant vectors;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`.

### Benchmark-Matrix Tests

The tests must verify:

- benchmark JSON formal-schema validity;
- exact row count;
- exact row order;
- exact architecture identities;
- exact scheduler-mode identities;
- exact comparison values;
- exact CSV header;
- exact CSV column count;
- exact CSV row order;
- exact JSON-to-CSV field correspondence;
- numeric-value preservation;
- deterministic CSV serialization;
- one final LF byte.

JSON and CSV must be parsed independently before their cross-format relation is checked.

### Comparative Benchmark Tests

The tests must verify the exact source paths:

- `benchmarks/architecture_comparison/profiles/workload_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/normalized_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/thermal_proxy_profile_v1.json`;
- `benchmarks/architecture_comparison/profiles/hardware_sensitivity_cost_profile_v1.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76.json`;
- `benchmarks/architecture_comparison/results/reference_comparison_seed_76_hardware_sensitivity_v1.json`.

The tests must verify:

- exact schema or registry-bound identity;
- workload binding;
- profile binding;
- declared digest relations;
- architecture order;
- scenario order;
- recorded rankings;
- operation-count preservation;
- thermal-proxy preservation;
- contour separation.

The tests must not derive a physical-chip claim.

### M15 Export Tests

For each of the ten M15 JSON exports, the tests must verify:

- exact filename;
- exact schema identifier;
- exact artifact kind;
- exact version;
- exact producer command;
- formal schema validity;
- deterministic regeneration;
- byte equality with the committed file.

The encoding-map tests must independently verify:

| State | Code | Encoded integer |
|---:|---|---:|
| `-1` | `11` | `3` |
| `0` | `00` | `0` |
| `1` | `01` | `1` |
| reserved | `10` | `2` |

The reserved value must not be accepted as a canonical processor state.

### M15 Vector-Package Tests

The tests must independently declare the exact ten-member package.

They must verify:

- exact member count;
- exact filename set;
- exact lexicographic order;
- exact header format;
- exact trace kinds;
- exact scheduler bindings;
- exact preload root fields;
- exact preload array lengths;
- packed-state consistency;
- canonical ternary membership;
- exact Q30 lookup-table entry count;
- contiguous lookup-table indices;
- exact nine-member internal SHA-256 manifest;
- internal self-exclusion;
- raw-byte digest equality;
- descriptor filename equality;
- descriptor byte-length equality;
- descriptor digest equality;
- deterministic package digest equality.

Negative package fixtures must independently test:

- one missing member;
- one unexpected member;
- one renamed member;
- one duplicate record;
- one altered member;
- one incorrect digest;
- one internal self-entry;
- one invalid state code;
- one scheduler mismatch;
- one lookup-table ordering violation.

### Manifest Tests

`M18ManifestTests` must verify:

- exact manifest path;
- exact schema identifier;
- exact root identity;
- exact closed publication scope;
- lexicographic record ordering;
- unique paths;
- safe relative paths;
- exact filename derivation;
- regular-file targets;
- exact artifact classes;
- exact formats;
- exact identification bases;
- exact schema bindings;
- exact producer bindings;
- exact measurement contours;
- exact byte lengths;
- exact raw-byte SHA-256 values;
- exact `artifact_count`;
- exact `artifact_set_sha256`;
- `canonical = true`;
- `mutable = false`;
- self-exclusion;
- deterministic serialization.

Negative manifest fixtures must test:

- absolute path rejection;
- parent-component rejection;
- backslash rejection;
- duplicate path rejection;
- symbolic-link rejection;
- unknown schema rejection;
- wrong producer rejection;
- wrong contour rejection;
- incorrect byte length;
- incorrect digest;
- incorrect ordering;
- self-binding;
- environment-dependent fields.

### Qualification Record Tests

`M18QualificationRecordTests` must verify:

- exact qualification-record path;
- formal schema validity;
- exact root identity;
- exact registry binding;
- exact manifest binding;
- exact artifact-set binding;
- stable check identifiers;
- unique `(check_id, subject_path)` pairs;
- valid categories;
- valid outcomes;
- valid severity relations;
- deterministic check ordering;
- exact aggregate counters;
- `overall_status = "PASS"`;
- zero failed checks;
- zero warnings;
- zero not-evaluated checks;
- deterministic serialization.

An independently altered check vector must prove that inconsistent aggregate counters or status are rejected.

### Self-Test Record Tests

`M18SelfTestRecordTests` must invoke:

`python frp_m18_canonical_artifacts.py --self-test --output json`

The tests must verify:

- exit code `0`;
- empty diagnostic standard error;
- valid UTF-8 JSON standard output;
- exact schema identity;
- exact root identity;
- exact thirty-four case identifiers;
- exact lexicographic case order;
- no duplicate case;
- `case_count = 34`;
- `passed_count = 34`;
- `failed_count = 0`;
- `overall_status = "PASS"`;
- every case has `status = "PASS"`;
- byte equality with the committed self-test record.

### Determinism Tests

`M18DeterminismTests` must create two independent temporary output roots.

The producer must generate the complete M18 generated set into both roots.

The tests must compare recursively:

- relative path sets;
- file counts;
- byte lengths;
- raw bytes;
- SHA-256 digests.

The two generated trees must be byte-identical.

Every generated canonical file must also be byte-identical to its committed counterpart.

The tests must independently run qualification twice and compare the emitted JSON bytes.

The tests must independently run self-test twice and compare the emitted JSON bytes.

### Security Boundary Tests

`M18SecurityBoundaryTests` must prove rejection of:

- an output path escaping through `..`;
- an absolute artifact path;
- a symbolic-link target;
- an unregistered write target;
- an artifact-provided executable path;
- an artifact-provided command option;
- an unresolved remote schema reference;
- executable object deserialization;
- non-finite JSON numbers;
- a timestamp in a deterministic record;
- a hostname in a deterministic record;
- a temporary absolute path in canonical output.

The tests must verify that the producer never uses:

`shell = True`

The tests must not execute SystemVerilog or artifact contents.

### Failure Preservation Tests

For every tested failure path, the suite must verify:

- nonzero exit status;
- no partial canonical output;
- no changed committed source byte;
- no changed committed digest;
- no write outside the temporary output root;
- no network access;
- stable diagnostic classification.

### Test Output Contract

The isolated M18 test command must finish with:

`OK`

The complete repository test command must finish with:

`OK`

Skipped tests are not permitted for M18 closure.

Expected failures are not permitted for M18 closure.

Warnings must not substitute for failed assertions.

### Test Qualification

M18 test qualification requires:

1. Python source compilation succeeds;
2. the isolated M18 suite succeeds;
3. the complete repository suite succeeds;
4. the exact thirty-four internal self-tests pass;
5. all formal schemas pass Draft 2020-12 validation;
6. all canonical fixtures pass their registered validators;
7. all required negative cases are rejected;
8. both generated trees are byte-identical;
9. generated and committed artifacts are byte-identical;
10. repeated qualification output is byte-identical;
11. repeated self-test output is byte-identical;
12. repository source bytes remain unchanged.

Any test-contract violation fails M18 qualification.

## M18 Workflow Contract

The M18 qualification workflow is:

`.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml`

The exact workflow name is:

`FRP M18 Formal Schema and Canonical Artifacts`

The workflow qualifies formal schemas, canonical artifacts, deterministic regeneration, tests, manifests, qualification records, and repository immutability.

### Workflow Triggers

The workflow must run on:

- push to `main` affecting the M18 boundary;
- pull requests to `main` affecting the M18 boundary;
- manual `workflow_dispatch`.

The path filter must include:

- `frp_prototype_v1_7_0.py`;
- `frp_m18_canonical_artifacts.py`;
- `requirements.txt`;
- `schemas/m18/**`;
- `artifacts/m18/**`;
- `benchmarks/architecture_comparison/**`;
- `tests/test_frp_m18_canonical_artifacts.py`;
- `docs/m18_formal_schema_canonical_artifact_publication_contract.md`;
- `docs/m18_formal_schema_canonical_artifact_publication_qualification.md`;
- `docs/m18_formal_schema_canonical_artifact_publication_closure.md`;
- `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml`.

Changes outside this path set remain covered by their existing workflows.

### Workflow Permissions

The workflow permission boundary is:

`contents: read`

The workflow must not request:

- `contents: write`;
- pull-request write access;
- issue write access;
- package publication access;
- release publication access;
- deployment access;
- identity-token access.

The workflow must not commit, push, tag, create a release, or modify a pull request.

### Workflow Concurrency

The concurrency group is:

`frp-m18-formal-schema-canonical-artifacts-${{ github.ref }}`

The workflow must declare:

`cancel-in-progress: false`

A running qualification must not be silently replaced by a newer run.

### Qualified Runner

The qualified runner is:

`ubuntu-latest`

The qualified Python version is:

`3.12`

The workflow must use:

- `actions/checkout@v5`;
- `actions/setup-python@v6`;
- `actions/upload-artifact@v4`.

Checkout must use:

`persist-credentials: false`

### Job Identity

The exact job identifier is:

`m18-formal-schema-canonical-artifacts`

The exact job name is:

`M18 Formal Schema and Canonical Artifact Qualification`

The job timeout is:

`30 minutes`

### Deterministic Environment

The job environment must declare:

| Variable | Value |
|---|---|
| `M18_EVIDENCE_DIR` | `/tmp/frp_m18_qualification_evidence` |
| `M18_GENERATION_A` | `/tmp/frp_m18_generation_a` |
| `M18_GENERATION_B` | `/tmp/frp_m18_generation_b` |
| `PYTHONHASHSEED` | `0` |
| `PYTHONDONTWRITEBYTECODE` | `1` |
| `PYTHONUNBUFFERED` | `1` |
| `PYTHONUTF8` | `1` |
| `LC_ALL` | `C.UTF-8` |
| `TZ` | `UTC` |

Canonical outputs must not depend on these values for semantic content.

The environment fixes execution variability and supports deterministic comparison.

### Dependency Installation

The workflow must:

1. display the Python version;
2. upgrade `pip`;
3. install `requirements.txt`;
4. verify that `jsonschema` is exactly version `4.25.1`;
5. verify availability of `Draft202012Validator`.

`requirements.txt` must contain the exact M18 validator pin:

`jsonschema==4.25.1`

A missing or different validator version fails before schema validation.

### Evidence-Directory Preparation

The workflow must recreate the three exact temporary directories:

- `${M18_EVIDENCE_DIR}`;
- `${M18_GENERATION_A}`;
- `${M18_GENERATION_B}`.

Before deletion or creation, each resolved path must:

- be absolute;
- begin with `/tmp/frp_m18_`;
- not equal `/tmp`;
- not equal `/`;
- not contain a symbolic-link component.

The workflow must not delete a repository directory.

### Source Compilation

The workflow must compile:

- `frp_prototype_v1_7_0.py`;
- `frp_m18_canonical_artifacts.py`;
- `tests/test_frp_m18_canonical_artifacts.py`.

The exact command class is:

`python -m compileall -q`

Any syntax, indentation, or import error fails immediately.

### Independent Self-Test Pair

The workflow must execute:

`python frp_m18_canonical_artifacts.py --self-test --output json`

twice.

The outputs must be written to:

- `${M18_EVIDENCE_DIR}/self-test-a.json`;
- `${M18_EVIDENCE_DIR}/self-test-b.json`.

The two files must be byte-identical.

Both files must be byte-identical to:

`artifacts/m18/manifests/canonical-artifact-self-test.json`

The workflow must verify:

- `case_count = 34`;
- `passed_count = 34`;
- `failed_count = 0`;
- `overall_status = "PASS"`.

### Independent Generation Pair

The workflow must execute:

`python frp_m18_canonical_artifacts.py --generate --repository-root . --output-root "${M18_GENERATION_A}"`

and:

`python frp_m18_canonical_artifacts.py --generate --repository-root . --output-root "${M18_GENERATION_B}"`

The two output roots must be independent.

The workflow must not copy generation A into generation B.

### Generated-Tree Comparison

The workflow must recursively compare generation A and generation B.

The comparison must verify:

- identical relative path sets;
- identical file counts;
- identical byte lengths;
- byte-identical file contents;
- no symbolic links;
- no unexpected files.

A filename-only or digest-only comparison is insufficient.

Raw-byte equality is required.

### Committed-Tree Comparison

The generated M18 artifact tree must be compared with:

`artifacts/m18/`

The comparison must prove that every generated canonical artifact is byte-identical to its committed counterpart.

The committed tree must contain no additional unregistered M18 artifact.

Registry and formal schemas remain under:

`schemas/m18/`

They are validated separately and are not copied into the generated artifact tree.

### Schema Registry Validation

The workflow must verify:

- registry formal-schema validity;
- exact twenty-four-entry closure;
- unique identifiers;
- unique formal schema paths;
- exact `$id` bindings;
- offline reference resolution;
- absence of unregistered schemas;
- absence of remote schema retrieval.

All formal schemas must pass:

`Draft202012Validator.check_schema`

### Committed Verification

The workflow must execute:

`python frp_m18_canonical_artifacts.py --verify --repository-root . --output text`

The command must return exit code `0`.

The text output must report:

- registry status;
- formal schema status;
- canonical artifact status;
- manifest status;
- qualification-record status;
- self-test-record status;
- overall `PASS`.

### Independent Qualification Pair

The workflow must execute:

`python frp_m18_canonical_artifacts.py --qualify --repository-root . --output json`

twice.

The outputs must be written to:

- `${M18_EVIDENCE_DIR}/qualification-a.json`;
- `${M18_EVIDENCE_DIR}/qualification-b.json`.

The two qualification outputs must be byte-identical.

Both files must be byte-identical to:

`artifacts/m18/manifests/canonical-artifact-qualification.json`

The workflow must verify:

- `check_count > 0`;
- `passed_count = check_count`;
- `failed_count = 0`;
- `warning_count = 0`;
- `not_evaluated_count = 0`;
- `overall_status = "PASS"`.

### Isolated M18 Test Suite

The workflow must execute:

`python -m unittest discover -s tests -p 'test_frp_m18_canonical_artifacts.py' -v`

The command must complete with:

`OK`

Skipped tests and expected failures are not accepted for M18 closure.

### Complete Repository Test Suite

The workflow must execute:

`python -m unittest discover -s tests -p 'test_*.py' -v`

The command must complete with:

`OK`

M18 must not regress M16, M17, comparative benchmark, structured-output, or existing semantic-reference tests.

### Repository Immutability Check

After generation, validation, qualification, and tests, the workflow must execute:

`git diff --exit-code`

It must also verify that:

`git status --porcelain`

is empty.

Any tracked modification or unexpected untracked file inside the repository fails qualification.

All workflow-generated evidence must remain under the registered `/tmp` directories.

### Evidence Artifact

After every qualification step succeeds, the workflow must upload:

- `${M18_EVIDENCE_DIR}/self-test-a.json`;
- `${M18_EVIDENCE_DIR}/self-test-b.json`;
- `${M18_EVIDENCE_DIR}/qualification-a.json`;
- `${M18_EVIDENCE_DIR}/qualification-b.json`;
- `${M18_GENERATION_A}/artifacts/m18/`.

The exact uploaded artifact name is:

`frp-m18-formal-schema-canonical-artifacts`

The retention period is:

`30 days`

The uploaded workflow artifact is qualification evidence.

It is not a GitHub release and does not change the committed canonical source files.

### Network Boundary

Network use is limited to:

- GitHub Action retrieval;
- repository checkout;
- Python dependency installation;
- evidence upload.

The M18 producer, schema validator, artifact validator, test suite, and qualification commands must perform no network retrieval.

Formal schema references must resolve entirely from committed local files.

### Failure Behavior

Any failed step must stop the job.

The workflow must not:

- repair a committed artifact;
- update a digest;
- rewrite a schema;
- commit generated output;
- continue publication after failed qualification;
- mark a partial result as PASS.

Failure logs may identify the failed check and subject path.

They must not replace machine-readable qualification evidence.

### Workflow Success Conditions

The workflow succeeds only when:

1. dependencies and exact validator version are verified;
2. all Python sources compile;
3. both self-test outputs are byte-identical;
4. all thirty-four self-test cases pass;
5. all formal schemas are valid Draft 2020-12 schemas;
6. the registry closes at exactly twenty-four identifiers;
7. generation A and generation B are byte-identical;
8. generated artifacts match committed artifacts;
9. committed verification passes;
10. both qualification outputs are byte-identical;
11. every qualification check passes;
12. the isolated M18 test suite passes;
13. the complete repository test suite passes;
14. repository source bytes remain unchanged;
15. the evidence package uploads successfully.

Any workflow-contract violation fails M18 qualification.

## Downstream Compatibility Boundary

M18 establishes a one-way machine-readable publication boundary.

The integration direction is:

`Fractal-Resonance-Processor → published artifacts → downstream consumers`

FRP remains the sole authority for processor semantics, published metric values, scheduler behavior, transition routing, invariants, and qualification evidence.

### Repository Independence

FRP Trace Observatory remains a separate downstream repository.

The FRP repository must not import:

- Observatory source code;
- Observatory parsers;
- Observatory validators;
- Observatory UI dependencies;
- Observatory release metadata;
- Observatory test fixtures;
- Observatory version constants.

Observatory must not become a runtime or qualification dependency of FRP.

### Exact Observatory Mode Vocabulary

The supported downstream mode values are:

- `artifact_auditor`;
- `ternary_transition_visualizer`;
- `trace_explorer`.

Every `observatory_modes` array must:

- contain only these values;
- contain no duplicate value;
- be ordered lexicographically;
- contain at least one value.

The public mode names remain:

- Artifact Auditor;
- Ternary Transition Visualizer;
- Trace Explorer.

### Registry Authority

The M18 supported-schema registry is the upstream authority for:

- exact schema identifier;
- exact format identity;
- formal schema path;
- artifact format;
- artifact role;
- identification basis;
- producer path;
- producer version;
- measurement contour;
- eligible Observatory modes.

Downstream support must be declared against exact registry records.

A downstream consumer must not infer compatibility from filename similarity alone.

### Artifact Auditor Eligibility

`artifact_auditor` may be registered for:

- formal schemas;
- schema registries;
- JSON artifacts;
- CSV artifacts;
- headered vectors;
- headered traces;
- package-role text vectors;
- canonical manifests;
- qualification records;
- self-test records.

Eligibility permits read-only identification and validation.

It does not permit arbitrary code execution or semantic reinterpretation.

### Trace Explorer Eligibility

`trace_explorer` may be registered only for artifacts containing an ordered processor trace or a deterministic trace projection.

Eligible data may include:

- ordered ticks;
- per-cell trace rows;
- scheduler state;
- scheduler counters;
- retained ternary state;
- phase-derived targets;
- accepted requests;
- rejected requests;
- pending routes;
- transition-capacity telemetry;
- switching-load telemetry;
- thermal-state telemetry;
- coherence quantities;
- pressure quantities;
- invariant vectors.

A non-trace summary artifact must not be marked as Trace Explorer input solely because it contains aggregate counters.

### Ternary Transition Visualizer Eligibility

`ternary_transition_visualizer` may be registered only for artifacts containing transition, route, scheduler, request-lane, state-encoding, or invariant evidence.

Eligible data may include:

- canonical states `-1`, `0`, and `1`;
- active neutral state `0`;
- `-1 → 0 → 1`;
- `1 → 0 → -1`;
- first-leg neutralization;
- retained pending polarity;
- pending-route completion;
- scheduler deferral;
- transition-capacity deferral;
- accepted request lanes;
- rejected request lanes;
- `actual_direct_events`;
- `reserved_state_events`;
- `queue_overflow_events`;
- invariant flags.

A visualizer may render these relations.

It must not create alternative transition semantics.

### Raw Source Preservation

A downstream consumer must capture the exact source bytes before parsing.

The downstream provenance record must contain:

- source filename;
- source repository path, when known;
- exact schema or format identifier;
- producer version;
- raw-byte SHA-256 digest;
- downstream load timestamp;
- validation status;
- validation messages.

The downstream load timestamp is Observatory metadata.

It must not be inserted into or written over the upstream artifact.

### Normalized Representation Boundary

A downstream normalized representation must remain separate from:

- source bytes;
- source digest;
- source path;
- upstream schema identity;
- published values.

Normalization may:

- expose typed fields;
- create indexes;
- attach source locations;
- support filtering;
- support deterministic display ordering.

Normalization must not:

- replace an upstream value;
- change a metric definition;
- change a scheduler state;
- change a ternary state;
- complete a missing field through inference;
- merge distinct benchmark contours;
- overwrite provenance.

### Derived View Label

Every computed downstream representation must be labelled:

`Observatory-derived view`

A derived view may calculate display coordinates, filtering indexes, grouped counters, or visual layout.

It must preserve direct links to the source artifact and source locations used for the derivation.

A derived view must not be presented as an upstream FRP artifact.

### Digest Verification

When a source artifact is listed in the M18 canonical artifact manifest, the downstream consumer must compare:

- repository path, when available;
- filename;
- byte length;
- SHA-256 digest;
- schema or format identity.

A digest mismatch must be reported before semantic visualization.

A downstream consumer must not normalize source bytes and then claim that the normalized digest is the upstream artifact digest.

### Formal Schema Use

A downstream consumer may use the committed M18 formal schemas for validation.

It must preserve:

- exact `$id`;
- exact upstream schema identifier;
- Draft 2020-12 behavior;
- required fields;
- optional fields;
- enum values;
- numeric constraints;
- additional-field rules.

A downstream consumer must not modify an upstream formal schema and continue reporting the original `$id`.

A downstream extension requires its own identifier and must not replace the upstream schema.

### Registry-Bound Artifact Use

Schema-free artifacts must remain identified through their exact registry binding.

The downstream consumer must not inject an invented `schema` field into the source artifact.

Registry-bound validation must use:

- exact path;
- exact filename;
- exact role;
- exact format;
- exact producer;
- exact producer version;
- enclosing manifest relation.

### Unknown Artifact Handling

An unknown or unsupported artifact may be:

- captured as immutable raw bytes;
- assigned a source digest;
- reported as unrecognized;
- presented to Artifact Auditor as unsupported input.

It must not be:

- assigned a guessed schema;
- parsed using a similar registered schema;
- displayed as a qualified trace;
- merged with a supported artifact set;
- used to create an FRP semantic claim.

### Version Independence

FRP and FRP Trace Observatory have independent version cycles.

An Observatory version must not automatically copy the FRP release version.

Compatibility must be declared using:

- supported FRP release;
- exact schema identifiers;
- exact format identifiers;
- exact producer versions;
- exact artifact roles.

An older schema remains an older supported version.

It must not be renamed automatically to an M18 or Observatory version.

### Canonical Fixture Transfer

A canonical fixture transferred into a downstream repository must retain:

- exact upstream filename;
- exact upstream repository path in provenance;
- exact raw bytes;
- exact byte length;
- exact SHA-256 digest;
- exact schema or format identity;
- exact producer binding.

The downstream copy must be verified against the M18 manifest.

A changed copy is a different artifact and must not retain canonical-fixture status.

### Measurement-Contour Separation

Downstream consumers must preserve separate presentation and filtering for:

- operation count;
- thermal proxy;
- transition pressure;
- `heat_peak`;
- switching load;
- scheduler timing;
- latency;
- throughput;
- RTL execution;
- FPGA preparation;
- physical measurements.

The presence of similarly named fields does not authorize cross-contour aggregation.

### Scheduler Separation

The scheduler modes remain:

- `free`;
- `7/1`;
- `1/7`.

They must not be presented as equivalent traces.

The downstream consumer must preserve their exact state vocabularies and counter relations.

### M16 Boundary

M18 does not publish machine-readable M16 RTL execution or FPGA preparation schemas.

Those artifacts remain outside the M18 formal-schema and canonical-artifact set.

Machine-readable M16 publication is assigned to M19.

M18 must not:

- invent an M16 schema;
- convert M16 prose evidence into an undeclared canonical schema;
- classify FPGA preparation as physical-chip evidence;
- merge RTL execution with Python semantic-reference execution.

### No Reverse Integration

Observatory must not write into the FRP repository.

Observatory must not modify:

- canonical artifacts;
- formal schemas;
- manifests;
- qualification records;
- benchmark results;
- deterministic vectors;
- producer sources.

Any future upstream link to Observatory requires a separate explicit FRP change.

### Security Boundary

Downstream consumption must treat every published artifact as data.

Artifact analysis must not execute:

- embedded commands;
- Python code;
- shell text;
- SystemVerilog;
- file paths as commands;
- serialized executable objects;
- remote schema references.

Validation must remain read-only.

### AI Scope Exclusion

The M18 downstream boundary does not include:

- an AI inference engine;
- a training pipeline;
- autonomous agent logic;
- semantic mutation;
- adaptive processor execution;
- new FRP execution claims.

A future FRP-based AI project remains outside both M18 and Observatory scope.

### Downstream Qualification Requirements

M18 qualification must prove:

1. the mode vocabulary is exact;
2. registry mode arrays contain only registered values;
3. mode arrays are unique and lexicographically ordered;
4. every trace-mode assignment corresponds to trace-capable data;
5. every visualizer assignment corresponds to transition-capable data;
6. every published artifact remains eligible for Artifact Auditor;
7. source bytes and normalized representations remain distinct;
8. provenance fields remain available;
9. raw-byte digest scope is explicit;
10. schema-free artifacts retain registry-bound identity;
11. unknown artifacts cannot acquire guessed compatibility;
12. measurement contours remain separate;
13. scheduler modes remain separate;
14. no M16 machine-readable schema is invented;
15. no physical-chip claim is derived from FPGA preparation;
16. no downstream dependency enters the FRP runtime;
17. the integration direction remains one-way.

Any downstream-boundary violation fails M18 qualification.

## M18 Closure Gates

M18 closure is evidence-driven. Contract publication, implementation completion, qualification, closure, version assignment, and release publication are separate states.

### Status Semantics

The permitted M18 milestone states are:

- `PLANNED`: the technical contract exists, but the complete implementation evidence does not yet exist;
- `IMPLEMENTED`: the required schemas, artifacts, producer, tests, and workflow exist, but successful qualification evidence has not yet been recorded;
- `QUALIFIED`: every mandatory local and workflow gate has passed for one exact repository commit;
- `CLOSED`: the qualification and closure records have been committed and bind the qualified implementation to the exact evidence commit.

No state transition is automatic.

Publication of this contract does not qualify or close M18.

The M18 version target is `v2.0.0`. It must not be represented as the current FRP release until M18 is qualified, closed, and explicitly released.

Until that explicit release action occurs, the current published FRP release remains `FRP v1.8.0 / M16`.

### Required Implementation Evidence

M18 implementation must contain:

- this complete technical contract;
- the canonical-state assertion-text correction in the existing M15 producer;
- the M18 formal schema directory;
- all 24 exact registry identifiers;
- the formal schema registry;
- the 11 canonical structured-output artifacts;
- the canonical benchmark-matrix JSON artifact;
- the canonical benchmark-matrix CSV artifact;
- the six existing comparative benchmark artifacts validated in place;
- the 10 canonical M15 JSON exports;
- the 10 canonical M15 deterministic vector-package members;
- the canonical artifact manifest;
- the canonical artifact qualification record;
- the canonical artifact self-test record;
- `frp_m18_canonical_artifacts.py`;
- `tests/test_frp_m18_canonical_artifacts.py`;
- `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml`.

A missing required path, artifact, schema, record, producer mode, test, or workflow step prevents M18 qualification.

### Contract Gate

The contract gate passes only when:

- every M18 path is defined exactly once;
- every schema identifier is defined exactly once;
- every producer command is explicit;
- required and optional fields are distinguishable;
- artifact-set membership is closed and deterministic;
- measurement contours remain separate;
- scheduler modes remain separate;
- raw-byte provenance remains distinct from derived views;
- M18 does not introduce processor semantics;
- M18 does not include M16 machine-readable execution qualification assigned to M19.

Conflicting definitions or duplicate authoritative declarations fail the gate.

### Formal Schema Gate

The formal schema gate passes only when:

- every registered schema document is valid JSON;
- every schema document uses JSON Schema Draft 2020-12;
- every schema document has its exact declared `$id`;
- every `$id` follows the M18 URN contract;
- every registry identifier resolves to exactly one formal schema document;
- every formal schema document is represented by exactly one registry record;
- all references resolve offline within the repository;
- required fields, optional fields, types, enums, bounds, and structural constraints match the corresponding producer contract;
- no historical identifier is silently renamed or reversioned;
- the registry closes at exactly 24 identifiers.

An unresolved reference, duplicate identity, undocumented identity, or identity mismatch fails the gate.

### Canonical Artifact Gate

The canonical artifact gate passes only when:

- every required canonical artifact exists at its exact contract path;
- every generated JSON artifact is valid JSON;
- every CSV artifact matches its exact column and ordering contract;
- every M15 vector member matches its exact text-format contract;
- every declared schema identifier is recognized by the M18 registry;
- every artifact validates against its applicable formal schema or exact format validator;
- every manifest record matches the source filename, path, byte length, and raw-byte SHA-256 digest;
- the six comparative benchmark artifacts are validated at their existing upstream paths and are not copied into a competing authority;
- no artifact from another measurement contour is substituted for a required artifact;
- source artifacts remain unchanged after validation.

A missing member, undeclared member, misplaced artifact, validation failure, or source-byte mutation fails the gate.

### Determinism Gate

The determinism gate passes only when:

- two independent M18 generation runs produce byte-identical canonical output trees;
- two independent self-test runs produce byte-identical JSON records;
- two independent qualification runs produce byte-identical JSON records after excluding no fields;
- manifest ordering follows the exact contract;
- JSON serialization follows the exact contract;
- CSV serialization follows the exact contract;
- M15 vector serialization follows the exact contract;
- every artifact digest is stable across independent runs;
- every artifact-set digest is stable across independent runs;
- the M15 deterministic vector package has the exact package digest `703dd4b56f4b34289a2c5bc5521ad4ddc3113bdec8c38238c3244c69cb4d58df`.

A nondeterministic timestamp, environment-dependent path, unstable ordering, or digest mismatch fails the gate.

### Semantic Invariance Gate

The semantic invariance gate passes only when:

- the canonical processor domain remains `-1, 0, 1`;
- state `0` remains an active neutral state;
- opposite-polarity routes remain `-1 → 0 → 1` and `1 → 0 → -1`;
- the `free` scheduler mode remains unrestricted;
- the `7/1` scheduler mode remains seven `balance` ticks followed by one `commit` tick;
- the `1/7` scheduler mode remains one `excite` tick followed by seven `neutralize` ticks;
- retained state, pending polarity, request acceptance, request rejection, scheduler deferral, and transition-capacity deferral retain their published meanings;
- published metric values are not rewritten;
- measurement contours are not merged;
- no target-independent FPGA preparation evidence is represented as physical-chip evidence.

Any semantic reinterpretation, scheduler substitution, metric substitution, or unsupported physical claim fails the gate.

### Downstream Compatibility Gate

The downstream compatibility gate passes only when:

- the integration direction remains FRP to published artifacts to downstream consumers;
- FRP remains the sole authority for processor semantics;
- the supported Observatory mode values remain exactly `artifact_auditor`, `ternary_transition_visualizer`, and `trace_explorer`;
- every registry record declares only applicable downstream modes;
- original artifact bytes remain independently available from normalized or derived views;
- schema identity, producer identity, source digest, and validation status remain recoverable;
- unknown identifiers remain unsupported rather than being guessed;
- Observatory versioning remains independent from FRP versioning;
- no downstream parser, UI dependency, or release dependency is introduced into the qualified FRP boundary.

A reverse dependency, inferred schema, altered artifact, or downstream semantic override fails the gate.

### Self-Test Gate

The self-test gate passes only when:

- `python frp_m18_canonical_artifacts.py --self-test` exits with status `0`;
- `python frp_m18_canonical_artifacts.py --self-test --output json` exits with status `0`;
- both invocations evaluate the same 34 defined cases;
- the JSON record declares `case_count` as `34`;
- the JSON record declares `passed_case_count` as `34`;
- the JSON record declares `failed_case_count` as `0`;
- the JSON record declares `overall_status` as `PASS`;
- the emitted self-test record matches the committed canonical self-test artifact byte for byte.

A skipped mandatory case, unexpected case, failed case, unstable result, or record mismatch fails the gate.

### Test Gate

The test gate passes only when:

- all M18 Python sources compile under Python 3.12;
- the isolated M18 test module passes with zero failures and zero errors;
- the complete repository test suite passes with zero failures and zero errors;
- all existing M15, M16, and M17 regression tests remain passing;
- every required positive test succeeds;
- every required negative test rejects the invalid input;
- no test mutates a committed upstream source artifact;
- the working tree remains unchanged after test execution.

A regression, untested mandatory relation, unexpected mutation, skipped mandatory test, failure, or error fails the gate.

### Workflow Gate

The workflow gate passes only when:

- the exact M18 workflow exists on the qualified commit;
- the workflow runs on GitHub Actions for that exact commit;
- every mandatory workflow step executes;
- every mandatory workflow step succeeds;
- the workflow conclusion is `success`;
- the uploaded qualification evidence corresponds to the same commit;
- the workflow records the exact commit SHA;
- the repository remains unchanged after workflow execution;
- no required result depends solely on an uncommitted local run.

Local PASS results do not replace workflow evidence.

A cancelled, skipped, neutral, timed-out, action-required, stale, or failed workflow run does not qualify M18.

### Qualification Record Gate

After all technical gates pass, the qualification document must be created at:

`docs/m18_formal_schema_canonical_artifact_publication_qualification.md`

It must record:

- the exact qualified commit SHA;
- the exact workflow name;
- the exact workflow run number;
- the exact workflow run identifier;
- the workflow event;
- the workflow conclusion;
- the Python version;
- the pinned `jsonschema` version;
- schema-registry validation results;
- canonical artifact validation results;
- deterministic comparison results;
- self-test results;
- isolated test results;
- complete test-suite results;
- repository-immutability results;
- final qualification status.

The qualification status may be `PASS` only when every mandatory gate passes for the same commit.

### Closure Record Gate

After the qualification document is committed, the closure document must be created at:

`docs/m18_formal_schema_canonical_artifact_publication_closure.md`

It must bind:

- the M18 milestone identity;
- the `v2.0.0` version target;
- the qualified implementation commit;
- the qualification-evidence commit;
- the qualification workflow evidence;
- the canonical schema-registry identity;
- the canonical artifact-manifest identity;
- the canonical qualification-record identity;
- the canonical self-test-record identity;
- all unresolved exclusions assigned to later milestones;
- the final milestone status.

The closure status may be `CLOSED` only when the qualification record reports `PASS` and every referenced path exists in the closure commit.

### Release Boundary

M18 closure does not automatically:

- create a Git tag;
- create a GitHub release;
- replace the current published FRP release;
- qualify M19;
- qualify M20 through M30;
- add machine-readable M16 execution qualification;
- establish physical implementation evidence;
- qualify FRP Trace Observatory.

An FRP `v2.0.0` release requires a separate explicit release action after M18 closure.

### Failure Rule

Failure of any mandatory gate leaves M18 in `PLANNED` or `IMPLEMENTED` state.

Partial PASS results must not be aggregated into a qualified or closed status.

A later correction invalidates prior evidence whenever the correction changes:

- a formal schema;
- the schema registry;
- a canonical artifact;
- a producer;
- a digest;
- a validator;
- a required test;
- the qualification workflow;
- a qualification or closure record.

Affected gates must then be rerun against the corrected commit.

Until every gate passes, M18 remains planned or implemented and must not be represented as qualified, closed, or released.

## M18 Closure Gates

M18 closure is evidence-driven. Contract publication, implementation completion, qualification, closure, version assignment, and release publication are separate states.

### Status Semantics

The permitted M18 milestone states are:

- `PLANNED`: the technical contract exists, but the complete implementation evidence does not yet exist;
- `IMPLEMENTED`: the required schemas, artifacts, producer, tests, and workflow exist, but successful qualification evidence has not yet been recorded;
- `QUALIFIED`: every mandatory local and workflow gate has passed for one exact repository commit;
- `CLOSED`: the qualification and closure records have been committed and bind the qualified implementation to the exact evidence commit.

No state transition is automatic.

Publication of this contract does not qualify or close M18.

The M18 version target is `v2.0.0`. It must not be represented as the current FRP release until M18 is qualified, closed, and explicitly released.

Until that explicit release action occurs, the current published FRP release remains `FRP v1.8.0 / M16`.

### Required Implementation Evidence

M18 implementation must contain:

- this complete technical contract;
- the canonical-state assertion-text correction in the existing M15 producer;
- the M18 formal schema directory;
- all 24 exact registry identifiers;
- the formal schema registry;
- the 11 canonical structured-output artifacts;
- the canonical benchmark-matrix JSON artifact;
- the canonical benchmark-matrix CSV artifact;
- the six existing comparative benchmark artifacts validated in place;
- the 10 canonical M15 JSON exports;
- the 10 canonical M15 deterministic vector-package members;
- the canonical artifact manifest;
- the canonical artifact qualification record;
- the canonical artifact self-test record;
- `frp_m18_canonical_artifacts.py`;
- `tests/test_frp_m18_canonical_artifacts.py`;
- `.github/workflows/frp-m18-formal-schema-canonical-artifacts.yml`.

A missing required path, artifact, schema, record, producer mode, test, or workflow step prevents M18 qualification.

### Contract Gate

The contract gate passes only when:

- every M18 path is defined exactly once;
- every schema identifier is defined exactly once;
- every producer command is explicit;
- required and optional fields are distinguishable;
- artifact-set membership is closed and deterministic;
- measurement contours remain separate;
- scheduler modes remain separate;
- raw-byte provenance remains distinct from derived views;
- M18 does not introduce processor semantics;
- M18 does not include M16 machine-readable execution qualification assigned to M19.

Conflicting definitions or duplicate authoritative declarations fail the gate.

### Formal Schema Gate

The formal schema gate passes only when:

- every registered schema document is valid JSON;
- every schema document uses JSON Schema Draft 2020-12;
- every schema document has its exact declared `$id`;
- every `$id` follows the M18 URN contract;
- every registry identifier resolves to exactly one formal schema document;
- every formal schema document is represented by exactly one registry record;
- all references resolve offline within the repository;
- required fields, optional fields, types, enums, bounds, and structural constraints match the corresponding producer contract;
- no historical identifier is silently renamed or reversioned;
- the registry closes at exactly 24 identifiers.

An unresolved reference, duplicate identity, undocumented identity, or identity mismatch fails the gate.

### Canonical Artifact Gate

The canonical artifact gate passes only when:

- every required canonical artifact exists at its exact contract path;
- every generated JSON artifact is valid JSON;
- every CSV artifact matches its exact column and ordering contract;
- every M15 vector member matches its exact text-format contract;
- every declared schema identifier is recognized by the M18 registry;
- every artifact validates against its applicable formal schema or exact format validator;
- every manifest record matches the source filename, path, byte length, and raw-byte SHA-256 digest;
- the six comparative benchmark artifacts are validated at their existing upstream paths and are not copied into a competing authority;
- no artifact from another measurement contour is substituted for a required artifact;
- source artifacts remain unchanged after validation.

A missing member, undeclared member, misplaced artifact, validation failure, or source-byte mutation fails the gate.

### Determinism Gate

The determinism gate passes only when:

- two independent M18 generation runs produce byte-identical canonical output trees;
- two independent self-test runs produce byte-identical JSON records;
- two independent qualification runs produce byte-identical JSON records after excluding no fields;
- manifest ordering follows the exact contract;
- JSON serialization follows the exact contract;
- CSV serialization follows the exact contract;
- M15 vector serialization follows the exact contract;
- every artifact digest is stable across independent runs;
- every artifact-set digest is stable across independent runs;
- the M15 deterministic vector package has the exact package digest `703dd4b56f4b34289a2c5bc5521ad4ddc3113bdec8c38238c3244c69cb4d58df`.

A nondeterministic timestamp, environment-dependent path, unstable ordering, or digest mismatch fails the gate.

### Semantic Invariance Gate

The semantic invariance gate passes only when:

- the canonical processor domain remains `-1, 0, 1`;
- state `0` remains an active neutral state;
- opposite-polarity routes remain `-1 → 0 → 1` and `1 → 0 → -1`;
- the `free` scheduler mode remains unrestricted;
- the `7/1` scheduler mode remains seven `balance` ticks followed by one `commit` tick;
- the `1/7` scheduler mode remains one `excite` tick followed by seven `neutralize` ticks;
- retained state, pending polarity, request acceptance, request rejection, scheduler deferral, and transition-capacity deferral retain their published meanings;
- published metric values are not rewritten;
- measurement contours are not merged;
- no target-independent FPGA preparation evidence is represented as physical-chip evidence.

Any semantic reinterpretation, scheduler substitution, metric substitution, or unsupported physical claim fails the gate.

### Downstream Compatibility Gate

The downstream compatibility gate passes only when:

- the integration direction remains FRP to published artifacts to downstream consumers;
- FRP remains the sole authority for processor semantics;
- the supported Observatory mode values remain exactly `artifact_auditor`, `ternary_transition_visualizer`, and `trace_explorer`;
- every registry record declares only applicable downstream modes;
- original artifact bytes remain independently available from normalized or derived views;
- schema identity, producer identity, source digest, and validation status remain recoverable;
- unknown identifiers remain unsupported rather than being guessed;
- Observatory versioning remains independent from FRP versioning;
- no downstream parser, UI dependency, or release dependency is introduced into the qualified FRP boundary.

A reverse dependency, inferred schema, altered artifact, or downstream semantic override fails the gate.

### Self-Test Gate

The self-test gate passes only when:

- `python frp_m18_canonical_artifacts.py --self-test` exits with status `0`;
- `python frp_m18_canonical_artifacts.py --self-test --output json` exits with status `0`;
- both invocations evaluate the same 34 defined cases;
- the JSON record declares `case_count` as `34`;
- the JSON record declares `passed_case_count` as `34`;
- the JSON record declares `failed_case_count` as `0`;
- the JSON record declares `overall_status` as `PASS`;
- the emitted self-test record matches the committed canonical self-test artifact byte for byte.

A skipped mandatory case, unexpected case, failed case, unstable result, or record mismatch fails the gate.

### Test Gate

The test gate passes only when:

- all M18 Python sources compile under Python 3.12;
- the isolated M18 test module passes with zero failures and zero errors;
- the complete repository test suite passes with zero failures and zero errors;
- all existing M15, M16, and M17 regression tests remain passing;
- every required positive test succeeds;
- every required negative test rejects the invalid input;
- no test mutates a committed upstream source artifact;
- the working tree remains unchanged after test execution.

A regression, untested mandatory relation, unexpected mutation, skipped mandatory test, failure, or error fails the gate.

### Workflow Gate

The workflow gate passes only when:

- the exact M18 workflow exists on the qualified commit;
- the workflow runs on GitHub Actions for that exact commit;
- every mandatory workflow step executes;
- every mandatory workflow step succeeds;
- the workflow conclusion is `success`;
- the uploaded qualification evidence corresponds to the same commit;
- the workflow records the exact commit SHA;
- the repository remains unchanged after workflow execution;
- no required result depends solely on an uncommitted local run.

Local PASS results do not replace workflow evidence.

A cancelled, skipped, neutral, timed-out, action-required, stale, or failed workflow run does not qualify M18.

### Qualification Record Gate

After all technical gates pass, the qualification document must be created at:

`docs/m18_formal_schema_canonical_artifact_publication_qualification.md`

It must record:

- the exact qualified commit SHA;
- the exact workflow name;
- the exact workflow run number;
- the exact workflow run identifier;
- the workflow event;
- the workflow conclusion;
- the Python version;
- the pinned `jsonschema` version;
- schema-registry validation results;
- canonical artifact validation results;
- deterministic comparison results;
- self-test results;
- isolated test results;
- complete test-suite results;
- repository-immutability results;
- final qualification status.

The qualification status may be `PASS` only when every mandatory gate passes for the same commit.

### Closure Record Gate

After the qualification document is committed, the closure document must be created at:

`docs/m18_formal_schema_canonical_artifact_publication_closure.md`

It must bind:

- the M18 milestone identity;
- the `v2.0.0` version target;
- the qualified implementation commit;
- the qualification-evidence commit;
- the qualification workflow evidence;
- the canonical schema-registry identity;
- the canonical artifact-manifest identity;
- the canonical qualification-record identity;
- the canonical self-test-record identity;
- all unresolved exclusions assigned to later milestones;
- the final milestone status.

The closure status may be `CLOSED` only when the qualification record reports `PASS` and every referenced path exists in the closure commit.

### Release Boundary

M18 closure does not automatically:

- create a Git tag;
- create a GitHub release;
- replace the current published FRP release;
- qualify M19;
- qualify M20 through M30;
- add machine-readable M16 execution qualification;
- establish physical implementation evidence;
- qualify FRP Trace Observatory.

An FRP `v2.0.0` release requires a separate explicit release action after M18 closure.

### Failure Rule

Failure of any mandatory gate leaves M18 in `PLANNED` or `IMPLEMENTED` state.

Partial PASS results must not be aggregated into a qualified or closed status.

A later correction invalidates prior evidence whenever the correction changes:

- a formal schema;
- the schema registry;
- a canonical artifact;
- a producer;
- a digest;
- a validator;
- a required test;
- the qualification workflow;
- a qualification or closure record.

Affected gates must then be rerun against the corrected commit.

Until every gate passes, M18 remains planned or implemented and must not be represented as qualified, closed, or released.
