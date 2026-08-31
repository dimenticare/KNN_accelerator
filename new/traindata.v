`timescale 1ns / 1ps

module traindata (
    input wire clk,
    input wire rst_n,
    //wrapper
    input wire data_valid,
    input wire [31:0] data_in,
    input wire label_in,
    //control
    input wire load_train,
    input wire read_train_start,
    input wire read_train_next,
    
    //control
    output reg load_train_done,
    //distance
    output reg [63:0] train_data,
    //topk
    output reg train_label
);
    //traindata和trainlabel寄存器
    reg [63:0] train_mem [0:199];
    reg label_mem [0:199];
    //traindata的加载和读取计数器
    reg [7:0] load_index;
    reg [7:0] read_index;
    //区分数据高低位：0低1高
    reg half_word;
    //处于何种状态
    reg load_active;
    reg read_active;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            load_train_done <= 1'b0;
            load_index <= 8'd0;
            read_index <= 8'd0;
            half_word <= 1'b0;
            //IDLE
            load_active <= 1'b0;
            read_active <= 1'b0;
            //清空
            train_data <= 64'd0;
            train_label <= 1'b0;
        end
        else begin
            // load_done只保持1周期
            load_train_done <= 1'b0;
            //load
            if (!load_active && !read_active) begin
                if (load_train) begin
                    load_active <= 1'b1;
                    load_index <= 8'd0;
                    half_word <= 1'b0;
                end
            end
            if (load_active) begin
                if (data_valid) begin
                    if (!half_word) begin
                        train_mem[load_index][31:0] <= data_in;
                        half_word <= 1'b1;
                    end
                    else begin
                        train_mem[load_index][63:32] <= data_in;
                        label_mem[load_index] <= label_in;
                        half_word <= 1'b0;
                        //当加载完毕，回归IDLE，输出完成信号，计数器清零
                        //仅在高位判断，避免数据遗漏
                        //判断当前是否是最后一个数据的高位
                        if (load_index == 8'd199) begin
                            load_active <= 1'b0;
                            load_train_done <= 1'b1;
                            load_index <= 8'd0;
                        end
                        else begin
                            load_index <= load_index + 1'b1;
                        end
                    end
                end
            end
            //read_start，由read_train_start信号控制
            if (!load_active && !read_active) begin
                if (read_train_start) begin
                    read_active <= 1'b1;
                    read_index <= 8'd0;
                    train_data <= train_mem[0];
                    train_label <= label_mem[0];
                end
            end
            //read_next,1-199，由read_train_next信号控制
            if (read_active) begin
                if (read_train_next) begin
                    //判断是否还有下一个traindata需要读取
                    if (read_index < 8'd199) begin
                        read_index <= read_index + 1'b1;
                        train_data <= train_mem[read_index + 1'b1];
                        train_label <= label_mem[read_index + 1'b1];
                    end
                    else begin
                        read_active <= 1'b0;
                        read_index <= 8'd0;
                    end
                end
            end
        end
    end

endmodule