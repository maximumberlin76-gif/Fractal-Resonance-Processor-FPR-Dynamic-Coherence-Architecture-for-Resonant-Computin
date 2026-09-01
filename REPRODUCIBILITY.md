# Fractal Resonance Processor (FRP)

**Ternary Fractal Resonant Coherence Processor**

## Reproducibility

This document defines the clean-environment reproduction and byte-verification procedure for **FRP v3.3.0 / M31**.

## Release boundary

| Field | Reproducible record |
|---|---|
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification | `PASS` |
| Focused M31 tests | `60 / 60 PASS` |
| Qualification checks | `13 / 13 PASS` |
| Canonical M31 outputs | `4 / 4 exact` |
| Preserved archival baseline | `FRP v3.2.0 / M30 — PASS` |
| Python | `3.12+` |

The M31 reproduction boundary preserves balanced ternary notation `-1/0/1`, active state `0`, temporal scheduler modes `1/7` and `7/1`, and the separate service scheduler mode `free`.

## Reproducibility guarantees

The procedure verifies:

1. exact identities of the M31 producer, tests, schema, evidence, manifest, and qualification record;
2. exact identity and member continuity of the preserved M30 archival package;
3. all 60 focused M31 qualification tests;
4. two independent M31 generations with byte-identical outputs;
5. byte identity between independently generated and committed M31 outputs;
6. exact reproduction of the historical FRP v0.9.3 model workload;
7. preservation of evidence, benchmark, schema, and release histories.

The focused M31 suite qualifies the M31 publication boundary. The repository-wide regression is reserved for final documentation and release closure.

## 1. Create a clean Python 3.12 environment

Clone the repository and enter it:

```
git clone https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor.git
cd Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor
git switch main
git status --porcelain
```

The final command must produce no output.

Create an isolated environment outside the repository:

```
python3.12 -m venv /tmp/frp-v3.3.0-venv
. /tmp/frp-v3.3.0-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python --version
```

Expected Python line:

`Python 3.12.x`

## 2. Verify immutable source identities

| Path | Bytes | SHA-256 |
|---|---:|---|
| `requirements.txt` | `33` | `75b9bd6237473a063c852298fee983bdfcf550cb1cc828a237afaf726cccc3c7` |
| `frp_m31_phase_interference_thermal_evidence.py` | `42092` | `1e4ccfd7b157cd2bac609c34dfec9da791653a31af7b29b75502c755807b9c62` |
| `tests/test_frp_m31_phase_interference_thermal_evidence.py` | `22370` | `f64214a9c785d8cf579e3a6a5afa6e364772d8972775cc010a3dba89d852c1ed` |
| `schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json` | `1468` | `53d79d45d70753ccd24c3dc4c97af6fee481f86a9d7cdca7ef78b486c76479f7` |
| `artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json` | `39993` | `bdaa676acbfb09d86d848070e8a2673c5ce6902657a0b13b2e4293383bec8b42` |
| `artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json` | `828` | `80f0841d0041cd22c2f76175b6139e601aede7b69823356ae1fefbce5f793e7c` |
| `artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json` | `1512` | `4c2446f954e01ec0aa37cc6c0fc70cf4a87ec565c450628e31b0efcac9160224` |
| `artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz` | `10189989` | `05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa` |

Run the identity check:

```
python - <<'PY'
import hashlib
from pathlib import Path

expected = {
    "requirements.txt": (33, "75b9bd6237473a063c852298fee983bdfcf550cb1cc828a237afaf726cccc3c7"),
    "frp_m31_phase_interference_thermal_evidence.py": (42092, "1e4ccfd7b157cd2bac609c34dfec9da791653a31af7b29b75502c755807b9c62"),
    "tests/test_frp_m31_phase_interference_thermal_evidence.py": (22370, "f64214a9c785d8cf579e3a6a5afa6e364772d8972775cc010a3dba89d852c1ed"),
    "schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json": (1468, "53d79d45d70753ccd24c3dc4c97af6fee481f86a9d7cdca7ef78b486c76479f7"),
    "artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json": (39993, "bdaa676acbfb09d86d848070e8a2673c5ce6902657a0b13b2e4293383bec8b42"),
    "artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json": (828, "80f0841d0041cd22c2f76175b6139e601aede7b69823356ae1fefbce5f793e7c"),
    "artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json": (1512, "4c2446f954e01ec0aa37cc6c0fc70cf4a87ec565c450628e31b0efcac9160224"),
    "artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz": (10189989, "05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa"),
}
for name, identity in expected.items():
    raw = Path(name).read_bytes()
    observed = (len(raw), hashlib.sha256(raw).hexdigest())
    if observed != identity:
        raise SystemExit(f"identity mismatch: {name}")
print("M31 immutable source identities: PASS")
PY
```

## 3. Run the focused M31 qualification

```
python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v
```

Expected terminal result:

```
Ran 60 tests

OK
```

## 4. Verify the committed canonical publication

```
python frp_m31_phase_interference_thermal_evidence.py --verify
```

The command generates an independent expected publication, compares all four outputs byte-for-byte with the committed records, and reports `status: PASS`.

Run the deterministic self-test:

```
python frp_m31_phase_interference_thermal_evidence.py --self-test
```

## 5. Reproduce two independent output trees

```
replay_a="$(mktemp -d)"
replay_b="$(mktemp -d)"

python frp_m31_phase_interference_thermal_evidence.py \
  --generate \
  --repository-root . \
  --output-root "$replay_a"

python frp_m31_phase_interference_thermal_evidence.py \
  --generate \
  --repository-root . \
  --output-root "$replay_b"
```

Compare both independent trees and the committed outputs:

```
while IFS= read -r record; do
  cmp "$replay_a/$record" "$replay_b/$record"
  cmp "$replay_a/$record" "$record"
done <<'RECORDS'
schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json
artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json
artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json
artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json
RECORDS

echo "Two-run replay and committed publication: BYTE-IDENTICAL"
```

## 6. Reproduce the historical thermal-load contour

Run the exact FRP v0.9.3 model workload captured by M31:

```
python3 frp_prototype_v0_9_3_mobile.py \
  --mode bench \
  --steps 128 \
  --seeds 5 \
  > /tmp/frp-v0.9.3-bench.txt

wc -c /tmp/frp-v0.9.3-bench.txt
sha256sum /tmp/frp-v0.9.3-bench.txt
```

Expected identity:

| Field | Value |
|---|---|
| Exit code | `0` |
| Bytes | `640` |
| SHA-256 | `b18e1affec6dec8029086e923b907c9ae3cb0c50131e4291b31fbd2a4d97cbb6` |

The captured historical model reports `heat_peak` values of `0.051000` and `0.003250`, a ratio of `15.6923076923`, and a relative reduction of `93.63%`. These values remain bound to that exact model and workload as a historical thermal-load contour.

## 7. Verify M30 archival continuity

```
test "$(wc -c < artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz)" -eq 10189989
test "$(sha256sum artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz | cut -d' ' -f1)" = 05ea33f6f3f505d315af930c2d51779f7189905308473f32a57375e477069caa
tar -tzf artifacts/m30/packages/frp-v3.2.0-m30-archival-release.tar.gz > /tmp/frp-m30-members.txt
test -s /tmp/frp-m30-members.txt
echo "M30 archival package identity: PASS"
```

The M31 producer additionally verifies the declared M30 archive members byte-for-byte against the repository records.

## 8. Verify protected repository histories

The M31 documentation workflows preserve these inventories:

| Protected record set | Files | Sorted digest-inventory SHA-256 |
|---|---:|---|
| `artifacts/` | `127` | `0d86a8c50c86ba0196f635903cb8cc8d635dd1399787625f7619ad4dd8121f2b` |
| `benchmarks/` | `19` | `54dc4ae9aa858ccd60f577367be909abf1266b76fcefe10c8223e1f22cc78670` |
| `schemas/` | `125` | `384cede6b31eea78b9e85804405d7d8bb3bec42e0ce8489d3f9ed20d36f213d9` |
| Historical root release records | `51` | `4e9e38fc72b1704712eb4a8da34ee1cdd658c5a1bb69d070954e0cb431dccaa2` |

Each inventory digest is calculated from the lexicographically sorted SHA-256 and repository-relative path of every protected regular file.

## 9. Interpret the result

A complete M31 reproduction records:

| Gate | Result |
|---|---|
| Immutable inputs | `PASS` |
| Focused M31 qualification | `60 / 60 PASS` |
| Qualification checks | `13 / 13 PASS` |
| Canonical outputs | `4 / 4 exact` |
| Independent replay | `BYTE-IDENTICAL` |
| Historical model replay | `PASS` |
| M30 archive continuity | `PASS` |
| Protected histories | `BYTE-IDENTICAL` |

## FRP Trace Observatory boundary

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

Reproduction occurs inside the FRP authority boundary. The Observatory consumes the committed publication through a one-way, read-only interface and preserves FRP semantics, metrics, contours, and bytes.

## Release records

- [FRP v3.3.0 validation index](FRP_VALIDATION_INDEX_v3_3_0.md)
- [FRP v3.3.0 release notes](RELEASE_NOTES_v3_3_0.md)
- [FRP v3.3.0 test report](TEST_REPORT_v3_3_0.md)
- [Current usage](USAGE.md)

