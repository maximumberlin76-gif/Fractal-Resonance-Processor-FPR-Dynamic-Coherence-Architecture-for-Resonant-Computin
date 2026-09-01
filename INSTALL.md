# Fractal Resonance Processor (FRP)

## Current Installation — FRP v3.3.0 / M31

Current repository release:

`FRP v3.3.0 / M31 — PASS`

Current milestone:

`M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication`

Current Python environment:

`Python 3.12+`

Current balanced ternary domain:

`-1/0/1`

Current M31 focused qualification:

`60 / 60 PASS`

## 1. Installation Boundary

Run the following commands from the root of a clean repository checkout on branch `main`.

Confirm Python:

```
python --version
```

Install the declared dependencies:

```
python -m pip install --disable-pip-version-check -r requirements.txt
```

The dependency boundary is defined by [`requirements.txt`](requirements.txt):

- `jsonschema==4.25.1`;
- `numpy>=1.26.0`.

## 2. Verify the M31 Source and Test Boundary

Required source:

[`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py)

Required test module:

[`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py)

Run the complete focused M31 suite:

```
python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v
```

Expected result:

```
Ran 60 tests

OK
```

## 3. Verify the Published M31 Evidence

Verify the canonical files already published in the repository:

```
python frp_m31_phase_interference_thermal_evidence.py \
  --verify \
  --repository-root . \
  --output-root . \
  --output /tmp/m31-verification.json
```

Run the internal M31 self-test:

```
python frp_m31_phase_interference_thermal_evidence.py \
  --self-test \
  --repository-root . \
  --output /tmp/m31-self-test.json
```

Both commands emit canonical JSON and return exit code `0` on a passing boundary.

## 4. Reproduce the M31 Publication in a Temporary Directory

Create a temporary output directory and reproduce the complete publication:

```
M31_REPLAY_ROOT="$(mktemp -d)"

python frp_m31_phase_interference_thermal_evidence.py \
  --generate \
  --repository-root . \
  --output-root "$M31_REPLAY_ROOT" \
  --output "$M31_REPLAY_ROOT/generation.json"
```

The generated publication contains the schema, evidence, manifest, and qualification records under the temporary output root.

## 5. Current Canonical M31 Files

| Role | Path |
|---|---|
| Source | [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py) |
| Test | [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py) |
| Schema | [`schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json) |
| Evidence | [`artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json) |
| Manifest | [`artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json) |
| Qualification | [`artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json) |

## 6. Current Release Records

- validation index: [`FRP_VALIDATION_INDEX_v3_3_0.md`](FRP_VALIDATION_INDEX_v3_3_0.md);
- release notes: [`RELEASE_NOTES_v3_3_0.md`](RELEASE_NOTES_v3_3_0.md);
- test report: [`TEST_REPORT_v3_3_0.md`](TEST_REPORT_v3_3_0.md);
- complete qualification workflow: [`.github/workflows/frp-m31-complete.yml`](.github/workflows/frp-m31-complete.yml).

The complete workflow is launched manually from GitHub Actions on branch `main`.

## 7. Semantic Foundation and M30 Archive

The executable semantic foundation remains [`frp_prototype_v1_7_0.py`](frp_prototype_v1_7_0.py). The versioned M17–M31 producers extend the qualified repository through publication, evidence, correlation, interface, verification, compatibility, archival, and M31 thermal-evidence layers.

The M30 archival package remains available at [`artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz`](artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz).

## 8. Observatory Installation Boundary

FRP-Trace-Observatory is an independent downstream consumer. It reads FRP-published bytes, schemas, identifiers, digests, and provenance through the one-way, read-only interchange. FRP installation and qualification remain rooted in this repository.

## 9. Historical Installation Records

Historical executable references, requirements, commands, workflow records, test reports, validation indices, release notes, schemas, evidence, and benchmark contours retain their original release identity below.

## Preserved Installation History Through M30

**Ternary Resonant Coherence Processor — Structured Output Prototype**

## Installation

This document defines the installation, first-run, validation, and deterministic reproduction path for the current Fractal Resonance Processor (FRP) release layer, including the M15-qualified executable semantic reference, the M16 integrated SystemVerilog RTL execution layer, and the M16 target-independent FPGA preparation layer.

FRP is a ternary resonant coherence processor.

Its computational mechanism combines resonant phase dynamics, coherence evolution, stateful feedback, and balanced ternary state retention.

