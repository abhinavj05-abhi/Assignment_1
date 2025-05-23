`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 28.01.2025 16:28:20
// Design Name: 
// Module Name: top_module
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


module top_module (
    input clk_100MHz,       // 100 MHz clock input
    input rst_n,            // Active-low reset
    input [3:0] load_value, // Value to be loaded into the counter
    input [2:0] mode, 
    input [4:0] N_switches,      // Mode control
    output [15:0] LED       // Thermometric code LED output
);

    // Internal signals
    wire clk_1Hz;
    wire [4:0] N = N_switches;

    // Instantiate the clock divider
    clock_divider D0(
        .clk(clk_100MHz),
        .reset(rst_n),
        .clk_new(clk_1Hz)
    );

    // Instantiate the up_down_counterN module
    counter_N (
 // Example modulus value
        .clk(clk_1Hz),        // Connect the divided clock
        .rst_n(rst_n),        // Reset signal
        .load_value(load_value), // Load value for the counter
        .mode(mode),
        .N_switches(N),          // Mode control
        .LED(LED)             // Counter output to LEDs
        );
        
           binary_to_thermometric BT(.count(count), .LED(LED));

endmodule

