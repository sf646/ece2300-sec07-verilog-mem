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

  //''' ACTIVITY '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement a 4-to-1 4-bit mux using an always_comb block
  //>'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  `ECE2300_UNUSED( in0 );
  `ECE2300_UNUSED( in1 );
  `ECE2300_UNUSED( in2 );
  `ECE2300_UNUSED( in3 );
  `ECE2300_UNUSED( sel );
  `ECE2300_UNDRIVEN( out );

endmodule

`endif /* MUX4_4B_RTL */
