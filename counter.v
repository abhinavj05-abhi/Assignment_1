`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.03.2025 21:10:49
// Design Name: 
// Module Name: counter
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
    input  wire        clk,
    input  wire        rst_n,
    input  wire        enable,      
    input  wire [3:0]  load_value,  
    input  wire [2:0]  mode,        
    input  wire [4:0]  N_switches,  
    output reg  [3:0]  count
);

    reg direction;
    wire [4:0] N = (N_switches > 16) ? 16 : N_switches;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count     <= 4'b0000;
            direction <= 1'b0;
        end 
        else if (enable) begin // Use enable instead of direct pb_in
            case (mode)
                3'b000: count <= count;
                3'b001: count <= (count == N-1) ? 4'b0000 : count + 1;
                3'b010: count <= (count == 0) ? N-1 : count - 1;
                3'b011: begin
                    if (direction == 0) begin
                        if (count == N-1) begin
                            direction <= 1; count <= count - 1;
                        end else count <= count + 1;
                    end else begin
                        if (count == 0) begin
                            direction <= 0; count <= count + 1;
                        end else count <= count - 1;
                    end
                end
                3'b100: count <= load_value % N;
                3'b101: count <= 4'b0000;
                default: count <= count;
            endcase
        end
    end

endmodule

