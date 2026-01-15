# """
# 测试集模型评估脚本：计算开题报告要求的7项核心指标
# 运行方式：code目录下执行 python evaluate_test_set.py
# 依赖：已训练好的模型（model文件夹下的.pkl文件）、test_set.csv（data文件夹下）
# """
# import pandas as pd
# import joblib
# import jieba
# import numpy as np
# from sklearn.metrics import accuracy_score, hamming_loss, f1_score
#
# # ---------------------- 1. 加载必要工具和模型（复用训练时的文件） ----------------------
# # 加载训练好的模型、特征器、标签编码器
# tfidf = joblib.load("../model/tfidf.pkl")  # TF-IDF特征器
# mlb = joblib.load("../model/mlb.pkl")  # 标签编码器
# xgb_model = joblib.load("../model/xgb_chain_model.pkl")  # XGBoost核心模型
# knn_model = joblib.load("../model/knn_chain_model.pkl")  # KNN对比模型
#
# # 加载停用词表
# with open("../data/stopwords.txt", "r", encoding="utf-8") as f:
#     stopwords = set(f.read().splitlines())
#
#
# # ---------------------- 2. 加载并预处理测试集（与训练集预处理逻辑完全一致） ----------------------
# def preprocess_text(text):
#     """复用训练时的文本预处理函数：分词+停用词过滤"""
#     if pd.isna(text):
#         return ""
#     words = jieba.lcut(text.strip())
#     filtered_words = [w for w in words if w not in stopwords and len(w) >= 2]
#     return " ".join(filtered_words)
#
#
# # 加载测试集
# test_df = pd.read_csv("../data/test_set.csv")
# print(f"测试集规模：{len(test_df)} 篇")
#
# # 预处理文本和标签
# test_df["processed_text"] = test_df["文本内容"].apply(preprocess_text)
# test_df["标签"] = test_df["标签"].apply(
#     lambda x: [label.strip() for label in str(x).split(",")] if pd.notna(x) else []
# )
#
# # 转换标签为二进制矩阵（适配模型输入）
# y_test = mlb.transform(test_df["标签"])
# # 提取测试集特征（用训练好的TF-IDF特征器，避免数据泄露）
# X_test = tfidf.transform(test_df["processed_text"])
#
# # ---------------------- 3. 模型预测 ----------------------
# # XGBoost模型预测（核心模型）
# y_pred_xgb = xgb_model.predict(X_test)
# y_pred_xgb_proba = xgb_model.predict_proba(X_test)  # 用于Top-k准确率计算
#
# # KNN模型预测（对比模型）
# y_pred_knn = knn_model.predict(X_test)
# y_pred_knn_proba = knn_model.predict_proba(X_test)
#
#
# # ---------------------- 4. 计算开题报告要求的7项指标 ----------------------
# def calculate_all_metrics(y_true, y_pred, y_pred_proba, model_name):
#     """计算7项核心指标：准确率、汉明损失、宏平均F1、微平均F1、Top-1/2/3准确率"""
#     # 1. 准确率（预测标签与真实标签完全一致）
#     accuracy = accuracy_score(y_true, y_pred)
#     # 2. 汉明损失（单样本标签错误率）
#     hamming = hamming_loss(y_true, y_pred)
#     # 3. 宏平均F1（各领域F1的算术平均）
#     macro_f1 = f1_score(y_true, y_pred, average="macro")
#     # 4. 微平均F1（全局混淆矩阵计算）
#     micro_f1 = f1_score(y_true, y_pred, average="micro")
#     # 5-7. Top-1/2/3准确率
#     top1 = calculate_top_k_accuracy(y_true, y_pred_proba, k=1)
#     top2 = calculate_top_k_accuracy(y_true, y_pred_proba, k=2)
#     top3 = calculate_top_k_accuracy(y_true, y_pred_proba, k=3)
#
#     return {
#         "模型": model_name,
#         "准确率": round(accuracy, 4),
#         "汉明损失": round(hamming, 4),
#         "宏平均F1": round(macro_f1, 4),
#         "微平均F1": round(micro_f1, 4),
#         "Top-1准确率": round(top1, 4),
#         "Top-2准确率": round(top2, 4),
#         "Top-3准确率": round(top3, 4)
#     }
#
#
# def calculate_top_k_accuracy(y_true, y_pred_proba, k):
#     """计算Top-k准确率（预测置信度前k个标签中至少1个命中真实标签）"""
#     correct = 0
#     for true, proba in zip(y_true, y_pred_proba):
#         top_k_idx = np.argsort(proba)[-k:]  # 取置信度前k的标签索引
#         if np.any(true[top_k_idx] == 1):  # 检查是否有真实标签在Top-k中
#             correct += 1
#     return correct / len(y_true)
#
#
# # ---------------------- 5. 执行评估并输出结果 ----------------------
# # 计算两个模型的指标
# xgb_metrics = calculate_all_metrics(y_test, y_pred_xgb, y_pred_xgb_proba, "XGBoost（核心模型）")
# knn_metrics = calculate_all_metrics(y_test, y_pred_knn, y_pred_knn_proba, "KNN（对比模型）")
#
# # 转换为DataFrame，方便查看
# metrics_df = pd.DataFrame([xgb_metrics, knn_metrics])
#
# # 打印结果
# print("\n" + "=" * 80)
# print("模型测试集指标评估结果")
# print("=" * 80)
# print(metrics_df.to_string(index=False))
#
# # ---------------------- 6. 分领域指标评估----------------------
# print("\n" + "=" * 80)
# print("分领域准确率评估（XGBoost）")
# print("=" * 80)
# domain_accuracy = []
# for i, domain in enumerate(mlb.classes_):
#     true_domain = y_test[:, i]
#     pred_domain = y_pred_xgb[:, i]
#     acc = accuracy_score(true_domain, pred_domain)
#     domain_accuracy.append({"领域": domain, "准确率": round(acc, 4)})
#
# domain_df = pd.DataFrame(domain_accuracy).sort_values("准确率", ascending=False)
# for idx, row in domain_df.iterrows():
#     print(f"{row['领域']:15s} → 准确率：{row['准确率']:.4f}")
#
# # ---------------------- 7. 指标达标情况判断 ----------------------
# print("\n" + "=" * 80)
# print("✅ 开题报告指标达标情况（XGBoost模型）")
# print("=" * 80)
# standards = {
#     "准确率": 0.75,
#     "汉明损失": 0.02,
#     "宏平均F1": 0.85,
#     "微平均F1": 0.85,
#     "Top-1准确率": 0.80,
#     "Top-2准确率": 0.90,
#     "Top-3准确率": 0.95
# }
#
# for metric, standard in standards.items():
#     value = xgb_metrics[metric]
#     if metric == "汉明损失":  # 汉明损失越低越好
#         status = "✅" if value <= standard else "❌"
#         print(f"{metric:12s}：{value:.4f}（标准≤{standard}）→ {status}")
#     else:  # 其他指标越高越好
#         status = "✅" if value >= standard else "❌"
#         print(f"{metric:12s}：{value:.4f}（标准≥{standard}）→ {status}")
#
# print("\n" + "=" * 80)
# print("结果已保存至 data/test_set_evaluation_result.csv")
# print("=" * 80)
# # 保存结果到CSV，方便论文使用
# metrics_df.to_csv("../data/test_set_evaluation_result.csv", index=False, encoding="utf-8-sig")
# domain_df.to_csv("../data/domain_accuracy_result.csv", index=False, encoding="utf-8-sig")


