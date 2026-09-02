// SPDX-License-Identifier: Apache-2.0
// FRP M31 integrated retained-phase, active-zero and thermal RTL contour.

`ifndef FRP_M31_CORE_SV
`define FRP_M31_CORE_SV

`timescale 1ns / 1ps

`include "frp_m31_execution_core.sv"
`include "frp_m31_phase_interference.sv"
`include "frp_m31_phase_request_adapter.sv"
`include "frp_m31_thermal_proxy.sv"
`include "frp_m31_stability.sv"

module frp_m31_core #(
  parameter int CELLS = 8,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS,
  parameter string SIN_LUT_FILE = "rtl/m31/frp_m31_sin_q30.mem"
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic clear_counters,
  input frp_m31_pkg::frp_m31_scheduler_mode_e scheduler_mode,

  input logic phase_load_valid,
  input logic [(CELLS*32)-1:0] phase_load,
  input logic [(CELLS*32)-1:0] frequency_load_q16,
  input logic [(CELLS*32)-1:0] gamma_effective_word,
  input logic [(CELLS*32)-1:0] thermal_node_factor_q30,

  input logic auto_target_enable,
  input logic [REQUEST_LANES-1:0] external_request_valid,
  input logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] external_request_cell_index,
  input logic [(REQUEST_LANES*2)-1:0] external_request_target,
  input logic [(CELLS*2)-1:0] external_target_bank,

  output logic [(CELLS*32)-1:0] phase_word_q,
  output logic [(CELLS*32)-1:0] frequency_current_q16,
  output logic [(CELLS*32)-1:0] coupling_field_q16,
  output logic [(CELLS*32)-1:0] phase_projection_q30,
  output logic [(CELLS*2)-1:0] phase_target,
  output logic [(CELLS*2)-1:0] state_out,
  output logic [(CELLS*2)-1:0] pending_route_out,

  output frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state_q,
  output logic [COUNTER_BITS-1:0] ticks_recorded_q,
  output logic [CELLS-1:0] accepted_change_mask,
  output logic [COUNTER_BITS-1:0] accepted_changes,
  output logic [COUNTER_BITS-1:0] switch_load_numerator,
  output logic [COUNTER_BITS-1:0] actual_direct_events,
  output logic [COUNTER_BITS-1:0] reserved_state_events,
  output logic [COUNTER_BITS-1:0] queue_overflow_events,
  output logic [frp_m31_pkg::FRP_M31_INVARIANT_FLAGS-1:0] invariant_flags,

  output logic signed [31:0] pair_coherence_q30,
  output logic signed [31:0] cluster_coherence_q30,
  output logic signed [31:0] global_coherence_q30,
  output logic signed [31:0] organization_dispersion_q30,
  output logic signed [31:0] temperature_proxy_q16,
  output logic signed [31:0] peak_temperature_proxy_q16,
  output logic signed [31:0] coherence_capacity_q16,
  output logic signed [31:0] pressure_q16,
  output logic signed [31:0] stability_margin_q16,
  output logic stable
);

  import frp_m31_pkg::*;
  import frp_m31_fixed_point_pkg::*;

  logic [REQUEST_LANES-1:0] phase_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] phase_request_cell_index;
  logic [(REQUEST_LANES*2)-1:0] phase_request_target;
  logic [REQUEST_LANES-1:0] selected_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] selected_request_cell_index;
  logic [(REQUEST_LANES*2)-1:0] selected_request_target;
  logic [(CELLS*2)-1:0] selected_target_bank;

  frp_m31_scheduler_mode_e scheduler_mode_q_unused;
  logic [COUNTER_BITS-1:0] scheduler_count_free_q_unused;
  logic [COUNTER_BITS-1:0] scheduler_count_balance_q_unused;
  logic [COUNTER_BITS-1:0] scheduler_count_commit_q_unused;
  logic [COUNTER_BITS-1:0] scheduler_count_excite_q_unused;
  logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q_unused;
  logic [REQUEST_LANES-1:0] request_accept_unused;
  logic [REQUEST_LANES-1:0] request_reject_unused;
  logic [CELLS-1:0] accepted_cell_mask_unused;
  logic [CELLS-1:0] neutral_routed_cell_mask_unused;
  logic [COUNTER_BITS-1:0] capacity_remaining_unused;
  logic capacity_exhausted_unused;
  logic [COUNTER_BITS-1:0] requested_direct_events_unused;
  logic [COUNTER_BITS-1:0] prevented_direct_events_unused;
  logic [COUNTER_BITS-1:0] neutral_routed_events_unused;

  logic signed [31:0] normalized_cycle_cost_q16;
  logic [63:0] normalized_cycle_cost_wide;
  logic [31:0] thermal_sample_count_unused;

  frp_m31_phase_request_adapter #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS)
  ) u_phase_request_adapter (
    .enable(auto_target_enable),
    .retained_state(state_out),
    .pending_route(pending_route_out),
    .phase_target(phase_target),
    .scheduler_state(scheduler_state_q),
    .request_valid(phase_request_valid),
    .request_cell_index(phase_request_cell_index),
    .request_target(phase_request_target)
  );

  always_comb begin
    if (auto_target_enable) begin
      selected_request_valid = phase_request_valid;
      selected_request_cell_index = phase_request_cell_index;
      selected_request_target = phase_request_target;
      selected_target_bank = phase_target;
    end else begin
      selected_request_valid = external_request_valid;
      selected_request_cell_index = external_request_cell_index;
      selected_request_target = external_request_target;
      selected_target_bank = external_target_bank;
    end

    normalized_cycle_cost_wide = switch_load_numerator;
    normalized_cycle_cost_wide = normalized_cycle_cost_wide << 16;
    normalized_cycle_cost_q16 =
      (normalized_cycle_cost_wide + (CELLS / 2)) / CELLS;
  end

  frp_m31_execution_core #(
    .CELLS(CELLS),
    .STATE_BITS(2),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_execution (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .request_valid(selected_request_valid),
    .request_cell_index(selected_request_cell_index),
    .request_target(selected_request_target),
    .target_q(selected_target_bank),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .scheduler_mode_q(scheduler_mode_q_unused),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q_unused),
    .scheduler_count_balance_q(scheduler_count_balance_q_unused),
    .scheduler_count_commit_q(scheduler_count_commit_q_unused),
    .scheduler_count_excite_q(scheduler_count_excite_q_unused),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q_unused),
    .request_accept(request_accept_unused),
    .request_reject(request_reject_unused),
    .accepted_cell_mask(accepted_cell_mask_unused),
    .neutral_routed_cell_mask(neutral_routed_cell_mask_unused),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .capacity_remaining(capacity_remaining_unused),
    .capacity_exhausted(capacity_exhausted_unused),
    .switch_load_numerator(switch_load_numerator),
    .requested_direct_events(requested_direct_events_unused),
    .prevented_direct_events(prevented_direct_events_unused),
    .neutral_routed_events(neutral_routed_events_unused),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags)
  );

  frp_m31_phase_interference #(
    .CELLS(CELLS),
    .SIN_LUT_FILE(SIN_LUT_FILE)
  ) u_phase_interference (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .load_valid(phase_load_valid),
    .phase_load(phase_load),
    .frequency_load_q16(frequency_load_q16),
    .gamma_effective_word(gamma_effective_word),
    .thermal_node_factor_q30(thermal_node_factor_q30),
    .retained_state(state_out),
    .switch_activity(accepted_change_mask),
    .scheduler_state(scheduler_state_q),
    .phase_word_q(phase_word_q),
    .frequency_current_q16(frequency_current_q16),
    .coupling_field_q16(coupling_field_q16),
    .phase_projection_q30(phase_projection_q30),
    .phase_target(phase_target),
    .pair_coherence_q30(pair_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .global_coherence_q30(global_coherence_q30),
    .organization_dispersion_q30(organization_dispersion_q30)
  );

  frp_m31_thermal_proxy u_thermal_proxy (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear(clear_counters),
    .normalized_cycle_cost_q16(normalized_cycle_cost_q16),
    .temperature_proxy_q16(temperature_proxy_q16),
    .peak_temperature_proxy_q16(peak_temperature_proxy_q16),
    .sample_count_q(thermal_sample_count_unused)
  );

  frp_m31_stability #(
    .CELLS(CELLS)
  ) u_stability (
    .retained_state(state_out),
    .global_coherence_q30(global_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .temperature_proxy_q16(temperature_proxy_q16),
    .switch_load_q16(normalized_cycle_cost_q16),
    .coherence_capacity_q16(coherence_capacity_q16),
    .pressure_q16(pressure_q16),
    .stability_margin_q16(stability_margin_q16),
    .stable(stable)
  );

endmodule

`endif
