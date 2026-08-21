// SPDX-License-Identifier: Apache-2.0
// FRP M26 synthesis-only replacement for the executable M23 assertion monitor.
// The monitor has no functional outputs and is qualified separately by M24.

`ifndef FRP_M23_INTERFACE_PROTOCOL_ASSERTIONS_SV
`define FRP_M23_INTERFACE_PROTOCOL_ASSERTIONS_SV

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
endmodule : frp_m23_interface_protocol_assertions

`endif
