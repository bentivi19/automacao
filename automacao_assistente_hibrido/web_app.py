from flask import Flask, render_template, jsonify, request
from ocr_extract import process_text, save_to_excel
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process-text', methods=['POST'])
def process_content():
    try:
        content = request.json.get('content', '')
        if not content:
            return jsonify({'success': False, 'error': 'Nenhum conteúdo fornecido'})
        
        # Processa o texto para extrair NFs
        nfs = process_text(content)
        if not nfs:
            return jsonify({'success': False, 'error': 'Nenhuma NF encontrada no texto'})
        
        # Salva no Excel
        excel_path = r'C:\Users\Julio Soama\Desktop\Setor Notíficia de Fato\atribuicoes_do_dia.xlsx'
        success, duplicates = save_to_excel(nfs, excel_path)
        
        return jsonify({
            'success': success,
            'duplicates': duplicates if duplicates else []
        })
        
    except Exception as e:
        logging.error(f"Erro ao processar texto: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5000)