## Historical reproducibility record

The complete prior reproducibility document is preserved below as an exact byte sequence. Its release-local “current” labels describe the historical boundary through FRP v3.2.0 / M30.

<details>
<summary>Open the complete historical REPRODUCIBILITY.md through M30</summary>

<!-- Exact historical REPRODUCIBILITY.md begins on the next line. -->
# Fractal Resonance Processor (FRP)

**Ternary Resonant Coherence Processor — Structured Output Prototype**

## Reproducibility

This document defines the complete reproducibility path for the current Fractal Resonance Processor (FRP) release, the M15-qualified executable semantic reference and deterministic implementation mapping, the M16 integrated SystemVerilog RTL execution layer, and the M16 target-independent FPGA preparation layer.

FRP is a ternary resonant coherence processor.

FRP computes through resonant phase dynamics, coherence evolution, stateful feedback, and balanced ternary state retention.

The complete current computational path combines:

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

↓

`deterministic fixed-point implementation mapping`

↓

`stateful quantized hardware shadow execution`

↓

`cycle-exact integer golden trace`

↓

`deterministic RTL comparison vectors`

↓

`SystemVerilog interface mapping`

↓

`RTL assertion correlation`

↓

`reference equivalence`

↓

`M15 qualification closure`

↓

`M16 integrated SystemVerilog RTL execution`

↓

`scheduler execution and request-lane arbitration`

↓

`active-neutral routing and retained pending-route completion`

↓

`transition-capacity enforcement and retained-state writeback`

↓

`ten integrated invariant flags and SystemVerilog assertions`

↓

`target-independent FPGA integration`

↓

`asynchronous reset assertion and two-stage synchronous reset release`

↓

`core_ready and execution-input gating`

↓

`M16 RTL and FPGA preparation qualification closure`

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

`FRP v3.2.0`

Current milestone:

`M30 — Reproducibility, Qualification, and Archival Release Closure`

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

## 1. Reproducibility Target

The reproducibility target is the complete dynamic computational path together with the final retained ternary state vector.

A complete reproduction must preserve the dynamic computational path that produces and retains that state.

The primary reproducibility chain is:

`source revision`

↓

`execution environment`

↓

`deterministic initialization`

↓

`processor configuration`

↓

`balanced ternary state domain`

↓

`phase and frequency initialization`

↓

`hierarchical coupling topology`

↓

`Kuramoto-Sakaguchi phase interaction`

↓

`delay and thermal dynamics`

↓

`local gamma dynamics`

↓

`phase evolution`

↓

`global and multiscale phase coherence`

↓

`nonlinear coherence compression`

↓

`dynamic stability`

↓

`phase-derived ternary target formation`

↓

`distributed commit`

↓

`active neutral routing`

↓

`retained state`

↓

`structured telemetry`

↓

`independent deterministic repeat`

↓

`M15 fixed-point mapping`

↓

`quantized hardware shadow`

↓

`cycle-exact reference trace`

↓

`deterministic RTL vector regeneration`

↓

`reference equivalence`

↓

`qualification closure`

↓

`M16 RTL source-boundary validation`

↓

`M16 executable RTL testbench build and execution`

↓

`M16 assertion and invariant validation`

↓

`M16 FPGA integration-top elaboration`

↓

`M16 executable FPGA integration testbench build and execution`

↓

`M16 reset, readiness, input-gating, route, and invariant validation`

A complete reproduction verifies the connected set of:

- the final `{-1, 0, 1}` vector;
- the two-bit ternary encoding;
- the resonant phase-coherence execution path;
- the retained ternary state path;
- all required M15 artifacts;
- the complete self-test matrix;
- the ten-file M16 SystemVerilog RTL boundary;
- the executable M16 RTL architectural testbench;
- the two-file M16 FPGA preparation boundary;
- the executable M16 FPGA integration testbench;
- the M16 zero-event counters;
- the ten M16 integrated invariant flags.

The resonant phase-coherence path and the retained ternary state path remain connected throughout the reproduction sequence.

## 2. Two Inseparable Reproducibility Domains

The FRP computational core contains two inseparable reproducibility domains.

### 2.1 Resonant dynamic domain

The resonant dynamic domain contains:

- cell phase;
- base frequency;
- target frequency;
- current frequency;
- Kuramoto-Sakaguchi interaction;
- asymmetric phase lag;
- hierarchical fractal coupling;
- scheduler-dependent phase push;
- delayed frequency response;
- distributed thermal state;
- local thermal coupling degradation;
- local gamma drift;
- phase evolution;
- global phase order;
- multiscale phase coherence;
- nonlinear coherence compression;
- dynamic stability.

### 2.2 Balanced ternary state and retention domain

The balanced ternary domain contains:

- states `{-1, 0, 1}`;
- active neutral state `0`;
- phase-derived ternary targets;
- transition requests;
- distributed commit;
- transition-fraction limits;
- pending neutral routes;
- mandatory tick separation;
- scheduler-controlled execution;
- retained ternary state.

The resonant dynamic domain drives the evolving computation.

The ternary domain provides the target, state, transition, and retained-result layer.

A valid reproduction must preserve both.

## 3. Current Executable Semantic Reference and Execution Layers

Use:

`frp_prototype_v1_7_0.py`

The current FRP v1.8.0 release uses the M15-qualified `frp_prototype_v1_7_0.py` executable as its Python semantic reference.

Historical executable references remain preserved for their corresponding historical architecture layers.

The M15-qualified executable semantic reference contains:

- the floating semantic reference path inherited through M14;
- the qualified M15 fixed-point interface contract;
- the stateful quantized hardware shadow;
- deterministic reference traces;
- deterministic vector generation;
- SystemVerilog interface mapping;
- RTL correlation contracts;
- qualification closure.

The current M16 RTL execution source boundary is:

`rtl/m16/`

The current M16 FPGA preparation source boundary is:

`fpga/m16/`

The M16 layer realizes the qualified M15 execution semantics through:

- integrated SystemVerilog scheduler execution;
- deterministic request-lane arbitration;
- active-neutral transition routing;
- retained pending-route completion;
- transition-capacity enforcement;
- retained-state writeback;
- ten integrated invariant flags;
- executable SystemVerilog assertions;
- target-independent FPGA integration;
- reset synchronization, readiness, and execution-input gating.

## 4. Environment

Inherited M15 GitHub Actions environment:

| Parameter | Value |
|---|---|
| runner | `ubuntu-latest` |
| Python | `3.12` |
| workflow timeout | `30 minutes` |

Current M16 RTL GitHub Actions environment:

| Parameter | Value |
|---|---|
| runner | `ubuntu-latest` |
| SystemVerilog simulator and compiler | `Verilator` |
| generated-testbench compiler | `g++` |
| workflow timeout | `20 minutes` |

Current M16 FPGA preparation GitHub Actions environment:

| Parameter | Value |
|---|---|
| runner | `ubuntu-latest` |
| SystemVerilog simulator and compiler | `Verilator` |
| generated-testbench compiler | `g++` |
| workflow timeout | `20 minutes` |

Recommended local environment:

`Python 3.12`

M16 RTL and FPGA preparation tools:

- `Verilator`;
- `g++`.

The declared dependency file is:

`requirements.txt`

Repository external dependency:

`numpy>=1.26.0`

NumPy is used by the historical FRP v0.9.3 and v0.9.4 executable layers. The M15-qualified FRP v1.7.0 executable semantic reference and Comparative Architecture Benchmark Suite use the Python standard library and repository-local modules. The M16 RTL and FPGA preparation paths use Verilator and g++.

Install from the repository root:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

The M16 workflows install the SystemVerilog toolchain with:

    sudo apt-get update
    sudo apt-get install --yes verilator g++

Record the installed tool versions with:

    verilator --version
    g++ --version

On systems where the interpreter command is:

`python3`

replace `python` with `python3`.

## 5. Record the Exact Source State

Before running a reproducibility sequence, record:

    git rev-parse HEAD
    git status --short
    python --version
    python -m pip freeze
    verilator --version
    g++ --version

Preserve:

- exact commit hash;
- working-tree state;
- Python version;
- installed dependency versions;
- Verilator version for M16 RTL and FPGA preparation reproduction;
- g++ version for generated executable testbench reproduction;
- operating environment;
- execution date;
- exact commands used.

Record the working-tree state exactly, including every uncommitted source difference, because those differences can alter deterministic output.

## 6. Required Current Files

Primary executable and dependency files:

- `frp_prototype_v1_7_0.py`;
- `requirements.txt`.

Current architecture and validation files:

- `README.md`;
- `INSTALL.md`;
- `USAGE.md`;
- `REPRODUCIBILITY.md`;
- `CI.md`;
- `docs/core_principles.md`;
- `docs/resonance_computation.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `docs/m16_rtl_core_realization_execution_semantics.md`;
- `TEST_REPORT_v1_8_0.md`;
- `FRP_VALIDATION_INDEX_v1_8_0.md`;
- `RELEASE_NOTES_v1_8_0.md`.

Inherited M15 release evidence files:

- `TEST_REPORT_v1_7_0.md`;
- `FRP_VALIDATION_INDEX_v1_7_0.md`;
- `RELEASE_NOTES_v1_7_0.md`.

Current M16 RTL SystemVerilog files:

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

Current M16 RTL documentation files:

- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`.

