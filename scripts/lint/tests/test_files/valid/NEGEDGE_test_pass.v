
module negedge_test_pass(
    input logic clk,
    input logic a,
    output logic y
);

always_ff @(posedge clk) begin
    y <= a;
end

endmodule

