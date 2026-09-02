// SPDX-License-Identifier: Apache-2.0
/*
    FRP M31 Pending-Route Register Module

    Project:
        Fractal Resonance Processor (FRP)
        Ternary Fractal Resonant Coherence Processor

    Version:
        FRP v3.3.0

    Milestone:
        M31 RTL Core Realization and Execution Semantics Package

    Purpose:
        Retains the target polarity of every capacity-approved opposite-
        polarity request while the retained ternary state executes the
        mandatory active-neutral route:

            -1 -> 0 -> 1
            1 -> 0 -> -1

        The first eligible tick commits only the nonzero-to-zero leg and
        stores the requested opposite polarity. A later commit-capable and
        capacity-approved tick may complete only from retained state 0, after
        which the pending route is cleared.

    Preserved architecture:
        - one retained pending-route slot per element_index;
        - canonical balanced ternary route encoding;
        - pending completion priority over new same-element_index requests;
        - no overwrite of retained route polarity;
        - scheduler/capacity deferral without polarity loss;
        - deterministic ascending request-lane processing;
        - zero direct opposite-polarity execution;
        - zero queue overflow in qualified operation.
*/

`ifndef FRP_M31_PENDING_ROUTES_SV
`define FRP_M31_PENDING_ROUTES_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_pending_routes #(
    parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
    parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
    parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
    parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
    parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
    input logic clk,
    input logic rst_n,
    input logic tick_enable,
    input logic [(CELLS * STATE_BITS) - 1:0] state_q,
    input logic [REQUEST_LANES - 1:0] request_accept,
    input logic [REQUEST_LANES - 1:0] request_neutralized,
    input logic [(REQUEST_LANES * CELL_INDEX_BITS) - 1:0] request_cell_index,
    input logic [(REQUEST_LANES * STATE_BITS) - 1:0] request_target,
    input logic [CELLS - 1:0] pending_completion_accept_mask,

    output logic [(CELLS * STATE_BITS) - 1:0] pending_route_q,
    output logic [(CELLS * STATE_BITS) - 1:0] pending_route_d,
    output logic [CELLS - 1:0] pending_active_mask,
    output logic [CELLS - 1:0] pending_created_mask,
    output logic [CELLS - 1:0] pending_completed_mask,
    output logic [CELLS - 1:0] pending_cleared_mask,
    output logic [CELLS - 1:0] pending_retained_mask,
    output logic [CELLS - 1:0] pending_blocked_mask,
    output logic [CELLS - 1:0] pending_reserved_mask,
    output logic [CELLS - 1:0] pending_overflow_mask,

    output logic [COUNTER_BITS - 1:0] pending_active_count,
    output logic [COUNTER_BITS - 1:0] pending_created_events,
    output logic [COUNTER_BITS - 1:0] pending_completed_events,
    output logic [COUNTER_BITS - 1:0] pending_cleared_events,
    output logic [COUNTER_BITS - 1:0] pending_retained_events,
    output logic [COUNTER_BITS - 1:0] pending_reserved_events,
    output logic [COUNTER_BITS - 1:0] neutral_routed_events,
    output logic [COUNTER_BITS - 1:0] prevented_direct_events,
    output logic [COUNTER_BITS - 1:0] queue_overflow_events,
    output logic [COUNTER_BITS - 1:0] actual_direct_events,

    output logic pending_domain_valid,
    output logic pending_polarity_valid,
    output logic pending_completion_from_zero_valid,
    output logic pending_non_overwrite_valid,
    output logic pending_capacity_valid,
    output logic pending_replay_deterministic,
    output logic no_pending_reserved_state,
    output logic no_queue_overflow,
    output logic no_actual_direct_events
);

    import frp_m31_pkg::*;

    localparam logic [COUNTER_BITS - 1:0] COUNTER_ONE =
        {{(COUNTER_BITS - 1){1'b0}}, 1'b1};

    localparam logic [COUNTER_BITS - 1:0] REQUEST_LANE_LIMIT =
        REQUEST_LANES;

    logic [(CELLS * STATE_BITS) - 1:0] pending_route_next;
    logic [CELLS - 1:0] creation_claimed_mask;

    function automatic logic [STATE_BITS - 1:0] packed_value_at_index(
        input logic [(CELLS * STATE_BITS) - 1:0] packed_value,
        input int element_index
    );
        begin
            packed_value_at_index = packed_value[
                (element_index * STATE_BITS) +: STATE_BITS
            ];
        end
    endfunction

    function automatic logic [(CELLS * STATE_BITS) - 1:0]
        set_packed_value_at_index(
            input logic [(CELLS * STATE_BITS) - 1:0] packed_value,
            input int element_index,
            input logic [STATE_BITS - 1:0] element_value
        );

        logic [(CELLS * STATE_BITS) - 1:0] updated_value;

        begin
            updated_value = packed_value;

            updated_value[
                (element_index * STATE_BITS) +: STATE_BITS
            ] = element_value;

            set_packed_value_at_index = updated_value;
        end
    endfunction

    function automatic logic [CELL_INDEX_BITS - 1:0] lane_index_value(
        input int lane_index
    );
        begin
            lane_index_value = request_cell_index[
                (lane_index * CELL_INDEX_BITS) +: CELL_INDEX_BITS
            ];
        end
    endfunction

    function automatic logic [STATE_BITS - 1:0] lane_target_value(
        input int lane_index
    );
        begin
            lane_target_value = request_target[
                (lane_index * STATE_BITS) +: STATE_BITS
            ];
        end
    endfunction

    always_comb begin
        pending_route_next = pending_route_q;
        creation_claimed_mask = '0;

        pending_active_mask = '0;
        pending_created_mask = '0;
        pending_completed_mask = '0;
        pending_cleared_mask = '0;
        pending_retained_mask = '0;
        pending_blocked_mask = '0;
        pending_reserved_mask = '0;
        pending_overflow_mask = '0;

        pending_active_count = '0;
        pending_created_events = '0;
        pending_completed_events = '0;
        pending_cleared_events = '0;
        pending_retained_events = '0;
        pending_reserved_events = '0;
        neutral_routed_events = '0;
        prevented_direct_events = '0;
        queue_overflow_events = '0;
        actual_direct_events = '0;

        pending_domain_valid = 1'b1;
        pending_polarity_valid = 1'b1;
        pending_completion_from_zero_valid = 1'b1;
        pending_non_overwrite_valid = 1'b1;
        pending_capacity_valid = 1'b1;
        pending_replay_deterministic = 1'b1;
        no_pending_reserved_state = 1'b1;
        no_queue_overflow = 1'b1;
        no_actual_direct_events = 1'b1;

        // Current retained pending-route domain and active-route snapshot.
        for (
            int element_index = 0;
            element_index < CELLS;
            element_index++
        ) begin
            logic [STATE_BITS - 1:0] pending_value;

            pending_value = packed_value_at_index(
                pending_route_q,
                element_index
            );

            if (!frp_is_valid_ternary(pending_value)) begin
                pending_reserved_mask[element_index] = 1'b1;

                pending_reserved_events =
                    pending_reserved_events + COUNTER_ONE;

                pending_domain_valid = 1'b0;
                no_pending_reserved_state = 1'b0;
            end else if (frp_is_nonzero(pending_value)) begin
                pending_active_mask[element_index] = 1'b1;

                pending_active_count =
                    pending_active_count + COUNTER_ONE;
            end
        end

        // Capacity-approved completion has priority over new same-element_index input.
        for (
            int element_index = 0;
            element_index < CELLS;
            element_index++
        ) begin
            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] pending_value;
            logic route_active;
            logic completion_requested;
            logic completion_legal;

            retained_state = packed_value_at_index(
                state_q,
                element_index
            );

            pending_value = packed_value_at_index(
                pending_route_q,
                element_index
            );

            route_active =
                frp_is_valid_ternary(pending_value)
                && frp_is_nonzero(pending_value);

            completion_requested =
                tick_enable
                && pending_completion_accept_mask[element_index];

            completion_legal =
                frp_is_valid_ternary(retained_state)
                && frp_is_zero(retained_state)
                && route_active;

            if (completion_requested && completion_legal) begin
                pending_route_next = set_packed_value_at_index(
                    pending_route_next,
                    element_index,
                    FRP_STATE_ZERO
                );

                pending_completed_mask[element_index] = 1'b1;
                pending_cleared_mask[element_index] = 1'b1;

                pending_completed_events =
                    pending_completed_events + COUNTER_ONE;

                pending_cleared_events =
                    pending_cleared_events + COUNTER_ONE;
            end else if (route_active) begin
                pending_retained_mask[element_index] = 1'b1;
                pending_blocked_mask[element_index] = 1'b1;

                if (tick_enable) begin
                    pending_retained_events =
                        pending_retained_events + COUNTER_ONE;
                end

                if (completion_requested) begin
                    pending_completion_from_zero_valid = 1'b0;
                    pending_capacity_valid = 1'b0;
                    pending_replay_deterministic = 1'b0;
                end
            end else if (completion_requested) begin
                pending_capacity_valid = 1'b0;
                pending_replay_deterministic = 1'b0;
            end
        end

        // New route creation is legal only for a capacity-approved accepted
        // opposite-polarity request whose first leg is routed to active zero.
        for (
            int lane_index = 0;
            lane_index < REQUEST_LANES;
            lane_index++
        ) begin
            logic [CELL_INDEX_BITS - 1:0] packed_index_value;
            int element_index_int;

            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] existing_pending;
            logic [STATE_BITS - 1:0] requested_target;

            logic valid_index;
            logic route_request;
            logic route_relation_valid;
            logic route_slot_free;
            logic completion_owns_cell;
            logic duplicate_creation;

            packed_index_value =
                lane_index_value(lane_index);

            element_index_int =
                int'(packed_index_value);

            requested_target =
                lane_target_value(lane_index);

            valid_index =
                (element_index_int < CELLS);

            route_request =
                tick_enable
                && request_accept[lane_index]
                && request_neutralized[lane_index];

            retained_state = FRP_STATE_ZERO;
            existing_pending = FRP_STATE_ZERO;
            route_relation_valid = 1'b0;
            route_slot_free = 1'b0;
            completion_owns_cell = 1'b0;
            duplicate_creation = 1'b0;

            if (valid_index) begin
                retained_state = packed_value_at_index(
                    state_q,
                    element_index_int
                );

                existing_pending = packed_value_at_index(
                    pending_route_q,
                    element_index_int
                );

                route_relation_valid =
                    frp_is_valid_ternary(retained_state)
                    && frp_is_nonzero(retained_state)
                    && frp_is_valid_ternary(requested_target)
                    && frp_is_nonzero(requested_target)
                    && frp_is_opposite_polarity(
                        retained_state,
                        requested_target
                    );

                route_slot_free =
                    frp_is_valid_ternary(existing_pending)
                    && frp_is_zero(existing_pending);

                completion_owns_cell =
                    pending_completed_mask[element_index_int];

                duplicate_creation =
                    creation_claimed_mask[element_index_int];
            end

            if (route_request) begin
                neutral_routed_events =
                    neutral_routed_events + COUNTER_ONE;

                prevented_direct_events =
                    prevented_direct_events + COUNTER_ONE;

                if (!valid_index) begin
                    pending_domain_valid = 1'b0;
                    pending_replay_deterministic = 1'b0;
                end else if (!route_relation_valid) begin
                    pending_polarity_valid = 1'b0;
                    pending_replay_deterministic = 1'b0;
                end else if (
                    !route_slot_free
                    || completion_owns_cell
                    || duplicate_creation
                ) begin
                    pending_blocked_mask[element_index_int] = 1'b1;
                    pending_overflow_mask[element_index_int] = 1'b1;

                    queue_overflow_events =
                        queue_overflow_events + COUNTER_ONE;

                    pending_non_overwrite_valid = 1'b0;
                    pending_replay_deterministic = 1'b0;
                end else begin
                    pending_route_next = set_packed_value_at_index(
                        pending_route_next,
                        element_index_int,
                        requested_target
                    );

                    creation_claimed_mask[element_index_int] = 1'b1;
                    pending_created_mask[element_index_int] = 1'b1;

                    pending_created_events =
                        pending_created_events + COUNTER_ONE;
                end
            end
        end

        // Next-state domain, route-polarity retention, and completion clearing.
        for (
            int element_index = 0;
            element_index < CELLS;
            element_index++
        ) begin
            logic [STATE_BITS - 1:0] pending_q_value;
            logic [STATE_BITS - 1:0] pending_d_value;

            pending_q_value = packed_value_at_index(
                pending_route_q,
                element_index
            );

            pending_d_value = packed_value_at_index(
                pending_route_next,
                element_index
            );

            if (!frp_is_valid_ternary(pending_d_value)) begin
                pending_reserved_mask[element_index] = 1'b1;
                pending_domain_valid = 1'b0;
                no_pending_reserved_state = 1'b0;
            end

            if (
                frp_is_nonzero(pending_q_value)
                && !pending_completed_mask[element_index]
                && (pending_d_value != pending_q_value)
            ) begin
                pending_non_overwrite_valid = 1'b0;
                pending_polarity_valid = 1'b0;
            end

            if (
                pending_completed_mask[element_index]
                && !frp_is_zero(pending_d_value)
            ) begin
                pending_capacity_valid = 1'b0;
            end

            if (
                pending_created_mask[element_index]
                && !frp_is_nonzero(pending_d_value)
            ) begin
                pending_polarity_valid = 1'b0;
            end
        end

        no_queue_overflow =
            (queue_overflow_events == '0);

        no_actual_direct_events =
            (actual_direct_events == '0);

        pending_domain_valid =
            pending_domain_valid
            && no_pending_reserved_state;

        pending_polarity_valid =
            pending_polarity_valid
            && (
                neutral_routed_events
                >= pending_created_events
            )
            && (
                prevented_direct_events
                >= pending_created_events
            );

        pending_capacity_valid =
            pending_capacity_valid
            && (
                pending_completed_events
                <= REQUEST_LANE_LIMIT
            );
    end

    assign pending_route_d =
        pending_route_next;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pending_route_q <= '0;
        end else if (tick_enable) begin
            pending_route_q <= pending_route_d;
        end
    end

endmodule : frp_m31_pending_routes

`endif
