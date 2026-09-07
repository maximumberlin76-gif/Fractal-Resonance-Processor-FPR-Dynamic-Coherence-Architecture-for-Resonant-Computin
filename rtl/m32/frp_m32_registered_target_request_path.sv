// SPDX-License-Identifier: Apache-2.0
// FRP M32 registered phase-target to request-formation path.

`ifndef FRP_M32_REGISTERED_TARGET_REQUEST_PATH_SV
`define FRP_M32_REGISTERED_TARGET_REQUEST_PATH_SV

`timescale 1ns / 1ps

`include "frp_m32_registered_target_boundary.sv"
`include "frp_m31_phase_request_adapter.sv"

module frp_m32_registered_target_request_path #(
  parameter int CELLS = frp_m31_pkg::FRP_M31_DEFAULT_CELLS,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m31_pkg::FRP_M31_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,
  input logic tick_enable,
  input logic clear_counters,

  input logic phase_target_valid,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] phase_target_source,

  input logic auto_target_enable,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] retained_state,
  input logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] pending_route,
  input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,

  output logic [
    (CELLS*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] registered_target_q,
  output logic registered_target_valid_q,
  output logic phase_target_domain_valid,
  output logic registered_target_domain_valid,
  output logic capture_accepted,
  output logic capture_rejected,
  output logic [COUNTER_BITS-1:0] accepted_capture_events_q,
  output logic [COUNTER_BITS-1:0] rejected_capture_events_q,
  output logic registered_request_enable,

  output logic [REQUEST_LANES-1:0] phase_request_valid,
  output logic [
    (REQUEST_LANES*CELL_INDEX_BITS)-1:0
  ] phase_request_cell_index,
  output logic [
    (REQUEST_LANES*frp_m31_pkg::FRP_M31_STATE_BITS)-1:0
  ] phase_request_target
);

  frp_m32_registered_target_boundary #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_registered_target_boundary (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .phase_target_valid(phase_target_valid),
    .phase_target(phase_target_source),
    .registered_target_q(registered_target_q),
    .registered_target_valid_q(registered_target_valid_q),
    .phase_target_domain_valid(phase_target_domain_valid),
    .registered_target_domain_valid(registered_target_domain_valid),
    .capture_accepted(capture_accepted),
    .capture_rejected(capture_rejected),
    .accepted_capture_events_q(accepted_capture_events_q),
    .rejected_capture_events_q(rejected_capture_events_q)
  );

  always_comb begin
    registered_request_enable =
      auto_target_enable
      && registered_target_valid_q
      && registered_target_domain_valid;
  end

  frp_m31_phase_request_adapter #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS)
  ) u_phase_request_adapter (
    .enable(registered_request_enable),
    .retained_state(retained_state),
    .pending_route(pending_route),
    .phase_target(registered_target_q),
    .scheduler_state(scheduler_state),
    .request_valid(phase_request_valid),
    .request_cell_index(phase_request_cell_index),
    .request_target(phase_request_target)
  );

endmodule

`endif
