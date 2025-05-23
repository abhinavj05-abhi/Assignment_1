`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12.03.2025 01:13:26
// Design Name: 
// Module Name: SPI_BRAM_TB
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


module SPI_BRAM_TB;

    reg spi_clk;
    reg spi_ss_n;
    reg spi_mosi;
    reg resetn;
    wire spi_miso;
    


    integer file; 
 
    SPI_BRAM uut (
        .spi_clk(spi_clk),
        .spi_ss_n(spi_ss_n),
        .spi_mosi(spi_mosi),
        .resetn(resetn),
        .spi_miso(spi_miso)
    );


    always #5 spi_clk = ~spi_clk;


    task send_byte;
        input [7:0] data;
        integer i;
        begin
            for (i = 7; i >= 0; i = i - 1) begin
                spi_mosi = data[i];
                @(negedge spi_clk);  
                #10; 
            end
        end
    endtask
    

    task send_word;
        input [31:0] data;
        integer i;
        begin
            for (i = 31; i >= 0; i = i - 1) begin
                spi_mosi = data[i];
                @(negedge spi_clk);  
                #10; 
            end
        end
    endtask
    
    
    task receive_word;
        input integer word_num;
        reg [31:0] data;
        integer i;
        begin
            data = 32'h0;
            for (i = 31; i >= 0; i = i - 1) begin
                @(negedge spi_clk);  
                #10; 
                data[i] = spi_miso;
                
            end
            $fwrite(file, "Word %0d: %h\n", word_num, data); 

        end
    endtask
       
 
    initial begin

            file = $fopen("spi_read_output.txt", "w");
    spi_clk = 0;
    spi_ss_n = 1;
    resetn = 0;
    spi_mosi = 0;
    #150;  


    resetn = 1;
    #50; 

   
    spi_ss_n = 0;
    
    send_byte(8'hBD); 

    send_byte(8'h05);  
        
    send_byte(8'hA0); 
        
    send_word(32'h0123ABCD); 
        
    send_word(32'h22222222);  
        
    send_word(32'h321EDCBA);        
            
    send_word(32'h12121212);        
        
    send_word(32'h07080907);        

    #20;
    
    $display("Write operation completed");

    spi_ss_n = 1;
    #100;
    resetn = 0;
    spi_mosi = 0;
    #150;


    resetn = 1;
    #50;

 
    spi_ss_n = 0;
    
    send_byte(8'hDB);  
        
    send_byte(8'h04);  
        
    send_byte(8'hA0);  
        
    #10;
    #10; 
    
    receive_word(1); 
        
    #10;
    receive_word(2);
         
    #10;
    receive_word(3);
         
    #10;
    receive_word(4);
         
    #10;
        receive_word(5);
         
    #10;
    spi_ss_n = 1;
    #300;
    
    
        $fclose(file);

    $finish;
end

endmodule