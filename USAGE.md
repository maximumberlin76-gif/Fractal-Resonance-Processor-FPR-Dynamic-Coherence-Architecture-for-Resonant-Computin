# Fractal Resonance Processor (FRP)

**Ternary Fractal Resonant Coherence Processor**

## Usage

This document provides the current execution, verification, inspection, and replay paths for **FRP v3.3.0 / M31**.

## Release boundary

| Field | Current record |
|---|---|
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification | `PASS` |
| Focused M31 tests | `60 / 60 PASS` |
| Qualification checks | `13 / 13 PASS` |
| Canonical M31 outputs | `4 / 4 exact` |
| Preserved archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| RTL and FPGA implementation anchor | `M16 — PASS` |

M31 publishes deterministic evidence for relative-phase interference, active-zero routing, and separated thermal-measurement contours. The discrete state domain remains `-1/0/1`, and state `0` remains an active mediation, routing, retention, balancing, and transition-staging state.

## Requirements

- Python `3.12+`;
- the exact dependency declared in `requirements.txt`;
- a clean checkout when reproducing release evidence.

Install the repository dependency:

```
python -m pip install -r requirements.txt
```

## Run the executable semantic reference

Run the structured demo with the full trace:

```
python frp_prototype_v1_7_0.py --mode demo --output json --include-trace
```

Run the qualified semantic-reference self-test:

```
python frp_prototype_v1_7_0.py --mode self-test --output json
```

The semantic reference preserves the processor execution order:

`phase dynamics → relative-phase organization → ternary target → scheduler → request handling → active-zero routing → retained state`

The phase-derived target and executed retained state are separate processor states. Opposite-polarity requests use the tick-separated routes `-1 → 0 → 1` and `1 → 0 → -1`.

## Verify the committed M31 publication

Verify all four committed canonical outputs:

```
python frp_m31_phase_interference_thermal_evidence.py --verify
```

Expected result:

```
{"milestone":"M31","schema":"frp.m31.verification_result.v1","status":"PASS",...}
```

The verification command independently regenerates the expected records, compares their bytes with the committed publication, and removes its temporary verification tree.

## Run the deterministic M31 self-test

```
python frp_m31_phase_interference_thermal_evidence.py --self-test
```

The result records deterministic replay, active-zero computation, and separation of historical and current thermal contours.

## Run the focused M31 qualification

```
python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v
```

Recorded release result:

```
Ran 60 tests

OK
```

This command qualifies the focused M31 publication boundary. The repository-wide regression is reserved for the final documentation and release closure.

## Reproduce M31 into an isolated output tree

Create a fresh output directory and generate the four canonical records without changing the committed publication:

```
replay_root="$(mktemp -d)"
python frp_m31_phase_interference_thermal_evidence.py \
  --generate \
  --repository-root . \
  --output-root "$replay_root"
```

Generated paths:

- `schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`;
- `artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`;
- `artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`;
- `artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`.

Detailed clean-environment replay and byte-comparison commands are maintained in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Inspect the canonical M31 records

Format the evidence:

```
python -m json.tool \
  artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json
```

Format the manifest:

```
python -m json.tool \
  artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json
```

Format the qualification record:

```
python -m json.tool \
  artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json
```

## Published execution record

| Record | Value |
|---|---:|
| Execution records | `100` |
| Cell observations | `800` |
| Active-zero observations | `702` |
| Requested direct events | `5` |
| Prevented direct events | `5` |
| Neutral-routed events | `5` |
| Actual direct events | `0` |
| Reserved-state events | `0` |
| Queue-overflow events | `0` |
| Polarity-to-active-zero transitions | `5` |
| Active-zero-to-polarity transitions | `12` |
| Direct opposite-polarity transitions | `0` |
| Retained-same observations | `783` |

## Thermal evidence scope

The preserved FRP v0.9.3 model workload records a binary-style forced-switch `heat_peak` of `0.051000` and a distributed active-neutral ternary `heat_peak` of `0.003250`, with a ratio of `15.6923076923` and a relative reduction of `93.63%`.

These values are model thermal-load records for the exact historical workload. Historical `heat_peak`, current architecture-comparison data, normalized activity cost, and the RC temperature proxy remain separate measurement contours.

## FRP Trace Observatory boundary

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

The Observatory consumes committed FRP schemas, traces, evidence, manifests, registries, and qualification records through a one-way, read-only boundary. FRP remains the semantic and publication authority; downstream processing preserves the published bytes and declared measurement contours.

## Release records

- [FRP v3.3.0 validation index](FRP_VALIDATION_INDEX_v3_3_0.md)
- [FRP v3.3.0 release notes](RELEASE_NOTES_v3_3_0.md)
- [FRP v3.3.0 test report](TEST_REPORT_v3_3_0.md)
- [M31 schema](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json)
- [M31 evidence](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json)
- [M31 manifest](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json)
- [M31 qualification](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json)

## Historical usage record

The complete prior usage document is preserved below as an exact byte sequence. Its release-local “current” labels describe the historical FRP v1.8.0 / M16 boundary.

<details>
<summary>Open the complete historical USAGE.md through M16</summary>

<!-- Exact historical USAGE.md begins on the next line. -->
# Fractal Resonance Processor (FRP)

**Ternary Resonant Coherence Processor — Structured Output Prototype**

## Usage

This document defines how to run, inspect, validate, export, and reproduce the current Fractal Resonance Processor (FRP) executable reference.

FRP is a ternary resonant coherence processor.

Its computational mechanism combines resonant phase dynamics, coherence evolution, stateful feedback, and balanced ternary state retention.

The complete current processor path combines:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`cell phase and frequency state`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric Sakaguchi phase lag gamma`

↓

`hierarchical fractal coupling`

↓

`phase evolution`

↓

`resonance selection`

↓

`Kuramoto order parameter R`

↓

`multiscale phase-coherence evaluation`

↓

`delay dynamics`

↓

`local thermal-phase interaction`

↓

`local gamma drift`

↓

`nonlinear coherence compression`

↓

`dynamic stability C(t) - P(t)`

↓

`phase-derived ternary target`

↓

`distributed ternary commit`

↓

`mandatory tick-separated routing through active neutral state 0`

↓

`retained coherent ternary state`

The balanced ternary state and retained-result domain is:

`{-1, 0, 1}`

The active neutral state is:

`0`

Validated opposite-polarity routes are:

`-1 → 0 → 1`

`1 → 0 → -1`

Validated kernel invariant:

`actual_direct_events = 0`

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current M15 benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Inherited M15 semantic and implementation-mapping qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current M16 RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Current M16 FPGA preparation qualification workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Current test report:

`TEST_REPORT_v1_8_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

Current published validation status:

`PASS`

Inherited M15 validated self-test result:

`41/41 PASS`

Current M16 RTL workflow result:

`SUCCESS`

Current M16 RTL closure status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation workflow result:

`SUCCESS`

Current M16 FPGA preparation closure status:

`M16 FPGA PREPARATION LAYER CLOSED`

## 1. Processor Identity

The current executable form is:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

The word `prototype` identifies the current executable reference form.

The processor itself is defined by the complete resonant computational mechanism and the balanced ternary state-retention mechanism.

The processor identity is defined by the complete connected path from resonant phase dynamics to retained balanced ternary state.

