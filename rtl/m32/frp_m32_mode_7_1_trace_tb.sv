// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic full-trace composition for scheduler mode 7/1.

`ifndef FRP_M32_MODE_7_1_TRACE_TB_SV
`define FRP_M32_MODE_7_1_TRACE_TB_SV

`timescale 1ns / 1ps

`include "frp_m32_mode_7_1_tb.sv"
`include "frp_m32_trace_monitor.sv"

module frp_m32_mode_7_1_trace_tb;

  import frp_m31_pkg::*;

  localparam int CELLS = 8;
  localparam int STATE_BITS = FRP_M31_STATE_BITS;
  localparam int REQUEST_LANES = frp_calc_request_lanes(CELLS);
  localparam int CELL_INDEX_BITS = $clog2(CELLS);
  localparam int COUNTER_BITS = FRP_M31_COUNTER_BITS;
  localparam logic [63:0] EXPECTED_TRACE_SAMPLES = 64'd16;

  logic trace_sample;
  logic [63:0] trace_source_tick;
  logic trace_tick_enable;
  logic trace_clear_counters;
  logic trace_phase_load_valid;
  logic trace_auto_target_enable;

  logic [(CELLS*32)-1:0] trace_phase_word_q;
  logic [(CELLS*32)-1:0] trace_frequency_current_q16;
  logic [(CELLS*32)-1:0] trace_coupling_field_q16;
  logic [(CELLS*32)-1:0] trace_phase_projection_q30;
  logic [(CELLS*STATE_BITS)-1:0] trace_phase_target_source;

  logic [(CELLS*STATE_BITS)-1:0] trace_registered_target_q;
  logic trace_registered_target_valid_q;
  logic trace_phase_target_domain_valid;
  logic trace_registered_target_domain_valid;
  logic trace_target_capture_accepted;
  logic trace_target_capture_rejected;
  logic trace_registered_request_enable;

  logic [REQUEST_LANES-1:0] trace_phase_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    trace_phase_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] trace_phase_request_target;

  logic [REQUEST_LANES-1:0] trace_execution_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    trace_execution_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0]
    trace_execution_request_target;
  logic [(CELLS*STATE_BITS)-1:0] trace_execution_target_bank;

  frp_m31_scheduler_mode_e trace_scheduler_mode_q;
  frp_m31_scheduler_state_e trace_scheduler_state_q;
  logic [REQUEST_LANES-1:0] trace_request_accept;
  logic [REQUEST_LANES-1:0] trace_request_reject;
  logic [CELLS-1:0] trace_accepted_cell_mask;
  logic [CELLS-1:0] trace_neutral_routed_cell_mask;
  logic [CELLS-1:0] trace_accepted_change_mask;
  logic [CELLS-1:0] trace_first_route_leg_mask;
  logic [CELLS-1:0] trace_second_route_leg_mask;
  logic [COUNTER_BITS-1:0] trace_accepted_changes;
  logic [COUNTER_BITS-1:0] trace_capacity_remaining;
  logic trace_capacity_exhausted;
  logic [COUNTER_BITS-1:0] trace_switch_load_numerator;

  frp_m32_mode_7_1_tb mode_7_1_testbench();

  frp_m32_trace_monitor #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) trace_monitor (
    .trace_sample(trace_sample),
    .source_tick(trace_source_tick),
    .tick_enable(trace_tick_enable),
    .clear_counters(trace_clear_counters),
    .phase_load_valid(trace_phase_load_valid),
    .auto_target_enable(trace_auto_target_enable),
    .gamma_effective_word(mode_7_1_testbench.gamma_effective_word),
    .thermal_node_factor_q30(
      mode_7_1_testbench.thermal_node_factor_q30
    ),
    .phase_word_q(trace_phase_word_q),
    .frequency_current_q16(trace_frequency_current_q16),
    .coupling_field_q16(trace_coupling_field_q16),
    .phase_projection_q30(trace_phase_projection_q30),
    .phase_target_source(trace_phase_target_source),
    .registered_target_q(trace_registered_target_q),
    .registered_target_valid_q(trace_registered_target_valid_q),
    .phase_target_domain_valid(trace_phase_target_domain_valid),
    .registered_target_domain_valid(trace_registered_target_domain_valid),
    .target_capture_accepted(trace_target_capture_accepted),
    .target_capture_rejected(trace_target_capture_rejected),
    .accepted_target_capture_events_q(
      mode_7_1_testbench.accepted_target_capture_events_q
    ),
    .rejected_target_capture_events_q(
      mode_7_1_testbench.rejected_target_capture_events_q
    ),
    .registered_request_enable(trace_registered_request_enable),
    .phase_request_valid(trace_phase_request_valid),
    .phase_request_cell_index(trace_phase_request_cell_index),
    .phase_request_target(trace_phase_request_target),
    .execution_request_valid(trace_execution_request_valid),
    .execution_request_cell_index(trace_execution_request_cell_index),
    .execution_request_target(trace_execution_request_target),
    .execution_target_bank(trace_execution_target_bank),
    .state_out(mode_7_1_testbench.state_out),
    .pending_route_out(mode_7_1_testbench.pending_route_out),
    .scheduler_mode_q(trace_scheduler_mode_q),
    .scheduler_state_q(trace_scheduler_state_q),
    .ticks_recorded_q(mode_7_1_testbench.ticks_recorded_q),
    .scheduler_count_free_q(
      mode_7_1_testbench.scheduler_count_free_q
    ),
    .scheduler_count_balance_q(
      mode_7_1_testbench.scheduler_count_balance_q
    ),
    .scheduler_count_commit_q(
      mode_7_1_testbench.scheduler_count_commit_q
    ),
    .scheduler_count_excite_q(
      mode_7_1_testbench.scheduler_count_excite_q
    ),
    .scheduler_count_neutralize_q(
      mode_7_1_testbench.scheduler_count_neutralize_q
    ),
    .request_accept(trace_request_accept),
    .request_reject(trace_request_reject),
    .accepted_cell_mask(trace_accepted_cell_mask),
    .neutral_routed_cell_mask(trace_neutral_routed_cell_mask),
    .accepted_change_mask(trace_accepted_change_mask),
    .first_route_leg_mask(trace_first_route_leg_mask),
    .second_route_leg_mask(trace_second_route_leg_mask),
    .accepted_changes(trace_accepted_changes),
    .capacity_remaining(trace_capacity_remaining),
    .capacity_exhausted(trace_capacity_exhausted),
    .switch_load_numerator(trace_switch_load_numerator),
    .requested_direct_events(
      mode_7_1_testbench.requested_direct_events
    ),
    .prevented_direct_events(
      mode_7_1_testbench.prevented_direct_events
    ),
    .neutral_routed_events(mode_7_1_testbench.neutral_routed_events),
    .actual_direct_events(mode_7_1_testbench.actual_direct_events),
    .reserved_state_events(mode_7_1_testbench.reserved_state_events),
    .queue_overflow_events(mode_7_1_testbench.queue_overflow_events),
    .invariant_flags(mode_7_1_testbench.invariant_flags),
    .pair_coherence_q30(mode_7_1_testbench.pair_coherence_q30),
    .cluster_coherence_q30(mode_7_1_testbench.cluster_coherence_q30),
    .global_coherence_q30(mode_7_1_testbench.global_coherence_q30),
    .organization_dispersion_q30(
      mode_7_1_testbench.organization_dispersion_q30
    ),
    .normalized_cycle_cost_q16(
      mode_7_1_testbench.normalized_cycle_cost_q16
    ),
    .temperature_proxy_q16(mode_7_1_testbench.temperature_proxy_q16),
    .peak_temperature_proxy_q16(
      mode_7_1_testbench.peak_temperature_proxy_q16
    ),
    .thermal_sample_count_q(mode_7_1_testbench.thermal_sample_count_q),
    .coherence_capacity_q16(
      mode_7_1_testbench.coherence_capacity_q16
    ),
    .pressure_q16(mode_7_1_testbench.pressure_q16),
    .stability_margin_q16(mode_7_1_testbench.stability_margin_q16),
    .stable(mode_7_1_testbench.stable)
  );

  function automatic logic [STATE_BITS-1:0] trace_cell_state(
    input logic [(CELLS*STATE_BITS)-1:0] packed_state,
    input int cell_index
  );
    begin
      trace_cell_state = packed_state[
        (cell_index*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction

  initial begin
    trace_sample = 1'b0;
    trace_source_tick = '0;
    trace_tick_enable = 1'b0;
    trace_clear_counters = 1'b0;
    trace_phase_load_valid = 1'b0;
    trace_auto_target_enable = 1'b0;
    trace_phase_word_q = '0;
    trace_frequency_current_q16 = '0;
    trace_coupling_field_q16 = '0;
    trace_phase_projection_q30 = '0;
    trace_phase_target_source = '0;
    trace_registered_target_q = '0;
    trace_registered_target_valid_q = 1'b0;
    trace_phase_target_domain_valid = 1'b0;
    trace_registered_target_domain_valid = 1'b0;
    trace_target_capture_accepted = 1'b0;
    trace_target_capture_rejected = 1'b0;
    trace_registered_request_enable = 1'b0;
    trace_phase_request_valid = '0;
    trace_phase_request_cell_index = '0;
    trace_phase_request_target = '0;
    trace_execution_request_valid = '0;
    trace_execution_request_cell_index = '0;
    trace_execution_request_target = '0;
    trace_execution_target_bank = '0;
    trace_scheduler_mode_q = FRP_MODE_FREE;
    trace_scheduler_state_q = FRP_SCHED_FREE;
    trace_request_accept = '0;
    trace_request_reject = '0;
    trace_accepted_cell_mask = '0;
    trace_neutral_routed_cell_mask = '0;
    trace_accepted_change_mask = '0;
    trace_first_route_leg_mask = '0;
    trace_second_route_leg_mask = '0;
    trace_accepted_changes = '0;
    trace_capacity_remaining = '0;
    trace_capacity_exhausted = 1'b0;
    trace_switch_load_numerator = '0;
  end

  // Source, boundary, scheduler, request, route, phase, and capacity fields
  // are captured before the active execution edge. Retained state, pending
  // route, counters, invariant state, thermal state, and stability state are
  // sampled by the monitor after that edge.
  /* verilator lint_off BLKSEQ */
  always @(negedge mode_7_1_testbench.clk) begin : trace_transaction
    #2;

    if (mode_7_1_testbench.tick_enable) begin : enabled_trace_transaction
      if (trace_source_tick >= EXPECTED_TRACE_SAMPLES)
        $fatal(1, "FRP M32 7/1 trace TB: excess trace sample");

      trace_tick_enable = mode_7_1_testbench.tick_enable;
      trace_clear_counters = mode_7_1_testbench.clear_counters;
      trace_phase_load_valid = mode_7_1_testbench.phase_load_valid;
      trace_auto_target_enable = mode_7_1_testbench.auto_target_enable;
      trace_phase_word_q = mode_7_1_testbench.phase_word_q;
      trace_frequency_current_q16 =
        mode_7_1_testbench.frequency_current_q16;
      trace_coupling_field_q16 = mode_7_1_testbench.coupling_field_q16;
      trace_phase_projection_q30 =
        mode_7_1_testbench.phase_projection_q30;
      trace_phase_target_source = mode_7_1_testbench.phase_target_source;
      trace_registered_target_q = mode_7_1_testbench.registered_target_q;
      trace_registered_target_valid_q =
        mode_7_1_testbench.registered_target_valid_q;
      trace_phase_target_domain_valid =
        mode_7_1_testbench.phase_target_domain_valid;
      trace_registered_target_domain_valid =
        mode_7_1_testbench.registered_target_domain_valid;
      trace_target_capture_accepted =
        mode_7_1_testbench.target_capture_accepted;
      trace_target_capture_rejected =
        mode_7_1_testbench.target_capture_rejected;
      trace_registered_request_enable =
        mode_7_1_testbench.registered_request_enable;
      trace_phase_request_valid = mode_7_1_testbench.phase_request_valid;
      trace_phase_request_cell_index =
        mode_7_1_testbench.phase_request_cell_index;
      trace_phase_request_target = mode_7_1_testbench.phase_request_target;
      trace_execution_request_valid =
        mode_7_1_testbench.execution_request_valid;
      trace_execution_request_cell_index =
        mode_7_1_testbench.execution_request_cell_index;
      trace_execution_request_target =
        mode_7_1_testbench.execution_request_target;
      trace_execution_target_bank =
        mode_7_1_testbench.execution_target_bank;
      trace_scheduler_mode_q = mode_7_1_testbench.scheduler_mode_q;
      trace_scheduler_state_q = mode_7_1_testbench.scheduler_state_q;
      trace_request_accept = mode_7_1_testbench.request_accept;
      trace_request_reject = mode_7_1_testbench.request_reject;
      trace_accepted_cell_mask = mode_7_1_testbench.accepted_cell_mask;
      trace_neutral_routed_cell_mask =
        mode_7_1_testbench.neutral_routed_cell_mask;
      trace_accepted_change_mask =
        mode_7_1_testbench.accepted_change_mask;
      trace_first_route_leg_mask =
        mode_7_1_testbench.neutral_routed_cell_mask;
      trace_second_route_leg_mask = '0;

      for (int cell_index = 0; cell_index < CELLS; cell_index++) begin
        trace_second_route_leg_mask[cell_index] =
          mode_7_1_testbench.accepted_change_mask[cell_index]
          && (trace_cell_state(mode_7_1_testbench.state_out, cell_index)
            == FRP_ACTIVE_NEUTRAL)
          && (trace_cell_state(
            mode_7_1_testbench.pending_route_out,
            cell_index
          ) != FRP_STATE_ZERO);
      end

      trace_accepted_changes = mode_7_1_testbench.accepted_changes;
      trace_capacity_remaining = mode_7_1_testbench.capacity_remaining;
      trace_capacity_exhausted = mode_7_1_testbench.capacity_exhausted;
      trace_switch_load_numerator =
        mode_7_1_testbench.switch_load_numerator;

      @(posedge mode_7_1_testbench.clk);
      #1;
      trace_sample = 1'b1;
      #1;
      trace_sample = 1'b0;
      trace_source_tick = trace_source_tick + 64'd1;

      if (trace_source_tick == EXPECTED_TRACE_SAMPLES) begin
        $display(
          "FRP_M32_MODE_7_1_TRACE_TB: PASS samples=%0d",
          trace_source_tick
        );
      end
    end
  end
  /* verilator lint_on BLKSEQ */

endmodule

`endif
