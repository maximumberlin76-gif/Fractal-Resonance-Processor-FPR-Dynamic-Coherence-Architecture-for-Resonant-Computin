# FRP M31 Complete RTL Core

**SystemVerilog realization of the Ternary Fractal Resonant Coherence Processor**

## Release identity

| Field | Value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Processor | `Ternary Fractal Resonant Coherence Processor` |
| Version | `FRP v3.3.0` |
| Milestone | `M31 — RTL Core Realization and Execution Semantics Package` |
| Top-level RTL module | `frp_m31_core` |
| Qualified configuration | `8` cells, `2` request lanes |
| Language | SystemVerilog |
| Qualification | `PASS` |
| License | Apache-2.0 |

This directory contains the complete M31 RTL realization of the FRP core. It
connects retained relative-phase interference, hierarchical coupling,
phase-derived balanced-ternary targets, deterministic temporal scheduling,
request arbitration, neutral-mediated polarity transitions, retained pending
routes, bounded transition activity, a normalized thermal proxy, and an
operational stability projection.

The implementation is stateful. Phase, delayed frequency, balanced-ternary
state, unfinished polarity routes, scheduler position, thermal-proxy state, and
architectural counters are retained from one enabled processor tick to the
next.

## Core computation

The complete M31 RTL computation is:

`retained phase and delayed frequency`

→ `thermally weighted hierarchical relative-phase interference`

→ `phase velocity and wrapped phase evolution`

→ `pair, cluster, and global phase-order measurement`

→ `phase-to-balanced-ternary qualification`

→ `temporal scheduler and deterministic request selection`

→ `neutral-mediated retained-state transition`

→ `per-tick transition-capacity admission`

→ `retained state and pending-route writeback`

→ `normalized thermal and stability observables`

The phase-derived target and the retained executed state are separate
architectural quantities. A new target becomes retained state only when the
scheduler, pending-route ownership, arbitration, transition topology, and
capacity conditions admit it.

## 1. State-space formalism

For the qualified eight-cell core, let the retained state at tick `n` be:

```
X[n] = {
  theta_i[n],
  omega_i[n],
  q_i[n],
  p_i[n],
  scheduler_mode[n],
  scheduler_position[n],
  tau[n],
  counters[n]
}
```

for cell indexes:

```
i in {0, 1, ..., 7}
```

where:

| Symbol | RTL quantity | Meaning |
|---|---|---|
| `theta_i[n]` | `phase_word_q` | retained phase of cell `i` |
| `omega_i[n]` | `frequency_current_q16` | retained delayed frequency |
| `q_i[n]` | `state_out` | retained balanced-ternary processor state |
| `p_i[n]` | `pending_route_out` | retained unfinished opposite-polarity target |
| `tau[n]` | `temperature_proxy_q16` | normalized common-RC comparative thermal proxy |
| `scheduler_position[n]` | `scheduler_state_q` and internal period index | temporal transition-eligibility state |

The tick input includes external per-cell effective phase lag and thermal
coupling factors, the selected scheduler mode, and either phase-derived or
explicit balanced-ternary requests:

```
U[n] = {
  gamma_i[n],
  T_i[n],
  scheduler_mode,
  automatic_or_external_requests,
  control_inputs
}
```

The enabled tick transition is:

```
X[n + 1] = F_M31(X[n], U[n])
```

When `tick_enable = 0`, retained execution state remains unchanged. A
`phase_load_valid` transaction explicitly loads the phase and frequency banks
independently of the enabled execution tick.

## 2. Numeric representation

M31 uses deterministic integer arithmetic at the RTL boundary.

| Domain | RTL type | Scale |
|---|---|---:|
| scalar fixed point | signed `S32Q16` | `2^16` |
| trigonometric and normalized fixed point | signed `S32Q30` | `2^30` |
| phase | unsigned `PHASE_U32` | `2^32` words per full turn |
| effective phase lag | signed 32-bit phase word | same angular scale as `PHASE_U32` |

Canonical units:

```
Q16_ONE = 65536
Q30_ONE = 1073741824
one complete phase turn = 2^32 phase words
```

