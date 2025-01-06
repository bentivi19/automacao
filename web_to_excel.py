import pyautogui
import time
import pandas as pd
import sys
from pathlib import Path

# Configurações de segurança do PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.0

def copiar_colar_conteudo():
    try:
        # Dar tempo para posicionar o mouse na área desejada
        print("Posicione o mouse no início do conteúdo em 5 segundos...")
        time.sleep(5)
        
        # Captura a posição inicial
        pos_inicial = pyautogui.position()
        print(f"Posição inicial capturada: {pos_inicial}")
        
        # Clica e arrasta para selecionar
        pyautogui.mouseDown(pos_inicial)
        time.sleep(0.5)
        
        # Move o mouse para baixo para selecionar o conteúdo
        # Você pode ajustar esses valores conforme necessário
        pyautogui.moveRel(0, 100, duration=0.5)
        pyautogui.mouseUp()
        
        # Copia o conteúdo selecionado
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)
        
        # Abre o Excel (ajuste o caminho conforme necessário)
        excel_path = r"C:\Users\Julio Soama\Desktop\Setor Notíficia de Fato\atribuicoes_do_dia.xlsx"
        if not Path(excel_path).exists():
            print(f"Arquivo Excel não encontrado em: {excel_path}")
            return
            
        # Abre o Excel com o aplicativo padrão
        os.startfile(excel_path)
        time.sleep(3)  # Espera o Excel abrir
        
        # Cola o conteúdo
        pyautogui.hotkey('ctrl', 'v')
        
        print("Operação concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a execução: {str(e)}")

if __name__ == "__main__":
    print("Iniciando automação...")
    print("Pressione Ctrl+C para interromper")
    copiar_colar_conteudo()
