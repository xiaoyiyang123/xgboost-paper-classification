let pdfResults = [];  // 存储PDF分类结果，用于导出

// 切换标签页
function openTab(tabId) {
    const tabs = document.getElementsByClassName("tab-content");
    const btns = document.getElementsByClassName("tab-btn");
    // 隐藏所有标签页，取消所有按钮激活状态
    for (let tab of tabs) tab.classList.remove("active");
    for (let btn of btns) btn.classList.remove("active");
    // 显示当前标签页，激活当前按钮
    document.getElementById(tabId).classList.add("active");
    event.currentTarget.classList.add("active");
}

// 文本分类
async function classifyText() {
    const text = document.getElementById("text-input").value.trim();
    const resultDiv = document.getElementById("text-result");
    if (!text) {
        resultDiv.innerHTML = "<p>请输入论文文本内容！</p>";
        return;
    }
    resultDiv.innerHTML = "<p>分类中...</p>";
    try {
        const response = await fetch("/classify/text", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text: text})
        });
        const data = await response.json();
        if (data.labels.length === 0) {
            resultDiv.innerHTML = "<p>未识别到相关细分领域标签</p>";
            return;
        }
        // 渲染标签和置信度
        let html = "<p>分类结果（按置信度排序）：</p>";
        data.labels.forEach((label, idx) => {
            html += `<span class="label-item">${label}（置信度：${data.confidences[idx]}）</span>`;
        });
        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = "<p>分类失败，请重试！</p>";
        console.error(error);
    }
}

// PDF批量分类
async function classifyPdf() {
    const files = document.getElementById("pdf-input").files;
    const resultDiv = document.getElementById("pdf-result");
    const exportBtn = document.getElementById("export-btn");
    if (files.length === 0) {
        resultDiv.innerHTML = "<p>请选择PDF文件！</p>";
        return;
    }
    resultDiv.innerHTML = "<p>正在提取文本并分类...</p>";
    // 构建FormData
    const formData = new FormData();
    for (let file of files) formData.append("pdf_files", file);
    try {
        const response = await fetch("/classify/pdf", {
            method: "POST",
            body: formData
        });
        const data = await response.json();
        pdfResults = data.results;  // 保存结果用于导出
        // 渲染结果
        let html = "<p>批量分类结果：</p>";
        data.results.forEach(item => {
            html += `<div class="file-result">
                <p><strong>文件：${item.filename}</strong></p>
                <div>`;
            if (item.labels.length === 0) {
                html += "<p>未识别到相关标签</p>";
            } else {
                item.labels.forEach((label, idx) => {
                    html += `<span class="label-item">${label}（${item.confidences[idx]}）</span>`;
                });
            }
            html += "</div></div>";
        });
        resultDiv.innerHTML = html;
        exportBtn.style.display = "inline-block";  // 显示导出按钮
    } catch (error) {
        resultDiv.innerHTML = "<p>分类失败，请重试！</p>";
        console.error(error);
    }
}

// 导出结果为Excel
async function exportResults() {
    if (pdfResults.length === 0) {
        alert("暂无结果可导出！");
        return;
    }
    try {
        const response = await fetch("/export/results", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({results: pdfResults})
        });
        // 下载Excel文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "论文分类结果.xlsx";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert("导出失败，请重试！");
        console.error(error);
    }
}