The current executable reference contains:

- phase states;
- frequency states;
- Kuramoto-Sakaguchi interaction;
- asymmetric phase lag;
- hierarchical fractal coupling;
- phase evolution;
- global phase coherence;
- multiscale phase coherence;
- delay dynamics;
- distributed thermal state;
- thermal coupling degradation;
- local gamma drift;
- nonlinear coherence compression;
- dynamic stability evaluation;
- phase-derived ternary target formation;
- distributed commit;
- active neutral routing;
- retained ternary state;
- deterministic M15 hardware-facing semantic and implementation mapping.

The current M16 release layer contains:

- M16 RTL core realization and execution semantics;
- M16 target-independent FPGA preparation.

## 2. Two Connected Computational Domains

The FRP computational core contains two connected domains.

### 2.1 Resonant dynamic domain

The resonant dynamic domain contains:

- phase;
- frequency;
- coupling;
- phase lag;
- hierarchy;
- delay;
- thermal feedback;
- coherence;
- nonlinear compression;
- dynamic stability.

### 2.2 Balanced ternary state and retention domain

The ternary domain contains:

- states `{-1, 0, 1}`;
- active neutral state `0`;
- phase-derived ternary targets;
- distributed transition requests;
- transition-fraction limits;
- pending neutral routes;
- scheduler-controlled execution;
- retained ternary state.

The resonant dynamic domain drives the evolving computational process.

The balanced ternary domain provides the state, target, transition, and retained-result layer.

Together these domains form the complete FRP computational mechanism.

## 3. Complete Computational Chain

The current processor chain is:

`initial phase and frequency field`

↓

`current ternary state`

↓

`scheduler state`

↓

`pending neutral-route processing`

↓

`transition-request processing`

↓

`phase-derived ternary target extraction`

↓

`distributed transition-limit enforcement`

↓

`frequency-target formation`

↓

`delayed frequency response`

↓

`local generated power`

↓

`distributed thermal update`

↓

`local thermal overload`

↓

`correlated gamma-noise update`

↓

`local effective Sakaguchi phase lag`

↓

`thermal coupling-factor update`

↓

`hierarchical Kuramoto-Sakaguchi coupling field`

↓

`phase velocity`

↓

`phase evolution`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`nonlinear coherence compression`

↓

`C(t), P(t), and C(t) - P(t)`

↓

`structured telemetry`

↓

`next processor tick`

At each tick, ternary target extraction uses the current phase field before that tick's phase-field update.

Across successive ticks:

`evolved phase field`

↓

`next target-state decision`

↓

`distributed ternary transition`

↓

`retained state`

This preserves the dynamic relation between resonant phase evolution and ternary state formation.

## 4. Kuramoto-Sakaguchi Resonant Phase Layer

Each processor cell has:

- a phase;
- a base frequency;
- a frequency target;
- a current frequency;
- a local effective gamma value;
- a local thermal coupling factor.

The current phase interaction uses the Kuramoto-Sakaguchi relation:

`sin(phase_j - phase_i - gamma_effective_i)`

The interaction is weighted by:

- hierarchical coupling topology;
- local thermal coupling factors;
- nominal coupling strength.

Current default nominal phase lag:

`gamma = 0.30 × pi`

Current default nominal coupling strength:

`coupling_nominal = 0.28`

Current default fractal coupling exponent:

`fractal_alpha = 0.70`

The resonant phase layer provides the processor's evolving computational dynamics.

## 5. Phase Evolution

The current phase velocity is composed from:

`0.060 × current frequency`

+

`scheduler push`

+

`coupling field`

The resulting phase update is:

`phase_i = (phase_i + phase_velocity_i) mod 2π`

The scheduler contributes to phase velocity.

Current scheduler pushes are:

| Scheduler state | Phase push |
|---|---:|
| `commit` | `0.010` |
| `excite` | `0.006` |
| other scheduler states | `0.003` |

Phase evolution is therefore coupled to:

- local frequency state;
- scheduler state;
- hierarchical resonant coupling.

## 6. Kuramoto Order Parameter R

The current global phase order is:

`R = sqrt(mean(cos(phase))² + mean(sin(phase))²)`

This is evaluated by the current executable through:

`phase_order(phases)`

The resulting value represents collective phase alignment.

The current processor also evaluates the same phase-order relation across hierarchical domains.

The phase-order path contributes directly to operational processor-state evaluation.

It is part of the operational processor state.

## 7. Multiscale Phase Coherence

The current executable evaluates phase coherence across the dyadic hierarchy.

Current coherence domains include:

- pair domain;
- cluster domain;
- supercluster domain;
- global domain.

Current multiscale outputs include:

- pair-domain coherence mean;
- pair-domain coherence minimum;
- cluster coherence mean;
- cluster coherence minimum;
- supercluster coherence mean;
- supercluster coherence minimum;
- global phase coherence;
- coherence dispersion across clusters.

The current processor preserves the global coherence scalar together with multiscale coherence metrics across the hierarchy.

## 8. Hierarchical Fractal Coupling

The current executable uses a dyadic hierarchical ultrametric topology.

The cell count must be:

- a power of two;
- at least `2`.

Current default cell count:

`16`

Current default hierarchy depth:

`4`

The hierarchy depth is:

`cells.bit_length() - 1`

The hierarchical distance between cells is derived from their index relation.

Current shell population:

`2^(distance - 1)`

Current hierarchical coupling weights depend on:

- hierarchical distance;
- shell population;
- fractal exponent;
- normalization across all hierarchy levels.

The current default fractal exponent is:

`0.70`

Validated topology exactness marker:

`fixed_point_topology_sum_exact = True`

## 9. Delay Dynamics

Current default delay coefficient:

`delay_alpha = 0.30`

Each cell maintains:

- base frequency;
- frequency target;
- current frequency.

The current frequency target contains contributions from:

- base frequency;
- absolute ternary state;
- local switching activity.

The current frequency target relation is:

`frequency_target = base_frequency + state_frequency_gain × abs(state) + switching_frequency_gain × switch_activity`

Current gains:

`state_frequency_gain = 0.06`

`switching_frequency_gain = 0.12`

The current delayed response is:

`frequency_next = frequency_current + delay_alpha × (frequency_target - frequency_current)`

The resulting frequency lag contributes to:

- phase evolution;
- generated power;
- coherence;
- stability.

## 10. Local Thermal-Phase Interaction

The current executable maintains a distributed thermal field.

Each cell tracks:

- generated power;
- thermal dissipation;
- thermal diffusion;
- local heat;
- thermal overload.

Current generated-power components include:

- base power;
- switching activity;
- frequency lag.

Current default thermal parameters:

| Parameter | Default |
|---|---:|
| `thermal_beta` | `1.20` |
| `ambient_heat` | `0.05` |
| `thermal_time_constant` | `14.0` |
| `thermal_soft_limit` | `0.22` |
| `thermal_hard_limit` | `0.90` |
| `thermal_diffusion_gain` | `0.035` |

The thermal field feeds back into the resonant phase layer through:

- local thermal coupling factors;
- local effective gamma;
- nonlinear coherence compression.

## 11. Thermal Coupling Degradation

The current executable derives local thermal node factors from local overload.

These factors modify the effective resonant interaction.

