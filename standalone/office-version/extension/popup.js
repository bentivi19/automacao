document.addEventListener('DOMContentLoaded', function() {
    const statusDiv = document.getElementById('status');

    // Verifica se o Office.js está disponível
    if (typeof Office !== 'undefined') {
        Office.onReady(function(info) {
            if (info.host === Excel) {
                statusDiv.className = 'status success';
                statusDiv.textContent = 'Conectado ao Excel com sucesso!';
            } else {
                statusDiv.className = 'status error';
                statusDiv.textContent = 'Excel não detectado. Abra uma planilha do Excel.';
            }
        });
    } else {
        statusDiv.className = 'status error';
        statusDiv.textContent = 'Office.js não encontrado. Recarregue a página.';
    }
});
