import os
import yaml
import logging
from pathlib import Path
from string import Template
from typing import Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/email_sender.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmailManager:
    def __init__(self, templates_dir: str = 'config/templates'):
        """Inicializa o gerenciador de emails.
        
        Args:
            templates_dir: Diretório contendo os templates de email
        """
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Template]:
        """Carrega os templates de email do diretório."""
        templates = {}
        try:
            for template_file in self.templates_dir.glob('*.txt'):
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates[template_file.stem] = Template(f.read())
            return templates
        except Exception as e:
            logger.error(f"Erro ao carregar templates: {str(e)}")
            return {}

    def create_email(self, 
                    template_name: str, 
                    data: dict,
                    department: str) -> Optional[MIMEMultipart]:
        """Cria um email usando o template especificado.
        
        Args:
            template_name: Nome do template a ser usado
            data: Dados para preencher o template
            department: Departamento destinatário
            
        Returns:
            Objeto MIMEMultipart com o email formatado
        """
        try:
            if template_name not in self.templates:
                raise ValueError(f"Template '{template_name}' não encontrado")

            # Cria o email
            msg = MIMEMultipart()
            msg['Subject'] = f"Requisição de Instauração - {data.get('numero_nf', 'N/A')}"
            msg['From'] = "seu_email@mp.sp.gov.br"  # Configurar email correto
            msg['To'] = self._get_department_email(department)

            # Preenche o template
            body = self.templates[template_name].safe_substitute(data)
            msg.attach(MIMEText(body, 'plain'))

            return msg

        except Exception as e:
            logger.error(f"Erro ao criar email: {str(e)}")
            return None

    def _get_department_email(self, department: str) -> str:
        """Retorna o email do departamento."""
        # Carregar de um arquivo de configuração ou usar um dicionário
        department_emails = {
            'DEIC': 'deic@policiacivil.sp.gov.br',
            'DEINTER': 'deinter@policiacivil.sp.gov.br',
            'DECRADI': 'decradi@policiacivil.sp.gov.br',
            'DECAP': 'decap@policiacivil.sp.gov.br',
            'DHPP': 'dhpp@policiacivil.sp.gov.br',
            'DPPC': 'dppc@policiacivil.sp.gov.br'
        }
        return department_emails.get(department, '')

    def save_draft(self, 
                   email: MIMEMultipart, 
                   output_dir: str = 'drafts') -> bool:
        """Salva o email como rascunho.
        
        Args:
            email: Email formatado
            output_dir: Diretório para salvar o rascunho
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"draft_{email['Subject'].replace(' ', '_')}.eml"
            path = os.path.join(output_dir, filename)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(email.as_string())
            
            logger.info(f"Rascunho salvo em: {path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar rascunho: {str(e)}")
            return False
