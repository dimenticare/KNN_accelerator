`timescale 1ns / 1ps

module voting(
    input wire clk,
    input wire rst_n,
    //topk
    input wire label0,
    input wire label1,
    input wire label2,
    //control
    input wire voting_valid,

    //wrapper
    output reg prediction
    );
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prediction <= 1'b0;
        end
        else begin
            if (voting_valid) begin
                //多数表决
                prediction <= (label0 & label1) | (label0 & label2) | (label1 & label2);
            end
        end
    end

endmodule