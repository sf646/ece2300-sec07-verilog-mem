
module alwaysff_test_fail(
    input logic a, 
    input logic b,
    output logic y
);

always_ff begin
    y = a | b;
end

endmodule

