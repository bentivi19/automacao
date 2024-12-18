"""
Main module for web automation functionality
"""
import pyautogui
import time
import os
import tkinter as tk
from tkinter import messagebox
import mouse

# Configurações globais
EXCEL_PATH = r"C:\Users\Julio Soama\Desktop\Setor Notíficia de Fato\atribuicoes_do_dia.xlsx"

class AutomationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Automação Web → Excel")
        self.root.geometry("500x450")
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        self.selection_mode = False
        self.start_pos = None
        self.end_pos = None
        self.last_click_time = 0
        self.setup_gui()

    def setup_gui(self):
        # Título
        title = tk.Label(self.root, 
                        text="Automação Web → Excel",
                        font=("Arial", 16, "bold"),
                        bg='#f0f0f0')
        title.pack(pady=15)

        # Instruções
        instructions = """
1. Use ALT+TAB para ir à página desejada
2. Clique em 'Iniciar Seleção'
3. Dê um DUPLO CLIQUE no início do texto
4. Dê outro DUPLO CLIQUE no fim do texto
5. A seleção será feita automaticamente
6. Clique em 'Colar no Excel' quando estiver pronto
        """
        tk.Label(self.root, 
                text=instructions,
                justify=tk.LEFT,
                bg='#f0f0f0',
                font=("Arial", 11)).pack(pady=15, padx=25)

        # Frame para os botões
        btn_frame = tk.Frame(self.root, bg='#f0f0f0')
        btn_frame.pack(pady=15)

        # Botões de controle em um frame
        control_frame = tk.Frame(btn_frame, bg='#f0f0f0')
        control_frame.pack()

        # Botão de iniciar seleção
        self.start_btn = tk.Button(control_frame,
                                 text="Iniciar Seleção",
                                 command=self.start_selection,
                                 bg='#4CAF50',
                                 fg='white',
                                 font=("Arial", 10, "bold"),
                                 width=15,
                                 height=1)
        self.start_btn.pack(pady=5)

        # Botão de colar em frame separado
        paste_frame = tk.Frame(btn_frame, bg='#f0f0f0')
        paste_frame.pack(pady=10)

        self.paste_btn = tk.Button(paste_frame,
                                text="Colar no Excel",
                                command=self.paste_to_excel,
                                bg='#FF9800',
                                fg='white',
                                font=("Arial", 12, "bold"),
                                width=30,
                                height=2,
                                state=tk.DISABLED)
        self.paste_btn.pack()

        # Status
        self.status_label = tk.Label(self.root,
                                   text="Pronto para começar",
                                   bg='#f0f0f0',
                                   font=("Arial", 10, "bold"))
        self.status_label.pack(pady=10)

        # Coordenadas
        self.coord_label = tk.Label(self.root,
                                  text="",
                                  bg='#f0f0f0',
                                  font=("Arial", 9))
        self.coord_label.pack(pady=5)

        # Resultado
        self.result_label = tk.Label(self.root,
                                   text="",
                                   bg='#f0f0f0',
                                   fg='#4CAF50',
                                   font=("Arial", 11, "bold"))
        self.result_label.pack(pady=5)

    def start_selection(self):
        self.selection_mode = True
        self.start_pos = None
        self.end_pos = None
        self.start_btn.config(state=tk.DISABLED)
        self.paste_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Dê um DUPLO CLIQUE no início do texto")
        self.result_label.config(text="")
        self.root.attributes('-alpha', 0.8)
        
        # Inicia monitoramento do mouse
        self.monitor_mouse()

    def is_double_click(self):
        current_time = time.time()
        if current_time - self.last_click_time < 0.3:  # 300ms para duplo clique
            self.last_click_time = 0  # Reset
            return True
        self.last_click_time = current_time
        return False

    def monitor_mouse(self):
        if not self.selection_mode:
            return
        
        # Atualiza coordenadas
        x, y = mouse.get_position()
        self.coord_label.config(text=f"Posição do mouse: x={x}, y={y}")
        
        # Verifica cliques
        if mouse.is_pressed("left"):
            if self.is_double_click():
                if self.start_pos is None:
                    self.start_pos = pyautogui.position()
                    self.status_label.config(text="Agora dê um DUPLO CLIQUE no fim do texto")
                else:
                    self.end_pos = pyautogui.position()
                    self.perform_selection()
                    return
                time.sleep(0.3)  # Evita detecção dupla
        
        # Continua monitoramento
        if self.selection_mode:
            self.root.after(50, self.monitor_mouse)

    def perform_selection(self):
        try:
            # Seleciona o texto
            pyautogui.moveTo(self.start_pos.x, self.start_pos.y)
            pyautogui.mouseDown(button='left')
            time.sleep(0.2)
            pyautogui.moveTo(self.end_pos.x, self.end_pos.y, duration=0.3)
            pyautogui.mouseUp(button='left')
            time.sleep(0.2)
            
            # Copia o texto
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            # Atualiza a interface
            self.selection_mode = False
            self.start_btn.config(state=tk.NORMAL)
            self.paste_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Seleção concluída!")
            self.result_label.config(text="✓ Texto copiado com sucesso!", fg='#4CAF50')
            self.root.attributes('-alpha', 1.0)
            self.coord_label.config(text="")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao copiar seleção: {str(e)}")
            self.reset_interface()

    def paste_to_excel(self):
        try:
            # Cola o conteúdo diretamente
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            self.status_label.config(text="Conteúdo colado no Excel!")
            self.result_label.config(text="✓ Colado com sucesso!", fg='#4CAF50')
            self.paste_btn.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao colar no Excel: {str(e)}")
            self.status_label.config(text="Erro ao colar no Excel")

    def reset_interface(self):
        self.selection_mode = False
        self.start_pos = None
        self.end_pos = None
        self.start_btn.config(state=tk.NORMAL)
        self.paste_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Pronto para começar")
        self.result_label.config(text="")
        self.coord_label.config(text="")
        self.root.attributes('-alpha', 1.0)

    def run(self):
        self.root.mainloop()

def main():
    """Main function to run the automation"""
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    app = AutomationGUI()
    app.run()

if __name__ == "__main__":
    main()