The processor combines:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`cell phase and frequency state`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric phase lag gamma`

↓

`hierarchical fractal coupling`

↓

`phase evolution`

↓

`resonance selection`

↓

`Kuramoto order parameter R and multiscale phase coherence`

↓

`delay dynamics`

↓

`local thermal-phase interaction`

↓

`local correlated gamma drift`

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

↓

`M15 deterministic implementation mapping and qualification closure`

↓

`M16 integrated SystemVerilog RTL execution`

↓

`M16 executable architectural testbench and invariant evaluation`

↓

`M16 target-independent FPGA integration, reset synchronization, readiness, and execution-input gating`

↓

`M16 RTL and FPGA preparation qualification closure`

The balanced ternary domain is:

`{-1, 0, 1}`

The neutral state is:

`0`

The neutral state remains an active balancing, damping, transition, and stabilization state.

Validated opposite-polarity routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Validated kernel invariant:

`actual_direct_events = 0`

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Main executable semantic reference file:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Inherited M15 architecture document:

`docs/m15_implementation_mapping_domain_interface_qualification_closure.md`

Current M16 architecture document:

`docs/m16_rtl_core_realization_execution_semantics.md`

Mathematical foundation:

`docs/mathematical_foundation.md`

Physical foundation:

`docs/physical_foundation.md`

Current test report:

`TEST_REPORT_v1_8_0.md`

Current validation index:

`FRP_VALIDATION_INDEX_v1_8_0.md`

Current release notes:

`RELEASE_NOTES_v1_8_0.md`

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current M16 RTL qualification workflow:

`.github/workflows/frp-m16-rtl-artifact-boundary.yml`

Current M16 FPGA preparation workflow:

`.github/workflows/frp-m16-fpga-preparation.yml`

Current published validation status:

`PASS`

Inherited validated M15 self-test result:

`41/41 PASS`

Current M16 RTL status:

`M16 RTL EXECUTION LAYER CLOSED`

Current M16 FPGA preparation status:

`M16 FPGA PREPARATION LAYER CLOSED`

## 1. Processor Identity and Computational Core

FRP v1.8.0 is the current RTL execution and FPGA preparation release layer of the processor.

The M15-qualified executable semantic reference remains:

`frp_prototype_v1_7_0.py`

The word `prototype` identifies the executable reference form.

The current M16 execution forms are:

- the integrated SystemVerilog RTL core and executable architectural testbench under `rtl/m16/`;
- the target-independent FPGA integration top and executable integration testbench under `fpga/m16/`.

The processor computational core contains two inseparable domains.

### 1.1 Resonant dynamic domain

The resonant dynamic domain contains:

- cell phases;
- cell frequencies;
- Kuramoto-Sakaguchi phase interaction;
- asymmetric phase lag;
- hierarchical fractal coupling;
- phase evolution;
- resonance selection;
- global and multiscale phase coherence;
- delay dynamics;
- local thermal interaction;
- gamma drift;
- nonlinear coherence compression;
- dynamic stability evaluation.

### 1.2 Ternary state and retention domain

The ternary state and retained-result domain contains:

- balanced ternary states `{-1, 0, 1}`;
- active neutral state `0`;
- phase-derived ternary targets;
- distributed commit;
- transition-fraction control;
- pending neutral routes;
- mandatory tick-separated opposite-polarity routing;
- retained ternary state.

The resonant phase layer drives the dynamic computation.

The ternary layer provides the state, target, transition, and retained-result domain.

Together these domains form the complete FRP computational mechanism.

## 2. What the Executable Semantic Reference and M16 Execution Layers Run

The M15-qualified executable semantic reference is:

`frp_prototype_v1_7_0.py`

The default Python semantic execution path performs the following sequence on every tick:

`scheduler state selection`

↓

`pending neutral-route processing`

↓

`transition-request processing`

↓

`phase-derived target-state processing`

↓

`distributed transition-limit enforcement`

↓

`frequency-delay update`

↓

`local thermal-field update`

↓

`local gamma-drift update`

↓

`thermal coupling-factor update`

↓

`hierarchical Kuramoto-Sakaguchi phase-field update`

↓

`multiscale phase-coherence evaluation`

↓

`nonlinear coherence compression`

↓

`C(t), P(t), and C(t) - P(t) evaluation`

↓

`structured telemetry and trace capture`

Across successive ticks, this execution produces the complete computational relation:

`phase evolution`

↓

`resonance selection`

↓

`phase-coherence accumulation`

↓

`phase-derived ternary target`

↓

`distributed commit`

↓

`active neutral routing`

↓

`retained ternary state`

This is the M15-qualified Python semantic execution path that the installation commands below prepare and run.

The current M16 RTL execution path performs:

`scheduler-state propagation`

↓

`request-lane arbitration`

↓

`pending-route eligibility evaluation`

↓

`active-neutral first-leg evaluation`

↓

`transition-capacity enforcement`

↓

`retained-state and pending-route writeback`

↓

`counter and telemetry update`

↓

`ten integrated invariant-flag evaluations`

The M16 FPGA preparation path adds:

`asynchronous external reset assertion`

↓

`two-stage synchronous reset release`

↓

`core_ready generation`

↓

`tick, counter-clear, and request-valid gating before readiness`

↓

`scheduler and request-interface propagation`

↓

`M16 RTL core execution through the target-independent FPGA integration boundary`

## 3. Kuramoto-Sakaguchi Resonant Phase Layer

Each processor cell has a phase.

The current floating reference coupling path evaluates phase interaction through the term:

`sin(phase_j - phase_i - gamma_effective_i)`

The interaction is combined with:

- hierarchical coupling weights;
- local thermal coupling factors;
- nominal coupling strength;
- local effective gamma.

Current default nominal phase lag:

`gamma = 0.30 × pi`

Current default nominal coupling strength:

`coupling_nominal = 0.28`

Current default fractal coupling exponent:

`fractal_alpha = 0.70`

The current phase velocity is composed from:

`0.060 × current frequency`

+

`scheduler push`

+

`coupling field`

The phase then evolves as:

`phase_i = (phase_i + phase_velocity_i) mod 2π`

This resonant phase evolution forms the processor's evolving computational mechanism.

## 4. Phase Coherence and Kuramoto Order Parameter R

The current executable calculates global phase coherence through the Kuramoto order parameter:

`R = sqrt(mean(cos(phase))² + mean(sin(phase))²)`

The same phase-order calculation is applied across hierarchical domains.

Current multiscale coherence includes:

- pair-domain coherence;
- cluster coherence;
- supercluster coherence;
- global phase coherence;
- coherence dispersion across clusters.

The phase field and coherence field are part of the computation.

The complete FRP execution path includes the phase field, coherence field, transition history, and retained ternary vector.

## 5. Hierarchical Fractal Coupling

The current reference architecture uses a dyadic hierarchical ultrametric topology.

Current default cell count:

`16`

Current default hierarchy depth:

`4`

Current default fractal coupling exponent:

`0.70`

The coupling field is constructed from hierarchy-level interactions with level-dependent connection weights.

The hierarchical path includes:

- dyadic hierarchy depth;
- hierarchical distance;
- shell population;
- level-dependent phase-coupling weights;
- exact normalized fixed-point topology closure.

Current validated topology exactness marker:

`fixed_point_topology_sum_exact = True`

The current floating reference also preserves a dense interaction path for correlation and equivalence analysis.

## 6. Delay Dynamics

Current default delay coefficient:

`delay_alpha = 0.30`

Each cell maintains:

- base frequency;
- frequency target;
- current frequency.

The current frequency target includes contributions from:

- base frequency;
- current ternary state;
- switching activity.

The current frequency approaches its target through the delayed relation:

`current frequency += delay_alpha × (target frequency - current frequency)`

The resulting frequency lag contributes to:

- local generated power;
- phase evolution;
- coherence evaluation;
- dynamic stability.

The delay layer is therefore part of the resonant computational path.

## 7. Local Thermal-Phase Interaction

The current architecture tracks distributed local thermal state.

Each cell contains:

- generated power;
- thermal dissipation;
- thermal diffusion;
- local heat;
- thermal overload.

The local thermal field is affected by:

- switching activity;
- frequency lag;
- ambient heat;
- thermal relaxation;
- thermal diffusion.

Thermal state feeds back into the resonant phase layer through:

- local thermal coupling factors;
- local gamma drift;
- nonlinear coherence compression.

The current processor therefore contains a coupled dynamic relation:

`phase and frequency dynamics`

↓

`local generated power`

↓

`thermal field`

↓

`effective coupling and gamma drift`

↓

`phase evolution`

↓

`coherence`

↓

`stability`

## 8. Local Gamma Drift

The current architecture uses:

- nominal gamma;
- deterministic correlated gamma-noise targets;
- gamma-noise state;
- thermal overload;
- effective local gamma.

The effective local gamma is derived from the nominal phase lag plus a thermal and correlated-noise contribution.

The resulting local gamma enters the Kuramoto-Sakaguchi phase interaction.

The M15-qualified hardware-facing path also externalizes deterministic gamma-noise targets into the verification stimulus stream.

Validated verification fields include:

`gamma_noise_update_valid`

`gamma_noise_target_q[cell]`

## 9. Nonlinear Coherence Compression

The current executable applies nonlinear coherence compression to raw phase coherence.

The resulting relation is:

`effective coherence = raw phase coherence × coherence compression`

The compression factor decreases under increasing:

- thermal overload;
- stability-margin pressure.

This nonlinear layer preserves a bounded effective coherence response under increasing coupled load.

It is part of the M15-qualified v1.7.0 executable semantic reference behavior.

## 10. Dynamic Stability

The current processor tracks:

`C(t)`

`P(t)`

`C(t) - P(t)`

Current destabilizing load:

`P(t) = heat + switch_load`

Required validated condition:

`C_minus_P_min > 0.0`

The current coherence state includes contributions from:

- effective phase coherence;
- cluster coherence;
- neutral-state fraction;
- frequency-lag penalty.

The stability layer therefore remains coupled to the phase, delay, thermal, coherence, and ternary-transition layers.

## 11. Phase-Derived Ternary Targets

The current executable derives automatic ternary targets from the evolving phase field.

Current mapping:

`sin(phase) > 0.33 → 1`

`sin(phase) < -0.33 → -1`

`otherwise → 0`

This mapping connects the resonant phase domain to the balanced ternary state domain.

The ternary target enters bounded distributed transition processing.

The target is processed through:

- transition-fraction control;
- distributed commit;
- active neutral routing;
- pending-route retention;
- scheduler timing.

## 12. Active Neutral Routing

The current processor prohibits actual direct opposite-polarity execution.

Prohibited direct transition:

`-1 ↔ 1`

Validated routes:

`-1 → 0 → 1`

`1 → 0 → -1`

Validated tick-separated relation:

`tick N: active polarity → 0`

↓

`pending neutral route retained`

↓

`tick N+1 or later: 0 → target polarity`

Required invariant:

`actual_direct_events = 0`

Additional current invariants:

`reserved_state_events = 0`

`queue_overflow_events = 0`

## 13. Distributed Commit

The current processor applies bounded distributed transition capacity to the ternary state vector.

Current default transition fraction:

`0.25`

Current relation:

`maximum changes per tick = round(cells × transition_fraction)`

For the default 16-cell configuration:

`request_lanes = 4`

The current default validated switching boundary is:

`switch_load_peak <= 0.25`

Distributed commit connects the resonant phase-derived target path to bounded state transition and retained ternary state.

## 14. Requirements

Use the current CI-aligned Python environment:

`Python 3.12`

Required tools:

- Python;
- pip;
- Git when cloning the repository;
- Verilator for M16 RTL and FPGA preparation execution;
- g++ for generated executable SystemVerilog testbenches.

The current dependency file is:

`requirements.txt`

Repository external dependency:

`numpy>=1.26.0`

NumPy is used by the historical FRP v0.9.3 and v0.9.4 executable layers. The M15-qualified FRP v1.7.0 executable semantic reference and Comparative Architecture Benchmark Suite use the Python standard library and repository-local modules. The M16 RTL and FPGA preparation paths use Verilator and g++.

Check the local tools:

    python --version
    python -m pip --version
    git --version
    verilator --version
    g++ --version

On systems where the interpreter command is:

`python3`

replace `python` with `python3` throughout.

## 15. Obtain the Repository

Clone:

    git clone https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor.git

Enter the repository directory:

    cd Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor

Confirm that the executable semantic reference exists:

    python -c "from pathlib import Path; p=Path('frp_prototype_v1_7_0.py'); print(p, p.exists())"

Required result:

`frp_prototype_v1_7_0.py True`

Confirm that the current M16 source boundaries exist:

    python -c "from pathlib import Path; paths=[Path('rtl/m16/frp_m16_tb.sv'), Path('fpga/m16/frp_m16_fpga_top.sv'), Path('fpga/m16/frp_m16_fpga_tb.sv')]; print([(str(p), p.exists()) for p in paths])"

Required result:

`all three paths report True`

When using a downloaded archive instead of Git, unpack the complete archive and run the remaining commands from the repository root.

## 16. Create a Virtual Environment

Create:

    python -m venv .venv

### Linux and macOS

Activate:

    source .venv/bin/activate

### Windows PowerShell

Activate:

    .venv\Scripts\Activate.ps1

### Windows Command Prompt

Activate:

    .venv\Scripts\activate.bat

After activation, verify:

    python --version

## 17. Install Dependencies and the M16 Toolchain

Upgrade pip:

    python -m pip install --upgrade pip

Install the declared dependency set:

    python -m pip install -r requirements.txt

Verify NumPy:

    python -c "import numpy; print(numpy.__version__)"

The installed version must satisfy:

`numpy>=1.26.0`

The M16 GitHub Actions workflows install the CI-aligned SystemVerilog toolchain with:

    sudo apt-get update
    sudo apt-get install --yes verilator g++

Verify the installed M16 toolchain:

    verilator --version
    g++ --version

Local M16 execution requires both commands to complete with exit status `0`.

## 18. Python Compile and M16 Toolchain Gates

Run:

    python -m py_compile frp_prototype_v1_7_0.py

Required result:

`PASS`

A successful compile gate completes with exit status `0`.

Run the M16 toolchain gates:

    verilator --version
    g++ --version

Required result:

`PASS`

Each toolchain gate completes with exit status `0`.

## 19. Inspect the Current Command Interface

Run:

    python frp_prototype_v1_7_0.py --help

The current interface includes:

- `--mode {demo,self-test,benchmark}`;
- `--output {text,json}`;
- `--include-trace`;
- `--scheduler {free,7/1,1/7}`;
- `--cells`;
- `--steps`;
- `--seed`;
- `--transition-fraction`;
- `--gamma`;
- `--fractal-alpha`;
- `--thermal-beta`;
- `--ambient-heat`;
- `--thermal-time-constant`;
- `--thermal-soft-limit`;
- `--thermal-hard-limit`;
- `--coupling-nominal`;
- `--delay-alpha`;
- `--thermal-diffusion-gain`;
- `--equivalence-tolerance`;
- `--vector-output-dir`;
- `--export-fixed-point-interface-profile`;
- `--export-balanced-ternary-hardware-encoding-map`;
- `--export-quantized-reference-shadow-model`;
- `--export-cycle-exact-reference-trace`;
- `--export-rtl-comparison-vector-package`;
- `--export-systemverilog-testbench-interface-map`;
- `--export-synthesizable-rtl-reference-core`;
- `--export-rtl-assertion-correlation-harness`;
- `--export-reference-rtl-equivalence-report`;
- `--export-qualification-closure-manifest`;
- `--export-benchmark-matrix`.

## 20. M15 Executable Semantic Reference First Run

Run the M15-qualified executable semantic reference:

    python frp_prototype_v1_7_0.py --mode demo

Expected leading markers:

`FRP v1.7.0`

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

`kind: demo`

Expected preserved-kernel markers:

- `balanced_ternary_state_domain: True`;
- `reserved_state_events: 0`;
- `actual_direct_events: 0`;
- `fixed_point_topology_sum_exact: True`;
- `fixed_point_thermal_sum_exact: True`.

Default scheduler:

`7/1`

Default 64-tick scheduler counts:

`balance = 56`

`commit = 8`

## 21. What the M15 First Run Executes

The first run executes the M15-qualified coupled processor path:

`phase and frequency state`

↓

`Kuramoto-Sakaguchi coupling`

↓

`hierarchical resonant interaction`

↓

`phase evolution`

↓

`resonance selection`

↓

`global and multiscale coherence`

↓

`delay and thermal feedback`

↓

`nonlinear coherence compression`

↓

`dynamic stability evaluation`

↓

`phase-derived ternary target`

↓

`distributed transition`

↓

`active neutral routing`

↓

`retained ternary state`

The first run therefore exercises both the resonant computational mechanism and the balanced ternary state-retention mechanism.

## 22. M15 Structured JSON First Run

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json

Expected schema:

`frp.structured_output.v1.7.0`

Expected version:

`1.7.0`

Expected milestone:

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

Default configuration:

| Parameter | Value |
|---|---:|
| cells | `16` |
| hierarchy depth | `4` |
| request lanes | `4` |
| steps | `64` |
| seed | `76` |
| scheduler | `7/1` |
| transition fraction | `0.25` |
| gamma | `0.30 × pi` |
| fractal alpha | `0.70` |
| coupling nominal | `0.28` |
| delay alpha | `0.30` |

Required default summary invariants:

- `balanced_ternary_state_domain = True`;
- `reserved_state_events = 0`;
- `actual_direct_events = 0`;
- `queue_overflow_events = 0`;
- `scheduler_counts_valid = True`;
- `fixed_point_topology_sum_exact = True`;
- `fixed_point_thermal_sum_exact = True`;
- `switch_load_peak <= 0.25`;
- `C_minus_P_min > 0.0`.

## 23. M15 Full Trace Output

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace

The full structured output adds:

- `trace`;
- `cell_trace`;
- `route_events`.

The default configuration records:

- `64` processor ticks;
- `1024` cell-tick rows;
- route-event history;
- phase and coherence telemetry;
- thermal and stability telemetry.

Use full trace output when exact tick-by-tick or cell-by-cell inspection is required.

## 24. M15 Standard Self-Test

Run:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Required result:

| Field | Required value |
|---|---|
| `schema` | `frp.structured_output.v1.7.0` |
| `version` | `1.7.0` |
| `status` | `PASS` |
| `check_count` | `41` |
| all values in `checks` | `True` |

Current validated result:

`41/41 PASS`

## 25. M15 Full Scheduler Self-Test Matrix

Run the default profile:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Run the free scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

Run the 7/1 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

Run the 1/7 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Every profile must report:

`status = PASS`

`check_count = 41`

All 41 checks must be:

`True`

## 26. M15 Scheduler Layer

The M15-qualified executable semantic reference preserves three scheduler modes.

| Scheduler | 16-tick validated profile |
|---|---|
| `free` | `free = 16` |
| `7/1` | `balance = 14`, `commit = 2` |
| `1/7` | `excite = 2`, `neutralize = 14` |

Validated default 64-tick 7/1 profile:

`balance = 56`

`commit = 8`

The scheduler contributes directly to the resonant phase layer.

The M15-qualified executable semantic reference also applies scheduler-dependent phase push during phase evolution.

## 27. Cell-Count Rule

The `--cells` value must be:

- a power of two;
- at least `2`.

Valid examples:

`2`

`8`

`16`

`32`

The current command interface validates this cell-count rule before execution.

## 28. Balanced Ternary Hardware Encoding

FRP v1.7.0 defines the canonical two-bit balanced ternary encoding:

`-1 → 2'b11`

