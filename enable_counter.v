`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.03.2025 14:37:07
// Design Name: 
// Module Name: enable_counter
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

module counter_N(
    input wire clk,
    input  wire         rst_n,
    input  wire         enable,      // from push button (asynchronous)
    input  wire [3:0]   load_value,  
    input  wire [2:0]   mode,        
    input  wire [4:0]   N_switches,  
    output reg  [3:0]   count
);
    reg direction;
    wire [4:0] N = (N_switches > 16) ? 16 : N_switches;

    // Trigger on every rising edge of 'enable'
    // (In practice, this is dangerous because 'enable' is asynchronous)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n ) begin
            count     <= 4'b0000;
            direction <= 1'b0; 
        end 
        else if (enable) begin
            case (mode)
                3'b000: count <= count; 
                3'b001: count <= (count == N-1) ? 4'b0000 : count + 1; 
                3'b010: count <= (count == 0) ? N-1 : count - 1;
                3'b011: begin
                    if (direction == 1'b0) begin
                        // counting up
                        if (count == N-1) begin
                            direction <= 1'b1; // switch to down
                            count <= count - 1;
                        end else begin
                            count <= count + 1;
                        end
                    end else begin
                        // counting down
                        if (count == 0) begin
                            direction <= 1'b0; // switch to up
                            count <= count + 1;
                        end else begin
                            count <= count - 1;
                        end
                    end
                end
                3'b100: count <= load_value % N;
                3'b101: count <= 4'b0000;  
                default: count <= count;   
            endcase
        end
        else
        count<=count;
    end
endmodule

