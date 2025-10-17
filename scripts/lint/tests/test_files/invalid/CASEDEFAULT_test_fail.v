
module casedefault_test_fail(
    input logic a, 
    input logic b,
    output logic y
);

always_comb begin
    case (a)
        1'b0: y = 1'b0;
        1'b1: y = b;
    endcase
end

endmodule

