// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Assertion Binding Layer
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
//   Verifies the externally visible M31 retained-state execution boundary.
//
// Protected architecture:
//   - canonical balanced ternary domain {-1, 0, 1};
//   - active neutral 0 as an executable retained state;
//   - forbidden direct -1 <-> 1 retained-state transitions;
//   - mandatory tick-separated opposite-polarity routing through 0;
//   - retained pending-route polarity;
//   - pending completion only from retained state 0;
//   - deterministic scheduler and request-lane boundaries;
//   - transition-capacity enforcement;
//   - zero direct, reserved-state, and queue-overflow events.

`ifndef FRP_M31_ASSERTIONS_SV
`define FRP_M31_ASSERTIONS_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_assertions #(
    parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
    parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
    parameter int REQUEST_LANES =
        frp_m31_pkg::frp_calc_request_lanes(CELLS),
    parameter int COUNTER_BITS =
        frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
    input logic clk,
    input logic rst_n,
    input logic tick_enable,
    input logic clear_counters,

    input frp_m31_pkg::frp_m31_scheduler_mode_e
        scheduler_mode_q,

    input frp_m31_pkg::frp_m31_scheduler_state_e
        scheduler_state_q,

    input logic [COUNTER_BITS - 1:0]
        ticks_recorded_q,

    input logic [COUNTER_BITS - 1:0]
        scheduler_count_free_q,

    input logic [COUNTER_BITS - 1:0]
        scheduler_count_balance_q,

    input logic [COUNTER_BITS - 1:0]
        scheduler_count_commit_q,

    input logic [COUNTER_BITS - 1:0]
        scheduler_count_excite_q,

    input logic [COUNTER_BITS - 1:0]
        scheduler_count_neutralize_q,

    input logic [(CELLS * STATE_BITS) - 1:0]
        state_out,

    input logic [(CELLS * STATE_BITS) - 1:0]
        pending_route_out,

    input logic [REQUEST_LANES - 1:0]
        request_accept,

    input logic [REQUEST_LANES - 1:0]
        request_reject,

    input logic [CELLS - 1:0]
        accepted_cell_mask,

    input logic [CELLS - 1:0]
        neutral_routed_cell_mask,

    input logic [CELLS - 1:0]
        accepted_change_mask,

    input logic [COUNTER_BITS - 1:0]
        accepted_changes,

    input logic [COUNTER_BITS - 1:0]
        capacity_remaining,

    input logic
        capacity_exhausted,

    input logic [COUNTER_BITS - 1:0]
        switch_load_numerator,

    input logic [COUNTER_BITS - 1:0]
        requested_direct_events,

    input logic [COUNTER_BITS - 1:0]
        prevented_direct_events,

    input logic [COUNTER_BITS - 1:0]
        neutral_routed_events,

    input logic [COUNTER_BITS - 1:0]
        actual_direct_events,

    input logic [COUNTER_BITS - 1:0]
        reserved_state_events,

    input logic [COUNTER_BITS - 1:0]
        queue_overflow_events,

    input logic [
        frp_m31_pkg::FRP_M31_INVARIANT_FLAGS - 1:0
    ] invariant_flags
);

    import frp_m31_pkg::*;

    localparam logic [COUNTER_BITS - 1:0]
        COUNTER_ONE =
            {{(COUNTER_BITS - 1){1'b0}}, 1'b1};

    localparam logic [COUNTER_BITS - 1:0]
        REQUEST_LANE_LIMIT =
            REQUEST_LANES;

    logic [COUNTER_BITS - 1:0]
        scheduler_count_sum;

    assign scheduler_count_sum =
        scheduler_count_free_q
        + scheduler_count_balance_q
        + scheduler_count_commit_q
        + scheduler_count_excite_q
        + scheduler_count_neutralize_q;

    // ----------------------------------------------------------------------
    // Static inherited capacity profiles
    // ----------------------------------------------------------------------

    initial begin
        if (
            (CELLS == 8)
            && (REQUEST_LANES != 2)
        ) begin
            $fatal(
                1,
                "FRP M31 assertion failed: 8 cells must expose 2 request lanes"
            );
        end

        if (
            (CELLS == 16)
            && (REQUEST_LANES != 4)
        ) begin
            $fatal(
                1,
                "FRP M31 assertion failed: 16 cells must expose 4 request lanes"
            );
        end

        if (
            (CELLS == 32)
            && (REQUEST_LANES != 8)
        ) begin
            $fatal(
                1,
                "FRP M31 assertion failed: 32 cells must expose 8 request lanes"
            );
        end
    end

    // ----------------------------------------------------------------------
    // Default assertion clock
    // ----------------------------------------------------------------------

    default clocking
        frp_m31_assertion_clock
        @(posedge clk);
    endclocking

    // ----------------------------------------------------------------------
    // Reset boundary
    // ----------------------------------------------------------------------

    assert property (
        !rst_n
        |->
        (
            (state_out == '0)
            && (pending_route_out == '0)
        )
    ) else $error(
        "FRP M31 assertion failed: reset did not establish active-neutral retained state"
    );

    assert property (
        !rst_n
        |->
        (
            (ticks_recorded_q == '0)
            && (scheduler_count_free_q == '0)
            && (scheduler_count_balance_q == '0)
            && (scheduler_count_commit_q == '0)
            && (scheduler_count_excite_q == '0)
            && (scheduler_count_neutralize_q == '0)
        )
    ) else $error(
        "FRP M31 assertion failed: reset did not clear scheduler counters"
    );

    // ----------------------------------------------------------------------
    // Per-element_index ternary and retained-route assertions
    // ----------------------------------------------------------------------

    genvar element_index;

    generate
        for (
            element_index = 0;
            element_index < CELLS;
            element_index = element_index + 1
        ) begin : g_cell_assertions

            localparam int CELL_LSB =
                element_index * STATE_BITS;

            assert property (
                disable iff (!rst_n)

                frp_is_valid_ternary(
                    state_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: state_out contains reserved ternary encoding"
            );

            assert property (
                disable iff (!rst_n)

                frp_is_valid_ternary(
                    pending_route_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: pending_route_out contains reserved encoding"
            );

            assert property (
                disable iff (!rst_n)

                !tick_enable
                |=>
                $stable(
                    state_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: retained state changed while tick_enable was low"
            );

            assert property (
                disable iff (!rst_n)

                !tick_enable
                |=>
                $stable(
                    pending_route_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: pending route changed while tick_enable was low"
            );

            assert property (
                disable iff (!rst_n)

                (
                    tick_enable
                    && !accepted_change_mask[
                        element_index
                    ]
                )
                |=>
                $stable(
                    state_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: state changed without accepted_change_mask"
            );

            assert property (
                disable iff (!rst_n)

                tick_enable
                |=>
                !frp_is_opposite_polarity(
                    $past(
                        state_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    ),
                    state_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: direct opposite-polarity retained-state transition"
            );

            assert property (
                disable iff (!rst_n)

                (
                    tick_enable
                    && neutral_routed_cell_mask[
                        element_index
                    ]
                    && accepted_change_mask[
                        element_index
                    ]
                )
                |=>
                (
                    frp_is_zero(
                        state_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && frp_is_nonzero(
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && frp_is_opposite_polarity(
                        $past(
                            state_out[
                                CELL_LSB +: STATE_BITS
                            ]
                        ),
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                )
            ) else $error(
                "FRP M31 assertion failed: opposite-polarity request did not route through active neutral with retained pending polarity"
            );

            assert property (
                disable iff (!rst_n)

                (
                    tick_enable
                    && frp_is_nonzero(
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && !accepted_change_mask[
                        element_index
                    ]
                )
                |=>
                $stable(
                    pending_route_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: deferred pending route was cleared or overwritten"
            );

            assert property (
                disable iff (!rst_n)

                (
                    tick_enable
                    && frp_is_zero(
                        state_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && frp_is_nonzero(
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && accepted_change_mask[
                        element_index
                    ]
                    && !neutral_routed_cell_mask[
                        element_index
                    ]
                )
                |=>
                (
                    state_out[
                        CELL_LSB +: STATE_BITS
                    ]
                    ==
                    $past(
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                )
                &&
                frp_is_zero(
                    pending_route_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: pending completion did not execute 0 to retained target"
            );

            assert property (
                disable iff (!rst_n)

                (
                    tick_enable
                    && frp_is_nonzero(
                        state_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                    && frp_is_nonzero(
                        pending_route_out[
                            CELL_LSB +: STATE_BITS
                        ]
                    )
                )
                |=>
                $stable(
                    pending_route_out[
                        CELL_LSB +: STATE_BITS
                    ]
                )
            ) else $error(
                "FRP M31 assertion failed: pending route completed from nonzero retained state"
            );

        end
    endgenerate

          // ----------------------------------------------------------------------
    // Scheduler assertions
    // ----------------------------------------------------------------------

    assert property (
        disable iff (!rst_n)

        frp_is_valid_scheduler_mode(
            scheduler_mode_q
        )
    ) else $error(
        "FRP M31 assertion failed: invalid scheduler mode"
    );

    assert property (
        disable iff (!rst_n)

        frp_scheduler_state_is_valid(
            scheduler_state_q
        )
    ) else $error(
        "FRP M31 assertion failed: invalid scheduler state"
    );

    assert property (
        disable iff (!rst_n)

        scheduler_count_sum
        ==
        ticks_recorded_q
    ) else $error(
        "FRP M31 assertion failed: scheduler counters do not sum to ticks_recorded"
    );

    assert property (
        disable iff (!rst_n)

        (
            scheduler_mode_q
            == FRP_MODE_FREE
        )
        |->
        (
            scheduler_state_q
            == FRP_SCHED_FREE
        )
    ) else $error(
        "FRP M31 assertion failed: free mode emitted non-free scheduler state"
    );

    assert property (
        disable iff (!rst_n)

        (
            scheduler_mode_q
            == FRP_MODE_7_1
        )
        |->
        (
            (
                scheduler_state_q
                == FRP_SCHED_BALANCE
            )
            ||
            (
                scheduler_state_q
                == FRP_SCHED_COMMIT
            )
        )
    ) else $error(
        "FRP M31 assertion failed: 7/1 mode emitted invalid scheduler state"
    );

    assert property (
        disable iff (!rst_n)

        (
            scheduler_mode_q
            == FRP_MODE_1_7
        )
        |->
        (
            (
                scheduler_state_q
                == FRP_SCHED_EXCITE
            )
            ||
            (
                scheduler_state_q
                == FRP_SCHED_NEUTRALIZE
            )
        )
    ) else $error(
        "FRP M31 assertion failed: 1/7 mode emitted invalid scheduler state"
    );

    assert property (
        disable iff (!rst_n)

        (
            !tick_enable
            && !clear_counters
        )
        |=>
        (
            $stable(ticks_recorded_q)
            && $stable(scheduler_count_free_q)
            && $stable(scheduler_count_balance_q)
            && $stable(scheduler_count_commit_q)
            && $stable(scheduler_count_excite_q)
            && $stable(scheduler_count_neutralize_q)
        )
    ) else $error(
        "FRP M31 assertion failed: scheduler counters changed without tick or clear"
    );

    assert property (
        disable iff (!rst_n)

        (
            clear_counters
            && !tick_enable
        )
        |=>
        (
            (ticks_recorded_q == '0)
            && (scheduler_count_free_q == '0)
            && (scheduler_count_balance_q == '0)
            && (scheduler_count_commit_q == '0)
            && (scheduler_count_excite_q == '0)
            && (scheduler_count_neutralize_q == '0)
        )
    ) else $error(
        "FRP M31 assertion failed: clear_counters did not clear the scheduler counter bank"
    );

    assert property (
        disable iff (!rst_n)

        (
            clear_counters
            && tick_enable
        )
        |=>
        (
            (
                ticks_recorded_q
                == COUNTER_ONE
            )
            &&
            (
                scheduler_count_sum
                == COUNTER_ONE
            )
        )
    ) else $error(
        "FRP M31 assertion failed: clear-plus-tick did not record exactly one scheduler event"
    );

    // ----------------------------------------------------------------------
    // Request-lane and capacity assertions
    // ----------------------------------------------------------------------

    assert property (
        disable iff (!rst_n)

        (
            request_accept
            & request_reject
        )
        == '0
    ) else $error(
        "FRP M31 assertion failed: request lane accepted and rejected simultaneously"
    );

    assert property (
        disable iff (!rst_n)

        !tick_enable
        |->
        (
            (request_accept == '0)
            && (accepted_cell_mask == '0)
            && (accepted_change_mask == '0)
            && (accepted_changes == '0)
        )
    ) else $error(
        "FRP M31 assertion failed: execution was accepted while tick_enable was low"
    );

    assert property (
        disable iff (!rst_n)

        $countones(
            accepted_cell_mask
        )
        <= REQUEST_LANES
    ) else $error(
        "FRP M31 assertion failed: accepted_cell_mask exceeds request-lane boundary"
    );

    assert property (
        disable iff (!rst_n)

        $countones(
            accepted_change_mask
        )
        ==
        accepted_changes
    ) else $error(
        "FRP M31 assertion failed: accepted_change_mask does not match accepted_changes"
    );

    assert property (
        disable iff (!rst_n)

        (
            neutral_routed_cell_mask
            & ~accepted_cell_mask
        )
        == '0
    ) else $error(
        "FRP M31 assertion failed: neutral route exists outside accepted-element_index mask"
    );

    assert property (
        disable iff (!rst_n)

        (
            neutral_routed_cell_mask
            & ~accepted_change_mask
        )
        == '0
    ) else $error(
        "FRP M31 assertion failed: neutral route exists without an accepted state change"
    );

    assert property (
        disable iff (!rst_n)

        accepted_changes
        <= REQUEST_LANE_LIMIT
    ) else $error(
        "FRP M31 assertion failed: accepted_changes exceeds REQUEST_LANES"
    );

    assert property (
        disable iff (!rst_n)

        capacity_remaining
        ==
        (
            REQUEST_LANE_LIMIT
            - accepted_changes
        )
    ) else $error(
        "FRP M31 assertion failed: capacity_remaining relation mismatch"
    );

    assert property (
        disable iff (!rst_n)

        capacity_exhausted
        ==
        (
            accepted_changes
            == REQUEST_LANE_LIMIT
        )
    ) else $error(
        "FRP M31 assertion failed: capacity_exhausted relation mismatch"
    );

    assert property (
        disable iff (!rst_n)

        switch_load_numerator
        ==
        accepted_changes
    ) else $error(
        "FRP M31 assertion failed: switch_load_numerator must equal accepted_changes"
    );

    // ----------------------------------------------------------------------
    // Event and global zero-event assertions
    // ----------------------------------------------------------------------

    assert property (
        disable iff (!rst_n)

        actual_direct_events
        == '0
    ) else $error(
        "FRP M31 assertion failed: actual_direct_events must remain zero"
    );

    assert property (
        disable iff (!rst_n)

        reserved_state_events
        == '0
    ) else $error(
        "FRP M31 assertion failed: reserved_state_events must remain zero"
    );

    assert property (
        disable iff (!rst_n)

        queue_overflow_events
        == '0
    ) else $error(
        "FRP M31 assertion failed: queue_overflow_events must remain zero"
    );

    assert property (
        disable iff (!rst_n)

        prevented_direct_events
        >= requested_direct_events
    ) else $error(
        "FRP M31 assertion failed: requested direct event was not prevented"
    );

    assert property (
        disable iff (!rst_n)

        neutral_routed_events
        >= prevented_direct_events
    ) else $error(
        "FRP M31 assertion failed: prevented direct event was not neutral-routed"
    );

           // ----------------------------------------------------------------------
    // Integrated invariant-flag assertions
    // ----------------------------------------------------------------------

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_STATE_DOMAIN_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: state-domain invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_SCHEDULER_COUNTS_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: scheduler-count invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_REQUEST_LANE_ORDER_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: request-lane invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_PENDING_POLARITY_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: pending-polarity invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_ACTIVE_NEUTRAL_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: active-neutral invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_TRANSITION_CAPACITY_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: transition-capacity invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_STATE_UPDATE_VALID
        ]
    ) else $error(
        "FRP M31 assertion failed: state-update invariant flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_NO_ACTUAL_DIRECT_EVENTS
        ]
    ) else $error(
        "FRP M31 assertion failed: no-actual-direct-events flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_NO_RESERVED_STATE
        ]
    ) else $error(
        "FRP M31 assertion failed: no-reserved-state flag is false"
    );

    assert property (
        disable iff (!rst_n)

        invariant_flags[
            FRP_INV_NO_QUEUE_OVERFLOW
        ]
    ) else $error(
        "FRP M31 assertion failed: no-queue-overflow flag is false"
    );

    // ----------------------------------------------------------------------
    // Qualification coverage
    // ----------------------------------------------------------------------

    cover property (
        scheduler_mode_q
        == FRP_MODE_FREE
    );

    cover property (
        scheduler_mode_q
        == FRP_MODE_7_1
    );

    cover property (
        scheduler_mode_q
        == FRP_MODE_1_7
    );

    cover property (
        neutral_routed_cell_mask
        != '0
    );

    cover property (
        (
            accepted_change_mask
            != '0
        )
        &&
        (
            pending_route_out
            != '0
        )
    );

    cover property (
        capacity_exhausted
    );

endmodule : frp_m31_assertions

`endif 