The current relation uses:

`thermal_node_factor = exp(-0.5 × thermal_coupling_gain × overload)`

The pair interaction is then affected by both participating cells.

The current resonant coupling therefore depends on:

`phase relation`

×

`hierarchical weight`

×

`thermal factor of cell i`

×

`thermal factor of cell j`

The thermal field feeds directly into the phase computation.

## 12. Local Gamma Drift

The current processor tracks:

- nominal gamma;
- gamma-noise targets;
- correlated gamma-noise states;
- local thermal overload;
- effective local gamma;
- gamma drift.

The gamma-noise target field is refreshed deterministically on the current update schedule.

The correlated state then approaches the target through:

`gamma_correlation_alpha = 0.15`

Current thermal gamma gain:

`gamma_thermal_gain = 0.08`

The effective local gamma is derived from:

`nominal gamma`

+

`thermal overload contribution`

×

`correlated gamma-noise state`

The resulting local gamma enters the Kuramoto-Sakaguchi interaction.

## 13. Nonlinear Coherence Compression

The current executable applies nonlinear compression to raw phase coherence.

The relation is:

`effective_coherence = raw_phase_coherence × coherence_compression`

The compression factor is reduced by:

- mean thermal overload;
- stability-margin pressure.

Current internal gains include:

`thermal_compression_gain = 3.0`

`margin_compression_gain = 1.5`

Current stability soft margin:

`0.25`

This layer is part of the current nonlinear processor behavior.

## 14. Dynamic Stability

The current executable tracks:

`C(t)`

`P(t)`

`C(t) - P(t)`

Current destabilizing load:

`P(t) = heat + switch_load`

Current operational coherence includes contributions from:

- effective phase coherence;
- cluster coherence;
- neutral-state fraction;
- frequency-lag penalty.

Current required validation condition:

`C_minus_P_min > 0.0`

The stability path is therefore coupled to:

- resonance;
- phase coherence;
- delay;
- thermal state;
- switching load;
- active neutral state.

## 15. Phase-Derived Ternary Target

The current executable maps the evolving phase field into ternary targets.

Current mapping:

`sin(phase) > 0.33 → 1`

`sin(phase) < -0.33 → -1`

`otherwise → 0`

This relation connects:

`resonant phase field`

to:

`balanced ternary target domain`

The target is then processed through the distributed transition mechanism.

The target enters distributed transition processing under transition-capacity and active-neutral execution rules.

## 16. Balanced Ternary State Domain

The processor state and retained-result domain is:

`{-1, 0, 1}`

The valid states are:

`-1`

`0`

`1`

The active neutral state is:

`0`

The neutral state supports:

- balancing;
- damping;
- transition;
- stabilization;
- conflict neutralization;
- switching-load control.

Required current state-domain marker:

`balanced_ternary_state_domain = True`

Required reserved-state marker:

`reserved_state_events = 0`

## 17. Mandatory Active-Neutral Routing

Opposite-polarity execution follows the mandatory active-neutral routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Tick-separated execution relation:

`tick N: active polarity → 0`

↓

`pending neutral route retained`

↓

`tick N+1 or later: 0 → target polarity`

Required invariant:

`actual_direct_events = 0`

Correct processor behavior is evidenced by the transition path together with the final state vector.

The transition path preserves the active neutral route.

## 18. Distributed Commit

The current executable limits the number of state changes per tick.

Current default transition fraction:

`0.25`

Current maximum-change relation:

`max_changes = max(1, round(cells × transition_fraction))`

For the default 16-cell configuration:

`request_lanes = 4`

Current validated switching condition:

`switch_load_peak <= transition_fraction`

Default validated boundary:

`switch_load_peak <= 0.25`

Distributed commit connects the phase-derived target path to bounded retained-state transition.

## 19. Installation

Install dependencies from the repository root:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Repository external dependency:

`numpy>=1.26.0`

NumPy is used by the historical FRP v0.9.3 and v0.9.4 executable layers. The FRP v1.7.0 executable semantic reference and Comparative Architecture Benchmark Suite use the Python standard library and repository-local modules.

Compile the current executable semantic reference:

    python -m py_compile frp_prototype_v1_7_0.py

A successful compile gate returns exit status `0`.

The M16 RTL and FPGA preparation execution paths require:

- Verilator;
- a C++ compiler.

The qualified Ubuntu workflow installation command is:

    sudo apt-get update
    sudo apt-get install --yes verilator g++

Record the installed toolchain versions:

    verilator --version
    g++ --version

Detailed installation instructions:

`INSTALL.md`

## 20. Basic Command Structure

M15 executable semantic-reference command form:

    python frp_prototype_v1_7_0.py [options]

Primary execution modes:

| Mode | Role |
|---|---|
| `demo` | runs the M15 executable semantic-reference execution |
| `self-test` | runs the qualified M15 semantic and implementation-mapping self-test package |
| `benchmark` | emits the M15 implementation-mapping benchmark matrix |

General mode form:

    python frp_prototype_v1_7_0.py --mode <mode>

Default mode:

`demo`

Default output:

`text`

## 21. Quick Start

Run the default processor execution:

    python frp_prototype_v1_7_0.py

Run the explicit demo mode:

    python frp_prototype_v1_7_0.py --mode demo

Run the demo as structured JSON:

    python frp_prototype_v1_7_0.py --mode demo --output json

Run the demo with full trace data:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace

Run the qualified M15 self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Run the free-scheduler self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

Run the 7/1-scheduler self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

Run the 1/7-scheduler self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Generate the M15 benchmark matrix:

    python frp_prototype_v1_7_0.py --mode benchmark

Build the current M16 RTL testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_tb -Irtl/m16 --Mdir /tmp/frp_m16_obj rtl/m16/frp_m16_tb.sv

Run the current M16 RTL testbench:

    /tmp/frp_m16_obj/Vfrp_m16_tb

Elaborate the current M16 FPGA integration top:

    verilator --sv --lint-only --top-module frp_m16_fpga_top -Irtl/m16 -Ifpga/m16 fpga/m16/frp_m16_fpga_top.sv

Build the current M16 FPGA preparation testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_fpga_tb -Irtl/m16 -Ifpga/m16 --Mdir /tmp/frp_m16_fpga_obj fpga/m16/frp_m16_fpga_tb.sv

Run the current M16 FPGA preparation testbench:

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

## 22. Current CLI Options

| Option | Values | Default | Role |
|---|---|---|---|
| `--mode` | `demo`, `self-test`, `benchmark` | `demo` | selects execution mode |
| `--output` | `text`, `json` | `text` | selects normal output format |
| `--include-trace` | flag | disabled | includes complete trace arrays in demo JSON |
| `--scheduler` | `free`, `7/1`, `1/7` | `7/1` | selects scheduler mode |
| `--cells` | power-of-two integer, at least `2` | `16` | selects processor cell count |
| `--steps` | integer | `64` | selects execution tick count |
| `--seed` | integer | `76` | selects deterministic seed |
| `--transition-fraction` | number | `0.25` | limits state changes per tick |
| `--gamma` | number | `0.30 × pi` | sets nominal Sakaguchi phase lag |
| `--fractal-alpha` | number | `0.70` | sets hierarchical coupling exponent |
| `--thermal-beta` | number | `1.20` | sets hierarchical thermal exponent |
| `--ambient-heat` | number | `0.05` | sets ambient thermal baseline |
| `--thermal-time-constant` | number | `14.0` | sets thermal relaxation time |
| `--thermal-soft-limit` | number | `0.22` | sets thermal soft limit |
| `--thermal-hard-limit` | number | `0.90` | sets thermal hard limit |
| `--coupling-nominal` | number | `0.28` | sets nominal resonant coupling strength |
| `--delay-alpha` | number | `0.30` | sets delayed frequency-response coefficient |
| `--thermal-diffusion-gain` | number | `0.035` | sets thermal diffusion gain |
| `--equivalence-tolerance` | number | `1e-12` | sets floating equivalence tolerance |
| `--vector-output-dir` | directory path | none | writes deterministic M15 vector files |

