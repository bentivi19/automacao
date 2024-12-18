# Copiando do backup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import re
import tkinter as tk
from tkinter import messagebox
import logging
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    filename='logs/selenium_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class NFExtractor:
    def __init__(self):
        self.setup_chrome()
        self.setup_gui()
        
    def setup_chrome(self):
        """Configura o Chrome Driver."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            self.driver = webdriver.Chrome(options=options)
            logging.info("Chrome Driver iniciado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao iniciar Chrome Driver: {str(e)}")
            raise

    def setup_gui(self):
        """Configura a interface gráfica."""
        self.root = tk.Tk()
        self.root.withdraw()

    def extract_nf_numbers(self, text):
        """Extrai números de NF do texto."""
        pattern = r'NF-e\s*n[º°]?\s*(\d{6,})'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        return [match.group(1) for match in matches]

    def save_to_excel(self, nf_numbers):
        """Salva os números no Excel."""
        try:
            import win32com.client
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            
            file_path = os.path.abspath("resultados.xlsx")
            
            try:
                wb = excel.Workbooks.Open(file_path)
                ws = wb.Sheets(1)
            except:
                wb = excel.Workbooks.Add()
                ws = wb.Sheets(1)
                ws.Range("A1").Value = "Números NF"

            last_row = ws.Cells(ws.Rows.Count, 1).End(-4162).Row
            
            for i, nf in enumerate(nf_numbers, 1):
                ws.Cells(last_row + i, 1).Value = nf

            wb.Save()
            wb.Close()
            excel.Quit()
            
            logging.info(f"Números salvos com sucesso: {nf_numbers}")
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar no Excel: {str(e)}")
            if 'excel' in locals():
                excel.Quit()
            return False

    def run(self):
        """Executa o processo de extração."""
        try:
            while True:
                if not messagebox.askyesno("Continuar", "Posicione o cursor sobre a NF e clique em Sim para capturar."):
                    break

                try:
                    # Captura o texto da página
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    
                    # Extrai os números de NF
                    nf_numbers = self.extract_nf_numbers(page_text)
                    
                    if nf_numbers:
                        if self.save_to_excel(nf_numbers):
                            messagebox.showinfo("Sucesso", f"NFs encontradas e salvas: {', '.join(nf_numbers)}")
                        else:
                            messagebox.showerror("Erro", "Erro ao salvar no Excel!")
                    else:
                        messagebox.showwarning("Aviso", "Nenhuma NF encontrada na página!")

                except Exception as e:
                    logging.error(f"Erro durante a extração: {str(e)}")
                    messagebox.showerror("Erro", f"Erro durante a extração: {str(e)}")

        finally:
            self.cleanup()

    def cleanup(self):
        """Limpa recursos."""
        try:
            self.driver.quit()
            logging.info("Chrome Driver fechado com sucesso")
        except Exception as e:
            logging.error(f"Erro ao fechar Chrome Driver: {str(e)}")

if __name__ == "__main__":
    try:
        extractor = NFExtractor()
        extractor.run()
    except Exception as e:
        logging.error(f"Erro fatal: {str(e)}")
        messagebox.showerror("Erro Fatal", str(e))
