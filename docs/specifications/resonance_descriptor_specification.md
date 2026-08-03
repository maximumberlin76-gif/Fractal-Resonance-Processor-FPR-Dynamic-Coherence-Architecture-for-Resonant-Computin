# TR-EIF Resonance Descriptor Specification

## Document Status

This document is the normative specification governing resonance descriptors in the **TR-EIF — Ternary Resonant Equivariant Interatomic Framework**.

It defines:

- the boundary between continuous resonance state and derived descriptors;
- descriptor ownership;
- descriptor classes;
- units and dimensional status;
- normalization requirements;
- local and global descriptor semantics;
- E(3) transformation behavior;
- permutation behavior;
- temporal sampling;
- descriptor validation;
- request-generation boundaries;
- energy-conditioning boundaries;
- serialization and trace requirements;
- deterministic replay;
- validation and conformance criteria.

This document defines descriptor interfaces and semantic requirements.

It does not define one universal resonance equation, coupling matrix, phase-lag value, threshold set, normalization coefficient, or material-specific parameterization.

## Normative Language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** define normative requirements within this specification.

## Scientific Provenance

### CLASSICAL

The following structures are classified as `CLASSICAL`:

- oscillator phase;
- angular frequency;
- natural frequency;
- effective frequency;
- phase difference;
- wrapped phase difference;
- coupling strength;
- phase lag;
- complex order parameter;
- coherence magnitude;
- collective phase;
- local and global oscillator statistics;
- graph-weighted aggregation;
- time sampling;
- continuous observables.

### TR-EIF EXTENSION

The following structures are classified as `TR-EIF EXTENSION`:

- use of validated resonance descriptors as inputs to ternary request generation;
- use of validated resonance descriptors as conditioning inputs to an equivariant interatomic model;
- separation of resonance state, descriptor record, requested ternary state, and executed ternary state;
- descriptor provenance linked to configuration, graph, continuous-state, and update identities;
- explicit E(3) and permutation contracts for resonance-conditioned atomic descriptors;
- descriptor freezing during one ternary request and physical-evaluation interval;
- synchronized resonance, ternary, energy, and trace identities;
- rejection of undeclared descriptor thresholds and implicit normalization;
- prohibition of converting descriptor failure into state `0`.

The classical oscillator quantities retain their established mathematical meanings.

TR-EIF defines how such quantities enter the continuous-discrete and interatomic architecture.

## Source Basis

The classical source basis includes:

- Yoshiki Kuramoto, “Self-Entrainment of a Population of Coupled Non-Linear Oscillators,” *Lecture Notes in Physics*, volume 39, 1975, pages 420–422, DOI `10.1007/BFb0013365`.
- Hidetsugu Sakaguchi and Yoshiki Kuramoto, “A Soluble Active Rotator Model Showing Phase Transitions via Mutual Entrainment,” *Progress of Theoretical Physics*, volume 76, issue 3, 1986, pages 576–581, DOI `10.1143/PTP.76.576`.

Additional classical and application-specific sources are controlled through:

`docs/references/kuramoto_sakaguchi_sources.md`

## Dependencies

This specification depends on:

- `README.md`
- `docs/README.md`
- `docs/architecture/framework_architecture.md`
- `docs/architecture/continuous_discrete_contract.md`
- `docs/architecture/energy_model_contract.md`
- `docs/architecture/determinism_contract.md`
- `docs/specifications/ternary_state_specification.md`
- `docs/specifications/transition_semantics.md`
- `docs/specifications/neutral_routing_specification.md`

All dependent artifacts MUST preserve the definitions and invariants established by those documents.

## Scope

This specification applies to:

- global oscillator descriptors;
- local oscillator descriptors;
- per-atom resonance descriptors;
- per-edge resonance descriptors;
- per-oscillator descriptors;
- per-channel resonance descriptors;
- batched descriptor records;
- continuous-to-ternary request generation;
- resonance-conditioned equivariant features;
- resonance-conditioned energy evaluation;
- transition traces;
- deterministic replay;
- multiscale resonance observables.

This specification does not define:

- one universal oscillator population;
- one universal interaction topology;
- one universal numerical integrator;
- one universal descriptor vector;
- one universal threshold map;
- one universal physical interpretation;
- one universal FLiBe resonance parameterization.

