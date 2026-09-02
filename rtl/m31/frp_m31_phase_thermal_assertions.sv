// SPDX-License-Identifier: Apache-2.0
// FRP M31 integrated phase, ternary and thermal assertion layer.

`ifndef FRP_M31_PHASE_THERMAL_ASSERTIONS_SV
`define FRP_M31_PHASE_THERMAL_ASSERTIONS_SV

`include "frp_m31_pkg.sv"
`include "frp_m31_fixed_point_pkg.sv"

module frp_m31_phase_thermal_assertions #(
  parameter int CELLS = 8,
  parameter int COUNTER_BITS = 32
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic [(CELLS*2)-1:0] state_out,
  input logic [(CELLS*2)-1:0] phase_target,
  input logic [(CELLS*32)-1:0] phase_projection_q30,
  input logic signed [31:0] pair_coherence_q30,
  input logic signed [31:0] cluster_coherence_q30,
  input logic signed [31:0] global_coherence_q30,
  input logic signed [31:0] organization_dispersion_q30,
  input logic signed [31:0] temperature_proxy_q16,
  input logic signed [31:0] peak_temperature_proxy_q16,
  input logic [COUNTER_BITS-1:0] actual_direct_events,
  input logic [COUNTER_BITS-1:0] reserved_state_events,
  input logic [COUNTER_BITS-1:0] queue_overflow_events
);

  import frp_m31_pkg::*;
  import frp_m31_fixed_point_pkg::*;

  default clocking m31_assertion_clock @(posedge clk); endclocking

  assert property (
    disable iff (!rst_n)
    (actual_direct_events == '0)
    && (reserved_state_events == '0)
    && (queue_overflow_events == '0)
  ) else $error("FRP M31 zero-event invariant failed");

  assert property (
    disable iff (!rst_n)
    (pair_coherence_q30 >= 0)
    && (pair_coherence_q30 <= FRP_M31_Q30_ONE)
    && (cluster_coherence_q30 >= 0)
    && (cluster_coherence_q30 <= FRP_M31_Q30_ONE)
    && (global_coherence_q30 >= 0)
    && (global_coherence_q30 <= FRP_M31_Q30_ONE)
    && (organization_dispersion_q30 >= 0)
    && (organization_dispersion_q30 <= FRP_M31_Q30_ONE)
  ) else $error("FRP M31 coherence range invariant failed");

  assert property (
    disable iff (!rst_n)
    (temperature_proxy_q16 >= 0)
    && (peak_temperature_proxy_q16 >= temperature_proxy_q16)
  ) else $error("FRP M31 thermal proxy range invariant failed");

  generate
    for (genvar cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin : g_cell_assertions
      assert property (
        disable iff (!rst_n)
        frp_is_valid_ternary(state_out[(cell_index*2) +: 2])
      ) else $error("FRP M31 retained ternary domain invariant failed");

      assert property (
        disable iff (!rst_n)
        (
          ($signed(phase_projection_q30[(cell_index*32) +: 32]) >
            FRP_M31_TARGET_THRESHOLD_Q30)
          |-> (phase_target[(cell_index*2) +: 2] == FRP_STATE_POS)
        )
      ) else $error("FRP M31 positive resonance target invariant failed");

      assert property (
        disable iff (!rst_n)
        (
          ($signed(phase_projection_q30[(cell_index*32) +: 32]) <
            -FRP_M31_TARGET_THRESHOLD_Q30)
          |-> (phase_target[(cell_index*2) +: 2] == FRP_STATE_NEG)
        )
      ) else $error("FRP M31 negative resonance target invariant failed");

      assert property (
        disable iff (!rst_n)
        (
          ($signed(phase_projection_q30[(cell_index*32) +: 32]) <=
            FRP_M31_TARGET_THRESHOLD_Q30)
          &&
          ($signed(phase_projection_q30[(cell_index*32) +: 32]) >=
            -FRP_M31_TARGET_THRESHOLD_Q30)
        ) |-> (phase_target[(cell_index*2) +: 2] == FRP_ACTIVE_NEUTRAL)
      ) else $error("FRP M31 active-zero resonance target invariant failed");

      assert property (
        disable iff (!rst_n)
        tick_enable
        |-> !frp_is_opposite_polarity(
          $past(state_out[(cell_index*2) +: 2]),
          state_out[(cell_index*2) +: 2]
        )
      ) else $error("FRP M31 direct opposite-polarity writeback detected");
    end
  endgenerate

endmodule

`endif