"""
测试集模型评估脚本：计算开题报告要求的7项核心指标
运行方式：code目录下执行 python evaluate_test_set.py
依赖：已训练好的模型（model文件夹下的.pkl文件）、test_set.csv（data文件夹下）
"""
import pandas as pd
import joblib
import jieba
import numpy as np
from sklearn.metrics import accuracy_score, hamming_loss, f1_score

# ---------------------- 新增：概率归一化函数 ----------------------
def normalize_proba(y_pred_proba):
    """
    对多标签预测概率做L1归一化，确保每个样本的所有标签概率和为1
    :param y_pred_proba: 形状为 (n_samples, n_labels) 的概率矩阵
    :return: 归一化后的概率矩阵
    """
    row_sums = y_pred_proba.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1  # 避免除以0
    return y_pred_proba / row_sums

# ---------------------- 1. 加载必要工具和模型（复用训练时的文件） ----------------------
# 加载训练好的模型、特征器、标签编码器
tfidf = joblib.load("../model/tfidf.pkl")  # TF-IDF特征器
mlb = joblib.load("../model/mlb.pkl")  # 标签编码器
xgb_model = joblib.load("../model/xgb_chain_model.pkl")  # XGBoost核心模型
knn_model = joblib.load("../model/knn_chain_model.pkl")  # KNN对比模型