`0 → 2'b00`

`+1 → 2'b01`

Reserved encoding:

`2'b10`

Canonical integer encoding:

`-1 → 3`

`0 → 0`

`+1 → 1`

Reserved integer code:

`2`

Required invariant:

`reserved_state_events = 0`

The hardware encoding provides the hardware-facing representation of the ternary state domain within the complete FRP computational mechanism.

The resonant phase-coherence core remains upstream of the ternary target, transition, and retained-state path.

## 29. M15 Hardware-Facing Numeric Profile

M15-qualified primary numeric representations:

| Domain | Representation |
|---|---|
| general dynamic scalar | `S32Q16` |
| normalized coefficient | `S32Q30` |
| phase | `PHASE_U32` |
| Sakaguchi gamma offset | `GAMMA_S32` |

Current deterministic trigonometric profile:

`4096-entry full-cycle lookup table`

Validated exactness markers:

`fixed_point_topology_sum_exact = True`

`fixed_point_thermal_sum_exact = True`

## 30. Benchmark-Matrix Smoke Check

Run:

    python frp_prototype_v1_7_0.py --mode benchmark

Expected schema:

`frp.m3.benchmark_matrix.v1.7.0`

Expected row count:

`5`

Expected architecture order:

1. `frp_v1_6_0_m14_floating_semantic_reference`;
2. `frp_v1_7_0_quantized_hardware_shadow`;
3. `frp_v1_7_0_cycle_exact_vector_package`;
4. `frp_v1_7_0_systemverilog_correlation_contract`;
5. `frp_v1_7_0_qualification_closure`.

