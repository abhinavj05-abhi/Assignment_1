`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.03.2025 14:35:23
// Design Name: 
// Module Name: push_button
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
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.03.2025 14:35:23
// Design Name: 
// Module Name: push_button
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

module top_module(
    input wire clk,
    input wire rst_n,  
    input wire pb_in,     
    input wire [3:0] load_value,
    input wire [2:0] mode,      
    input wire [4:0] N_switches,
    output wire [15:0] LED       
);
    
    wire pb_edge;
    
    // Edge Detector Module
    edge_detector u_edge_detector (
        .clk(clk),
        .rst_n(rst_n),
        .signal_in(pb_in),
        .edge_out(pb_edge)
    );
    
    wire [3:0] count;

    counter_N u_counter (
        .clk(clk),
        .rst_n(rst_n),
        .enable(pb_edge),      
        .load_value(load_value),
        .mode(mode),
        .N_switches(N_switches),
        .count(count)
    );
    
    binary_to_thermometric b2t (
        .count(count),
        .LED(LED)
    );
endmodule

// Edge Detector Module
module edge_detector(
    input wire clk,
    input wire rst_n,
    input wire signal_in,
    output reg edge_out
);
    reg signal_delayed;
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            signal_delayed <= 1'b0;
            edge_out <= 1'b0;
        end else begin
            edge_out <= signal_in & ~signal_delayed;
            signal_delayed <= signal_in;
        end
    end
endmodule
