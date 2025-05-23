`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.04.2025 14:41:14
// Design Name: 
// Module Name: pe
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

module pe
  ( input  var logic        i_clk
  , input  var logic        i_arst
  , input  var logic        i_doProcess
  , input  var logic [7:0]  i_a  // Activation input
  , input  var logic [7:0]  i_b  // Weight input
  , output var logic [7:0]  o_a
  , output var logic [7:0]  o_b
  , output var logic [31:0] o_y  // Output with ReLU
  );

  // MAC for output stationary
  logic [31:0] mult;
  always_comb
    mult = i_a * i_b;

  logic [31:0] mac_d, mac_q;
  always_ff @(posedge i_clk, posedge i_arst)
    if (i_arst)
      mac_q <= '0;
    else
      mac_q <= mac_d;

  always_comb
    if (i_doProcess)
      mac_d = mac_q + mult;  // Accumulate partial sum
    else
      mac_d = '0;

  // ReLU activation
  logic [31:0] relu_out;
  always_comb
    relu_out = (mac_q[31]) ? '0 : mac_q;  // ReLU: output 0 if negative, else output mac_q

  always_comb
    o_y = relu_out;

  // Pass inputs through
  logic [7:0] a_q, b_q;
  always_ff @(posedge i_clk, posedge i_arst)
    if (i_arst)
      a_q <= '0;
    else if (i_doProcess)
      a_q <= i_a;
    else
      a_q <= a_q;

  always_ff @(posedge i_clk, posedge i_arst)
    if (i_arst)
      b_q <= '0;
    else if (i_doProcess)
      b_q <= i_b;
    else
      b_q <= b_q;

  always_comb
    o_a = a_q;
  always_comb
    o_b = b_q;
endmodule

`resetall

