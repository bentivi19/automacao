import os
import re
import yaml
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import spacy
from collections import defaultdict
from typing import Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rules_engine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RuleProcessor:
    def __init__(self):
        """Inicializa o processador de regras."""
        try:
            # Obtém o caminho absoluto para o diretório do projeto
            project_root = Path(__file__).parent.parent.parent
            rules_dir = project_root / 'config' / 'rules'
            
            # Carrega todas as regras de diferentes tipos
            self.rules = {
                'pre_analysis': self._load_rules_from_file(rules_dir / 'pre_analysis_rules.yaml'),
                'final_output': self._load_rules_from_file(rules_dir / 'final_output_rules.yaml'),
                'alerts': self._load_rules_from_file(rules_dir / 'alert_rules.yaml'),
                'exceptions': self._load_rules_from_file(rules_dir / 'exception_rules.yaml')
            }
                
            logger.info("Regras carregadas com sucesso")
            
            self.nlp = spacy.load("pt_core_news_lg")
            self.similarity_threshold = 0.85

        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            self.rules = {
                'pre_analysis': {'rules': []},
                'final_output': {'rules': []},
                'alerts': {'rules': []},
                'exceptions': {'rules': []}
            }

    def _load_rules_from_file(self, file_path: Path) -> dict:
        """Carrega regras de um arquivo específico."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {'rules': []}
        except Exception as e:
            logger.error(f"Erro ao carregar regras de {file_path}: {str(e)}")
            return {'rules': []}

    def check_specialized_department(self, 
                                  crime: str, 
                                  local: str, 
                                  autoria_conhecida: bool) -> Optional[Dict[str, str]]:
        """Verifica se o caso deve ser enviado para algum departamento especializado."""
        if not self.rules.get('email_rules', {}).get('specialized_departments'):
            return None

        for dept in self.rules['email_rules']['specialized_departments']:
            # Verifica DEINTER (fora da capital)
            if dept['name'] == 'DEINTER' and 'São Paulo' not in local:
                return {'department': 'DEINTER', 'email': dept['email']}

            # Verifica DECRADI/DECAP (crimes de intolerância)
            if any(c.lower() in crime.lower() for c in ['racismo', 'intolerância']):
                if autoria_conhecida and dept['name'] == 'DECAP':
                    return {'department': 'DECAP', 'email': dept['email']}
                if not autoria_conhecida and dept['name'] == 'DECRADI':
                    return {'department': 'DECRADI', 'email': dept['email']}

            # Verifica outros departamentos baseado nas condições
            if 'conditions' in dept:
                for condition in dept['conditions']:
                    if isinstance(condition, str) and condition.lower() in crime.lower():
                        return {'department': dept['name'], 'email': dept['email']}

        return None

    def get_dp_address(self, 
                      representante: str, 
                      data_crime: str, 
                      plataforma: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Determina o endereço do DP para cadastro no Portal."""
        try:
            # Regras JUCESP
            if "JUCESP" in representante:
                data = datetime.strptime(data_crime, "%Y-%m-%d")
                if data <= datetime(2019, 7, 31):
                    return {
                        "dp": "23º DP",
                        "endereco": "Rua Barra Funda, 930"
                    }
                else:
                    return {
                        "dp": "7º DP",
                        "endereco": "Rua Guaicurus, 2394"
                    }

            # Regras redes sociais
            if plataforma:
                social_rules = self.rules['portal_rules']['social_media_rules']
                for rule in social_rules:
                    if plataforma in rule['platforms']:
                        return {
                            "dp": rule['dp'],
                            "endereco": rule['endereco']
                        }

        except Exception as e:
            logger.error(f"Erro ao processar regras de endereço: {str(e)}")
        
        return None

    def should_use_portal(self, 
                         crime: str, 
                         local: str, 
                         autoria_conhecida: bool) -> bool:
        """Determina se deve usar o Portal de Documentos."""
        # Se não se enquadra em nenhuma regra de departamento especializado,
        # deve usar o portal
        return self.check_specialized_department(crime, local, autoria_conhecida) is None

    def process_rules(self, text: str, rule_type: str = 'pre_analysis') -> str:
        """Processa o texto usando as regras definidas.
        
        Args:
            text: Texto a ser processado
            rule_type: Tipo de regra a ser processada (padrão: pre_analysis)
            
        Returns:
            str: Texto processado com os resultados da análise
        """
        try:
            results = {}
            
            # Processa cada regra do tipo especificado
            for rule in self.rules.get(rule_type, {}).get('rules', []):
                rule_name = rule.get('name')
                condition = rule.get('condition')
                recommended_action = rule.get('recommended_action')
                
                # Verifica se a condição da regra é atendida
                if condition and re.search(condition, text, re.IGNORECASE):
                    results[rule_name] = {
                        'condition': condition,
                        'recommended_action': recommended_action
                    }
            
            # Formata os resultados como texto
            output = []
            output.append(f"Resultados da análise ({rule_type}):")
            for rule_name, rule_details in results.items():
                output.append(f"\n{rule_name}:")
                output.append(f"  - Condição: {rule_details['condition']}")
                output.append(f"  - Ação Recomendada: {rule_details['recommended_action']}")
            
            return "\n".join(output) if results else text
            
        except Exception as e:
            logger.error(f"Erro ao processar regras de {rule_type}: {str(e)}")
            return text

    def process_text(self, text: str, additional_context: str = None) -> Dict[str, List[str]]:
        """
        Processa o texto e o contexto adicional para extrair entidades e palavras-chave.
        """
        # Combina texto principal e contexto adicional
        full_text = text
        if additional_context:
            full_text = f"{text}\n\nContexto Adicional:\n{additional_context}"
        
        # Processa o texto com spaCy
        doc = self.nlp(full_text)
        
        # Extrai entidades e suas menções
        entities = defaultdict(list)
        for ent in doc.ents:
            if ent.label_ in ['PER', 'ORG']:  # Pessoas e Organizações
                entities[ent.text.lower()].append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        # Extrai palavras-chave importantes
        keywords = defaultdict(list)
        important_pos = ['NOUN', 'VERB', 'ADJ']
        for token in doc:
            if token.pos_ in important_pos:
                keywords[token.text.lower()].append({
                    'text': token.text,
                    'pos': token.pos_,
                    'start': token.idx,
                    'end': token.idx + len(token.text)
                })
        
        return {
            'entities': dict(entities),
            'keywords': dict(keywords)
        }

    def match_condition(self, condition: str, text_info: Dict) -> Tuple[bool, List[Dict]]:
        """
        Verifica se uma condição se aplica ao texto, considerando agentes específicos.
        Retorna uma tupla (matches, evidências).
        """
        # Parseia a condição
        condition_parts = self._parse_condition(condition)
        if not condition_parts:
            return False, []
        
        matches = []
        current_result = True
        
        for part in condition_parts:
            if part['type'] == 'condition':
                agent_match = self._match_agent(part['agent'], text_info['entities'])
                action_match = self._match_action(part['action'], text_info['keywords'])
                
                # Uma condição só é válida se tanto o agente quanto a ação correspondem
                part_result = bool(agent_match and action_match)
                
                if part['connector'] == 'se':
                    current_result = part_result
                elif part['connector'] == 'e':
                    current_result = current_result and part_result
                elif part['connector'] == 'ou':
                    current_result = current_result or part_result
                elif part['connector'] == 'se não (for)':
                    current_result = current_result and not part_result
                
                if agent_match or action_match:
                    matches.append({
                        'agent': agent_match,
                        'action': action_match,
                        'connector': part['connector']
                    })
        
        return current_result, matches

    def _parse_condition(self, condition: str) -> List[Dict]:
        """Parseia uma string de condição em suas partes componentes."""
        parts = []
        current_part = {}
        
        # Divide a condição em tokens
        tokens = condition.lower().split()
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            if token == 'se':
                if current_part:
                    parts.append(current_part)
                current_part = {'type': 'condition', 'connector': 'se'}
                i += 1
            elif token in ['e', 'ou']:
                if current_part:
                    parts.append(current_part)
                current_part = {'type': 'condition', 'connector': token}
                i += 1
            elif token == 'não' and i + 1 < len(tokens) and tokens[i+1] == '(for)':
                if current_part:
                    parts.append(current_part)
                current_part = {'type': 'condition', 'connector': 'se não (for)'}
                i += 2
            else:
                # Coleta o agente até encontrar um verbo ou próximo conectivo
                agent_parts = []
                while i < len(tokens) and tokens[i] not in ['e', 'ou', 'se', 'não']:
                    agent_parts.append(tokens[i])
                    i += 1
                    if len(agent_parts) > 1 and self._is_verb(agent_parts[-1]):
                        agent_parts.pop()
                        i -= 1
                        break
                
                if agent_parts:
                    current_part['agent'] = ' '.join(agent_parts)
                
                # Coleta a ação até o próximo conectivo
                action_parts = []
                while i < len(tokens) and tokens[i] not in ['e', 'ou', 'se', 'não']:
                    action_parts.append(tokens[i])
                    i += 1
                
                if action_parts:
                    current_part['action'] = ' '.join(action_parts)
        
        if current_part:
            parts.append(current_part)
        
        return parts

    def _is_verb(self, word: str) -> bool:
        """Verifica se uma palavra é um verbo."""
        doc = self.nlp(word)
        return doc[0].pos_ == 'VERB'

    def _match_agent(self, agent: str, entities: Dict) -> Optional[Dict]:
        """
        Verifica se um agente específico está presente nas entidades do texto.
        Usa correspondência por similaridade para lidar com variações.
        """
        if not agent:
            return None
        
        agent_doc = self.nlp(agent.lower())
        best_match = None
        best_score = 0
        
        for entity, mentions in entities.items():
            entity_doc = self.nlp(entity)
            score = agent_doc.similarity(entity_doc)
            
            if score > self.similarity_threshold and score > best_score:
                best_score = score
                best_match = {
                    'text': mentions[0]['text'],
                    'score': score,
                    'mentions': mentions
                }
        
        return best_match

    def _match_action(self, action: str, keywords: Dict) -> Optional[Dict]:
        """
        Verifica se uma ação específica está presente nas palavras-chave do texto.
        Usa correspondência por similaridade para lidar com variações.
        """
        if not action:
            return None
        
        action_doc = self.nlp(action.lower())
        matches = []
        
        # Procura por correspondências de palavras-chave
        for keyword, mentions in keywords.items():
            keyword_doc = self.nlp(keyword)
            score = action_doc.similarity(keyword_doc)
            
            if score > self.similarity_threshold:
                matches.append({
                    'text': mentions[0]['text'],
                    'score': score,
                    'mentions': mentions
                })
        
        if matches:
            # Retorna o conjunto de correspondências encontradas
            return {
                'matches': matches,
                'best_match': max(matches, key=lambda x: x['score'])
            }
        
        return None
