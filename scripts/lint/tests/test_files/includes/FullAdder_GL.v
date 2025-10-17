module FullAdder_GL
(
  input  wire in0,
  input  wire in1,
  input  wire cin,
  output wire cout,
  output wire sum
);

  xor( sum, in0, in1, cin );

  wire t2, t3, t4;
  and( t2, in0, in1 );
  and( t3, in0, cin );
  and( t4, in1, cin );
  or( cout, t2, t3, t4 );

endmodule

