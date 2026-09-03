# FRP M31 RTL Artifact Manifest

## Release Identity

| Field | Value |
|---|---|
| Processor | `FRP — Ternary Fractal Resonant Coherence Processor` |
| Repository release | `FRP v3.3.0` |
| Milestone | `M31 — RTL Core Realization and Execution Semantics Package` |
| RTL directory | `rtl/m31/` |
| Integrated synthesis boundary | `frp_m31_core` |
| Complete qualification boundary | `frp_m31_tb` |
| Execution-only qualification boundary | `frp_m31_execution_tb` |
| License | `Apache-2.0` |
| Qualification status | `PASS` |

## Manifest Boundary

This manifest records the complete M31 RTL implementation payload published in
`rtl/m31/` for `FRP v3.3.0`.

The implementation payload contains exactly:

- eighteen SystemVerilog source and qualification files;
- one SystemVerilog compilation file list;
- one 4096-entry Q30 sine lookup memory;
- twenty implementation artifacts in total;
- `288056` bytes in total.

The five-file M31 RTL documentation record is versioned alongside the
implementation payload:

| Documentation file | Record |
|---|---|
| `README.md` | complete M31 RTL architecture and interface specification |
| `ARTIFACTS.md` | exact artifact roles, byte counts, hashes, and evidence links |
| `SIMULATION.md` | deterministic build, execution, and validation procedure |
| `SIMULATION_TRANSCRIPT.md` | qualified command and terminal-output record |
| `CLOSURE.md` | M31 RTL closure and preservation record |

Documentation files are outside the twenty-artifact implementation checksum
boundary so that explanatory records can evolve while the qualified RTL payload
retains an exact cryptographic identity.

## Implementation Inventory

| File | Module, package, or data role | Architectural function |
|---|---|---|
| `frp_m31.f` | compilation file list | establishes `rtl/m31` as the include directory and selects `frp_m31_core.sv` as the integrated source root |
| `frp_m31_pkg.sv` | `frp_m31_pkg` | defines the canonical `-1/0/1` state encoding, scheduler modes and states, transition classes, rejection classes, invariant indexes, capacity relation, and shared semantic functions |
| `frp_m31_fixed_point_pkg.sv` | `frp_m31_fixed_point_pkg` | defines signed Q16 and Q30 arithmetic, unsigned phase words, exact constants, saturation, rounding, multiplication, phase addressing, and sine-table access |
| `frp_m31_scheduler.sv` | `frp_m31_scheduler` | realizes deterministic `free`, `7/1`, and `1/7` temporal execution |
| `frp_m31_request_lanes.sv` | `frp_m31_request_lanes` | performs deterministic ascending request-lane arbitration and scheduler-qualified request admission |
| `frp_m31_pending_routes.sv` | `frp_m31_pending_routes` | retains an opposite-polarity destination while the transition is completed through state `0` on separate eligible ticks |
| `frp_m31_active_neutral.sv` | `frp_m31_active_neutral` | classifies retained-state transitions and generates the legal candidate sequence through computational state `0` |
| `frp_m31_capacity_guard.sv` | `frp_m31_capacity_guard` | applies the distributed per-tick transition-capacity boundary after pending-completion priority and lane arbitration |
| `frp_m31_state_update.sv` | `frp_m31_state_update` | commits capacity-qualified retained-state changes and preserves state across disabled or deferred ticks |
| `frp_m31_execution_core.sv` | `frp_m31_execution_core` | integrates the scheduler, request lanes, pending routes, transition classification, capacity guard, retained-state writeback, counters, and invariant flags |
| `frp_m31_phase_interference.sv` | `frp_m31_phase_interference` | advances retained phase, evaluates relative-phase coupling, derives coherence observables, and selects a ternary target for every cell |
| `frp_m31_phase_request_adapter.sv` | `frp_m31_phase_request_adapter` | converts the phase-derived target bank into deterministic request lanes while respecting retained state and pending-route ownership |
| `frp_m31_thermal_proxy.sv` | `frp_m31_thermal_proxy` | integrates normalized switching activity in the common-RC comparative thermal domain |
| `frp_m31_stability.sv` | `frp_m31_stability` | combines coherence capacity, switching pressure, and the thermal proxy into a signed stability margin and `stable` flag |
| `frp_m31_core.sv` | `frp_m31_core` | integrates retained phase, interference, resonance selection, request generation, ternary execution, thermal integration, and stability evaluation |
| `frp_m31_assertions.sv` | `frp_m31_assertions` | verifies the retained-state execution boundary, scheduler accounting, lane order, routing, capacity, writeback, and zero-event invariants |
| `frp_m31_phase_thermal_assertions.sv` | `frp_m31_phase_thermal_assertions` | verifies the integrated phase, target, coherence, thermal-proxy, and stability boundary |
| `frp_m31_execution_tb.sv` | `frp_m31_execution_tb` | executes the deterministic inherited execution profiles independently of the phase and thermal contour |
| `frp_m31_tb.sv` | `frp_m31_tb` | executes the complete phase-to-retained-state-to-thermal-to-stability qualification contour |
| `frp_m31_sin_q30.mem` | Q30 sine lookup memory | supplies exactly 4096 signed Q30 sine values addressed by the upper twelve bits of the 32-bit phase word |

