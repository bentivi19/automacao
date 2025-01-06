"""
Script de teste para debug da extração usando Selenium
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import tkinter as tk
from tkinter import messagebox
import time

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_debug.log'),
        logging.StreamHandler()
    ]
)

class SeleniumDebugGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Debug Selenium")
        self.root.geometry("600x500")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        self.setup_gui()
        
    def setup_gui(self):
        # Título
        title = tk.Label(self.root, 
                        text="Teste de Debug - Selenium",
                        font=("Arial", 16, "bold"),
                        bg='#f0f0f0')
        title.pack(pady=15)

        # Frame para botões
        btn_frame = tk.Frame(self.root, bg='#f0f0f0')
        btn_frame.pack(pady=10)

        # Botões de teste
        self.test_btn1 = tk.Button(btn_frame,
                                 text="Teste 1: Verificar Driver",
                                 command=lambda: self.run_test(1),
                                 bg='#4CAF50',
                                 fg='white',
                                 font=("Arial", 10))
        self.test_btn1.pack(pady=5)

        self.test_btn2 = tk.Button(btn_frame,
                                 text="Teste 2: Capturar HTML",
                                 command=lambda: self.run_test(2),
                                 bg='#2196F3',
                                 fg='white',
                                 font=("Arial", 10))
        self.test_btn2.pack(pady=5)

        self.test_btn3 = tk.Button(btn_frame,
                                 text="Teste 3: Localizar Elementos",
                                 command=lambda: self.run_test(3),
                                 bg='#FF9800',
                                 fg='white',
                                 font=("Arial", 10))
        self.test_btn3.pack(pady=5)

        # Log na interface
        self.log_text = tk.Text(self.root, height=20, width=70)
        self.log_text.pack(pady=10, padx=20)

    def log_message(self, message):
        logging.debug(message)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def setup_driver(self):
        try:
            self.log_message("Configurando opções do Chrome...")
            options = Options()
            options.add_argument('--log-level=3')  # Reduz logs do Chrome
            options.add_argument('--disable-logging')
            options.add_argument('--disable-dev-shm-usage')
            
            self.log_message("Iniciando ChromeDriver...")
            driver = webdriver.Chrome(options=options)
            self.log_message("ChromeDriver iniciado com sucesso!")
            return driver
        except Exception as e:
            self.log_message(f"ERRO ao iniciar ChromeDriver: {str(e)}")
            return None

    def test_driver(self):
        driver = self.setup_driver()
        if driver:
            self.log_message("Teste do driver bem-sucedido!")
            driver.quit()
            return True
        return False

    def test_html_capture(self):
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            self.log_message("Aguardando 3 segundos para mudança de janela...")
            time.sleep(3)
            
            self.log_message("Tentando capturar HTML da página...")
            html = driver.page_source
            self.log_message(f"HTML capturado (primeiros 200 caracteres):\n{html[:200]}")
            
            return True
        except Exception as e:
            self.log_message(f"ERRO ao capturar HTML: {str(e)}")
            return False
        finally:
            driver.quit()

    def test_find_elements(self):
        driver = self.setup_driver()
        if not driver:
            return False
        
        try:
            self.log_message("Aguardando 3 segundos para mudança de janela...")
            time.sleep(3)
            
            self.log_message("Procurando elementos com classe 'NF'...")
            nf_elements = driver.find_elements(By.CLASS_NAME, "NF")
            self.log_message(f"Encontrados {len(nf_elements)} elementos NF")
            
            for i, elem in enumerate(nf_elements[:3]):  # Mostra só os 3 primeiros
                self.log_message(f"Elemento {i+1}: {elem.text}")
                
            return True
        except Exception as e:
            self.log_message(f"ERRO ao procurar elementos: {str(e)}")
            return False
        finally:
            driver.quit()

    def run_test(self, test_num):
        self.log_text.delete(1.0, tk.END)
        self.log_message(f"Iniciando Teste {test_num}...")
        
        try:
            if test_num == 1:
                success = self.test_driver()
            elif test_num == 2:
                success = self.test_html_capture()
            elif test_num == 3:
                success = self.test_find_elements()
                
            if success:
                self.log_message(f"Teste {test_num} concluído com sucesso!")
            else:
                self.log_message(f"Teste {test_num} falhou!")
                
        except Exception as e:
            self.log_message(f"ERRO no teste {test_num}: {str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SeleniumDebugGUI()
    app.run()
