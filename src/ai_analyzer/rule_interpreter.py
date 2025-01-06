"""
RuleInterpreter - Agente especializado em leitura e interpretação de regras
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from ..rules_engine.rules_manager import RulesManager
from .document_indexer import DocumentIndexer
from .chronological_analyzer import ChronologicalAnalyzer
from .pdf_consolidator import PDFConsolidator
from .pdf_reader import get_pdf_content

logger = logging.getLogger(__name__)

class RuleInterpreter:
    def __init__(self):
        self.document_chunks = []
        self.full_text = ""
        self.rules_manager = RulesManager()
        self.pdf_consolidator = PDFConsolidator()
        self.document_indexer = DocumentIndexer()
        self.chronological_analyzer = ChronologicalAnalyzer()
        self.agent_id = "RuleInterpreter-1"
        self._load_rules()
        
    def _load_rules(self):
        """Carrega todas as regras cadastradas."""
        self.rules = {}
        rule_types = ['pre_analysis', 'final_output', 'alerts', 'exceptions']
        
        for rule_type in rule_types:
            rules = self.rules_manager.get_rules(rule_type)
            for rule in rules:
                rule_id = rule.get('id')
                if rule_id:
                    self.rules[rule_id] = rule
        
    def interpret_document(self, chunks: List[str]) -> Dict:
        """Interpreta o documento focando em regras e últimas manifestações."""
        try:
            self.document_chunks = chunks
            self.full_text = ' '.join(chunks)
            analysis = {}
            
            # Consolida chunks em arquivo temporário
            logger.info("Consolidando chunks em arquivo temporário...")
            self.pdf_consolidator.consolidate_chunks(chunks)
            
            # Verifica se arquivo foi criado
            if not self.pdf_consolidator.temp_file_path.exists():
                logger.error("Arquivo temporário não foi criado!")
                return {}
            else:
                logger.info(f"Arquivo temporário criado em: {self.pdf_consolidator.temp_file_path}")
            
            # Extrai informações básicas
            analysis['nf_number'] = self._extract_nf_number()
            analysis['promotoria'] = self._extract_promotoria()
            analysis['crime_details'] = self._extract_crime_details()
            analysis['dates'] = self._extract_dates()
            
            # Primeira análise de manifestações
            manifestations = self._find_all_manifestations()
            last_manifestation = self._determine_last_manifestation(manifestations)
            
            # Valida último promotor usando arquivo consolidado
            if last_manifestation:
                real_last_promoter = self.pdf_consolidator.validate_last_promoter(
                    last_manifestation.get('promoter', '')
                )
                if real_last_promoter:
                    last_manifestation['promoter'] = real_last_promoter
            
            analysis['manifestations'] = manifestations
            analysis['last_manifestation'] = last_manifestation
            
            # Analisa palavras-chave usando arquivo consolidado
            keywords = self._extract_keywords_from_rules()
            found_keywords = self.pdf_consolidator.verify_keywords(keywords)
            analysis['keywords'] = found_keywords
            
            # Aplica regras e gera recomendações
            analysis['rules_results'] = self._apply_rules(found_keywords)
            analysis['pre_analysis_report'] = self._format_pre_analysis_report(analysis)
            analysis['recommendation'] = self._generate_recommendation(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao interpretar documento: {str(e)}")
            return {}
            
    def _analyze_keywords(self) -> Dict[str, List[Dict]]:
        """
        Analisa palavras-chave de todas as regras usando o DocumentIndexer.
        """
        keywords_results = {}
        
        # Para cada regra, busca suas palavras-chave
        for rule_id, rule in self.rules.items():
            # Extrai palavras-chave da condição
            condition = rule.get('condition', '')
            if condition:
                # Divide por ponto e vírgula e remove espaços
                keywords = [k.strip() for k in condition.split(';') if k.strip()]
                
                # Busca cada palavra-chave
                search_results = self.document_indexer.search_terms(keywords)
                
                if search_results:
                    keywords_results[f'rule_{rule_id}'] = search_results
                    
        return keywords_results
        
    def _apply_rules(self, found_keywords: Dict[str, List[str]]) -> List[Dict]:
        """Aplica regras usando as palavras-chave encontradas."""
        triggered_rules = []
        
        for rule_id, rule in self.rules.items():
            condition = rule.get('condition', '')
            if not condition:
                continue
                
            # Verifica se as palavras-chave da regra foram encontradas
            rule_keywords = [k.strip() for k in condition.split(';') if k.strip()]
            matched_keywords = []
            
            for keyword in rule_keywords:
                if keyword in found_keywords:
                    matched_keywords.append(keyword)
                    
            if matched_keywords:
                triggered_rules.append({
                    'id': rule_id,
                    'name': rule.get('name'),
                    'action': rule.get('action', ''),
                    'description': rule.get('description'),
                    'keywords_found': matched_keywords,
                    'contexts': [ctx for kw in matched_keywords for ctx in found_keywords[kw]]
                })
                
        return triggered_rules
        
    def _format_pre_analysis_report(self, analysis: Dict) -> str:
        """Formata o relatório padrão."""
        last_manifestation = analysis.get('last_manifestation', {})
        
        report = []
        
        # 1. Nome do último promotor
        promoter = last_manifestation.get('promoter', 'Não identificado')
        report.append(f"1. Nome COMPLETO do(a) último(a) Promotor(a) que se manifestou (da última Promotoria): {promoter}")
        
        # 2. Resumo da última manifestação
        action = last_manifestation.get('action', 'Não encontrado')
        report.append(f"2. Resumo DETALHADO da última manifestação (da última Promotoria): {action}")
        
        # 3. Número da NF
        nf = analysis.get('nf_number', 'Não encontrado')
        report.append(f"3. Número da NF (formato XXXX.XXXXXXX/XXXX): {nf}")
        
        # 4. Promotoria
        promotoria = analysis.get('promotoria', 'Não identificada')
        report.append(f"4. Promotoria de Justiça que enviou a NF: {promotoria}")
        
        # 5. Crime e detalhes
        crime = analysis.get('crime_details', 'Não especificado')
        report.append(f"5. Crime específico (Artigo do CP) e detalhes: {crime}")
        
        # 6. Nome e profissão da vítima/investigado (texto corrigido conforme solicitado)
        report.append("6. Nome e profissão da vítima ou investigado que o último Promotor manifestante solicitou a instauração de inquérito policial ou outra providência")
        
        # 7. Datas relevantes
        dates = analysis.get('dates', [])
        if dates:
            report.append(f"7. Datas relevantes do BO/documento: {', '.join(dates)}")
        else:
            report.append("7. Datas relevantes do BO/documento: Não encontradas")
        
        return "\n".join(report)

    def _generate_recommendation(self, analysis: Dict) -> str:
        """Gera recomendação baseada na análise completa."""
        # Primeiro verifica o conteúdo consolidado
        pdf_content = get_pdf_content()
        if not pdf_content:
            logger.warning("Arquivo consolidado não encontrado ou vazio")
            pdf_content = self.full_text  # Usa o texto atual como fallback
            
        recommendation = ""
        reasons = []
        
        # Processa regras acionadas
        rules_results = analysis.get('rules_results', [])
        
        for rule in rules_results:
            rule_id = rule.get('id')
            action = rule.get('action', '')
            description = rule.get('description', '')
            keywords_found = rule.get('keywords_found', [])
            
            # Verifica cada palavra-chave no conteúdo consolidado
            confirmed_keywords = []
            for keyword in keywords_found:
                if keyword.lower() in pdf_content.lower():
                    confirmed_keywords.append(keyword)
                    context = self._extract_keyword_context(pdf_content, keyword)
                    if context:
                        reasons.append(f"Palavra-chave '{keyword}' encontrada no contexto: {context}")
            
            if confirmed_keywords:
                recommendation = action
                reason = f"Regra {rule_id}: {description}"
                reason += f" (Palavras-chave confirmadas: {', '.join(confirmed_keywords)})"
                reasons.append(reason)
                
        # Se não encontrou recomendação específica
        if not recommendation:
            recommendation = "CADASTRAMENTO PELO PORTAL"
            reasons.append("Nenhuma regra específica foi confirmada no documento completo")
            
        # Formata a saída em português
        output = "RECOMENDAÇÃO:\n"
        output += "Após análise detalhada do documento, "
        
        if recommendation == "CADASTRAMENTO PELO PORTAL":
            output += "recomenda-se realizar o CADASTRAMENTO PELO PORTAL, "
        else:
            output += f"recomenda-se {recommendation}, "
            
        output += "pelos seguintes motivos:\n\n"
        
        for reason in reasons:
            output += f"- {reason}\n"
                
        return output
        
    def _extract_keyword_context(self, content: str, keyword: str, context_size: int = 100) -> Optional[str]:
        """Extrai o contexto em torno de uma palavra-chave."""
        import re
        match = re.search(f"[^.]*{keyword}[^.]*", content, re.IGNORECASE)
        if match:
            context = match.group()
            if len(context) > context_size:
                # Trunca o contexto mantendo a palavra-chave no centro
                start = context.lower().find(keyword.lower())
                half = context_size // 2
                if start < half:
                    return context[:context_size] + "..."
                else:
                    return "..." + context[start-half:start+half] + "..."
            return context
        return None

    def _extract_nf_number(self) -> Optional[str]:
        """Extrai número da NF."""
        nf_pattern = r'\d{4}\.\d{7}/\d{4}'
        for chunk in self.document_chunks:
            match = re.search(nf_pattern, chunk)
            if match:
                return match.group()
        return None

    def _extract_promotoria(self) -> Optional[str]:
        """Extrai nome da promotoria."""
        promotoria_pattern = r'(?i)promotoria\s+[^.]*'
        for chunk in self.document_chunks:
            match = re.search(promotoria_pattern, chunk)
            if match:
                return match.group().strip()
        return None

    def _extract_crime_details(self) -> Optional[str]:
        """Extrai detalhes do crime."""
        crime_pattern = r'(?i)(?:art(?:igo)?\.?\s*\d+|crime\s+de\s+[^.]*)'
        for chunk in self.document_chunks:
            match = re.search(crime_pattern, chunk)
            if match:
                start = max(0, match.start() - 50)
                end = min(len(chunk), match.end() + 100)
                return chunk[start:end].strip()
        return None

    def _extract_dates(self) -> List[str]:
        """Extrai datas do documento."""
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # dd/mm/yyyy
            r'\d{3}/\d{4}',  # xxx/yyyy
        ]
        
        dates = []
        for chunk in self.document_chunks:
            for pattern in date_patterns:
                matches = re.finditer(pattern, chunk)
                for match in matches:
                    dates.append(match.group())
        return dates

    def _extract_victim_info(self, context: str) -> Optional[str]:
        """Extrai informações da vítima/investigado."""
        victim_pattern = r'(?i)(?:vítima|investigado)\s+[^.]*'
        match = re.search(victim_pattern, context)
        if match:
            return match.group().strip()
        return None

    def _extract_keywords_from_rules(self) -> List[str]:
        """Extrai todas as palavras-chave das regras."""
        keywords = set()
        
        for rule in self.rules.values():
            condition = rule.get('condition', '')
            if condition:
                # Divide por ponto e vírgula e remove espaços
                rule_keywords = [k.strip() for k in condition.split(';') if k.strip()]
                keywords.update(rule_keywords)
                
        return list(keywords)
