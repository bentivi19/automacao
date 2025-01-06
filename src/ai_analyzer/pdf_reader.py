"""
Módulo auxiliar para leitura do arquivo PDF consolidado.
"""

import os
from pathlib import Path

def get_pdf_content():
    """Lê e retorna o conteúdo do arquivo PDF consolidado."""
    # Caminho do arquivo consolidado
    project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    pdf_file = project_root / "pdf_provisorio.py"
    
    if not pdf_file.exists():
        return None
        
    try:
        # Lê o arquivo como texto
        with open(pdf_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extrai o conteúdo da variável PDF_CONTENT
        import re
        match = re.search(r'PDF_CONTENT\s*=\s*"""(.*?)"""', content, re.DOTALL)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Erro ao ler arquivo consolidado: {str(e)}")
        
    return None
