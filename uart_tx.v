`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.04.2025 14:41:14
// Design Name: 
// Module Name: uart_tx
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


module uart_tx
#(
    parameter DBIT = 8,    // Data bits (32 bits)
    parameter SB_TICK = 16  // Number of clock ticks for stop bit
)
(
    input wire clk, reset,
    input wire tx_start,   // Start signal for transmission
    input wire s_tick,     // Serial tick signal
    input wire [7:0] din, // 8-bit data element to transmit
    output reg tx_done_tick, // Transmission done flag
    output wire tx         // UART transmit line
);
    // State machine states
    localparam [1:0]
        idle  = 2'b00,  // Idle state
        start = 2'b01,  // Start bit transmission
        data  = 2'b10,  // Data bits transmission
        stop  = 2'b11;  // Stop bit transmission

    // Registers for state, counters, data, and transmission output
    reg [1:0] state_reg, state_next;  // State register and next state
    reg [3:0] s_reg, s_next;          // Serial shift counter
    reg [4:0] n_reg, n_next;          // Data bit counter (up to 31 bits for 32-bit data)
    reg [31:0] b_reg, b_next;         // Data to transmit (shift register)
    reg tx_reg, tx_next;              // UART transmit register

    // State transition and data update on clock
    always @(posedge clk, posedge reset) begin
        if (reset) begin
            state_reg <= idle;
            s_reg <= 0;
            n_reg <= 0;
            b_reg <= 0;
            tx_reg <= 1'b1;  // TX is high when idle
        end else begin
            state_reg <= state_next;
            s_reg <= s_next;
            n_reg <= n_next;
            b_reg <= b_next;
            tx_reg <= tx_next;
        end
    end

    // State machine logic
    always @* begin
        // Default values
        state_next = state_reg;
        s_next = s_reg;
        n_next = n_reg;
        b_next = b_reg;
        tx_next = tx_reg;
        tx_done_tick = 1'b0;

        case (state_reg)
            idle: begin
                tx_next = 1'b1;  // UART idle state (TX high)
                if (tx_start) begin  // Start transmission when tx_start is asserted
                    state_next = start;
                    s_next = 0;
                    b_next = din;  // Load 32-bit data to transmit
                end
            end
            start: begin
                tx_next = 1'b0;  // Send start bit (TX low)
                if (s_tick) begin
                    if (s_reg == 15) begin
                        state_next = data;  // Move to data bit transmission
                        s_next = 0;
                        n_next = 0;
                    end else begin
                        s_next = s_reg + 1;  // Increment serial tick counter
                    end
                end
            end
            data: begin
                tx_next = b_reg[0];  // Send the current bit (LSB first)
                if (s_tick) begin
                    if (s_reg == 15) begin
                        s_next = 0;
                        b_next = b_reg >> 1;  // Shift the data byte to send the next bit
                        if (n_reg == (DBIT - 1)) begin
                            state_next = stop;  // All data bits transmitted, move to stop bit
                        end else begin
                            n_next = n_reg + 1;  // Increment data bit counter
                        end
                    end else begin
                        s_next = s_reg + 1;  // Increment serial tick counter
                    end
                end
            end
            stop: begin
                tx_next = 1'b1;  // Send stop bit (TX high)
                if (s_tick) begin
                    if (s_reg == (SB_TICK - 1)) begin
                        state_next = idle;  // Back to idle after stop bit
                        tx_done_tick = 1'b1;  // Indicate transmission is complete
                    end else begin
                        s_next = s_reg + 1;  // Increment serial tick counter
                    end
                end
            end
        endcase
    end

    assign tx = tx_reg;  // Output the UART transmit line
endmodule
