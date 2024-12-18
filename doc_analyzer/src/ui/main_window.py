import customtkinter as ctk
from tkinter import filedialog
import logging
from pathlib import Path
from typing import Callable, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ui.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MainWindow:
    def __init__(self):
        """Inicializa a janela principal."""
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configura a janela principal."""
        self.window = ctk.CTk()
        self.window.title("Analisador de Documentos")
        self.window.geometry("800x600")
        
        # Configura o tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def create_widgets(self):
        """Cria os widgets da interface."""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Analisador de Documentos Jurídicos",
            font=("Roboto", 24)
        )
        self.title_label.pack(pady=20)

        # Frame para seleção de arquivo
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.pack(fill="x", padx=20, pady=10)

        self.file_label = ctk.CTkLabel(
            self.file_frame,
            text="Nenhum arquivo selecionado",
            font=("Roboto", 12)
        )
        self.file_label.pack(side="left", padx=10)

        self.select_file_btn = ctk.CTkButton(
            self.file_frame,
            text="Selecionar PDF",
            command=self.select_file
        )
        self.select_file_btn.pack(side="right", padx=10)

        # Frame para output
        self.output_frame = ctk.CTkFrame(self.main_frame)
        self.output_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.output_text = ctk.CTkTextbox(
            self.output_frame,
            wrap="word",
            font=("Roboto", 12)
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame para botões de ação
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.pack(fill="x", padx=20, pady=10)

        self.analyze_btn = ctk.CTkButton(
            self.action_frame,
            text="Analisar Documento",
            command=self.analyze_document,
            state="disabled"
        )
        self.analyze_btn.pack(side="left", padx=10)

        self.save_btn = ctk.CTkButton(
            self.action_frame,
            text="Salvar Análise",
            command=self.save_analysis,
            state="disabled"
        )
        self.save_btn.pack(side="right", padx=10)

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.progress_bar.hide()

    def select_file(self):
        """Abre diálogo para seleção de arquivo PDF."""
        file_path = filedialog.askopenfilename(
            title="Selecione o PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self.file_label.configure(text=self.current_file.name)
            self.analyze_btn.configure(state="normal")
            logger.info(f"Arquivo selecionado: {file_path}")

    def analyze_document(self):
        """Inicia a análise do documento."""
        if not hasattr(self, 'current_file'):
            return

        self.progress_bar.show()
        self.progress_bar.start()
        self.analyze_btn.configure(state="disabled")
        self.select_file_btn.configure(state="disabled")
        
        # Aqui será integrada a análise do documento
        # Por enquanto apenas simula o processo
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", "Analisando documento...\n")
        
        # Habilita o botão de salvar após a análise
        self.save_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_bar.hide()

    def save_analysis(self):
        """Salva a análise em um arquivo de texto."""
        if not self.output_text.get("0.0", "end").strip():
            return

        save_path = filedialog.asksaveasfilename(
            title="Salvar Análise",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.get("0.0", "end"))
                logger.info(f"Análise salva em: {save_path}")
            except Exception as e:
                logger.error(f"Erro ao salvar análise: {str(e)}")

    def run(self):
        """Inicia a execução da interface."""
        self.window.mainloop()