Current M16 FPGA preparation files:

- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`.

Inherited M15 qualification workflow:

- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`.

Current M16 qualification workflows:

- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`.

Current M16 maintenance workflows:

- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`.

Historical files preserve release-specific evidence.

The current v1.8.0 reproduction path uses the M15-qualified v1.7.0 executable semantic reference and schemas together with the current M16 RTL, FPGA preparation, validation, and workflow files.

## 7. Install, Compile, and Check Toolchains

Install dependencies:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Compile the M15-qualified executable semantic reference:

    python -m py_compile frp_prototype_v1_7_0.py

Required result:

`PASS`

A successful compile gate completes with exit status `0`.

Check the M16 RTL and FPGA preparation toolchain:

    verilator --version
    g++ --version

Each tool-version command must complete with exit status `0`.

## 8. M15 Executable Semantic Reference Default Configuration

The M15-qualified executable semantic reference default execution configuration is:

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

Derived default values:

| Derived parameter | Value |
|---|---:|
| hierarchy depth | `4` |
| request lanes | `4` |
| packed ternary state width | `32 bits` |

## 9. M15 Executable Internal Deterministic Constants

The M15-qualified executable semantic reference also contains internal constants that contribute to deterministic behavior.

Frequency and delay:

| Parameter | Value |
|---|---:|
| state frequency gain | `0.06` |
| switching frequency gain | `0.12` |
| delay alpha | `0.30` |

Thermal generation:

| Parameter | Value |
|---|---:|
| base power per cell | `0.0018` |
| switching power gain | `0.052` |
| frequency-lag power gain | `0.018` |

Thermal coupling:

| Parameter | Value |
|---|---:|
| thermal coupling gain | `2.50` |

Gamma dynamics:

| Parameter | Value |
|---|---:|
| gamma correlation alpha | `0.15` |
| gamma thermal gain | `0.08` |

Nonlinear coherence compression:

| Parameter | Value |
|---|---:|
| thermal compression gain | `3.0` |
| margin compression gain | `1.5` |
| stability soft margin | `0.25` |

Scheduler phase push:

| Scheduler state | Phase push |
|---|---:|
| `commit` | `0.010` |
| `excite` | `0.006` |
| all other states | `0.003` |

These constants are part of the M15-qualified executable semantic reference behavior.

## 10. Deterministic Initialization

Current default deterministic seed:

`76`

Use:

    python frp_prototype_v1_7_0.py --seed 76 --mode demo --output json

The seed contributes to deterministic initialization and deterministic correlated gamma-noise behavior.

A reproducibility record must preserve the exact seed.

Changing the seed creates a different deterministic execution.

## 11. M15 Semantic and M16 RTL Tick Execution Order

The M15-qualified floating semantic reference tick executes in this order:

`scheduler-state selection`

↓

`switch-activity reset`

↓

`maximum transition capacity calculation`

↓

`pending neutral-route processing`

↓

`explicit transition-request processing`

↓

`phase-derived ternary target processing`

↓

`switch-load update`

↓

`delay-dynamics update`

↓

`local thermal-field update`

↓

`local gamma-drift update`

↓

`thermal coupling-factor update`

↓

`Kuramoto-Sakaguchi phase-field update`

↓

`multiscale phase-coherence evaluation`

↓

`cluster-metric evaluation`

↓

`nonlinear coherence compression and global stability update`

↓

`structured telemetry capture`

This order is part of the M15-qualified semantic reference.

A change in update order can alter deterministic behavior even if every individual formula remains unchanged.

The current M16 RTL tick executes in this order:

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

`accepted transition and route-mask formation`

↓

`retained-state writeback`

↓

`retained pending-route writeback`

↓

`counter and telemetry update`

↓

`ten integrated invariant-flag evaluations`

The M16 RTL reproduction validates scheduler execution, request-lane arbitration, active-neutral routing, retained pending-route completion, transition-capacity enforcement, retained-state writeback, zero-event counters, and integrated invariant flags.

## 12. Phase-to-Target Temporal Relation

The current tick extracts automatic ternary targets from the phase field that exists at the beginning of the target-processing stage.

The same tick then updates:

- delay state;
- thermal state;
- gamma state;
- coupling field;
- phase state;
- coherence state.

Therefore, across successive ticks, the temporal relation is:

`phase field produced by previous evolution`

↓

`current tick ternary target extraction`

↓

`distributed transition`

↓

`delay and thermal update`

↓

`Kuramoto-Sakaguchi phase evolution`

↓

`new phase field`

↓

`next tick ternary target extraction`

This distinction must be preserved.

The reproduction preserves this stateful cross-tick relation exactly.

## 13. Kuramoto-Sakaguchi Resonant Phase Interaction

The current floating reference uses the phase-interaction term:

`sin(phase_j - phase_i - gamma_effective_i)`

The dense reference path evaluates:

`coupling_nominal × sum(weight_ij × thermal_factor_i × thermal_factor_j × sin(phase_j - phase_i - gamma_effective_i))`

The current default nominal coupling strength is:

`0.28`

The current default nominal phase lag is:

`0.30 × pi`

The current hierarchical path evaluates the same interaction through dyadic shell aggregation.

The dense and hierarchical paths provide two reference representations for correlation and equivalence work.

## 14. Hierarchical Fractal Coupling

The current architecture uses a dyadic hierarchical ultrametric topology.

The cell count must be:

- a power of two;
- at least `2`.

Hierarchy depth:

`cells.bit_length() - 1`

Current default:

`16 cells → hierarchy depth 4`

Hierarchical distance between two distinct cells:

`(i XOR j).bit_length()`

Shell population:

`2^(distance - 1)`

Current default fractal exponent:

`0.70`

The current shell-normalized coupling weights preserve exact normalized closure in the M15 fixed-point representation.

Required marker:

`fixed_point_topology_sum_exact = True`

## 15. Hierarchical Coupling Reproducibility

Changes affecting:

- cell count;
- hierarchy depth;
- hierarchical distance;
- shell population;
- coupling weight normalization;
- fractal exponent;
- dense reference path;
- hierarchical accelerated path;

must reproduce:

- deterministic topology;
- exact fixed-point topology closure;
- reference correlation;
- phase-field behavior;
- multiscale coherence behavior.

Topology reproduction covers deterministic topology, exact fixed-point closure, reference correlation, phase-field behavior, multiscale coherence behavior, and the final state.

## 16. Phase Velocity

The current floating reference phase velocity is:

`phase_velocity_i = 0.060 × current_frequency_i + scheduler_push + coupling_field_i`

The scheduler push is:

`commit → 0.010`

`excite → 0.006`

`other scheduler states → 0.003`

The phase then evolves as:

`phase_i = (phase_i + phase_velocity_i) mod 2π`

A valid reproduction must preserve:

- frequency contribution;
- scheduler contribution;
- coupling contribution;
- phase wrapping.

## 17. Global Kuramoto Order Parameter R

The current global phase order is:

`R = sqrt(mean(cos(phase))² + mean(sin(phase))²)`

The executable calculates this through:

`phase_order(phases)`

The same phase-order calculation is used for hierarchical coherence domains.

The phase-order path is part of the processor operational state, and reproduction preserves `R` as a required computational metric.

## 18. Multiscale Phase-Coherence Reproduction

Current coherence domains include:

- pair domain;
- cluster domain;
- supercluster domain;
- global domain.

Current telemetry includes:

- pair-domain coherence mean;
- pair-domain coherence minimum;
- cluster coherence mean;
- cluster coherence minimum;
- supercluster coherence mean;
- supercluster coherence minimum;
- global phase coherence;
- coherence dispersion across clusters.

A change affecting the phase field should inspect all affected scales.

Changes affecting local or hierarchical dynamics are evaluated across every affected coherence scale together with global phase order.

## 19. Delay Dynamics

Each cell maintains:

- base frequency;
- frequency target;
- current frequency.

The current frequency target is:

`base_frequency`

+

`0.06 × abs(ternary state)`

+

`0.12 × local switching activity`

The delayed update is:

`frequency_current += 0.30 × (frequency_target - frequency_current)`

The remaining frequency lag is:

`abs(frequency_target - frequency_current)`

Frequency lag contributes to:

- phase velocity;
- generated power;
- operational coherence;
- dynamic stability.

A valid reproduction must preserve the stateful delayed frequency path.

## 20. Local Thermal Field

The current generated power per cell is:

`base power`

+

`switching power`

+

`frequency-lag power`

Current relation:

`generated_power_i = 0.0018 + 0.052 × switch_activity_i + 0.018 × frequency_lag_i`

Current thermal dissipation relation:

`thermal_dissipation_i = (previous_heat_i - ambient_heat) / thermal_time_constant`

Current thermal diffusion relation uses:

- the hierarchical thermal matrix;
- temperature differences between cells;
- thermal diffusion gain.

