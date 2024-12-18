import os
import json
import logging
from mistralai.client import MistralClient as BaseClient
from mistralai.models.chat_completion import ChatMessage
from dotenv import load_dotenv

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logs/ai_analyzer.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class MistralClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = BaseClient(api_key=self.api_key)
        self.model = "mistral-medium"

    def analyze_document(self, text: str) -> str:
        """Analisa um documento usando o Mistral AI.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            str: Resultado da análise
        """
        try:
            # Garante que o texto é uma string
            if not isinstance(text, str):
                text = str(text)
            
            system_prompt = """Você é um assistente especializado em análise de Notas Fiscais (NFs) e documentos jurídicos.
Para NFs, extraia e organize as seguintes informações em formato estruturado:
1. Número da NF
2. Data de emissão
3. Valor total
4. Nome do emitente
5. CNPJ do emitente
6. Nome do destinatário
7. CNPJ do destinatário
8. Lista de produtos/serviços com valores

Para documentos jurídicos, extraia:
1. Tipo de documento
2. Número do processo
3. Partes envolvidas
4. Datas relevantes
5. Principais pontos do documento

Formate a saída de forma clara e organizada, usando marcadores para facilitar a leitura.
Ao final, indique se há alguma ação necessária ou ponto que requer atenção especial.

Estou pronto para responder perguntas específicas sobre o documento. O usuário pode me perguntar sobre qualquer detalhe do documento."""

            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=text)
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            raise

    def ask_question(self, text: str, question: str) -> str:
        """Faz uma pergunta específica sobre o documento.
        
        Args:
            text: Texto do documento
            question: Pergunta sobre o documento
            
        Returns:
            str: Resposta à pergunta
        """
        try:
            messages = [
                ChatMessage(
                    role="system",
                    content="Você é um assistente especializado em análise de documentos. "
                           "Responda à pergunta do usuário com base no documento fornecido, "
                           "sendo preciso e direto na resposta."
                ),
                ChatMessage(role="user", content=f"Documento:\n{text}\n\nPergunta: {question}")
            ]
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {str(e)}")
            raise

class DocumentAnalyzer:
    def __init__(self):
        """Inicializa o analisador de documentos usando Mistral AI."""
        self.client = MistralClient()
        
    def analyze_document(self, text: str) -> dict:
        """Analisa o texto do documento e extrai informações relevantes.
        
        Args:
            text: Texto extraído do documento PDF
            
        Returns:
            Dict com as informações extraídas
        """
        try:
            # Faz a chamada à API
            response = self.client.analyze_document(text)

            # Processa a resposta
            analysis = self._parse_response(response)
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
