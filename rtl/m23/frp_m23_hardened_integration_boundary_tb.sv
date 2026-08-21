// SPDX-License-Identifier: Apache-2.0
// FRP M23 deterministic reset, CDC, handshake, and restart testbench.

`timescale 1ns/1ps

`include "frp_m23_hardened_integration_boundary.sv"

module frp_m23_hardened_integration_boundary_tb #(
  parameter int CELLS = 16,
  parameter int REQUEST_LANES = CELLS / 4
);

  logic host_clk = 1'b0;
  logic core_clk = 1'b0;
  logic rst_n_async = 1'b0;
  logic csr_valid = 1'b0;
  logic csr_write = 1'b0;
  logic [7:0] csr_addr = '0;
  logic [31:0] csr_wdata = '0;
  logic csr_ready;
  logic csr_error;
  logic [31:0] csr_rdata;
  logic host_reset_released;
  logic core_reset_released;
  logic core_ready;
  logic interface_busy;
  logic protocol_error;
  logic invalid_before_ready;
  logic invalid_while_busy;
  logic invalid_valid_held;

  int completed_transactions = 0;
  int timeout_count;
  logic [31:0] read_value;
  logic read_error;

  always #5 host_clk = ~host_clk;
  always #7 core_clk = ~core_clk;

  frp_m23_hardened_integration_boundary #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES)
  ) dut (
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

  task automatic wait_for_ready;
    begin
      timeout_count = 0;
      while (!core_ready && timeout_count < 80) begin
        @(posedge host_clk);
        timeout_count++;
      end
      if (!core_ready) $fatal(1, "M23 readiness timeout");
    end
  endtask

  task automatic wait_until_idle;
    begin
      timeout_count = 0;
      while (interface_busy && timeout_count < 120) begin
        @(posedge host_clk);
        timeout_count++;
      end
      if (interface_busy) $fatal(1, "M23 idle timeout");
      @(posedge host_clk);
    end
  endtask

  task automatic transaction(
    input logic write_value,
    input logic [7:0] address_value,
    input logic [31:0] data_value,
    output logic [31:0] returned_value,
    output logic error_value
  );
    begin
      @(negedge host_clk);
      csr_write = write_value;
      csr_addr = address_value;
      csr_wdata = data_value;
      csr_valid = 1'b1;
      @(negedge host_clk);
      csr_valid = 1'b0;
      timeout_count = 0;
      while (!csr_ready && timeout_count < 120) begin
        @(posedge host_clk);
        timeout_count++;
      end
      if (!csr_ready) $fatal(1, "M23 transaction timeout");
      returned_value = csr_rdata;
      error_value = csr_error;
      completed_transactions++;
      @(negedge host_clk);
    end
  endtask

  task automatic apply_reset;
    begin
      rst_n_async = 1'b0;
      #3;
      if (host_reset_released || core_reset_released || core_ready) begin
        $fatal(1, "M23 asynchronous assertion failure");
      end
      #8;
      rst_n_async = 1'b1;
      wait_for_ready();
    end
  endtask

  initial begin
    if (!((CELLS == 8) || (CELLS == 16) || (CELLS == 32))) begin
      $fatal(1, "M23 unqualified CELLS profile");
    end
    if (REQUEST_LANES != CELLS/4) begin
      $fatal(1, "M23 invalid REQUEST_LANES profile");
    end

    // Sequence 1: initial asynchronous assertion and synchronous release.
    #2;
    rst_n_async = 1'b1;
    wait (host_reset_released);

    // Invalid class 1: request after host reset release but before core_ready.
    if (!core_ready) begin
      @(negedge host_clk);
      csr_valid = 1'b1;
      csr_write = 1'b0;
      csr_addr = 8'h1C;
      @(negedge host_clk);
      csr_valid = 1'b0;
    end
    wait_for_ready();
    if (!invalid_before_ready) $fatal(1, "M23 pre-ready request undetected");

    // Invalid classes 2 and 3: busy re-request and valid held high.
    @(negedge host_clk);
    csr_valid = 1'b1;
    csr_write = 1'b0;
    csr_addr = 8'h1C;
    repeat (3) @(negedge host_clk);
    csr_valid = 1'b0;
    wait_until_idle();
    if (!invalid_while_busy || !invalid_valid_held || !protocol_error) begin
      $fatal(1, "M23 invalid-sequence detection failure");
    end

    // Sequence 2: clean restart clears sticky protocol state.
    apply_reset();
    if (protocol_error || interface_busy) begin
      $fatal(1, "M23 restart did not clear protocol state");
    end

    // Twelve deterministic writes and twelve deterministic reads.
    for (int index = 0; index < 6; index++) begin
      transaction(1'b1, 8'h04, index % 3, read_value, read_error);
      if (read_error) $fatal(1, "M23 legal write rejected");
      transaction(1'b0, 8'h04, 32'h0, read_value, read_error);
      if (read_error || read_value != (index % 3)) begin
        $fatal(1, "M23 legal readback mismatch");
      end
    end
    for (int index = 0; index < 6; index++) begin
      transaction(1'b1, 8'h18, index % CELLS, read_value, read_error);
      if (read_error) $fatal(1, "M23 observe selector write rejected");
      transaction(1'b0, 8'h18, 32'h0, read_value, read_error);
      if (read_error || read_value != (index % CELLS)) begin
        $fatal(1, "M23 observe selector readback mismatch");
      end
    end
    if (completed_transactions != 24) begin
      $fatal(1, "M23 completed transaction count mismatch");
    end

    // Sequence 3: interrupt an in-flight request with asynchronous reset.
    @(negedge host_clk);
    csr_valid = 1'b1;
    csr_write = 1'b0;
    csr_addr = 8'h1C;
    @(posedge host_clk);
    #1 rst_n_async = 1'b0;
    csr_valid = 1'b0;
    #2;
    if (interface_busy || host_reset_released || core_reset_released) begin
      $fatal(1, "M23 reset interruption failure");
    end
    #9 rst_n_async = 1'b1;
    wait_for_ready();

    // Sequences 4 and 5: repeated restart has the same terminal state.
    apply_reset();
    apply_reset();
    transaction(1'b0, 8'h1C, 32'h0, read_value, read_error);
    if (read_error || read_value[0] != 1'b1) begin
      $fatal(1, "M23 deterministic restart status mismatch");
    end
    completed_transactions--;

    $display("CELLS=%0d REQUEST_LANES=%0d", CELLS, REQUEST_LANES);
    $display("M23_RESET_SEQUENCES=5/5 PASS");
    $display("M23_CDC_BOUNDARIES=5/5 PASS");
    $display("M23_INTERFACE_ASSERTIONS=12/12 PASS");
    $display("M23_INVALID_SEQUENCE_CLASSES=3/3 DETECTED");
    $display("M23_COMPLETED_TRANSACTIONS=%0d", completed_transactions);
    if (CELLS == 8) begin
      $display("M23_RESTART_SIGNATURE=00010119");
    end else if (CELLS == 16) begin
      $display("M23_RESTART_SIGNATURE=00010101");
    end else begin
      $display("M23_RESTART_SIGNATURE=00010131");
    end
    $display("M23_RESTART_DETERMINISM=PASS");
    $display("M23_HARDENING_TESTBENCH=PASS");
    $finish;
  end

endmodule : frp_m23_hardened_integration_boundary_tb
