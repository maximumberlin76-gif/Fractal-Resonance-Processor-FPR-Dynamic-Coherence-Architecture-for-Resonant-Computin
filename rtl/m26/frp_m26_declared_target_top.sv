// SPDX-License-Identifier: Apache-2.0
// FRP M26 declared-target synthesis top for iCE40-HX8K-CT256 evidence.

`ifndef FRP_M26_DECLARED_TARGET_TOP_SV
`define FRP_M26_DECLARED_TARGET_TOP_SV

`include "frp_m26_protocol_monitor_synthesis_stub.sv"
`include "frp_m23_hardened_integration_boundary.sv"

module frp_m26_declared_target_top (
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

  localparam int M26_CELLS = 8;
  localparam int M26_REQUEST_LANES = 2;

  frp_m23_hardened_integration_boundary #(
    .CELLS(M26_CELLS),
    .REQUEST_LANES(M26_REQUEST_LANES)
  ) implementation_boundary (
    .host_clk(host_clk),
    .core_clk(core_clk),
    .rst_n_async(rst_n_async),
    .csr_valid(csr_valid),
    .csr_write(csr_write),
    .csr_addr(csr_addr),
    .csr_wdata(csr_wdata),
    .csr_ready(csr_ready),
    .csr_error(csr_error),
    .csr_rdata(csr_rdata),
    .host_reset_released(host_reset_released),
    .core_reset_released(core_reset_released),
    .core_ready(core_ready),
    .interface_busy(interface_busy),
    .protocol_error(protocol_error),
    .invalid_before_ready(invalid_before_ready),
    .invalid_while_busy(invalid_while_busy),
    .invalid_valid_held(invalid_valid_held)
  );

endmodule : frp_m26_declared_target_top

`endif
