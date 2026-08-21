// SPDX-License-Identifier: Apache-2.0
// FRP M23 asynchronous-assertion, synchronous-release reset synchronizer.

`ifndef FRP_M23_RESET_RELEASE_SYNC_SV
`define FRP_M23_RESET_RELEASE_SYNC_SV

module frp_m23_reset_release_sync (
  input  logic clk,
  input  logic rst_n_async,
  output logic rst_n_sync
);

  (* ASYNC_REG = "TRUE" *) logic [1:0] release_q;

  always_ff @(posedge clk or negedge rst_n_async) begin
    if (!rst_n_async) begin
      release_q <= 2'b00;
    end else begin
      release_q <= {release_q[0], 1'b1};
    end
  end

  assign rst_n_sync = release_q[1];

endmodule : frp_m23_reset_release_sync

`endif
