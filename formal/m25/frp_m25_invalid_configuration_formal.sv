// SPDX-License-Identifier: Apache-2.0
// FRP M25 invalid configuration rejection and deterministic recovery proof.

module frp_m25_invalid_configuration_formal;
  localparam int COUNTER_BITS = 8;
  (* anyseq *) logic clock;
  logic [2:0] proof_step_q;

  wire [1:0] requested_mode =
    (proof_step_q == 0) ? FRP_MODE_RESERVED : FRP_MODE_FREE;
  wire [1:0] scheduler_mode_q;
  wire [2:0] scheduler_state_q;
  wire mode_reserved;
  wire state_reserved;
  wire scheduler_valid;
  wire free_enable;
  wire balance_enable;
  wire commit_enable;
  wire excite_enable;
  wire neutralize_enable;

  frp_m16_scheduler #(.COUNTER_BITS(COUNTER_BITS)) dut (
    .clk(clock), .rst_n(1'b1), .tick_enable(1'b0),
    .clear_counters(1'b0), .scheduler_mode(requested_mode),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q), .tick_index_q(),
    .period_index_q(), .ticks_recorded_q(),
    .scheduler_count_free_q(), .scheduler_count_balance_q(),
    .scheduler_count_commit_q(), .scheduler_count_excite_q(),
    .scheduler_count_neutralize_q(), .free_enable(free_enable),
    .balance_enable(balance_enable), .commit_enable(commit_enable),
    .excite_enable(excite_enable), .neutralize_enable(neutralize_enable),
    .scheduler_mode_reserved(mode_reserved),
    .scheduler_state_reserved(state_reserved),
    .scheduler_valid(scheduler_valid), .scheduler_counts_valid()
  );

  always @(posedge clock) begin
    proof_step_q <= proof_step_q + 1'b1;
  end

  wire M25_P15 =
    (proof_step_q != 1)
    || ((scheduler_mode_q == FRP_MODE_RESERVED)
      && (scheduler_state_q == FRP_SCHED_INVALID)
      && mode_reserved && state_reserved && !scheduler_valid);
  wire M25_P16 =
    (proof_step_q != 1)
    || !(free_enable || balance_enable || commit_enable
      || excite_enable || neutralize_enable);
  wire M25_P17 =
    (proof_step_q < 2)
    || ((scheduler_mode_q == FRP_MODE_FREE)
      && (scheduler_state_q == FRP_SCHED_FREE)
      && !mode_reserved && !state_reserved && scheduler_valid);

  always @* begin
    assert(M25_P15); assert(M25_P16); assert(M25_P17);
  end
endmodule
