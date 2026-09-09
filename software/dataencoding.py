import pandas as pd


# ============================================================
# 1. 读取原始数据集
# ============================================================

# pd.read_csv() 用于读取 CSV 文件。
# r"..." 表示原始字符串，可以避免 Windows 路径中的
# 反斜杠 "\" 被 Python 当作特殊转义字符。
df = pd.read_csv(
    r"D:\Desktop\NUS\EE5003\Dataset\Health_Risk_Dataset.csv"
)


# ============================================================
# 2. 删除 Patient_ID
# ============================================================

# Patient_ID 只是病人的唯一编号，不包含用于 KNN 分类的有效信息。
# 因此不能作为输入特征。
#
# axis=1 表示删除“列”。
# inplace=True 表示直接修改原来的 DataFrame。
df.drop("Patient_ID", axis=1, inplace=True)


# ============================================================
# 3. 编码 Consciousness
# ============================================================

# Consciousness 是类别/状态特征。
#
# 按照之前确定的方案，根据意识状态严重程度进行序数编码：
#
# A = Alert            -> 0
# C = Confusion        -> 1
# V = Verbal           -> 2
# P = Pain response    -> 3
# U = Unresponsive     -> 4
#
# 使用字典保存“原始类别 -> 数值”的对应关系。
consciousness_mapping = {
    "A": 0,
    "C": 1,
    "V": 2,
    "P": 3,
    "U": 4
}

df["Consciousness"] = df["Consciousness"].map(
    consciousness_mapping
)


# ============================================================
# 4. 编码 Risk_Level
# ============================================================

# Risk_Level 是 KNN 最终需要预测的输出标签。
#
# 按照之前确定的方案：
#
# Normal = 0
# Low    = 1
# Medium = 2
# High   = 3
#
# 这里的 0~3 是类别标签。
risk_mapping = {
    "Normal": 0,
    "Low": 1,
    "Medium": 1,
    "High": 1
}

df["Risk_Level"] = df["Risk_Level"].map(
    risk_mapping
)


# ============================================================
# 5. 检查编码是否成功
# ============================================================

# 如果 map() 找不到对应的类别，会产生 NaN。
# 因此检查编码后是否产生缺失值。
print("========== 编码检查 ==========")

print("\nConsciousness 编码后的取值：")
print(df["Consciousness"].unique())

print("\nRisk_Level 编码后的取值：")
print(df["Risk_Level"].unique())

print("\n编码后缺失值数量：")
print(df.isnull().sum())


# ============================================================
# 6. Temperature 映射到 0~255
# ============================================================

# Temperature 原始数据为 float64。
#
# 数据范围：
# 最小值 = 35.6 °C
# 最大值 = 41.8 °C
#
# 使用 Min-Max 方法将 Temperature 映射到 0~255：
#
# Temperature_8bit =
#     (Temperature - 35.6)
#     / (41.8 - 35.6)
#     * 255
#
# 映射后：
# 35.6 °C -> 0
# 41.8 °C -> 255
#
# round() 用于四舍五入到最近的整数。
# 最后转换为 uint8，保证其为 8-bit 无符号整数。

temperature_min = 35.6
temperature_max = 41.8

df["Temperature"] = (
    (df["Temperature"] - temperature_min)
    / (temperature_max - temperature_min)
    * 255
).round().astype("uint8")


# ============================================================
# 7. 检查 Temperature 映射结果
# ============================================================

print("\n========== Temperature 映射检查 ==========")

print("Temperature 数据类型：")
print(df["Temperature"].dtype)

print("\nTemperature 映射后的最小值：")
print(df["Temperature"].min())

print("\nTemperature 映射后的最大值：")
print(df["Temperature"].max())

print("\nTemperature 映射后的不同取值数量：")
print(df["Temperature"].nunique())

print("\nTemperature 映射后的前 10 条数据：")
print(df["Temperature"].head(10))


# ============================================================
# 8. 定义最终的 8 个输入特征
# ============================================================

# 经过 Patient_ID 删除以后，数据集保持：
#
# 8 个输入特征 + 1 个输出标签
#
# 特征顺序必须固定。
# 后续 Python KNN、Golden Dataset 和 RTL 都必须使用
# 完全相同的特征顺序。

feature_columns = [
    "Respiratory_Rate",
    "Oxygen_Saturation",
    "O2_Scale",
    "Systolic_BP",
    "Heart_Rate",
    "Temperature",
    "Consciousness",
    "On_Oxygen"
]

target_column = "Risk_Level"


# ============================================================
# 9. 检查最终数据结构
# ============================================================

print("\n========== 最终数据结构 ==========")

print("输入特征数量:", len(feature_columns))

print("输入特征:")
for i, feature in enumerate(feature_columns):
    print(f"{i}: {feature}")

print("\n输出标签:", target_column)

print("\n最终数据规模:")
print(df.shape)


# ============================================================
# 10. 检查最终数据类型
# ============================================================

# 检查所有用于 KNN 的数据是否已经转换成数值类型。
print("\n========== 最终数据类型 ==========")
print(df.dtypes)


# ============================================================
# 11. 查看编码后的前 10 条数据
# ============================================================

print("\n========== 编码后的前 10 条数据 ==========")
print(df.head(10))


# ============================================================
# 12. 检查 8 个输入特征的数据范围
# ============================================================

print("\n========== 8 个输入特征的数据范围 ==========")

for feature in feature_columns:
    print(
        f"{feature:20s} : "
        f"min = {df[feature].min()}, "
        f"max = {df[feature].max()}, "
        f"dtype = {df[feature].dtype}"
    )


# ============================================================
# 13. 检查输入数据是否存在缺失值
# ============================================================

print("\n========== 最终缺失值检查 ==========")

print(df[feature_columns + [target_column]].isnull().sum())


# ============================================================
# 14. 保存处理后的数据集
# ============================================================

# 使用新的文件名 Health_Risk_Dataset_Encoded2.csv
# 与之前的 Encoded 文件进行区分。
#
# index=False：
# 不把 Pandas 自动生成的行号保存到 CSV 中。

output_file = (
    r"D:\Desktop\NUS\EE5003\Dataset"
    r"\Health_Risk_Dataset_Encoded.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("\n处理后的数据集已经保存到：")
print(output_file)


# ============================================================
# 15. 输出下一阶段工作
# ============================================================

print("\n\n========== 接下来要做的步骤 ==========")

print("1. 检查处理后的 8 个输入特征是否存在异常值")
print("2. 检查 8 个输入特征的数据范围是否符合 8-bit RTL 要求")
print("3. 确认 Temperature 已完成 0~255 的 8-bit 量化")
print("4. 确认其他整数特征保持原始数值，不进行额外归一化")
print("5. 确认 Consciousness、O2_Scale 和 On_Oxygen 的编码方式")
print("6. 划分训练集和测试集")
print("7. 使用处理后的数据建立 Python KNN baseline")
print("8. 测试不同 K 值并确定最终 K")
print("9. 统计 Python KNN 的分类准确率")
print("10. 保存 Python KNN 的 Golden Dataset")
print("11. 根据 Golden Dataset 开始设计 KNN RTL")