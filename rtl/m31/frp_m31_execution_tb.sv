// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Deterministic Architectural RTL Testbench
//
// Project:
//   Fractal Resonance Processor (FRP)
//   Ternary Fractal Resonant Coherence Processor
//
// Version:
//   FRP v3.3.0
//
// Milestone:
//   M31 — RTL Core Realization and Execution Semantics Package
//
// Purpose:
//   Verifies the integrated executable RTL boundary against the inherited
//   processor architecture, including exact free / 7/1 / 1/7 tick semantics,
//   active-neutral balanced ternary routing, retained pending polarity,
//   transition capacity, and zero-event invariants.
`ifndef FRP_M31_EXECUTION_TB_SV
`define FRP_M31_EXECUTION_TB_SV
`timescale 1ns / 1ps
`include "frp_m31_pkg.sv"
`include "frp_m31_execution_core.sv"
`include "frp_m31_assertions.sv"
module frp_m31_execution_tb;
  import frp_m31_pkg::*;
  localparam int CELLS = 8;
  localparam int STATE_BITS = FRP_M31_STATE_BITS;
  localparam int REQUEST_LANES = frp_calc_request_lanes(CELLS);
  localparam int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS);
  localparam int COUNTER_BITS = FRP_M31_COUNTER_BITS;
  logic clk;
  logic rst_n;
  logic tick_enable;
  logic clear_counters;
  frp_m31_scheduler_mode_e scheduler_mode;
  logic [REQUEST_LANES-1:0] request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target;
  logic [(CELLS*STATE_BITS)-1:0] target_q;
  logic [(CELLS*STATE_BITS)-1:0] state_out;
  logic [(CELLS*STATE_BITS)-1:0] pending_route_out;
  frp_m31_scheduler_mode_e scheduler_mode_q;
  frp_m31_scheduler_state_e scheduler_state_q;
  logic [COUNTER_BITS-1:0] ticks_recorded_q;
  logic [COUNTER_BITS-1:0] scheduler_count_free_q;
  logic [COUNTER_BITS-1:0] scheduler_count_balance_q;
  logic [COUNTER_BITS-1:0] scheduler_count_commit_q;
  logic [COUNTER_BITS-1:0] scheduler_count_excite_q;
  logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q;
  logic [REQUEST_LANES-1:0] request_accept;
  logic [REQUEST_LANES-1:0] request_reject;
  logic [CELLS-1:0] accepted_cell_mask;
  logic [CELLS-1:0] neutral_routed_cell_mask;
  logic [CELLS-1:0] accepted_change_mask;
  logic [COUNTER_BITS-1:0] accepted_changes;
  logic [COUNTER_BITS-1:0] capacity_remaining;
  logic capacity_exhausted;
  logic [COUNTER_BITS-1:0] switch_load_numerator;
  logic [COUNTER_BITS-1:0] requested_direct_events;
  logic [COUNTER_BITS-1:0] prevented_direct_events;
  logic [COUNTER_BITS-1:0] neutral_routed_events;
  logic [COUNTER_BITS-1:0] actual_direct_events;
  logic [COUNTER_BITS-1:0] reserved_state_events;
  logic [COUNTER_BITS-1:0] queue_overflow_events;
  logic [FRP_M31_INVARIANT_FLAGS-1:0] invariant_flags;
  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end
  frp_m31_execution_core #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .request_valid(request_valid),
    .request_cell_index(request_cell_index),
    .request_target(request_target),
    .target_q(target_q),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q),
    .request_accept(request_accept),
    .request_reject(request_reject),
    .accepted_cell_mask(accepted_cell_mask),
    .neutral_routed_cell_mask(neutral_routed_cell_mask),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .capacity_remaining(capacity_remaining),
    .capacity_exhausted(capacity_exhausted),
    .switch_load_numerator(switch_load_numerator),
    .requested_direct_events(requested_direct_events),
    .prevented_direct_events(prevented_direct_events),
    .neutral_routed_events(neutral_routed_events),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags)
  );
  frp_m31_assertions #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .COUNTER_BITS(COUNTER_BITS)
  ) assertions (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .request_accept(request_accept),
    .request_reject(request_reject),
    .accepted_cell_mask(accepted_cell_mask),
    .neutral_routed_cell_mask(neutral_routed_cell_mask),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .capacity_remaining(capacity_remaining),
    .capacity_exhausted(capacity_exhausted),
    .switch_load_numerator(switch_load_numerator),
    .requested_direct_events(requested_direct_events),
    .prevented_direct_events(prevented_direct_events),
    .neutral_routed_events(neutral_routed_events),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags)
  );
  function automatic logic [STATE_BITS-1:0] packed_cell_value(
    input logic [(CELLS*STATE_BITS)-1:0] packed_value,
    input int element_index
  );
    begin
      packed_cell_value = packed_value[
        (element_index*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction
  task automatic clear_requests;
    begin
      request_valid = '0;
      request_cell_index = '0;
      request_target = '0;
      target_q = '0;
    end
  endtask
  task automatic set_lane(
    input int lane_index,
    input int element_index,
    input logic [STATE_BITS-1:0] target_value
  );
    begin
      request_valid[lane_index] = 1'b1;
      request_cell_index[
        (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
      ] = element_index[CELL_INDEX_BITS-1:0];
      request_target[
        (lane_index*STATE_BITS) +: STATE_BITS
      ] = target_value;
      target_q[
        (element_index*STATE_BITS) +: STATE_BITS
      ] = target_value;
    end
  endtask
  task automatic apply_reset(
    input frp_m31_scheduler_mode_e selected_mode
  );
    begin
      tick_enable = 1'b0;
      clear_counters = 1'b0;
      scheduler_mode = selected_mode;
      clear_requests();
      rst_n = 1'b0;
      repeat (3) @(negedge clk);
      rst_n = 1'b1;
      repeat (2) @(negedge clk);
      #1;
      if (state_out !== '0) begin
        $fatal(1, "FRP M31 TB: reset state is not active neutral zero");
      end
      if (pending_route_out !== '0) begin
        $fatal(1, "FRP M31 TB: reset pending-route bank is not zero");
      end
      if (ticks_recorded_q !== '0) begin
        $fatal(1, "FRP M31 TB: reset scheduler counter is not zero");
      end
    end
  endtask
  task automatic start_tick(
    input frp_m31_scheduler_state_e expected_state
  );
    begin
      @(negedge clk);
      if (scheduler_state_q !== expected_state) begin
        $fatal(
          1,
          "FRP M31 TB: scheduler state mismatch, expected=%0d actual=%0d",
          expected_state,
          scheduler_state_q
        );
      end
      tick_enable = 1'b1;
      #1;
    end
  endtask
  task automatic finish_tick;
    begin
      @(negedge clk);
      tick_enable = 1'b0;
      #1;
    end
  endtask
  task automatic expect_cell(
    input int element_index,
    input logic [STATE_BITS-1:0] expected_state,
    input logic [STATE_BITS-1:0] expected_pending
  );
    begin
      if (
        packed_cell_value(state_out, element_index)
        !== expected_state
      ) begin
        $fatal(1, "FRP M31 TB: retained state mismatch at element_index %0d", element_index);
      end
      if (
        packed_cell_value(pending_route_out, element_index)
        !== expected_pending
      ) begin
        $fatal(1, "FRP M31 TB: pending route mismatch at element_index %0d", element_index);
      end
    end
  endtask
  task automatic expect_zero_events_and_flags;
    begin
      if (actual_direct_events !== '0) begin
        $fatal(1, "FRP M31 TB: actual_direct_events is nonzero");
      end
      if (reserved_state_events !== '0) begin
        $fatal(1, "FRP M31 TB: reserved_state_events is nonzero");
      end
      if (queue_overflow_events !== '0) begin
        $fatal(1, "FRP M31 TB: queue_overflow_events is nonzero");
      end
      if (invariant_flags !== {FRP_M31_INVARIANT_FLAGS{1'b1}}) begin
        $fatal(1, "FRP M31 TB: integrated invariant flag set is incomplete");
      end
    end
  endtask
  task automatic clear_counter_bank_without_state_reset;
    logic [(CELLS*STATE_BITS)-1:0] state_snapshot;
    logic [(CELLS*STATE_BITS)-1:0] pending_snapshot;
    begin
      state_snapshot = state_out;
      pending_snapshot = pending_route_out;
      @(negedge clk);
      clear_counters = 1'b1;
      tick_enable = 1'b0;
      @(negedge clk);
      clear_counters = 1'b0;
      #1;
      if (ticks_recorded_q !== '0) begin
        $fatal(1, "FRP M31 TB: clear_counters did not clear ticks_recorded");
      end
      if (
        scheduler_count_free_q !== '0
        || scheduler_count_balance_q !== '0
        || scheduler_count_commit_q !== '0
        || scheduler_count_excite_q !== '0
        || scheduler_count_neutralize_q !== '0
      ) begin
        $fatal(1, "FRP M31 TB: clear_counters did not clear scheduler counts");
      end
      if (state_out !== state_snapshot) begin
        $fatal(1, "FRP M31 TB: clear_counters changed retained state");
      end
      if (pending_route_out !== pending_snapshot) begin
        $fatal(1, "FRP M31 TB: clear_counters changed pending routes");
      end
    end
  endtask
  initial begin
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    scheduler_mode = FRP_MODE_FREE;
    clear_requests();
    // Free: exact 16 free ticks, both neutral-route directions and capacity.
    apply_reset(FRP_MODE_FREE);
    for (int tick = 0; tick < 16; tick++) begin
      clear_requests();
      if (tick == 0) begin
        set_lane(0, 0, FRP_STATE_POS);
      end else if (tick == 1) begin
        set_lane(0, 0, FRP_STATE_NEG);
      end else if (tick == 3) begin
        set_lane(0, 0, FRP_STATE_POS);
      end else if (tick == 5) begin
        set_lane(0, 1, FRP_STATE_POS);
        set_lane(1, 2, FRP_STATE_POS);
      end
      start_tick(FRP_SCHED_FREE);
      if (tick == 1 || tick == 3) begin
        if (
          neutral_routed_cell_mask[0] !== 1'b1
          || requested_direct_events !== 1
          || prevented_direct_events !== 1
          || neutral_routed_events !== 1
          || actual_direct_events !== 0
        ) begin
          $fatal(1, "FRP M31 TB: free-mode active-neutral routing mismatch");
        end
      end
      if (tick == 5) begin
        if (
          accepted_changes !== 2
          || capacity_remaining !== 0
          || capacity_exhausted !== 1'b1
          || switch_load_numerator !== 2
        ) begin
          $fatal(1, "FRP M31 TB: two-lane capacity relation mismatch");
        end
      end
      finish_tick();
      if (tick == 0) begin
        expect_cell(0, FRP_STATE_POS, FRP_STATE_ZERO);
      end else if (tick == 1) begin
        expect_cell(0, FRP_STATE_ZERO, FRP_STATE_NEG);
      end else if (tick == 2) begin
        expect_cell(0, FRP_STATE_NEG, FRP_STATE_ZERO);
      end else if (tick == 3) begin
        expect_cell(0, FRP_STATE_ZERO, FRP_STATE_POS);
      end else if (tick == 4) begin
        expect_cell(0, FRP_STATE_POS, FRP_STATE_ZERO);
      end else if (tick == 5) begin
        expect_cell(1, FRP_STATE_POS, FRP_STATE_ZERO);
        expect_cell(2, FRP_STATE_POS, FRP_STATE_ZERO);
      end
      expect_zero_events_and_flags();
    end
    if (
      ticks_recorded_q !== 16
      || scheduler_count_free_q !== 16
      || scheduler_count_balance_q !== 0
      || scheduler_count_commit_q !== 0
      || scheduler_count_excite_q !== 0
      || scheduler_count_neutralize_q !== 0
    ) begin
      $fatal(1, "FRP M31 TB: free-mode 16-tick profile mismatch");
    end
    clear_counter_bank_without_state_reset();
    expect_zero_events_and_flags();
    // 7/1: ticks 0-6 balance, tick 7 commit, repeated for 64 ticks.
    apply_reset(FRP_MODE_7_1);
    for (int tick = 0; tick < 64; tick++) begin
      clear_requests();
      if (tick <= 7) begin
        set_lane(0, 0, FRP_STATE_POS);
      end else if (tick == 8) begin
        set_lane(0, 0, FRP_STATE_NEG);
      end
      start_tick(
        ((tick % 8) == 7)
          ? FRP_SCHED_COMMIT
          : FRP_SCHED_BALANCE
      );
      if (tick < 7) begin
        if (request_accept !== '0 || request_reject[0] !== 1'b1) begin
          $fatal(1, "FRP M31 TB: 7/1 balance admitted zero release");
        end
      end
      if (tick == 7 && request_accept[0] !== 1'b1) begin
        $fatal(1, "FRP M31 TB: 7/1 commit rejected zero release");
      end
      if (tick == 8 && neutral_routed_cell_mask[0] !== 1'b1) begin
        $fatal(1, "FRP M31 TB: 7/1 balance rejected active-neutral route");
      end
      finish_tick();
      if (tick < 7) begin
        expect_cell(0, FRP_STATE_ZERO, FRP_STATE_ZERO);
      end else if (tick == 7) begin
        expect_cell(0, FRP_STATE_POS, FRP_STATE_ZERO);
      end else if (tick >= 8 && tick < 15) begin
        expect_cell(0, FRP_STATE_ZERO, FRP_STATE_NEG);
      end else if (tick >= 15) begin
        expect_cell(0, FRP_STATE_NEG, FRP_STATE_ZERO);
      end
      expect_zero_events_and_flags();
    end
    if (
      ticks_recorded_q !== 64
      || scheduler_count_balance_q !== 56
      || scheduler_count_commit_q !== 8
      || scheduler_count_free_q !== 0
      || scheduler_count_excite_q !== 0
      || scheduler_count_neutralize_q !== 0
    ) begin
      $fatal(1, "FRP M31 TB: 7/1 64-tick profile mismatch");
    end
    // 1/7: tick 0 excite, ticks 1-7 neutralize, repeated for 16 ticks.
    apply_reset(FRP_MODE_1_7);
    for (int tick = 0; tick < 16; tick++) begin
      clear_requests();
      if (tick == 0) begin
        set_lane(0, 0, FRP_STATE_POS);
      end else if (tick == 1) begin
        set_lane(0, 0, FRP_STATE_NEG);
      end
      start_tick(
        ((tick % 8) == 0)
          ? FRP_SCHED_EXCITE
          : FRP_SCHED_NEUTRALIZE
      );
      if (tick == 0 && request_accept[0] !== 1'b1) begin
        $fatal(1, "FRP M31 TB: 1/7 excite rejected zero release");
      end
      if (tick == 1 && neutral_routed_cell_mask[0] !== 1'b1) begin
        $fatal(1, "FRP M31 TB: 1/7 neutralize rejected active-neutral route");
      end
      finish_tick();
      if (tick == 0) begin
        expect_cell(0, FRP_STATE_POS, FRP_STATE_ZERO);
      end else if (tick >= 1 && tick < 8) begin
        expect_cell(0, FRP_STATE_ZERO, FRP_STATE_NEG);
      end else if (tick >= 8) begin
        expect_cell(0, FRP_STATE_NEG, FRP_STATE_ZERO);
      end
      expect_zero_events_and_flags();
    end
    if (
      ticks_recorded_q !== 16
      || scheduler_count_excite_q !== 2
      || scheduler_count_neutralize_q !== 14
      || scheduler_count_free_q !== 0
      || scheduler_count_balance_q !== 0
      || scheduler_count_commit_q !== 0
    ) begin
      $fatal(1, "FRP M31 TB: 1/7 16-tick profile mismatch");
    end
    $display("FRP M31 deterministic RTL testbench completed.");
    $display("CELLS=%0d REQUEST_LANES=%0d", CELLS, REQUEST_LANES);
    $display("ticks_recorded=%0d", ticks_recorded_q);
    $display("actual_direct_events=%0d", actual_direct_events);
    $display("reserved_state_events=%0d", reserved_state_events);
    $display("queue_overflow_events=%0d", queue_overflow_events);
    $finish;
  end
endmodule : frp_m31_execution_tb
`endif
