
module complexrhs_test_pass(
    input logic a,
    input logic b,
    output logic [1:0] y
);

assign y[1] = a;
assign y[0] = b;

endmodule

