import fitz  # PyMuPDF
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, pdf_path: str) -> str:
        """Extrai texto de um arquivo PDF."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
            raise
