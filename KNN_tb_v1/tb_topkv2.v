`timescale 1ns / 1ps

module tb_topkv2;
reg clk;
reg rst_n;
reg clear;
reg valid;
reg [18:0] distance;
reg label;

wire label0;
wire label1;
wire label2;

topkv2 topk2 (
    .clk(clk),
    .rst_n(rst_n),
    .clear(clear),
    .valid(valid),

    .distance(distance),
    .label(label),

    .label0(label0),
    .label1(label1),
    .label2(label2)
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
    // 80   label 1
    // 90   label 0
    // --------------------------------------------------------

    send_data(19'd300, 1'd0);
    send_data(19'd100, 1'd1);
    send_data(19'd700, 1'd1);
    send_data(19'd200, 1'd0);
    send_data(19'd50, 1'd1);
    send_data(19'd600, 1'd1);
    send_data(19'd80, 1'd1);
    send_data(19'd400, 1'd0);
    send_data(19'd90, 1'd0);
    send_data(19'd150, 1'd1);
    #20;
    $finish;
end

endmodule