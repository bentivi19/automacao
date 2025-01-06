import customtkinter as ctk
from typing import Dict, List
import logging
from src.rules_engine.rules_manager import RulesManager
from src.ui.rules_dialog import RuleDialog

logger = logging.getLogger(__name__)

class RulesManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent, rules_manager: RulesManager):
        super().__init__(parent)
        
        self.rules_manager = rules_manager
        
        # Configuração da janela
        self.title("Gerenciador de Regras")
        self.geometry("1000x700")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame superior com os botões de tipo de regra
        self.type_frame = ctk.CTkFrame(self.main_frame)
        self.type_frame.pack(fill="x", padx=5, pady=5)
        
        self.current_type = "pre_analysis"
        
        # Botões para cada tipo de regra
        self.type_buttons = {}
        for rule_type, label in {
            'pre_analysis': 'Pré-Análise',
            'final_output': 'Saída Final',
            'alerts': 'Alertas',
            'exceptions': 'Exceções'
        }.items():
            btn = ctk.CTkButton(
                self.type_frame,
                text=label,
                command=lambda t=rule_type: self.show_rules(t)
            )
            btn.pack(side="left", padx=5)
            self.type_buttons[rule_type] = btn
        
        # Frame para a lista de regras
        self.list_frame = ctk.CTkFrame(self.main_frame)
        self.list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para a lista de regras
        self.rules_frame = ctk.CTkFrame(self.list_frame)
        self.rules_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Usar TextBox para exibir as regras ou texto consolidado
        self.rules_text = ctk.CTkTextbox(self.rules_frame, width=980, height=400)
        self.rules_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Variável para armazenar o texto consolidado
        self.consolidated_text = ""
        
        # Frame para seleção de regra por ID
        self.id_frame = ctk.CTkFrame(self.main_frame)
        self.id_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(self.id_frame, text="ID da Regra:").pack(side="left", padx=5)
        self.rule_id_entry = ctk.CTkEntry(self.id_frame, width=100)
        self.rule_id_entry.pack(side="left", padx=5)
        
        # Armazena as regras atuais
        self.current_rules = []
        
        # Botões de ação
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            self.action_frame,
            text="Nova Regra",
            command=self.add_rule
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.action_frame,
            text="Editar",
            command=self.edit_rule
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.action_frame,
            text="Excluir",
            command=self.delete_rule
        ).pack(side="left", padx=5)
        
        # Mostra as regras iniciais
        self.show_rules("pre_analysis")

    def show_rules(self, rule_type: str):
        """Mostra as regras do tipo selecionado ou o texto consolidado para Saída Final."""
        self.current_type = rule_type
        
        self.rules_text.delete("1.0", "end")
        
        if rule_type == 'final_output':
            if self.consolidated_text:
                self.rules_text.insert("end", self.consolidated_text)
            else:
                self.rules_text.insert("end", "Nenhum texto consolidado disponível.")
            return
            
        self.current_rules = self.rules_manager.get_rules(rule_type)
        
        if not self.current_rules:
            self.rules_text.insert("end", f"Nenhuma regra do tipo {rule_type} encontrada.")
            return
        
        # Exibe as regras formatadas
        for rule in self.current_rules:
            rule_text = f"ID: {rule['id']}\n"
            rule_text += f"Nome: {rule['name']}\n"
            rule_text += f"Descrição: {rule['description']}\n"
            
            # Formata a condição de forma mais legível
            condition = rule.get('condition', '')
            if condition:
                # Destaca os conectivos lógicos
                condition = condition.replace(" e ", "\n  E ")
                condition = condition.replace(" ou ", "\n  OU ")
                condition = condition.replace(" se não (for) ", "\n  SE NÃO (for) ")
            rule_text += f"Condição:\n  {condition}\n"
            
            # Tenta obter a ação de ambos os campos possíveis
            action = rule.get('action', rule.get('recommended_action', 'Ação não especificada'))
            rule_text += f"Ação Recomendada: {action}\n"
            rule_text += f"Prioridade: {rule.get('priority', 'Média')}\n"
            
            # Adiciona timestamps se disponíveis
            if 'created_at' in rule:
                rule_text += f"Criado em: {rule['created_at']}\n"
            if 'updated_at' in rule:
                rule_text += f"Atualizado em: {rule['updated_at']}\n"
            
            rule_text += "-" * 50 + "\n\n"
            self.rules_text.insert("end", rule_text)
    
    def add_rule(self):
        """Adiciona uma nova regra."""
        def save_new_rule(rule_data: Dict):
            try:
                if self.rules_manager.add_rule(self.current_type, rule_data):
                    self.show_rules(self.current_type)
                else:
                    logging.error("Falha ao adicionar nova regra")
            except Exception as e:
                logging.error(f"Erro ao adicionar regra: {str(e)}")
                
        dialog = RuleDialog(self, self.current_type, save_new_rule)
        dialog.focus_force()  # Força o foco na janela
        self.wait_window(dialog)
    
    def edit_rule(self):
        """Edita a regra selecionada."""
        rule_id = self.rule_id_entry.get()
        if not rule_id:
            logging.error("Nenhum ID de regra fornecido para edição")
            return
        
        try:
            rule_id = int(rule_id)
            rule = next((r for r in self.current_rules if r['id'] == rule_id), None)
            
            if not rule:
                logging.error(f"Regra com ID {rule_id} não encontrada")
                return
                
            def save_edited_rule(rule_data: Dict):
                try:
                    if self.rules_manager.update_rule(self.current_type, rule_id, rule_data):
                        self.show_rules(self.current_type)
                    else:
                        logging.error("Falha ao atualizar regra")
                except Exception as e:
                    logging.error(f"Erro ao atualizar regra: {str(e)}")
            
            dialog = RuleDialog(self, self.current_type, save_edited_rule, rule)
            dialog.focus_force()  # Força o foco na janela
            self.wait_window(dialog)
            
        except ValueError:
            logging.error("ID de regra inválido")
    
    def delete_rule(self):
        """Exclui a regra selecionada."""
        rule_id = self.rule_id_entry.get()
        if not rule_id:
            logging.error("Nenhum ID de regra fornecido para exclusão")
            return
        
        try:
            rule_id = int(rule_id)
            if self.rules_manager.delete_rule(self.current_type, rule_id):
                self.show_rules(self.current_type)
            else:
                logging.error(f"Não foi possível excluir a regra com ID {rule_id}")
        except ValueError:
            logging.error("ID de regra inválido")

    def update_consolidated_text(self, text: str):
        """Atualiza o texto consolidado e mostra na interface se estiver na aba Saída Final."""
        self.consolidated_text = text
        if self.current_type == 'final_output':
            self.rules_text.delete("1.0", "end")
            self.rules_text.insert("end", text)

    def run(self):
        """Inicia a execução da interface."""
        self.mainloop()
