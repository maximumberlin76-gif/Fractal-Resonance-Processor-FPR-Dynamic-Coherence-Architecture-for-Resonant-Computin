# FRP M32 RTL Simulation Transcript

## Boundary identity

| Field | Recorded value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Released upstream baseline | `FRP v3.3.0 / M31` |
| Implementation milestone | `M32` |
| M32 boundary | registered target and deterministic RTL trace export |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Integrated top module | `frp_m32_core` |
| Qualified integrated configuration | `8` cells, `2` request lanes |
| Registered-boundary synthesis profiles | `8`, `16`, and `32` cells |
| Scheduler modes | `7/1` and `1/7` |
| Canonical ternary notation | `-1/0/1` |
| Canonical trace schema | `frp.m32.deterministic_rtl_trace_bundle.v1` |
| Canonical trace qualification | `38 / 38 PASS` |

This transcript records two successful manual GitHub Actions runs: the M32
registered-target source qualification and the deterministic trace-export
publication qualification. Stable terminal records below are literal records
required by the corresponding workflow. Counts, byte lengths, and SHA-256
identities are reproduced from the workflows and tracked M32 artifacts.

Runner-generated toolchain records, synthesis identities, bounded-proof
records, and intermediate trace identities are retained in the uploaded
workflow artifacts. Values that are not present in the repository or the
stable workflow record are not reconstructed here.

## Successful qualification runs

### Registered-target core

| Field | Recorded value |
|---|---|
| Workflow | `FRP M32 Registered Target Core` |
| Workflow file | `.github/workflows/frp-m32-registered-target-boundary-workflow.yml` |
| Trigger | `workflow_dispatch` |
| Branch | `main` |
| Successful run | [`#6`](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/runs/34254436439) |
| Run ID | `34254436439` |
| Qualified commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Run created | `2026-09-08T17:00:01Z` |
| Run updated | `2026-09-08T17:03:14Z` |
| Recorded duration | `3m 13s` |
| Status | `completed` |
| Conclusion | `success` |

### Deterministic RTL trace export

