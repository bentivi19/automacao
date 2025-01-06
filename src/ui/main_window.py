import logging
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from src.ai_analyzer.mixtral_client import MixtralAnalyzer
from src.rules_engine.rules_manager import RulesManager
from src.ui.rules_manager_dialog import RulesManagerDialog
from src.ui.rules_registration_dialog import RulesRegistrationDialog
from src.pdf_processor.pdf_splitter import PDFSplitter
import re

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    def __init__(self, analyzer_factory):
        super().__init__()

        self.title("Analisador de Documentos")
        self.geometry("1200x800")

        # Configuração do grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variáveis de controle
        self.current_splitter = None

        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # Frame superior para botões
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Dropdown para seleção do modelo
        self.model_var = ctk.StringVar(value="mixtral-8x7b")  # Mixtral como padrão
        self.model_dropdown = ctk.CTkOptionMenu(
            button_frame,
            values=["mixtral-8x7b", "claude-3-opus", "gpt-3.5-turbo"],  # Mixtral primeiro
            variable=self.model_var,
            command=self.change_model
        )
        self.model_dropdown.grid(row=0, column=0, padx=5, pady=5)

        # Botão para gerenciar regras
        self.rules_button = ctk.CTkButton(
            button_frame,
            text="Gerenciar Regras",
            command=self.show_rules_manager
        )
        self.rules_button.grid(row=0, column=1, padx=5, pady=5)

        # Botão para cadastrar regras
        self.register_rules_button = ctk.CTkButton(
            button_frame,
            text="Cadastrar Regras",
            command=self.show_rules_registration
        )
        self.register_rules_button.grid(row=0, column=2, padx=5, pady=5)

        # Botão para selecionar arquivo
        self.select_button = ctk.CTkButton(
            button_frame, 
            text="Selecionar Arquivo",
            command=self.select_file
        )
        self.select_button.grid(row=0, column=3, padx=5, pady=5)

        # Botão de busca
        self.search_button = ctk.CTkButton(
            button_frame,
            text="Buscar",
            command=self.show_search_dialog
        )
        self.search_button.grid(row=0, column=4, padx=5, pady=5)

        # Label de status
        self.status_label = ctk.CTkLabel(button_frame, text="")
        self.status_label.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Frame para o resultado
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)

        # Widget de texto para mostrar o resultado
        self.result_text = ctk.CTkTextbox(result_frame)
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Frame para área de complemento
        complete_frame = ctk.CTkFrame(main_frame)
        complete_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        complete_frame.grid_columnconfigure(1, weight=1)

        # Label para instruções
        self.complete_label = ctk.CTkLabel(
            complete_frame,
            text="Cole aqui partes do PDF que precisam de esclarecimentos:",
            anchor="w"
        )
        self.complete_label.grid(row=0, column=0, padx=5, pady=(5,0))

        self.complete_entry = ctk.CTkTextbox(
            complete_frame,
            height=100
        )
        self.complete_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)

        self.complete_button = ctk.CTkButton(
            complete_frame,
            text="Complete",
            command=self.process_completion,
            width=100
        )
        self.complete_button.grid(row=1, column=2, padx=5)

        # Frame para área de perguntas
        question_frame = ctk.CTkFrame(main_frame)
        question_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        question_frame.grid_columnconfigure(1, weight=1)

        self.question_entry = ctk.CTkEntry(
            question_frame,
            placeholder_text="Digite sua pergunta sobre o documento...",
            width=600
        )
        self.question_entry.grid(row=0, column=0, sticky="ew", padx=5)

        self.ask_button = ctk.CTkButton(
            question_frame,
            text="Perguntar",
            command=self.ask_question,
            width=100
        )
        self.ask_button.grid(row=0, column=1, padx=5)

        # Desabilita área de complemento inicialmente
        self.complete_entry.configure(state="disabled")
        self.complete_button.configure(state="disabled")

        # Desabilita área de perguntas inicialmente
        self.question_entry.configure(state="disabled")
        self.ask_button.configure(state="disabled")

        # Configuração de pesos para o grid
        main_frame.grid_rowconfigure(1, weight=1)

        # Inicializa o gerenciador de regras
        self.rules_manager = RulesManager()

        # Salva a fábrica de analisadores
        self.analyzer_factory = analyzer_factory

        # Inicializa o analisador
        self.change_model(self.model_var.get())  # Inicializa o analisador com o modelo padrão

    def change_model(self, model_name):
        """Altera o modelo de IA atual."""
        if model_name == "mixtral-8x7b":
            self.analyzer = MixtralAnalyzer()
        else:
            self.analyzer = self.analyzer_factory.create_analyzer(model_name)
        logger.info(f"Modelo alterado para: {model_name}")

    def select_file(self):
        """Abre diálogo para selecionar arquivo PDF."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )

        if file_path:
            try:
                self.current_file = file_path
                self.status_label.configure(text=f"Arquivo: {Path(file_path).name}")

                # Processa o documento
                self.process_file(file_path)

            except Exception as e:
                logger.error(f"Erro ao processar arquivo: {str(e)}")
                self.result_text.delete("1.0", "end")
                self.result_text.insert("1.0", f"Erro ao processar arquivo: {str(e)}")
                self.ask_button.configure(state="disabled")

    def process_file(self, file_path):
        """Processa o arquivo selecionado."""
        try:
            # Limpa o splitter anterior se existir
            if hasattr(self, 'current_splitter') and self.current_splitter:
                self.current_splitter.cleanup()
            
            self.file_path = file_path
            self.status_label.configure(text="Processando arquivo...")
            
            # Processa o arquivo PDF
            self.current_splitter = PDFSplitter()
            # Bloqueia a limpeza dos arquivos temporários até que tenhamos certeza que o texto foi salvo
            self.current_splitter.block_cleanup()
            
            chunk_paths = self.current_splitter.split_pdf(file_path)
            
            # Lê e consolida o texto de todos os chunks
            consolidated_text = ""
            for chunk_path in chunk_paths:
                try:
                    with open(chunk_path, 'r', encoding='utf-8') as f:
                        chunk_text = f.read().strip()
                        if chunk_text:  # Só adiciona se houver texto
                            consolidated_text += chunk_text + "\n\n"
                except Exception as e:
                    logger.error(f"Erro ao ler chunk {chunk_path}: {str(e)}")
            
            # Remove espaços em branco extras e normaliza quebras de linha
            consolidated_text = "\n".join(line.strip() for line in consolidated_text.splitlines() if line.strip())
            consolidated_text = re.sub(r'\n{3,}', '\n\n', consolidated_text)
            
            # Cria o diálogo do gerenciador de regras se não existir
            if not hasattr(self, 'rules_manager_dialog'):
                self.rules_manager_dialog = RulesManagerDialog(self, self.rules_manager)
            
            # Atualiza o texto consolidado no gerenciador de regras
            self.rules_manager_dialog.update_consolidated_text(consolidated_text)
            
            try:
                # Analisa o documento
                result = self.analyzer.analyze_document(chunk_paths)
                
                # Se precisa de confirmação da página
                if result.get("needs_confirmation"):
                    # Mostra o texto da página no campo Complete
                    self.complete_entry.configure(state="normal")
                    self.complete_entry.delete("1.0", "end")
                    self.complete_entry.insert("1.0", result["page_text"])
                    
                    # Cria uma janela de diálogo personalizada não modal
                    if not hasattr(self, 'nav_dialog'):
                        self.nav_dialog = ctk.CTkToplevel(self)
                        self.nav_dialog.title("Navegação")
                        self.nav_dialog.geometry("400x150")
                        self.nav_dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Impede fechar
                        
                        # Frame para os botões
                        button_frame = ctk.CTkFrame(self.nav_dialog)
                        button_frame.pack(pady=10)
                        
                        # Botões de navegação
                        self.prev_btn = ctk.CTkButton(
                            button_frame, 
                            text="← Anterior", 
                            command=lambda: self.navigate_pages("prev")
                        )
                        self.next_btn = ctk.CTkButton(
                            button_frame, 
                            text="Próxima →", 
                            command=lambda: self.navigate_pages("next")
                        )
                        self.confirm_btn = ctk.CTkButton(
                            button_frame, 
                            text="Confirmar", 
                            command=lambda: self.confirm_page()
                        )
                        
                        self.prev_btn.pack(side="left", padx=5)
                        self.next_btn.pack(side="left", padx=5)
                        self.confirm_btn.pack(side="left", padx=5)
                        
                        # Label para informação da página
                        self.page_info = ctk.CTkLabel(self.nav_dialog, text="")
                        self.page_info.pack(pady=10)
                    
                    # Atualiza a informação da página
                    self.page_info.configure(text=result["message"])
                    
                    # Atualiza estado dos botões
                    self.prev_btn.configure(state="normal" if result["current_index"] > 0 else "disabled")
                    self.next_btn.configure(state="normal" if result["current_index"] < result["total_pages"] - 1 else "disabled")
                    
                    # Mostra o diálogo se ainda não estiver visível
                    if not self.nav_dialog.winfo_viewable():
                        self.nav_dialog.deiconify()
                    
                    # Armazena o resultado atual para uso posterior
                    self.current_result = result
                    return
                
                # Atualiza a interface com o resultado
                self.update_ui_with_result(result)
                
            except Exception as e:
                logger.error(f"Erro ao analisar documento: {str(e)}")
                self.status_label.configure(text=f"Erro ao analisar documento: {str(e)}")
                # Mesmo com erro na análise, mantém o texto consolidado disponível
                self.complete_entry.configure(state="normal")
                self.complete_button.configure(state="normal")
                self.question_entry.configure(state="normal")
                self.ask_button.configure(state="normal")
                # Desbloqueia a limpeza dos arquivos temporários
                self.current_splitter.unblock_cleanup()
            
        except Exception as e:
            logger.error(f"Erro ao processar arquivo: {str(e)}")
            self.status_label.configure(text=f"Erro ao processar arquivo: {str(e)}")

    def complete_text(self):
        """Processa o texto complementar."""
        try:
            text = self.complete_entry.get("1.0", "end").strip()
            if text:
                # Se o usuário digitou um número, assume que é uma página
                if text.isdigit():
                    page = int(text)
                    # Verifica se a página é válida
                    if page < 1 or page > 107:  # Ajuste esse número conforme necessário
                        self.status_label.configure(text="Número de página inválido")
                        return
                        
                    # Ativa a navegação manual
                    self.analyzer.set_specific_page(page)
                    
                    # Processa o arquivo novamente
                    self.process_file(self.file_path)
                else:
                    # Caso contrário, usa como contexto adicional
                    result = self.analyzer.analyze_document(None, text)
                    self.update_ui_with_result(result)
        except Exception as e:
            logger.error(f"Erro ao processar complemento: {str(e)}")
            self.status_label.configure(text=f"Erro ao processar complemento: {str(e)}")

    def navigate_pages(self, direction):
        """Navega entre as páginas do documento."""
        try:
            # Calcula o novo índice
            if direction == "prev":
                self.analyzer.current_page_index = max(0, self.analyzer.current_page_index - 1)
            else:
                self.analyzer.current_page_index = min(
                    len(self.analyzer.paginas) - 1, 
                    self.analyzer.current_page_index + 1
                )
            
            # Processa o arquivo novamente
            self.process_file(self.file_path)
        except Exception as e:
            logger.error(f"Erro ao navegar: {str(e)}")
            self.status_label.configure(text=f"Erro ao navegar: {str(e)}")

    def confirm_page(self):
        """Confirma a página atual como contendo a manifestação correta."""
        try:
            if hasattr(self.analyzer, 'paginas') and self.analyzer.paginas:
                # Usa o texto da página atual como contexto
                pagina_atual = self.analyzer.paginas[self.analyzer.current_page_index]
                result = self.analyzer.analyze_document(None, pagina_atual['texto'])
                
                # Atualiza a interface
                self.update_ui_with_result(result)
                
                # Fecha o diálogo de navegação
                if hasattr(self, 'nav_dialog'):
                    self.nav_dialog.destroy()
                    delattr(self, 'nav_dialog')
        except Exception as e:
            logger.error(f"Erro ao confirmar página: {str(e)}")
            self.status_label.configure(text=f"Erro ao confirmar página: {str(e)}")

    def ask_question(self):
        """Processa uma pergunta do usuário."""
        try:
            question = self.question_entry.get()
            if not question:
                return

            self.result_text.insert("end", f"\n\nPergunta: {question}\n")
            self.result_text.insert("end", "Processando...\n")
            self.update_idletasks()

            response = self.analyzer.answer_question(question, self.current_context)
            self.result_text.insert("end", f"Resposta: {response}\n")

            # Limpa a entrada
            self.question_entry.delete(0, "end")

        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {str(e)}")
            self.result_text.insert("end", f"Erro ao processar pergunta: {str(e)}\n")

    def process_completion(self):
        """Processa o complemento fornecido pelo usuário com o Auxiliar de Promotoria."""
        try:
            # Verifica se já existe uma janela de diálogo
            if not hasattr(self, 'complete_dialog') or not self.complete_dialog.winfo_exists():
                # Cria nova janela de diálogo
                self.complete_dialog = ctk.CTkToplevel(self)
                self.complete_dialog.title("Auxiliar de Promotoria")
                self.complete_dialog.geometry("1000x800")
                
                # Frame principal
                main_frame = ctk.CTkFrame(self.complete_dialog)
                main_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Frame superior para controles
                control_frame = ctk.CTkFrame(main_frame)
                control_frame.pack(fill="x", padx=10, pady=10)
                
                # Campo de busca
                self.search_entry = ctk.CTkEntry(
                    control_frame,
                    placeholder_text="Buscar palavra-chave ou frase...",
                    width=400
                )
                self.search_entry.pack(side="left", padx=5, pady=5)
                
                # Botão de busca
                search_button = ctk.CTkButton(
                    control_frame,
                    text="Buscar",
                    command=self._search_in_complete_text,
                    width=100
                )
                search_button.pack(side="left", padx=5, pady=5)
                
                # Botão de análise com IA
                analyze_button = ctk.CTkButton(
                    control_frame,
                    text="Analisar com IA",
                    command=self._analyze_with_ai,
                    width=120
                )
                analyze_button.pack(side="left", padx=5, pady=5)
                
                # Botão de conversa
                self.chat_button = ctk.CTkButton(
                    control_frame,
                    text="Conversar",
                    command=self._chat_with_ai,
                    width=120
                )
                self.chat_button.pack(side="left", padx=5, pady=5)
                
                # Frame para conteúdo
                content_frame = ctk.CTkFrame(main_frame)
                content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Área de texto com conteúdo consolidado
                self.complete_text_area = ctk.CTkTextbox(content_frame)
                self.complete_text_area.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Frame inferior para resultados
                result_frame = ctk.CTkFrame(main_frame)
                result_frame.pack(fill="x", padx=10, pady=10)
                
                # Área de texto para resultados da IA
                self.ai_result_area = ctk.CTkTextbox(result_frame, height=150)
                self.ai_result_area.pack(fill="x", padx=10, pady=10)
            
            # Preenche o conteúdo consolidado
            self.complete_text_area.delete("1.0", "end")
            self.ai_result_area.delete("1.0", "end")
            
            # Obtém o texto consolidado
            if hasattr(self, 'rules_manager_dialog') and self.rules_manager_dialog.consolidated_text:
                text_blocks = self.rules_manager_dialog.consolidated_text.split('\n\n')
                promotor_text = text_blocks[0] if text_blocks else ""
                
                # Insere a manifestação completa
                self.complete_text_area.insert("end", "Última Manifestação do Promotor:\n")
                self.complete_text_area.insert("end", promotor_text)
                self.complete_text_area.insert("end", "\n\n")
            
            # Obtém e insere todas as regras cadastradas
            self.complete_text_area.insert("end", "Regras Cadastradas:\n")
            for rule_type in ['pre_analysis', 'final_output', 'alerts', 'exceptions']:
                rules = self.rules_manager.get_rules(rule_type)
                if rules:
                    self.complete_text_area.insert("end", f"\nTipo: {rule_type.upper()}\n")
                    for rule in rules:
                        self.complete_text_area.insert("end", f"- {rule['name']}\n")
                        if 'condition' in rule:
                            self.complete_text_area.insert("end", f"  Condição: {rule['condition']}\n")
                        if 'action' in rule:
                            self.complete_text_area.insert("end", f"  Ação: {rule['action']}\n")
                        if 'keywords' in rule:
                            self.complete_text_area.insert("end", f"  Palavras-chave: {', '.join(rule['keywords'])}\n")
                        self.complete_text_area.insert("end", "\n")
            
            # Foca na janela de diálogo
            self.complete_dialog.focus_force()
            
        except Exception as e:
            logger.error(f"Erro ao processar complemento: {str(e)}")
            self.result_text.insert("end", f"\n\nErro ao processar complemento: {str(e)}\n")

    def _analyze_with_ai(self):
        """Analisa o conteúdo com o Auxiliar de Promotoria."""
        try:
            # Obtém o texto selecionado ou todo o conteúdo
            selected_text = self.complete_text_area.get("sel.first", "sel.last")
            if not selected_text:
                selected_text = self.complete_text_area.get("1.0", "end")
            
            # Limpa a área de resultados
            self.ai_result_area.delete("1.0", "end")
            self.ai_result_area.insert("end", "Analisando com IA...\n")
            self.update_idletasks()
            
            # Cria uma nova instância do analisador com contexto restrito
            restricted_analyzer = self.analyzer_factory.create_analyzer(self.model_var.get())
            restricted_analyzer.set_context(selected_text)
            
            # Analisa o texto selecionado com base nas regras
            result = restricted_analyzer.analyze_document_with_context(selected_text)
            
            # Exibe o resultado
            if result.get("success"):
                self.ai_result_area.delete("1.0", "end")
                self.ai_result_area.insert("end", "Resultado da Análise:\n\n")
                self.ai_result_area.insert("end", result.get("report", "Nenhuma ação recomendada"))
            else:
                self.ai_result_area.insert("end", f"\nErro na análise: {result.get('error', 'Erro desconhecido')}")
            
        except Exception as e:
            self.ai_result_area.insert("end", f"\nErro ao analisar texto: {str(e)}")

    def _search_in_complete_text(self):
        """Realiza busca no texto consolidado."""
        try:
            keyword = self.search_entry.get().strip()
            if not keyword:
                return
                
            # Obtém todo o texto consolidado
            complete_text = self.complete_text_area.get("1.0", "end")
            
            # Realiza a busca
            matches = []
            for match in re.finditer(re.escape(keyword), complete_text, re.IGNORECASE):
                # Captura o contexto (15 palavras antes e depois)
                start = max(0, match.start() - 150)
                end = min(len(complete_text), match.end() + 150)
                context = complete_text[start:end]
                
                matches.append({
                    'position': match.start(),
                    'context': context
                })
                
            # Exibe os resultados na área de resultados da IA
            self.ai_result_area.delete("1.0", "end")
            if matches:
                self.ai_result_area.insert("end", f"Resultados para '{keyword}':\n\n")
                for match in matches:
                    self.ai_result_area.insert("end", f"...{match['context']}...\n\n")
                    self.ai_result_area.insert("end", "-"*50 + "\n")
            else:
                self.ai_result_area.insert("end", f"Nenhum resultado encontrado para '{keyword}'.\n")
                
        except Exception as e:
            self.ai_result_area.insert("end", f"Erro ao realizar busca: {str(e)}\n")

    def _chat_with_ai(self):
        """Processa a interação do usuário com o Auxiliar de Promotoria."""
        try:
            # Obtém a pergunta do usuário da área de resultados da IA
            user_input = self.ai_result_area.get("1.0", "end").strip()
            if not user_input:
                return

            # Obtém o histórico de conversa existente
            current_content = self.ai_result_area.get("1.0", "end").strip()
            chat_history = []
            if "Você:" in current_content:
                # Extrai o histórico de conversa existente
                messages = current_content.split("\n\n")
                for i in range(0, len(messages)-1, 2):
                    if messages[i].startswith("Você:"):
                        user_msg = messages[i].replace("Você:", "").strip()
                        assistant_msg = messages[i+1].replace("Auxiliar de Promotoria:", "").strip()
                        chat_history.append({"role": "user", "content": user_msg})
                        chat_history.append({"role": "assistant", "content": assistant_msg})

            # Obtém apenas o texto relevante da área de texto principal
            text_content = self.complete_text_area.get("1.0", "end").strip()
            context = ""
            
            # Extrai apenas a última manifestação do promotor
            if "Última Manifestação do Promotor:" in text_content:
                context = text_content.split("Última Manifestação do Promotor:")[1].split("Regras Cadastradas:")[0].strip()
            
            # Limpa a área de resultados mantendo o histórico
            self.ai_result_area.delete("1.0", "end")
            self.ai_result_area.insert("end", "Processando...\n")
            self.update_idletasks()

            # Cria uma nova instância do analisador
            analyzer = self.analyzer_factory.create_analyzer(self.model_var.get())
            
            # Prepara o contexto com o histórico de conversa
            if chat_history:
                context_with_history = (
                    "Histórico da conversa:\n" + 
                    "\n".join([f"Usuário: {msg['content']}" if msg['role'] == 'user' else f"Assistente: {msg['content']}" 
                              for msg in chat_history[-4:]]) +  # Mantém apenas as últimas 2 interações
                    "\n\nÚltima Manifestação do Promotor:\n" + context
                )
            else:
                context_with_history = "Última Manifestação do Promotor:\n" + context

            # Define o contexto reduzido
            analyzer.set_context(context_with_history)

            # Processa a pergunta do usuário
            response = analyzer.answer_question(user_input)

            # Reconstrói a área de resultados com o histórico
            self.ai_result_area.delete("1.0", "end")
            if chat_history:
                for i in range(0, len(chat_history), 2):
                    self.ai_result_area.insert("end", f"Você: {chat_history[i]['content']}\n\n")
                    self.ai_result_area.insert("end", f"Auxiliar de Promotoria: {chat_history[i+1]['content']}\n\n")
            
            # Adiciona a nova interação
            self.ai_result_area.insert("end", f"Você: {user_input}\n\n")
            self.ai_result_area.insert("end", f"Auxiliar de Promotoria: {response}\n")

        except Exception as e:
            self.ai_result_area.insert("end", f"\nErro ao processar interação: {str(e)}\n")

    def update_ui_with_result(self, result):
        """Atualiza a interface com o resultado da análise."""
        try:
            if result["success"]:
                self.current_context = result.get("context", "")
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", result["report"])
                
                # Habilita os campos de complemento e perguntas
                self.complete_entry.configure(state="normal")
                self.complete_button.configure(state="normal")
                self.question_entry.configure(state="normal")
                self.ask_button.configure(state="normal")
                
                # Pergunta se o Promotor está correto
                reply = ctk.CTkInputDialog(
                    title="Confirmação do Promotor",
                    text="O último Promotor manifestante informado no relatório está correto? (S/N)"
                ).get_input()
                
                if reply and reply.upper() == "N":
                    # Pede a página da última manifestação
                    page = ctk.CTkInputDialog(
                        title="Página da Manifestação",
                        text="Informe a página da última manifestação:"
                    ).get_input()
                    
                    if page and page.isdigit():
                        # Atualiza a análise com a página específica
                        self.analyzer.specific_page = int(page)
                        self.process_file(self.file_path)
                else:
                    # Desbloqueia a limpeza dos arquivos temporários
                    if hasattr(self, 'current_splitter') and self.current_splitter:
                        self.current_splitter.unblock_cleanup()
                        # Limpa os arquivos apenas se o usuário confirmar que está tudo certo
                        self.current_splitter.cleanup()
                        self.current_splitter = None
            else:
                self.result_text.delete("1.0", "end")
                self.result_text.insert("end", f"Erro: {result['error']}")
                
                # Desabilita os campos em caso de erro
                self.complete_entry.configure(state="disabled")
                self.complete_button.configure(state="disabled")
                self.question_entry.configure(state="disabled")
                self.ask_button.configure(state="disabled")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar interface: {str(e)}")
            self.result_text.delete("1.0", "end")
            self.result_text.insert("end", f"Erro ao atualizar interface: {str(e)}")

    def show_search_dialog(self):
        """Mostra o diálogo de busca por palavras-chave."""
        if not hasattr(self, 'search_dialog') or not self.search_dialog.winfo_exists():
            self.search_dialog = ctk.CTkToplevel(self)
            self.search_dialog.title("Busca no Documento")
            self.search_dialog.geometry("400x200")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.search_dialog)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Campo de busca
            self.search_entry = ctk.CTkEntry(
                main_frame,
                placeholder_text="Digite a palavra-chave para buscar..."
            )
            self.search_entry.pack(fill="x", padx=10, pady=10)
            
            # Botão de busca
            search_button = ctk.CTkButton(
                main_frame,
                text="Buscar",
                command=self.perform_search
            )
            search_button.pack(pady=10)
            
            # Área de resultados
            self.search_results = ctk.CTkTextbox(main_frame)
            self.search_results.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.search_dialog.focus_force()

    def perform_search(self):
        """Executa a busca no texto consolidado."""
        try:
            keyword = self.search_entry.get().strip()
            if not keyword:
                return
                
            if not hasattr(self, 'rules_manager_dialog') or not self.rules_manager_dialog.consolidated_text:
                self.search_results.insert("end", "Nenhum texto consolidado disponível para busca.\n")
                return
                
            # Obtém o texto consolidado
            consolidated_text = self.rules_manager_dialog.consolidated_text
            
            # Realiza a busca
            matches = []
            for match in re.finditer(re.escape(keyword), consolidated_text, re.IGNORECASE):
                # Captura o contexto (15 palavras antes e depois)
                start = max(0, match.start() - 150)
                end = min(len(consolidated_text), match.end() + 150)
                context = consolidated_text[start:end]
                
                matches.append({
                    'position': match.start(),
                    'context': context
                })
                
            # Exibe os resultados
            self.search_results.delete("1.0", "end")
            if matches:
                self.search_results.insert("end", f"Resultados para '{keyword}':\n\n")
                for match in matches:
                    self.search_results.insert("end", f"...{match['context']}...\n\n")
                    self.search_results.insert("end", "-"*50 + "\n")
            else:
                self.search_results.insert("end", f"Nenhum resultado encontrado para '{keyword}'.\n")
                
        except Exception as e:
            self.search_results.insert("end", f"Erro ao realizar busca: {str(e)}\n")

    def show_rules_manager(self):
        """Mostra o diálogo de gerenciamento de regras."""
        if not hasattr(self, 'rules_manager_dialog') or not self.rules_manager_dialog.winfo_exists():
            self.rules_manager_dialog = RulesManagerDialog(self, self.rules_manager)
        else:
            self.rules_manager_dialog.focus_force()

    def show_rules_registration(self):
        """Mostra o diálogo de cadastro de regras."""
        dialog = RulesRegistrationDialog(self, self.rules_manager)
        self.wait_window(dialog)

    def run(self):
        """Inicia a execução da interface."""
        self.mainloop()
