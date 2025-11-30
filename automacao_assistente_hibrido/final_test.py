"""
Script final combinando as melhores partes dos testes anteriores
"""
import pyautogui
import time
import re
import tkinter as tk
from tkinter import messagebox
import logging
import clipboard

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction_debug.log'),
        logging.StreamHandler()
    ]
)

class ExtractionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extrator de Dados")
        self.root.geometry("600x500")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        self.setup_gui()
        
    def setup_gui(self):
        # Título
        title = tk.Label(self.root, 
                        text="Extrator de Dados Web → Excel",
                        font=("Arial", 16, "bold"),
                        bg='#f0f0f0')
        title.pack(pady=15)

        # Instruções
        instructions = """
1. Abra a página com os dados que deseja copiar
2. Abra o Excel onde deseja colar
3. Volte para a página com os dados
4. Clique em 'Iniciar Extração'
5. O programa irá:
   - Selecionar o texto automaticamente
   - Extrair os números e promotorias
   - Colar no Excel em A1 e B1
        """
        tk.Label(self.root, 
                text=instructions,
                justify=tk.LEFT,
                bg='#f0f0f0',
                font=("Arial", 11)).pack(pady=15, padx=25)

        # Botão de extração
        self.extract_btn = tk.Button(self.root,
                                   text="Iniciar Extração",
                                   command=self.start_extraction,
                                   bg='#4CAF50',
                                   fg='white',
                                   font=("Arial", 12, "bold"),
                                   width=20,
                                   height=2)
        self.extract_btn.pack(pady=20)

        # Log na interface
        self.log_text = tk.Text(self.root, height=12, width=70)
        self.log_text.pack(pady=10, padx=20)

    def log_message(self, message):
        logging.debug(message)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def extract_data(self):
        """Extrai números de processo e promotorias do texto"""
        try:
            # Seleciona todo o texto
            self.log_message("Selecionando texto...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # Copia o texto
            self.log_message("Copiando texto...")
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            # Pega o texto do clipboard
            text = clipboard.paste()
            self.log_message(f"Texto capturado (trecho):\n{text[:200]}...")
            
            # Procura por números de processo (ajustado para seu formato)
            number_pattern = r'\d{4}\.\d{7}/\d{4}'
            promotoria_pattern = r'Promotoria de Justiça do I Tribunal do Júri'
            
            numbers = re.findall(number_pattern, text)
            promotorias = re.findall(promotoria_pattern, text)
            
            self.log_message(f"Números encontrados: {numbers}")
            self.log_message(f"Promotorias encontradas: {promotorias}")
            
            return numbers, promotorias
            
        except Exception as e:
            self.log_message(f"ERRO ao extrair dados: {str(e)}")
            return [], []

    def paste_to_excel(self, numbers, promotorias):
        """Cola os dados no Excel"""
        try:
            if not numbers or not promotorias:
                self.log_message("Nenhum dado para colar!")
                return False
            
            # Vai para o Excel
            self.log_message("Mudando para o Excel...")
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            
            # Vai para A1
            self.log_message("Indo para célula A1...")
            pyautogui.hotkey('ctrl', 'home')
            time.sleep(0.5)
            
            # Cola os dados
            for i, (number, promotoria) in enumerate(zip(numbers, promotorias)):
                self.log_message(f"Colando item {i+1}: {number} - {promotoria}")
                
                # Cola o número
                pyautogui.write(number)
                pyautogui.press('tab')
                
                # Cola a promotoria
                pyautogui.write(promotoria)
                pyautogui.press('enter')
                
                time.sleep(0.2)
            
            return True
            
        except Exception as e:
            self.log_message(f"ERRO ao colar no Excel: {str(e)}")
            return False

    def start_extraction(self):
        self.extract_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.log_message("Iniciando extração...")
        
        try:
            # Espera um pouco para o usuário mudar para a página
            self.log_message("Aguarde 3 segundos e vá para a página com os dados...")
            time.sleep(3)
            
            # Extrai os dados
            numbers, promotorias = self.extract_data()
            
            if numbers and promotorias:
                # Cola no Excel
                if self.paste_to_excel(numbers, promotorias):
                    self.log_message("Extração concluída com sucesso!")
                    messagebox.showinfo("Sucesso", f"Extraídos e colados {len(numbers)} itens!")
                else:
                    self.log_message("Falha ao colar no Excel!")
                    messagebox.showerror("Erro", "Falha ao colar no Excel")
            else:
                self.log_message("Nenhum dado encontrado para extrair!")
                messagebox.showwarning("Aviso", "Nenhum dado encontrado!")
            
        except Exception as e:
            error_msg = f"ERRO durante a extração: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Erro", error_msg)
            
        finally:
            self.extract_btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExtractionGUI()
    app.run()
