import os
import re
import yaml
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

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
            rules_path = project_root / 'config' / 'rules' / 'dispatch_rules.yaml'
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                self.rules = yaml.safe_load(f)
                
            logger.info("Regras carregadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            self.rules = {'rules': [], 'settings': {}}

    def _load_rules(self) -> dict:
        """Carrega as regras do arquivo YAML."""
        try:
            # Obtém o caminho absoluto para o diretório do projeto
            project_root = Path(__file__).parent.parent.parent
            rules_path = project_root / 'config' / 'rules' / 'dispatch_rules.yaml'
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            return {}

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

    def process_rules(self, text: str) -> str:
        """Processa o texto usando as regras definidas.
        
        Args:
            text: Texto a ser processado
            
        Returns:
            str: Texto processado com os resultados da análise
        """
        try:
            results = {}
            
            # Processa cada regra
            for rule in self.rules.get('rules', []):
                rule_name = rule.get('name')
                patterns = rule.get('patterns', [])
                action = rule.get('action')
                
                matches = []
                for pattern in patterns:
                    found = re.finditer(pattern, text)
                    matches.extend([m.group() for m in found])
                
                if matches:
                    results[rule_name] = matches
            
            # Formata os resultados como texto
            output = []
            output.append("Resultados da análise:")
            for rule_name, matches in results.items():
                output.append(f"\n{rule_name}:")
                for match in matches:
                    output.append(f"  - {match}")
            
            return "\n".join(output) if results else text
            
        except Exception as e:
            logger.error(f"Erro ao processar regras: {str(e)}")
            return text
