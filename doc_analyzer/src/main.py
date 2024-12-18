import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from src.pdf_processor.pdf_extractor import PDFExtractor
from src.rules_engine.rule_processor import RuleProcessor
from src.email_sender.email_manager import EmailManager
from src.ui.main_window import MainWindow

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self):
        load_dotenv()
        self.mistral_client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))
        self.pdf_extractor = PDFExtractor()
        self.rule_processor = RuleProcessor()
        self.email_manager = EmailManager()

    def analyze_document(self, file_path: str) -> dict:
        """Analisa um documento usando o Mistral AI."""
        try:
            # Extrai texto do PDF
            text = self.pdf_extractor.extract_text(file_path)
            
            # Analisa com Mistral
            messages = [
                ChatMessage(role="system", content="Você é um assistente especializado em análise de documentos jurídicos."),
                ChatMessage(role="user", content=f"Analise este documento e extraia as informações principais: {text[:4000]}")
            ]
            
            chat_response = self.mistral_client.chat(
                model="mistral-medium",
                messages=messages
            )
            
            analysis = chat_response.choices[0].message.content
            
            # Processa regras
            rules_result = self.rule_processor.process(analysis)
            
            # Prepara email se necessário
            if rules_result.get('send_email'):
                self.email_manager.prepare_email(rules_result)
            
            return {
                'analysis': analysis,
                'rules_result': rules_result
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            raise

def main():
    try:
        # Cria diretórios necessários
        Path("logs").mkdir(exist_ok=True)
        
        # Inicializa o analisador
        analyzer = DocumentAnalyzer()
        
        # Inicia a interface gráfica
        app = MainWindow(analyzer)
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {str(e)}")
        raise

if __name__ == "__main__":
    main()
