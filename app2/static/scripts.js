async function checkServerStatus() {
    const serverStatusElement = document.getElementById('server-status');
    serverStatusElement.style.display = 'block';
    serverStatusElement.textContent = '正在檢查...';

    try {
        const response = await fetch('/check_server_status');
        const result = await response.json();
        if (result.status === 'online') {
            serverStatusElement.textContent = 'Minecraft 伺服器在線上！';
            serverStatusElement.classList.remove('alert-danger');
            serverStatusElement.classList.add('alert-success');
        } else {
            serverStatusElement.textContent = 'Minecraft 伺服器離線！';
            serverStatusElement.classList.remove('alert-success');
            serverStatusElement.classList.add('alert-danger');
        }
    } catch (error) {
        serverStatusElement.textContent = '檢查伺服器狀態時出錯！';
        serverStatusElement.classList.remove('alert-success');
        serverStatusElement.classList.add('alert-danger');
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    checkServerStatus();
});
