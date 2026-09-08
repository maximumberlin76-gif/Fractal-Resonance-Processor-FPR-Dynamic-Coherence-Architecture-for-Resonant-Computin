// SPDX-License-Identifier: Apache-2.0
// FRP M32 deterministic integrated registered-target core testbench.

`ifndef FRP_M32_CORE_TB_SV
`define FRP_M32_CORE_TB_SV

`timescale 1ns / 1ps

`include "frp_m32_core.sv"
`include "frp_m31_phase_thermal_assertions.sv"

module frp_m32_core_tb;

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

  logic [(CELLS*STATE_BITS)-1:0] first_source_snapshot;
  logic [(CELLS*STATE_BITS)-1:0] opposite_source_snapshot;

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
    input logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] packed_index,
    input int lane_index
  );
    begin
      lane_cell_index = packed_index[
        (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
      ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] lane_target(
    input logic [(REQUEST_LANES*STATE_BITS)-1:0] packed_target,
    input int lane_index
  );
    begin
      lane_target = packed_target[
        (lane_index*STATE_BITS) +: STATE_BITS
      ];
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

  task automatic load_phases;
    begin
      @(negedge clk);
      phase_load_valid = 1'b1;
      @(negedge clk);
      phase_load_valid = 1'b0;
      #1;
    end
  endtask

  initial begin : qualification_sequence
    rst_n = 1'b0;
    tick_enable = 1'b0;
    clear_counters = 1'b0;
    scheduler_mode = FRP_MODE_FREE;
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
    first_source_snapshot = '0;
    opposite_source_snapshot = '0;

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

    if (REQUEST_LANES != 2)
      $fatal(1, "FRP M32 core TB: eight-cell profile must expose two lanes");
    if (state_out !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: reset state is not active zero");
    if (pending_route_out !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: reset pending-route word mismatch");
    if (registered_target_q !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: reset registered target mismatch");
    if (registered_target_valid_q || registered_request_enable)
      $fatal(1, "FRP M32 core TB: reset registered validity mismatch");
    if (execution_request_valid !== '0)
      $fatal(1, "FRP M32 core TB: reset execution request mismatch");

    phase_load = '0;
    set_phase(0, 32'h40000000);
    set_phase(1, 32'hC0000000);
    load_phases();

    if (cell_s32(phase_projection_q30, 0) !== FRP_M31_Q30_ONE)
      $fatal(1, "FRP M32 core TB: positive phase projection mismatch");
    if (cell_s32(phase_projection_q30, 1) !== -FRP_M31_Q30_ONE)
      $fatal(1, "FRP M32 core TB: negative phase projection mismatch");
    if (cell_state(phase_target_source, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: positive source target mismatch");
    if (cell_state(phase_target_source, 1) !== FRP_STATE_NEG)
      $fatal(1, "FRP M32 core TB: negative source target mismatch");
    if (!phase_target_domain_valid || !registered_target_domain_valid)
      $fatal(1, "FRP M32 core TB: target domain mismatch");
    if (coupling_field_q16 === '0)
      $fatal(1, "FRP M32 core TB: relative-phase coupling field is zero");

    first_source_snapshot = phase_target_source;
    auto_target_enable = 1'b1;
    #1;
    if (execution_target_bank !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: source bypassed registered target bank");
    if (execution_request_valid !== '0)
      $fatal(1, "FRP M32 core TB: unregistered source formed a request");

    start_tick();
    if (!target_capture_accepted || target_capture_rejected)
      $fatal(1, "FRP M32 core TB: first target capture mismatch");
    if (registered_target_q !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: source changed target before clock edge");
    if (state_out !== {CELLS{FRP_ACTIVE_NEUTRAL}})
      $fatal(1, "FRP M32 core TB: unregistered source changed state");
    finish_tick();

    if (registered_target_q !== first_source_snapshot)
      $fatal(1, "FRP M32 core TB: first source was not registered");
    if (!registered_target_valid_q || !registered_request_enable)
      $fatal(1, "FRP M32 core TB: registered request gate did not open");
    if (execution_target_bank !== registered_target_q)
      $fatal(1, "FRP M32 core TB: execution target is not registered target");
    if (phase_request_valid !== 2'b11)
      $fatal(1, "FRP M32 core TB: initial phase request mask mismatch");
    if (execution_request_valid !== phase_request_valid)
      $fatal(1, "FRP M32 core TB: automatic request mux mismatch");
    if ((lane_cell_index(execution_request_cell_index, 0) !== 3'd0)
        || (lane_target(execution_request_target, 0) !== FRP_STATE_POS)) begin
      $fatal(1, "FRP M32 core TB: positive request lane mismatch");
    end
    if ((lane_cell_index(execution_request_cell_index, 1) !== 3'd1)
        || (lane_target(execution_request_target, 1) !== FRP_STATE_NEG)) begin
      $fatal(1, "FRP M32 core TB: negative request lane mismatch");
    end

    start_tick();
    if (execution_target_bank !== registered_target_q)
      $fatal(1, "FRP M32 core TB: registered target changed during execute");
    finish_tick();

    if (cell_state(state_out, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: active zero did not commit positive target");
    if (cell_state(state_out, 1) !== FRP_STATE_NEG)
      $fatal(1, "FRP M32 core TB: active zero did not commit negative target");
    if (cell_s32(frequency_current_q16, 0)
        === FRP_M31_BASE_FREQUENCY_Q16) begin
      $fatal(1, "FRP M32 core TB: retained frequency did not record activity");
    end

    phase_load = phase_word_q;
    set_phase(0, 32'hC0000000);
    load_phases();

    if (cell_state(phase_target_source, 0) !== FRP_STATE_NEG)
      $fatal(1, "FRP M32 core TB: opposite source target mismatch");
    if (cell_state(registered_target_q, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: source bypassed prior registered target");
    if (cell_state(execution_target_bank, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: source bypassed execution target bank");
    opposite_source_snapshot = phase_target_source;

    start_tick();
    if (cell_state(registered_target_q, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: opposite source bypassed clock boundary");
    finish_tick();

    if (registered_target_q !== opposite_source_snapshot)
      $fatal(1, "FRP M32 core TB: opposite source was not registered");
    if (cell_state(state_out, 0) !== FRP_STATE_POS)
      $fatal(1, "FRP M32 core TB: source changed retained state directly");
    if (execution_target_bank !== registered_target_q)
      $fatal(1, "FRP M32 core TB: opposite execution target mismatch");

    start_tick();
    if (execution_request_valid[0] !== 1'b1)
      $fatal(1, "FRP M32 core TB: opposite request was not formed");
    if ((lane_cell_index(execution_request_cell_index, 0) !== 3'd0)
        || (lane_target(execution_request_target, 0) !== FRP_STATE_NEG)) begin
      $fatal(1, "FRP M32 core TB: opposite request lane mismatch");
    end
    if ((requested_direct_events !== 1)
        || (prevented_direct_events !== 1)
        || (neutral_routed_events !== 1)) begin
      $fatal(1, "FRP M32 core TB: opposite-route event accounting mismatch");
    end
    finish_tick();

    if (cell_state(state_out, 0) !== FRP_ACTIVE_NEUTRAL)
      $fatal(1, "FRP M32 core TB: first route leg did not enter active zero");
    if (cell_state(pending_route_out, 0) !== FRP_STATE_NEG)
      $fatal(1, "FRP M32 core TB: opposite target was not retained");

    start_tick();
    finish_tick();

    if (cell_state(state_out, 0) !== FRP_STATE_NEG)
      $fatal(1, "FRP M32 core TB: second route leg did not complete");
    if (cell_state(pending_route_out, 0) !== FRP_STATE_ZERO)
      $fatal(1, "FRP M32 core TB: completed pending route did not clear");

    if (accepted_target_capture_events_q !== 5)
      $fatal(1, "FRP M32 core TB: accepted target capture count mismatch");
    if (rejected_target_capture_events_q !== '0)
      $fatal(1, "FRP M32 core TB: unexpected rejected target capture");
    if (ticks_recorded_q !== 5)
      $fatal(1, "FRP M32 core TB: integrated tick count mismatch");
    if (scheduler_count_free_q !== 5)
      $fatal(1, "FRP M32 core TB: free scheduler count mismatch");
    if ((scheduler_count_balance_q !== '0)
        || (scheduler_count_commit_q !== '0)
        || (scheduler_count_excite_q !== '0)
        || (scheduler_count_neutralize_q !== '0)) begin
      $fatal(1, "FRP M32 core TB: inactive scheduler count mismatch");
    end
    if (thermal_sample_count_q !== 5)
      $fatal(1, "FRP M32 core TB: thermal sample count mismatch");
    if (temperature_proxy_q16 <= 0)
      $fatal(1, "FRP M32 core TB: thermal proxy did not integrate activity");
    if (!stable)
      $fatal(1, "FRP M32 core TB: qualified profile lost stability margin");
    if (actual_direct_events !== '0)
      $fatal(1, "FRP M32 core TB: direct opposite-polarity event detected");
    if (reserved_state_events !== '0)
      $fatal(1, "FRP M32 core TB: reserved state detected");
    if (queue_overflow_events !== '0)
      $fatal(1, "FRP M32 core TB: pending-route overflow detected");
    if (invariant_flags !== {FRP_M31_INVARIANT_FLAGS{1'b1}})
      $fatal(1, "FRP M32 core TB: inherited execution invariant failed");

    $display("FRP_M32_INTEGRATED_REGISTERED_TARGET_CORE_TB: PASS");
    $display(
      "source/registered/request/execution/active-zero/frequency/thermal: PASS"
    );
    $finish;
  end

endmodule

`endif