# 加载停用词表
with open("../data/stopwords.txt", "r", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())


# ---------------------- 2. 加载并预处理测试集（与训练集预处理逻辑完全一致） ----------------------
def preprocess_text(text):
    """复用训练时的文本预处理函数：分词+停用词过滤"""
    if pd.isna(text):
        return ""
    words = jieba.lcut(text.strip())
    filtered_words = [w for w in words if w not in stopwords and len(w) >= 2]
    return " ".join(filtered_words)


# 加载测试集
test_df = pd.read_csv("../data/test_set.csv")
print(f"测试集规模：{len(test_df)} 篇")

# 预处理文本和标签
test_df["processed_text"] = test_df["文本内容"].apply(preprocess_text)
test_df["标签"] = test_df["标签"].apply(
    lambda x: [label.strip() for label in str(x).split(",")] if pd.notna(x) else []
)

# 转换标签为二进制矩阵（适配模型输入）
y_test = mlb.transform(test_df["标签"])
# 提取测试集特征（用训练好的TF-IDF特征器，避免数据泄露）
X_test = tfidf.transform(test_df["processed_text"])

# ---------------------- 3. 模型预测 ----------------------
# XGBoost模型预测（核心模型）
y_pred_xgb = xgb_model.predict(X_test)
y_pred_xgb_proba = xgb_model.predict_proba(X_test)  # 原始概率
y_pred_xgb_proba_normalized = normalize_proba(y_pred_xgb_proba)  # 归一化后概率

# KNN模型预测（对比模型）
y_pred_knn = knn_model.predict(X_test)
y_pred_knn_proba = knn_model.predict_proba(X_test)  # 原始概率
y_pred_knn_proba_normalized = normalize_proba(y_pred_knn_proba)  # 归一化后概率


# ---------------------- 4. 计算开题报告要求的7项指标 ----------------------
def calculate_all_metrics(y_true, y_pred, y_pred_proba, model_name):
    """计算7项核心指标：准确率、汉明损失、宏平均F1、微平均F1、Top-1/2/3准确率"""
    # 1. 准确率（预测标签与真实标签完全一致）
    accuracy = accuracy_score(y_true, y_pred)
    # 2. 汉明损失（单样本标签错误率）
    hamming = hamming_loss(y_true, y_pred)
    # 3. 宏平均F1（各领域F1的算术平均）
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    # 4. 微平均F1（全局混淆矩阵计算）
    micro_f1 = f1_score(y_true, y_pred, average="micro")
    # 5-7. Top-1/2/3准确率（使用归一化后的概率）
    top1 = calculate_top_k_accuracy(y_true, y_pred_proba, k=1)
    top2 = calculate_top_k_accuracy(y_true, y_pred_proba, k=2)
    top3 = calculate_top_k_accuracy(y_true, y_pred_proba, k=3)

    return {
        "模型": model_name,
        "准确率": round(accuracy, 4),
        "汉明损失": round(hamming, 4),
        "宏平均F1": round(macro_f1, 4),
        "微平均F1": round(micro_f1, 4),
        "Top-1准确率": round(top1, 4),
        "Top-2准确率": round(top2, 4),
        "Top-3准确率": round(top3, 4)
    }


