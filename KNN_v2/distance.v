`timescale 1ns / 1ps

module distance(
    input wire clk,
    input wire rst_n,
    //control
    input wire distance_valid,
    //testdata
    input wire [63:0] test_data,
    //traindata
    input wire [63:0] train_data,
    
    //control
    output reg distance_done,
    //topk
    output reg [18:0] distance_result 
    );
    
    wire [7:0] test0 = test_data[7:0];
    wire [7:0] test1 = test_data[15:8];
    wire [7:0] test2 = test_data[23:16];
    wire [7:0] test3 = test_data[31:24];
    wire [7:0] test4 = test_data[39:32];
    wire [7:0] test5 = test_data[47:40];
    wire [7:0] test6 = test_data[55:48];
    wire [7:0] test7 = test_data[63:56];
    
    wire [7:0] train0 = train_data[7:0];
    wire [7:0] train1 = train_data[15:8];
    wire [7:0] train2 = train_data[23:16];
    wire [7:0] train3 = train_data[31:24];
    wire [7:0] train4 = train_data[39:32];
    wire [7:0] train5 = train_data[47:40];
    wire [7:0] train6 = train_data[55:48];
    wire [7:0] train7 = train_data[63:56];
    
    wire [7:0] diff0 = (test0 >= train0) ? (test0 - train0) : (train0 - test0);
    wire [7:0] diff1 = (test1 >= train1) ? (test1 - train1) : (train1 - test1);
    wire [7:0] diff2 = (test2 >= train2) ? (test2 - train2) : (train2 - test2);
    wire [7:0] diff3 = (test3 >= train3) ? (test3 - train3) : (train3 - test3);
    wire [7:0] diff4 = (test4 >= train4) ? (test4 - train4) : (train4 - test4);
    wire [7:0] diff5 = (test5 >= train5) ? (test5 - train5) : (train5 - test5);
    wire [7:0] diff6 = (test6 >= train6) ? (test6 - train6) : (train6 - test6);
    wire [7:0] diff7 = (test7 >= train7) ? (test7 - train7) : (train7 - test7);
    
    //diff<=255 => square<=255*255<2^(8+8)=2^16
    wire [15:0] square0 = diff0 * diff0;
    wire [15:0] square1 = diff1 * diff1;
    wire [15:0] square2 = diff2 * diff2;
    wire [15:0] square3 = diff3 * diff3;
    wire [15:0] square4 = diff4 * diff4;
    wire [15:0] square5 = diff5 * diff5;
    wire [15:0] square6 = diff6 * diff6;
    wire [15:0] square7 = diff7 * diff7;
    
    //square<2^16 => distance=8*square<2*(16+3)=2*19
    wire [18:0] distance = {3'b000,square0} + {3'b000,square1} + {3'b000,square2} + {3'b000,square3} +
                         {3'b000,square4} + {3'b000,square5} + {3'b000,square6} + {3'b000,square7};
    
    always @(posedge clk or negedge rst_n) begin
        distance_done <= 1'b0;
        if (!rst_n) begin
            distance_result <= 19'd0;
        end
        else begin            
            if (distance_valid) begin
                distance_result <= distance;
                distance_done <=1'b1;
            end
        end
    end
    
endmodule