`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:
// Design Name: 
// Module Name: 
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



module synchronizer_enable(
    input clk,                
    input rst_n,             
    input slow_clk,           // Slow clock input (1 Hz)
    output reg slow_clk_en    // Slow clock enable signal
);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            slow_clk_en <= 0;
        end else begin
            slow_clk_en <= slow_clk; // Enable on slow clock high
        end
    end

endmodule
