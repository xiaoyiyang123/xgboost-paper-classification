import xgboost as xgb
import joblib
import numpy as np
from sklearn.multioutput import ClassifierChain
from sklearn.metrics import accuracy_score, hamming_loss, f1_score
from sklearn.neighbors import KNeighborsClassifier

# ---------------------- 1. 加载预处理后的数据 ----------------------
X_train, X_test, y_train, y_test = joblib.load("../data/processed_data.pkl")
mlb = joblib.load("../model/mlb.pkl")  # 加载标签编码器

# ---------------------- 2. 构建XGBoost多标签模型（ClassifierChain） ----------------------
# 初始化XGBoost分类器
xgb_clf = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="binary:logistic",
    random_state=42,
    eval_metric="logloss"
)
# 构建分类器链（建模标签间依赖）
chain = ClassifierChain(xgb_clf)
# 训练模型
chain.fit(X_train, y_train)
# 保存XGBoost多标签模型
joblib.dump(chain, "../model/xgb_chain_model.pkl")

# ---------------------- 3. 构建KNN对比模型 ----------------------
knn = KNeighborsClassifier(n_neighbors=5, metric="euclidean")
knn_chain = ClassifierChain(knn)
knn_chain.fit(X_train, y_train)
joblib.dump(knn_chain, "../model/knn_chain_model.pkl")


# ---------------------- 4. 模型评估（验证指标） ----------------------
def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    # 计算核心指标
    accuracy = accuracy_score(y_test, y_pred)
    hamming = hamming_loss(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    micro_f1 = f1_score(y_test, y_pred, average="micro")
    # Top-1/2/3准确率（自定义计算）
    y_pred_proba = model.predict_proba(X_test)
    top1_acc = calculate_top_k_accuracy(y_test, y_pred_proba, k=1)
    top2_acc = calculate_top_k_accuracy(y_test, y_pred_proba, k=2)
    top3_acc = calculate_top_k_accuracy(y_test, y_pred_proba, k=3)

    print("模型评估结果：")
    print(f"准确率: {accuracy:.4f} | 汉明损失: {hamming:.4f}")
    print(f"宏平均F1: {macro_f1:.4f} | 微平均F1: {micro_f1:.4f}")
    print(f"Top-1准确率: {top1_acc:.4f} | Top-2准确率: {top2_acc:.4f} | Top-3准确率: {top3_acc:.4f}")


def calculate_top_k_accuracy(y_true, y_pred_proba, k):
    """计算Top-k准确率"""
    correct = 0
    for true, proba in zip(y_true, y_pred_proba):
        # 取置信度前k的标签索引
        top_k_idx = np.argsort(proba)[-k:]
        # 检查真实标签中是否有至少一个在Top-k中
        if np.any(true[top_k_idx] == 1):
            correct += 1
    return correct / len(y_true)


# 评估两个模型
print("=" * 50)
print("XGBoost多标签模型评估：")
evaluate_model(chain, X_test, y_test)
print("=" * 50)
print("KNN多标签模型评估：")
evaluate_model(knn_chain, X_test, y_test)