The next local heat state is bounded below by ambient heat.

Current default ambient heat:

`0.05`

Current default thermal time constant:

`14.0`

Current default thermal diffusion gain:

`0.035`

## 21. Thermal Overload

Current local thermal overload is:

`max(0, local_heat - thermal_soft_limit)`

Current default thermal soft limit:

`0.22`

The overload field affects:

- local thermal coupling degradation;
- local gamma drift;
- nonlinear coherence compression.

The thermal field is therefore coupled back into the resonant phase computation.

## 22. Thermal Coupling Degradation

Current local thermal node factor:

`exp(-0.5 × thermal_coupling_gain × overload)`

Current thermal coupling gain:

`2.50`

The dense pair interaction uses:

`thermal_node_factor_i × thermal_node_factor_j`

The hierarchical path preserves the same local thermal weighting structure.

A valid reproduction must preserve the feedback chain:

`local thermal overload`

↓

`thermal node factor`

↓

`effective coupling`

↓

`phase evolution`

↓

`coherence`

↓

`stability`

## 23. Local Gamma Drift

The current gamma-noise target field is refreshed every:

`8 ticks`

Current target range:

`[-1.0, 1.0]`

The correlated gamma-noise state approaches its target through:

`gamma_noise_state += 0.15 × (gamma_noise_target - gamma_noise_state)`

The effective local gamma is:

`gamma_nominal + 0.08 × thermal_overload × gamma_noise_state`

The local gamma drift is:

`gamma_effective - gamma_nominal`

The resulting local gamma enters the Kuramoto-Sakaguchi phase interaction.

A valid reproduction must preserve:

- deterministic target generation;
- update cadence;
- correlated state evolution;
- thermal coupling;
- effective local phase lag.

## 24. Nonlinear Coherence Compression

The current processor applies nonlinear compression to raw phase coherence.

Thermal overload mean:

`mean(local thermal overload)`

Margin pressure:

`max(0, stability_soft_margin - previous_C_minus_P)`

Current stability soft margin:

`0.25`

Current compression relation:

`coherence_compression = exp(-(3.0 × thermal_overload_mean² + 1.5 × margin_pressure²))`

Effective coherence:

`effective_coherence = raw_phase_coherence × coherence_compression`

This nonlinear relation is part of the M15-qualified v1.7.0 executable semantic reference.

The reproduction uses the current effective-coherence relation exactly: raw phase coherence multiplied by coherence compression.

## 25. Dynamic Stability

The current processor tracks:

`C(t)`

`P(t)`

`C(t) - P(t)`

Current operational coherence:

`C = 0.82`

+

`0.34 × effective_coherence`

+

`0.16 × cluster_coherence_mean`

+

`0.08 × neutral_fraction`

-

`0.10 × mean_frequency_lag`

Current destabilizing load:

`P = heat + switch_load`

Current stability margin:

`C_minus_P = C - P`

Required default validation condition:

`C_minus_P_min > 0.0`

A reproduction must preserve the relationship between:

- phase coherence;
- multiscale coherence;
- neutral-state fraction;
- frequency lag;
- heat;
- switching load.

## 26. Phase-Derived Ternary Target

Current target mapping:

`sin(phase) > 0.33 → 1`

`sin(phase) < -0.33 → -1`

`otherwise → 0`

This mapping connects:

`resonant phase field`

to:

`balanced ternary target domain`

The derived target remains subject to:

- transition-fraction limits;
- distributed commit;
- pending routes;
- active neutral routing.

The target enters distributed commit and route processing under transition-capacity and active-neutral execution rules.

## 27. Balanced Ternary State Domain

The state and retained-result domain is:

`{-1, 0, 1}`

Valid states:

`-1`

`0`

`1`

Active neutral state:

`0`

Required marker:

`balanced_ternary_state_domain = True`

Reserved-state requirement:

`reserved_state_events = 0`

## 28. Mandatory Active-Neutral Routing

Opposite-polarity execution follows mandatory active-neutral routes.

Validated routing relation:

`-1 → 0 → 1`

`1 → 0 → -1`

Current execution rule:

`tick N: active polarity → 0`

↓

`pending neutral route retained`

↓

`tick N+1 or later: 0 → target polarity`

Required invariant:

`actual_direct_events = 0`

The transition history must preserve the route.

Route evidence includes transition history and route counters together with the final state vector.

## 29. Pending Neutral Routes

Pending neutral routes preserve:

- cell index;
- target polarity;
- earliest ready tick.

A route is applied when all of the following conditions hold:

- its ready tick has been reached;
- transition capacity remains;
- the current state is neutral.

Current required conditions include:

`actual_direct_events = 0`

`queue_overflow_events = 0`

Changes affecting pending routes require exact trace validation.

## 30. Distributed Commit

Current default transition fraction:

`0.25`

Maximum state changes per tick:

`max(1, round(cells × transition_fraction))`

Default:

`16 cells × 0.25 → 4 request lanes`

Current required default boundary:

`switch_load_peak <= 0.25`

Distributed commit is part of the connection between:

`phase-derived target`

and:

`retained ternary state`

## 31. M15 Structured Semantic Reproduction

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-a.json

Expected schema:

`frp.structured_output.v1.7.0`

Expected version:

`1.7.0`

Expected milestone:

`M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

Required default summary values:

| Field | Required value |
|---|---|
| `cells` | `16` |
| `hierarchy_depth` | `4` |
| `request_lanes` | `4` |
| `ticks_recorded` | `64` |
| `scheduler` | `7/1` |
| `scheduler_counts.balance` | `56` |
| `scheduler_counts.commit` | `8` |
| `scheduler_counts_valid` | `True` |
| `balanced_ternary_state_domain` | `True` |
| `reserved_state_events` | `0` |
| `actual_direct_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |

Additional required conditions:

`switch_load_peak <= 0.25`

`C_minus_P_min > 0.0`

## 32. Independent Structured Repeat

Generate the first output:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-a.json

Generate an independent second output:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-b.json

Compare:

    cmp demo-a.json demo-b.json

Required result:

`byte-identical`

The two runs must use:

- the same source revision;
- the same Python environment;
- the same dependency versions;
- the same configuration;
- the same seed.

## 33. Full Trace Reproduction

Run:

    python frp_prototype_v1_7_0.py --mode demo --output json --include-trace > demo-full-trace.json

The full output adds:

- `trace`;
- `cell_trace`;
- `route_events`.

Default expected sizes:

`trace = 64 processor-tick rows`

`cell_trace = 1024 cell-tick rows`

The full trace exposes:

- scheduler state;
- ternary cell state;
- phase state;
- frequency target;
- current frequency;
- frequency lag;
- switching load;
- generated power;
- thermal dissipation;
- thermal diffusion;
- local heat;
- thermal overload;
- effective gamma;
- gamma drift;
- thermal coupling factors;
- coupling field;
- raw phase coherence;
- coherence compression;
- effective coherence;
- multiscale coherence;
- C(t);
- P(t);
- C(t) - P(t);
- direct-event counters;
- neutral-route counters;
- pending-route count.

## 34. Digest Reproduction

Standard structured execution omits the `--include-trace` flag and preserves:

- preload digest;
- trace digest;
- cell-trace digest.

Use digest execution for:

- compact deterministic identity;
- routine CI validation;
- reproducibility comparisons.

Use full trace output for:

- phase-dynamics inspection;
- route inspection;
- cell-level analysis;
- correlation work.

## 35. Standard Self-Test

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

## 36. Complete Scheduler Self-Test Matrix

Default profile:

    python frp_prototype_v1_7_0.py --mode self-test --output json

Free scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

7/1 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

1/7 scheduler:

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Every output must report:

`status = PASS`

`check_count = 41`

All checks must be:

`True`

## 37. Scheduler Reproduction

Current scheduler modes:

- `free`;
- `7/1`;
- `1/7`.

Validated 16-tick profiles:

| Scheduler | Required counts |
|---|---|
| `free` | `free = 16` |
| `7/1` | `balance = 14`, `commit = 2` |
| `1/7` | `excite = 2`, `neutralize = 14` |

Validated default 64-tick profile:

`balance = 56`

`commit = 8`

Required relation:

`sum(scheduler_counts) = ticks_recorded`

Required marker:

`scheduler_counts_valid = True`

## 38. Inherited M15 Artifact Layers

FRP v1.7.0 defines ten M15 artifact layers:

1. `fixed_point_interface_profile`;
2. `balanced_ternary_hardware_encoding_map`;
3. `quantized_reference_shadow_model`;
4. `cycle_exact_reference_trace`;
5. `rtl_comparison_vector_package`;
6. `systemverilog_testbench_interface_map`;
7. `synthesizable_rtl_reference_core`;
8. `rtl_assertion_correlation_harness`;
9. `reference_rtl_equivalence_report`;
10. `qualification_closure_manifest`.

The inherited M15 chain maps the complete processor behavior into deterministic hardware-facing representation.

The resonant phase-coherence computational core remains the source computational mechanism for the M15 mapping chain.

## 39. Generate the M15 Qualification Directory

Create:

    mkdir -p artifacts/m15/vectors_a
    mkdir -p artifacts/m15/vectors_b

