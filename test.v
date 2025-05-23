`timescale 1ns / 1ps
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


module tb_top_module;

    // Testbench signals
    reg clk_100MHz;       // 100 MHz clock input
    reg rst_n;            // Active-low reset
    reg [3:0] load_value; // Load value for the counter
    reg [2:0] mode;       // Mode control
    wire [15:0] LED;      // LED output (thermometric code)

    // Instantiate the top-level module
    top_module uut (
        .clk_100MHz(clk_100MHz),
        .rst_n(rst_n),
        .load_value(load_value),
        .mode(mode),
        .LED(LED)
    );

    // Clock generation (100 MHz)
    always begin
        #5 clk_100MHz = ~clk_100MHz; // Toggle clock every 5 ns (100 MHz clock)
    end

    // Test sequence
    initial begin
        // Initialize signals
        clk_100MHz = 0;
        rst_n = 0; // Start in reset
        load_value = 4'b0000;
        mode = 3'b000;

        // Apply reset
        $display("Applying reset...");
        rst_n = 0;
        #20;
        rst_n = 1; // Release reset
        $display("Reset released.");
        #20;

        // Test mode 000 (Hold value)
        $display("Testing mode 000 (Hold value)...");
        mode = 3'b000;
        #100; // Wait for a few cycles

        // Test mode 001 (Count up)
        $display("Testing mode 001 (Count up)...");
        mode = 3'b001;
        #500; // Wait to observe counting up

        // Test mode 010 (Count down)
        $display("Testing mode 010 (Count down)...");
        mode = 3'b010;
        #500; // Wait to observe counting down

        // Test mode 011 (Count up-down)
        $display("Testing mode 011 (Count up-down)...");
        mode = 3'b011;
        #1000; // Wait to observe up-down behavior

        // Test mode 100 (Load value)
        $display("Testing mode 100 (Load value)...");
        mode = 3'b100;
        load_value = 4'b0110; // Load value 6
        #200; // Observe loaded value

        // Test mode 101 (Reset counter)
        $display("Testing mode 101 (Reset counter)...");
        mode = 3'b101;
        #200;

        // End simulation
        $display("Test completed.");
        $finish;
    end

    // Monitor signals
    initial begin
        $monitor("Time: %0t | Mode: %b | Load Value: %d | LED: %b", $time, mode, load_value, LED);
    end

endmodule

