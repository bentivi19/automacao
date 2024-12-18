import customtkinter as ctk
import logging
from tkinter import filedialog
from pathlib import Path

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        self.current_text = ""
        
        # Configuração da janela
        self.title("Analisador de Documentos")
        self.geometry("1000x800")
        
        # Criação dos widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame superior para seleção de arquivo
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", padx=5, pady=5)
        
        # Botão para selecionar arquivo
        self.select_file_btn = ctk.CTkButton(
            self.top_frame, 
            text="Selecionar Arquivo",
            command=self.select_file
        )
        self.select_file_btn.pack(side="left", padx=5)
        
        # Campo de texto para mostrar o caminho do arquivo
        self.file_path_label = ctk.CTkLabel(self.top_frame, text="Nenhum arquivo selecionado")
        self.file_path_label.pack(side="left", padx=5)
        
        # Frame para resultados e perguntas
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Área de texto para mostrar resultados
        self.result_text = ctk.CTkTextbox(self.content_frame, height=400)
        self.result_text.pack(fill="both", expand=True, pady=5)
        
        # Frame para perguntas
        self.question_frame = ctk.CTkFrame(self.content_frame)
        self.question_frame.pack(fill="x", pady=5)
        
        # Campo para digitar pergunta
        self.question_entry = ctk.CTkEntry(
            self.question_frame,
            placeholder_text="Digite sua pergunta sobre o documento...",
            width=400
        )
        self.question_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botão para enviar pergunta
        self.ask_button = ctk.CTkButton(
            self.question_frame,
            text="Perguntar",
            command=self.ask_question,
            state="disabled"
        )
        self.ask_button.pack(side="right", padx=5)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                self.file_path_label.configure(text=f"Arquivo: {Path(file_path).name}")
                
                # Processa o documento
                result = self.analyzer.process_document(file_path)
                self.current_text = result.get('text', '')
                
                # Mostra o resultado
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", result.get('analysis', ''))
                
                # Habilita o botão de perguntas
                self.ask_button.configure(state="normal")
                
            except Exception as e:
                logger.error(f"Erro ao processar arquivo: {str(e)}")
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", f"Erro ao processar arquivo: {str(e)}")
                self.ask_button.configure(state="disabled")
    
    def ask_question(self):
        question = self.question_entry.get()
        if not question:
            return
        
        try:
            # Faz a pergunta ao analisador
            answer = self.analyzer.mistral_client.ask_question(self.current_text, question)
            
            # Adiciona a pergunta e resposta ao resultado
            self.result_text.insert("end", f"\n\nPergunta: {question}\nResposta: {answer}")
            
            # Limpa o campo de pergunta
            self.question_entry.delete(0, "end")
            
        except Exception as e:
            logger.error(f"Erro ao fazer pergunta: {str(e)}")
            self.result_text.insert("end", f"\n\nErro ao responder pergunta: {str(e)}")
    
    def run(self):
        """Inicia a execução da interface."""
        self.mainloop()
