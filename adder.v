`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 13.02.2025 16:56:02
// Design Name: 
// Module Name: adder
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


module adder_module(
    input signed [15:0] pp1, pp2, pp3, pp4, 
    output reg signed [15:0] P       
);
    always @(*) begin
        P = pp1 + (pp2 << 2) + (pp3 << 4) + (pp4 << 6);
    end
endmodule
