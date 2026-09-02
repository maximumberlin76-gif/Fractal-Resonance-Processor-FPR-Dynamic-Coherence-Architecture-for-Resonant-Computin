// SPDX-License-Identifier: Apache-2.0
/*
    FRP M31 Active Neutral Transition Module

    Project:
        Fractal Resonance Processor (FRP)
        Ternary Fractal Resonant Coherence Processor

    Version:
        FRP v3.3.0

    Milestone:
        M31 RTL Core Realization and Execution Semantics Package

    Purpose:
        Generates the complete pre-capacity retained-state transition
        candidate for the M31 RTL execution chain.

        Architectural contract:
            - balanced ternary retained states {-1, 0, 1};
            - active neutral 0 is an executable computational state;
            - same-state retention is legal and consumes no state change;
            - 0 -> +/-1 is a commit-capable release;
            - +/-1 -> 0 is a neutralize-capable transition;
            - direct -1 <-> 1 execution is forbidden;
            - opposite-polarity requests execute only the first tick leg
              +/-1 -> 0 and retain the opposite target in pending_route;
            - pending routes complete only on a later eligible tick from 0;
            - pending completion has priority over a new same-element_index request;
            - capacity selection is performed downstream without changing
              the transition class or the retained pending-route polarity.
*/

`ifndef FRP_M31_ACTIVE_NEUTRAL_SV
`define FRP_M31_ACTIVE_NEUTRAL_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_active_neutral #(
    parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
    parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
    parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
    parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
    parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
    input logic tick_enable,
    input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,

    input logic [(CELLS * STATE_BITS) - 1:0] state_q,
    input logic [(CELLS * STATE_BITS) - 1:0] pending_route_q,

    input logic [REQUEST_LANES - 1:0] request_accept,
    input logic [REQUEST_LANES - 1:0] request_neutralized,
    input logic [(REQUEST_LANES * CELL_INDEX_BITS) - 1:0] request_cell_index,
    input logic [(REQUEST_LANES * STATE_BITS) - 1:0] request_target,

    input logic [CELLS - 1:0] pending_completion_enable,

    output logic [(CELLS * STATE_BITS) - 1:0] state_candidate_d,

    output logic [CELLS - 1:0] transition_valid_mask,
    output logic [CELLS - 1:0] same_state_mask,
    output logic [CELLS - 1:0] zero_to_nonzero_mask,
    output logic [CELLS - 1:0] nonzero_to_zero_mask,
    output logic [CELLS - 1:0] opposite_polarity_mask,
    output logic [CELLS - 1:0] neutral_routed_mask,
    output logic [CELLS - 1:0] pending_completion_mask,
    output logic [CELLS - 1:0] actual_direct_mask,
    output logic [CELLS - 1:0] reserved_transition_mask,
    output logic [CELLS - 1:0] accepted_change_candidate_mask,

    output logic [COUNTER_BITS - 1:0] same_state_events,
    output logic [COUNTER_BITS - 1:0] zero_to_nonzero_events,
    output logic [COUNTER_BITS - 1:0] nonzero_to_zero_events,
    output logic [COUNTER_BITS - 1:0] requested_direct_events,
    output logic [COUNTER_BITS - 1:0] prevented_direct_events,
    output logic [COUNTER_BITS - 1:0] neutral_routed_events,
    output logic [COUNTER_BITS - 1:0] pending_completion_events,
    output logic [COUNTER_BITS - 1:0] actual_direct_events,
    output logic [COUNTER_BITS - 1:0] reserved_transition_events,
    output logic [COUNTER_BITS - 1:0] accepted_change_candidate_events,

    output logic transition_domain_valid,
    output logic active_neutral_routing_valid,
    output logic pending_completion_from_zero_valid,
    output logic no_reserved_transition,
    output logic no_actual_direct_events,
    output logic transition_capacity_valid,
    output logic state_output_domain_valid,
    output logic transition_replay_deterministic
);

    import frp_m31_pkg::*;

    localparam logic [COUNTER_BITS - 1:0] COUNTER_ONE =
        {{(COUNTER_BITS - 1){1'b0}}, 1'b1};

    logic [(CELLS * STATE_BITS) - 1:0] state_candidate_next;
    logic scheduler_state_valid;

    function automatic logic [STATE_BITS - 1:0] packed_state_value(
        input logic [(CELLS * STATE_BITS) - 1:0] packed_state,
        input int element_index
    );
        begin
            packed_state_value = packed_state[
                (element_index * STATE_BITS) +: STATE_BITS
            ];
        end
    endfunction

    function automatic logic [(CELLS * STATE_BITS) - 1:0]
        set_packed_state_value(
            input logic [(CELLS * STATE_BITS) - 1:0] packed_state,
            input int element_index,
            input logic [STATE_BITS - 1:0] element_value
        );

        logic [(CELLS * STATE_BITS) - 1:0] updated_state;

        begin
            updated_state = packed_state;

            updated_state[
                (element_index * STATE_BITS) +: STATE_BITS
            ] = element_value;

            set_packed_state_value = updated_state;
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
        state_candidate_next = state_q;

        scheduler_state_valid =
            frp_scheduler_state_is_valid(
                scheduler_state
            );

        transition_valid_mask = '0;
        same_state_mask = '0;
        zero_to_nonzero_mask = '0;
        nonzero_to_zero_mask = '0;
        opposite_polarity_mask = '0;
        neutral_routed_mask = '0;
        pending_completion_mask = '0;
        actual_direct_mask = '0;
        reserved_transition_mask = '0;
        accepted_change_candidate_mask = '0;

        same_state_events = '0;
        zero_to_nonzero_events = '0;
        nonzero_to_zero_events = '0;
        requested_direct_events = '0;
        prevented_direct_events = '0;
        neutral_routed_events = '0;
        pending_completion_events = '0;
        actual_direct_events = '0;
        reserved_transition_events = '0;
        accepted_change_candidate_events = '0;

        transition_domain_valid = 1'b1;
        active_neutral_routing_valid = 1'b1;
        pending_completion_from_zero_valid = 1'b1;
        no_reserved_transition = 1'b1;
        no_actual_direct_events = 1'b1;
        transition_capacity_valid = 1'b1;
        state_output_domain_valid = 1'b1;
        transition_replay_deterministic = 1'b1;

        // Validate the complete retained-state and pending-route domains.
        // Invalid operands are exposed and never converted into an accepted
        // transition candidate.

        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] pending_target;

            retained_state =
                packed_state_value(
                    state_q,
                    element_index
                );

            pending_target =
                packed_state_value(
                    pending_route_q,
                    element_index
                );

            if (
                !frp_is_valid_ternary(retained_state)
                || !frp_is_valid_ternary(pending_target)
            ) begin
                reserved_transition_mask[
                    element_index
                ] = 1'b1;

                reserved_transition_events =
                    reserved_transition_events
                    + COUNTER_ONE;

                transition_domain_valid = 1'b0;
                no_reserved_transition = 1'b0;
            end
        end

        // Pending-route completion is evaluated before explicit request
        // lanes. A retained pending polarity owns its element_index until a later
        // commit-capable and capacity-approved tick completes 0 -> target.

        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] pending_target;

            logic completion_requested;
            logic completion_operands_valid;
            logic completion_scheduler_legal;

            retained_state =
                packed_state_value(
                    state_q,
                    element_index
                );

            pending_target =
                packed_state_value(
                    pending_route_q,
                    element_index
                );

            completion_requested =
                tick_enable
                && pending_completion_enable[
                    element_index
                ];

            completion_operands_valid =
                frp_is_valid_ternary(
                    retained_state
                )
                && frp_is_valid_ternary(
                    pending_target
                )
                && frp_is_nonzero(
                    pending_target
                );

            completion_scheduler_legal =
                scheduler_state_valid
                && frp_scheduler_is_commit_capable(
                    scheduler_state
                );

            if (completion_requested) begin
                if (
                    completion_operands_valid
                    && frp_is_zero(
                        retained_state
                    )
                    && completion_scheduler_legal
                ) begin
                    state_candidate_next =
                        set_packed_state_value(
                            state_candidate_next,
                            element_index,
                            pending_target
                        );

                    transition_valid_mask[
                        element_index
                    ] = 1'b1;

                    zero_to_nonzero_mask[
                        element_index
                    ] = 1'b1;

                    pending_completion_mask[
                        element_index
                    ] = 1'b1;

                    accepted_change_candidate_mask[
                        element_index
                    ] = 1'b1;

                    zero_to_nonzero_events =
                        zero_to_nonzero_events
                        + COUNTER_ONE;

                    pending_completion_events =
                        pending_completion_events
                        + COUNTER_ONE;

                    accepted_change_candidate_events =
                        accepted_change_candidate_events
                        + COUNTER_ONE;
                end else begin
                    pending_completion_from_zero_valid = 1'b0;
                    transition_replay_deterministic = 1'b0;

                    if (!completion_operands_valid) begin
                        reserved_transition_mask[
                            element_index
                        ] = 1'b1;

                        transition_domain_valid = 1'b0;
                        no_reserved_transition = 1'b0;
                    end
                end
            end
        end

               // Accepted request lanes are evaluated in deterministic ascending
        // lane order. Request arbitration has already prevented duplicate
        // accepted cells and blocked cells owned by a retained pending route.

        for (
            int lane_index = 0;
            lane_index < REQUEST_LANES;
            lane_index = lane_index + 1
        ) begin
            logic [CELL_INDEX_BITS - 1:0] packed_index;
            int element_index_int;

            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] requested_target;

            logic valid_index;
            logic valid_state;
            logic valid_target;
            logic pending_completion_owns_cell;
            logic scheduler_allows_class;

            frp_m31_transition_class_e transition_class;

            packed_index =
                lane_index_value(
                    lane_index
                );

            element_index_int =
                int'(packed_index);

            requested_target =
                lane_target_value(
                    lane_index
                );

            valid_index =
                (element_index_int < CELLS);

            retained_state = FRP_STATE_ZERO;
            valid_state = 1'b1;

            valid_target =
                frp_is_valid_ternary(
                    requested_target
                );

            pending_completion_owns_cell = 1'b0;
            transition_class = FRP_TRANS_INVALID;
            scheduler_allows_class = 1'b0;

            if (valid_index) begin
                retained_state =
                    packed_state_value(
                        state_q,
                        element_index_int
                    );

                valid_state =
                    frp_is_valid_ternary(
                        retained_state
                    );

                pending_completion_owns_cell =
                    pending_completion_mask[
                        element_index_int
                    ];
            end

            if (
                valid_index
                && valid_state
                && valid_target
            ) begin
                transition_class =
                    frp_classify_transition(
                        retained_state,
                        requested_target,
                        FRP_STATE_ZERO
                    );

                scheduler_allows_class =
                    frp_scheduler_allows_transition(
                        scheduler_state,
                        transition_class
                    );
            end

            if (
                tick_enable
                && request_accept[lane_index]
            ) begin
                if (!valid_index) begin
                    transition_domain_valid = 1'b0;
                    no_reserved_transition = 1'b0;
                    transition_replay_deterministic = 1'b0;
                end else if (
                    !valid_state
                    || !valid_target
                ) begin
                    reserved_transition_mask[
                        element_index_int
                    ] = 1'b1;

                    reserved_transition_events =
                        reserved_transition_events
                        + COUNTER_ONE;

                    transition_domain_valid = 1'b0;
                    no_reserved_transition = 1'b0;
                    transition_replay_deterministic = 1'b0;
                end else if (
                    pending_completion_owns_cell
                ) begin
                    // A retained pending route has strict priority.
                    // A new same-element_index request cannot replace its polarity.

                    transition_replay_deterministic = 1'b0;
                end else begin
                    unique case (transition_class)

                        FRP_TRANS_SAME_STATE: begin
                            transition_valid_mask[
                                element_index_int
                            ] = 1'b1;

                            same_state_mask[
                                element_index_int
                            ] = 1'b1;

                            same_state_events =
                                same_state_events
                                + COUNTER_ONE;
                        end

                        FRP_TRANS_ZERO_TO_NONZERO: begin
                            if (scheduler_allows_class) begin
                                state_candidate_next =
                                    set_packed_state_value(
                                        state_candidate_next,
                                        element_index_int,
                                        requested_target
                                    );

                                transition_valid_mask[
                                    element_index_int
                                ] = 1'b1;

                                zero_to_nonzero_mask[
                                    element_index_int
                                ] = 1'b1;

                                accepted_change_candidate_mask[
                                    element_index_int
                                ] = 1'b1;

                                zero_to_nonzero_events =
                                    zero_to_nonzero_events
                                    + COUNTER_ONE;

                                accepted_change_candidate_events =
                                    accepted_change_candidate_events
                                    + COUNTER_ONE;
                            end
                        end

                        FRP_TRANS_NONZERO_TO_ZERO: begin
                            if (scheduler_allows_class) begin
                                state_candidate_next =
                                    set_packed_state_value(
                                        state_candidate_next,
                                        element_index_int,
                                        FRP_ACTIVE_NEUTRAL
                                    );

                                transition_valid_mask[
                                    element_index_int
                                ] = 1'b1;

                                nonzero_to_zero_mask[
                                    element_index_int
                                ] = 1'b1;

                                accepted_change_candidate_mask[
                                    element_index_int
                                ] = 1'b1;

                                nonzero_to_zero_events =
                                    nonzero_to_zero_events
                                    + COUNTER_ONE;

                                accepted_change_candidate_events =
                                    accepted_change_candidate_events
                                    + COUNTER_ONE;
                            end
                        end

                        FRP_TRANS_OPPOSITE_POLARITY: begin
                            requested_direct_events =
                                requested_direct_events
                                + COUNTER_ONE;

                            if (
                                request_neutralized[
                                    lane_index
                                ]
                                && scheduler_allows_class
                            ) begin
                                // Only the first route leg executes now:
                                //
                                //     -1 -> 0
                                //     1 -> 0
                                //
                                // The opposite target remains available on
                                // request_target for capacity-approved
                                // storage by frp_m31_pending_routes.

                                state_candidate_next =
                                    set_packed_state_value(
                                        state_candidate_next,
                                        element_index_int,
                                        FRP_ACTIVE_NEUTRAL
                                    );

                                transition_valid_mask[
                                    element_index_int
                                ] = 1'b1;

                                opposite_polarity_mask[
                                    element_index_int
                                ] = 1'b1;

                                neutral_routed_mask[
                                    element_index_int
                                ] = 1'b1;

                                nonzero_to_zero_mask[
                                    element_index_int
                                ] = 1'b1;

                                accepted_change_candidate_mask[
                                    element_index_int
                                ] = 1'b1;

                                prevented_direct_events =
                                    prevented_direct_events
                                    + COUNTER_ONE;

                                neutral_routed_events =
                                    neutral_routed_events
                                    + COUNTER_ONE;

                                nonzero_to_zero_events =
                                    nonzero_to_zero_events
                                    + COUNTER_ONE;

                                accepted_change_candidate_events =
                                    accepted_change_candidate_events
                                    + COUNTER_ONE;
                            end else begin
                                active_neutral_routing_valid = 1'b0;
                            end
                        end

                        FRP_TRANS_RESERVED_OPERAND,
                        FRP_TRANS_INVALID: begin
                            reserved_transition_mask[
                                element_index_int
                            ] = 1'b1;

                            reserved_transition_events =
                                reserved_transition_events
                                + COUNTER_ONE;

                            transition_domain_valid = 1'b0;
                            no_reserved_transition = 1'b0;
                            transition_replay_deterministic = 1'b0;
                        end

                        default: begin
                            transition_replay_deterministic = 1'b0;
                        end

                    endcase
                end
            end
        end

        // Final candidate-state qualification detects any direct opposite
        // polarity execution after all deterministic priorities have been
        // applied. Capacity rejection later may only retain state; it cannot
        // replace this route with a direct polarity transition.

        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            logic [STATE_BITS - 1:0] retained_state;
            logic [STATE_BITS - 1:0] candidate_state;

            retained_state =
                packed_state_value(
                    state_q,
                    element_index
                );

            candidate_state =
                packed_state_value(
                    state_candidate_next,
                    element_index
                );

            if (
                !frp_is_valid_ternary(
                    candidate_state
                )
            ) begin
                reserved_transition_mask[
                    element_index
                ] = 1'b1;

                state_output_domain_valid = 1'b0;
                no_reserved_transition = 1'b0;
            end

            if (
                frp_is_valid_ternary(
                    retained_state
                )
                && frp_is_valid_ternary(
                    candidate_state
                )
                && frp_is_opposite_polarity(
                    retained_state,
                    candidate_state
                )
            ) begin
                actual_direct_mask[
                    element_index
                ] = 1'b1;

                actual_direct_events =
                    actual_direct_events
                    + COUNTER_ONE;

                no_actual_direct_events = 1'b0;
            end
        end

        state_candidate_d =
            state_candidate_next;

        transition_domain_valid =
            transition_domain_valid
            && state_output_domain_valid
            && no_reserved_transition;

        active_neutral_routing_valid =
            active_neutral_routing_valid
            && (
                prevented_direct_events
                >= requested_direct_events
            )
            && (
                neutral_routed_events
                >= prevented_direct_events
            )
            && no_actual_direct_events;

        // Candidate generation precedes the downstream capacity guard.
        // This flag qualifies candidate accounting and one-change-per-element_index
        // determinism. The capacity guard alone authorizes the bounded
        // subset that may reach retained-state writeback.

        transition_capacity_valid =
            (
                accepted_change_candidate_events
                == $countones(
                    accepted_change_candidate_mask
                )
            )
            && (
                (
                    accepted_change_candidate_mask
                    & actual_direct_mask
                )
                == '0
            );

        transition_replay_deterministic =
            transition_replay_deterministic
            && scheduler_state_valid
            && transition_domain_valid
            && pending_completion_from_zero_valid
            && active_neutral_routing_valid
            && no_actual_direct_events;
    end

endmodule : frp_m31_active_neutral

`endif 
