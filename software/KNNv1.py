import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# Optimized KNN 5-Fold Cross Validation
# ============================================================
#
# 功能：
#   1. 读取已经划分好的 Fold1 ~ Fold5.csv
#   2. K = 1, 3, 5, 7, 9, 11, 13
#   3. 每个 K 进行 5-fold cross validation
#   4. 每轮使用 4 个 Fold 作为训练集
#   5. 剩余 1 个 Fold 作为 Validation Set
#   6. 保存全部 35 次 Accuracy
#   7. 计算每个 K 的平均 Accuracy
#   8. 自动选择最佳 K
#
# 优化：
#   对每个 Validation Fold：
#       Distance Matrix → 计算一次
#       Nearest Neighbors → 排序一次
#
#   然后所有 K 共享已经计算好的最近邻结果。
#
# 这样避免：
#   K=1 重新计算距离
#   K=3 重新计算距离
#   K=5 重新计算距离
#   ...
#
# ============================================================


# ------------------------------------------------------------
# 1. 设置路径
# ------------------------------------------------------------

# 获取当前 Python 程序所在的文件夹
BASE_DIR = Path(__file__).resolve().parent

# Fold CSV 所在文件夹
FOLD_DIR = BASE_DIR / "Health_Risk_5Fold"

# KNN 结果输出文件夹
RESULT_DIR = BASE_DIR / "KNN_Results_v1"
RESULT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 2. 定义 8 个输入特征
# ------------------------------------------------------------

FEATURE_COLUMNS = [
    "Respiratory_Rate",
    "Oxygen_Saturation",
    "O2_Scale",
    "Systolic_BP",
    "Heart_Rate",
    "Temperature",
    "Consciousness",
    "On_Oxygen"
]


# ------------------------------------------------------------
# 3. 定义输出标签
# ------------------------------------------------------------

TARGET_COLUMN = "Risk_Level"


# ------------------------------------------------------------
# 4. 定义 K 值
# ------------------------------------------------------------

# 按项目要求，只选择 1~13 中的奇数
K_VALUES = [1, 3, 5, 7, 9, 11, 13]


# ------------------------------------------------------------
# 5. 读取 Fold1 ~ Fold5
# ------------------------------------------------------------

fold_data = {}

for fold_number in range(1, 6):

    # 创建 CSV 文件路径
    file_path = FOLD_DIR / f"Fold{fold_number}.csv"

    # 检查文件是否存在
    if not file_path.exists():
        raise FileNotFoundError(
            f"找不到文件：{file_path}"
        )

    # 读取 CSV
    df = pd.read_csv(file_path)

    # 保存到字典
    fold_data[fold_number] = df


# ------------------------------------------------------------
# 6. 检查输入数据
# ------------------------------------------------------------

required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

for fold_number, df in fold_data.items():

    # 检查必要的数据列
    if not all(
        column in df.columns
        for column in required_columns
    ):
        raise ValueError(
            f"Fold{fold_number}.csv 缺少必要的数据列。"
        )

    # 检查缺失值
    if df[required_columns].isnull().any().any():
        raise ValueError(
            f"Fold{fold_number}.csv 存在缺失值。"
        )

    # 检查数据是否为空
    if len(df) == 0:
        raise ValueError(
            f"Fold{fold_number}.csv 没有数据。"
        )


# ------------------------------------------------------------
# 7. 将每个 Fold 的数据提前转换成 NumPy
# ------------------------------------------------------------
#
# 这样可以避免在后面的循环中反复进行 DataFrame → NumPy
# 的转换，提高运行速度。
# ------------------------------------------------------------

fold_X = {}
fold_y = {}

for fold_number, df in fold_data.items():

    fold_X[fold_number] = df[
        FEATURE_COLUMNS
    ].to_numpy(dtype=np.float64)

    fold_y[fold_number] = df[
        TARGET_COLUMN
    ].to_numpy()


# ------------------------------------------------------------
# 8. 开始 5-Fold Cross Validation
# ------------------------------------------------------------

# 保存所有原始实验结果
results = []


