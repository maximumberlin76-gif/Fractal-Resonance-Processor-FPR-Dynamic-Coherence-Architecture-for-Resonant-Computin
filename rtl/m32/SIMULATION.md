# FRP M32 Simulation and Qualification Procedure

## Boundary identity

| Field | Value |
|---|---|
| Project | `Fractal Resonance Processor (FRP)` |
| Milestone | `M32` |
| RTL source boundary commit | `c0bc0fbc2c1c2e500b19d0ba84b3431a813e3941` |
| Integrated top-level module | `frp_m32_core` |
| Qualified integrated configuration | `8` cells, `2` request lanes |
| Registered-boundary synthesis profiles | `8`, `16`, and `32` cells |
| Scheduler trace modes | `7/1` and `1/7` |
| Canonical ternary notation | `-1/0/1` |

This document reproduces the commands encoded in the M32 registered-target
and deterministic trace-export workflows. Commands are executed from the
repository root.

## Qualification boundaries

| Boundary | Tool and operation |
|---|---|
| Exact source identities | byte count and SHA-256 comparison |
| M32 RTL and testbenches | Verilator lint |
| Registered target boundary | Yosys synthesis for `8`, `16`, and `32` cells |
| Registered target boundary | bounded Yosys SAT proofs at depth `4` |
| M32 testbenches | Verilator binary build and deterministic replay |
| Scheduler traces | record cardinality, cadence, route-leg, and invariant checks |
| Trace exporter | `49` independent Python tests |
| Canonical outputs | deterministic generation, schema validation, mutation rejection, exact identity, and repository comparison |

The synthesis procedure applies to
`frp_m32_registered_target_boundary`. The integrated `frp_m32_core` procedure
uses lint, deterministic simulation, assertion execution, and trace export.

## Toolchain

The GitHub Actions jobs use:

| Component | Workflow setting |
|---|---|
| Runner | `ubuntu-24.04` |
| Python | `3.12` |
| Verilator | Ubuntu runner package, version recorded in each run artifact |
| C++ compiler | Ubuntu `g++`, C++20 mode |
| Yosys | `yowasp-yosys==0.68.0.0.post1208` |
| JSON Schema validator | `jsonschema==4.25.1` |
| Locale | `C.UTF-8` |
| Time zone | `UTC` |
| Python hash seed | `0` for the export workflow |

Install the execution dependencies:

```
sudo apt-get update
sudo apt-get install --yes --no-install-recommends g++ verilator
python -m pip install \
  --disable-pip-version-check \
  yowasp-yosys==0.68.0.0.post1208 \
  jsonschema==4.25.1
```

Record the active toolchain:

```
verilator --version
g++ --version | head -n 1
python --version
yowasp-yosys -V
python -c 'from importlib.metadata import version; print(version("jsonschema"))'
```

Initialize deterministic shell state and an isolated work directory:

```
set -euo pipefail
export LC_ALL=C.UTF-8
export TZ=UTC
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
export M32_WORK_DIR="$(mktemp -d)"
```

## Source-identity preflight

The canonical exporter validates all `29` M31/M32 source identities, including
the registered-target workflow identity:

```
python - <<'PY'
from pathlib import Path

import frp_m32_deterministic_rtl_trace_export as m32

records = m32.validate_source_identities(Path(".").resolve())
if len(records) != 29:
    raise SystemExit("unexpected M32 source identity count")
print("FRP M32 source identities: PASS count=29")
PY
```

The complete identity table is recorded in
[`ARTIFACTS.md`](ARTIFACTS.md).

## Verilator lint

Use the same lint function as the registered-target workflow:

