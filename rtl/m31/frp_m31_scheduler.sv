// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Scheduler State RTL Realization
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
//   Realizes the explicit FRP temporal execution modes and presents the
//   scheduler state used by the complete M31 execution chain:
//
//     scheduler
//       -> request-lane arbitration
//       -> pending-route processing
//       -> active-neutral transition generation
//       -> transition-capacity guard
//       -> retained-state writeback
//
// Preserved execution profiles:
//   - free: every enabled tick is free and commit-capable;
//   - 7/1: seven balance ticks followed by one commit tick;
//   - 1/7: one excite tick followed by seven neutralize ticks.
//
// Preserved scheduler invariants:
//   - tick index advances only on tick_enable;
//   - period_index_q = tick_index_q mod 8;
//   - scheduler counters count the state actually presented for the tick;
//   - counter clear does not reset tick index, scheduler mode, scheduler
//     state progression, retained ternary state, or pending-route state;
//   - a mode change is registered at a clock boundary and never changes
//     retained ternary state directly;
//   - exactly one scheduler enable is active on each valid enabled tick;
//   - scheduler counts sum to ticks_recorded_q.

`ifndef FRP_M31_SCHEDULER_SV
`define FRP_M31_SCHEDULER_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_scheduler #(
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,

  input logic tick_enable,
  input logic clear_counters,

  input frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode,

  output frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode_q,
  output frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state_q,

  output logic [COUNTER_BITS-1:0] tick_index_q,
  output logic [2:0] period_index_q,

  output logic [COUNTER_BITS-1:0] ticks_recorded_q,

  output logic [COUNTER_BITS-1:0] scheduler_count_free_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_balance_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_commit_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_excite_q,
  output logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q,

  output logic free_enable,
  output logic balance_enable,
  output logic commit_enable,
  output logic excite_enable,
  output logic neutralize_enable,

  output logic scheduler_mode_reserved,
  output logic scheduler_state_reserved,
  output logic scheduler_valid,
  output logic scheduler_counts_valid
);

  import frp_m31_pkg::*;

  localparam logic [COUNTER_BITS-1:0] COUNTER_ONE =
    {{(COUNTER_BITS-1){1'b0}}, 1'b1};

  frp_m31_scheduler_mode_e scheduler_mode_d;
  frp_m31_scheduler_state_e scheduler_state_d;

  logic [COUNTER_BITS-1:0] tick_index_d;
  logic [2:0] period_index_d;

  logic [COUNTER_BITS-1:0] ticks_recorded_d;

  logic [COUNTER_BITS-1:0] scheduler_count_free_d;
  logic [COUNTER_BITS-1:0] scheduler_count_balance_d;
  logic [COUNTER_BITS-1:0] scheduler_count_commit_d;
  logic [COUNTER_BITS-1:0] scheduler_count_excite_d;
  logic [COUNTER_BITS-1:0] scheduler_count_neutralize_d;

  logic [COUNTER_BITS-1:0] scheduler_count_sum;
  logic [4:0] scheduler_enable_vector;

  // --------------------------------------------------------------------------
  // Complete scheduler next-state relation
  // --------------------------------------------------------------------------

  always_comb begin
    scheduler_mode_d = scheduler_mode_q;
    scheduler_state_d = scheduler_state_q;

    tick_index_d = tick_index_q;
    period_index_d = period_index_q;

    ticks_recorded_d = ticks_recorded_q;

    scheduler_count_free_d = scheduler_count_free_q;
    scheduler_count_balance_d = scheduler_count_balance_q;
    scheduler_count_commit_d = scheduler_count_commit_q;
    scheduler_count_excite_d = scheduler_count_excite_q;
    scheduler_count_neutralize_d = scheduler_count_neutralize_q;

    // The selected mode is registered at the clock boundary.
    // Reconfiguration does not consume a processor tick and does not modify
    // retained balanced ternary state or retained pending-route state.

    if (frp_is_valid_scheduler_mode(scheduler_mode)) begin
      scheduler_mode_d = scheduler_mode;
    end else begin
      scheduler_mode_d = FRP_MODE_RESERVED;
    end

    // Counter clear applies only to the scheduler event-counter bank.
    //
    // It does not reset:
    //   - tick_index_q;
    //   - period_index_q;
    //   - scheduler mode;
    //   - scheduler-state progression;
    //   - retained balanced ternary state;
    //   - pending-route state.

    if (clear_counters) begin
      ticks_recorded_d = '0;

      scheduler_count_free_d = '0;
      scheduler_count_balance_d = '0;
      scheduler_count_commit_d = '0;
      scheduler_count_excite_d = '0;
      scheduler_count_neutralize_d = '0;
    end

    // scheduler_state_q is the scheduler state presented to the complete
    // downstream M31 execution chain for the currently enabled tick.
    //
    // The same state is therefore used for:
    //   - request-lane scheduler eligibility;
    //   - pending-route completion eligibility;
    //   - active-neutral transition eligibility;
    //   - transition-capacity accounting;
    //   - retained-state writeback eligibility;
    //   - scheduler-state event counting.

    if (tick_enable) begin
      tick_index_d =
        tick_index_q + COUNTER_ONE;

      ticks_recorded_d =
        ticks_recorded_d + COUNTER_ONE;

      unique case (scheduler_state_q)
        FRP_SCHED_FREE: begin
          scheduler_count_free_d =
            scheduler_count_free_d + COUNTER_ONE;
        end

        FRP_SCHED_BALANCE: begin
          scheduler_count_balance_d =
            scheduler_count_balance_d + COUNTER_ONE;
        end

        FRP_SCHED_COMMIT: begin
          scheduler_count_commit_d =
            scheduler_count_commit_d + COUNTER_ONE;
        end

        FRP_SCHED_EXCITE: begin
          scheduler_count_excite_d =
            scheduler_count_excite_d + COUNTER_ONE;
        end

        FRP_SCHED_NEUTRALIZE: begin
          scheduler_count_neutralize_d =
            scheduler_count_neutralize_d + COUNTER_ONE;
        end

        default: begin
          // No legal scheduler-state counter is incremented for an invalid
          // scheduler state. scheduler_counts_valid then exposes the invalid
          // execution rather than concealing it.
        end
      endcase
    end

    // Exact modulo-8 scheduler relation inherited from M15:
    //
    //   period_index_q = tick_index_q mod 8
    //
    // scheduler_state_d is predecoded for the resulting current/next tick
    // index, preserving the qualified state sequence.

    period_index_d =
      tick_index_d[2:0];

    scheduler_state_d =
      frp_decode_scheduler_state(
        scheduler_mode_d,
        period_index_d
      );
  end

  // --------------------------------------------------------------------------
  // Sequential scheduler registers
  // --------------------------------------------------------------------------

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      scheduler_mode_q <= FRP_MODE_FREE;
      scheduler_state_q <= FRP_SCHED_FREE;

      tick_index_q <= '0;
      period_index_q <= 3'd0;

      ticks_recorded_q <= '0;

      scheduler_count_free_q <= '0;
      scheduler_count_balance_q <= '0;
      scheduler_count_commit_q <= '0;
      scheduler_count_excite_q <= '0;
      scheduler_count_neutralize_q <= '0;
    end else begin
      scheduler_mode_q <= scheduler_mode_d;
      scheduler_state_q <= scheduler_state_d;

      tick_index_q <= tick_index_d;
      period_index_q <= period_index_d;

      ticks_recorded_q <= ticks_recorded_d;

      scheduler_count_free_q <= scheduler_count_free_d;
      scheduler_count_balance_q <= scheduler_count_balance_d;
      scheduler_count_commit_q <= scheduler_count_commit_d;
      scheduler_count_excite_q <= scheduler_count_excite_d;
      scheduler_count_neutralize_q <=
        scheduler_count_neutralize_d;
    end
  end

  // --------------------------------------------------------------------------
  // Scheduler-state execution enables
  // --------------------------------------------------------------------------

  always_comb begin
    free_enable = 1'b0;
    balance_enable = 1'b0;
    commit_enable = 1'b0;
    excite_enable = 1'b0;
    neutralize_enable = 1'b0;

    if (tick_enable) begin
      unique case (scheduler_state_q)
        FRP_SCHED_FREE: begin
          free_enable = 1'b1;
        end

        FRP_SCHED_BALANCE: begin
          balance_enable = 1'b1;
        end

        FRP_SCHED_COMMIT: begin
          commit_enable = 1'b1;
        end

        FRP_SCHED_EXCITE: begin
          excite_enable = 1'b1;
        end

        FRP_SCHED_NEUTRALIZE: begin
          neutralize_enable = 1'b1;
        end

        default: begin
          free_enable = 1'b0;
          balance_enable = 1'b0;
          commit_enable = 1'b0;
          excite_enable = 1'b0;
          neutralize_enable = 1'b0;
        end
      endcase
    end
  end

  assign scheduler_enable_vector = {
    neutralize_enable,
    excite_enable,
    commit_enable,
    balance_enable,
    free_enable
  };

  // --------------------------------------------------------------------------
  // Scheduler validity and counter relations
  // --------------------------------------------------------------------------

  always_comb begin
    scheduler_mode_reserved =
      !frp_is_valid_scheduler_mode(
        scheduler_mode_q
      );

    scheduler_state_reserved =
      !frp_scheduler_state_is_valid(
        scheduler_state_q
      );

    scheduler_valid =
      !scheduler_mode_reserved
      && !scheduler_state_reserved
      && (
        period_index_q
        == tick_index_q[2:0]
      )
      && (
        !tick_enable
        || (
          $countones(
            scheduler_enable_vector
          )
          == 1
        )
      );

    scheduler_count_sum =
      scheduler_count_free_q
      + scheduler_count_balance_q
      + scheduler_count_commit_q
      + scheduler_count_excite_q
      + scheduler_count_neutralize_q;

    scheduler_counts_valid =
      (
        scheduler_count_sum
        == ticks_recorded_q
      );
  end

endmodule : frp_m31_scheduler

`endif
