// SPDX-License-Identifier: Apache-2.0
// FRP M31 complete deterministic RTL qualification testbench.

`ifndef FRP_M31_TB_SV
`define FRP_M31_TB_SV

`timescale 1ns / 1ps

`include "frp_m31_core.sv"
`include "frp_m31_phase_thermal_assertions.sv"

module frp_m31_tb;

  import frp_m31_pkg::*;
  import frp_m31_fixed_point_pkg::*;

  localparam int CELLS = 8;
  localparam int REQUEST_LANES = frp_calc_request_lanes(CELLS);
  localparam int CELL_INDEX_BITS = $clog2(CELLS);
  localparam int COUNTER_BITS = FRP_M31_COUNTER_BITS;

  logic clk;
  logic rst_n;
  logic tick_enable;
  logic clear_counters;
  frp_m31_scheduler_mode_e scheduler_mode;
  logic phase_load_valid;
  logic [(CELLS*32)-1:0] phase_load;
  logic [(CELLS*32)-1:0] frequency_load_q16;
  logic [(CELLS*32)-1:0] gamma_effective_word;
  logic [(CELLS*32)-1:0] thermal_node_factor_q30;
  logic auto_target_enable;
  logic [REQUEST_LANES-1:0] external_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] external_request_cell_index;
  logic [(REQUEST_LANES*2)-1:0] external_request_target;
  logic [(CELLS*2)-1:0] external_target_bank;

  logic [(CELLS*32)-1:0] phase_word_q;
  logic [(CELLS*32)-1:0] frequency_current_q16;
  logic [(CELLS*32)-1:0] coupling_field_q16;
  logic [(CELLS*32)-1:0] phase_projection_q30;
  logic [(CELLS*2)-1:0] phase_target;
  logic [(CELLS*2)-1:0] state_out;
  logic [(CELLS*2)-1:0] pending_route_out;
  frp_m31_scheduler_state_e scheduler_state_q;
  logic [COUNTER_BITS-1:0] ticks_recorded_q;
  logic [CELLS-1:0] accepted_change_mask;
  logic [COUNTER_BITS-1:0] accepted_changes;
  logic [COUNTER_BITS-1:0] switch_load_numerator;
  logic [COUNTER_BITS-1:0] actual_direct_events;
  logic [COUNTER_BITS-1:0] reserved_state_events;
  logic [COUNTER_BITS-1:0] queue_overflow_events;
  logic [FRP_M31_INVARIANT_FLAGS-1:0] invariant_flags;
  logic signed [31:0] pair_coherence_q30;
  logic signed [31:0] cluster_coherence_q30;
  logic signed [31:0] global_coherence_q30;
  logic signed [31:0] organization_dispersion_q30;
  logic signed [31:0] temperature_proxy_q16;
  logic signed [31:0] peak_temperature_proxy_q16;
  logic signed [31:0] coherence_capacity_q16;
  logic signed [31:0] pressure_q16;
  logic signed [31:0] stability_margin_q16;
  logic stable;

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  frp_m31_core #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .phase_load_valid(phase_load_valid),
    .phase_load(phase_load),
    .frequency_load_q16(frequency_load_q16),
    .gamma_effective_word(gamma_effective_word),
    .thermal_node_factor_q30(thermal_node_factor_q30),
    .auto_target_enable(auto_target_enable),
    .external_request_valid(external_request_valid),
    .external_request_cell_index(external_request_cell_index),
    .external_request_target(external_request_target),
    .external_target_bank(external_target_bank),
    .phase_word_q(phase_word_q),
    .frequency_current_q16(frequency_current_q16),
    .coupling_field_q16(coupling_field_q16),
    .phase_projection_q30(phase_projection_q30),
    .phase_target(phase_target),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .switch_load_numerator(switch_load_numerator),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags),
    .pair_coherence_q30(pair_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .global_coherence_q30(global_coherence_q30),
    .organization_dispersion_q30(organization_dispersion_q30),
    .temperature_proxy_q16(temperature_proxy_q16),
    .peak_temperature_proxy_q16(peak_temperature_proxy_q16),
    .coherence_capacity_q16(coherence_capacity_q16),
    .pressure_q16(pressure_q16),
    .stability_margin_q16(stability_margin_q16),
    .stable(stable)
  );

  frp_m31_phase_thermal_assertions #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) integrated_assertions (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .state_out(state_out),
    .phase_target(phase_target),
    .phase_projection_q30(phase_projection_q30),
    .pair_coherence_q30(pair_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .global_coherence_q30(global_coherence_q30),
    .organization_dispersion_q30(organization_dispersion_q30),
    .temperature_proxy_q16(temperature_proxy_q16),
    .peak_temperature_proxy_q16(peak_temperature_proxy_q16),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events)
  );

  function automatic logic [1:0] cell_state(
    input logic [(CELLS*2)-1:0] packed_state,
    input int cell_index
  );
    begin
      cell_state = packed_state[(cell_index*2) +: 2];
    end
  endfunction

  function automatic logic signed [31:0] cell_s32(
    input logic [(CELLS*32)-1:0] packed_value,
    input int cell_index
  );
    begin
      cell_s32 = packed_value[(cell_index*32) +: 32];
    end
  endfunction

  task automatic set_phase(
    input int cell_index,
    input logic [31:0] value
  );
    begin
      phase_load[(cell_index*32) +: 32] = value;
    end
  endtask

  task automatic run_tick;
    begin
      @(negedge clk);
      tick_enable = 1'b1;
      @(negedge clk);
      tick_enable = 1'b0;
      #1;
    end
  endtask

  initial begin : qualification_sequence
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    scheduler_mode = FRP_MODE_FREE;
    phase_load_valid = 1'b0;
    phase_load = '0;
    frequency_load_q16 = '0;
    gamma_effective_word = '0;
    thermal_node_factor_q30 = '0;
    auto_target_enable = 1'b0;
    external_request_valid = '0;
    external_request_cell_index = '0;
    external_request_target = '0;
    external_target_bank = '0;

    for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
      frequency_load_q16[(cell_index*32) +: 32] = FRP_M31_BASE_FREQUENCY_Q16;
      gamma_effective_word[(cell_index*32) +: 32] = FRP_M31_GAMMA_NOMINAL;
      thermal_node_factor_q30[(cell_index*32) +: 32] = FRP_M31_Q30_ONE;
    end

    repeat (3) @(negedge clk);
    rst_n = 1'b1;
    repeat (2) @(negedge clk);
    #1;

    if (state_out !== '0)
      $fatal(1, "FRP M31 TB: reset state is not active zero");
    if (pending_route_out !== '0)
      $fatal(1, "FRP M31 TB: reset pending-route bank is not zero");
    if (REQUEST_LANES != 2)
      $fatal(1, "FRP M31 TB: eight-cell_index profile must expose two lanes");

    phase_load = '0;
    set_phase(0, 32'h40000000);
    set_phase(1, 32'hC0000000);
    @(negedge clk);
    phase_load_valid = 1'b1;
    @(negedge clk);
    phase_load_valid = 1'b0;
    #1;

    if (cell_s32(phase_projection_q30, 0) !== FRP_M31_Q30_ONE)
      $fatal(1, "FRP M31 TB: positive phase projection mismatch");
    if (cell_s32(phase_projection_q30, 1) !== -FRP_M31_Q30_ONE)
      $fatal(1, "FRP M31 TB: negative phase projection mismatch");
    if (cell_state(phase_target, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M31 TB: positive resonance target mismatch");
    if (cell_state(phase_target, 1) !== FRP_STATE_NEG)
      $fatal(1, "FRP M31 TB: negative resonance target mismatch");
    if (coupling_field_q16 === '0)
      $fatal(1, "FRP M31 TB: relative-phase coupling field is empty");

    auto_target_enable = 1'b1;
    run_tick();
    if (cell_state(state_out, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M31 TB: active zero did not commit positive target");
    if (cell_state(state_out, 1) !== FRP_STATE_NEG)
      $fatal(1, "FRP M31 TB: active zero did not commit negative target");

    phase_load = phase_word_q;
    set_phase(0, 32'hC0000000);
    @(negedge clk);
    phase_load_valid = 1'b1;
    @(negedge clk);
    phase_load_valid = 1'b0;
    #1;

    run_tick();
    if (cell_state(state_out, 0) !== FRP_ACTIVE_NEUTRAL)
      $fatal(1, "FRP M31 TB: opposite polarity did not route through zero");
    if (cell_state(pending_route_out, 0) !== FRP_STATE_NEG)
      $fatal(1, "FRP M31 TB: opposite target was not retained");

    run_tick();
    if (cell_state(state_out, 0) !== FRP_STATE_NEG)
      $fatal(1, "FRP M31 TB: pending negative target did not complete");
    if (cell_state(pending_route_out, 0) !== FRP_STATE_ZERO)
      $fatal(1, "FRP M31 TB: completed pending route did not clear");

    if (temperature_proxy_q16 <= 0)
      $fatal(1, "FRP M31 TB: thermal proxy did not integrate activity");
    if (!stable)
      $fatal(1, "FRP M31 TB: qualified profile lost positive stability margin");
    if (actual_direct_events !== '0)
      $fatal(1, "FRP M31 TB: direct opposite-polarity event detected");
    if (reserved_state_events !== '0)
      $fatal(1, "FRP M31 TB: reserved state detected");
    if (queue_overflow_events !== '0)
      $fatal(1, "FRP M31 TB: pending-route overflow detected");
    if (invariant_flags !== {FRP_M31_INVARIANT_FLAGS{1'b1}})
      $fatal(1, "FRP M31 TB: inherited execution invariant failed");
    if (ticks_recorded_q !== 3)
      $fatal(1, "FRP M31 TB: integrated tick count mismatch");

    $display("FRP_M31_COMPLETE_RTL: PASS");
    $display("phase/coherence/resonance/active-zero/thermal/stability: PASS");
    $finish;
  end

endmodule

`endif
