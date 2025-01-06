import os
import re
import time
import json
import logging
import pyautogui
from PIL import Image
import pytesseract
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment
import numpy as np
import win32com.client
import tkinter as tk
from tkinter import messagebox

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tenta diferentes caminhos comuns do Tesseract
possible_tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Julio Soama\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Julio Soama\AppData\Local\Tesseract-OCR\tesseract.exe'
]

# Configura o TESSDATA_PREFIX se não estiver definido
if 'TESSDATA_PREFIX' not in os.environ:
    for path in possible_tesseract_paths:
        tessdata = os.path.join(os.path.dirname(path), 'tessdata')
        if os.path.exists(tessdata):
            os.environ['TESSDATA_PREFIX'] = tessdata
            break

# Encontra e configura o caminho do Tesseract
for path in possible_tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break
else:
    raise Exception("Tesseract não encontrado! Por favor, execute o script install_tesseract.ps1 como administrador.")

def get_promotoria_format(text):
    """Formata o texto da promotoria de acordo com as regras específicas"""
    text = text.strip().upper()
    
    # Casos especiais
    if "JUIZADO ESPECIAL CRIMINAL" in text or "JECRIM" in text:
        return "Jecrim"
    if "SANCTVS" in text:
        return "Sanc"
    if "GECRADI" in text:
        return "Gecr"
    
    # Tribunais do Júri (numeração romana)
    juri_match = re.search(r'(?:DO\s+)?([IVX]+)\s+(?:TRIBUNAL\s+DO\s+)?JÚRI', text)
    if juri_match:
        roman_num = juri_match.group(1)
        roman_values = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
        num = roman_values.get(roman_num, 1)
        return f"{num}ºJúri"
    
    # Promotorias Criminais
    crim_match = re.search(r'(\d+)(?:ª|º)\s*PROMOTORIA\s+(?:DE\s+JUSTIÇA\s+)?CRIMINAL', text)
    if crim_match:
        num = crim_match.group(1)
        return f"{num}ªCrim"
    
    # Outras Promotorias
    if "PROMOTORIA" in text:
        return "Outras PJ's"
    
    return None

def adjust_screen_for_capture():
    """Ajusta a tela e captura todas as NFs"""
    try:
        time.sleep(2)
        logger.info("Iniciando captura de tela...")
        
        screenshots = []
        
        # Diminui o zoom duas vezes
        pyautogui.hotkey('ctrl', '-')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', '-')
        time.sleep(0.5)
        
        # Posição inicial
        logger.info("Capturando tela inicial...")
        initial_screenshot = pyautogui.screenshot()
        screenshots.append(initial_screenshot)
        
        # Contador para evitar loop infinito
        max_scrolls = 30
        scroll_count = 0
        last_screen = None
        
        while scroll_count < max_scrolls:
            current_screen = pyautogui.screenshot()
            
            if last_screen is not None:
                curr_array = np.array(current_screen)
                last_array = np.array(last_screen)
                if np.array_equal(curr_array, last_array):
                    logger.info("Chegou ao fim da página")
                    break
            
            last_screen = current_screen
            
            logger.info(f"Realizando rolagem {scroll_count + 1}")
            for _ in range(3):
                pyautogui.scroll(-300)
                time.sleep(0.5)
            
            time.sleep(1)
            
            screenshots.append(pyautogui.screenshot())
            scroll_count += 1
        
        # Volta ao topo suavemente
        logger.info("Voltando ao topo da página...")
        time.sleep(0.5)
        for _ in range(scroll_count * 3):
            pyautogui.scroll(300)
            time.sleep(0.1)
        
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', '0')
        time.sleep(0.5)
        
        logger.info(f"Total de screenshots capturados: {len(screenshots)}")
        return screenshots
        
    except Exception as e:
        logger.error(f"Erro ao ajustar tela: {str(e)}")
        return None

