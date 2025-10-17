
module complexrhs_add_test_fail(
    input logic a,
    input logic b,
    output logic [1:0] y
);

assign y = a + b;

endmodule