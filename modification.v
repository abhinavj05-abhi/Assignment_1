`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 22.03.2025 02:40:38
// Design Name: 
// Module Name: modification
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

module top_module(
    input  wire            clk,
    input  wire            reset,
    input  wire signed [7:0] A,  // Multiplicand
    input  wire signed [7:0] B,  // Multiplier
    output reg  signed [15:0]sum3_reg // Final Product
);

    reg signed [7:0] A_reg, B_reg;
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            A_reg <= 0;
            B_reg <= 0;
        end else begin
            A_reg <= A;
            B_reg <= B;
        end
    end

    wire [2:0] Booth_recoded1, Booth_recoded2, Booth_recoded3, Booth_recoded4;
    assign Booth_recoded1 = {B_reg[1], B_reg[0], 1'b0};
    assign Booth_recoded2 = {B_reg[3], B_reg[2], B_reg[1]};
    assign Booth_recoded3 = {B_reg[5], B_reg[4], B_reg[3]};
    assign Booth_recoded4 = {B_reg[7], B_reg[6], B_reg[5]};
    wire signed [15:0] pp1_wire, pp2_wire, pp3_wire, pp4_wire;
    reg  signed [15:0] pp1_reg,  pp2_reg,  pp3_reg,  pp4_reg;


    pp_generator partial_product_1(.A(A_reg),.Booth_recoded(Booth_recoded1),.pp(pp1_wire));
    pp_generator partial_product_2(.A(A_reg),.Booth_recoded(Booth_recoded2), .pp(pp2_wire));
    pp_generator partial_product_3(.A(A_reg),.Booth_recoded(Booth_recoded3), .pp(pp3_wire));
    pp_generator partial_product_4( .A(A_reg),.Booth_recoded(Booth_recoded4), .pp(pp4_wire));

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            pp1_reg <= 0;
            pp2_reg <= 0;
            pp3_reg <= 0;
            pp4_reg <= 0;
        end else begin
            pp1_reg <= pp1_wire;
            pp2_reg <= pp2_wire;
            pp3_reg <= pp3_wire;
            pp4_reg <= pp4_wire;
        end
    end


    reg signed [15:0] sum1_reg, sum2_reg;
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            sum1_reg <= 0;
            sum2_reg <= 0;
        end else begin

            sum1_reg <= pp1_reg + (pp2_reg <<< 2);
            sum2_reg <= (pp3_reg <<< 4) + (pp4_reg <<< 6);
        end
    end


    always @(posedge clk or posedge reset) begin
        if (reset) begin
            sum3_reg <= 0;
        end else begin
            sum3_reg <= sum1_reg + sum2_reg;
        end
    end


endmodule


module pp_generator(
    input  wire signed [7:0] A,
    input  wire [2:0] Booth_recoded,
    output reg  signed [15:0] pp
);
    always @(*) begin
        case (Booth_recoded)
            3'b000: pp <= 16'b0;                    
            3'b001: pp <= {{8{A[7]}}, A};          
            3'b010: pp <= {{8{A[7]}}, A};          
            3'b011: pp <= {{8{A[7]}}, A} << 1;     
            3'b100: pp <= -{{8{A[7]}}, A} << 1;    
            3'b101: pp <= -{{8{A[7]}}, A};         
            3'b110: pp <= -{{8{A[7]}}, A};         
            3'b111: pp <= 16'b0;                   
            default: pp <= 16'b0;                  
        endcase
    end
endmodule


