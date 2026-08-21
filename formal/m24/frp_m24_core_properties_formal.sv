// SPDX-License-Identifier: Apache-2.0
// FRP M24 bounded proof harness for the integrated M16 core RTL.

module frp_m24_core_properties_formal;
  localparam int CELLS = 2;
  localparam int REQUEST_LANES = 2;
  localparam int STATE_BITS = 2;
  localparam int CELL_INDEX_BITS = 1;
  localparam int COUNTER_BITS = 8;

  (* anyseq *) logic clock;
  (* anyseq *) logic tick_enable;
  (* anyseq *) logic clear_counters;
  (* anyseq *) logic [1:0] scheduler_mode;
  (* anyseq *) logic [REQUEST_LANES-1:0] request_valid;
  (* anyseq *) logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] request_cell_index;
  (* anyseq *) logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target;
  (* anyseq *) logic [(CELLS*STATE_BITS)-1:0] target_q;

  logic history_valid_q;
  logic history_tick_enable_q;
  logic [(CELLS*STATE_BITS)-1:0] history_state_q;
  logic [(CELLS*STATE_BITS)-1:0] history_pending_q;

  wire rst_n = 1'b1;
  wire [(CELLS*STATE_BITS)-1:0] state_out;
  wire [(CELLS*STATE_BITS)-1:0] pending_route_out;
  wire [1:0] scheduler_mode_q;
  wire [2:0] scheduler_state_q;
  wire [COUNTER_BITS-1:0] ticks_recorded_q;
  wire [COUNTER_BITS-1:0] scheduler_count_free_q;
  wire [COUNTER_BITS-1:0] scheduler_count_balance_q;
  wire [COUNTER_BITS-1:0] scheduler_count_commit_q;
  wire [COUNTER_BITS-1:0] scheduler_count_excite_q;
  wire [COUNTER_BITS-1:0] scheduler_count_neutralize_q;
  wire [REQUEST_LANES-1:0] request_accept;
  wire [REQUEST_LANES-1:0] request_reject;
  wire [CELLS-1:0] accepted_cell_mask;
  wire [CELLS-1:0] neutral_routed_cell_mask;
  wire [CELLS-1:0] accepted_change_mask;
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
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
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

  wire state_domain_valid =
    frp_is_valid_ternary(state_out[1:0])
    && frp_is_valid_ternary(state_out[3:2]);
  wire pending_domain_valid =
    frp_is_valid_pending_route(pending_route_out[1:0])
    && frp_is_valid_pending_route(pending_route_out[3:2]);
  wire duplicate_request =
    request_valid[0] && request_valid[1]
    && (request_cell_index[0] == request_cell_index[1]);

  wire M24_P16 = (request_accept & request_reject) == 2'b00;
  wire M24_P17 = accepted_changes <= REQUEST_LANES;
  wire M24_P18 =
    !duplicate_request || !(request_accept[0] && request_accept[1]);
  wire M24_P19 =
    (capacity_remaining + accepted_changes == REQUEST_LANES)
    && (capacity_exhausted == (capacity_remaining == 0));
  wire M24_P20 = switch_load_numerator == accepted_changes;
  wire M24_P21 =
    ((neutral_routed_cell_mask & ~accepted_cell_mask) == 0)
    && ((neutral_routed_cell_mask & ~accepted_change_mask) == 0);
  wire M24_P22 = state_domain_valid;
  wire M24_P23 = pending_domain_valid;
  wire M24_P24 = actual_direct_events == 0;
  wire M24_P25 = reserved_state_events == 0;
  wire M24_P26 = queue_overflow_events == 0;
  wire M24_P27 = invariant_flags == {FRP_M16_INVARIANT_FLAGS{1'b1}};
  wire M24_P28 =
    !history_valid_q
    || history_tick_enable_q
    || ((state_out == history_state_q)
      && (pending_route_out == history_pending_q));
  wire M24_P29 =
    !$initstate
    || ((state_out == 0) && (pending_route_out == 0)
      && (ticks_recorded_q == 0));

  always @(posedge clock) begin
    history_valid_q <= 1'b1;
    history_tick_enable_q <= tick_enable;
    history_state_q <= state_out;
    history_pending_q <= pending_route_out;
  end

  always @* begin
    assume(frp_is_valid_scheduler_mode(scheduler_mode));
    assume(frp_is_valid_ternary(request_target[1:0]));
    assume(frp_is_valid_ternary(request_target[3:2]));
    assume(frp_is_valid_ternary(target_q[1:0]));
    assume(frp_is_valid_ternary(target_q[3:2]));
    assert(M24_P16);
    assert(M24_P17);
    assert(M24_P18);
    assert(M24_P19);
    assert(M24_P20);
    assert(M24_P21);
    assert(M24_P22);
    assert(M24_P23);
    assert(M24_P24);
    assert(M24_P25);
    assert(M24_P26);
    assert(M24_P27);
    assert(M24_P28);
    assert(M24_P29);
  end
endmodule
