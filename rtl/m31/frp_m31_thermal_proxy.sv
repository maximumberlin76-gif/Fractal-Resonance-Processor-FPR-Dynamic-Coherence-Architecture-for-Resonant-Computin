// SPDX-License-Identifier: Apache-2.0
// FRP M31 normalized common-RC comparative thermal proxy.

`ifndef FRP_M31_THERMAL_PROXY_SV
`define FRP_M31_THERMAL_PROXY_SV

`timescale 1ns / 1ps

`include "frp_m31_fixed_point_pkg.sv"

module frp_m31_thermal_proxy (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic clear,
  input frp_m31_fixed_point_pkg::frp_m31_s32q16_t normalized_cycle_cost_q16,
  output frp_m31_fixed_point_pkg::frp_m31_s32q16_t temperature_proxy_q16,
  output frp_m31_fixed_point_pkg::frp_m31_s32q16_t peak_temperature_proxy_q16,
  output logic [31:0] sample_count_q
);

  import frp_m31_fixed_point_pkg::*;

  logic signed [31:0] temperature_d;
  logic signed [31:0] decayed_temperature_q16;
  logic signed [31:0] generated_temperature_q16;

  always_comb begin
    decayed_temperature_q16 = frp_m31_mul_q16_q30(
      temperature_proxy_q16,
      FRP_M31_THERMAL_DECAY_Q30
    );
    generated_temperature_q16 = frp_m31_mul_q16_q30(
      normalized_cycle_cost_q16,
      FRP_M31_THERMAL_GAIN_Q30
    );
    temperature_d = frp_m31_sat_s32(
      {{32{decayed_temperature_q16[31]}}, decayed_temperature_q16} +
      {{32{generated_temperature_q16[31]}}, generated_temperature_q16}
    );
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      temperature_proxy_q16 <= FRP_M31_Q16_ZERO;
      peak_temperature_proxy_q16 <= FRP_M31_Q16_ZERO;
      sample_count_q <= 32'd0;
    end else if (clear) begin
      temperature_proxy_q16 <= FRP_M31_Q16_ZERO;
      peak_temperature_proxy_q16 <= FRP_M31_Q16_ZERO;
      sample_count_q <= 32'd0;
    end else if (tick_enable) begin
      temperature_proxy_q16 <= temperature_d;
      if (temperature_d > peak_temperature_proxy_q16)
        peak_temperature_proxy_q16 <= temperature_d;
      sample_count_q <= sample_count_q + 32'd1;
    end
  end

endmodule

`endif
