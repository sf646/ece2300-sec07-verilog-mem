
module asyncreset_test_fail(
    input logic clk,
    input logic reset,
    input logic a,
    output logic y
);

always_ff @(posedge clk or negedge reset) begin
    if (reset) begin
        y <= 1'b0;
    end else begin
        y <= a;
    end
end

endmodule

