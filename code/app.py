from flask import Flask, render_template, request, jsonify, send_file
import joblib
import jieba
import pdfplumber
import numpy as np
import os
from io import BytesIO, StringIO
import pandas as pd

app = Flask(__name__, static_folder="../static", template_folder="../templates")

# ---------------------- 加载训练好的模型/工具 ----------------------
mlb = joblib.load("../model/mlb.pkl")  # 标签编码器
tfidf = joblib.load("../model/tfidf.pkl")  # TF-IDF特征器
xgb_model = joblib.load("../model/xgb_chain_model.pkl")  # XGBoost模型
stopwords = set(open("../data/stopwords.txt", "r", encoding="utf-8").read().splitlines())


# ---------------------- 文本预处理函数（与训练时一致） ----------------------
def preprocess_text(text):
    words = jieba.lcut(text.strip())
    filtered_words = [w for w in words if w not in stopwords and len(w) >= 2]
    return " ".join(filtered_words)


# ---------------------- PDF文本提取函数 ----------------------
def extract_pdf_text(pdf_file):
    """提取PDF前3页核心内容（标题、摘要、引言）"""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        # 仅提取前3页
        for page in pdf.pages[:3]:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# ---------------------- 分类预测函数 ----------------------
def predict_labels(text):
    """预测文本对应的细分领域标签及置信度"""
    # 预处理
    processed_text = preprocess_text(text)
    if not processed_text:
        return [], []
    # 特征提取
    X = tfidf.transform([processed_text])
    # 预测标签（二进制矩阵）和置信度
    y_pred = xgb_model.predict(X)[0]
    y_pred_proba = xgb_model.predict_proba(X)[0]
    # 筛选置信度>0.3的标签（可调整阈值）
    labels = mlb.classes_[y_pred == 1]
    confidences = y_pred_proba[y_pred == 1]
    # 按置信度降序排序
    sorted_idx = np.argsort(confidences)[::-1]
    return labels[sorted_idx].tolist(), confidences[sorted_idx].round(3).tolist()


# ---------------------- Web路由 ----------------------
@app.route("/")
def index():
    """首页：提供文本输入和PDF上传入口"""
    return render_template("index.html")


@app.route("/classify/text", methods=["POST"])
def classify_text():
    """文本分类接口"""
    data = request.json
    text = data.get("text", "")
    labels, confidences = predict_labels(text)
    return jsonify({"labels": labels, "confidences": confidences})


@app.route("/classify/pdf", methods=["POST"])
def classify_pdf():
    """PDF批量分类接口"""
    if "pdf_files" not in request.files:
        return jsonify({"error": "未上传PDF文件"}), 400

    files = request.files.getlist("pdf_files")
    results = []
    for file in files:
        if file.filename.endswith(".pdf"):
            # 提取PDF文本
            pdf_text = extract_pdf_text(file)
            # 预测标签
            labels, confidences = predict_labels(pdf_text)
            results.append({
                "filename": file.filename,
                "labels": labels,
                "confidences": confidences
            })
    return jsonify({"results": results})


@app.route("/export/results", methods=["POST"])
def export_results():
    """导出分类结果为Excel"""
    data = request.json
    results = data.get("results", [])
    # 转换为DataFrame
    df = pd.DataFrame(results)
    # 保存为Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="分类结果", index=False)
    output.seek(0)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="论文分类结果.xlsx"
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)