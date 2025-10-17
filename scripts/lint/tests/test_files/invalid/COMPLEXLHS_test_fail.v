
module complexlhs_test_fail(
    input logic a,
    input logic b,
    output logic y,
    output logic v
);

assign {y, v} = {a, b}; 

endmodule

