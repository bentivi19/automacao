"""
InteractiveAnalyzer - Agente especializado em responder perguntas do usuário
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class InteractiveAnalyzer:
    def __init__(self):
        self.document_chunks = []
        self.last_analysis = None
        
    def set_context(self, chunks: List[str], analysis: Dict) -> None:
        """
        Define o contexto para responder perguntas.
        
        Args:
            chunks: Lista de chunks do documento
            analysis: Análise prévia do documento
        """
        self.document_chunks = chunks
        self.last_analysis = analysis
    
    def answer_question(self, question: str) -> str:
        """
        Responde a uma pergunta do usuário sobre o documento.
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Resposta baseada no contexto e análise prévia
        """
        try:
            if not self.document_chunks or not self.last_analysis:
                return "Não há documento carregado para análise. Por favor, carregue um documento primeiro."
            
            # Normaliza a pergunta
            question = question.lower().strip()
            
            # Identifica o tipo de pergunta
            if any(word in question for word in ['última', 'manifestação', 'promotor']):
                return self._answer_about_manifestation(question)
            elif any(word in question for word in ['vítima', 'investigado', 'acusado']):
                return self._answer_about_person(question)
            elif any(word in question for word in ['processo', 'inquérito', 'boletim']):
                return self._answer_about_ids(question)
            elif 'remessa' in question:
                return self._answer_about_remessa(question)
            else:
                return self._answer_general_question(question)
            
        except Exception as e:
            logger.error(f"Erro ao responder pergunta: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, tente reformulá-la."
    
    def _answer_about_manifestation(self, question: str) -> str:
        """Responde perguntas sobre manifestações."""
        last_manifestation = self.last_analysis.get('last_manifestation', {})
        manifestations = self.last_analysis.get('manifestations', [])
        
        if not last_manifestation and not manifestations:
            return "Não foram encontradas manifestações no documento."
        
        if 'última' in question:
            if last_manifestation:
                promoter = last_manifestation.get('promoter', 'Não identificado')
                action = last_manifestation.get('action', 'Não identificada')
                return f"A última manifestação foi do(a) Promotor(a) {promoter}, que {action}."
            return "Não foi possível identificar a última manifestação."
            
        return f"Foram encontradas {len(manifestations)} manifestações no documento."
    
    def _answer_about_person(self, question: str) -> str:
        """Responde perguntas sobre pessoas mencionadas."""
        # Busca em todos os chunks por informações sobre a pessoa
        person_info = []
        person_type = 'vítima' if 'vítima' in question else 'investigado' if 'investigado' in question else 'acusado'
        
        for chunk in self.document_chunks:
            # Procura por menções à pessoa
            pattern = f"(?i)(?:{person_type}|nome)\\s+([^,\\n.]+)"
            matches = re.finditer(pattern, chunk)
            for match in matches:
                # Extrai o contexto
                start = max(0, match.start() - 100)
                end = min(len(chunk), match.end() + 100)
                context = chunk[start:end]
                person_info.append(context)
        
        if person_info:
            return f"Informações encontradas sobre {person_type}:\n" + "\n".join(person_info)
        return f"Não foram encontradas informações específicas sobre {person_type} no documento."
    
    def _answer_about_ids(self, question: str) -> str:
        """Responde perguntas sobre números de documentos."""
        document_ids = self.last_analysis.get('document_ids', {})
        
        if not document_ids:
            return "Não foram encontrados números de identificação no documento."
            
        # Identifica qual tipo de ID está sendo perguntado
        id_type = None
        if 'processo' in question:
            id_type = 'processo'
        elif 'inquérito' in question:
            id_type = 'inquerito'
        elif 'boletim' in question:
            id_type = 'boletim'
            
        if id_type and id_type in document_ids:
            return f"Números de {id_type} encontrados: {', '.join(document_ids[id_type])}"
            
        # Se não especificou tipo, retorna todos
        response = []
        for id_type, ids in document_ids.items():
            response.append(f"{id_type.title()}: {', '.join(ids)}")
        return "\n".join(response)
    
    def _answer_about_remessa(self, question: str) -> str:
        """Responde perguntas sobre remessas."""
        remessas = self.last_analysis.get('remessas', [])
        
        if not remessas:
            return "Não foram encontradas remessas no documento."
            
        response = [f"Foram encontradas {len(remessas)} remessas:"]
        for remessa in remessas:
            destination = remessa.get('destination', 'Destino não especificado')
            response.append(f"- Remessa para: {destination}")
            
        return "\n".join(response)
    
    def _answer_general_question(self, question: str) -> str:
        """Responde perguntas gerais sobre o documento."""
        # Busca palavras-chave na pergunta
        keywords = re.findall(r'\b\w+\b', question)
        relevant_chunks = []
        
        for chunk in self.document_chunks:
            # Verifica se o chunk contém as palavras-chave
            if any(keyword in chunk.lower() for keyword in keywords):
                # Extrai um trecho relevante
                for keyword in keywords:
                    if keyword in chunk.lower():
                        start = chunk.lower().find(keyword)
                        # Pega um contexto de 200 caracteres antes e depois
                        context_start = max(0, start - 200)
                        context_end = min(len(chunk), start + 200)
                        relevant_chunks.append(chunk[context_start:context_end])
        
        if relevant_chunks:
            return "Encontrei as seguintes informações relevantes:\n" + "\n...\n".join(relevant_chunks)
        return "Não encontrei informações específicas sobre sua pergunta no documento."
