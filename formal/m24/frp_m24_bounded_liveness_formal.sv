// SPDX-License-Identifier: Apache-2.0
// FRP M24 controlled bounded-liveness proof over the actual M16 core RTL.

module frp_m24_bounded_liveness_formal;
  localparam int COUNTER_BITS = 8;

  (* anyseq *) logic clock;
  logic [3:0] proof_step_q;

  wire rst_n = 1'b1;
  wire tick_enable = 1'b1;
  wire clear_counters = 1'b0;
  wire [1:0] scheduler_mode = FRP_MODE_FREE;
  wire request_valid = (proof_step_q == 0) || (proof_step_q == 1);
  wire request_cell_index = 1'b0;
  wire [1:0] request_target =
    (proof_step_q == 0) ? FRP_STATE_POS : FRP_STATE_NEG;
  wire [1:0] target_q = FRP_STATE_ZERO;

  wire [1:0] state_out;
  wire [1:0] pending_route_out;
  wire [1:0] scheduler_mode_q;
  wire [2:0] scheduler_state_q;
  wire [COUNTER_BITS-1:0] ticks_recorded_q;
  wire [COUNTER_BITS-1:0] scheduler_count_free_q;
  wire [COUNTER_BITS-1:0] scheduler_count_balance_q;
  wire [COUNTER_BITS-1:0] scheduler_count_commit_q;
  wire [COUNTER_BITS-1:0] scheduler_count_excite_q;
  wire [COUNTER_BITS-1:0] scheduler_count_neutralize_q;
  wire request_accept;
  wire request_reject;
  wire accepted_cell_mask;
  wire neutral_routed_cell_mask;
  wire accepted_change_mask;
  wire [COUNTER_BITS-1:0] accepted_changes;
  wire [COUNTER_BITS-1:0] capacity_remaining;
  wire capacity_exhausted;
  wire [COUNTER_BITS-1:0] switch_load_numerator;
  wire [COUNTER_BITS-1:0] requested_direct_events;
  wire [COUNTER_BITS-1:0] prevented_direct_events;
  wire [COUNTER_BITS-1:0] neutral_routed_events;
  wire [COUNTER_BITS-1:0] actual_direct_events;
  wire [COUNTER_BITS-1:0] reserved_state_events;
  wire [COUNTER_BITS-1:0] queue_overflow_events;
  wire [FRP_M16_INVARIANT_FLAGS-1:0] invariant_flags;

  frp_m16_core #(
    .CELLS(1),
    .STATE_BITS(2),
    .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clock),
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

  always @(posedge clock) begin
    proof_step_q <= proof_step_q + 1'b1;
  end

  wire M24_P30 = (proof_step_q != 1) || (state_out == FRP_STATE_POS);
  wire M24_P31 =
    (proof_step_q != 2)
    || ((state_out == FRP_ACTIVE_NEUTRAL)
      && (pending_route_out == FRP_STATE_NEG));
  wire M24_P32 =
    (proof_step_q < 3)
    || ((state_out == FRP_STATE_NEG)
      && (pending_route_out == FRP_STATE_ZERO));

  always @* begin
    assert(M24_P30);
    assert(M24_P31);
    assert(M24_P32);
  end
endmodule