M15 semantic-reference export flags appear in dedicated sections below.

## 23. Current Default Configuration

The current default configuration is:

| Parameter | Default |
|---|---:|
| cells | `16` |
| steps | `64` |
| seed | `76` |
| scheduler | `7/1` |
| transition fraction | `0.25` |
| gamma | `0.30 × pi` |
| fractal alpha | `0.70` |
| thermal beta | `1.20` |
| ambient heat | `0.05` |
| thermal time constant | `14.0` |
| thermal soft limit | `0.22` |
| thermal hard limit | `0.90` |
| nominal coupling | `0.28` |
| delay alpha | `0.30` |
| thermal diffusion gain | `0.035` |
| equivalence tolerance | `1e-12` |

Derived default values include:

| Derived value | Default |
|---|---:|
| hierarchy depth | `4` |
| request lanes | `4` |
| packed ternary state width | `32 bits` |

## 24. Help Output

Inspect the current command interface:

    python frp_prototype_v1_7_0.py --help

Use the executable itself as the final command-line source of truth for the M15 executable semantic-reference interface.

## 25. Demo Mode

Run:

    python frp_prototype_v1_7_0.py --mode demo

The default demo executes the qualified M15 stateful quantized hardware-shadow path with:

- deterministic request plan;
- automatic phase-derived ternary targets;
- current scheduler mode;
- active neutral routing;
- delay dynamics;
- thermal dynamics;
- gamma dynamics;
- hierarchical phase coupling;
- coherence evaluation;
- stability evaluation.

The default text output includes:

- executable semantic-reference version;
- M15 semantic-reference milestone;
- execution kind;
- balanced ternary state-domain status;
- reserved-state event count;
- actual direct-event count;
- scheduler;
- scheduler counts;
- switch-load peak;
- minimum `C_minus_P`;
- fixed-point topology exactness;
- fixed-point thermal exactness.

Expected leading text markers:

`FRP v1.7.0`

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

`kind: demo`

## 26. What Demo Mode Actually Computes

Demo mode executes the complete coupled processor path:

`current phase field`

↓

`phase-derived ternary target`

↓

`distributed state-transition decision`

↓

`delay update`

↓

`thermal update`

↓

`local gamma update`

↓

`thermal coupling update`

↓

`Kuramoto-Sakaguchi phase-field update`

↓

`new phase field`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`nonlinear coherence compression`

↓

`dynamic stability`

↓

`next processor tick`

The evolving phase field continuously affects subsequent ternary target formation.

## 27. Demo Text Output

Run:

    python frp_prototype_v1_7_0.py --mode demo --output text

Expected markers include:

`balanced_ternary_state_domain: True`

`reserved_state_events: 0`

`actual_direct_events: 0`

`scheduler: 7/1`

`fixed_point_topology_sum_exact: True`

`fixed_point_thermal_sum_exact: True`

The text report is a compact operational summary.

Use JSON output for complete machine-readable inspection.

## 28. Structured JSON Demo Output

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json

Expected schema:

`frp.structured_output.v1.7.0`

Expected version:

`1.7.0`

Expected milestone:

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

Expected kind:

`demo`

Default top-level fields:

- `cell_trace_digest`;
- `configuration`;
- `hardware_profile`;
- `kernel`;
- `kind`;
- `milestone`;
- `preload_digest`;
- `schema`;
- `summary`;
- `trace_digest`;
- `version`.

## 29. Structured Configuration Object

The current `configuration` object contains:

- `cells`;
- `steps`;
- `seed`;
- `scheduler`;
- `transition_fraction`;
- `request_lanes`;
- `gamma_nominal`;
- `fractal_alpha`;
- `thermal_beta`;
- `ambient_heat`;
- `thermal_time_constant`;
- `thermal_soft_limit`;
- `thermal_hard_limit`;
- `coupling_nominal`;
- `delay_alpha`;
- `thermal_diffusion_gain`.

This object records the primary input configuration used for the execution.

## 30. Structured Kernel Object

The current `kernel` object records:

`balanced_ternary_states = [-1, 0, 1]`

`active_neutral_state = 0`

Neutral routes:

`-1 -> 0 -> 1`

`1 -> 0 -> -1`

Scheduler modes:

`free`

`7/1`

`1/7`

Direct-event target:

`actual_direct_events_target = 0`

The kernel object records the ternary transition contract.

The resonant computational mechanism is represented through the execution state, configuration, trace, coherence, thermal, and hardware-facing layers.

## 31. Structured Hardware Profile

The current structured output records:

| Domain | Representation |
|---|---|
| scalar | `S32Q16` |
| normalized unit | `S32Q30` |
| phase | `PHASE_U32` |
| gamma | `GAMMA_S32` |

Balanced ternary hardware encoding:

`-1 → 11`

`0 → 00`

`+1 → 01`

Reserved:

`10`

## 32. Full Trace Output

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace

The full output adds:

- `trace`;
- `cell_trace`;
- `route_events`.

With the default configuration:

`trace`

contains:

`64`

processor-tick rows.

`cell_trace`

contains:

`1024`

cell-tick rows.

The full trace exposes the processor evolution needed for detailed inspection of:

- states;
- phases;
- frequencies;
- scheduler behavior;
- pending routes;
- gamma targets;
- gamma state;
- thermal state;
- coherence;
- stability.

## 33. Digest Output and Full Trace Output

Default structured output retains:

- preload digest;
- trace digest;
- cell-trace digest.

This provides compact deterministic identity through the recorded digests.

Full trace output uses:

`--include-trace`

and includes the complete arrays.

Use digest output for:

- compact CI inspection;
- deterministic identity checks;
- routine machine-readable execution.

Use full trace output for:

- tick-by-tick analysis;
- cell-by-cell analysis;
- phase-dynamics inspection;
- route inspection;
- correlation work.

## 34. Scheduler Modes

FRP v1.7.0 supports three scheduler modes.

| Scheduler | Behavior |
|---|---|
| `free` | every tick uses free scheduler state |
| `7/1` | seven balance ticks followed by one commit tick |
| `1/7` | one excite tick followed by seven neutralize ticks |

The scheduler affects:

- scheduler counts;
- state-transition timing;
- phase velocity through scheduler push.

It is therefore part of both the transition and resonant execution paths.

## 35. Free Scheduler

Run:

    python frp_prototype_v1_7_0.py --mode demo --scheduler free

Validated 16-tick profile:

`free = 16`

Run the corresponding self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

## 36. 7/1 Scheduler