def calculate_top_k_accuracy(y_true, y_pred_proba, k):
    """计算Top-k准确率（使用归一化后的概率）"""
    correct = 0
    for true, proba in zip(y_true, y_pred_proba):
        top_k_idx = np.argsort(proba)[-k:]  # 取置信度前k的标签索引
        if np.any(true[top_k_idx] == 1):  # 检查是否有真实标签在Top-k中
            correct += 1
    return correct / len(y_true)


# ---------------------- 5. 执行评估并输出结果 ----------------------
# 计算两个模型的指标（传入归一化后的概率）
xgb_metrics = calculate_all_metrics(y_test, y_pred_xgb, y_pred_xgb_proba_normalized, "XGBoost（核心模型）")
knn_metrics = calculate_all_metrics(y_test, y_pred_knn, y_pred_knn_proba_normalized, "KNN（对比模型）")

# 转换为DataFrame，方便查看
metrics_df = pd.DataFrame([xgb_metrics, knn_metrics])

# 打印结果
print("\n" + "=" * 80)
print("模型测试集指标评估结果")
print("=" * 80)
print(metrics_df.to_string(index=False))

# 验证归一化结果
print(f"\nXGBoost随机样本归一化概率和: {y_pred_xgb_proba_normalized[0].sum():.4f} (应≈1)")
print(f"KNN随机样本归一化概率和: {y_pred_knn_proba_normalized[0].sum():.4f} (应≈1)")

# ---------------------- 6. 分领域指标评估----------------------
print("\n" + "=" * 80)
print("分领域准确率评估（XGBoost）")
print("=" * 80)
domain_accuracy = []
for i, domain in enumerate(mlb.classes_):
    true_domain = y_test[:, i]
    pred_domain = y_pred_xgb[:, i]
    acc = accuracy_score(true_domain, pred_domain)
    domain_accuracy.append({"领域": domain, "准确率": round(acc, 4)})

domain_df = pd.DataFrame(domain_accuracy).sort_values("准确率", ascending=False)
for idx, row in domain_df.iterrows():
    print(f"{row['领域']:15s} → 准确率：{row['准确率']:.4f}")

# ---------------------- 7. 指标达标情况判断 ----------------------
print("\n" + "=" * 80)
print("✅ 开题报告指标达标情况（XGBoost模型）")
print("=" * 80)
standards = {
    "准确率": 0.75,
    "汉明损失": 0.02,
    "宏平均F1": 0.85,
    "微平均F1": 0.85,
    "Top-1准确率": 0.80,
    "Top-2准确率": 0.90,
    "Top-3准确率": 0.95
}

for metric, standard in standards.items():
    value = xgb_metrics[metric]
    if metric == "汉明损失":  # 汉明损失越低越好
        status = "✅" if value <= standard else "❌"
        print(f"{metric:12s}：{value:.4f}（标准≤{standard}）→ {status}")
    else:  # 其他指标越高越好
        status = "✅" if value >= standard else "❌"
        print(f"{metric:12s}：{value:.4f}（标准≥{standard}）→ {status}")

print("\n" + "=" * 80)
print("结果已保存至 data/test_set_evaluation_result.csv")
print("=" * 80)
# 保存结果到CSV，方便论文使用
metrics_df.to_csv("../data/test_set_evaluation_result.csv", index=False, encoding="utf-8-sig")
domain_df.to_csv("../data/domain_accuracy_result.csv", index=False, encoding="utf-8-sig")