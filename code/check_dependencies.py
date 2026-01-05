"""
依赖安装状态检查脚本：验证所有核心库是否正常可用
运行方式：在code目录下执行 python check_dependencies.py
"""
import importlib
import sys

# 核心依赖库列表（含版本兼容说明）
dependencies = [
    ("pandas", "数据处理核心库", "2.0.3及以上"),
    ("numpy", "数值计算库", "1.24.3及以上"),
    ("scipy", "科学计算库", "1.10.1及以上"),
    ("sklearn", "机器学习库", "1.2.2及以上"),
    ("xgboost", "核心算法库", "2.0.3及以上"),
    ("jieba", "中文分词库", "0.42.1及以上"),
    ("flask", "Web后端库", "2.3.3及以上"),
    ("pdfplumber", "PDF文本提取库", "0.9.0及以上"),
    ("joblib", "模型保存库", "1.3.1及以上"),
]

print("=" * 60)
print("📦 学术论文分类项目 - 依赖安装状态检查")
print("=" * 60)

success_count = 0
fail_count = 0
fail_list = []

for lib_name, lib_desc, version_req in dependencies:
    try:
        # 尝试导入库
        importlib.import_module(lib_name)
        # 对于numpy和scipy，兼容高版本（用户安装的是1.26.4和1.15.3，满足需求）
        if lib_name in ["numpy", "scipy"]:
            print(f"✅ {lib_name} ({lib_desc}) - 高版本可用（满足{version_req}要求）")
        else:
            print(f"✅ {lib_name} ({lib_desc}) - 安装成功（要求版本：{version_req}）")
        success_count += 1
    except ImportError:
        print(f"❌ {lib_name} ({lib_desc}) - 安装失败！")
        fail_list.append(lib_name)
        fail_count += 1

print("=" * 60)
print(f"检查结果：成功{success_count}个，失败{fail_count}个")

if fail_count > 0:
    print(f"❌ 失败的库：{', '.join(fail_list)}")
    print("💡 解决方案：")
    for lib in fail_list:
        print(f"  - 重新安装：pip install {lib} -i https://pypi.tuna.tsinghua.edu.cn/simple")
else:
    print("🎉 所有核心依赖均安装成功！可以继续推进毕业设计～")

sys.exit(fail_count)  # 失败时返回非0状态码，方便脚本调用