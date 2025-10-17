`include "ece2300-xprop.v"

module xprop_test_pass(
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

    `ECE2300_XPROP1(y, a);
end

endmodule