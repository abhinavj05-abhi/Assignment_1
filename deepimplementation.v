`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 30.01.2025 14:42:56
// Design Name: 
// Module Name: deepimplementatin
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


module deepimplementatin(
    input [15:0] A, B,  // 16-bit inputs
    input Cin,          // Carry input
    output [15:0] Sum,  // 16-bit sum output
    output Cout         // Carry output
);

    wire [3:0] Sum0_3, Sum4_7, Sum8_11, Sum12_15; // Sum for each block
    wire [3:0] Sum0_3_c0, Sum4_7_c0, Sum8_11_c0, Sum12_15_c0; // Sum when Cin=0
    wire [3:0] Sum0_3_c1, Sum4_7_c1, Sum8_11_c1, Sum12_15_c1; // Sum when Cin=1
    wire Cout0_3, Cout4_7, Cout8_11, Cout12_15; // Carry out for each block
    wire Cout0_3_c0, Cout4_7_c0, Cout8_11_c0, Cout12_15_c0; // Cout when Cin=0
    wire Cout0_3_c1, Cout4_7_c1, Cout8_11_c1, Cout12_15_c1; // Cout when Cin=1

    // Block 0: Bits 0-3
    assign {Cout0_3_c0, Sum0_3_c0} = A[3:0] + B[3:0] + 1'b0;
    assign {Cout0_3_c1, Sum0_3_c1} = A[3:0] + B[3:0] + 1'b1;
    assign Sum0_3 = (Cin) ? Sum0_3_c1 : Sum0_3_c0;
    assign Cout0_3 = (Cin) ? Cout0_3_c1 : Cout0_3_c0;

    // Block 1: Bits 4-7
    assign {Cout4_7_c0, Sum4_7_c0} = A[7:4] + B[7:4] + 1'b0;
    assign {Cout4_7_c1, Sum4_7_c1} = A[7:4] + B[7:4] + 1'b1;
    assign Sum4_7 = (Cout0_3) ? Sum4_7_c1 : Sum4_7_c0;
    assign Cout4_7 = (Cout0_3) ? Cout4_7_c1 : Cout4_7_c0;

    // Block 2: Bits 8-11
    assign {Cout8_11_c0, Sum8_11_c0} = A[11:8] + B[11:8] + 1'b0;
    assign {Cout8_11_c1, Sum8_11_c1} = A[11:8] + B[11:8] + 1'b1;
    assign Sum8_11 = (Cout4_7) ? Sum8_11_c1 : Sum8_11_c0;
    assign Cout8_11 = (Cout4_7) ? Cout8_11_c1 : Cout8_11_c0;

    // Block 3: Bits 12-15
    assign {Cout12_15_c0, Sum12_15_c0} = A[15:12] + B[15:12] + 1'b0;
    assign {Cout12_15_c1, Sum12_15_c1} = A[15:12] + B[15:12] + 1'b1;
    assign Sum12_15 = (Cout8_11) ? Sum12_15_c1 : Sum12_15_c0;
    assign Cout12_15 = (Cout8_11) ? Cout12_15_c1 : Cout12_15_c0;

    // Final Outputs
    assign Sum = {Sum12_15, Sum8_11, Sum4_7, Sum0_3};
    assign Cout = Cout12_15;


endmodule
