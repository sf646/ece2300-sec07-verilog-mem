//========================================================================
// RegfileFlat1r1w_4x4b_RTL
//========================================================================

`ifndef REGFILE_FLAT_1R1W_4X4B_RTL
`define REGFILE_FLAT_1R1W_4X4B_RTL

`include "ece2300/ece2300-misc.v"

module RegfileFlat1r1w_4x4b_RTL
(
  (* keep=1 *) input  logic       clk,

  (* keep=1 *) input  logic       wen,
  (* keep=1 *) input  logic [1:0] waddr,
  (* keep=1 *) input  logic [3:0] wdata,

  (* keep=1 *) input  logic [1:0] raddr,
  (* keep=1 *) output logic [3:0] rdata
);

  logic [3:0] regfile [4];

  always_ff @( posedge clk ) begin
    if ( wen )
      case (waddr)
      2'd0: regfile[0] <= wdata;
      2'd1: regfile[1] <= wdata;
      2'd2: regfile[2] <= wdata;
      2'd3: regfile[3] <= wdata;
      default: {regfile[0], regfile[1], regfile[2], regfile[3]} = 'x;
      endcase
  end

  always_comb begin
    case (raddr)
    2'd0: rdata = regfile[0];
    2'd1: rdata = regfile[1];
    2'd2: rdata = regfile[2];
    2'd3: rdata = regfile[3];
    default: rdata = 'x;
    endcase
  end

endmodule

`endif /* REGFILE_FLAT_1R1W_4X4B2To4_RTL */
