# FRP M32 Registered-Target and Deterministic RTL Trace Boundary Closure

## Boundary identity

| Field | Recorded value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Released upstream baseline | `FRP v3.3.0 / M31` |
| Implementation milestone | `M32` |
| Closed directory | `rtl/m32/` |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Trace-export qualification commit | `c9944b801d5c84464130d4705b7aa47919acd9ca` |
| Documentation antecedent commit | `bcf1d39020475817e87c18d472af8807079fab23` |
| Integrated top module | `frp_m32_core` |
| Registered-boundary synthesis top | `frp_m32_registered_target_boundary` |
| Scheduler modes | `7/1` and `1/7` |
| Canonical ternary notation | `-1/0/1` |
| Trace schema | `frp.m32.deterministic_rtl_trace_bundle.v1` |
| License | Apache-2.0 |
| Closure status | `M32 REGISTERED-TARGET AND DETERMINISTIC RTL TRACE BOUNDARY CLOSED` |

This closure applies to the implemented M32 registered-target integration,
its bounded formal and registered-boundary synthesis records, deterministic
SystemVerilog execution, scheduler-specific traces, exact trace exporter, and
canonical publication artifacts. The released upstream baseline remains
`FRP v3.3.0 / M31`; this closure does not assign a new release version.

## Closure authority

The M32 implementation and publication boundary is supported by two
successful manual GitHub Actions records.

| Qualification boundary | Workflow | Successful run | Qualified commit | Result |
|---|---|---|---|---|
| registered-target RTL, synthesis, bounded proofs, simulations, and traces | [`FRP M32 Registered Target Core`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) | [`#6`](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/runs/34254436439) | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` | `SUCCESS` |
| deterministic transcript replay, canonical generation, verification, and published-output comparison | [`FRP M32 Deterministic RTL Trace Export`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) | [`#2`](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/runs/34292365277) | `c9944b801d5c84464130d4705b7aa47919acd9ca` | `SUCCESS` |

The synchronized simulation transcript at commit
`bcf1d39020475817e87c18d472af8807079fab23` was followed by these successful
repository checks:

| Workflow record | Result |
|---|---|
| `FRP Self Test #709` | `SUCCESS` |
| `FRP Structured Output #665` | `SUCCESS` |
| `FRP Benchmark Smoke Test #705` | `SUCCESS` |

## Closed artifact classes

The M32 closure keeps implementation, formal, workflow, exporter,
publication, and documentation identities distinct.

