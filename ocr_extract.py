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

# Padrão para encontrar NFs
nf_pattern = r'\d{4}\.\d{7}/\d{4}'

def clean_promotoria(text):
    """Limpa e padroniza o texto da promotoria"""
    try:
        # Remove caracteres indesejados e espaços extras
        text = text.strip()
        text = ' '.join(text.split())  # Normaliza espaços
        
        # Mapeamento de variações conhecidas para o formato padrão
        promotoria_patterns = {
            r'Promotoria de Justiça do I Tribunal do Júri': '1ºJúri',
            r'Promotoria de Justiça do 1 Tribunal do Júri': '1ºJúri',
            r'Promotoria de Justiça do Tribunal do Júri': '1ºJúri',  # Caso o I não seja capturado
            r'Promotoria de Justiça do l Tribunal do Júri': '1ºJúri',  # Caso o I seja capturado como l minúsculo
            r'.*?\bI\s+Tribunal do Júri\b': '1ºJúri',  # Padrão mais flexível
            r'.*?\b1\s+Tribunal do Júri\b': '1ºJúri',
            r'.*?Tribunal do Júri\b': '1ºJúri',  # Caso mais genérico
            'SANCTVUS': 'SANCTVUS',
            'Juizado Especial Criminal': 'Juizado Especial Criminal'
        }
        
        # Tenta encontrar um padrão que corresponda
        for pattern, replacement in promotoria_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return replacement
        
        # Se não encontrar nenhum padrão conhecido, retorna o texto limpo
        if "Promotoria" in text and "Júri" in text:
            return "1ºJúri"
            
        return text
        
    except Exception as e:
        logger.error(f"Erro ao limpar promotoria: {str(e)}")
        return text

def adjust_screen_for_capture():
    """Ajusta a tela e captura todas as NFs"""
    try:
        # Pausa inicial para garantir que a página esteja carregada
        time.sleep(2)
        logger.info("Iniciando captura de tela...")
        
        # Lista para armazenar todos os screenshots
        all_screenshots = []
        
        # Diminui o zoom duas vezes
        pyautogui.hotkey('ctrl', '-')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', '-')
        time.sleep(0.5)
        
        # Posição inicial
        logger.info("Capturando tela inicial...")
        initial_screenshot = pyautogui.screenshot()
        all_screenshots.append(initial_screenshot)
        
        # Contador para evitar loop infinito
        max_scrolls = 30
        scroll_count = 0
        last_screen = None
        
        while scroll_count < max_scrolls:
            # Captura tela atual
            current_screen = pyautogui.screenshot()
            
            # Se a tela atual é igual à anterior, chegamos ao fim
            if last_screen is not None:
                curr_array = np.array(current_screen)
                last_array = np.array(last_screen)
                if np.array_equal(curr_array, last_array):
                    logger.info("Chegou ao fim da página")
                    break
            
            # Salva a tela atual
            last_screen = current_screen
            
            # Scroll mais suave
            logger.info(f"Realizando rolagem {scroll_count + 1}")
            for _ in range(3):  # Divide o scroll em 3 partes
                pyautogui.scroll(-300)  # Scroll menor e mais suave
                time.sleep(0.5)  # Espera entre cada parte do scroll
            
            time.sleep(1)  # Espera adicional para carregar o conteúdo
            
            # Captura a tela após o scroll
            current_screenshot = pyautogui.screenshot()
            all_screenshots.append(current_screenshot)
            
            scroll_count += 1
        
        # Volta ao topo suavemente
        logger.info("Voltando ao topo da página...")
        time.sleep(0.5)
        for _ in range(scroll_count * 3):  # Multiplica por 3 devido ao scroll dividido
            pyautogui.scroll(300)
            time.sleep(0.1)
        
        # Restaura o zoom
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', '0')
        time.sleep(0.5)
        
        logger.info(f"Total de screenshots capturados: {len(all_screenshots)}")
        return all_screenshots
        
    except Exception as e:
        logger.error(f"Erro ao ajustar tela: {str(e)}")
        return None

