
module alwaysstar_test_fail(
    input logic a, 
    input logic b,
    output logic y
);

always @(*) begin
    y = 1'b0;

    if (a) begin
        y = b;
    end else begin
        y = 1'b0;
    end
end

endmodule

