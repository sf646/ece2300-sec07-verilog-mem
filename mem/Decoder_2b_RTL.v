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

  //''' ACTIVITY '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement a 2-to-4 decoder using an always_comb block
  //>'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  `ECE2300_UNUSED( in );
  `ECE2300_UNDRIVEN( out );

endmodule

`endif /* DECODER_2B_RTL */
