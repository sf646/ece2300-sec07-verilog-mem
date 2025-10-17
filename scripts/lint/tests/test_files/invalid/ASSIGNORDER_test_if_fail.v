
module assignorder_test_if_fail(
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

    y = 1'b1;

end

endmodule