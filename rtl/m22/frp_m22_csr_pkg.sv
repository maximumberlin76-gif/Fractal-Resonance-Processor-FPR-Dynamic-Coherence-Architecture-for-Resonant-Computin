// SPDX-License-Identifier: Apache-2.0
//
// FRP M22 Control, Status, and Register Interface Package
//
// Version: FRP v2.4.0
// Milestone: M22 — Control, Status, and Register Interface Realization

`ifndef FRP_M22_CSR_PKG_SV
`define FRP_M22_CSR_PKG_SV

package frp_m22_csr_pkg;

  localparam int FRP_M22_CSR_DATA_BITS = 32;
  localparam int FRP_M22_CSR_ADDR_BITS = 8;
  localparam int FRP_M22_CSR_BYTE_LANES = 4;
  localparam int FRP_M22_REGISTER_COUNT = 26;

  typedef logic [FRP_M22_CSR_ADDR_BITS-1:0] frp_m22_csr_addr_t;
  typedef logic [FRP_M22_CSR_DATA_BITS-1:0] frp_m22_csr_data_t;

  localparam frp_m22_csr_addr_t FRP_M22_ADDR_CONTROL = 8'h00;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_SCHEDULER_MODE = 8'h04;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_LANE_SELECT = 8'h08;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_CELL_INDEX = 8'h0C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_TARGET = 8'h10;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_VALID = 8'h14;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_OBSERVE_CELL_INDEX = 8'h18;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_STATUS = 8'h1C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_SCHEDULER_MODE_ACTIVE = 8'h20;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_SCHEDULER_STATE = 8'h24;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_TICKS_RECORDED = 8'h28;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_ACCEPT = 8'h2C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUEST_REJECT = 8'h30;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_RETAINED_STATE = 8'h34;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_PENDING_ROUTE = 8'h38;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_ACCEPTED_CHANGES = 8'h3C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_CAPACITY_REMAINING = 8'h40;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_CAPACITY_EXHAUSTED = 8'h44;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_SWITCH_LOAD_NUMERATOR = 8'h48;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_INVARIANT_FLAGS = 8'h4C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_REQUESTED_DIRECT_EVENTS = 8'h50;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_PREVENTED_DIRECT_EVENTS = 8'h54;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_NEUTRAL_ROUTED_EVENTS = 8'h58;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS = 8'h5C;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_RESERVED_STATE_EVENTS = 8'h60;
  localparam frp_m22_csr_addr_t FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS = 8'h64;

  localparam frp_m22_csr_data_t FRP_M22_CONTROL_TICK = 32'h00000001;
  localparam frp_m22_csr_data_t FRP_M22_CONTROL_CLEAR_COUNTERS = 32'h00000002;
  localparam frp_m22_csr_data_t FRP_M22_CONTROL_CLEAR_REQUESTS = 32'h00000004;
  localparam frp_m22_csr_data_t FRP_M22_CONTROL_MASK = 32'h00000007;

  localparam int FRP_M22_STATUS_READY = 0;
  localparam int FRP_M22_STATUS_CAPACITY_EXHAUSTED = 1;
  localparam int FRP_M22_STATUS_REQUEST_ACCEPTED = 2;
  localparam int FRP_M22_STATUS_REQUEST_REJECTED = 3;
  localparam int FRP_M22_STATUS_PENDING_ACTIVE = 4;
  localparam int FRP_M22_STATUS_INVARIANT_FAILURE = 5;
  localparam int FRP_M22_STATUS_ACTUAL_DIRECT_NONZERO = 6;
  localparam int FRP_M22_STATUS_RESERVED_STATE_NONZERO = 7;
  localparam int FRP_M22_STATUS_QUEUE_OVERFLOW_NONZERO = 8;

  function automatic logic frp_m22_is_word_aligned(
    input frp_m22_csr_addr_t address
  );
    begin
      frp_m22_is_word_aligned =
        (address[1:0] == 2'b00);
    end
  endfunction

  function automatic logic frp_m22_is_defined_address(
    input frp_m22_csr_addr_t address
  );
    begin
      unique case (address)
        FRP_M22_ADDR_CONTROL,
        FRP_M22_ADDR_SCHEDULER_MODE,
        FRP_M22_ADDR_REQUEST_LANE_SELECT,
        FRP_M22_ADDR_REQUEST_CELL_INDEX,
        FRP_M22_ADDR_REQUEST_TARGET,
        FRP_M22_ADDR_REQUEST_VALID,
        FRP_M22_ADDR_OBSERVE_CELL_INDEX,
        FRP_M22_ADDR_STATUS,
        FRP_M22_ADDR_SCHEDULER_MODE_ACTIVE,
        FRP_M22_ADDR_SCHEDULER_STATE,
        FRP_M22_ADDR_TICKS_RECORDED,
        FRP_M22_ADDR_REQUEST_ACCEPT,
        FRP_M22_ADDR_REQUEST_REJECT,
        FRP_M22_ADDR_RETAINED_STATE,
        FRP_M22_ADDR_PENDING_ROUTE,
        FRP_M22_ADDR_ACCEPTED_CHANGES,
        FRP_M22_ADDR_CAPACITY_REMAINING,
        FRP_M22_ADDR_CAPACITY_EXHAUSTED,
        FRP_M22_ADDR_SWITCH_LOAD_NUMERATOR,
        FRP_M22_ADDR_INVARIANT_FLAGS,
        FRP_M22_ADDR_REQUESTED_DIRECT_EVENTS,
        FRP_M22_ADDR_PREVENTED_DIRECT_EVENTS,
        FRP_M22_ADDR_NEUTRAL_ROUTED_EVENTS,
        FRP_M22_ADDR_ACTUAL_DIRECT_EVENTS,
        FRP_M22_ADDR_RESERVED_STATE_EVENTS,
        FRP_M22_ADDR_QUEUE_OVERFLOW_EVENTS:
          frp_m22_is_defined_address = 1'b1;
        default:
          frp_m22_is_defined_address = 1'b0;
      endcase
    end
  endfunction

  function automatic logic frp_m22_is_readable_address(
    input frp_m22_csr_addr_t address
  );
    begin
      frp_m22_is_readable_address =
        frp_m22_is_defined_address(address)
        && (address != FRP_M22_ADDR_CONTROL);
    end
  endfunction

  function automatic logic frp_m22_is_writable_address(
    input frp_m22_csr_addr_t address
  );
    begin
      unique case (address)
        FRP_M22_ADDR_CONTROL,
        FRP_M22_ADDR_SCHEDULER_MODE,
        FRP_M22_ADDR_REQUEST_LANE_SELECT,
        FRP_M22_ADDR_REQUEST_CELL_INDEX,
        FRP_M22_ADDR_REQUEST_TARGET,
        FRP_M22_ADDR_REQUEST_VALID,
        FRP_M22_ADDR_OBSERVE_CELL_INDEX:
          frp_m22_is_writable_address = 1'b1;
        default:
          frp_m22_is_writable_address = 1'b0;
      endcase
    end
  endfunction

endpackage : frp_m22_csr_pkg

`endif
