import customtkinter as ctk
import logging
from tkinter import filedialog
from pathlib import Path
from queue import Queue
import threading

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        self.current_text = ""
        self.queue = Queue()
        
        # Configuração da janela
        self.title("Analisador de Documentos")
        self.geometry("800x600")
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame superior
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", padx=5, pady=5)
        
        # Botão para selecionar arquivo
        self.select_button = ctk.CTkButton(
            self.top_frame, 
            text="Selecionar Arquivo",
            command=self.select_file
        )
        self.select_button.pack(side="left", padx=5)
        
        # Label para mostrar o arquivo selecionado
        self.file_path_label = ctk.CTkLabel(self.top_frame, text="Nenhum arquivo selecionado")
        self.file_path_label.pack(side="left", padx=5)
        
        # Frame para o resultado
        self.result_frame = ctk.CTkFrame(self.main_frame)
        self.result_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Widget de texto para mostrar o resultado
        self.result_text = ctk.CTkTextbox(self.result_frame)
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame inferior para perguntas
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)
        
        # Entry para perguntas
        self.question_entry = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text="Digite sua pergunta aqui..."
        )
        self.question_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Botão para fazer pergunta
        self.ask_button = ctk.CTkButton(
            self.bottom_frame,
            text="Perguntar",
            command=self.ask_question,
            state="disabled"
        )
        self.ask_button.pack(side="right", padx=5)
    
    def select_file(self):
        """Abre diálogo para selecionar arquivo PDF."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.current_file = file_path
                self.file_path_label.configure(text=f"Arquivo: {Path(file_path).name}")
                
                # Processa o documento
                self.process_file(file_path)
                
            except Exception as e:
                logger.error(f"Erro ao processar arquivo: {str(e)}")
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", f"Erro ao processar arquivo: {str(e)}")
                self.ask_button.configure(state="disabled")
    
    def process_file(self, file_path):
        """Processa o arquivo selecionado."""
        if not file_path:
            return
        
        try:
            # Mostra mensagem de processamento
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", "Processando arquivo...\n")
            self.result_text.update()
            
            # Processa o arquivo
            result = self.analyzer.process_document(file_path)
            
            # Limpa o widget
            self.result_text.delete("1.0", "end")
            
            # Mostra o resultado
            if result:
                self.result_text.insert("end", "Análise do Documento:\n\n")
                
                # Informações básicas
                if result.get("basic_info"):
                    self.result_text.insert("end", "Informações Básicas:\n")
                    for key, value in result["basic_info"].items():
                        self.result_text.insert("end", f"{key}: {value}\n")
                    self.result_text.insert("end", "\n")
                
                # Análise
                if result.get("analysis"):
                    self.result_text.insert("end", "Análise:\n")
                    for key, value in result["analysis"].items():
                        self.result_text.insert("end", f"{key}: {value}\n")
                    self.result_text.insert("end", "\n")
                
                # Conclusão
                if result.get("conclusion"):
                    self.result_text.insert("end", "Conclusão:\n")
                    for key, value in result["conclusion"].items():
                        self.result_text.insert("end", f"{key}: {value}\n")
            
            # Atualiza a interface
            self.result_text.update()
            self.current_text = result.get('text', '')
            self.ask_button.configure(state="normal")
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {str(e)}")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"Erro ao processar arquivo: {str(e)}")
            self.ask_button.configure(state="disabled")
    
    def ask_question(self):
        """Processa uma pergunta sobre o documento."""
        question = self.question_entry.get()
        if not question:
            return
            
        try:
            # Mostra mensagem de processamento
            self.result_text.insert("end", "\nProcessando pergunta...\n")
            self.result_text.update()
            
            # Obtém resposta
            answer = self.analyzer.answer_question(question, self.current_text)
            
            # Mostra a resposta
            self.result_text.insert("end", f"\nPergunta: {question}\n")
            self.result_text.insert("end", f"Resposta: {answer}\n")
            
            # Limpa o campo de pergunta
            self.question_entry.delete(0, "end")
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            self.result_text.insert("end", f"\nErro ao processar pergunta: {str(e)}\n")
    
    def run(self):
        """Inicia a execução da interface."""
        self.mainloop()