Multiplication uses the appropriate fixed-point right shift, round-to-nearest
with half cases away from zero, and signed 32-bit saturation. Phase addition
wraps modulo `2^32`.

The trigonometric implementation uses a committed `4096`-entry Q30 sine
table. The address is the upper twelve bits of the phase word:

```
sin_q30(theta) = sine_lut[theta[31:20]]
cos_q30(theta) = sine_lut[theta[31:20] + 1024 mod 4096]
```

The table anchors are qualified exactly:

| Index | Value |
|---:|---:|
| `0` | `0` |
| `1024` | `1073741824` |
| `2048` | `0` |
| `3072` | `-1073741824` |

## 3. Continuous phase foundation

The RTL phase path is a deterministic fixed-point projection of the weighted
Kuramoto-Sakaguchi relation:

```
d theta_i / dt =
  omega_i
  + K * sum_(j != i) W_ij * T_i * T_j
      * sin(theta_j - theta_i - gamma_i)
  + u_i
```

where:

| Symbol | Meaning |
|---|---|
| `theta_i` | phase of cell `i` |
| `omega_i` | retained local frequency |
| `K` | nominal coupling strength |
| `W_ij` | hierarchical topology weight |
| `T_i`, `T_j` | externally supplied local thermal coupling factors |
| `gamma_i` | externally supplied effective Sakaguchi phase lag |
| `u_i` | scheduler-dependent phase contribution |

The interaction depends on relative phase rather than independent scalar
addition of cell outputs.

## 4. Hierarchical relative-phase interference

For cell indexes `i` and `j`, M31 uses the dyadic hierarchy:

```
d(i, j) = bit_length(i XOR j)
```

For the qualified eight-cell topology, the exact Q30 shell weights are:

| Distance | Shell population | Exact Q30 weight | Real-valued interpretation |
|---:|---:|---:|---:|
| `1` | `1` | `516461574` | `0.4809923228` |
| `2` | `2` | `158959695` | `0.1480427524` |
| `3` | `4` | `59840215` | `0.0557305431` |

The weighted shell sum closes exactly to Q30 unity:

```
516461574 + 2 * 158959695 + 4 * 59840215
= 1073741824
= Q30_ONE
```

For each ordered pair `i != j`, define the exact fixed-point pair factor:

```
A_ij[n] = mul_q30(T_i[n], T_j[n])
B_ij[n] = mul_q30(W_d(i,j), A_ij[n])
J_ij[n] = mul_q30(
  B_ij[n],
  sin_q30(theta_j[n] - theta_i[n] - gamma_i[n])
)
```

The cell coupling field is:

```
I_i[n] = mul_q16(
  K_nominal_q16,
  q30_to_q16(sat_s32(sum_(j != i) J_ij[n]))
)
```

with:

```
K_nominal_q16 = 18350
K_nominal_q16 / 2^16 = 0.279998779296875
```

The nominal phase-lag constant is:

```
gamma_nominal_word = 644245094
= 0.15 turn
= 0.30 * pi radians
```

The top-level core accepts `gamma_effective_word` and
`thermal_node_factor_q30` as explicit per-cell inputs. The internal normalized
thermal proxy remains a separate architectural observable.

## 5. Retained frequency and phase evolution

Define:

```
nonzero_i[n] = 1, when q_i[n] is -1 or 1
nonzero_i[n] = 0, when q_i[n] is 0

switch_i[n] = 1, when the cell has an admitted state change on tick n
switch_i[n] = 0, otherwise
```

The frequency target is:

```
omega_target_i[n] =
  1.0
  + 0.06 * nonzero_i[n]
  + 0.12 * switch_i[n]
```

The exact Q16 constants are:

| Term | Exact Q16 | Real-valued interpretation |
|---|---:|---:|
| base frequency | `65536` | `1.0` |
| nonzero-state gain | `3932` | `0.0599975586` |
| switching gain | `7864` | `0.1199951172` |
| delay coefficient | `19661` | `0.3000030518` |

The delayed frequency update is:

```
omega_i[n + 1] =
  omega_i[n]
  + alpha * (omega_target_i[n] - omega_i[n])

alpha_q16 = 19661
```

The scheduler phase contribution is:

| Scheduler state | Exact Q16 push | Real-valued interpretation |
|---|---:|---:|
| `free` | `197` | `0.0030059814` |
| `balance` | `197` | `0.0030059814` |
| `commit` | `655` | `0.0099945068` |
| `excite` | `393` | `0.0059967041` |
| `neutralize` | `197` | `0.0030059814` |

The phase velocity is:

```
v_i[n] =
  mul_q16(3932, omega_i[n + 1])
  + scheduler_push[n]
  + I_i[n]
```

The Q16 radian velocity is converted to a phase word by the exact rounded
integer transform implemented in `frp_m31_velocity_to_phase_word`:

```
delta_theta_word_i[n] =
  round_away_from_zero(
    velocity_q16_i[n] * 44798133900177 / 2^32
  )
```

The retained phase update is:

```
theta_i[n + 1] =
  (theta_i[n] + delta_theta_word_i[n]) mod 2^32
```

## 6. Phase-order observables

For any cell group `G`, M31 evaluates the phase-order magnitude:

```
R_G[n] = sqrt(
  mean_(i in G)(cos(theta_i[n]))^2
  + mean_(i in G)(sin(theta_i[n]))^2
)
```

The RTL computes this with Q30 means and an integer square root.

The qualified hierarchy is:

| Output | Groups | Definition |
|---|---|---|
| `pair_coherence_q30` | `(0,1)`, `(2,3)`, `(4,5)`, `(6,7)` | mean of four pair phase-order magnitudes |
| `cluster_coherence_q30` | `(0..3)`, `(4..7)` | mean of two four-cell phase-order magnitudes |
| `global_coherence_q30` | `(0..7)` | eight-cell phase-order magnitude |
| `organization_dispersion_q30` | two four-cell clusters | half the absolute difference between cluster magnitudes |

The signal names contain `coherence` for interface continuity. These outputs
record phase-order magnitudes. Complete phase-and-amplitude coherence remains
a separate measurement domain.

## 7. Phase-to-balanced-ternary qualification

The phase projection is:

```
y_i[n] = sin(theta_i[n])
```

The exact threshold is:

```
h_q30 = 354334802
h_q30 / 2^30 = 0.3300000000745058
```

The phase-derived target is:

```
                 1, when y_i[n] > h
t_i[n] =         0, when -h <= y_i[n] <= h
                -1, when y_i[n] < -h
```

The target is a discrete qualification of the retained phase projection. The
target and the full retained phase remain separate processor variables.

## 8. Balanced-ternary retained-state domain

The retained processor-state domain is:

```
T = {-1, 0, 1}
```

Canonical notation:

```
-1/0/1
```

Canonical two-bit encoding:

| Semantic state | Encoding | Architectural meaning |
|---:|---:|---|
| `-1` | `2'b11` | retained negative polarity |
| `0` | `2'b00` | retained active state for balancing, routing, damping, mediation, transition staging, retention, and controlled neutralization |
| `1` | `2'b01` | retained positive polarity |
| reserved | `2'b10` | reserved encoding excluded from retained state |

### Active state `0`

State `0` is a stored and executable processor state. It participates in phase
qualification, scheduling, transition routing, retained-state writeback,
pending-route completion, load distribution, and stability evaluation.

State `0` has six explicit RTL roles:

1. **Phase qualification:** it is selected when the phase projection lies in
   the central interval `[-h, h]`.
2. **Reset state:** every retained cell starts in state `0`.
3. **Polarity mediation:** an opposite-polarity request enters state `0` before
   reaching its requested polarity.
4. **Pending-route boundary:** retained pending polarity completes from state
   `0`.
5. **Temporal load distribution:** the two transition legs consume capacity on
   separate eligible ticks.
6. **Stability contribution:** the retained fraction of cells in state `0`
   contributes directly to `coherence_capacity_q16`.

The architectural functions of state `0` are therefore:

- active balancing;
- routing;
- damping;
- mediation;
- transition staging;
- conflict neutralization;
- polarity bridging;
- switching-load distribution;
- retained-state stabilization.

## 9. Neutral-mediated transition topology

The legal adjacent retained-state relation is:

```
A = {
  (-1, -1), (-1, 0),
  ( 0, -1), ( 0, 0), (0, 1),
  ( 1,  0), ( 1, 1)
}
```

Direct opposite-polarity writebacks are excluded:

```
(-1, 1)
(1, -1)
```

Every opposite-polarity request is decomposed into two retained state changes:

```
-1 -> 0 -> 1
1 -> 0 -> -1
```

Let `q_i[n]` be the retained state, `t_i[n]` the selected target, and `p_i[n]`
the retained pending route. Before capacity admission, the transition
candidate is:

```
q_candidate_i[n] =
  p_i[n],  when q_i[n] = 0, p_i[n] in {-1, 1},
              and the scheduler is commit-capable;

  q_i[n],  when q_i[n] = t_i[n];

  t_i[n],  when q_i[n] = 0, t_i[n] in {-1, 1},
              and the scheduler is commit-capable;

  0,       when q_i[n] in {-1, 1}, t_i[n] = 0,
              and the scheduler is neutralize-capable;

  0,       when q_i[n] and t_i[n] are opposite polarities,
              and the scheduler is neutralize-capable;

  q_i[n],  otherwise.
```

For an admitted opposite-polarity first leg:

```
q_i[n + 1] = 0
p_i[n + 1] = t_i[n]
```

For an admitted pending-route completion on a later eligible tick:

```
q_i[n] = 0
p_i[n] in {-1, 1}

q_i[n + 1] = p_i[n]
p_i[n + 1] = 0
```

Scheduler or capacity deferral retains the current state and pending polarity.
A pending route owns its cell until completion and excludes a new request from
overwriting that route.

## 10. Temporal scheduler

The scheduler is a transition-eligibility operator.

| Scheduler state | Commit-capable | Neutralize-capable |
|---|:---:|:---:|
| `free` | yes | yes |
| `balance` | no | yes |
| `commit` | yes | no |
| `excite` | yes | no |
| `neutralize` | no | yes |

Eligibility by transition class:

| Transition class | Required scheduler capability |
|---|---|
| same-state retention | any valid scheduler state |
| `0 -> -1` or `0 -> 1` | commit-capable |
| pending completion `0 -> p_i` | commit-capable |
| `-1 -> 0` or `1 -> 0` | neutralize-capable |
| opposite-polarity first leg into `0` | neutralize-capable |

The three scheduler modes are:

### `free`

Every enabled tick is commit-capable and neutralize-capable.

### `7/1`

The repeating eight-tick sequence is:

```
balance, balance, balance, balance,
balance, balance, balance, commit
```

### `1/7`

The repeating eight-tick sequence is:

```
excite, neutralize, neutralize, neutralize,
neutralize, neutralize, neutralize, neutralize
```

The scheduler counter invariant is:

```
free_count
+ balance_count
+ commit_count
+ excite_count
+ neutralize_count
= ticks_recorded
```

## 11. Deterministic arbitration and transition capacity

The transition fraction is:

```
rho = 1 / 4
```

The request-lane and per-tick state-change limit is:

```
M(N) = max(1, round(N * rho))
```

Qualified profiles:

| Cells | Request lanes / maximum changes per tick |
|---:|---:|
| `8` | `2` |
| `16` | `4` |
| `32` | `8` |

The integrated phase engine is qualified for exactly `8` cells. The
parameterized execution subcore retains the inherited `8`, `16`, and
`32`-cell request-lane relations.

Transition priority is deterministic:

1. eligible pending-route completions in ascending cell order;
2. accepted explicit or phase-derived request lanes in ascending lane order.

Request arbitration evaluates:

- cell-index validity;
- target encoding;
- same-tick duplicate cell ownership;
- retained pending-route ownership;
- scheduler eligibility;
- remaining transition capacity.

Exact capacity relations:

```
accepted_changes[n] <= M
capacity_remaining[n] = M - accepted_changes[n]
capacity_exhausted[n] = (accepted_changes[n] = M)
switch_load_numerator[n] = accepted_changes[n]
switch_load[n] = accepted_changes[n] / N
```

