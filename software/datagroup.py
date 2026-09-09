import pandas as pd
from pathlib import Path

# ============================================================
# 1. 读取数据
# ============================================================

input_path = Path(r"D:\Desktop\NUS\EE5003\Dataset\Health_Risk_Dataset_Encoded.csv")
output_path = Path(r"D:\Desktop\NUS\EE5003\Dataset\Health_Risk_Dataset_5Fold.csv")

df = pd.read_csv(input_path)

# ============================================================
# 2. 按照当前顺序划分5个Fold
#    每个Fold 200条
# ============================================================

df = df.copy()

# Sample_ID：仅用于数据追踪，不参与KNN计算
df.insert(
    0,
    "Sample_ID",
    range(1, len(df) + 1)
)

# Fold：用于5-fold交叉验证，不参与KNN计算
df.insert(
    1,
    "Fold",
    [(i // 200) + 1 for i in range(len(df))]
)

# ============================================================
# 3. 检查每个Fold的数据量
# ============================================================

fold_counts = df["Fold"].value_counts().sort_index()

if not all(fold_counts == 200):
    raise ValueError(
        "分组检查失败：不是每个Fold 200条数据。"
    )

# ============================================================
# 4. 检查Fold编号
# ============================================================

if sorted(df["Fold"].unique()) != [1, 2, 3, 4, 5]:
    raise ValueError(
        "分组检查失败：Fold编号不完整。"
    )

# ============================================================
# 5. 输出验证结果
# ============================================================

print("=" * 60)
print("5-Fold 数据分组检查")
print("=" * 60)

print("\n每个Fold的数据量：")

for fold_id in range(1, 6):

    count = fold_counts[fold_id]

    start_id = df[df["Fold"] == fold_id]["Sample_ID"].min()
    end_id = df[df["Fold"] == fold_id]["Sample_ID"].max()

    if count == 200:
        result = "PASS"
    else:
        result = "FAIL"

    print(
        f"Fold {fold_id}: "
        f"{count} 条数据, "
        f"Sample_ID {start_id} ~ {end_id}, "
        f"{result}"
    )

# ============================================================
# 6. 保存为CSV
# ============================================================

df.to_csv(
    output_path,
    index=False
)

# ============================================================
# 7. 最终检查
# ============================================================

if all(fold_counts == 200):
    print("\n最终检查：PASS")
    print("1000条数据已经正确分成5个Fold，每组200条。")
else:
    print("\n最终检查：FAIL")

print(f"\n输出文件：{output_path}")