import os
import logging
from typing import Dict, List, Union, Optional, Any
import yaml
from datetime import datetime
import httpx
from src.ai_analyzer.legal_knowledge_base import LegalKnowledgeBase
from src.pdf_processor.pdf_reader import PDFReader
from src.pdf_processor.pdf_splitter import PDFSplitter
import pytesseract
from PIL import Image
import pdf2image
import io
import re
from src.rules_engine.rules_manager import RulesManager

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

logger = logging.getLogger(__name__)

class MixtralAnalyzer:
    def __init__(self):
        """Inicializa o analisador."""
        self.context = None
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configuração do cliente HTTP com proxy se necessário
        proxy = os.getenv('HTTPS_PROXY')
        if proxy:
            self.client = httpx.Client(proxies={"https": proxy}, timeout=600)  # 10 minutos
        else:
            self.client = httpx.Client(timeout=600)  # 10 minutos
        
        self.knowledge_base = LegalKnowledgeBase()
        self.pdf_splitter = PDFSplitter(max_tokens_per_chunk=16000)  # Metade do limite do Mixtral
        
        # Configura o gerenciador de regras com o arquivo correto
        rules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "rules", "dispatch_rules.yaml")
        self.rules_manager = RulesManager(rules_path)
        
        self.initialize_knowledge()
        
        # Inicializa variáveis de estado
        self.current_context = ""
        self.manifestacoes = []
        self.ultima_manifestacao = None
        self.found_keywords = {
            'imesc': [],
            'desobediencia': [],
            'crime': [],
            'nf': [],
            'promotoria': [],
            'complete_rules': []  # Lista para armazenar regras completas encontradas
        }
        self.navegacao_manual = False
        self.specific_page = None

    def initialize_knowledge(self):
        """Inicializa a base de conhecimento jurídico e policial."""
        logger.info("Inicializando base de conhecimento...")
        self.knowledge_base.initialize()

    def set_context(self, context: str):
        """Define o contexto para análise."""
        self.context = context

    def analyze_document(self, chunk_paths: List[str], additional_context: str = None) -> Dict:
        """
        Analisa o documento completo e retorna as informações extraídas.
        """
        try:
            # Limpa o contexto anterior
            self.manifestacoes = []
            self.ultima_manifestacao = None
            self.found_keywords = {
                'imesc': [],
                'desobediencia': [],
                'crime': [],
                'nf': [],
                'promotoria': []
            }
            
            # Processa os chunks do documento
            texto_completo = ""
            for chunk_path in chunk_paths:
                with open(chunk_path, 'r', encoding='utf-8') as f:
                    texto_completo += f.read() + "\n"
            
            # Mantém o texto completo no contexto
            self.current_context = texto_completo
            
            if additional_context:
                texto_completo += f"\nContexto Adicional:\n{additional_context}"
                # Se tem contexto adicional, considera ele como última manifestação
                self.ultima_manifestacao = {
                    'texto': additional_context,
                    'pagina_inicial': 1,
                    'pagina_final': 1,
                    'assinatura': None
                }
            else:
                # Se não tem contexto adicional, extrai manifestações normalmente
                self.manifestacoes = self._extrair_manifestacoes(texto_completo)
                self.ultima_manifestacao = self._encontrar_ultima_manifestacao_promotor(self.manifestacoes)
            
            if not self.ultima_manifestacao:
                return {
                    "success": False,
                    "error": "Não foi possível identificar uma manifestação de Promotor no documento. Use o botão Complete para informar a página correta.",
                    "needs_confirmation": True
                }
            
            # Procura palavras-chave priorizando a última manifestação
            logger.info("Iniciando busca de palavras-chave no texto completo")
            self._procurar_palavras_chave(texto_completo, self.ultima_manifestacao)
            
            # Carrega as regras de pré-análise
            logger.info("Carregando regras de pré-análise")
            regras = self.rules_manager.get_rules('pre_analysis')
            if not regras:
                logger.warning("Nenhuma regra de pré-análise encontrada")
                regras = []
            
            # Formata as regras para o prompt
            regras_formatadas = "\n".join([
                f"Regra {regra.get('id', 'N/A')}: {regra.get('descricao', 'Sem descrição')}"
                for regra in regras
            ])
            
            # Extrai informações críticas da última manifestação
            info_criticas = self._extrair_informacoes_criticas(self.ultima_manifestacao['texto'])
            
            # Se não encontrou na última manifestação, busca no texto completo
            if not info_criticas['nf'] or not info_criticas['promotoria']:
                info_complementar = self._extrair_informacoes_criticas(texto_completo)
                if not info_criticas['nf']:
                    info_criticas['nf'] = info_complementar['nf']
                if not info_criticas['promotoria']:
                    info_criticas['promotoria'] = info_complementar['promotoria']
            
            # Prepara o input consolidado com contexto mais rico
            consolidated_input = f"""Analise a última manifestação do Promotor e as palavras-chave encontradas para gerar um relatório detalhado.

ÚLTIMA MANIFESTAÇÃO DO PROMOTOR:
{self.ultima_manifestacao['texto']}

INFORMAÇÕES CRÍTICAS:
NF: {info_criticas.get('nf', 'Não encontrada')}
Promotoria: {info_criticas.get('promotoria', 'Não encontrada')}

PALAVRAS-CHAVE ENCONTRADAS:
- Na última manifestação:
{self._formatar_palavras_chave_manifestacao()}

- No documento completo:
{self._formatar_palavras_chave_complementares()}

{regras_formatadas}

IMPORTANTE: 
1. Se uma regra tiver todas suas palavras-chave encontradas na última manifestação do Promotor, 
   você DEVE usar EXATAMENTE a ação definida na regra: "enviar e-mail ao DP do inquérito policial"
2. SEMPRE responda em português.
3. NUNCA modifique a ação definida na regra.
4. NÃO CRIE uma nova ação ou recomendação - use EXATAMENTE a ação da regra.

Por favor:
1. Analise o texto e identifique palavras-chave que correspondam a qualquer regra cadastrada
2. Se encontrar uma correspondência COMPLETA com uma regra (todas as palavras-chave da condição) na última manifestação do Promotor:
   - Use EXATAMENTE a ação definida na regra: "enviar e-mail ao DP do inquérito policial"
   - NÃO crie uma nova ação ou recomendação
3. Se não encontrar correspondência completa na última manifestação:
   - Busque no documento completo
   - Se encontrar correspondência completa, aplique a ação da regra
   - Se encontrar apenas algumas palavras-chave, recomende busca minuciosa
4. Forneça um relatório detalhado com:
   - Nome COMPLETO do(a) último(a) Promotor(a) que se manifestou
   - Resumo DETALHADO da última manifestação
   - Número da NF: USE EXATAMENTE o valor encontrado acima
   - Promotoria de Justiça: USE EXATAMENTE o valor encontrado acima
   - Crime específico (Artigo do CP) e detalhes
   - Nome e profissão da vítima ou investigado
   - Datas relevantes do BO/documento
   - Recomendação: use EXATAMENTE a ação da regra - "enviar e-mail ao DP do inquérito policial"
"""

            # Gera o relatório final
            messages = [
                {"role": "system", "content": self.knowledge_base.get_system_prompt()},
                {"role": "user", "content": consolidated_input}
            ]
            
            report = self._call_api(messages)
            
            return {
                "success": True,
                "report": report,
                "context": self.current_context,  # Retorna o texto completo no contexto
                "manifestacao": {
                    'pagina_inicial': self.ultima_manifestacao.get('pagina_inicial', 1),
                    'pagina_final': self.ultima_manifestacao.get('pagina_final', 1),
                    'assinatura': self.ultima_manifestacao.get('assinatura', '')
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _encontrar_ultima_manifestacao_promotor(self, manifestacoes: List[Dict]) -> Optional[Dict]:
        """Encontra a última manifestação assinada por um Promotor."""
        # Filtra manifestações com assinatura de promotor, priorizando assinaturas mais específicas
        manifestacoes_promotor = []
        for m in manifestacoes:
            if not m['assinatura']:
                continue
                
            assinatura = m['assinatura'].lower()
            # Prioriza assinaturas mais específicas (com nome ou cargo completo)
            if 'promotor' in assinatura and 'justiça' in assinatura:
                m['prioridade'] = 3
                manifestacoes_promotor.append(m)
            elif 'promotor' in assinatura:
                m['prioridade'] = 2
                manifestacoes_promotor.append(m)
            elif any(termo in assinatura for termo in ['mp', 'mpsp', 'pjsp']):
                m['prioridade'] = 1
                manifestacoes_promotor.append(m)
        
        # Adiciona log para debug
        logger.info(f"Manifestações de promotor encontradas: {len(manifestacoes_promotor)}")
        for m in manifestacoes_promotor:
            logger.info(f"Manifestação: Páginas {m['pagina_inicial']}-{m['pagina_final']}, "
                      f"Assinatura: {m['assinatura']}")
        
        # Primeiro tenta encontrar pela maior prioridade
        maior_prioridade = max((m['prioridade'] for m in manifestacoes_promotor), default=0)
        manifestacoes_prioritarias = [
            m for m in manifestacoes_promotor 
            if m['prioridade'] == maior_prioridade
        ]
        
        # Retorna a última manifestação da maior prioridade
        if manifestacoes_prioritarias:
            return max(manifestacoes_prioritarias, key=lambda m: m['pagina_final'])
        return None

    def _consolidar_texto(self, chunk_paths: List[str], additional_context: str = None) -> str:
        """
        Consolida o texto de todos os chunks em um único texto.
        """
        texto_completo = ""
        for chunk_path in chunk_paths:
            with open(chunk_path, 'r', encoding='utf-8') as f:
                texto_completo += f.read() + "\n"
        
        if additional_context:
            texto_completo += f"\nContexto Adicional:\n{additional_context}"
        
        return texto_completo

    def _analisar_palavras_chave_e_regras(self, texto_completo: str, ultima_manifestacao: Dict) -> Dict:
        """
        Realiza a análise de palavras-chave e aplicação de regras após confirmação do Promotor.
        """
        try:
            # Carrega as regras de pré-análise
            logger.info("Carregando regras de pré-análise")
            regras = self.rules_manager.get_rules('pre_analysis')
            if not regras:
                logger.warning("Nenhuma regra de pré-análise encontrada")
                return self._criar_relatorio_padrao(ultima_manifestacao)
            
            # Primeiro tenta encontrar todas as palavras-chave na manifestação do Promotor
            logger.info("Buscando palavras-chave na manifestação do Promotor")
            regras_manifestacao = self._buscar_palavras_chave(ultima_manifestacao['texto'], regras)
            
            # Se encontrou uma regra completa na manifestação do Promotor, usa ela
            regra_completa = next((r for r in regras_manifestacao if r['completa']), None)
            if regra_completa:
                logger.info("Regra completa encontrada na manifestação do Promotor")
                return self._criar_relatorio(regra_completa, ultima_manifestacao)
            
            # Se não encontrou regra completa, busca no documento todo
            logger.info("Buscando palavras-chave complementares no documento completo")
            regras_documento = self._buscar_palavras_chave(texto_completo, regras)
            
            # Usa a regra mais prioritária encontrada
            regras_ordenadas = self._ordenar_regras_por_prioridade(regras_documento)
            if regras_ordenadas:
                logger.info(f"Usando regra encontrada no documento completo: {regras_ordenadas[0]['regra'].get('id', 'sem id')}")
                return self._criar_relatorio(regras_ordenadas[0], ultima_manifestacao)
            
            # Se não encontrou nenhuma regra, usa a padrão
            logger.warning("Nenhuma regra encontrada, usando regra padrão")
            return self._criar_relatorio_padrao(ultima_manifestacao)
            
        except Exception as e:
            logger.error(f"Erro na análise de palavras-chave: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _buscar_palavras_chave(self, texto: str, regras: List[Dict]) -> List[Dict]:
        """
        Busca palavras-chave em um texto específico.
        """
        resultados = []
        for regra in regras:
            palavras_encontradas = []
            for palavra in regra['palavras_chave']:
                for variante in palavra.split('|'):
                    if variante.lower() in texto.lower():
                        # Extrai o contexto
                        indice = texto.lower().find(variante.lower())
                        inicio = max(0, texto.rfind('.', 0, indice) + 1)
                        fim = texto.find('.', indice)
                        if fim == -1:
                            fim = len(texto)
                        contexto = texto[inicio:fim].strip()
                        
                        palavras_encontradas.append({
                            'palavra': palavra,
                            'contexto': contexto
                        })
                        break
            
            if palavras_encontradas:
                resultados.append({
                    'regra': regra,
                    'palavras': palavras_encontradas,
                    'completa': len(palavras_encontradas) == len(regra['palavras_chave']),
                    'prioridade': regra.get('prioridade', 'baixa')
                })
        
        return resultados

    def _criar_relatorio(self, regra: Dict, ultima_manifestacao: Dict) -> Dict:
        """
        Cria o relatório final com base na regra encontrada.
        """
        return {
            'success': True,
            'report': self._gerar_report_llm(regra, ultima_manifestacao),
            'regra_aplicada': regra['regra'].get('id', 'padrao'),
            'acao': regra['regra'].get('acao', 'Encaminhar para análise manual'),
            'palavras_chave': [
                {
                    'palavra': p['palavra'],
                    'contexto': p['contexto']
                }
                for p in regra['palavras']
            ],
            'prioridade': regra['prioridade'],
            'completa': regra['completa'],
            'ultima_manifestacao': {
                'texto': ultima_manifestacao.get('texto', ''),
                'pagina': ultima_manifestacao.get('pagina', 0),
                'assinatura': ultima_manifestacao.get('assinatura', '')
            }
        }

    def _criar_relatorio_padrao(self, ultima_manifestacao: Dict) -> Dict:
        """
        Cria um relatório padrão quando nenhuma regra é encontrada.
        """
        regra_padrao = self._get_regra_padrao()
        return self._criar_relatorio(regra_padrao, ultima_manifestacao)

    def _gerar_report_llm(self, regra: Dict, ultima_manifestacao: Dict) -> str:
        """
        Gera o relatório usando o modelo de linguagem.
        """
        try:
            input_text = f"""
Última manifestação do Promotor:
{ultima_manifestacao.get('texto', '')}

Regra aplicada: {regra['regra'].get('id', 'padrao')}
Ação recomendada: {regra['regra'].get('acao', 'Encaminhar para análise manual')}

Palavras-chave encontradas:
{chr(10).join([f'- {p["palavra"]}: {p["contexto"]}' for p in regra['palavras']])}
"""
            messages = [
                {"role": "system", "content": self.knowledge_base.get_system_prompt()},
                {"role": "user", "content": input_text}
            ]
            
            return self._call_api(messages)
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório LLM: {str(e)}")
            return "Não foi possível gerar o relatório detalhado."

    def _ordenar_regras_por_prioridade(self, regras: List[Dict]) -> List[Dict]:
        """
        Ordena as regras por prioridade (alta, média, baixa) e completude.
        """
        def _get_prioridade_valor(prioridade: str) -> int:
            prioridade = prioridade.lower()
            if prioridade == 'alta':
                return 3
            elif prioridade == 'média' or prioridade == 'media':
                return 2
            return 1  # baixa ou qualquer outro valor
        
        return sorted(
            regras,
            key=lambda x: (
                _get_prioridade_valor(x['prioridade']),
                x['completa'],
                len(x['palavras'])
            ),
            reverse=True
        )

    def _get_regra_padrao(self) -> Dict:
        """
        Retorna a regra padrão para casos onde nenhuma regra é encontrada.
        """
        return {
            'regra': {
                'id': 'padrao',
                'descricao': 'Regra padrão - nenhuma regra específica encontrada',
                'acao': 'Encaminhar para análise manual',
                'prioridade': 'baixa'
            },
            'palavras': [],
            'completa': True,
            'prioridade': 'baixa'
        }

    def analyze_document_with_context(self, context: str) -> Dict:
        """
        Analisa um documento usando apenas o contexto fornecido.
        Retorna um dicionário com a análise completa.
        """
        try:
            # Prepara o input consolidado com as palavras-chave encontradas
            found_keywords = {
                'imesc': [],
                'desobediencia': [],
                'crime': [],
                'nf': [],
                'promotoria': []
            }
            
            # Procura palavras-chave no contexto
            imesc_matches = re.finditer(r'IMESC|Instituto\s+de\s+Medicina\s+Social\s+e\s+de\s+Criminologia', context, re.IGNORECASE)
            found_keywords['imesc'].extend(match.group(0) for match in imesc_matches)
            
            desobediencia_matches = re.finditer(r'desobediência|desobediencia|art(?:igo)?\s*\.?\s*330|330\s+do\s+CP', context, re.IGNORECASE)
            found_keywords['desobediencia'].extend(match.group(0) for match in desobediencia_matches)
            
            crime_matches = re.finditer(r'art(?:igo)?\s*\.?\s*\d+(?:\s*,\s*\d+)*(?:\s+do\s+CP)?', context, re.IGNORECASE)
            found_keywords['crime'].extend(match.group(0) for match in crime_matches)
            
            nf_matches = re.finditer(r'\d{4}\.\d{7}/\d{4}', context)
            found_keywords['nf'].extend(match.group(0) for match in nf_matches)
            
            promotoria_matches = re.finditer(r'\d+ª?\s*Promotoria\s+de\s+Justiça[^.]*', context, re.IGNORECASE)
            found_keywords['promotoria'].extend(match.group(0) for match in promotoria_matches)
            
            # Prepara o input consolidado
            consolidated_input = f"""
Palavras-chave encontradas:
- IMESC/Instituto: {', '.join(found_keywords['imesc']) if found_keywords['imesc'] else 'Não encontrado'}
- Desobediência/Art. 330: {', '.join(found_keywords['desobediencia']) if found_keywords['desobediencia'] else 'Não encontrado'}
- Artigos do CP: {', '.join(found_keywords['crime']) if found_keywords['crime'] else 'Não encontrado'}
- NF: {found_keywords['nf'][0] if found_keywords['nf'] else 'Não encontrado'}
- Promotoria: {found_keywords['promotoria'][0] if found_keywords['promotoria'] else 'Promotoria de Justiça de São Paulo'}

Conteúdo do documento:
{context}
"""
            # Gera o relatório final
            messages = [
                {"role": "system", "content": """Você é um assistente especializado em análise de documentos jurídicos.
                
                TAREFA 1 - RELATÓRIO:
                Gere um relatório padronizado com exatamente 7 itens sobre o documento analisado.
                
                DIRETRIZES DO RELATÓRIO:
                1. Use as palavras-chave encontradas no início do texto
                2. Para o item 3 (NF), use EXATAMENTE o valor encontrado
                3. Para o item 4 (Promotoria), use EXATAMENTE o valor encontrado
                4. Para o item 5 (Crime), use os artigos encontrados ou a última manifestação
                5. NUNCA retorne "Não identificado" para os itens 4 e 5
                
                O relatório deve conter:
                1. Nome COMPLETO do(a) último(a) Promotor(a) que se manifestou
                2. Resumo DETALHADO da última manifestação
                3. Número da NF no formato XXXX.XXXXXXX/XXXX
                4. Promotoria de Justiça que enviou a NF
                5. Crime específico (Artigo do CP) e detalhes
                6. Nome e profissão da vítima ou investigado
                7. Datas relevantes do BO/documento
                
                TAREFA 2 - RECOMENDAÇÃO:
                Após o relatório, analise se o documento se enquadra na seguinte regra:
                
                REGRA: Se encontrar IMESC (Instituto de Medicina Social e de Criminologia) E artigo 330 do CP (desobediência),
                a ação recomendada é encerrar a tarefa por e-mail ao DPPC.
                
                DIRETRIZES DA RECOMENDAÇÃO:
                1. Use as palavras-chave encontradas no início do texto
                2. Se encontrar IMESC E artigo 330/desobediência, recomende encerrar por e-mail
                3. Inclua as palavras-chave que fundamentaram a recomendação
                4. Indique o nível de confiança (95% se encontrar ambas as palavras-chave)"""},
                {"role": "user", "content": consolidated_input}
            ]
            
            response = self._send_request(messages)
            if not response:
                return {
                    "success": False,
                    "error": "Erro ao gerar relatório"
                }
            
            return {
                "success": True,
                "report": response,
                "context": consolidated_input
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao analisar documento: {str(e)}"
            }

    def answer_question(self, question: str, context: str = None) -> str:
        """Responde a uma pergunta do usuário sobre o documento analisado."""
        try:
            messages = [
                {"role": "system", "content": "Você é um assistente jurídico especializado em análise de documentos do Ministério Público. Responda às perguntas de forma clara e objetiva, baseando-se apenas no contexto fornecido."},
            ]
            
            if context:
                messages.append({"role": "user", "content": f"Contexto do documento:\n{context}\n\nPergunta: {question}"})
            else:
                messages.append({"role": "user", "content": f"Pergunta: {question}"})
            
            data = {
                "model": "mistral-medium",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = self.client.post(
                self.api_url,
                json=data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Erro ao fazer pergunta: {response.status_code} - {response.text}")
                return "Desculpe, não foi possível processar sua pergunta no momento."
                
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta."

    def _navegar_paginas(self, texto_completo: str) -> Dict:
        """Permite navegação manual pelas páginas do documento."""
        try:
            # Divide o texto em páginas
            paginas = re.split(r'\[PÁGINA\s+(\d+)\]', texto_completo)
            self.paginas = []
            
            # Organiza as páginas
            for i in range(1, len(paginas), 2):
                num_pagina = int(paginas[i])
                texto_pagina = paginas[i + 1].strip()
                self.paginas.append({
                    'numero': num_pagina,
                    'texto': texto_pagina
                })
            
            # Ordena as páginas pelo número
            self.paginas.sort(key=lambda x: x['numero'])
            
            # Inicializa o índice de navegação se necessário
            if not hasattr(self, 'current_page_index'):
                self.current_page_index = len(self.paginas) - 1  # Começa da última página
            
            # Se uma página específica foi solicitada
            if hasattr(self, 'specific_page') and self.specific_page is not None:
                # Encontra o índice da página solicitada
                for i, pagina in enumerate(self.paginas):
                    if pagina['numero'] == self.specific_page:
                        self.current_page_index = i
                        break
            
            # Garante que o índice está dentro dos limites
            self.current_page_index = max(0, min(self.current_page_index, len(self.paginas) - 1))
            
            # Pega a página atual
            pagina_atual = self.paginas[self.current_page_index]
            
            return {
                "success": True,
                "needs_confirmation": True,
                "page_text": pagina_atual['texto'],
                "message": f"Página {pagina_atual['numero']} ({self.current_page_index + 1} de {len(self.paginas)})",
                "current_page": pagina_atual['numero'],
                "current_index": self.current_page_index,
                "total_pages": len(self.paginas)
            }
            
        except Exception as e:
            logger.error(f"Erro na navegação de páginas: {str(e)}")
            return {
                "success": False,
                "error": f"Erro ao navegar páginas: {str(e)}",
                "needs_confirmation": True
            }

    def set_specific_page(self, page_number: int):
        """Ativa a navegação manual e define a página específica."""
        self.navegacao_manual = True
        self.specific_page = page_number
        self.current_page_index = page_number - 1  # Ajusta o índice para 0-based

    def _extrair_manifestacoes(self, texto: str) -> List[Dict]:
        """Extrai todas as manifestações do documento."""
        manifestacoes = []
        paginas = re.split(r'\[PÁGINA\s+(\d+)\]', texto)
        
        # Padrões para identificar manifestações
        inicio_patterns = [
            r'MANIFESTAÇÃO(?:\s+DO\s+MP)?',
            r'VISTO[S]?',
            r'MM\.?\s*(?:Juiz|Juíza)',
            r'MERITÍSSIMO',
            r'EXCELENTÍSSIMO',
            r'EXMO',
            r'COTA\s+(?:DO\s+)?M(?:INISTÉRIO)?\.?\s*P(?:ÚBLICO)?'
        ]
        
        assinatura_patterns = [
            r'Promotor[a]?\s+(?:de\s+)?[Jj]ustiça',
            r'Promotor[a]?\s+(?:de\s+)?[Jj]ustiça\s+[Ss]ubstitut[oa]',
            r'PJSP',
            r'MP(?:SP)?'
        ]
        
        # Combina os padrões com flag case-insensitive no início
        inicio_pattern = '|'.join(f'(?:{p})' for p in inicio_patterns)
        inicio_pattern = f'(?i)(?:{inicio_pattern})'
        
        assinatura_pattern = '|'.join(f'(?:{p})' for p in assinatura_patterns)
        assinatura_pattern = f'(?i)(?:{assinatura_pattern})'
        
        # Variáveis para controlar a manifestação atual
        manifestacao_atual = None
        
        # Processa cada página
        for i in range(1, len(paginas), 2):
            num_pagina = int(paginas[i])
            texto_pagina = paginas[i + 1].strip()
            
            # Procura por início de manifestação
            inicio_matches = list(re.finditer(inicio_pattern, texto_pagina))
            assinatura_matches = list(re.finditer(assinatura_pattern, texto_pagina))
            
            # Se encontrou início de manifestação
            if inicio_matches:
                # Se já tinha uma manifestação em andamento, fecha ela
                if manifestacao_atual:
                    manifestacao_atual['pagina_final'] = num_pagina - 1
                    manifestacoes.append(manifestacao_atual)
                
                # Inicia nova manifestação
                pos_inicio = inicio_matches[0].start()
                manifestacao_atual = {
                    'pagina_inicial': num_pagina,
                    'pagina_final': num_pagina,
                    'texto': texto_pagina[pos_inicio:],
                    'assinatura': None
                }
            
            # Se tem manifestação em andamento
            elif manifestacao_atual:
                # Adiciona o texto da página
                manifestacao_atual['texto'] += f"\n{texto_pagina}"
                manifestacao_atual['pagina_final'] = num_pagina
            
            # Se encontrou assinatura
            if assinatura_matches and manifestacao_atual:
                # Pega a última assinatura da página
                manifestacao_atual['assinatura'] = assinatura_matches[-1].group()
                manifestacoes.append(manifestacao_atual)
                manifestacao_atual = None
        
        # Se sobrou manifestação em andamento, fecha ela
        if manifestacao_atual:
            manifestacoes.append(manifestacao_atual)
        
        # Adiciona log para debug
        logger.info(f"Manifestações encontradas: {len(manifestacoes)}")
        for m in manifestacoes:
            logger.info(f"Manifestação: Páginas {m['pagina_inicial']}-{m['pagina_final']}, Assinatura: {m['assinatura']}")
        
        return manifestacoes

    def _extrair_informacoes_criticas(self, texto: str) -> Dict[str, Any]:
        """
        Extrai informações críticas do texto usando regex otimizado.
        """
        info = {
            'nf': None,
            'promotoria': None,
            'promotor': None,
            'crime': None,
            'vitima': None,
            'datas_relevantes': []
        }
        
        # Padrões regex aprimorados
        padroes = {
            'nf': [
                r'NF\s*n[°º]\s*(\d{4}\.\d{7}/\d{4})',
                r'NF\s*n[°º]\s*(\d{4}/\d{7})',
                r'NF\s*(?:número)?\s*(\d{4}\.\d{7}/\d{4})',
                r'(?:^|\s)(\d{4}\.\d{7}/\d{4})'
            ],
            'promotoria': [
                r'(\d+[ªa°º]\s*Promotoria\s+de\s+Justiça\s+Criminal)',
                r'(\d+[ªa°º]\s*Promotoria\s+de\s+Justiça(?:\s+Criminal)?)',
                r'((?:\d+[ªa°º]\s*)?Promotoria\s+de\s+Justiça\s+Criminal)',
                r'(\d+[ªa°º]\s*PJ(?:\s+Criminal)?)'
            ]
        }

        # Busca cada tipo de informação
        for tipo, lista_padroes in padroes.items():
            for padrao in lista_padroes:
                match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
                if match and match.groups():
                    valor = match.group(1).strip()
                    if tipo == 'nf' and not re.match(r'\d{4}\.\d{7}/\d{4}', valor):
                        continue  # Pula se não estiver no formato correto
                    info[tipo] = valor
                    break

        return info

    def _processar_manifestacao(self, texto: str, pagina: int) -> Dict[str, Any]:
        """
        Processa uma manifestação identificada, extraindo todas as informações relevantes.
        """
        manifestacao = {
            'texto': texto,
            'pagina': pagina,
            'info': self._extrair_informacoes_criticas(texto, pagina)
        }
        
        # Adiciona as informações encontradas aos keywords
        if manifestacao['info']['nf']:
            self.found_keywords['nf'] = [{'keyword': manifestacao['info']['nf'], 'in_ultima_manifestacao': True}]
        if manifestacao['info']['promotoria']:
            self.found_keywords['promotoria'] = [{'keyword': manifestacao['info']['promotoria'], 'in_ultima_manifestacao': True}]
        
        return manifestacao

    def _identificar_manifestacoes(self, texto_completo: str) -> None:
        """
        Identifica todas as manifestações no documento.
        """
        paginas = self._extrair_paginas(texto_completo)
        manifestacoes = []
        
        for pagina, texto in paginas.items():
            # Verifica se é uma manifestação do promotor
            if re.search(r'promotor[a]?\s+de\s+justiça', texto, re.IGNORECASE):
                manifestacao = self._processar_manifestacao(texto, pagina)
                manifestacoes.append(manifestacao)
        
        self.manifestacoes = manifestacoes
        if manifestacoes:
            self.ultima_manifestacao = manifestacoes[-1]
            logger.info(f"Manifestação: Páginas {self.ultima_manifestacao['pagina']}-{self.ultima_manifestacao['pagina']}, " + 
                       f"Assinatura: {self.ultima_manifestacao['info']['promotor'] if self.ultima_manifestacao['info']['promotor'] else 'mp'}")
        
    def _procurar_palavras_chave(self, texto_completo: str, ultima_manifestacao: Dict) -> None:
        """
        Procura palavras-chave priorizando a última manifestação do promotor.
        """
        logger.info("Iniciando busca detalhada de palavras-chave")
        
        # Primeiro busca na última manifestação do Promotor
        logger.info("Buscando palavras-chave na última manifestação do Promotor")
        if ultima_manifestacao and 'texto' in ultima_manifestacao:
            self._buscar_palavras_chave_em_texto(ultima_manifestacao['texto'], True)
        
        # Se não encontrou todas as palavras-chave de nenhuma regra, busca no texto completo
        logger.info("Buscando palavras-chave complementares no texto completo")
        self._buscar_palavras_chave_em_texto(texto_completo, False)

    def _buscar_palavras_chave_em_texto(self, texto: str, eh_ultima_manifestacao: bool) -> None:
        """
        Busca palavras-chave em um texto específico.
        """
        # Carrega todas as regras
        todas_regras = {}
        for tipo in ['pre_analysis', 'final_output', 'alerts', 'exceptions']:
            try:
                regras = self.rules_manager.get_rules(tipo)
                todas_regras[tipo] = regras if regras else []
            except Exception as e:
                logger.error(f"Erro ao carregar regras do tipo {tipo}: {str(e)}")
                todas_regras[tipo] = []

        # Para cada tipo de regra
        for tipo, regras in todas_regras.items():
            for regra in regras:
                # Verifica se todas as palavras-chave da regra estão presentes
                if 'keywords' in regra:
                    palavras_encontradas = []
                    for keyword in regra['keywords']:
                        if keyword.lower() in texto.lower():
                            palavras_encontradas.append(keyword)
                            # Registra a palavra-chave encontrada
                            for categoria in self.found_keywords.keys():
                                if categoria != 'complete_rules':  # Não adiciona à lista de regras completas
                                    if keyword.lower() in texto.lower():
                                        self.found_keywords[categoria].append({
                                            'keyword': keyword,
                                            'in_ultima_manifestacao': eh_ultima_manifestacao,
                                            'rule_id': regra.get('id'),
                                            'rule_type': tipo,
                                            'action': regra.get('action')
                                        })
                    
                    # Se todas as palavras-chave foram encontradas
                    if len(palavras_encontradas) == len(regra['keywords']):
                        logger.info(f"Regra completa encontrada - ID: {regra.get('id')}, Tipo: {tipo}")
                        # Se for na última manifestação, adiciona à lista de regras completas
                        if eh_ultima_manifestacao:
                            self.found_keywords['complete_rules'].append({
                                'rule_id': regra.get('id'),
                                'rule_type': tipo,
                                'action': regra.get('action'),
                                'keywords': palavras_encontradas
                            })

    def _extrair_texto_pagina(self, texto_completo: str, pagina: int) -> Optional[str]:
        """Extrai o texto de uma página específica."""
        try:
            linhas = texto_completo.split('\n')
            texto_pagina = ""
            dentro_pagina = False
            
            for linha in linhas:
                if f"FL. {pagina}" in linha:
                    dentro_pagina = True
                elif f"FL. {pagina + 1}" in linha:
                    dentro_pagina = False
                
                if dentro_pagina:
                    texto_pagina += linha + "\n"
            
            return texto_pagina
        except Exception as e:
            logger.error(f"Erro ao extrair texto da página {pagina}: {str(e)}")
            return None

    def _formatar_palavras_chave_manifestacao(self) -> str:
        """Formata as palavras-chave encontradas na última manifestação."""
        resultado = []
        for categoria, palavras in self.found_keywords.items():
            if categoria == 'complete_rules':  # Pula a chave especial
                continue
            palavras_manifestacao = [p['keyword'] for p in palavras if isinstance(p, dict) and p.get('in_ultima_manifestacao')]
            if palavras_manifestacao:
                resultado.append(f"{categoria}: {', '.join(palavras_manifestacao)}")
        return "\n".join(resultado) if resultado else "Nenhuma palavra-chave encontrada na última manifestação"

    def _formatar_palavras_chave_complementares(self) -> str:
        """Formata as palavras-chave encontradas no resto do documento."""
        resultado = []
        for categoria, palavras in self.found_keywords.items():
            if categoria == 'complete_rules':  # Pula a chave especial
                continue
            palavras_complementares = [p['keyword'] for p in palavras if isinstance(p, dict) and not p.get('in_ultima_manifestacao')]
            if palavras_complementares:
                resultado.append(f"{categoria}: {', '.join(palavras_complementares)}")
        return "\n".join(resultado) if resultado else "Nenhuma palavra-chave complementar encontrada"

    def _call_api(self, messages: List[Dict], max_tokens: int = 4000) -> str:
        """Faz a chamada para a API da Mistral."""
        try:
            data = {
                "model": "mistral-medium",
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.3,
                "top_p": 0.7,
                "random_seed": 42
            }
            
            response = self.client.post(
                self.api_url,
                json=data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"Erro na API: {response.status_code} - {response.text}")
            
        except Exception as e:
            logger.error(f"Erro na chamada da API: {str(e)}")
            raise

    def _send_request(self, messages: List[Dict]) -> str:
        """Faz a chamada para a API da Mistral."""
        try:
            data = {
                "model": "mistral-medium",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = self.client.post(
                self.api_url,
                headers=self.headers,
                json=data,
                timeout=300
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                logger.error(f"Erro ao fazer pergunta: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            return ""
