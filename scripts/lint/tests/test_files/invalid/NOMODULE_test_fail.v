`include "FullAdder_GL.v"

module nomodule_test_fail(
    input  wire [1:0] in0,
    input  wire [1:0] in1,
    input  wire cin,
    output wire cout, 
    output wire [1:0] out
);
  
  wire cout1;

  FullAdder_GL fa1 (
    .in0 (inp[0]),
    .in1 (in1[0]),
    .cin (cin),
    .cout(cout1),
    .sum (out[0])
  );

  FullAdder_GL fa2 (
    .in0 (in0[1]),
    .in1 (in1[1]),
    .cin (cin),
    .cout(cout),
    .sum (out[1])
  );

endmodule

