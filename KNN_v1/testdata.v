`timescale 1ns / 1ps

module testdata(
    input wire clk,
    input wire rst_n,
    //wrapper
    input wire data_valid,
    input wire [31:0] data_in,
    //control
    input wire load_test,
    
    //control
    output reg load_test_done,
    //distance
    output reg [63:0] test_data
);

    //�������ݸߵ�λ��0��1��
    reg half_word;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            test_data <= 64'b0;
            half_word <= 1'b0;
            load_test_done <= 1'b0;
        end
        else begin
            //�����һ������ɽ��
            load_test_done <= 1'b0;
            //���յ�����ָ����������Чʱ�ſ�ʼ��������
            if (load_test && data_valid) begin
                if (!half_word) begin
                    test_data[31:0] <= data_in;
                    half_word <= 1'b1;
                end
                else begin
                    test_data[63:32] <= data_in;
                    half_word <= 1'b0;
                    //���testdata����
                    load_test_done <= 1'b1;
                end
            end
            //��֤���޼���ָ���´ӵ�λ��ʼ����testdata
            if (!load_test) begin
                half_word <= 1'b0;
            end
        end
    end

endmodule