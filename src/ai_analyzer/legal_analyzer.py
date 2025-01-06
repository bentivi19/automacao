"""
LegalAnalyzer - Coordena os agentes especializados para análise de documentos
"""

import logging
from typing import Dict, List, Optional

from .rule_interpreter import RuleInterpreter
from .interactive_analyzer import InteractiveAnalyzer

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self):
        self.rule_interpreter = RuleInterpreter()
        self.interactive_analyzer = InteractiveAnalyzer()
        self.current_chunks = []
        self.current_analysis = None
        
    def analyze_document(self, chunks: List[str]) -> Dict:
        """
        Analisa o documento usando os agentes especializados.
        
        Args:
            chunks: Lista de chunks do documento
            
        Returns:
            Dicionário com a análise do documento
        """
        try:
            # Armazena os chunks atuais
            self.current_chunks = chunks
            
            # Usa o RuleInterpreter para análise inicial
            logger.info("Iniciando análise do documento...")
            self.current_analysis = self.rule_interpreter.interpret_document(chunks)
            
            # Verifica se o arquivo consolidado foi criado
            if self.rule_interpreter.pdf_consolidator.temp_file_path.exists():
                logger.info("Arquivo consolidado disponível para consultas")
            else:
                logger.warning("Arquivo consolidado não encontrado")
            
            # Configura o InteractiveAnalyzer com o contexto
            self.interactive_analyzer.set_context(chunks, self.current_analysis)
            
            return self.current_analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            return {}
            
    def cleanup(self):
        """Limpa recursos temporários."""
        try:
            if hasattr(self, 'rule_interpreter'):
                self.rule_interpreter.pdf_consolidator.cleanup()
        except Exception as e:
            logger.error(f"Erro ao limpar recursos: {str(e)}")
            
    def answer_question(self, question: str) -> str:
        """
        Responde uma pergunta do usuário sobre o documento.
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            Resposta baseada na análise do documento
        """
        if not self.current_chunks or not self.current_analysis:
            return "Nenhum documento carregado. Por favor, carregue um documento primeiro."
            
        return self.interactive_analyzer.answer_question(question)
