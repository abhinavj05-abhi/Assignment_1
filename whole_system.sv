`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.04.2025 14:41:14
// Design Name: 
// Module Name: whole_system
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


module whole_system //#(
    // DVSR = clk_freq / (baud_rate * 16)
    //parameter DVSR = 54,          // 54 for 115200 baud, 651 for 9600 for 100MHz & 163 for 19,200 baud at 50MHz clk
    //parameter DVSR_BIT = 6,      // 54 accomodated in 6 bits, 651 accomodated in 10 bits for 9600 for 100MHz and 8 for 19200 baud at 50MHz clk
    //parameter int N = 4,                        // Matrix dimension
    //parameter int DATA_IN_COUNT_MAX = 2 * N * N,   // Total values to receive
    //parameter int DATA_OUT_COUNT_MAX = N * N   // Total values to transmit
//)
(
    input  clk,
    input  reset,
    input  rx,
    output reg tx
);
    //parameter DVSR = 54; //M
    //parameter DVSR_BIT = 6; //N
    parameter int N = 12;
    parameter int DATA_IN_COUNT_MAX = 2 * N * N;
    parameter int DATA_OUT_COUNT_MAX = N * N;

    // FSM States
    typedef enum logic [3:0] {
        IDLE       = 0,
        RECEIVE    = 1,
        READ_READY = 2,
        READ_DELAY = 3,
        READ       = 4,
        LOAD       = 5,
        COMPUTE    = 6,
        STORE      = 7,
        LOAD2      = 8,
        READ2_READY= 9,
        READ2_DELAY= 10,
        TRANSMIT   = 11  
    } state_t;

    state_t next_state;
    
    logic tick;
    
    mod_m_counter #(
        .N(3), // DVSR_BIT 6 for 54
        .M(7) // DVSR 7 for 921600, 54 for 115200
    )  BAUD_GEN_UNIT(
        .clk(clk), 
        .reset(reset), 
        .q(), 
        .max_tick(tick)
    );
        
        
    // Internal Signals
    logic [7:0] rx_data_out;
    logic rx_done_tick;
    
    //----------------------------------
    // UART RX Instance
    //----------------------------------
    uart_rx #(
        .DBIT(8),
        .SB_TICK(16)
    ) UART_Rx_UNIT (
        .clk(clk),
        .reset(reset),
        .rx(rx),
        .s_tick(tick),
        .rx_done_tick(rx_done_tick),
        .dout(rx_data_out)
    );

    logic       wea_in;
    logic [7:0] din_in;
    logic [7:0] dout_in;
    logic [9:0] data_count;
    logic [8:0] addr_in;
    
    logic   bram_input_full;
    logic [DATA_IN_COUNT_MAX-1:0][7:0] a_buffer;
    
    //----------------------------------
    // Input BRAM Instance with data width of 8 and depth 1024
    //----------------------------------
    blk_mem_gen_0 BRAM_INPUT (
        .clka(clk),
        .wea(wea_in),
        .addra(addr_in),
        .dina(din_in),
        .douta(dout_in)
    );
    
    
    logic [N-1:0][N-1:0][7:0] i_a;
    logic [N-1:0][N-1:0][7:0] i_b;
    logic [N-1:0][N-1:0][31:0] o_c;
    logic i_validInput;
    logic o_validResult;
    
    //----------------------------------
    // Instantiate systolic array
    //----------------------------------
    topSystolicArray #(.N(N)) MATRIX_MULT_MODULE (
        .i_clk(clk),
        .i_arst(reset),
        .i_a(i_a),
        .i_b(i_b),
        .i_validInput(i_validInput),
        .o_c(o_c),
        .o_validResult(o_validResult)
    );

    logic wea_out;
    logic [31:0] din_out;
    logic [31:0] dout_out;
    logic [8:0] data_cnt;
    logic [7:0] addr_out;
    
    logic   out_buff_full;
    logic   bram_output_full;
    logic [DATA_OUT_COUNT_MAX -1:0][31:0] out_buffer;
    
     //----------------------------------
    // Output BRAM Instance with data width of 32 and depth 512
    //----------------------------------
    blk_mem_gen_1 BRAM_OUTPUT (
        .clka(clk),
        .wea(wea_out),  
        .addra(addr_out),
        .dina(din_out),  
        .douta(dout_out)  
    );
    
    logic tx_start;
    logic done;
    logic [7:0] tx_data_out;
    logic tx_done_tick;
    //----------------------------------
    // UART TX Instance
    //----------------------------------
    uart_tx #(
        .DBIT(8),
        .SB_TICK(16)
    ) UART_Tx_UNIT (
        .clk(clk),
        .reset(reset),
        //.tx_start(bram_output_full),
        .tx_start(tx_start),
        .s_tick(tick),
        .din(tx_data_out),
        .tx_done_tick(tx_done_tick),
        .tx(tx)
    );
    
      logic [1:0] byte_cnt;
     //----------------------------------
    // Combined FSM: State, Next State, and Outputs
    //----------------------------------
    always_ff @(posedge clk or posedge reset) begin
        if (reset) begin
            next_state       <= IDLE;
            data_count       <= 0;
            data_cnt         <= 0;
            out_buff_full    <= 0;
            bram_input_full  <= 0;
            bram_output_full <= 0;
            tx_start         <= 0;
            //tx               <= 0;
            done             <= 0;  
            byte_cnt         <= 0;
        end else begin
            // State transition
        //if (!enable) begin
            done <= 0;
            case (next_state)
                IDLE: begin
                    data_count <= 0;
                    if (!done) begin
                        wea_in <= 1; 
                        next_state <= RECEIVE;
                    end
                    else begin
                        //$stop;
                        //$display;
                        //$display("Time=%0t: IDLE with done=1", $time);
                        next_state <= IDLE;
                    end
                end


                RECEIVE: begin
                    if (rx_done_tick & wea_in) begin
                        addr_in <= data_count;
                        din_in <= rx_data_out;
    
                        if (data_count == DATA_IN_COUNT_MAX-1) begin
                            bram_input_full <= 1'b1;
                            data_count <= 0;
                            next_state <= READ_READY;
                        end else begin
                            data_count <= data_count + 1;
                            next_state <= RECEIVE;
                        end
                    end else begin
                        next_state <= RECEIVE;
                    end
                end

                READ_READY: begin
                        wea_in <= 0;
                        if (bram_input_full & !wea_in) begin
                            addr_in <= data_count;
                            next_state <= READ_DELAY;
                        end
                end
                    
                READ_DELAY: begin
                        if (data_count == DATA_IN_COUNT_MAX) begin
                                next_state <= LOAD;
                        end else begin
                            next_state <= READ;
                        end
                end
                    
                READ: begin
                      a_buffer[data_count] <= dout_in;
                      data_count <= data_count + 1;
                      next_state <= READ_READY;
                end
                    
                    
                LOAD: begin
                        // Unpack a_buffer into matrices
                        for (int i = 0; i < N; i++) begin
                            for (int j = 0; j < N; j++) begin
                                i_a[i][j] <= a_buffer[i * N + j];
                                i_b[i][j] <= a_buffer[N * N + i * N + j];
                            end
                        end
                        next_state <= COMPUTE;
                end
                
                COMPUTE: begin
                    i_validInput <= 1;
                    next_state <= STORE;
                end
                
                STORE: begin
                    i_validInput <= 0;
                    if (o_validResult) begin
                        for (int i = 0; i < N; i++) begin
                            for (int j = 0; j < N; j++) begin
                                out_buffer[i * N + j] <= o_c[i][j];
                            end
                        end
                        data_cnt <= 0;
                        out_buff_full <= 1;
                        wea_out <= 1'b1;
                        next_state <= LOAD2;
                    end
                    else
                        next_state <= STORE;
                end
                
                LOAD2: begin
                    if (out_buff_full) begin
                        addr_out <= data_cnt;
                        din_out <= out_buffer[data_cnt];
    
                        if (data_cnt == DATA_OUT_COUNT_MAX - 1) begin
                            bram_output_full <= 1'b1;
                            data_cnt <= 0;
                            next_state <= READ2_READY;
                        end else begin
                            data_cnt <= data_cnt + 1;
                            next_state <= LOAD2;
                        end
                   end else 
                        next_state <= LOAD2;
                end
                
                
                READ2_READY: begin
                    wea_out <= 0;
                    tx_start<=0;
                    if (bram_output_full & !wea_out) begin
                        addr_out <= data_cnt;
                        next_state <= READ2_DELAY;
                    end
                end
                
                READ2_DELAY: begin
                        if (data_cnt == DATA_OUT_COUNT_MAX) begin
                                done<= 1;
                                //enable <= 1;
                                tx_start<=0;
                                next_state <= IDLE;
                        end else begin
                            next_state <= TRANSMIT;
                        end
                 end
                    

                
                TRANSMIT: begin
                    if (!tx_start) begin
                        // Start new transmission when UART is idle
                        tx_start <= 1;
                        tx_data_out <= dout_out[byte_cnt*8 +: 8]; // Select byte 0, 1, 2, or 3
                    end
                    if (tx_done_tick) begin
                        tx_start <= 0; // Clear tx_start
                        if (byte_cnt == 2'd3) begin
                            // All 4 bytes sent
                            byte_cnt <= 0;
                            data_cnt <= data_cnt + 1;
                            next_state <= READ2_READY;
                        end else begin
                            // Send next byte
                            byte_cnt <= byte_cnt + 1;
                        end
                    end
                end
                            
            default: next_state <= IDLE;
            endcase
        end

     //else tx_start<=0;
     //end
    end
      
endmodule

