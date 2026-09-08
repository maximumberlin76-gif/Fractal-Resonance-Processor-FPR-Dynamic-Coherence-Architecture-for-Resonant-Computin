// SPDX-License-Identifier: Apache-2.0
// FRP M32 bounded formal harnesses for the registered target boundary.

module frp_m32_registered_target_boundary_safety_formal;
  localparam int CELLS = 8;
  localparam int STATE_BITS = 2;
  localparam int COUNTER_BITS = 32;
  localparam int TARGET_BITS = CELLS * STATE_BITS;

  (* anyseq *) logic clock;
  (* anyseq *) logic tick_enable;
  (* anyseq *) logic clear_counters;
  (* anyseq *) logic phase_target_valid;
  (* anyseq *) logic [TARGET_BITS-1:0] phase_target;

  logic history_valid_q;
  logic history_capture_accepted_q;
  logic history_capture_rejected_q;
  logic history_clear_counters_q;
  logic [TARGET_BITS-1:0] history_phase_target_q;
  logic [TARGET_BITS-1:0] history_registered_target_q;
  logic history_registered_target_valid_q;
  logic [COUNTER_BITS-1:0] history_accepted_events_q;
  logic [COUNTER_BITS-1:0] history_rejected_events_q;

  wire rst_n = 1'b1;
  wire [TARGET_BITS-1:0] registered_target_q;
  wire registered_target_valid_q;
  wire phase_target_domain_valid;
  wire registered_target_domain_valid;
  wire capture_accepted;
  wire capture_rejected;
  wire [COUNTER_BITS-1:0] accepted_capture_events_q;
  wire [COUNTER_BITS-1:0] rejected_capture_events_q;

  logic expected_phase_target_domain_valid;

  function automatic logic [COUNTER_BITS-1:0] expected_increment(
    input logic [COUNTER_BITS-1:0] value
  );
    begin
      if (&value)
        expected_increment = value;
      else
        expected_increment = value + 1'b1;
    end
  endfunction

  frp_m32_registered_target_boundary #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clock),
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

  always @* begin
    expected_phase_target_domain_valid = 1'b1;
    for (int cell_index = 0; cell_index < CELLS; cell_index++) begin
      case (phase_target[(cell_index*STATE_BITS) +: STATE_BITS])
        2'b00,
        2'b01,
        2'b11: begin
        end
        default: expected_phase_target_domain_valid = 1'b0;
      endcase
    end
  end

  always @(posedge clock) begin
    history_valid_q <= 1'b1;
    history_capture_accepted_q <= capture_accepted;
    history_capture_rejected_q <= capture_rejected;
    history_clear_counters_q <= clear_counters;
    history_phase_target_q <= phase_target;
    history_registered_target_q <= registered_target_q;
    history_registered_target_valid_q <= registered_target_valid_q;
    history_accepted_events_q <= accepted_capture_events_q;
    history_rejected_events_q <= rejected_capture_events_q;
  end

  wire M32_P01 =
    phase_target_domain_valid == expected_phase_target_domain_valid;
  wire M32_P02 =
    capture_accepted
    == (tick_enable && phase_target_valid && phase_target_domain_valid);
  wire M32_P03 =
    capture_rejected
    == (tick_enable && phase_target_valid && !phase_target_domain_valid);
  wire M32_P04 = !(capture_accepted && capture_rejected);
  wire M32_P05 = registered_target_domain_valid;
  wire M32_P06 =
    !$initstate
    || (
      (registered_target_q == {CELLS{2'b00}})
      && !registered_target_valid_q
      && (accepted_capture_events_q == 0)
      && (rejected_capture_events_q == 0)
    );
  wire M32_P07 =
    !history_valid_q
    || !history_capture_accepted_q
    || (
      (registered_target_q == history_phase_target_q)
      && registered_target_valid_q
    );
  wire M32_P08 =
    !history_valid_q
    || history_capture_accepted_q
    || (
      (registered_target_q == history_registered_target_q)
      && (
        registered_target_valid_q
        == history_registered_target_valid_q
      )
    );
  wire M32_P09 =
    !history_valid_q
    || (
      accepted_capture_events_q
      == (
        history_clear_counters_q
        ? {COUNTER_BITS{1'b0}}
        : (
          history_capture_accepted_q
          ? expected_increment(history_accepted_events_q)
          : history_accepted_events_q
        )
      )
    );
  wire M32_P10 =
    !history_valid_q
    || (
      rejected_capture_events_q
      == (
        history_clear_counters_q
        ? {COUNTER_BITS{1'b0}}
        : (
          history_capture_rejected_q
          ? expected_increment(history_rejected_events_q)
          : history_rejected_events_q
        )
      )
    );

  always @* begin
    assert(M32_P01);
    assert(M32_P02);
    assert(M32_P03);
    assert(M32_P04);
    assert(M32_P05);
    assert(M32_P06);
    assert(M32_P07);
    assert(M32_P08);
    assert(M32_P09);
    assert(M32_P10);
  end
endmodule

module frp_m32_registered_target_boundary_sequence_formal;
  localparam int CELLS = 8;
  localparam int STATE_BITS = 2;
  localparam int COUNTER_BITS = 32;
  localparam int TARGET_BITS = CELLS * STATE_BITS;
  localparam logic [TARGET_BITS-1:0] POSITIVE_TARGET = {CELLS{2'b01}};
  localparam logic [TARGET_BITS-1:0] RESERVED_SOURCE_TARGET = {
    {(CELLS-1){2'b01}},
    2'b10
  };

  (* anyseq *) logic clock;
  logic [2:0] proof_step_q;

  wire rst_n = 1'b1;
  wire tick_enable = proof_step_q < 2;
  wire clear_counters = 1'b0;
  wire phase_target_valid = proof_step_q < 2;
  wire [TARGET_BITS-1:0] phase_target =
    (proof_step_q == 0) ? POSITIVE_TARGET : RESERVED_SOURCE_TARGET;

  wire [TARGET_BITS-1:0] registered_target_q;
  wire registered_target_valid_q;
  wire phase_target_domain_valid;
  wire registered_target_domain_valid;
  wire capture_accepted;
  wire capture_rejected;
  wire [COUNTER_BITS-1:0] accepted_capture_events_q;
  wire [COUNTER_BITS-1:0] rejected_capture_events_q;

  frp_m32_registered_target_boundary #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clock),
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

  always @(posedge clock) begin
    proof_step_q <= proof_step_q + 1'b1;
  end

  wire M32_P11 =
    (proof_step_q != 0)
    || (
      phase_target_domain_valid
      && capture_accepted
      && !capture_rejected
    );
  wire M32_P12 =
    (proof_step_q != 1)
    || (
      (registered_target_q == POSITIVE_TARGET)
      && registered_target_valid_q
      && (accepted_capture_events_q == 1)
      && (rejected_capture_events_q == 0)
      && !phase_target_domain_valid
      && !capture_accepted
      && capture_rejected
    );
  wire M32_P13 =
    (proof_step_q < 2)
    || (
      (registered_target_q == POSITIVE_TARGET)
      && registered_target_valid_q
      && (accepted_capture_events_q == 1)
      && (rejected_capture_events_q == 1)
    );
  wire M32_P14 = registered_target_domain_valid;

  always @* begin
    assert(M32_P11);
    assert(M32_P12);
    assert(M32_P13);
    assert(M32_P14);
  end
endmodule
