// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic registered-target 1/7 scheduler testbench.

`ifndef FRP_M32_MODE_1_7_TB_SV
`define FRP_M32_MODE_1_7_TB_SV

`timescale 1ns / 1ps

`include "frp_m32_core.sv"
`include "frp_m31_assertions.sv"
`include "frp_m31_phase_thermal_assertions.sv"

module frp_m32_mode_1_7_tb;

  import frp_m31_pkg::*;
  import frp_m31_fixed_point_pkg::*;

  localparam int CELLS = 8;
  localparam int STATE_BITS = FRP_M31_STATE_BITS;
  localparam int REQUEST_LANES = frp_calc_request_lanes(CELLS);
  localparam int CELL_INDEX_BITS = $clog2(CELLS);
  localparam int COUNTER_BITS = FRP_M31_COUNTER_BITS;

  logic clk;
  logic rst_n;
  logic tick_enable;
  logic clear_counters;
  frp_m31_scheduler_mode_e scheduler_mode;

  logic phase_load_valid;
  logic [(CELLS*32)-1:0] phase_load;
  logic [(CELLS*32)-1:0] frequency_load_q16;
  logic [(CELLS*32)-1:0] gamma_effective_word;
  logic [(CELLS*32)-1:0] thermal_node_factor_q30;

  logic auto_target_enable;
  logic [REQUEST_LANES-1:0] external_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    external_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] external_request_target;
  logic [(CELLS*STATE_BITS)-1:0] external_target_bank;

  logic [(CELLS*32)-1:0] phase_word_q;
  logic [(CELLS*32)-1:0] frequency_current_q16;
  logic [(CELLS*32)-1:0] coupling_field_q16;
  logic [(CELLS*32)-1:0] phase_projection_q30;
  logic [(CELLS*STATE_BITS)-1:0] phase_target_source;

  logic [(CELLS*STATE_BITS)-1:0] registered_target_q;
  logic registered_target_valid_q;
  logic phase_target_domain_valid;
  logic registered_target_domain_valid;
  logic target_capture_accepted;
  logic target_capture_rejected;
  logic [COUNTER_BITS-1:0] accepted_target_capture_events_q;
  logic [COUNTER_BITS-1:0] rejected_target_capture_events_q;
  logic registered_request_enable;

  logic [REQUEST_LANES-1:0] phase_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    phase_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] phase_request_target;

  logic [REQUEST_LANES-1:0] execution_request_valid;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0]
    execution_request_cell_index;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] execution_request_target;
  logic [(CELLS*STATE_BITS)-1:0] execution_target_bank;

  logic [(CELLS*STATE_BITS)-1:0] state_out;
  logic [(CELLS*STATE_BITS)-1:0] pending_route_out;

  frp_m31_scheduler_mode_e scheduler_mode_q;
  frp_m31_scheduler_state_e scheduler_state_q;
  logic [COUNTER_BITS-1:0] ticks_recorded_q;
  logic [COUNTER_BITS-1:0] scheduler_count_free_q;
  logic [COUNTER_BITS-1:0] scheduler_count_balance_q;
  logic [COUNTER_BITS-1:0] scheduler_count_commit_q;
  logic [COUNTER_BITS-1:0] scheduler_count_excite_q;
  logic [COUNTER_BITS-1:0] scheduler_count_neutralize_q;

  logic [REQUEST_LANES-1:0] request_accept;
  logic [REQUEST_LANES-1:0] request_reject;
  logic [CELLS-1:0] accepted_cell_mask;
  logic [CELLS-1:0] neutral_routed_cell_mask;
  logic [CELLS-1:0] accepted_change_mask;
  logic [COUNTER_BITS-1:0] accepted_changes;
  logic [COUNTER_BITS-1:0] capacity_remaining;
  logic capacity_exhausted;
  logic [COUNTER_BITS-1:0] switch_load_numerator;

  logic [COUNTER_BITS-1:0] requested_direct_events;
  logic [COUNTER_BITS-1:0] prevented_direct_events;
  logic [COUNTER_BITS-1:0] neutral_routed_events;
  logic [COUNTER_BITS-1:0] actual_direct_events;
  logic [COUNTER_BITS-1:0] reserved_state_events;
  logic [COUNTER_BITS-1:0] queue_overflow_events;
  logic [FRP_M31_INVARIANT_FLAGS-1:0] invariant_flags;

  logic signed [31:0] pair_coherence_q30;
  logic signed [31:0] cluster_coherence_q30;
  logic signed [31:0] global_coherence_q30;
  logic signed [31:0] organization_dispersion_q30;
  logic signed [31:0] normalized_cycle_cost_q16;
  logic signed [31:0] temperature_proxy_q16;
  logic signed [31:0] peak_temperature_proxy_q16;
  logic [31:0] thermal_sample_count_q;
  logic signed [31:0] coherence_capacity_q16;
  logic signed [31:0] pressure_q16;
  logic signed [31:0] stability_margin_q16;
  logic stable;

  initial begin
    clk = 1'b0;
    forever #5 clk = ~clk;
  end

  frp_m32_core #(
    .CELLS(CELLS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) dut (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode(scheduler_mode),
    .phase_load_valid(phase_load_valid),
    .phase_load(phase_load),
    .frequency_load_q16(frequency_load_q16),
    .gamma_effective_word(gamma_effective_word),
    .thermal_node_factor_q30(thermal_node_factor_q30),
    .auto_target_enable(auto_target_enable),
    .external_request_valid(external_request_valid),
    .external_request_cell_index(external_request_cell_index),
    .external_request_target(external_request_target),
    .external_target_bank(external_target_bank),
    .phase_word_q(phase_word_q),
    .frequency_current_q16(frequency_current_q16),
    .coupling_field_q16(coupling_field_q16),
    .phase_projection_q30(phase_projection_q30),
    .phase_target_source(phase_target_source),
    .registered_target_q(registered_target_q),
    .registered_target_valid_q(registered_target_valid_q),
    .phase_target_domain_valid(phase_target_domain_valid),
    .registered_target_domain_valid(registered_target_domain_valid),
    .target_capture_accepted(target_capture_accepted),
    .target_capture_rejected(target_capture_rejected),
    .accepted_target_capture_events_q(accepted_target_capture_events_q),
    .rejected_target_capture_events_q(rejected_target_capture_events_q),
    .registered_request_enable(registered_request_enable),
    .phase_request_valid(phase_request_valid),
    .phase_request_cell_index(phase_request_cell_index),
    .phase_request_target(phase_request_target),
    .execution_request_valid(execution_request_valid),
    .execution_request_cell_index(execution_request_cell_index),
    .execution_request_target(execution_request_target),
    .execution_target_bank(execution_target_bank),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q),
    .request_accept(request_accept),
    .request_reject(request_reject),
    .accepted_cell_mask(accepted_cell_mask),
    .neutral_routed_cell_mask(neutral_routed_cell_mask),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .capacity_remaining(capacity_remaining),
    .capacity_exhausted(capacity_exhausted),
    .switch_load_numerator(switch_load_numerator),
    .requested_direct_events(requested_direct_events),
    .prevented_direct_events(prevented_direct_events),
    .neutral_routed_events(neutral_routed_events),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags),
    .pair_coherence_q30(pair_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .global_coherence_q30(global_coherence_q30),
    .organization_dispersion_q30(organization_dispersion_q30),
    .normalized_cycle_cost_q16(normalized_cycle_cost_q16),
    .temperature_proxy_q16(temperature_proxy_q16),
    .peak_temperature_proxy_q16(peak_temperature_proxy_q16),
    .thermal_sample_count_q(thermal_sample_count_q),
    .coherence_capacity_q16(coherence_capacity_q16),
    .pressure_q16(pressure_q16),
    .stability_margin_q16(stability_margin_q16),
    .stable(stable)
  );

  frp_m31_assertions #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .COUNTER_BITS(COUNTER_BITS)
  ) inherited_execution_assertions (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .clear_counters(clear_counters),
    .scheduler_mode_q(scheduler_mode_q),
    .scheduler_state_q(scheduler_state_q),
    .ticks_recorded_q(ticks_recorded_q),
    .scheduler_count_free_q(scheduler_count_free_q),
    .scheduler_count_balance_q(scheduler_count_balance_q),
    .scheduler_count_commit_q(scheduler_count_commit_q),
    .scheduler_count_excite_q(scheduler_count_excite_q),
    .scheduler_count_neutralize_q(scheduler_count_neutralize_q),
    .state_out(state_out),
    .pending_route_out(pending_route_out),
    .request_accept(request_accept),
    .request_reject(request_reject),
    .accepted_cell_mask(accepted_cell_mask),
    .neutral_routed_cell_mask(neutral_routed_cell_mask),
    .accepted_change_mask(accepted_change_mask),
    .accepted_changes(accepted_changes),
    .capacity_remaining(capacity_remaining),
    .capacity_exhausted(capacity_exhausted),
    .switch_load_numerator(switch_load_numerator),
    .requested_direct_events(requested_direct_events),
    .prevented_direct_events(prevented_direct_events),
    .neutral_routed_events(neutral_routed_events),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events),
    .invariant_flags(invariant_flags)
  );

  frp_m31_phase_thermal_assertions #(
    .CELLS(CELLS),
    .COUNTER_BITS(COUNTER_BITS)
  ) inherited_phase_thermal_assertions (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_enable),
    .state_out(state_out),
    .phase_target(phase_target_source),
    .phase_projection_q30(phase_projection_q30),
    .pair_coherence_q30(pair_coherence_q30),
    .cluster_coherence_q30(cluster_coherence_q30),
    .global_coherence_q30(global_coherence_q30),
    .organization_dispersion_q30(organization_dispersion_q30),
    .temperature_proxy_q16(temperature_proxy_q16),
    .peak_temperature_proxy_q16(peak_temperature_proxy_q16),
    .actual_direct_events(actual_direct_events),
    .reserved_state_events(reserved_state_events),
    .queue_overflow_events(queue_overflow_events)
  );

  function automatic logic [STATE_BITS-1:0] cell_state(
    input logic [(CELLS*STATE_BITS)-1:0] packed_state,
    input int cell_index
  );
    begin
      cell_state = packed_state[(cell_index*STATE_BITS) +: STATE_BITS];
    end
  endfunction

  function automatic logic signed [31:0] cell_s32(
    input logic [(CELLS*32)-1:0] packed_value,
    input int cell_index
  );
    begin
      cell_s32 = packed_value[(cell_index*32) +: 32];
    end
  endfunction

  function automatic logic [CELL_INDEX_BITS-1:0] lane_cell_index(
    input int lane_index
  );
    begin
      lane_cell_index = execution_request_cell_index[
        (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
      ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] lane_target(
    input int lane_index
  );
    begin
      lane_target = execution_request_target[
        (lane_index*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction

  function automatic logic execution_request_for_cell(
    input int cell_index
  );
    begin
      execution_request_for_cell = 1'b0;
      for (int lane_index = 0; lane_index < REQUEST_LANES; lane_index++) begin
        if (
          execution_request_valid[lane_index]
          && (lane_cell_index(lane_index)
            == cell_index[CELL_INDEX_BITS-1:0])
        ) begin
          execution_request_for_cell = 1'b1;
        end
      end
    end
  endfunction

  function automatic integer ternary_value(
    input logic [STATE_BITS-1:0] state_value
  );
    begin
      case (state_value)
        FRP_STATE_NEG: ternary_value = -1;
        FRP_ACTIVE_NEUTRAL: ternary_value = 0;
        FRP_STATE_POS: ternary_value = 1;
        default: ternary_value = 2;
      endcase
    end
  endfunction

  task automatic set_phase(
    input int cell_index,
    input logic [31:0] value
  );
    begin
      phase_load[(cell_index*32) +: 32] = value;
    end
  endtask

  task automatic load_phases;
    begin
      @(negedge clk);
      phase_load_valid = 1'b1;
      @(negedge clk);
      phase_load_valid = 1'b0;
      #1;
    end
  endtask

  task automatic start_tick(
    input frp_m31_scheduler_state_e expected_state
  );
    begin
      @(negedge clk);
      if (scheduler_state_q !== expected_state) begin
        $fatal(
          1,
          "FRP M32 1/7 TB: scheduler mismatch expected=%0d actual=%0d",
          expected_state,
          scheduler_state_q
        );
      end
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

  initial begin : qualification_sequence
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    scheduler_mode = FRP_MODE_1_7;
    phase_load_valid = 1'b0;
    phase_load = '0;
    frequency_load_q16 = '0;
    gamma_effective_word = '0;
    thermal_node_factor_q30 = '0;
    auto_target_enable = 1'b0;
    external_request_valid = '0;
    external_request_cell_index = '0;
    external_request_target = '0;
    external_target_bank = '0;

    for (int cell_index = 0; cell_index < CELLS; cell_index++) begin
      frequency_load_q16[(cell_index*32) +: 32] =
        FRP_M31_BASE_FREQUENCY_Q16;
      gamma_effective_word[(cell_index*32) +: 32] =
        FRP_M31_GAMMA_NOMINAL;
      thermal_node_factor_q30[(cell_index*32) +: 32] =
        FRP_M31_Q30_ONE;
    end

    repeat (3) @(negedge clk);
    rst_n = 1'b1;
    repeat (2) @(negedge clk);
    #1;

    if (scheduler_mode_q !== FRP_MODE_1_7)
      $fatal(1, "FRP M32 1/7 TB: scheduler mode registration mismatch");
    if (scheduler_state_q !== FRP_SCHED_EXCITE)
      $fatal(1, "FRP M32 1/7 TB: initial excite state mismatch");
    if (state_out !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 1/7 TB: reset state is not active zero");
    if (pending_route_out !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 1/7 TB: reset pending-route word mismatch");
    if (registered_target_valid_q)
      $fatal(1, "FRP M32 1/7 TB: reset target validity mismatch");

    phase_load = '0;
    set_phase(0, 32'h40000000);
    load_phases();

    if (cell_s32(phase_projection_q30, 0) !== FRP_M31_Q30_ONE)
      $fatal(1, "FRP M32 1/7 TB: positive phase projection mismatch");
    if (cell_state(phase_target_source, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 1/7 TB: positive source target mismatch");
    if (!phase_target_domain_valid || !registered_target_domain_valid)
      $fatal(1, "FRP M32 1/7 TB: target domain mismatch");

    auto_target_enable = 1'b1;
    #1;

    for (int tick = 0; tick < 17; tick++) begin
      frp_m31_scheduler_state_e expected_scheduler;
      logic [STATE_BITS-1:0] source_before_tick;
      logic [STATE_BITS-1:0] registered_before_tick;
      logic [STATE_BITS-1:0] execution_before_tick;
      logic registered_valid_before_tick;
      logic capture_before_tick;
      logic request_before_tick;
      logic first_leg_before_tick;
      logic second_leg_before_tick;

      expected_scheduler = ((tick % 8) == 0)
        ? FRP_SCHED_EXCITE
        : FRP_SCHED_NEUTRALIZE;

      if (tick == 9) begin
        phase_load = phase_word_q;
        set_phase(0, 32'hC0000000);
        load_phases();

        if (cell_state(phase_target_source, 0) !== FRP_STATE_NEG)
          $fatal(1, "FRP M32 1/7 TB: opposite source target mismatch");
        if (cell_state(registered_target_q, 0) !== FRP_STATE_POS)
          $fatal(1, "FRP M32 1/7 TB: source bypassed target register");
        if (cell_state(execution_target_bank, 0) !== FRP_STATE_POS)
          $fatal(1, "FRP M32 1/7 TB: source bypassed execution target");
      end

      start_tick(expected_scheduler);

      if (!target_capture_accepted || target_capture_rejected)
        $fatal(1, "FRP M32 1/7 TB: target capture mismatch");
      if (execution_target_bank !== registered_target_q)
        $fatal(1, "FRP M32 1/7 TB: execution target registration mismatch");

      source_before_tick = cell_state(phase_target_source, 0);
      registered_before_tick = cell_state(registered_target_q, 0);
      execution_before_tick = cell_state(execution_target_bank, 0);
      registered_valid_before_tick = registered_target_valid_q;
      capture_before_tick = target_capture_accepted;
      request_before_tick = execution_request_for_cell(0);
      first_leg_before_tick = neutral_routed_cell_mask[0];
      second_leg_before_tick =
        accepted_change_mask[0]
        && (cell_state(state_out, 0) == FRP_ACTIVE_NEUTRAL)
        && (cell_state(pending_route_out, 0) == FRP_STATE_NEG);

      if (tick == 0) begin
        if (execution_request_for_cell(0)) begin
          $fatal(1, "FRP M32 1/7 TB: unregistered source formed request");
        end
      end else if (tick < 8) begin
        if (execution_request_for_cell(0))
          $fatal(1, "FRP M32 1/7 TB: neutralize admitted zero release");
      end else if (tick == 8) begin
        if (!execution_request_valid[0]
            || (lane_cell_index(0) !== 3'd0)
            || (lane_target(0) !== FRP_STATE_POS)) begin
          $fatal(1, "FRP M32 1/7 TB: excite release request mismatch");
        end
      end else if (tick == 9) begin
        if (execution_request_for_cell(0))
          $fatal(1, "FRP M32 1/7 TB: source bypassed capture tick");
      end else if (tick == 10) begin
        if (!execution_request_valid[0]
            || (lane_cell_index(0) !== 3'd0)
            || (lane_target(0) !== FRP_STATE_NEG)) begin
          $fatal(1, "FRP M32 1/7 TB: opposite request mismatch");
        end
        if ((requested_direct_events !== 1)
            || (prevented_direct_events !== 1)
            || (neutral_routed_events !== 1)) begin
          $fatal(1, "FRP M32 1/7 TB: first-leg accounting mismatch");
        end
      end else if (execution_request_for_cell(0)) begin
        $fatal(1, "FRP M32 1/7 TB: pending route emitted new request");
      end

      finish_tick();

      if (tick < 8) begin
        if (cell_state(state_out, 0) !== FRP_ACTIVE_NEUTRAL)
          $fatal(1, "FRP M32 1/7 TB: pre-release state mismatch");
        if (cell_state(pending_route_out, 0) !== FRP_STATE_ZERO)
          $fatal(1, "FRP M32 1/7 TB: pre-release pending mismatch");
      end else if (tick == 8) begin
        if (cell_state(state_out, 0) !== FRP_STATE_POS)
          $fatal(1, "FRP M32 1/7 TB: excite did not release positive state");
      end else if (tick == 9) begin
        if (cell_state(registered_target_q, 0) !== FRP_STATE_NEG)
          $fatal(1, "FRP M32 1/7 TB: opposite target was not registered");
        if (cell_state(state_out, 0) !== FRP_STATE_POS)
          $fatal(1, "FRP M32 1/7 TB: capture tick changed retained state");
      end else if (tick < 16) begin
        if (cell_state(state_out, 0) !== FRP_ACTIVE_NEUTRAL)
          $fatal(1, "FRP M32 1/7 TB: first route leg state mismatch");
        if (cell_state(pending_route_out, 0) !== FRP_STATE_NEG)
          $fatal(1, "FRP M32 1/7 TB: pending polarity was not retained");
      end else begin
        if (!second_leg_before_tick)
          $fatal(1, "FRP M32 1/7 TB: second route leg was not accepted");
        if (cell_state(state_out, 0) !== FRP_STATE_NEG)
          $fatal(1, "FRP M32 1/7 TB: second route leg did not complete");
        if (cell_state(pending_route_out, 0) !== FRP_STATE_ZERO)
          $fatal(1, "FRP M32 1/7 TB: completed pending route did not clear");
      end

      if (actual_direct_events !== '0)
        $fatal(1, "FRP M32 1/7 TB: direct execution event detected");
      if (reserved_state_events !== '0)
        $fatal(1, "FRP M32 1/7 TB: reserved state event detected");
      if (queue_overflow_events !== '0)
        $fatal(1, "FRP M32 1/7 TB: pending-route overflow detected");
      if (invariant_flags !== {FRP_M31_INVARIANT_FLAGS{1'b1}})
        $fatal(1, "FRP M32 1/7 TB: inherited invariant failed");

      $write(
        "M32_MODE_1_7_TRACE tick=%0d scheduler_state=%0d ",
        tick,
        expected_scheduler
      );
      $write(
        "excite_tick=%0d neutralize_tick=%0d ",
        expected_scheduler == FRP_SCHED_EXCITE,
        expected_scheduler == FRP_SCHED_NEUTRALIZE
      );
      $write(
        "source_target=%0d registered_target=%0d ",
        ternary_value(source_before_tick),
        ternary_value(registered_before_tick)
      );
      $write(
        "registered_valid=%0d capture_accepted=%0d ",
        registered_valid_before_tick,
        capture_before_tick
      );
      $write(
        "execution_target=%0d request_valid=%0d first_leg=%0d ",
        ternary_value(execution_before_tick),
        request_before_tick,
        first_leg_before_tick
      );
      $display(
        "second_leg=%0d executed_state=%0d active_zero=%0d pending_target=%0d",
        second_leg_before_tick,
        ternary_value(cell_state(state_out, 0)),
        cell_state(state_out, 0) == FRP_ACTIVE_NEUTRAL,
        ternary_value(cell_state(pending_route_out, 0))
      );
    end

    if (accepted_target_capture_events_q !== 17)
      $fatal(1, "FRP M32 1/7 TB: accepted capture count mismatch");
    if (rejected_target_capture_events_q !== '0)
      $fatal(1, "FRP M32 1/7 TB: rejected capture count mismatch");
    if (ticks_recorded_q !== 17)
      $fatal(1, "FRP M32 1/7 TB: tick count mismatch");
    if ((scheduler_count_excite_q !== 3)
        || (scheduler_count_neutralize_q !== 14)
        || (scheduler_count_free_q !== '0)
        || (scheduler_count_balance_q !== '0)
        || (scheduler_count_commit_q !== '0)) begin
      $fatal(1, "FRP M32 1/7 TB: scheduler cadence count mismatch");
    end
    if (thermal_sample_count_q !== 17)
      $fatal(1, "FRP M32 1/7 TB: thermal sample count mismatch");
    if (temperature_proxy_q16 <= 0)
      $fatal(1, "FRP M32 1/7 TB: thermal proxy did not integrate activity");
    if (cell_s32(frequency_current_q16, 0)
        === FRP_M31_BASE_FREQUENCY_Q16) begin
      $fatal(1, "FRP M32 1/7 TB: retained frequency did not evolve");
    end
    if (!stable)
      $fatal(1, "FRP M32 1/7 TB: stability state mismatch");

    $display("FRP_M32_REGISTERED_TARGET_MODE_1_7_TB: PASS");
    $finish;
  end

endmodule

`endif