A concrete TR-EIP model MUST declare the descriptor subset it implements.

## Continuous Resonance State

The continuous resonance state contains variables evolved directly by the selected resonance model.

It MAY contain:

- oscillator phases;
- natural angular frequencies;
- effective angular frequencies;
- coupling parameters;
- phase-lag parameters;
- oscillator weights;
- continuous memory variables;
- integrator state;
- application-specific continuous variables.

A continuous resonance state is not itself a descriptor record.

The state contains primary or retained dynamic variables.

A descriptor record contains quantities derived from a declared state snapshot.

## Resonance Descriptor

A resonance descriptor is a declared quantity derived from:

- a validated continuous resonance state;
- a validated interaction graph;
- a validated atomic configuration;
- declared model parameters;
- a declared temporal sampling rule.

Every descriptor MUST have:

- a unique semantic name;
- a mathematical definition;
- an input domain;
- an output domain;
- an owner;
- a shape;
- an ordering;
- units or explicit dimensionless status;
- a normalization rule;
- a transformation type;
- a sampling identity;
- a validity domain;
- a numerical representation;
- an invalid-value policy.

A numerical value without these properties is not a complete TR-EIF resonance descriptor.

## Descriptor Record

A descriptor record is an immutable collection of validated resonance descriptors derived from one declared evaluation snapshot.

A descriptor record MUST contain or reference:

- schema identity;
- specification version;
- descriptor-record identity;
- model identity;
- configuration identity;
- graph identity;
- continuous-state identity;
- continuous update index;
- ternary update index where applicable;
- sampling time or sampling index;
- descriptor definitions;
- descriptor values;
- units;
- shapes;
- owner mappings;
- normalization metadata;
- transformation metadata;
- numerical precision;
- validation status.

## Descriptor Lifecycle

The controlled descriptor lifecycle is:

1. validate retained continuous state;
2. generate candidate continuous state;
3. validate candidate continuous state;
4. evaluate descriptor candidates;
5. validate descriptor candidates;
6. create immutable descriptor record;
7. generate ternary requests or conditioned features;
8. use the same record throughout the declared evaluation interval;
9. commit or abort the coupled cycle.

A descriptor candidate MUST NOT be used by downstream layers before validation.

## Descriptor Ownership

Every descriptor MUST have a declared owner type.

Permitted owner types MAY include:

- model;
- configuration;
- atom;
- graph node;
- graph edge;
- oscillator;
- feature channel;
- spatial region;
- batch member.

Ownership determines:

- shape;
- ordering;
- permutation behavior;
- aggregation rules;
- trace identity.

A descriptor MUST NOT be applied to an owner different from the one declared without an explicit controlled mapping.

## Descriptor Classes

TR-EIF recognizes the following descriptor classes:

- phase descriptors;
- frequency descriptors;
- phase-difference descriptors;
- coupling descriptors;
- phase-lag descriptors;
- coherence descriptors;
- temporal descriptors;
- regime descriptors;
- graph-aggregated descriptors;
- application-specific descriptors.

A concrete model MAY implement a subset.

Every implemented descriptor MUST belong to a declared class or define a new class through a controlled specification update.

## Phase Descriptors

A phase descriptor represents oscillator phase information.

The canonical phase symbol is:

`θ`

An oscillator phase belongs to the unit circle.

The storage convention MUST declare:

- angular unit;
- canonical interval;
- wrapping rule;
- owner;
- ordering;
- numerical precision.

A phase stored outside the canonical interval MUST be wrapped or rejected according to the declared convention.

The wrapping operation MUST be deterministic.

## Angular Unit

The canonical angular unit SHOULD be radians.

A model using another angular unit MUST declare the conversion explicitly.

Angles are dimensionless in dimensional analysis but MUST retain their angular-unit metadata in serialized scientific records.

## Phase-Origin Invariance

For oscillator models in which only phase differences are physically relevant, a uniform phase shift applied to every oscillator MUST NOT change phase-difference or coherence-magnitude descriptors.

A concrete descriptor specification MUST declare whether global phase origin is physically relevant.

Global phase-origin invariance MUST NOT be claimed without validation.

## Phase-Difference Descriptor

A phase-difference descriptor represents the angular difference between two declared oscillator phases.

The raw difference is:

