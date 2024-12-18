import os
import logging
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from typing import Dict, List, Optional
import yaml
import re
from datetime import datetime
from src.knowledge_base.legal_knowledge import LegalKnowledgeBase
from src.pdf_processor.pdf_reader import PDFReader

logger = logging.getLogger(__name__)

class MistralAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = MistralClient(api_key=self.api_key)
        self.knowledge_base = LegalKnowledgeBase()
        self.pdf_reader = PDFReader()
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
    
    def process_document(self, file_path: str) -> Dict:
        """Processa o documento PDF e retorna a análise estruturada."""
        # Carrega e processa o PDF
        if not self.pdf_reader.load_pdf(file_path):
            raise ValueError("Erro ao carregar o arquivo PDF")
        
        text = self.pdf_reader.get_text()
        
        # Extrai campos usando os padrões definidos nas regras
        fields_config = {
            'numero_noticia_fato': [pattern for item in self.rules['scraping_items'] 
                                  if item['nome'] == 'numero_noticia_fato' 
                                  for pattern in item['padroes']],
            'orgao_origem': [pattern for item in self.rules['scraping_items'] 
                           if item['nome'] == 'orgao_origem' 
                           for pattern in item['padroes']],
            'sujeito_ativo': [pattern for item in self.rules['scraping_items'] 
                            if item['nome'] == 'sujeito_ativo' 
                            for pattern in item['padroes']],
            'sujeito_passivo': [pattern for item in self.rules['scraping_items'] 
                              if item['nome'] == 'sujeito_passivo' 
                              for pattern in item['padroes']],
            'boletim_ocorrencia': [pattern for item in self.rules['scraping_items'] 
                                 if item['nome'] == 'boletim_ocorrencia' 
                                 for pattern in item['padroes']],
            'local_fatos': [pattern for item in self.rules['scraping_items']
                          if item['nome'] == 'local_fatos'
                          for pattern in item['padroes']],
            'tipo_penal': [pattern for item in self.rules['scraping_items']
                         if item['nome'] == 'tipo_penal'
                         for pattern in item['padroes']]
        }
        
        basic_info = self.pdf_reader.extract_fields(fields_config)
        
        # Enriquece a análise com conhecimento jurídico
        enriched_info = self._enrich_with_legal_knowledge(basic_info)
        
        # Análise específica baseada nas regras
        analysis_result = self._analyze_with_rules(text, enriched_info)
        
        # Determina o método de conclusão (portal ou email)
        conclusion = self._determine_conclusion_method(analysis_result)
        
        return {
            "text": text,
            "basic_info": enriched_info,
            "analysis": analysis_result,
            "conclusion": conclusion,
            "metadata": self.pdf_reader.get_metadata()
        }
    
    def _enrich_with_legal_knowledge(self, basic_info: Dict) -> Dict:
        """Enriquece as informações básicas com conhecimento jurídico."""
        enriched = basic_info.copy()
        
        # Adiciona informações sobre departamentos policiais
        if 'departamento' in basic_info:
            dep_info = self.knowledge_base.get_department_info(basic_info['departamento'])
            if dep_info:
                enriched['departamento_info'] = dep_info
        
        # Adiciona informações sobre legislação
        if 'enquadramento_legal' in basic_info:
            legal_info = self.knowledge_base.get_legal_info('penal')  # ou área específica
            if legal_info:
                enriched['legislacao_info'] = legal_info
        
        return enriched
    
    def _analyze_with_rules(self, text: str, basic_info: Dict) -> Dict:
        """Analisa o documento aplicando as regras específicas."""
        # Prepara o prompt com o conhecimento jurídico relevante
        knowledge_context = self._get_relevant_knowledge(basic_info)
        
        # Analisa o desfecho da manifestação do Promotor
        desfecho = self._analyze_promotor_decision(text, basic_info)
        
        messages = [
            ChatMessage(role="system", content=f"""Você é um assistente especializado em análise de documentos jurídicos.
            Use o seguinte conhecimento jurídico e policial para sua análise:
            {knowledge_context}
            
            Foque sua análise nos seguintes pontos cruciais:
            1. Assunto principal da Notícia de Fato
            2. Origem da notícia/denúncia
            3. Sujeitos ativo e passivo
            4. Local e data dos fatos (especialmente do BO)
            5. Legislação aplicável e tipo penal
            6. Última manifestação do Promotor e seu desfecho
            7. Necessidade de encaminhamento a departamento especializado
            
            {desfecho['context'] if desfecho else ''}
            
            Forneça uma análise estruturada e objetiva."""),
            ChatMessage(role="user", content=f"Documento:\n\n{text}")
        ]

        response = self.client.chat(
            model="mistral-medium",
            messages=messages
        )

        # Processa a resposta do modelo
        analysis = self._process_llm_response(response.choices[0].message.content)
        
        # Adiciona o desfecho analisado
        if desfecho:
            analysis['desfecho'] = desfecho
        
        return analysis
    
    def _analyze_promotor_decision(self, text: str, basic_info: Dict) -> Optional[Dict]:
        """Analisa especificamente a decisão/manifestação do Promotor."""
        if 'ultima_manifestacao_promotor' not in basic_info:
            return None
            
        manifestacao = basic_info['ultima_manifestacao_promotor']
        
        # Verifica assinatura digital
        tem_assinatura = bool(basic_info.get('assinatura_digital'))
        
        # Analisa o tipo de decisão
        decisao = {
            'texto': manifestacao,
            'tem_assinatura_digital': tem_assinatura,
            'tipo': None,
            'encaminhamento': None
        }
        
        # Identifica o tipo de decisão
        if re.search(r'instauração\s*(?:de)?\s*(?:inquérito|IP)', manifestacao, re.IGNORECASE):
            decisao['tipo'] = 'instauracao_ip'
        elif re.search(r'arquiv(?:o|amento)', manifestacao, re.IGNORECASE):
            decisao['tipo'] = 'arquivamento'
        
        # Identifica encaminhamento específico
        match_encaminhamento = re.search(r'(?:remetam-se|encaminhem-se)\s*(?:os\s*autos)?\s*(?:à|ao|para)\s*([^,\n]+)', manifestacao, re.IGNORECASE)
        if match_encaminhamento:
            decisao['encaminhamento'] = match_encaminhamento.group(1).strip()
        
        return decisao
    
    def _determine_conclusion_method(self, analysis: Dict) -> Dict:
        """Determina se o documento deve ser processado via portal ou email."""
        # Verifica se é caso para departamento especializado
        if self._is_specialized_department_case(analysis):
            return {
                "method": "email",
                "department": analysis.get("departamento_especializado"),
                "reason": "Caso para departamento especializado",
                "alerts": self._get_email_alerts(analysis)
            }
        
        # Verifica se é caso fora da capital
        if self._is_outside_capital(analysis):
            return {
                "method": "email",
                "department": "DEINTER",
                "reason": "Local dos fatos fora da capital",
                "alerts": self._get_email_alerts(analysis)
            }
        
        # Caso padrão: cadastro no portal
        return {
            "method": "portal",
            "reason": "Caso padrão para cadastro no portal",
            "alerts": self._get_portal_alerts(analysis)
        }

    def _get_email_alerts(self, analysis: Dict) -> List[str]:
        """Gera alertas específicos para envio por email."""
        alerts = []
        
        # Verifica se tem todas as informações necessárias
        if not analysis.get("departamento_especializado"):
            alerts.append("Atenção: Departamento especializado não identificado claramente")
        
        if not analysis.get("tipo_penal"):
            alerts.append("Atenção: Tipo penal não identificado")
            
        if not analysis.get("local_fatos"):
            alerts.append("Atenção: Local dos fatos não identificado")
            
        return alerts

    def _get_portal_alerts(self, analysis: Dict) -> List[str]:
        """Gera alertas específicos para cadastro no portal."""
        alerts = []
        
        # Verifica informações essenciais para o portal
        required_fields = {
            "numero_noticia_fato": "Número da Notícia de Fato",
            "orgao_origem": "Órgão de origem",
            "data_fato": "Data do fato",
            "local_fato": "Local do fato",
            "tipo_penal": "Tipo penal"
        }
        
        for field, description in required_fields.items():
            if not analysis.get(field):
                alerts.append(f"Atenção: {description} não identificado")
                
        # Alertas específicos do portal
        if analysis.get("tipo_penal") and "171" in analysis.get("tipo_penal"):
            alerts.append("Atenção: Para casos de estelionato, verificar se há prejuízo financeiro")
            
        return alerts

    def _is_specialized_department_case(self, analysis: Dict) -> bool:
        """Verifica se o caso deve ser encaminhado a departamento especializado."""
        if not analysis.get('tipo_penal'):
            return False
            
        tipo_penal = analysis['tipo_penal'].lower()
        
        # Verifica cada departamento especializado
        for dep in self.rules['regras_analise']['departamentos_especializados']:
            # Verifica crimes
            if 'crimes' in dep and any(crime in tipo_penal for crime in dep['crimes']):
                return True
                
            # Verifica leis específicas
            if 'leis' in dep and any(lei.lower() in tipo_penal for lei in dep['leis']):
                return True
                
            # Verifica artigos do CP
            if 'artigos_cp' in dep:
                for artigo in dep['artigos_cp']:
                    if re.search(f"art(?:igo)?\\s*{artigo}\\s*(?:do)?\\s*(?:CP|Código\\s*Penal)", tipo_penal, re.IGNORECASE):
                        return True
        
        return False
    
    def _is_outside_capital(self, analysis: Dict) -> bool:
        """Verifica se o local dos fatos é fora da capital."""
        if not analysis.get('local_fatos'):
            return False
            
        local = analysis['local_fatos'].lower()
        
        # Lista de termos que indicam local fora da capital
        termos_interior = [
            'interior', 'grande são paulo', 'região metropolitana',
            'campinas', 'santos', 'são josé dos campos', 'ribeirão preto',
            'sorocaba', 'guarulhos', 'osasco', 'barueri'
        ]
        
        return any(termo in local for termo in termos_interior)
    
    def _get_relevant_knowledge(self, basic_info: Dict) -> str:
        """Obtém conhecimento jurídico relevante para o contexto."""
        relevant_info = []
        
        # Busca informações relevantes na base de conhecimento
        if 'crime' in basic_info:
            results = self.knowledge_base.search(basic_info['crime'])
            for result in results:
                relevant_info.append(f"Informação sobre {result['tipo']}: {result['info']}")
        
        if 'departamento' in basic_info:
            dep_info = self.knowledge_base.get_department_info(basic_info['departamento'])
            if dep_info:
                relevant_info.append(f"Informação sobre departamento: {dep_info}")
        
        return "\n".join(relevant_info)
    
    def _process_llm_response(self, response: str) -> Dict:
        """Processa a resposta do LLM em um formato estruturado."""
        # Implementa o processamento da resposta
        return {}
    
    def ask_question(self, text: str, question: str) -> str:
        """Permite fazer perguntas específicas sobre o documento."""
        # Obtém conhecimento relevante para a pergunta
        relevant_knowledge = self._get_relevant_knowledge_for_question(question)
        
        messages = [
            ChatMessage(role="system", content=f"""Você é um assistente especializado em análise de documentos jurídicos.
            Use o seguinte conhecimento jurídico e policial para sua resposta:
            {relevant_knowledge}
            
            Responda à pergunta do usuário com base no documento fornecido.
            Seja preciso e objetivo, citando as partes relevantes do documento que fundamentam sua resposta."""),
            ChatMessage(role="user", content=f"Documento:\n\n{text}\n\nPergunta: {question}")
        ]

        response = self.client.chat(
            model="mistral-medium",
            messages=messages
        )

        return response.choices[0].message.content
    
    def _get_relevant_knowledge_for_question(self, question: str) -> str:
        """Obtém conhecimento relevante para uma pergunta específica."""
        results = self.knowledge_base.search(question)
        relevant_info = []
        
        for result in results:
            relevant_info.append(f"Informação sobre {result['tipo']}: {result['info']}")
        
        return "\n".join(relevant_info)

    def answer_question(self, question: str, context: str) -> str:
        """Responde a uma pergunta sobre o documento usando o modelo Mistral."""
        try:
            # Prepara o prompt
            prompt = f"""Com base no seguinte documento, responda à pergunta de forma clara e objetiva.

Documento:
{context}

Pergunta: {question}

Por favor, forneça uma resposta direta e precisa baseada apenas nas informações contidas no documento."""

            # Envia para o Mistral
            messages = [
                ChatMessage(role="system", content="Você é um assistente especializado em análise de documentos jurídicos e policiais."),
                ChatMessage(role="user", content=prompt)
            ]

            response = self.client.chat(
                model="mistral-medium",
                messages=messages
            )

            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            raise ValueError(f"Erro ao processar pergunta: {str(e)}")