Equivalent export command:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix

## 31. M15 Export Smoke Check

Generate the fixed-point interface profile:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile

Generate the balanced ternary hardware encoding map:

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map

Generate the quantized reference shadow model:

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model

Generate the cycle-exact reference trace:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace

Generate the RTL comparison vector package:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package

Generate the SystemVerilog testbench interface map:

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map

Generate the synthesizable RTL reference core:

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core

Generate the RTL assertion correlation harness:

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness

Generate the reference RTL equivalence report:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report

Generate the qualification closure manifest:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

The qualification closure manifest must report:

`status = PASS`

The manifest must contain:

`10`

M15 artifact layers.

## 32. M15 Artifact Schemas

| Artifact | Required schema |
|---|---|
| fixed-point interface profile | `frp.m15.fixed_point_interface_profile.v1.7.0` |
| balanced ternary hardware encoding map | `frp.m15.balanced_ternary_hardware_encoding_map.v1.7.0` |
| quantized reference shadow model | `frp.m15.quantized_reference_shadow_model.v1.7.0` |
| cycle-exact reference trace | `frp.m15.cycle_exact_reference_trace.v1.7.0` |
| RTL comparison vector package | `frp.m15.rtl_comparison_vector_package.v1.7.0` |
| SystemVerilog testbench interface map | `frp.m15.systemverilog_testbench_interface_map.v1.7.0` |
| synthesizable RTL reference core | `frp.m15.synthesizable_rtl_reference_core.v1.7.0` |
| RTL assertion correlation harness | `frp.m15.rtl_assertion_correlation_harness.v1.7.0` |
| reference RTL equivalence report | `frp.m15.reference_rtl_equivalence_report.v1.7.0` |
| qualification closure manifest | `frp.m15.qualification_closure_manifest.v1.7.0` |

