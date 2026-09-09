# 基于 RISC-V 的 KNN 硬件加速器

## 项目简介

本项目面向 FPGA 平台设计 KNN（K-Nearest Neighbors）硬件加速器，计划通过 Hummingbird E203 的 NICE 接口与 RISC-V 处理器集成。

当前仓库已完成 KNN 软件模型、数据预处理以及独立的 Verilog RTL 数据通路与控制逻辑。现阶段硬件采用 **K=3、二分类**，每个样本包含 **8 个 8-bit 特征**，共使用 **200 个训练样本**完成距离计算、Top-K 排序和多数投票。

> 本项目仍在开发中。目前尚未完成 NICE 接口集成及 FPGA 板级验证。

## 当前实现

硬件部分主要包含以下模块：

- `testdata.v`：接收并存储待分类的测试样本
- `traindata.v`：存储并依次读取训练样本及其标签
- `distance.v`：计算测试样本与训练样本之间的平方欧氏距离
- `topkv2.v`：保存距离最近的 3 个训练样本标签
- `voting.v`：通过多数投票输出二分类结果
- `control.v`：控制数据加载、距离计算、Top-K 更新和投票流程
- `wrapper.v`：连接各功能模块并提供统一的顶层接口

## 目录结构

```text
KNN_accelerator/
├── KNN_v1/                # 固定周期控制版本，无模块 done 返回信号
│   ├── sources/           # Verilog RTL 源代码
│   ├── simulations/       # Testbench
│   └── README.md          # RTL 模块说明
├── KNN_v2/                # 握手控制版本，带模块 done 返回信号
│   ├── sources/           # Verilog RTL 源代码
│   └── simulations/       # Testbench
├── software/              # 数据处理、软件 KNN 模型及实验结果
│   └── README.md          # 软件部分文件说明
└── README.md
```

## RTL 版本说明

| 版本 | 控制方式 | 说明 |
|------|----------|------|
| `KNN_v1` | 固定周期控制 | 控制器按照各模块预设执行周期切换状态，不接收 `done` 返回信号 |
| `KNN_v2` | 握手控制 | `distance`、`topk` 和 `voting` 模块通过 `done` 信号通知控制器操作完成 |

## 软件部分

`software` 目录包含：

- 原始数据清洗与异常项处理
- 字符串及浮点数据的整数编码
- 5-Fold 数据划分
- KNN 软件模型与交叉验证
- 四分类 `v1` 与二分类 `v2` 的实验结果

软件实验最终采用二分类方案，并确定 **K=3**，为后续 RTL 实现提供数据格式和分类结果参考。详细说明见 [`software/README.md`](software/README.md)。

## 后续工作

- 将 KNN 加速器接入 Hummingbird E203 NICE 接口
- 完成 RISC-V 自定义指令调用流程
- 开展系统级仿真与软硬件结果对比
- 在 FPGA 平台完成综合、实现及板级验证

