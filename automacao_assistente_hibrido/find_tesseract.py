import os
import sys
from pathlib import Path

def find_tesseract():
    # Locais comuns de instalação
    common_paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        r"C:\Tesseract-OCR",
        os.path.expanduser("~") + r"\AppData\Local\Programs\Tesseract-OCR",
        os.path.expanduser("~") + r"\AppData\Local\Tesseract-OCR",
    ]
    
    # Procura em todos os drives do sistema
    drives = [d + ":\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(d + ":")]
    
    print("Procurando Tesseract-OCR...")
    
    # Primeiro verifica os caminhos comuns
    for path in common_paths:
        tesseract_exe = os.path.join(path, "tesseract.exe")
        if os.path.exists(tesseract_exe):
            print(f"\nTesseract encontrado em: {tesseract_exe}")
            return tesseract_exe
    
    # Se não encontrou, procura em todos os drives
    for drive in drives:
        print(f"\nProcurando no drive {drive}...")
        for root, dirs, files in os.walk(drive):
            if "tesseract.exe" in files:
                tesseract_exe = os.path.join(root, "tesseract.exe")
                print(f"\nTesseract encontrado em: {tesseract_exe}")
                return tesseract_exe
            
            # Ignora alguns diretórios para tornar a busca mais rápida
            if any(skip in root.lower() for skip in ['windows', 'program files (x86)', '$recycle.bin', 'system volume information']):
                dirs.clear()
    
    print("\nTesseract não encontrado!")
    return None

if __name__ == "__main__":
    tesseract_path = find_tesseract()
    if tesseract_path:
        print("\nCopie este caminho e use no script:")
        print(f"pytesseract.pytesseract.tesseract_cmd = r'{tesseract_path}'")
