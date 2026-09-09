import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# KNNv2 - Binary KNN 5-Fold Cross Validation
# ============================================================
#
# Classification:
#
#   Original Risk_Level:
#       Normal
#       Low
#       Medium
#       High
#
#   Binary Risk_Level:
#       Normal                  -> 0
#       Low / Medium / High     -> 1 (Abnormal)
#
# Because this is a binary classification problem and
# all K values are odd numbers, voting ties cannot occur.
#
# ============================================================


# ------------------------------------------------------------
# 1. 设置路径
# ------------------------------------------------------------

# 获取当前 Python 程序所在文件夹
BASE_DIR = Path(__file__).resolve().parent

# Fold CSV 所在文件夹
FOLD_DIR = BASE_DIR / "Health_Risk_5Fold"

# KNNv2 结果输出文件夹
RESULT_DIR = BASE_DIR / "KNN_Results_v2"
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

K_VALUES = [1, 3, 5, 7, 9, 11, 13]


# ------------------------------------------------------------
# 5. Risk_Level 二分类转换函数
# ------------------------------------------------------------
#
# Binary Classification:
#
#   Normal  -> 0
#
#   Low     -> 1
#   Medium  -> 1
#   High    -> 1
#
# 同时兼容原 Risk_Level 已经编码成：
#
#   0 = Normal
#   1 = Low
#   2 = Medium
#   3 = High
#
# ------------------------------------------------------------

def convert_to_binary_labels(labels):

    binary_labels = []

    for label in labels:

        # ----------------------------------------------------
        # 情况 1：
        # Risk_Level 为字符串
        # ----------------------------------------------------

        if isinstance(label, str):

            label_clean = label.strip().lower()

            if label_clean == "normal":

                binary_labels.append(0)

            elif label_clean in [
                "low",
                "medium",
                "high"
            ]:

                binary_labels.append(1)

            else:

                raise ValueError(
                    f"发现未知 Risk_Level：{label}"
                )


        # ----------------------------------------------------
        # 情况 2：
        # Risk_Level 已经是数字编码
        # ----------------------------------------------------

        else:

            label_int = int(label)

            if label_int == 0:

                binary_labels.append(0)

            elif label_int in [1, 2, 3]:

                binary_labels.append(1)

            else:

                raise ValueError(
                    f"发现未知 Risk_Level 编码：{label}"
                )


    return np.array(
        binary_labels,
        dtype=np.int64
    )


# ------------------------------------------------------------
# 6. 读取 Fold1 ~ Fold5
# ------------------------------------------------------------

fold_data = {}

for fold_number in range(1, 6):

    file_path = (
        FOLD_DIR /
        f"Fold{fold_number}.csv"
    )

    if not file_path.exists():

        raise FileNotFoundError(
            f"找不到文件：{file_path}"
        )

    df = pd.read_csv(
        file_path
    )

    fold_data[
        fold_number
    ] = df


# ------------------------------------------------------------
# 7. 检查输入数据
# ------------------------------------------------------------

required_columns = (
    FEATURE_COLUMNS +
    [TARGET_COLUMN]
)


for fold_number, df in fold_data.items():

    # 检查必要的数据列
    if not all(
        column in df.columns
        for column in required_columns
    ):

        raise ValueError(
            f"Fold{fold_number}.csv "
            f"缺少必要的数据列。"
        )


    # 检查缺失值
    if df[
        required_columns
    ].isnull().any().any():

        raise ValueError(
            f"Fold{fold_number}.csv "
            f"存在缺失值。"
        )


    # 检查数据是否为空
    if len(df) == 0:

        raise ValueError(
            f"Fold{fold_number}.csv "
            f"没有数据。"
        )


# ------------------------------------------------------------
# 8. 将每个 Fold 转换为 NumPy
# ------------------------------------------------------------

fold_X = {}
fold_y = {}


