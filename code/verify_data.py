"""
数据格式验证脚本：检查cnki_papers.csv的列名、标签合法性、文本完整性
运行方式：code目录下执行 python verify_data.py
"""
import pandas as pd
import os

# 12个目标细分领域（严格对应开题报告）
TARGET_LABELS = {
    "管理信息系统", "机器视觉", "计算机网络", "聚类算法",
    "农业信息化", "神经网络", "数据分析", "数据库应用",
    "智能算法", "资源优化调度", "单片机应用", "工业控制系统"
}

# 加载数据
data_path = "../data/cnki_papers.csv"
if not os.path.exists(data_path):
    print(f"❌ 未找到数据文件：{data_path}")
    print("请将cnki_papers.csv放入data文件夹")
    exit(1)

df = pd.read_csv(data_path)
print("✅ 数据文件加载成功！")
print(f"数据总量：{len(df)} 条")

# 验证列名
required_cols = ["文本内容", "标签", "文本长度"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"❌ 缺少必要列：{', '.join(missing_cols)}")
    exit(1)
print("✅ 列名验证通过！")

# 验证文本内容非空
df["文本内容"] = df["文本内容"].fillna("")
empty_text_count = len(df[df["文本内容"].str.strip() == ""])
if empty_text_count > 0:
    print(f"⚠️  存在 {empty_text_count} 条空文本数据，已自动填充为空字符串")
else:
    print("✅ 文本内容无空值！")

# 验证标签合法性（支持单标签/多标签）
def validate_labels(label_str):
    if pd.isna(label_str):
        return False, []
    labels = [label.strip() for label in str(label_str).split(",")]
    invalid_labels = [lab for lab in labels if lab not in TARGET_LABELS]
    return len(invalid_labels) == 0, labels

df["标签_有效"] = df["标签"].apply(lambda x: validate_labels(x)[0])
df["标签列表"] = df["标签"].apply(lambda x: validate_labels(x)[1])

invalid_label_count = len(df[~df["标签_有效"]])
if invalid_label_count > 0:
    invalid_samples = df[~df["标签_有效"]][["文本内容", "标签"]].head(3)
    print(f"❌ 存在 {invalid_label_count} 条无效标签数据，示例：")
    for idx, row in invalid_samples.iterrows():
        print(f"  - 标签：{row['标签']}（文本前50字：{row['文本内容'][:50]}...）")
    print(f"⚠️  有效标签仅支持：{', '.join(TARGET_LABELS)}")
else:
    print("✅ 所有标签均合法！")

# 统计各标签分布
all_labels = []
for labels in df["标签列表"]:
    all_labels.extend(labels)
label_counts = pd.Series(all_labels).value_counts()
print("\n📊 各领域标签分布：")
for label, count in label_counts.items():
    print(f"  - {label}：{count} 条")

# 验证数据规模（开题报告要求≥1200条，每领域≥100条）
total_count = len(df)
meet_total = total_count >= 1200
print(f"\n📈 数据规模验证：")
print(f"  - 总样本数：{total_count}（要求≥1200：{'✅' if meet_total else '❌'}）")

meet_per_label = all(count >= 100 for count in label_counts.values)
print(f"  - 各领域样本数≥100：{'✅' if meet_per_label else '❌'}")
if not meet_per_label:
    insufficient = [f"{label}（{count}条）" for label, count in label_counts.items() if count < 100]
    print(f"    不足100条的领域：{', '.join(insufficient)}")

print("\n" + "="*50)
if meet_total and meet_per_label and invalid_label_count == 0 and empty_text_count == 0:
    print("🎉 数据格式完全符合要求，可以开始预处理！")
else:
    print("⚠️  数据存在部分问题，请根据上述提示修正后再执行预处理。")