| Artifact class | Count | Bytes | Identity authority |
|---|---:|---:|---|
| inherited M31 RTL sources | `16` | `252826` | canonical M32 manifest |
| M32 RTL sources and testbenches | `11` | `140680` | canonical M32 manifest |
| M32 bounded-formal source | `1` | `7698` | canonical M32 manifest |
| registered-target workflow | `1` | `41712` | canonical M32 manifest |
| complete canonical source boundary | `29` | `442916` | source commit `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| deterministic trace exporter | `1` | `64267` | exact export-workflow identity |
| independent exporter tests | `1` | `30889` | exact export-workflow identity |
| deterministic export workflow | `1` | `20361` | repository identity recorded in `ARTIFACTS.md` |
| canonical publication outputs | `4` | `458096` | raw and embedded SHA-256 records |
| antecedent M32 documentation | `4` | `70031` | current repository identities |
| this closure record | `1` | self-excluded | repository path `rtl/m32/CLOSURE.md` |

The five-file M32 documentation boundary after this addition is:

- `README.md`;
- `ARTIFACTS.md`;
- `SIMULATION.md`;
- `SIMULATION_TRANSCRIPT.md`;
- `CLOSURE.md`.

`CLOSURE.md` is excluded from its own byte and SHA-256 table to avoid a
self-referential identity.

## M32 implementation artifact closure

| Artifact | Closed function | Qualification record |
|---|---|---|
| `frp_m32_registered_target_boundary.sv` | clocked target capture, ternary-domain validation, retained valid state, and capture counters | lint, `8/16/32`-cell synthesis, bounded proof, deterministic simulation |
| `frp_m32_registered_target_boundary_tb.sv` | accepted, rejected, disabled, reset, retained-bank, and counter-clear capture sequences | `2/2` byte-identical executions |
| `frp_m32_registered_target_request_path.sv` | registered target gate and M31 request-adapter composition | lint and deterministic simulation |
| `frp_m32_registered_target_request_path_tb.sv` | source, registered, request, pending-route, and scheduler separation | `2/2` byte-identical executions |
| `frp_m32_core.sv` | integrated registered-target top-level over the M31 phase, execution, thermal, and stability contour | lint and deterministic simulation |
| `frp_m32_core_tb.sv` | integrated capture, request, execution, routing, frequency, thermal, stability, and invariant sequence | `2/2` byte-identical executions |
| `frp_m32_mode_7_1_tb.sv` | dedicated `7/1` cadence and two-leg route sequence | `2/2` byte-identical executions |
| `frp_m32_mode_1_7_tb.sv` | dedicated `1/7` cadence and two-leg route sequence | `2/2` byte-identical executions |
| `frp_m32_trace_monitor.sv` | deterministic sample, bank, cell, and request records | lint and structured trace execution |
| `frp_m32_mode_7_1_trace_tb.sv` | mode `7/1` testbench and trace-monitor composition | `2/2` byte-identical full transcripts |
| `frp_m32_mode_1_7_trace_tb.sv` | mode `1/7` testbench and trace-monitor composition | `2/2` byte-identical full transcripts |
| `formal/m32/frp_m32_registered_target_boundary_formal.sv` | registered-target safety and capture-sequence harnesses | `14` assertions at depth `4`, each harness `2/2` deterministic |

Implementation artifact result:

```
PASS
```

## Integrated execution-chain closure

The qualified automatic execution chain is:

```
M31 retained phase and frequency dynamics
-> M31 relative-phase interference with local gamma_effective_i
-> M31 phase-to-ternary source target
-> M32 registered target boundary
-> M32 registered request gate
-> M31 deterministic request formation
-> M31 scheduler and request handling
-> M31 pending opposite-polarity routing
-> active state 0
-> M31 capacity control
-> M31 retained-state writeback
-> M31 invariant, thermal, and stability records
-> M32 deterministic structured trace monitor
-> M32 canonical trace exporter
```

The relative-phase term remains:

```
sin(theta_j - theta_i - gamma_effective_i)
```

The receiving-cell value `gamma_effective_i` is used throughout the local
interaction sum. Phase remains a retained unsigned 32-bit modular word, and
retained frequency remains a signed Q16 dynamic state with relaxation toward
its target.

Integrated execution-chain result:

```
PASS
```

## Registered-target closure

The registered boundary accepts a phase-derived target bank only when:

```
tick_enable
&& phase_target_valid
&& phase_target_domain_valid
```

The complete capture transaction is rejected when any cell contains the
reserved encoding. A rejected or disabled capture retains the preceding
registered target bank and registered-valid state.

| Registered-target relation | Result |
|---|---|
| reset target bank equals active state `0` | `PASS` |
| reset registered-valid state is clear | `PASS` |
| valid enabled source bank is captured on the clock edge | `PASS` |
| invalid source bank is rejected as one transaction | `PASS` |
| disabled capture retains the registered bank | `PASS` |
| source target remains separate from registered target | `PASS` |
| registered target remains separate from executed state | `PASS` |
| unregistered source cannot form an automatic request | `PASS` |
| accepted and rejected capture counters saturate independently | `PASS` |
| counter clearing preserves the registered target bank | `PASS` |

Registered-target boundary result:

```
PASS
```

## Balanced ternary execution closure

The retained processor-state domain is exactly:

```
T = {-1, 0, 1}
```

| State | Encoding | Recorded execution role |
|---:|---|---|
| `-1` | `2'b11` | negative-polarity retained state |
| `0` | `2'b00` | mediation, balancing, routing, damping, transition staging, retained-state participation, pending-route handling, and controlled neutralization |
| `1` | `2'b01` | positive-polarity retained state |
| reserved | `2'b10` | excluded encoding |

