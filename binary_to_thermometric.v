`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 31.01.2025 19:59:33
// Design Name: 
// Module Name: binary_to_thermometric
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


module binary_to_thermometric(

   input[3:0] count,
   output [15:0] LED
   );
   assign LED = (1<< count)-1;
endmodule

