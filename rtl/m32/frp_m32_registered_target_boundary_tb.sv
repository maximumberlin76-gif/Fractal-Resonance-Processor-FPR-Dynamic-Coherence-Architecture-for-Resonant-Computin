// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic registered-target boundary testbench.

`ifndef FRP_M32_REGISTERED_TARGET_BOUNDARY_TB_SV
`define FRP_M32_REGISTERED_TARGET_BOUNDARY_TB_SV

`timescale 1ns / 1ps

`include "frp_m32_registered_target_boundary.sv"

module frp_m32_registered_target_boundary_tb;

  localparam int CELLS = 8;
  localparam int STATE_BITS = frp_m31_pkg::FRP_M31_STATE_BITS;
  localparam int COUNTER_BITS = 2;

  localparam logic [(CELLS*STATE_BITS)-1:0] CAPTURE_WORD = {
    frp_m31_pkg::FRP_STATE_POS,
    frp_m31_pkg::FRP_ACTIVE_NEUTRAL,
    frp_m31_pkg::FRP_STATE_NEG,
    frp_m31_pkg::FRP_STATE_POS,
    frp_m31_pkg::FRP_ACTIVE_NEUTRAL,
    frp_m31_pkg::FRP_STATE_NEG,
    frp_m31_pkg::FRP_STATE_POS,
    frp_m31_pkg::FRP_ACTIVE_NEUTRAL
  };

  logic clk;
  logic rst_n;
  logic tick_enable;
  logic clear_counters;
  logic phase_target_valid;
  logic [(CELLS*STATE_BITS)-1:0] phase_target;
  logic [(CELLS*STATE_BITS)-1:0] registered_target_q;
  logic registered_target_valid_q;
  logic phase_target_domain_valid;
  logic registered_target_domain_valid;
  logic capture_accepted;
  logic capture_rejected;
  logic [COUNTER_BITS-1:0] accepted_capture_events_q;
  logic [COUNTER_BITS-1:0] rejected_capture_events_q;

  frp_m32_registered_target_boundary #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .phase_target_valid(phase_target_valid),
    .phase_target(phase_target),
    .registered_target_q(registered_target_q),
    .registered_target_valid_q(registered_target_valid_q),
    .phase_target_domain_valid(phase_target_domain_valid),
    .registered_target_domain_valid(registered_target_domain_valid),
    .capture_accepted(capture_accepted),
    .capture_rejected(capture_rejected),
    .accepted_capture_events_q(accepted_capture_events_q),
    .rejected_capture_events_q(rejected_capture_events_q)
  );

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

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

  task automatic run_accepted_capture;
    begin
      start_tick();
      if (!capture_accepted || capture_rejected)
        $fatal(1, "FRP M32 TB: valid capture classification mismatch");
      finish_tick();
    end
  endtask

  task automatic run_rejected_capture;
    begin
      start_tick();
      if (capture_accepted || !capture_rejected)
        $fatal(1, "FRP M32 TB: invalid capture classification mismatch");
      finish_tick();
    end
  endtask

  initial begin : qualification_sequence
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    phase_target_valid = 1'b0;
    phase_target = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};

    repeat (3) @(negedge clk);
    rst_n = 1'b1;
    repeat (2) @(negedge clk);
    #1;

    if (registered_target_q !== {
      CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}
    }) begin
      $fatal(1, "FRP M32 TB: reset target is not active state zero");
    end
    if (registered_target_valid_q !== 1'b0)
      $fatal(1, "FRP M32 TB: reset capture validity mismatch");
    if (!registered_target_domain_valid)
      $fatal(1, "FRP M32 TB: reset target domain mismatch");
    if ((accepted_capture_events_q !== '0)
        || (rejected_capture_events_q !== '0)) begin
      $fatal(1, "FRP M32 TB: reset counter mismatch");
    end

    phase_target = CAPTURE_WORD;
    phase_target_valid = 1'b1;
    if (!phase_target_domain_valid)
      $fatal(1, "FRP M32 TB: valid source target rejected by domain check");
    run_accepted_capture();

    if (registered_target_q !== CAPTURE_WORD)
      $fatal(1, "FRP M32 TB: valid target was not registered");
    if (!registered_target_valid_q)
      $fatal(1, "FRP M32 TB: registered validity was not asserted");
    if (!registered_target_domain_valid)
      $fatal(1, "FRP M32 TB: registered target left the ternary domain");
    if (accepted_capture_events_q !== 2'd1)
      $fatal(1, "FRP M32 TB: accepted event count mismatch");

    phase_target = {CELLS{frp_m31_pkg::FRP_STATE_NEG}};
    @(negedge clk);
    #1;
    if (capture_accepted || capture_rejected)
      $fatal(1, "FRP M32 TB: disabled tick produced a capture event");
    if (registered_target_q !== CAPTURE_WORD)
      $fatal(1, "FRP M32 TB: disabled tick changed the registered target");

    phase_target[STATE_BITS-1:0] = frp_m31_pkg::FRP_STATE_RESERVED;
    phase_target_valid = 1'b0;
    start_tick();
    if (phase_target_domain_valid)
      $fatal(1, "FRP M32 TB: reserved source target passed the domain check");
    if (capture_accepted || capture_rejected)
      $fatal(1, "FRP M32 TB: invalid source-valid flag produced an event");
    finish_tick();
    if (registered_target_q !== CAPTURE_WORD)
      $fatal(1, "FRP M32 TB: invalid source-valid flag changed the target");

    phase_target_valid = 1'b1;
    run_rejected_capture();
    if (registered_target_q !== CAPTURE_WORD)
      $fatal(1, "FRP M32 TB: reserved target crossed the boundary");
    if (!registered_target_valid_q)
      $fatal(1, "FRP M32 TB: rejected target cleared registered validity");
    if (!registered_target_domain_valid)
      $fatal(1, "FRP M32 TB: rejected target changed registered domain state");
    if (rejected_capture_events_q !== 2'd1)
      $fatal(1, "FRP M32 TB: rejected event count mismatch");

    phase_target = {CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}};
    clear_counters = 1'b1;
    run_accepted_capture();
    clear_counters = 1'b0;
    if (registered_target_q !== phase_target)
      $fatal(1, "FRP M32 TB: counter clear blocked a valid capture");
    if ((accepted_capture_events_q !== '0)
        || (rejected_capture_events_q !== '0)) begin
      $fatal(1, "FRP M32 TB: counter clear mismatch");
    end

    repeat (4) run_accepted_capture();
    if (accepted_capture_events_q !== {COUNTER_BITS{1'b1}})
      $fatal(1, "FRP M32 TB: accepted counter did not saturate");

    phase_target[STATE_BITS-1:0] = frp_m31_pkg::FRP_STATE_RESERVED;
    repeat (4) run_rejected_capture();
    if (rejected_capture_events_q !== {COUNTER_BITS{1'b1}})
      $fatal(1, "FRP M32 TB: rejected counter did not saturate");
    if (registered_target_q !== {
      CELLS{frp_m31_pkg::FRP_ACTIVE_NEUTRAL}
    }) begin
      $fatal(1, "FRP M32 TB: rejected saturation sequence changed target");
    end
    if (!registered_target_domain_valid)
      $fatal(1, "FRP M32 TB: final registered domain mismatch");

    $display("FRP_M32_REGISTERED_TARGET_BOUNDARY_TB: PASS");
    $finish;
  end

endmodule

`endif