Same-state retention consumes zero transition capacity. Each admitted
state-changing leg consumes one capacity slot. The two legs of an
opposite-polarity route therefore consume capacity on different ticks.

## 12. Normalized thermal proxy

Let:

```
L[n] = accepted_changes[n] / N
```

The M31 common-RC comparative thermal proxy is:

```
tau[n + 1] = d * tau[n] + g * L[n]
```

with exact Q30 coefficients:

| Coefficient | Exact Q30 | Real-valued interpretation |
|---|---:|---:|
| decay `d` | `1020054733` | `0.9500000002` |
| gain `g` | `10737418` | `0.0099999998` |

The implementation retains:

```
tau_peak[n + 1] = max(tau_peak[n], tau[n + 1])
```

and increments a sample counter on every enabled tick.

This signal belongs to the normalized common-RC comparative thermal-proxy
domain. Physical temperature and energy measurements remain separate
measurement classes. The per-cell `thermal_node_factor_q30` and
`gamma_effective_word` values remain explicit top-level inputs.

## 13. Operational stability projection

Define the retained-state-zero fraction:

```
z[n] = count_i(q_i[n] = 0) / N
```

The M31 RTL coherence-capacity projection is:

```
C_RTL[n] =
  0.82
  + 0.34 * R_global[n]
  + 0.16 * R_cluster_mean[n]
  + 0.08 * z[n]
```

The exact Q16 coefficients are:

| Term | Exact Q16 | Real-valued interpretation |
|---|---:|---:|
| base capacity | `53740` | `0.8200073242` |
| global phase-order gain | `22282` | `0.3399963379` |
| cluster phase-order gain | `10486` | `0.1600036621` |
| state-zero fraction gain | `5243` | `0.0800018311` |

The operational pressure is:

```
P_RTL[n] = tau[n] + L[n]
```

The stability margin and status are:

```
Delta_RTL[n] = C_RTL[n] - P_RTL[n]
stable[n] = (Delta_RTL[n] > 0)
```

`C_RTL`, `P_RTL`, and `Delta_RTL` are fixed-point operational RTL
observables.

## 14. Enabled-tick execution order

For each enabled processor tick, the integrated core performs the following
deterministic operation:

1. Decode the scheduler state for the retained scheduler mode and period.
2. Evaluate the Q30 sine and cosine projections of all retained phases.
3. Evaluate thermally weighted hierarchical relative-phase interference.
4. Form delayed frequency updates and next wrapped phases.
5. Measure pair, cluster, and global phase order and organization dispersion.
6. Quantize every phase projection to a target in `-1/0/1`.
7. Select automatic phase-derived requests or the external request interface.
8. Identify eligible pending-route completions.
9. Arbitrate new requests deterministically.
10. Classify same-state, state-zero entry, state-zero exit,
    opposite-polarity, and pending-completion transitions.
11. Replace every opposite-polarity candidate by its first legal leg into
    retained state `0`.
12. Admit pending completions first, then new state-changing requests, up to
    the per-tick capacity limit.
13. Commit admitted state changes, create or clear pending routes, and retain
    all deferred state.
14. Update phase, delayed frequency, scheduler state, thermal-proxy state, and
    architectural counters on the active clock edge.
15. Re-evaluate the operational stability projection from the new retained
    outputs.

The resulting state is the input state of the next enabled tick.

## 15. Top-level interface

The synthesis and integration boundary is `frp_m31_core`.

### Control and state-loading inputs

| Port | Meaning |
|---|---|
| `clk` | core clock |
| `rst_n` | asynchronous active-low reset |
| `tick_enable` | enables one retained processor transition |
| `clear_counters` | clears architectural counters and the thermal-proxy accumulator, peak, and sample counter |
| `scheduler_mode` | selects `free`, `7/1`, or `1/7` execution |
| `phase_load_valid` | loads the phase and frequency banks |
| `phase_load` | packed per-cell `PHASE_U32` values |
| `frequency_load_q16` | packed per-cell Q16 frequencies |
| `gamma_effective_word` | packed per-cell effective phase-lag words |
| `thermal_node_factor_q30` | packed per-cell Q30 coupling factors |

### Target and request inputs

