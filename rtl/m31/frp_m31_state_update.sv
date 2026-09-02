// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 Retained State Update Module
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
// Writeback contract:
//   - reset initializes retained state to active neutral 0;
//   - disabled ticks retain the complete state bank;
//   - state-changing writeback requires a qualified candidate and capacity;
//   - same-state retention consumes no capacity;
//   - opposite polarity commits only the legal first leg +/-1 -> 0;
//   - pending completion commits only on a later eligible tick from 0;
//   - capacity rejection defers without state or pending-route corruption;
//   - reserved encoding and direct -1 <-> 1 writeback are never committed.

`ifndef FRP_M31_STATE_UPDATE_SV
`define FRP_M31_STATE_UPDATE_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m31_state_update #(
  parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
  parameter int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,
  input logic [(CELLS*STATE_BITS)-1:0] state_candidate_d,
  input logic [CELLS-1:0] capacity_accept_mask,
  input logic [CELLS-1:0] accepted_change_candidate_mask,
  input logic [CELLS-1:0] neutral_routed_mask,
  input logic [CELLS-1:0] pending_completion_mask,
  input logic [CELLS-1:0] reserved_transition_mask,
  input logic [CELLS-1:0] actual_direct_mask,
  output logic [(CELLS*STATE_BITS)-1:0] state_q,
  output logic [(CELLS*STATE_BITS)-1:0] state_d,
  output logic [(CELLS*STATE_BITS)-1:0] state_out,
  output logic [CELLS-1:0] state_write_enable_mask,
  output logic [CELLS-1:0] state_hold_mask,
  output logic [CELLS-1:0] state_reset_mask,
  output logic [CELLS-1:0] state_reserved_mask,
  output logic [COUNTER_BITS-1:0] accepted_changes,
  output logic [COUNTER_BITS-1:0] switch_load_numerator,
  output logic [COUNTER_BITS-1:0] state_write_events,
  output logic [COUNTER_BITS-1:0] state_hold_events,
  output logic [COUNTER_BITS-1:0] state_reset_events,
  output logic [COUNTER_BITS-1:0] accepted_change_events,
  output logic [COUNTER_BITS-1:0] neutral_routed_commit_events,
  output logic [COUNTER_BITS-1:0] pending_completion_commit_events,
  output logic [COUNTER_BITS-1:0] reserved_state_events,
  output logic [COUNTER_BITS-1:0] actual_direct_events,
  output logic state_domain_valid,
  output logic state_output_domain_valid,
  output logic state_update_valid,
  output logic state_write_capacity_valid,
  output logic same_state_hold_valid,
  output logic active_neutral_writeback_valid,
  output logic pending_completion_writeback_valid,
  output logic no_reserved_state_output,
  output logic no_actual_direct_events
);

  import frp_m31_pkg::*;

  localparam logic [COUNTER_BITS-1:0] COUNTER_ONE =
    {{(COUNTER_BITS-1){1'b0}}, 1'b1};

  localparam logic [COUNTER_BITS-1:0] REQUEST_LANE_LIMIT =
    REQUEST_LANES[COUNTER_BITS-1:0];

  logic [(CELLS*STATE_BITS)-1:0] state_next;
  logic writeback_contract_valid;

  logic [CELLS-1:0] current_valid_w;
  logic [CELLS-1:0] candidate_valid_w;
  logic [CELLS-1:0] state_changes_w;
  logic [CELLS-1:0] direct_candidate_w;
  logic [CELLS-1:0] scheduler_legal_w;
  logic [CELLS-1:0] metadata_legal_w;
  logic [CELLS-1:0] commit_allowed_w;
  logic [CELLS-1:0] final_state_valid_w;
  logic [CELLS-1:0] final_state_changed_w;
  logic [CELLS-1:0] final_direct_w;

  function automatic logic [STATE_BITS-1:0] packed_state_value(
    input logic [(CELLS*STATE_BITS)-1:0] packed_state,
    input int element_index
  );
    packed_state_value =
      packed_state[(element_index*STATE_BITS) +: STATE_BITS];
  endfunction

  always_comb begin
    state_next = state_q;

    state_write_enable_mask = '0;
    state_hold_mask = '0;
    state_reset_mask = '0;
    state_reserved_mask = '0;

    accepted_changes = '0;
    switch_load_numerator = '0;
    state_write_events = '0;
    state_hold_events = '0;
    state_reset_events = '0;
    accepted_change_events = '0;
    neutral_routed_commit_events = '0;
    pending_completion_commit_events = '0;
    reserved_state_events = '0;
    actual_direct_events = '0;

    state_domain_valid = 1'b1;
    state_output_domain_valid = 1'b1;
    state_update_valid = 1'b1;
    state_write_capacity_valid = 1'b1;
    same_state_hold_valid = 1'b1;
    active_neutral_writeback_valid = 1'b1;
    pending_completion_writeback_valid = 1'b1;
    no_reserved_state_output = 1'b1;
    no_actual_direct_events = 1'b1;
    writeback_contract_valid = 1'b1;

    current_valid_w = '0;
    candidate_valid_w = '0;
    state_changes_w = '0;
    direct_candidate_w = '0;
    scheduler_legal_w = '1;
    metadata_legal_w = '1;
    commit_allowed_w = '0;
    final_state_valid_w = '0;
    final_state_changed_w = '0;
    final_direct_w = '0;

    for (
      int element_index = 0;
      element_index < CELLS;
      element_index++
    ) begin
      current_valid_w[element_index] =
        frp_is_valid_ternary(
          packed_state_value(
            state_q,
            element_index
          )
        );

      candidate_valid_w[element_index] =
        frp_is_valid_ternary(
          packed_state_value(
            state_candidate_d,
            element_index
          )
        );

      state_changes_w[element_index] =
        packed_state_value(
          state_q,
          element_index
        )
        !=
        packed_state_value(
          state_candidate_d,
          element_index
        );

      direct_candidate_w[element_index] =
        actual_direct_mask[element_index]
        || (
          current_valid_w[element_index]
          && candidate_valid_w[element_index]
          && frp_is_opposite_polarity(
            packed_state_value(
              state_q,
              element_index
            ),
            packed_state_value(
              state_candidate_d,
              element_index
            )
          )
        );
    end

    if (!rst_n) begin
      state_next = '0;
      state_reset_mask = '1;

      for (
        int element_index = 0;
        element_index < CELLS;
        element_index++
      ) begin
        state_reset_events =
          state_reset_events + COUNTER_ONE;
      end
    end else begin
      for (
        int element_index = 0;
        element_index < CELLS;
        element_index++
      ) begin
        if (
          !current_valid_w[element_index]
          || !candidate_valid_w[element_index]
          || reserved_transition_mask[element_index]
        ) begin
          state_reserved_mask[element_index] = 1'b1;

          reserved_state_events =
            reserved_state_events + COUNTER_ONE;

          state_domain_valid = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        if (direct_candidate_w[element_index]) begin
          metadata_legal_w[element_index] = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        if (
          neutral_routed_mask[element_index]
          && pending_completion_mask[element_index]
        ) begin
          active_neutral_writeback_valid = 1'b0;
          pending_completion_writeback_valid = 1'b0;
          metadata_legal_w[element_index] = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        if (
          accepted_change_candidate_mask[element_index]
          && !state_changes_w[element_index]
        ) begin
          same_state_hold_valid = 1'b0;
          metadata_legal_w[element_index] = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        if (state_changes_w[element_index]) begin
          if (
            !accepted_change_candidate_mask[
              element_index
            ]
          ) begin
            state_write_capacity_valid = 1'b0;
            metadata_legal_w[element_index] = 1'b0;
            writeback_contract_valid = 1'b0;
          end

          if (neutral_routed_mask[element_index]) begin
            scheduler_legal_w[element_index] =
              frp_scheduler_state_is_valid(
                scheduler_state
              )
              &&
              frp_scheduler_is_neutralize_capable(
                scheduler_state
              );

            if (
              !frp_is_nonzero(
                packed_state_value(
                  state_q,
                  element_index
                )
              )
              ||
              !frp_is_zero(
                packed_state_value(
                  state_candidate_d,
                  element_index
                )
              )
            ) begin
              active_neutral_writeback_valid = 1'b0;
              metadata_legal_w[element_index] = 1'b0;
              writeback_contract_valid = 1'b0;
            end
          end else if (
            pending_completion_mask[
              element_index
            ]
          ) begin
            scheduler_legal_w[element_index] =
              frp_scheduler_state_is_valid(
                scheduler_state
              )
              &&
              frp_scheduler_is_commit_capable(
                scheduler_state
              );

            if (
              !frp_is_zero(
                packed_state_value(
                  state_q,
                  element_index
                )
              )
              ||
              !frp_is_nonzero(
                packed_state_value(
                  state_candidate_d,
                  element_index
                )
              )
            ) begin
              pending_completion_writeback_valid =
                1'b0;

              metadata_legal_w[element_index] =
                1'b0;

              writeback_contract_valid = 1'b0;
            end
          end else if (
            frp_is_zero(
              packed_state_value(
                state_q,
                element_index
              )
            )
            &&
            frp_is_nonzero(
              packed_state_value(
                state_candidate_d,
                element_index
              )
            )
          ) begin
            scheduler_legal_w[element_index] =
              frp_scheduler_state_is_valid(
                scheduler_state
              )
              &&
              frp_scheduler_is_commit_capable(
                scheduler_state
              );
          end else if (
            frp_is_nonzero(
              packed_state_value(
                state_q,
                element_index
              )
            )
            &&
            frp_is_zero(
              packed_state_value(
                state_candidate_d,
                element_index
              )
            )
          ) begin
            scheduler_legal_w[element_index] =
              frp_scheduler_state_is_valid(
                scheduler_state
              )
              &&
              frp_scheduler_is_neutralize_capable(
                scheduler_state
              );
          end else begin
            scheduler_legal_w[element_index] =
              1'b0;
          end
        end

        if (!scheduler_legal_w[element_index]) begin
          if (neutral_routed_mask[element_index]) begin
            active_neutral_writeback_valid =
              1'b0;
          end

          if (
            pending_completion_mask[
              element_index
            ]
          ) begin
            pending_completion_writeback_valid =
              1'b0;
          end

          metadata_legal_w[element_index] = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        commit_allowed_w[element_index] =
          tick_enable
          && current_valid_w[element_index]
          && candidate_valid_w[element_index]
          && state_changes_w[element_index]
          && capacity_accept_mask[element_index]
          && accepted_change_candidate_mask[
            element_index
          ]
          && !reserved_transition_mask[
            element_index
          ]
          && !direct_candidate_w[element_index]
          && scheduler_legal_w[element_index]
          && metadata_legal_w[element_index];

        if (commit_allowed_w[element_index]) begin
          state_next[
            (element_index*STATE_BITS)
            +: STATE_BITS
          ] =
            packed_state_value(
              state_candidate_d,
              element_index
            );
        end
      end

            for (
        int element_index = 0;
        element_index < CELLS;
        element_index++
      ) begin
        final_state_valid_w[element_index] =
          frp_is_valid_ternary(
            packed_state_value(
              state_next,
              element_index
            )
          );

        final_state_changed_w[element_index] =
          packed_state_value(
            state_q,
            element_index
          )
          !=
          packed_state_value(
            state_next,
            element_index
          );

        final_direct_w[element_index] =
          current_valid_w[element_index]
          && final_state_valid_w[element_index]
          && frp_is_opposite_polarity(
            packed_state_value(
              state_q,
              element_index
            ),
            packed_state_value(
              state_next,
              element_index
            )
          );

        if (!final_state_valid_w[element_index]) begin
          state_reserved_mask[element_index] =
            1'b1;

          state_output_domain_valid = 1'b0;
          no_reserved_state_output = 1'b0;
        end

        if (final_direct_w[element_index]) begin
          actual_direct_events =
            actual_direct_events + COUNTER_ONE;

          no_actual_direct_events = 1'b0;
          writeback_contract_valid = 1'b0;
        end

        if (
          final_state_changed_w[
            element_index
          ]
        ) begin
          state_write_enable_mask[
            element_index
          ] = 1'b1;

          accepted_changes =
            accepted_changes + COUNTER_ONE;

          state_write_events =
            state_write_events + COUNTER_ONE;

          accepted_change_events =
            accepted_change_events + COUNTER_ONE;

          if (
            !capacity_accept_mask[element_index]
            ||
            !accepted_change_candidate_mask[
              element_index
            ]
          ) begin
            state_write_capacity_valid = 1'b0;
          end

          if (
            neutral_routed_mask[
              element_index
            ]
          ) begin
            if (
              frp_is_nonzero(
                packed_state_value(
                  state_q,
                  element_index
                )
              )
              &&
              frp_is_zero(
                packed_state_value(
                  state_next,
                  element_index
                )
              )
              &&
              frp_scheduler_is_neutralize_capable(
                scheduler_state
              )
            ) begin
              neutral_routed_commit_events =
                neutral_routed_commit_events
                + COUNTER_ONE;
            end else begin
              active_neutral_writeback_valid =
                1'b0;
            end
          end

          if (
            pending_completion_mask[
              element_index
            ]
          ) begin
            if (
              frp_is_zero(
                packed_state_value(
                  state_q,
                  element_index
                )
              )
              &&
              frp_is_nonzero(
                packed_state_value(
                  state_next,
                  element_index
                )
              )
              &&
              frp_scheduler_is_commit_capable(
                scheduler_state
              )
            ) begin
              pending_completion_commit_events =
                pending_completion_commit_events
                + COUNTER_ONE;
            end else begin
              pending_completion_writeback_valid =
                1'b0;
            end
          end
        end else begin
          state_hold_mask[element_index] = 1'b1;

          state_hold_events =
            state_hold_events + COUNTER_ONE;
        end
      end
    end

    switch_load_numerator =
      accepted_changes;

    state_write_capacity_valid =
      state_write_capacity_valid
      && (
        accepted_changes
        <= REQUEST_LANE_LIMIT
      )
      && (
        (
          state_write_enable_mask
          & ~capacity_accept_mask
        )
        == '0
      )
      && (
        (
          state_write_enable_mask
          & ~accepted_change_candidate_mask
        )
        == '0
      );

    same_state_hold_valid =
      same_state_hold_valid
      && (
        (
          state_write_enable_mask
          & state_hold_mask
        )
        == '0
      )
      && (
        (
          state_write_enable_mask
          | state_hold_mask
          | state_reset_mask
        )
        == {CELLS{1'b1}}
      );

    state_domain_valid =
      state_domain_valid
      && state_output_domain_valid
      && no_reserved_state_output;

    state_update_valid =
      writeback_contract_valid
      && frp_scheduler_state_is_valid(
        scheduler_state
      )
      && state_domain_valid
      && state_write_capacity_valid
      && same_state_hold_valid
      && active_neutral_writeback_valid
      && pending_completion_writeback_valid
      && no_reserved_state_output
      && no_actual_direct_events;
  end

  assign state_d =
    state_next;

  assign state_out =
    state_q;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      state_q <= '0;
    end else if (tick_enable) begin
      state_q <= state_d;
    end
  end

endmodule : frp_m31_state_update

`endif
