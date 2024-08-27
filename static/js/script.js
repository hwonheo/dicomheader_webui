let inputDirHandle = null;
let outputDirHandle = null;

document.addEventListener('DOMContentLoaded', function() {
    const collapseBtns = document.querySelectorAll('.collapse-btn');
    const description = document.querySelector('.description');
    
    collapseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (description.style.display === 'none') {
                description.style.display = 'block';
                collapseBtns.forEach(b => b.textContent = b.textContent.replace('▼', '▲'));
            } else {
                description.style.display = 'none';
                collapseBtns.forEach(b => b.textContent = b.textContent.replace('▲', '▼'));
            }
        });
    });

    const langKo = document.getElementById('lang-ko');
    const langEn = document.getElementById('lang-en');

    langKo.addEventListener('click', () => setLanguage('ko'));
    langEn.addEventListener('click', () => setLanguage('en'));

    function setLanguage(lang) {
        document.querySelectorAll('[data-lang]').forEach(elem => {
            if (elem.getAttribute('data-lang') === lang) {
                elem.style.display = '';
            } else {
                elem.style.display = 'none';
            }
        });
    }
});

async function selectDirectory(inputId) {
    try {
        const dirHandle = await window.showDirectoryPicker();
        document.getElementById(inputId).value = dirHandle.name;
        if (inputId === 'input_dir') {
            inputDirHandle = dirHandle;
        } else if (inputId === 'output_dir') {
            outputDirHandle = dirHandle;
        }
    } catch (error) {
        console.error('디렉토리 선택 취소 또는 오류:', error);
    }
}

document.querySelector('form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    let inputPath = document.getElementById('input_dir').value;
    let outputPath = document.getElementById('output_dir').value;
    
    if (inputDirHandle) {
        inputPath = await getDirectoryPath(inputDirHandle);
    }
    if (outputDirHandle) {
        outputPath = await getDirectoryPath(outputDirHandle);
    }
    
    const formData = new FormData();
    formData.append('input_dir', inputPath);
    formData.append('output_dir', outputPath);
    
    showLoading();
    
    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const messages = text.split('\n');
            
            for (const message of messages) {
                if (message.trim()) {
                    try {
                        const data = JSON.parse(message.trim());
                        if (data.progress) {
                            updateProgress(data.progress);
                        } else if (data.result) {
                            displayResult(data.result);
                        }
                    } catch (error) {
                        console.error('Error parsing JSON:', error, 'Raw message:', message);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        displayResult({ success: false, message: '서버와의 통신 중 오류가 발생했습니다.' });
    } finally {
        hideLoading();
    }
});

async function getDirectoryPath(dirHandle) {
    let path = dirHandle.name;
    while (dirHandle.parent) {
        dirHandle = await dirHandle.parent;
        path = dirHandle.name + '/' + path;
    }
    return '/' + path;
}

function pasteFromClipboard(inputId) {
    navigator.clipboard.readText().then(text => {
        document.getElementById(inputId).value = text.trim();
    }).catch(err => {
        console.error('클립보드 읽기 실패:', err);
        alert('클립보드에서 텍스트를 읽을 수 없습니다. 수동으로 붙여넣기를 해주세요.');
    });
}

function showLoading() {
    document.getElementById('overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('overlay').style.display = 'none';
}

function updateProgress(progress) {
    document.getElementById('progress-message').textContent = progress;
}

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = result.message;
    resultDiv.className = result.success ? 'result success' : 'result error';
    
    if (result.success) {
        const loadingMessage = document.getElementById('loading-message');
        loadingMessage.textContent = 'Process Done!';
        loadingMessage.className = 'process-done';
        
        setTimeout(() => {
            hideLoading();
        }, 2000);
    } else {
        hideLoading();
    }
}