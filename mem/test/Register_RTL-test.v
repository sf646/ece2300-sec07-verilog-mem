//========================================================================
// Register_RTL-test
//========================================================================

`include "ece2300-test.v"
`include "Register_RTL.v"

//========================================================================
// Parameterized Test Suite
//========================================================================

module TestRegister
#(
  parameter p_test_suite,
  parameter p_nbits
)();

  //----------------------------------------------------------------------
  // Setup
  //----------------------------------------------------------------------

  logic clk;
  logic reset;

  ece2300_TestUtils t( .* );

  //----------------------------------------------------------------------
  // Instantiate design under test
  //----------------------------------------------------------------------

  logic               dut_rst;
  logic               dut_en;
  logic [p_nbits-1:0] dut_d;
  logic [p_nbits-1:0] dut_q;

  Register_RTL
  #(
    .p_nbits (p_nbits)
  )
  dut
  (
    .clk (clk),
    .rst (reset || dut_rst),
    .en  (dut_en),
    .d   (dut_d),
    .q   (dut_q)
  );

  //----------------------------------------------------------------------
  // check
  //----------------------------------------------------------------------
  // All tasks start at #1 after the rising edge of the clock. So we
  // write the inputs #1 after the rising edge, and check the outputs #1
  // before the next rising edge.

  task check
  (
    input logic               rst,
    input logic               en,
    input logic [p_nbits-1:0] d,
    input logic [p_nbits-1:0] q
  );
    if ( !t.failed ) begin

      dut_rst = rst;
      dut_en  = en;
      dut_d   = d;

      #8;

      if ( t.n != 0 ) begin
        if ( p_nbits <= 8 )
          $display( "%3d: %b %b %b > %b", t.cycles,
                    dut_rst, dut_en, dut_d, dut_q );
        else
          $display( "%3d: %b %b %h > %h", t.cycles,
                    dut_rst, dut_en, dut_d, dut_q );
      end

      `ECE2300_CHECK_EQ( dut_q, q );

      #2;

    end
  endtask

  //----------------------------------------------------------------------
  // test_case_1_basic
  //----------------------------------------------------------------------

  task test_case_1_basic();
    t.test_case_begin( "test_case_1_basic" );

    //    rst en d  q
    check( 0, 1, 0, 0 );
    check( 0, 1, 1, 0 );
    check( 0, 1, 0, 1 );
    check( 0, 1, 0, 0 );
    check( 0, 1, 0, 0 );

  endtask

  //----------------------------------------------------------------------
  // test_case_2_directed_4bit
  //----------------------------------------------------------------------

  task test_case_2_directed_4bit();
    t.test_case_begin( "test_case_2_directed_4bit" );

    //    rst en d                  q
    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b0001), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b0010), p_nbits'(4'b0001) );
    check( 0, 1, p_nbits'(4'b0011), p_nbits'(4'b0010) );

    check( 0, 1, p_nbits'(4'b0100), p_nbits'(4'b0011) );
    check( 0, 1, p_nbits'(4'b0101), p_nbits'(4'b0100) );
    check( 0, 1, p_nbits'(4'b0110), p_nbits'(4'b0101) );
    check( 0, 1, p_nbits'(4'b0111), p_nbits'(4'b0110) );

    check( 0, 1, p_nbits'(4'b1000), p_nbits'(4'b0111) );
    check( 0, 1, p_nbits'(4'b1001), p_nbits'(4'b1000) );
    check( 0, 1, p_nbits'(4'b1010), p_nbits'(4'b1001) );
    check( 0, 1, p_nbits'(4'b1011), p_nbits'(4'b1010) );

    check( 0, 1, p_nbits'(4'b1100), p_nbits'(4'b1011) );
    check( 0, 1, p_nbits'(4'b1101), p_nbits'(4'b1100) );
    check( 0, 1, p_nbits'(4'b1110), p_nbits'(4'b1101) );
    check( 0, 1, p_nbits'(4'b1111), p_nbits'(4'b1110) );

    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b1111) );

  endtask

  //----------------------------------------------------------------------
  // test_case_3_directed_4bit_enable
  //----------------------------------------------------------------------
  // Test enable input

  task test_case_3_directed_4bit_enable();
    t.test_case_begin( "test_case_3_directed_4bit_enable" );

    //    rst en d             q
    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b0000) ); // en=1
    check( 0, 1, p_nbits'(4'b0011), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b1100), p_nbits'(4'b0011) );

    check( 0, 0, p_nbits'(4'b1111), p_nbits'(4'b1100) ); // en=0
    check( 0, 0, p_nbits'(4'b0000), p_nbits'(4'b1100) );
    check( 0, 0, p_nbits'(4'b1111), p_nbits'(4'b1100) );

    check( 0, 1, p_nbits'(4'b1111), p_nbits'(4'b1100) ); // en=1
    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b1111) );
    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b0000) );

  endtask

  //----------------------------------------------------------------------
  // test_case_4_directed_4bit_reset
  //----------------------------------------------------------------------
  // Test various reset conditions

  task test_case_4_directed_4bit_reset();
    t.test_case_begin( "test_case_4_directed_4bit_reset" );

    //    rst en d                  q
    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b0011), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b1100), p_nbits'(4'b0011) );

    check( 1, 1, p_nbits'(4'b1111), p_nbits'(4'b1100) ); // rst=1, en=1
    check( 1, 1, p_nbits'(4'b1111), p_nbits'(4'b0000) );
    check( 1, 1, p_nbits'(4'b1111), p_nbits'(4'b0000) );

    check( 0, 1, p_nbits'(4'b0000), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b0011), p_nbits'(4'b0000) );
    check( 0, 1, p_nbits'(4'b1100), p_nbits'(4'b0011) );

    check( 1, 0, p_nbits'(4'b1111), p_nbits'(4'b1100) ); // rst=1, en=0
    check( 1, 0, p_nbits'(4'b1111), p_nbits'(4'b0000) );
    check( 1, 0, p_nbits'(4'b1111), p_nbits'(4'b0000) );

    check( 0, 0, p_nbits'(4'b0000), p_nbits'(4'b0000) );
    check( 0, 0, p_nbits'(4'b0011), p_nbits'(4'b0000) );
    check( 0, 0, p_nbits'(4'b1100), p_nbits'(4'b0000) );

  endtask

  //----------------------------------------------------------------------
  // test_case_5_random
  //----------------------------------------------------------------------

  logic               rand_en;
  logic [p_nbits-1:0] rand_d;
  logic [p_nbits-1:0] rand_q;

  task test_case_5_random();
    t.test_case_begin( "test_case_5_random" );

    for ( int i = 0; i < 50; i = i+1 ) begin

      // Generate random values for en, in

      rand_en = 1'($urandom(t.seed));
      rand_d  = p_nbits'($urandom(t.seed));

      // Check DUT output matches correct answer

      check( 0, rand_en, rand_d, rand_q );

      // Keep track of correct output for next check

      if ( rand_en )
        rand_q = rand_d;

    end

  endtask

  //----------------------------------------------------------------------
  // test_case_6_random_reset
  //----------------------------------------------------------------------

  logic               rand_reset_rst;
  logic               rand_reset_en;
  logic [p_nbits-1:0] rand_reset_d;
  logic [p_nbits-1:0] rand_reset_q;

  task test_case_6_random_reset();
    t.test_case_begin( "test_case_6_random_reset" );

    for ( int i = 0; i < 50; i = i+1 ) begin

      // Generate random values for rst, en, in

      rand_reset_rst = 1'($urandom(t.seed));
      rand_reset_en  = 1'($urandom(t.seed));
      rand_reset_d   = p_nbits'($urandom(t.seed));

      // Check DUT output matches correct answer

      check( rand_reset_rst, rand_reset_en, rand_reset_d, rand_reset_q );

      // Keep track of correct output for next check

      if ( rand_reset_rst )
        rand_reset_q = 0;
      else if ( rand_reset_en )
        rand_reset_q = rand_reset_d;

    end

  endtask

  //----------------------------------------------------------------------
  // run_test_suite
  //----------------------------------------------------------------------

  string test_suite_name;

  task run_test_suite( input int test_suite, input int n );
    if (( test_suite <= 0 ) || ( test_suite == p_test_suite )) begin
      $sformat( test_suite_name, "TestSuite: %0d\nRegister(.p_nbits(%0d))", p_test_suite, p_nbits );
      t.test_suite_begin( test_suite_name );

      if ((n <= 0) || (n == 1)) test_case_1_basic();
      if ((n <= 0) || (n == 2)) test_case_2_directed_4bit();
      if ((n <= 0) || (n == 3)) test_case_3_directed_4bit_enable();
      if ((n <= 0) || (n == 4)) test_case_4_directed_4bit_reset();
      if ((n <= 0) || (n == 5)) test_case_5_random();
      if ((n <= 0) || (n == 6)) test_case_6_random_reset();

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

  TestRegister
  #(
    .p_test_suite(1),
    .p_nbits(1)
  )
  test_register_nbits_1();

  TestRegister
  #(
    .p_test_suite(2),
    .p_nbits(5)
  )
  test_register_nbits_5();

  TestRegister
  #(
    .p_test_suite(3),
    .p_nbits(13)
  )
  test_register_nbits_13();

  //----------------------------------------------------------------------
  // main
  //----------------------------------------------------------------------

  initial begin
    t.test_bench_begin( `__FILE__ );

    test_register_nbits_1.run_test_suite ( t.test_suite, t.test_case );
    test_register_nbits_5.run_test_suite ( t.test_suite, t.test_case );
    test_register_nbits_13.run_test_suite( t.test_suite, t.test_case );

    t.test_bench_end();
  end

endmodule