| Port | Meaning |
|---|---|
| `auto_target_enable` | selects phase-derived request generation |
| `external_request_valid` | packed explicit request-valid lanes |
| `external_request_cell_index` | packed requested cell indexes |
| `external_request_target` | packed explicit ternary targets |
| `external_target_bank` | explicit packed target-state bank |

### Dynamic outputs

| Port group | Meaning |
|---|---|
| `phase_word_q` | retained cell phases |
| `frequency_current_q16` | retained delayed frequencies |
| `coupling_field_q16` | per-cell relative-phase coupling fields |
| `phase_projection_q30` | per-cell sine projections |
| `phase_target` | phase-derived balanced-ternary targets |
| `state_out` | retained balanced-ternary state |
| `pending_route_out` | retained unfinished polarity routes |

### Telemetry outputs

| Port group | Meaning |
|---|---|
| scheduler and tick outputs | temporal execution state |
| accepted-change outputs | admitted transition activity |
| direct/reserved/overflow counters | zero-event safety observables |
| pair/cluster/global outputs | phase-order observables |
| organization dispersion | cluster phase-order separation |
| thermal proxy and peak | normalized comparative thermal state |
| coherence capacity, pressure, margin, stable | operational stability projection |

## 16. RTL source map

| File | Role |
|---|---|
| `frp_m31_fixed_point_pkg.sv` | fixed-point types, constants, saturation, rounding, topology, and phase conversion |
| `frp_m31_pkg.sv` | balanced-ternary encodings, scheduler states, transition classes, capacity profiles, and invariant definitions |
| `frp_m31_scheduler.sv` | retained temporal execution modes and scheduler counters |
| `frp_m31_request_lanes.sv` | deterministic request-lane validation and arbitration |
| `frp_m31_pending_routes.sv` | retained opposite-polarity target storage, ownership, deferral, and clearing |
| `frp_m31_active_neutral.sv` | legal transition-candidate generation and mediation through state `0` |
| `frp_m31_capacity_guard.sv` | pending-first bounded transition admission |
| `frp_m31_state_update.sv` | capacity-approved retained-state writeback |
| `frp_m31_execution_core.sv` | integrated scheduler, request, route, capacity, and retained-state execution subcore |
| `frp_m31_phase_interference.sv` | LUT-based relative-phase coupling, frequency delay, phase evolution, target qualification, and phase-order metrics |
| `frp_m31_phase_request_adapter.sv` | deterministic conversion of phase targets to request lanes |
| `frp_m31_thermal_proxy.sv` | normalized common-RC comparative thermal accumulator |
| `frp_m31_stability.sv` | fixed-point coherence-capacity, pressure, margin, and stable flag |
| `frp_m31_core.sv` | complete integrated M31 top-level core |
| `frp_m31_assertions.sv` | execution-subcore architectural and temporal assertions |
| `frp_m31_phase_thermal_assertions.sv` | integrated phase, target, thermal, and retained-state assertions |
| `frp_m31_execution_tb.sv` | deterministic execution-subcore qualification testbench |
| `frp_m31_tb.sv` | complete integrated-core qualification testbench |
| `frp_m31_sin_q30.mem` | exact 4096-entry signed Q30 sine table |
| `frp_m31.f` | complete top-level source-list entry |

## 17. Architectural invariants

The qualified core preserves:

```
q_i[n] in {-1, 0, 1}
p_i[n] in {-1, 0, 1}
reserved encoding 2'b10 never reaches retained state
direct -1 -> 1 writeback never occurs
direct 1 -> -1 writeback never occurs
pending completion begins only from retained state 0
accepted_changes <= REQUEST_LANES
capacity_remaining = REQUEST_LANES - accepted_changes
switch_load_numerator = accepted_changes
sum(scheduler_state_counts) = ticks_recorded
```

The ten integrated invariant flags are:

| Index | Invariant |
|---:|---|
| `0` | retained ternary state domain is valid |
| `1` | scheduler states and counters are valid |
| `2` | request-lane order is deterministic |
| `3` | pending polarity remains valid and retained |
| `4` | opposite polarity is mediated by state `0` |
| `5` | transition capacity is respected |
| `6` | retained-state writeback matches admission |
| `7` | zero actual direct opposite-polarity events |
| `8` | zero reserved retained-state encodings |
| `9` | zero pending-route queue-overflow events |

