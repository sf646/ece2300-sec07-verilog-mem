
module negedge_test_fail(
    input logic clk,
    input logic a,
    output logic y
);

always_ff @(negedge clk) begin
    y <= a;
end

endmodule

