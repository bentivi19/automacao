// Injetar Office.js na página
if (!document.querySelector('script[src*="office.js"]')) {
    const script = document.createElement('script');
    script.src = 'https://appsforoffice.microsoft.com/lib/1/hosted/office.js';
    document.head.appendChild(script);
}

// Comunicação com a página
window.addEventListener('message', function(event) {
    // Verifica se a mensagem é do nosso domínio
    if (event.origin !== window.location.origin) return;

    const { action, data } = event.data;

    if (action === 'writeToExcel') {
        writeToExcel(data);
    }
});

// Função para escrever no Excel
function writeToExcel(data) {
    Office.onReady()
        .then(function() {
            return Excel.run(function(context) {
                const sheet = context.workbook.worksheets.getActiveWorksheet();
                
                // Encontra a última linha usada
                const range = sheet.getUsedRange();
                range.load('rowCount');
                
                return context.sync()
                    .then(function() {
                        const startRow = range.rowCount + 1;
                        
                        // Adiciona os dados
                        data.forEach((row, index) => {
                            sheet.getRange(`A${startRow + index}`).values = [[row.nf]];
                            sheet.getRange(`B${startRow + index}`).values = [[row.promotoria]];
                            sheet.getRange(`C${startRow + index}`).values = [[new Date().toLocaleDateString('pt-BR')]];
                        });
                        
                        return context.sync();
                    });
            });
        })
        .catch(function(error) {
            console.error('Erro ao escrever no Excel:', error);
            window.postMessage({
                action: 'excelError',
                error: error.message
            }, window.location.origin);
        });
}
