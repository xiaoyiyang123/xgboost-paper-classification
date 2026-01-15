import pandas as pd
import jieba
import os
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib

# ---------------------- 1. 加载数据与停用词 ----------------------
df = pd.read_csv("../data/cnki_papers.csv")
with open("../data/stopwords.txt", "r", encoding="utf-8") as f:
    stopwords = set(f.read().splitlines())

# ---------------------- 2. 文本预处理 ----------------------
def preprocess_text(text):
    """文本预处理：分词、过滤停用词"""
    if pd.isna(text):
        return ""
    # jieba分词
    words = jieba.lcut(text.strip())
    # 过滤停用词、长度<2的词
    filtered_words = [w for w in words if w not in stopwords and len(w) >= 2]
    return " ".join(filtered_words)

# 对"文本内容"列预处理
df["processed_text"] = df["文本内容"].apply(preprocess_text)

# ---------------------- 3. 多标签编码 ----------------------
# 标签列（假设标签已用逗号分隔，如"神经网络,数据分析"）
# 适配单标签/多标签（标签列用逗号分隔）
df["标签"] = df["标签"].apply(
    lambda x: [label.strip() for label in str(x).split(",")] if pd.notna(x) else []
)
# 过滤无效标签（避免验证时遗漏的错误标签）
TARGET_LABELS = {
    "管理信息系统", "机器视觉", "计算机网络", "聚类算法",
    "农业信息化", "神经网络", "数据分析", "数据库应用",
    "智能算法", "资源优化调度", "单片机应用", "工业控制系统"
}
df["标签"] = df["标签"].apply(lambda x: [lab for lab in x if lab in TARGET_LABELS])

# 初始化多标签编码器
mlb = MultiLabelBinarizer(classes=list(TARGET_LABELS))
y = mlb.fit_transform(df["标签"])
# 保存标签编码器（后续Web部署用）
joblib.dump(mlb, "../model/mlb.pkl")

# ---------------------- 4. 特征提取（TF-IDF） ----------------------
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X = tfidf.fit_transform(df["processed_text"])
joblib.dump(tfidf, "../model/tfidf.pkl")

# ---------------------- 5. 划分训练集/测试集（8:2） ----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

# ---------------------- 6. 保存处理后的数据（供训练用） ----------------------
joblib.dump((X_train, X_test, y_train, y_test), "../data/processed_data.pkl")
print("数据预处理完成！已生成：标签编码器、TF-IDF特征器、训练/测试集")