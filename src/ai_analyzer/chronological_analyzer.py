"""
ChronologicalAnalyzer - Componente especializado em análise cronológica de manifestações
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Manifestation:
    """Representa uma manifestação no documento."""
    promoter: str
    action: str
    date: str
    context: str
    position: int
    references: List[str] = None  # Referências a outras manifestações
    temporal_markers: List[str] = None  # Marcadores temporais encontrados

class ChronologicalAnalyzer:
    def __init__(self):
        self.manifestations = []
        self.temporal_graph = defaultdict(list)
        self.date_formats = [
            ('%d/%m/%Y', r'\d{2}/\d{2}/\d{4}'),
            ('%d/%m/%y', r'\d{2}/\d{2}/\d{2}'),
            ('%d.%m.%Y', r'\d{2}\.\d{2}\.\d{4}'),
            ('%d-%m-%Y', r'\d{2}-\d{2}-\d{4}'),
            ('%d de %B de %Y', r'\d{1,2}\s+de\s+[^\s]+\s+de\s+\d{4}')
        ]
        self.temporal_markers = {
            'anterior': -1,
            'posteriormente': 1,
            'em seguida': 1,
            'na mesma data': 0,
            'nesta data': 0,
            'anteriormente': -1,
            'após': 1,
            'antes': -1,
            'logo depois': 1,
            'na sequência': 1
        }
        
    def analyze_manifestations(self, text: str) -> List[Manifestation]:
        """
        Analisa o documento e extrai manifestações com suas relações temporais.
        """
        # Extrai manifestações básicas
        self.manifestations = self._extract_manifestations(text)
        
        # Analisa relações temporais
        self._build_temporal_graph()
        
        # Ordena manifestações
        ordered_manifestations = self._order_manifestations()
        
        return ordered_manifestations
        
    def _extract_manifestations(self, text: str) -> List[Manifestation]:
        """
        Extrai manifestações do texto com contexto expandido.
        """
        manifestations = []
        
        # Padrões para identificar manifestações
        patterns = [
            # Com data explícita
            r'(?P<date>\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4}|\d{1,2}\s+de\s+[^\s]+\s+de\s+\d{4})[^.]*(?P<promoter>(?:Dr\.|Doutor[a]*|Promotor[a]*)[^,\n.]+)(?P<action>(?:determinou|manifestou-se|requereu)[^.]+)',
            
            # Com referência temporal
            r'(?P<temporal>(?:' + '|'.join(self.temporal_markers.keys()) + r'))[^.]*(?P<promoter>(?:Dr\.|Doutor[a]*|Promotor[a]*)[^,\n.]+)(?P<action>(?:determinou|manifestou-se|requereu)[^.]+)',
            
            # Sem referência temporal explícita
            r'(?P<promoter>(?:Dr\.|Doutor[a]*|Promotor[a]*)[^,\n.]+)(?P<action>(?:determinou|manifestou-se|requereu)[^.]+)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Extrai informações básicas
                promoter = match.group('promoter').strip()
                action = match.group('action').strip()
                
                # Extrai data ou marcador temporal
                date = None
                temporal_markers = []
                if 'date' in match.groupdict() and match.group('date'):
                    date = match.group('date')
                elif 'temporal' in match.groupdict() and match.group('temporal'):
                    temporal_markers.append(match.group('temporal').lower())
                
                # Obtém contexto expandido
                start = max(0, match.start() - 500)
                end = min(len(text), match.end() + 500)
                context = text[start:end]
                
                # Procura por referências a outras manifestações
                references = self._find_references(context)
                
                # Procura por marcadores temporais adicionais
                temporal_markers.extend(self._find_temporal_markers(context))
                
                manifestation = Manifestation(
                    promoter=promoter,
                    action=action,
                    date=date,
                    context=context,
                    position=match.start(),
                    references=references,
                    temporal_markers=temporal_markers
                )
                
                manifestations.append(manifestation)
        
        return manifestations
        
    def _find_references(self, text: str) -> List[str]:
        """
        Encontra referências a outras manifestações no texto.
        """
        references = []
        
        # Padrões para referências
        patterns = [
            r'(?:conforme|segundo|de acordo com)[^.]*(?:manifestação|parecer)[^.]*(?:Dr\.|Doutor[a]*|Promotor[a]*)[^,\n.]+',
            r'(?:mencionad[oa]|citad[oa]|referid[oa])[^.]*(?:Dr\.|Doutor[a]*|Promotor[a]*)[^,\n.]+'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            references.extend(match.group().strip() for match in matches)
            
        return references
        
    def _find_temporal_markers(self, text: str) -> List[str]:
        """
        Encontra marcadores temporais no texto.
        """
        markers = []
        
        for marker in self.temporal_markers.keys():
            if re.search(r'\b' + re.escape(marker) + r'\b', text, re.IGNORECASE):
                markers.append(marker)
                
        return markers
        
    def _build_temporal_graph(self):
        """
        Constrói um grafo direcionado de relações temporais entre manifestações.
        """
        self.temporal_graph.clear()
        
        for i, manifest_a in enumerate(self.manifestations):
            for j, manifest_b in enumerate(self.manifestations):
                if i != j:
                    relation = self._determine_temporal_relation(manifest_a, manifest_b)
                    if relation:
                        self.temporal_graph[i].append((j, relation))
                        
    def _determine_temporal_relation(self, manifest_a: Manifestation, manifest_b: Manifestation) -> Optional[int]:
        """
        Determina a relação temporal entre duas manifestações.
        Retorna: -1 (antes), 0 (mesmo momento), 1 (depois), None (indeterminado)
        """
        # Verifica datas explícitas primeiro
        if manifest_a.date and manifest_b.date:
            date_a = self._parse_date(manifest_a.date)
            date_b = self._parse_date(manifest_b.date)
            if date_a and date_b:
                if date_a < date_b:
                    return -1
                elif date_a > date_b:
                    return 1
                return 0
                
        # Verifica referências diretas
        if any(ref in manifest_b.context for ref in manifest_a.references):
            return -1
            
        # Verifica marcadores temporais
        for marker in manifest_b.temporal_markers:
            if marker in self.temporal_markers:
                return self.temporal_markers[marker]
                
        # Se não conseguiu determinar, usa posição no documento
        return 1 if manifest_a.position < manifest_b.position else -1
        
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Tenta converter string de data para objeto datetime.
        """
        for date_format, pattern in self.date_formats:
            if re.match(pattern, date_str):
                try:
                    return datetime.strptime(date_str, date_format)
                except ValueError:
                    continue
        return None
        
    def _order_manifestations(self) -> List[Manifestation]:
        """
        Ordena manifestações usando o grafo temporal.
        """
        # Implementa ordenação topológica
        visited = set()
        temp = set()
        order = []
        
        def visit(node):
            if node in temp:
                return  # Evita ciclos
            if node in visited:
                return
                
            temp.add(node)
            
            # Visita nós relacionados
            for next_node, relation in self.temporal_graph[node]:
                if relation >= 0:  # Mesmo momento ou depois
                    visit(next_node)
                    
            temp.remove(node)
            visited.add(node)
            order.append(node)
            
        # Visita todos os nós
        for node in range(len(self.manifestations)):
            if node not in visited:
                visit(node)
                
        # Retorna manifestações ordenadas
        return [self.manifestations[i] for i in reversed(order)]
        
    def get_last_manifestation(self) -> Optional[Manifestation]:
        """
        Retorna a última manifestação do documento.
        """
        ordered = self._order_manifestations()
        return ordered[-1] if ordered else None

    def find_last_manifestation(self, chunks: List[str]) -> Optional[Dict]:
        """
        Encontra a última manifestação do promotor baseado na data mais recente.
        """
        manifestations = []
        full_text = ' '.join(chunks)
        
        # Padrões para identificar manifestações
        patterns = [
            # Padrão para manifestação com data por extenso
            r'(?P<date>\d{1,2}\s+de\s+[a-zA-Zç]+\s+de\s+\d{4})[^.]*?(?:Promotor[a]?\s+(?:de\s+Justiça\s+)?)?(?P<promoter>[A-ZÀ-Ú][A-ZÀ-Ú\s]+)(?:[^.]*?(?:determinou|manifestou-se|requereu|opinou|decidiu)[^.]*)',
            
            # Padrão para manifestação com data numérica
            r'(?P<date>\d{2}/\d{2}/\d{4})[^.]*?(?:Promotor[a]?\s+(?:de\s+Justiça\s+)?)?(?P<promoter>[A-ZÀ-Ú][A-ZÀ-Ú\s]+)(?:[^.]*?(?:determinou|manifestou-se|requereu|opinou|decidiu)[^.]*)',
            
            # Padrão para manifestação com "Dr." ou "Doutor"
            r'(?P<date>\d{1,2}[/\s](?:de\s+)?[a-zA-Zç]+[/\s](?:de\s+)?\d{4})[^.]*?(?:Dr\.?|Doutor[a]?)\s+(?P<promoter>[A-ZÀ-Ú][A-ZÀ-Ú\s]+)(?:[^.]*?(?:determinou|manifestou-se|requereu|opinou|decidiu)[^.]*)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                date_str = match.group('date').strip()
                promoter = match.group('promoter').strip()
                
                # Converte a data para um objeto datetime
                try:
                    date = self._parse_date(date_str)
                    if date:
                        # Extrai o contexto completo da manifestação
                        start = max(0, match.start() - 100)
                        end = min(len(full_text), match.end() + 100)
                        context = full_text[start:end].strip()
                        
                        # Extrai a ação do promotor
                        action_match = re.search(r'(?:determinou|manifestou-se|requereu|opinou|decidiu)[^.]*', context)
                        action = action_match.group().strip() if action_match else "Não especificada"
                        
                        manifestations.append({
                            'date': date,
                            'promoter': promoter,
                            'action': action,
                            'context': context
                        })
                except Exception as e:
                    logger.error(f"Erro ao processar data '{date_str}': {str(e)}")
                    continue
        
        # Ordena por data e retorna a mais recente
        if manifestations:
            manifestations.sort(key=lambda x: x['date'])
            last = manifestations[-1]
            return {
                'promoter': last['promoter'],
                'action': last['action'],
                'context': last['context'],
                'date': last['date'].strftime('%d/%m/%Y')
            }
            
        return None
        
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Converte uma string de data para objeto datetime."""
        # Remove espaços extras e palavras desnecessárias
        date_str = re.sub(r'\s+de\s+', ' ', date_str.lower().strip())
        
        # Tenta diferentes formatos
        for pattern in self.date_formats:
            match = re.match(pattern[1], date_str)
            if match:
                try:
                    day, month, year = match.groups()
                    
                    # Converte mês por extenso para número
                    if month.isalpha():
                        month = {
                            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                        }.get(month.lower(), 1)
                    else:
                        month = int(month)
                        
                    return datetime(int(year), month, int(day))
                except (ValueError, KeyError):
                    continue
                    
        return None
