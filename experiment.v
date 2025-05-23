`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12.02.2025 18:55:58
// Design Name: 
// Module Name: experiment
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
    input clk,
    input reset,
    input signed [7:0] A,  
    input signed [7:0] B,   
    output reg signed [15:0] P  
);
    reg signed [7:0] A_reg, B_reg;
    wire signed [15:0] P_reg;

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            A_reg <= 0;
            B_reg <= 0;
        end else begin
            A_reg <= A;
            B_reg <= B;
        end
    end
    wire signed [15:0] pp1, pp2, pp3, pp4;
    wire [2:0] Booth_recoded1, Booth_recoded2, Booth_recoded3, Booth_recoded4;

    assign Booth_recoded1 = {B_reg[1], B_reg[0], 1'b0};
    assign Booth_recoded2 = {B_reg[3], B_reg[2], B_reg[1]};
    assign Booth_recoded3 = {B_reg[5], B_reg[4], B_reg[3]};
    assign Booth_recoded4 = {B_reg[7], B_reg[6], B_reg[5]};

    pp_generator partial_product_1( .A(A_reg), .Booth_recoded(Booth_recoded1), .pp(pp1));
    pp_generator partial_product_2( .A(A_reg), .Booth_recoded(Booth_recoded2), .pp(pp2));
    pp_generator partial_product_3( .A(A_reg), .Booth_recoded(Booth_recoded3), .pp(pp3));
    pp_generator partial_product_4( .A(A_reg), .Booth_recoded(Booth_recoded4), .pp(pp4));

    adder_module partial_product_adder( .pp1(pp1), .pp2(pp2), .pp3(pp3), .pp4(pp4), .P(P_reg));

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            P <= 0;
        end else begin
            P <= P_reg;
        end
    end
endmodule
