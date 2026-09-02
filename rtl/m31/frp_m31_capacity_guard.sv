// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Transition Capacity Guard Module
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
//   Enforces the M15-qualified per-tick retained-state transition boundary
//   without redefining scheduler, active-neutral, or pending-route semantics.
//
// Preserved architecture:
//   - transition_fraction = 0.25;
//   - pending-route completion precedes new request lanes;
//   - request lanes retain ascending deterministic order;
//   - same-state retention does not consume capacity;
//   - each legal state-changing tick leg consumes one capacity slot;
//   - opposite-polarity routing remains split through active neutral 0;
//   - rejected pending completion remains retained for a later eligible tick;
//   - capacity exhaustion never authorizes a direct -1 <-> 1 transition.

`ifndef FRP_M31_CAPACITY_GUARD_SV
`define FRP_M31_CAPACITY_GUARD_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_capacity_guard #(
    parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
    parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
    parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
    parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
    parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
    input logic tick_enable,
    input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,

    input logic [REQUEST_LANES - 1:0] request_accept_candidate,
    input logic [(REQUEST_LANES * CELL_INDEX_BITS) - 1:0] request_cell_index,
    input logic [(REQUEST_LANES * 4) - 1:0] transition_class,

    input logic [CELLS - 1:0] pending_completion_candidate,
    input logic [CELLS - 1:0] neutral_routed_candidate,

    input logic [(CELLS * STATE_BITS) - 1:0] state_q,
    input logic [(CELLS * STATE_BITS) - 1:0] state_candidate_d,

    output logic [REQUEST_LANES - 1:0] request_accept_capacity,
    output logic [REQUEST_LANES - 1:0] request_reject_capacity,

    output logic [CELLS - 1:0] capacity_accept_mask,
    output logic [CELLS - 1:0] capacity_reject_mask,
    output logic [CELLS - 1:0] accepted_change_mask,

    output logic [COUNTER_BITS - 1:0] accepted_changes,
    output logic [COUNTER_BITS - 1:0] capacity_remaining,
    output logic capacity_exhausted,
    output logic [COUNTER_BITS - 1:0] switch_load_numerator,

    output logic [COUNTER_BITS - 1:0] capacity_candidate_events,
    output logic [COUNTER_BITS - 1:0] capacity_accept_events,
    output logic [COUNTER_BITS - 1:0] capacity_reject_events,
    output logic [COUNTER_BITS - 1:0] capacity_exhausted_events,
    output logic [COUNTER_BITS - 1:0] accepted_change_events,

    output logic transition_capacity_valid,
    output logic accepted_changes_within_limit,
    output logic capacity_remaining_valid,
    output logic capacity_exhaustion_valid,
    output logic same_state_capacity_valid,
    output logic pending_capacity_valid,
    output logic active_neutral_capacity_valid,
    output logic switch_load_bound_valid,
    output logic no_queue_overflow,
    output logic no_actual_direct_events
);

    import frp_m31_pkg::*;

    localparam logic [COUNTER_BITS - 1:0] COUNTER_ONE =
        {{(COUNTER_BITS - 1){1'b0}}, 1'b1};

    localparam logic [COUNTER_BITS - 1:0] CAPACITY_LIMIT =
        REQUEST_LANES[COUNTER_BITS - 1:0];

    logic [CELLS - 1:0] direct_candidate_mask;

    function automatic logic [CELL_INDEX_BITS - 1:0] lane_cell_index(
        input int lane_index
    );
        begin
            lane_cell_index = request_cell_index[
                (lane_index * CELL_INDEX_BITS) +: CELL_INDEX_BITS
            ];
        end
    endfunction

    function automatic frp_m31_transition_class_e lane_transition_class(
        input int lane_index
    );
        begin
            lane_transition_class = frp_m31_transition_class_e'(
                transition_class[(lane_index * 4) +: 4]
            );
        end
    endfunction

    function automatic logic [STATE_BITS - 1:0] state_value_at_index(
        input logic [(CELLS * STATE_BITS) - 1:0] packed_state,
        input int element_index
    );
        begin
            state_value_at_index = packed_state[
                (element_index * STATE_BITS) +: STATE_BITS
            ];
        end
    endfunction

    function automatic logic lane_class_is_supported(
        input frp_m31_transition_class_e class_value
    );
        begin
            unique case (class_value)
                FRP_TRANS_SAME_STATE,
                FRP_TRANS_ZERO_TO_NONZERO,
                FRP_TRANS_NONZERO_TO_ZERO,
                FRP_TRANS_OPPOSITE_POLARITY:
                    lane_class_is_supported = 1'b1;

                default:
                    lane_class_is_supported = 1'b0;
            endcase
        end
    endfunction

    always_comb begin
        request_accept_capacity = '0;
        request_reject_capacity = '0;

        capacity_accept_mask = '0;
        capacity_reject_mask = '0;
        accepted_change_mask = '0;
        direct_candidate_mask = '0;

        accepted_changes = '0;
        capacity_remaining = CAPACITY_LIMIT;
        capacity_exhausted = 1'b0;
        switch_load_numerator = '0;

        capacity_candidate_events = '0;
        capacity_accept_events = '0;
        capacity_reject_events = '0;
        capacity_exhausted_events = '0;
        accepted_change_events = '0;

        transition_capacity_valid = 1'b1;
        accepted_changes_within_limit = 1'b1;
        capacity_remaining_valid = 1'b1;
        capacity_exhaustion_valid = 1'b1;
        same_state_capacity_valid = 1'b1;
        pending_capacity_valid = 1'b1;
        active_neutral_capacity_valid = 1'b1;
        switch_load_bound_valid = 1'b1;
        no_queue_overflow = 1'b1;
        no_actual_direct_events = 1'b1;

        // Pending-route completion has deterministic priority.
        //
        // A clean capacity rejection does not invalidate the pending route
        // and does not clear its retained target polarity.
        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            logic [STATE_BITS - 1:0] current_state;
            logic [STATE_BITS - 1:0] candidate_state;
            logic current_valid;
            logic candidate_valid;
            logic state_changes;
            logic capacity_available;

            current_state =
                state_value_at_index(
                    state_q,
                    element_index
                );

            candidate_state =
                state_value_at_index(
                    state_candidate_d,
                    element_index
                );

            current_valid =
                frp_is_valid_ternary(current_state);

            candidate_valid =
                frp_is_valid_ternary(candidate_state);

            state_changes =
                (current_state != candidate_state);

            capacity_available =
                (accepted_changes < CAPACITY_LIMIT);

            if (
                tick_enable
                && pending_completion_candidate[element_index]
            ) begin
                if (
                    !current_valid
                    || !candidate_valid
                    || !frp_is_zero(current_state)
                    || !frp_is_nonzero(candidate_state)
                    || !state_changes
                ) begin
                    capacity_reject_mask[element_index] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;

                    pending_capacity_valid = 1'b0;
                end else begin
                    capacity_candidate_events =
                        capacity_candidate_events
                        + COUNTER_ONE;

                    if (capacity_available) begin
                        capacity_accept_mask[element_index] = 1'b1;
                        accepted_change_mask[element_index] = 1'b1;

                        accepted_changes =
                            accepted_changes
                            + COUNTER_ONE;

                        capacity_accept_events =
                            capacity_accept_events
                            + COUNTER_ONE;

                        accepted_change_events =
                            accepted_change_events
                            + COUNTER_ONE;
                    end else begin
                        capacity_reject_mask[element_index] = 1'b1;

                        capacity_reject_events =
                            capacity_reject_events
                            + COUNTER_ONE;
                    end
                end
            end
        end

            // New request lanes follow retained pending-route priority and retain
        // deterministic ascending lane order.
        for (
            int lane_index = 0;
            lane_index < REQUEST_LANES;
            lane_index = lane_index + 1
        ) begin
            logic [CELL_INDEX_BITS - 1:0] packed_cell_index;
            int element_index_int;
            logic valid_cell;

            logic [STATE_BITS - 1:0] current_state;
            logic [STATE_BITS - 1:0] candidate_state;

            logic current_valid;
            logic candidate_valid;
            logic state_changes;
            logic capacity_available;
            logic class_supported;
            logic class_same_state;
            logic class_opposite_polarity;
            logic direct_candidate;
            logic neutral_route_legal;

            frp_m31_transition_class_e class_value;

            packed_cell_index =
                lane_cell_index(lane_index);

            element_index_int =
                int'(packed_cell_index);

            valid_cell =
                (element_index_int < CELLS);

            current_state = FRP_STATE_ZERO;
            candidate_state = FRP_STATE_ZERO;

            current_valid = 1'b1;
            candidate_valid = 1'b1;
            state_changes = 1'b0;
            direct_candidate = 1'b0;
            neutral_route_legal = 1'b0;

            class_value =
                lane_transition_class(lane_index);

            class_supported =
                lane_class_is_supported(class_value);

            class_same_state =
                (class_value == FRP_TRANS_SAME_STATE);

            class_opposite_polarity =
                (class_value == FRP_TRANS_OPPOSITE_POLARITY);

            capacity_available =
                (accepted_changes < CAPACITY_LIMIT);

            if (valid_cell) begin
                current_state =
                    state_value_at_index(
                        state_q,
                        element_index_int
                    );

                candidate_state =
                    state_value_at_index(
                        state_candidate_d,
                        element_index_int
                    );

                current_valid =
                    frp_is_valid_ternary(current_state);

                candidate_valid =
                    frp_is_valid_ternary(candidate_state);

                state_changes =
                    (current_state != candidate_state);

                direct_candidate =
                    frp_is_opposite_polarity(
                        current_state,
                        candidate_state
                    );

                if (direct_candidate) begin
                    direct_candidate_mask[element_index_int] = 1'b1;
                end

                neutral_route_legal =
                    neutral_routed_candidate[element_index_int]
                    && frp_is_nonzero(current_state)
                    && frp_is_zero(candidate_state)
                    && state_changes;
            end

            if (
                tick_enable
                && request_accept_candidate[lane_index]
            ) begin
                if (!valid_cell) begin
                    request_reject_capacity[lane_index] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;

                    transition_capacity_valid = 1'b0;
                end else if (
                    pending_completion_candidate[element_index_int]
                ) begin
                    // A retained pending route keeps priority even when its
                    // completion is deferred by exhausted capacity.
                    request_reject_capacity[lane_index] = 1'b1;
                    capacity_reject_mask[element_index_int] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;
                end else if (
                    capacity_accept_mask[element_index_int]
                ) begin
                    // A higher-priority candidate or earlier lane already
                    // owns this element_index for the current tick.
                    request_reject_capacity[lane_index] = 1'b1;
                    capacity_reject_mask[element_index_int] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;
                end else if (
                    !current_valid
                    || !candidate_valid
                    || !class_supported
                    || direct_candidate
                ) begin
                    request_reject_capacity[lane_index] = 1'b1;
                    capacity_reject_mask[element_index_int] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;

                    transition_capacity_valid = 1'b0;

                    if (direct_candidate) begin
                        active_neutral_capacity_valid = 1'b0;
                    end
                end else if (class_opposite_polarity) begin
                    capacity_candidate_events =
                        capacity_candidate_events
                        + COUNTER_ONE;

                    if (!neutral_route_legal) begin
                        request_reject_capacity[lane_index] = 1'b1;
                        capacity_reject_mask[element_index_int] = 1'b1;

                        capacity_reject_events =
                            capacity_reject_events
                            + COUNTER_ONE;

                        active_neutral_capacity_valid = 1'b0;
                    end else if (capacity_available) begin
                        request_accept_capacity[lane_index] = 1'b1;
                        capacity_accept_mask[element_index_int] = 1'b1;
                        accepted_change_mask[element_index_int] = 1'b1;

                        accepted_changes =
                            accepted_changes
                            + COUNTER_ONE;

                        capacity_accept_events =
                            capacity_accept_events
                            + COUNTER_ONE;

                        accepted_change_events =
                            accepted_change_events
                            + COUNTER_ONE;
                    end else begin
                        // Only the current neutral leg is deferred. No direct
                        // opposite-polarity execution is authorized.
                        request_reject_capacity[lane_index] = 1'b1;
                        capacity_reject_mask[element_index_int] = 1'b1;

                        capacity_reject_events =
                            capacity_reject_events
                            + COUNTER_ONE;
                    end
                end else if (!state_changes) begin
                    if (class_same_state) begin
                        request_accept_capacity[lane_index] = 1'b1;
                        capacity_accept_mask[element_index_int] = 1'b1;
                    end else begin
                        request_reject_capacity[lane_index] = 1'b1;
                        capacity_reject_mask[element_index_int] = 1'b1;

                        capacity_reject_events =
                            capacity_reject_events
                            + COUNTER_ONE;

                        same_state_capacity_valid = 1'b0;
                    end
                end else if (class_same_state) begin
                    request_reject_capacity[lane_index] = 1'b1;
                    capacity_reject_mask[element_index_int] = 1'b1;

                    capacity_reject_events =
                        capacity_reject_events
                        + COUNTER_ONE;

                    same_state_capacity_valid = 1'b0;
                end else begin
                    capacity_candidate_events =
                        capacity_candidate_events
                        + COUNTER_ONE;

                    if (capacity_available) begin
                        request_accept_capacity[lane_index] = 1'b1;
                        capacity_accept_mask[element_index_int] = 1'b1;
                        accepted_change_mask[element_index_int] = 1'b1;

                        accepted_changes =
                            accepted_changes
                            + COUNTER_ONE;

                        capacity_accept_events =
                            capacity_accept_events
                            + COUNTER_ONE;

                        accepted_change_events =
                            accepted_change_events
                            + COUNTER_ONE;
                    end else begin
                        request_reject_capacity[lane_index] = 1'b1;
                        capacity_reject_mask[element_index_int] = 1'b1;

                        capacity_reject_events =
                            capacity_reject_events
                            + COUNTER_ONE;
                    end
                end
            end
        end

        if (tick_enable) begin
            if (accepted_changes <= CAPACITY_LIMIT) begin
                capacity_remaining =
                    CAPACITY_LIMIT
                    - accepted_changes;
            end else begin
                capacity_remaining = '0;
            end

            capacity_exhausted =
                (accepted_changes == CAPACITY_LIMIT);

            if (capacity_exhausted) begin
                capacity_exhausted_events = COUNTER_ONE;
            end

            switch_load_numerator =
                accepted_changes;
        end

        accepted_changes_within_limit =
            (accepted_changes <= CAPACITY_LIMIT);

        capacity_remaining_valid =
            accepted_changes_within_limit
            && (capacity_remaining <= CAPACITY_LIMIT)
            && (
                capacity_remaining
                == (CAPACITY_LIMIT - accepted_changes)
            );

        capacity_exhaustion_valid =
            (
                capacity_exhausted
                == (accepted_changes == CAPACITY_LIMIT)
            );

        same_state_capacity_valid =
            same_state_capacity_valid
            && (
                capacity_accept_events
                == accepted_change_events
            );

        active_neutral_capacity_valid =
            active_neutral_capacity_valid
            && (
                (
                    accepted_change_mask
                    & neutral_routed_candidate
                )
                == (
                    capacity_accept_mask
                    & neutral_routed_candidate
                )
            );

        switch_load_bound_valid =
            (switch_load_numerator <= CAPACITY_LIMIT)
            && (
                switch_load_numerator
                == accepted_changes
            );

        no_actual_direct_events =
            (
                (
                    capacity_accept_mask
                    & direct_candidate_mask
                )
                == '0
            );

        transition_capacity_valid =
            transition_capacity_valid
            && frp_scheduler_state_is_valid(scheduler_state)
            && accepted_changes_within_limit
            && capacity_remaining_valid
            && capacity_exhaustion_valid
            && same_state_capacity_valid
            && pending_capacity_valid
            && active_neutral_capacity_valid
            && switch_load_bound_valid
            && no_queue_overflow
            && no_actual_direct_events;
    end

endmodule : frp_m31_capacity_guard

`endif
