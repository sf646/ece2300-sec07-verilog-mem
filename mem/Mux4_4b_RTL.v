//========================================================================
// Mux4_4b_RTL
//========================================================================

`ifndef MUX4_4B_RTL
`define MUX4_4B_RTL

`include "ece2300/ece2300-misc.v"

module Mux4_4b_RTL
(
  (* keep=1 *) input  logic [3:0] in0,
  (* keep=1 *) input  logic [3:0] in1,
  (* keep=1 *) input  logic [3:0] in2,
  (* keep=1 *) input  logic [3:0] in3,
  (* keep=1 *) input  logic [1:0] sel,
  (* keep=1 *) output logic [3:0] out
);

  always_comb begin
    case (sel)
    2'd0: out = in0;
    2'd1: out = in1;
    2'd2: out = in2;
    2'd3: out = in3;
    default: out = 'x;
    endcase
    `ECE2300_XPROP (out, $isunknown(sel));
  end

endmodule

`endif /* MUX4_4B_RTL */
