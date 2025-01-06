import customtkinter as ctk
from src.rules_engine.rules_manager import RulesManager
from src.ui.rules_dialog import RuleDialog
from tkinter import messagebox

class RulesRegistrationDialog(ctk.CTkToplevel):
    def __init__(self, master, rules_manager: RulesManager):
        super().__init__(master)
        self.title("Cadastro de Regras")
        self.geometry("400x200")
        self.rules_manager = rules_manager

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Tipo de Regra
        ctk.CTkLabel(main_frame, text="Selecione o Tipo de Regra:").pack(pady=(10, 0))
        self.rule_type_var = ctk.StringVar(value="pre_analysis")
        rule_type_combo = ctk.CTkOptionMenu(
            main_frame,
            values=["pre_analysis", "final_output", "alerts", "exceptions"],
            variable=self.rule_type_var
        )
        rule_type_combo.pack(pady=(0, 10))

        # Botões
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Nova Regra",
            command=self.create_rule
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side="right", padx=5)

    def create_rule(self):
        """Abre o diálogo de criação de regra."""
        def on_save(rule_data: dict):
            try:
                # Adiciona a regra usando o RulesManager
                self.rules_manager.add_rule(
                    rule_type=self.rule_type_var.get(),
                    rule_data=rule_data
                )
                self.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar regra: {str(e)}")

        # Abre o diálogo de regra
        dialog = RuleDialog(
            self,
            rule_type=self.rule_type_var.get(),
            on_save=on_save
        )
        self.wait_window(dialog)