Qualification requires all ten flags to be asserted.

## 18. Build and execute

Run commands from the repository root.

Install repository dependencies and Verilator:

```
python -m pip install -r requirements.txt
verilator --version
```

Run the focused M31 publication tests:

```
python -m unittest \
  tests.test_frp_m31_phase_interference_thermal_evidence \
  -v
```

Recorded result:

```
Ran 60 tests
OK
```

Lint the complete RTL core:

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

Build and execute the complete-core qualification:

```
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

/tmp/frp-m31-complete-obj/Vfrp_m31_tb
```

The qualified terminal record is:

```
FRP_M31_COMPLETE_RTL: PASS
phase/coherence/resonance/active-zero/thermal/stability: PASS
```

The retained-state execution subcore uses `frp_m31_execution_tb` and a
separate output directory. Its qualified terminal counters are:

```
FRP M31 deterministic RTL testbench completed.
CELLS=8 REQUEST_LANES=2
ticks_recorded=16
actual_direct_events=0
reserved_state_events=0
queue_overflow_events=0
```

## 19. Qualification and evidence boundary

The complete M31 RTL package was qualified together with the existing M31
publication tests. The RTL qualification verifies:

- phase projection;
- non-empty relative-phase coupling;
- phase-derived target polarity;
- opposite-polarity mediation through state `0`;
- retained pending-route completion;
- thermal-proxy integration;
- positive operational stability in the deterministic testbench;
- zero forbidden events;
- all integrated invariant flags.

Authoritative M31 repository records:

| Record | Link |
|---|---|
| Mathematical foundation | [docs/mathematical_foundation.md](../../docs/mathematical_foundation.md) |
| Core principles | [docs/core_principles.md](../../docs/core_principles.md) |
| M31 producer | [frp_m31_phase_interference_thermal_evidence.py](../../frp_m31_phase_interference_thermal_evidence.py) |
| M31 focused tests | [tests/test_frp_m31_phase_interference_thermal_evidence.py](../../tests/test_frp_m31_phase_interference_thermal_evidence.py) |
| M31 schema | [schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json](../../schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json) |
| M31 evidence | [artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json](../../artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json) |
| M31 manifest | [artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json](../../artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json) |
| M31 qualification | [artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json](../../artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json) |
| FRP v3.3.0 validation index | [FRP_VALIDATION_INDEX_v3_3_0.md](../../FRP_VALIDATION_INDEX_v3_3_0.md) |
| FRP v3.3.0 release notes | [RELEASE_NOTES_v3_3_0.md](../../RELEASE_NOTES_v3_3_0.md) |
| FRP v3.3.0 test report | [TEST_REPORT_v3_3_0.md](../../TEST_REPORT_v3_3_0.md) |
| M31 RTL publication workflow | [.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml](../../.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml) |
| Inherited M16 RTL boundary | [rtl/m16/README.md](../m16/README.md) |

M31 adds the complete RTL contour while preserving every historical evidence,
benchmark, schema, qualification, release, RTL, FPGA, workflow, and archival
record in its original release-specific repository path.

## 20. Measurement domains

The RTL records each quantity inside its declared measurement domain:

- `R_G` records phase-only order;
- phase-and-amplitude coherence remains a separate measurement domain;
- `tau` records the normalized common-RC comparative thermal proxy;
- physical temperature and energy use separate measurement domains;
- `thermal_node_factor_q30` and `gamma_effective_word` remain explicit
  per-cell top-level inputs;
- the phase-derived target and retained executed state remain separate
  architectural variables;
- `C_RTL`, `P_RTL`, and `Delta_RTL` are fixed-point operational RTL
  projections;
- the complete integrated phase engine is qualified for the exact eight-cell
  M31 profile;
- every historical benchmark and evidence class retains its original schema,
  unit, workload, provenance, and release boundary.

## License

Licensed under the [Apache License 2.0](../../LICENSE).

## Author

**Maksym Marnov (Alchimist)**

Berlin, Germany
