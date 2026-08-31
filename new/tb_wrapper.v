`timescale 1ns / 1ps

module tb_wrapper;

    reg         clk;
    reg         rst_n;

    reg         load_train_cmd;
    reg         load_test_cmd;

    reg         data_valid;
    reg  [31:0] data_in;
    reg         label_in;

    wire        busy;
    wire        prediction;
    wire        prediction_valid;


    wrapper uut (
        .clk              (clk),
        .rst_n            (rst_n),

        .load_train_cmd   (load_train_cmd),
        .load_test_cmd    (load_test_cmd),

        .data_valid       (data_valid),
        .data_in          (data_in),
        .label_in         (label_in),

        .busy             (busy),
        .prediction       (prediction),
        .prediction_valid (prediction_valid)
    );


    //============================================================
    // Clock
    //============================================================
    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    //============================================================
    // Send one 64-bit training sample
    //============================================================
    task send_train;
        input [63:0] train_value;
        input        train_label;

        begin
            @(negedge clk);
            data_valid = 1'b1;
            data_in    = train_value[31:0];
            label_in   = train_label;

            @(negedge clk);
            data_valid = 1'b1;
            data_in    = train_value[63:32];
            label_in   = train_label;

            @(negedge clk);
            data_valid = 1'b0;
            data_in    = 32'b0;
            label_in   = 1'b0;
        end
    endtask


    //============================================================
    // Send one 64-bit test sample
    //============================================================
    task send_test;
        input [63:0] test_value;

        begin
            @(negedge clk);
            data_valid = 1'b1;
            data_in    = test_value[31:0];

            @(negedge clk);
            data_valid = 1'b1;
            data_in    = test_value[63:32];

            @(negedge clk);
            data_valid = 1'b0;
            data_in    = 32'b0;
        end
    endtask


    integer i;


    initial begin

        //========================================================
        // Initial state
        //========================================================
        rst_n          = 1'b0;
        load_train_cmd = 1'b0;
        load_test_cmd  = 1'b0;

        data_valid     = 1'b0;
        data_in        = 32'b0;
        label_in       = 1'b0;


        //========================================================
        // Reset
        //========================================================
        #12;
        rst_n = 1'b1;

        repeat (2) @(negedge clk);


         @(negedge clk);
        load_train_cmd = 1'b1;

        // Wait until control really enables traindata loading
        wait (uut.u_traindata.load_active == 1'b1);

        for (i = 0; i < 200; i = i + 1) begin
            send_train(
                i,
                i % 2
            );
        end


        // Stop train command
        @(negedge clk);
        load_train_cmd = 1'b0;

        repeat (2) @(negedge clk);


        //========================================================
        // Load test sample
        //========================================================
        @(negedge clk);
        load_test_cmd = 1'b1;


        // Wait until control really enables testdata loading
        wait (uut.load_test == 1'b1);


        send_test(
            64'd199
        );


        // Stop test command
        @(negedge clk);
        load_test_cmd = 1'b0;


        //========================================================
        // Wait for complete KNN calculation
        //========================================================
        repeat (1500) @(negedge clk);


        $finish;

    end

endmodule