# 每一个 Fold 都轮流作为 Validation Set
for validation_fold in range(1, 6):

    # --------------------------------------------------------
    # 确定训练 Fold
    # --------------------------------------------------------
    #
    # 例如 validation_fold = 1：
    #
    # Training:
    #   Fold2 + Fold3 + Fold4 + Fold5
    #
    # Validation:
    #   Fold1
    # --------------------------------------------------------

    training_folds = [
        fold
        for fold in range(1, 6)
        if fold != validation_fold
    ]


    # --------------------------------------------------------
    # 合并 4 个训练 Fold
    # --------------------------------------------------------

    X_train = np.concatenate(
        [
            fold_X[fold]
            for fold in training_folds
        ],
        axis=0
    )

    y_train = np.concatenate(
        [
            fold_y[fold]
            for fold in training_folds
        ],
        axis=0
    )


    # --------------------------------------------------------
    # 获取当前 Validation Fold
    # --------------------------------------------------------

    X_validation = fold_X[validation_fold]
    y_validation = fold_y[validation_fold]


    # --------------------------------------------------------
    # 9. 一次性计算全部距离
    # --------------------------------------------------------
    #
    # X_validation 的形状：
    #       200 × 8
    #
    # X_train 的形状：
    #       800 × 8
    #
    # 最终 distance_matrix：
    #       200 × 800
    #
    # distance_matrix[i][j]
    # 表示：
    # 第 i 个 Validation Sample
    # 与第 j 个 Training Sample
    # 之间的欧氏距离。
    #
    # 欧氏距离：
    #
    # sqrt(
    #   (x1-y1)^2 +
    #   (x2-y2)^2 +
    #   ...
    #   (x8-y8)^2
    # )
    #
    # --------------------------------------------------------

    distance_matrix = np.sqrt(
        np.sum(
            (
                X_validation[:, np.newaxis, :]
                - X_train[np.newaxis, :, :]
            ) ** 2,
            axis=2
        )
    )


    # --------------------------------------------------------
    # 10. 一次性找到全部最近邻
    # --------------------------------------------------------
    #
    # 每一行对应一个 Validation Sample。
    #
    # argsort() 按距离从小到大排列 Training Sample。
    #
    # 由于最大的 K = 13，
    # 实际上只需要保留前 13 个最近邻。
    #
    # nearest_indices：
    #
    #       200 × 13
    #
    # --------------------------------------------------------

    nearest_indices = np.argsort(
        distance_matrix,
        axis=1
    )[:, :max(K_VALUES)]


    # --------------------------------------------------------
    # 11. 获取最近邻对应的标签
    # --------------------------------------------------------

    nearest_labels = y_train[
        nearest_indices
    ]


    # --------------------------------------------------------
    # 12. 对每一个 K 进行预测
    # --------------------------------------------------------

    for k in K_VALUES:

        # ----------------------------------------------------
        # 只取前 K 个最近邻
        # ----------------------------------------------------

        current_labels = nearest_labels[:, :k]


        # ----------------------------------------------------
        # 多数投票
        # ----------------------------------------------------
        #
        # 对每一个 Validation Sample：
        #
        #   统计 K 个邻居中每个类别出现的次数
        #
        # 然后选择出现次数最多的类别。
        #
        # 这里使用 bincount()，
        # 适合 Risk_Level 为整数类别的情况。
        # ----------------------------------------------------

        predictions = np.empty(
            len(X_validation),
            dtype=y_train.dtype
        )

        for sample_index in range(
            len(X_validation)
        ):

            labels = current_labels[
                sample_index
            ]

            # 统计每个类别出现次数
            counts = np.bincount(
                labels.astype(int)
            )

            # 找到出现次数最多的类别
            predictions[sample_index] = np.argmax(
                counts
            )


        # ----------------------------------------------------
        # 13. 计算 Accuracy
        # ----------------------------------------------------
        #
        # Accuracy =
        #
        # 正确预测数量
        # ----------------
        # 总预测数量
        #
        # ----------------------------------------------------

        correct_predictions = np.sum(
            predictions == y_validation
        )

        total_predictions = len(
            y_validation
        )

        accuracy = (
            correct_predictions
            / total_predictions
        )


        # ----------------------------------------------------
        # 14. 保存当前结果
        # ----------------------------------------------------
        #
        # 不在 Terminal 中打印每个 Accuracy。
        # 所有结果统一保存到 results。
        # ----------------------------------------------------

        results.append({

            "K": k,

            "Validation_Fold":
                validation_fold,

            "Training_Folds":
                "+".join(
                    map(str, training_folds)
                ),

            "Training_Samples":
                len(X_train),

            "Validation_Samples":
                len(X_validation),

            "Correct_Predictions":
                int(correct_predictions),

            "Total_Predictions":
                int(total_predictions),

            "Accuracy":
                accuracy,

            "Accuracy_Percent":
                accuracy * 100
        })


