# FRP M31 RTL Simulation

## Release Identity

| Field | Value |
|---|---|
| Processor | `FRP — Ternary Fractal Resonant Coherence Processor` |
| Repository release | `FRP v3.3.0` |
| Milestone | `M31 — RTL Core Realization and Execution Semantics Package` |
| RTL directory | `rtl/m31/` |
| Qualification status | `PASS` |

## Simulation Boundaries

M31 provides two deterministic SystemVerilog qualification boundaries.

| Boundary | Source | Top module | Scope |
|---|---|---|---|
| Execution semantics | `rtl/m31/frp_m31_execution_tb.sv` | `frp_m31_execution_tb` | scheduler, request lanes, pending routes, state-`0` routing, capacity, retained writeback, counters, and execution invariants |
| Complete processor contour | `rtl/m31/frp_m31_tb.sv` | `frp_m31_tb` | retained phase, relative-phase interference, coherence, resonance target, ternary execution, thermal proxy, and stability |

Both simulations are compiled and executed from the repository root. This
working-directory boundary resolves:

- the `rtl/m31` include path;
- the default sine-table path `rtl/m31/frp_m31_sin_q30.mem`;
- the complete source hierarchy beneath each top module.

## Toolchain

The qualified simulation path uses:

- Verilator with SystemVerilog support;
- timing execution;
- SystemVerilog assertion execution;
- generated C++20 simulation executables;
- a C++ compiler supported by Verilator.

Inspect the installed versions:

```
verilator --version
g++ --version
```

The repository qualification workflow uses Python 3.12 for the focused M31
evidence suite and Verilator for the RTL boundaries.

## Source and LUT Preflight

Run from the repository root:

```
set -euo pipefail

test -f rtl/m31/frp_m31_execution_tb.sv
test -f rtl/m31/frp_m31_tb.sv
test -f rtl/m31/frp_m31_sin_q30.mem
test "$(wc -l < rtl/m31/frp_m31_sin_q30.mem)" -eq 4096
test "$(wc -c < rtl/m31/frp_m31_sin_q30.mem)" -eq 36864
test "$(sha256sum rtl/m31/frp_m31_sin_q30.mem | cut -d' ' -f1)" = \
  "adbb4b94fcf8fa0bfc981d654679fd7518a5c4c9c97b611a35cd8accaf28233d"
```

The sine memory contains 4096 signed Q30 entries. The upper twelve bits of each
32-bit modular phase word select the lookup address.

## Execution-Semantics Simulation

### Build and Log Paths

| Record | Path |
|---|---|
| Verilator object directory | `/tmp/frp-m31-execution-obj` |
| Generated executable | `/tmp/frp-m31-execution-obj/Vfrp_m31_execution_tb` |
| Runtime log | `/tmp/m31e1-execution.log` |

### Lint

```
verilator \
  --lint-only \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  --top-module frp_m31_execution_tb \
  -Irtl/m31 \
  rtl/m31/frp_m31_execution_tb.sv
```

### Build

```
rm -rf /tmp/frp-m31-execution-obj

verilator \
  --binary \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  -CFLAGS "-std=c++20" \
  --top-module frp_m31_execution_tb \
  --Mdir /tmp/frp-m31-execution-obj \
  -Irtl/m31 \
  rtl/m31/frp_m31_execution_tb.sv

test -x /tmp/frp-m31-execution-obj/Vfrp_m31_execution_tb
```

### Execute

```
/tmp/frp-m31-execution-obj/Vfrp_m31_execution_tb \
  2>&1 | tee /tmp/m31e1-execution.log
```

### Validate

```
grep -Fqx "FRP M31 deterministic RTL testbench completed." \
  /tmp/m31e1-execution.log
grep -Fqx "CELLS=8 REQUEST_LANES=2" \
  /tmp/m31e1-execution.log
grep -Fqx "ticks_recorded=16" \
  /tmp/m31e1-execution.log
grep -Fqx "actual_direct_events=0" \
  /tmp/m31e1-execution.log
grep -Fqx "reserved_state_events=0" \
  /tmp/m31e1-execution.log
grep -Fqx "queue_overflow_events=0" \
  /tmp/m31e1-execution.log
```

## Complete-Contour Simulation

### Build and Log Paths

| Record | Path |
|---|---|
| Verilator object directory | `/tmp/frp-m31-complete-obj` |
| Generated executable | `/tmp/frp-m31-complete-obj/Vfrp_m31_tb` |
| Runtime log | `/tmp/m31e1-complete.log` |

### Lint

```
verilator \
  --lint-only \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  --top-module frp_m31_tb \
  -Irtl/m31 \
  rtl/m31/frp_m31_tb.sv
```

### Build