## 33. Deterministic RTL Vector Check

Create two output directories:

    mkdir -p vectors_a
    mkdir -p vectors_b

Generate package A:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_a > vector-package-a.json

Generate package B independently:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir vectors_b > vector-package-b.json

Compare the generated vector directories:

    diff -qr vectors_a vectors_b

Required result:

`byte-identical equality`

Expected vector files:

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

The independently generated vector directories must be byte-identical.

## 34. Scaling Smoke Check

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

Every scaling run must preserve:

- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- balanced ternary state-domain validity;
- valid scheduler counts;
- exact fixed-point topology sum;
- exact fixed-point thermal sum.

## 35. M16 RTL Installation Verification

The M16 RTL source boundary contains ten SystemVerilog files under:

`rtl/m16/`

Prepare an isolated build directory:

    rm -rf /tmp/frp_m16_obj
    rm -f /tmp/frp_m16_build.log
    rm -f /tmp/frp_m16_execution.log
    mkdir -p /tmp/frp_m16_obj

Build the integrated M16 RTL testbench:

    verilator --sv --timing --assert --binary \
      --top-module frp_m16_tb \
      -Irtl/m16 \
      --Mdir /tmp/frp_m16_obj \
      rtl/m16/frp_m16_tb.sv \
      2>&1 | tee /tmp/frp_m16_build.log

Check the generated executable:

    test -x /tmp/frp_m16_obj/Vfrp_m16_tb

Run the executable architectural testbench:

    /tmp/frp_m16_obj/Vfrp_m16_tb \
      2>&1 | tee /tmp/frp_m16_execution.log

Required terminal output:

`FRP M16 deterministic RTL testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`ticks_recorded=16`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

The executable RTL testbench validates:

- scheduler modes `free`, `7/1`, and `1/7`;
- request-lane arbitration;
- active-neutral first-leg execution;
- retained pending-route completion;
- transition-capacity saturation;
- retained-state writeback;
- counter clearing with retained state preserved;
- SystemVerilog assertion execution;
- all ten integrated invariant flags.

## 36. M16 FPGA Preparation Installation Verification

The M16 FPGA preparation source boundary contains:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`.

Prepare an isolated FPGA integration build directory:

    rm -rf /tmp/frp_m16_fpga_obj
    rm -f /tmp/frp_m16_fpga_top_lint.log
    rm -f /tmp/frp_m16_fpga_build.log
    rm -f /tmp/frp_m16_fpga_execution.log
    mkdir -p /tmp/frp_m16_fpga_obj

Elaborate the target-independent FPGA integration top:

    verilator --sv --lint-only \
      --top-module frp_m16_fpga_top \
      -Irtl/m16 \
      -Ifpga/m16 \
      fpga/m16/frp_m16_fpga_top.sv \
      2>&1 | tee /tmp/frp_m16_fpga_top_lint.log

Build the executable FPGA integration testbench:

    verilator --sv --timing --assert --binary \
      --top-module frp_m16_fpga_tb \
      -Irtl/m16 \
      -Ifpga/m16 \
      --Mdir /tmp/frp_m16_fpga_obj \
      fpga/m16/frp_m16_fpga_tb.sv \
      2>&1 | tee /tmp/frp_m16_fpga_build.log

Check the generated executable:

    test -x /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Reject latch and multidriven diagnostics:

    ! grep -E '%Warning-(LATCH|MULTIDRIVEN)' \
      /tmp/frp_m16_fpga_top_lint.log \
      /tmp/frp_m16_fpga_build.log

Run the executable FPGA integration testbench:

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb \
      2>&1 | tee /tmp/frp_m16_fpga_execution.log

Required terminal output:

`FRP M16 FPGA integration testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`core_ready=1`

`ticks_recorded=1`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

`invariant_flags=1111111111`

The executable FPGA integration testbench validates:

- asynchronous external reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- tick, counter-clear, and request-valid gating before readiness;
- scheduler propagation;
- request-interface propagation;
- active-neutral first-leg execution;
- retained pending-route completion;
- transition-capacity enforcement;
- retained-state writeback;
- all ten integrated invariant flags.

## 37. Installation Acceptance Criteria

The current FRP v1.8.0 installation is ready when:

- the repository has been cloned or unpacked completely;
- `frp_prototype_v1_7_0.py` exists;
- the declared dependency is installed;
- the compile gate completes with exit status `0`;
- the default processor demo runs;
- the structured output reports schema `frp.structured_output.v1.7.0`;
- the Kuramoto-Sakaguchi resonant phase layer executes;
- the phase-evolution path executes;
- the Kuramoto order parameter and multiscale coherence path execute;
- the phase-derived ternary target path executes;
- the balanced ternary state domain remains valid;
- `actual_direct_events = 0`;
- the standard self-test reports `41/41 PASS`;
- all scheduler-specific self-tests report `41/41 PASS`;
- the benchmark matrix reports the five expected rows;
- the qualification closure manifest reports `PASS`;
- Verilator is installed and reports its version;
- g++ is installed and reports its version;
- the ten-file M16 RTL source boundary is present;
- the M16 RTL executable testbench builds and runs;
- SystemVerilog assertions pass;
- all ten integrated M16 invariant flags remain asserted;
- the M16 RTL terminal record reports `ticks_recorded = 16`;
- the M16 RTL terminal record reports all three zero-event counters as `0`;
- the two-file M16 FPGA preparation source boundary is present;
- the nine required M16 RTL dependencies are present;
- FPGA integration-top elaboration passes;
- the FPGA integration executable testbench builds and runs;
- latch and multidriven diagnostics remain absent;
- asynchronous reset assertion and two-stage synchronous reset release execute;
- `core_ready = 1` after reset release;
- execution inputs remain gated before readiness;
- the FPGA terminal record reports `ticks_recorded = 1`;
- the FPGA terminal record reports all three zero-event counters as `0`;
- the FPGA terminal record reports `invariant_flags = 1111111111`.

For complete deterministic vector reproduction, also require byte-identical equality between independently generated vector directories.

### Published GitHub Actions validation evidence

The current `CI.md` exposes 23 GitHub Actions workflow status badges.

The repository contains 23 GitHub Actions workflow files.

The inherited M15 release evidence recorded in `TEST_REPORT_v1_7_0.md` and `RELEASE_NOTES_v1_7_0.md` includes:

- validated release commit `5fd9a4f`;
- `FRP Structured Output #113 — PASS`;
- `FRP M15 Implementation Mapping and Qualification Closure #1 — PASS`;
- `FRP Self Test #154 — PASS`;
- `FRP Benchmark Smoke Test #152 — PASS`.

