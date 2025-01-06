import json
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Rule:
    def __init__(self, name: str, pattern: str, category: str, priority: int = 1, exceptions: List[str] = None, action: str = "CADASTRAR_PORTAL", notify: str = None):
        self.name = name
        self.pattern = pattern
        self.category = category
        self.priority = priority
        self.exceptions = exceptions or []
        self.action = action
        self.notify = notify

class RulesManager:
    def __init__(self):
        self.rules_file = os.path.join(os.path.dirname(__file__), "..", "data", "rules.json")
        self.rules: Dict[str, List[Rule]] = {
            "pessoas_expostas": [],
            "instituicoes_sensiveis": [],
            "alertas": []
        }
        self.load_rules()

    def load_rules(self) -> None:
        """Carrega as regras do arquivo JSON."""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for category, rules in data.items():
                    self.rules[category] = [
                        Rule(
                            name=rule["name"],
                            pattern=rule["pattern"],
                            category=category,
                            priority=rule.get("priority", 1),
                            exceptions=rule.get("exceptions", []),
                            action=rule.get("action", "CADASTRAR_PORTAL"),
                            notify=rule.get("notify", None)
                        )
                        for rule in rules
                    ]
                logger.info("Regras carregadas com sucesso")
            else:
                self._create_default_rules()
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            self._create_default_rules()

    def _create_default_rules(self) -> None:
        """Cria regras padrão se o arquivo não existir."""
        default_rules = {
            "pessoas_expostas": [
                {
                    "name": "Autoridades",
                    "pattern": r"(Governador|Secretário|Deputado|Prefeito|Vereador)",
                    "priority": 2,
                    "exceptions": ["ex-", "antigo"]
                }
            ],
            "instituicoes_sensiveis": [
                {
                    "name": "Órgãos Públicos",
                    "pattern": r"(Secretaria|Ministério|Assembleia|Prefeitura)",
                    "priority": 2
                }
            ],
            "alertas": [
                {
                    "name": "Urgência",
                    "pattern": r"(URGENTE|PRIORIDADE|IMEDIATO)",
                    "priority": 3
                }
            ]
        }
        
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            json.dump(default_rules, f, indent=4, ensure_ascii=False)
        
        self.load_rules()

    def add_rule(self, category: str, name: str, pattern: str, priority: int = 1, exceptions: List[str] = None, action: str = "CADASTRAR_PORTAL", notify: str = None) -> bool:
        """Adiciona uma nova regra."""
        try:
            if category not in self.rules:
                return False
                
            rule = Rule(name, pattern, category, priority, exceptions, action, notify)
            self.rules[category].append(rule)
            self._save_rules()
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar regra: {str(e)}")
            return False

    def remove_rule(self, category: str, name: str) -> bool:
        """Remove uma regra existente."""
        try:
            if category not in self.rules:
                return False
            
            # Encontra a regra pelo nome
            rules = self.rules[category]
            for i, rule in enumerate(rules):
                if rule.name == name:
                    del rules[i]
                    self._save_rules()
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover regra: {str(e)}")
            return False

    def _save_rules(self) -> None:
        """Salva as regras no arquivo JSON."""
        try:
            rules_dict = {}
            for category, rules in self.rules.items():
                rules_dict[category] = [
                    {
                        "name": rule.name,
                        "pattern": rule.pattern,
                        "priority": rule.priority,
                        "exceptions": rule.exceptions,
                        "action": rule.action,
                        "notify": rule.notify
                    }
                    for rule in rules
                ]
            
            os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_dict, f, indent=4, ensure_ascii=False)
            
            logger.info("Regras salvas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar regras: {str(e)}")

    def check_rules(self, text: str) -> Dict[str, List[Dict]]:
        """Verifica o texto contra todas as regras e retorna as correspondências."""
        import re
        matches = {
            "pessoas_expostas": [],
            "instituicoes_sensiveis": [],
            "alertas": []
        }
        
        for category, rules in self.rules.items():
            for rule in rules:
                if re.search(rule.pattern, text, re.IGNORECASE):
                    # Verifica exceções
                    has_exception = any(
                        re.search(exc, text, re.IGNORECASE)
                        for exc in rule.exceptions
                    )
                    
                    if not has_exception:
                        matches[category].append({
                            "name": rule.name,
                            "priority": rule.priority,
                            "action": rule.action,
                            "notify": rule.notify
                        })
        
        return matches

    def get_rules(self, category: Optional[str] = None) -> Dict[str, List[Rule]]:
        """Retorna todas as regras ou apenas de uma categoria específica."""
        if category:
            return {category: self.rules.get(category, [])}
        return self.rules

# Singleton para gerenciar as regras
rules_manager = RulesManager()

def load_rules() -> Dict[str, List[Rule]]:
    """Função de conveniência para carregar as regras."""
    return rules_manager.get_rules()
