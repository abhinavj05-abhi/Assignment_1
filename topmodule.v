`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.03.2025 20:18:05
// Design Name: 
// Module Name: topmodule
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
    input  wire        clk,        // 100 MHz clock
    input  wire        rst_n,     
    input  wire        pb_in,      // Asynchronous push button
    input  wire [3:0]  load_value, 
    input  wire [2:0]  mode,      
    input  wire [4:0]  N_switches, 
    output wire [15:0] LED        
);

    wire pb_pulse;
    debouncer db_inst (
        .clk      (clk),
        .rst_n    (rst_n),
        .pb_in    (pb_in),
        .pb_pulse(pb_pulse)
    );


    wire [3:0] count;
    counter_N u_counter (
        .clk       (clk),       // 100 MHz system clock
        .rst_n     (rst_n),
        .enable    (pb_pulse),  // Enable on each debounced pulse
        .load_value(load_value),
        .mode      (mode),
        .N_switches(N_switches),
        .count     (count)
    );

    binary_to_thermometric b2t (
        .count (count),
        .LED   (LED)
    );

endmodule
