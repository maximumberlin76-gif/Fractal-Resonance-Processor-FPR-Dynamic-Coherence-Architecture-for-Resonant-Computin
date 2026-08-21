// SPDX-License-Identifier: Apache-2.0
// FRP M24 deliberately false claims used to retain expected SAT witnesses.

module frp_m24_reserved_encoding_counterexample;
  (* anyconst *) logic [1:0] state_value;
  wire M24_N01_FALSE_CLAIM = frp_is_valid_ternary(state_value);

  always @* begin
    assert(M24_N01_FALSE_CLAIM);
  end
endmodule

module frp_m24_direct_transition_counterexample;
  wire tick_enable = 1'b1;
  wire [2:0] scheduler_state = FRP_SCHED_NEUTRALIZE;
  wire [1:0] state_q = FRP_STATE_POS;
  wire [1:0] pending_route_q = FRP_STATE_ZERO;
  wire request_accept = 1'b1;
  wire request_neutralized = 1'b1;
  wire request_cell_index = 1'b0;
  wire [1:0] request_target = FRP_STATE_NEG;
  wire pending_completion_enable = 1'b0;

  wire [1:0] state_candidate_d;
  wire transition_valid_mask;
  wire same_state_mask;
  wire zero_to_nonzero_mask;
  wire nonzero_to_zero_mask;
  wire opposite_polarity_mask;
  wire neutral_routed_mask;
  wire pending_completion_mask;
  wire actual_direct_mask;
  wire reserved_transition_mask;
  wire accepted_change_candidate_mask;
  wire [7:0] same_state_events;
  wire [7:0] zero_to_nonzero_events;
  wire [7:0] nonzero_to_zero_events;
  wire [7:0] requested_direct_events;
  wire [7:0] prevented_direct_events;
  wire [7:0] neutral_routed_events;
  wire [7:0] pending_completion_events;
  wire [7:0] actual_direct_events;
  wire [7:0] reserved_transition_events;
  wire [7:0] accepted_change_candidate_events;
  wire transition_domain_valid;
  wire active_neutral_routing_valid;
  wire pending_completion_from_zero_valid;
  wire no_reserved_transition;
  wire no_actual_direct_events;
  wire transition_capacity_valid;
  wire state_output_domain_valid;
  wire transition_replay_deterministic;

  frp_m16_active_neutral #(
    .CELLS(1),
    .STATE_BITS(2),
    .REQUEST_LANES(1),
    .CELL_INDEX_BITS(1),
    .COUNTER_BITS(8)
  ) dut (
    .tick_enable(tick_enable),
    .scheduler_state(scheduler_state),
    .state_q(state_q),
    .pending_route_q(pending_route_q),
    .request_accept(request_accept),
    .request_neutralized(request_neutralized),
    .request_cell_index(request_cell_index),
    .request_target(request_target),
    .pending_completion_enable(pending_completion_enable),
    .state_candidate_d(state_candidate_d),
    .transition_valid_mask(transition_valid_mask),
    .same_state_mask(same_state_mask),
    .zero_to_nonzero_mask(zero_to_nonzero_mask),
    .nonzero_to_zero_mask(nonzero_to_zero_mask),
    .opposite_polarity_mask(opposite_polarity_mask),
    .neutral_routed_mask(neutral_routed_mask),
    .pending_completion_mask(pending_completion_mask),
    .actual_direct_mask(actual_direct_mask),
    .reserved_transition_mask(reserved_transition_mask),
    .accepted_change_candidate_mask(accepted_change_candidate_mask),
    .same_state_events(same_state_events),
    .zero_to_nonzero_events(zero_to_nonzero_events),
    .nonzero_to_zero_events(nonzero_to_zero_events),
    .requested_direct_events(requested_direct_events),
    .prevented_direct_events(prevented_direct_events),
    .neutral_routed_events(neutral_routed_events),
    .pending_completion_events(pending_completion_events),
    .actual_direct_events(actual_direct_events),
    .reserved_transition_events(reserved_transition_events),
    .accepted_change_candidate_events(accepted_change_candidate_events),
    .transition_domain_valid(transition_domain_valid),
    .active_neutral_routing_valid(active_neutral_routing_valid),
    .pending_completion_from_zero_valid(pending_completion_from_zero_valid),
    .no_reserved_transition(no_reserved_transition),
    .no_actual_direct_events(no_actual_direct_events),
    .transition_capacity_valid(transition_capacity_valid),
    .state_output_domain_valid(state_output_domain_valid),
    .transition_replay_deterministic(transition_replay_deterministic)
  );

  wire M24_N02_FALSE_CLAIM = state_candidate_d == FRP_STATE_NEG;

  always @* begin
    assert(M24_N02_FALSE_CLAIM);
  end
endmodule
