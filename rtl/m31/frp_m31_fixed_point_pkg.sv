// SPDX-License-Identifier: Apache-2.0
// FRP M31 fixed-point and phase-domain definitions.

`ifndef FRP_M31_FIXED_POINT_PKG_SV
`define FRP_M31_FIXED_POINT_PKG_SV

package frp_m31_fixed_point_pkg;

  typedef logic signed [31:0] frp_m31_s32q16_t;
  typedef logic signed [31:0] frp_m31_s32q30_t;
  typedef logic        [31:0] frp_m31_phase_u32_t;
  typedef logic signed [31:0] frp_m31_gamma_s32_t;

  localparam int FRP_M31_Q16_FRACTION_BITS = 16;
  localparam int FRP_M31_Q30_FRACTION_BITS = 30;
  localparam int FRP_M31_TRIG_ADDRESS_BITS = 12;
  localparam int FRP_M31_TRIG_ENTRIES = 4096;

  localparam frp_m31_s32q16_t FRP_M31_Q16_ZERO = 32'sd0;
  localparam frp_m31_s32q16_t FRP_M31_Q16_ONE = 32'sd65536;
  localparam frp_m31_s32q30_t FRP_M31_Q30_ZERO = 32'sd0;
  localparam frp_m31_s32q30_t FRP_M31_Q30_ONE = 32'sd1073741824;

  // Values are round-to-nearest with half cases away from zero, matching
  // the published M15 fixed-point interface used by M31 evidence.
  localparam frp_m31_s32q30_t FRP_M31_TARGET_THRESHOLD_Q30 = 32'sd354334802;
  localparam frp_m31_gamma_s32_t FRP_M31_GAMMA_NOMINAL = 32'sd644245094;
  localparam frp_m31_s32q16_t FRP_M31_COUPLING_NOMINAL_Q16 = 32'sd18350;
  localparam frp_m31_s32q16_t FRP_M31_DELAY_ALPHA_Q16 = 32'sd19661;
  localparam frp_m31_s32q16_t FRP_M31_BASE_FREQUENCY_Q16 = 32'sd65536;
  localparam frp_m31_s32q16_t FRP_M31_BASE_VELOCITY_GAIN_Q16 = 32'sd3932;
  localparam frp_m31_s32q16_t FRP_M31_STATE_FREQUENCY_GAIN_Q16 = 32'sd3932;
  localparam frp_m31_s32q16_t FRP_M31_SWITCH_FREQUENCY_GAIN_Q16 = 32'sd7864;
  localparam frp_m31_s32q16_t FRP_M31_PUSH_FREE_Q16 = 32'sd197;
  localparam frp_m31_s32q16_t FRP_M31_PUSH_BALANCE_Q16 = 32'sd197;
  localparam frp_m31_s32q16_t FRP_M31_PUSH_COMMIT_Q16 = 32'sd655;
  localparam frp_m31_s32q16_t FRP_M31_PUSH_EXCITE_Q16 = 32'sd393;
  localparam frp_m31_s32q16_t FRP_M31_PUSH_NEUTRALIZE_Q16 = 32'sd197;

  // Exact dyadic topology weights for the eight-cell M31 qualification
  // profile.  Each shell-weighted sum closes to Q30 one.
  localparam frp_m31_s32q30_t FRP_M31_WEIGHT_DISTANCE_1_Q30 = 32'sd516461574;
  localparam frp_m31_s32q30_t FRP_M31_WEIGHT_DISTANCE_2_Q30 = 32'sd158959695;
  localparam frp_m31_s32q30_t FRP_M31_WEIGHT_DISTANCE_3_Q30 = 32'sd59840215;

  // Current common-RC comparative proxy; this is a normalized proxy, not a
  // physical temperature or energy measurement.
  localparam frp_m31_s32q30_t FRP_M31_THERMAL_DECAY_Q30 = 32'sd1020054733;
  localparam frp_m31_s32q30_t FRP_M31_THERMAL_GAIN_Q30 = 32'sd10737418;

  function automatic frp_m31_s32q16_t frp_m31_sat_s32(
    input logic signed [63:0] value
  );
    begin
      if (value > 64'sd2147483647)
        frp_m31_sat_s32 = 32'sh7fffffff;
      else if (value < -64'sd2147483648)
        frp_m31_sat_s32 = 32'sh80000000;
      else
        frp_m31_sat_s32 = value[31:0];
    end
  endfunction

  function automatic logic signed [63:0] frp_m31_round_shift_s64(
    input logic signed [63:0] value,
    input int unsigned shift
  );
    logic signed [63:0] magnitude;
    logic signed [63:0] rounded;
    logic signed [63:0] half_value;
    begin
      if (shift == 0) begin
        frp_m31_round_shift_s64 = value;
      end else begin
        half_value = 64'sd1 <<< (shift - 1);
        if (value < 0) begin
          magnitude = -value;
          rounded = (magnitude + half_value) >>> shift;
          frp_m31_round_shift_s64 = -rounded;
        end else begin
          frp_m31_round_shift_s64 = (value + half_value) >>> shift;
        end
      end
    end
  endfunction

  function automatic frp_m31_s32q16_t frp_m31_mul_q16(
    input frp_m31_s32q16_t left,
    input frp_m31_s32q16_t right
  );
    logic signed [63:0] product;
    begin
      product = left * right;
      frp_m31_mul_q16 = frp_m31_sat_s32(
        frp_m31_round_shift_s64(product, FRP_M31_Q16_FRACTION_BITS)
      );
    end
  endfunction

  function automatic frp_m31_s32q30_t frp_m31_mul_q30(
    input frp_m31_s32q30_t left,
    input frp_m31_s32q30_t right
  );
    logic signed [63:0] product;
    begin
      product = left * right;
      frp_m31_mul_q30 = frp_m31_sat_s32(
        frp_m31_round_shift_s64(product, FRP_M31_Q30_FRACTION_BITS)
      );
    end
  endfunction

  function automatic frp_m31_s32q16_t frp_m31_mul_q16_q30(
    input frp_m31_s32q16_t left_q16,
    input frp_m31_s32q30_t right_q30
  );
    logic signed [63:0] product;
    begin
      product = left_q16 * right_q30;
      frp_m31_mul_q16_q30 = frp_m31_sat_s32(
        frp_m31_round_shift_s64(product, FRP_M31_Q30_FRACTION_BITS)
      );
    end
  endfunction

  function automatic frp_m31_s32q16_t frp_m31_q30_to_q16(
    input frp_m31_s32q30_t value_q30
  );
    begin
      frp_m31_q30_to_q16 = frp_m31_sat_s32(
        frp_m31_round_shift_s64(
          {{32{value_q30[31]}}, value_q30},
          FRP_M31_Q30_FRACTION_BITS - FRP_M31_Q16_FRACTION_BITS
        )
      );
    end
  endfunction

  function automatic frp_m31_s32q30_t frp_m31_q16_to_q30(
    input frp_m31_s32q16_t value_q16
  );
    logic signed [63:0] extended;
    begin
      extended = {{32{value_q16[31]}}, value_q16};
      extended = extended <<< (FRP_M31_Q30_FRACTION_BITS - FRP_M31_Q16_FRACTION_BITS);
      frp_m31_q16_to_q30 = frp_m31_sat_s32(extended);
    end
  endfunction

  function automatic frp_m31_s32q30_t frp_m31_topology_weight_q30(
    input int unsigned left_index,
    input int unsigned right_index
  );
    int unsigned differing;
    begin
      differing = left_index ^ right_index;
      if (differing < 2)
        frp_m31_topology_weight_q30 = FRP_M31_WEIGHT_DISTANCE_1_Q30;
      else if (differing < 4)
        frp_m31_topology_weight_q30 = FRP_M31_WEIGHT_DISTANCE_2_Q30;
      else
        frp_m31_topology_weight_q30 = FRP_M31_WEIGHT_DISTANCE_3_Q30;
    end
  endfunction

  function automatic frp_m31_s32q16_t frp_m31_scheduler_push_q16(
    input logic [2:0] scheduler_state
  );
    begin
      case (scheduler_state)
        3'b010: frp_m31_scheduler_push_q16 = FRP_M31_PUSH_COMMIT_Q16;
        3'b011: frp_m31_scheduler_push_q16 = FRP_M31_PUSH_EXCITE_Q16;
        3'b001: frp_m31_scheduler_push_q16 = FRP_M31_PUSH_BALANCE_Q16;
        3'b100: frp_m31_scheduler_push_q16 = FRP_M31_PUSH_NEUTRALIZE_Q16;
        default: frp_m31_scheduler_push_q16 = FRP_M31_PUSH_FREE_Q16;
      endcase
    end
  endfunction

  // Convert a Q16 radian velocity into the published PHASE_U32 scale.
  function automatic logic signed [31:0] frp_m31_velocity_to_phase_word(
    input frp_m31_s32q16_t velocity_rad_q16
  );
    logic signed [79:0] velocity_extended;
    logic signed [79:0] conversion_constant;
    logic signed [79:0] product;
    logic signed [79:0] magnitude;
    logic signed [79:0] rounded;
    begin
      velocity_extended = {{48{velocity_rad_q16[31]}}, velocity_rad_q16};
      conversion_constant = 80'sd44798133900177;
      product = velocity_extended * conversion_constant;
      if (product < 0) begin
        magnitude = -product;
        rounded = (magnitude + 80'sd2147483648) >>> 32;
        frp_m31_velocity_to_phase_word = -rounded[31:0];
      end else begin
        rounded = (product + 80'sd2147483648) >>> 32;
        frp_m31_velocity_to_phase_word = rounded[31:0];
      end
    end
  endfunction

endpackage

`endif