def capture_screen_data():
    """Captura todos os dados da tela e retorna uma lista de resultados"""
    try:
        # Captura todas as screenshots
        screenshots = adjust_screen_for_capture()
        if not screenshots:
            messagebox.showerror("Erro", "Não foi possível capturar a tela.")
            return None

        all_results = []
        processed_nfs = set()  # Para evitar duplicatas durante a captura
        
        # Processa cada screenshot
        for screenshot in screenshots:
            # Salva a captura temporariamente
            temp_image_path = "temp_capture.png"
            screenshot.save(temp_image_path)
            
            try:
                # Realiza OCR na imagem
                logger.info("Realizando OCR na imagem...")
                with Image.open(temp_image_path) as img:
                    try:
                        text = pytesseract.image_to_string(img, lang='por')
                    except:
                        logger.warning("Erro ao usar idioma português, tentando sem especificar idioma...")
                        text = pytesseract.image_to_string(img)
                
                # Processa o texto
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                
                for i, line in enumerate(lines):
                    if not is_valid_nf_line(line):
                        continue
                    
                    nf_matches = re.finditer(nf_pattern, line)
                    for nf_match in nf_matches:
                        nf = nf_match.group()
                        
                        # Pula se já processamos esta NF
                        if nf in processed_nfs:
                            continue
                            
                        promotoria = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line:
                                promotoria = clean_promotoria(next_line)
                        
                        if promotoria:
                            processed_nfs.add(nf)
                            all_results.append({
                                "nf": nf,
                                "promotoria": promotoria,
                                "data_captura": datetime.now().strftime('%m/%d/%Y')
                            })
                            logger.info(f"Capturado: NF {nf} - Promotoria: {promotoria}")
                
            finally:
                # Limpa arquivo temporário
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
        
        return all_results if all_results else None
        
    except Exception as e:
        logger.error(f"Erro durante a captura de dados: {str(e)}")
        messagebox.showerror("Erro", f"Erro durante a captura: {str(e)}")
        return None

def save_to_excel(results):
    """Salva os resultados no arquivo principal mesmo que esteja aberto"""
    if not results:
        logger.info("Nenhum resultado para salvar")
        return False

    excel_file = r'C:\Users\Julio Soama\Desktop\Setor Notíficia de Fato\atribuicoes_do_dia.xlsx'
    current_date = datetime.now().strftime('%m/%d/%Y')
    
    try:
        # Tenta abrir o arquivo com suporte a arquivos abertos
        app = win32com.client.Dispatch("Excel.Application")
        app.Visible = True  # Mantém o Excel visível
        app.DisplayAlerts = False  # Desativa alertas
        
        try:
            logger.info(f"Tentando abrir o arquivo: {excel_file}")
            wb = app.Workbooks.Open(excel_file)
            ws = wb.ActiveSheet
            logger.info("Arquivo aberto com sucesso")
            
            # Encontra a primeira linha vazia após o cabeçalho
            row = 2  # Começa da linha 2 (após o cabeçalho)
            while ws.Cells(row, 1).Value is not None:
                row += 1
            last_row = row - 1
            logger.info(f"Primeira linha vazia encontrada: {row}")
            
            # Coleta NFs existentes para evitar duplicatas
            existing_nfs = set()
            for i in range(2, last_row + 1):
                nf = ws.Cells(i, 1).Value
                if nf:
                    existing_nfs.add(str(nf))
            logger.info(f"NFs existentes encontradas: {len(existing_nfs)}")
            
            # Filtra apenas novas NFs
            new_results = [r for r in results if r['nf'] not in existing_nfs]
            logger.info(f"Novas NFs para adicionar: {len(new_results)}")
            
            if not new_results:
                logger.info("Não há novas NFs para adicionar")
                wb.Close(SaveChanges=False)
                app.Quit()
                return True
            
            # Registra detalhes das NFs que serão adicionadas
            for result in new_results:
                logger.info(f"Preparando para adicionar - NF: {result['nf']}, Promotoria: {result['promotoria']}")
            
            # Adiciona as novas NFs
            start_row = row  # Usa a primeira linha vazia encontrada
            for i, result in enumerate(new_results):
                current_row = start_row + i
                
                try:
                    # Adiciona os dados
                    ws.Cells(current_row, 1).Value = result['nf']
                    ws.Cells(current_row, 2).Value = result['promotoria']
                    ws.Cells(current_row, 3).Value = current_date
                    
                    # Formata as células
                    ws.Cells(current_row, 1).HorizontalAlignment = -4108  # xlCenter
                    ws.Cells(current_row, 3).HorizontalAlignment = -4108  # xlCenter
                    
                    logger.info(f"Dados adicionados com sucesso na linha {current_row}")
                    
                except Exception as e:
                    logger.error(f"Erro ao adicionar dados na linha {current_row}: {str(e)}")
                    raise
            
            # Salva as alterações
            logger.info("Tentando salvar as alterações...")
            wb.Save()
            logger.info("Alterações salvas com sucesso")
            
            # Mantém o Excel aberto
            messagebox.showinfo("Sucesso", f"Foram adicionadas {len(new_results)} novas NFs à planilha!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar o Excel: {str(e)}")
            try:
                wb.Close(SaveChanges=False)
            except:
                pass
            app.Quit()
            raise
            
    except Exception as e:
        error_msg = f"Erro ao salvar no Excel: {str(e)}"
        logger.error(error_msg)
        messagebox.showerror("Erro", error_msg)
        return False

