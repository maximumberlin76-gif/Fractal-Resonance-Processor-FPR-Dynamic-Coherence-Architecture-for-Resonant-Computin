// SPDX-License-Identifier: Apache-2.0
// FRP M23 executable integration-boundary protocol assertions.

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

  logic host_reset_released_q;
  logic core_reset_released_q;
  logic request_toggle_q;
  logic response_toggle_q;
  logic [40:0] held_request_q;
  logic [32:0] held_response_q;

  always_ff @(posedge host_clk or negedge rst_n_async) begin
    if (!rst_n_async) begin
      host_reset_released_q <= 1'b0;
      request_toggle_q <= 1'b0;
      held_request_q <= '0;
    end else begin
      assert (host_reset_released || !host_reset_released_q)
        else $error("M23_A01_HOST_RESET_MONOTONIC");
      assert (!host_ready || host_reset_released)
        else $error("M23_A03_HOST_READY_AFTER_HOST_RESET");
      assert (!host_csr_ready || !host_busy)
        else $error("M23_A06_RESPONSE_CLEARS_BUSY");
      assert (!((request_toggle != request_toggle_q) && !host_ready))
        else $error("M23_A07_REQUEST_REQUIRES_READY");
      if (host_busy && !(request_toggle != request_toggle_q)) begin
        assert (held_request == held_request_q)
          else $error("M23_A08_REQUEST_PAYLOAD_STABLE");
      end
      assert (!host_csr_ready || host_ready)
        else $error("M23_A12_HOST_RESPONSE_AFTER_READY");
      host_reset_released_q <= host_reset_released;
      request_toggle_q <= request_toggle;
      held_request_q <= held_request;
    end
  end

  always_ff @(posedge core_clk or negedge rst_n_async) begin
    if (!rst_n_async) begin
      core_reset_released_q <= 1'b0;
      response_toggle_q <= 1'b0;
      held_response_q <= '0;
    end else begin
      assert (core_reset_released || !core_reset_released_q)
        else $error("M23_A02_CORE_RESET_MONOTONIC");
      assert (!core_ready_core || core_reset_released)
        else $error("M23_A04_CORE_READY_AFTER_CORE_RESET");
      assert (!core_csr_valid || core_ready_core)
        else $error("M23_A05_CORE_REQUEST_AFTER_READY");
      assert (!core_csr_ready || core_csr_valid)
        else $error("M23_A09_CORE_RESPONSE_REQUIRES_REQUEST");
      if (response_toggle == response_toggle_q) begin
        assert (held_response == held_response_q)
          else $error("M23_A10_RESPONSE_PAYLOAD_STABLE");
      end
      assert (!((response_toggle != response_toggle_q) && !core_ready_core))
        else $error("M23_A11_RESPONSE_TOGGLE_AFTER_CORE_READY");
      core_reset_released_q <= core_reset_released;
      response_toggle_q <= response_toggle;
      held_response_q <= held_response;
    end
  end

endmodule : frp_m23_interface_protocol_assertions

`endif
