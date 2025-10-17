`include "ece2300-xprop.v"

module xprop_seq_test_pass(
    input clk,
    input d,
    input rst,
    output q
);

always_ff @(posedge clk) begin
    if (rst) begin
        q <= d;
    end

    `ECE2300_SEQ_XPROP1(q, d);
end

endmodule

