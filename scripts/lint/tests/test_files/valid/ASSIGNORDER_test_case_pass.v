
module assignorder_test_if_pass(
    input logic a, 
    input logic b,
    output logic y
);

always_comb begin
    
    y = 1'b1;

    case (a)
        1'b0: y = 1'b0;
        1'b1: y = b;
        default: y = 1'bx; 
    endcase
end

endmodule