import pyautogui
import pytesseract
import json
import re
import time
from PIL import Image
import tkinter as tk
from tkinter import messagebox
import logging
import pandas as pd
import os
import openpyxl
from openpyxl.styles import Font, Alignment

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

def clean_promotoria(text):
    # Remove caracteres indesejados e espaços extras
    text = text.replace('Q ', '')
    text = text.replace(' | ', ' ')
    text = text.replace('" CRIMINAL', '')
    text = re.sub(r'\s+', ' ', text)  # Remove espaços múltiplos
    return text.strip()

def save_to_excel(results):
    try:
        # Caminho da planilha
        excel_file = r'C:\Users\Julio Soama\Desktop\Setor Notíficia de Fato\atribuicoes_do_dia.xlsx'
        
        try:
            # Tenta carregar o arquivo existente
            workbook = openpyxl.load_workbook(excel_file)
            sheet = workbook.active
        except FileNotFoundError:
            # Se o arquivo não existir, cria um novo
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = 'Extrações'
        
        # Adiciona cabeçalhos
        sheet['A1'] = 'Número NF'
        sheet['B1'] = 'Promotoria'
        
        # Formata cabeçalhos
        for cell in sheet['A1:B1'][0]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Ajusta largura das colunas
        sheet.column_dimensions['A'].width = 20
        sheet.column_dimensions['B'].width = 60
        
        # Ordena os resultados por número de NF
        sorted_results = sorted(results, key=lambda x: x['nf'])
        
        # Adiciona os dados a partir da linha 2
        for i, result in enumerate(sorted_results, start=2):
            sheet[f'A{i}'] = result['nf']
            sheet[f'B{i}'] = result['promotoria']
            
            # Centraliza o número da NF
            sheet[f'A{i}'].alignment = Alignment(horizontal='center')
        
        # Salva o arquivo
        try:
            workbook.save(excel_file)
            logger.info(f"Dados salvos em {excel_file}")
            return True
        except PermissionError:
            logger.error("Erro: A planilha está aberta. Por favor, feche-a e tente novamente.")
            messagebox.showerror("Erro", "A planilha está aberta. Por favor, feche-a e tente novamente.")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao salvar Excel: {str(e)}")
        messagebox.showerror("Erro", f"Erro ao salvar no Excel: {str(e)}")
        return False

def extract_nf_and_promotorias():
    try:
        # Captura a tela inteira
        logger.info("Capturando a tela...")
        screenshot = pyautogui.screenshot()
        
        # Salva a captura temporariamente
        temp_image_path = "temp_capture.png"
        screenshot.save(temp_image_path)
        
        # Realiza OCR na imagem salva
        logger.info("Realizando OCR na imagem...")
        with Image.open(temp_image_path) as img:
            try:
                text = pytesseract.image_to_string(img, lang='por')
            except:
                logger.warning("Erro ao usar idioma português, tentando sem especificar idioma...")
                text = pytesseract.image_to_string(img)
        
        # Remove o arquivo temporário
        os.remove(temp_image_path)
        
        # Padrão para encontrar NFs (0000.0000000/0000)
        nf_pattern = r'\d{4}\.\d{7}/\d{4}'
        
        # Lista para armazenar os resultados
        results = []
        
        # Divide o texto em linhas e remove linhas vazias
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Procura por NFs e suas promotorias
        for i, line in enumerate(lines):
            nf_match = re.search(nf_pattern, line)
            if nf_match:
                nf = nf_match.group()
                # A promotoria é a próxima linha não vazia após a NF
                promotoria = ""
                j = i + 1
                while j < len(lines) and not promotoria:
                    current_line = lines[j].strip()
                    if "Promotoria" in current_line:
                        promotoria = current_line
                    j += 1
                
                if promotoria:
                    # Limpa o texto da promotoria
                    promotoria = clean_promotoria(promotoria)
                    results.append({
                        "nf": nf,
                        "promotoria": promotoria
                    })
                    logger.info(f"Encontrado: NF {nf} - Promotoria: {promotoria}")
        
        # Salva os resultados em JSON
        with open('resultados.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        
        # Salva os resultados em Excel
        if results:
            save_to_excel(results)
            logger.info(f"Extração concluída. Encontrados {len(results)} resultados.")
            return True
        else:
            logger.warning("Nenhum resultado encontrado!")
            return False
        
    except Exception as e:
        logger.error(f"Erro durante a extração: {str(e)}")
        return False

def create_gui():
    root = tk.Tk()
    root.title("Extrator de NFs")
    root.geometry("300x150")
    
    def on_extract():
        success = extract_nf_and_promotorias()
        if success:
            messagebox.showinfo("Sucesso", "Extração concluída! Os dados foram salvos em:\nC:\\Users\\Julio Soama\\Desktop\\Setor Notíficia de Fato\\atribuicoes_do_dia.xlsx")
        else:
            messagebox.showerror("Erro", "Ocorreu um erro durante a extração")
    
    button = tk.Button(root, text="Extrair NFs", command=on_extract)
    button.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