def extract_nf_and_promotorias():
    """Função principal que coordena a captura e salvamento dos dados"""
    try:
        logger.info("Iniciando processo de extração de NFs...")
        
        # Captura os dados
        screenshots = adjust_screen_for_capture()
        if not screenshots:
            logger.error("Não foi possível capturar a tela")
            messagebox.showerror("Erro", "Não foi possível capturar a tela.")
            return False
        
        # Lista para armazenar os resultados
        results = []
        processed_nfs = set()  # Para evitar duplicatas durante a captura
        
        # Processa cada screenshot
        for i, screenshot in enumerate(screenshots):
            logger.info(f"Processando screenshot {i+1} de {len(screenshots)}")
            
            # Salva a captura temporariamente
            temp_image_path = "temp_capture.png"
            screenshot.save(temp_image_path)
            
            try:
                # Realiza OCR na imagem
                logger.info("Realizando OCR na imagem...")
                with Image.open(temp_image_path) as img:
                    try:
                        text = pytesseract.image_to_string(img, lang='por')
                        logger.info("OCR realizado com sucesso usando idioma português")
                    except:
                        logger.warning("Erro ao usar idioma português, tentando sem especificar idioma...")
                        text = pytesseract.image_to_string(img)
                        logger.info("OCR realizado com sucesso sem especificar idioma")
                
                # Processa o texto
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                logger.info(f"Linhas encontradas para processar: {len(lines)}")
                
                for i, line in enumerate(lines):
                    if not is_valid_nf_line(line):
                        continue
                    
                    nf_matches = re.finditer(nf_pattern, line)
                    for nf_match in nf_matches:
                        nf = nf_match.group()
                        
                        # Pula se já processamos esta NF
                        if nf in processed_nfs:
                            logger.info(f"NF já processada, pulando: {nf}")
                            continue
                            
                        promotoria = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line:
                                promotoria = clean_promotoria(next_line)
                                
                        if promotoria:
                            processed_nfs.add(nf)
                            results.append({
                                "nf": nf,
                                "promotoria": promotoria
                            })
                            logger.info(f"NF capturada - Número: {nf}, Promotoria: {promotoria}")
                
            finally:
                # Limpa arquivo temporário
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                    logger.info("Arquivo temporário removido")
        
        if not results:
            logger.warning("Nenhuma NF foi encontrada")
            messagebox.showwarning("Aviso", "Nenhuma NF foi encontrada!")
            return False
        
        # Tenta salvar no Excel
        logger.info(f"Tentando salvar {len(results)} NFs no Excel...")
        return save_to_excel(results)
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {str(e)}")
        messagebox.showerror("Erro", f"Erro durante a execução: {str(e)}")
        return False

def is_valid_nf_line(line):
    """Verifica se a linha contém uma NF válida e não é um protocolo"""
    if "Protocolo:" in line or "protocolo" in line.lower():
        return False
    return True

def create_gui():
    root = tk.Tk()
    root.title("Extrator de NFs")
    root.geometry("300x150")
    
    def on_extract():
        success = extract_nf_and_promotorias()
        if success:
            messagebox.showinfo("Sucesso", "Extração concluída! Os dados foram salvos em:\nnfs_capturadas.xlsx")
        else:
            messagebox.showerror("Erro", "Ocorreu um erro durante a extração")
    
    button = tk.Button(root, text="Extrair NFs", command=on_extract)
    button.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