State `0` is retained, executable, and separately observable. It is the
first retained state of an opposite-polarity route before the later pending
destination writeback.

Direct opposite-polarity retained transitions remain excluded:

```
-1 -> 1
1 -> -1
```

The required routes remain:

```
-1 -> 0 -> 1
1 -> 0 -> -1
```

The M32 canonical full traces record the `1 -> 0 -> -1` route with separate
first and second legs in both scheduler modes.

| Mode | First leg | Second leg | Direct-event count | Result |
|---|---|---|---:|---|
| `7/1` | source tick `9`, cell `0`, retained state `0`, pending target `-1` | source tick `15`, cell `0`, retained state `-1`, pending cleared | `0` | `PASS` |
| `1/7` | source tick `10`, cell `0`, retained state `0`, pending target `-1` | source tick `16`, cell `0`, retained state `-1`, pending cleared | `0` | `PASS` |

Balanced ternary execution result:

```
PASS
```

## Scheduler closure

The two scheduler modes retain separate testbenches, traces, records, and
transcript identities.

| Record | Mode `7/1` | Mode `1/7` |
|---|---:|---:|
| source ticks | `16` | `17` |
| cadence | `14 balance / 2 commit` | `3 excite / 14 neutralize` |
| sample records | `16` | `17` |
| packed-bank records | `16` | `17` |
| per-cell records | `128` | `136` |
| request-lane records | `32` | `34` |
| total structured records | `192` | `204` |
| active-state-`0` cell observations | `115` | `123` |
| full-transcript replay | `2/2` byte-identical | `2/2` byte-identical |

Scheduler closure result:

```
PASS
```

## Trace-observation closure

`frp_m32_trace_monitor` emits four deterministic record classes for every
enabled source tick.

| Record class | Cardinality per tick | Closed observation boundary |
|---|---:|---|
| `M32_TRACE_SAMPLE` | `1` | scheduler, capture, counters, capacity, invariants, phase order, coherence capacity, thermal, and stability records |
| `M32_TRACE_BANK` | `1` | packed source, registered, execution, retained, pending, acceptance, and route-leg banks |
| `M32_TRACE_CELL` | `8` | source coordinates, phase, retained frequency, local gamma, interference, targets, retained state, active state `0`, and pending route |
| `M32_TRACE_REQUEST` | `2` | request-lane coordinates, automatic request, execution request, target, and acceptance state |

The combined canonical trace contains:

```
33 source ticks
33 sample records
33 packed-bank records
264 per-cell records
66 request-lane records
396 structured records
```

The trace records preserve pair, cluster, and global phase-order fields as
separate quantities. `coherence_capacity_q16` remains distinct from these
phase-order fields.

| Trace invariant | Recorded result |
|---|---|
| source-tick coordinates complete | `PASS` |
| cell coordinates complete | `PASS` |
| request-lane coordinates complete | `PASS` |
| packed banks match cell records | `PASS` |
| packed masks match cell records | `PASS` |
| ternary code/value pairs valid | `PASS` |
| active-state-`0` markers exact | `PASS` |
| first and second route legs separately observable | `PASS` |
| phase evolution records present | `PASS` |
| local effective gamma records present | `PASS` |
| relative-phase interference records present | `PASS` |
| retained-frequency dynamics observed | `PASS` |
| thermal telemetry present | `PASS` |
| stability telemetry present | `PASS` |
| invariant flags valid for every sample | `PASS` |
| direct opposite-polarity events | `0` |
| reserved-state events | `0` |
| queue-overflow events | `0` |

Trace-observation closure result:

```
PASS
```

## Lint, synthesis, and bounded-formal closure

