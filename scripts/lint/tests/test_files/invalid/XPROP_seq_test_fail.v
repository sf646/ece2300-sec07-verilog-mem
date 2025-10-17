module xprop_seq_test_fail(
    input clk,
    input d,
    input rst,
    output q
);

always_ff @(posedge clk) begin
    if (rst) begin
        q <= d;
    end
end

endmodule

