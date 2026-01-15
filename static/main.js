// 全局变量：存储PDF分类结果，用于导出
let pdfClassificationResults = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 文本分类按钮点击事件
    const classifyTextBtn = document.getElementById('classify-text-btn');
    if (classifyTextBtn) {
        classifyTextBtn.addEventListener('click', classifyText);
    }

    // PDF批量分类按钮点击事件
    const classifyPdfBtn = document.getElementById('classify-pdf-btn');
    if (classifyPdfBtn) {
        classifyPdfBtn.addEventListener('click', classifyPdf);
    }

    // 导出结果按钮点击事件
    const exportResultBtn = document.getElementById('export-result-btn');
    if (exportResultBtn) {
        exportResultBtn.addEventListener('click', exportResults);
    }
});

/**
 * 文本分类请求
 */
async function classifyText() {
    const textInput = document.getElementById('text-input');
    const textResult = document.getElementById('text-result');
    const text = textInput.value.trim();

    if (!text) {
        alert('请输入分类文本内容！');
        return;
    }

    try {
        // 禁用按钮防止重复提交
        const btn = document.getElementById('classify-text-btn');
        btn.disabled = true;
        btn.textContent = '分类中...';

        // 发送请求
        const res = await fetch('/classify/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });

        const data = await res.json();
        btn.disabled = false;
        btn.textContent = '开始分类';

        // 渲染结果
        renderTextResult(textResult, data.labels, data.confidences);
    } catch (err) {
        alert('分类失败：网络错误');
        const btn = document.getElementById('classify-text-btn');
        btn.disabled = false;
        btn.textContent = '开始分类';
    }
}

/**
 * PDF批量分类请求
 */
async function classifyPdf() {
    const pdfFilesInput = document.getElementById('pdf-files');
    const pdfResult = document.getElementById('pdf-result');
    const exportBtn = document.getElementById('export-result-btn');
    const files = pdfFilesInput.files;

    if (files.length === 0) {
        alert('请选择至少一个PDF文件！');
        return;
    }

    // 构建FormData
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('pdf_files', files[i]);
    }

    try {
        // 禁用按钮
        const btn = document.getElementById('classify-pdf-btn');
        btn.disabled = true;
        btn.textContent = '分类中...';

        // 发送请求
        const res = await fetch('/classify/pdf', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        btn.disabled = false;
        btn.textContent = '批量分类';

        // 存储结果用于导出
        pdfClassificationResults = data.results || [];
        // 渲染结果
        renderPdfResult(pdfResult, pdfClassificationResults);
        // 显示导出按钮
        exportBtn.style.display = 'inline-block';
    } catch (err) {
        alert('分类失败：网络错误');
        const btn = document.getElementById('classify-pdf-btn');
        btn.disabled = false;
        btn.textContent = '批量分类';
    }
}

/**
 * 渲染文本分类结果（多标签）
 */
function renderTextResult(container, labels, confidences) {
    container.innerHTML = '';

    if (labels.length === 0) {
        container.innerHTML = '<div class="empty-tip">未识别到有效标签</div>';
        return;
    }

    const resultDiv = document.createElement('div');
    resultDiv.innerHTML = '<strong>分类结果：</strong>';

    labels.forEach((label, index) => {
        const confidence = confidences[index];
        const tagSpan = document.createElement('span');
        tagSpan.className = 'tag';
        tagSpan.innerHTML = `${label} <span>(${confidence})</span>`;
        resultDiv.appendChild(tagSpan);
    });

    container.appendChild(resultDiv);
}

/**
 * 渲染PDF批量分类结果（多标签）
 */
function renderPdfResult(container, results) {
    container.innerHTML = '';

    if (results.length === 0) {
        container.innerHTML = '<div class="empty-tip">暂无分类结果</div>';
        return;
    }

    const resultList = document.createElement('div');
    results.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'history-item'; // 复用历史记录样式

        // 文件名
        const filenameDiv = document.createElement('div');
        filenameDiv.className = 'history-content';
        filenameDiv.innerHTML = `<strong>文件：</strong>${item.filename}`;
        itemDiv.appendChild(filenameDiv);

        // 多标签
        const labelsDiv = document.createElement('div');
        labelsDiv.className = 'history-labels';
        labelsDiv.innerHTML = '<strong>标签：</strong>';

        if (item.labels.length === 0) {
            labelsDiv.innerHTML += '<span class="tag" style="background:#999;">未识别到有效标签</span>';
        } else {
            item.labels.forEach((label, index) => {
                const confidence = item.confidences[index];
                const tagSpan = document.createElement('span');
                tagSpan.className = 'tag';
                tagSpan.innerHTML = `${label} <span>(${confidence})</span>`;
                labelsDiv.appendChild(tagSpan);
            });
        }

        itemDiv.appendChild(labelsDiv);
        resultList.appendChild(itemDiv);
    });

    container.appendChild(resultList);
}

/**
 * 导出分类结果为Excel
 */
async function exportResults() {
    if (pdfClassificationResults.length === 0) {
        alert('暂无可导出的分类结果');
        return;
    }

    try {
        const res = await fetch('/export/results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ results: pdfClassificationResults })
        });

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '论文分类结果.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (err) {
        alert('导出失败：网络错误');
    }
}