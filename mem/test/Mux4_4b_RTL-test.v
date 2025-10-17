//========================================================================
// Mux4_4b_RTL-test
//========================================================================

`include "ece2300/ece2300-test.v"

// ece2300-lint
`include "mem/Mux4_4b_RTL.v"

module Top();

  //----------------------------------------------------------------------
  // Setup
  //----------------------------------------------------------------------

  CombinationalTestUtils t();

  //----------------------------------------------------------------------
  // Instantiate design under test
  //----------------------------------------------------------------------

  logic [3:0] in0;
  logic [3:0] in1;
  logic [3:0] in2;
  logic [3:0] in3;
  logic [1:0] sel;
  logic [3:0] out;

  Mux4_4b_RTL dut( .* );

  //----------------------------------------------------------------------
  // check
  //----------------------------------------------------------------------
  // We set the inputs, wait 8 tau, check the outputs, wait 2 tau. Each
  // check will take a total of 10 tau.

  task check
  (
    input logic [3:0] in0_,
    input logic [3:0] in1_,
    input logic [3:0] in2_,
    input logic [3:0] in3_,
    input logic [1:0] sel_,
    input logic [3:0] out_
  );
    if ( !t.failed ) begin
      t.num_checks += 1;

      in0 = in0_;
      in1 = in1_;
      in2 = in2_;
      in3 = in3_;
      sel = sel_;

      #8;

      if ( t.n != 0 )
        $display( "%3d: %b %b %b %b %b > %b", t.cycles, in0, in1, in2, in3, sel, out );

      `ECE2300_CHECK_EQ( out, out_ );

      #2;

    end
  endtask

  //----------------------------------------------------------------------
  // test_case_1_basic
  //----------------------------------------------------------------------

  task test_case_1_basic();
    t.test_case_begin( "test_case_1_basic" );

    //     in0      in1      in2      in3      sel out
    check( 4'b0000, 4'b0000, 4'b0000, 4'b0000, 0,  4'b0000 );
    check( 4'b0000, 4'b0000, 4'b0000, 4'b0000, 1,  4'b0000 );
    check( 4'b0000, 4'b0000, 4'b0000, 4'b0000, 2,  4'b0000 );
    check( 4'b0000, 4'b0000, 4'b0000, 4'b0000, 3,  4'b0000 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_2_directed
  //----------------------------------------------------------------------

  task test_case_2_directed();
    t.test_case_begin( "test_case_2_directed" );

    //     in0      in1      in2      in3      sel out
    check( 4'b0001, 4'b0010, 4'b0100, 4'b1000, 0,  4'b0001 );
    check( 4'b0101, 4'b1010, 4'b0101, 4'b1010, 1,  4'b1010 );
    check( 4'b1000, 4'b0100, 4'b0010, 4'b0001, 2,  4'b0010 );
    check( 4'b1010, 4'b0101, 4'b1010, 4'b0101, 3,  4'b0101 );

    check( 4'b0001, 4'b0010, 4'b0100, 4'b1000, 1,  4'b0010 );
    check( 4'b0101, 4'b1010, 4'b0101, 4'b1010, 2,  4'b0101 );
    check( 4'b1000, 4'b0100, 4'b0010, 4'b0001, 3,  4'b0001 );
    check( 4'b1010, 4'b0101, 4'b1010, 4'b0101, 0,  4'b1010 );

    check( 4'b0001, 4'b0010, 4'b0100, 4'b1000, 2,  4'b0100 );
    check( 4'b0101, 4'b1010, 4'b0101, 4'b1010, 3,  4'b1010 );
    check( 4'b1000, 4'b0100, 4'b0010, 4'b0001, 0,  4'b1000 );
    check( 4'b1010, 4'b0101, 4'b1010, 4'b0101, 1,  4'b0101 );

    check( 4'b0001, 4'b0010, 4'b0100, 4'b1000, 3,  4'b1000 );
    check( 4'b0101, 4'b1010, 4'b0101, 4'b1010, 0,  4'b0101 );
    check( 4'b1000, 4'b0100, 4'b0010, 4'b0001, 1,  4'b0100 );
    check( 4'b1010, 4'b0101, 4'b1010, 4'b0101, 2,  4'b1010 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_3_random
  //----------------------------------------------------------------------

  logic [3:0] rand_in0;
  logic [3:0] rand_in1;
  logic [3:0] rand_in2;
  logic [3:0] rand_in3;
  logic [1:0] rand_sel;
  logic [3:0] rand_out;

  task test_case_3_random();
    t.test_case_begin( "test_case_3_random" );

    for ( int i = 0; i < 50; i = i+1 ) begin

      // Generate random values for in0, in1, sel

      rand_in0 = 4'($urandom(t.seed));
      rand_in1 = 4'($urandom(t.seed));
      rand_in2 = 4'($urandom(t.seed));
      rand_in3 = 4'($urandom(t.seed));
      rand_sel = 2'($urandom(t.seed));

      // Determine correct answer

      if ( rand_sel == 0 )
        rand_out = rand_in0;
      else if ( rand_sel == 1 )
        rand_out = rand_in1;
      else if ( rand_sel == 2 )
        rand_out = rand_in2;
      else
        rand_out = rand_in3;

      // Check DUT output matches correct answer

      check( rand_in0, rand_in1, rand_in2, rand_in3, rand_sel, rand_out );

    end

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_4_xprop
  //----------------------------------------------------------------------

  task test_case_4_xprop();
    t.test_case_begin( "test_case_4_xprop" );

    //     in0 in1 in2 in3 sel out
    check( 'x, 'x, 'x, 'x, 'x, 'x );

    check( '0, '0, '0, '1, 'x, 'x );
    check( '0, '0, '1, '0, 'x, 'x );
    check( '0, '1, '0, '0, 'x, 'x );
    check( '1, '0, '0, '0, 'x, 'x );

    check( 'x, '0, '0, '0,  0, 'x );
    check( '0, 'x, '0, '0,  1, 'x );
    check( '0, '0, 'x, '0,  2, 'x );
    check( '0, '0, '0, 'x,  3, 'x );

    check( 'x, '1, '1, '1,  0, 'x );
    check( '1, 'x, '1, '1,  1, 'x );
    check( '1, '1, 'x, '1,  2, 'x );
    check( '1, '1, '1, 'x,  3, 'x );

    check( '0, 'x, 'x, 'x,  0, '0 );
    check( 'x, '0, 'x, 'x,  1, '0 );
    check( 'x, 'x, '0, 'x,  2, '0 );
    check( 'x, 'x, 'x, '0,  3, '0 );

    check( '1, 'x, 'x, 'x,  0, '1 );
    check( 'x, '1, 'x, 'x,  1, '1 );
    check( 'x, 'x, '1, 'x,  2, '1 );
    check( 'x, 'x, 'x, '1,  3, '1 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // main
  //----------------------------------------------------------------------

  initial begin
    t.test_bench_begin();

    if ((t.n <= 0) || (t.n == 1)) test_case_1_basic();
    if ((t.n <= 0) || (t.n == 2)) test_case_2_directed();
    if ((t.n <= 0) || (t.n == 3)) test_case_3_random();
    if ((t.n <= 0) || (t.n == 4)) test_case_4_xprop();

    t.test_bench_end();
  end

endmodule
