"""
Script de teste para debug da extração de dados
"""
import pyautogui
import time
import re
import tkinter as tk
from tkinter import messagebox
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   filename='debug_extraction.log',
                   filemode='w')

class TestExtractionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Teste de Extração")
        self.root.geometry("500x400")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        self.setup_gui()
        
    def setup_gui(self):
        # Título
        title = tk.Label(self.root, 
                        text="Teste de Extração Web → Excel",
                        font=("Arial", 16, "bold"),
                        bg='#f0f0f0')
        title.pack(pady=15)

        # Instruções
        instructions = """
1. Abra a página com os dados
2. Selecione todo o conteúdo (Ctrl+A)
3. Clique em 'Iniciar Teste'
4. O programa tentará extrair os dados
5. Verifique o arquivo debug_extraction.log
        """
        tk.Label(self.root, 
                text=instructions,
                justify=tk.LEFT,
                bg='#f0f0f0',
                font=("Arial", 11)).pack(pady=15, padx=25)

        # Botão de teste
        self.test_btn = tk.Button(self.root,
                                text="Iniciar Teste",
                                command=self.start_test,
                                bg='#4CAF50',
                                fg='white',
                                font=("Arial", 12, "bold"),
                                width=20,
                                height=2)
        self.test_btn.pack(pady=20)

        # Log na interface
        self.log_text = tk.Text(self.root, height=8, width=50)
        self.log_text.pack(pady=10, padx=20)

    def log_message(self, message):
        logging.debug(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def extract_data_from_clipboard(self):
        """Tenta extrair dados do clipboard"""
        try:
            # Copia o conteúdo selecionado
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            # Pega o texto do clipboard
            import clipboard
            text = clipboard.paste()
            
            self.log_message(f"Conteúdo copiado: {text[:200]}...")  # Primeiros 200 caracteres
            
            # Procura por números de processo e promotorias
            number_pattern = r'\d{4}\.\d{7}/\d{4}'
            promotoria_pattern = r'Promotoria de Justiça do I Tribunal do Júri'
            
            numbers = re.findall(number_pattern, text)
            promotorias = re.findall(promotoria_pattern, text)
            
            self.log_message(f"Números encontrados: {numbers}")
            self.log_message(f"Promotorias encontradas: {promotorias}")
            
            return list(zip(numbers, promotorias))
            
        except Exception as e:
            self.log_message(f"Erro ao extrair dados: {str(e)}")
            return []

    def start_test(self):
        self.test_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        self.log_message("Iniciando teste de extração...")
        
        try:
            # Espera para mudar para a página
            self.log_message("Aguardando 3 segundos para mudança de janela...")
            time.sleep(3)
            
            # Seleciona todo o conteúdo
            self.log_message("Selecionando conteúdo (Ctrl+A)...")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            
            # Extrai os dados
            data = self.extract_data_from_clipboard()
            self.log_message(f"Dados extraídos: {len(data)} pares")
            
            if data:
                # Vai para o Excel
                self.log_message("Mudando para o Excel...")
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.5)
                
                # Vai para A1
                self.log_message("Indo para célula A1...")
                pyautogui.hotkey('ctrl', 'home')
                time.sleep(0.5)
                
                # Cola os dados
                for i, (number, promotoria) in enumerate(data):
                    self.log_message(f"Colando item {i+1}: {number} - {promotoria}")
                    
                    # Cola o número
                    pyautogui.write(number)
                    pyautogui.press('tab')
                    
                    # Cola a promotoria
                    pyautogui.write(promotoria)
                    pyautogui.press('enter')
                    
                    time.sleep(0.2)
                
                self.log_message("Extração concluída com sucesso!")
                messagebox.showinfo("Sucesso", f"Extraídos e colados {len(data)} itens!")
            else:
                self.log_message("Nenhum dado encontrado para extrair!")
                messagebox.showwarning("Aviso", "Nenhum dado encontrado!")
            
        except Exception as e:
            error_msg = f"Erro durante o teste: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Erro", error_msg)
            
        finally:
            self.test_btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Instala o módulo clipboard se necessário
    try:
        import clipboard
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'clipboard'])
        import clipboard
        
    app = TestExtractionGUI()
    app.run()
