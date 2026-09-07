// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic registered-target request-path testbench.

`ifndef FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB_SV
`define FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB_SV

`timescale 1ns / 1ps

`include "frp_m32_registered_target_request_path.sv"

module frp_m32_registered_target_request_path_tb;

  localparam int CELLS = 8;
  localparam int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS;
  localparam int REQUEST_LANES = 2;
  localparam int CELL_INDEX_BITS = 3;
  localparam int COUNTER_BITS = 4;

  logic clk;
  logic rst_n;
  logic tick_enable;
  logic clear_counters;
  logic phase_target_valid;
  logic [(CELLS*STATE_BITS)-1:0] phase_target_source;
  logic auto_target_enable;
  logic [(CELLS*STATE_BITS)-1:0] retained_state;
  logic [(CELLS*STATE_BITS)-1:0] pending_route;
  frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state;

  logic [(CELLS*STATE_BITS)-1:0] registered_target_q;
  logic registered_target_valid_q;
  logic phase_target_domain_valid;
  logic registered_target_domain_valid;
  logic capture_accepted;
  logic capture_rejected;
  logic [COUNTER_BITS-1:0] accepted_capture_events_q;
  logic [COUNTER_BITS-1:0] rejected_capture_events_q;
  logic registered_request_enable;
  logic [REQUEST_LANES-1:0] phase_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] phase_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] phase_request_target;

  logic [(CELLS*STATE_BITS)-1:0] first_target_word;
  logic [(CELLS*STATE_BITS)-1:0] second_target_word;
  logic [(CELLS*STATE_BITS)-1:0] opposite_target_word;

  frp_m32_registered_target_request_path #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .phase_target_valid(phase_target_valid),
    .phase_target_source(phase_target_source),
    .auto_target_enable(auto_target_enable),
    .retained_state(retained_state),
    .pending_route(pending_route),
    .scheduler_state(scheduler_state),
    .registered_target_q(registered_target_q),
    .registered_target_valid_q(registered_target_valid_q),
    .phase_target_domain_valid(phase_target_domain_valid),
    .registered_target_domain_valid(registered_target_domain_valid),
    .capture_accepted(capture_accepted),
    .capture_rejected(capture_rejected),
    .accepted_capture_events_q(accepted_capture_events_q),
    .rejected_capture_events_q(rejected_capture_events_q),
    .registered_request_enable(registered_request_enable),
    .phase_request_valid(phase_request_valid),
    .phase_request_cell_index(phase_request_cell_index),
    .phase_request_target(phase_request_target)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  function automatic logic [CELL_INDEX_BITS-1:0] lane_cell_index(
    input int lane_index
  );
    begin
      lane_cell_index = phase_request_cell_index[
        (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
      ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] lane_target(
    input int lane_index
  );
    begin
      lane_target = phase_request_target[
        (lane_index*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction

  task automatic start_tick;
    begin
      @(negedge clk);
      tick_enable = 1'b1;
      #1;
    end
  endtask

  task automatic finish_tick;
    begin
      @(negedge clk);
      tick_enable = 1'b0;
      #1;
    end
  endtask

  task automatic expect_no_requests;
    begin
      if (phase_request_valid !== '0)
        $fatal(1, "FRP M32 request-path TB: unexpected request");
      if (phase_request_cell_index !== '0)
        $fatal(1, "FRP M32 request-path TB: inactive cell index mismatch");
      if (phase_request_target !== '0)
        $fatal(1, "FRP M32 request-path TB: inactive target mismatch");
    end
  endtask

  task automatic expect_lane(
    input int lane_index,
    input int expected_cell_index,
    input logic [STATE_BITS-1:0] expected_target
  );
    begin
      if (!phase_request_valid[lane_index])
        $fatal(1, "FRP M32 request-path TB: expected lane is not valid");
      if (
        lane_cell_index(lane_index)
        !== expected_cell_index[CELL_INDEX_BITS-1:0]
      ) begin
        $fatal(1, "FRP M32 request-path TB: lane cell index mismatch");
      end
      if (lane_target(lane_index) !== expected_target)
        $fatal(1, "FRP M32 request-path TB: lane target mismatch");
    end
  endtask

  initial begin : qualification_sequence
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    phase_target_valid = 1'b1;
    phase_target_source = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    auto_target_enable = 1'b1;
    retained_state = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    pending_route = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    scheduler_state = frp_m31_pkg::FRP_SCHED_FREE;
    first_target_word = '0;
    second_target_word = '0;
    opposite_target_word = '0;

    repeat (3) @(negedge clk);
    rst_n = 1'b1;
    repeat (2) @(negedge clk);
    #1;

    if (registered_target_q !== {
      CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}
    }) begin
      $fatal(1, "FRP M32 request-path TB: reset target mismatch");
    end
    if (registered_target_valid_q)
      $fatal(1, "FRP M32 request-path TB: reset validity mismatch");
    if (registered_request_enable)
      $fatal(1, "FRP M32 request-path TB: reset request gate mismatch");
    expect_no_requests();

    first_target_word[(0*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_POS;
    first_target_word[(1*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_NEG;
    phase_target_source = first_target_word;
    #1;

    if (!phase_target_domain_valid)
      $fatal(1, "FRP M32 request-path TB: first source domain mismatch");
    expect_no_requests();

    start_tick();
    if (!capture_accepted || capture_rejected)
      $fatal(1, "FRP M32 request-path TB: first capture mismatch");
    if (registered_target_q !== {
      CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}
    }) begin
      $fatal(1, "FRP M32 request-path TB: source bypassed the register");
    end
    expect_no_requests();
    finish_tick();

    if (registered_target_q !== first_target_word)
      $fatal(1, "FRP M32 request-path TB: first target was not registered");
    if (!registered_target_valid_q || !registered_target_domain_valid)
      $fatal(1, "FRP M32 request-path TB: registered target state mismatch");
    if (!registered_request_enable)
      $fatal(1, "FRP M32 request-path TB: registered request gate is closed");
    if (phase_request_valid !== 2'b11)
      $fatal(1, "FRP M32 request-path TB: first request mask mismatch");
    expect_lane(0, 0, frp_m31_pkg::FRP_STATE_POS);
    expect_lane(1, 1, frp_m31_pkg::FRP_STATE_NEG);

    second_target_word[(2*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_POS;
    phase_target_source = second_target_word;
    #1;
    if (registered_target_q !== first_target_word)
      $fatal(1, "FRP M32 request-path TB: source changed registered target");
    if (phase_request_valid !== 2'b11)
      $fatal(1, "FRP M32 request-path TB: source changed registered requests");
    expect_lane(0, 0, frp_m31_pkg::FRP_STATE_POS);
    expect_lane(1, 1, frp_m31_pkg::FRP_STATE_NEG);

    start_tick();
    if (registered_target_q !== first_target_word)
      $fatal(1, "FRP M32 request-path TB: second source bypassed register");
    finish_tick();

    if (registered_target_q !== second_target_word)
      $fatal(1, "FRP M32 request-path TB: second target was not registered");
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: second request mask mismatch");
    expect_lane(0, 2, frp_m31_pkg::FRP_STATE_POS);

    scheduler_state = frp_m31_pkg::FRP_SCHED_BALANCE;
    #1;
    expect_no_requests();
    scheduler_state = frp_m31_pkg::FRP_SCHED_COMMIT;
    #1;
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: commit request mismatch");
    expect_lane(0, 2, frp_m31_pkg::FRP_STATE_POS);

    pending_route[(2*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_NEG;
    #1;
    expect_no_requests();
    pending_route = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    retained_state[(2*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_POS;
    #1;
    expect_no_requests();
    retained_state = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};

    auto_target_enable = 1'b0;
    #1;
    if (registered_request_enable)
      $fatal(1, "FRP M32 request-path TB: disabled automatic path is enabled");
    expect_no_requests();
    auto_target_enable = 1'b1;
    scheduler_state = frp_m31_pkg::FRP_SCHED_FREE;
    #1;
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: restored request mismatch");
    expect_lane(0, 2, frp_m31_pkg::FRP_STATE_POS);

    phase_target_source = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    phase_target_source[STATE_BITS-1:0] =
      frp_m31_pkg::FRP_STATE_RESERVED;
    #1;
    if (phase_target_domain_valid)
      $fatal(1, "FRP M32 request-path TB: reserved source passed domain check");
    start_tick();
    if (capture_accepted || !capture_rejected)
      $fatal(1, "FRP M32 request-path TB: reserved capture mismatch");
    if (registered_target_q !== second_target_word)
      $fatal(1, "FRP M32 request-path TB: reserved source bypassed register");
    finish_tick();
    if (registered_target_q !== second_target_word)
      $fatal(1, "FRP M32 request-path TB: reserved source changed target");
    if (accepted_capture_events_q !== 4'd2)
      $fatal(1, "FRP M32 request-path TB: accepted count mismatch");
    if (rejected_capture_events_q !== 4'd1)
      $fatal(1, "FRP M32 request-path TB: rejected count mismatch");
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: rejected capture changed requests");
    expect_lane(0, 2, frp_m31_pkg::FRP_STATE_POS);

    opposite_target_word[(0*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_NEG;
    phase_target_source = opposite_target_word;
    start_tick();
    if (!capture_accepted || capture_rejected)
      $fatal(1, "FRP M32 request-path TB: opposite target capture mismatch");
    finish_tick();
    if (registered_target_q !== opposite_target_word)
      $fatal(1, "FRP M32 request-path TB: opposite target register mismatch");

    retained_state[(0*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_POS;
    scheduler_state = frp_m31_pkg::FRP_SCHED_COMMIT;
    #1;
    expect_no_requests();
    scheduler_state = frp_m31_pkg::FRP_SCHED_BALANCE;
    #1;
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: opposite request mask mismatch");
    expect_lane(0, 0, frp_m31_pkg::FRP_STATE_NEG);

    pending_route[(0*STATE_BITS) +: STATE_BITS] =
      frp_m31_pkg::FRP_STATE_NEG;
    #1;
    expect_no_requests();
    pending_route = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};

    phase_target_source = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    clear_counters = 1'b1;
    start_tick();
    if (!capture_accepted || capture_rejected)
      $fatal(1, "FRP M32 request-path TB: active-zero capture mismatch");
    finish_tick();
    clear_counters = 1'b0;

    if (registered_target_q !== {
      CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}
    }) begin
      $fatal(1, "FRP M32 request-path TB: active-zero target mismatch");
    end
    if ((accepted_capture_events_q !== '0)
        || (rejected_capture_events_q !== '0)) begin
      $fatal(1, "FRP M32 request-path TB: counter clear mismatch");
    end
    if (phase_request_valid !== 2'b01)
      $fatal(1, "FRP M32 request-path TB: active-zero request mismatch");
    expect_lane(0, 0, frp_m31_pkg::FRP_ACTIVE_NEUTRAL);

    retained_state = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    #1;
    expect_no_requests();
    if (!registered_target_domain_valid)
      $fatal(1, "FRP M32 request-path TB: final target domain mismatch");

    $display("FRP_M32_REGISTERED_TARGET_REQUEST_PATH_TB: PASS");
    $finish;
  end

endmodule

`endif
