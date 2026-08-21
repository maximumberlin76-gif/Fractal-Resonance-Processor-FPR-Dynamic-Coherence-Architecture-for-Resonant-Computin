// SPDX-License-Identifier: Apache-2.0
// FRP M24 bounded proof harness for the actual M16 scheduler RTL.

module frp_m24_scheduler_properties_formal;
  localparam int COUNTER_BITS = 8;

  (* anyseq *) logic clock;
  (* anyseq *) logic tick_enable;
  (* anyseq *) logic clear_counters;
  (* anyseq *) logic [1:0] scheduler_mode;

  wire rst_n = 1'b1;
  wire [1:0] scheduler_mode_q;
  wire [2:0] scheduler_state_q;
  wire [COUNTER_BITS-1:0] tick_index_q;
  wire [2:0] period_index_q;
  wire [COUNTER_BITS-1:0] ticks_recorded_q;
  wire [COUNTER_BITS-1:0] scheduler_count_free_q;
  wire [COUNTER_BITS-1:0] scheduler_count_balance_q;
  wire [COUNTER_BITS-1:0] scheduler_count_commit_q;
  wire [COUNTER_BITS-1:0] scheduler_count_excite_q;
  wire [COUNTER_BITS-1:0] scheduler_count_neutralize_q;
  wire free_enable;
  wire balance_enable;
  wire commit_enable;
  wire excite_enable;
  wire neutralize_enable;
  wire scheduler_mode_reserved;
  wire scheduler_state_reserved;
  wire scheduler_valid;
  wire scheduler_counts_valid;

  frp_m16_scheduler #(.COUNTER_BITS(COUNTER_BITS)) dut (
    .clk(clock),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .tick_index_q(tick_index_q),
    .period_index_q(period_index_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q),
    .free_enable(free_enable),
    .balance_enable(balance_enable),
    .commit_enable(commit_enable),
    .excite_enable(excite_enable),
    .neutralize_enable(neutralize_enable),
    .scheduler_mode_reserved(scheduler_mode_reserved),
    .scheduler_state_reserved(scheduler_state_reserved),
    .scheduler_valid(scheduler_valid),
    .scheduler_counts_valid(scheduler_counts_valid)
  );

  wire [4:0] enable_vector = {
    neutralize_enable,
    excite_enable,
    commit_enable,
    balance_enable,
    free_enable
  };
  wire [COUNTER_BITS-1:0] counter_sum =
    scheduler_count_free_q
    + scheduler_count_balance_q
    + scheduler_count_commit_q
    + scheduler_count_excite_q
    + scheduler_count_neutralize_q;

  wire M24_P10 = !scheduler_mode_reserved;
  wire M24_P11 = !scheduler_state_reserved;
  wire M24_P12 = period_index_q == tick_index_q[2:0];
  wire M24_P13 = scheduler_counts_valid && (counter_sum == ticks_recorded_q);
  wire M24_P14 = tick_enable ? ($countones(enable_vector) == 1) : (enable_vector == 5'b0);
  wire M24_P15 =
    scheduler_valid
    && (scheduler_state_q == frp_decode_scheduler_state(
      scheduler_mode_q, period_index_q
    ));

  always @* begin
    assume(frp_is_valid_scheduler_mode(scheduler_mode));
    assert(M24_P10);
    assert(M24_P11);
    assert(M24_P12);
    assert(M24_P13);
    assert(M24_P14);
    assert(M24_P15);
  end
endmodule
