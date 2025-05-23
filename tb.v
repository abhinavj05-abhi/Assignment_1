`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12.02.2025 19:31:53
// Design Name: 
// Module Name: tb
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

module top_module_tb;
    reg clk, reset;
    reg signed [7:0] A, B;
    wire signed [15:0] P;
    

    top_module uut (
        .clk(clk),
        .reset(reset),
        .A(A),
        .B(B),
        .P(P)
    );
    
  
    initial begin
        clk = 1;
        forever #5 clk = ~clk; 
    end
    
    
    initial begin
      
        $monitor("Time = %0t | Reset = %b | A = %d | B = %d | P = %d", $time, reset, A, B, P);
        
        reset = 1;
        #120;
        reset = 0;
        
        A = 8'd3; B = 8'd2;
        #10;
        
        A = -8'd4; B = 8'd3;
        #10;
        
        A = 8'd7; B = -8'd5;
        #10;
  
        A = -8'd6; B = -8'd6;
        #10;
        
   
        A = 8'd0; B = 8'd9;
        #10;
    
        A = 8'd127; B = 8'd127;
        #10;
  
        A = -8'd128; B = -8'd128;
        #10;
        

        A = 8'd127; B = -8'd128;
        #10;
        
      
        reset = 1;
        #10;
        reset = 0;
        
     
        A = 8'd12; B = 8'd11;
        #100;
        
        $finish;
    end
endmodule
