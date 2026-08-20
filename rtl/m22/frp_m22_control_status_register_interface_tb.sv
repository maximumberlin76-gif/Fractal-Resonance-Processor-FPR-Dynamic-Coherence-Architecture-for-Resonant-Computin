// SPDX-License-Identifier: Apache-2.0
//
// FRP M22 executable control, status, and register interface testbench.

`timescale 1ns / 1ps

`include "frp_m22_control_status_register_interface.sv"

module frp_m22_control_status_register_interface_tb #(
  parameter int CELLS = 16,
  parameter int REQUEST_LANES = frp_m16_pkg::frp_calc_request_lanes(CELLS),
  parameter int STATE_BITS = frp_m16_pkg::FRP_M16_STATE_BITS,
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m16_pkg::FRP_M16_COUNTER_BITS
);

  import frp_m16_pkg::*;
  import frp_m22_csr_pkg::*;

  localparam frp_m22_csr_data_t CSR_MODE_FREE = 32'h00000000;
  localparam frp_m22_csr_data_t CSR_MODE_7_1 = 32'h00000001;
  localparam frp_m22_csr_data_t CSR_MODE_1_7 = 32'h00000002;
  localparam frp_m22_csr_data_t CSR_MODE_RESERVED = 32'h00000003;
  localparam frp_m22_csr_data_t CSR_STATE_ZERO = 32'h00000000;
  localparam frp_m22_csr_data_t CSR_STATE_POS = 32'h00000001;
  localparam frp_m22_csr_data_t CSR_STATE_RESERVED = 32'h00000002;
  localparam frp_m22_csr_data_t CSR_STATE_NEG = 32'h00000003;

  logic clk;
  logic rst_n;
  logic csr_valid;
  logic csr_write;
  frp_m22_csr_addr_t csr_addr;
  frp_m22_csr_data_t csr_wdata;
  logic csr_ready;
  logic csr_error;
  frp_m22_csr_data_t csr_rdata;

  int transaction_count;
  int invalid_access_count;

  frp_m22_control_status_register_interface #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .csr_valid(csr_valid),
    .csr_write(csr_write),
    .csr_addr(csr_addr),
    .csr_wdata(csr_wdata),
    .csr_ready(csr_ready),
    .csr_error(csr_error),
    .csr_rdata(csr_rdata)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  task automatic csr_idle;
    begin
      csr_valid = 1'b0;
      csr_write = 1'b0;
      csr_addr = '0;
      csr_wdata = '0;
    end
  endtask

  task automatic transact_write(
    input frp_m22_csr_addr_t address,
    input frp_m22_csr_data_t value,
    input logic expected_error
  );
    begin
      @(negedge clk);
      csr_valid = 1'b1;
      csr_write = 1'b1;
      csr_addr = address;
      csr_wdata = value;
      #1;
      if (csr_ready !== 1'b1) begin
        $fatal(1, "FRP M22 TB: write transaction was not ready");
      end
      if (csr_error !== expected_error) begin
        $fatal(
          1,
          "FRP M22 TB: write error mismatch addr=%h data=%h",
          address,
          value
        );
      end
      @(posedge clk);
      #1;
      csr_idle();
      transaction_count++;
      if (expected_error) begin
        invalid_access_count++;
      end
    end
  endtask

  task automatic transact_read(
    input frp_m22_csr_addr_t address,
    input logic expected_error,
    output frp_m22_csr_data_t value
  );
    begin
      @(negedge clk);
      csr_valid = 1'b1;
      csr_write = 1'b0;
      csr_addr = address;
      csr_wdata = '0;
      #1;
      if (csr_ready !== 1'b1) begin
        $fatal(1, "FRP M22 TB: read transaction was not ready");
      end
      if (csr_error !== expected_error) begin
        $fatal(1, "FRP M22 TB: read error mismatch addr=%h", address);
      end
      value = csr_rdata;
      @(posedge clk);
      #1;
      csr_idle();
      transaction_count++;
      if (expected_error) begin
        invalid_access_count++;
      end
    end
  endtask

  task automatic write_ok(
    input frp_m22_csr_addr_t address,
    input frp_m22_csr_data_t value
  );
    begin
      transact_write(address, value, 1'b0);
    end
  endtask

  task automatic write_error(
    input frp_m22_csr_addr_t address,
    input frp_m22_csr_data_t value
  );
    begin
      transact_write(address, value, 1'b1);
    end
  endtask

  task automatic read_error(input frp_m22_csr_addr_t address);
    frp_m22_csr_data_t ignored;
    begin
      transact_read(address, 1'b1, ignored);
      if (ignored !== '0) begin
        $fatal(1, "FRP M22 TB: invalid read returned nonzero data");
      end
    end
  endtask

  task automatic expect_read(
    input frp_m22_csr_addr_t address,
    input frp_m22_csr_data_t expected
  );
    frp_m22_csr_data_t actual;
    begin
      transact_read(address, 1'b0, actual);
      if (actual !== expected) begin
        $fatal(
          1,
          "FRP M22 TB: read mismatch addr=%h expected=%h actual=%h",
          address,
          expected,
          actual
        );
      end
    end
  endtask

  task automatic select_lane(input int lane_index);
    begin
      write_ok(FRP_M22_ADDR_REQUEST_LANE_SELECT, lane_index);
    end
  endtask

  task automatic stage_request(
    input int lane_index,
    input int cell_index,
    input logic [STATE_BITS-1:0] target_value
  );
    begin
      select_lane(lane_index);
      write_ok(FRP_M22_ADDR_REQUEST_CELL_INDEX, cell_index);
      write_ok(
        FRP_M22_ADDR_REQUEST_TARGET,
        frp_m22_csr_data_t'(target_value)
      );
      write_ok(FRP_M22_ADDR_REQUEST_VALID, 1);
    end
  endtask

  task automatic observe_cell(input int cell_index);
    begin
      write_ok(FRP_M22_ADDR_OBSERVE_CELL_INDEX, cell_index);
    end
  endtask

  task automatic apply_reset;
    begin
      csr_idle();
      rst_n = 1'b0;
      repeat (3) @(negedge clk);
      rst_n = 1'b1;
      repeat (2) @(negedge clk);
      #1;
    end
  endtask

  initial begin
    frp_m22_csr_data_t status_value;
    frp_m22_csr_data_t invariant_value;
    frp_m22_csr_data_t all_lanes_mask;

    transaction_count = 0;
    invalid_access_count = 0;
    rst_n = 1'b0;
    csr_idle();
    apply_reset();

    // Reset-value verification for every writable state holder.
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_FREE);
    expect_read(FRP_M22_ADDR_REQUEST_LANE_SELECT, 0);
    expect_read(FRP_M22_ADDR_REQUEST_CELL_INDEX, 0);
    expect_read(FRP_M22_ADDR_REQUEST_TARGET, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_REQUEST_VALID, 0);
    expect_read(FRP_M22_ADDR_OBSERVE_CELL_INDEX, 0);
    expect_read(FRP_M22_ADDR_TICKS_RECORDED, 0);
    expect_read(FRP_M22_ADDR_RETAINED_STATE, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_PENDING_ROUTE, CSR_STATE_ZERO);

    transact_read(FRP_M22_ADDR_STATUS, 1'b0, status_value);
    if (status_value[FRP_M22_STATUS_READY] !== 1'b1) begin
      $fatal(1, "FRP M22 TB: ready status was not asserted");
    end
    if (status_value[FRP_M22_STATUS_INVARIANT_FAILURE] !== 1'b0) begin
      $fatal(1, "FRP M22 TB: reset invariant status failed");
    end
    transact_read(FRP_M22_ADDR_INVARIANT_FLAGS, 1'b0, invariant_value);
    if (
      invariant_value[FRP_M16_INVARIANT_FLAGS-1:0]
      !== {FRP_M16_INVARIANT_FLAGS{1'b1}}
    ) begin
      $fatal(1, "FRP M22 TB: reset invariant vector is incomplete");
    end

    // Access-policy and invalid-payload qualification.
    read_error(FRP_M22_ADDR_CONTROL);
    read_error(8'h01);
    read_error(8'h68);
    write_error(FRP_M22_ADDR_STATUS, 0);
    write_error(FRP_M22_ADDR_CONTROL, 0);
    write_error(FRP_M22_ADDR_CONTROL, 3);
    write_error(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_RESERVED);
    write_error(FRP_M22_ADDR_REQUEST_LANE_SELECT, REQUEST_LANES);
    write_error(FRP_M22_ADDR_REQUEST_CELL_INDEX, CELLS);
    write_error(FRP_M22_ADDR_REQUEST_TARGET, CSR_STATE_RESERVED);
    write_error(FRP_M22_ADDR_REQUEST_VALID, 2);
    write_error(FRP_M22_ADDR_OBSERVE_CELL_INDEX, CELLS);

    // Invalid writes preserve the reset values.
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_FREE);
    expect_read(FRP_M22_ADDR_REQUEST_LANE_SELECT, 0);
    expect_read(FRP_M22_ADDR_REQUEST_CELL_INDEX, 0);
    expect_read(FRP_M22_ADDR_REQUEST_TARGET, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_REQUEST_VALID, 0);
    expect_read(FRP_M22_ADDR_OBSERVE_CELL_INDEX, 0);

    // Exact scheduler configuration exposure.
    write_ok(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_7_1);
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_7_1);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE_ACTIVE, CSR_MODE_7_1);
    write_ok(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_1_7);
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_1_7);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    expect_read(FRP_M22_ADDR_SCHEDULER_MODE_ACTIVE, CSR_MODE_1_7);
    write_ok(FRP_M22_ADDR_SCHEDULER_MODE, CSR_MODE_FREE);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_CLEAR_COUNTERS);
    expect_read(FRP_M22_ADDR_TICKS_RECORDED, 0);

    // Explicit request clearing does not execute the core.
    stage_request(0, 0, FRP_STATE_POS);
    expect_read(FRP_M22_ADDR_REQUEST_VALID, 1);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_CLEAR_REQUESTS);
    expect_read(FRP_M22_ADDR_REQUEST_VALID, 0);
    expect_read(FRP_M22_ADDR_TICKS_RECORDED, 0);

    // Zero -> 1 request submission and retained-state observation.
    stage_request(0, 0, FRP_STATE_POS);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    expect_read(FRP_M22_ADDR_REQUEST_VALID, 0);
    observe_cell(0);
    expect_read(FRP_M22_ADDR_RETAINED_STATE, CSR_STATE_POS);
    expect_read(FRP_M22_ADDR_PENDING_ROUTE, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_REQUEST_ACCEPT, 1);
    expect_read(FRP_M22_ADDR_REQUEST_REJECT, 0);
    expect_read(FRP_M22_ADDR_ACCEPTED_CHANGES, 1);
    expect_read(FRP_M22_ADDR_CAPACITY_REMAINING, REQUEST_LANES - 1);
    expect_read(FRP_M22_ADDR_CAPACITY_EXHAUSTED, 0);
    expect_read(FRP_M22_ADDR_SWITCH_LOAD_NUMERATOR, 1);

    // Opposite polarity is retained through active neutral state 0.
    stage_request(0, 0, FRP_STATE_NEG);
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    observe_cell(0);
    expect_read(FRP_M22_ADDR_RETAINED_STATE, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_PENDING_ROUTE, CSR_STATE_NEG);
    expect_read(FRP_M22_ADDR_REQUESTED_DIRECT_EVENTS, 1);
    expect_read(FRP_M22_ADDR_PREVENTED_DIRECT_EVENTS, 1);
    expect_read(FRP_M22_ADDR_NEUTRAL_ROUTED_EVENTS, 1);
    expect_read(FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS, 0);
    expect_read(FRP_M22_ADDR_RESERVED_STATE_EVENTS, 0);
    expect_read(FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS, 0);

    // A following free-mode tick completes 0 -> -1 and clears the route.
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    observe_cell(0);
    expect_read(FRP_M22_ADDR_RETAINED_STATE, CSR_STATE_NEG);
    expect_read(FRP_M22_ADDR_PENDING_ROUTE, CSR_STATE_ZERO);
    expect_read(FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS, 0);
    expect_read(FRP_M22_ADDR_RESERVED_STATE_EVENTS, 0);
    expect_read(FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS, 0);

    // Saturate the exact CELLS/4 transition-capacity profile.
    for (int lane_index = 0; lane_index < REQUEST_LANES; lane_index++) begin
      stage_request(
        lane_index,
        lane_index + 1,
        FRP_STATE_POS
      );
    end
    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_TICK);
    all_lanes_mask = (32'h00000001 << REQUEST_LANES) - 1;
    expect_read(FRP_M22_ADDR_REQUEST_ACCEPT, all_lanes_mask);
    expect_read(FRP_M22_ADDR_REQUEST_REJECT, 0);
    expect_read(FRP_M22_ADDR_ACCEPTED_CHANGES, REQUEST_LANES);
    expect_read(FRP_M22_ADDR_CAPACITY_REMAINING, 0);
    expect_read(FRP_M22_ADDR_CAPACITY_EXHAUSTED, 1);
    expect_read(FRP_M22_ADDR_SWITCH_LOAD_NUMERATOR, REQUEST_LANES);

    for (int lane_index = 0; lane_index < REQUEST_LANES; lane_index++) begin
      observe_cell(lane_index + 1);
      expect_read(FRP_M22_ADDR_RETAINED_STATE, CSR_STATE_POS);
      expect_read(FRP_M22_ADDR_PENDING_ROUTE, CSR_STATE_ZERO);
    end

    // Final invariant and status observations.
    transact_read(FRP_M22_ADDR_INVARIANT_FLAGS, 1'b0, invariant_value);
    if (
      invariant_value[FRP_M16_INVARIANT_FLAGS-1:0]
      !== {FRP_M16_INVARIANT_FLAGS{1'b1}}
    ) begin
      $fatal(1, "FRP M22 TB: final invariant vector is incomplete");
    end
    transact_read(FRP_M22_ADDR_STATUS, 1'b0, status_value);
    if (status_value[FRP_M22_STATUS_READY] !== 1'b1) begin
      $fatal(1, "FRP M22 TB: final ready status is not asserted");
    end
    if (status_value[FRP_M22_STATUS_CAPACITY_EXHAUSTED] !== 1'b1) begin
      $fatal(1, "FRP M22 TB: capacity status is not asserted");
    end
    if (status_value[FRP_M22_STATUS_INVARIANT_FAILURE] !== 1'b0) begin
      $fatal(1, "FRP M22 TB: final invariant status failed");
    end
    if (
      status_value[FRP_M22_STATUS_ACTUAL_DIRECT_NONZERO]
      || status_value[FRP_M22_STATUS_RESERVED_STATE_NONZERO]
      || status_value[FRP_M22_STATUS_QUEUE_OVERFLOW_NONZERO]
    ) begin
      $fatal(1, "FRP M22 TB: forbidden event status asserted");
    end

    write_ok(FRP_M22_ADDR_CONTROL, FRP_M22_CONTROL_CLEAR_COUNTERS);
    expect_read(FRP_M22_ADDR_TICKS_RECORDED, 0);
    expect_read(FRP_M22_ADDR_REQUEST_ACCEPT, 0);
    expect_read(FRP_M22_ADDR_REQUEST_REJECT, 0);
    expect_read(FRP_M22_ADDR_ACCEPTED_CHANGES, 0);
    expect_read(FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS, 0);
    expect_read(FRP_M22_ADDR_RESERVED_STATE_EVENTS, 0);
    expect_read(FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS, 0);

    $display("FRP M22 deterministic CSR testbench completed.");
    $display("CELLS=%0d REQUEST_LANES=%0d", CELLS, REQUEST_LANES);
    $display("M22_INTERFACE_TRANSACTIONS=%0d", transaction_count);
    $display("M22_INVALID_ACCESSES=%0d", invalid_access_count);
    $display("actual_direct_events=0");
    $display("reserved_state_events=0");
    $display("queue_overflow_events=0");
    $display("invariant_flags=1111111111");
    $display("M22_CSR_TESTBENCH=PASS");
    $finish;
  end

endmodule : frp_m22_control_status_register_interface_tb
