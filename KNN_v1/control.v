`timescale 1ns / 1ps

module control(
    input  wire clk,
    input  wire rst_n,
    //wrapper
    input  wire load_train_cmd,
    input  wire load_test_cmd,
    //traindata
    input  wire load_train_done,
    //testdata
    input  wire load_test_done,

    //traindata
    output reg  load_train,
    output reg  read_train_start,
    output reg  read_train_next,
    //testdata
    output reg  load_test,
    //distance
    output reg  distance_valid,
    //topk
    output reg  topk_clear,
    output reg  topk_valid,
    //voting
    output reg  voting_valid,
    //wrapper
    output reg  busy,
    output reg  prediction_valid
);

    //FSM1:
    //IDLE -> LOAD_TRAIN -> IDLE
    
    //FSM2:
    //IDLE -> LOAD_TEST -> CLEAR -> READ_TRAIN_START ->
    //DISTANCE -> TOPK -> READ_TRAIN_NEXT ->
    //(train_count < 199) -> DISTANCE -> (repeat)
    //(train_count = 199) -> VOTE -> 
    //DONE -> IDLE
    
    localparam [3:0]
        IDLE             = 4'd0,
        LOAD_TRAIN       = 4'd1,
        LOAD_TEST        = 4'd2,
        CLEAR            = 4'd3,
        READ_TRAIN_START = 4'd4,
        DISTANCE         = 4'd5,
        TOPK             = 4'd6,
        READ_TRAIN_NEXT  = 4'd7,
        VOTE             = 4'd8,
        DONE             = 4'd9;

    reg [3:0] state;
    reg [3:0] next_state;

    //单次测试已经完成topk的计数器
    reg [7:0] train_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= IDLE;
        else
            state <= next_state;
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            train_count <= 8'd0;
        end
        else begin
            //新一轮预测开始
            if (state == CLEAR) begin
                train_count <= 8'd0;
            end

            //进入到read_train_next阶段则说明数据完成了一次处理
            else if (state == READ_TRAIN_NEXT) begin
                if (train_count < 8'd199)
                    train_count <= train_count + 1'b1;
            end
        end
    end

    always @(*) begin
        next_state = state;
        case (state)
            
            //两种功能：LOAD_TRAIN/TEST
            IDLE: begin
                if (load_train_cmd)
                    next_state = LOAD_TRAIN;
                else if (load_test_cmd)
                    next_state = LOAD_TEST;
            end
            
            LOAD_TRAIN: begin
                if (load_train_done)
                    next_state = IDLE;
            end
            
            LOAD_TEST: begin
                if (load_test_done)
                    next_state = CLEAR;
            end

            CLEAR: begin
                next_state = READ_TRAIN_START;
            end

            READ_TRAIN_START: begin
                next_state = DISTANCE;
            end

            //单周期即可完成
            DISTANCE: begin
                next_state = TOPK;
            end

            //单周期即可完成
            TOPK: begin
                //无论是否最后一个train，都先进入READ_TRAIN_NEXT
                //最后一个train时，该状态用于让traindata清除read_active
                next_state = READ_TRAIN_NEXT;
            end

            //根据完成比较次数决定完成READ_TRAIN_NEXT下一个状态
            READ_TRAIN_NEXT: begin
                if (train_count == 8'd199)
                    next_state = VOTE;
                else
                    next_state = DISTANCE;
            end

            //单周期即可完成
            VOTE: begin
                next_state = DONE;
            end

            //记录有效的prediction于寄存器
            DONE: begin
                next_state = IDLE;
            end

            default: begin
                next_state = IDLE;
            end
        endcase
    end

    // Output logic
    always @(*) begin
        //traindata/testdata
        load_train = 1'b0;
        load_test = 1'b0;
        read_train_start = 1'b0;
        read_train_next = 1'b0;

        //distance
        distance_valid = 1'b0;

        //topk
        topk_clear = 1'b0;
        topk_valid = 1'b0;

        //voting
        voting_valid = 1'b0;

        //wrapper
        busy = 1'b0;
        prediction_valid = 1'b0;

        case (state)

            IDLE: begin
                busy = 1'b0;
            end

            LOAD_TRAIN: begin
                busy = 1'b1;
                    if (!load_train_done)
                        load_train = 1'b1;
            end

            LOAD_TEST: begin
                busy = 1'b1;
                    if (!load_test_done)
                        load_test = 1'b1;
            end

            CLEAR: begin
                busy = 1'b1;
                topk_clear = 1'b1;
            end

            READ_TRAIN_START: begin
                busy = 1'b1;
                read_train_start = 1'b1;
            end

            DISTANCE: begin
                busy = 1'b1;
                distance_valid = 1'b1;
            end

            TOPK: begin
                busy = 1'b1;
                topk_valid = 1'b1;
            end

            READ_TRAIN_NEXT: begin
                busy = 1'b1;
                read_train_next = 1'b1;
            end

            VOTE: begin
                busy = 1'b1;
                voting_valid = 1'b1;
            end

            DONE: begin
                busy = 1'b0;
                prediction_valid = 1'b1;
            end

            default: begin
                busy = 1'b0;
            end
        endcase
    end

endmodule