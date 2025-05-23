`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 25.03.2025 20:18:47
// Design Name: 
// Module Name: debouncer
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
module debouncer (
    input  wire clk,      // 100 MHz clock
    input  wire rst_n,    // Active-low reset
    input  wire pb_in,    // Asynchronous push button input
    output wire pb_pulse  // Single-clock-wide pulse output
);

    reg pb_sync1, pb_sync2;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pb_sync1 <= 1'b0;
            pb_sync2 <= 1'b0;
        end else begin
            pb_sync1 <= pb_in;   
            pb_sync2 <= pb_sync1; 
        end
    end

    
    reg [21:0] counter;   
    reg pb_db;            // Debounced output

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 20'b0;
            pb_db   <= 1'b0;
        end else begin
            if (pb_sync2 == pb_db) begin
                counter <= 20'b0;
            end else begin
                counter <= counter + 1;
                if (counter == 20'd1999999) // 20ms debounce time at 100MHz
                    pb_db <= pb_sync2; 
            end
        end
    end

   reg pb_last;
  always @(posedge clk or negedge rst_n) begin
       if (!rst_n) begin
        pb_last <= 1'b0;
     end else begin
        pb_last <= pb_db; // Store previous state
     end
  end

 assign pb_pulse = pb_db & ~pb_last; // Rising-edge detection

endmodule
