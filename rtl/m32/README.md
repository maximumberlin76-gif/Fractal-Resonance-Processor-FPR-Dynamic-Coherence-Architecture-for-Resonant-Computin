# FRP M32 Registered-Target and Deterministic RTL Trace Boundary

**SystemVerilog registered-target integration and deterministic trace
publication over the qualified M31 RTL contour**

## Boundary identity

| Field | Value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Milestone | `M32` |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Top-level integration module | `frp_m32_core` |
| Qualified integrated configuration | `8` cells, `2` request lanes |
| Registered-boundary synthesis profiles | `8`, `16`, and `32` cells |
| Scheduler trace modes | `7/1` and `1/7` |
| Canonical ternary notation | `-1/0/1` |
| Trace schema | `frp.m32.deterministic_rtl_trace_bundle.v1` |
| Trace qualification | `38 / 38 PASS` |
| License | Apache-2.0 |

M32 inserts a clocked registered boundary between the phase-derived target
bank and automatic request formation. The phase-derived source target,
registered target, request target, execution target, retained state, and
pending route remain separately observable quantities.

The M32 integration consumes the existing M31 phase-interference, scheduler,
request, pending-route, active-state-`0`, capacity, retained-writeback,
thermal-proxy, and stability modules at their recorded source identities. M32
does not duplicate those modules.

## Execution chain

The automatic phase-derived path is:

```
M31 retained phase dynamics
-> M31 relative-phase interference with local effective gamma
-> M31 phase-to-ternary source target
-> M32 registered target boundary
-> M32 registered request gate
-> M31 deterministic request formation
-> M31 scheduler and request handling
-> M31 pending opposite-polarity routing
-> active state 0
-> M31 capacity control
-> M31 retained writeback
-> M31 invariant, thermal, and stability records
```

The relative-phase term remains:

```
sin(theta_j - theta_i - gamma_effective_i)
```

`gamma_effective_i` is local to cell `i`. The phase word remains an unsigned
32-bit value normalized by modular wrap over one complete turn.

## Architectural separation

| Stage | RTL quantity | Role |
|---|---|---|
| Upstream phase result | `phase_target_source` | phase-derived target bank in the canonical ternary domain |
| Registered boundary | `registered_target_q` | accepted target bank retained across the clock boundary |
| Registered validity | `registered_target_valid_q` | records that an accepted upstream bank has been captured |
| Automatic request formation | `phase_request_target` | targets selected from the registered bank for request lanes |
| Execution request | `execution_request_target` | automatic or external request presented to the execution core |
| Execution target bank | `execution_target_bank` | automatic registered bank or external target bank selected by the request mux |
| Retained execution state | `state_out` | state committed by scheduler, routing, arbitration, and capacity logic |
| Retained pending route | `pending_route_out` | unfinished destination polarity retained after a first route leg |

The following identities are therefore false:

```
phase_target_source == executed state
registered_target_q == executed state
request target == retained writeback
phase-order record == coherence-capacity record
```

Each equality may occur for a particular sample, but none is an architectural
identity.

## Registered-target capture

`frp_m32_registered_target_boundary` accepts a source bank only when all of
the following are true:

```
tick_enable
&& phase_target_valid
&& phase_target_domain_valid
```

Every cell symbol is checked against the canonical encodings for `-1`, `0`,
and `1`. A reserved encoding rejects the complete capture transaction. A
rejected or disabled capture retains the previously registered bank and its
validity state.

Reset initializes every registered target cell to active state `0` and clears
the validity bit. The validity bit records accepted upstream capture history;
it does not change the active meaning of state `0`.

The boundary exposes independent, saturating counters for accepted and
rejected capture events. `clear_counters` clears these counters without
replacing the retained registered target bank.

## Registered request formation

`frp_m32_registered_target_request_path` enables automatic requests only when:

```
auto_target_enable
&& registered_target_valid_q
&& registered_target_domain_valid
```

