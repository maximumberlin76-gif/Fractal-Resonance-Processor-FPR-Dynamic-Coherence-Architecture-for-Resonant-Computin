// SPDX-License-Identifier: Apache-2.0
// Deterministic phase-target to active-neutral request-lane adapter.

`ifndef FRP_M31_PHASE_REQUEST_ADAPTER_SV
`define FRP_M31_PHASE_REQUEST_ADAPTER_SV

`include "frp_m31_pkg.sv"

module frp_m31_phase_request_adapter #(
  parameter int CELLS = 8,
  parameter int REQUEST_LANES = frp_m31_pkg::frp_calc_request_lanes(CELLS),
  parameter int CELL_INDEX_BITS = (CELLS <= 1) ? 1 : $clog2(CELLS)
) (
  input logic enable,
  input logic [(CELLS*2)-1:0] retained_state,
  input logic [(CELLS*2)-1:0] pending_route,
  input logic [(CELLS*2)-1:0] phase_target,
  input frp_m31_pkg::frp_m31_scheduler_state_e scheduler_state,
  output logic [REQUEST_LANES-1:0] request_valid,
  output logic [(REQUEST_LANES*CELL_INDEX_BITS)-1:0] request_cell_index,
  output logic [(REQUEST_LANES*2)-1:0] request_target
);

  import frp_m31_pkg::*;

  always_comb begin : select_phase_requests
    int unsigned selected;
    logic [1:0] current_value;
    logic [1:0] pending_value;
    logic [1:0] target_value;
    frp_m31_transition_class_e transition_class;

    request_valid = '0;
    request_cell_index = '0;
    request_target = '0;
    selected = 0;

    if (enable) begin
      for (int cell_index = 0; cell_index < CELLS; cell_index = cell_index + 1) begin
        current_value = retained_state[(cell_index*2) +: 2];
        pending_value = pending_route[(cell_index*2) +: 2];
        target_value = phase_target[(cell_index*2) +: 2];
        transition_class = frp_classify_transition(
          current_value,
          target_value,
          FRP_STATE_ZERO
        );

        if (
          (selected < REQUEST_LANES)
          && frp_is_valid_ternary(current_value)
          && frp_is_valid_ternary(target_value)
          && !frp_has_pending_route(pending_value)
          && (current_value != target_value)
          && frp_scheduler_allows_transition(scheduler_state, transition_class)
        ) begin
          request_valid[selected] = 1'b1;
          request_cell_index[(selected*CELL_INDEX_BITS) +: CELL_INDEX_BITS] =
            cell_index[CELL_INDEX_BITS-1:0];
          request_target[(selected*2) +: 2] = target_value;
          selected = selected + 1;
        end
      end
    end
  end

endmodule

`endif