for fold_number, df in fold_data.items():

    # 输入特征
    fold_X[
        fold_number
    ] = df[
        FEATURE_COLUMNS
    ].to_numpy(
        dtype=np.float64
    )


    # 获取原始 Risk_Level
    original_labels = df[
        TARGET_COLUMN
    ].to_numpy()


    # 转换为二分类标签
    fold_y[
        fold_number
    ] = convert_to_binary_labels(
        original_labels
    )


# ------------------------------------------------------------
# 9. 检查二分类转换结果
# ------------------------------------------------------------

for fold_number in range(1, 6):

    unique_labels = np.unique(
        fold_y[
            fold_number
        ]
    )

    if not np.all(
        np.isin(
            unique_labels,
            [0, 1]
        )
    ):

        raise ValueError(
            f"Fold{fold_number} "
            f"二分类标签转换失败。"
        )


# ------------------------------------------------------------
# 10. 开始 5-Fold Cross Validation
# ------------------------------------------------------------

results = []


# 每一个 Fold 都轮流作为 Validation Set
for validation_fold in range(1, 6):


    # --------------------------------------------------------
    # 确定 Training Folds
    # --------------------------------------------------------

    training_folds = [

        fold

        for fold in range(1, 6)

        if fold != validation_fold
    ]


    # --------------------------------------------------------
    # 合并四个 Training Fold
    # --------------------------------------------------------

    X_train = np.concatenate(

        [
            fold_X[
                fold
            ]

            for fold in training_folds
        ],

        axis=0
    )


    y_train = np.concatenate(

        [
            fold_y[
                fold
            ]

            for fold in training_folds
        ],

        axis=0
    )


    # --------------------------------------------------------
    # 获取当前 Validation Fold
    # --------------------------------------------------------

    X_validation = fold_X[
        validation_fold
    ]

    y_validation = fold_y[
        validation_fold
    ]


    # --------------------------------------------------------
    # 11. 计算 Squared Euclidean Distance
    # --------------------------------------------------------
    #
    # d^2 =
    #
    # (x1-y1)^2
    # + (x2-y2)^2
    # + ...
    # + (x8-y8)^2
    #
    # 不进行 sqrt()。
    #
    # 因为 sqrt() 是单调函数，
    # 是否开平方不会影响最近邻排序。
    #
    # 这也与后续 RTL distance module
    # 使用 squared L2 distance 保持一致。
    #
    # --------------------------------------------------------

    distance_matrix = np.sum(

        (
            X_validation[
                :, np.newaxis, :
            ]

            -

            X_train[
                np.newaxis, :, :
            ]

        ) ** 2,

        axis=2
    )


    # --------------------------------------------------------
    # 12. 找到最近的 13 个邻居
    # --------------------------------------------------------

    nearest_indices = np.argsort(

        distance_matrix,

        axis=1

    )[:, :max(K_VALUES)]


    # --------------------------------------------------------
    # 13. 获取最近邻对应标签
    # --------------------------------------------------------

    nearest_labels = y_train[
        nearest_indices
    ]


    # --------------------------------------------------------
    # 14. 对每一个 K 进行预测
    # --------------------------------------------------------

    for k in K_VALUES:


        # ----------------------------------------------------
        # 获取前 K 个最近邻
        # ----------------------------------------------------

        current_labels = nearest_labels[
            :, :k
        ]


        # ----------------------------------------------------
        # Binary Majority Voting
        # ----------------------------------------------------
        #
        # Label:
        #
        #   0 = Normal
        #   1 = Abnormal
        #
        # 因为类别只有两个，
        # 并且 K 始终为奇数，
        # 所以不会发生平票。
        #
        # Abnormal = 1，
        # 因此直接对邻居标签求和，
        # 就可以得到 Abnormal 的票数。
        #
        # ----------------------------------------------------

        abnormal_votes = np.sum(

            current_labels,

            axis=1
        )


        # 多数票门限
        #
        # K = 1 -> 1
        # K = 3 -> 2
        # K = 5 -> 3
        # K = 7 -> 4
        # ...

        majority_threshold = (
            k // 2 + 1
        )


        # Abnormal 票数达到多数票门限
        # 则预测为 1，否则预测为 0

        predictions = (

            abnormal_votes
            >=
            majority_threshold

        ).astype(
            np.int64
        )


        # ----------------------------------------------------
        # 15. 计算 Confusion Matrix
        # ----------------------------------------------------
        #
        #                   Predicted
        #
        #                Normal  Abnormal
        #
        # Actual Normal     TN      FP
        #
        # Actual Abnormal   FN      TP
        #
        # ----------------------------------------------------


        # True Negative
        #
        # 实际为 Normal
        # 预测也为 Normal

        TN = np.sum(

            (y_validation == 0)

            &

            (predictions == 0)
        )


        # False Positive
        #
        # 实际为 Normal
        # 预测为 Abnormal

        FP = np.sum(

            (y_validation == 0)

            &

            (predictions == 1)
        )


        # False Negative
        #
        # 实际为 Abnormal
        # 预测为 Normal

        FN = np.sum(

            (y_validation == 1)

            &

            (predictions == 0)
        )


        # True Positive
        #
        # 实际为 Abnormal
        # 预测也为 Abnormal

        TP = np.sum(

            (y_validation == 1)

            &

            (predictions == 1)
        )


        # ----------------------------------------------------
        # 16. 计算 Recall
        # ----------------------------------------------------
        #
        # Recall_Normal:
        #
        #           TN
        # ----------------------
        #        TN + FP
        #
        #
        # Recall_Abnormal:
        #
        #           TP
        # ----------------------
        #        TP + FN
        #
        # ----------------------------------------------------


        recall_normal = (

            TN
            /
            (TN + FP)

            if (TN + FP) > 0

            else 0.0
        )


        recall_abnormal = (

            TP
            /
            (TP + FN)

            if (TP + FN) > 0

            else 0.0
        )


        # ----------------------------------------------------
        # 17. 计算 Accuracy
        # ----------------------------------------------------
        #
        # Accuracy =
        #
        #      TN + TP
        # -------------------
        #   Total Samples
        #
        # ----------------------------------------------------

        correct_predictions = (
            TN + TP
        )


        total_predictions = len(
            y_validation
        )


        accuracy = (

            correct_predictions

            /

            total_predictions
        )


        # ----------------------------------------------------
        # 18. 保存当前 K 和 Fold 的全部结果
        # ----------------------------------------------------

        results.append({

            "K":
                k,

            "Validation_Fold":
                validation_fold,

            "Training_Folds":
                "+".join(
                    map(
                        str,
                        training_folds
                    )
                ),

            "Training_Samples":
                len(
                    X_train
                ),

            "Validation_Samples":
                len(
                    X_validation
                ),

            "TN":
                int(TN),

            "FP":
                int(FP),

            "FN":
                int(FN),

            "TP":
                int(TP),

            "Recall_Normal":
                recall_normal,

            "Recall_Normal_Percent":
                recall_normal * 100,

            "Recall_Abnormal":
                recall_abnormal,

            "Recall_Abnormal_Percent":
                recall_abnormal * 100,

            "Correct_Predictions":
                int(
                    correct_predictions
                ),

            "Total_Predictions":
                int(
                    total_predictions
                ),

            "Accuracy":
                accuracy,

            "Accuracy_Percent":
                accuracy * 100
        })


