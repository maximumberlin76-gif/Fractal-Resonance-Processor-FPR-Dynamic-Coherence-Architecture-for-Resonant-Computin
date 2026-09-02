// SPDX-License-Identifier: Apache-2.0
// FRP M31 retained relative-phase interference and resonance-selection path.

`ifndef FRP_M31_PHASE_INTERFERENCE_SV
`define FRP_M31_PHASE_INTERFERENCE_SV

`timescale 1ns / 1ps

`include "frp_m31_pkg.sv"
`include "frp_m31_fixed_point_pkg.sv"

module frp_m31_phase_interference #(
  parameter int CELLS = 8,
  parameter string SIN_LUT_FILE = "rtl/m31/frp_m31_sin_q30.mem"
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic load_valid,

  input logic [(CELLS*32)-1:0] phase_load,
  input logic [(CELLS*32)-1:0] frequency_load_q16,
  input logic [(CELLS*32)-1:0] gamma_effective_word,
  input logic [(CELLS*32)-1:0] thermal_node_factor_q30,
  input logic [(CELLS*2)-1:0] retained_state,
  input logic [CELLS-1:0] switch_activity,
  input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,

  output logic [(CELLS*32)-1:0] phase_word_q,
  output logic [(CELLS*32)-1:0] frequency_current_q16,
  output logic [(CELLS*32)-1:0] coupling_field_q16,
  output logic [(CELLS*32)-1:0] phase_projection_q30,
  output logic [(CELLS*2)-1:0] phase_target,
  output logic signed [31:0] pair_coherence_q30,
  output logic signed [31:0] cluster_coherence_q30,
  output logic signed [31:0] global_coherence_q30,
  output logic signed [31:0] organization_dispersion_q30
);

  import frp_m31_pkg::*;
  import frp_m31_fixed_point_pkg::*;

  logic signed [31:0] sin_lut [0:FRP_M31_TRIG_ENTRIES-1];

  logic [31:0] phase_q [0:CELLS-1];
  logic [31:0] phase_d [0:CELLS-1];
  logic signed [31:0] frequency_q [0:CELLS-1];
  logic signed [31:0] frequency_d [0:CELLS-1];
  logic signed [31:0] sine_q30 [0:CELLS-1];
  logic signed [31:0] cosine_q30 [0:CELLS-1];
  logic signed [31:0] coupling_q16 [0:CELLS-1];
  logic signed [31:0] pair_group_q30 [0:3];
  logic signed [31:0] cluster_group_q30 [0:1];

  function automatic logic signed [31:0] sin_phase_q30(
    input logic [31:0] phase_word
  );
    begin
      sin_phase_q30 = sin_lut[phase_word[31:20]];
    end
  endfunction

  function automatic logic signed [31:0] cos_phase_q30(
    input logic [31:0] phase_word
  );
    logic [11:0] index;
    begin
      index = phase_word[31:20] + 12'd1024;
      cos_phase_q30 = sin_lut[index];
    end
  endfunction

  function automatic logic signed [63:0] round_div_s64(
    input logic signed [63:0] numerator,
    input int unsigned denominator
  );
    logic signed [63:0] magnitude;
    logic signed [63:0] half_denominator;
    begin
      half_denominator = denominator / 2;
      if (numerator < 0) begin
        magnitude = -numerator;
        round_div_s64 = -((magnitude + half_denominator) / denominator);
      end else begin
        round_div_s64 = (numerator + half_denominator) / denominator;
      end
    end
  endfunction

  function automatic logic [31:0] isqrt_u64(
    input logic [63:0] radicand
  );
    logic [31:0] root;
    logic [31:0] trial;
    logic [63:0] square;
    integer bit_index;
    begin
      root = 32'd0;
      for (bit_index = 31; bit_index >= 0; bit_index = bit_index - 1) begin
        trial = root | (32'd1 << bit_index);
        square = trial * trial;
        if (square <= radicand)
          root = trial;
      end
      isqrt_u64 = root;
    end
  endfunction

  function automatic logic signed [31:0] coherence_from_sums(
    input logic signed [63:0] sum_cos_q30,
    input logic signed [63:0] sum_sin_q30,
    input int unsigned population
  );
    logic signed [63:0] mean_cos_q30;
    logic signed [63:0] mean_sin_q30;
    logic [63:0] magnitude_square_q60;
    logic [31:0] magnitude_q30;
    begin
      mean_cos_q30 = round_div_s64(sum_cos_q30, population);
      mean_sin_q30 = round_div_s64(sum_sin_q30, population);
      magnitude_square_q60 =
        (mean_cos_q30 * mean_cos_q30) +
        (mean_sin_q30 * mean_sin_q30);
      magnitude_q30 = isqrt_u64(magnitude_square_q60);
      if (magnitude_q30 > 32'd1073741824)
        coherence_from_sums = FRP_M31_Q30_ONE;
      else
        coherence_from_sums = magnitude_q30;
    end
  endfunction

  initial begin
    if (CELLS != 8)
      $fatal(1, "FRP M31 phase engine currently qualifies exactly eight cells");
    $readmemh(SIN_LUT_FILE, sin_lut);
    if (sin_lut[0] !== 32'sd0)
      $fatal(1, "FRP M31 sine LUT zero-point mismatch");
    if (sin_lut[1024] !== FRP_M31_Q30_ONE)
      $fatal(1, "FRP M31 sine LUT quarter-cycle mismatch");
    if (sin_lut[2048] !== 32'sd0)
      $fatal(1, "FRP M31 sine LUT half-cycle mismatch");
    if (sin_lut[3072] !== -FRP_M31_Q30_ONE)
      $fatal(1, "FRP M31 sine LUT three-quarter-cycle mismatch");
  end

  always_comb begin : phase_combinational
    logic signed [63:0] total_q30;
    logic signed [31:0] pair_factor_q30;
    logic signed [31:0] weighted_factor_q30;
    logic signed [31:0] pair_term_q30;
    logic signed [31:0] target_frequency_q16;
    logic signed [31:0] frequency_delta_q16;
    logic signed [31:0] filtered_delta_q16;
    logic signed [31:0] velocity_q16;
    logic signed [31:0] phase_step;
    logic signed [31:0] state_gain_q16;
    logic signed [31:0] switch_gain_q16;
    logic [31:0] phase_plus_gamma;
    logic [31:0] relative_phase;
    logic signed [31:0] thermal_i_q30;
    logic signed [31:0] thermal_j_q30;
    logic signed [31:0] topology_weight_q30;
    logic [1:0] state_value;
    logic signed [63:0] sum_cos_q30;
    logic signed [63:0] sum_sin_q30;
    logic signed [63:0] group_sum_q30;
    logic signed [63:0] cluster_difference_q30;

    phase_word_q = '0;
    frequency_current_q16 = '0;
    coupling_field_q16 = '0;
    phase_projection_q30 = '0;
    phase_target = '0;

    for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      sine_q30[cell_index] = sin_phase_q30(phase_q[cell_index]);
      cosine_q30[cell_index] = cos_phase_q30(phase_q[cell_index]);
      phase_word_q[(cell_index*32) +: 32] = phase_q[cell_index];
      frequency_current_q16[(cell_index*32) +: 32] = frequency_q[cell_index];
      phase_projection_q30[(cell_index*32) +: 32] = sine_q30[cell_index];

      if (sine_q30[cell_index] > FRP_M31_TARGET_THRESHOLD_Q30)
        phase_target[(cell_index*2) +: 2] = FRP_STATE_POS;
      else if (sine_q30[cell_index] < -FRP_M31_TARGET_THRESHOLD_Q30)
        phase_target[(cell_index*2) +: 2] = FRP_STATE_NEG;
      else
        phase_target[(cell_index*2) +: 2] = FRP_ACTIVE_NEUTRAL;
    end

    for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      total_q30 = 64'sd0;
      thermal_i_q30 = thermal_node_factor_q30[(cell_index*32) +: 32];
      phase_plus_gamma = phase_q[cell_index] + gamma_effective_word[(cell_index*32) +: 32];

      for (int other = 0; other < CELLS; other = other + 1) begin
        if (other != cell_index) begin
          thermal_j_q30 = thermal_node_factor_q30[(other*32) +: 32];
          topology_weight_q30 = frp_m31_topology_weight_q30(cell_index, other);
          pair_factor_q30 = frp_m31_mul_q30(thermal_i_q30, thermal_j_q30);
          weighted_factor_q30 = frp_m31_mul_q30(
            topology_weight_q30,
            pair_factor_q30
          );
          relative_phase = phase_q[other] - phase_plus_gamma;
          pair_term_q30 = frp_m31_mul_q30(
            weighted_factor_q30,
            sin_phase_q30(relative_phase)
          );
          total_q30 = total_q30 + pair_term_q30;
        end
      end

      coupling_q16[cell_index] = frp_m31_mul_q16(
        FRP_M31_COUPLING_NOMINAL_Q16,
        frp_m31_q30_to_q16(frp_m31_sat_s32(total_q30))
      );
      coupling_field_q16[(cell_index*32) +: 32] = coupling_q16[cell_index];

      state_value = retained_state[(cell_index*2) +: 2];
      if ((state_value == FRP_STATE_NEG) || (state_value == FRP_STATE_POS))
        state_gain_q16 = FRP_M31_STATE_FREQUENCY_GAIN_Q16;
      else
        state_gain_q16 = FRP_M31_Q16_ZERO;

      if (switch_activity[cell_index])
        switch_gain_q16 = FRP_M31_SWITCH_FREQUENCY_GAIN_Q16;
      else
        switch_gain_q16 = FRP_M31_Q16_ZERO;

      target_frequency_q16 = FRP_M31_BASE_FREQUENCY_Q16
        + state_gain_q16 + switch_gain_q16;
      frequency_delta_q16 = target_frequency_q16 - frequency_q[cell_index];
      filtered_delta_q16 = frp_m31_mul_q16(
        FRP_M31_DELAY_ALPHA_Q16,
        frequency_delta_q16
      );
      frequency_d[cell_index] = frp_m31_sat_s32(
        {{32{frequency_q[cell_index][31]}}, frequency_q[cell_index]} +
        {{32{filtered_delta_q16[31]}}, filtered_delta_q16}
      );

      velocity_q16 = frp_m31_mul_q16(
        FRP_M31_BASE_VELOCITY_GAIN_Q16,
        frequency_d[cell_index]
      ) + frp_m31_scheduler_push_q16(scheduler_state) + coupling_q16[cell_index];
      phase_step = frp_m31_velocity_to_phase_word(velocity_q16);
      phase_d[cell_index] = phase_q[cell_index] + phase_step;
    end

    for (int group = 0; group < 4; group = group + 1) begin
      sum_cos_q30 = cosine_q30[group*2] + cosine_q30[group*2+1];
      sum_sin_q30 = sine_q30[group*2] + sine_q30[group*2+1];
      pair_group_q30[group] = coherence_from_sums(sum_cos_q30, sum_sin_q30, 2);
    end

    for (int group = 0; group < 2; group = group + 1) begin
      sum_cos_q30 = 64'sd0;
      sum_sin_q30 = 64'sd0;
      for (int member = 0; member < 4; member = member + 1) begin
        sum_cos_q30 = sum_cos_q30 + cosine_q30[group*4+member];
        sum_sin_q30 = sum_sin_q30 + sine_q30[group*4+member];
      end
      cluster_group_q30[group] = coherence_from_sums(sum_cos_q30, sum_sin_q30, 4);
    end

    sum_cos_q30 = 64'sd0;
    sum_sin_q30 = 64'sd0;
    group_sum_q30 = 64'sd0;
    for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      sum_cos_q30 = sum_cos_q30 + cosine_q30[cell_index];
      sum_sin_q30 = sum_sin_q30 + sine_q30[cell_index];
    end
    for (int group = 0; group < 4; group = group + 1)
      group_sum_q30 = group_sum_q30 + pair_group_q30[group];
    pair_coherence_q30 = round_div_s64(group_sum_q30, 4);
    cluster_coherence_q30 = round_div_s64(
      cluster_group_q30[0] + cluster_group_q30[1],
      2
    );
    global_coherence_q30 = coherence_from_sums(sum_cos_q30, sum_sin_q30, CELLS);

    cluster_difference_q30 = cluster_group_q30[0] - cluster_group_q30[1];
    if (cluster_difference_q30 < 0)
      cluster_difference_q30 = -cluster_difference_q30;
    organization_dispersion_q30 = round_div_s64(cluster_difference_q30, 2);
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
        phase_q[cell_index] <= cell_index * 32'h20000000;
        frequency_q[cell_index] <= FRP_M31_BASE_FREQUENCY_Q16;
      end
    end else if (load_valid) begin
      for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
        phase_q[cell_index] <= phase_load[(cell_index*32) +: 32];
        frequency_q[cell_index] <= frequency_load_q16[(cell_index*32) +: 32];
      end
    end else if (tick_enable) begin
      for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
        phase_q[cell_index] <= phase_d[cell_index];
        frequency_q[cell_index] <= frequency_d[cell_index];
      end
    end
  end

endmodule

`endif
