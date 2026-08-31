`timescale 1ns / 1ps

module topkv2(
    input wire clk,
    input wire rst_n,
    //control
    input wire topk_clear,
    input wire topk_valid,
    //distance
    input wire [18:0] distance_result,
    //traindata
    input wire train_label,

    //voting
    output reg label0,
    output reg label1,
    output reg label2
    );
    
    localparam [18:0] DISTANCE_MAX = {3'b111, 16'hFFFF};
    
    reg [18:0] dis0;
    reg [18:0] dis1;
    reg [18:0] dis2;
    
    //判定顺序为rst_n>clear>valid，即重启>train全轮次比较>train单轮次比较
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            dis0 <= DISTANCE_MAX;
            dis1 <= DISTANCE_MAX;
            dis2 <= DISTANCE_MAX;

            label0 <= 1'b0;
            label1 <= 1'b0;
            label2 <= 1'b0;
        end
        //rstn复位
        else if (topk_clear) begin
            dis0 <= DISTANCE_MAX;
            dis1 <= DISTANCE_MAX;
            dis2 <= DISTANCE_MAX;

            label0 <= 1'b0;
            label1 <= 1'b0;
            label2 <= 1'b0;
        end
        //clear复位，便于重复检测数据
        else if (topk_valid) begin
        //valid=1时，当前distance和label为一组新的有效输入
            if (distance_result < dis0) begin
                dis2 <= dis1;
                dis1 <= dis0;
                dis0 <= distance_result;
            
                label2 <= label1;
                label1 <= label0;
                label0 <= train_label;
            end
            //首次计算结果，一定小于等于最大值，最大值时等效计入distance但无法计入label（但意义不大
            //随后若检测出输入值比原最小值还小，直接发生替代
            else if (distance_result < dis1) begin
                dis2 <= dis1;
                dis1 <= distance_result;
            
                label2 <= label1;
                label1 <= train_label;
            end
            //继续往较大的数值比较，若更小则余下的位置发生替换
            else if (distance_result < dis2) begin
                dis2 <= distance_result;
            
                label2 <= train_label;
            end
            //同上
        end
        //valid的if循环结束
    end
    
endmodule