## Exact Cryptographic Identity

The following byte counts and SHA-256 digests identify the complete
twenty-artifact implementation payload.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `frp_m31.f` | `40` | `9f8d99d47f1545f2763b9ac63f46b571b5f8cc6f6eaaabaa978fd5810e9fe6f0` |
| `frp_m31_active_neutral.sv` | `25909` | `765429b33df3f843626bdc411ad8371fd963738a58ab10201abef75dcdafcaf0` |
| `frp_m31_assertions.sv` | `24366` | `16a6abea57d2161a58ad5660c62f86cf057e65dbb1d9ae76e355e912a378077b` |
| `frp_m31_capacity_guard.sv` | `20787` | `d0587897f955ce49923aca807b5d3e0c637383c88e5d5e0dfa8405f47917c123` |
| `frp_m31_core.sv` | `9019` | `92d394a0838515a6e00c0c5c5330edf42077b5d75d290d05ac73dd4f06e1510c` |
| `frp_m31_execution_core.sv` | `33724` | `e516a5cd378bd2ddecdadc5abb13ddef26c63fafe5bda65b47a6bd859ca66f92` |
| `frp_m31_execution_tb.sv` | `16492` | `53d0f4f0d723aec2d39e52ba28e0cbb952e7afc0804de0e252d1b990221fbb6c` |
| `frp_m31_fixed_point_pkg.sv` | `7278` | `6b2afb8d1583c93d95d2386ba25dd1eaef6bb5bd9a4e1c9e9abff1dd004cbf24` |
| `frp_m31_pending_routes.sv` | `17005` | `18889d85e78b23b844f1db4c46a35a6b7d01e609e3f1f0e6263a39a6c5729411` |
| `frp_m31_phase_interference.sv` | `11245` | `e8ceb80feb0b30db5e28d70bc4d68d51506da4d596b46a73c0137465d1455fe0` |
| `frp_m31_phase_request_adapter.sv` | `2251` | `fa78bcfe965270cc74855908aa392989d857575a2097a126539aabb1aab8990d` |
| `frp_m31_phase_thermal_assertions.sv` | `3783` | `fe7b06073e65fc64acf7232038911230db27fe3a5ce000d0e1d421e2f49b1b3b` |
| `frp_m31_pkg.sv` | `18531` | `762302f1c7a7f7f40cb029f5ada6a111fc8c3e3f6be9920e9b2401b95e179c94` |
| `frp_m31_request_lanes.sv` | `18290` | `32f75cc70df5dba3f4fbb511397be9a5921236c2afd16cfeb1350eca3f6e8109` |
| `frp_m31_scheduler.sv` | `10560` | `fc9de24b41736e5c5a9f9e464318c80adbfda9dc8cc4362c0c55bfed403bf97f` |
| `frp_m31_sin_q30.mem` | `36864` | `adbb4b94fcf8fa0bfc981d654679fd7518a5c4c9c97b611a35cd8accaf28233d` |
| `frp_m31_stability.sv` | `2203` | `69c06833e6dfbb28e25b74a5787dcd03756dddf0f66726de3ea47c1ad2931931` |
| `frp_m31_state_update.sv` | `18147` | `ebad1f7ee952a577239445d33d99cae799afaaff5c181c7162514bbcea6eab90` |
| `frp_m31_tb.sv` | `9679` | `3e6bc290634159b77d27e4970827b856f95c0988c269542abfd36e0bfb49fb93` |
| `frp_m31_thermal_proxy.sv` | `1883` | `34df4ebfc5dfad8e3e5e454e560404585de5c881e6f75abaae367d3bd9fb11bd` |
| **Total** | **`288056`** | **twenty implementation artifacts** |

