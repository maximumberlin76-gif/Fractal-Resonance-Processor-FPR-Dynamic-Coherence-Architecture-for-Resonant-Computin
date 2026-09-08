// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic simulation trace monitor.

`ifndef FRP_M32_TRACE_MONITOR_SV
`define FRP_M32_TRACE_MONITOR_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m32_trace_monitor #(
  parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic trace_sample,
  input logic [63:0] source_tick,

  input logic tick_enable,
  input logic clear_counters,
  input logic phase_load_valid,
  input logic auto_target_enable,

  input logic [(CELLS*32)-1:0] gamma_effective_word,
  input logic [(CELLS*32)-1:0] thermal_node_factor_q30,

  input logic [(CELLS*32)-1:0] phase_word_q,
  input logic [(CELLS*32)-1:0] frequency_current_q16,
  input logic [(CELLS*32)-1:0] coupling_field_q16,
  input logic [(CELLS*32)-1:0] phase_projection_q30,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] phase_target_source,

  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] registered_target_q,
  input logic registered_target_valid_q,
  input logic phase_target_domain_valid,
  input logic registered_target_domain_valid,
  input logic target_capture_accepted,
  input logic target_capture_rejected,
  input logic [COUNTER_BITS-1:0] accepted_target_capture_events_q,
  input logic [COUNTER_BITS-1:0] rejected_target_capture_events_q,
  input logic registered_request_enable,

  input logic [REQUEST_LANES-1:0] phase_request_valid,
  input logic [
    (REQUEST_LANES*CELL_INDEX_BITS)-1:0
  ] phase_request_cell_index,
  input logic [
    (REQUEST_LANES*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] phase_request_target,

  input logic [REQUEST_LANES-1:0] execution_request_valid,
  input logic [
    (REQUEST_LANES*CELL_INDEX_BITS)-1:0
  ] execution_request_cell_index,
  input logic [
    (REQUEST_LANES*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] execution_request_target,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] execution_target_bank,

  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] state_out,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] pending_route_out,

  input frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode_q,
  input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state_q,
  input logic [COUNTER_BITS-1:0] ticks_recorded_q,
  input logic [COUNTER_BITS-1:0] scheduler_count_free_q,
  input logic [COUNTER_BITS-1:0] scheduler_count_balance_q,
  input logic [COUNTER_BITS-1:0] scheduler_count_commit_q,
  input logic [COUNTER_BITS-1:0] scheduler_count_excite_q,
  input logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q,

  input logic [REQUEST_LANES-1:0] request_accept,
  input logic [REQUEST_LANES-1:0] request_reject,
  input logic [CELLS-1:0] accepted_cell_mask,
  input logic [CELLS-1:0] neutral_routed_cell_mask,
  input logic [CELLS-1:0] accepted_change_mask,
  input logic [CELLS-1:0] first_route_leg_mask,
  input logic [CELLS-1:0] second_route_leg_mask,
  input logic [COUNTER_BITS-1:0] accepted_changes,
  input logic [COUNTER_BITS-1:0] capacity_remaining,
  input logic capacity_exhausted,
  input logic [COUNTER_BITS-1:0] switch_load_numerator,

  input logic [COUNTER_BITS-1:0] requested_direct_events,
  input logic [COUNTER_BITS-1:0] prevented_direct_events,
  input logic [COUNTER_BITS-1:0] neutral_routed_events,
  input logic [COUNTER_BITS-1:0] actual_direct_events,
  input logic [COUNTER_BITS-1:0] reserved_state_events,
  input logic [COUNTER_BITS-1:0] queue_overflow_events,
  input logic [
    frp_m31_pkg::FRP_M31_INVARIANT_FLAGS-1:0
  ] invariant_flags,

  input logic signed [31:0] pair_coherence_q30,
  input logic signed [31:0] cluster_coherence_q30,
  input logic signed [31:0] global_coherence_q30,
  input logic signed [31:0] organization_dispersion_q30,
  input logic signed [31:0] normalized_cycle_cost_q16,
  input logic signed [31:0] temperature_proxy_q16,
  input logic signed [31:0] peak_temperature_proxy_q16,
  input logic [31:0] thermal_sample_count_q,
  input logic signed [31:0] coherence_capacity_q16,
  input logic signed [31:0] pressure_q16,
  input logic signed [31:0] stability_margin_q16,
  input logic stable
);

  import frp_m31_pkg::*;

  integer cell_index;
  integer request_lane;

  function automatic integer ternary_value(
    input logic [FRP_M31_STATE_BITS-1:0] ternary_code
  );
    begin
      case (ternary_code)
        FRP_STATE_NEG:      ternary_value = -1;
        FRP_STATE_ZERO:     ternary_value = 0;
        FRP_STATE_POS:      ternary_value = 1;
        FRP_STATE_RESERVED: ternary_value = 2;
        default:            ternary_value = 3;
      endcase
    end
  endfunction

  initial begin
    if (CELLS < 1)
      $fatal(1, "FRP M32 trace monitor: CELLS must be positive");
    if (REQUEST_LANES < 1)
      $fatal(1, "FRP M32 trace monitor: REQUEST_LANES must be positive");
    if (CELL_INDEX_BITS < 1)
      $fatal(1, "FRP M32 trace monitor: CELL_INDEX_BITS must be positive");
    if (COUNTER_BITS < 1)
      $fatal(1, "FRP M32 trace monitor: COUNTER_BITS must be positive");
  end

  // The monitor is simulation-only. A testbench pulses trace_sample after the
  // sampled core outputs and the two route-leg masks are stable.
  always @(posedge trace_sample) begin
    $write(
      "M32_TRACE_SAMPLE source_tick=%0d tick_enable=%0d ",
      source_tick,
      tick_enable
    );
    $write(
      "clear_counters=%0d phase_load_valid=%0d auto_target_enable=%0d ",
      clear_counters,
      phase_load_valid,
      auto_target_enable
    );
    $write(
      "scheduler_mode=%0d scheduler_state=%0d ",
      scheduler_mode_q,
      scheduler_state_q
    );
    $write(
      "balance_tick=%0d commit_tick=%0d excite_tick=%0d neutralize_tick=%0d ",
      scheduler_state_q == FRP_SCHED_BALANCE,
      scheduler_state_q == FRP_SCHED_COMMIT,
      scheduler_state_q == FRP_SCHED_EXCITE,
      scheduler_state_q == FRP_SCHED_NEUTRALIZE
    );
    $write(
      "registered_target_valid=%0d phase_target_domain_valid=%0d ",
      registered_target_valid_q,
      phase_target_domain_valid
    );
    $write(
      "registered_target_domain_valid=%0d capture_accepted=%0d ",
      registered_target_domain_valid,
      target_capture_accepted
    );
    $write(
      "capture_rejected=%0d registered_request_enable=%0d ",
      target_capture_rejected,
      registered_request_enable
    );
    $write(
      "accepted_capture_events=%0d rejected_capture_events=%0d ",
      accepted_target_capture_events_q,
      rejected_target_capture_events_q
    );
    $write(
      "ticks_recorded=%0d scheduler_free=%0d scheduler_balance=%0d ",
      ticks_recorded_q,
      scheduler_count_free_q,
      scheduler_count_balance_q
    );
    $write(
      "scheduler_commit=%0d scheduler_excite=%0d scheduler_neutralize=%0d ",
      scheduler_count_commit_q,
      scheduler_count_excite_q,
      scheduler_count_neutralize_q
    );
    $write(
      "accepted_changes=%0d capacity_remaining=%0d capacity_exhausted=%0d ",
      accepted_changes,
      capacity_remaining,
      capacity_exhausted
    );
    $write(
      "switch_load_numerator=%0d requested_direct_events=%0d ",
      switch_load_numerator,
      requested_direct_events
    );
    $write(
      "prevented_direct_events=%0d neutral_routed_events=%0d ",
      prevented_direct_events,
      neutral_routed_events
    );
    $write(
      "actual_direct_events=%0d reserved_state_events=%0d ",
      actual_direct_events,
      reserved_state_events
    );
    $write(
      "queue_overflow_events=%0d invariant_flags=%0h invariant_all_valid=%0d ",
      queue_overflow_events,
      invariant_flags,
      invariant_flags == {FRP_M31_INVARIANT_FLAGS{1'b1}}
    );
    // The M31 interface-continuity signal names contain "coherence". Their
    // documented values are pair, cluster, and global phase-order magnitudes.
    $write(
      "pair_phase_order_q30=%0d cluster_phase_order_q30=%0d ",
      pair_coherence_q30,
      cluster_coherence_q30
    );
    $write(
      "global_phase_order_q30=%0d organization_dispersion_q30=%0d ",
      global_coherence_q30,
      organization_dispersion_q30
    );
    $write(
      "normalized_cycle_cost_q16=%0d temperature_proxy_q16=%0d ",
      normalized_cycle_cost_q16,
      temperature_proxy_q16
    );
    $write(
      "peak_temperature_proxy_q16=%0d thermal_sample_count=%0d ",
      peak_temperature_proxy_q16,
      thermal_sample_count_q
    );
    $display(
      "coherence_capacity_q16=%0d pressure_q16=%0d stability_margin_q16=%0d stable=%0d",
      coherence_capacity_q16,
      pressure_q16,
      stability_margin_q16,
      stable
    );

    $write(
      "M32_TRACE_BANK source_tick=%0d phase_target_source=%0h ",
      source_tick,
      phase_target_source
    );
    $write(
      "registered_target=%0h execution_target=%0h retained_state=%0h ",
      registered_target_q,
      execution_target_bank,
      state_out
    );
    $write(
      "pending_route=%0h accepted_cell_mask=%0h neutral_routed_cell_mask=%0h ",
      pending_route_out,
      accepted_cell_mask,
      neutral_routed_cell_mask
    );
    $display(
      "accepted_change_mask=%0h first_route_leg_mask=%0h second_route_leg_mask=%0h",
      accepted_change_mask,
      first_route_leg_mask,
      second_route_leg_mask
    );

    for (cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      $write(
        "M32_TRACE_CELL source_tick=%0d source_cell=%0d phase_word=%08h ",
        source_tick,
        cell_index,
        phase_word_q[(cell_index*32) +: 32]
      );
      $write(
        "frequency_current_q16=%0d gamma_effective_word=%08h ",
        $signed(frequency_current_q16[(cell_index*32) +: 32]),
        gamma_effective_word[(cell_index*32) +: 32]
      );
      $write(
        "thermal_node_factor_q30=%0d coupling_field_q16=%0d ",
        $signed(thermal_node_factor_q30[(cell_index*32) +: 32]),
        $signed(coupling_field_q16[(cell_index*32) +: 32])
      );
      $write(
        "phase_projection_q30=%0d source_target_code=%0h source_target_value=%0d ",
        $signed(phase_projection_q30[(cell_index*32) +: 32]),
        phase_target_source[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(phase_target_source[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ])
      );
      $write(
        "registered_target_code=%0h registered_target_value=%0d ",
        registered_target_q[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(registered_target_q[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ])
      );
      $write(
        "execution_target_code=%0h execution_target_value=%0d ",
        execution_target_bank[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(execution_target_bank[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ])
      );
      $write(
        "retained_state_code=%0h retained_state_value=%0d active_zero=%0d ",
        state_out[(cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS],
        ternary_value(state_out[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ]),
        state_out[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ] == FRP_ACTIVE_NEUTRAL
      );
      $write(
        "pending_target_code=%0h pending_target_value=%0d pending_active=%0d ",
        pending_route_out[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(pending_route_out[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ]),
        pending_route_out[
          (cell_index*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ] != FRP_STATE_ZERO
      );
      $write(
        "accepted_cell=%0d neutral_routed=%0d state_changed=%0d ",
        accepted_cell_mask[cell_index],
        neutral_routed_cell_mask[cell_index],
        accepted_change_mask[cell_index]
      );
      $display(
        "first_route_leg=%0d second_route_leg=%0d",
        first_route_leg_mask[cell_index],
        second_route_leg_mask[cell_index]
      );
    end

    for (
      request_lane = 0;
      request_lane < REQUEST_LANES;
      request_lane = request_lane + 1
    ) begin
      $write(
        "M32_TRACE_REQUEST source_tick=%0d request_lane=%0d phase_valid=%0d ",
        source_tick,
        request_lane,
        phase_request_valid[request_lane]
      );
      $write(
        "phase_cell=%0d phase_target_code=%0h phase_target_value=%0d ",
        phase_request_cell_index[
          (request_lane*CELL_INDEX_BITS) +: CELL_INDEX_BITS
        ],
        phase_request_target[
          (request_lane*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(phase_request_target[
          (request_lane*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ])
      );
      $write(
        "execution_valid=%0d execution_cell=%0d ",
        execution_request_valid[request_lane],
        execution_request_cell_index[
          (request_lane*CELL_INDEX_BITS) +: CELL_INDEX_BITS
        ]
      );
      $display(
        "execution_target_code=%0h execution_target_value=%0d accepted=%0d rejected=%0d",
        execution_request_target[
          (request_lane*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ],
        ternary_value(execution_request_target[
          (request_lane*FRP_M31_STATE_BITS) +: FRP_M31_STATE_BITS
        ]),
        request_accept[request_lane],
        request_reject[request_lane]
      );
    end
  end

endmodule

`endif