| Field | Recorded value |
|---|---|
| Workflow | `FRP M32 Deterministic RTL Trace Export` |
| Workflow file | `.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml` |
| Trigger | `workflow_dispatch` |
| Branch | `main` |
| Successful run | [`#2`](https://github.com/maximumberlin76-gif/Fractal-Resonance-Processor-FRP-Ternary-Resonant-Coherence-Processor/actions/runs/34292365277) |
| Run ID | `34292365277` |
| Qualified commit | `c9944b801d5c84464130d4705b7aa47919acd9ca` |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Run created | `2026-09-08T23:49:49Z` |
| Run updated | `2026-09-08T23:51:05Z` |
| Recorded duration | `1m 16s` |
| Status | `completed` |
| Conclusion | `success` |

The export run occurred after the exporter, independent tests, canonical
outputs, and exact published-output comparison were present at the qualified
commit. It retains the fixed RTL source boundary commit recorded by the
canonical bundle.

## Execution environment

| Record | Registered-target run | Trace-export run |
|---|---|---|
| Runner | `ubuntu-24.04` | `ubuntu-24.04` |
| Locale | `C.UTF-8` | `C.UTF-8` |
| Time zone | `UTC` | `UTC` |
| Python | `3.12` | `3.12` |
| RTL simulator and lint tool | `verilator` | `verilator` |
| Native compiler | `g++` | `g++` |
| Formal and synthesis package | `yowasp-yosys==0.68.0.0.post1208` | not used |
| Schema validator | not used | `jsonschema==4.25.1` |
| Python hash seed | workflow default | `0` |

The workflows wrote the resolved runtime version strings to
`m32-toolchain.txt` and `m32-trace-export-toolchain.txt` inside their uploaded
qualification artifacts.

## Registered-target qualification sequence

The successful registered-target run completed these ordered gates:

| Gate | Recorded result |
|---|---|
| checkout of the dispatched commit with credentials disabled | `PASS` |
| Python 3.12 setup | `PASS` |
| manual `workflow_dispatch` and `main` branch guard | `PASS` |
| clean checked-out repository guard | `PASS` |
| exact M31/M32 source identity verification | `28 / 28 PASS` |
| Verilator and exact Yosys package installation | `PASS` |
| lint of registered-target and trace contours | `11 / 11 PASS` |
| registered-boundary deterministic synthesis profiles | `3 / 3 PASS` |
| registered-target bounded safety proofs | `10` assertions, depth `4`, `2 / 2` deterministic records |
| registered-target capture-sequence proofs | `4` assertions, depth `4`, `2 / 2` deterministic records |
| deterministic testbench executions | `7` testbenches, each `2 / 2` byte-identical |
| scheduler and full-trace record verification | `PASS` |
| qualification artifact upload | `PASS` |
| final repository-preservation guard | `PASS` |

Overall registered-target workflow result:

```
SUCCESS
```

## Exact source boundary

The registered-target workflow checked `28` exact source identities:

| Source class | Count |
|---|---:|
| inherited M31 RTL sources | `16` |
| M32 RTL sources and testbenches | `11` |
| M32 formal source | `1` |
| total checked by the registered-target workflow | `28` |

The canonical M32 trace bundle adds the registered-target workflow itself as
the twenty-ninth source identity:

| Canonical source-boundary record | Value |
|---|---:|
| exact source identities | `29 / 29` |
| complete source bytes | `442916` |
| source commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |

Exact paths, byte lengths, and SHA-256 values are recorded in
[`ARTIFACTS.md`](ARTIFACTS.md) and in the canonical manifest.

## Verilator lint record

The successful run linted these eleven top modules with SystemVerilog,
timing, and assertion processing enabled:

| Top module | Result |
|---|---|
| `frp_m32_registered_target_boundary` | `PASS` |
| `frp_m32_registered_target_boundary_tb` | `PASS` |
| `frp_m32_registered_target_request_path` | `PASS` |
| `frp_m32_registered_target_request_path_tb` | `PASS` |
| `frp_m32_core` | `PASS` |
| `frp_m32_core_tb` | `PASS` |
| `frp_m32_mode_7_1_tb` | `PASS` |
| `frp_m32_mode_1_7_tb` | `PASS` |
| `frp_m32_trace_monitor` | `PASS` |
| `frp_m32_mode_7_1_trace_tb` | `PASS` |
| `frp_m32_mode_1_7_trace_tb` | `PASS` |

Stable workflow record:

```
FRP M32 Verilator lint: PASS
```

## Registered-boundary synthesis record

Synthesis applied only to `frp_m32_registered_target_boundary`. The workflow
used `synth -noabc`, structural checks, statistics generation, and JSON
netlist export.

| Cell profile | Netlist executions | Byte comparison | Result |
|---:|---:|---|---|
| `8` | `2` | byte-identical | `PASS` |
| `16` | `2` | byte-identical | `PASS` |
| `32` | `2` | byte-identical | `PASS` |

Stable workflow record:

```
FRP M32 deterministic synthesis profiles: PASS
```

This synthesis record applies to the registered-target boundary module. The
integrated `frp_m32_core` record in this M32 workflow consists of lint,
deterministic simulation, assertion execution, and trace generation.

## Bounded formal record

The formal workflow command used a four-step sequence with
`-set-def-formal`, `-set-init-zero`, `-seq 4`, `-timeout 300`, and `-verify`.

| Formal top | Assertions | Depth | Executions | Filtered records | Result |
|---|---:|---:|---:|---|---|
| `frp_m32_registered_target_boundary_safety_formal` | `10` | `4` | `2` | byte-identical | `PASS` |
| `frp_m32_registered_target_boundary_sequence_formal` | `4` | `4` | `2` | byte-identical | `PASS` |

Each execution required the terminal Yosys record:

```
SAT proof finished - no model found: SUCCESS!
```

Stable workflow record:

```
FRP M32 registered-target bounded proofs: PASS
```

The recorded formal boundary is bounded to depth `4` and applies to the two
listed registered-target harness tops.

## Deterministic testbench record

Each testbench was built once and executed twice. The two runtime logs for
each top were compared byte-for-byte before its terminal marker was accepted.

| Top module | Runtime replays | Stable terminal marker | Result |
|---|---:|---|---|
| `frp_m32_registered_target_boundary_tb` | `2 / 2` | `FRP_M32_REGISTERED_TARGET_BOUNDARY_TB: PASS` | `PASS` |
| `frp_m32_registered_target_request_path_tb` | `2 / 2` | `FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB: PASS` | `PASS` |
| `frp_m32_core_tb` | `2 / 2` | `FRP_M32_INTEGRATED_REGISTERED_TARGET_CORE_TB: PASS` | `PASS` |
| `frp_m32_mode_7_1_tb` | `2 / 2` | `FRP_M32_REGISTERED_TARGET_MODE_7_1_TB: PASS` | `PASS` |
| `frp_m32_mode_1_7_tb` | `2 / 2` | `FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS` | `PASS` |
| `frp_m32_mode_7_1_trace_tb` | `2 / 2` | `FRP_M32_MODE_7_1_TRACE_TB: PASS samples=16` | `PASS` |
| `frp_m32_mode_1_7_trace_tb` | `2 / 2` | `FRP_M32_MODE_1_7_TRACE_TB: PASS samples=17` | `PASS` |

Stable workflow record:

```
FRP M32 deterministic replays: PASS
```

## Scheduler trace record

The two scheduler modes retained separate testbenches, runtime logs,
structured records, and replay identities.

| Record | Mode `7/1` | Mode `1/7` |
|---|---:|---:|
| source ticks | `16` | `17` |
| balance ticks | `14` | not applicable |
| commit ticks | `2` | not applicable |
| excite ticks | not applicable | `3` |
| neutralize ticks | not applicable | `14` |
| sample records | `16` | `17` |
| packed-bank records | `16` | `17` |
| per-cell records | `128` | `136` |
| request-lane records | `32` | `34` |
| total structured records | `192` | `204` |
| active-state-`0` cell observations | `115` | `123` |

Combined record count:

```
33 source ticks
33 sample records
33 packed-bank records
264 per-cell records
66 request-lane records
396 structured records
```

Stable workflow record:

```
FRP M32 scheduler and full traces: PASS
```

## Opposite-polarity route record

The recorded route is:

```
1 → 0 → -1
```

The first and second legs occurred on separate source ticks.

| Mode | Route leg | Source tick | Cell | Retained state | Pending target | Active state `0` | Result |
|---|---|---:|---:|---:|---:|---|---|
| `7/1` | first | `9` | `0` | `0` | `-1` | active | `PASS` |
| `7/1` | second | `15` | `0` | `-1` | `0` | not asserted | `PASS` |
| `1/7` | first | `10` | `0` | `0` | `-1` | active | `PASS` |
| `1/7` | second | `16` | `0` | `-1` | `0` | not asserted | `PASS` |

For both first-leg records, the pending route was active and retained the
destination `-1`. For both second-leg records, the destination `-1` was
written back and the pending route was cleared.

## Trace telemetry and invariant record

| Verified record | Mode `7/1` | Mode `1/7` | Result |
|---|---:|---:|---|
| `invariant_all_valid=1` sample records | `16 / 16` | `17 / 17` | `PASS` |
| `actual_direct_events=0` sample records | `16 / 16` | `17 / 17` | `PASS` |
| `reserved_state_events=0` sample records | `16 / 16` | `17 / 17` | `PASS` |
| `queue_overflow_events=0` sample records | `16 / 16` | `17 / 17` | `PASS` |
| phase-order fields present | `16 / 16` | `17 / 17` | `PASS` |
| coherence-capacity fields present | `16 / 16` | `17 / 17` | `PASS` |
| phase fields present in cell records | `128 / 128` | `136 / 136` | `PASS` |
| retained-frequency fields present in cell records | `128 / 128` | `136 / 136` | `PASS` |
| local interference fields present in cell records | `128 / 128` | `136 / 136` | `PASS` |
| phase-projection fields present in cell records | `128 / 128` | `136 / 136` | `PASS` |

The structured records preserve phase evolution, local effective gamma,
relative-phase interference contribution, phase-derived source target,
registered target, request and execution targets, retained state, active
state `0`, pending route, retained frequency, separate phase-order scales,
coherence capacity, thermal telemetry, stability telemetry, invariant state,
and source coordinates.

The successful run recorded zero direct opposite-polarity retained
transitions, zero reserved-state events, and zero queue-overflow events in
every sample.

## Registered-target artifact upload

The successful workflow uploaded one artifact named:

```
frp-m32-registered-target-core-c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941
```

The artifact contains:

- exact source identity records;
- resolved toolchain records;
- two synthesis netlists and logs for each `8`, `16`, and `32` cell profile;
- two safety-proof logs and two filtered safety records;
- two sequence-proof logs and two filtered sequence records;
- two runtime logs for each deterministic testbench;
- scheduler-specific trace extracts;
- full sample, bank, cell, and request record extracts;
- SHA-256 identity records for synthesis, proofs, simulations, and traces.

The workflow retention setting is `90` days.

## Deterministic trace-export qualification sequence

The successful trace-export run completed these ordered gates:

| Gate | Recorded result |
|---|---|
| checkout of the dispatched commit with credentials disabled | `PASS` |
| Python 3.12 setup | `PASS` |
| manual `workflow_dispatch` and `main` branch guard | `PASS` |
| clean checked-out repository guard | `PASS` |
| exporter and independent-test source identities | `2 / 2 PASS` |
| canonical RTL source identities | `29 / 29 PASS` |
| exact execution dependency installation | `PASS` |
| focused exporter tests | `49 / 49 PASS` |
| mode `7/1` transcript executions | `2 / 2` byte-identical |
| mode `1/7` transcript executions | `2 / 2` byte-identical |
| deterministic generation self-test | `2` replays |
| mutation rejection self-test | `4 / 4` rejected |
| canonical output generation | `4 / 4 PASS` |
| canonical schema and semantic verification | `EXACT` |
| tracked publication-file comparison | `4 / 4` byte-identical |
| qualification artifact upload | `PASS` |
| final repository-preservation guard | `PASS` |

Overall trace-export workflow result:

```
SUCCESS
```

## Exporter source identities

| Path | Bytes | SHA-256 | Result |
|---|---:|---|---|
| `frp_m32_deterministic_rtl_trace_export.py` | `64267` | `1a575482d0c62f977afc72f25c8d8eacb0daa35981f39cb64b7f85069e5c43cd` | `PASS` |
| `tests/test_frp_m32_deterministic_rtl_trace_export.py` | `30889` | `e2b53c9973219b02c0fce2eda835bef87de0d8681ab61af89ef621fbafdfe774` | `PASS` |

The focused test log contained one line matching
`^Ran 49 tests in [0-9.]+s$` and exactly one terminal line equal to `OK`.

Stable workflow record:

```
FRP M32 focused exporter tests: PASS
```

## Exact deterministic transcript identities

| Scheduler mode | Replay | Artifact member | Bytes | SHA-256 |
|---|---:|---|---:|---|
| `7/1` | `1` | `m32-mode-7-1-full-trace-run-1.log` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `7/1` | `2` | `m32-mode-7-1-full-trace-run-2.log` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `1/7` | `1` | `m32-mode-1-7-full-trace-run-1.log` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |
| `1/7` | `2` | `m32-mode-1-7-full-trace-run-2.log` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |

Stable workflow record:

```
FRP M32 exact deterministic trace replay pairs: PASS
```

## Canonical output record

| Output | Bytes | Raw file SHA-256 | Result |
|---|---:|---|---|
| `schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json` | `34066` | `534db8227218184cac5d1cabb461dd63b1b61a99e0269c98535539ad3f7d7da2` | `PASS` |
| `artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json` | `412195` | `62d8c1e6d205b9262a5c950883d3259275d5049f7a896ae12956a210cb75b7e0` | `PASS` |
| `artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json` | `7211` | `da011dbc726d6d1fc0b7dbae12afe1e13d8240df64b9474fd0130c94ba005859` | `PASS` |
| `artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json` | `4624` | `26ec2d3eadd73b490eb023572101bb78cf5d11561ead91b78b1a30e690458273` | `PASS` |
| **Total** | **`458096`** | **`4` exact files** | **`PASS`** |

Canonical embedded digests:

| Record | Digest scope | Embedded SHA-256 |
|---|---|---|
| trace bundle | canonical JSON without `bundle_sha256` | `63b36c1fb29d28a33bb5387d7658c97fc0a51f6823f79dc71382132236685f9b` |
| manifest | canonical JSON without `manifest_sha256` | `a9dd7d470fd094cb1dbb6fa360f6c28bf50d4aae4bf2f1ba34ad223655968c2e` |
| qualification | canonical JSON without `qualification_sha256` | `a695ccb3c7f083e219ff6908dfc38e6f4e7ef37fca6da22f40c6303117027c5d` |

The self-test, generation, and verification commands each recorded:

| Field | Value |
|---|---|
| milestone | `M32` |
| schema | `frp.m32.deterministic_rtl_trace_bundle.v1` |
| source commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| source identities | `29` |
| transcript identities | `4` |
| source ticks | `33` |
| structured records | `396` |
| generated files | `4` |
| status | `PASS` |

The verification command recorded:

```
EXACT
```

Stable workflow records:

```
FRP M32 published canonical trace outputs: PASS
FRP M32 canonical trace outputs: PASS
```

## Canonical qualification checks

The tracked qualification record contains `38` checks, `38` passed checks,
and `0` failed checks.

| Check group | Check identifiers | Result |
|---|---|---|
| source and workflow identities | `source_identities_exact`, `workflow_identity_exact` | `2 / 2 PASS` |
| transcript identities and replay equality | mode-specific primary identity, replay identity, and byte equality checks | `6 / 6 PASS` |
| scheduler cadence | `mode_7_1_scheduler_cadence_exact`, `mode_1_7_scheduler_cadence_exact` | `2 / 2 PASS` |
| source coordinates | source-tick, cell, and request-lane completeness checks | `3 / 3 PASS` |
| packed record consistency | bank-to-cell and mask-to-cell consistency checks | `2 / 2 PASS` |
| ternary and active-state records | ternary code/value validity and active-state-`0` marker checks | `2 / 2 PASS` |
| pending and execution separation | pending-route marker, source-target separation, registered-target separation, and source/execution field separation checks | `4 / 4 PASS` |
| route-leg execution | first-leg, second-leg, and separate-observability checks | `3 / 3 PASS` |
| prohibited-event counters | direct opposite transitions absent, reserved states zero, queue overflow zero | `3 / 3 PASS` |
| invariant record | all invariant flags valid | `1 / 1 PASS` |
| phase and frequency records | phase evolution, local effective gamma, relative-phase interference, and retained-frequency dynamics checks | `4 / 4 PASS` |
| multiscale separation | phase-order scales separate and coherence capacity separate from phase order | `2 / 2 PASS` |
| thermal and stability records | thermal telemetry and stability telemetry present | `2 / 2 PASS` |
| schema and digest | canonical schema valid and bundle digest reproduced | `2 / 2 PASS` |
| **Total** | **all qualification checks** | **`38 / 38 PASS`** |

The qualification file records three antecedent qualified artifacts: the
schema, trace bundle, and manifest. The qualification record itself is the
fourth deterministic generated output.

## Trace-export artifact upload

The successful workflow uploaded one artifact named:

```
frp-m32-deterministic-rtl-trace-export-c9944b801d5c84464130d4705b7aa47919acd9ca
```

The artifact contains:

- exporter and test source identity records;
- the `29`-source identity validation record;
- resolved toolchain records;
- focused exporter test logs and identity records;
- two exact full transcripts for each scheduler mode;
- transcript identity records;
- self-test, generation, and verification command results;
- generated schema, bundle, manifest, and qualification files;
- SHA-256 records for generated command outputs.

The workflow retention setting is `90` days.

## Stable workflow completion records

Registered-target workflow:

```
Manual main-branch boundary: PASS
Exact M31/M32 source identities: PASS
FRP M32 Verilator lint: PASS
FRP M32 deterministic synthesis profiles: PASS
FRP M32 registered-target bounded proofs: PASS
FRP M32 deterministic replays: PASS
FRP M32 scheduler and full traces: PASS
Repository preservation: PASS
```

Deterministic trace-export workflow:

```
Manual main-branch boundary: PASS
Exporter and RTL source identities: PASS
FRP M32 focused exporter tests: PASS
FRP M32 exact deterministic trace replay pairs: PASS
FRP M32 published canonical trace outputs: PASS
FRP M32 canonical trace outputs: PASS
Repository preservation: PASS
```

## Qualification boundary

The recorded M32 qualification establishes:

| Boundary | Recorded state |
|---|---|
| registered-target source identities | `28 / 28 exact` |
| canonical source identities | `29 / 29 exact` |
| registered-target and trace lint tops | `11 / 11 PASS` |
| registered-boundary synthesis profiles | `8`, `16`, and `32` cells, deterministic replay `PASS` |
| bounded registered-target properties | `14` assertions at depth `4`, deterministic replay `PASS` |
| deterministic RTL testbenches | `7`, each `2 / 2` byte-identical |
| scheduler modes | separate `7/1` and `1/7` records `PASS` |
| canonical trace bundle | `33` source ticks and `396` structured records |
| independent exporter tests | `49 / 49 PASS` |
| mutation rejections | `4 / 4 PASS` |
| canonical qualification checks | `38 / 38 PASS` |
| published canonical outputs | `4 / 4` byte-identical with generated outputs |
| repository preservation | `PASS` in both qualification runs |

The M32 implementation boundary is additive over the released
`FRP v3.3.0 / M31` upstream baseline. No release identifier is assigned by
this transcript.

## Evidence links

| Record | Path |
|---|---|
| M32 architecture and boundary | [`README.md`](README.md) |
| exact artifact index | [`ARTIFACTS.md`](ARTIFACTS.md) |
| reproducible execution procedure | [`SIMULATION.md`](SIMULATION.md) |
| registered-target workflow | [`../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) |
| deterministic trace-export workflow | [`../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) |
| bounded formal harness | [`../../formal/m32/frp_m32_registered_target_boundary_formal.sv`](../../formal/m32/frp_m32_registered_target_boundary_formal.sv) |
| trace exporter | [`../../frp_m32_deterministic_rtl_trace_export.py`](../../frp_m32_deterministic_rtl_trace_export.py) |
| independent exporter tests | [`../../tests/test_frp_m32_deterministic_rtl_trace_export.py`](../../tests/test_frp_m32_deterministic_rtl_trace_export.py) |
| trace schema | [`../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json`](../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json) |
| trace bundle | [`../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json`](../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json) |
| manifest | [`../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json`](../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json) |
| qualification | [`../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json`](../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json) |

## Provenance and preservation

The canonical bundle assigns the exact M31/M32 source boundary to the
`upstream_frp_systemverilog_rtl` provenance class. It contains no downstream
Observatory implementation artifact.

Earlier RTL, FPGA, evidence, benchmark, schema, workflow, release, failed-run,
successful-run, and deterministic identity history remains outside this
additive M32 transcript and is not replaced by it.

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany  
ORCID: `0009-0000-0832-9597`
