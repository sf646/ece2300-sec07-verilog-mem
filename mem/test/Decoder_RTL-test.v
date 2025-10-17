//========================================================================
// Decoder_RTL-test
//========================================================================

`include "ece2300-test.v"
`include "Decoder_RTL.v"

//========================================================================
// Parameterized Test Suite
//========================================================================

module TestDecoder
#(
  parameter p_test_suite,
  parameter p_nbits
)();

  //----------------------------------------------------------------------
  // Setup
  //----------------------------------------------------------------------

  // verilator lint_off UNUSED
  logic clk;
  logic reset;
  // verilator lint_on UNUSED

  ece2300_TestUtils t( .* );

  //----------------------------------------------------------------------
  // Instantiate design under test
  //----------------------------------------------------------------------

  logic [$clog2(p_nbits)-1:0] dut_in;
  logic         [p_nbits-1:0] dut_out;

  Decoder_RTL
  #(
    .p_nbits (p_nbits)
  )
  dut
  (
    .in  (dut_in),
    .out (dut_out)
  );

  //----------------------------------------------------------------------
  // check
  //----------------------------------------------------------------------
  // All tasks start at #1 after the rising edge of the clock. So we
  // write the inputs #1 after the rising edge, and check the outputs #1
  // before the next rising edge.

  task check
  (
    input logic [$clog2(p_nbits)-1:0] in,
    input logic         [p_nbits-1:0] out
  );
    if ( !t.failed ) begin

      dut_in = in;

      #8;

      if ( t.n != 0 ) begin
        $display( "%3d: %d > %b", t.cycles, dut_in, dut_out );
      end

      `ECE2300_CHECK_EQ( dut_out, out );

      #2;

    end
  endtask

  //----------------------------------------------------------------------
  // test_case_1_basic
  //----------------------------------------------------------------------

  task test_case_1_basic();
    t.test_case_begin( "test_case_1_basic" );

    //     in  out
    check( 0,  1 );

  endtask

  //----------------------------------------------------------------------
  // test_case_2_directed_4bit
  //----------------------------------------------------------------------

  task test_case_2_directed_4bit();
    t.test_case_begin( "test_case_2_directed_4bit" );

    //     in  out
    check( 0,  p_nbits'(4'b0001) );
    check( 1,  p_nbits'(4'b0010) );
    check( 2,  p_nbits'(4'b0100) );
    check( 3,  p_nbits'(4'b1000) );

  endtask

  //----------------------------------------------------------------------
  // test_case_3_random
  //----------------------------------------------------------------------

  logic [$clog2(p_nbits)-1:0] rand_in;
  logic         [p_nbits-1:0] rand_out;

  task test_case_3_random();
    t.test_case_begin( "test_case_3_random" );

    for ( int i = 0; i < 50; i = i+1 ) begin

      // Generate random values for inputs and sel

      rand_in = $clog2(p_nbits)'($urandom(t.seed));

      // Determine correct answer

      rand_out = 0;
      rand_out[rand_in] = 1;

      // Check DUT output matches correct answer

      check( rand_in, rand_out );

    end

  endtask

  //----------------------------------------------------------------------
  // run_test_suite
  //----------------------------------------------------------------------

  string test_suite_name;

  task run_test_suite( input int test_suite, input int n );
    if (( test_suite <= 0 ) || ( test_suite == p_test_suite )) begin
      $sformat( test_suite_name, "TestSuite: %0d\nDecoder(.p_nbits(%0d))", p_test_suite, p_nbits );
      t.test_suite_begin( test_suite_name );

      if ((n <= 0) || (n == 1)) test_case_1_basic();
      if ((n <= 0) || (n == 2)) test_case_2_directed_4bit();
      if ((n <= 0) || (n == 3)) test_case_3_random();

      t.test_suite_end();
    end
  endtask

endmodule

//========================================================================
// Top
//========================================================================

module Top();

  //----------------------------------------------------------------------
  // Setup
  //----------------------------------------------------------------------

  // verilator lint_off UNUSED
  logic clk;
  logic reset;
  // verilator lint_on UNUSED

  ece2300_TestUtils t( .* );

  //----------------------------------------------------------------------
  // Parameterized Test Suites
  //----------------------------------------------------------------------

  TestDecoder
  #(
    .p_test_suite(1),
    .p_nbits(4)
  )
  test_decoder_nbits_4();

  TestDecoder
  #(
    .p_test_suite(2),
    .p_nbits(8)
  )
  test_decoder_nbits_8();

  TestDecoder
  #(
    .p_test_suite(3),
    .p_nbits(16)
  )
  test_decoder_nbits_16();

  //----------------------------------------------------------------------
  // main
  //----------------------------------------------------------------------

  initial begin
    t.test_bench_begin( `__FILE__ );

    test_decoder_nbits_4.run_test_suite ( t.test_suite, t.test_case );
    test_decoder_nbits_8.run_test_suite ( t.test_suite, t.test_case );
    test_decoder_nbits_16.run_test_suite( t.test_suite, t.test_case );

    t.test_bench_end();
  end

endmodule

