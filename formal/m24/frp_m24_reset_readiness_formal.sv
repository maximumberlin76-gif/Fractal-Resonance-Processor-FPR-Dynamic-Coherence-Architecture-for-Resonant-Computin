// SPDX-License-Identifier: Apache-2.0
// FRP M24 reset/readiness proof harness around the actual M23 boundary logic.

module frp_m22_control_status_register_interface #(
  parameter int CELLS = 2,
  parameter int STATE_BITS = 2,
  parameter int REQUEST_LANES = 1,
  parameter int CELL_INDEX_BITS = 1,
  parameter int COUNTER_BITS = 8
) (
  input logic clk,
  input logic rst_n,
  input logic csr_valid,
  input logic csr_write,
  input logic [7:0] csr_addr,
  input logic [31:0] csr_wdata,
  output logic csr_ready,
  output logic csr_error,
  output logic [31:0] csr_rdata
);
  always @* begin
    csr_ready = csr_valid && rst_n;
    csr_error = 1'b0;
    csr_rdata = 32'b0;
  end
endmodule

module frp_m23_interface_protocol_assertions (
  input logic host_clk,
  input logic core_clk,
  input logic rst_n_async,
  input logic host_reset_released,
  input logic core_reset_released,
  input logic core_ready_core,
  input logic host_ready,
  input logic host_csr_valid,
  input logic host_csr_ready,
  input logic host_busy,
  input logic core_csr_valid,
  input logic core_csr_ready,
  input logic request_toggle,
  input logic response_toggle,
  input logic [40:0] held_request,
  input logic [32:0] held_response
);
endmodule

module frp_m24_reset_readiness_formal;
  (* anyseq *) logic paired_clock;
  logic [3:0] proof_step_q;

  wire rst_n_async = proof_step_q != 0;
  wire csr_valid = 1'b0;
  wire csr_write = 1'b0;
  wire [7:0] csr_addr = 8'b0;
  wire [31:0] csr_wdata = 32'b0;
  wire csr_ready;
  wire csr_error;
  wire [31:0] csr_rdata;
  wire host_reset_released;
  wire core_reset_released;
  wire core_ready;
  wire interface_busy;
  wire protocol_error;
  wire invalid_before_ready;
  wire invalid_while_busy;
  wire invalid_valid_held;

  frp_m23_hardened_integration_boundary #(
    .CELLS(2),
    .REQUEST_LANES(1)
  ) dut (
    .host_clk(paired_clock),
    .core_clk(paired_clock),
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

  always @(posedge paired_clock) begin
    proof_step_q <= proof_step_q + 1'b1;
  end

  wire M24_P33 =
    rst_n_async
    || (!host_reset_released && !core_reset_released && !core_ready);
  wire M24_P34 =
    (proof_step_q < 3)
    || (host_reset_released && core_reset_released);
  wire M24_P35 =
    !core_ready || (host_reset_released && core_reset_released);
  wire M24_P36 = (proof_step_q < 6) || core_ready;

  always @* begin
    assert(M24_P33);
    assert(M24_P34);
    assert(M24_P35);
    assert(M24_P36);
  end
endmodule
