`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.04.2025 14:41:14
// Design Name: 
// Module Name: systolicArray
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


`default_nettype none

module systolicArray
  #(parameter int unsigned N = 16)
  ( input  var logic                         i_clk
  , input  var logic                         i_arst

  , input  var logic                         i_doProcess

  , input  var logic [N-1:0][(2*N)-2:0][7:0] i_row
  , input  var logic [N-1:0][(2*N)-2:0][7:0] i_col

  , output var logic [N-1:0][N-1:0][31:0]    o_c
  );

  /* verilator lint_off UNUSED */
  // Variable used to pass data horizontally between PEs in the same row. The
  // output o_a of one PE is connected to the input i_a of the PE to its right.
  logic [N-1:0][N:0][7:0] rowInterConnect;

  // Variable used to pass data vertically between PEs in the same column. The
  // output o_b of one PE is connected to the input i_b of the PE below it.
  logic [N:0][N-1:0][7:0] colInterConnect;
  /* verilator lint_off UNUSED */

  for (genvar i = 0; i < N; i++) begin: PerDummyRowColInterconnect

    // These are dummy interconnects used to pass data from the row matrices to
    // the i_a ports of PE in the first col.
    always_comb
      rowInterConnect[i][0] = i_row[i][0];

    // These are dummy interconnects used to pass data  from the col matrices to
    // the i_b ports of PE in the first row.
    always_comb
      colInterConnect[0][i] = i_col[i][0];

  end: PerDummyRowColInterconnect

  for (genvar i = 0; i < N; i++) begin: PerRow
    for (genvar j = 0; j < N; j++) begin: PerCol

      pe u_pe
      ( .i_clk
      , .i_arst

      , .i_doProcess

      , .i_a (rowInterConnect[i][j])
      , .i_b (colInterConnect[i][j])

      , .o_a (rowInterConnect[i][j+1])
      , .o_b (colInterConnect[i+1][j])
      , .o_y (o_c[i][j])
      );

    end: PerCol
  end: PerRow

endmodule

`resetall