```
rm -rf /tmp/frp-m31-complete-obj

verilator \
  --binary \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  -CFLAGS "-std=c++20" \
  --top-module frp_m31_tb \
  --Mdir /tmp/frp-m31-complete-obj \
  -Irtl/m31 \
  rtl/m31/frp_m31_tb.sv

test -x /tmp/frp-m31-complete-obj/Vfrp_m31_tb
```

### Execute

```
/tmp/frp-m31-complete-obj/Vfrp_m31_tb \
  2>&1 | tee /tmp/m31e1-complete.log
```

### Validate

```
grep -Fqx "FRP_M31_COMPLETE_RTL: PASS" \
  /tmp/m31e1-complete.log
grep -Fqx \
  "phase/coherence/resonance/active-zero/thermal/stability: PASS" \
  /tmp/m31e1-complete.log
```

## Complete Reproduction Sequence

The following sequence reproduces both qualified RTL boundaries and validates
their stable terminal records:

```
set -euo pipefail

test -f rtl/m31/frp_m31_execution_tb.sv
test -f rtl/m31/frp_m31_tb.sv
test -f rtl/m31/frp_m31_sin_q30.mem
test "$(wc -l < rtl/m31/frp_m31_sin_q30.mem)" -eq 4096
test "$(sha256sum rtl/m31/frp_m31_sin_q30.mem | cut -d' ' -f1)" = \
  "adbb4b94fcf8fa0bfc981d654679fd7518a5c4c9c97b611a35cd8accaf28233d"

rm -rf /tmp/frp-m31-execution-obj
rm -rf /tmp/frp-m31-complete-obj
rm -f /tmp/m31e1-execution.log
rm -f /tmp/m31e1-complete.log

verilator \
  --lint-only \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  --top-module frp_m31_execution_tb \
  -Irtl/m31 \
  rtl/m31/frp_m31_execution_tb.sv

verilator \
  --binary \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  -CFLAGS "-std=c++20" \
  --top-module frp_m31_execution_tb \
  --Mdir /tmp/frp-m31-execution-obj \
  -Irtl/m31 \
  rtl/m31/frp_m31_execution_tb.sv

/tmp/frp-m31-execution-obj/Vfrp_m31_execution_tb \
  2>&1 | tee /tmp/m31e1-execution.log

grep -Fqx "FRP M31 deterministic RTL testbench completed." \
  /tmp/m31e1-execution.log
grep -Fqx "CELLS=8 REQUEST_LANES=2" \
  /tmp/m31e1-execution.log
grep -Fqx "ticks_recorded=16" \
  /tmp/m31e1-execution.log
grep -Fqx "actual_direct_events=0" \
  /tmp/m31e1-execution.log
grep -Fqx "reserved_state_events=0" \
  /tmp/m31e1-execution.log
grep -Fqx "queue_overflow_events=0" \
  /tmp/m31e1-execution.log

verilator \
  --lint-only \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  --top-module frp_m31_tb \
  -Irtl/m31 \
  rtl/m31/frp_m31_tb.sv

verilator \
  --binary \
  --sv \
  --timing \
  --assert \
  -Wall \
  -Wno-fatal \
  -CFLAGS "-std=c++20" \
  --top-module frp_m31_tb \
  --Mdir /tmp/frp-m31-complete-obj \
  -Irtl/m31 \
  rtl/m31/frp_m31_tb.sv

/tmp/frp-m31-complete-obj/Vfrp_m31_tb \
  2>&1 | tee /tmp/m31e1-complete.log

grep -Fqx "FRP_M31_COMPLETE_RTL: PASS" \
  /tmp/m31e1-complete.log
grep -Fqx \
  "phase/coherence/resonance/active-zero/thermal/stability: PASS" \
  /tmp/m31e1-complete.log
```

## Qualified Configuration

Both testbenches use the same retained-state capacity profile:

| Parameter | Value |
|---|---:|
| `CELLS` | `8` |
| ternary state width | `2` bits |
| `REQUEST_LANES` | `2` |
| cell-index width | `3` bits |
| counter width | `32` bits |
| transition fraction | `1/4 = 0.25` |

The request-lane relation is:

`REQUEST_LANES = max(1, round(CELLS × 0.25))`

For eight retained cells:

`REQUEST_LANES = 2`

## Clock and Reset

Both testbenches declare `timescale 1ns / 1ps` and toggle the clock every five
time units.

| Clock property | Value |
|---|---:|
| half period | `5 ns` |
| full period | `10 ns` |
| frequency | `100 MHz` |

Reset drives every retained cell and every pending-route slot to state `0`.
State `0` is the computational balancing, damping, mediation, routing,
transition-buffering, switching-load-distribution, and stabilization state of
the `-1/0/1` processor domain.

## Execution-Semantics Qualification

`frp_m31_execution_tb` independently exercises the retained ternary execution
chain.