## Compilation and Elaboration Boundary

`frp_m31.f` contains the exact integrated compilation root:

`+incdir+rtl/m31`

`rtl/m31/frp_m31_core.sv`

`frp_m31_core.sv` includes:

- `frp_m31_execution_core.sv`;
- `frp_m31_phase_interference.sv`;
- `frp_m31_phase_request_adapter.sv`;
- `frp_m31_thermal_proxy.sv`;
- `frp_m31_stability.sv`.

`frp_m31_execution_core.sv` includes:

- `frp_m31_pkg.sv`;
- `frp_m31_scheduler.sv`;
- `frp_m31_request_lanes.sv`;
- `frp_m31_pending_routes.sv`;
- `frp_m31_active_neutral.sv`;
- `frp_m31_capacity_guard.sv`;
- `frp_m31_state_update.sv`.

`frp_m31_phase_interference.sv` includes:

- `frp_m31_pkg.sv`;
- `frp_m31_fixed_point_pkg.sv`.

The complete qualification boundary `frp_m31_tb.sv` includes:

- `frp_m31_core.sv`;
- `frp_m31_phase_thermal_assertions.sv`.

The execution-only qualification boundary `frp_m31_execution_tb.sv` includes:

- `frp_m31_pkg.sv`;
- `frp_m31_execution_core.sv`;
- `frp_m31_assertions.sv`.

Every SystemVerilog artifact has an include guard, and every source file carries
the SPDX identifier `Apache-2.0`.

## Processor-State Contract

The retained discrete processor domain is exactly:

`{-1, 0, 1}`

| Semantic state | Canonical encoding | Computational role |
|---:|---|---|
| `-1` | `2'b11` | retained negative-polarity state |
| `0` | `2'b00` | balancing, damping, mediation, routing, transition buffering, switching-load distribution, and retained-state stabilization |
| `1` | `2'b01` | retained positive-polarity state |
| reserved | `2'b10` | excluded from the retained processor domain |

Opposite-polarity retained-state transitions are realized as two ordered state
changes on separate eligible ticks:

`-1 → 0 → 1`

`1 → 0 → -1`

The first leg commits state `0` and records the destination polarity in the
pending-route bank. The second leg commits the retained destination from state
`0`. Each state-changing leg independently consumes transition capacity.

## Temporal and Capacity Contract

| Property | Exact M31 relation |
|---|---|
| Scheduler modes | `free`, `7/1`, `1/7` |
| Scheduler period | `8` enabled ticks |
| `7/1` sequence | seven `balance` ticks followed by one `commit` tick |
| `1/7` sequence | one `excite` tick followed by seven `neutralize` ticks |
| Transition fraction | `1/4 = 0.25` |
| Request-lane relation | `REQUEST_LANES = max(1, round(CELLS × 0.25))` |
| Qualified cell count | `8` |
| Qualified request lanes | `2` |
| Pending-route priority | pending completion before new explicit requests |
| Lane arbitration | ascending lane order, one accepted request per cell per tick |

Qualified parameter profiles encoded by `frp_calc_request_lanes` are:

| Cells | Request lanes |
|---:|---:|
| `8` | `2` |
| `16` | `4` |
| `32` | `8` |

## Phase, Coherence, Thermal, and Stability Contract

The integrated M31 data path is:

1. retain 32-bit phase and Q16 frequency state;
2. evaluate weighted relative-phase interference with the 4096-entry Q30 sine table;
3. derive phase projection and a target in the `-1/0/1` domain;
4. evaluate pair, cluster, and global coherence plus organization dispersion;
5. convert phase-derived targets into deterministic request lanes;
6. apply scheduler, pending-route, state-`0`, and capacity semantics;
7. commit the retained ternary state;
8. normalize accepted switching activity across the cell bank;
9. integrate the common-RC comparative thermal proxy;
10. evaluate coherence capacity, pressure, signed stability margin, and the `stable` flag.

Fixed-point boundaries are:

| Domain | Representation |
|---|---|
| phase | unsigned 32-bit modular phase word |
| frequency, coupling, thermal, pressure, margin | signed Q16 |
| sine, phase projection, coherence, dispersion | signed Q30 |
| sine address | upper 12 bits of the phase word |
| sine table | 4096 signed Q30 entries |

The thermal outputs represent normalized common-RC comparative units. Physical
temperature and physical energy remain separate measurement domains requiring a
calibrated device, process, voltage, frequency, activity, package, and ambient
measurement contour.