`θ_j - θ_i`

A wrapped phase difference applies the declared wrapping rule to that raw difference.

Every phase-difference descriptor MUST declare:

- source oscillator identities;
- orientation from `i` to `j`;
- wrapping interval;
- angular unit;
- graph-edge identity where applicable;
- sign convention;
- ordering.

Reversing edge direction changes the sign of an oriented phase difference before wrapping.

## Natural-Frequency Descriptor

A natural-frequency descriptor represents the intrinsic angular-frequency parameter assigned to an oscillator by the declared model.

It MUST declare:

- angular-frequency unit;
- owner;
- parameter source;
- parameter version;
- physical or learned status;
- validity domain.

A natural frequency is a model input or parameter.

It MUST NOT be mislabeled as an observed effective frequency.

## Effective-Frequency Descriptor

An effective-frequency descriptor represents the declared instantaneous, averaged, or fitted rate of phase evolution under coupling and other modeled effects.

It MUST declare whether it is:

- instantaneous;
- finite-difference;
- time-window averaged;
- fitted;
- filtered.

It MUST also declare:

- time interval;
- angular-frequency unit;
- numerical method;
- owner;
- uncertainty where estimated.

Different effective-frequency definitions MUST NOT share one semantic name.

## Frequency-Mismatch Descriptor

A frequency-mismatch descriptor compares two declared frequencies.

The comparison MUST identify:

- the two frequency quantities;
- subtraction or absolute-difference convention;
- sign convention;
- unit;
- owner;
- temporal sampling;
- normalization when used.

An absolute mismatch and a signed mismatch are different descriptors.

## Coupling Descriptor

A coupling descriptor represents a declared interaction quantity between oscillators or oscillator populations.

It MAY describe:

- scalar coupling strength;
- edge coupling;
- local aggregate coupling;
- global aggregate coupling;
- learned coupling;
- geometry-conditioned coupling.

Every coupling descriptor MUST declare:

- source and target ownership;
- sign convention;
- units;
- symmetry or asymmetry;
- graph dependence;
- normalization;
- update rule;
- validity domain.

A coupling matrix MUST NOT be assumed symmetric unless symmetry is declared and validated.

## Phase-Lag Descriptor

A phase-lag descriptor represents the declared angular lag associated with an interaction.

It MUST declare:

- angular unit;
- owner;
- edge direction where applicable;
- constant, state-dependent, or learned status;
- update rule;
- wrapping convention;
- validity domain.

A global phase lag and an edge-dependent phase lag are distinct descriptor structures.

## Global Coherence Magnitude

The classical global coherence magnitude is the modulus of the arithmetic mean of the oscillator unit phasors.

Under the standard normalized definition, its range is:

`0 ≤ global_coherence ≤ 1`

The descriptor is dimensionless.

A value near `0` indicates weak resultant phase alignment under that definition.

A value near `1` indicates strong resultant phase alignment under that definition.

These statements concern the standard order-parameter magnitude.

They do not prove dynamical stability, complete frequency locking, or physical resonance in an application-specific system.

## Collective Phase

The collective phase is the argument of the global complex order parameter when that order parameter has nonzero magnitude.

It MUST declare:

- angular unit;
- canonical interval;
- undefined or low-magnitude behavior;
- numerical tolerance;
- sampling identity.

When the coherence magnitude is numerically indistinguishable from zero under the declared tolerance, the collective phase MUST NOT be treated as reliably defined.

## Local Coherence

A local coherence descriptor summarizes phase alignment within a declared neighborhood.

It MUST declare:

- central owner;
- neighbor set;
- graph identity;
- edge weights;
- weight sign restrictions;
- normalization;
- handling of zero total weight;
- angular convention;
- output range when claimed.

A local coherence range of `0` to `1` may be claimed only when the declared construction guarantees that range.

Signed, complex, or unnormalized weights require a separately declared interpretation.

## Weighted Coherence

A weighted coherence descriptor MUST declare:

- weight source;
- weight units;
- non-negativity or signed status;
- normalization;
- zero-weight behavior;
- graph directionality;
- aggregation order.

A weighted descriptor MUST NOT be described as a probability unless probability axioms are satisfied.

## Graph-Local Descriptor

A graph-local descriptor belongs to one node or edge and depends only on its declared graph neighborhood.

