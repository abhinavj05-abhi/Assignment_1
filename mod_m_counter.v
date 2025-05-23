`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.04.2025 14:41:14
// Design Name: 
// Module Name: mod_m_counter
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


module mod_m_counter
#(
    parameter N = 10,   // number of bits in counter, 10 to achieve 9600 baud-rate@100Mhz =>log(M)(base 2)
    parameter M = 651   // mod-M, 651 for 9600 baud-rate at 100Mhz: DVSR = clk_freq / baud_rate * 16
)
(
    input wire clk, reset,
    output wire max_tick,
    output wire [N-1:0] q
);

    // signal declaration
    reg [N-1:0] r_reg;
    wire [N-1:0] r_next;

    // body
    // register
    always @(posedge clk, posedge reset)
        if (reset)
            r_reg <= 0;
        else
            r_reg <= r_next;

    // next-state logic
    assign r_next = (r_reg == (M-1)) ? 0 : r_reg + 1;

    // output logic
    assign q = r_reg;
    assign max_tick = (r_reg == (M-1)) ? 1'b1 : 1'b0;
endmodule