Generate the standard structured output:

    python frp_prototype_v1_7_0.py --mode demo --output json > artifacts/m15/structured-output.json

Generate the self-test matrix:

    python frp_prototype_v1_7_0.py --mode self-test --output json > artifacts/m15/self-test.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json > artifacts/m15/self-test-free.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json > artifacts/m15/self-test-7-1.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json > artifacts/m15/self-test-1-7.json

## 40. Generate the Ten M15 Artifact Layers

Fixed-point interface profile:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile > artifacts/m15/fixed-point-interface-profile.json

Balanced ternary hardware encoding map:

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map > artifacts/m15/balanced-ternary-hardware-encoding-map.json

Quantized reference shadow model:

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model > artifacts/m15/quantized-reference-shadow-model.json

Cycle-exact reference trace:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace > artifacts/m15/cycle-exact-reference-trace.json

RTL comparison vector package:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package > artifacts/m15/rtl-comparison-vector-package.json

SystemVerilog testbench interface map:

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map > artifacts/m15/systemverilog-testbench-interface-map.json

Synthesizable RTL reference core:

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core > artifacts/m15/synthesizable-rtl-reference-core.json

RTL assertion correlation harness:

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness > artifacts/m15/rtl-assertion-correlation-harness.json

Reference RTL equivalence report:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report > artifacts/m15/reference-rtl-equivalence-report.json

Qualification closure manifest:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest > artifacts/m15/qualification-closure-manifest.json

## 41. Expected M15 Schemas

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

Every artifact must report:

`version = 1.7.0`

and:

`milestone = M15 — Implementation Mapping, Domain Interface, and Qualification Closure Package`

## 42. Fixed-Point Interface Reproduction

Current hardware-facing numeric representations:

| Domain | Representation |
|---|---|
| general dynamic scalar | `S32Q16` |
| normalized coefficient | `S32Q30` |
| phase | `PHASE_U32` |
| Sakaguchi gamma offset | `GAMMA_S32` |

Current trigonometric profile:

`4096-entry full-cycle lookup table`

Required exactness markers:

`fixed_point_topology_sum_exact = True`

`fixed_point_thermal_sum_exact = True`

The fixed-point mapping covers the resonant phase domain together with the balanced ternary state domain.

## 43. Balanced Ternary Hardware Encoding

Current two-bit encoding:

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

Required interface values:

`request_lanes = 4`

`cell_id_width = 4`

Required invariant:

`reserved_state_events = 0`

The encoding represents the balanced ternary state domain inside the complete resonant processor computation.

## 44. Quantized Hardware Shadow Reproduction

Generate:

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model > quantized-reference-shadow-model.json

The stateful quantized shadow preserves processor domains including:

- ternary state;
- scheduler state;
- pending neutral routes;
- phase;
- frequency;
- gamma;
- thermal state;
- coherence;
- stability;
- event counters.

Required summary conditions:

- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- balanced ternary state-domain validity;
- valid scheduler counts;
- `ticks_recorded = 64`;
- `switch_load_peak <= 0.25`;
- `C_minus_P_min > 0.0`;
- exact fixed-point topology sum;
- exact fixed-point thermal sum.

## 45. Cycle-Exact Reference Trace

Generate:

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace > cycle-exact-reference-trace.json

Current default trace length:

`64`

Required trace conditions:

- every row has zero actual direct events;
- every row has zero reserved-state events;
- each row contains gamma-noise target data for all 16 cells.

The cycle-exact trace is the integer reference path between:

`stateful quantized processor execution`

and:

`deterministic RTL comparison`

## 46. Deterministic RTL Vector Package

Generate package A:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir artifacts/m15/vectors_a > artifacts/m15/vector-package-a.json

Generate package B independently:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir artifacts/m15/vectors_b > artifacts/m15/vector-package-b.json

Expected files in each vector directory:

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

Expected file count:

`10`

## 47. Deterministic Vector Repeat

Compare:

    diff -qr artifacts/m15/vectors_a artifacts/m15/vectors_b

Required result:

`byte-identical equality`

Every corresponding generated file must be byte-identical.

Acceptance requires byte-identical equality.

## 48. Vector SHA-256 Integrity

Each generated vector directory contains:

`frp_m15_sha256_manifest.json`

The manifest contains SHA-256 digests for the nine non-manifest vector files.

A complete integrity check must:

1. load the manifest;
2. locate every named vector file;
3. calculate its SHA-256 digest;
4. compare it with the recorded digest;
5. require exact equality.

The two independently generated vector directories must also be byte-identical.

## 49. SystemVerilog Interface Mapping

Generate:

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map > systemverilog-testbench-interface-map.json

Current default interface parameters:

| Parameter | Value |
|---|---:|
| `NUM_CELLS` | `16` |
| `HIERARCHY_DEPTH` | `4` |
| `REQUEST_LANES` | `4` |
| `CELL_ID_WIDTH` | `4` |
| `STATE_VECTOR_WIDTH` | `32` |
| `SCALAR_WIDTH` | `32` |
| `PHASE_WIDTH` | `32` |

The verification stimulus interface includes:

`gamma_noise_target_q`

This preserves deterministic externalization of gamma-noise targets.

## 50. Synthesizable RTL Reference-Core Contract

Generate:

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core > synthesizable-rtl-reference-core.json

The current export defines:

`26`

exact tick-execution stages.

Required kernel conditions include:

`actual_direct_events = 0`

`tick_separated_neutral_routing = True`

Supported scheduler modes:

- `free`;
- `7/1`;
- `1/7`.

The RTL mapping remains a representation of the full processor execution semantics.

## 51. RTL Assertion Correlation

Generate:

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness > rtl-assertion-correlation-harness.json

Current assertion count:

`13`

Current exact comparison rule:

`actual integer field == expected integer field`

The assertion layer connects RTL-facing execution to deterministic reference vectors.

## 52. Floating Reference to Quantized Shadow Equivalence

Generate:

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report > reference-rtl-equivalence-report.json

Required exact sequence matches:

- state sequence match `1.0`;
- scheduler sequence match `1.0`;
- neutral-route sequence match `1.0`;
- `C_minus_P` sign match `1.0`;
- boundary-order match `1.0`.

Required maximum error bounds:

| Field | Maximum error |
|---|---:|
| phase | `0.02` |
| frequency | `0.0001` |
| heat | `0.001` |
| gamma | `0.000001` |
| coherence | `0.01` |
| `C` | `0.01` |
| `P` | `0.001` |
| `C_minus_P` | `0.01` |

These thresholds correlate the floating semantic reference with the quantized hardware shadow.

## 53. Exact Quantized Shadow Replay

The same equivalence report validates exact deterministic replay.

Required exact values:

- state match `1.0`;
- scheduler match `1.0`;
- pending-route match `1.0`;
- counter match `1.0`;
- trace match `1.0`;
- cell-trace match `1.0`.

This is a stricter boundary than floating-to-quantized numeric correlation.

## 54. Qualification Closure

Generate:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest > qualification-closure-manifest.json

Required result:

`status = PASS`

All closure checks must be:

`True`

Current artifact-layer count:

`10`

The qualification closure manifest is the inherited M15 qualification endpoint.

## 55. M15 Benchmark Matrix

Generate:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix > artifacts/m15/benchmark-matrix.json

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

This matrix represents the M15 implementation-mapping chain.

The Comparative Architecture Benchmark Suite provides its own supporting comparison contour.

## 56. Scaling Reproduction

Generate 8-cell execution:

    python frp_prototype_v1_7_0.py --cells 8 --steps 16 --mode demo --output json > artifacts/m15/scaling-8.json

Generate 16-cell execution:

    python frp_prototype_v1_7_0.py --cells 16 --steps 16 --mode demo --output json > artifacts/m15/scaling-16.json

Generate 32-cell execution:

    python frp_prototype_v1_7_0.py --cells 32 --steps 16 --mode demo --output json > artifacts/m15/scaling-32.json

Expected structure:

| Cells | Hierarchy depth | Request lanes | Packed state width |
|---|---:|---:|---:|
| `8` | `3` | `2` | `16 bits` |
| `16` | `4` | `4` | `32 bits` |
| `32` | `5` | `8` | `64 bits` |

## 57. Scaling Invariants

Every scaling output must preserve:

- balanced ternary state-domain validity;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- valid scheduler counts;
- exact fixed-point topology sum;
- exact fixed-point thermal sum.

Scaling also changes:

- hierarchy depth;
- shell structure;
- phase-coupling topology;
- thermal topology;
- multiscale coherence domains;
- request-lane count;
- packed ternary state width.

A complete scaling analysis should inspect these coupled changes.

## 58. Reproducibility Acceptance Criteria

### 58.1 Inherited M15 foundation

The FRP v1.7.0 M15 foundation is reproducible when:

