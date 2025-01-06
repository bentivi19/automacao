import customtkinter as ctk
from typing import Optional, Dict, Callable
import logging
from src.rules_engine.rules_manager import RulesManager

logger = logging.getLogger(__name__)

class RuleDialog(ctk.CTkToplevel):
    def __init__(self, parent, rule_type: str, on_save: Callable, 
                 existing_rule: Optional[Dict] = None):
        super().__init__(parent)
        
        self.rule_type = rule_type
        self.on_save = on_save
        self.existing_rule = existing_rule
        self.conditions = []
        
        # Configuração da janela
        self.title(f"{'Editar' if existing_rule else 'Nova'} Regra - {rule_type}")
        self.geometry("800x600")
        
        # Frame principal com scroll
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campos do formulário
        self._create_form()
        
        if existing_rule:
            self._load_existing_rule()
        
        # Força o foco na janela
        self.focus_force()

    def _create_form(self):
        """Cria os campos do formulário."""
        # Nome da regra
        ctk.CTkLabel(self.main_frame, text="Nome da Regra:").pack(anchor="w", padx=5, pady=2)
        self.name_entry = ctk.CTkEntry(self.main_frame, width=400)
        self.name_entry.pack(anchor="w", padx=5, pady=2)
        
        # Descrição
        ctk.CTkLabel(self.main_frame, text="Descrição da Regra:").pack(anchor="w", padx=5, pady=2)
        self.description_text = ctk.CTkTextbox(self.main_frame, width=400, height=60)
        self.description_text.pack(anchor="w", padx=5, pady=2)
        
        # Frame para condições
        self.conditions_frame = ctk.CTkFrame(self.main_frame)
        self.conditions_frame.pack(fill="x", padx=5, pady=5)
        
        # Label para condições
        ctk.CTkLabel(self.conditions_frame, text="Condições:").pack(anchor="w", padx=5, pady=2)
        
        # Primeira condição (sempre começa com "Se")
        self._add_condition_row(is_first=True)
        
        # Botão para adicionar mais condições
        self.add_condition_button = ctk.CTkButton(
            self.conditions_frame,
            text="+ Adicionar Condição",
            command=lambda: self._add_condition_row(is_first=False)
        )
        self.add_condition_button.pack(anchor="w", padx=5, pady=5)
        
        # Ação Recomendada
        ctk.CTkLabel(self.main_frame, text="Ação Recomendada:").pack(anchor="w", padx=5, pady=2)
        self.action_text = ctk.CTkTextbox(self.main_frame, width=400, height=60)
        self.action_text.pack(anchor="w", padx=5, pady=2)
        
        # Prioridade
        ctk.CTkLabel(self.main_frame, text="Prioridade:").pack(anchor="w", padx=5, pady=2)
        self.priority_var = ctk.StringVar(value="Média")
        self.priority_menu = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Baixa", "Média", "Alta", "Crítica"],
            variable=self.priority_var
        )
        self.priority_menu.pack(anchor="w", padx=5, pady=2)
        
        # Botões de ação
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            self.button_frame,
            text="Salvar",
            command=self._save_rule
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            self.button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side="right", padx=5)

    def _add_condition_row(self, is_first: bool = False):
        """Adiciona uma nova linha de condição."""
        condition_frame = ctk.CTkFrame(self.conditions_frame)
        condition_frame.pack(fill="x", padx=5, pady=2)
        
        # Prefixo "Se" para primeira condição ou conectivo para as demais
        if is_first:
            ctk.CTkLabel(condition_frame, text="Se").pack(side="left", padx=2)
            connector_var = None
        else:
            connector_var = ctk.StringVar(value="e")
            connector = ctk.CTkOptionMenu(
                condition_frame,
                values=["e", "ou", "se não (for)"],
                variable=connector_var,
                width=100
            )
            connector.pack(side="left", padx=2)
        
        # Campo para agente
        agent_entry = ctk.CTkEntry(condition_frame, width=200, placeholder_text="agente")
        agent_entry.pack(side="left", padx=2)
        
        # Campo para ação/condição
        action_entry = ctk.CTkEntry(condition_frame, width=200, placeholder_text="ação/condição")
        action_entry.pack(side="left", padx=2)
        
        # Botão remover (exceto primeira condição)
        if not is_first:
            remove_button = ctk.CTkButton(
                condition_frame,
                text="X",
                width=30,
                command=lambda: self._remove_condition_row(condition_frame)
            )
            remove_button.pack(side="left", padx=2)
        
        # Armazena referências
        self.conditions.append({
            'frame': condition_frame,
            'connector': connector_var,
            'agent': agent_entry,
            'action': action_entry
        })

    def _remove_condition_row(self, frame):
        """Remove uma linha de condição."""
        # Encontra e remove a condição da lista
        self.conditions = [c for c in self.conditions if c['frame'] != frame]
        frame.destroy()

    def _build_condition_string(self) -> str:
        """Constrói a string de condição a partir dos campos."""
        condition_parts = []
        
        for i, condition in enumerate(self.conditions):
            agent = condition['agent'].get().strip()
            action = condition['action'].get().strip()
            
            if not agent or not action:
                continue
                
            if i == 0:
                condition_parts.append(f"Se {agent} {action}")
            else:
                connector = condition['connector'].get()
                condition_parts.append(f"{connector} {agent} {action}")
        
        return " ".join(condition_parts)

    def _parse_condition_string(self, condition: str):
        """Parseia uma string de condição para os campos."""
        # Limpa condições existentes
        for c in self.conditions:
            c['frame'].destroy()
        self.conditions = []
        
        # Divide a condição em partes
        parts = condition.split(" ")
        current_part = []
        conditions_text = []
        
        for part in parts:
            if part.lower() in ['e', 'ou', 'se']:
                if current_part:
                    conditions_text.append(" ".join(current_part))
                    current_part = []
                if part.lower() != 'se':
                    conditions_text.append(part.lower())
            else:
                current_part.append(part)
        
        if current_part:
            conditions_text.append(" ".join(current_part))
        
        # Cria campos para cada condição
        for i, text in enumerate(conditions_text):
            if text not in ['e', 'ou', 'se não (for)']:
                self._add_condition_row(is_first=(i == 0))
                if i > 0:
                    self.conditions[-1]['connector'].set(conditions_text[i-1])
                
                # Tenta separar agente e ação
                parts = text.split(" ", 1)
                if len(parts) == 2:
                    self.conditions[-1]['agent'].insert(0, parts[0])
                    self.conditions[-1]['action'].insert(0, parts[1])
                else:
                    self.conditions[-1]['action'].insert(0, text)

    def _save_rule(self):
        """Salva a regra e fecha o diálogo."""
        try:
            # Validação dos campos obrigatórios
            name = self.name_entry.get().strip()
            description = self.description_text.get('1.0', 'end-1c').strip()
            action = self.action_text.get('1.0', 'end-1c').strip()
            
            if not name:
                raise ValueError("O nome da regra é obrigatório")
            if not description:
                raise ValueError("A descrição da regra é obrigatória")
            if not action:
                raise ValueError("A ação recomendada é obrigatória")
            
            # Constrói a condição
            condition = self._build_condition_string()
            if not condition:
                raise ValueError("Pelo menos uma condição completa é obrigatória")
            
            rule_data = {
                'name': name,
                'description': description,
                'condition': condition,
                'action': action,
                'priority': self.priority_var.get(),
                'type': self.rule_type
            }
            
            if self.existing_rule:
                rule_data['id'] = self.existing_rule['id']
            
            # Chama o callback passando os dados validados
            self.on_save(rule_data)
            
            # Fecha o diálogo apenas se não houver exceções
            self.destroy()
            
        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Erro ao salvar regra: {str(e)}")
            self._show_error("Erro ao salvar regra. Verifique o log para mais detalhes.")

    def _load_existing_rule(self):
        """Carrega os dados de uma regra existente nos campos."""
        if not self.existing_rule:
            return
            
        self.name_entry.insert(0, self.existing_rule.get('name', ''))
        self.description_text.insert('1.0', self.existing_rule.get('description', ''))
        self.action_text.insert('1.0', self.existing_rule.get('action', ''))
        self.priority_var.set(self.existing_rule.get('priority', 'Média'))
        
        # Carrega condições
        condition = self.existing_rule.get('condition', '')
        if condition:
            self._parse_condition_string(condition)

    def _show_error(self, message: str):
        """Mostra uma mensagem de erro para o usuário."""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Erro")
        error_dialog.geometry("400x150")
        
        # Centraliza o diálogo
        error_dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (error_dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (error_dialog.winfo_height() // 2)
        error_dialog.geometry(f"+{x}+{y}")
        
        # Conteúdo do diálogo
        frame = ctk.CTkFrame(error_dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame, 
            text=message,
            wraplength=350
        ).pack(pady=20)
        
        ctk.CTkButton(
            frame,
            text="OK",
            command=error_dialog.destroy
        ).pack(pady=10)
        
        # Força o foco no diálogo de erro
        error_dialog.focus_force()
        error_dialog.grab_set()
