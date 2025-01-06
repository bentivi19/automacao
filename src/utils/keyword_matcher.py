import re
from typing import List, Dict, Tuple
from difflib import get_close_matches

class KeywordMatcher:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def extract_keywords(self, condition: str) -> List[str]:
        """Extrai palavras-chave de uma condição."""
        # Remove caracteres especiais e divide por ponto e vírgula ou ponto
        keywords = re.split('[;.]', condition)
        # Limpa e normaliza cada palavra-chave
        cleaned_keywords = []
        for keyword in keywords:
            # Remove espaços extras e converte para minúsculas
            cleaned = keyword.strip().lower()
            # Remove caracteres especiais mantendo acentos
            cleaned = re.sub(r'[^\w\s\-áéíóúâêîôûãõàèìòùäëïöüç]', '', cleaned)
            if cleaned:
                cleaned_keywords.append(cleaned)
        return cleaned_keywords

    def find_matches(self, text: str, keywords: List[str]) -> List[Tuple[str, str, float]]:
        """
        Encontra correspondências aproximadas das palavras-chave no texto.
        Retorna uma lista de tuplas (palavra_encontrada, palavra_chave, similaridade)
        """
        matches = []
        # Normaliza o texto para busca
        text_lower = text.lower()
        # Divide o texto em palavras
        words = re.findall(r'\b\w+\b', text_lower)
        
        for keyword in keywords:
            # Para cada palavra-chave, procura correspondências aproximadas
            close_matches = get_close_matches(
                keyword, 
                words, 
                n=3,  # número máximo de correspondências por palavra-chave
                cutoff=self.similarity_threshold
            )
            
            for match in close_matches:
                # Calcula a similaridade
                similarity = self._calculate_similarity(keyword, match)
                matches.append((match, keyword, similarity))
        
        return matches

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calcula a similaridade entre duas strings."""
        # Implementação simples do coeficiente de Levenshtein normalizado
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1, str2).ratio()

    def find_keywords_in_text(self, text: str, rules: List[Dict]) -> List[Dict]:
        """
        Encontra palavras-chave das regras no texto.
        Retorna uma lista de regras acionadas com suas correspondências.
        """
        triggered_rules = []
        
        for rule in rules:
            condition = rule.get('condition', '')
            if not condition:
                continue
                
            # Extrai palavras-chave da condição
            keywords = self.extract_keywords(condition)
            # Encontra correspondências no texto
            matches = self.find_matches(text, keywords)
            
            # Se encontrou correspondências suficientes, considera a regra acionada
            if matches:
                # Calcula a média de similaridade das correspondências
                avg_similarity = sum(m[2] for m in matches) / len(matches)
                
                # Se a média de similaridade for maior que o threshold
                if avg_similarity >= self.similarity_threshold:
                    triggered_rule = {
                        'id': rule.get('id'),
                        'name': rule.get('name'),
                        'action': rule.get('action', rule.get('recommended_action', '')),
                        'description': rule.get('description'),
                        'type': rule.get('type', 'regra'),
                        'priority': rule.get('priority', 'Média'),
                        'matches': [
                            {
                                'found': m[0],
                                'keyword': m[1],
                                'similarity': m[2]
                            } for m in matches
                        ]
                    }
                    triggered_rules.append(triggered_rule)
        
        return triggered_rules