The inherited published M15 result is:

`PASS`

The inherited validated M15 self-test result is:

`41/41 PASS`

The current M16 release evidence recorded in `TEST_REPORT_v1_8_0.md`, `FRP_VALIDATION_INDEX_v1_8_0.md`, and `RELEASE_NOTES_v1_8_0.md` includes:

| Layer | Workflow run | Qualified commit | Result | Artifact count | Status |
|---|---:|---|---|---:|---|
| M16 RTL initial closure | `#82` | `a68a2af` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| M16 RTL qualification rerun | `#84` | `ede53cf` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| M16 FPGA preparation initial closure | `#1` | `326b69e` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| M16 FPGA preparation qualification rerun | `#2` | `ede53cf` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

The current published M16 result is:

`PASS`

## 38. Saving M15 Semantic and Mapping Output

Save the default structured demo:

    python frp_prototype_v1_7_0.py --mode demo --output json > frp-v1.7.0-demo.json

Save the full trace:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace > frp-v1.7.0-demo-trace.json

Save the self-test result:

    python frp_prototype_v1_7_0.py --mode self-test --output json > frp-v1.7.0-self-test.json

Save the benchmark matrix:

    python frp_prototype_v1_7_0.py --mode benchmark > frp-v1.7.0-benchmark-matrix.json

Save the qualification closure manifest:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest > frp-v1.7.0-qualification-closure.json

## 39. Running Through the Virtual-Environment Interpreter

Direct interpreter invocation provides the complete virtual-environment execution path.

### Linux and macOS

Use the virtual-environment interpreter directly:

    ./.venv/bin/python -m pip install -r requirements.txt
    ./.venv/bin/python -m py_compile frp_prototype_v1_7_0.py
    ./.venv/bin/python frp_prototype_v1_7_0.py --mode self-test --output json

### Windows PowerShell

Use:

    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m py_compile frp_prototype_v1_7_0.py
    .venv\Scripts\python.exe frp_prototype_v1_7_0.py --mode self-test --output json

## 40. Updating an Existing Clone

Enter the repository directory:

    cd Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor

Inspect the working tree before updating:

    git status

Update the current branch:

    git pull

Refresh dependencies:

    python -m pip install -r requirements.txt

Re-run the compile gate:

    python -m py_compile frp_prototype_v1_7_0.py

Re-run the M15-qualified self-test:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Re-check the M16 toolchain:

    verilator --version
    g++ --version

Re-run the M16 RTL installation verification from Section 35.

Re-run the M16 FPGA preparation installation verification from Section 36.

## 41. Troubleshooting

### Python command resolution

Check the available interpreter command:

    python3 --version

Use `python3` for the remaining commands when that interpreter is available.

### pip command resolution

Use:

    python -m pip install -r requirements.txt

### NumPy import verification

Run:

    python -m pip install -r requirements.txt

Then verify:

    python -c "import numpy; print(numpy.__version__)"

### Verilator command resolution

Check:

    verilator --version

The M16 RTL and FPGA preparation commands require the `verilator` command to resolve successfully.

### g++ command resolution

Check:

    g++ --version

The executable M16 SystemVerilog testbench builds require the `g++` command to resolve successfully.

### Virtual-environment interpreter path

Use the virtual-environment interpreter directly as shown in Section 39.

### PowerShell blocks activation

Use:

    .venv\Scripts\python.exe frp_prototype_v1_7_0.py --mode self-test --output json

Direct interpreter invocation uses the virtual environment immediately.

### `--cells` validation

The current executable requires:

- a power-of-two cell count;
- at least `2` cells.

Valid examples:

`2`

`8`

`16`

`32`

### Self-test result diagnosis

Record:

    git rev-parse HEAD
    git status --short
    python --version
    python -m pip freeze
    verilator --version
    g++ --version

Then compare the local source revision and environment with:

- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `REPRODUCIBILITY.md`;
- `CI.md`.

### M16 RTL build or execution diagnosis

Check:

- Verilator version;
- g++ version;
- `rtl/m16/` source completeness;
- top module `frp_m16_tb`;
- include path `rtl/m16`;
- `/tmp/frp_m16_build.log`;
- `/tmp/frp_m16_execution.log`;
- generated executable `/tmp/frp_m16_obj/Vfrp_m16_tb`;
- SystemVerilog assertion results;
- terminal zero-event counters.

