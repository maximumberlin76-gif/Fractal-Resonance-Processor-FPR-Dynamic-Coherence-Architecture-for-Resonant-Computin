// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Request-Lane Arbitration Module
//
// Project:
//   Fractal Resonance Processor (FRP)
//   Ternary Fractal Resonant Coherence Processor
//
// Version:
//   FRP v3.3.0
//
// Milestone:
//   M31 RTL Core Realization and Execution Semantics Package
//
// Purpose:
//   Deterministic request-lane arbitration for the integrated M31 RTL chain.
//
// Preserved architecture:
//   - balanced ternary targets {-1, 0, 1};
//   - active neutral 0 as an executable retained state;
//   - deterministic ascending request-lane order;
//   - one accepted request per element_index per tick;
//   - pending-route ownership before new same-element_index requests;
//   - scheduler-qualified transition admission;
//   - opposite-polarity routing through active neutral 0;
//   - no direct -1 <-> 1 execution;
//   - downstream transition-capacity qualification.

`ifndef FRP_M31_REQUEST_LANES_SV
`define FRP_M31_REQUEST_LANES_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_request_lanes #(
    parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
    parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
    parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
    parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
    parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
    input logic tick_enable,
    input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,
    input logic [REQUEST_LANES - 1:0] request_valid,
    input logic [(REQUEST_LANES * CELL_INDEX_BITS) - 1:0] request_cell_index,
    input logic [(REQUEST_LANES * STATE_BITS) - 1:0] request_target,
    input logic [(CELLS * STATE_BITS) - 1:0] state_q,
    input logic [(CELLS * STATE_BITS) - 1:0] target_q,
    input logic [(CELLS * STATE_BITS) - 1:0] pending_route_q,
    output logic [REQUEST_LANES - 1:0] request_accept,
    output logic [REQUEST_LANES - 1:0] request_reject,
    output logic [REQUEST_LANES - 1:0] request_reject_invalid_cell,
    output logic [REQUEST_LANES - 1:0] request_reject_invalid_target,
    output logic [REQUEST_LANES - 1:0] request_reject_duplicate_cell,
    output logic [REQUEST_LANES - 1:0] request_reject_scheduler,
    output logic [REQUEST_LANES - 1:0] request_reject_capacity,
    output logic [REQUEST_LANES - 1:0] request_reject_pending_busy,
    output logic [REQUEST_LANES - 1:0] request_reject_tick_disabled,
    output logic [REQUEST_LANES - 1:0] request_neutralized,
    output logic [CELLS - 1:0] accepted_cell_mask,
    output logic [CELLS - 1:0] rejected_cell_mask,
    output logic [CELLS - 1:0] neutral_routed_cell_mask,
    output logic [CELLS - 1:0] requested_direct_cell_mask,
    output logic [COUNTER_BITS - 1:0] accepted_changes,
    output logic [COUNTER_BITS - 1:0] requested_lane_events,
    output logic [COUNTER_BITS - 1:0] accepted_lane_events,
    output logic [COUNTER_BITS - 1:0] rejected_lane_events,
    output logic [COUNTER_BITS - 1:0] requested_direct_events,
    output logic [COUNTER_BITS - 1:0] prevented_direct_events,
    output logic [COUNTER_BITS - 1:0] neutral_routed_events,
    output logic request_lane_order_valid,
    output logic request_cell_domain_valid,
    output logic request_target_domain_valid,
    output logic duplicate_cell_guard_valid,
    output logic scheduler_gate_valid,
    output logic transition_capacity_valid,
    output logic active_neutral_routing_valid,
    output logic no_actual_direct_events,
    output logic no_queue_overflow
);

    import frp_m31_pkg::*;

    localparam logic [COUNTER_BITS - 1:0] COUNTER_ONE =
        {{(COUNTER_BITS - 1){1'b0}}, 1'b1};

    localparam logic [COUNTER_BITS - 1:0] REQUEST_LANE_LIMIT =
        REQUEST_LANES;

    logic [STATE_BITS - 1:0] domain_retained_w [0:CELLS - 1];
    logic [STATE_BITS - 1:0] domain_target_w [0:CELLS - 1];
    logic [STATE_BITS - 1:0] domain_pending_w [0:CELLS - 1];

    logic [CELL_INDEX_BITS - 1:0] lane_index_w [0:REQUEST_LANES - 1];
    integer lane_element_w [0:REQUEST_LANES - 1];
    logic [STATE_BITS - 1:0] lane_retained_w [0:REQUEST_LANES - 1];
    logic [STATE_BITS - 1:0] lane_target_w [0:REQUEST_LANES - 1];
    logic [STATE_BITS - 1:0] lane_pending_w [0:REQUEST_LANES - 1];
    logic [CELLS - 1:0] lane_cell_mask_w [0:REQUEST_LANES - 1];
    logic lane_invalid_index_w [0:REQUEST_LANES - 1];
    logic lane_invalid_target_w [0:REQUEST_LANES - 1];
    logic lane_duplicate_w [0:REQUEST_LANES - 1];
    logic lane_pending_busy_w [0:REQUEST_LANES - 1];
    logic lane_scheduler_blocked_w [0:REQUEST_LANES - 1];

    frp_m31_transition_class_e lane_class_w [0:REQUEST_LANES - 1];

    function automatic logic [STATE_BITS - 1:0] packed_state_value(
        input logic [(CELLS * STATE_BITS) - 1:0] packed_state,
        input int element_index
    );
        packed_state_value =
            packed_state[
                (element_index * STATE_BITS) +: STATE_BITS
            ];
    endfunction

    function automatic logic scheduler_allows_request_class(
        input frp_m31_scheduler_state_e sched,
        input frp_m31_transition_class_e transition_class
    );
        scheduler_allows_request_class = 1'b0;

        if (frp_scheduler_state_is_valid(sched)) begin
            unique case (transition_class)
                FRP_TRANS_SAME_STATE:
                    scheduler_allows_request_class = 1'b1;

                FRP_TRANS_ZERO_TO_NONZERO:
                    scheduler_allows_request_class =
                        frp_scheduler_is_commit_capable(sched);

                FRP_TRANS_NONZERO_TO_ZERO,
                FRP_TRANS_OPPOSITE_POLARITY:
                    scheduler_allows_request_class =
                        frp_scheduler_is_neutralize_capable(sched);

                default:
                    scheduler_allows_request_class = 1'b0;
            endcase
        end
    endfunction

    always_comb begin
        request_accept = '0;
        request_reject = '0;
        request_reject_invalid_cell = '0;
        request_reject_invalid_target = '0;
        request_reject_duplicate_cell = '0;
        request_reject_scheduler = '0;
        request_reject_capacity = '0;
        request_reject_pending_busy = '0;
        request_reject_tick_disabled = '0;
        request_neutralized = '0;

        accepted_cell_mask = '0;
        rejected_cell_mask = '0;
        neutral_routed_cell_mask = '0;
        requested_direct_cell_mask = '0;

        accepted_changes = '0;
        requested_lane_events = '0;
        accepted_lane_events = '0;
        rejected_lane_events = '0;
        requested_direct_events = '0;
        prevented_direct_events = '0;
        neutral_routed_events = '0;

        request_lane_order_valid = 1'b1;
        request_cell_domain_valid = 1'b1;
        request_target_domain_valid = 1'b1;
        duplicate_cell_guard_valid = 1'b1;
        scheduler_gate_valid = 1'b1;
        transition_capacity_valid = 1'b1;
        active_neutral_routing_valid = 1'b1;
        no_actual_direct_events = 1'b1;
        no_queue_overflow = 1'b1;

        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            domain_retained_w[element_index] = FRP_STATE_ZERO;
            domain_target_w[element_index] = FRP_STATE_ZERO;
            domain_pending_w[element_index] = FRP_STATE_ZERO;
        end

        for (
            int lane_index = 0;
            lane_index < REQUEST_LANES;
            lane_index = lane_index + 1
        ) begin
            lane_index_w[lane_index] = '0;
            lane_element_w[lane_index] = 0;
            lane_retained_w[lane_index] = FRP_STATE_ZERO;
            lane_target_w[lane_index] = FRP_STATE_ZERO;
            lane_pending_w[lane_index] = FRP_STATE_ZERO;
            lane_cell_mask_w[lane_index] = '0;
            lane_invalid_index_w[lane_index] = 1'b1;
            lane_invalid_target_w[lane_index] = 1'b1;
            lane_duplicate_w[lane_index] = 1'b0;
            lane_pending_busy_w[lane_index] = 1'b0;
            lane_scheduler_blocked_w[lane_index] = 1'b1;
            lane_class_w[lane_index] = FRP_TRANS_RESERVED_OPERAND;
        end

        for (
            int element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin
            domain_retained_w[element_index] =
                packed_state_value(
                    state_q,
                    element_index
                );

            domain_target_w[element_index] =
                packed_state_value(
                    target_q,
                    element_index
                );

            domain_pending_w[element_index] =
                packed_state_value(
                    pending_route_q,
                    element_index
                );

            if (
                !frp_is_valid_ternary(
                    domain_retained_w[element_index]
                )
            ) begin
                request_cell_domain_valid = 1'b0;
            end

            if (
                !frp_is_valid_ternary(
                    domain_target_w[element_index]
                )
            ) begin
                request_target_domain_valid = 1'b0;
            end

            if (
                !frp_is_valid_ternary(
                    domain_pending_w[element_index]
                )
            ) begin
                request_target_domain_valid = 1'b0;
            end
        end

        if (!tick_enable) begin
            request_reject_tick_disabled = request_valid;
        end else begin
            for (
                int lane_index = 0;
                lane_index < REQUEST_LANES;
                lane_index = lane_index + 1
            ) begin
                lane_index_w[lane_index] =
                    request_cell_index[
                        (lane_index * CELL_INDEX_BITS)
                        +: CELL_INDEX_BITS
                    ];

                lane_element_w[lane_index] =
                    int'(lane_index_w[lane_index]);

                lane_target_w[lane_index] =
                    request_target[
                        (lane_index * STATE_BITS)
                        +: STATE_BITS
                    ];

                lane_invalid_index_w[lane_index] =
                    lane_element_w[lane_index] >= CELLS;

                lane_invalid_target_w[lane_index] =
                    !frp_is_valid_ternary(
                        lane_target_w[lane_index]
                    );

                if (!lane_invalid_index_w[lane_index]) begin
                    lane_retained_w[lane_index] =
                        packed_state_value(
                            state_q,
                            lane_element_w[lane_index]
                        );

                    lane_pending_w[lane_index] =
                        packed_state_value(
                            pending_route_q,
                            lane_element_w[lane_index]
                        );

                    lane_cell_mask_w[lane_index][
                        lane_element_w[lane_index]
                    ] = 1'b1;
                end

                lane_class_w[lane_index] =
                    frp_classify_transition(
                        lane_retained_w[lane_index],
                        lane_target_w[lane_index],
                        FRP_STATE_ZERO
                    );

                lane_duplicate_w[lane_index] =
                    !lane_invalid_index_w[lane_index]
                    && (
                        (
                            accepted_cell_mask
                            & lane_cell_mask_w[lane_index]
                        )
                        != '0
                    );

                lane_pending_busy_w[lane_index] =
                    !lane_invalid_index_w[lane_index]
                    && frp_is_nonzero(
                        lane_pending_w[lane_index]
                    );

                lane_scheduler_blocked_w[lane_index] =
                    !scheduler_allows_request_class(
                        scheduler_state,
                        lane_class_w[lane_index]
                    );

                if (request_valid[lane_index]) begin
                    requested_lane_events =
                        requested_lane_events
                        + COUNTER_ONE;

                    if (lane_invalid_index_w[lane_index]) begin
                        request_reject[lane_index] = 1'b1;
                        request_reject_invalid_cell[lane_index] = 1'b1;
                        request_cell_domain_valid = 1'b0;

                        rejected_lane_events =
                            rejected_lane_events
                            + COUNTER_ONE;
                    end else if (
                        lane_invalid_target_w[lane_index]
                    ) begin
                        request_reject[lane_index] = 1'b1;
                        request_reject_invalid_target[lane_index] = 1'b1;
                        request_target_domain_valid = 1'b0;

                        rejected_cell_mask =
                            rejected_cell_mask
                            | lane_cell_mask_w[lane_index];

                        rejected_lane_events =
                            rejected_lane_events
                            + COUNTER_ONE;
                    end else if (
                        lane_duplicate_w[lane_index]
                    ) begin
                        request_reject[lane_index] = 1'b1;
                        request_reject_duplicate_cell[lane_index] = 1'b1;

                        rejected_cell_mask =
                            rejected_cell_mask
                            | lane_cell_mask_w[lane_index];

                        rejected_lane_events =
                            rejected_lane_events
                            + COUNTER_ONE;
                    end else if (
                        lane_pending_busy_w[lane_index]
                    ) begin
                        request_reject[lane_index] = 1'b1;
                        request_reject_pending_busy[lane_index] = 1'b1;

                        rejected_cell_mask =
                            rejected_cell_mask
                            | lane_cell_mask_w[lane_index];

                        rejected_lane_events =
                            rejected_lane_events
                            + COUNTER_ONE;
                    end else if (
                        lane_scheduler_blocked_w[lane_index]
                    ) begin
                        request_reject[lane_index] = 1'b1;
                        request_reject_scheduler[lane_index] = 1'b1;

                        rejected_cell_mask =
                            rejected_cell_mask
                            | lane_cell_mask_w[lane_index];

                        rejected_lane_events =
                            rejected_lane_events
                            + COUNTER_ONE;
                    end else begin
                        request_accept[lane_index] = 1'b1;

                        accepted_cell_mask =
                            accepted_cell_mask
                            | lane_cell_mask_w[lane_index];

                        accepted_lane_events =
                            accepted_lane_events
                            + COUNTER_ONE;

                        if (
                            lane_class_w[lane_index]
                            != FRP_TRANS_SAME_STATE
                        ) begin
                            accepted_changes =
                                accepted_changes
                                + COUNTER_ONE;
                        end

                        if (
                            lane_class_w[lane_index]
                            == FRP_TRANS_OPPOSITE_POLARITY
                        ) begin
                            request_neutralized[lane_index] = 1'b1;

                            requested_direct_cell_mask =
                                requested_direct_cell_mask
                                | lane_cell_mask_w[lane_index];

                            neutral_routed_cell_mask =
                                neutral_routed_cell_mask
                                | lane_cell_mask_w[lane_index];

                            requested_direct_events =
                                requested_direct_events
                                + COUNTER_ONE;

                            prevented_direct_events =
                                prevented_direct_events
                                + COUNTER_ONE;

                            neutral_routed_events =
                                neutral_routed_events
                                + COUNTER_ONE;
                        end
                    end
                end
            end
        end

        request_lane_order_valid =
            (
                (
                    request_accept
                    & request_reject
                )
                == '0
            )
            && (
                !tick_enable
                || (
                    (
                        request_accept
                        | request_reject
                    )
                    == request_valid
                )
            );

        duplicate_cell_guard_valid =
            (
                (
                    request_accept
                    & request_reject_duplicate_cell
                )
                == '0
            );

        scheduler_gate_valid =
            (
                (
                    request_accept
                    & request_reject_scheduler
                )
                == '0
            );

        transition_capacity_valid =
            accepted_changes <= REQUEST_LANE_LIMIT;

        active_neutral_routing_valid =
            (
                prevented_direct_events
                >= requested_direct_events
            )
            && (
                neutral_routed_events
                >= prevented_direct_events
            );

        no_actual_direct_events = 1'b1;
        no_queue_overflow = 1'b1;
    end

endmodule : frp_m31_request_lanes

`endif