Run:

    python frp_prototype_v1_7_0.py --mode demo --scheduler 7/1

Validated 16-tick profile:

`balance = 14`

`commit = 2`

Validated default 64-tick profile:

`balance = 56`

`commit = 8`

Run the corresponding self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

## 37. 1/7 Scheduler

Run:

    python frp_prototype_v1_7_0.py --mode demo --scheduler 1/7

Validated 16-tick profile:

`excite = 2`

`neutralize = 14`

Run the corresponding self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

## 38. Scheduler Count Invariant

Required relation:

`sum(scheduler_counts) = ticks_recorded`

Current structured execution reports:

`scheduler_counts_valid`

This value must remain:

`True`

## 39. Cell-Count Selection

Use:

    python frp_prototype_v1_7_0.py --cells <value>

The cell count must be:

- a power of two;
- at least `2`.

Valid examples:

    python frp_prototype_v1_7_0.py --cells 2

    python frp_prototype_v1_7_0.py --cells 8

    python frp_prototype_v1_7_0.py --cells 16

    python frp_prototype_v1_7_0.py --cells 32

Invalid examples include:

`1`

`3`

`10`

`24`

Invalid values are rejected by the command parser.

## 40. Hierarchy Scaling

The hierarchy depth follows the power-of-two cell count.

Current validated examples:

| Cells | Hierarchy depth |
|---|---:|
| `8` | `3` |
| `16` | `4` |
| `32` | `5` |

The packed ternary state width is:

`2 × cells`

Current examples:

| Cells | Packed state width |
|---|---:|
| `8` | `16 bits` |
| `16` | `32 bits` |
| `32` | `64 bits` |

## 41. Transition-Fraction Control

Use:

    python frp_prototype_v1_7_0.py --transition-fraction 0.25

Current default:

`0.25`

The value controls the maximum bounded state-transition capacity per tick.

The current derived relation is:

`max_changes = max(1, round(cells × transition_fraction))`

For the default 16-cell configuration:

`max_changes = 4`

The same derived value defines:

`request_lanes = 4`

## 42. Gamma Control

Use:

    python frp_prototype_v1_7_0.py --gamma <value>

Current default:

`0.30 × pi`

The command expects a numeric value in radians.

Provide gamma as a concrete numeric radian value.

A concrete numeric example is:

    python frp_prototype_v1_7_0.py --gamma 0.9424777960769379

Changing gamma changes the asymmetric phase offset in the Kuramoto-Sakaguchi interaction.

## 43. Fractal Coupling Control

Use:

    python frp_prototype_v1_7_0.py --fractal-alpha 0.70

Current default:

`0.70`

The value controls the hierarchy-distance weighting profile of the phase-coupling topology.

The executable requires:

`fractal_alpha > 0`

## 44. Thermal Topology Control

Use:

    python frp_prototype_v1_7_0.py --thermal-beta 1.20

Current default:

`1.20`

The value controls the hierarchy-distance weighting profile of the thermal-diffusion topology.

The executable requires:

`thermal_beta > 0`

## 45. Nominal Coupling Control

Use:

    python frp_prototype_v1_7_0.py --coupling-nominal 0.28

Current default:

`0.28`

The nominal coupling is multiplied by:

- hierarchy-weighted phase interaction;
- local thermal coupling factors.

## 46. Delay Control

Use:

    python frp_prototype_v1_7_0.py --delay-alpha 0.30

Current default:

`0.30`

The value controls how rapidly the current frequency approaches the frequency target.

Lower values produce slower internal frequency response.

Higher values produce faster internal frequency response.

## 47. Thermal Controls

Current thermal command options are:

    --ambient-heat

    --thermal-time-constant

    --thermal-soft-limit

    --thermal-hard-limit

    --thermal-diffusion-gain

Example:

    python frp_prototype_v1_7_0.py --ambient-heat 0.05 --thermal-time-constant 14.0 --thermal-soft-limit 0.22 --thermal-hard-limit 0.90 --thermal-diffusion-gain 0.035

These parameters affect the coupled thermal-phase path.

## 48. Deterministic Seed

Use:

    python frp_prototype_v1_7_0.py --seed 76

Current default:

`76`

The seed contributes to deterministic initialization and deterministic gamma-noise behavior.

For reproducibility, record the exact seed with the source revision and complete configuration.

## 49. Self-Test Mode

Run:

    python frp_prototype_v1_7_0.py --mode self-test

Expected text markers:

`FRP v1.7.0`

`kind: self_test`

`status: PASS`

`check_count: 41`

Run the machine-readable self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Expected schema:

`frp.structured_output.v1.7.0`

Expected version:

`1.7.0`

Expected status:

`PASS`

Expected check count:

`41`

All values in:

`checks`

must be:

`True`

## 50. Complete Self-Test Matrix

Default profile:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Free scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

7/1 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

1/7 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Every profile must report:

`status = PASS`

`check_count = 41`

All checks must be:

`True`

## 51. Current Self-Test Coverage

The qualified M15 self-test package validates the complete semantic and implementation-mapping qualification chain.

Coverage includes:

- balanced ternary encoding;
- reserved-state rejection;
- packed-state roundtrip;
- scheduler encodings;
- fixed-point primitive behavior;
- phase representation;
- phase wrapping;
- hierarchy topology;
- exact fixed-point coupling normalization;
- exact fixed-point thermal normalization;
- deterministic trigonometric lookup table;
- quantized execution;
- active neutral routing;
- zero actual direct events;
- scheduler behavior;
- deterministic vector generation;
- scaling profiles;
- floating-to-quantized correlation;
- exact quantized replay;
- qualification closure.

The self-test therefore covers substantially more than final ternary state output.

## 52. Benchmark Mode

Run:

    python frp_prototype_v1_7_0.py --mode benchmark

Benchmark mode emits JSON.

The benchmark path emits machine-readable JSON across the CLI output selector.

Expected schema:

`frp.m3.benchmark_matrix.v1.7.0`

Expected kind:

`benchmark_matrix`

Expected row count:

`5`

## 53. Current Benchmark-Matrix Rows

Expected architecture order:

1. `frp_v1_6_0_m14_floating_semantic_reference`;
2. `frp_v1_7_0_quantized_hardware_shadow`;
3. `frp_v1_7_0_cycle_exact_vector_package`;
4. `frp_v1_7_0_systemverilog_correlation_contract`;
5. `frp_v1_7_0_qualification_closure`.

The benchmark matrix represents the qualified M15 implementation-mapping chain inherited by FRP v1.8.0.

The Comparative Architecture Benchmark Suite provides a dedicated supporting execution path under `benchmarks/architecture_comparison/`.

## 54. Benchmark-Matrix Export Flag

Equivalent explicit export:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix

Export flags emit JSON.

Expected schema:

`frp.m3.benchmark_matrix.v1.7.0`

## 55. M15 Export Commands

The current executable exposes ten primary M15 artifact exports.

### Fixed-point interface profile

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile

Schema:

`frp.m15.fixed_point_interface_profile.v1.7.0`

### Balanced ternary hardware encoding map

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map

Schema:

`frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0`

### Quantized reference shadow model

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model

Schema:

`frp.m15.quantized_reference_shadow_model.v1.7.0`