# ------------------------------------------------------------
# 19. 将所有结果转换为 DataFrame
# ------------------------------------------------------------

results_df = pd.DataFrame(
    results
)


# ------------------------------------------------------------
# 20. 保存全部 35 次原始结果
# ------------------------------------------------------------
#
# 7 个 K × 5 个 Fold = 35 条结果
#
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
# 21. 创建 K × Fold Accuracy 表
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


accuracy_table.columns = [

    "K",

    "Fold1_Accuracy",

    "Fold2_Accuracy",

    "Fold3_Accuracy",

    "Fold4_Accuracy",

    "Fold5_Accuracy"
]


# ------------------------------------------------------------
# 22. 计算每个 K 的平均 Accuracy
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
] = (

    accuracy_table[
        accuracy_columns
    ]

    .mean(axis=1)
)


# ------------------------------------------------------------
# 23. 计算最小、最大 Accuracy 和标准差
# ------------------------------------------------------------

accuracy_table[
    "Minimum_Accuracy"
] = (

    accuracy_table[
        accuracy_columns
    ]

    .min(axis=1)
)


accuracy_table[
    "Maximum_Accuracy"
] = (

    accuracy_table[
        accuracy_columns
    ]

    .max(axis=1)
)


accuracy_table[
    "Std_Accuracy"
] = (

    accuracy_table[
        accuracy_columns
    ]

    .std(axis=1)
)


