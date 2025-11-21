//========================================================================
// Decoder_2b_RTL
//========================================================================

`ifndef DECODER_2B_RTL
`define DECODER_2B_RTL

`include "ece2300/ece2300-misc.v"

module Decoder_2b_RTL
(
  (* keep=1 *) input  logic [1:0] in,
  (* keep=1 *) output logic [3:0] out
);

  always_comb begin
    case (in)
    2'd0: out = 4'b0001;
    2'd1: out = 4'b0010;
    2'd2: out = 4'b0100;
    2'd3: out = 4'b1000;
    default: out = 'x;
    endcase
  end

endmodule

`endif /* DECODER_2B_RTL */
