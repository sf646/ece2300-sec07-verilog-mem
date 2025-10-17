
module primonly_test_pass(
    input logic a,
    output logic b,
    output logic y
);

buf (y, a);
buf (b, a);


endmodule

