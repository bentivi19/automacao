import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from .base_analyzer import BaseAnalyzer
from ..knowledge_base.legal_knowledge import LegalKnowledgeBase
from ..pdf_processor.pdf_splitter import PDFSplitter
from ..pdf_processor.pdf_reader import PDFReader
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

logger = logging.getLogger(__name__)

class MistralAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        # Configuração do cliente com proxy se necessário
        proxy = os.getenv('HTTPS_PROXY')
        if proxy:
            import httpx
            transport = httpx.HTTPTransport(proxy=proxy)
            client = httpx.Client(transport=transport)
            self.client = MistralClient(
                api_key=self.api_key,
                http_client=client
            )
        else:
            self.client = MistralClient(api_key=self.api_key)
        
        self._load_rules()
        self._init_knowledge_base()

    def analyze_document(self, file_path: str) -> str:
        try:
            logger.info("Iniciando análise do documento...")
            
            # Divide o documento em partes
            splitter = PDFSplitter()
            chunks = splitter.split_pdf(file_path)
            
            logger.info(f"Documento dividido em {len(chunks)} partes")
            
            # Analisa cada parte
            analysis_results = []
            for i, chunk_path in enumerate(chunks, 1):
                logger.info(f"Analisando parte {i} de {len(chunks)}")
                chunk_text = PDFReader.read_text_file(chunk_path)
                
                # Monta o prompt com o contexto
                prompt = f"{self.rules}\n\nCONTEXTO DO DOCUMENTO:\n{chunk_text}\n\nANÁLISE:"
                
                # Faz a chamada para a API
                messages = [
                    ChatMessage(role="system", content="Você é um assistente especializado em análise de documentos."),
                    ChatMessage(role="user", content=prompt)
                ]
                
                response = self.client.chat(
                    model="mistral-large-latest",
                    messages=messages,
                    temperature=0,
                    max_tokens=4000
                )
                
                analysis_results.append(response.choices[0].message.content)
            
            # Combina os resultados
            combined_analysis = "\n\n".join(analysis_results)
            
            # Limpa os arquivos temporários
            splitter.cleanup()
            
            return combined_analysis
            
        except Exception as e:
            logger.error(f"Erro na análise do documento: {str(e)}")
            splitter.cleanup()
            raise

    def answer_question(self, question: str, context: str) -> str:
        try:
            prompt = f"{self.rules}\n\nCONTEXTO:\n{context}\n\nPERGUNTA: {question}\n\nRESPOSTA:"
            
            messages = [
                ChatMessage(role="system", content="Você é um assistente especializado em análise de documentos."),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model="mistral-large-latest",
                messages=messages,
                temperature=0,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            raise
