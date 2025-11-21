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

  always_ff @(posedge clk) begin
    if (en)
      q <= d;
    `ECE2300_SEQ_XPROP(q, $isunknown(en));
  end

endmodule

`endif /* REGISTER_4B_RTL_V */
