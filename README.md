# Fractal Resonance Processor (FRP)

**Ternary Fractal Resonant Coherence Processor**

[![Version](https://img.shields.io/badge/version-v3.3.0-blue.svg)](#release-status)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](#quick-start)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)

[![FRP M31 Complete](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-m31-complete.yml/badge.svg)](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-m31-complete.yml)
[![FRP Self Test](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-self-test.yml/badge.svg)](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-self-test.yml)
[![FRP Benchmark Smoke Test](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-benchmark-smoke.yml/badge.svg)](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-benchmark-smoke.yml)
[![FRP Structured Output](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-structured-output.yml/badge.svg)](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/workflows/frp-structured-output.yml)

FRP is a processor architecture in which computation is organized through
relative-phase interference, resonant selection, multiscale coherence, and a
balanced ternary retained-state boundary. Classical bit addition is not the
primary computational mechanism.

The discrete processor domain is `-1/0/1`. State `0` is active: it performs
mediation, routing, retention, balancing, transition staging, and controlled
neutralization.

## Release status

| Field | Current record |
|---|---|
| Version | `FRP v3.3.0` |
| Milestone | `M31 — Phase-Interference, Active-Zero, and Thermal-Evidence Publication` |
| Qualification | `PASS` |
| Focused M31 tests | `60 / 60 PASS` |
| M31 qualification checks | `13 / 13 PASS` |
| Canonical M31 outputs | `4 / 4 exact` |
| Executable semantic reference | `frp_prototype_v1_7_0.py` |
| RTL and FPGA implementation anchor | `M16 — PASS` |
| Preserved archival baseline | `FRP v3.2.0 / M30 — PASS` |

Current release records:

- [FRP v3.3.0 validation index](FRP_VALIDATION_INDEX_v3_3_0.md)
- [FRP v3.3.0 release notes](RELEASE_NOTES_v3_3_0.md)
- [FRP v3.3.0 test report](TEST_REPORT_v3_3_0.md)

## Processor model

FRP combines two inseparable computational layers:

1. A resonant phase layer evolves local phase and frequency states through
   Kuramoto-Sakaguchi interaction, hierarchical fractal coupling, asymmetric
   phase lag, retained frequency memory, local thermal-phase interaction, and
   multiscale phase organization.
2. A balanced ternary layer registers targets, schedules requests, enforces
   active-zero routing, retains state, and exposes deterministic execution
   evidence.

The execution chain is:

`phase dynamics → relative-phase organization → ternary target → scheduler → request handling → active-zero routing → retained state`

The phase-derived target and the executed retained state are separate
processor states.

### Fixed ternary invariants

| Invariant | Value |
|---|---|
| Balanced ternary notation | `-1/0/1` |
| Semantic values | `-1`, `0`, `1` |
| Active neutral state | `0` |
| Direct `-1 → 1` transition | forbidden |
| Direct `1 → -1` transition | forbidden |
| Negative-to-positive route | `-1 → 0 → 1` |
| Positive-to-negative route | `1 → 0 → -1` |
| Temporal scheduler modes | `1/7`, `7/1` |
| Separate service scheduler mode | `free` |

Opposite-polarity transitions are split into two tick-separated legs. The
first leg enters active state `0`; the second leg may complete later under the
scheduler, pending-route, and capacity boundaries.

## Quick start

Required Python version:

`Python 3.12+`

Install the exact repository dependencies:

```
python -m pip install -r requirements.txt
```

Verify the committed M31 publication:

```
python frp_m31_phase_interference_thermal_evidence.py --verify
```

Run the deterministic M31 self-test:

```
python frp_m31_phase_interference_thermal_evidence.py --self-test
```

Run all focused M31 qualification tests:

```
python -m unittest tests.test_frp_m31_phase_interference_thermal_evidence -v
```

Recorded result:

`Ran 60 tests — OK`

Run the executable semantic reference:

```
python frp_prototype_v1_7_0.py --mode demo --output json --include-trace
```

Run its qualified self-test:

```
python frp_prototype_v1_7_0.py --mode self-test --output json
```

Additional commands are documented in [USAGE.md](USAGE.md) and
[REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## M31 canonical publication

| Record | Path |
|---|---|
| Producer | [`frp_m31_phase_interference_thermal_evidence.py`](frp_m31_phase_interference_thermal_evidence.py) |
| Focused tests | [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](tests/test_frp_m31_phase_interference_thermal_evidence.py) |
| Schema | [`schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`](schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json) |
| Evidence | [`artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`](artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json) |
| Manifest | [`artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`](artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json) |
| Qualification | [`artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`](artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json) |

Schema identity:

`frp.m31.phase_interference_active_zero_thermal_evidence.v1`

The producer emits the schema, evidence, manifest, and qualification records
as four deterministic canonical outputs.

## Active-zero evidence

| Published record | Value |
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

Every published opposite-polarity request is routed through active state `0`.
The committed evidence contains no executed direct opposite-polarity
transition.

## Thermal evidence

M31 keeps historical and current evidence contours separate.

The reproduced FRP v0.9.3 model workload records:

| Historical model value | Recorded value |
|---|---:|
| Binary-style forced-switch `heat_peak` | `0.051000` |
| Distributed active-neutral ternary `heat_peak` | `0.003250` |
| Ratio | `15.6923076923` |
| Relative reduction | `93.63%` |
| Physical temperature measurement | `false` |

These values belong to the exact historical model and workload preserved in
the evidence record. Historical `heat_peak`, current architecture-comparison
records, normalized activity cost, and the RC temperature-proxy profile are
not merged or normalized into one measurement class.

## FRP Trace Observatory

[FRP Trace Observatory](https://github.com/maximumberlin76-gif/FRP-Trace-Observatory)
is a separate downstream validation and visualization repository.

Publication direction:

`FRP published bytes → FRP-Trace-Observatory`

The boundary is one-way and read-only. The Observatory consumes committed
FRP schemas, traces, evidence, manifests, registries, and qualification
records. It does not execute FRP producer source and does not modify FRP
source, published records, benchmarks, workflows, or release history.

The downstream contract forbids:

- metric normalization;
- semantic reimplementation;
- FRP source mutation;
- downstream writeback.

The M28 upstream interchange records remain available under
[`artifacts/m28/`](artifacts/m28/) and [`schemas/m28/`](schemas/m28/).

## Implementation layers

| Layer | Repository boundary | Status |
|---|---|---|
| M15 | Deterministic executable semantics and implementation mapping | `PASS` |
| M16 | SystemVerilog RTL core and target-independent FPGA preparation | `PASS` |
| M17–M29 | Published-artifact, trace, registry, Observatory, and qualification progression | `PASS` |
| M30 | Reproducibility, qualification, and archival release closure | `PASS` |
| M31 | Phase-interference, active-zero, and thermal-evidence publication | `PASS` |

RTL records are stored under [`rtl/m16/`](rtl/m16/). FPGA preparation records
are stored under [`fpga/m16/`](fpga/m16/). Milestone artifacts and schemas are
stored under [`artifacts/`](artifacts/) and [`schemas/`](schemas/).

## Repository navigation

| Subject | Record |
|---|---|
| Execution | [USAGE.md](USAGE.md) |
| Reproducibility | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) |
| Repository structure | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Architecture progression | [ROADMAP.md](ROADMAP.md) |
| Release history | [CHANGELOG.md](CHANGELOG.md) |
| Structured output | [docs/output_schema.md](docs/output_schema.md) |
| RTL implementation | [rtl/m16/README.md](rtl/m16/README.md) |
| FPGA preparation | [fpga/m16/CLOSURE.md](fpga/m16/CLOSURE.md) |
| M31 validation index | [FRP_VALIDATION_INDEX_v3_3_0.md](FRP_VALIDATION_INDEX_v3_3_0.md) |
| M31 release notes | [RELEASE_NOTES_v3_3_0.md](RELEASE_NOTES_v3_3_0.md) |
| M31 test report | [TEST_REPORT_v3_3_0.md](TEST_REPORT_v3_3_0.md) |

All historical evidence, benchmark results, schemas, qualification records,
release documents, workflows, and archival packages remain preserved in their
release-specific repository paths.

## License

Licensed under the [Apache License 2.0](LICENSE).

## Author

**Maksym Marnov (Alchimist)**

Berlin, Germany
