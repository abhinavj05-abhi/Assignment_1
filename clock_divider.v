`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 28.01.2025 16:29:33
// Design Name: 
// Module Name: clock_divider
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


module clock_divider(
 
    input clk,reset,
    output reg clk_new
);
    reg  [26:0] counter;
    always @(posedge clk or negedge reset) begin
        if (reset == 0) begin
            counter <= 0;
            clk_new <= 0;
        end else begin
            if (counter == 99999999) begin
                counter <= 0;
                clk_new <= ~clk_new;
            end else begin
                counter <= counter + 1;
            end
        end
    end
endmodule

