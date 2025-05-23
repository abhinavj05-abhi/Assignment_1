`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 13.02.2025 16:56:28
// Design Name: 
// Module Name: partial_products
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

module pp_generator(
    input signed [7:0] A,   
    input [2:0] Booth_recoded, 
    output reg signed [15:0] pp   
);
    always @(*) begin
        case (Booth_recoded)
            3'b000: pp <= 16'b0;                    // No operation
            3'b001: pp <= {{8{A[7]}}, A};          // Add A (multiplicand)
            3'b010: pp <= {{8{A[7]}}, A};          // Add A (multiplicand)
            3'b011: pp <= {{8{A[7]}}, A} << 1;     // Add 2A
            3'b100: pp <= -{{8{A[7]}}, A} << 1;    // Subtract 2A
            3'b101: pp <= -{{8{A[7]}}, A};         // Subtract A
            3'b110: pp <= -{{8{A[7]}}, A};         // Subtract A
            3'b111: pp <= 16'b0;                   // No operation
            default: pp <= 16'b0;                  // Default case
        endcase
    end
endmodule
