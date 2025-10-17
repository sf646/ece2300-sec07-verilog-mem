//========================================================================
// SevenSegFL
//========================================================================
// Functional level model of a seven segment display.

`ifndef SEVEN_SEG_FL_V
`define SEVEN_SEG_FL_V

module SevenSegFL
(
  input [6:0] in
);

  task write_row( int row_idx );

    if ( row_idx == 0 ) begin
      if ( ~in[0] )
        $write( " === " );
      else
        $write( "     " );
    end

    else if (( row_idx == 1 ) || ( row_idx == 2 )) begin

      if ( ~in[5] )
        $write( "|" );
      else
        $write( " " );

      $write( "   " );

      if ( ~in[1] )
        $write( "|" );
      else
        $write( " " );
    end

    else if ( row_idx == 3 ) begin
      if ( ~in[6] )
        $write( " === " );
      else
        $write( "     " );
    end

    else if (( row_idx == 4 ) || ( row_idx == 5 )) begin

      if ( ~in[4] )
        $write( "|" );
      else
        $write( " " );

      $write( "   " );

      if ( ~in[2] )
        $write( "|" );
      else
        $write( " " );
    end

    else if ( row_idx == 6 ) begin
      if ( ~in[3] )
        $write( " === " );
      else
        $write( "     " );
    end

  endtask

endmodule

`endif /* SEVEN_SEG_FL_V */

