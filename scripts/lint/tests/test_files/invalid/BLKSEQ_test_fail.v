
module blkseq_test_fail(
    input logic clk, 
    input logic b,
    output logic y
);

always_ff @(posedge clk) begin
    y = b;
end

endmodule

