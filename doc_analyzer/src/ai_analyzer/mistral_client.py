from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_analyzer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def __init__(self):
        """Inicializa o analisador de documentos usando Mistral AI."""
        load_dotenv()
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = MistralClient(api_key=self.api_key)
        self.model = "mistral-medium"  # ou outro modelo disponível

    def analyze_document(self, text: str) -> dict:
        """Analisa o texto do documento e extrai informações relevantes.
        
        Args:
            text: Texto extraído do documento PDF
            
        Returns:
            Dict com as informações extraídas
        """
        try:
            # Prepara o prompt para a análise
            messages = [
                ChatMessage(
                    role="system",
                    content="Você é um assistente especializado em análise de documentos jurídicos. "
                           "Extraia as seguintes informações do texto fornecido: "
                           "1. Número da Notícia de Fato "
                           "2. Promotoria responsável "
                           "3. Artigos do código penal ou enquadramento legal "
                           "4. Endereço para encaminhamento "
                           "5. Promotor que fez a última manifestação "
                           "6. Se há assinatura digital "
                           "7. Local e data dos fatos"
                ),
                ChatMessage(
                    role="user",
                    content=text
                )
            ]

            # Faz a chamada à API
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Baixa temperatura para respostas mais precisas
                max_tokens=1000
            )

            # Processa a resposta
            analysis = self._parse_response(response.messages[-1].content)
            logger.info("Análise concluída com sucesso")
            return analysis

        except Exception as e:
            logger.error(f"Erro na análise do documento: {str(e)}")
            raise

    def _parse_response(self, response: str) -> dict:
        """Processa a resposta da API e extrai as informações em formato estruturado."""
        try:
            # Aqui você pode implementar um parser mais robusto
            # Por enquanto, vamos usar um formato simples
            lines = response.split('\n')
            result = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
            
            return result

        except Exception as e:
            logger.error(f"Erro ao processar resposta da API: {str(e)}")
            return {}
