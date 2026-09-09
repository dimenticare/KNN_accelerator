# README.md

### Python 脚本

| 文件 | 功能 |
|------|------|
| `datacleaning.py` | 清洗原始数据中的异常值和缺失值 |
| `dataencoding.py` | 将浮点型和字符串型数据转换为整数编码，并将结果保存至 `Health_Risk_Dataset_Encoded.csv` |
| `datagroup.py` | 将编码后的数据划分为 5 Fold，并将结果保存至 `Health_Risk_Dataset_5Fold.csv` |
| `KNNv1.py` | 使用 `Health_Risk_5Fold` 中的数据进行 KNN 训练与验证，并将结果保存至 `KNN_Results` |

### CSV 数据文件

| 文件 | 内容 |
|------|------|
| `Health_Risk_Dataset.csv` | 原始数据及清洗后的数据 |
| `Health_Risk_Dataset_Encoded.csv` | 完成整数编码后的数据 |
| `Health_Risk_Dataset_5Fold.csv` | 完成编码和 5 Fold 划分后的数据 |

### 结果与 Fold 文件夹

| 文件夹 | 内容 |
|--------|------|
| `Health_Risk_5Fold/` | 按 Fold 分别存放数据，共 5 组 |
| `KNN_Results/` | 存放 KNN 的训练与验证结果 |

### KNN_Results 版本说明

| 版本 | 输出类别 | 平票处理 |
|------|----------|----------|
| `v1` | 输出分为 0、1、2、3 四类 | 出现平票时，选择数值最小的类别 |
| `v2` | 输出分为 0、1 两类 | 采用奇数 K 值，不会出现平票 |
