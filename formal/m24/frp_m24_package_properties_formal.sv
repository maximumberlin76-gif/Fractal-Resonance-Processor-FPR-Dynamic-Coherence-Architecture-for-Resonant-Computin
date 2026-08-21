// SPDX-License-Identifier: Apache-2.0
// FRP M24 bounded proof harness for canonical balanced-ternary helpers.

module frp_m24_package_properties_formal;
  (* anyconst *) logic [1:0] state_value;
  (* anyconst *) logic [1:0] target_value;
  (* anyconst *) logic [1:0] pending_value;

  wire state_valid = frp_is_valid_ternary(state_value);
  wire target_valid = frp_is_valid_ternary(target_value);
  wire pending_valid = frp_is_valid_ternary(pending_value);
  wire operands_valid = state_valid && target_valid && pending_valid;

  wire [3:0] transition_class =
    frp_classify_transition(state_value, target_value, pending_value);
  wire [1:0] selected_target =
    frp_transition_selected_target(state_value, target_value, pending_value);

  wire M24_P01 =
    state_valid == (state_value != FRP_STATE_RESERVED);
  wire M24_P02 =
    (FRP_STATE_ZERO == 2'b00)
    && (FRP_STATE_POS == 2'b01)
    && (FRP_STATE_RESERVED == 2'b10)
    && (FRP_STATE_NEG == 2'b11)
    && (FRP_ACTIVE_NEUTRAL == FRP_STATE_ZERO);
  wire M24_P03 =
    !(operands_valid && (pending_value == FRP_STATE_ZERO)
      && (state_value == target_value))
    || (transition_class == FRP_TRANS_SAME_STATE);
  wire M24_P04 =
    !(operands_valid && (pending_value == FRP_STATE_ZERO)
      && frp_is_zero(state_value) && frp_is_nonzero(target_value))
    || (transition_class == FRP_TRANS_ZERO_TO_NONZERO);
  wire M24_P05 =
    !(operands_valid && (pending_value == FRP_STATE_ZERO)
      && frp_is_nonzero(state_value) && frp_is_zero(target_value))
    || (transition_class == FRP_TRANS_NONZERO_TO_ZERO);
  wire M24_P06 =
    !(operands_valid && (pending_value == FRP_STATE_ZERO)
      && frp_is_opposite_polarity(state_value, target_value))
    || (transition_class == FRP_TRANS_OPPOSITE_POLARITY);
  wire M24_P07 =
    !(operands_valid && (pending_value == FRP_STATE_ZERO)
      && frp_is_opposite_polarity(state_value, target_value))
    || ((selected_target == FRP_ACTIVE_NEUTRAL)
      && !frp_is_legal_state_change(state_value, target_value));
  wire M24_P08 =
    !(operands_valid && frp_is_zero(state_value)
      && frp_has_pending_route(pending_value))
    || ((transition_class == FRP_TRANS_PENDING_COMPLETION)
      && (selected_target == pending_value));
  wire M24_P09 =
    !frp_transition_consumes_capacity(FRP_TRANS_SAME_STATE)
    && frp_transition_consumes_capacity(FRP_TRANS_ZERO_TO_NONZERO)
    && frp_transition_consumes_capacity(FRP_TRANS_NONZERO_TO_ZERO)
    && frp_transition_consumes_capacity(FRP_TRANS_OPPOSITE_POLARITY)
    && frp_transition_consumes_capacity(FRP_TRANS_PENDING_COMPLETION);

  always @* begin
    assert(M24_P01);
    assert(M24_P02);
    assert(M24_P03);
    assert(M24_P04);
    assert(M24_P05);
    assert(M24_P06);
    assert(M24_P07);
    assert(M24_P08);
    assert(M24_P09);
  end
endmodule
