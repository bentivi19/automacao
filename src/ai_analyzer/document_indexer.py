"""
DocumentIndexer - Componente especializado em indexação e busca de termos em documentos
"""

import re
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging
from unidecode import unidecode
from dataclasses import dataclass
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from nltk.corpus import stopwords

# Download recursos necessários do NLTK
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('rslp')

logger = logging.getLogger(__name__)

@dataclass
class TermOccurrence:
    """Representa uma ocorrência de um termo no documento."""
    term: str
    position: int
    context: str
    date: str = None
    paragraph_id: int = None

class DocumentIndexer:
    def __init__(self):
        self.stemmer = RSLPStemmer()
        self.stop_words = set(stopwords.words('portuguese'))
        self.index = defaultdict(list)
        self.paragraphs = []
        self.term_variations = {}
        
    def index_document(self, text: str) -> None:
        """
        Indexa o documento completo, criando índices invertidos e mapeamento de variações.
        """
        # Divide o documento em parágrafos
        self.paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Processa cada parágrafo
        for paragraph_id, paragraph in enumerate(self.paragraphs):
            # Tokeniza o texto
            tokens = word_tokenize(paragraph.lower())
            
            # Remove stopwords e aplica stemming
            processed_terms = []
            for token in tokens:
                if token not in self.stop_words and len(token) > 2:
                    stem = self.stemmer.stem(token)
                    processed_terms.append((token, stem))
                    
            # Indexa os termos
            for position, (term, stem) in enumerate(processed_terms):
                # Obtém contexto expandido
                context_start = max(0, position - 10)
                context_end = min(len(processed_terms), position + 10)
                context = ' '.join(t[0] for t in processed_terms[context_start:context_end])
                
                # Extrai data se presente no contexto
                date = self._extract_date(context)
                
                # Armazena ocorrência
                occurrence = TermOccurrence(
                    term=term,
                    position=position,
                    context=context,
                    date=date,
                    paragraph_id=paragraph_id
                )
                
                # Indexa pelo stem e pelo termo original
                self.index[stem].append(occurrence)
                self.index[term].append(occurrence)
                
                # Registra variação
                if stem not in self.term_variations:
                    self.term_variations[stem] = set()
                self.term_variations[stem].add(term)
                
    def search_terms(self, terms: List[str], use_variations: bool = True) -> Dict[str, List[TermOccurrence]]:
        """
        Busca termos no documento, incluindo suas variações.
        """
        results = {}
        
        for term in terms:
            # Normaliza o termo
            normalized_term = term.lower().strip()
            stem = self.stemmer.stem(normalized_term)
            
            # Coleta todas as variações do termo
            variations = {normalized_term}
            if use_variations:
                # Adiciona variações baseadas no stem
                variations.update(self.term_variations.get(stem, set()))
                
                # Adiciona variações sem acentos
                variations.update({unidecode(v) for v in variations})
                
                # Adiciona variações com diferentes separadores
                for v in list(variations):
                    if ' ' in v:
                        variations.add(v.replace(' ', ''))
                        variations.add(v.replace(' ', '.'))
                        variations.add(v.replace(' ', '_'))
                        variations.add(v.replace(' ', '-'))
            
            # Busca ocorrências para todas as variações
            occurrences = []
            for variation in variations:
                occurrences.extend(self.index.get(variation, []))
                
            # Remove duplicatas e ordena por posição
            unique_occurrences = list({(o.position, o.paragraph_id): o for o in occurrences}.values())
            unique_occurrences.sort(key=lambda x: (x.paragraph_id, x.position))
            
            if unique_occurrences:
                results[term] = unique_occurrences
                
        return results
        
    def get_paragraph_context(self, paragraph_id: int, window: int = 1) -> str:
        """
        Retorna o contexto expandido de um parágrafo.
        """
        start = max(0, paragraph_id - window)
        end = min(len(self.paragraphs), paragraph_id + window + 1)
        return '\n'.join(self.paragraphs[start:end])
        
    def _extract_date(self, text: str) -> str:
        """
        Extrai data do texto em vários formatos.
        """
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}\s+de\s+[^\s]+\s+de\s+\d{4}',
            r'\d{2}\.\d{2}\.\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()
                
        return None
        
    def get_term_statistics(self) -> Dict[str, Dict]:
        """
        Retorna estatísticas sobre os termos indexados.
        """
        stats = {}
        for term, occurrences in self.index.items():
            stats[term] = {
                'count': len(occurrences),
                'variations': list(self.term_variations.get(self.stemmer.stem(term), set())),
                'paragraphs': len(set(o.paragraph_id for o in occurrences))
            }
        return stats
