"""
Script para extrair dados usando Selenium com interface gráfica
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import re
import tkinter as tk
from tkinter import messagebox

class ExtractionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extrator de Dados")
        self.root.geometry("400x300")
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
1. Abra a página com os dados
2. Clique em 'Iniciar Extração'
3. Os dados serão copiados automaticamente
4. Aguarde a mensagem de conclusão
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

        # Status
        self.status_label = tk.Label(self.root,
                                   text="Pronto para começar",
                                   bg='#f0f0f0',
                                   font=("Arial", 10, "bold"))
        self.status_label.pack(pady=10)

    def extract_number(self, text):
        """Extrai o número no formato 0000.0000000/0000"""
        match = re.search(r'\d{4}\.\d{7}/\d{4}', text)
        return match.group(0) if match else None

    def start_extraction(self):
        self.extract_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Iniciando extração...")
        self.root.update()

        try:
            # Configurar o Chrome
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(options=options)
            
            # Pega o foco da janela atual
            current_window = pyautogui.getActiveWindow()
            
            # Espera um pouco para o usuário mudar para a página
            self.status_label.config(text="Por favor, vá para a página com os dados (3s)...")
            self.root.update()
            time.sleep(3)
            
            # Captura o HTML da página ativa
            html = driver.page_source
            
            # Encontra todos os elementos NF
            nf_elements = driver.find_elements(By.CLASS_NAME, "NF")
            
            data = []
            for nf in nf_elements:
                # Pega o número do processo
                number = self.extract_number(nf.text)
                
                # Pega o texto da promotoria na linha seguinte
                promotoria = nf.find_element(By.XPATH, "following-sibling::*[1]").text
                
                if number and promotoria:
                    data.append((number, promotoria))
            
            # Mostra quantos itens encontrou
            self.status_label.config(text=f"Encontrados {len(data)} itens. Colando no Excel...")
            self.root.update()
            
            # Abre o Excel
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            
            # Vai para A1
            pyautogui.hotkey('ctrl', 'home')
            time.sleep(0.5)
            
            # Cola os dados
            for i, (number, promotoria) in enumerate(data):
                # Cola o número
                pyautogui.write(number)
                pyautogui.press('tab')  # Vai para coluna B
                
                # Cola a promotoria
                pyautogui.write(promotoria)
                pyautogui.press('enter')  # Próxima linha
                
                # Atualiza status
                self.status_label.config(text=f"Colando item {i+1} de {len(data)}...")
                self.root.update()
            
            # Finaliza
            self.status_label.config(text="Extração concluída com sucesso!")
            messagebox.showinfo("Sucesso", "Dados extraídos e colados com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a extração: {str(e)}")
            self.status_label.config(text="Erro durante a extração")
        finally:
            driver.quit()
            self.extract_btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExtractionGUI()
    app.run()
