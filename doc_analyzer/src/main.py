import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Adiciona o diretório pai ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai_analyzer.mistral_client import MistralClient
from src.pdf_processor.pdf_extractor import PDFExtractor
from src.rules_engine.rule_processor import RuleProcessor
from src.email_sender.email_manager import EmailManager
from src.ui.main_window import MainWindow

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

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
        """Inicializa o analisador de documentos."""
        # Carrega variáveis de ambiente
        load_dotenv()
        
        # Inicializa os componentes
        self.mistral_client = MistralClient()
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

    def process_document(self, file_path: str) -> dict:
        """Processa um documento PDF e retorna os resultados da análise.
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            dict: Resultados da análise
        """
        try:
            # Extrai texto do PDF
            text = self.pdf_extractor.extract_text(file_path)
            
            # Aplica regras de negócio
            processed_text = self.rule_processor.process_rules(text)
            
            # Analisa com IA
            analysis = self.mistral_client.analyze_document(processed_text)
            
            return {
                'text': text,
                'processed': processed_text,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar documento: {str(e)}")
            raise

def main():
    try:
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