It MUST preserve:

- graph identity;
- owner identity;
- neighbor ordering;
- periodic-image identity where applicable;
- cutoff policy;
- deterministic aggregation order.

A graph rebuild that changes ownership or ordering invalidates the previous graph-local descriptor record unless an explicit remapping is performed.

## Global Descriptor

A global descriptor belongs to one complete configuration or oscillator population.

It MUST declare:

- population definition;
- included entities;
- weights;
- exclusions;
- normalization;
- batch membership;
- reduction order.

A global descriptor MUST NOT silently combine independent batch members.

## Temporal Descriptor

A temporal descriptor depends on more than one time or update point.

It MUST declare:

- input time interval;
- sampling frequency;
- window length;
- weighting;
- endpoint convention;
- missing-sample handling;
- initial-window behavior;
- uncertainty where applicable.

A temporal descriptor MUST NOT read future data in an online execution mode unless that mode explicitly permits non-causal processing.

## Instantaneous Descriptor

An instantaneous descriptor is evaluated from one declared state snapshot.

Its record MUST identify the exact snapshot and update index.

An instantaneous descriptor MUST NOT be described as time-averaged.

## Window-Averaged Descriptor

A window-averaged descriptor MUST declare:

- window start;
- window end;
- included samples;
- weighting;
- normalization;
- correlation treatment;
- update alignment.

Changing the window requires a new descriptor identity.

## Regime Descriptor

A regime descriptor classifies or scores a declared resonance regime.

A regime descriptor MUST declare:

- source descriptors;
- classification rule;
- output domain;
- threshold values;
- boundary handling;
- hysteresis;
- uncertainty or confidence interpretation;
- training or calibration source where learned.

A regime label is not a theorem about system stability.

It is an output of the declared classification rule.

## Descriptor Vector

A descriptor vector is an ordered collection of individually defined descriptors.

It MUST declare:

- component names;
- component order;
- component units;
- component normalization;
- component owners;
- shape;
- version.

Components with different physical units MUST NOT be combined arithmetically without explicit normalization or dimensional treatment.

A descriptor vector version MUST change when component meaning or order changes.

## Normalization

Normalization converts a descriptor into a declared scaled representation.

Every normalization MUST declare:

- source descriptor;
- source unit;
- normalization operation;
- reference value or statistics;
- output domain;
- fitting data where applicable;
- handling of zero scale;
- clipping policy;
- version.

Normalization parameters are result-affecting model artifacts.

They MUST be immutable or content-addressed for deterministic replay.

## Prohibited Implicit Normalization

The following are prohibited:

- undocumented division by system size;
- undocumented division by neighbor count;
- undocumented standardization;
- undocumented clipping;
- undocumented min-max scaling;
- undocumented unit conversion;
- batch-dependent normalization during deterministic inference unless declared.

## Clipping

A descriptor MAY be clipped only when the clipping rule is explicitly declared.

The record MUST preserve:

- unclipped value where required for audit;
- lower bound;
- upper bound;
- clipping event;
- reason;
- version.

Clipping MUST NOT conceal descriptor-domain failure.

## Missing Descriptor

A missing descriptor is not numerical zero.

A missing descriptor MUST:

- prevent dependent request generation or energy conditioning; or
- be processed through an explicit controlled missing-data rule.

A missing descriptor MUST NOT be converted automatically to:

- `0`;
- ternary state `0`;
- a mean value;
- a previous value;
- a default threshold value.

## Invalid Descriptor

A descriptor is invalid when it violates its declared:

- type;
- shape;
- owner;
- ordering;
- unit;
- domain;
- finite-value requirement;
- normalization contract;
- transformation contract.

An invalid descriptor MUST NOT be used by downstream layers.

## Non-Finite Values

NaN and infinite descriptor values MUST be rejected unless a separate diagnostic schema explicitly permits them as failure evidence.

They MUST NOT enter:

- ternary request generation;
- equivariant conditioning;
- energy evaluation;
- physical observables;
- committed state.

## E(3) Transformation Contract

Every descriptor MUST declare its behavior under the selected geometric group action.

Permitted categories include:

- invariant scalar;
- equivariant vector;
- equivariant tensor;
- non-geometric internal variable;
- frame-dependent application variable.

