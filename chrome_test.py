"""
Script automatizado para extrair NFs e Promotorias
"""
import pyautogui
import time
import tkinter as tk
import logging
import json
import re
import pyperclip
from bs4 import BeautifulSoup

# Configurações de segurança do pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.0  # Aumentado para dar mais tempo entre ações

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

class ExtractorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extrator de NFs")
        self.root.geometry("600x400")
        self.setup_gui()
        
    def setup_gui(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Botão para extrair
        tk.Button(
            frame, 
            text="Extrair NFs", 
            command=self.extract_data,
            bg='#4CAF50',
            fg='white',
            font=("Arial", 12),
            height=2
        ).pack(pady=20)

        # Área de log
        self.log_text = tk.Text(frame, height=15, width=60)
        self.log_text.pack(pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def switch_to_chrome(self):
        """Alterna para a janela do Chrome"""
        self.log("Alternando para o Chrome...")
        self.root.iconify()
        time.sleep(1)
        pyautogui.hotkey('alt', 'tab')
        time.sleep(2)  # Espera a janela do Chrome ficar ativa

    def auto_inspect_page(self):
        """Automatiza a inspeção da página"""
        try:
            # Primeiro alterna para o Chrome
            self.switch_to_chrome()
            
            self.log("Abrindo ferramentas do desenvolvedor...")
            # Pressiona F12 para abrir DevTools
            pyautogui.press('f12')
            time.sleep(2)
            
            self.log("Selecionando aba Elements...")
            # Garante que estamos na aba Elements
            pyautogui.hotkey('ctrl', 'shift', 'c')
            time.sleep(2)
            
            self.log("Copiando o HTML...")
            # Seleciona todo o HTML
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            
            # Copia o conteúdo
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            
            # Fecha as ferramentas do desenvolvedor
            pyautogui.press('f12')
            time.sleep(1)
            
            # Restaura a janela do script
            self.root.deiconify()
            
            html_content = pyperclip.paste()
            if not html_content:
                raise Exception("Não foi possível copiar o HTML da página")
                
            return html_content
            
        except Exception as e:
            self.log(f"Erro ao inspecionar página: {str(e)}")
            self.root.deiconify()
            return None

    def extract_data(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Iniciando extração automatizada...")
        
        try:
            # Obtém o HTML automaticamente
            html_content = self.auto_inspect_page()
            
            if not html_content:
                self.log("Falha ao obter o HTML da página!")
                return
            
            # Salva o HTML para debug
            with open('pagina.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.log("HTML salvo em 'pagina.html' para verificação")
            
            # Usa BeautifulSoup para analisar o HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Procura por elementos com as classes específicas
            nf_elements = []
            
            # Tenta diferentes seletores baseados na estrutura vista no print
            selectors = [
                'div.d-flex.align-items-center',
                'div.area-exibicao',
                'div[data-v]',
                'div.titulo',
                '*[class*="flex"]',  # Qualquer elemento com "flex" na classe
                '*[class*="align"]'   # Qualquer elemento com "align" na classe
            ]
            
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    self.log(f"Encontrados {len(elements)} elementos com selector '{selector}'")
                    nf_elements.extend(elements)
                except Exception as e:
                    self.log(f"Erro ao procurar selector '{selector}': {str(e)}")
            
            results = []
            for element in nf_elements:
                text = element.get_text(strip=True)
                # Procura por NFs no formato XXXX.XXXXXXX/XXXX
                nf_matches = re.finditer(r'\d{4}\.\d{7}/\d{4}', text)
                
                for nf_match in nf_matches:
                    nf = nf_match.group(0)
                    self.log(f"Encontrado possível NF: {nf}")
                    
                    # Procura a promotoria no elemento mais próximo
                    promotoria = ""
                    
                    # Primeiro tenta o próximo elemento
                    next_elem = element.find_next_sibling()
                    if next_elem:
                        promotoria_text = next_elem.get_text(strip=True)
                        if "Promotoria" in promotoria_text:
                            promotoria = promotoria_text
                    
                    # Se não encontrou, procura no elemento pai
                    if not promotoria:
                        parent = element.parent
                        if parent:
                            for elem in parent.find_all(True):
                                if "Promotoria" in elem.get_text(strip=True):
                                    promotoria = elem.get_text(strip=True)
                                    break
                    
                    if promotoria:
                        self.log(f"Promotoria encontrada: {promotoria}")
                        results.append({
                            'nf': nf,
                            'promotoria': promotoria
                        })
            
            if results:
                # Salva os resultados
                with open('resultados.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                self.log(f"\nTotal de NFs encontradas: {len(results)}")
                self.log("Resultados salvos em 'resultados.json'")
            else:
                self.log("\nNenhuma NF encontrada no HTML!")
                
        except Exception as e:
            self.log(f"\nErro durante a extração: {str(e)}")
        
        self.log("\nExtração concluída!")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExtractorGUI()
    app.run()