### Cycle-exact reference trace

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace

Schema:

`frp.m15.cycle_exact_reference_trace.v1.7.0`

### RTL comparison vector package

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package

Schema:

`frp.m15.rtl_comparison_vector_package.v1.7.0`

### SystemVerilog testbench interface map

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map

Schema:

`frp.m15.systemverilog_testbench_interface_map.v1.7.0`

### Synthesizable RTL reference core

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core

Schema:

`frp.m15.synthesizable_rtl_reference_core.v1.7.0`

### RTL assertion correlation harness

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness

Schema:

`frp.m15.rtl_assertion_correlation_harness.v1.7.0`

### Reference RTL equivalence report

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report

Schema:

`frp.m15.reference_rtl_equivalence_report.v1.7.0`

### Qualification closure manifest

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

Schema:

`frp.m15.qualification_closure_manifest.v1.7.0`

## 56. Export Precedence

When an M15 export flag is supplied, the export path takes precedence over normal mode execution.

The executable evaluates export flags before:

- `self-test`;
- `benchmark`;
- `demo`.

Use one primary export flag per command for clear reproducibility.

## 57. Export Output Format

All M15 export flags emit JSON.

Benchmark mode also emits JSON.

This behavior applies with the default CLI output selection.

Examples:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile

    python frp_prototype_v1_7_0.py --mode benchmark

Both commands emit machine-readable JSON.

## 58. Fixed-Point Interface Profile

Run:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile

The current hardware-facing numeric profile includes:

| Domain | Representation |
|---|---|
| general dynamic scalar | `S32Q16` |
| normalized coefficient | `S32Q30` |
| phase | `PHASE_U32` |
| Sakaguchi gamma offset | `GAMMA_S32` |

Current trigonometric table size:

`4096`

This profile maps the resonant computational state into deterministic hardware-facing numeric domains.

## 59. Balanced Ternary Hardware Encoding Export

Run:

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map

Current two-bit encoding:

`-1 → 2'b11`

`0 → 2'b00`

`+1 → 2'b01`

Reserved encoding:

`2'b10`

Canonical integer codes:

`-1 → 3`

`0 → 0`

`+1 → 1`

Reserved integer code:

`2`

The encoding provides the hardware-facing representation of the balanced ternary state domain within the complete FRP computational mechanism.

## 60. Quantized Reference Shadow Model

Run:

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model

The stateful quantized shadow maps the floating semantic reference into deterministic fixed-point execution.

The shadow retains processor domains including:

- ternary state;
- scheduler state;
- pending neutral routes;
- phase;
- frequency;
- gamma;
- thermal state;
- coherence;
- stability;
- exact counters.

## 61. Cycle-Exact Reference Trace

Run:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace

The current cycle-exact trace provides the integer reference path for RTL comparison.

Current validated default trace length:

`64`

ticks.

Current required invariants include:

`actual_direct_events = 0`

`reserved_state_events = 0`

## 62. RTL Comparison Vector Package

Run:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package

To write the deterministic vector files to a directory:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors

Expected files:

- `frp_m15_kernel_vectors.vec`;
- `frp_m15_pending_routes.trace`;
- `frp_m15_scheduler_free_vectors.vec`;
- `frp_m15_scheduler_7_1_vectors.vec`;
- `frp_m15_scheduler_1_7_vectors.vec`;
- `frp_m15_full_correlation_vectors.vec`;
- `frp_m15_cell_trace.vec`;
- `frp_m15_reference_preload.json`;
- `frp_m15_trig_lut_q30.vec`;
- `frp_m15_sha256_manifest.json`.

## 63. Deterministic Vector Repeat Check

Generate package A:

    mkdir -p vectors_a

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_a > vector-package-a.json

Generate package B independently:

    mkdir -p vectors_b

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_b > vector-package-b.json

Compare the generated directories:

    diff -qr vectors_a vectors_b

Required result:

`byte-identical directory equality`

The generated vector directories must be byte-identical.

The wrapper JSON output records the chosen output directory, so directory equality is the direct deterministic vector-package check.

## 64. SystemVerilog Interface Map

Run:

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map

Current default interface parameters include:

| Parameter | Value |
|---|---:|
| `NUM_CELLS` | `16` |
| `HIERARCHY_DEPTH` | `4` |
| `REQUEST_LANES` | `4` |
| `CELL_ID_WIDTH` | `4` |
| `STATE_VECTOR_WIDTH` | `32` |
| `SCALAR_WIDTH` | `32` |
| `PHASE_WIDTH` | `32` |

The verification interface includes deterministic gamma-noise target input.

## 65. Synthesizable RTL Reference Core Export

Run:

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core

The export maps the current processor execution semantics into the M15 RTL reference-core contract.

The mapped behavior includes:

- balanced ternary state execution;
- scheduler behavior;
- active neutral routing;
- pending routes;
- transition limits;
- phase-domain fixed-point behavior;
- deterministic reference comparison.

## 66. RTL Assertion Correlation Harness

Run:

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness

Current comparison rule:

`actual integer field == expected integer field`

The assertion-correlation layer connects RTL-facing output to deterministic M15 reference vectors.

## 67. Reference RTL Equivalence Report

Run:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report

The report distinguishes:

- floating semantic reference to quantized shadow correlation;
- exact quantized shadow deterministic replay.

The first boundary uses exact sequence checks and bounded numeric error.

The second boundary requires exact replay equality.

## 68. Qualification Closure Manifest

Run:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

Required status:

`PASS`

All closure checks must be:

`True`

Qualified M15 artifact layer count:

`10`

This is the inherited M15 semantic and implementation-mapping qualification endpoint.

## 69. M16 RTL Execution and Qualification

The current M16 RTL execution layer uses the qualified M15 semantic and implementation-mapping foundation.

M16 RTL source boundary:

- `rtl/m16/frp_m16_pkg.sv`;
- `rtl/m16/frp_m16_scheduler.sv`;
- `rtl/m16/frp_m16_request_lanes.sv`;
- `rtl/m16/frp_m16_pending_routes.sv`;
- `rtl/m16/frp_m16_active_neutral.sv`;
- `rtl/m16/frp_m16_capacity_guard.sv`;
- `rtl/m16/frp_m16_state_update.sv`;
- `rtl/m16/frp_m16_core.sv`;
- `rtl/m16/frp_m16_assertions.sv`;
- `rtl/m16/frp_m16_tb.sv`.

Remove previous M16 RTL simulation paths:

    rm -rf /tmp/frp_m16_obj
    rm -f /tmp/frp_m16_build.log
    rm -f /tmp/frp_m16_execution.log

Create the build directory:

    mkdir -p /tmp/frp_m16_obj

Build the integrated M16 RTL testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_tb -Irtl/m16 --Mdir /tmp/frp_m16_obj rtl/m16/frp_m16_tb.sv 2>&1 | tee /tmp/frp_m16_build.log

Check the generated executable:

    test -x /tmp/frp_m16_obj/Vfrp_m16_tb

Run the integrated M16 RTL testbench:

    /tmp/frp_m16_obj/Vfrp_m16_tb 2>&1 | tee /tmp/frp_m16_execution.log

Required terminal markers:

