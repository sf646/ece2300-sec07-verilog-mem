//========================================================================
// Register_4b_RTL-test
//========================================================================

`include "ece2300/ece2300-misc.v"
`include "ece2300/ece2300-test.v"

// ece2300-lint
`include "mem/Register_4b_RTL.v"

module Top();

  //--------------------------------------------------------------------
  // Setup
  //--------------------------------------------------------------------

  logic clk;
  logic rst;

  TestUtilsClkRst t( .* );

  `ECE2300_UNUSED( rst );

  //--------------------------------------------------------------------
  // Instantiate design under test
  //--------------------------------------------------------------------

  logic       en;
  logic [3:0] d;
  logic [3:0] q;

  Register_4b_RTL register( .* );

  //----------------------------------------------------------------------
  // check
  //----------------------------------------------------------------------
  // The ECE 2300 test framework adds a 1 tau delay with respect to the
  // rising clock edge at the very beginning of the test bench. So if we
  // immediately set the inputs this will take effect 1 tau after the clock
  // edge. Then we wait 8 tau, check the outputs, and wait 2 tau which
  // means the next check will again start 1 tau after the rising clock
  // edge.

  task check
  (
    input logic       en_,
    input logic [3:0] d_,
    input logic [3:0] q_,
    input logic       outputs_undefined = 0
  );
    if ( !t.failed ) begin
      t.num_checks += 1;

      en  = en_;
      d   = d_;

      #8;

      if ( t.n != 0 )
        $display( "%3d: %b %h > %h", t.cycles, en, d, q );

      if ( !outputs_undefined )
        `ECE2300_CHECK_EQ( q, q_ );

      #2;

    end
  endtask

  //--------------------------------------------------------------------
  // test_case_1_basic
  //--------------------------------------------------------------------

  task test_case_1_basic();
    t.test_case_begin( "test_case_1_basic" );

    //     en d        q
    check( 1, 4'b0000, 4'b0000, t.outputs_undefined );
    check( 1, 4'b0001, 4'b0000 );
    check( 1, 4'b0000, 4'b0001 );
    check( 1, 4'b0010, 4'b0000 );
    check( 1, 4'b0000, 4'b0010 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_2_directed_ones
  //----------------------------------------------------------------------
  // Test registering different values with a single one

  task test_case_2_directed_ones();
    t.test_case_begin( "test_case_2_directed_ones" );

    //     en d        q
    check( 1, 4'b0000, 4'b0000, t.outputs_undefined );
    check( 1, 4'b0001, 4'b0000 );
    check( 1, 4'b0010, 4'b0001 );
    check( 1, 4'b0100, 4'b0010 );
    check( 1, 4'b1000, 4'b0100 );
    check( 1, 4'b0000, 4'b1000 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_3_directed_values
  //----------------------------------------------------------------------
  // Test registering different multi-bit values

  task test_case_3_directed_values();
    t.test_case_begin( "test_case_3_directed_values" );

    //     en d        q
    check( 1, 4'b0000, 4'b0000, t.outputs_undefined );
    check( 1, 4'b0101, 4'b0000 );
    check( 1, 4'b1010, 4'b0101 );
    check( 1, 4'b1111, 4'b1010 );
    check( 1, 4'b0000, 4'b1111 );
    check( 1, 4'b0000, 4'b0000 );
    check( 1, 4'b1111, 4'b0000 );
    check( 1, 4'b0000, 4'b1111 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_4_directed_enable
  //----------------------------------------------------------------------
  // Test enable input

  task test_case_4_directed_enable();
    t.test_case_begin( "test_case_4_directed_enable" );

    //     en d        q
    check( 1, 4'b0000, 4'b0000, t.outputs_undefined );
    check( 1, 4'b0000, 4'b0000 ); // en=1
    check( 1, 4'b0011, 4'b0000 );
    check( 1, 4'b1100, 4'b0011 );

    check( 0, 4'b1111, 4'b1100 ); // en=0
    check( 0, 4'b0000, 4'b1100 );
    check( 0, 4'b1111, 4'b1100 );

    check( 1, 4'b1111, 4'b1100 ); // en=1
    check( 1, 4'b0000, 4'b1111 );
    check( 1, 4'b0000, 4'b0000 );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // test_case_5_xprop
  //----------------------------------------------------------------------

  task test_case_5_xprop();
    t.test_case_begin( "test_case_5_xprop" );

    //     en  d   q
    check( 'x, 'x, 'x, t.outputs_undefined );
    check( 'x, 'x, 'x );
    check( 'x, 'x, 'x );
    check( 'x, 'x, 'x );

    t.test_case_end();
  endtask

  //----------------------------------------------------------------------
  // main
  //----------------------------------------------------------------------

  initial begin
    t.test_bench_begin();

    if ((t.n <= 0) || (t.n == 1)) test_case_1_basic();
    if ((t.n <= 0) || (t.n == 2)) test_case_2_directed_ones();
    if ((t.n <= 0) || (t.n == 3)) test_case_3_directed_values();
    if ((t.n <= 0) || (t.n == 4)) test_case_4_directed_enable();
    if ((t.n <= 0) || (t.n == 5)) test_case_5_xprop();

    t.test_bench_end();
  end

endmodule
