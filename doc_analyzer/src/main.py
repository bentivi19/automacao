import logging
import os
from dotenv import load_dotenv
from src.ui.main_window import MainWindow
from src.ai_analyzer.mistral_client import MistralAnalyzer

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    try:
        # Inicializa o analisador
        analyzer = MistralAnalyzer()
        
        # Cria e executa a janela principal
        app = MainWindow(analyzer)
        app.run()
        
    except Exception as e:
        logger.error(f"Erro ao iniciar aplicação: {str(e)}")
        raise

if __name__ == "__main__":
    main()
