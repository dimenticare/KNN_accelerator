`timescale 1ns / 1ps

module tb_topkv1;
reg clk;
reg rst_n;
reg clear;
reg valid;
reg [18:0] distance;
reg [1:0] label;

wire [18:0] dis0;
wire [18:0] dis1;
wire [18:0] dis2;
wire [18:0] dis3;
wire [18:0] dis4;

wire [1:0] label0;
wire [1:0] label1;
wire [1:0] label2;
wire [1:0] label3;
wire [1:0] label4;

topkv1 topk1 (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .valid(valid),

    .distance(distance),
    .label(label),

    .dis0(dis0),
    .dis1(dis1),
    .dis2(dis2),
    .dis3(dis3),
    .dis4(dis4),

    .label0(label0),
    .label1(label1),
    .label2(label2),
    .label3(label3),
    .label4(label4)
);

initial begin
    clk = 0;
    forever #5 clk = ~clk;
end

task send_data;
    input [18:0] distance_in;
    input [1:0] label_in;

    begin
        @(negedge clk);
        distance = distance_in;
        label = label_in;
        valid = 1;

        @(negedge clk);
        valid = 0;
    end

endtask

initial begin
    rst_n = 0;
    clear = 0;
    valid = 0;

    distance = 0;
    label = 0;

    #20;
    rst_n = 1;
    #10;
    clear = 1;
    #10;
    clear = 0;

    // --------------------------------------------------------
    // Input test data
    //
    // distance   label
    // 300        0
    // 100        1
    // 700        2
    // 200        3
    // 50         1
    // 600        2
    // 80         3
    // 400        0
    // 90         2
    // 150        1
    //
    // Expected Top-5:
    //
    // 50   label 1
    // 80   label 3
    // 90   label 2
    // 100  label 1
    // 150  label 1
    // --------------------------------------------------------

    send_data(19'd300, 2'd0);
    send_data(19'd100, 2'd1);
    send_data(19'd700, 2'd2);
    send_data(19'd200, 2'd3);
    send_data(19'd50, 2'd1);
    send_data(19'd600, 2'd2);
    send_data(19'd80, 2'd3);
    send_data(19'd400, 2'd0);
    send_data(19'd90, 2'd2);
    send_data(19'd150, 2'd1);
    #20;
    $finish;
end

endmodule