// SPDX-License-Identifier: Apache-2.0
// FRP M32 registered boundary for phase-derived ternary targets.

`ifndef FRP_M32_REGISTERED_TARGET_BOUNDARY_SV
`define FRP_M32_REGISTERED_TARGET_BOUNDARY_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"

module frp_m32_registered_target_boundary #(
  parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic clear_counters,

  input logic phase_target_valid,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] phase_target,

  output logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] registered_target_q,
  output logic registered_target_valid_q,

  output logic phase_target_domain_valid,
  output logic registered_target_domain_valid,
  output logic capture_accepted,
  output logic capture_rejected,

  output logic [COUNTER_BITS-1:0] accepted_capture_events_q,
  output logic [COUNTER_BITS-1:0] rejected_capture_events_q
);

  function automatic logic target_symbol_valid(
    input logic [frp_m31_pkg::FRP_M31_STATE_BITS-1:0] value
  );
    begin
      case (value)
        frp_m31_pkg::FRP_STATE_NEG,
        frp_m31_pkg::FRP_ACTIVE_NEUTRAL,
        frp_m31_pkg::FRP_STATE_POS: target_symbol_valid = 1'b1;
        default: target_symbol_valid = 1'b0;
      endcase
    end
  endfunction

  function automatic logic [COUNTER_BITS-1:0] saturating_increment(
    input logic [COUNTER_BITS-1:0] value
  );
    begin
      if (&value)
        saturating_increment = value;
      else
        saturating_increment = value + {{(COUNTER_BITS-1){1'b0}}, 1'b1};
    end
  endfunction

  initial begin
    if (CELLS < 1)
      $fatal(1, "FRP M32 registered target boundary requires CELLS >= 1");
    if (COUNTER_BITS < 1)
      $fatal(
        1,
        "FRP M32 registered target boundary requires COUNTER_BITS >= 1"
      );
  end

  always_comb begin : target_domain_checks
    phase_target_domain_valid = 1'b1;
    registered_target_domain_valid = 1'b1;

    for (int cell_index = 0; cell_index < CELLS; cell_index++) begin
      if (!target_symbol_valid(
        phase_target[
          (cell_index*frp_m31_pkg::FRP_M31_STATE_BITS)
          +: frp_m31_pkg::FRP_M31_STATE_BITS
        ]
      )) begin
        phase_target_domain_valid = 1'b0;
      end

      if (!target_symbol_valid(
        registered_target_q[
          (cell_index*frp_m31_pkg::FRP_M31_STATE_BITS)
          +: frp_m31_pkg::FRP_M31_STATE_BITS
        ]
      )) begin
        registered_target_domain_valid = 1'b0;
      end
    end

    capture_accepted =
      tick_enable
      && phase_target_valid
      && phase_target_domain_valid;

    capture_rejected =
      tick_enable
      && phase_target_valid
      && !phase_target_domain_valid;
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      // The reset word is the active state 0 for every cell.  The validity
      // bit records upstream capture history; it does not make state 0 idle.
      registered_target_q <= {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
      registered_target_valid_q <= 1'b0;
    end else if (capture_accepted) begin
      registered_target_q <= phase_target;
      registered_target_valid_q <= 1'b1;
    end
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      accepted_capture_events_q <= '0;
      rejected_capture_events_q <= '0;
    end else if (clear_counters) begin
      accepted_capture_events_q <= '0;
      rejected_capture_events_q <= '0;
    end else begin
      if (capture_accepted) begin
        accepted_capture_events_q <= saturating_increment(
          accepted_capture_events_q
        );
      end

      if (capture_rejected) begin
        rejected_capture_events_q <= saturating_increment(
          rejected_capture_events_q
        );
      end
    end
  end

endmodule

`endif