| Qualification operation | Exact scope | Recorded result |
|---|---|---|
| Verilator lint | `11` M32 implementation and trace tops | `11/11 PASS` |
| registered-boundary synthesis | `frp_m32_registered_target_boundary` at `8`, `16`, and `32` cells | `3/3 profiles, 2/2 byte-identical netlists per profile` |
| safety bounded proof | `frp_m32_registered_target_boundary_safety_formal`, `10` assertions, depth `4` | `2/2 deterministic filtered records` |
| capture-sequence bounded proof | `frp_m32_registered_target_boundary_sequence_formal`, `4` assertions, depth `4` | `2/2 deterministic filtered records` |

The synthesis record applies to the registered-target boundary top. The
integrated `frp_m32_core` is qualified in this boundary by lint,
deterministic simulation, assertion execution, and deterministic trace
generation.

Lint, synthesis, and bounded-formal result:

```
PASS
```

## Deterministic execution closure

Each executable top was built once and executed twice. Each runtime pair was
compared byte-for-byte.

| Executable top | Stable terminal marker | Replay result |
|---|---|---|
| `frp_m32_registered_target_boundary_tb` | `FRP_M32_REGISTERED_TARGET_BOUNDARY_TB: PASS` | `2/2 byte-identical` |
| `frp_m32_registered_target_request_path_tb` | `FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB: PASS` | `2/2 byte-identical` |
| `frp_m32_core_tb` | `FRP_M32_INTEGRATED_REGISTERED_TARGET_CORE_TB: PASS` | `2/2 byte-identical` |
| `frp_m32_mode_7_1_tb` | `FRP_M32_REGISTERED_TARGET_MODE_7_1_TB: PASS` | `2/2 byte-identical` |
| `frp_m32_mode_1_7_tb` | `FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS` | `2/2 byte-identical` |
| `frp_m32_mode_7_1_trace_tb` | `FRP_M32_MODE_7_1_TRACE_TB: PASS samples=16` | `2/2 byte-identical` |
| `frp_m32_mode_1_7_trace_tb` | `FRP_M32_MODE_1_7_TRACE_TB: PASS samples=17` | `2/2 byte-identical` |

Deterministic execution result:

```
PASS
```

## Exact transcript closure

| Scheduler mode | Replay | Bytes | SHA-256 |
|---|---:|---:|---|
| `7/1` | `1` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `7/1` | `2` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `1/7` | `1` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |
| `1/7` | `2` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |

Exact transcript closure result:

```
PASS
```

## Deterministic exporter closure

| Exporter boundary | Recorded value |
|---|---|
| exporter path | `frp_m32_deterministic_rtl_trace_export.py` |
| exporter bytes | `64267` |
| exporter SHA-256 | `1a575482d0c62f977afc72f25c8d8eacb0daa35981f39cb64b7f85069e5c43cd` |
| independent test path | `tests/test_frp_m32_deterministic_rtl_trace_export.py` |
| independent test bytes | `30889` |
| independent test SHA-256 | `e2b53c9973219b02c0fce2eda835bef87de0d8681ab61af89ef621fbafdfe774` |
| focused tests | `49/49 PASS` |
| deterministic generation replays | `2` |
| rejected mutations | `4/4` |
| source identities | `29/29 exact` |
| transcript identities | `4/4 exact` |
| output verification state | `EXACT` |
| published-output comparison | `4/4 byte-identical` |

Deterministic exporter result:

```
PASS
```

## Canonical publication closure

| Canonical output | Bytes | Raw SHA-256 | Result |
|---|---:|---|---|
| `schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json` | `34066` | `534db8227218184cac5d1cabb461dd63b1b61a99e0269c98535539ad3f7d7da2` | `PASS` |
| `artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json` | `412195` | `62d8c1e6d205b9262a5c950883d3259275d5049f7a896ae12956a210cb75b7e0` | `PASS` |
| `artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json` | `7211` | `da011dbc726d6d1fc0b7dbae12afe1e13d8240df64b9474fd0130c94ba005859` | `PASS` |
| `artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json` | `4624` | `26ec2d3eadd73b490eb023572101bb78cf5d11561ead91b78b1a30e690458273` | `PASS` |
| **Total** | **`458096`** | **`4` exact files** | **`PASS`** |

