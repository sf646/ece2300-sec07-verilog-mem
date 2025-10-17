//========================================================================
// ece2300-xprop
//========================================================================
// Author : Simeon Turner (Cornell)
// Date   : June 23 2025
//
// ECE 2300 standard library for X-propagation handling in lab assignments.
//

`ifndef ECE2300_XPROPLIB_V
`define ECE2300_XPROPLIB_V

//------------------------------------------------------------------------
// ECE2300_XPROP1
//------------------------------------------------------------------------
// Checks if any bit in __in is undefined. If so, we X propagate to __out.

`define ECE2300_XPROP1( __out, __in )                                   \
  if ((|(__in ^ __in)) === 1'b0) begin                                  \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out = 'x;                                                         \
  end                                                                   \

//------------------------------------------------------------------------
// ECE2300_XPROP2
//------------------------------------------------------------------------
// Checks if any bit in __in0 or __in1 is undefined. If so, we X 
// propagate to __out.

`define ECE2300_XPROP2( __out, __in0, __in1 )                           \
  if (((|(__in0 ^ __in0)) === 1'b0)                                     \
      && ((|(__in1 ^ __in1)) === 1'b0)) begin                           \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out = 'x;                                                         \
  end                                                                   \

//------------------------------------------------------------------------
// ECE2300_XPROP3
//------------------------------------------------------------------------
// Checks if any bit in __in0 or __in1 or __in2 is undefined. If so, we X 
// propagate to __out.

`define ECE2300_XPROP3( __out, __in0, __in1, __in2 )                    \
  if (((|(__in0 ^ __in0)) === 1'b0)                                     \
      && ((|(__in1 ^ __in1)) === 1'b0)                                  \
      && ((|(__in2 ^ __in2)) === 1'b0)) begin                           \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out = 'x;                                                         \
  end                                                                   \

//------------------------------------------------------------------------
// ECE2300_XPROP4
//------------------------------------------------------------------------
// Checks if any bit in __in0, __in1, __in2, or __in3 is undefined. If so,
// we X propagate to __out.

`define ECE2300_XPROP4( __out, __in0, __in1, __in2, __in3 )             \
  if (((|(__in0 ^ __in0)) === 1'b0)                                     \
      && ((|(__in1 ^ __in1)) === 1'b0)                                  \
      && ((|(__in2 ^ __in2)) === 1'b0)                                  \
      && ((|(__in3 ^ __in3)) === 1'b0)) begin                           \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out = 'x;                                                         \
  end                                                                   \

//------------------------------------------------------------------------
// ECE2300_XPROP5
//------------------------------------------------------------------------
// Checks if any bit in __in0, __in1, __in2, __in3, or __in4 is undefined. 
// If so, we X propagate to __out.

`define ECE2300_XPROP5( __out, __in0, __in1, __in2, __in3, __in4 )      \
  if (((|(__in0 ^ __in0)) === 1'b0)                                     \
      && ((|(__in1 ^ __in1)) === 1'b0)                                  \
      && ((|(__in2 ^ __in2)) === 1'b0)                                  \
      && ((|(__in3 ^ __in3)) === 1'b0)                                  \
      && ((|(__in4 ^ __in4)) === 1'b0)) begin                           \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out = 'x;                                                         \
  end                                                                   \

//------------------------------------------------------------------------
// ECE2300_SEQ_XPROP1
//------------------------------------------------------------------------
// Checks if any bit in __in is undefined. If so, we X propagate to __out. 
// This uses sequential logic

`define ECE2300_SEQ_XPROP1( __out, __in )                               \
  if ((|(__in ^ __in)) === 1'b0) begin                                  \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out <= 'x;                                                        \
  end       

//------------------------------------------------------------------------
// ECE2300_SEQ_XPROP2
//------------------------------------------------------------------------
// Checks if any bit in __in is undefined. If so, we X propagate to __out. 
// This uses sequential logic

`define ECE2300_SEQ_XPROP2( __out, __in0, __in1 )                       \
  if (((|(__in0 ^ __in0)) === 1'b0)                                     \
      && ((|(__in1 ^ __in1)) === 1'b0)) begin                           \
    /* do nothing */                                                    \
  end else begin                                                        \
    __out <= 'x;                                                        \
  end       

`endif /* ECE2300_XPROPLIB_V */