```
lint_top() {
  local top_module="$1"
  local source_path="$2"

  verilator \
    --lint-only \
    --sv \
    --timing \
    --assert \
    -Wall \
    -Wno-fatal \
    --top-module "$top_module" \
    -Irtl/m31 \
    -Irtl/m32 \
    "$source_path"
}

lint_top \
  frp_m32_registered_target_boundary \
  rtl/m32/frp_m32_registered_target_boundary.sv
lint_top \
  frp_m32_registered_target_boundary_tb \
  rtl/m32/frp_m32_registered_target_boundary_tb.sv
lint_top \
  frp_m32_registered_target_request_path \
  rtl/m32/frp_m32_registered_target_request_path.sv
lint_top \
  frp_m32_registered_target_request_path_tb \
  rtl/m32/frp_m32_registered_target_request_path_tb.sv
lint_top \
  frp_m32_core \
  rtl/m32/frp_m32_core.sv
lint_top \
  frp_m32_core_tb \
  rtl/m32/frp_m32_core_tb.sv
lint_top \
  frp_m32_mode_7_1_tb \
  rtl/m32/frp_m32_mode_7_1_tb.sv
lint_top \
  frp_m32_mode_1_7_tb \
  rtl/m32/frp_m32_mode_1_7_tb.sv
lint_top \
  frp_m32_trace_monitor \
  rtl/m32/frp_m32_trace_monitor.sv
lint_top \
  frp_m32_mode_7_1_trace_tb \
  rtl/m32/frp_m32_mode_7_1_trace_tb.sv
lint_top \
  frp_m32_mode_1_7_trace_tb \
  rtl/m32/frp_m32_mode_1_7_trace_tb.sv
```

## Registered-boundary synthesis

Run two synthesis replays for each qualified cell profile and compare the
generated JSON netlists:

```
synthesize_profile() {
  local cells="$1"
  local replay
  local netlist_path
  local log_path
  local yosys_script

  for replay in 1 2; do
    netlist_path="${M32_WORK_DIR}/boundary-synth-${cells}-run-${replay}.json"
    log_path="${M32_WORK_DIR}/boundary-synth-${cells}-run-${replay}.log"
    yosys_script="read_verilog -sv -I rtl/m31 rtl/m32/frp_m32_registered_target_boundary.sv; chparam -set CELLS ${cells} frp_m32_registered_target_boundary; synth -noabc -top frp_m32_registered_target_boundary; check; stat; write_json ${netlist_path}"

    yowasp-yosys -p "$yosys_script" 2>&1 | tee "$log_path"
    test -s "$netlist_path"
    test "$(grep -Fc 'Found and reported 0 problems.' "$log_path")" -ge 3
    test "$(grep -Fc 'End of script.' "$log_path")" -eq 1
  done

  cmp \
    "${M32_WORK_DIR}/boundary-synth-${cells}-run-1.json" \
    "${M32_WORK_DIR}/boundary-synth-${cells}-run-2.json"
  sha256sum \
    "${M32_WORK_DIR}/boundary-synth-${cells}-run-1.json"
}

synthesize_profile 8
synthesize_profile 16
synthesize_profile 32
```

Each profile requires a non-empty netlist, zero reported Yosys problems, a
completed script, and byte-identical replay netlists.

## Bounded formal qualification

The formal source contains two top modules:

| Top module | Assertions | Depth | Replay count |
|---|---:|---:|---:|
| `frp_m32_registered_target_boundary_safety_formal` | `10` | `4` | `2` |
| `frp_m32_registered_target_boundary_sequence_formal` | `4` | `4` | `2` |

Run the same bounded proof command used by the workflow:

```
prove_top() {
  local top_module="$1"
  local assertion_count="$2"
  local record_prefix="$3"
  local expected_imports
  local replay
  local log_path
  local record_path
  local yosys_script

  expected_imports="$((assertion_count * 4))"
  yosys_script="read_verilog -sv -formal -I rtl/m31 rtl/m32/frp_m32_registered_target_boundary.sv formal/m32/frp_m32_registered_target_boundary_formal.sv; prep -top ${top_module}; flatten; chformal -lower; async2sync; opt_clean; check; sat -prove-asserts -set-def-formal -set-init-zero -seq 4 -timeout 300 -verify"

  for replay in 1 2; do
    log_path="${M32_WORK_DIR}/${record_prefix}-run-${replay}.log"
    record_path="${M32_WORK_DIR}/${record_prefix}-record-run-${replay}.txt"

    yowasp-yosys -p "$yosys_script" 2>&1 | tee "$log_path"
    test "$(grep -Fc 'SAT proof finished - no model found: SUCCESS!' "$log_path")" -eq 1
    test "$(grep -Fc 'Import proof for assert:' "$log_path")" -eq "$expected_imports"

    {
      printf 'top=%s\n' "$top_module"
      printf 'depth=%s\n' "4"
      printf 'assertions=%s\n' "$assertion_count"
      grep -F 'Import proof for assert:' "$log_path"
      grep -F 'Solving problem with' "$log_path"
      grep -F 'SAT proof finished - no model found: SUCCESS!' "$log_path"
    } > "$record_path"
  done

  cmp \
    "${M32_WORK_DIR}/${record_prefix}-record-run-1.txt" \
    "${M32_WORK_DIR}/${record_prefix}-record-run-2.txt"
  sha256sum \
    "${M32_WORK_DIR}/${record_prefix}-record-run-1.txt"
}

prove_top \
  frp_m32_registered_target_boundary_safety_formal \
  10 \
  m32-formal-safety
prove_top \
  frp_m32_registered_target_boundary_sequence_formal \
  4 \
  m32-formal-sequence
```

