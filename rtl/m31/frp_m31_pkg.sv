// SPDX-License-Identifier: Apache-2.0
//
// FRP M31 RTL Core Realization Package
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
//   Defines the canonical shared semantic domain for the complete M31 RTL
//   execution chain:
//
//     scheduler
//       -> request-lane arbitration
//       -> pending-route processing
//       -> active-neutral transition generation
//       -> transition-capacity guarding
//       -> retained-state writeback
//
// Architecture preserved:
//   - balanced ternary retained-state domain {-1, 0, 1};
//   - active neutral state 0 as a computational state;
//   - mandatory tick-separated routing -1 -> 0 -> 1 and 1 -> 0 -> -1;
//   - retained pending-route target polarity;
//   - free / 7/1 / 1/7 temporal execution modes;
//   - deterministic ascending request-lane order;
//   - transition_fraction = 0.25 capacity boundary;
//   - zero direct opposite-polarity execution;
//   - zero reserved-state emission;
//   - zero pending-route queue overflow.

`ifndef FRP_M31_PKG_SV
`define FRP_M31_PKG_SV

package frp_m31_pkg;

  // --------------------------------------------------------------------------
  // Canonical M31 widths and execution constants
  // --------------------------------------------------------------------------

  localparam int FRP_M31_STATE_BITS             = 2;
  localparam int FRP_M31_SCHED_MODE_BITS        = 2;
  localparam int FRP_M31_SCHED_BITS             = 3;
  localparam int FRP_M31_PERIOD_BITS            = 3;
  localparam int FRP_M31_PERIOD_TICKS           = 8;
  localparam int FRP_M31_TRANSITION_CLASS_BITS  = 4;
  localparam int FRP_M31_REJECT_REASON_BITS     = 4;
  localparam int FRP_M31_COUNTER_BITS           = 32;
  localparam int FRP_M31_DEFAULT_CELLS          = 8;

  // M15-qualified transition boundary:
  //
  //   transition_fraction = 0.25
  //   REQUEST_LANES = max(1, round(CELLS * transition_fraction))
  //
  // Qualified profiles:
  //   8 cells  -> 2 request lanes
  //   16 cells -> 4 request lanes
  //   32 cells -> 8 request lanes

  localparam int FRP_M31_TRANSITION_FRACTION_NUM = 1;
  localparam int FRP_M31_TRANSITION_FRACTION_DEN = 4;

  // --------------------------------------------------------------------------
  // Canonical balanced ternary encoding
  // --------------------------------------------------------------------------

  typedef enum logic [FRP_M31_STATE_BITS-1:0] {
    FRP_TERN_ZERO     = 2'b00,
    FRP_TERN_POS      = 2'b01,
    FRP_TERN_RESERVED = 2'b10,
    FRP_TERN_NEG      = 2'b11
  } frp_m31_ternary_e;

  localparam logic [FRP_M31_STATE_BITS-1:0] FRP_STATE_ZERO =
    FRP_TERN_ZERO;

  localparam logic [FRP_M31_STATE_BITS-1:0] FRP_STATE_POS =
    FRP_TERN_POS;

  localparam logic [FRP_M31_STATE_BITS-1:0] FRP_STATE_NEG =
    FRP_TERN_NEG;

  localparam logic [FRP_M31_STATE_BITS-1:0] FRP_STATE_RESERVED =
    FRP_TERN_RESERVED;

  // The active neutral state is not an empty or unused encoding. It is the
  // required balancing, damping, transition-buffer, polarity-bridge, and
  // stabilization state of the retained ternary architecture.

  localparam logic [FRP_M31_STATE_BITS-1:0] FRP_ACTIVE_NEUTRAL =
    FRP_STATE_ZERO;

  // --------------------------------------------------------------------------
  // Scheduler mode and scheduler-state encodings
  // --------------------------------------------------------------------------

  typedef enum logic [FRP_M31_SCHED_MODE_BITS-1:0] {
    FRP_MODE_FREE     = 2'b00,
    FRP_MODE_7_1      = 2'b01,
    FRP_MODE_1_7      = 2'b10,
    FRP_MODE_RESERVED = 2'b11
  } frp_m31_scheduler_mode_e;

  typedef enum logic [FRP_M31_SCHED_BITS-1:0] {
    FRP_SCHED_FREE       = 3'b000,
    FRP_SCHED_BALANCE    = 3'b001,
    FRP_SCHED_COMMIT     = 3'b010,
    FRP_SCHED_EXCITE     = 3'b011,
    FRP_SCHED_NEUTRALIZE = 3'b100,
    FRP_SCHED_INVALID    = 3'b111
  } frp_m31_scheduler_state_e;

  // --------------------------------------------------------------------------
  // Transition and rejection encodings
  // --------------------------------------------------------------------------

  typedef enum logic [FRP_M31_TRANSITION_CLASS_BITS-1:0] {
    FRP_TRANS_SAME_STATE         = 4'd0,
    FRP_TRANS_ZERO_TO_NONZERO    = 4'd1,
    FRP_TRANS_NONZERO_TO_ZERO    = 4'd2,
    FRP_TRANS_OPPOSITE_POLARITY  = 4'd3,
    FRP_TRANS_PENDING_COMPLETION = 4'd4,
    FRP_TRANS_HOLD               = 4'd5,
    FRP_TRANS_REJECTED           = 4'd6,
    FRP_TRANS_RESERVED_OPERAND   = 4'd7,
    FRP_TRANS_INVALID            = 4'd15
  } frp_m31_transition_class_e;

  typedef enum logic [FRP_M31_REJECT_REASON_BITS-1:0] {
    FRP_REJECT_NONE           = 4'd0,
    FRP_REJECT_INVALID_CELL   = 4'd1,
    FRP_REJECT_INVALID_TARGET = 4'd2,
    FRP_REJECT_DUPLICATE_CELL = 4'd3,
    FRP_REJECT_SCHEDULER      = 4'd4,
    FRP_REJECT_CAPACITY       = 4'd5,
    FRP_REJECT_PENDING_BUSY   = 4'd6,
    FRP_REJECT_TICK_DISABLED  = 4'd7,
    FRP_REJECT_RESERVED       = 4'd15
  } frp_m31_reject_reason_e;

  // --------------------------------------------------------------------------
  // Integrated invariant flag indexes
  // --------------------------------------------------------------------------

  localparam int FRP_INV_STATE_DOMAIN_VALID         = 0;
  localparam int FRP_INV_SCHEDULER_COUNTS_VALID     = 1;
  localparam int FRP_INV_REQUEST_LANE_ORDER_VALID   = 2;
  localparam int FRP_INV_PENDING_POLARITY_VALID     = 3;
  localparam int FRP_INV_ACTIVE_NEUTRAL_VALID       = 4;
  localparam int FRP_INV_TRANSITION_CAPACITY_VALID  = 5;
  localparam int FRP_INV_STATE_UPDATE_VALID         = 6;
  localparam int FRP_INV_NO_ACTUAL_DIRECT_EVENTS    = 7;
  localparam int FRP_INV_NO_RESERVED_STATE          = 8;
  localparam int FRP_INV_NO_QUEUE_OVERFLOW          = 9;

  localparam int FRP_M31_INVARIANT_FLAGS = 10;

  // --------------------------------------------------------------------------
  // Balanced ternary domain helpers
  // --------------------------------------------------------------------------

  function automatic logic frp_is_valid_ternary(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_valid_ternary =
        (value == FRP_STATE_NEG)  ||
        (value == FRP_STATE_ZERO) ||
        (value == FRP_STATE_POS);
    end
  endfunction

  function automatic logic frp_is_reserved_ternary(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_reserved_ternary =
        (value == FRP_STATE_RESERVED);
    end
  endfunction

  function automatic logic frp_is_zero(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_zero =
        (value == FRP_STATE_ZERO);
    end
  endfunction

  function automatic logic frp_is_positive(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_positive =
        (value == FRP_STATE_POS);
    end
  endfunction

  function automatic logic frp_is_negative(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_negative =
        (value == FRP_STATE_NEG);
    end
  endfunction

  function automatic logic frp_is_nonzero(
    input logic [FRP_M31_STATE_BITS-1:0] value
  );
    begin
      frp_is_nonzero =
        (value == FRP_STATE_NEG) ||
        (value == FRP_STATE_POS);
    end
  endfunction

  function automatic logic frp_is_opposite_polarity(
    input logic [FRP_M31_STATE_BITS-1:0] left,
    input logic [FRP_M31_STATE_BITS-1:0] right
  );
    begin
      frp_is_opposite_polarity =
        (
          (left == FRP_STATE_NEG) &&
          (right == FRP_STATE_POS)
        )
        ||
        (
          (left == FRP_STATE_POS) &&
          (right == FRP_STATE_NEG)
        );
    end
  endfunction

  function automatic logic frp_is_state_change(
    input logic [FRP_M31_STATE_BITS-1:0] from_state,
    input logic [FRP_M31_STATE_BITS-1:0] to_state
  );
    begin
      frp_is_state_change =
        (from_state != to_state);
    end
  endfunction

  function automatic logic frp_is_legal_state_change(
    input logic [FRP_M31_STATE_BITS-1:0] from_state,
    input logic [FRP_M31_STATE_BITS-1:0] to_state
  );
    begin
      frp_is_legal_state_change =
        frp_is_valid_ternary(from_state)
        && frp_is_valid_ternary(to_state)
        && (from_state != to_state)
        && !frp_is_opposite_polarity(
          from_state,
          to_state
        );
    end
  endfunction

  function automatic logic frp_is_valid_pending_route(
    input logic [FRP_M31_STATE_BITS-1:0] pending_value
  );
    begin
      frp_is_valid_pending_route =
        frp_is_valid_ternary(pending_value);
    end
  endfunction

  function automatic logic frp_has_pending_route(
    input logic [FRP_M31_STATE_BITS-1:0] pending_value
  );
    begin
      frp_has_pending_route =
        frp_is_nonzero(pending_value);
    end
  endfunction

  // --------------------------------------------------------------------------
  // Transition classification and exact active-neutral next-state semantics
  // --------------------------------------------------------------------------

  function automatic frp_m31_transition_class_e frp_classify_transition(
    input logic [FRP_M31_STATE_BITS-1:0] state_value,
    input logic [FRP_M31_STATE_BITS-1:0] target_value,
    input logic [FRP_M31_STATE_BITS-1:0] pending_value
  );
    begin
      if (
        !frp_is_valid_ternary(state_value)
        || !frp_is_valid_ternary(target_value)
        || !frp_is_valid_ternary(pending_value)
      ) begin
        frp_classify_transition =
          FRP_TRANS_RESERVED_OPERAND;
      end else if (
        frp_is_zero(state_value)
        && frp_has_pending_route(pending_value)
      ) begin
        // Retained pending continuation has priority over a new same-element_index
        // target. Completion uses pending_value, never target_value.

        frp_classify_transition =
          FRP_TRANS_PENDING_COMPLETION;
      end else if (
        state_value == target_value
      ) begin
        frp_classify_transition =
          FRP_TRANS_SAME_STATE;
      end else if (
        frp_is_zero(state_value)
        && frp_is_nonzero(target_value)
      ) begin
        frp_classify_transition =
          FRP_TRANS_ZERO_TO_NONZERO;
      end else if (
        frp_is_nonzero(state_value)
        && frp_is_zero(target_value)
      ) begin
        frp_classify_transition =
          FRP_TRANS_NONZERO_TO_ZERO;
      end else if (
        frp_is_opposite_polarity(
          state_value,
          target_value
        )
      ) begin
        frp_classify_transition =
          FRP_TRANS_OPPOSITE_POLARITY;
      end else begin
        frp_classify_transition =
          FRP_TRANS_INVALID;
      end
    end
  endfunction

  function automatic logic [FRP_M31_STATE_BITS-1:0]
    frp_transition_selected_target(
      input logic [FRP_M31_STATE_BITS-1:0] state_value,
      input logic [FRP_M31_STATE_BITS-1:0] target_value,
      input logic [FRP_M31_STATE_BITS-1:0] pending_value
    );

    frp_m31_transition_class_e transition_class;

    begin
      transition_class =
        frp_classify_transition(
          state_value,
          target_value,
          pending_value
        );

      unique case (transition_class)

        FRP_TRANS_PENDING_COMPLETION: begin
          frp_transition_selected_target =
            pending_value;
        end

        FRP_TRANS_OPPOSITE_POLARITY: begin
          // Only the first legal tick leg is selected here.
          // The opposite target remains retained in pending_route.

          frp_transition_selected_target =
            FRP_ACTIVE_NEUTRAL;
        end

        FRP_TRANS_SAME_STATE: begin
          frp_transition_selected_target =
            state_value;
        end

        FRP_TRANS_ZERO_TO_NONZERO,
        FRP_TRANS_NONZERO_TO_ZERO: begin
          frp_transition_selected_target =
            target_value;
        end

        default: begin
          frp_transition_selected_target =
            state_value;
        end

      endcase
    end
  endfunction

  function automatic logic frp_transition_consumes_capacity(
    input frp_m31_transition_class_e transition_class
  );
    begin
      unique case (transition_class)

        FRP_TRANS_ZERO_TO_NONZERO,
        FRP_TRANS_NONZERO_TO_ZERO,
        FRP_TRANS_OPPOSITE_POLARITY,
        FRP_TRANS_PENDING_COMPLETION: begin
          frp_transition_consumes_capacity =
            1'b1;
        end

        default: begin
          frp_transition_consumes_capacity =
            1'b0;
        end

      endcase
    end
  endfunction
  
    // --------------------------------------------------------------------------
  // Scheduler helpers and transition eligibility
  // --------------------------------------------------------------------------

  function automatic logic frp_is_valid_scheduler_mode(
    input frp_m31_scheduler_mode_e mode
  );
    begin
      frp_is_valid_scheduler_mode =
        (mode == FRP_MODE_FREE)
        || (mode == FRP_MODE_7_1)
        || (mode == FRP_MODE_1_7);
    end
  endfunction

  function automatic logic frp_scheduler_state_is_valid(
    input frp_m31_scheduler_state_e state
  );
    begin
      frp_scheduler_state_is_valid =
        (state == FRP_SCHED_FREE)
        || (state == FRP_SCHED_BALANCE)
        || (state == FRP_SCHED_COMMIT)
        || (state == FRP_SCHED_EXCITE)
        || (state == FRP_SCHED_NEUTRALIZE);
    end
  endfunction

  function automatic frp_m31_scheduler_state_e frp_decode_scheduler_state(
    input frp_m31_scheduler_mode_e mode,
    input logic [FRP_M31_PERIOD_BITS-1:0] period_index
  );
    begin
      unique case (mode)

        FRP_MODE_FREE: begin
          frp_decode_scheduler_state =
            FRP_SCHED_FREE;
        end

        FRP_MODE_7_1: begin
          if (
            period_index == 3'd7
          ) begin
            frp_decode_scheduler_state =
              FRP_SCHED_COMMIT;
          end else begin
            frp_decode_scheduler_state =
              FRP_SCHED_BALANCE;
          end
        end

        FRP_MODE_1_7: begin
          if (
            period_index == 3'd0
          ) begin
            frp_decode_scheduler_state =
              FRP_SCHED_EXCITE;
          end else begin
            frp_decode_scheduler_state =
              FRP_SCHED_NEUTRALIZE;
          end
        end

        default: begin
          frp_decode_scheduler_state =
            FRP_SCHED_INVALID;
        end

      endcase
    end
  endfunction

  function automatic logic frp_scheduler_is_commit_capable(
    input frp_m31_scheduler_state_e state
  );
    begin
      frp_scheduler_is_commit_capable =
        (state == FRP_SCHED_FREE)
        || (state == FRP_SCHED_COMMIT)
        || (state == FRP_SCHED_EXCITE);
    end
  endfunction

  function automatic logic frp_scheduler_is_neutralize_capable(
    input frp_m31_scheduler_state_e state
  );
    begin
      frp_scheduler_is_neutralize_capable =
        (state == FRP_SCHED_FREE)
        || (state == FRP_SCHED_BALANCE)
        || (state == FRP_SCHED_NEUTRALIZE);
    end
  endfunction

  function automatic logic frp_scheduler_allows_transition(
    input frp_m31_scheduler_state_e state,
    input frp_m31_transition_class_e transition_class
  );
    begin
      if (
        !frp_scheduler_state_is_valid(state)
      ) begin
        frp_scheduler_allows_transition =
          1'b0;
      end else begin
        unique case (transition_class)

          FRP_TRANS_SAME_STATE,
          FRP_TRANS_HOLD: begin
            frp_scheduler_allows_transition =
              1'b1;
          end

          FRP_TRANS_ZERO_TO_NONZERO,
          FRP_TRANS_PENDING_COMPLETION: begin
            frp_scheduler_allows_transition =
              frp_scheduler_is_commit_capable(
                state
              );
          end

          FRP_TRANS_NONZERO_TO_ZERO,
          FRP_TRANS_OPPOSITE_POLARITY: begin
            frp_scheduler_allows_transition =
              frp_scheduler_is_neutralize_capable(
                state
              );
          end

          default: begin
            frp_scheduler_allows_transition =
              1'b0;
          end

        endcase
      end
    end
  endfunction

  // --------------------------------------------------------------------------
  // Parameter and packed-state helpers
  // --------------------------------------------------------------------------

  function automatic int frp_calc_request_lanes(
    input int cells
  );

    int rounded_value;

    begin
      rounded_value =
        (
          (cells * FRP_M31_TRANSITION_FRACTION_NUM)
          + (FRP_M31_TRANSITION_FRACTION_DEN / 2)
        )
        / FRP_M31_TRANSITION_FRACTION_DEN;

      if (
        rounded_value < 1
      ) begin
        frp_calc_request_lanes =
          1;
      end else begin
        frp_calc_request_lanes =
          rounded_value;
      end
    end
  endfunction

  function automatic int frp_calc_cell_index_bits(
    input int cells
  );
    begin
      if (
        cells <= 1
      ) begin
        frp_calc_cell_index_bits =
          1;
      end else begin
        frp_calc_cell_index_bits =
          $clog2(cells);
      end
    end
  endfunction

  function automatic int frp_calc_packed_state_bits(
    input int cells
  );
    begin
      frp_calc_packed_state_bits =
        cells * FRP_M31_STATE_BITS;
    end
  endfunction

  function automatic int frp_cell_lsb(
    input int cell_index
  );
    begin
      frp_cell_lsb =
        cell_index * FRP_M31_STATE_BITS;
    end
  endfunction

  function automatic int frp_cell_msb(
    input int cell_index
  );
    begin
      frp_cell_msb =
        (cell_index * FRP_M31_STATE_BITS)
        + (FRP_M31_STATE_BITS - 1);
    end
  endfunction

  // --------------------------------------------------------------------------
  // Static inherited qualification profiles
  // --------------------------------------------------------------------------

  localparam int FRP_M31_REQUEST_LANES_8_CELLS =
    frp_calc_request_lanes(8);

  localparam int FRP_M31_REQUEST_LANES_16_CELLS =
    frp_calc_request_lanes(16);

  localparam int FRP_M31_REQUEST_LANES_32_CELLS =
    frp_calc_request_lanes(32);

  localparam logic FRP_M31_REQUEST_LANE_PROFILES_VALID =
    (FRP_M31_REQUEST_LANES_8_CELLS == 2)
    && (FRP_M31_REQUEST_LANES_16_CELLS == 4)
    && (FRP_M31_REQUEST_LANES_32_CELLS == 8);

endpackage : frp_m31_pkg

`endif
