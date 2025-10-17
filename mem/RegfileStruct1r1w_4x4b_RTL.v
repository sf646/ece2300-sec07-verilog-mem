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
  //:
  //: `ECE2300_UNUSED( clk );
  //: `ECE2300_UNUSED( wen );
  //: `ECE2300_UNUSED( waddr );
  //: `ECE2300_UNUSED( wdata );
  //: `ECE2300_UNUSED( rdata );
  //: `ECE2300_UNDRIVEN( rdata );
  //:

  // Write Address Decoder

  logic [3:0] regfile_en;

  Decoder_2b_RTL waddr_decoder
  (
    .in  (waddr),
    .out (regfile_en)
  );

  // Read data for each register

  logic [3:0] reg_q[4];

  // Register 0

  wire reg0_en;
  and( reg0_en, regfile_en[0], wen );

  Register_4b_RTL reg0
  (
    .clk (clk),
    .en  (reg0_en),
    .d   (wdata),
    .q   (reg_q[0])
  );

  // Register 1

  wire reg1_en;
  and( reg1_en, regfile_en[1], wen );

  Register_4b_RTL reg1
  (
    .clk (clk),
    .en  (reg1_en),
    .d   (wdata),
    .q   (reg_q[1])
  );

  // Register 2

  wire reg2_en;
  and( reg2_en, regfile_en[2], wen );

  Register_4b_RTL reg2
  (
    .clk (clk),
    .en  (reg2_en),
    .d   (wdata),
    .q   (reg_q[2])
  );

  // Register 3

  wire reg3_en;
  and( reg3_en, regfile_en[3], wen );

  Register_4b_RTL reg3
  (
    .clk (clk),
    .en  (reg3_en),
    .d   (wdata),
    .q   (reg_q[3])
  );

  // Read mux

  Mux4_4b_RTL mux
  (
    .in0 (reg_q[0]),
    .in1 (reg_q[1]),
    .in2 (reg_q[2]),
    .in3 (reg_q[3]),
    .sel (raddr),
    .out (rdata)
  );

endmodule

`endif /* REGFILE_STRUCT_1R1W_4X4B2To4_RTL */