`FRP M16 deterministic RTL testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`ticks_recorded=16`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

Required integrated invariant flags:

- `FRP_INV_STATE_DOMAIN_VALID = 1`;
- `FRP_INV_SCHEDULER_COUNTS_VALID = 1`;
- `FRP_INV_REQUEST_LANE_ORDER_VALID = 1`;
- `FRP_INV_PENDING_POLARITY_VALID = 1`;
- `FRP_INV_ACTIVE_NEUTRAL_VALID = 1`;
- `FRP_INV_TRANSITION_CAPACITY_VALID = 1`;
- `FRP_INV_STATE_UPDATE_VALID = 1`;
- `FRP_INV_NO_ACTUAL_DIRECT_EVENTS = 1`;
- `FRP_INV_NO_RESERVED_STATE = 1`;
- `FRP_INV_NO_QUEUE_OVERFLOW = 1`.

Current M16 RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Qualified records:

| Record | Workflow run | Qualified commit | Result |
|---|---:|---|---:|
| initial closure | `#82` | `a68a2af` | `SUCCESS` |
| qualification rerun | `#84` | `ede53cf` | `SUCCESS` |

Current closure status:

`M16 RTL EXECUTION LAYER CLOSED`

## 70. M16 FPGA Preparation Execution and Qualification

The current M16 FPGA preparation layer provides the target-independent FPGA integration boundary for the qualified M16 RTL core.

FPGA preparation source boundary:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`.

Inherited qualified RTL dependency boundary:

`9 SystemVerilog artifacts`

Remove previous M16 FPGA simulation paths:

    rm -rf /tmp/frp_m16_fpga_obj
    rm -f /tmp/frp_m16_fpga_top_lint.log
    rm -f /tmp/frp_m16_fpga_build.log
    rm -f /tmp/frp_m16_fpga_execution.log

Create the FPGA build directory:

    mkdir -p /tmp/frp_m16_fpga_obj

Elaborate the M16 FPGA integration top:

    verilator --sv --lint-only --top-module frp_m16_fpga_top -Irtl/m16 -Ifpga/m16 fpga/m16/frp_m16_fpga_top.sv 2>&1 | tee /tmp/frp_m16_fpga_top_lint.log

Build the M16 FPGA integration testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_fpga_tb -Irtl/m16 -Ifpga/m16 --Mdir /tmp/frp_m16_fpga_obj fpga/m16/frp_m16_fpga_tb.sv 2>&1 | tee /tmp/frp_m16_fpga_build.log

Check the generated executable:

    test -x /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Run the M16 FPGA integration testbench:

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb 2>&1 | tee /tmp/frp_m16_fpga_execution.log

Required terminal markers:

`FRP M16 FPGA integration testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`core_ready=1`

`ticks_recorded=1`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

`invariant_flags=1111111111`

Qualified reset and execution-input relations:

- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- tick gating before readiness;
- counter-clear gating before readiness;
- request-valid gating before readiness;
- scheduler propagation;
- request-interface propagation;
- active-neutral first-leg execution;
- retained pending-route completion.

Current M16 FPGA preparation workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Qualified records:

| Record | Workflow run | Qualified commit | Result |
|---|---:|---|---:|
| initial closure | `#1` | `326b69e` | `SUCCESS` |
| qualification rerun | `#2` | `ede53cf` | `SUCCESS` |

Current closure status:

`M16 FPGA PREPARATION LAYER CLOSED`

## 71. Scaling Execution

Run 8 cells:

    python frp_prototype_v1_7_0.py --cells 8 --steps 16 --mode demo --output json

Run 16 cells:

    python frp_prototype_v1_7_0.py --cells 16 --steps 16 --mode demo --output json

Run 32 cells:

    python frp_prototype_v1_7_0.py --cells 32 --steps 16 --mode demo --output json

Expected structure:

| Cells | Hierarchy depth | Request lanes | Packed state width |
|---|---:|---:|---:|
| `8` | `3` | `2` | `16 bits` |
| `16` | `4` | `4` | `32 bits` |
| `32` | `5` | `8` | `64 bits` |

## 72. Scaling Invariants

Every validated scaling profile must preserve:

- balanced ternary state-domain validity;
- `reserved_state_events = 0`;
- `actual_direct_events = 0`;
- `queue_overflow_events = 0`;
- scheduler-count validity;
- switch load within transition fraction;
- exact fixed-point topology sum;
- exact fixed-point thermal sum.

Scaling changes also affect:

- hierarchy depth;
- phase-coupling structure;
- thermal topology;
- multiscale coherence domains;
- packed ternary state width.

## 73. Saving Demo Output

Save the compact structured demo:

    python frp_prototype_v1_7_0.py --mode demo --output json > frp-v1.7.0-demo.json

Save the full trace:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace > frp-v1.7.0-demo-trace.json

Save a custom configuration:

    python frp_prototype_v1_7_0.py --mode demo --cells 32 --steps 128 --scheduler 7/1 --output json > frp-v1.7.0-custom-demo.json

## 74. Saving Self-Test Output

Save the default self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json > frp-v1.7.0-self-test.json

Save the free-scheduler self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json > frp-v1.7.0-self-test-free.json

Save the 7/1 self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json > frp-v1.7.0-self-test-7-1.json

Save the 1/7 self-test:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json > frp-v1.7.0-self-test-1-7.json

## 75. Saving M15 Export Output

Example:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile > fixed-point-interface-profile.json

Example:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace > cycle-exact-reference-trace.json

Example:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report > reference-rtl-equivalence-report.json

Example:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest > qualification-closure-manifest.json

## 76. Minimal Current Validation Sequence

Compile the M15 executable semantic reference:

    python -m py_compile frp_prototype_v1_7_0.py

Run the default self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Run all scheduler profiles:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Generate qualification closure:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

Build and run the M16 RTL testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_tb -Irtl/m16 --Mdir /tmp/frp_m16_obj rtl/m16/frp_m16_tb.sv

    /tmp/frp_m16_obj/Vfrp_m16_tb

Elaborate the M16 FPGA integration top:

    verilator --sv --lint-only --top-module frp_m16_fpga_top -Irtl/m16 -Ifpga/m16 fpga/m16/frp_m16_fpga_top.sv

Build and run the M16 FPGA preparation testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_fpga_tb -Irtl/m16 -Ifpga/m16 --Mdir /tmp/frp_m16_fpga_obj fpga/m16/frp_m16_fpga_tb.sv

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Required results:

`Python compilation PASS`

`41/41 PASS`

`qualification closure PASS`

`M16 RTL execution PASS`

`M16 FPGA preparation PASS`

## 77. Complete Deterministic Reproduction Sequence

Record the source state:

    git rev-parse HEAD
    git status --short
    python --version
    python -m pip freeze

Generate structured output:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-a.json

Generate an independent repeat:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-b.json

Compare:

    cmp demo-a.json demo-b.json

Generate two vector packages:

    mkdir -p vectors_a
    mkdir -p vectors_b

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_a > vector-package-a.json

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_b > vector-package-b.json

Compare:

    diff -qr vectors_a vectors_b

Required deterministic result:

`byte-identical`