The inherited request adapter receives the registered target together with
the current retained state, pending-route bank, and scheduler state. An
unregistered phase-derived source cannot form an automatic request or bypass
the clocked target boundary.

When `auto_target_enable` is clear, `frp_m32_core` selects the explicit
external request lanes and external target bank. The automatic registered path
and the explicit external path remain separate inputs to the execution mux.

## Active state `0` and route legs

State `0` is retained and executable. Within the M32 trace boundary it is
recorded in its mediation, balancing, routing, damping, transition-staging,
retained-state, pending-route, and controlled-neutralization roles.

Direct opposite-polarity retained transitions are excluded:

```
-1 -> 1
1 -> -1
```

The required routes are:

```
-1 -> 0 -> 1
1 -> 0 -> -1
```

The first route leg commits active state `0` and retains the requested
destination in `pending_route_out`. The second route leg commits that retained
destination on a later eligible tick and clears the pending route. The trace
monitor records `first_route_leg` and `second_route_leg` independently.

## Scheduler-specific trace records

The two cadence modes have separate testbenches, transcripts, structured
records, and replay identities.

| Record | Mode `7/1` | Mode `1/7` |
|---|---:|---:|
| Source ticks | `16` | `17` |
| Cadence counts | `14 balance / 2 commit` | `3 excite / 14 neutralize` |
| Sample records | `16` | `17` |
| Packed-bank records | `16` | `17` |
| Per-cell records | `128` | `136` |
| Request-lane records | `32` | `34` |
| Total structured records | `192` | `204` |
| Active-state-`0` cell observations | `115` | `123` |
| First route leg | source tick `9`, cell `0` | source tick `10`, cell `0` |
| Second route leg | source tick `15`, cell `0` | source tick `16`, cell `0` |

The combined canonical bundle contains:

```
33 source ticks
33 sample records
33 packed-bank records
264 per-cell records
66 request-lane records
396 structured records
```

## Trace record classes

`frp_m32_trace_monitor` emits four record classes for every enabled source
tick.

| Prefix | Cardinality per tick | Recorded boundary |
|---|---:|---|
| `M32_TRACE_SAMPLE` | `1` | scheduler state, capture state, counters, capacity, invariants, phase-order, thermal, and stability telemetry |
| `M32_TRACE_BANK` | `1` | packed source, registered, execution, retained, pending-route, acceptance, and route-leg banks |
| `M32_TRACE_CELL` | `8` | cell coordinates, phase, retained frequency, local effective gamma, interference contribution, targets, retained state, active state `0`, and route state |
| `M32_TRACE_REQUEST` | `2` | request-lane coordinates, automatic and execution request values, and acceptance state |

The exporter parses these records without replacing their source coordinates.
It preserves source transcript identities and produces canonical JSON with
deterministic key ordering and serialization.

## RTL and formal artifacts

| Path | Role |
|---|---|
| [`frp_m32_registered_target_boundary.sv`](frp_m32_registered_target_boundary.sv) | clocked target capture, domain checks, and capture counters |
| [`frp_m32_registered_target_boundary_tb.sv`](frp_m32_registered_target_boundary_tb.sv) | deterministic boundary testbench |
| [`frp_m32_registered_target_request_path.sv`](frp_m32_registered_target_request_path.sv) | registered target to automatic request formation |
| [`frp_m32_registered_target_request_path_tb.sv`](frp_m32_registered_target_request_path_tb.sv) | deterministic request-path testbench |
| [`frp_m32_core.sv`](frp_m32_core.sv) | integrated M32 top-level over the M31 RTL contour |
| [`frp_m32_core_tb.sv`](frp_m32_core_tb.sv) | integrated registered-target execution testbench |
| [`frp_m32_mode_7_1_tb.sv`](frp_m32_mode_7_1_tb.sv) | scheduler mode `7/1` execution testbench |
| [`frp_m32_mode_1_7_tb.sv`](frp_m32_mode_1_7_tb.sv) | scheduler mode `1/7` execution testbench |
| [`frp_m32_trace_monitor.sv`](frp_m32_trace_monitor.sv) | deterministic structured trace monitor |
| [`frp_m32_mode_7_1_trace_tb.sv`](frp_m32_mode_7_1_trace_tb.sv) | full mode `7/1` trace wrapper |
| [`frp_m32_mode_1_7_trace_tb.sv`](frp_m32_mode_1_7_trace_tb.sv) | full mode `1/7` trace wrapper |
| [`../../formal/m32/frp_m32_registered_target_boundary_formal.sv`](../../formal/m32/frp_m32_registered_target_boundary_formal.sv) | bounded safety and capture-sequence harnesses |