## Deterministic simulation replays

Build each testbench once and execute it twice:

```
build_and_replay() {
  local top_module="$1"
  local source_path="$2"
  local pass_record="$3"
  local record_prefix="$4"
  local build_dir="${M32_WORK_DIR}/build-${record_prefix}"
  local executable

  verilator \
    --binary \
    --sv \
    --timing \
    --assert \
    -Wall \
    -Wno-fatal \
    -CFLAGS "-std=c++20" \
    --top-module "$top_module" \
    --Mdir "$build_dir" \
    -Irtl/m31 \
    -Irtl/m32 \
    "$source_path"

  executable="${build_dir}/V${top_module}"
  test -x "$executable"

  "$executable" 2>&1 \
    | tee "${M32_WORK_DIR}/${record_prefix}-run-1.log"
  "$executable" 2>&1 \
    | tee "${M32_WORK_DIR}/${record_prefix}-run-2.log"

  cmp \
    "${M32_WORK_DIR}/${record_prefix}-run-1.log" \
    "${M32_WORK_DIR}/${record_prefix}-run-2.log"
  test "$(grep -Fxc \
    "$pass_record" \
    "${M32_WORK_DIR}/${record_prefix}-run-1.log")" -eq 1
}

build_and_replay \
  frp_m32_registered_target_boundary_tb \
  rtl/m32/frp_m32_registered_target_boundary_tb.sv \
  "FRP_M32_REGISTERED_TARGET_BOUNDARY_TB: PASS" \
  m32-boundary

build_and_replay \
  frp_m32_registered_target_request_path_tb \
  rtl/m32/frp_m32_registered_target_request_path_tb.sv \
  "FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB: PASS" \
  m32-request-path

build_and_replay \
  frp_m32_core_tb \
  rtl/m32/frp_m32_core_tb.sv \
  "FRP_M32_INTEGRATED_REGISTERED_TARGET_CORE_TB: PASS" \
  m32-core

build_and_replay \
  frp_m32_mode_7_1_tb \
  rtl/m32/frp_m32_mode_7_1_tb.sv \
  "FRP_M32_REGISTERED_TARGET_MODE_7_1_TB: PASS" \
  m32-mode-7-1

build_and_replay \
  frp_m32_mode_1_7_tb \
  rtl/m32/frp_m32_mode_1_7_tb.sv \
  "FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS" \
  m32-mode-1-7

build_and_replay \
  frp_m32_mode_7_1_trace_tb \
  rtl/m32/frp_m32_mode_7_1_trace_tb.sv \
  "FRP_M32_MODE_7_1_TRACE_TB: PASS samples=16" \
  m32-mode-7-1-full-trace

build_and_replay \
  frp_m32_mode_1_7_trace_tb \
  rtl/m32/frp_m32_mode_1_7_trace_tb.sv \
  "FRP_M32_MODE_1_7_TRACE_TB: PASS samples=17" \
  m32-mode-1-7-full-trace
```

Accepted terminal records are:

| Testbench | Required terminal record |
|---|---|
| Registered boundary | `FRP_M32_REGISTERED_TARGET_BOUNDARY_TB: PASS` |
| Registered request path | `FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB: PASS` |
| Integrated core | `FRP_M32_INTEGRATED_REGISTERED_TARGET_CORE_TB: PASS` |
| Mode `7/1` | `FRP_M32_REGISTERED_TARGET_MODE_7_1_TB: PASS` |
| Mode `1/7` | `FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS` |
| Mode `7/1` full trace | `FRP_M32_MODE_7_1_TRACE_TB: PASS samples=16` |
| Mode `1/7` full trace | `FRP_M32_MODE_1_7_TRACE_TB: PASS samples=17` |

## Scheduler and trace checks

Extract the scheduler summary records:

```
grep '^M32_MODE_7_1_TRACE ' \
  "${M32_WORK_DIR}/m32-mode-7-1-run-1.log" \
  > "${M32_WORK_DIR}/m32-mode-7-1-trace.log"
grep '^M32_MODE_1_7_TRACE ' \
  "${M32_WORK_DIR}/m32-mode-1-7-run-1.log" \
  > "${M32_WORK_DIR}/m32-mode-1-7-trace.log"

test "$(wc -l < "${M32_WORK_DIR}/m32-mode-7-1-trace.log")" -eq 16
test "$(grep -Fc ' balance_tick=1 commit_tick=0 ' \
  "${M32_WORK_DIR}/m32-mode-7-1-trace.log")" -eq 14
test "$(grep -Fc ' balance_tick=0 commit_tick=1 ' \
  "${M32_WORK_DIR}/m32-mode-7-1-trace.log")" -eq 2

test "$(wc -l < "${M32_WORK_DIR}/m32-mode-1-7-trace.log")" -eq 17
test "$(grep -Fc ' excite_tick=1 neutralize_tick=0 ' \
  "${M32_WORK_DIR}/m32-mode-1-7-trace.log")" -eq 3
test "$(grep -Fc ' excite_tick=0 neutralize_tick=1 ' \
  "${M32_WORK_DIR}/m32-mode-1-7-trace.log")" -eq 14
```

Extract the four structured record classes from each full trace:

```
extract_trace_records() {
  local mode="$1"
  local source_log="$2"

  grep '^M32_TRACE_' "$source_log" \
    > "${M32_WORK_DIR}/${mode}-records.log"
  grep '^M32_TRACE_SAMPLE ' "$source_log" \
    > "${M32_WORK_DIR}/${mode}-sample.log"
  grep '^M32_TRACE_BANK ' "$source_log" \
    > "${M32_WORK_DIR}/${mode}-bank.log"
  grep '^M32_TRACE_CELL ' "$source_log" \
    > "${M32_WORK_DIR}/${mode}-cell.log"
  grep '^M32_TRACE_REQUEST ' "$source_log" \
    > "${M32_WORK_DIR}/${mode}-request.log"
}

extract_trace_records \
  m32-mode-7-1-full-trace \
  "${M32_WORK_DIR}/m32-mode-7-1-full-trace-run-1.log"
extract_trace_records \
  m32-mode-1-7-full-trace \
  "${M32_WORK_DIR}/m32-mode-1-7-full-trace-run-1.log"
```

Required record cardinalities are:

| Mode | Sample | Bank | Cell | Request | Total |
|---|---:|---:|---:|---:|---:|
| `7/1` | `16` | `16` | `128` | `32` | `192` |
| `1/7` | `17` | `17` | `136` | `34` | `204` |

Every sample record must contain `invariant_all_valid=1` and zero values for
`actual_direct_events`, `reserved_state_events`, and
`queue_overflow_events`.

The separately observable route coordinates are:

| Mode | First leg | Second leg |
|---|---|---|
| `7/1` | source tick `9`, cell `0`, retained state `0` | source tick `15`, cell `0`, retained state `-1` |
| `1/7` | source tick `10`, cell `0`, retained state `0` | source tick `16`, cell `0`, retained state `-1` |

## Exporter tests

Run the independent exporter suite:

```
python -m unittest \
  tests.test_frp_m32_deterministic_rtl_trace_export \
  -v 2>&1 | tee "${M32_WORK_DIR}/m32-exporter-tests.log"

grep -Eq '^Ran 49 tests in [0-9.]+s$' \
  "${M32_WORK_DIR}/m32-exporter-tests.log"
test "$(grep -Fxc 'OK' \
  "${M32_WORK_DIR}/m32-exporter-tests.log")" -eq 1
```

The suite covers parsing, source and transcript identities, schema structure,
coordinate completeness, packed-record agreement, ternary code/value pairs,
registered-boundary separation, route-leg separation, invariants,
deterministic generation, and mutation rejection.

## Canonical trace generation and verification

Use the two replay logs from each full-trace testbench:

```
export M32_OUTPUT_ROOT="${M32_WORK_DIR}/canonical-output"

export M32_MODE_7_1_PRIMARY="${M32_WORK_DIR}/m32-mode-7-1-full-trace-run-1.log"
export M32_MODE_7_1_REPLAY="${M32_WORK_DIR}/m32-mode-7-1-full-trace-run-2.log"
export M32_MODE_1_7_PRIMARY="${M32_WORK_DIR}/m32-mode-1-7-full-trace-run-1.log"
export M32_MODE_1_7_REPLAY="${M32_WORK_DIR}/m32-mode-1-7-full-trace-run-2.log"

python frp_m32_deterministic_rtl_trace_export.py \
  --repository-root . \
  --mode-7-1-primary "$M32_MODE_7_1_PRIMARY" \
  --mode-7-1-replay "$M32_MODE_7_1_REPLAY" \
  --mode-1-7-primary "$M32_MODE_1_7_PRIMARY" \
  --mode-1-7-replay "$M32_MODE_1_7_REPLAY" \
  --self-test \
  | tee "${M32_WORK_DIR}/m32-export-self-test.json"

python frp_m32_deterministic_rtl_trace_export.py \
  --repository-root . \
  --output-root "$M32_OUTPUT_ROOT" \
  --mode-7-1-primary "$M32_MODE_7_1_PRIMARY" \
  --mode-7-1-replay "$M32_MODE_7_1_REPLAY" \
  --mode-1-7-primary "$M32_MODE_1_7_PRIMARY" \
  --mode-1-7-replay "$M32_MODE_1_7_REPLAY" \
  --generate \
  | tee "${M32_WORK_DIR}/m32-export-generation.json"

python frp_m32_deterministic_rtl_trace_export.py \
  --repository-root . \
  --output-root "$M32_OUTPUT_ROOT" \
  --mode-7-1-primary "$M32_MODE_7_1_PRIMARY" \
  --mode-7-1-replay "$M32_MODE_7_1_REPLAY" \
  --mode-1-7-primary "$M32_MODE_1_7_PRIMARY" \
  --mode-1-7-replay "$M32_MODE_1_7_REPLAY" \
  --verify \
  | tee "${M32_WORK_DIR}/m32-export-verification.json"
```

The self-test requires two byte-identical generation replays and four rejected
mutations. Verification requires the state `EXACT`.

Compare generated outputs with the tracked publication files:

```
cmp \
  "${M32_OUTPUT_ROOT}/schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json" \
  schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json
cmp \
  "${M32_OUTPUT_ROOT}/artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json" \
  artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json
cmp \
  "${M32_OUTPUT_ROOT}/artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json" \
  artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json
cmp \
  "${M32_OUTPUT_ROOT}/artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json" \
  artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json
```

Required raw file identities are:

| Output | Bytes | SHA-256 |
|---|---:|---|
| Schema | `34066` | `534db8227218184cac5d1cabb461dd63b1b61a99e0269c98535539ad3f7d7da2` |
| Trace bundle | `412195` | `62d8c1e6d205b9262a5c950883d3259275d5049f7a896ae12956a210cb75b7e0` |
| Manifest | `7211` | `da011dbc726d6d1fc0b7dbae12afe1e13d8240df64b9474fd0130c94ba005859` |
| Qualification | `4624` | `26ec2d3eadd73b490eb023572101bb78cf5d11561ead91b78b1a30e690458273` |

## Manual GitHub Actions execution

Run the workflows separately from the GitHub interface:

```
Actions
-> FRP M32 Registered Target Core
-> Run workflow
-> main
```

and:

```
Actions
-> FRP M32 Deterministic RTL Trace Export
-> Run workflow
-> main
```

Uploading or committing a workflow file does not start a
`workflow_dispatch` run. The selected workflow must be started manually.

## Evidence records

| Record | Path |
|---|---|
| Boundary specification | [`README.md`](README.md) |
| Artifact identities | [`ARTIFACTS.md`](ARTIFACTS.md) |
| Registered-target workflow | [`../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml`](../../.github/workflows/frp-m32-registered-target-boundary-workflow.yml) |
| Deterministic export workflow | [`../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml`](../../.github/workflows/frp-m32-deterministic-rtl-trace-export-workflow.yml) |
| Trace schema | [`../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json`](../../schemas/m32/frp.m32.deterministic_rtl_trace_bundle.v1.schema.json) |
| Trace bundle | [`../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json`](../../artifacts/m32/exports/m32-deterministic-rtl-trace-bundle.json) |
| Manifest | [`../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json`](../../artifacts/m32/manifests/m32-deterministic-rtl-trace-manifest.json) |
| Qualification | [`../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json`](../../artifacts/m32/qualification/m32-deterministic-rtl-trace-qualification.json) |

## Author

**Maksym Marnov (Alchimist)**  
Berlin, Germany  
ORCID: `0009-0000-0832-9597`