- the source revision is recorded;
- the working-tree state is recorded;
- the Python version is recorded;
- dependency versions are recorded;
- the executable compiles;
- deterministic initialization is preserved;
- the default structured run completes;
- an independent structured repeat is byte-identical;
- the Kuramoto-Sakaguchi phase path executes;
- phase evolution remains deterministic;
- global phase order remains available;
- multiscale coherence remains available;
- delay dynamics remain stateful;
- local thermal behavior remains coupled;
- local gamma drift remains deterministic;
- nonlinear coherence compression remains active;
- dynamic stability remains positive in the validated default profile;
- phase-derived ternary targets remain connected to the evolving phase field;
- balanced ternary state-domain validity remains true;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- all four self-test profiles report `41/41 PASS`;
- all ten M15 artifact layers are generated;
- every M15 artifact reports the expected schema;
- the quantized hardware shadow preserves the kernel invariants;
- the cycle-exact trace contains 64 rows;
- independently generated vector directories are byte-identical;
- SHA-256 vector integrity passes;
- floating-to-quantized correlation stays within contract;
- exact quantized replay reports full equality;
- the qualification closure manifest reports `PASS`.

### 58.2 Current M16 RTL execution layer

The current M16 RTL execution layer is reproducible when:

- the source revision is recorded;
- the working-tree state is recorded;
- the Verilator version is recorded;
- the g++ version is recorded;
- the ten required SystemVerilog artifacts are present;
- the five required RTL documentation artifacts are present;
- the integrated testbench builds with SystemVerilog timing and assertions enabled;
- the generated executable exists;
- the executable architectural testbench completes;
- scheduler modes `free`, `7/1`, and `1/7` execute;
- request-lane arbitration remains deterministic;
- active-neutral first-leg execution remains valid;
- retained pending-route completion remains valid;
- transition-capacity enforcement remains valid;
- retained-state writeback remains valid;
- counter clearing preserves retained state;
- SystemVerilog assertions pass;
- all ten integrated invariant flags remain asserted;
- `ticks_recorded = 16`;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`.

### 58.3 Current M16 FPGA preparation layer

The current M16 FPGA preparation layer is reproducible when:

- the source revision is recorded;
- the working-tree state is recorded;
- the Verilator version is recorded;
- the g++ version is recorded;
- the two required FPGA SystemVerilog artifacts are present;
- the nine required M16 RTL dependencies are present;
- FPGA integration-top elaboration passes;
- the executable FPGA integration testbench builds;
- the generated executable exists;
- inferred latch diagnostics remain absent;
- multidriven diagnostics remain absent;
- asynchronous external reset assertion executes;
- two-stage synchronous reset release executes;
- `core_ready = 1` after reset release;
- tick, counter-clear, and request-valid inputs remain gated before readiness;
- scheduler propagation remains valid;
- request-interface propagation remains valid;
- active-neutral first-leg execution remains valid;
- retained pending-route completion remains valid;
- transition-capacity enforcement remains valid;
- retained-state writeback remains valid;
- all ten integrated invariant flags remain asserted;
- `ticks_recorded = 1`;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`;
- `invariant_flags = 1111111111`.

## 59. Minimal Current M15 and M16 Reproduction Sequence

Record source state:

    git rev-parse HEAD
    git status --short
    python --version
    python -m pip freeze
    verilator --version
    g++ --version

Compile the M15-qualified executable semantic reference:

    python -m py_compile frp_prototype_v1_7_0.py

Run the M15-qualified processor semantic reference:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-a.json

Repeat independently:

    python frp_prototype_v1_7_0.py --mode demo --output json > demo-b.json

Compare:

    cmp demo-a.json demo-b.json

Run the full scheduler self-test matrix:

    python frp_prototype_v1_7_0.py --mode self-test --output json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json

Generate qualification closure:

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest

Required results:

`Python compilation PASS`

`structured repeat byte-identical`

`all self-tests 41/41 PASS`

`qualification closure PASS`

Prepare the M16 RTL build paths:

    rm -rf /tmp/frp_m16_obj
    rm -f /tmp/frp_m16_build.log
    rm -f /tmp/frp_m16_execution.log
    rm -f /tmp/frp_m16_sources.sha256
    mkdir -p /tmp/frp_m16_obj

Record M16 RTL source hashes:

    sha256sum rtl/m16/*.sv | sort > /tmp/frp_m16_sources.sha256

Build the integrated M16 RTL testbench:

    verilator --sv --timing --assert --binary \
      --top-module frp_m16_tb \
      -Irtl/m16 \
      --Mdir /tmp/frp_m16_obj \
      rtl/m16/frp_m16_tb.sv \
      2>&1 | tee /tmp/frp_m16_build.log

Check the generated RTL executable:

    test -x /tmp/frp_m16_obj/Vfrp_m16_tb

Run the M16 RTL architectural testbench:

    /tmp/frp_m16_obj/Vfrp_m16_tb \
      2>&1 | tee /tmp/frp_m16_execution.log

Validate the M16 RTL terminal markers:

    grep -Fqx "FRP M16 deterministic RTL testbench completed." /tmp/frp_m16_execution.log
    grep -Fqx "CELLS=8 REQUEST_LANES=2" /tmp/frp_m16_execution.log
    grep -Fqx "ticks_recorded=16" /tmp/frp_m16_execution.log
    grep -Fqx "actual_direct_events=0" /tmp/frp_m16_execution.log
    grep -Fqx "reserved_state_events=0" /tmp/frp_m16_execution.log
    grep -Fqx "queue_overflow_events=0" /tmp/frp_m16_execution.log

Prepare the M16 FPGA preparation build paths:

    rm -rf /tmp/frp_m16_fpga_obj
    rm -f /tmp/frp_m16_fpga_top_lint.log
    rm -f /tmp/frp_m16_fpga_build.log
    rm -f /tmp/frp_m16_fpga_execution.log
    rm -f /tmp/frp_m16_fpga_sources.sha256
    mkdir -p /tmp/frp_m16_fpga_obj

Record M16 FPGA and RTL source hashes:

    sha256sum rtl/m16/*.sv fpga/m16/*.sv \
      | sort \
      > /tmp/frp_m16_fpga_sources.sha256

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

Check the generated FPGA integration executable:

    test -x /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb

Reject latch and multidriven diagnostics:

    ! grep -E '%Warning-(LATCH|MULTIDRIVEN)' \
      /tmp/frp_m16_fpga_top_lint.log \
      /tmp/frp_m16_fpga_build.log

Run the M16 FPGA integration testbench:

    /tmp/frp_m16_fpga_obj/Vfrp_m16_fpga_tb \
      2>&1 | tee /tmp/frp_m16_fpga_execution.log

Validate the M16 FPGA preparation terminal markers:

    grep -Fqx "FRP M16 FPGA integration testbench completed." /tmp/frp_m16_fpga_execution.log
    grep -Fqx "CELLS=8 REQUEST_LANES=2" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "core_ready=1" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "ticks_recorded=1" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "actual_direct_events=0" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "reserved_state_events=0" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "queue_overflow_events=0" /tmp/frp_m16_fpga_execution.log
    grep -Fqx "invariant_flags=1111111111" /tmp/frp_m16_fpga_execution.log

Required M16 results:

`M16 RTL build and execution PASS`

`M16 SystemVerilog assertions PASS`

`M16 RTL zero-event counters PASS`

`M16 FPGA integration-top elaboration PASS`

`M16 FPGA testbench build and execution PASS`

`M16 FPGA reset, readiness, and execution-input gating PASS`

`M16 FPGA zero-event counters and invariant flags PASS`

## 60. Complete M15 Reproduction Sequence

Create the artifact directories:

    mkdir -p artifacts/m15/vectors_a
    mkdir -p artifacts/m15/vectors_b

Generate structured output and self-tests:

    python frp_prototype_v1_7_0.py --mode demo --output json > artifacts/m15/structured-output.json

    python frp_prototype_v1_7_0.py --mode self-test --output json > artifacts/m15/self-test.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler free --output json > artifacts/m15/self-test-free.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 7/1 --output json > artifacts/m15/self-test-7-1.json

    python frp_prototype_v1_7_0.py --mode self-test --scheduler 1/7 --output json > artifacts/m15/self-test-1-7.json

Generate all ten M15 exports:

    python frp_prototype_v1_7_0.py --export-fixed-point-interface-profile > artifacts/m15/fixed-point-interface-profile.json

    python frp_prototype_v1_7_0.py --export-balanced-ternary-hardware-encoding-map > artifacts/m15/balanced-ternary-hardware-encoding-map.json

    python frp_prototype_v1_7_0.py --export-quantized-reference-shadow-model > artifacts/m15/quantized-reference-shadow-model.json

    python frp_prototype_v1_7_0.py --export-cycle-exact-reference-trace > artifacts/m15/cycle-exact-reference-trace.json

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package > artifacts/m15/rtl-comparison-vector-package.json

    python frp_prototype_v1_7_0.py --export-systemverilog-testbench-interface-map > artifacts/m15/systemverilog-testbench-interface-map.json

    python frp_prototype_v1_7_0.py --export-synthesizable-rtl-reference-core > artifacts/m15/synthesizable-rtl-reference-core.json

    python frp_prototype_v1_7_0.py --export-rtl-assertion-correlation-harness > artifacts/m15/rtl-assertion-correlation-harness.json

    python frp_prototype_v1_7_0.py --export-reference-rtl-equivalence-report > artifacts/m15/reference-rtl-equivalence-report.json

    python frp_prototype_v1_7_0.py --export-qualification-closure-manifest > artifacts/m15/qualification-closure-manifest.json

Generate benchmark matrix:

    python frp_prototype_v1_7_0.py --export-benchmark-matrix > artifacts/m15/benchmark-matrix.json

Generate scaling outputs:

    python frp_prototype_v1_7_0.py --cells 8 --steps 16 --mode demo --output json > artifacts/m15/scaling-8.json

    python frp_prototype_v1_7_0.py --cells 16 --steps 16 --mode demo --output json > artifacts/m15/scaling-16.json

    python frp_prototype_v1_7_0.py --cells 32 --steps 16 --mode demo --output json > artifacts/m15/scaling-32.json

Generate independent vector packages:

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir artifacts/m15/vectors_a > artifacts/m15/vector-package-a.json

    python frp_prototype_v1_7_0.py --export-rtl-comparison-vector-package --vector-output-dir artifacts/m15/vectors_b > artifacts/m15/vector-package-b.json

Compare:

    diff -qr artifacts/m15/vectors_a artifacts/m15/vectors_b

Required result:

`byte-identical equality`

## 61. Published M15 Foundation and Current M16 Qualification Evidence

### 61.1 Inherited FRP v1.7.0 M15 evidence

Inherited release layer:

`FRP v1.7.0 — M15 Implementation Mapping, Domain Interface, and Qualification Closure Package`

Validation environment:

`GitHub Actions`

Workflow runner:

`ubuntu-latest`

Validated release commit:

`5fd9a4f`

Validated workflow runs recorded in `TEST_REPORT_v1_7_0.md`:

- `FRP Structured Output #113`;
- `FRP M15 Implementation Mapping and Qualification Closure #1`;
- `FRP Self Test #154`;
- `FRP Benchmark Smoke Test #152`.

Published result:

`PASS`

Published M15 self-test result:

`41/41 PASS`

Published M15 qualification results:

| Qualification record | Result |
|---|---:|
| M15 self-test suite | `41 / 41 PASS` |
| deterministic vector files | `10 / 10 byte-identical` |
| required semantic correlation matches | `5 / 5 = 1.0` |
| deterministic replay matches | `6 / 6 = 1.0` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `fixed_point_topology_sum_exact` | `True` |
| `fixed_point_thermal_sum_exact` | `True` |

These values are release-specific validation evidence.

The validated release commit remains recorded exactly as `5fd9a4f`, while later documentation and maintenance commits retain their own commit identities.

### 61.2 Current FRP v1.8.0 M16 evidence

Current release layer:

`FRP v1.8.0 — M16 RTL Core Realization and Execution Semantics Package`

Current qualification records:

| Layer | Workflow run | Qualified commit | Branch | Result | Artifact count | Closure status |
|---|---:|---|---|---|---:|---|
| M16 RTL initial closure | `#82` | `a68a2af` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| M16 RTL qualification rerun | `#84` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 RTL EXECUTION LAYER CLOSED` |
| M16 FPGA preparation initial closure | `#1` | `326b69e` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |
| M16 FPGA preparation qualification rerun | `#2` | `ede53cf` | `main` | `SUCCESS` | `1` | `M16 FPGA PREPARATION LAYER CLOSED` |

Current M16 RTL terminal record:

| Field | Recorded value |
|---|---:|
| `CELLS` | `8` |
| `REQUEST_LANES` | `2` |
| `ticks_recorded` | `16` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |

Current M16 FPGA preparation terminal record:

| Field | Recorded value |
|---|---:|
| `CELLS` | `8` |
| `REQUEST_LANES` | `2` |
| `core_ready` | `1` |
| `ticks_recorded` | `1` |
| `actual_direct_events` | `0` |
| `reserved_state_events` | `0` |
| `queue_overflow_events` | `0` |
| `invariant_flags` | `1111111111` |

Current M16 published result:

`PASS`

## 62. Historical Release Preservation

Historical executable references remain bound to their own release layers.

Examples:

- `frp_prototype_v0_9_3_mobile.py`;
- `frp_prototype_v0_9_4.py`;
- `frp_prototype_v0_9_5.py`;
- `frp_prototype_v0_9_6.py`;
- `frp_prototype_v0_9_7.py`;
- `frp_prototype_v0_9_8.py`;
- `frp_prototype_v0_9_9.py`;
- `frp_prototype_v1_0_0.py`;
- `frp_prototype_v1_1_0.py`;
- `frp_prototype_v1_2_0.py`;
- `frp_prototype_v1_3_0.py`;
- `frp_prototype_v1_4_0.py`;
- `frp_prototype_v1_5_0.py`;
- `frp_prototype_v1_6_0.py`;
- `frp_prototype_v1_7_0.py`.

Historical workflows retain their release-specific executable bindings.

Historical schemas retain their release-specific schema identities.

Historical test reports remain release-specific records.

## 63. Supporting Comparative Architecture Reproduction

The Comparative Architecture Benchmark Suite adds a supporting validation contour.

Directory:

`benchmarks/architecture_comparison/`

Compared architecture references:

1. `binary_synchronous_reference`;
2. `binary_clock_gated_reference`;
3. `direct_ternary_reference`;
4. `frp_v1_7_0_quantized_shadow`.

The FRP reference remains a resonant phase-coherence architecture with balanced ternary state retention.

## 64. Comparative Architecture Self-Test

Enter:

    cd benchmarks/architecture_comparison

Run:

    python run_architecture_comparison.py --self-test --output text

The comparison suite runs alongside the inherited M15 qualification path and current M16 execution qualification paths as a supporting validation contour.

## 65. Canonical Comparative Architecture Run

From:

`benchmarks/architecture_comparison/`

run:

    python run_architecture_comparison.py --workload-profile profiles/workload_profile_v1.json --cost-profile profiles/normalized_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler "7/1" --write results/reference_comparison_seed_76.json --output text

Generate an independent repeat:

    mkdir -p .qualification

    python run_architecture_comparison.py --workload-profile profiles/workload_profile_v1.json --cost-profile profiles/normalized_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler "7/1" --write .qualification/reference_comparison_seed_76_repeat.json --output text

Compare:

    cmp results/reference_comparison_seed_76.json .qualification/reference_comparison_seed_76_repeat.json

Required result:

`byte-identical`

## 66. Comparative Qualification Policy

Current qualification policy:

`integrity_only_no_winner_assertions`

Required winner assertions:

`[]`

The comparison result remains machine-readable data.

Reproducibility verifies deterministic comparison integrity under the recorded qualification policy.

## 67. Supporting Hardware-Sensitivity Reproduction

From:

`benchmarks/architecture_comparison/`

validate the profile:

    python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --output text

Run the profile validator self-test:

    python validate_hardware_sensitivity_profile.py --profile profiles/hardware_sensitivity_cost_profile_v1.json --self-test --output text

Run the hardware-sensitivity comparison self-test:

    python run_hardware_sensitivity_comparison.py --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json --self-test --output json

Generate the canonical sensitivity result:

    python run_hardware_sensitivity_comparison.py --workload-profile profiles/workload_profile_v1.json --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler "7/1" --write results/reference_comparison_seed_76_hardware_sensitivity_v1.json --output text

Generate an independent repeat:

    python run_hardware_sensitivity_comparison.py --workload-profile profiles/workload_profile_v1.json --hardware-sensitivity-profile profiles/hardware_sensitivity_cost_profile_v1.json --thermal-profile profiles/thermal_proxy_profile_v1.json --frp-scheduler "7/1" --write .qualification/reference_comparison_seed_76_hardware_sensitivity_v1_repeat.json --output text

Compare:

    cmp results/reference_comparison_seed_76_hardware_sensitivity_v1.json .qualification/reference_comparison_seed_76_hardware_sensitivity_v1_repeat.json

Required result:

`byte-identical`

## 68. Failure Diagnosis

When a reproduction fails, first record:

    git rev-parse HEAD
    git status --short
    python --version
    python -m pip freeze
    verilator --version
    g++ --version

Then identify which boundary failed.

### Compile failure

Check:

- Python version;
- source integrity;
- incomplete file replacement;
- merge markers.

### Structured-output mismatch

Check:

- seed;
- scheduler;
- cell count;
- steps;
- command-line parameters;
- source revision.

### Phase or coherence mismatch

Check:

- gamma;
- fractal alpha;
- nominal coupling;
- delay alpha;
- scheduler state;
- thermal parameters;
- update order.

### Ternary-state mismatch

Check:

- phase-derived target mapping;
- transition fraction;
- pending neutral routes;
- scheduler behavior;
- active neutral routing.

### M15 quantized mismatch

Check:

- fixed-point formats;
- rounding behavior;
- phase wrapping;
- trigonometric lookup;
- quantized hierarchy weights;
- gamma stimulus.

### Vector mismatch

Check:

- source revision;
- output directory contents;
- deterministic seed;
- generator changes;
- manifest digests.

### M16 RTL build or execution mismatch

Check:

- Verilator version;
- g++ version;
- `rtl/m16/*.sv` source hashes;
- `rtl/m16` include path;
- top module `frp_m16_tb`;
- build log;
- generated executable path;
- SystemVerilog assertion results;
- scheduler mode and scheduler-state sequence;
- request-lane ordering;
- active-neutral route sequence;
- retained pending-route sequence;
- transition-capacity telemetry;
- retained-state writeback;
- terminal zero-event counters.

### M16 FPGA preparation mismatch

Check:

- Verilator version;
- g++ version;
- `rtl/m16/*.sv` and `fpga/m16/*.sv` source hashes;
- required RTL dependency inventory;
- FPGA top elaboration log;
- FPGA testbench build log;
- latch and multidriven diagnostics;
- top module `frp_m16_fpga_top`;
- testbench module `frp_m16_fpga_tb`;
- asynchronous reset assertion;
- two-stage synchronous reset release;
- `core_ready` generation;
- execution-input gating before readiness;
- scheduler and request-interface propagation;
- active-neutral and pending-route execution;
- terminal zero-event counters;
- integrated invariant flags.

Preserve the recorded thresholds during regression diagnosis.

## 69. Reproducibility Record Template

A reproducibility record should preserve:

### Source

`commit:`

`working tree:`

### Environment

`operating system:`

`Python version:`

`dependency versions:`

`Verilator version:`

`g++ version:`

### Processor configuration

`cells:`

`steps:`

`seed:`

`scheduler:`

`transition fraction:`

`gamma:`

`fractal alpha:`

`thermal beta:`

`ambient heat:`

`thermal time constant:`

`thermal limits:`

`nominal coupling:`

`delay alpha:`

`thermal diffusion gain:`

### Commands

`exact commands executed:`

### Dynamic result

`structured-output schema:`

`trace digest:`

`cell-trace digest:`

`actual_direct_events:`

`C_minus_P_min:`

`phase-coherence markers:`

### Self-test result

`status:`

`check count:`

### M15 result

`artifact schemas:`

`vector repeat:`

`equivalence result:`

`qualification closure:`

### M16 RTL result

`RTL source hashes:`

`build result:`

`execution result:`

`SystemVerilog assertion result:`

`scheduler profiles:`

`ticks_recorded:`

`actual_direct_events:`

`reserved_state_events:`

`queue_overflow_events:`

`integrated invariant flags:`

### M16 FPGA preparation result

`FPGA and RTL source hashes:`

`integration-top elaboration result:`

`testbench build result:`

`testbench execution result:`

`latch diagnostics:`

`multidriven diagnostics:`

`core_ready:`

`ticks_recorded:`

`actual_direct_events:`

`reserved_state_events:`

`queue_overflow_events:`

`invariant_flags:`

## 70. Repository Alignment Rule

When the current architecture layer changes, review:

- `README.md`;
- `INSTALL.md`;
- `USAGE.md`;
- `REPRODUCIBILITY.md`;
- `CI.md`;
- `PROJECT_STRUCTURE.md`;
- `ROADMAP.md`;
- `MILESTONES.md`;
- `CHANGELOG.md`;
- current executable semantic reference;
- current test report;
- current validation index;
- current release notes;
- current architecture document;
- current milestone workflow;
- `docs/README.md`;
- `docs/core_principles.md`;
- `docs/resonance_computation.md`;
- `docs/mathematical_foundation.md`;
- `docs/physical_foundation.md`;
- `docs/m15_implementation_mapping_domain_interface_qualification_closure.md`;
- `docs/m16_rtl_core_realization_execution_semantics.md`;
- `rtl/m16/README.md`;
- `rtl/m16/ARTIFACTS.md`;
- `rtl/m16/SIMULATION.md`;
- `rtl/m16/SIMULATION_TRANSCRIPT.md`;
- `rtl/m16/CLOSURE.md`;
- `fpga/m16/frp_m16_fpga_top.sv`;
- `fpga/m16/frp_m16_fpga_tb.sv`;
- `fpga/m16/SIMULATION_TRANSCRIPT.md`;
- `fpga/m16/CLOSURE.md`;
- `.github/workflows/frp-m15-implementation-mapping-qualification.yml`;
- `.github/workflows/frp-m16-rtl-artifact-boundary.yml`;
- `.github/workflows/frp-m16-fpga-preparation.yml`;
- `.github/workflows/frp-m16-canonical-core-domain.yml`;
- `.github/workflows/frp-m16-reserved-cell-cleanup.yml`.

Files describing FRP computation preserve the complete computational subject where relevant:

`Kuramoto-Sakaguchi resonant phase dynamics`

↓

`phase evolution`

↓

`resonance selection`

↓

`phase coherence`

↓

`delay and thermal feedback`

↓

`nonlinear coherence compression`

↓

`dynamic stability`

↓

`phase-derived ternary target`

↓

`distributed commit`

↓

`active neutral routing`

↓

`retained ternary state`

## 71. Complete Current Technical Chain

The current reproducible technical chain is:

`balanced ternary state and retained-result domain {-1, 0, 1}`

↓

`deterministic phase and frequency initialization`

↓

`dyadic hierarchical ultrametric topology`

↓

`Kuramoto-Sakaguchi resonant phase coupling`

↓

`asymmetric local phase lag gamma`

↓

`hierarchical fractal phase interaction`

↓

`stateful delay dynamics`

↓

`distributed local thermal field`

↓

`thermal coupling degradation`

↓

`local correlated gamma drift`

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

`dynamic stability C(t) - P(t)`

↓

`phase-derived ternary target`

↓

`distributed transition limit`

↓

`mandatory active-neutral route`

↓

`retained coherent ternary state`

↓

`structured machine-readable telemetry`

↓

`independent byte-identical execution repeat`

↓

`fixed-point implementation profile`

↓

`balanced ternary hardware encoding`

↓

`stateful quantized hardware shadow`

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

`floating-to-quantized reference correlation`

↓

`exact quantized deterministic replay`

↓

`M15 qualification closure`

↓

`M16 integrated SystemVerilog scheduler, request, route, capacity, and writeback execution`

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

The resonant phase-coherence mechanism remains the computational core throughout this chain.

The balanced ternary domain remains the state and retained-result domain throughout this chain.

## 72. Current Status

Processor:

`Fractal Resonance Processor (FRP)`

Processor class:

`Ternary Resonant Coherence Processor`

Computational mechanism:

`Kuramoto-Sakaguchi resonant phase dynamics with asymmetric phase lag, hierarchical fractal coupling, phase evolution, Kuramoto order parameter R, multiscale phase coherence, stateful delay dynamics, local thermal-phase interaction, local correlated gamma drift, nonlinear coherence compression, dynamic stability evaluation, phase-derived ternary targets, distributed commit, mandatory active-neutral routing, and retained coherent ternary state`

State and retained-result domain:

`{-1, 0, 1}`

Active neutral state:

`0`

Current executable semantic reference form:

`Ternary Resonant Coherence Processor — Structured Output Prototype`

Current RTL execution form:

`Integrated SystemVerilog RTL core and executable architectural testbench`

Current FPGA preparation form:

`Target-independent FPGA integration top and executable integration testbench`

Current version:

`FRP v3.2.0`

Current milestone:

`M30 — Reproducibility, Qualification, and Archival Release Closure`

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

Current M16 RTL qualification:

| Field | Recorded value |
|---|---|
| Workflow | `FRP M16 RTL Artifact Boundary` |
| Workflow file | `.github/workflows/frp-m16-rtl-artifact-boundary.yml` |
| Workflow run | `#84` |
| Qualified source commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Status | `M16 RTL EXECUTION LAYER CLOSED` |

Current M16 FPGA preparation qualification:

| Field | Recorded value |
|---|---|
| Workflow | `FRP M16 FPGA Preparation` |
| Workflow file | `.github/workflows/frp-m16-fpga-preparation.yml` |
| Workflow run | `#2` |
| Qualified repository commit | `ede53cf` |
| Branch | `main` |
| Result | `SUCCESS` |
| Status | `M16 FPGA PREPARATION LAYER CLOSED` |

Current M16 zero-event record:

`actual_direct_events = 0`

`reserved_state_events = 0`

`queue_overflow_events = 0`

Current M16 integrated invariant record:

`invariant_flags = 1111111111`

Mathematical foundation:

`docs/mathematical_foundation.md`

Physical foundation:

`docs/physical_foundation.md`

## 73. M30 Clean-Environment Reproduction

M30 reproduction uses Python 3.12, the exact repository requirements, the
immutable M29 source commit, the captured successful M17 through M29 workflow
records, and the committed M30 producer and test source.

Primary command:

`python frp_m30_reproducibility_qualification_archival_closure.py --verify --repository-root . --source-commit ff3dd434da5dcbd9e8fa62444f658ed4c495b540`

Complete repository test command:

`python -m unittest discover -s tests -p 'test_*.py' -v`

The reproduction procedure constructs two independent M30 output trees,
requires byte identity, verifies the archival package SHA-256 digest, validates
every archive member, and validates all committed M30 JSON documents against
their declared schemas.

Canonical processor notation remains `-1/0/1`; active neutral state remains
`0`; temporal scheduler modes remain `1/7` and `7/1`; `free` remains a separate
service scheduler mode.

</details>
