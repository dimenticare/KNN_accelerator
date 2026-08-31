`timescale 1ns / 1ps

module tb_distance;
    reg clk;
    reg rst_n;
    reg distance_start;
    reg [63:0] test;
    reg [63:0] train;

    wire [18:0] distance;
    wire distance_done;

    distance dis1 (
        .clk(clk),
        .rst_n(rst_n),
        .distance_start(distance_start),
        .test(test),
        .train(train),
        .distance(distance),
        .distance_done(distance_done)
    );

    always #5 clk = ~clk;

    initial begin
        clk   = 1'b0;
        rst_n = 1'b0;
        distance_start = 1'b1;

        test  = 64'd8;
        train = 64'd1;

        #10;
        rst_n = 1'b1;        
        #10;
        rst_n = 1'b0;
        #20;
        rst_n = 1'b1;

        test = {8'd8, 8'd7, 8'd6, 8'd5, 8'd4, 8'd3, 8'd2, 8'd1};
        train ={8'd1, 8'd2, 8'd3, 8'd4, 8'd5, 8'd6, 8'd7, 8'd8};

        #10;
        distance_start = 1'b1;
        #10;
        distance_start = 1'b0;
        #20;
        $finish;

    end

endmodule