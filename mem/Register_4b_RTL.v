//========================================================================
// Register_4b_RTL
//========================================================================

`ifndef REGISTER_4B_RTL_V
`define REGISTER_4B_RTL_V

`include "ece2300/ece2300-misc.v"

module Register_4b_RTL
(
  (* keep=1 *) input  logic       clk,
  (* keep=1 *) input  logic       en,
  (* keep=1 *) input  logic [3:0] d,
  (* keep=1 *) output logic [3:0] q
);

  //''' LAB ASSIGNMENT '''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement a register using an always_ff
  //>'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  `ECE2300_UNUSED( clk );
  `ECE2300_UNUSED( en );
  `ECE2300_UNUSED( d );
  `ECE2300_UNDRIVEN( q );

endmodule

`endif /* REGISTER_4B_RTL_V */