# ------------------------------------------------------------
# 24. 找到最佳 K
# ------------------------------------------------------------

best_index = (

    accuracy_table[
        "Average_Accuracy"
    ]

    .idxmax()
)


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
# 25. 保存 K 值比较结果
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
# 26. 获取最佳 K 对应的 5-Fold 结果
# ------------------------------------------------------------

best_k_results = results_df[

    results_df[
        "K"
    ]

    ==

    best_k
]


# ------------------------------------------------------------
# 27. 累加最佳 K 的 5 个 Fold Confusion Matrix
# ------------------------------------------------------------

total_TN = int(

    best_k_results[
        "TN"
    ].sum()
)


total_FP = int(

    best_k_results[
        "FP"
    ].sum()
)


total_FN = int(

    best_k_results[
        "FN"
    ].sum()
)


total_TP = int(

    best_k_results[
        "TP"
    ].sum()
)


# ------------------------------------------------------------
# 28. 计算最佳 K 的整体 Recall
# ------------------------------------------------------------
#
# 注意：
#
# 这里不是直接对 5 个 Fold 的 Recall 求平均。
#
# 而是先把 5 个 Fold 的 TN/FP/FN/TP 累加，
# 再重新计算整体 Recall。
#
# 这样得到的是全部 1000 个样本上的整体结果。
#
# ------------------------------------------------------------


best_recall_normal = (

    total_TN

    /

    (total_TN + total_FP)

    if (
        total_TN + total_FP
    ) > 0

    else 0.0
)


best_recall_abnormal = (

    total_TP

    /

    (total_TP + total_FN)

    if (
        total_TP + total_FN
    ) > 0

    else 0.0
)


# ------------------------------------------------------------
# 29. 计算最佳 K 的整体 Accuracy
# ------------------------------------------------------------

total_correct = (
    total_TN
    +
    total_TP
)


total_samples = (
    total_TN
    +
    total_FP
    +
    total_FN
    +
    total_TP
)


overall_accuracy = (

    total_correct

    /

    total_samples
)


# ------------------------------------------------------------
# 30. 保存最佳 K
# ------------------------------------------------------------

best_k_df = pd.DataFrame({

    "Best_K":
        [best_k],

    "Best_Average_Accuracy_Percent":
        [best_accuracy],

    "Overall_Accuracy_Percent":
        [
            overall_accuracy * 100
        ],

    "TN":
        [total_TN],

    "FP":
        [total_FP],

    "FN":
        [total_FN],

    "TP":
        [total_TP],

    "Recall_Normal_Percent":
        [
            best_recall_normal * 100
        ],

    "Recall_Abnormal_Percent":
        [
            best_recall_abnormal * 100
        ]
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
# 31. Terminal 只输出最终概要
# ------------------------------------------------------------

print("=" * 60)

print(
    "KNNv2 Binary 5-Fold "
    "Cross Validation completed."
)

print("=" * 60)

print(
    "Classification:"
)

print(
    "Normal = 0"
)

print(
    "Low / Medium / High "
    "= Abnormal = 1"
)

print()

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

print(
    f"Best K = {best_k}"
)

print(
    f"Average Accuracy = "
    f"{best_accuracy:.4f}%"
)

print(
    f"Overall Accuracy = "
    f"{overall_accuracy * 100:.4f}%"
)

print(
    f"Recall Normal = "
    f"{best_recall_normal * 100:.4f}%"
)

print(
    f"Recall Abnormal = "
    f"{best_recall_abnormal * 100:.4f}%"
)

print("=" * 60)