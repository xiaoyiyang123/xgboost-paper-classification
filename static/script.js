//// 全局变量
//let selectedFiles = [];
//let isProcessing = false;
//
//// DOM 加载完成后初始化
//document.addEventListener('DOMContentLoaded', function() {
//    initTooltips();
//    initFileUpload();
//    initClassifyButtons();
//    updateUserInfo();
//    checkFlashMessages();
//});
//
//// 初始化工具提示
//function initTooltips() {
//    const tooltips = document.querySelectorAll('[data-tooltip]');
//    tooltips.forEach(element => {
//        element.addEventListener('mouseenter', showTooltip);
//        element.addEventListener('mouseleave', hideTooltip);
//    });
//}
//
//function showTooltip(event) {
//    const tooltipText = event.target.getAttribute('data-tooltip');
//    const tooltip = document.createElement('div');
//    tooltip.className = 'tooltip';
//    tooltip.textContent = tooltipText;
//    tooltip.style.position = 'absolute';
//    tooltip.style.background = '#333';
//    tooltip.style.color = '#fff';
//    tooltip.style.padding = '5px 10px';
//    tooltip.style.borderRadius = '4px';
//    tooltip.style.fontSize = '12px';
//    tooltip.style.zIndex = '1000';
//    tooltip.style.whiteSpace = 'nowrap';
//
//    const rect = event.target.getBoundingClientRect();
//    tooltip.style.top = (rect.top - 35) + 'px';
//    tooltip.style.left = (rect.left + rect.width / 2) + 'px';
//    tooltip.style.transform = 'translateX(-50%)';
//
//    event.target.tooltipElement = tooltip;
//    document.body.appendChild(tooltip);
//}
//
//function hideTooltip(event) {
//    if (event.target.tooltipElement) {
//        event.target.tooltipElement.remove();
//    }
//}
//
//// 初始化文件上传
//function initFileUpload() {
//    const uploadArea = document.getElementById('uploadArea');
//    const fileInput = document.getElementById('fileInput');
//
//    if (!uploadArea || !fileInput) return;
//
//    uploadArea.addEventListener('click', () => fileInput.click());
//    fileInput.addEventListener('change', handleFileSelect);
//
//    uploadArea.addEventListener('dragover', (e) => {
//        e.preventDefault();
//        uploadArea.classList.add('drag-over');
//    });
//
//    uploadArea.addEventListener('dragleave', () => {
//        uploadArea.classList.remove('drag-over');
//    });
//
//    uploadArea.addEventListener('drop', (e) => {
//        e.preventDefault();
//        uploadArea.classList.remove('drag-over');
//
//        if (e.dataTransfer.files.length) {
//            handleFiles(e.dataTransfer.files);
//        }
//    });
//}
//
//// 处理文件选择
//function handleFileSelect(event) {
//    const files = event.target.files;
//    handleFiles(files);
//}
//
//// 处理文件
//function handleFiles(files) {
//    Array.from(files).forEach(file => {
//        if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
//            addFileToList(file);
//        }
//    });
//}
//
//// 添加文件到列表
//function addFileToList(file) {
//    if (selectedFiles.some(f => f.name === file.name)) {
//        showMessage('文件 ' + file.name + ' 已存在', 'warning');
//        return;
//    }
//
//    selectedFiles.push(file);
//    updateFileList();
//}
//
//// 更新文件列表显示
//function updateFileList() {
//    const fileList = document.getElementById('fileList');
//    if (!fileList) return;
//
//    fileList.innerHTML = '';
//
//    selectedFiles.forEach((file, index) => {
//        const fileItem = document.createElement('div');
//        fileItem.className = 'file-item';
//        fileItem.innerHTML = `
//            <div>
//                <div class="file-name">${file.name}</div>
//                <div class="file-size">${formatFileSize(file.size)}</div>
//            </div>
//            <button class="file-remove" onclick="removeFile(${index})" data-tooltip="移除文件">
//                <i class="fas fa-times"></i>
//            </button>
//        `;
//        fileList.appendChild(fileItem);
//    });
//
//    updateClassifyButtonState();
//}
//
//// 移除文件
//function removeFile(index) {
//    selectedFiles.splice(index, 1);
//    updateFileList();
//}
//
//// 清空所有文件
//function clearAllFiles() {
//    selectedFiles = [];
//    updateFileList();
//    document.getElementById('fileInput').value = '';
//}
//
//// 格式化文件大小
//function formatFileSize(bytes) {
//    if (bytes === 0) return '0 Bytes';
//    const k = 1024;
//    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
//    const i = Math.floor(Math.log(bytes) / Math.log(k));
//    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
//}
//
//// 更新分类按钮状态
//function updateClassifyButtonState() {
//    const classifyBtn = document.getElementById('classifyBtn');
//    if (classifyBtn) {
//        classifyBtn.disabled = selectedFiles.length === 0 || isProcessing;
//    }
//}
//
//// 初始化分类按钮事件
//function initClassifyButtons() {
//    const classifyBtn = document.getElementById('classifyBtn');
//    const classifyTextBtn = document.getElementById('classifyTextBtn');
//
//    if (classifyBtn) {
//        classifyBtn.addEventListener('click', classifyPDFs);
//    }
//
//    if (classifyTextBtn) {
//        classifyTextBtn.addEventListener('click', classifyText);
//    }
//}
//
//// 分类 PDF 文件
//async function classifyPDFs() {
//    if (selectedFiles.length === 0 || isProcessing) return;
//
//    isProcessing = true;
//    updateClassifyButtonState();
//
//    const loading = document.getElementById('loading');
//    const resultsContainer = document.getElementById('resultsContainer');
//    const classifyBtn = document.getElementById('classifyBtn');
//    const originalText = classifyBtn.innerHTML;
//
//    loading.classList.add('active');
//    classifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
//
//    if (resultsContainer) {
//        resultsContainer.innerHTML = '<div class="no-results">正在处理文件...</div>';
//    }
//
//    const formData = new FormData();
//    selectedFiles.forEach(file => {
//        formData.append('pdf_files', file);
//    });
//
//    try {
//        const response = await fetch('/classify/pdf', {
//            method: 'POST',
//            body: formData,
//            credentials: 'same-origin'
//        });
//
//        const data = await response.json();
//
//        if (response.ok && data.success) {
//            displayResults(data.results);
//            showMessage(`分类完成！成功处理 ${data.results.length} 个文件`, 'success');
//        } else {
//            throw new Error(data.error || '分类失败');
//        }
//    } catch (error) {
//        console.error('分类错误:', error);
//        showMessage('分类失败: ' + error.message, 'error');
//        if (resultsContainer) {
//            resultsContainer.innerHTML = '<div class="no-results" style="color: #ff4444;">分类失败: ' + error.message + '</div>';
//        }
//    } finally {
//        isProcessing = false;
//        updateClassifyButtonState();
//        loading.classList.remove('active');
//        classifyBtn.innerHTML = originalText;
//    }
//}
//
//// 分类文本
//async function classifyText() {
//    const textInput = document.getElementById('textInput');
//    const textResults = document.getElementById('textResults');
//    const classifyTextBtn = document.getElementById('classifyTextBtn');
//
//    if (!textInput || !textInput.value.trim()) {
//        showMessage('请输入要分类的文本', 'warning');
//        return;
//    }
//
//    if (textInput.value.trim().length < 10) {
//        showMessage('文本内容太短，请至少输入10个字符', 'warning');
//        return;
//    }
//
//    const originalText = classifyTextBtn.innerHTML;
//    classifyTextBtn.disabled = true;
//    classifyTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 分类中...';
//
//    if (textResults) {
//        textResults.innerHTML = '<div class="no-results">正在分类...</div>';
//    }
//
//    try {
//        const response = await fetch('/classify/text', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify({ text: textInput.value })
//        });
//
//        const data = await response.json();
//
//        if (response.ok && data.success) {
//            displayTextResults(data);
//            showMessage('文本分类完成', 'success');
//        } else {
//            throw new Error(data.error || '分类失败');
//        }
//    } catch (error) {
//        console.error('文本分类错误:', error);
//        showMessage('文本分类失败: ' + error.message, 'error');
//        if (textResults) {
//            textResults.innerHTML = '<div class="no-results" style="color: #ff4444;">分类失败: ' + error.message + '</div>';
//        }
//    } finally {
//        classifyTextBtn.disabled = false;
//        classifyTextBtn.innerHTML = originalText;
//    }
//}
//
//// 显示 PDF 分类结果
//function displayResults(results) {
//    const resultsContainer = document.getElementById('resultsContainer');
//    if (!resultsContainer) return;
//
//    resultsContainer.innerHTML = '';
//
//    if (!results || results.length === 0) {
//        resultsContainer.innerHTML = '<div class="no-results">没有分类结果</div>';
//        return;
//    }
//
//    let hasValidResults = false;
//
//    results.forEach(result => {
//        if (result.error) {
//            const errorItem = document.createElement('div');
//            errorItem.className = 'result-item';
//            errorItem.style.borderColor = '#ff4444';
//            errorItem.innerHTML = `
//                <div class="result-header">
//                    <div class="result-filename" style="color: #ff4444;">
//                        <i class="fas fa-exclamation-triangle"></i> ${result.filename}
//                    </div>
//                </div>
//                <div style="color: #ff4444;">错误: ${result.error}</div>
//            `;
//            resultsContainer.appendChild(errorItem);
//            return;
//        }
//
//        hasValidResults = true;
//        const resultItem = document.createElement('div');
//        resultItem.className = 'result-item';
//
//        let labelsHtml = '';
//        if (result.labels && result.labels.length > 0) {
//            labelsHtml = result.labels.map((label, index) => {
//                const confidence = result.confidences && result.confidences[index] !== undefined
//                    ? result.confidences[index]
//                    : 0;
//                return `
//                    <span class="label-tag">
//                        ${label}
//                        <span class="confidence-badge">${(confidence * 100).toFixed(1)}%</span>
//                    </span>
//                `;
//            }).join('');
//        } else {
//            labelsHtml = '<span class="no-labels">未识别到相关标签</span>';
//        }
//
//        resultItem.innerHTML = `
//            <div class="result-header">
//                <div class="result-filename">${result.filename || '未知文件'}</div>
//            </div>
//            <div class="result-labels">
//                ${labelsHtml}
//            </div>
//        `;
//
//        resultsContainer.appendChild(resultItem);
//    });
//
//    if (hasValidResults) {
//        const exportBtn = document.createElement('button');
//        exportBtn.className = 'btn';
//        exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出结果';
//        exportBtn.style.marginTop = '1rem';
//        exportBtn.onclick = () => exportResults(results);
//
//        resultsContainer.appendChild(exportBtn);
//    }
//}
//
//// 显示文本分类结果
//function displayTextResults(data) {
//    const textResults = document.getElementById('textResults');
//    if (!textResults) return;
//
//    textResults.innerHTML = '';
//
//    if (!data.labels || data.labels.length === 0) {
//        textResults.innerHTML = '<div class="no-results">未识别到相关标签</div>';
//        return;
//    }
//
//    const resultItem = document.createElement('div');
//    resultItem.className = 'result-item';
//
//    const labelsHtml = data.labels.map((label, index) => {
//        const confidence = data.confidences && data.confidences[index] !== undefined
//            ? data.confidences[index]
//            : 0;
//        return `
//            <span class="label-tag">
//                ${label}
//                <span class="confidence-badge">${(confidence * 100).toFixed(1)}%</span>
//            </span>
//        `;
//    }).join('');
//
//    resultItem.innerHTML = `
//        <div class="result-header">
//            <div class="result-filename">文本分类结果</div>
//        </div>
//        <div class="result-labels">
//            ${labelsHtml}
//        </div>
//    `;
//
//    textResults.appendChild(resultItem);
//}
//
//// 导出结果
//async function exportResults(results) {
//    try {
//        // 过滤掉错误的结果
//        const validResults = results.filter(r => !r.error && r.labels && r.labels.length > 0);
//
//        if (validResults.length === 0) {
//            showMessage('没有有效的结果可以导出', 'warning');
//            return;
//        }
//
//        const response = await fetch('/export/results', {
//            method: 'POST',
//            headers: {
//                'Content-Type': 'application/json',
//            },
//            body: JSON.stringify({ results: validResults }),
//            credentials: 'same-origin'
//        });
//
//        if (response.ok) {
//            const blob = await response.blob();
//            const url = window.URL.createObjectURL(blob);
//            const a = document.createElement('a');
//            a.href = url;
//            a.download = `论文分类结果_${new Date().toISOString().slice(0,10)}.xlsx`;
//            document.body.appendChild(a);
//            a.click();
//            window.URL.revokeObjectURL(url);
//            document.body.removeChild(a);
//
//            showMessage('导出成功', 'success');
//        } else {
//            const errorData = await response.json();
//            throw new Error(errorData.error || '导出失败');
//        }
//    } catch (error) {
//        console.error('导出错误:', error);
//        showMessage('导出失败: ' + error.message, 'error');
//    }
//}
//
//// 显示消息
//function showMessage(message, type = 'info') {
//    let messagesContainer = document.querySelector('.flash-messages');
//    if (!messagesContainer) {
//        messagesContainer = document.createElement('div');
//        messagesContainer.className = 'flash-messages';
//        document.body.appendChild(messagesContainer);
//    }
//
//    const messageElement = document.createElement('div');
//    messageElement.className = `flash-message ${type}`;
//    messageElement.textContent = message;
//
//    messagesContainer.appendChild(messageElement);
//
//    setTimeout(() => {
//        messageElement.style.opacity = '0';
//        messageElement.style.transform = 'translateX(100%)';
//        setTimeout(() => {
//            if (messageElement.parentNode) {
//                messageElement.parentNode.removeChild(messageElement);
//            }
//        }, 300);
//    }, 5000);
//}
//
//// 更新用户信息
//function updateUserInfo() {
//    const userInfo = document.querySelector('.user-info');
//    const username = document.querySelector('.username');
//
//    if (username && !username.textContent) {
//        username.textContent = '用户';
//    }
//}
//
//// 检查闪存消息
//function checkFlashMessages() {
//    // 这里可以添加从后端获取闪存消息的逻辑
//}
//
//// 登出函数
//function logout() {
//    if (confirm('确定要退出登录吗？')) {
//        fetch('/logout')
//            .then(response => {
//                if (response.ok) {
//                    window.location.href = '/';
//                }
//            })
//            .catch(error => {
//                console.error('登出错误:', error);
//                showMessage('登出失败', 'error');
//            });
//    }
//}
//
//// 删除历史记录（在历史页面使用）
//function deleteHistory(id) {
//    if (!confirm('确定要删除这条历史记录吗？')) {
//        return;
//    }
//
//    fetch(`/history/delete/${id}`, {
//        method: 'POST',
//        credentials: 'same-origin'
//    })
//    .then(response => response.json())
//    .then(data => {
//        if (data.success) {
//            showMessage('删除成功', 'success');
//            const row = document.querySelector(`[data-id="${id}"]`);
//            if (row) {
//                row.remove();
//                updateRecordCount();
//            }
//        } else {
//            showMessage('删除失败: ' + (data.error || '未知错误'), 'error');
//        }
//    })
//    .catch(error => {
//        console.error('删除错误:', error);
//        showMessage('删除失败: ' + error.message, 'error');
//    });
//}
//
//// 更新记录计数（在历史页面使用）
//function updateRecordCount() {
//    const rows = document.querySelectorAll('.history-table tbody tr');
//    const countElement = document.querySelector('.history-table + div');
//    if (countElement) {
//        countElement.textContent = `共 ${rows.length} 条记录`;
//    }
//}

// 全局变量
let selectedFiles = [];

// DOM 加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initFileUpload();
    initClassifyButtons();
});

// 初始化文件上传
function initFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    if (!uploadArea || !fileInput) return;

    uploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // 拖放功能
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
}

// 处理文件选择
function handleFileSelect(event) {
    const files = event.target.files;
    handleFiles(files);
}

// 处理文件
function handleFiles(files) {
    Array.from(files).forEach(file => {
        if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
            addFileToList(file);
        }
    });
}

// 添加文件到列表
function addFileToList(file) {
    if (selectedFiles.some(f => f.name === file.name)) {
        showMessage('文件 ' + file.name + ' 已存在', 'warning');
        return;
    }

    selectedFiles.push(file);
    updateFileList();
}

// 更新文件列表显示
function updateFileList() {
    const fileList = document.getElementById('fileList');
    if (!fileList) return;

    fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div>
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">
                <i class="fas fa-times"></i>
            </button>
        `;
        fileList.appendChild(fileItem);
    });

    updateClassifyButtonState();
}

// 移除文件
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
}

// 清空所有文件
function clearAllFiles() {
    selectedFiles = [];
    updateFileList();
    document.getElementById('fileInput').value = '';
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 更新分类按钮状态
function updateClassifyButtonState() {
    const classifyBtn = document.getElementById('classifyBtn');
    if (classifyBtn) {
        classifyBtn.disabled = selectedFiles.length === 0;
    }
}

// 初始化分类按钮事件
function initClassifyButtons() {
    const classifyBtn = document.getElementById('classifyBtn');
    const classifyTextBtn = document.getElementById('classifyTextBtn');

    if (classifyBtn) {
        classifyBtn.addEventListener('click', classifyPDFs);
    }

    if (classifyTextBtn) {
        classifyTextBtn.addEventListener('click', classifyText);
    }
}

// 分类 PDF 文件
async function classifyPDFs() {
    if (selectedFiles.length === 0) return;

    const loading = document.getElementById('loading');
    const resultsContainer = document.getElementById('resultsContainer');
    const classifyBtn = document.getElementById('classifyBtn');

    loading.classList.add('active');
    classifyBtn.disabled = true;
    classifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';

    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="no-results">正在处理文件...</div>';
    }

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('pdf_files', file);
    });

    try {
        const response = await fetch('/classify/pdf', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayResults(data.results);
            showMessage(`分类完成！成功处理 ${data.results.length} 个文件`, 'success');
        } else {
            throw new Error(data.error || '分类失败');
        }
    } catch (error) {
        console.error('分类错误:', error);
        showMessage('分类失败: ' + error.message, 'error');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="no-results" style="color: #ff4444;">分类失败: ' + error.message + '</div>';
        }
    } finally {
        loading.classList.remove('active');
        classifyBtn.disabled = false;
        classifyBtn.innerHTML = '<i class="fas fa-brain"></i> 开始分类';
    }
}

// 分类文本
async function classifyText() {
    const textInput = document.getElementById('textInput');
    const textResults = document.getElementById('textResults');
    const classifyTextBtn = document.getElementById('classifyTextBtn');

    if (!textInput || !textInput.value.trim()) {
        showMessage('请输入要分类的文本', 'warning');
        return;
    }

    classifyTextBtn.disabled = true;
    classifyTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 分类中...';

    if (textResults) {
        textResults.innerHTML = '<div class="no-results">正在分类...</div>';
    }

    try {
        const response = await fetch('/classify/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textInput.value })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            displayTextResults(data);
            showMessage('文本分类完成', 'success');
        } else {
            throw new Error(data.error || '分类失败');
        }
    } catch (error) {
        console.error('文本分类错误:', error);
        showMessage('文本分类失败: ' + error.message, 'error');
        if (textResults) {
            textResults.innerHTML = '<div class="no-results" style="color: #ff4444;">分类失败: ' + error.message + '</div>';
        }
    } finally {
        classifyTextBtn.disabled = false;
        classifyTextBtn.innerHTML = '<i class="fas fa-brain"></i> 文本分类';
    }
}

// 显示 PDF 分类结果
function displayResults(results) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '';

    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">没有分类结果</div>';
        return;
    }

    results.forEach(result => {
        if (result.error) {
            const errorItem = document.createElement('div');
            errorItem.className = 'result-item';
            errorItem.style.borderColor = '#ff4444';
            errorItem.innerHTML = `
                <div class="result-header">
                    <div class="result-filename" style="color: #ff4444;">
                        <i class="fas fa-exclamation-triangle"></i> ${result.filename}
                    </div>
                </div>
                <div style="color: #ff4444;">错误: ${result.error}</div>
            `;
            resultsContainer.appendChild(errorItem);
            return;
        }

        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';

        let labelsHtml = '';
        if (result.labels && result.labels.length > 0) {
            // 确保是多标签显示
            labelsHtml = result.labels.map((label, index) => {
                const confidence = result.confidences && result.confidences[index] !== undefined
                    ? result.confidences[index]
                    : 0;
                return `
                    <span class="label-tag">
                        ${label}
                        <span class="confidence-badge">${(confidence * 100).toFixed(1)}%</span>
                    </span>
                `;
            }).join('');
        } else {
            labelsHtml = '<span class="no-labels">未识别到相关标签</span>';
        }

        resultItem.innerHTML = `
            <div class="result-header">
                <div class="result-filename">${result.filename || '未知文件'}</div>
                <div style="color: var(--medium-gray); font-size: 0.9em;">
                    ${result.labels ? result.labels.length + ' 个标签' : '0 个标签'}
                </div>
            </div>
            <div class="result-labels">
                ${labelsHtml}
            </div>
        `;

        resultsContainer.appendChild(resultItem);
    });

    // 添加导出按钮
    if (results.length > 0) {
        const exportBtn = document.createElement('button');
        exportBtn.className = 'btn';
        exportBtn.innerHTML = '<i class="fas fa-download"></i> 导出结果';
        exportBtn.style.marginTop = '1rem';
        exportBtn.onclick = () => exportResults(results);

        resultsContainer.appendChild(exportBtn);
    }
}

// 显示文本分类结果
function displayTextResults(data) {
    const textResults = document.getElementById('textResults');
    if (!textResults) return;

    textResults.innerHTML = '';

    if (!data.labels || data.labels.length === 0) {
        textResults.innerHTML = '<div class="no-results">未识别到相关标签</div>';
        return;
    }

    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';

    const labelsHtml = data.labels.map((label, index) => {
        const confidence = data.confidences && data.confidences[index] !== undefined
            ? data.confidences[index]
            : 0;
        return `
            <span class="label-tag">
                ${label}
                <span class="confidence-badge">${(confidence * 100).toFixed(1)}%</span>
            </span>
        `;
    }).join('');

    resultItem.innerHTML = `
        <div class="result-header">
            <div class="result-filename">文本分类结果</div>
            <div style="color: var(--medium-gray); font-size: 0.9em;">
                ${data.labels.length} 个标签
            </div>
        </div>
        <div class="result-labels">
            ${labelsHtml}
        </div>
    `;

    textResults.appendChild(resultItem);
}

// 导出结果
async function exportResults(results) {
    try {
        const validResults = results.filter(r => !r.error && r.labels && r.labels.length > 0);

        if (validResults.length === 0) {
            showMessage('没有有效的结果可以导出', 'warning');
            return;
        }

        const response = await fetch('/export/results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ results: validResults })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `论文分类结果_${new Date().toISOString().slice(0,10)}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showMessage('导出成功', 'success');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error || '导出失败');
        }
    } catch (error) {
        console.error('导出错误:', error);
        showMessage('导出失败: ' + error.message, 'error');
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    let messagesContainer = document.querySelector('.flash-messages');
    if (!messagesContainer) {
        messagesContainer = document.createElement('div');
        messagesContainer.className = 'flash-messages';
        document.body.appendChild(messagesContainer);
    }

    const messageElement = document.createElement('div');
    messageElement.className = `flash-message ${type}`;
    messageElement.textContent = message;

    messagesContainer.appendChild(messageElement);

    setTimeout(() => {
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 300);
    }, 5000);
}

// 登出函数
function logout() {
    if (confirm('确定要退出登录吗？')) {
        window.location.href = '/logout';
    }
}

// 删除历史记录
function deleteHistory(id) {
    if (!confirm('确定要删除这条历史记录吗？')) {
        return;
    }

    fetch(`/history/delete/${id}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('删除成功', 'success');
            const row = document.querySelector(`[data-id="${id}"]`);
            if (row) {
                row.remove();
                updateRecordCount();
            }
        } else {
            showMessage('删除失败: ' + (data.error || '未知错误'), 'error');
        }
    })
    .catch(error => {
        console.error('删除错误:', error);
        showMessage('删除失败: ' + error.message, 'error');
    });
}

// 更新记录计数
function updateRecordCount() {
    const rows = document.querySelectorAll('.history-table tbody tr');
    const countElement = document.querySelector('.history-table + div');
    if (countElement) {
        countElement.textContent = `共 ${rows.length} 条记录`;
    }
}