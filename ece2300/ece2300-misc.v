//========================================================================
// ece2300-misc
//========================================================================
// Author : Christopher Batten (Cornell)
// Date   : September 5, 2025
//
// ECE 2300 miscellaneous macros
//

`ifndef ECE2300_MISC_V
`define ECE2300_MISC_V

//------------------------------------------------------------------------
// ECE2300_UNUSED
//------------------------------------------------------------------------
// We want this macro to work with slices like this:
//
//   `ECE2300_UNUSED( foo[3:0] );
//
// We use the $bits system task to get the bitwidth of the signal so we
// can declare an unused signal of the same bitwidth. So we use \signal
// to escape the signal name which means the generated signal name might
// have brackets in it. We also use `` which is token contenation in the
// Verilog processor. So the above will declare a new signal named
// \foo[3:0]_unused.
//
// We want users to add a semicolon after the macro call (see above) so
// we need to be careful we do not end up with two semicolons. This is
// why the assign does not have a trailing semicolon. The semicolon after
// the actual macro call will turn into the semicolon at the end of the
// assign.
//
// This macro does not work on Quartus, so we check to see if we are
// using Quartus with the ALTERA_RESERVED_QIS preprocessor macro. If so,
// we simply turn this macro into always @(*) which does nothing. Again
// there is no trailing semicolon because we will pick up the semicolon
// after the actual macro call.
//

`ifndef ALTERA_RESERVED_QIS
`define ECE2300_UNUSED( signal_ )                 \
  logic [$bits(signal_)-1:0] \signal_``_unused ;  \
  assign \signal_``_unused = signal_
`else
`define ECE2300_UNUSED( signal_ ) \
  always @(*)
`endif

//------------------------------------------------------------------------
// ECE2300_UNDRIVEN
//------------------------------------------------------------------------
// We use the $bits system task to get the bitwidth of the signal so we
// can use the repeat operator to create a literal with all Zs. Unlike
// just using 'z, this approach works in Verilog-2001 and SystemVerilog.
// We want users to add a semicolon after the macro call so we need to be
// careful we do not end up with two semicolons. This is why the assign
// does not have a trailing semicolon. The semicolon after the actual
// macro call will turn into the semicolon at the end of the assign.

`define ECE2300_UNDRIVEN( signal_ ) \
  assign signal_ = {$bits(signal_){1'bz}}

//------------------------------------------------------------------------
// ECE2300_XPROP
//------------------------------------------------------------------------
// This macro enables forcing a signal to be 'x to avoid X-optimism in
// combinational logic. You can use it in an always_comb block like this:
//
//  always_comb begin
//
//    a = 'x;
//
//    if ( b )
//      a = c;
//
//    `ECE2300_XPROP( a, $isunknown(b) );
//
//  end
//

`ifndef ALTERA_RESERVED_QIS
`define ECE2300_XPROP( signal_, expression_ ) \
  if ( expression_ ) \
    signal_ = 'x; \
  if (0)
`else
`define ECE2300_XPROP( signal_, expression_ ) \
  if (0)
`endif

//------------------------------------------------------------------------
// ECE2300_SEQ_XPROP
//------------------------------------------------------------------------
// This macro enables forcing a signal to be 'x to avoid X-optimism in
// combinational logic. You can use it in an always_comb block like this:
//
//  always_ff @( posedge clk ) begin
//
//    if ( rst )
//      q <= 1'b0;
//    else
//      q <= d;
//
//    `ECE2300_SEQ_XPROP( q, $isunknown(rst) );
//
//  end
//

`ifndef ALTERA_RESERVED_QIS
`define ECE2300_SEQ_XPROP( signal_, expression_ ) \
  if ( expression_ ) \
    signal_ <= 'x; \
  if (0)
`else
`define ECE2300_SEQ_XPROP( signal_, expression_ ) \
  if (0)
`endif

`endif /* ECE2300_MISC */

