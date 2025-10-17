module nomodule_test_pass(
    input  wire [1:0] in0,
    input  wire [1:0] in1,
    input  wire cin,
    output wire cout, 
    output wire [1:0] out
);
  wire sum1;
  wire sum2;

  xor( sum1, in0[0], in1[0], cin );

  wire t2, t3, t4;
  and( t2, in0[0], in1[1] );
  and( t3, in0[0], cin );
  and( t4, in1[0], cin );
  or( cout, t2, t3, t4 );

  xor( sum2, in0[1], in1[1], cin );

  wire t5, t6, t7;
  and( t5, in0[1], in1[1] );
  and( t6, in0[1], cin );
  and( t7, in1[1], cin );
  or( cout, t5, t6, t7 );

  assign out[1] = sum2;
  assign out[0] = sum1;


endmodule

