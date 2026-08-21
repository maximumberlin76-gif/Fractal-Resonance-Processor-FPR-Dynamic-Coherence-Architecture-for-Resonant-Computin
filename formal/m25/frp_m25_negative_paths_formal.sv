// SPDX-License-Identifier: Apache-2.0
// FRP M25 deterministic negative-path proof over the actual M16 RTL modules.

module frp_m25_negative_paths_formal;
  localparam int COUNTER_BITS = 8;

  // Reserved ternary target rejection.
  wire inv_accept;
  wire inv_reject;
  wire inv_invalid_target;
  frp_m16_request_lanes #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) invalid_target_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_FREE),
    .request_valid(1'b1), .request_cell_index(1'b0),
    .request_target(FRP_STATE_RESERVED), .state_q(FRP_STATE_ZERO),
    .target_q(FRP_STATE_ZERO), .pending_route_q(FRP_STATE_ZERO),
    .request_accept(inv_accept), .request_reject(inv_reject),
    .request_reject_invalid_cell(),
    .request_reject_invalid_target(inv_invalid_target),
    .request_reject_duplicate_cell(), .request_reject_scheduler(),
    .request_reject_capacity(), .request_reject_pending_busy(),
    .request_reject_tick_disabled(), .request_neutralized(),
    .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // Invalid cell-index rejection.
  wire cell_accept;
  wire cell_reject;
  wire cell_invalid;
  frp_m16_request_lanes #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) invalid_cell_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_FREE),
    .request_valid(1'b1), .request_cell_index(1'b1),
    .request_target(FRP_STATE_POS), .state_q(FRP_STATE_ZERO),
    .target_q(FRP_STATE_ZERO), .pending_route_q(FRP_STATE_ZERO),
    .request_accept(cell_accept), .request_reject(cell_reject),
    .request_reject_invalid_cell(cell_invalid),
    .request_reject_invalid_target(), .request_reject_duplicate_cell(),
    .request_reject_scheduler(), .request_reject_capacity(),
    .request_reject_pending_busy(), .request_reject_tick_disabled(),
    .request_neutralized(), .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // Ascending-lane duplicate arbitration.
  wire [1:0] dup_accept;
  wire [1:0] dup_reject;
  wire [1:0] dup_reason;
  frp_m16_request_lanes #(
    .CELLS(2), .STATE_BITS(2), .REQUEST_LANES(2),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) duplicate_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_FREE),
    .request_valid(2'b11), .request_cell_index(2'b00),
    .request_target({FRP_STATE_POS, FRP_STATE_POS}),
    .state_q({FRP_STATE_ZERO, FRP_STATE_ZERO}),
    .target_q({FRP_STATE_ZERO, FRP_STATE_ZERO}),
    .pending_route_q({FRP_STATE_ZERO, FRP_STATE_ZERO}),
    .request_accept(dup_accept), .request_reject(dup_reject),
    .request_reject_invalid_cell(), .request_reject_invalid_target(),
    .request_reject_duplicate_cell(dup_reason),
    .request_reject_scheduler(), .request_reject_capacity(),
    .request_reject_pending_busy(), .request_reject_tick_disabled(),
    .request_neutralized(), .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // Scheduler deferral of a 0 -> 1 request during a balance state.
  wire sched_accept;
  wire sched_reject;
  wire sched_reason;
  frp_m16_request_lanes #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) scheduler_deferral_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_BALANCE),
    .request_valid(1'b1), .request_cell_index(1'b0),
    .request_target(FRP_STATE_POS), .state_q(FRP_STATE_ZERO),
    .target_q(FRP_STATE_ZERO), .pending_route_q(FRP_STATE_ZERO),
    .request_accept(sched_accept), .request_reject(sched_reject),
    .request_reject_invalid_cell(), .request_reject_invalid_target(),
    .request_reject_duplicate_cell(), .request_reject_scheduler(sched_reason),
    .request_reject_capacity(), .request_reject_pending_busy(),
    .request_reject_tick_disabled(), .request_neutralized(),
    .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // Existing pending route owns its cell before a new lane.
  wire pending_accept;
  wire pending_reject;
  wire pending_reason;
  frp_m16_request_lanes #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) pending_busy_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_FREE),
    .request_valid(1'b1), .request_cell_index(1'b0),
    .request_target(FRP_STATE_POS), .state_q(FRP_STATE_ZERO),
    .target_q(FRP_STATE_ZERO), .pending_route_q(FRP_STATE_NEG),
    .request_accept(pending_accept), .request_reject(pending_reject),
    .request_reject_invalid_cell(), .request_reject_invalid_target(),
    .request_reject_duplicate_cell(), .request_reject_scheduler(),
    .request_reject_capacity(), .request_reject_pending_busy(pending_reason),
    .request_reject_tick_disabled(), .request_neutralized(),
    .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // A disabled tick classifies the lane and never accepts it.
  wire disabled_accept;
  wire disabled_reason;
  frp_m16_request_lanes #(
    .CELLS(1), .STATE_BITS(2), .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) tick_disabled_dut (
    .tick_enable(1'b0), .scheduler_state(FRP_SCHED_FREE),
    .request_valid(1'b1), .request_cell_index(1'b0),
    .request_target(FRP_STATE_POS), .state_q(FRP_STATE_ZERO),
    .target_q(FRP_STATE_ZERO), .pending_route_q(FRP_STATE_ZERO),
    .request_accept(disabled_accept), .request_reject(),
    .request_reject_invalid_cell(), .request_reject_invalid_target(),
    .request_reject_duplicate_cell(), .request_reject_scheduler(),
    .request_reject_capacity(), .request_reject_pending_busy(),
    .request_reject_tick_disabled(disabled_reason), .request_neutralized(),
    .accepted_cell_mask(), .rejected_cell_mask(),
    .neutral_routed_cell_mask(), .requested_direct_cell_mask(),
    .accepted_changes(), .requested_lane_events(),
    .accepted_lane_events(), .rejected_lane_events(),
    .requested_direct_events(), .prevented_direct_events(),
    .neutral_routed_events(), .request_lane_order_valid(),
    .request_cell_domain_valid(), .request_target_domain_valid(),
    .duplicate_cell_guard_valid(), .scheduler_gate_valid(),
    .transition_capacity_valid(), .active_neutral_routing_valid(),
    .no_actual_direct_events(), .no_queue_overflow()
  );

  // Two pending completions consume both lane slots before a new request.
  wire [1:0] cap_accept_lane;
  wire [1:0] cap_reject_lane;
  wire [3:0] cap_accept_mask;
  wire [7:0] cap_accepted_changes;
  wire cap_exhausted;
  frp_m16_capacity_guard #(
    .CELLS(4), .STATE_BITS(2), .REQUEST_LANES(2),
    .CELL_INDEX_BITS(2), .COUNTER_BITS(COUNTER_BITS)
  ) capacity_deferral_dut (
    .tick_enable(1'b1), .scheduler_state(FRP_SCHED_FREE),
    .request_accept_candidate(2'b01), .request_cell_index(4'b0010),
    .transition_class(8'h01),
    .pending_completion_candidate(4'b0011),
    .neutral_routed_candidate(4'b0000),
    .state_q(8'b00000000), .state_candidate_d(8'b00011101),
    .request_accept_capacity(cap_accept_lane),
    .request_reject_capacity(cap_reject_lane),
    .capacity_accept_mask(cap_accept_mask), .capacity_reject_mask(),
    .accepted_change_mask(), .accepted_changes(cap_accepted_changes),
    .capacity_remaining(), .capacity_exhausted(cap_exhausted),
    .switch_load_numerator(), .capacity_candidate_events(),
    .capacity_accept_events(), .capacity_reject_events(),
    .capacity_exhausted_events(), .accepted_change_events(),
    .transition_capacity_valid(), .accepted_changes_within_limit(),
    .capacity_remaining_valid(), .capacity_exhaustion_valid(),
    .same_state_capacity_valid(), .pending_capacity_valid(),
    .active_neutral_capacity_valid(), .switch_load_bound_valid(),
    .no_queue_overflow(), .no_actual_direct_events()
  );

  // Duplicate creation is detected as queue overflow and cannot overwrite
  // the polarity selected by the first deterministic lane.
  wire clock = 1'b0;
  wire [3:0] overflow_pending_d;
  wire [1:0] overflow_created;
  wire [1:0] overflow_mask;
  wire [7:0] overflow_events;
  wire overflow_no_queue;
  wire overflow_no_direct;
  frp_m16_pending_routes #(
    .CELLS(2), .STATE_BITS(2), .REQUEST_LANES(2),
    .CELL_INDEX_BITS(1), .COUNTER_BITS(COUNTER_BITS)
  ) overflow_dut (
    .clk(clock), .rst_n(1'b1), .tick_enable(1'b1),
    .state_q({FRP_STATE_ZERO, FRP_STATE_POS}),
    .request_accept(2'b11), .request_neutralized(2'b11),
    .request_cell_index(2'b00),
    .request_target({FRP_STATE_NEG, FRP_STATE_NEG}),
    .pending_completion_accept_mask(2'b00), .pending_route_q(),
    .pending_route_d(overflow_pending_d), .pending_active_mask(),
    .pending_created_mask(overflow_created), .pending_completed_mask(),
    .pending_cleared_mask(), .pending_retained_mask(),
    .pending_blocked_mask(), .pending_reserved_mask(),
    .pending_overflow_mask(overflow_mask), .pending_active_count(),
    .pending_created_events(), .pending_completed_events(),
    .pending_cleared_events(), .pending_retained_events(),
    .pending_reserved_events(), .neutral_routed_events(),
    .prevented_direct_events(), .queue_overflow_events(overflow_events),
    .actual_direct_events(), .pending_domain_valid(),
    .pending_polarity_valid(), .pending_completion_from_zero_valid(),
    .pending_non_overwrite_valid(), .pending_capacity_valid(),
    .pending_replay_deterministic(), .no_pending_reserved_state(),
    .no_queue_overflow(overflow_no_queue),
    .no_actual_direct_events(overflow_no_direct)
  );

  wire M25_P01 = inv_reject && !inv_accept;
  wire M25_P02 = inv_invalid_target;
  wire M25_P03 = cell_reject && cell_invalid && !cell_accept;
  wire M25_P04 = (dup_accept == 2'b01) && (dup_reject == 2'b10);
  wire M25_P05 = (dup_reason == 2'b10);
  wire M25_P06 = sched_reject && sched_reason && !sched_accept;
  wire M25_P07 = pending_reject && pending_reason && !pending_accept;
  wire M25_P08 = disabled_reason && !disabled_accept;
  wire M25_P09 = (cap_accept_mask == 4'b0011) && (cap_accepted_changes == 8'd2);
  wire M25_P10 = cap_exhausted && cap_reject_lane[0] && !cap_accept_lane[0];
  wire M25_P11 = (overflow_created == 2'b01) && (overflow_mask == 2'b01);
  wire M25_P12 = (overflow_pending_d[1:0] == FRP_STATE_NEG);
  wire M25_P13 = (overflow_events == 8'd1) && !overflow_no_queue;
  wire M25_P14 = overflow_no_direct;

  always @* begin
    assert(M25_P01); assert(M25_P02); assert(M25_P03);
    assert(M25_P04); assert(M25_P05); assert(M25_P06);
    assert(M25_P07); assert(M25_P08); assert(M25_P09);
    assert(M25_P10); assert(M25_P11); assert(M25_P12);
    assert(M25_P13); assert(M25_P14);
  end
endmodule
