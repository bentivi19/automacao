import os
import anthropic
import logging
from typing import Dict, List
from datetime import datetime
import time
from src.knowledge_base.legal_knowledge import LegalKnowledgeBase
from src.pdf_processor.pdf_reader import PDFReader
from src.pdf_processor.pdf_splitter import PDFSplitter
from src.utils.rules_loader import RulesLoader, rules_manager

logger = logging.getLogger(__name__)

class AnthropicAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-opus-20240229"
        self.knowledge_base = LegalKnowledgeBase()
        self.pdf_splitter = PDFSplitter(max_tokens_per_chunk=16000)
        self.rules = RulesLoader.load_rules()
        self.initialize_knowledge()
    
    def initialize_knowledge(self):
        """Inicializa a base de conhecimento jurídico e policial."""
        logger.info("Inicializando base de conhecimento...")
        self.knowledge_base.initialize()
    
    def _analyze_chunk(self, text: str, is_last_chunk: bool = False) -> str:
        """Analisa um chunk de texto usando o modelo Claude."""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Verifica regras antes da análise
                rule_matches = rules_manager.check_rules(text)
                
                # Prepara informações sobre regras encontradas
                rules_info = ""
                action = "CADASTRAR_PORTAL"
                notify = None
                
                for category, matches in rule_matches.items():
                    if matches:
                        rules_info += f"\nRegras de {category} encontradas:\n"
                        for match in matches:
                            rules_info += f"- {match['name']} (Prioridade: {match['priority']})\n"
                            if match['action'] == "NÃO_CADASTRAR":
                                action = "NÃO_CADASTRAR"
                            if match['notify']:
                                notify = match['notify']
                
                system_prompt = f"""Você é um assistente especializado em análise de documentos jurídicos.
                         
                         !!! ATENÇÃO - INSTRUÇÕES CRÍTICAS E ABSOLUTAMENTE OBRIGATÓRIAS !!!
                         
                         VOCÊ DEVE OBRIGATORIAMENTE ENCONTRAR A ÚLTIMA MANIFESTAÇÃO DO PROMOTOR!
                         - Comece a busca pelas últimas 5 páginas do documento
                         - Use OCR se necessário
                         - APENAS em último caso pergunte ao usuário
                         
                         INFORMAÇÕES QUE VOCÊ DEVE EXTRAIR (TODAS SÃO OBRIGATÓRIAS):
                         
                         1. DA ÚLTIMA MANIFESTAÇÃO DO PROMOTOR:
                            - NÚMERO DA NF (XXXX.XXXXXXX/XXXX)
                            - PROMOTORIA DE JUSTIÇA
                            - NOME DO PROMOTOR(A)
                            - CRIME/ARTIGO
                            - RESUMO DA MANIFESTAÇÃO
                         
                         2. IDENTIFICAÇÃO DAS PARTES
                         3. ORIGEM DA NF
                         4. DATAS RELEVANTES
                         
                         ESTRUTURE A RESPOSTA EXATAMENTE ASSIM:
                         
                         RELATÓRIO DE PRÉ-ANÁLISE
                         ------------------------
                         Promotor(a): [Nome completo]
                         Manifestação: [Breve resumo]
                         
                         INFORMAÇÕES DETALHADAS
                         ---------------------
                         1. Número da NF: [XXXX.XXXXXXX/XXXX]
                         2. Promotoria: [Nome exato]
                         3. Crime/Artigo: [Descrição]
                         4. Partes:
                            - Vítima(s): [Nome, função]
                            - Investigado(s): [Nome, função]
                         5. Origem da NF: [Documento]
                         6. Datas Relevantes: [Lista]
                         
                         {rules_info if rules_info else ""}
                         
                         CONCLUSÃO
                         ---------
                         Ação: {action}
                         {f'Notificação: {notify}' if notify else ''}
                         """
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[{
                        "role": "system",
                        "content": system_prompt
                    }, {
                        "role": "user",
                        "content": text
                    }]
                )
                
                return message.content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    logger.warning(f"Erro na tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Erro após {max_retries} tentativas: {str(e)}")
                    raise

    def _consolidate_analyses_in_parts(self, analyses: List[str], batch_size: int = 3) -> str:
        """Consolida as análises em partes menores para respeitar o limite de tokens."""
        if len(analyses) <= batch_size:
            return self._consolidate_batch(analyses)
        
        # Divide as análises em batches menores
        batches = [analyses[i:i + batch_size] for i in range(0, len(analyses), batch_size)]
        intermediate_results = []
        
        # Consolida cada batch
        for batch in batches:
            consolidated_batch = self._consolidate_batch(batch)
            intermediate_results.append(consolidated_batch)
        
        # Consolida os resultados intermediários
        return self._consolidate_batch(intermediate_results)
    
    def _consolidate_batch(self, analyses: List[str]) -> str:
        """Consolida um batch de análises."""
        consolidated_input = "\n\n".join([
            f"=== Análise {i+1} ===\n{analysis}"
            for i, analysis in enumerate(analyses)
        ])
        
        system_prompt = """Você é um assistente especializado em análise de documentos jurídicos.
        
        ATENÇÃO - INSTRUÇÕES CRÍTICAS:
        1. Consolide as análises em um relatório estruturado começando com:
           
           RELATÓRIO DE PRÉ-ANÁLISE
           ------------------------
           Promotor(a): [Nome completo]
           Manifestação: [Breve resumo da última manifestação]
           
           1. Número da NF: [XXXX.XXXXXXX/XXXX]
           2. Promotoria: [Nome exato]
           3. Crime/Artigo: [Descrição completa]
           4. Origem: [Documento que gerou a NF]
           5. Partes Envolvidas:
              - Vítima(s): [Nome e função]
              - Investigado(s): [Nome e função]
           
           ANÁLISE DETALHADA
           ----------------
           [Demais informações relevantes]
           
           REGRAS E EXCEÇÕES ENCONTRADAS
           ----------------------------
           [Lista detalhada]
           
           CONCLUSÃO
           ---------
           Ação: [CADASTRAR_PORTAL ou NÃO_CADASTRAR]
           Notificação: [email se aplicável]
           
        2. SEMPRE inclua o nome do Promotor e um resumo de sua manifestação no início
        3. Se encontrar regras/exceções (ex: Diretor do IMESC, IMESC), indique claramente
        4. Se houver alerta de desobediência, destaque no relatório"""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": f"Consolide as seguintes análises em um único relatório estruturado:\n\n{consolidated_input}"
            }]
        )
        
        return message.content

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
            
            # Ajusta o tamanho dos chunks baseado no modo
            if is_large_file:
                self.pdf_splitter.max_tokens_per_chunk = 32000  # Chunks maiores para menos requisições
            else:
                self.pdf_splitter.max_tokens_per_chunk = 16000  # Chunks menores para melhor precisão
            
            # Divide o PDF em chunks
            chunk_paths = self.pdf_splitter.split_pdf(file_path)
            logger.info(f"Documento dividido em {len(chunk_paths)} partes")
            
            # Analisa cada chunk
            chunk_analyses = []
            
            for i, chunk_path in enumerate(chunk_paths, 1):
                logger.info(f"Analisando parte {i} de {len(chunk_paths)}")
                pdf_reader = PDFReader()
                
                if not pdf_reader.load_pdf(chunk_path):
                    logger.error(f"Erro ao carregar chunk {i}")
                    continue
                
                text = pdf_reader.get_text()
                if not text.strip():
                    logger.warning(f"Chunk {i} está vazio, pulando...")
                    continue
                
                pdf_reader.close()
                pdf_reader = None
                
                # Adiciona delay para arquivos grandes para evitar rate limits
                if is_large_file:
                    time.sleep(2)  # 2 segundos entre chamadas
                
                analysis = self._analyze_chunk(text, is_last_chunk=(i == len(chunk_paths)))
                chunk_analyses.append(analysis)
            
            if not chunk_analyses:
                raise ValueError("Nenhum texto válido encontrado no documento")
            
            # Consolida as análises em partes
            consolidated_analysis = self._consolidate_analyses_in_parts(chunk_analyses)
            
            # Gera recomendações
            recommendations = self._generate_recommendations(consolidated_analysis)
            
            return {
                'analysis': consolidated_analysis,
                'recommendations': recommendations,
                'metadata': {
                    'timestamp': str(datetime.now()),
                    'model': self.model,
                    'document_path': file_path,
                    'parts_analyzed': len(chunk_paths)
                }
            }
            
        except Exception as e:
            logger.error(f"Erro na análise do documento: {str(e)}")
            raise
        finally:
            if pdf_reader:
                pdf_reader.close()
            self.pdf_splitter.cleanup()

    def _generate_recommendations(self, analysis: str) -> List[str]:
        """Gera recomendações baseadas na análise do documento."""
        try:
            system_prompt = "Gere recomendações práticas baseadas na análise do documento."
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": f"Com base nesta análise, quais são as recomendações principais?\n\n{analysis}"
                }]
            )
            
            recommendations = message.content.split('\n')
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return []

    def ask_question(self, document_text: str, question: str) -> str:
        """Permite fazer perguntas interativas sobre o documento."""
        try:
            system_prompt = """Você é um assistente especializado em análise de documentos jurídicos.
            Responda à pergunta do usuário com base no conteúdo do documento fornecido.
            Seja preciso e objetivo em suas respostas, citando partes relevantes do documento quando necessário."""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": f"Documento analisado:\n{document_text}\n\nPergunta do usuário:\n{question}"
                }]
            )
            
            return message.content
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            raise