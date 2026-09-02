// SPDX-License-Identifier: Apache-2.0
// FRP M31 fixed-point coherence/pressure stability observable.

`ifndef FRP_M31_STABILITY_SV
`define FRP_M31_STABILITY_SV

`include "frp_m31_fixed_point_pkg.sv"

module frp_m31_stability #(
  parameter int CELLS = 8
) (
  input logic [(CELLS*2)-1:0] retained_state,
  input logic signed [31:0] global_coherence_q30,
  input logic signed [31:0] cluster_coherence_q30,
  input logic signed [31:0] temperature_proxy_q16,
  input logic signed [31:0] switch_load_q16,
  output logic signed [31:0] coherence_capacity_q16,
  output logic signed [31:0] pressure_q16,
  output logic signed [31:0] stability_margin_q16,
  output logic stable
);

  import frp_m31_fixed_point_pkg::*;

  localparam logic signed [31:0] BASE_CAPACITY_Q16 = 32'sd53740;
  localparam logic signed [31:0] GLOBAL_GAIN_Q16 = 32'sd22282;
  localparam logic signed [31:0] CLUSTER_GAIN_Q16 = 32'sd10486;
  localparam logic signed [31:0] NEUTRAL_GAIN_Q16 = 32'sd5243;

  always_comb begin : stability_combinational
    int unsigned neutral_count;
    logic signed [31:0] neutral_fraction_q30;
    logic signed [63:0] capacity_sum;
    logic signed [63:0] pressure_sum;

    neutral_count = 0;
    for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      if (retained_state[(cell_index*2) +: 2] == 2'b00)
        neutral_count = neutral_count + 1;
    end

    neutral_fraction_q30 = (neutral_count * 64'sd1073741824) / CELLS;
    capacity_sum = 64'sd53740;
    capacity_sum = capacity_sum + frp_m31_mul_q16_q30(
      GLOBAL_GAIN_Q16,
      global_coherence_q30
    );
    capacity_sum = capacity_sum + frp_m31_mul_q16_q30(
      CLUSTER_GAIN_Q16,
      cluster_coherence_q30
    );
    capacity_sum = capacity_sum + frp_m31_mul_q16_q30(
      NEUTRAL_GAIN_Q16,
      neutral_fraction_q30
    );
    coherence_capacity_q16 = frp_m31_sat_s32(capacity_sum);

    pressure_sum =
      {{32{temperature_proxy_q16[31]}}, temperature_proxy_q16} +
      {{32{switch_load_q16[31]}}, switch_load_q16};
    pressure_q16 = frp_m31_sat_s32(pressure_sum);
    stability_margin_q16 = coherence_capacity_q16 - pressure_q16;
    stable = stability_margin_q16 > 0;
  end

endmodule

`endif