Record the M16 RTL source boundary:

    sha256sum rtl/m16/*.sv | sort > m16-rtl-sources.sha256

Build and execute the M16 RTL testbench:

    verilator --sv --timing --assert --binary --top-module frp_m16_tb -Irtl/m16 --Mdir /tmp/frp_m16_obj rtl/m16/frp_m16_tb.sv

    /tmp/frp_m16_obj/Vfrp_m16_tb

Record the M16 FPGA and inherited RTL source boundary:

    sha256sum rtl/m16/*.sv fpga/m16/*.sv | sort > m16-fpga-rtl-sources.sha256

Elaborate, build, and execute the M16 FPGA preparation boundary:

    verilator --sv --lint-only --top-module frp_m16_fpga_top -Irtl/m16 -Ifpga/m16 fpga/m16/frp_m16_fpga_top.sv

    verilator --sv --timing --assert --binary --top-module frp_m16_fpga_tb -Irtl/m16 -Ifpga/m16 --Mdir /tmp/frp_m16_fpga_obj fpga/m16/frp_m16_fpga_tb.sv

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Detailed reproducibility requirements:

`REPRODUCIBILITY.md`

## 78. Supporting Comparative Architecture Suite

The Comparative Architecture Benchmark Suite is located at:

`benchmarks/architecture_comparison/`

It compares:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The FRP architecture in this suite remains a resonant phase-coherence architecture.

The comparison adapter carries the resonant phase-coherence architecture into the shared deterministic workload and cost-model interface.

## 79. Comparative Architecture Self-Test

Enter the benchmark directory:

    cd benchmarks/architecture_comparison

Run:

    python run_architecture_comparison.py --self-test --output text

The comparison suite is a supporting validation contour.

The comparison suite provides a supporting validation contour alongside the FRP v1.7.0 M15 executable semantic-reference path inherited by FRP v1.8.0.

## 80. Canonical Comparative Architecture Run

From:

`benchmarks/architecture_comparison/`

run:

    python run_architecture_comparison.py --workload-profile profiles/workload_profile_v1.json --cost-profile profiles/normalized_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler "7/1" --write results/reference_comparison_seed_76.json --output text

The comparison policy is:

`integrity_only_no_winner_assertions`

Required winner assertions:

`[]`

The result remains data.

## 81. Supporting Hardware-Sensitivity Run

From:

`benchmarks/architecture_comparison/`

validate the hardware-sensitivity profile:

    python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --output text

Run the profile self-test:

    python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --self-test --output text

Run the hardware-sensitivity comparison self-test:

    python run_hardware_sensitivity_comparison.py --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json --self-test --output json

These commands serve the supporting hardware-sensitivity validation path.

## 82. Current Usage Paths

Use:

`frp_prototype_v1_7_0.py`

for the qualified FRP v1.7.0 M15 executable semantic reference.

Use:

`rtl/m16/frp_m16_tb.sv`

for the current M16 RTL executable testbench.

Use:

`fpga/m16/frp_m16_fpga_top.sv`

for the current target-independent M16 FPGA integration top.

Use:

`fpga/m16/frp_m16_fpga_tb.sv`

for the current M16 FPGA preparation testbench.

Use:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

for the current M16 RTL qualification workflow.

Use:

`.github/workflows/frp-m16-fpga-preparation.yml`

for the current M16 FPGA preparation qualification workflow.

Use:

`--mode demo`

for M15 executable semantic-reference execution.

Use:

`--mode self-test`

for the qualified M15 self-test package.

Use:

`--mode benchmark`

for the qualified M15 implementation-mapping benchmark matrix.

Use:

`benchmarks/architecture_comparison/`

for the Comparative Architecture Benchmark Suite.

Report each execution purpose under its own result scope.

## 83. Current Technical Chain

The published FRP architecture and qualification progression recorded across the repository milestones is:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`cell phase and frequency state`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric phase lag gamma`

↓

`hierarchical fractal phase interaction`

↓

`phase evolution`

↓

`resonance selection`

↓

`Kuramoto order parameter R`

↓

`multiscale phase coherence`

↓

`delay dynamics`

↓

`local thermal-phase interaction`

↓

`local gamma drift`

↓

`nonlinear coherence compression`

↓

`dynamic stability C(t) - P(t)`

↓

`phase-derived ternary target`

↓

`distributed commit`

↓

`active neutral routing`

↓

`retained ternary state`

↓

`structured machine-readable validation`

↓

`hardware-facing signal mapping`

↓

`HDL and testbench preparation`

↓

`RTL interface and assertion contracts`

↓

`formal verification and equivalence scaffolds`

↓

`FPGA synthesis and timing structures`

↓

`stable production interface freeze`

↓

`silicon and heterogeneous implementation architecture`

↓

`silicon production and tapeout readiness`

↓

`production integration and external implementation handoff`

↓

`external implementation feedback and production iteration`

↓

`production scaling and implementation stabilization`

↓

`physical implementation correlation and production qualification`

↓

`fixed-point implementation mapping`

↓

`stateful quantized hardware shadow execution`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`SystemVerilog interface mapping`

↓

`synthesizable RTL reference-core mapping`

↓

`RTL assertion correlation`

↓

`reference equivalence`

↓

`qualification closure`

↓

`M16 phase-derived balanced ternary target and request-interface boundary`

↓

`M16 scheduler and request-lane execution`

↓

`M16 active-neutral and retained pending-route execution`

↓

`M16 transition-capacity enforcement and retained-state writeback`

↓

`M16 integrated invariant execution`

↓

`M16 target-independent FPGA integration and preparation qualification`

The resonant phase-coherence computational mechanism remains the processor core throughout this chain.

The balanced ternary domain remains the state and retained-result domain throughout this chain.

## 84. Current File Alignment

This usage path is aligned with:

- `README.md`;
- `INSTALL.md`;
- `frp_prototype_v1_7_0.py`;
- `REPRODUCIBILITY.md`;
- `CI.md`;
- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `verification/README.md`;
- `verification/coherence_metrics.md`;
- `docs/core_principles.md`;
- `docs/resonance_computation.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `docs/m16_rtl_core_realization_execution_semantics.md`;
- `rtl/m16/README.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`;
- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`;
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`.

Inherited M15 release evidence remains aligned with:

- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`.

Historical executable files and historical release records remain bound to their corresponding release layers.

## 85. Current Status

Processor:

`Fractal Resonance Processor (FRP)`

Processor class:

`Ternary Resonant Coherence Processor`

Computational mechanism:

`Kuramoto-Sakaguchi resonant phase dynamics with asymmetric phase lag, hierarchical fractal coupling, phase evolution, Kuramoto order parameter R, multiscale phase coherence, delay dynamics, local thermal-phase interaction, local gamma drift, nonlinear coherence compression, dynamic stability evaluation, phase-derived ternary targets, distributed commit, mandatory active-neutral routing, and retained coherent ternary state`

State and retained-result domain:

`{-1, 0, 1}`

Active neutral state:

`0`

Current executable form:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

Current version:

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

Inherited M15 validated self-test result:

`41/41 PASS`

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Inherited M15 qualification closure result:

`PASS`

Current M16 RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Current M16 RTL qualification result:

`PASS`

Current M16 RTL closure status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Current M16 FPGA preparation qualification result:

`PASS`

Current M16 FPGA preparation closure status:

`M16 FPGA PREPARATION LAYER CLOSED`

Current release qualification state:

`FRP v1.8.0 / M16 — PASS`










</details>
