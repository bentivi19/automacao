import logging
import requests
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class LegalKnowledgeBase:
    """Base de conhecimento jurídico e policial."""
    
    def __init__(self):
        self.cache_dir = Path("cache/knowledge")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge = {}
        self.last_update = None
        
        # URLs para fontes de dados (exemplo)
        self.sources = {
            "legislacao": {
                "penal": "https://www.planalto.gov.br/api/legislacao/penal",
                "civil": "https://www.planalto.gov.br/api/legislacao/civil",
                "eca": "https://www.planalto.gov.br/api/legislacao/eca",
                "idoso": "https://www.planalto.gov.br/api/legislacao/idoso",
                "tributario": "https://www.planalto.gov.br/api/legislacao/tributario",
                "trabalhista": "https://www.planalto.gov.br/api/legislacao/trabalhista"
            },
            "jurisprudencia": {
                "stf": "https://jurisprudencia.stf.jus.br/api",
                "stj": "https://jurisprudencia.stj.jus.br/api",
                "tjsp": "https://jurisprudencia.tjsp.jus.br/api"
            },
            "policia": {
                "organograma": "https://www.policiacivil.sp.gov.br/api/organograma",
                "contatos": "https://www.policiacivil.sp.gov.br/api/contatos",
                "departamentos": "https://www.policiacivil.sp.gov.br/api/departamentos"
            }
        }
        
        # Estrutura da Polícia Civil de SP
        self.police_structure = {
            "DEIC": {
                "nome": "Departamento Estadual de Investigações Criminais",
                "divisoes": [
                    "1ª Delegacia - Investigações Gerais",
                    "2ª Delegacia - Roubo a Bancos",
                    "3ª Delegacia - Investigações sobre Estelionato",
                    "4ª Delegacia - Investigações sobre Crimes Contra o Patrimônio",
                    "5ª Delegacia - Investigações sobre Roubo e Latrocínio",
                    "6ª Delegacia - Investigações sobre Crime Organizado",
                    "7ª Delegacia - Investigações sobre Crimes Contra a Administração"
                ]
            },
            "DHPP": {
                "nome": "Departamento de Homicídios e Proteção à Pessoa",
                "divisoes": [
                    "Divisão de Homicídios",
                    "Divisão de Proteção à Pessoa",
                    "Divisão de Crimes contra o Patrimônio"
                ]
            },
            "DECRADI": {
                "nome": "Delegacia de Crimes Raciais e Delitos de Intolerância",
                "atribuicoes": [
                    "Crimes de racismo",
                    "Crimes de intolerância religiosa",
                    "Crimes de homofobia",
                    "Crimes de xenofobia"
                ]
            },
            "DECAP": {
                "nome": "Departamento de Polícia Judiciária da Capital",
                "atribuicoes": [
                    "Coordenação dos distritos policiais da capital",
                    "Investigação de crimes na capital"
                ]
            },
            "DEINTER": {
                "nome": "Departamento de Polícia Judiciária do Interior",
                "regioes": [
                    "DEINTER 1 - São José dos Campos",
                    "DEINTER 2 - Campinas",
                    "DEINTER 3 - Ribeirão Preto",
                    "DEINTER 4 - Bauru",
                    "DEINTER 5 - São José do Rio Preto",
                    "DEINTER 6 - Santos",
                    "DEINTER 7 - Sorocaba",
                    "DEINTER 8 - Presidente Prudente",
                    "DEINTER 9 - Piracicaba",
                    "DEINTER 10 - Araçatuba"
                ]
            }
        }
    
    def initialize(self):
        """Inicializa a base de conhecimento."""
        logger.info("Inicializando base de conhecimento jurídica e policial...")
        
        try:
            # Carrega dados do cache se existirem e forem recentes
            if self._load_from_cache():
                logger.info("Dados carregados do cache com sucesso")
                return
            
            # Se não houver cache ou estiver desatualizado, busca dados novos
            self._fetch_legal_data()
            self._fetch_police_data()
            self._save_to_cache()
            
            logger.info("Base de conhecimento inicializada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar base de conhecimento: {str(e)}")
            # Em caso de erro, tenta usar dados do cache mesmo que antigos
            self._load_from_cache(force=True)
    
    def _load_from_cache(self, force=False) -> bool:
        """Carrega dados do cache se existirem e forem recentes."""
        cache_file = self.cache_dir / "legal_knowledge.json"
        
        if not cache_file.exists():
            return False
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            last_update = datetime.fromisoformat(data.get('last_update', '2000-01-01'))
            
            # Verifica se o cache é recente (menos de 24h) ou se está sendo forçado
            if force or (datetime.now() - last_update).days < 1:
                self.knowledge = data.get('knowledge', {})
                self.last_update = last_update
                return True
                
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
            
        return False
    
    def _save_to_cache(self):
        """Salva dados atuais no cache."""
        cache_file = self.cache_dir / "legal_knowledge.json"
        
        try:
            data = {
                'knowledge': self.knowledge,
                'last_update': datetime.now().isoformat()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def _fetch_legal_data(self):
        """Busca dados jurídicos atualizados."""
        logger.info("Buscando dados jurídicos atualizados...")
        
        # Aqui você implementaria as chamadas reais às APIs
        # Por enquanto, vamos usar dados estáticos
        self.knowledge['legislacao'] = {
            'penal': {
                'codigo': 'Decreto-Lei nº 2.848/1940',
                'atualizacao': 'Lei 14.344/2022'
            },
            'civil': {
                'codigo': 'Lei nº 10.406/2002',
                'atualizacao': 'Lei 14.382/2022'
            }
        }
    
    def _fetch_police_data(self):
        """Busca dados atualizados da estrutura policial."""
        logger.info("Buscando dados da estrutura policial...")
        
        # Aqui você implementaria as chamadas reais às APIs
        self.knowledge['policia'] = self.police_structure
    
    def get_department_info(self, department: str) -> Optional[Dict]:
        """Retorna informações sobre um departamento específico."""
        return self.knowledge.get('policia', {}).get(department.upper())
    
    def get_legal_info(self, area: str) -> Optional[Dict]:
        """Retorna informações sobre uma área jurídica específica."""
        return self.knowledge.get('legislacao', {}).get(area.lower())
    
    def search(self, query: str) -> List[Dict]:
        """Pesquisa na base de conhecimento."""
        results = []
        query = query.lower()
        
        # Pesquisa em departamentos
        for dep_name, dep_info in self.knowledge.get('policia', {}).items():
            if query in dep_name.lower() or query in dep_info.get('nome', '').lower():
                results.append({
                    'tipo': 'departamento',
                    'nome': dep_name,
                    'info': dep_info
                })
        
        # Pesquisa em legislação
        for area, info in self.knowledge.get('legislacao', {}).items():
            if query in area or query in str(info).lower():
                results.append({
                    'tipo': 'legislacao',
                    'area': area,
                    'info': info
                })
        
        return results
