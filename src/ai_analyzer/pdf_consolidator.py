"""
PDFConsolidator - Responsável por consolidar chunks em um arquivo temporário
e fornecer métodos de validação e verificação.
"""

import os
from pathlib import Path
import re
import sys
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class PDFConsolidator:
    def __init__(self):
        # Define o caminho do arquivo no diretório raiz do projeto
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.temp_file_path = self.project_root / "pdf_provisorio.py"
        self.content = ""
        
    def consolidate_chunks(self, chunks: List[str]) -> bool:
        """Consolida os chunks em um único conteúdo e salva em arquivo."""
        try:
            logger.info(f"Iniciando consolidação de {len(chunks)} chunks...")
            self.content = "\n".join(chunks)
            
            # Garante que o diretório existe
            self.project_root.mkdir(parents=True, exist_ok=True)
            
            # Tenta criar o arquivo várias vezes
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    with open(self.temp_file_path, 'w', encoding='utf-8') as f:
                        f.write('"""Conteúdo consolidado do PDF para análise."""\n\n')
                        f.write('import re\n\n')
                        f.write('PDF_CONTENT = """\n')
                        f.write(self.content)
                        f.write('\n"""\n\n')
                        f.write('def get_content():\n')
                        f.write('    """Retorna o conteúdo completo do PDF."""\n')
                        f.write('    return PDF_CONTENT\n\n')
                        f.write('def search_text(query: str) -> str:\n')
                        f.write('    """Busca texto específico no conteúdo."""\n')
                        f.write('    match = re.search(f"[^.]*{query}[^.]*", PDF_CONTENT, re.IGNORECASE)\n')
                        f.write('    return match.group() if match else f"Texto {query} não encontrado"\n')
                    
                    # Verifica se o arquivo foi criado
                    if self.temp_file_path.exists():
                        size = self.temp_file_path.stat().st_size
                        logger.info(f"Arquivo consolidado criado com sucesso: {self.temp_file_path} ({size} bytes)")
                        return True
                        
                except Exception as e:
                    logger.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    if attempt < max_attempts - 1:
                        time.sleep(1)  # Espera 1 segundo antes de tentar novamente
                        continue
                    raise
                    
            return False
            
        except Exception as e:
            logger.error(f"Erro fatal ao consolidar chunks: {str(e)}")
            return False
            
    def get_content(self) -> str:
        """Retorna o conteúdo atual do arquivo consolidado."""
        try:
            if not self.temp_file_path.exists():
                logger.error(f"Arquivo consolidado não existe: {self.temp_file_path}")
                return ""
                
            with open(self.temp_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'PDF_CONTENT = """\n(.*?)\n"""', content, re.DOTALL)
                if match:
                    return match.group(1)
                    
            logger.error("Conteúdo PDF não encontrado no arquivo")
            return ""
            
        except Exception as e:
            logger.error(f"Erro ao ler arquivo consolidado: {str(e)}")
            return ""
            
    def search_in_content(self, query: str) -> Optional[str]:
        """Busca um texto específico no conteúdo consolidado."""
        content = self.get_content()
        if not content:
            logger.error("Conteúdo vazio, não é possível realizar busca")
            return None
            
        try:
            match = re.search(f"[^.]*{query}[^.]*", content, re.IGNORECASE)
            if match:
                return match.group()
                
            logger.info(f"Texto '{query}' não encontrado no conteúdo")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar texto: {str(e)}")
            return None
            
    def validate_last_promoter(self, current_promoter: str) -> Optional[str]:
        """Valida o último promotor usando o conteúdo consolidado."""
        content = self.get_content()
        if not content:
            return None
            
        try:
            # Busca o nome do promotor no contexto
            match = re.search(f"[^.]*{current_promoter}[^.]*", content, re.IGNORECASE)
            if match:
                return current_promoter
                
            logger.warning(f"Promotor '{current_promoter}' não encontrado no conteúdo")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao validar promotor: {str(e)}")
            return None
            
    def verify_keywords(self, keywords: List[str]) -> List[str]:
        """Verifica quais palavras-chave estão presentes no conteúdo."""
        content = self.get_content()
        if not content:
            return []
            
        try:
            found = []
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    found.append(keyword)
                    logger.info(f"Palavra-chave encontrada: {keyword}")
                    
            return found
            
        except Exception as e:
            logger.error(f"Erro ao verificar palavras-chave: {str(e)}")
            return []
            
    def cleanup(self):
        """Remove o arquivo temporário."""
        try:
            if self.temp_file_path.exists():
                self.temp_file_path.unlink()
                logger.info("Arquivo temporário removido com sucesso")
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário: {str(e)}")
