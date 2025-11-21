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

  logic [3:0] decode_out;

  Decoder_2b_RTL decoder
  (
    .in (waddr),
    .out (decode_out)
  );

  logic reg0en, reg1en, reg2en, reg3en;

  and( reg0en, wen, decode_out[0] );
  and( reg1en, wen, decode_out[1] );
  and( reg2en, wen, decode_out[2] );
  and( reg3en, wen, decode_out[3] );

  logic [3:0] regout [4];

  Register_4b_RTL reg0
  (
    .clk (clk),
    .en (reg0en),
    .d (wdata),
    .q (regout[0])
  );

  Register_4b_RTL reg1
  (
    .clk (clk),
    .en (reg1en),
    .d (wdata),
    .q (regout[1])
  );

  Register_4b_RTL reg2
  (
    .clk (clk),
    .en (reg2en),
    .d (wdata),
    .q (regout[2])
  );

  Register_4b_RTL reg3
  (
    .clk (clk),
    .en (reg3en),
    .d (wdata),
    .q (regout[3])
  );

  Mux4_4b_RTL mux
  (
    .in0 (regout[0]),
    .in1 (regout[1]),
    .in2 (regout[2]),
    .in3 (regout[3]),
    .sel (raddr),
    .out (rdata)
  );

endmodule

`endif /* REGFILE_STRUCT_1R1W_4X4B2To4_RTL */
