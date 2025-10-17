//========================================================================
// Decoder_2b_RTL-test
//========================================================================

`include "ece2300/ece2300-test.v"

// ece2300-lint
`include "mem/Decoder_2b_RTL.v"

module Top();

  //----------------------------------------------------------------------
  // Setup
  //----------------------------------------------------------------------

  CombinationalTestUtils t();

  //----------------------------------------------------------------------
  // Instantiate design under test
  //----------------------------------------------------------------------

  logic [1:0] in;
  logic [3:0] out;

  Decoder_2b_RTL duta( .* );

  //----------------------------------------------------------------------
  // check
  //----------------------------------------------------------------------
  // We set the inputs, wait 8 tau, check the outputs, wait 2 tau. Each
  // check will take a total of 10 tau.

  task check
  (
    input logic [1:0] in_,
    input logic [3:0] out_
  );
    if ( !t.failed ) begin
      t.num_checks += 1;

      in = in_;

      #8;

      if ( t.n != 0 )
        $display( "%3d: %d > %b", t.cycles, in, out );

      `ECE2300_CHECK_EQ( out, out_ );

      #2;

    end
  endtask

  //----------------------------------------------------------------------
  // test_case_1_basic
  //----------------------------------------------------------------------

  task test_case_1_basic();
    t.test_case_begin( "test_case_1_basic" );

    //     in  out
    check( 0,  4'b0001 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_2_exhaustive
  //----------------------------------------------------------------------

  task test_case_2_exhaustive();
    t.test_case_begin( "test_case_2_exhaustive" );

    //     in  out
    check( 0,  4'b0001 );
    check( 1,  4'b0010 );
    check( 2,  4'b0100 );
    check( 3,  4'b1000 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // main
  //----------------------------------------------------------------------

  initial begin
    t.test_bench_begin();

    if ((t.n <= 0) || (t.n == 1)) test_case_1_basic();
    if ((t.n <= 0) || (t.n == 2)) test_case_2_exhaustive();

    t.test_bench_end();
  end

endmodule