# ------------------------------------------------------------
# 15. 将所有原始结果转换为 DataFrame
# ------------------------------------------------------------

results_df = pd.DataFrame(results)


# ------------------------------------------------------------
# 16. 保存全部 35 次原始 Accuracy
# ------------------------------------------------------------
#
# 7 个 K × 5 个 Validation Fold = 35 条结果
#
# 这些数据完整保留，不会因为求平均值而丢失。
# ------------------------------------------------------------

raw_result_file = (
    RESULT_DIR /
    "KNN_CV_Raw_Results.csv"
)

results_df.to_csv(
    raw_result_file,
    index=False
)


# ------------------------------------------------------------
# 17. 创建 K × Fold 的 Accuracy 表
# ------------------------------------------------------------
#
# 最终形式：
#
# K | Fold1 | Fold2 | Fold3 | Fold4 | Fold5 | Average
#
# ------------------------------------------------------------

accuracy_table = (
    results_df
    .pivot(
        index="K",
        columns="Validation_Fold",
        values="Accuracy_Percent"
    )
    .reset_index()
)


# 修改列名称
accuracy_table.columns = [
    "K",
    "Fold1_Accuracy",
    "Fold2_Accuracy",
    "Fold3_Accuracy",
    "Fold4_Accuracy",
    "Fold5_Accuracy"
]


# ------------------------------------------------------------
# 18. 计算每一个 K 的平均 Accuracy
# ------------------------------------------------------------

accuracy_columns = [
    "Fold1_Accuracy",
    "Fold2_Accuracy",
    "Fold3_Accuracy",
    "Fold4_Accuracy",
    "Fold5_Accuracy"
]

accuracy_table[
    "Average_Accuracy"
] = accuracy_table[
    accuracy_columns
].mean(axis=1)


# ------------------------------------------------------------
# 19. 计算 Accuracy 的最小值、最大值和标准差
# ------------------------------------------------------------

accuracy_table[
    "Minimum_Accuracy"
] = accuracy_table[
    accuracy_columns
].min(axis=1)

accuracy_table[
    "Maximum_Accuracy"
] = accuracy_table[
    accuracy_columns
].max(axis=1)

accuracy_table[
    "Std_Accuracy"
] = accuracy_table[
    accuracy_columns
].std(axis=1)


# ------------------------------------------------------------
# 20. 找到最佳 K
# ------------------------------------------------------------

best_index = accuracy_table[
    "Average_Accuracy"
].idxmax()

best_k = int(
    accuracy_table.loc[
        best_index,
        "K"
    ]
)

best_accuracy = float(
    accuracy_table.loc[
        best_index,
        "Average_Accuracy"
    ]
)


# ------------------------------------------------------------
# 21. 保存 K 值比较结果
# ------------------------------------------------------------

comparison_file = (
    RESULT_DIR /
    "KNN_K_Comparison.csv"
)

accuracy_table.to_csv(
    comparison_file,
    index=False
)


# ------------------------------------------------------------
# 22. 保存最佳 K
# ------------------------------------------------------------

best_k_df = pd.DataFrame({

    "Best_K": [best_k],

    "Best_Average_Accuracy_Percent":
        [best_accuracy]
})


best_k_file = (
    RESULT_DIR /
    "KNN_Best_K.csv"
)

best_k_df.to_csv(
    best_k_file,
    index=False
)


# ------------------------------------------------------------
# 23. Terminal 只显示最终概要
# ------------------------------------------------------------
#
# 不输出 35 个 Accuracy。
# 详细数据已经保存在 CSV 中。
# ------------------------------------------------------------

print("=" * 60)
print("Optimized KNN 5-Fold Cross Validation completed.")
print("=" * 60)
print(
    f"Raw results saved to:\n"
    f"{raw_result_file}"
)
print(
    f"K comparison saved to:\n"
    f"{comparison_file}"
)
print(
    f"Best K saved to:\n"
    f"{best_k_file}"
)
print()
print(f"Best K = {best_k}")
print(
    f"Average Accuracy = "
    f"{best_accuracy:.4f}%"
)
print("=" * 60)