| Canonical record | Embedded SHA-256 |
|---|---|
| trace bundle | `63b36c1fb29d28a33bb5387d7658c97fc0a51f6823f79dc71382132236685f9b` |
| manifest | `a9dd7d470fd094cb1dbb6fa360f6c28bf50d4aae4bf2f1ba34ad223655968c2e` |
| qualification | `a695ccb3c7f083e219ff6908dfc38e6f4e7ef37fca6da22f40c6303117027c5d` |

The qualification record contains `38` checks, `38` passed checks, and `0`
failed checks. It qualifies the schema, trace bundle, and manifest. The
qualification record itself is the fourth generated file.

Canonical publication result:

```
38 / 38 PASS
```

## Documentation closure

| Documentation artifact | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `README.md` | `12728` | `e4ac144bd92d611eb04cc8b1e00fa016bd92cbefd5cddfa1ba91c4a60ef7a2cb` | `COMPLETE` |
| `ARTIFACTS.md` | `15458` | `b6679c124b08b3142fb4700ea23315770906799808d597b958ffb2280788133c` | `COMPLETE` |
| `SIMULATION.md` | `18011` | `c0095e7e9ef51b0ab698b09c8c76a29993e64203bb0f9d46bb9d1c47c61c4c2d` | `COMPLETE` |
| `SIMULATION_TRANSCRIPT.md` | `23834` | `19a0c612ff593306fa5e3886abf310a8994a22b8ef164a08de27121b3c108937` | `COMPLETE` |
| `CLOSURE.md` | self-excluded | self-excluded | `COMPLETE` |

Documentation closure:

```
5 / 5 COMPLETE
```

## Provenance closure

The canonical bundle assigns the exact M31/M32 source boundary to:

```
upstream_frp_systemverilog_rtl
```

The bundle records repository source paths, source byte lengths, source
SHA-256 values, transcript identities, and source coordinates. It contains no
downstream Observatory implementation artifact.

The trace schema, bundle, manifest, and qualification records form the exact
read-only artifact boundary available to downstream intake.

Provenance closure result:

```
PASS
```

## Historical preservation closure

Both successful M32 qualification workflows ended with a clean-repository
comparison and the stable terminal record:

```
Repository preservation: PASS
```

The M32 boundary is additive. Earlier evidence, benchmark, manifest, schema,
workflow, failed-run, successful-run, release, tag, archive, FPGA, RTL, and
deterministic identity history remains at its established repository and
GitHub paths.

The preserved repair workflow remains at:

```
.github/workflows/frp-m32-canonical-trace-bundle-repair.yml
```

It records the guarded restoration of the exact canonical bundle after
manual multipart insertion. It is not part of the canonical source identity
set and does not replace the deterministic export workflow.

Historical preservation result:

```
PASS
```

## Final closure table

