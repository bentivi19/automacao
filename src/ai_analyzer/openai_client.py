import os
import openai
import logging
from typing import Dict, List
import yaml
from datetime import datetime
from src.knowledge_base.legal_knowledge import LegalKnowledgeBase
from src.pdf_processor.pdf_reader import PDFReader
from src.pdf_processor.pdf_splitter import PDFSplitter
import pytesseract
from PIL import Image
import pdf2image
import io
import re
import time

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        
        openai.api_key = self.api_key
        
        # Configuração de proxy se necessário
        proxy = os.getenv('HTTPS_PROXY')
        if proxy:
            openai.proxy = proxy
        
        self.model = "gpt-4"  # Usando GPT-4 para melhor análise
        self.knowledge_base = LegalKnowledgeBase()
        self.pdf_splitter = PDFSplitter(max_tokens_per_chunk=4000)  # GPT-4 tem contexto de 8K tokens
        self.load_rules()
        self.initialize_knowledge()
    
    def initialize_knowledge(self):
        """Inicializa a base de conhecimento jurídico e policial."""
        logger.info("Inicializando base de conhecimento...")
        self.knowledge_base.initialize()
    
    def load_rules(self):
        """Carrega as regras do arquivo YAML."""
        rules_path = os.path.join("config", "rules", "dispatch_rules.yaml")
        try:
            with open(rules_path, 'r', encoding='utf-8') as file:
                self.rules = yaml.safe_load(file)
            logger.info("Regras carregadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            raise

    def _extract_text_with_ocr(self, pdf_path: str) -> str:
        """Extrai texto do PDF usando OCR quando necessário."""
        try:
            # Converte PDF para imagens
            images = pdf2image.convert_from_path(pdf_path)
            text_parts = []
            
            for img in images:
                # Converte imagem para bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Extrai texto via OCR
                text = pytesseract.image_to_string(Image.open(io.BytesIO(img_byte_arr)), lang='por')
                text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"Erro no OCR: {str(e)}")
            return ""

    def process_document(self, file_path: str) -> Dict:
        """Processa o documento PDF e retorna a análise estruturada."""
        pdf_reader = None
        try:
            logger.info("Iniciando análise do documento...")
            
            # Verifica o tamanho do documento
            with open(file_path, 'rb') as f:
                file_size = len(f.read())
            
            # Define o modo de análise baseado no tamanho do arquivo (5MB como limite)
            is_large_file = file_size > 5 * 1024 * 1024
            logger.info(f"Modo de análise: {'grande' if is_large_file else 'normal'}")
            
            # Ajusta o tamanho dos chunks e modelo baseado no modo
            if is_large_file:
                self.model = "gpt-3.5-turbo-16k"  # Modelo com contexto maior para arquivos grandes
                self.pdf_splitter.max_tokens_per_chunk = 8000  # Metade do contexto
            else:
                self.model = "gpt-4"  # Modelo mais preciso para arquivos menores
                self.pdf_splitter.max_tokens_per_chunk = 4000  # Metade do contexto
            
            # Divide o PDF em chunks
            chunk_paths = self.pdf_splitter.split_pdf(file_path)
            logger.info(f"Documento dividido em {len(chunk_paths)} partes")
            
            # Analisa cada chunk
            chunk_analyses = []
            
            for i, chunk_path in enumerate(chunk_paths, 1):
                logger.info(f"Analisando parte {i} de {len(chunk_paths)}")
                
                # Adiciona delay entre chunks para evitar rate limits
                if i > 1:
                    time.sleep(3 if is_large_file else 1)
                
                pdf_reader = PDFReader()
                if not pdf_reader.load_pdf(chunk_path):
                    raise ValueError(f"Erro ao carregar chunk: {chunk_path}")
                
                text = pdf_reader.get_text()
                if not text.strip():
                    text = self._extract_text_with_ocr(chunk_path)
                
                pdf_reader.close()
                pdf_reader = None
                
                if not text.strip():
                    logger.warning(f"Chunk {i} está vazio, pulando...")
                    continue
                
                # Sistema de retry com backoff exponencial
                retry_count = 0
                max_retries = 5
                base_delay = 2
                
                while True:
                    try:
                        analysis = self._analyze_chunk(text, is_last_chunk=(i == len(chunk_paths)))
                        chunk_analyses.append(analysis)
                        break
                    except openai.error.RateLimitError as e:
                        retry_count += 1
                        if retry_count > max_retries:
                            raise ValueError(f"Máximo de tentativas excedido ao processar chunk {i}")
                        
                        wait_time = base_delay ** retry_count
                        logger.warning(f"Rate limit atingido, tentativa {retry_count}/{max_retries}. Aguardando {wait_time}s...")
                        time.sleep(wait_time)
                    except Exception as e:
                        logger.error(f"Erro ao analisar chunk {i}: {str(e)}")
                        raise
            
            if not chunk_analyses:
                raise ValueError("Nenhum texto válido encontrado no documento")
            
            # Consolida as análises
            final_analysis = self._consolidate_analyses(chunk_analyses)
            
            # Estrutura o resultado
            result = {
                'analysis': final_analysis,
                'metadata': {
                    'timestamp': str(datetime.now()),
                    'model': self.model,
                    'document_path': file_path,
                    'parts_analyzed': len(chunk_paths),
                    'mode': 'large' if is_large_file else 'normal'
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise do documento: {str(e)}")
            raise
        finally:
            if pdf_reader is not None:
                pdf_reader.close()
            self.pdf_splitter.cleanup()

    def _analyze_chunk(self, text: str, is_last_chunk: bool = False) -> str:
        """Analisa um chunk de texto."""
        try:
            messages = [
                {"role": "system", "content": """Você é um assistente especializado em análise de documentos jurídicos.
                     
                     ATENÇÃO - INSTRUÇÕES CRÍTICAS:
                     1. {'Este é o último chunk do documento. ' if is_last_chunk else ''}A última manifestação do(a) Promotor(a) SEMPRE existe
                     2. Procure nas partes finais, especialmente nos rodapés das páginas (marcados com [PÁGINA X])
                     3. NUNCA peça ao usuário para fornecer documentos
                     4. Se não encontrar a manifestação, informe claramente
                     
                     ETAPA 1 - Localização da Última Manifestação:
                     - Procure por números de página para manter o contexto
                     - Procure por assinaturas digitais ou físicas
                     - Identifique o último Promotor(a) que se manifestou
                     
                     ETAPA 2 - Extração Precisa das Informações:
                     1. Número da NF (deve estar EXATAMENTE no formato XXXX.XXXXXXX/XXXX)
                     2. Promotoria de Justiça que enviou a NF por último
                     3. Artigo do código penal indicado OU enunciado relacionado
                     4. Endereço da vítima (ou da pessoa a ser investigada se não houver vítima)
                     5. Datas relevantes do BO ou documento que gerou a NF
                     
                     RETORNO:
                     - Se encontrar a manifestação: Liste TODAS as informações acima
                     - Se não encontrar: Retorne "Não foi possível encontrar a última manifestação neste trecho"
                     
                     IMPORTANTE:
                     - NUNCA peça documentos ao usuário
                     - Se não encontrar a manifestação, apenas informe
                     - Seja preciso e detalhado nas informações encontradas"""},
                {"role": "user", "content": f"Analise este texto seguindo as instruções:\n\n{text}"}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                n=1,
                request_timeout=300  # 5 minutos de timeout
            )
            
            return response['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Erro ao analisar chunk: {str(e)}")
            raise

    def _consolidate_analyses(self, analyses: List[str]) -> str:
        """Consolida as análises de diferentes partes do documento."""
        try:
            consolidated_input = "\n\n".join([
                f"=== Parte {i+1} ===\n{analysis}"
                for i, analysis in enumerate(analyses)
            ])
            
            messages = [
                {"role": "system", "content": """Você é um assistente especializado em análise de documentos jurídicos.
                     
                     TAREFA: Consolide as análises das diferentes partes do documento.
                     
                     REGRAS DE CONSOLIDAÇÃO:
                     1. Mantenha TODAS as informações da última manifestação do(a) Promotor(a):
                        - Número da NF (formato XXXX.XXXXXXX/XXXX)
                        - Promotoria de Justiça que enviou a NF por último
                        - Artigo do código penal ou enunciado relacionado
                        - Endereço da vítima/investigado
                        - Datas relevantes do BO/documento inicial
                     
                     2. Mantenha as exceções encontradas em TODO o documento:
                        - Se ID_1 foi encontrado em qualquer parte: "ENVIAR_EMAIL:ID_1"
                        - Se ID_2 foi encontrado em qualquer parte: "ENVIAR_EMAIL:ID_2"
                        - Se nenhuma exceção encontrada: "CADASTRAR_PORTAL"
                     
                     RETORNO OBRIGATÓRIO:
                     1. Liste TODAS as informações extraídas da última manifestação
                     2. Indique a ação baseada nas exceções encontradas
                     
                     IMPORTANTE: Não prossiga sem ter todas as informações solicitadas."""},
                {"role": "user", "content": f"Consolide estas análises seguindo as regras especificadas:\n\n{consolidated_input}"}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                n=1,
                request_timeout=300  # 5 minutos de timeout
            )
            
            return response['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Erro ao consolidar análises: {str(e)}")
            raise

    def _generate_recommendations(self, analysis: str) -> List[str]:
        """Gera recomendações baseadas na análise do documento."""
        try:
            messages = [
                {"role": "system", "content": "Gere recomendações práticas baseadas na análise do documento."},
                {"role": "user", "content": f"Com base nesta análise, quais são as recomendações principais?\n\n{analysis}"}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                n=1
            )
            
            recommendations = response['choices'][0]['message']['content'].split('\n')
            return [rec.strip() for rec in recommendations if rec.strip()]
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return []