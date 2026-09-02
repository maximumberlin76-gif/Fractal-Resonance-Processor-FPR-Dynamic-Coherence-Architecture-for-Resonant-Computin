// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Integrated RTL Core
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
//   Integrates the M31 scheduler, request-lane arbitration,
//   pending-route register layer, active-neutral transition layer,
//   transition-capacity guard, and retained-state update module.
//
// This core preserves the M15-qualified execution semantics:
//   - canonical balanced ternary encoding
//   - active neutral routing through 0
//   - free / 7/1 / 1/7 scheduler modes
//   - deterministic request-lane arbitration
//   - pending-route retained continuation
//   - transition-capacity boundary
//   - retained-state writeback
//   - zero direct opposite-polarity execution
//   - zero reserved-state emission
//   - zero queue-overflow qualification target

`ifndef FRP_M31_EXECUTION_CORE_SV
`define FRP_M31_EXECUTION_CORE_SV

`include "frp_m31_pkg.sv"
`include "frp_m31_scheduler.sv"
`include "frp_m31_request_lanes.sv"
`include "frp_m31_pending_routes.sv"
`include "frp_m31_active_neutral.sv"
`include "frp_m31_capacity_guard.sv"
`include "frp_m31_state_update.sv"

module frp_m31_execution_core #(
  parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
  parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,

  input logic tick_enable,
  input logic clear_counters,

  input frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode,

  input logic [REQUEST_LANES-1:0] request_valid,
  input logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] request_cell_index,
  input logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target,

  input logic [(CELLS*STATE_BITS)-1:0] target_q,

  output logic [(CELLS*STATE_BITS)-1:0] state_out,
  output logic [(CELLS*STATE_BITS)-1:0] pending_route_out,

  output frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode_q,
  output frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state_q,

  output logic [COUNTER_BITS-1:0] ticks_recorded_q,

  output logic [COUNTER_BITS-1:0] scheduler_count_free_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_balance_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_commit_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_excite_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q,

  output logic [REQUEST_LANES-1:0] request_accept,
  output logic [REQUEST_LANES-1:0] request_reject,

  output logic [CELLS-1:0] accepted_cell_mask,
  output logic [CELLS-1:0] neutral_routed_cell_mask,
  output logic [CELLS-1:0] accepted_change_mask,

  output logic [COUNTER_BITS-1:0] accepted_changes,
  output logic [COUNTER_BITS-1:0] capacity_remaining,
  output logic capacity_exhausted,
  output logic [COUNTER_BITS-1:0] switch_load_numerator,

  output logic [COUNTER_BITS-1:0] requested_direct_events,
  output logic [COUNTER_BITS-1:0] prevented_direct_events,
  output logic [COUNTER_BITS-1:0] neutral_routed_events,
  output logic [COUNTER_BITS-1:0] actual_direct_events,
  output logic [COUNTER_BITS-1:0] reserved_state_events,
  output logic [COUNTER_BITS-1:0] queue_overflow_events,

  output logic [
    frp_m31_pkg::FRP_M31_INVARIANT_FLAGS-1:0
  ] invariant_flags
);

  import frp_m31_pkg::*;

  // --------------------------------------------------------------------------
  // Scheduler wires
  // --------------------------------------------------------------------------

  logic [COUNTER_BITS-1:0] tick_index_q;
  logic [2:0] period_index_q;

  logic free_enable;
  logic balance_enable;
  logic commit_enable;
  logic excite_enable;
  logic neutralize_enable;

  logic scheduler_mode_reserved;
  logic scheduler_state_reserved;
  logic scheduler_valid;
  logic scheduler_counts_valid;

  // --------------------------------------------------------------------------
  // Retained-state wires
  // --------------------------------------------------------------------------

  logic [(CELLS*STATE_BITS)-1:0] state_q;
  logic [(CELLS*STATE_BITS)-1:0] state_d;

  logic [CELLS-1:0] state_write_enable_mask;
  logic [CELLS-1:0] state_hold_mask;
  logic [CELLS-1:0] state_reset_mask;
  logic [CELLS-1:0] state_reserved_mask;

  logic state_domain_valid;
  logic state_output_domain_valid;
  logic state_update_valid;
  logic state_write_capacity_valid;
  logic same_state_hold_valid;
  logic active_neutral_writeback_valid;
  logic pending_completion_writeback_valid;
  logic no_reserved_state_output;
  logic state_update_no_actual_direct_events;

  logic [COUNTER_BITS-1:0] state_update_accepted_changes;
  logic [COUNTER_BITS-1:0] state_update_switch_load_numerator;

  logic [COUNTER_BITS-1:0] state_write_events;
  logic [COUNTER_BITS-1:0] state_hold_events;
  logic [COUNTER_BITS-1:0] state_reset_events;
  logic [COUNTER_BITS-1:0] state_accepted_change_events;
  logic [COUNTER_BITS-1:0] neutral_routed_commit_events;
  logic [COUNTER_BITS-1:0] pending_completion_commit_events;
  logic [COUNTER_BITS-1:0] state_reserved_state_events;
  logic [COUNTER_BITS-1:0] state_actual_direct_events;

  // --------------------------------------------------------------------------
  // Request-lane wires
  // --------------------------------------------------------------------------

  logic [REQUEST_LANES-1:0] request_accept_lane;
  logic [REQUEST_LANES-1:0] request_reject_lane;

  logic [REQUEST_LANES-1:0] request_reject_invalid_cell;
  logic [REQUEST_LANES-1:0] request_reject_invalid_target;
  logic [REQUEST_LANES-1:0] request_reject_duplicate_cell;
  logic [REQUEST_LANES-1:0] request_reject_scheduler;
  logic [REQUEST_LANES-1:0] request_reject_capacity_lane;
  logic [REQUEST_LANES-1:0] request_reject_pending_busy;
  logic [REQUEST_LANES-1:0] request_reject_tick_disabled;

  logic [REQUEST_LANES-1:0] request_neutralized_lane;

  logic [CELLS-1:0] request_accepted_cell_mask;
  logic [CELLS-1:0] request_rejected_cell_mask;
  logic [CELLS-1:0] request_neutral_routed_cell_mask;
  logic [CELLS-1:0] request_requested_direct_cell_mask;

  logic [COUNTER_BITS-1:0] request_accepted_changes;
  logic [COUNTER_BITS-1:0] requested_lane_events;
  logic [COUNTER_BITS-1:0] accepted_lane_events;
  logic [COUNTER_BITS-1:0] rejected_lane_events;
  logic [COUNTER_BITS-1:0] request_requested_direct_events;
  logic [COUNTER_BITS-1:0] request_prevented_direct_events;
  logic [COUNTER_BITS-1:0] request_neutral_routed_events;

  logic request_lane_order_valid;
  logic request_cell_domain_valid;
  logic request_target_domain_valid;
  logic duplicate_cell_guard_valid;
  logic request_scheduler_gate_valid;
  logic request_transition_capacity_valid;
  logic request_active_neutral_routing_valid;
  logic request_no_actual_direct_events;
  logic request_no_queue_overflow;

  // --------------------------------------------------------------------------
  // Pending-route wires
  // --------------------------------------------------------------------------

  logic [(CELLS*STATE_BITS)-1:0] pending_route_q;
  logic [(CELLS*STATE_BITS)-1:0] pending_route_d;

  logic [CELLS-1:0] pending_completion_candidate;
  logic [CELLS-1:0] pending_completion_accept_mask;

  logic [CELLS-1:0] pending_active_mask;
  logic [CELLS-1:0] pending_created_mask;
  logic [CELLS-1:0] pending_completed_mask;
  logic [CELLS-1:0] pending_cleared_mask;
  logic [CELLS-1:0] pending_retained_mask;
  logic [CELLS-1:0] pending_blocked_mask;
  logic [CELLS-1:0] pending_reserved_mask;
  logic [CELLS-1:0] pending_overflow_mask;

  logic [COUNTER_BITS-1:0] pending_active_count;
  logic [COUNTER_BITS-1:0] pending_created_events;
  logic [COUNTER_BITS-1:0] pending_completed_events;
  logic [COUNTER_BITS-1:0] pending_cleared_events;
  logic [COUNTER_BITS-1:0] pending_retained_events;
  logic [COUNTER_BITS-1:0] pending_reserved_events;
  logic [COUNTER_BITS-1:0] pending_neutral_routed_events;
  logic [COUNTER_BITS-1:0] pending_prevented_direct_events;
  logic [COUNTER_BITS-1:0] pending_queue_overflow_events;
  logic [COUNTER_BITS-1:0] pending_actual_direct_events;

  logic pending_domain_valid;
  logic pending_polarity_valid;
  logic pending_completion_from_zero_valid;
  logic pending_non_overwrite_valid;
  logic pending_capacity_valid;
  logic pending_replay_deterministic;
  logic no_pending_reserved_state;
  logic pending_no_queue_overflow;
  logic pending_no_actual_direct_events;

  // --------------------------------------------------------------------------
  // Active-neutral transition wires
  // --------------------------------------------------------------------------

  logic [(CELLS*STATE_BITS)-1:0] state_candidate_d;

  logic [CELLS-1:0] transition_valid_mask;
  logic [CELLS-1:0] same_state_mask;
  logic [CELLS-1:0] zero_to_nonzero_mask;
  logic [CELLS-1:0] nonzero_to_zero_mask;
  logic [CELLS-1:0] opposite_polarity_mask;
  logic [CELLS-1:0] transition_neutral_routed_mask;
  logic [CELLS-1:0] transition_pending_completion_mask;
  logic [CELLS-1:0] transition_actual_direct_mask;
  logic [CELLS-1:0] reserved_transition_mask;
  logic [CELLS-1:0] accepted_change_candidate_mask;

  logic [COUNTER_BITS-1:0] same_state_events;
  logic [COUNTER_BITS-1:0] zero_to_nonzero_events;
  logic [COUNTER_BITS-1:0] nonzero_to_zero_events;
  logic [COUNTER_BITS-1:0] transition_requested_direct_events;
  logic [COUNTER_BITS-1:0] transition_prevented_direct_events;
  logic [COUNTER_BITS-1:0] transition_neutral_routed_events;
  logic [COUNTER_BITS-1:0] transition_pending_completion_events;
  logic [COUNTER_BITS-1:0] transition_actual_direct_events;
  logic [COUNTER_BITS-1:0] reserved_transition_events;
  logic [COUNTER_BITS-1:0] accepted_change_candidate_events;

  logic transition_domain_valid;
  logic active_neutral_routing_valid;
  logic transition_pending_completion_from_zero_valid;
  logic no_reserved_transition;
  logic transition_no_actual_direct_events;
  logic transition_capacity_valid_local;
  logic transition_state_output_domain_valid;
  logic transition_replay_deterministic;

  // --------------------------------------------------------------------------
  // Capacity-guard wires
  // --------------------------------------------------------------------------

  logic [REQUEST_LANES-1:0] request_accept_capacity;
  logic [REQUEST_LANES-1:0] request_reject_capacity;

  logic [CELLS-1:0] capacity_accept_mask;
  logic [CELLS-1:0] capacity_reject_mask;
  logic [CELLS-1:0] capacity_accepted_change_mask;

  logic [COUNTER_BITS-1:0] capacity_accepted_changes;
  logic [COUNTER_BITS-1:0] capacity_switch_load_numerator;

  logic [COUNTER_BITS-1:0] capacity_candidate_events;
  logic [COUNTER_BITS-1:0] capacity_accept_events;
  logic [COUNTER_BITS-1:0] capacity_reject_events;
  logic [COUNTER_BITS-1:0] capacity_exhausted_events;
  logic [COUNTER_BITS-1:0] capacity_accepted_change_events;

  logic capacity_transition_capacity_valid;
  logic accepted_changes_within_limit;
  logic capacity_remaining_valid;
  logic capacity_exhaustion_valid;
  logic same_state_capacity_valid;
  logic capacity_pending_capacity_valid;
  logic capacity_active_neutral_capacity_valid;
  logic switch_load_bound_valid;
  logic capacity_no_queue_overflow;
  logic capacity_no_actual_direct_events;

  // --------------------------------------------------------------------------
  // Lane transition-class bus
  // --------------------------------------------------------------------------

  logic [
    (REQUEST_LANES*FRP_M31_TRANSITION_CLASS_BITS)-1:0
  ] lane_transition_class_bus;

  function automatic logic [CELL_INDEX_BITS-1:0] lane_cell_index_value(
    input int lane_index
  );
    begin
      lane_cell_index_value =
        request_cell_index[
          (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
        ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] lane_target_value(
    input int lane_index
  );
    begin
      lane_target_value =
        request_target[
          (lane_index*STATE_BITS) +: STATE_BITS
        ];
    end
  endfunction

  // --------------------------------------------------------------------------
  // Derived pending-route completions and request transition classes
  // --------------------------------------------------------------------------

  always_comb begin
    pending_completion_candidate = '0;

    for (
      int element_index = 0;
      element_index < CELLS;
      element_index++
    ) begin
      logic [STATE_BITS-1:0] retained_state;
      logic [STATE_BITS-1:0] pending_target;

      retained_state =
        state_q[
          (element_index*STATE_BITS) +: STATE_BITS
        ];

      pending_target =
        pending_route_q[
          (element_index*STATE_BITS) +: STATE_BITS
        ];

      if (
        tick_enable
        && frp_is_zero(retained_state)
        && frp_is_nonzero(pending_target)
        && frp_scheduler_is_commit_capable(
          scheduler_state_q
        )
      ) begin
        pending_completion_candidate[element_index] = 1'b1;
      end
    end
  end

  always_comb begin
    lane_transition_class_bus = '0;

    for (
      int lane_index = 0;
      lane_index < REQUEST_LANES;
      lane_index++
    ) begin
      logic [CELL_INDEX_BITS-1:0] packed_cell_index;
      int element_index_int;
      logic [STATE_BITS-1:0] retained_state;
      logic [STATE_BITS-1:0] requested_target;
      frp_m31_transition_class_e class_value;

      packed_cell_index =
        lane_cell_index_value(lane_index);

      element_index_int =
        int'(packed_cell_index);

      requested_target =
        lane_target_value(lane_index);

      retained_state = FRP_STATE_ZERO;

      if (element_index_int < CELLS) begin
        retained_state =
          state_q[
            (element_index_int*STATE_BITS) +: STATE_BITS
          ];
      end

      class_value =
        frp_classify_transition(
          retained_state,
          requested_target,
          FRP_STATE_ZERO
        );

      lane_transition_class_bus[
        (lane_index*FRP_M31_TRANSITION_CLASS_BITS)
        +: FRP_M31_TRANSITION_CLASS_BITS
      ] = class_value;
    end
  end

  assign pending_completion_accept_mask =
    capacity_accept_mask
    & pending_completion_candidate;

  // --------------------------------------------------------------------------
  // Scheduler
  // --------------------------------------------------------------------------

  frp_m31_scheduler #(
    .COUNTER_BITS(COUNTER_BITS)
  ) u_scheduler (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .tick_index_q(tick_index_q),
    .period_index_q(period_index_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(
      scheduler_count_neutralize_q
    ),
    .free_enable(free_enable),
    .balance_enable(balance_enable),
    .commit_enable(commit_enable),
    .excite_enable(excite_enable),
    .neutralize_enable(neutralize_enable),
    .scheduler_mode_reserved(scheduler_mode_reserved),
    .scheduler_state_reserved(scheduler_state_reserved),
    .scheduler_valid(scheduler_valid),
    .scheduler_counts_valid(scheduler_counts_valid)
  );

  // --------------------------------------------------------------------------
  // Request-lane arbitration
  // --------------------------------------------------------------------------

  frp_m31_request_lanes #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_request_lanes (
    .tick_enable(tick_enable),
    .scheduler_state(scheduler_state_q),
    .request_valid(request_valid),
    .request_cell_index(request_cell_index),
    .request_target(request_target),
    .state_q(state_q),
    .target_q(target_q),
    .pending_route_q(pending_route_q),
    .request_accept(request_accept_lane),
    .request_reject(request_reject_lane),
    .request_reject_invalid_cell(
      request_reject_invalid_cell
    ),
    .request_reject_invalid_target(
      request_reject_invalid_target
    ),
    .request_reject_duplicate_cell(
      request_reject_duplicate_cell
    ),
    .request_reject_scheduler(
      request_reject_scheduler
    ),
    .request_reject_capacity(
      request_reject_capacity_lane
    ),
    .request_reject_pending_busy(
      request_reject_pending_busy
    ),
    .request_reject_tick_disabled(
      request_reject_tick_disabled
    ),
    .request_neutralized(
      request_neutralized_lane
    ),
    .accepted_cell_mask(
      request_accepted_cell_mask
    ),
    .rejected_cell_mask(
      request_rejected_cell_mask
    ),
    .neutral_routed_cell_mask(
      request_neutral_routed_cell_mask
    ),
    .requested_direct_cell_mask(
      request_requested_direct_cell_mask
    ),
    .accepted_changes(request_accepted_changes),
    .requested_lane_events(requested_lane_events),
    .accepted_lane_events(accepted_lane_events),
    .rejected_lane_events(rejected_lane_events),
    .requested_direct_events(
      request_requested_direct_events
    ),
    .prevented_direct_events(
      request_prevented_direct_events
    ),
    .neutral_routed_events(
      request_neutral_routed_events
    ),
    .request_lane_order_valid(
      request_lane_order_valid
    ),
    .request_cell_domain_valid(
      request_cell_domain_valid
    ),
    .request_target_domain_valid(
      request_target_domain_valid
    ),
    .duplicate_cell_guard_valid(
      duplicate_cell_guard_valid
    ),
    .scheduler_gate_valid(
      request_scheduler_gate_valid
    ),
    .transition_capacity_valid(
      request_transition_capacity_valid
    ),
    .active_neutral_routing_valid(
      request_active_neutral_routing_valid
    ),
    .no_actual_direct_events(
      request_no_actual_direct_events
    ),
    .no_queue_overflow(
      request_no_queue_overflow
    )
  );

  // --------------------------------------------------------------------------
  // Active-neutral candidate generation
  // --------------------------------------------------------------------------

  frp_m31_active_neutral #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_active_neutral (
    .tick_enable(tick_enable),
    .scheduler_state(scheduler_state_q),
    .state_q(state_q),
    .pending_route_q(pending_route_q),
    .request_accept(request_accept_lane),
    .request_neutralized(request_neutralized_lane),
    .request_cell_index(request_cell_index),
    .request_target(request_target),
    .pending_completion_enable(
      pending_completion_candidate
    ),
    .state_candidate_d(state_candidate_d),
    .transition_valid_mask(transition_valid_mask),
    .same_state_mask(same_state_mask),
    .zero_to_nonzero_mask(zero_to_nonzero_mask),
    .nonzero_to_zero_mask(nonzero_to_zero_mask),
    .opposite_polarity_mask(opposite_polarity_mask),
    .neutral_routed_mask(
      transition_neutral_routed_mask
    ),
    .pending_completion_mask(
      transition_pending_completion_mask
    ),
    .actual_direct_mask(
      transition_actual_direct_mask
    ),
    .reserved_transition_mask(
      reserved_transition_mask
    ),
    .accepted_change_candidate_mask(
      accepted_change_candidate_mask
    ),
    .same_state_events(same_state_events),
    .zero_to_nonzero_events(
      zero_to_nonzero_events
    ),
    .nonzero_to_zero_events(
      nonzero_to_zero_events
    ),
    .requested_direct_events(
      transition_requested_direct_events
    ),
    .prevented_direct_events(
      transition_prevented_direct_events
    ),
    .neutral_routed_events(
      transition_neutral_routed_events
    ),
    .pending_completion_events(
      transition_pending_completion_events
    ),
    .actual_direct_events(
      transition_actual_direct_events
    ),
    .reserved_transition_events(
      reserved_transition_events
    ),
    .accepted_change_candidate_events(
      accepted_change_candidate_events
    ),
    .transition_domain_valid(
      transition_domain_valid
    ),
    .active_neutral_routing_valid(
      active_neutral_routing_valid
    ),
    .pending_completion_from_zero_valid(
      transition_pending_completion_from_zero_valid
    ),
    .no_reserved_transition(
      no_reserved_transition
    ),
    .no_actual_direct_events(
      transition_no_actual_direct_events
    ),
    .transition_capacity_valid(
      transition_capacity_valid_local
    ),
    .state_output_domain_valid(
      transition_state_output_domain_valid
    ),
    .transition_replay_deterministic(
      transition_replay_deterministic
    )
  );

  // --------------------------------------------------------------------------
  // Transition-capacity guard
  // --------------------------------------------------------------------------

  frp_m31_capacity_guard #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_capacity_guard (
    .tick_enable(tick_enable),
    .scheduler_state(scheduler_state_q),
    .request_accept_candidate(request_accept_lane),
    .request_cell_index(request_cell_index),
    .transition_class(lane_transition_class_bus),
    .pending_completion_candidate(
      pending_completion_candidate
    ),
    .neutral_routed_candidate(
      transition_neutral_routed_mask
    ),
    .state_q(state_q),
    .state_candidate_d(state_candidate_d),
    .request_accept_capacity(
      request_accept_capacity
    ),
    .request_reject_capacity(
      request_reject_capacity
    ),
    .capacity_accept_mask(capacity_accept_mask),
    .capacity_reject_mask(capacity_reject_mask),
    .accepted_change_mask(
      capacity_accepted_change_mask
    ),
    .accepted_changes(capacity_accepted_changes),
    .capacity_remaining(capacity_remaining),
    .capacity_exhausted(capacity_exhausted),
    .switch_load_numerator(
      capacity_switch_load_numerator
    ),
    .capacity_candidate_events(
      capacity_candidate_events
    ),
    .capacity_accept_events(
      capacity_accept_events
    ),
    .capacity_reject_events(
      capacity_reject_events
    ),
    .capacity_exhausted_events(
      capacity_exhausted_events
    ),
    .accepted_change_events(
      capacity_accepted_change_events
    ),
    .transition_capacity_valid(
      capacity_transition_capacity_valid
    ),
    .accepted_changes_within_limit(
      accepted_changes_within_limit
    ),
    .capacity_remaining_valid(
      capacity_remaining_valid
    ),
    .capacity_exhaustion_valid(
      capacity_exhaustion_valid
    ),
    .same_state_capacity_valid(
      same_state_capacity_valid
    ),
    .pending_capacity_valid(
      capacity_pending_capacity_valid
    ),
    .active_neutral_capacity_valid(
      capacity_active_neutral_capacity_valid
    ),
    .switch_load_bound_valid(
      switch_load_bound_valid
    ),
    .no_queue_overflow(
      capacity_no_queue_overflow
    ),
    .no_actual_direct_events(
      capacity_no_actual_direct_events
    )
  );

  // --------------------------------------------------------------------------
  // Pending-route retained register
  // --------------------------------------------------------------------------

  frp_m31_pending_routes #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_pending_routes (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .state_q(state_q),
    .request_accept(request_accept_capacity),
    .request_neutralized(request_neutralized_lane),
    .request_cell_index(request_cell_index),
    .request_target(request_target),
    .pending_completion_accept_mask(
      pending_completion_accept_mask
    ),
    .pending_route_q(pending_route_q),
    .pending_route_d(pending_route_d),
    .pending_active_mask(pending_active_mask),
    .pending_created_mask(pending_created_mask),
    .pending_completed_mask(pending_completed_mask),
    .pending_cleared_mask(pending_cleared_mask),
    .pending_retained_mask(pending_retained_mask),
    .pending_blocked_mask(pending_blocked_mask),
    .pending_reserved_mask(pending_reserved_mask),
    .pending_overflow_mask(pending_overflow_mask),
    .pending_active_count(pending_active_count),
    .pending_created_events(pending_created_events),
    .pending_completed_events(
      pending_completed_events
    ),
    .pending_cleared_events(pending_cleared_events),
    .pending_retained_events(
      pending_retained_events
    ),
    .pending_reserved_events(
      pending_reserved_events
    ),
    .neutral_routed_events(
      pending_neutral_routed_events
    ),
    .prevented_direct_events(
      pending_prevented_direct_events
    ),
    .queue_overflow_events(
      pending_queue_overflow_events
    ),
    .actual_direct_events(
      pending_actual_direct_events
    ),
    .pending_domain_valid(pending_domain_valid),
    .pending_polarity_valid(
      pending_polarity_valid
    ),
    .pending_completion_from_zero_valid(
      pending_completion_from_zero_valid
    ),
    .pending_non_overwrite_valid(
      pending_non_overwrite_valid
    ),
    .pending_capacity_valid(
      pending_capacity_valid
    ),
    .pending_replay_deterministic(
      pending_replay_deterministic
    ),
    .no_pending_reserved_state(
      no_pending_reserved_state
    ),
    .no_queue_overflow(
      pending_no_queue_overflow
    ),
    .no_actual_direct_events(
      pending_no_actual_direct_events
    )
  );

  // --------------------------------------------------------------------------
  // Retained-state writeback
  // --------------------------------------------------------------------------

  frp_m31_state_update #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_state_update (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .scheduler_state(scheduler_state_q),
    .state_candidate_d(state_candidate_d),
    .capacity_accept_mask(capacity_accept_mask),
    .accepted_change_candidate_mask(
      accepted_change_candidate_mask
    ),
    .neutral_routed_mask(
      transition_neutral_routed_mask
    ),
    .pending_completion_mask(
      transition_pending_completion_mask
    ),
    .reserved_transition_mask(
      reserved_transition_mask
    ),
    .actual_direct_mask(
      transition_actual_direct_mask
    ),
    .state_q(state_q),
    .state_d(state_d),
    .state_out(state_out),
    .state_write_enable_mask(
      state_write_enable_mask
    ),
    .state_hold_mask(state_hold_mask),
    .state_reset_mask(state_reset_mask),
    .state_reserved_mask(state_reserved_mask),
    .accepted_changes(
      state_update_accepted_changes
    ),
    .switch_load_numerator(
      state_update_switch_load_numerator
    ),
    .state_write_events(state_write_events),
    .state_hold_events(state_hold_events),
    .state_reset_events(state_reset_events),
    .accepted_change_events(
      state_accepted_change_events
    ),
    .neutral_routed_commit_events(
      neutral_routed_commit_events
    ),
    .pending_completion_commit_events(
      pending_completion_commit_events
    ),
    .reserved_state_events(
      state_reserved_state_events
    ),
    .actual_direct_events(
      state_actual_direct_events
    ),
    .state_domain_valid(state_domain_valid),
    .state_output_domain_valid(
      state_output_domain_valid
    ),
    .state_update_valid(state_update_valid),
    .state_write_capacity_valid(
      state_write_capacity_valid
    ),
    .same_state_hold_valid(
      same_state_hold_valid
    ),
    .active_neutral_writeback_valid(
      active_neutral_writeback_valid
    ),
    .pending_completion_writeback_valid(
      pending_completion_writeback_valid
    ),
    .no_reserved_state_output(
      no_reserved_state_output
    ),
    .no_actual_direct_events(
      state_update_no_actual_direct_events
    )
  );

  // --------------------------------------------------------------------------
  // Public core outputs
  // --------------------------------------------------------------------------

  assign pending_route_out = pending_route_q;

  assign request_accept = request_accept_capacity;

  assign request_reject =
    request_reject_lane
    | request_reject_capacity;

  assign accepted_cell_mask =
    request_accepted_cell_mask
    & capacity_accept_mask;

  assign neutral_routed_cell_mask =
    transition_neutral_routed_mask
    & capacity_accept_mask;

  assign accepted_change_mask =
    capacity_accepted_change_mask;

  assign accepted_changes =
    capacity_accepted_changes;

  assign switch_load_numerator =
    capacity_switch_load_numerator;

  // Use one canonical transition-stage source for each direct-request event.
  // The same event is therefore not added repeatedly at arbitration,
  // transition generation, pending storage, and retained writeback.

  assign requested_direct_events =
    transition_requested_direct_events;

  assign prevented_direct_events =
    transition_prevented_direct_events;

  assign neutral_routed_events =
    transition_neutral_routed_events;

  // Actual execution is defined at the retained-state writeback boundary.

  assign actual_direct_events =
    state_actual_direct_events;

  assign reserved_state_events =
    reserved_transition_events
    + pending_reserved_events
    + state_reserved_state_events;

  assign queue_overflow_events =
    pending_queue_overflow_events;

  // --------------------------------------------------------------------------
  // Integrated invariant aggregation
  // --------------------------------------------------------------------------

  always_comb begin
    invariant_flags = '0;

    invariant_flags[FRP_INV_STATE_DOMAIN_VALID] =
      request_cell_domain_valid
      && request_target_domain_valid
      && transition_domain_valid
      && transition_state_output_domain_valid
      && pending_domain_valid
      && state_domain_valid
      && state_output_domain_valid;

    invariant_flags[FRP_INV_SCHEDULER_COUNTS_VALID] =
      scheduler_valid
      && scheduler_counts_valid;

    invariant_flags[FRP_INV_REQUEST_LANE_ORDER_VALID] =
      request_lane_order_valid
      && request_cell_domain_valid
      && request_target_domain_valid
      && duplicate_cell_guard_valid
      && request_scheduler_gate_valid
      && request_transition_capacity_valid
      && request_active_neutral_routing_valid;

    invariant_flags[FRP_INV_PENDING_POLARITY_VALID] =
      pending_domain_valid
      && pending_polarity_valid
      && pending_completion_from_zero_valid
      && pending_non_overwrite_valid
      && pending_capacity_valid
      && pending_replay_deterministic
      && no_pending_reserved_state;

    invariant_flags[FRP_INV_ACTIVE_NEUTRAL_VALID] =
      request_active_neutral_routing_valid
      && active_neutral_routing_valid
      && transition_pending_completion_from_zero_valid
      && transition_replay_deterministic
      && capacity_active_neutral_capacity_valid
      && active_neutral_writeback_valid
      && pending_completion_writeback_valid
      && transition_no_actual_direct_events
      && state_update_no_actual_direct_events;

    invariant_flags[FRP_INV_TRANSITION_CAPACITY_VALID] =
      request_transition_capacity_valid
      && transition_capacity_valid_local
      && capacity_transition_capacity_valid
      && accepted_changes_within_limit
      && capacity_remaining_valid
      && capacity_exhaustion_valid
      && same_state_capacity_valid
      && capacity_pending_capacity_valid
      && capacity_active_neutral_capacity_valid
      && switch_load_bound_valid
      && (
        capacity_accepted_changes
        == state_update_accepted_changes
      )
      && (
        capacity_accepted_change_mask
        == state_write_enable_mask
      )
      && (
        capacity_switch_load_numerator
        == state_update_switch_load_numerator
      );

    invariant_flags[FRP_INV_STATE_UPDATE_VALID] =
      state_update_valid
      && state_domain_valid
      && state_output_domain_valid
      && state_write_capacity_valid
      && same_state_hold_valid
      && active_neutral_writeback_valid
      && pending_completion_writeback_valid
      && no_reserved_state_output
      && state_update_no_actual_direct_events;

    invariant_flags[FRP_INV_NO_ACTUAL_DIRECT_EVENTS] =
      request_no_actual_direct_events
      && transition_no_actual_direct_events
      && pending_no_actual_direct_events
      && capacity_no_actual_direct_events
      && state_update_no_actual_direct_events
      && (actual_direct_events == '0);

    invariant_flags[FRP_INV_NO_RESERVED_STATE] =
      no_reserved_transition
      && no_pending_reserved_state
      && no_reserved_state_output
      && (reserved_state_events == '0);

    invariant_flags[FRP_INV_NO_QUEUE_OVERFLOW] =
      request_no_queue_overflow
      && pending_no_queue_overflow
      && capacity_no_queue_overflow
      && (queue_overflow_events == '0);
  end

endmodule : frp_m31_execution_core

`endif
