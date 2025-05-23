`timescale 1ns /1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 28.01.2025 15:59:13
// Design Name: 
// Module Name: test
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


module counter_N (
    input clk,        
    input rst_n,       
    input [3:0] load_value, 
    input [2:0] mode,
    input [4:0] N_switches,        
    output [15:0] LED    
);

    reg direction;
    reg [3:0]count; 
    wire [4:0] N = N_switches;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 4'b0000; // Reset the counter to 0
        end else begin
            case (mode)
                3'b000: count <= count;                                
                3'b001: count <= (count == N-1) ? 4'b0000 : count + 1; 
                3'b010: count <= (count == 4'b0000) ? N-1 : count - 1; 
                3'b011: begin
                    if (direction == 0) begin
                        if (count == N-1) begin
                            direction <= 1; // Switch to counting down when max is reached
                            count <= count - 1; // Start counting down
                        end else begin
                            count <= count + 1; // Count up
                        end
                    end else begin
                        if (count == 4'b0000) begin
                            direction <= 0; // Switch to counting up when min is reached
                            count <= count + 1; // Start counting up
                        end else begin
                            count <= count - 1; // Count down
                        end
                    end
                end
                3'b100: count <= load_value % N;                      
                3'b101: count <= 0;                                    
                default: count <= count;                               
            endcase
        end
    end
   
    assign LED = (1<< count)-1;

endmodule