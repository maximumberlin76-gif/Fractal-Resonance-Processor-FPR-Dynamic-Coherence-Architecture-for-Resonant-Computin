// SPDX-License-Identifier: Apache-2.0
// FRP M23 single-outstanding CSR request/response CDC bridge.

`ifndef FRP_M23_CSR_CDC_BRIDGE_SV
`define FRP_M23_CSR_CDC_BRIDGE_SV

module frp_m23_csr_cdc_bridge (
  input  logic        host_clk,
  input  logic        host_rst_n,
  input  logic        host_ready,
  input  logic        host_csr_valid,
  input  logic        host_csr_write,
  input  logic [7:0]  host_csr_addr,
  input  logic [31:0] host_csr_wdata,
  output logic        host_csr_ready,
  output logic        host_csr_error,
  output logic [31:0] host_csr_rdata,
  output logic        host_busy,
  output logic        invalid_before_ready,
  output logic        invalid_while_busy,
  output logic        invalid_valid_held,
  output logic        protocol_error,

  input  logic        core_clk,
  input  logic        core_rst_n,
  input  logic        core_ready,
  output logic        core_csr_valid,
  output logic        core_csr_write,
  output logic [7:0]  core_csr_addr,
  output logic [31:0] core_csr_wdata,
  input  logic        core_csr_ready,
  input  logic        core_csr_error,
  input  logic [31:0] core_csr_rdata,

  output logic        request_toggle_debug,
  output logic        response_toggle_debug,
  output logic [40:0] held_request_debug,
  output logic [32:0] held_response_debug
);

  logic request_toggle_host_q;
  logic request_valid_previous_q;
  logic request_write_hold_q;
  logic [7:0] request_addr_hold_q;
  logic [31:0] request_wdata_hold_q;

  (* ASYNC_REG = "TRUE" *) logic [1:0] request_toggle_core_sync_q;
  logic request_toggle_core_seen_q;
  logic response_toggle_core_q;
  logic response_error_hold_q;
  logic [31:0] response_rdata_hold_q;

  (* ASYNC_REG = "TRUE" *) logic [1:0] response_toggle_host_sync_q;
  logic response_toggle_host_seen_q;

  always_ff @(posedge host_clk or negedge host_rst_n) begin
    if (!host_rst_n) begin
      request_toggle_host_q <= 1'b0;
      request_valid_previous_q <= 1'b0;
      request_write_hold_q <= 1'b0;
      request_addr_hold_q <= '0;
      request_wdata_hold_q <= '0;
      response_toggle_host_sync_q <= 2'b00;
      response_toggle_host_seen_q <= 1'b0;
      host_csr_ready <= 1'b0;
      host_csr_error <= 1'b0;
      host_csr_rdata <= '0;
      host_busy <= 1'b0;
      invalid_before_ready <= 1'b0;
      invalid_while_busy <= 1'b0;
      invalid_valid_held <= 1'b0;
    end else begin
      response_toggle_host_sync_q <= {
        response_toggle_host_sync_q[0], response_toggle_core_q
      };
      host_csr_ready <= 1'b0;
      request_valid_previous_q <= host_csr_valid;

      if (host_csr_valid && request_valid_previous_q) begin
        invalid_valid_held <= 1'b1;
      end

      if (host_csr_valid) begin
        if (!host_ready) begin
          invalid_before_ready <= 1'b1;
        end else if (host_busy) begin
          invalid_while_busy <= 1'b1;
        end else if (!request_valid_previous_q) begin
          request_write_hold_q <= host_csr_write;
          request_addr_hold_q <= host_csr_addr;
          request_wdata_hold_q <= host_csr_wdata;
          request_toggle_host_q <= ~request_toggle_host_q;
          host_busy <= 1'b1;
        end
      end

      if (response_toggle_host_sync_q[1] != response_toggle_host_seen_q) begin
        response_toggle_host_seen_q <= response_toggle_host_sync_q[1];
        host_csr_ready <= 1'b1;
        host_csr_error <= response_error_hold_q;
        host_csr_rdata <= response_rdata_hold_q;
        host_busy <= 1'b0;
      end
    end
  end

  always_ff @(posedge core_clk or negedge core_rst_n) begin
    if (!core_rst_n) begin
      request_toggle_core_sync_q <= 2'b00;
      request_toggle_core_seen_q <= 1'b0;
      response_toggle_core_q <= 1'b0;
      response_error_hold_q <= 1'b0;
      response_rdata_hold_q <= '0;
      core_csr_valid <= 1'b0;
      core_csr_write <= 1'b0;
      core_csr_addr <= '0;
      core_csr_wdata <= '0;
    end else begin
      request_toggle_core_sync_q <= {
        request_toggle_core_sync_q[0], request_toggle_host_q
      };

      if (
        !core_csr_valid
        && core_ready
        && (request_toggle_core_sync_q[1] != request_toggle_core_seen_q)
      ) begin
        request_toggle_core_seen_q <= request_toggle_core_sync_q[1];
        core_csr_write <= request_write_hold_q;
        core_csr_addr <= request_addr_hold_q;
        core_csr_wdata <= request_wdata_hold_q;
        core_csr_valid <= 1'b1;
      end

      if (core_csr_valid && core_csr_ready) begin
        response_error_hold_q <= core_csr_error;
        response_rdata_hold_q <= core_csr_rdata;
        response_toggle_core_q <= ~response_toggle_core_q;
        core_csr_valid <= 1'b0;
      end
    end
  end

  assign protocol_error =
    invalid_before_ready || invalid_while_busy || invalid_valid_held;
  assign request_toggle_debug = request_toggle_host_q;
  assign response_toggle_debug = response_toggle_core_q;
  assign held_request_debug = {
    request_write_hold_q, request_addr_hold_q, request_wdata_hold_q
  };
  assign held_response_debug = {response_error_hold_q, response_rdata_hold_q};

endmodule : frp_m23_csr_cdc_bridge

`endif
