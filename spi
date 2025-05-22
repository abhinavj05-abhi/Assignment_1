`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11.03.2025 19:00:04
// Design Name: 
// Module Name: SPI_BRAM
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: Optimized SPI to BRAM Interface with 4-State Machine
// 
//////////////////////////////////////////////////////////////////////////////////


module SPI_BRAM (
    input wire spi_clk,
    input wire spi_ss_n,
    input wire spi_mosi,
    input wire resetn,
    output reg spi_miso
);

    // Defining States
    reg [1:0] state;
    localparam IDLE = 2'd0,
               DECIDER = 2'd1,
               WRITE = 2'd2,
               READ = 2'd3;
               
    // Internal Registers
    reg [7:0] command;
    reg [7:0] numberof_words;
    reg [7:0] address_reg;
    reg [31:0] data_input;
    reg [5:0] bit_cnt;
    reg [8:0] word_count;
     
    // BRAM Interface Signals
    reg [31:0] bram_in;
    wire [31:0] bram_out;
    reg [7:0] bram_address;
    reg bram_we;
    wire rsta_busy;

    blk_mem_gen_0 bram(
        .clka(spi_clk),
        .rsta(!resetn),
        .ena(1'b1),
        .wea(bram_we),
        .addra(bram_address),
        .dina(bram_in),
        .douta(bram_out),
        .rsta_busy(rsta_busy)
    );

    always @(posedge spi_clk or negedge resetn) begin
        if (!resetn) begin
            state <= IDLE;
            bit_cnt <= 0;
            word_count <= 0;
            spi_miso <= 0;
            bram_we <= 0;
            command <= 0;
            numberof_words <= 0;
            address_reg <= 0;
            data_input <= 0;
        end else if (!spi_ss_n) begin
            case (state)                
                IDLE: begin
                    if (bit_cnt < 8) begin
                        command <= {command[6:0], spi_mosi};
                        bit_cnt <= bit_cnt + 1;                      
                    end 
                    else begin
                        bit_cnt <= 0;
                        state <= DECIDER;
                    end
                end

                DECIDER: begin
                    if (bit_cnt < 7) begin
                        numberof_words <= {numberof_words[6:0], spi_mosi};
                        bit_cnt <= bit_cnt + 1;
                    end else if (bit_cnt < 15) begin
                        address_reg <= {address_reg[6:0], spi_mosi};
                        bit_cnt <= bit_cnt + 1;
                    end 
                    else begin
                        bit_cnt <= 0;
                        word_count <= 0;
                        state <= (command == 8'hBD) ? WRITE : READ;
                    end
                end

                WRITE: begin
                    if (bit_cnt < 31) begin
                        data_input <= {data_input[30:0], spi_mosi};
                        bit_cnt <= bit_cnt + 1;
                    end 
                    else begin
                        bram_we <= 1;
                        bram_address <= address_reg + word_count;
                        bram_in <= data_input;
                        word_count <= word_count + 1;
                        if (word_count == numberof_words) begin
                            state <= IDLE;
                        end 
                        else begin
                            bit_cnt <= 0;
                            data_input <= 0;
                        end                      
                    end
                end
                
                READ: begin
                    if (bit_cnt < 32) begin
                        bram_address <= address_reg + word_count;
                        spi_miso <= bram_out[31 - bit_cnt];
                        bit_cnt <= bit_cnt + 1;
                    end 
                    else begin
                        if (word_count == numberof_words) begin
                            state <= IDLE;                             
                        end else begin
                            bit_cnt <= 0;
                            word_count <= word_count + 1;
                        end                     
                    end
                end
            endcase
        end else begin
            state <= IDLE;
            bram_we <= 0;
        end
    end
    
endmodule