A descriptor without declared transformation behavior MUST NOT condition an E(3)-equivariant model.

## Internal Scalar Resonance Descriptors

Oscillator phase, angular frequency, phase lag, coherence magnitude, and ternary-request scores are ordinarily non-geometric scalar variables.

A rigid transformation of the atomic coordinate frame SHOULD NOT change these values when their construction depends only on geometrically invariant inputs.

If geometry enters the resonance model, the complete descriptor construction MUST preserve the declared transformation behavior.

## Per-Atom Permutation Behavior

A per-atom descriptor MUST follow atom-index permutation.

If atom ordering changes, the descriptor array MUST be reordered identically.

The numerical descriptor value remains attached to its owning atom.

## Per-Edge Permutation Behavior

A per-edge descriptor MUST follow the declared edge reordering.

It MUST preserve:

- source atom;
- target atom;
- periodic-image relation;
- edge direction;
- descriptor orientation.

An edge descriptor MUST NOT be interpreted without its graph identity.

## Scalar Request Invariance

A scalar ternary request generated from an E(3)-equivalent configuration MUST remain unchanged when all descriptor inputs are declared invariant.

Frame-dependent changes in a scalar requested state are prohibited unless a controlled application contract explicitly defines frame dependence.

## Request-Generation Boundary

A resonance descriptor MAY enter the ternary request-generation operator only after validation.

The controlled sequence is:

1. continuous state;
2. descriptor evaluation;
3. descriptor validation;
4. immutable descriptor record;
5. request generation;
6. requested ternary state;
7. transition evaluation;
8. executed ternary state.

The descriptor layer MUST NOT directly write:

- retained ternary state;
- executed ternary state;
- route status.

## Request Mapping Requirements

A request mapping using resonance descriptors MUST declare:

- descriptor components;
- component versions;
- normalization;
- thresholds;
- equality behavior;
- hysteresis;
- retained-state dependence;
- route-context dependence;
- tie handling;
- invalid-input handling;
- output ownership;
- deterministic scope.

No numerical threshold is defined by this specification.

Thresholds require source, derivation, calibration, or reproducible optimization evidence.

## Descriptor Failure and State 0

Descriptor failure is not an explicit request for state `0`.

When a required descriptor fails:

- no valid requested state is produced;
- no ternary transition occurs;
- retained state remains authoritative;
- the cycle is aborted or handled through an explicit failure contract.

## Energy-Conditioning Boundary

A resonance descriptor MAY condition an energy model only when:

- the descriptor is valid;
- the descriptor identity is recorded;
- its transformation type is compatible;
- its differentiation mode is declared;
- its executed ternary-state context is consistent;
- its validity domain includes the current evaluation.

## Descriptor Freezing

The descriptor record used for one request generation or physical evaluation MUST remain immutable for that evaluation interval.

Energy, forces, and stress associated with one energy-evaluation identity MUST use the same descriptor record.

A descriptor update MUST wait until the next declared update boundary.

## Differentiation Status

Every descriptor used by the energy model MUST be classified as:

- fixed during physical differentiation;
- differentiably connected to configuration or cell variables;
- externally controlled and fixed.

The classification MUST be recorded.

A descriptor MUST NOT be described as differentiable merely because its implementation uses floating-point arithmetic.

## Descriptor Trace

A descriptor trace MUST contain or reference:

- descriptor-record identity;
- source continuous-state identity;
- configuration identity;
- graph identity;
- update indices;
- owner mappings;
- component names;
- component order;
- values;
- units;
- normalization metadata;
- transformation metadata;
- precision;
- validation status;
- downstream request or energy identities.

## Deterministic Descriptor Evaluation

For identical:

- continuous-state snapshot;
- configuration;
- graph;
- model parameters;
- descriptor definitions;
- ordering;
- precision;
- execution environment;

descriptor evaluation MUST produce results consistent with the declared determinism scope.

## Reduction Determinism

Descriptor reductions MUST use a declared ordering or deterministic reduction method.

This applies to:

- global coherence;
- local coherence;
- weighted means;
- frequency statistics;
- occupancy statistics;
- temporal averages;
- histogram-like descriptors.

Unordered container iteration MUST NOT define authoritative reduction order.

## Batched Descriptor Records

A batched descriptor record MUST preserve independent system boundaries.

