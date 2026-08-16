// SPDX-License-Identifier: Apache-2.0
//
// FRP M19 Machine-Readable M16 Evidence Monitors
//
// These monitors observe the qualified M16 RTL and FPGA-preparation
// testbenches without modifying their source files or execution semantics.

`ifndef FRP_M19_M16_EVIDENCE_MONITORS_SV
`define FRP_M19_M16_EVIDENCE_MONITORS_SV

`timescale 1ns / 1ps

`include "frp_m16_tb.sv"
`include "frp_m16_fpga_tb.sv"

module frp_m19_rtl_evidence_tb;

  localparam int CELLS = 8;
  localparam int STATE_BITS = 2;
  localparam int REQUEST_LANES = 2;
  localparam int CELL_INDEX_BITS = 3;
  localparam int COUNTER_BITS = 32;
  localparam int INVARIANT_FLAGS = 10;
  localparam int EXPECTED_RECORDS = 96;

  frp_m16_tb source();

  integer evidence_sequence;
  logic capture_valid;
  logic core_ready_pre;
  logic [1:0] scheduler_mode_pre;
  logic [2:0] scheduler_state_pre;
  logic [COUNTER_BITS-1:0] ticks_before;
  logic [REQUEST_LANES-1:0] request_valid_pre;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    request_cell_index_pre;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target_pre;
  logic [(CELLS*STATE_BITS)-1:0] phase_target_pre;
  logic [(CELLS*STATE_BITS)-1:0] state_before;
  logic [(CELLS*STATE_BITS)-1:0] pending_before;
  logic [REQUEST_LANES-1:0] request_accept_pre;
  logic [REQUEST_LANES-1:0] request_reject_pre;
  logic [CELLS-1:0] accepted_cell_mask_pre;
  logic [CELLS-1:0] neutral_routed_cell_mask_pre;
  logic [CELLS-1:0] accepted_change_mask_pre;
  logic [COUNTER_BITS-1:0] accepted_changes_pre;
  logic [COUNTER_BITS-1:0] capacity_remaining_pre;
  logic capacity_exhausted_pre;
  logic [COUNTER_BITS-1:0] switch_load_numerator_pre;
  logic [COUNTER_BITS-1:0] requested_direct_events_pre;
  logic [COUNTER_BITS-1:0] prevented_direct_events_pre;
  logic [COUNTER_BITS-1:0] neutral_routed_events_pre;
  logic [COUNTER_BITS-1:0] actual_direct_events_pre;
  logic [COUNTER_BITS-1:0] reserved_state_events_pre;
  logic [COUNTER_BITS-1:0] queue_overflow_events_pre;
  logic [INVARIANT_FLAGS-1:0] invariant_flags_pre;

  initial begin
    evidence_sequence = 0;
    capture_valid = 1'b0;
  end

  always @(negedge source.clk) begin
    #2;
    if (source.tick_enable === 1'b1) begin
      if (capture_valid !== 1'b0) begin
        $fatal(1, "FRP M19 RTL monitor: overlapping tick capture");
      end
      if (evidence_sequence >= EXPECTED_RECORDS) begin
        $fatal(1, "FRP M19 RTL monitor: unexpected extra tick");
      end
      capture_valid = 1'b1;
      core_ready_pre = 1'b1;
      scheduler_mode_pre = source.scheduler_mode_q;
      scheduler_state_pre = source.scheduler_state_q;
      ticks_before = source.ticks_recorded_q;
      request_valid_pre = source.request_valid;
      request_cell_index_pre = source.request_cell_index;
      request_target_pre = source.request_target;
      phase_target_pre = source.target_q;
      state_before = source.state_out;
      pending_before = source.pending_route_out;
      request_accept_pre = source.request_accept;
      request_reject_pre = source.request_reject;
      accepted_cell_mask_pre = source.accepted_cell_mask;
      neutral_routed_cell_mask_pre =
        source.neutral_routed_cell_mask;
      accepted_change_mask_pre = source.accepted_change_mask;
      accepted_changes_pre = source.accepted_changes;
      capacity_remaining_pre = source.capacity_remaining;
      capacity_exhausted_pre = source.capacity_exhausted;
      switch_load_numerator_pre = source.switch_load_numerator;
      requested_direct_events_pre = source.requested_direct_events;
      prevented_direct_events_pre = source.prevented_direct_events;
      neutral_routed_events_pre = source.neutral_routed_events;
      actual_direct_events_pre = source.actual_direct_events;
      reserved_state_events_pre = source.reserved_state_events;
      queue_overflow_events_pre = source.queue_overflow_events;
      invariant_flags_pre = source.invariant_flags;
    end
  end

  always @(posedge source.clk) begin
    #1;
    if (capture_valid === 1'b1) begin
      $display(
        "FRP_M19|1|rtl|%0d|%0d|%0h|%0h|%0d|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0h|%0h|%0h|%0d|%0d|%0d|%0d|%0d|%0d",
        evidence_sequence,
        core_ready_pre,
        scheduler_mode_pre,
        scheduler_state_pre,
        ticks_before,
        request_valid_pre,
        request_cell_index_pre,
        request_target_pre,
        phase_target_pre,
        state_before,
        pending_before,
        request_accept_pre,
        request_reject_pre,
        accepted_cell_mask_pre,
        neutral_routed_cell_mask_pre,
        accepted_change_mask_pre,
        accepted_changes_pre,
        capacity_remaining_pre,
        capacity_exhausted_pre,
        switch_load_numerator_pre,
        requested_direct_events_pre,
        prevented_direct_events_pre,
        neutral_routed_events_pre,
        actual_direct_events_pre,
        reserved_state_events_pre,
        queue_overflow_events_pre,
        invariant_flags_pre,
        source.state_out,
        source.pending_route_out,
        source.ticks_recorded_q,
        source.scheduler_count_free_q,
        source.scheduler_count_balance_q,
        source.scheduler_count_commit_q,
        source.scheduler_count_excite_q,
        source.scheduler_count_neutralize_q
      );
      evidence_sequence = evidence_sequence + 1;
      capture_valid = 1'b0;
      if (evidence_sequence == EXPECTED_RECORDS) begin
        $display("FRP M19 RTL evidence records=96");
      end
    end
  end

endmodule : frp_m19_rtl_evidence_tb

module frp_m19_fpga_evidence_tb;

  localparam int CELLS = 8;
  localparam int STATE_BITS = 2;
  localparam int REQUEST_LANES = 2;
  localparam int CELL_INDEX_BITS = 3;
  localparam int COUNTER_BITS = 32;
  localparam int INVARIANT_FLAGS = 10;
  localparam int EXPECTED_RECORDS = 4;

  frp_m16_fpga_tb source();

  integer evidence_sequence;
  logic capture_valid;
  logic core_ready_pre;
  logic [1:0] scheduler_mode_pre;
  logic [2:0] scheduler_state_pre;
  logic [COUNTER_BITS-1:0] ticks_before;
  logic [REQUEST_LANES-1:0] request_valid_pre;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    request_cell_index_pre;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target_pre;
  logic [(CELLS*STATE_BITS)-1:0] phase_target_pre;
  logic [(CELLS*STATE_BITS)-1:0] state_before;
  logic [(CELLS*STATE_BITS)-1:0] pending_before;
  logic [REQUEST_LANES-1:0] request_accept_pre;
  logic [REQUEST_LANES-1:0] request_reject_pre;
  logic [CELLS-1:0] accepted_cell_mask_pre;
  logic [CELLS-1:0] neutral_routed_cell_mask_pre;
  logic [CELLS-1:0] accepted_change_mask_pre;
  logic [COUNTER_BITS-1:0] accepted_changes_pre;
  logic [COUNTER_BITS-1:0] capacity_remaining_pre;
  logic capacity_exhausted_pre;
  logic [COUNTER_BITS-1:0] switch_load_numerator_pre;
  logic [COUNTER_BITS-1:0] requested_direct_events_pre;
  logic [COUNTER_BITS-1:0] prevented_direct_events_pre;
  logic [COUNTER_BITS-1:0] neutral_routed_events_pre;
  logic [COUNTER_BITS-1:0] actual_direct_events_pre;
  logic [COUNTER_BITS-1:0] reserved_state_events_pre;
  logic [COUNTER_BITS-1:0] queue_overflow_events_pre;
  logic [INVARIANT_FLAGS-1:0] invariant_flags_pre;

  initial begin
    evidence_sequence = 0;
    capture_valid = 1'b0;
  end

  always @(negedge source.clk) begin
    #2;
    if (
      source.tick_enable === 1'b1
      && source.core_ready === 1'b1
    ) begin
      if (capture_valid !== 1'b0) begin
        $fatal(1, "FRP M19 FPGA monitor: overlapping tick capture");
      end
      if (evidence_sequence >= EXPECTED_RECORDS) begin
        $fatal(1, "FRP M19 FPGA monitor: unexpected extra tick");
      end
      capture_valid = 1'b1;
      core_ready_pre = source.core_ready;
      scheduler_mode_pre = source.scheduler_mode_q;
      scheduler_state_pre = source.scheduler_state_q;
      ticks_before = source.ticks_recorded_q;
      request_valid_pre = source.request_valid;
      request_cell_index_pre = source.request_cell_index;
      request_target_pre = source.request_target;
      phase_target_pre = source.target_q;
      state_before = source.state_out;
      pending_before = source.pending_route_out;
      request_accept_pre = source.request_accept;
      request_reject_pre = source.request_reject;
      accepted_cell_mask_pre = source.accepted_cell_mask;
      neutral_routed_cell_mask_pre =
        source.neutral_routed_cell_mask;
      accepted_change_mask_pre = source.accepted_change_mask;
      accepted_changes_pre = source.accepted_changes;
      capacity_remaining_pre = source.capacity_remaining;
      capacity_exhausted_pre = source.capacity_exhausted;
      switch_load_numerator_pre = source.switch_load_numerator;
      requested_direct_events_pre = source.requested_direct_events;
      prevented_direct_events_pre = source.prevented_direct_events;
      neutral_routed_events_pre = source.neutral_routed_events;
      actual_direct_events_pre = source.actual_direct_events;
      reserved_state_events_pre = source.reserved_state_events;
      queue_overflow_events_pre = source.queue_overflow_events;
      invariant_flags_pre = source.invariant_flags;
    end
  end

  always @(posedge source.clk) begin
    #1;
    if (capture_valid === 1'b1) begin
      $display(
        "FRP_M19|1|fpga_preparation|%0d|%0d|%0h|%0h|%0d|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0h|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0d|%0h|%0h|%0h|%0d|%0d|%0d|%0d|%0d|%0d",
        evidence_sequence,
        core_ready_pre,
        scheduler_mode_pre,
        scheduler_state_pre,
        ticks_before,
        request_valid_pre,
        request_cell_index_pre,
        request_target_pre,
        phase_target_pre,
        state_before,
        pending_before,
        request_accept_pre,
        request_reject_pre,
        accepted_cell_mask_pre,
        neutral_routed_cell_mask_pre,
        accepted_change_mask_pre,
        accepted_changes_pre,
        capacity_remaining_pre,
        capacity_exhausted_pre,
        switch_load_numerator_pre,
        requested_direct_events_pre,
        prevented_direct_events_pre,
        neutral_routed_events_pre,
        actual_direct_events_pre,
        reserved_state_events_pre,
        queue_overflow_events_pre,
        invariant_flags_pre,
        source.state_out,
        source.pending_route_out,
        source.ticks_recorded_q,
        source.scheduler_count_free_q,
        source.scheduler_count_balance_q,
        source.scheduler_count_commit_q,
        source.scheduler_count_excite_q,
        source.scheduler_count_neutralize_q
      );
      evidence_sequence = evidence_sequence + 1;
      capture_valid = 1'b0;
      if (evidence_sequence == EXPECTED_RECORDS) begin
        $display("FRP M19 FPGA evidence records=4");
      end
    end
  end

endmodule : frp_m19_fpga_evidence_tb

`endif
