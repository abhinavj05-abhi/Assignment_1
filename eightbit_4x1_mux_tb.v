`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 23.01.2025 15:31:25
// Design Name: 
// Module Name: eightbit_4x1_mux_tb
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


module eightbit_4x1_mux_tb;
    reg [7:0] in0, in1, in2, in3;
    reg [1:0] sel;
    wire [7:0] out;

    eightbit_4x1_mux uut (.in0(in0),.in1(in1),.in2(in2),.in3(in3),.sel(sel),.out(out));

    initial begin
        in0 = 8'b00000001; in1 = 8'b00000010; in2 = 8'b00000100; in3 = 8'b00001000; sel = 2'b00;
        #10 in0 = 8'b00000001; in1 = 8'b00000010; in2 = 8'b00000100; in3 = 8'b00001000; sel = 2'b01;
        #10 in0 = 8'b00000001; in1 = 8'b00000010; in2 = 8'b00000100; in3 = 8'b00001000; sel = 2'b10;
        #10 in0 = 8'b00000001; in1 = 8'b00000010; in2 = 8'b00000100; in3 = 8'b00001000; sel = 2'b11;
        #10 in0 = 8'b00000101; in1 = 8'b00001010; in2 = 8'b01000100; in3 = 8'b00101000;sel = 2'b01;
        #10 in0 = 8'b00000011; in1 = 8'b00100010; in2 = 8'b00001100; in3 = 8'b00011000;sel = 2'b10;
        #10 in0 = 8'b00000001; in1 = 8'b01100011; in2 = 8'b00000100; in3 = 8'b00001000;sel = 2'b11;
        #10 $finish;
    end

    initial begin
        $monitor("Time=%0t | sel=%b | out=%b", $time, sel, out);
    end

endmodule

   