| Scheduler profile | Enabled ticks | Exact state counts |
|---|---:|---|
| `free` | `16` | `free = 16` |
| `7/1` | `64` | `balance = 56`, `commit = 8` |
| `1/7` | `16` | `excite = 2`, `neutralize = 14` |

The simulation verifies:

- canonical state encoding `-1/0/1`;
- deterministic ascending request-lane arbitration;
- one accepted request per cell per tick;
- two accepted state changes at the qualified eight-cell capacity boundary;
- pending-route completion priority;
- retained pending polarity during scheduler and capacity deferral;
- separate-tick routes `-1 → 0 → 1` and `1 → 0 → -1`;
- counter clearing with retained state and pending routes preserved;
- `accepted_changes <= REQUEST_LANES`;
- `capacity_remaining = REQUEST_LANES - accepted_changes`;
- `capacity_exhausted = (accepted_changes == REQUEST_LANES)`;
- `switch_load_numerator = accepted_changes`;
- all ten integrated execution invariant flags asserted;
- `actual_direct_events = 0`;
- `reserved_state_events = 0`;
- `queue_overflow_events = 0`.

The terminal `ticks_recorded=16` belongs to the final `1/7` qualification
profile.

## Complete-Contour Qualification

`frp_m31_tb` exercises the full retained-phase and ternary processor contour.

Initial per-cell inputs are:

| Input | Exact value |
|---|---|
| frequency | `FRP_M31_BASE_FREQUENCY_Q16 = 65536` |
| effective gamma | `FRP_M31_GAMMA_NOMINAL = 644245094` |
| thermal node factor | `FRP_M31_Q30_ONE = 1073741824` |
| scheduler mode | `FRP_MODE_FREE` |

The deterministic sequence then verifies:

1. reset establishes retained state `0` and empty pending-route state for all eight cells;
2. phase word `0x40000000` produces Q30 projection `1` and ternary target `1`;
3. phase word `0xC0000000` produces Q30 projection `-1` and ternary target `-1`;
4. the relative-phase coupling field is populated;
5. automatic target execution commits `0 → 1` and `0 → -1` for the qualified cells;
6. a changed opposite-polarity phase target commits `1 → 0` and retains pending target `-1`;
7. the following eligible tick completes `0 → -1` and clears the pending route;
8. the normalized common-RC thermal proxy integrates accepted switching activity;
9. the qualified contour retains a positive stability margin and asserts `stable`;
10. all ten execution invariant flags remain asserted;
11. the integrated tick count closes at `3`;
12. direct-transition, reserved-state, and queue-overflow counters remain zero.

## Assertion Boundaries

Assertion execution is enabled by `--assert`.

`frp_m31_assertions` covers:

- retained-state and pending-route encoding;
- reset and disabled-tick retention;
- scheduler mode, state, period, and counter relations;
- request acceptance and rejection separation;
- deterministic lane and cell ownership;
- pending-route creation, retention, completion, and clearing;
- state-`0` mediation of opposite-polarity transitions;
- transition-capacity admission;
- retained-state writeback authorization;
- switch-load accounting;
- zero direct, reserved-state, and queue-overflow events;
- the ten-bit integrated invariant set.

`frp_m31_phase_thermal_assertions` covers:

- the retained `-1/0/1` state domain;
- positive, zero-band, and negative phase-target mapping;
- pair, cluster, and global coherence within the closed Q30 unit interval;
- organization dispersion within the closed Q30 unit interval;
- nonnegative normalized thermal-proxy values;
- peak thermal proxy greater than or equal to the current proxy;
- absence of direct opposite-polarity retained-state writeback;
- zero direct, reserved-state, and queue-overflow counters.

## Stable Terminal Records

Execution-semantics record:

```
FRP M31 deterministic RTL testbench completed.
CELLS=8 REQUEST_LANES=2
ticks_recorded=16
actual_direct_events=0
reserved_state_events=0
queue_overflow_events=0
```

Complete-contour record:

```
FRP_M31_COMPLETE_RTL: PASS
phase/coherence/resonance/active-zero/thermal/stability: PASS
```

## Evidence and Procedure Records

| Record | Path |
|---|---|
| M31 RTL specification | [`README.md`](README.md) |
| exact M31 RTL artifact manifest | [`ARTIFACTS.md`](ARTIFACTS.md) |
| M31 validation index | [`FRP_VALIDATION_INDEX_v3_3_0.md`](../../FRP_VALIDATION_INDEX_v3_3_0.md) |
| M31 test report | [`TEST_REPORT_v3_3_0.md`](../../TEST_REPORT_v3_3_0.md) |
| complete RTL qualification workflow | [`.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml`](../../.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml) |

The workflow executes the focused `60 / 60 PASS` M31 evidence suite before the
two RTL qualification boundaries and verifies preservation of the historical
evidence, benchmark, schema, FPGA, RTL, validation, release, and test-report
records.

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany
