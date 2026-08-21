// SPDX-License-Identifier: Apache-2.0
// FRP M25 pending-route, deferral, reset, and recovery proof on the real core.

module frp_m25_pending_reset_recovery_formal;
  localparam int COUNTER_BITS = 8;
  (* anyseq *) logic clock;
  logic [3:0] proof_step_q;

  wire rst_n = (proof_step_q != 3);
  wire tick_enable = (proof_step_q != 2);
  wire request_valid =
    (proof_step_q == 0) || (proof_step_q == 1)
    || (proof_step_q == 2) || (proof_step_q == 4);
  wire [1:0] request_target =
    (proof_step_q == 1) ? FRP_STATE_NEG : FRP_STATE_POS;

  wire [1:0] state_out;
  wire [1:0] pending_route_out;
  wire request_accept;
  wire request_reject;
  wire [COUNTER_BITS-1:0] actual_direct_events;
  wire [COUNTER_BITS-1:0] queue_overflow_events;
  wire [FRP_M16_INVARIANT_FLAGS-1:0] invariant_flags;

  frp_m16_core #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clock), .rst_n(rst_n), .tick_enable(tick_enable),
    .clear_counters(1'b0), .scheduler_mode(FRP_MODE_FREE),
    .request_valid(request_valid), .request_cell_index(1'b0),
    .request_target(request_target), .target_q(FRP_STATE_ZERO),
    .state_out(state_out), .pending_route_out(pending_route_out),
    .scheduler_mode_q(), .scheduler_state_q(), .ticks_recorded_q(),
    .scheduler_count_free_q(), .scheduler_count_balance_q(),
    .scheduler_count_commit_q(), .scheduler_count_excite_q(),
    .scheduler_count_neutralize_q(), .request_accept(request_accept),
    .request_reject(request_reject), .accepted_cell_mask(),
    .neutral_routed_cell_mask(), .accepted_change_mask(),
    .accepted_changes(), .capacity_remaining(), .capacity_exhausted(),
    .switch_load_numerator(), .requested_direct_events(),
    .prevented_direct_events(), .neutral_routed_events(),
    .actual_direct_events(actual_direct_events), .reserved_state_events(),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags)
  );

  always @(posedge clock) begin
    proof_step_q <= proof_step_q + 1'b1;
  end

  wire M25_P18 =
    (proof_step_q != 1)
    || ((state_out == FRP_STATE_POS)
      && (pending_route_out == FRP_STATE_ZERO));
  wire M25_P19 =
    (proof_step_q != 2)
    || ((state_out == FRP_ACTIVE_NEUTRAL)
      && (pending_route_out == FRP_STATE_NEG));
  wire M25_P20 =
    (proof_step_q != 2)
    || ((state_out == FRP_ACTIVE_NEUTRAL)
      && (pending_route_out == FRP_STATE_NEG)
      && !request_accept);
  wire M25_P21 =
    (proof_step_q != 3)
    || ((state_out == FRP_ACTIVE_NEUTRAL)
      && (pending_route_out == FRP_STATE_ZERO));
  wire M25_P22 =
    (proof_step_q < 5)
    || ((state_out == FRP_STATE_POS)
      && (pending_route_out == FRP_STATE_ZERO));
  wire M25_P23 = (actual_direct_events == 0);
  wire M25_P24 = (queue_overflow_events == 0);
  wire M25_P25 =
    (proof_step_q < 5)
    || (invariant_flags == {FRP_M16_INVARIANT_FLAGS{1'b1}});

  always @* begin
    assert(M25_P18); assert(M25_P19); assert(M25_P20);
    assert(M25_P21); assert(M25_P22); assert(M25_P23);
    assert(M25_P24); assert(M25_P25);
  end
endmodule