### M16 FPGA preparation diagnosis

Check:

- Verilator version;
- g++ version;
- `fpga/m16/` source completeness;
- required `rtl/m16/` dependencies;
- top module `frp_m16_fpga_top`;
- testbench module `frp_m16_fpga_tb`;
- `/tmp/frp_m16_fpga_top_lint.log`;
- `/tmp/frp_m16_fpga_build.log`;
- `/tmp/frp_m16_fpga_execution.log`;
- latch and multidriven diagnostics;
- `core_ready` terminal state;
- terminal zero-event counters;
- integrated invariant flags.

## 42. Complete Current Technical Chain

The repository preserves the processor architecture and qualification chain:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

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

`local correlated gamma drift`

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

`benchmark export and hardware signal mapping`

↓

`HDL trace and testbench preparation`

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

`M15 qualification closure`

↓

`M16 integrated SystemVerilog scheduler execution`

↓

`M16 deterministic request-lane arbitration`

↓

`M16 active-neutral routing and retained pending-route completion`

↓

`M16 transition-capacity enforcement and retained-state writeback`

↓

`M16 executable architectural testbench and SystemVerilog assertions`

↓

`M16 ten-flag integrated invariant evaluation`

↓

`M16 RTL execution qualification closure`

↓

`M16 target-independent FPGA integration top`

↓

`M16 asynchronous reset assertion and two-stage synchronous reset release`

↓

`M16 core_ready and execution-input gating`

↓

`M16 executable FPGA integration testbench`

↓

`M16 FPGA preparation qualification closure`

The resonant computational core remains the processor mechanism throughout this chain.

The balanced ternary domain remains the state and retained-result domain throughout this chain.

## 43. Current File Alignment

This installation path is aligned with:

- `README.md`;
- `frp_prototype_v1_7_0.py`;
- `requirements.txt`;
- `USAGE.md`;
- `REPRODUCIBILITY.md`;
- `CI.md`;
- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`;
- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `docs/m16_rtl_core_realization_execution_semantics.md`;
- `docs/m16_rtl_core_interface_contract.md`;
- `docs/m16_scheduler_state_rtl_realization.md`;
- `docs/m16_request_lane_arbitration_module.md`;
- `docs/m16_pending_route_register_module.md`;
- `docs/m16_active_neutral_transition_module.md`;
- `docs/m16_transition_capacity_guard_module.md`;
- `docs/m16_retained_state_update_module.md`;
- `docs/m16_invariant_assertion_set.md`;
- `docs/m16_external_simulator_execution_plan.md`;
- `docs/m16_m15_vector_replay_compatibility_report.md`;
- `docs/m16_rtl_artifact_boundary_qualification.md`;
- `docs/m16_artifact_boundary_test_stability_policy.md`;
- `docs/m16_qualification_manifest.md`;
- `docs/m16_qualification_index.md`;
- `docs/m16_public_status_snapshot.md`;
- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`;
- `rtl/m16/frp_m16_pkg.sv`;
- `rtl/m16/frp_m16_scheduler.sv`;
- `rtl/m16/frp_m16_request_lanes.sv`;
- `rtl/m16/frp_m16_pending_routes.sv`;
- `rtl/m16/frp_m16_active_neutral.sv`;
- `rtl/m16/frp_m16_capacity_guard.sv`;
- `rtl/m16/frp_m16_state_update.sv`;
- `rtl/m16/frp_m16_core.sv`;
- `rtl/m16/frp_m16_assertions.sv`;
- `rtl/m16/frp_m16_tb.sv`;
- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`;
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`;
- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`.

Historical executable files and historical release records remain bound to their corresponding release layers.

## 44. Current Status

Processor:

`Fractal Resonance Processor (FRP)`

Processor class:

`Ternary Resonant Coherence Processor`

Computational mechanism:

`Kuramoto-Sakaguchi resonant phase dynamics with hierarchical fractal coupling, phase evolution, resonance selection, Kuramoto order parameter R, multiscale phase coherence, delay dynamics, coupled thermal-phase behavior, nonlinear coherence compression, phase-derived ternary targets, distributed commit, and mandatory active-neutral routing`

State and retained-result domain:

`{-1, 0, 1}`

Active neutral state:

`0`

Current Python executable semantic-reference form:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

Current version:

`FRP v1.8.0`

Current milestone:

`M16 — RTL Core Realization and Execution Semantics Package`

Current Python executable semantic reference:

`frp_prototype_v1_7_0.py`

Current structured-output schema:

`frp.structured_output.v1.7.0`

Current benchmark-matrix schema:

`frp.m3.benchmark_matrix.v1.7.0`

Current published validation result:

`PASS`

Inherited M15 validated self-test result:

`41/41 PASS`

Inherited M15 qualification workflow:

`.github/workflows/frp-m15-implementation-mapping-qualification.yml`

Current M16 RTL execution layer:

| Qualification record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#84` |
| Qualified source commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation layer:

| Qualification record | Value |
|---|---|
| Workflow | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#2` |
| Qualified repository commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Artifact count | `1` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

Current terminal invariant records:

| Record | Value |
|---|---:|
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| RTL invariant flags | `1111111111` |
| FPGA invariant flags | `1111111111` |

Current mathematical foundation:

`docs/mathematical_foundation.md`

Current physical foundation:

`docs/physical_foundation.md`