It MUST declare:

- batch size;
- system ordering;
- per-system owners;
- padding;
- masks;
- segment offsets;
- reduction scope.

Padding and masks MUST remain separate from state `0`.

A global descriptor MUST NOT aggregate across batch members unless cross-system aggregation is explicitly defined.

## Multiscale Transfer

A resonance descriptor transferred to a coarser scale becomes a declared observable or field.

The transfer record MUST identify:

- source descriptor;
- source scale;
- target scale;
- aggregation;
- units;
- normalization;
- uncertainty;
- spatial support;
- temporal support;
- validity domain.

A coarse resonance observable is not automatically a microscopic oscillator state.

## Validation Requirements

A conforming implementation MUST validate:

1. descriptor definition;
2. source-state identity;
3. owner identity;
4. shape;
5. ordering;
6. units;
7. finite numerical values;
8. normalization;
9. transformation behavior;
10. sampling identity;
11. descriptor-vector component order;
12. request-mapping compatibility;
13. energy-conditioning compatibility;
14. descriptor freezing;
15. deterministic replay;
16. trace completeness.

## Required Phase Tests

The test suite MUST verify:

- phase-unit declaration;
- deterministic phase wrapping;
- canonical interval handling;
- phase-owner alignment;
- uniform phase-shift behavior for descriptors claiming phase-origin invariance.

## Required Frequency Tests

The suite MUST verify:

- natural and effective frequency separation;
- unit consistency;
- signed and absolute mismatch distinction;
- temporal sampling;
- finite-value validation;
- deterministic ordering.

## Required Coherence Tests

The suite MUST verify:

- population identity;
- weight identity;
- normalization;
- output range when claimed;
- zero-weight behavior;
- phase-shift behavior;
- permutation consistency;
- batch separation.

## Required E(3) Tests

The suite MUST verify the declared transformation class for every geometry-dependent descriptor.

For descriptors declared invariant, tests MUST include applicable:

- translations;
- rotations;
- reflections when E(3) is claimed;
- atom permutations.

## Required Request-Boundary Tests

The suite MUST verify:

- descriptor validation precedes request generation;
- invalid descriptors cannot produce a request;
- missing descriptors do not produce state `0`;
- requested state remains distinct from descriptor values;
- request mapping returns only `-1/0/1`;
- thresholds and ties follow the declared mapping.

## Required Energy-Boundary Tests

The suite MUST verify:

- only validated descriptors enter energy evaluation;
- descriptor identity remains fixed during one energy and derivative evaluation;
- energy, force, and stress reference the same descriptor record;
- differentiation status is respected;
- descriptor transformation behavior preserves model equivariance.

## Required Determinism Tests

Repeated identical descriptor evaluations MUST reproduce the declared:

- logical descriptor structure;
- owner ordering;
- component ordering;
- numerical values within tolerance;
- normalized record;
- byte identity where claimed.

## Required Failure Tests

The suite MUST test:

- missing continuous state;
- invalid continuous state;
- graph mismatch;
- owner mismatch;
- shape mismatch;
- ordering mismatch;
- unit mismatch;
- NaN;
- infinity;
- invalid normalization;
- unsupported transformation type;
- stale descriptor record;
- invalid descriptor version.

Every failure MUST prevent dependent state commitment when the descriptor is required.

## Schema Targets

The approved schema targets are:

- `schemas/resonance_state.schema.json`
- `schemas/observables.schema.json`
- `schemas/model_manifest.schema.json`
- `schemas/transition_trace.schema.json`

The continuous resonance-state schema stores primary dynamic state.

The observables schema MAY store validated descriptor outputs.

The model manifest MUST identify implemented descriptor versions.

The transition trace MUST reference the descriptor record used for request generation.

## Canonical Public Field Names

A descriptor record SHOULD use the following public field names where applicable:

- `descriptor_record_id`
- `descriptor_version`
- `continuous_state_id`
- `configuration_id`
- `graph_id`
- `continuous_update_index`
- `ternary_update_index`
- `owner_type`
- `owner_order`
- `components`
- `units`
- `normalization`
- `transformation_type`
- `precision`
- `validation_status`

Component-specific names MUST remain stable within one descriptor version.

## Implementation Ownership

The approved implementation target is:

`src/tr_eif/resonance/`

This package owns:

- resonance-state types;
- phase and frequency representations;
- descriptor evaluation;
- descriptor validation;
- descriptor records;
- descriptor normalization;
- deterministic descriptor ordering.

The approved package target:

`src/tr_eif/ternary/`

owns request generation from validated descriptors.

The approved package target:

`src/tr_eif/energy/`

owns energy conditioning using validated descriptor records.

The approved package target:

`src/tr_eif/observables/`

owns statistical and multiscale resonance observables.

## Non-Conforming Behaviors

An implementation is non-conforming if it:

- uses an undefined descriptor;
- omits descriptor units;
- omits descriptor ownership;
- changes descriptor ordering without versioning;
- silently normalizes descriptor values;
- silently clips descriptor values;
- converts missing descriptors to zero;
- converts descriptor failure to ternary state `0`;
- uses invalid descriptors for request generation;
- writes directly from a descriptor to retained ternary state;
- changes descriptors during one physical evaluation;
- combines independent batch members silently;
- claims coherence range without a construction guaranteeing that range;
- claims E(3)-invariance without testing;
- uses a geometry-dependent scalar descriptor that changes under coordinate-frame transformation;
- uses undeclared thresholds;
- permits NaN or infinity to enter downstream evaluation;
- claims deterministic replay without controlling reduction order;
- transfers a microscopic descriptor to a coarse model without an explicit transfer definition.

## Conformance Record

A resonance-descriptor implementation conformance record MUST identify:

- implementation version;
- applicable specification version;
- resonance-model identity;
- implemented descriptor classes;
- descriptor-vector version;
- owner types;
- units;
- normalization artifacts;
- transformation types;
- request-mapping compatibility;
- energy-conditioning compatibility;
- deterministic replay scope;
- schema versions;
- invariant-test suite;
- validation artifact identity;
- execution environment.

A conformance claim requires passing evidence.

Source code alone does not establish conformance.

## Acceptance Criteria

This specification is satisfied only when:

1. continuous resonance state and descriptor records remain distinct;
2. every descriptor has a complete definition;
3. every descriptor has declared ownership and ordering;
4. every descriptor has units or explicit dimensionless status;
5. every normalization rule is explicit;
6. phase wrapping is deterministic;
7. natural and effective frequencies remain distinct;
8. coherence claims match the implemented construction;
9. E(3) and permutation behavior are declared;
10. invalid and missing descriptors cannot reach downstream layers;
11. descriptor failure is not converted to state `0`;
12. request generation uses only validated descriptor records;
13. descriptors do not directly mutate retained or executed ternary state;
14. the request mapping returns only `-1/0/1`;
15. threshold values are declared and traceable;
16. energy conditioning uses a frozen descriptor record;
17. energy, force, and stress use the same descriptor identity;
18. deterministic reductions use controlled ordering;
19. batched records preserve system boundaries;
20. multiscale transfer preserves descriptor provenance;
21. traces preserve complete descriptor identity;
22. application-specific descriptors do not redefine TR-EIF core semantics.

## Related Controlled Documents

The following approved targets refine or depend on this specification:

- `docs/specifications/energy_output_specification.md`
- `docs/specifications/trace_specification.md`
- `docs/volume_02_ternary_resonance_theory/`
- `docs/volume_03_equivariant_interatomic_framework/`
- `docs/volume_07_flibe_reference_model/`
- `docs/validation/mathematical_validation_plan.md`
- `docs/validation/numerical_validation_plan.md`
- `docs/validation/invariant_validation_plan.md`
- `schemas/resonance_state.schema.json`
- `schemas/observables.schema.json`
- `schemas/model_manifest.schema.json`

Until a target file is committed, its path identifies an approved repository destination rather than an implemented artifact.

## Specification Closure

This document defines the complete resonance-descriptor interface of TR-EIF.

All mathematical, architectural, implementation, schema, test, trace, training, molecular-dynamics, multiscale, and application artifacts MUST preserve:

- explicit continuous-state provenance;
- defined descriptor semantics;
- dimensional and normalization control;
- declared E(3) behavior;
- deterministic ordering;
- validated request-generation input;
- frozen energy-conditioning records;
- active state `0`;
- zero direct opposite-state transitions;
- complete scientific traceability.
