from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import joblib
import jieba
import pdfplumber
import numpy as np
import os
from io import BytesIO, StringIO
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback

app = Flask(__name__, static_folder="../static", template_folder="../templates")
# 配置项（关键）
app.config['SECRET_KEY'] = '10f7608a9df95cdc683cfc7e371dcaa50dd85467813db531'

# ========== 修正数据库路径（核心修改） ==========
# 1. 获取app.py所在目录（code目录）的绝对路径
code_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 拼接根目录的data路径（code/../data → 根目录data）
root_data_dir = os.path.join(code_dir, "../data")
# 3. 确保data目录存在（不存在则自动创建）
os.makedirs(root_data_dir, exist_ok=True)
# 4. 配置SQLite绝对路径（避免相对路径解析错误）
db_path = os.path.join(root_data_dir, "user_history.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# ========== 修正结束 ==========

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False






# 初始化扩展
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 未登录时跳转的登录页面


# ---------------------- 数据库模型（用户表+历史记录表） ----------------------
class User(UserMixin, db.Model):
    """用户表：存储用户名、加密密码、创建时间"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # 唯一用户名
    password_hash = db.Column(db.String(256), nullable=False)  # 加密密码
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

    # 密码加密存储
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    # 密码验证
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ClassificationHistory(db.Model):
    """分类历史表：关联用户，存储分类记录"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户ID
    operation_type = db.Column(db.String(20), nullable=False)  # 操作类型
    content = db.Column(db.Text, nullable=False)  # 分类内容）
    labels = db.Column(db.String(500), nullable=False)  # 分类标签（增加到500字符）
    confidences = db.Column(db.String(500), nullable=False)  # 置信度（增加到500字符）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 分类时间

    # 关联用户表（反向查询：user.historys）
    user = db.relationship('User', backref=db.backref('historys', lazy=True))


# ---------------------- 初始化数据库 ----------------------
with app.app_context():
    db.create_all()  # 创建数据表


# ---------------------- Flask-Login回调（加载用户） ----------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------- 核心工具加载 ----------------------
try:
    mlb = joblib.load("../model/mlb.pkl")
    tfidf = joblib.load("../model/tfidf.pkl")
    xgb_model = joblib.load("../model/xgb_chain_model.pkl")
    stopwords = set(open("../data/stopwords.txt", "r", encoding="utf-8").read().splitlines())
    print(f"模型加载成功！标签数量: {len(mlb.classes_)}")
    print(f"标签列表: {mlb.classes_}")
except Exception as e:
    print(f"模型加载失败: {e}")
    traceback.print_exc()


    # 创建虚拟模型用于测试
    class DummyModel:
        def predict(self, X):
            # 返回多个标签（模拟多标签分类）
            return np.array([[1, 0, 1, 0, 1, 0]])  # 返回多标签示例

        def predict_proba(self, X):
            # 返回多个概率
            return np.array([[0.9, 0.1, 0.8, 0.2, 0.7, 0.3]])  # 返回概率


    class DummyMLB:
        classes_ = ['计算机网络', '数据库应用', '人工智能', '机器学习', '聚类算法', '其他']


    mlb = DummyMLB()
    tfidf = None
    xgb_model = DummyModel()
    stopwords = set()


# ---------------------- 工具函数----------------------
def preprocess_text(text):
    if not text or not isinstance(text, str):
        return ""
    words = jieba.lcut(text.strip())
    filtered_words = [w for w in words if w not in stopwords and len(w) >= 2]
    return " ".join(filtered_words)


def extract_pdf_text(pdf_file):
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages[:3]:  # 只读取前3页
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF提取错误: {e}")
    return text.strip()


def predict_labels(text):
    """预测文本的多标签分类"""
    try:
        if not text or not isinstance(text, str) or len(text.strip()) < 10:
            print("文本太短，无法分类")
            return [], []

        processed_text = preprocess_text(text)
        if not processed_text:
            print("预处理后文本为空")
            return [], []

        print(f"预处理文本: {processed_text[:100]}...")

        # 使用TF-IDF转换
        X = tfidf.transform([processed_text])

        # 预测多标签 - ClassifierChain返回的是多个标签的预测
        y_pred = xgb_model.predict(X)[0]  # 二进制预测结果
        y_pred_proba = xgb_model.predict_proba(X)[0]  # 概率

        print(f"原始预测结果: {y_pred}")
        print(f"预测概率: {y_pred_proba}")

        # 确保是二进制数组
        if not hasattr(y_pred, '__len__'):
            y_pred = [y_pred]
        if not hasattr(y_pred_proba, '__len__'):
            y_pred_proba = [y_pred_proba]

        labels = []
        confidences = []

        # 方法1: 使用阈值选择标签（推荐用于多标签分类）
        threshold = 0.3  # 置信度阈值
        for i, prob in enumerate(y_pred_proba):
            if i < len(mlb.classes_) and prob >= threshold:
                labels.append(mlb.classes_[i])
                confidences.append(float(prob))

        # 方法2: 如果通过阈值选择的标签太少，则选择概率最高的前N个
        if len(labels) < 2 and len(y_pred_proba) > 0:
            print("通过阈值选择的标签太少，使用Top-N方法")
            top_n = min(3, len(mlb.classes_))
            top_indices = np.argsort(y_pred_proba)[-top_n:][::-1]  # 降序排列

            for idx in top_indices:
                if idx < len(mlb.classes_):
                    label = mlb.classes_[idx]
                    confidence = float(y_pred_proba[idx])
                    if label not in labels:  # 避免重复
                        labels.append(label)
                        confidences.append(confidence)

        # 对结果进行排序（按置信度降序）
        if labels and confidences and len(labels) == len(confidences):
            sorted_pairs = sorted(zip(labels, confidences), key=lambda x: x[1], reverse=True)
            labels, confidences = zip(*sorted_pairs)
            labels = list(labels)
            confidences = list(confidences)

        # 限制最多5个标签
        labels = labels[:5]
        confidences = confidences[:5]

        # 确保置信度是浮点数
        confidences = [round(float(c), 3) for c in confidences]

        print(f"最终标签: {labels}")
        print(f"最终置信度: {confidences}")

        return labels, confidences

    except Exception as e:
        print(f"预测错误: {e}")
        traceback.print_exc()
        return [], []


# ---------------------- 用户认证路由（注册/登录/登出） ----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 验证逻辑
        if not username or not password:
            flash('用户名和密码不能为空！', 'error')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('两次密码不一致！', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('用户名已存在！', 'error')
            return redirect(url_for('register'))

        # 创建新用户
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # 注册成功后跳转登录页
        flash('注册成功！请登录', 'success')
        return redirect(url_for('login'))

    # GET请求：返回注册页面
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # 验证逻辑
        if not user or not user.check_password(password):
            flash('用户名或密码错误！', 'error')
            return redirect(url_for('login'))

        # 登录用户（记住登录状态）
        login_user(user, remember=True)
        flash('登录成功！', 'success')
        return redirect(url_for('index'))

    # GET请求：返回登录页面
    return render_template('login.html')


@app.route('/logout')
@login_required  # 必须登录才能访问
def logout():
    """用户登出"""
    logout_user()
    flash('已成功登出', 'info')
    return redirect(url_for('index'))


# ---------------------- 原有分类路由（修改：新增历史记录保存） ----------------------
@app.route("/")
def index():
    """首页：登录后显示用户名和历史记录入口"""
    return render_template("index.html")


@app.route("/classify/text", methods=["POST"])
@login_required  # 必须登录才能分类
def classify_text():
    """文本分类：新增历史记录保存"""
    try:
        data = request.json
        text = data.get("text", "")

        if not text or len(text.strip()) < 10:
            return jsonify({"error": "文本内容太短，请至少输入10个字符"}), 400

        labels, confidences = predict_labels(text)

        # 保存历史记录（关联当前登录用户）
        history = ClassificationHistory(
            user_id=current_user.id,
            operation_type='text',
            content=text[:100] + "..." if len(text) > 100 else text,
            labels=','.join(labels) if labels else '',
            confidences=','.join(str(c) for c in confidences) if confidences else ''
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({
            "success": True,
            "labels": labels,
            "confidences": confidences
        })

    except Exception as e:
        print(f"文本分类错误: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/classify/pdf", methods=["POST"])
@login_required
def classify_pdf():
    """PDF分类：新增历史记录保存"""
    try:
        if "pdf_files" not in request.files:
            return jsonify({"error": "未上传PDF文件"}), 400

        files = request.files.getlist("pdf_files")
        if not files or files[0].filename == '':
            return jsonify({"error": "未选择文件"}), 400

        results = []

        for file in files:
            if file.filename.endswith(".pdf"):
                try:
                    print(f"处理文件: {file.filename}")
                    pdf_text = extract_pdf_text(file)
                    print(f"提取文本长度: {len(pdf_text)}")

                    labels, confidences = predict_labels(pdf_text)

                    # 保存单条PDF分类记录
                    history = ClassificationHistory(
                        user_id=current_user.id,
                        operation_type='pdf',
                        content=file.filename,
                        labels=','.join(labels) if labels else '',
                        confidences=','.join(str(c) for c in confidences) if confidences else ''
                    )
                    db.session.add(history)

                    results.append({
                        "filename": file.filename,
                        "labels": labels,
                        "confidences": confidences
                    })

                    print(f"文件 {file.filename} 分类结果: {labels}")

                except Exception as e:
                    print(f"处理文件 {file.filename} 时出错: {e}")
                    traceback.print_exc()
                    results.append({
                        "filename": file.filename,
                        "error": str(e),
                        "labels": [],
                        "confidences": []
                    })

        db.session.commit()  # 批量提交记录

        return jsonify({
            "success": True,
            "results": results
        })

    except Exception as e:
        print(f"PDF分类错误: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ---------------------- 新增：历史记录查询路由 ----------------------
@app.route("/history")
@login_required
def history():
    """历史记录页面：查询当前用户的分类记录"""
    try:
        # 按时间倒序查询（最新的在前）
        history_records = ClassificationHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(ClassificationHistory.created_at.desc()).all()

        formatted_historys = []

        for record in history_records:
            try:
                # 处理标签和置信度
                labels_str = record.labels or ""
                confidences_str = record.confidences or ""

                # 分割标签和置信度
                labels_list = []
                confidences_list = []

                if labels_str and labels_str.strip():
                    labels_list = [label.strip() for label in labels_str.split(',') if label.strip()]

                if confidences_str and confidences_str.strip():
                    conf_parts = [c.strip() for c in confidences_str.split(',') if c.strip()]
                    for conf in conf_parts:
                        try:
                            # 处理可能的空字符串
                            if conf:
                                confidences_list.append(float(conf))
                        except ValueError:
                            confidences_list.append(0.0)

                # 如果长度不匹配，调整到较小的长度
                if labels_list and confidences_list:
                    min_len = min(len(labels_list), len(confidences_list))
                    if min_len > 0:
                        labels_list = labels_list[:min_len]
                        confidences_list = confidences_list[:min_len]

                formatted_historys.append({
                    "id": record.id,
                    "operation_type": record.operation_type,
                    "content": record.content,
                    "labels": labels_list,
                    "confidences": confidences_list,
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            except Exception as e:
                print(f"处理记录ID {record.id} 时出错: {e}")
                # 返回一个空的历史记录
                formatted_historys.append({
                    "id": record.id,
                    "operation_type": record.operation_type,
                    "content": record.content,
                    "labels": [],
                    "confidences": [],
                    "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

        return render_template("history.html", historys=formatted_historys)

    except Exception as e:
        print(f"查询历史记录错误: {e}")
        traceback.print_exc()
        flash(f"加载历史记录时出错: {str(e)}", "error")
        return render_template("history.html", historys=[])


# ---------------------- 新增：历史记录删除路由 ----------------------
@app.route("/history/delete/<int:history_id>", methods=["POST"])
@login_required
def delete_history(history_id):
    """删除指定历史记录（仅能删除自己的）"""
    try:
        history = ClassificationHistory.query.filter_by(
            id=history_id, user_id=current_user.id
        ).first()

        if not history:
            return jsonify({"success": False, "error": "记录不存在"}), 404

        db.session.delete(history)
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        print(f"删除历史记录错误: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------- 导出路由 ----------------------
@app.route("/export/results", methods=["POST"])
@login_required
def export_results():
    try:
        data = request.json
        results = data.get("results", [])

        # 创建DataFrame
        data_list = []
        for result in results:
            # 跳过错误结果
            if result.get("error"):
                continue

            labels = result.get("labels", [])
            confidences = result.get("confidences", [])

            # 创建标签-置信度对
            label_conf_pairs = []
            for i, label in enumerate(labels):
                if i < len(confidences):
                    conf = confidences[i]
                    label_conf_pairs.append(f"{label} ({conf * 100:.1f}%)")
                else:
                    label_conf_pairs.append(label)

            data_list.append({
                "文件名": result.get("filename", ""),
                "分类标签": ", ".join(labels),
                "标签详情": "; ".join(label_conf_pairs)
            })

        if not data_list:
            return jsonify({"error": "没有有效的结果可以导出"}), 400

        df = pd.DataFrame(data_list)
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

    except Exception as e:
        print(f"导出结果错误: {e}")
        return jsonify({"error": str(e)}), 500


# ---------------------- 测试路由 ----------------------
@app.route("/test/predict", methods=["GET"])
def test_predict():
    """测试预测功能"""
    test_text = "深度学习在自然语言处理中的应用，使用神经网络模型进行文本分类和情感分析"
    labels, confidences = predict_labels(test_text)

    return jsonify({
        "test_text": test_text,
        "labels": labels,
        "confidences": confidences,
        "is_multi_label": len(labels) > 1
    })


if __name__ == "__main__":
    with app.app_context():
        try:
            # 确保数据库表存在
            db.create_all()
            print("数据库初始化完成")

            # 检查是否有用户
            if User.query.count() == 0:
                print("创建测试用户...")
                test_user = User(username="test")
                test_user.set_password("test123")
                db.session.add(test_user)
                db.session.commit()
                print("测试用户创建成功: test/test123")

            # 检查模型
            print(f"模型信息:")
            print(f"  - 标签数量: {len(mlb.classes_)}")
            print(f"  - 标签示例: {mlb.classes_[:5]}...")

        except Exception as e:
            print(f"数据库初始化错误: {e}")
            traceback.print_exc()

    app.run(debug=True, host="0.0.0.0", port=5000)