def capture_screen_data():
    """Captura todos os dados da tela e retorna uma lista de resultados"""
    try:
        screenshots = adjust_screen_for_capture()
        if not screenshots:
            return None

        all_results = []
        processed_nfs = set()
        
        for i, screenshot in enumerate(screenshots, 1):
            logger.info(f"Processando screenshot {i} de {len(screenshots)}")
            
            # Salva temporariamente
            temp_path = f"temp_screenshot_{i}.png"
            screenshot.save(temp_path)
            
            try:
                # Realiza OCR
                text = pytesseract.image_to_string(Image.open(temp_path), lang='por')
                
                # Processa o texto
                lines = text.split('\n')
                logger.info(f"Linhas encontradas para processar: {len(lines)}")
                
                current_nf = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Verifica se é uma linha de NF
                    nf_match = re.search(r'(\d{4}\.\d{7}/\d{4})', line)
                    if nf_match:
                        nf = nf_match.group(1)
                        if nf not in processed_nfs:
                            current_nf = nf
                            
                    # Se temos uma NF atual, procura a promotoria
                    elif current_nf and ('Promotoria' in line or 'Júri' in line or 'Criminal' in line):
                        promotoria = get_promotoria_format(line)
                        if promotoria:
                            processed_nfs.add(current_nf)
                            all_results.append({
                                'nf': current_nf,
                                'promotoria': promotoria
                            })
                            logger.info(f"NF capturada - Número: {current_nf}, Promotoria: {promotoria}")
                            current_nf = None
                
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        return all_results
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        return None

def save_to_excel(nfs, excel_path):
    """Salva as NFs no arquivo Excel"""
    if not nfs:
        return False, []

    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = True
        
        # Verifica se o arquivo existe
        if os.path.exists(excel_path):
            wb = excel.Workbooks.Open(excel_path)
        else:
            wb = excel.Workbooks.Add()
            wb.SaveAs(excel_path)
        
        ws = wb.Worksheets(1)
        
        # Verifica se o cabeçalho existe
        if not ws.Cells(1, 1).Value:
            ws.Cells(1, 1).Value = "Notícia de Fato"
            ws.Cells(1, 2).Value = "PJ"
            ws.Cells(1, 3).Value = "Recebido"
        
        # Encontra última linha com dados
        last_row = 1
        while ws.Cells(last_row + 1, 1).Value:
            last_row += 1
        
        # Coleta NFs existentes
        existing_nfs = set()
        for i in range(2, last_row + 1):
            nf_cell = ws.Cells(i, 1).Value
            if nf_cell:
                existing_nfs.add(str(nf_cell).strip())
        
        # Verifica duplicatas
        duplicates = []
        new_nfs = []
        for nf in nfs:
            if nf['nf'] in existing_nfs:
                duplicates.append(nf['nf'])
            else:
                new_nfs.append(nf)
                existing_nfs.add(nf['nf'])
        
        # Adiciona novas NFs
        if new_nfs:
            next_row = last_row + 1
            current_date = datetime.now().strftime('%d/%m/%Y')
            
            for nf in new_nfs:
                ws.Cells(next_row, 1).Value = nf['nf']
                ws.Cells(next_row, 2).Value = nf['promotoria']
                ws.Cells(next_row, 3).Value = current_date
                next_row += 1
            
            wb.Save()
            
            if duplicates:
                logger.warning(f"NFs duplicadas encontradas: {', '.join(duplicates)}")
                messagebox.showwarning("Aviso", f"As seguintes NFs já existem na planilha:\n{', '.join(duplicates)}")
            
            messagebox.showinfo("Sucesso", f"{len(new_nfs)} NFs foram adicionadas com sucesso!")
        else:
            if duplicates:
                messagebox.showwarning("Aviso", "Todas as NFs já existem na planilha!")
            else:
                messagebox.showinfo("Aviso", "Nenhuma NF encontrada para adicionar.")
        
        return True, duplicates
        
    except Exception as e:
        logger.error(f"Erro ao salvar no Excel: {str(e)}")
        messagebox.showerror("Erro", f"Erro ao salvar no Excel: {str(e)}")
        return False, []

def extract_nf_and_promotorias():
    """Função principal que coordena a captura e salvamento dos dados"""
    try:
        excel_path = os.path.join(os.path.expanduser("~"), "Desktop", "Setor Notíficia de Fato", "atribuicoes_do_dia.xlsx")
        
        # Captura os dados
        nfs = capture_screen_data()
        if not nfs:
            return False, []
        
        # Salva no Excel
        return save_to_excel(nfs, excel_path)
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        return False, []

def create_gui():
    """Cria a interface gráfica"""
    root = tk.Tk()
    root.title("Extrator de NFs")
    root.geometry("300x150")
    
    def on_extract():
        success, duplicates = extract_nf_and_promotorias()
        if not success and not duplicates:
            messagebox.showerror("Erro", "Ocorreu um erro durante a extração")
    
    button = tk.Button(root, text="Extrair NFs", command=on_extract)
    button.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
