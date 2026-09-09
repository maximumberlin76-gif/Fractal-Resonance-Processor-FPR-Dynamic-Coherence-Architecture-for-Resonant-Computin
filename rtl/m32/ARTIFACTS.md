# FRP M32 Artifact Index

## Boundary identity

| Field | Value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Released upstream baseline | `FRP v3.3.0 / M31` |
| Implementation milestone | `M32` |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Top-level integration module | `frp_m32_core` |
| Canonical source identities | `29 / 29 exact` |
| Canonical publication outputs | `4 / 4 exact` |
| Trace qualification checks | `38 / 38 PASS` |
| Canonical ternary notation | `-1/0/1` |
| License | Apache-2.0 |

This index records the implemented M32 registered-target RTL boundary, its
exact inherited M31 dependencies, formal harness, qualification workflow,
deterministic trace exporter, and canonical publication outputs.

## Artifact classes

| Class | Count | Bytes | Identity authority |
|---|---:|---:|---|
| Inherited M31 RTL sources | `16` | `252826` | canonical M32 trace bundle source identities |
| M32 RTL sources and testbenches | `11` | `140680` | canonical M32 trace bundle source identities |
| M32 formal source | `1` | `7698` | canonical M32 trace bundle source identities |
| Registered-target qualification workflow | `1` | `41712` | canonical M32 trace bundle source identities |
| Complete canonical source boundary | `29` | `442916` | source commit `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Canonical publication outputs | `4` | `458096` | manifest, qualification, and exact export workflow comparison |

The deterministic trace exporter, independent exporter tests, export
workflow, M32 documentation, and preserved repair workflow were added after
the fixed RTL source boundary. Their identities are recorded separately and
do not alter the source commit embedded in the canonical bundle.

## M32 implementation inventory

| Artifact | Role | Qualification boundary |
|---|---|---|
| `rtl/m32/frp_m32_registered_target_boundary.sv` | clocked capture of valid phase-derived target banks, domain validation, and capture counters | lint, `8/16/32`-cell synthesis, bounded proofs, deterministic simulation |
| `rtl/m32/frp_m32_registered_target_boundary_tb.sv` | accepted, rejected, disabled-tick, counter-clear, reset, and retained-bank test sequence | deterministic simulation replay |
| `rtl/m32/frp_m32_registered_target_request_path.sv` | registered target gate and inherited request-adapter composition | lint and deterministic simulation replay |
| `rtl/m32/frp_m32_registered_target_request_path_tb.sv` | source/registered/request separation, scheduler eligibility, pending ownership, and invalid-source tests | deterministic simulation replay |
| `rtl/m32/frp_m32_core.sv` | integrated registered-target top-level over the M31 phase, execution, thermal, and stability contour | lint and deterministic simulation replay |
| `rtl/m32/frp_m32_core_tb.sv` | integrated phase-source, registered-target, request, execution, route, frequency, thermal, stability, and invariant test sequence | deterministic simulation replay |
| `rtl/m32/frp_m32_mode_7_1_tb.sv` | dedicated `7/1` cadence and two-leg route sequence | deterministic simulation replay |
| `rtl/m32/frp_m32_mode_1_7_tb.sv` | dedicated `1/7` cadence and two-leg route sequence | deterministic simulation replay |
| `rtl/m32/frp_m32_trace_monitor.sv` | structured sample, bank, cell, and request records | lint and deterministic transcript generation |
| `rtl/m32/frp_m32_mode_7_1_trace_tb.sv` | mode `7/1` testbench plus trace-monitor composition | `2/2` byte-identical full-trace executions |
| `rtl/m32/frp_m32_mode_1_7_trace_tb.sv` | mode `1/7` testbench plus trace-monitor composition | `2/2` byte-identical full-trace executions |
| `formal/m32/frp_m32_registered_target_boundary_formal.sv` | safety and capture-sequence bounded formal harnesses | `10` safety and `4` sequence assertions at depth `4`, each with `2/2` deterministic replays |

## Exact source identity boundary

These `29` records are reproduced from the canonical bundle and verified
against the current repository files.

### Inherited M31 RTL sources

| Path | Bytes | SHA-256 |
|---|---:|---|
| `rtl/m31/frp_m31_pkg.sv` | `18531` | `762302f1c7a7f7f40cb029f5ada6a111fc8c3e3f6be9920e9b2401b95e179c94` |
| `rtl/m31/frp_m31_fixed_point_pkg.sv` | `7278` | `6b2afb8d1583c93d95d2386ba25dd1eaef6bb5bd9a4e1c9e9abff1dd004cbf24` |
| `rtl/m31/frp_m31_scheduler.sv` | `10560` | `fc9de24b41736e5c5a9f9e464318c80adbfda9dc8cc4362c0c55bfed403bf97f` |
| `rtl/m31/frp_m31_request_lanes.sv` | `18290` | `32f75cc70df5dba3f4fbb511397be9a5921236c2afd16cfeb1350eca3f6e8109` |
| `rtl/m31/frp_m31_pending_routes.sv` | `17005` | `18889d85e78b23b844f1db4c46a35a6b7d01e609e3f1f0e6263a39a6c5729411` |
| `rtl/m31/frp_m31_active_neutral.sv` | `25909` | `765429b33df3f843626bdc411ad8371fd963738a58ab10201abef75dcdafcaf0` |
| `rtl/m31/frp_m31_capacity_guard.sv` | `20787` | `d0587897f955ce49923aca807b5d3e0c637383c88e5d5e0dfa8405f47917c123` |
| `rtl/m31/frp_m31_state_update.sv` | `18147` | `ebad1f7ee952a577239445d33d99cae799afaaff5c181c7162514bbcea6eab90` |
| `rtl/m31/frp_m31_execution_core.sv` | `33724` | `e516a5cd378bd2ddecdadc5abb13ddef26c63fafe5bda65b47a6bd859ca66f92` |
| `rtl/m31/frp_m31_phase_interference.sv` | `11245` | `e8ceb80feb0b30db5e28d70bc4d68d51506da4d596b46a73c0137465d1455fe0` |
| `rtl/m31/frp_m31_phase_request_adapter.sv` | `2251` | `fa78bcfe965270cc74855908aa392989d857575a2097a126539aabb1aab8990d` |
| `rtl/m31/frp_m31_thermal_proxy.sv` | `1883` | `34df4ebfc5dfad8e3e5e454e560404585de5c881e6f75abaae367d3bd9fb11bd` |
| `rtl/m31/frp_m31_stability.sv` | `2203` | `69c06833e6dfbb28e25b74a5787dcd03756dddf0f66726de3ea47c1ad2931931` |
| `rtl/m31/frp_m31_assertions.sv` | `24366` | `16a6abea57d2161a58ad5660c62f86cf057e65dbb1d9ae76e355e912a378077b` |
| `rtl/m31/frp_m31_phase_thermal_assertions.sv` | `3783` | `fe7b06073e65fc64acf7232038911230db27fe3a5ce000d0e1d421e2f49b1b3b` |
| `rtl/m31/frp_m31_sin_q30.mem` | `36864` | `adbb4b94fcf8fa0bfc981d654679fd7518a5c4c9c97b611a35cd8accaf28233d` |
| **Subtotal** | **`252826`** | **`16` inherited identities** |

### M32 RTL and formal sources

| Path | Bytes | SHA-256 |
|---|---:|---|
| `rtl/m32/frp_m32_registered_target_boundary.sv` | `3947` | `9626474b49d32b411e107d7ccc8ee5aa7f42728e9a6f70d634d16d3f2a414c5e` |
| `rtl/m32/frp_m32_registered_target_boundary_tb.sv` | `6748` | `0824e781f276f325aa86bb9a6a136f1d4da910920b64d15fafe5d7d017e5288a` |
| `rtl/m32/frp_m32_registered_target_request_path.sv` | `3244` | `02250069a68737f055a419cd67bf2d439b3f63b3f6a7a245f40e9bf29d1958eb` |
| `rtl/m32/frp_m32_registered_target_request_path_tb.sv` | `12135` | `a615d9b3bd456f60b37715433862830a4f3f8170859a2b12415d4b4b071faea5` |
| `rtl/m32/frp_m32_core.sv` | `10564` | `925342326b7ad555a1382e8ee3bc5754ed3012ba60e0eabf512113731e0ee6c9` |
| `rtl/m32/frp_m32_core_tb.sv` | `19348` | `4a2ac2778192199d02700c324da7d0cfba4a2f83730ea148497099e1a640d800` |
| `rtl/m32/frp_m32_mode_7_1_tb.sv` | `22207` | `7a6d610435bbd3f11441cb518bb64ab05b3748f5bb866092b1a734eab99c08f8` |
| `rtl/m32/frp_m32_mode_1_7_tb.sv` | `22388` | `3dcd66dbd8edc6989294298adb14d4e3b314e0af62512b5a1398b789cb510b97` |
| `rtl/m32/frp_m32_trace_monitor.sv` | `13827` | `556dd0759d91188b1947ae3abf61a0606cec238b67ff268f243eab370b01fc7c` |
| `rtl/m32/frp_m32_mode_7_1_trace_tb.sv` | `13136` | `4d02db27a3ae080c7c2a029e27d1b2c66bdbd2ad35c64ad3e020792c0bb841ca` |
| `rtl/m32/frp_m32_mode_1_7_trace_tb.sv` | `13136` | `bfb4b58f95f09e2fcbb81df3fae1c452a2e83111da7a9076dfaaefd2d76ab6cb` |
| `formal/m32/frp_m32_registered_target_boundary_formal.sv` | `7698` | `b4880df9c8ca6a3f220a26d4937c14b63e3b97277cdff16ce50de725c7f840d2` |
| **Subtotal** | **`148378`** | **`12` M32 RTL and formal identities** |

### Source qualification workflow

| Path | Bytes | SHA-256 |
|---|---:|---|
| `.github/workflows/frp-m32-registered-target-boundary-workflow.yml` | `41712` | `c0e3a9d134201d1d4d855f43d5740138155291d2074663207456841a08470afe` |
| **Complete source boundary** | **`442916`** | **`29` exact identities** |

## Deterministic transcript identities

| Scheduler mode | Replay | Artifact member | Bytes | SHA-256 |
|---|---:|---|---:|---|
| `7/1` | `1` | `m32-mode-7-1-full-trace-run-1.log` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `7/1` | `2` | `m32-mode-7-1-full-trace-run-2.log` | `105702` | `9517a02cd1ce2c687365f3712a453a9370e505ee4267e151fd05b266977ce915` |
| `1/7` | `1` | `m32-mode-1-7-full-trace-run-1.log` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |
| `1/7` | `2` | `m32-mode-1-7-full-trace-run-2.log` | `112364` | `41de8e92c28f150f8d163fc1438b4d4381fa42d76a970f9246bbda4679491d89` |

Each replay pair is byte-identical within its scheduler mode. The two modes
retain separate transcripts and identities.

## Canonical publication output identities

| Path | Bytes | Raw SHA-256 |
|---|---:|---|
| `schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json` | `34066` | `534db8227218184cac5d1cabb461dd63b1b61a99e0269c98535539ad3f7d7da2` |
| `artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json` | `412195` | `62d8c1e6d205b9262a5c950883d3259275d5049f7a896ae12956a210cb75b7e0` |
| `artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json` | `7211` | `da011dbc726d6d1fc0b7dbae12afe1e13d8240df64b9474fd0130c94ba005859` |
| `artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json` | `4624` | `26ec2d3eadd73b490eb023572101bb78cf5d11561ead91b78b1a30e690458273` |
| **Total** | **`458096`** | **`4` canonical outputs** |

Canonical payload digests embedded in the records are:

| Record | Digest scope | Embedded SHA-256 |
|---|---|---|
| Trace bundle | canonical JSON without `bundle_sha256` | `63b36c1fb29d28a33bb5387d7658c97fc0a51f6823f79dc71382132236685f9b` |
| Manifest | canonical JSON without `manifest_sha256` | `a9dd7d470fd094cb1dbb6fa360f6c28bf50d4aae4bf2f1ba34ad223655968c2e` |
| Qualification | canonical JSON without `qualification_sha256` | `a695ccb3c7f083e219ff6908dfc38e6f4e7ef37fca6da22f40c6303117027c5d` |

The qualification record contains `38` checks, `38` passed checks, and `0`
failed checks. It references the schema, bundle, and manifest. The
qualification file is the fourth generated output and is not included in its
own three-artifact antecedent list.

## Exporter and workflow identities

| Path | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `frp_m32_deterministic_rtl_trace_export.py` | canonical parser, validator, generator, verifier, deterministic self-test, and mutation rejection | `64267` | `1a575482d0c62f977afc72f25c8d8eacb0daa35981f39cb64b7f85069e5c43cd` |
| `tests/test_frp_m32_deterministic_rtl_trace_export.py` | `49` independent exporter tests | `30889` | `e2b53c9973219b02c0fce2eda835bef87de0d8681ab61af89ef621fbafdfe774` |
| `.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml` | exact transcript replay, canonical generation, verification, mutation rejection, and published-output comparison | `20361` | `6636eb82c736db4452692105babda97ce94542e2deeb7dfaf2b3bb3d8aba960e` |

The export workflow verifies all four generated files against fixed byte
counts and raw SHA-256 values and compares each generated file byte-for-byte
with its tracked repository counterpart.

## Documentation identity

| Path | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `rtl/m32/README.md` | M32 registered-target, scheduler-trace, formal, synthesis, publication, and provenance boundary | `12728` | `e4ac144bd92d611eb04cc8b1e00fa016bd92cbefd5cddfa1ba91c4a60ef7a2cb` |

`rtl/m32/ARTIFACTS.md` is excluded from its own identity tables to avoid a
self-referential digest.

## Preserved repair workflow

| Path | Historical role | Bytes | SHA-256 |
|---|---|---:|---|
| `.github/workflows/frp-m32-canonical-trace-bundle-repair.yml` | guarded restoration of the exact canonical bundle serialization after manual multipart insertion | `4850` | `961978c90e2b862df0c07866d0fae3a9f57c4be1d4b80e24311c555cb9a486a4` |

The repair workflow is preserved as workflow history. It is not a member of
the canonical RTL source identity set and does not replace the deterministic
export workflow.

## Composition boundary

`frp_m32_core.sv` includes:

- `frp_m31_execution_core.sv`;
- `frp_m31_phase_interference.sv`;
- `frp_m32_registered_target_request_path.sv`;
- `frp_m31_thermal_proxy.sv`;
- `frp_m31_stability.sv`.

`frp_m32_registered_target_request_path.sv` includes:

- `frp_m32_registered_target_boundary.sv`;
- `frp_m31_phase_request_adapter.sv`.

Each full-trace wrapper includes its dedicated scheduler-mode testbench and
`frp_m32_trace_monitor.sv`. The integrated source root uses include paths
`rtl/m31` and `rtl/m32` in the qualification workflows.

The registered-boundary synthesis evidence applies to
`frp_m32_registered_target_boundary` at `8`, `16`, and `32` cells. The
integrated `frp_m32_core` evidence in the current M32 workflow consists of
lint, deterministic simulation, assertion execution, and trace generation.

## Processor-state identity

The retained processor domain is exactly:

```
T = {-1, 0, 1}
```

State `0` is an active retained state used for mediation, balancing, routing,
damping, transition staging, retained-state participation, pending-route
handling, and controlled neutralization.

Opposite-polarity routes retain two separately observable legs:

```
-1 -> 0 -> 1
1 -> 0 -> -1
```

The canonical traces contain no direct opposite-polarity retained transition,
reserved-state event, or pending-route overflow event.

## Evidence links

| Record | Path |
|---|---|
| M32 boundary documentation | [`README.md`](README.md) |
| Registered-target workflow | [`../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) |
| Deterministic export workflow | [`../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) |
| Trace exporter | [`../../frp_m32_deterministic_rtl_trace_export.py`](../../frp_m32_deterministic_rtl_trace_export.py) |
| Independent exporter tests | [`../../tests/test_frp_m32_deterministic_rtl_trace_export.py`](../../tests/test_frp_m32_deterministic_rtl_trace_export.py) |
| Trace schema | [`../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json`](../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json) |
| Trace bundle | [`../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json`](../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json) |
| Manifest | [`../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json`](../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json) |
| Qualification | [`../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json`](../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json) |

## Provenance and preservation

The canonical trace bundle assigns the `upstream_frp_systemverilog_rtl`
provenance class to the exact M31/M32 source boundary. No downstream
Observatory implementation artifact is included in this identity set.

M32 is additive over M31. Earlier RTL, FPGA, evidence, benchmark, schema,
workflow, release, and deterministic identity records remain at their
established repository paths.

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany  
ORCID: `0009-0000-0832-9597`
