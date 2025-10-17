//========================================================================
// ece2300-test-mem.v
//========================================================================
// A non-synthesizable memory used for testing

`ifndef ECE2300_TEST_MEM_V
`define ECE2300_TEST_MEM_V

module ece2300_TestMem
#(
  parameter NUM_WORDS = 65536,
  parameter WORD_BITS = 32,

  // Internal parameters

  parameter ADDR_BITS = $clog2(NUM_WORDS)
)(
  input  logic clk,
  input  logic reset,

  //----------------------------------------------------------------------
  // Memory Interface
  //----------------------------------------------------------------------

  input  logic                 memreq_val,
  input  logic [ADDR_BITS-1:0] memreq_addr,
  output logic                 memresp_wait,
  output logic [WORD_BITS-1:0] memresp_data
);

  //----------------------------------------------------------------------
  // Delay
  //----------------------------------------------------------------------

  int delay;
  always @( posedge clk ) begin
    if( reset )
      delay <= 0;
  end

  task set_delay( int new_delay );
    delay = new_delay;
  endtask

  //----------------------------------------------------------------------
  // Set Memory Values
  //----------------------------------------------------------------------

  logic [WORD_BITS-1:0] mem_arr [NUM_WORDS-1:0];
  always @( posedge clk ) begin
    if( reset ) begin
      for( int i = 0; i < NUM_WORDS; i = i+1 ) begin
        mem_arr[i] <= {WORD_BITS{1'b0}};
      end
    end
  end

  task set_mem
  (
    input logic [ADDR_BITS-1:0] addr,
    input logic [WORD_BITS-1:0] data
  );
    mem_arr[addr] = data;
  endtask

  //----------------------------------------------------------------------
  // Memory Interface
  //----------------------------------------------------------------------

  logic [WORD_BITS-1:0] resp_data;
  logic                 req_in_flight;

  // verilator lint_off BLKSEQ

  always @( posedge clk ) begin

    // Start #1 after the rising edge
    #1;

    if( reset ) begin
      memresp_wait  = 1'b1;
      memresp_data  = {WORD_BITS{1'bx}};
      req_in_flight = 1'b0;
    end else if( memreq_val & ~req_in_flight ) begin
      resp_data     = mem_arr[memreq_addr];
      memresp_wait  = 1'b1;
      req_in_flight = 1'b1;

      // Delay for some number of cycles
      for( int i = 0; i < delay; i = i+1 ) #10;

      // Provide the data
      memresp_data  = resp_data;
      memresp_wait  = 1'b0;
      #10;

      memresp_data  = {WORD_BITS{1'bx}};
      memresp_wait  = 1'b1;
      req_in_flight = 1'b0;
    end
  end

  // verilator lint_on BLKSEQ

endmodule

`endif // ECE2300_TEST_MEM_V
