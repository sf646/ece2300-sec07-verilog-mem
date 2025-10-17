
module latch_test_fail(
    input logic a, 
    input logic b,
    output logic y
);

always_comb begin

    if (a) begin
        y = b;
    end else begin
        y = 1'b0;
    end
end

endmodule