| Closure boundary | Recorded result |
|---|---|
| fixed RTL source boundary commit | `PASS` |
| inherited M31 RTL identities | `16/16 exact` |
| M32 RTL identities | `11/11 exact` |
| M32 bounded-formal identity | `1/1 exact` |
| registered-target workflow identity | `1/1 exact` |
| complete canonical source boundary | `29/29 exact` |
| registered target capture and retention | `PASS` |
| phase-derived, registered, request, execution, and retained-state separation | `PASS` |
| canonical `-1/0/1` domain | `PASS` |
| active state `0` execution and observation | `PASS` |
| tick-separated pending-route legs | `PASS` |
| direct opposite-polarity events | `0` |
| reserved-state events | `0` |
| queue-overflow events | `0` |
| scheduler mode `7/1` | separate deterministic trace `PASS` |
| scheduler mode `1/7` | separate deterministic trace `PASS` |
| Verilator lint tops | `11/11 PASS` |
| registered-boundary synthesis profiles | `3/3 PASS` |
| bounded formal assertions | `14/14 PASS at depth 4` |
| deterministic testbench pairs | `7/7 byte-identical` |
| deterministic transcript identities | `4/4 exact` |
| focused exporter tests | `49/49 PASS` |
| mutation rejections | `4/4 PASS` |
| source ticks | `33` |
| structured trace records | `396` |
| canonical qualification checks | `38/38 PASS` |
| canonical publication files | `4/4 exact` |
| M32 documentation files | `5/5 COMPLETE` |
| provenance boundary | `PASS` |
| repository preservation | `PASS` |
| M32 registered-target and deterministic RTL trace boundary | `CLOSED` |

## Closure statement

The FRP M32 registered-target and deterministic RTL trace boundary is closed.

The closed technical boundary contains:

- the exact `29`-identity M31/M32 source boundary;
- the integrated `frp_m32_core` top module;
- clocked registered capture of valid phase-derived ternary target banks;
- separate phase-derived, registered, request, execution, retained-state,
  and pending-route quantities;
- inherited relative-phase interference using local `gamma_effective_i`;
- inherited retained modular phase and retained-frequency dynamics;
- active state `0` mediation and separately observable route staging;
- separate scheduler modes `7/1` and `1/7`;
- tick-separated pending-route first and second legs;
- deterministic request formation, capacity control, and retained writeback;
- pair, cluster, and global phase-order records separated from coherence
  capacity;
- thermal, stability, and invariant telemetry;
- eleven linted M32 implementation and trace tops;
- deterministic `8`, `16`, and `32` cell registered-boundary synthesis
  profiles;
- fourteen bounded assertions at depth `4`;
- seven byte-identical deterministic simulation pairs;
- four exact scheduler transcript identities;
- `33` source ticks and `396` structured records;
- forty-nine independent exporter tests;
- four deterministic mutation rejections;
- four exact canonical publication files;
- thirty-eight passed canonical qualification checks;
- five synchronized M32 documentation records;
- preserved historical repository records.

Final registered-target workflow:

```
FRP M32 Registered Target Core #6
```

Final trace-export workflow:

```
FRP M32 Deterministic RTL Trace Export #2
```

Final technical closure status:

```
M32 REGISTERED-TARGET AND DETERMINISTIC RTL TRACE BOUNDARY CLOSED
```

No GitHub Release, release tag, release date, or Zenodo deposit is created or
modified by this technical closure record.

## Closure references

| Record | Path |
|---|---|
| M32 architecture and boundary | [`README.md`](README.md) |
| exact artifact index | [`ARTIFACTS.md`](ARTIFACTS.md) |
| reproducible execution procedure | [`SIMULATION.md`](SIMULATION.md) |
| successful qualification transcript | [`SIMULATION_TRANSCRIPT.md`](SIMULATION_TRANSCRIPT.md) |
| registered-target workflow | [`../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) |
| deterministic trace-export workflow | [`../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) |
| bounded formal harness | [`../../formal/m32/frp_m32_registered_target_boundary_formal.sv`](../../formal/m32/frp_m32_registered_target_boundary_formal.sv) |
| trace exporter | [`../../frp_m32_deterministic_rtl_trace_export.py`](../../frp_m32_deterministic_rtl_trace_export.py) |
| independent exporter tests | [`../../tests/test_frp_m32_deterministic_rtl_trace_export.py`](../../tests/test_frp_m32_deterministic_rtl_trace_export.py) |
| trace schema | [`../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json`](../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json) |
| trace bundle | [`../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json`](../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json) |
| manifest | [`../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json`](../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json) |
| qualification | [`../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json`](../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json) |
| repository license | [`../../LICENSE`](../../LICENSE) |

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany  
ORCID: `0009-0000-0832-9597`
