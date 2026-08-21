// SPDX-License-Identifier: Apache-2.0
// FRP M23 hardened dual-clock integration boundary around the M22 CSR target.

`ifndef FRP_M23_HARDENED_INTEGRATION_BOUNDARY_SV
`define FRP_M23_HARDENED_INTEGRATION_BOUNDARY_SV

`include "frp_m23_reset_release_sync.sv"
`include "frp_m23_csr_cdc_bridge.sv"
`include "frp_m23_interface_protocol_assertions.sv"
`include "frp_m22_control_status_register_interface.sv"

module frp_m23_hardened_integration_boundary #(
  parameter int CELLS = frp_m16_pkg::FRP_M16_DEFAULT_CELLS,
  parameter int REQUEST_LANES = frp_m16_pkg::frp_calc_request_lanes(CELLS)
) (
  input  logic        host_clk,
  input  logic        core_clk,
  input  logic        rst_n_async,
  input  logic        csr_valid,
  input  logic        csr_write,
  input  logic [7:0]  csr_addr,
  input  logic [31:0] csr_wdata,
  output logic        csr_ready,
  output logic        csr_error,
  output logic [31:0] csr_rdata,
  output logic        host_reset_released,
  output logic        core_reset_released,
  output logic        core_ready,
  output logic        interface_busy,
  output logic        protocol_error,
  output logic        invalid_before_ready,
  output logic        invalid_while_busy,
  output logic        invalid_valid_held
);

  logic core_ready_core_q;
  (* ASYNC_REG = "TRUE" *) logic [1:0] core_ready_host_sync_q;

  logic core_csr_valid;
  logic core_csr_write;
  logic [7:0] core_csr_addr;
  logic [31:0] core_csr_wdata;
  logic core_csr_ready;
  logic core_csr_error;
  logic [31:0] core_csr_rdata;
  logic request_toggle_debug;
  logic response_toggle_debug;
  logic [40:0] held_request_debug;
  logic [32:0] held_response_debug;

  frp_m23_reset_release_sync host_reset_sync (
    .clk(host_clk),
    .rst_n_async(rst_n_async),
    .rst_n_sync(host_reset_released)
  );

  frp_m23_reset_release_sync core_reset_sync (
    .clk(core_clk),
    .rst_n_async(rst_n_async),
    .rst_n_sync(core_reset_released)
  );

  always_ff @(posedge core_clk or negedge core_reset_released) begin
    if (!core_reset_released) begin
      core_ready_core_q <= 1'b0;
    end else begin
      core_ready_core_q <= 1'b1;
    end
  end

  always_ff @(posedge host_clk or negedge host_reset_released) begin
    if (!host_reset_released) begin
      core_ready_host_sync_q <= 2'b00;
    end else begin
      core_ready_host_sync_q <= {
        core_ready_host_sync_q[0], core_ready_core_q
      };
    end
  end

  assign core_ready = host_reset_released && core_ready_host_sync_q[1];

  frp_m23_csr_cdc_bridge cdc_bridge (
    .host_clk(host_clk),
    .host_rst_n(host_reset_released),
    .host_ready(core_ready),
    .host_csr_valid(csr_valid),
    .host_csr_write(csr_write),
    .host_csr_addr(csr_addr),
    .host_csr_wdata(csr_wdata),
    .host_csr_ready(csr_ready),
    .host_csr_error(csr_error),
    .host_csr_rdata(csr_rdata),
    .host_busy(interface_busy),
    .invalid_before_ready(invalid_before_ready),
    .invalid_while_busy(invalid_while_busy),
    .invalid_valid_held(invalid_valid_held),
    .protocol_error(protocol_error),
    .core_clk(core_clk),
    .core_rst_n(core_reset_released),
    .core_ready(core_ready_core_q),
    .core_csr_valid(core_csr_valid),
    .core_csr_write(core_csr_write),
    .core_csr_addr(core_csr_addr),
    .core_csr_wdata(core_csr_wdata),
    .core_csr_ready(core_csr_ready),
    .core_csr_error(core_csr_error),
    .core_csr_rdata(core_csr_rdata),
    .request_toggle_debug(request_toggle_debug),
    .response_toggle_debug(response_toggle_debug),
    .held_request_debug(held_request_debug),
    .held_response_debug(held_response_debug)
  );

  frp_m22_control_status_register_interface #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES)
  ) csr_target (
    .clk(core_clk),
    .rst_n(core_reset_released),
    .csr_valid(core_csr_valid),
    .csr_write(core_csr_write),
    .csr_addr(core_csr_addr),
    .csr_wdata(core_csr_wdata),
    .csr_ready(core_csr_ready),
    .csr_error(core_csr_error),
    .csr_rdata(core_csr_rdata)
  );

  frp_m23_interface_protocol_assertions protocol_assertions (
    .host_clk(host_clk),
    .core_clk(core_clk),
    .rst_n_async(rst_n_async),
    .host_reset_released(host_reset_released),
    .core_reset_released(core_reset_released),
    .core_ready_core(core_ready_core_q),
    .host_ready(core_ready),
    .host_csr_valid(csr_valid),
    .host_csr_ready(csr_ready),
    .host_busy(interface_busy),
    .core_csr_valid(core_csr_valid),
    .core_csr_ready(core_csr_ready),
    .request_toggle(request_toggle_debug),
    .response_toggle(response_toggle_debug),
    .held_request(held_request_debug),
    .held_response(held_response_debug)
  );

endmodule : frp_m23_hardened_integration_boundary

`endif
