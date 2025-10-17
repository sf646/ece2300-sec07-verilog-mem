//========================================================================
// RegfileStruct1r1w_4x4b_RTL
//========================================================================

`ifndef REGFILE_STRUCT_1R1W_4X4B_RTL
`define REGFILE_STRUCT_1R1W_4X4B_RTL

`include "ece2300/ece2300-misc.v"

`include "mem/Mux4_4b_RTL.v"
`include "mem/Decoder_2b_RTL.v"
`include "mem/Register_4b_RTL.v"

module RegfileStruct1r1w_4x4b_RTL
(
  (* keep=1 *) input  logic       clk,

  (* keep=1 *) input  logic       wen,
  (* keep=1 *) input  logic [1:0] waddr,
  (* keep=1 *) input  logic [3:0] wdata,

  (* keep=1 *) input  logic [1:0] raddr,
  (* keep=1 *) output logic [3:0] rdata
);

  //''' LAB ASSIGNMENT '''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement 4-element, 4-bit regfile structurally
  //>'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

  `ECE2300_UNUSED( clk );
  `ECE2300_UNUSED( wen );
  `ECE2300_UNUSED( waddr );
  `ECE2300_UNUSED( wdata );
  `ECE2300_UNUSED( raddr );
  `ECE2300_UNDRIVEN( rdata );

endmodule

`endif /* REGFILE_STRUCT_1R1W_4X4B2To4_RTL */