## Integrated Invariant Set

`frp_m31_pkg.sv` defines ten integrated invariant flags:

| Index | Constant | Verified relation |
|---:|---|---|
| `0` | `FRP_INV_STATE_DOMAIN_VALID` | retained states use only the canonical `-1/0/1` encodings |
| `1` | `FRP_INV_SCHEDULER_COUNTS_VALID` | scheduler-state counters close exactly to recorded ticks |
| `2` | `FRP_INV_REQUEST_LANE_ORDER_VALID` | accepted lanes follow deterministic ascending order |
| `3` | `FRP_INV_PENDING_POLARITY_VALID` | pending routes retain only `-1`, `0`, or `1` encodings |
| `4` | `FRP_INV_ACTIVE_NEUTRAL_VALID` | opposite-polarity execution passes through state `0` |
| `5` | `FRP_INV_TRANSITION_CAPACITY_VALID` | accepted state changes remain within the per-tick capacity |
| `6` | `FRP_INV_STATE_UPDATE_VALID` | retained writeback is authorized by the qualified candidate mask |
| `7` | `FRP_INV_NO_ACTUAL_DIRECT_EVENTS` | `actual_direct_events = 0` |
| `8` | `FRP_INV_NO_RESERVED_STATE` | `reserved_state_events = 0` |
| `9` | `FRP_INV_NO_QUEUE_OVERFLOW` | `queue_overflow_events = 0` |

The qualification testbenches require all ten flags to be asserted.

## Qualification Anchors

The focused M31 evidence suite records:

| Qualification | Result |
|---|---|
| focused Python qualification | `60 / 60 PASS` |
| evidence generation | deterministic byte identity |
| schema validation | `PASS` |
| manifest validation | `PASS` |
| qualification record | `PASS` |
| complete RTL contour | `PASS` |

The complete integrated RTL testbench terminates with:

`FRP_M31_COMPLETE_RTL: PASS`

`phase/coherence/resonance/active-zero/thermal/stability: PASS`

The execution-only RTL testbench terminates with:

`FRP M31 deterministic RTL testbench completed.`

`CELLS=8 REQUEST_LANES=2`

`ticks_recorded=16`

`actual_direct_events=0`

`reserved_state_events=0`

`queue_overflow_events=0`

## Repository Evidence Chain

| Record | Repository path |
|---|---|
| M31 evidence generator | [`frp_m31_phase_interference_thermal_evidence.py`](../../frp_m31_phase_interference_thermal_evidence.py) |
| M31 focused tests | [`tests/test_frp_m31_phase_interference_thermal_evidence.py`](../../tests/test_frp_m31_phase_interference_thermal_evidence.py) |
| M31 evidence schema | [`schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json`](../../schemas/m31/frp.m31.phase_interference_active_zero_thermal_evidence.v1.schema.json) |
| M31 evidence document | [`artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json`](../../artifacts/m31/evidence/m31-phase-interference-active-zero-thermal-evidence.json) |
| M31 evidence manifest | [`artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json`](../../artifacts/m31/manifests/m31-phase-interference-active-zero-thermal-evidence-manifest.json) |
| M31 qualification record | [`artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json`](../../artifacts/m31/qualification/m31-phase-interference-active-zero-thermal-evidence-qualification.json) |
| M31 validation index | [`FRP_VALIDATION_INDEX_v3_3_0.md`](../../FRP_VALIDATION_INDEX_v3_3_0.md) |
| M31 release notes | [`RELEASE_NOTES_v3_3_0.md`](../../RELEASE_NOTES_v3_3_0.md) |
| M31 test report | [`TEST_REPORT_v3_3_0.md`](../../TEST_REPORT_v3_3_0.md) |
| M31 complete RTL qualification workflow | [`.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml`](../../.github/workflows/frp-m31e1-phase-interference-thermal-package-workflow.yml) |
| Repository license | [`LICENSE`](../../LICENSE) |

## Preservation Record

M31 is an additive RTL realization layer. Historical evidence, benchmarks,
schemas, release records, FPGA records, and earlier RTL milestone directories
retain their established repository paths. The M31 implementation consumes and
references those records without relocating their historical identities.

The implementation checksum boundary in this document covers only the twenty
files listed under **Exact Cryptographic Identity**. Evidence and benchmark
identity remains governed by their milestone manifests, qualification records,
validation indexes, release notes, and test reports.

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany
