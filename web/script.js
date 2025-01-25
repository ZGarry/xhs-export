// 状态更新
eel.expose(updateStatus);
function updateStatus(message) {
    const statusText = document.getElementById('status-text');
    statusText.textContent += message + '\n';
    statusText.scrollTop = statusText.scrollHeight;
}

// 进度更新
eel.expose(updateProgress);
function updateProgress(current, total) {
    const progress = document.getElementById('fetch-progress');
    const progressText = document.getElementById('fetch-progress-text');
    const percentage = Math.round((current / total) * 100);
    progress.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
}

// 文章下载进度更新
eel.expose(updateArticleProgress);
function updateArticleProgress(current, total) {
    const progress = document.getElementById('download-progress');
    const progressText = document.getElementById('download-progress-text');
    const percentage = Math.round((current / total) * 100);
    progress.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
}

// 显示错误
eel.expose(showError);
function showError(message) {
    alert(message);
    enableStartButton();
}

// 显示成功
eel.expose(showSuccess);
function showSuccess(message) {
    alert(message);
    enableStartButton();
}

// 显示登录模态框
eel.expose(showLoginModal);
function showLoginModal() {
    showModal('login-modal');
}

// 显示模态框
function showModal(id) {
    document.getElementById(id).classList.add('show');
}

// 关闭模态框
function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

// 确认已登录
function confirmLogin() {
    closeModal('login-modal');
    eel.confirm_login()();
}

// 禁用开始按钮
function disableStartButton() {
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="mdi mdi-loading mdi-spin"></i>导出中...';
}

// 启用开始按钮
function enableStartButton() {
    const startBtn = document.getElementById('start-btn');
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="mdi mdi-download"></i>开始导出';
    
    // 隐藏进度和日志区域
    document.getElementById('progress-section').classList.remove('show');
    document.getElementById('log-section').classList.remove('show');
    setTimeout(() => {
        document.getElementById('progress-section').classList.add('hidden');
        document.getElementById('log-section').classList.add('hidden');
    }, 300);
}

// 开始导出
async function startExport() {
    disableStartButton();
    
    // 显示进度和日志区域
    const progressSection = document.getElementById('progress-section');
    const logSection = document.getElementById('log-section');
    
    progressSection.classList.remove('hidden');
    logSection.classList.remove('hidden');
    
    // 触发重排以确保过渡动画生效
    progressSection.offsetHeight;
    logSection.offsetHeight;
    
    progressSection.classList.add('show');
    logSection.classList.add('show');
    
    startExportProcess();
}

// 开始导出流程
async function startExportProcess() {
    try {
        // 选择保存目录
        const directory = await eel.select_directory()();
        if (!directory) {
            enableStartButton();
            return;
        }
        
        // 重置进度条
        document.getElementById('fetch-progress').style.width = '0%';
        document.getElementById('fetch-progress-text').textContent = '0%';
        document.getElementById('download-progress').style.width = '0%';
        document.getElementById('download-progress-text').textContent = '0%';
        
        // 清空状态文本
        document.getElementById('status-text').textContent = '';
        
        // 开始导出
        eel.start_export(directory)();
    } catch (error) {
        showError('发生错误：' + error);
        enableStartButton();
    }
} 