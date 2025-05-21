
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.01.2025 15:50:42
// Design Name: 
// Module Name: csa_16bit
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

`timescale 1ns / 1ps
module csa_16bit(

    input  [15:0] A,    
    input  [15:0] B,    
    input         Cin,  
    output [15:0] Sum,  
    output        Cout 
);

    wire [7:0] Sum0_low, Sum1_low; 
    wire [7:0] Sum0_high, Sum1_high;  
    wire C0_low, C1_low;  
    wire C0_high, C1_high;  
    wire Carry_low;  
    assign {C0_low, Sum0_low} = A[7:0] + B[7:0] + 1'b0;  
    assign {C1_low, Sum1_low} = A[7:0] + B[7:0] + 1'b1; 
    assign {Carry_low, Sum[7:0]} = (Cin == 1'b0) ? {C0_low, Sum0_low} : {C1_low, Sum1_low};
    assign {C0_high, Sum0_high} = A[15:8] + B[15:8] + 1'b0;  
    assign {C1_high, Sum1_high} = A[15:8] + B[15:8] + 1'b1;  
    assign {Cout, Sum[15:8]} = (Carry_low == 1'b0) ? {C0_high, Sum0_high} : {C1_high, Sum1_high};
endmodule
