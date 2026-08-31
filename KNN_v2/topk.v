`timescale 1ns / 1ps

module topkv1(
    input wire clk,
    input wire rst_n,
    input wire clear,
    input wire valid,
    input wire [18:0] distance,
    input wire [1:0] label,

    output reg [18:0] dis0,
    output reg [18:0] dis1,
    output reg [18:0] dis2,
    output reg [18:0] dis3,
    output reg [18:0] dis4,

    output reg [1:0] label0,
    output reg [1:0] label1,
    output reg [1:0] label2,
    output reg [1:0] label3,
    output reg [1:0] label4
    );
    
    localparam [18:0] DISTANCE_MAX = {3'b111, 16'hFFFF};
    
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dis0 <= DISTANCE_MAX;
            dis1 <= DISTANCE_MAX;
            dis2 <= DISTANCE_MAX;
            dis3 <= DISTANCE_MAX;
            dis4 <= DISTANCE_MAX;

            label0 <= 2'd0;
            label1 <= 2'd0;
            label2 <= 2'd0;
            label3 <= 2'd0;
            label4 <= 2'd0;
        end
        //rstn复位
        else if (clear) begin
            dis0 <= DISTANCE_MAX;
            dis1 <= DISTANCE_MAX;
            dis2 <= DISTANCE_MAX;
            dis3 <= DISTANCE_MAX;
            dis4 <= DISTANCE_MAX;

            label0 <= 2'd0;
            label1 <= 2'd0;
            label2 <= 2'd0;
            label3 <= 2'd0;
            label4 <= 2'd0;
        end
        //clear复位，便于重复检测数据
        else if (valid) begin
        //valid=1时，当前distance和label为一组新的有效输入
            if (distance < dis0) begin
                dis4 <= dis3;
                dis3 <= dis2;
                dis2 <= dis1;
                dis1 <= dis0;
                dis0 <= distance;
            
                label4 <= label3;
                label3 <= label2;
                label2 <= label1;
                label1 <= label0;
                label0 <= label;
            end
            //首次计算结果，一定小于等于最大值，最大值时等效计入distance但无法计入label（但意义不大
            //随后若检测出输入值比原最小值还小，直接发生替代
            else if (distance < dis1) begin
                dis4 <= dis3;
                dis3 <= dis2;
                dis2 <= dis1;
                dis1 <= distance;
            
                label4 <= label3;
                label3 <= label2;
                label2 <= label1;
                label1 <= label;
            end
            //继续往较大的数值比较，若更小则余下的位置发生替换
            else if (distance < dis2) begin
                dis4 <= dis3;
                dis3 <= dis2;
                dis2 <= distance;
            
                label4 <= label3;
                label3 <= label2;
                label2 <= label;
            end
            //同上
            else if (distance < dis3) begin
                dis4 <= dis3;
                dis3 <= distance;
            
                label4 <= label3;
                label3 <= label;
            end
            //同上
            else if (distance < dis4) begin
                dis4 <= distance;
                label4 <= label;
            end
        end
        //valid的if循环结束
    end
endmodule