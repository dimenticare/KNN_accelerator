`timescale 1ns / 1ps

module wrapper (
    input  wire        clk,
    input  wire        rst_n,

    //============================================================
    // Command
    //============================================================
    input  wire        load_train_cmd,
    input  wire        load_test_cmd,

    //============================================================
    // RV32 data input
    // Train data and test data share the same input bus
    //============================================================
    input  wire        data_valid,
    input  wire [31:0] data_in,
    input  wire        label_in,

    //============================================================
    // Result / Status
    //============================================================
    output wire        busy,
    output wire        prediction,
    output wire        prediction_valid
);

    //============================================================
    // Internal wires
    //============================================================

    // control -> testdata
    wire load_test;

    // control -> traindata
    wire load_train;
    wire read_train_start;
    wire read_train_next;

    // control -> datapath
    wire distance_valid;
    wire topk_clear;
    wire topk_valid;
    wire voting_valid;

    // testdata -> control
    wire load_test_done;

    // traindata -> control
    wire load_train_done;

    // control -> datapath
    wire distance_done;
    wire topk_done;
    wire voting_done;

    // testdata -> distance
    wire [63:0] test_data;

    // traindata -> distance / topk
    wire [63:0] train_data;
    wire        train_label;

    // distance -> topk
    wire [18:0] distance_result;

    // topk -> voting
    wire label0;
    wire label1;
    wire label2;


    //============================================================
    // Control
    //============================================================
    control u_control (
        .clk                (clk),
        .rst_n              (rst_n),

        .load_train_cmd     (load_train_cmd),
        .load_test_cmd      (load_test_cmd),

        .load_train_done    (load_train_done),
        .load_test_done     (load_test_done),
        .distance_done    (distance_done),
        .topk_done     (topk_done),
        .voting_done    (voting_done),
        

        .load_train         (load_train),
        .load_test          (load_test),

        .read_train_start   (read_train_start),
        .read_train_next    (read_train_next),

        .distance_valid     (distance_valid),

        .topk_clear         (topk_clear),
        .topk_valid         (topk_valid),

        .voting_valid       (voting_valid),

        .busy               (busy),
        .prediction_valid   (prediction_valid)
    );


    //============================================================
    // Test Data
    // RV32 -> 64-bit test sample
    //============================================================
    testdata u_testdata (
        .clk                (clk),
        .rst_n              (rst_n),

        .data_valid         (data_valid),
        .data_in            (data_in),

        .load_test          (load_test),

        .load_test_done     (load_test_done),
        .test_data          (test_data)
    );


    //============================================================
    // Train Data
    // Store 200 x 64-bit training samples + labels
    //============================================================
    traindata u_traindata (
        .clk                (clk),
        .rst_n              (rst_n),

        .data_valid         (data_valid),
        .data_in            (data_in),
        .label_in           (label_in),

        .load_train         (load_train),

        .read_train_start   (read_train_start),
        .read_train_next    (read_train_next),

        .load_train_done    (load_train_done),

        .train_data         (train_data),
        .train_label        (train_label)
    );


    //============================================================
    // Distance
    //============================================================
    distance u_distance (
        .clk                (clk),
        .rst_n              (rst_n),

        .distance_valid     (distance_valid),

        .test_data          (test_data),
        .train_data         (train_data),

        .distance_done    (distance_done),
        .distance_result    (distance_result)
    );


    //============================================================
    // Top-K
    // Keep the three nearest labels
    //============================================================
    topkv2 u_topkv2 (
        .clk                (clk),
        .rst_n              (rst_n),

        .topk_clear              (topk_clear),
        .topk_valid              (topk_valid),

        .distance_result           (distance_result),
        .train_label              (train_label),

        .topk_done             (topk_done),  
        .label0             (label0),
        .label1             (label1),
        .label2             (label2)
    );


    //============================================================
    // Voting
    //============================================================
    voting u_voting (
        .clk                (clk),
        .rst_n              (rst_n),

        .voting_valid       (voting_valid),

        .label0             (label0),
        .label1             (label1),
        .label2             (label2),

        .voting_done        (voting_done),
        .prediction         (prediction)
    );

endmodule