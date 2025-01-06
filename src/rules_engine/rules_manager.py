import yaml
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import re
import os

logger = logging.getLogger(__name__)

class RulesManager:
    def __init__(self, rules_file: str = None):
        """
        Inicializa o gerenciador de regras.
        
        Args:
            rules_file: Caminho para o arquivo de regras YAML. Se não fornecido,
                       usa o arquivo padrão na pasta de configuração.
        """
        if not rules_file:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
            os.makedirs(config_dir, exist_ok=True)
            rules_file = os.path.join(config_dir, 'rules.yaml')
        
        self.rules_file = rules_file
        
        try:
            if os.path.exists(rules_file):
                with open(rules_file, 'r', encoding='utf-8') as f:
                    self.rules = yaml.safe_load(f) or {
                        'pre_analysis': [],
                        'final_output': [],
                        'alerts': [],
                        'exceptions': []
                    }
            else:
                self.rules = {
                    'pre_analysis': [],
                    'final_output': [],
                    'alerts': [],
                    'exceptions': []
                }
                self._save_rules()
                
            logger.info("Regras carregadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            self.rules = {
                'pre_analysis': [],
                'final_output': [],
                'alerts': [],
                'exceptions': []
            }

    def _save_rules(self) -> bool:
        """
        Salva as regras no arquivo YAML.
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário.
        """
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.rules, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar regras: {str(e)}")
            return False

    def get_rules(self, rule_type: str) -> List[Dict]:
        """
        Retorna todas as regras de um determinado tipo.
        
        Args:
            rule_type: Tipo de regra ('pre_analysis', 'final_output', 'alerts', 'exceptions')
            
        Returns:
            Lista de regras do tipo especificado.
        """
        return self.rules.get(rule_type, [])

    def add_rule(self, rule_type: str, rule_data: Dict) -> bool:
        """
        Adiciona uma nova regra.
        
        Args:
            rule_type: Tipo de regra
            rule_data: Dados da regra (nome, descrição, condição, ação, etc.)
            
        Returns:
            bool: True se adicionou com sucesso, False caso contrário.
        """
        try:
            # Validação dos campos obrigatórios
            required_fields = ['name', 'description', 'condition', 'action']
            if not all(field in rule_data for field in required_fields):
                logger.error("Campos obrigatórios ausentes")
                return False
            
            # Gera um novo ID único
            existing_ids = {r['id'] for r in self.rules[rule_type]}
            new_id = 1
            while new_id in existing_ids:
                new_id += 1
            
            # Adiciona campos de controle
            rule_data['id'] = new_id
            rule_data['created_at'] = datetime.now().isoformat()
            rule_data['updated_at'] = rule_data['created_at']
            
            # Adiciona a regra à lista
            self.rules[rule_type].append(rule_data)
            
            # Salva as alterações
            return self._save_rules()
            
        except Exception as e:
            logger.error(f"Erro ao adicionar regra: {str(e)}")
            return False

    def update_rule(self, rule_type: str, rule_id: int, rule_data: Dict) -> bool:
        """
        Atualiza uma regra existente.
        
        Args:
            rule_type: Tipo de regra
            rule_id: ID da regra a ser atualizada
            rule_data: Novos dados da regra
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário.
        """
        try:
            # Validação dos campos obrigatórios
            required_fields = ['name', 'description', 'condition', 'action']
            if not all(field in rule_data for field in required_fields):
                logger.error("Campos obrigatórios ausentes")
                return False
            
            # Encontra a regra
            rule_index = next(
                (i for i, r in enumerate(self.rules[rule_type]) if r['id'] == rule_id),
                None
            )
            
            if rule_index is None:
                logger.error(f"Regra {rule_id} não encontrada")
                return False
            
            # Mantém o ID original e atualiza o timestamp
            rule_data['id'] = rule_id
            rule_data['created_at'] = self.rules[rule_type][rule_index]['created_at']
            rule_data['updated_at'] = datetime.now().isoformat()
            
            # Atualiza a regra
            self.rules[rule_type][rule_index] = rule_data
            
            # Salva as alterações
            return self._save_rules()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar regra: {str(e)}")
            return False

    def delete_rule(self, rule_type: str, rule_id: int) -> bool:
        """
        Exclui uma regra.
        
        Args:
            rule_type: Tipo de regra
            rule_id: ID da regra a ser excluída
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário.
        """
        try:
            # Encontra a regra
            rule_index = next(
                (i for i, r in enumerate(self.rules[rule_type]) if r['id'] == rule_id),
                None
            )
            
            if rule_index is None:
                logger.error(f"Regra {rule_id} não encontrada")
                return False
            
            # Remove a regra
            self.rules[rule_type].pop(rule_index)
            
            # Salva as alterações
            return self._save_rules()
            
        except Exception as e:
            logger.error(f"Erro ao excluir regra: {str(e)}")
            return False

    def apply_rules(self, text: str) -> Dict:
        """Aplica as regras ao texto e retorna as regras acionadas usando busca flexível de palavras-chave."""
        try:
            from src.utils.keyword_matcher import KeywordMatcher
            matcher = KeywordMatcher(similarity_threshold=0.85)
            triggered_rules = []
            
            # Aplica regras de pré-análise
            pre_analysis_rules = self.get_rules('pre_analysis')
            if pre_analysis_rules:
                matches = matcher.find_keywords_in_text(text, pre_analysis_rules)
                for match in matches:
                    match['type'] = 'regra'
                    triggered_rules.append(match)
            
            # Aplica regras de exceção
            exception_rules = self.get_rules('exceptions')
            if exception_rules:
                matches = matcher.find_keywords_in_text(text, exception_rules)
                for match in matches:
                    match['type'] = 'exceção'
                    triggered_rules.append(match)
            
            # Aplica regras de alerta
            alert_rules = self.get_rules('alerts')
            if alert_rules:
                matches = matcher.find_keywords_in_text(text, alert_rules)
                for match in matches:
                    match['type'] = 'alerta'
                    triggered_rules.append(match)
            
            return {
                'success': True,
                'triggered_rules': triggered_rules,
                'total_rules': len(triggered_rules)
            }
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regras: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def format_rules_output(self, rules_result: Dict) -> str:
        """Formata o resultado das regras para exibição, incluindo informações sobre correspondências."""
        if not rules_result.get('success', False):
            return ""
            
        triggered_rules = rules_result.get('triggered_rules', [])
        if not triggered_rules:
            return ""
        
        output = ""
        
        # Separa as regras por tipo
        regras = [r for r in triggered_rules if r.get('type') == 'regra']
        excecoes = [r for r in triggered_rules if r.get('type') == 'exceção']
        alertas = [r for r in triggered_rules if r.get('type') == 'alerta']
        
        # Adiciona regras cadastradas
        if regras:
            output += "\n#### Regras Cadastradas\n"
            for rule in regras:
                output += f"- Regra #{rule['id']}: {rule['description']}\n"
                output += f"  Ação: {rule['action']}\n"
                if 'matches' in rule:
                    output += "  Palavras-chave encontradas:\n"
                    for match in rule['matches']:
                        output += f"    - Encontrado: '{match['found']}' (palavra-chave: '{match['keyword']}')\n"
        
        # Adiciona exceções encontradas
        if excecoes:
            output += "\n#### Exceções Encontradas\n"
            for rule in excecoes:
                output += f"- Exceção #{rule['id']}: {rule['description']}\n"
                output += f"  Ação: {rule['action']}\n"
                if 'matches' in rule:
                    output += "  Palavras-chave encontradas:\n"
                    for match in rule['matches']:
                        output += f"    - Encontrado: '{match['found']}' (palavra-chave: '{match['keyword']}')\n"
        
        # Adiciona alertas
        if alertas:
            output += "\n#### Alertas Cadastrados\n"
            for rule in alertas:
                output += f"- Alerta #{rule['id']}: {rule['description']}\n"
                output += f"  Ação: {rule['action']}\n"
                if 'matches' in rule:
                    output += "  Palavras-chave encontradas:\n"
                    for match in rule['matches']:
                        output += f"    - Encontrado: '{match['found']}' (palavra-chave: '{match['keyword']}')\n"
        
        return output
