
module asyncreset_test_pass(
    input logic clk,
    input logic reset,
    input logic a,
    output logic y
);

always_ff @(posedge clk) begin
    if (reset) begin
        y <= 1'b0;
    end else begin
        y <= a;
    end
end

endmodule

