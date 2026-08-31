# KNN_accelerator

distance.v
目的：计算train与test之间的距离
1.将test和train64位输入切割为8个8位（8*8）的特征输入
2.将各项特征输入进行差值计算
3.将差值进行平方
4.将所有平方数进行加和输出
    //control
    input wire distance_valid,			//开始信号
    //testdata
    input wire [63:0] test_data,		//test数据
    //traindata
    input wire [63:0] train_data,		//train数据
    
    //topk
    output reg [18:0] distance_result,	//两个数据之间的距离

///////////////////////////////////////////////////////////////////////////////////////////////

topk.v

topkv2.v
目的：将距离进行排序并输出最近的前K个数据的距离与label（K=3，1位输出）
1.将内部寄存器设置为最大值并与输入的距离进行比较
2.从最小的dis0开始比较
3.1若输入更小，则记录dis0和label0为输入的数据，并将原先数据传递至下一个寄存器
3.2若输入更大，则往较大的dis1进行比较；直到比较到dis2完成K=3的比较
4.输出距离最近的五个距离所对应的label
    //control
    input wire topk_clear,				//清除，便于重复检测数据
    input wire topk_valid,				//valid=1时，当前distance和label为一组新的有效输入
    //distance
    input wire [18:0] distance_result,		//输入的距离
    //traindata
    input wire train_label,				//输入的label，（1位，0-1）

    //voting
    output reg label0,			//最小距离的label
    output reg label1,			//第二小距离的label
    output reg label2			//第三小距离的label
notes：更新将K调整（5 -> 3），将label调整（2位 -> 1位），将距离输出删除并更改label的数目

topkv1.v
目的：将距离进行排序并输出最近的前K个数据的距离与label（K=5，2位输出）
1.将内部寄存器设置为最大值并与输入的距离进行比较
2.从最小的dis0开始比较
3.1若输入更小，则记录dis0和label0为输入的数据，并将原先数据传递至下一个寄存器
3.2若输入更大，则往较大的dis1进行比较；直到比较到dis4完成K=5的比较
4.输出距离最近的五个距离及其对应的label
    input wire clk,				//时钟
    input wire rst_n,				//复位
    input wire clear,				//清除，便于重复检测数据
    input wire valid,				//valid=1时，当前distance和label为一组新的有效输入
    input wire [18:0] distance,	//输入的距离
    input wire [1:0] label,		//输入的label，（2位，0-3）

    output reg [18:0] dis0,		//最小的距离
    output reg [18:0] dis1,		//第二小的距离
    output reg [18:0] dis2,		//第三小的距离
    output reg [18:0] dis3,		//第四小的距离
    output reg [18:0] dis4,		//第五小的距离

    output reg [1:0] label0,		//最小距离的label
    output reg [1:0] label1,		//第二小距离的label
    output reg [1:0] label2,		//第三小距离的label
    output reg [1:0] label3,		//第四小距离的label
    output reg [1:0] label4		//第五小距离的label

///////////////////////////////////////////////////////////////////////////////////////////////

voting.v
目的：决定测试目标的label的预测结果为0or1
少数决定多数，通过列表确定逻辑式
    //topk
    input wire label0,		//标签1
    input wire label1,		//标签2
    input wire label2,		//标签3
    //control
    input wire voting_valid	//是否为完成200次计算后的有效排序结果

    //wrapper
    output wire prediction	//预测结果

///////////////////////////////////////////////////////////////////////////////////////////////

traindata.v
目的1：存储traindata数据于寄存器		IDLE->LOAD->IDLE
目的2：调用寄存器中的traindata参与运算	IDLE->READ->IDLE
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



testdata.v
目的：读取测试的数据内容并存储到寄存器中参与后续运算
    //wrapper
    input wire data_valid,
    input wire [31:0] data_in,
    //control
    input wire load_test,
    
    //control
    output reg load_test_done,
    //distance
    output reg [63:0] test_data

///////////////////////////////////////////////////////////////////////////////////////////////

control.v
目的：加载traindata和针对testdata的计算，两种功能设计不同的状态机
    //FSM1:
    //IDLE -> LOAD_TRAIN -> IDLE
    
    //FSM2:
    //IDLE -> LOAD_TEST -> CLEAR -> READ_TRAIN_START ->
    //DISTANCE -> TOPK -> READ_TRAIN_NEXT ->
    //(train_count < 199) -> DISTANCE -> (repeat)
    //(train_count = 199) -> VOTE -> 
    //DONE -> IDLE

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