## Formal, synthesis, and simulation qualification

The registered-target workflow records the following qualification scope:

| Operation | Recorded result |
|---|---|
| Exact implementation identities | `28` RTL and formal source files |
| Verilator lint | M31/M32 integrated and trace contours `PASS` |
| Registered-boundary synthesis | deterministic `8`, `16`, and `32` cell profiles |
| Safety harness | `10` assertions, depth `4`, `2/2` deterministic replays |
| Capture-sequence harness | `4` assertions, depth `4`, `2/2` deterministic replays |
| Boundary execution | `2/2` deterministic executions |
| Request-path execution | `2/2` deterministic executions |
| Integrated core execution | `2/2` deterministic executions |
| Mode `7/1` execution | `2/2` deterministic executions |
| Mode `1/7` execution | `2/2` deterministic executions |
| Mode `7/1` full trace | `2/2` byte-identical executions |
| Mode `1/7` full trace | `2/2` byte-identical executions |

The synthesis records in this boundary apply to
`frp_m32_registered_target_boundary` for the three listed cell profiles. The
integrated `frp_m32_core` is compiled, linted, simulated, and traced by the
current M32 workflows.

## Canonical publication artifacts

| Record | Repository path |
|---|---|
| Trace schema | [`../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json`](../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json) |
| Trace bundle | [`../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json`](../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json) |
| Manifest | [`../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json`](../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json) |
| Qualification | [`../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json`](../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json) |
| Exporter | [`../../frp_m32_deterministic_rtl_trace_export.py`](../../frp_m32_deterministic_rtl_trace_export.py) |
| Independent exporter tests | [`../../tests/test_frp_m32_deterministic_rtl_trace_export.py`](../../tests/test_frp_m32_deterministic_rtl_trace_export.py) |

The canonical bundle records `29` source identities: `28` RTL and formal
source files plus the registered-target workflow. The manifest records exact
paths, byte lengths, and SHA-256 identities for the schema and trace bundle.
The qualification record references the schema, bundle, and manifest and
records `38 / 38 PASS`. The export workflow also compares all four generated
outputs byte-for-byte with their tracked repository counterparts.

## Workflows

| Workflow | Scope |
|---|---|
| [`FRP M32 Registered Target Core`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) | source identities, lint, registered-boundary synthesis, bounded proofs, deterministic simulations, scheduler traces, and uploaded records |
| [`FRP M32 Deterministic RTL Trace Export`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) | transcript replay, exporter tests, canonical generation, schema validation, mutation rejection, published-artifact comparison, and uploaded records |

Both workflows use `workflow_dispatch` and are executed manually on `main`.

## Provenance boundary

The canonical bundle assigns the M32 sources and their inherited M31 RTL
dependencies to the `upstream_frp_systemverilog_rtl` provenance class. The
bundle does not contain downstream Observatory implementation artifacts.

The M32 layer is additive. It retains all earlier RTL, FPGA, evidence,
benchmark, schema, workflow, release, and deterministic identity records at
their established repository paths.

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany  
ORCID: `0009-0000-0832-9597`
