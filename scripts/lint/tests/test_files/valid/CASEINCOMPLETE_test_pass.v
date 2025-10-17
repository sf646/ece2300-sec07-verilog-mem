
module caseincomplete_test_pass(
    input logic a, 
    output logic v,
    output logic y
);

always_comb begin
    case(a)
        1'b0: v = 1'b0;
        1'b1: y = 1'b1;
        default: begin
            v = 1'bx; 
            y = 1'bx; 
        end
    endcase
end

endmodule

