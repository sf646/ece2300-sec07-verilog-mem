
module latch_test_pass(
    input logic a, 
    input logic b,
    output logic y
);

always_comb begin
    y = 1'b0;

    if (a) begin
        y = b;
    end else begin
        y = 1'b0;
    end
end

endmodule

