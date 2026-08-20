// SPDX-License-Identifier: Apache-2.0
//
// FRP M22 deterministic integration-facing control, status, and register
// boundary around the qualified M16 execution core.

`ifndef FRP_M22_CONTROL_STATUS_REGISTER_INTERFACE_SV
`define FRP_M22_CONTROL_STATUS_REGISTER_INTERFACE_SV

`include "frp_m16_core.sv"
`include "frp_m22_csr_pkg.sv"

module frp_m22_control_status_register_interface #(
  parameter int CELLS = frp_m16_pkg::FRP_M16_DEFAULT_CELLS,
  parameter int STATE_BITS = frp_m16_pkg::FRP_M16_STATE_BITS,
  parameter int REQUEST_LANES = frp_m16_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS),
  parameter int COUNTER_BITS = frp_m16_pkg::FRP_M16_COUNTER_BITS
) (
  input logic clk,
  input logic rst_n,

  input logic csr_valid,
  input logic csr_write,
  input frp_m22_csr_pkg::frp_m22_csr_addr_t csr_addr,
  input frp_m22_csr_pkg::frp_m22_csr_data_t csr_wdata,

  output logic csr_ready,
  output logic csr_error,
  output frp_m22_csr_pkg::frp_m22_csr_data_t csr_rdata
);

  import frp_m16_pkg::*;
  import frp_m22_csr_pkg::*;

  logic [FRP_M16_SCHED_MODE_BITS-1:0] scheduler_mode_control_q;
  logic [CELL_INDEX_BITS-1:0] request_lane_select_q;
  logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] request_cell_index_q;
  logic [(REQUEST_LANES*STATE_BITS)-1:0] request_target_q;
  logic [REQUEST_LANES-1:0] request_valid_q;
  logic [CELL_INDEX_BITS-1:0] observe_cell_index_q;
  logic [(CELLS*STATE_BITS)-1:0] target_q;

  logic tick_pulse;
  logic clear_counters_pulse;
  logic clear_requests_pulse;
  logic accepted_write;
  logic write_payload_valid;

  logic [(CELLS*STATE_BITS)-1:0] state_out;
  logic [(CELLS*STATE_BITS)-1:0] pending_route_out;
  frp_m16_scheduler_mode_e scheduler_mode_q;
  frp_m16_scheduler_state_e scheduler_state_q;
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
  logic [FRP_M16_INVARIANT_FLAGS-1:0] invariant_flags;

  logic [REQUEST_LANES-1:0] request_accept_snapshot_q;
  logic [REQUEST_LANES-1:0] request_reject_snapshot_q;
  logic [COUNTER_BITS-1:0] accepted_changes_snapshot_q;
  logic [COUNTER_BITS-1:0] capacity_remaining_snapshot_q;
  logic capacity_exhausted_snapshot_q;
  logic [COUNTER_BITS-1:0] switch_load_snapshot_q;
  logic [COUNTER_BITS-1:0] requested_direct_snapshot_q;
  logic [COUNTER_BITS-1:0] prevented_direct_snapshot_q;
  logic [COUNTER_BITS-1:0] neutral_routed_snapshot_q;
  logic [COUNTER_BITS-1:0] actual_direct_snapshot_q;
  logic [COUNTER_BITS-1:0] reserved_state_snapshot_q;
  logic [COUNTER_BITS-1:0] queue_overflow_snapshot_q;

  function automatic logic [CELL_INDEX_BITS-1:0] lane_cell_index(
    input int lane_index
  );
    begin
      lane_cell_index = request_cell_index_q[
        (lane_index*CELL_INDEX_BITS) +: CELL_INDEX_BITS
      ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] lane_target(
    input int lane_index
  );
    begin
      lane_target = request_target_q[
        (lane_index*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction

  function automatic logic [STATE_BITS-1:0] observed_state(
    input logic [(CELLS*STATE_BITS)-1:0] packed_value
  );
    begin
      observed_state = packed_value[
        (int'(observe_cell_index_q)*STATE_BITS) +: STATE_BITS
      ];
    end
  endfunction

  initial begin
    if (!((CELLS == 8) || (CELLS == 16) || (CELLS == 32))) begin
      $fatal(1, "FRP M22: CELLS is outside the M21-qualified profiles");
    end
    if (REQUEST_LANES != frp_calc_request_lanes(CELLS)) begin
      $fatal(1, "FRP M22: REQUEST_LANES does not match CELLS/4");
    end
    if (STATE_BITS != FRP_M16_STATE_BITS) begin
      $fatal(1, "FRP M22: STATE_BITS differs from the M16 contract");
    end
    if (COUNTER_BITS != FRP_M16_COUNTER_BITS) begin
      $fatal(1, "FRP M22: COUNTER_BITS differs from the M16 contract");
    end
  end

  always_comb begin
    target_q = '0;
    for (int lane_index = 0; lane_index < REQUEST_LANES; lane_index++) begin
      int cell_index;
      cell_index = int'(lane_cell_index(lane_index));
      if (request_valid_q[lane_index] && (cell_index < CELLS)) begin
        target_q[(cell_index*STATE_BITS) +: STATE_BITS] =
          lane_target(lane_index);
      end
    end
  end

  always_comb begin
    write_payload_valid = 1'b0;
    unique case (csr_addr)
      FRP_M22_ADDR_CONTROL: begin
        write_payload_valid =
          (csr_wdata == FRP_M22_CONTROL_TICK)
          || (csr_wdata == FRP_M22_CONTROL_CLEAR_COUNTERS)
          || (csr_wdata == FRP_M22_CONTROL_CLEAR_REQUESTS);
      end
      FRP_M22_ADDR_SCHEDULER_MODE: begin
        write_payload_valid =
          (csr_wdata[31:2] == '0)
          && (csr_wdata[1:0] != FRP_MODE_RESERVED);
      end
      FRP_M22_ADDR_REQUEST_LANE_SELECT: begin
        write_payload_valid =
          ($unsigned(csr_wdata) < REQUEST_LANES);
      end
      FRP_M22_ADDR_REQUEST_CELL_INDEX: begin
        write_payload_valid =
          ($unsigned(csr_wdata) < CELLS);
      end
      FRP_M22_ADDR_REQUEST_TARGET: begin
        write_payload_valid =
          (csr_wdata == 32'h00000000)
          || (csr_wdata == 32'h00000001)
          || (csr_wdata == 32'h00000003);
      end
      FRP_M22_ADDR_REQUEST_VALID: begin
        write_payload_valid =
          (csr_wdata == 32'h00000000)
          || (csr_wdata == 32'h00000001);
      end
      FRP_M22_ADDR_OBSERVE_CELL_INDEX: begin
        write_payload_valid =
          ($unsigned(csr_wdata) < CELLS);
      end
      default: begin
        write_payload_valid = 1'b0;
      end
    endcase
  end

  always_comb begin
    csr_ready = 1'b0;
    csr_error = 1'b0;

    if (csr_valid) begin
      csr_ready = 1'b1;
      if (
        !frp_m22_is_word_aligned(csr_addr)
        || !frp_m22_is_defined_address(csr_addr)
      ) begin
        csr_error = 1'b1;
      end else if (csr_write) begin
        if (
          !frp_m22_is_writable_address(csr_addr)
          || !write_payload_valid
        ) begin
          csr_error = 1'b1;
        end
      end else if (!frp_m22_is_readable_address(csr_addr)) begin
        csr_error = 1'b1;
      end
    end
  end

  always_comb begin
    csr_rdata = '0;
    if (
      csr_valid
      && !csr_write
      && !csr_error
    ) begin
      unique case (csr_addr)
        FRP_M22_ADDR_SCHEDULER_MODE: begin
          csr_rdata[FRP_M16_SCHED_MODE_BITS-1:0] =
            scheduler_mode_control_q;
        end
        FRP_M22_ADDR_REQUEST_LANE_SELECT: begin
          csr_rdata[CELL_INDEX_BITS-1:0] = request_lane_select_q;
        end
        FRP_M22_ADDR_REQUEST_CELL_INDEX: begin
          csr_rdata[CELL_INDEX_BITS-1:0] =
            lane_cell_index(int'(request_lane_select_q));
        end
        FRP_M22_ADDR_REQUEST_TARGET: begin
          csr_rdata[STATE_BITS-1:0] =
            lane_target(int'(request_lane_select_q));
        end
        FRP_M22_ADDR_REQUEST_VALID: begin
          csr_rdata[0] = request_valid_q[int'(request_lane_select_q)];
        end
        FRP_M22_ADDR_OBSERVE_CELL_INDEX: begin
          csr_rdata[CELL_INDEX_BITS-1:0] = observe_cell_index_q;
        end
        FRP_M22_ADDR_STATUS: begin
          if (rst_n) begin
            csr_rdata[FRP_M22_STATUS_READY] = 1'b1;
            csr_rdata[FRP_M22_STATUS_CAPACITY_EXHAUSTED] =
              capacity_exhausted_snapshot_q;
            csr_rdata[FRP_M22_STATUS_REQUEST_ACCEPTED] =
              |request_accept_snapshot_q;
            csr_rdata[FRP_M22_STATUS_REQUEST_REJECTED] =
              |request_reject_snapshot_q;
            csr_rdata[FRP_M22_STATUS_PENDING_ACTIVE] =
              |pending_route_out;
            csr_rdata[FRP_M22_STATUS_INVARIANT_FAILURE] =
              !( &invariant_flags );
            csr_rdata[FRP_M22_STATUS_ACTUAL_DIRECT_NONZERO] =
              |actual_direct_snapshot_q;
            csr_rdata[FRP_M22_STATUS_RESERVED_STATE_NONZERO] =
              |reserved_state_snapshot_q;
            csr_rdata[FRP_M22_STATUS_QUEUE_OVERFLOW_NONZERO] =
              |queue_overflow_snapshot_q;
          end
        end
        FRP_M22_ADDR_SCHEDULER_MODE_ACTIVE: begin
          csr_rdata[FRP_M16_SCHED_MODE_BITS-1:0] = scheduler_mode_q;
        end
        FRP_M22_ADDR_SCHEDULER_STATE: begin
          csr_rdata[FRP_M16_SCHED_BITS-1:0] = scheduler_state_q;
        end
        FRP_M22_ADDR_TICKS_RECORDED: begin
          csr_rdata = ticks_recorded_q;
        end
        FRP_M22_ADDR_REQUEST_ACCEPT: begin
          csr_rdata[REQUEST_LANES-1:0] = request_accept_snapshot_q;
        end
        FRP_M22_ADDR_REQUEST_REJECT: begin
          csr_rdata[REQUEST_LANES-1:0] = request_reject_snapshot_q;
        end
        FRP_M22_ADDR_RETAINED_STATE: begin
          csr_rdata[STATE_BITS-1:0] = observed_state(state_out);
        end
        FRP_M22_ADDR_PENDING_ROUTE: begin
          csr_rdata[STATE_BITS-1:0] = observed_state(pending_route_out);
        end
        FRP_M22_ADDR_ACCEPTED_CHANGES: begin
          csr_rdata = accepted_changes_snapshot_q;
        end
        FRP_M22_ADDR_CAPACITY_REMAINING: begin
          csr_rdata = capacity_remaining_snapshot_q;
        end
        FRP_M22_ADDR_CAPACITY_EXHAUSTED: begin
          csr_rdata[0] = capacity_exhausted_snapshot_q;
        end
        FRP_M22_ADDR_SWITCH_LOAD_NUMERATOR: begin
          csr_rdata = switch_load_snapshot_q;
        end
        FRP_M22_ADDR_INVARIANT_FLAGS: begin
          if (rst_n) begin
            csr_rdata[FRP_M16_INVARIANT_FLAGS-1:0] = invariant_flags;
          end
        end
        FRP_M22_ADDR_REQUESTED_DIRECT_EVENTS: begin
          csr_rdata = requested_direct_snapshot_q;
        end
        FRP_M22_ADDR_PREVENTED_DIRECT_EVENTS: begin
          csr_rdata = prevented_direct_snapshot_q;
        end
        FRP_M22_ADDR_NEUTRAL_ROUTED_EVENTS: begin
          csr_rdata = neutral_routed_snapshot_q;
        end
        FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS: begin
          csr_rdata = actual_direct_snapshot_q;
        end
        FRP_M22_ADDR_RESERVED_STATE_EVENTS: begin
          csr_rdata = reserved_state_snapshot_q;
        end
        FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS: begin
          csr_rdata = queue_overflow_snapshot_q;
        end
        default: begin
          csr_rdata = '0;
        end
      endcase
    end
  end

  assign accepted_write =
    csr_valid
    && csr_ready
    && csr_write
    && !csr_error;

  assign tick_pulse =
    accepted_write
    && (csr_addr == FRP_M22_ADDR_CONTROL)
    && (csr_wdata == FRP_M22_CONTROL_TICK);

  assign clear_counters_pulse =
    accepted_write
    && (csr_addr == FRP_M22_ADDR_CONTROL)
    && (csr_wdata == FRP_M22_CONTROL_CLEAR_COUNTERS);

  assign clear_requests_pulse =
    accepted_write
    && (csr_addr == FRP_M22_ADDR_CONTROL)
    && (csr_wdata == FRP_M22_CONTROL_CLEAR_REQUESTS);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      scheduler_mode_control_q <= FRP_MODE_FREE;
      request_lane_select_q <= '0;
      request_cell_index_q <= '0;
      request_target_q <= '0;
      request_valid_q <= '0;
      observe_cell_index_q <= '0;
      request_accept_snapshot_q <= '0;
      request_reject_snapshot_q <= '0;
      accepted_changes_snapshot_q <= '0;
      capacity_remaining_snapshot_q <= '0;
      capacity_exhausted_snapshot_q <= 1'b0;
      switch_load_snapshot_q <= '0;
      requested_direct_snapshot_q <= '0;
      prevented_direct_snapshot_q <= '0;
      neutral_routed_snapshot_q <= '0;
      actual_direct_snapshot_q <= '0;
      reserved_state_snapshot_q <= '0;
      queue_overflow_snapshot_q <= '0;
    end else begin
      if (tick_pulse) begin
        request_accept_snapshot_q <= request_accept;
        request_reject_snapshot_q <= request_reject;
        accepted_changes_snapshot_q <= accepted_changes;
        capacity_remaining_snapshot_q <= capacity_remaining;
        capacity_exhausted_snapshot_q <= capacity_exhausted;
        switch_load_snapshot_q <= switch_load_numerator;
        requested_direct_snapshot_q <= requested_direct_events;
        prevented_direct_snapshot_q <= prevented_direct_events;
        neutral_routed_snapshot_q <= neutral_routed_events;
        actual_direct_snapshot_q <= actual_direct_events;
        reserved_state_snapshot_q <= reserved_state_events;
        queue_overflow_snapshot_q <= queue_overflow_events;
        request_valid_q <= '0;
      end

      if (clear_counters_pulse) begin
        request_accept_snapshot_q <= '0;
        request_reject_snapshot_q <= '0;
        accepted_changes_snapshot_q <= '0;
        capacity_remaining_snapshot_q <= '0;
        capacity_exhausted_snapshot_q <= 1'b0;
        switch_load_snapshot_q <= '0;
        requested_direct_snapshot_q <= '0;
        prevented_direct_snapshot_q <= '0;
        neutral_routed_snapshot_q <= '0;
        actual_direct_snapshot_q <= '0;
        reserved_state_snapshot_q <= '0;
        queue_overflow_snapshot_q <= '0;
      end

      if (clear_requests_pulse) begin
        request_valid_q <= '0;
      end

      if (accepted_write) begin
        unique case (csr_addr)
          FRP_M22_ADDR_SCHEDULER_MODE: begin
            scheduler_mode_control_q <= csr_wdata[
              FRP_M16_SCHED_MODE_BITS-1:0
            ];
          end
          FRP_M22_ADDR_REQUEST_LANE_SELECT: begin
            request_lane_select_q <= csr_wdata[CELL_INDEX_BITS-1:0];
          end
          FRP_M22_ADDR_REQUEST_CELL_INDEX: begin
            request_cell_index_q[
              (int'(request_lane_select_q)*CELL_INDEX_BITS)
              +: CELL_INDEX_BITS
            ] <= csr_wdata[CELL_INDEX_BITS-1:0];
          end
          FRP_M22_ADDR_REQUEST_TARGET: begin
            request_target_q[
              (int'(request_lane_select_q)*STATE_BITS)
              +: STATE_BITS
            ] <= csr_wdata[STATE_BITS-1:0];
          end
          FRP_M22_ADDR_REQUEST_VALID: begin
            request_valid_q[int'(request_lane_select_q)] <= csr_wdata[0];
          end
          FRP_M22_ADDR_OBSERVE_CELL_INDEX: begin
            observe_cell_index_q <= csr_wdata[CELL_INDEX_BITS-1:0];
          end
          default: begin
          end
        endcase
      end
    end
  end

  frp_m16_core #(
    .CELLS(CELLS),
    .STATE_BITS(STATE_BITS),
    .REQUEST_LANES(REQUEST_LANES),
    .CELL_INDEX_BITS(CELL_INDEX_BITS),
    .COUNTER_BITS(COUNTER_BITS)
  ) u_core (
    .clk(clk),
    .rst_n(rst_n),
    .tick_enable(tick_pulse),
    .clear_counters(clear_counters_pulse),
    .scheduler_mode(frp_m16_scheduler_mode_e'(scheduler_mode_control_q)),
    .request_valid(request_valid_q),
    .request_cell_index(request_cell_index_q),
    .request_target(request_target_q),
    .target_q(target_q),
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
    .invariant_flags(invariant_flags)
  );

endmodule : frp_m22_control_status_register_interface

`endif
