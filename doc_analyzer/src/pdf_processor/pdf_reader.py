import logging
import fitz  # PyMuPDF
from typing import Dict, List, Optional
import re

logger = logging.getLogger(__name__)

class PDFReader:
    def __init__(self):
        self.current_pdf = None
        self.text_content = ""
        self.metadata = {}
        
    def load_pdf(self, file_path: str) -> bool:
        """Carrega um arquivo PDF e extrai seu conteúdo."""
        try:
            self.current_pdf = fitz.open(file_path)
            self.text_content = ""
            self.metadata = {}
            
            # Extrai o texto de cada página com timeout
            for page in self.current_pdf:
                # Extrai o texto básico
                text = page.get_text()
                # Remove caracteres especiais e espaços extras
                text = re.sub(r'\s+', ' ', text)
                self.text_content += text + "\n"
            
            # Remove espaços extras no final
            self.text_content = self.text_content.strip()
            
            # Extrai metadados
            self.metadata = self.current_pdf.metadata
            
            logger.info(f"PDF carregado com sucesso: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar PDF: {str(e)}")
            return False
        
    def extract_field(self, field_name: str, patterns: List[str]) -> Optional[str]:
        """Extrai um campo específico do texto usando uma lista de padrões regex."""
        if not self.text_content:
            return None
            
        for pattern in patterns:
            try:
                # Simplifica o padrão mantendo os grupos
                pattern = pattern.replace("(?<=", "").replace("(?=", "")
                if "(" in pattern and ")" not in pattern:
                    pattern += ")"
                match = re.search(pattern, self.text_content, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Se o padrão tem grupos de captura, pega o último grupo não vazio
                    groups = [g for g in match.groups() if g]
                    if groups:
                        return groups[-1].strip()
                    return match.group(0).strip()
            except Exception as e:
                logger.warning(f"Erro ao processar padrão '{pattern}': {str(e)}")
                continue
                
        return None
        
    def extract_fields(self, fields_config: Dict) -> Dict:
        """Extrai múltiplos campos do PDF baseado em uma configuração."""
        results = {}
        
        for field_name, config in fields_config.items():
            if isinstance(config, list):
                # Se config é uma lista, são apenas padrões
                value = self.extract_field(field_name, config)
            elif isinstance(config, dict):
                # Se config é um dict, pode ter padrões e pós-processamento
                value = self.extract_field(field_name, config['patterns'])
                if value and 'post_process' in config:
                    value = config['post_process'](value)
            
            if value:
                results[field_name] = value
                
        return results
        
    def get_text(self) -> str:
        """Retorna o texto completo do PDF."""
        return self.text_content
        
    def get_metadata(self) -> Dict:
        """Retorna os metadados do PDF."""
        return self.metadata
        
    def __del__(self):
        """Fecha o PDF quando o objeto é destruído."""
        if self.current_pdf:
            self.current_pdf.close()
