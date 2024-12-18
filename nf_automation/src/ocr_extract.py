# Copiando do backup
import os
import re
import time
import json
import win32com.client
import pyautogui
import pytesseract
import numpy as np
from PIL import Image
import logging
import tkinter as tk
from tkinter import messagebox

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extraction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def setup_tesseract():
    """Configura o caminho do Tesseract."""
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        return True
    return False

def capture_screen():
    """Captura a tela atual."""
    screenshot = pyautogui.screenshot()
    return screenshot

def process_image(image):
    """Processa a imagem para melhorar o OCR."""
    # Converte para escala de cinza
    gray = image.convert('L')
    return gray

def extract_text_from_image(image):
    """Extrai texto da imagem usando OCR."""
    try:
        text = pytesseract.image_to_string(image, lang='por')
        return text
    except Exception as e:
        logger.error(f"Erro no OCR: {str(e)}")
        return ""

def process_text(text):
    """Processa o texto extraído para encontrar números de NF."""
    # Padrão para números de NF (ajuste conforme necessário)
    nf_pattern = r'NF-e\s*n[º°]?\s*(\d{6,})'
    matches = re.finditer(nf_pattern, text, re.IGNORECASE)
    
    nfs = []
    for match in matches:
        nf = match.group(1)
        if nf not in nfs:
            nfs.append(nf)
    
    return nfs

def save_to_excel(nfs, excel_path='resultados.xlsx'):
    """Salva os números de NF no Excel."""
    try:
        # Inicializa o Excel
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        
        try:
            # Tenta abrir o arquivo existente
            wb = excel.Workbooks.Open(os.path.abspath(excel_path))
            ws = wb.Sheets(1)
        except:
            # Se não existir, cria um novo
            wb = excel.Workbooks.Add()
            ws = wb.Sheets(1)
            ws.Range("A1").Value = "Números NF"
        
        # Encontra a última linha preenchida
        last_row = ws.Cells(ws.Rows.Count, 1).End(-4162).Row
        
        # Adiciona os novos números
        for i, nf in enumerate(nfs, start=1):
            ws.Cells(last_row + i, 1).Value = nf
        
        # Salva e fecha
        wb.Save()
        wb.Close()
        excel.Quit()
        
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar no Excel: {str(e)}")
        if 'excel' in locals():
            excel.Quit()
        return False

def main():
    """Função principal."""
    if not setup_tesseract():
        messagebox.showerror("Erro", "Tesseract não encontrado!")
        return

    # Interface básica
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal

    while True:
        # Aguarda confirmação do usuário
        if not messagebox.askyesno("Continuar", "Posicione o cursor sobre a NF e clique em Sim para capturar."):
            break

        # Captura e processa
        screenshot = capture_screen()
        processed_image = process_image(screenshot)
        text = extract_text_from_image(processed_image)
        nfs = process_text(text)

        if nfs:
            # Salva no Excel
            if save_to_excel(nfs):
                messagebox.showinfo("Sucesso", f"NFs encontradas e salvas: {', '.join(nfs)}")
            else:
                messagebox.showerror("Erro", "Erro ao salvar no Excel!")
        else:
            messagebox.showwarning("Aviso", "Nenhuma NF encontrada na imagem!")

if __name__ == "__main__":
    main()
