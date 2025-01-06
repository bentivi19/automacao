import os
import fitz  # PyMuPDF
import logging
import re
import tempfile
from typing import List

logger = logging.getLogger(__name__)

class PDFSplitter:
    def __init__(self, max_tokens_per_chunk: int = 15000):
        """
        Inicializa o PDFSplitter com um limite máximo de tokens por chunk.
        O limite padrão é 15000 para garantir que não exceda o limite do modelo.
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_chunks_")
        # Reserva 70% dos tokens para o prompt do sistema e overhead
        self.effective_token_limit = int(max_tokens_per_chunk * 0.3)
        # Limite para forçar quebra de texto ainda menor
        self.force_split_limit = int(max_tokens_per_chunk * 0.2)
        # Limite mínimo para chunks
        self.min_chunk_size = int(max_tokens_per_chunk * 0.1)
        # Flag para controlar se os arquivos já foram limpos
        self.cleaned_up = False
        # Flag para controlar se a limpeza está bloqueada
        self.cleanup_blocked = False
        logger.info(f"Diretório temporário criado em: {self.temp_dir}")

    def estimate_tokens(self, text: str) -> int:
        """Estimativa aproximada de tokens baseada no número de palavras."""
        # Uma estimativa conservadora: cada palavra tem em média 1.3 tokens
        return int(len(text.split()) * 1.3)

    def split_pdf(self, input_path: str) -> List[str]:
        """
        Divide um PDF em chunks de texto mantendo o contexto e respeitando o limite de tokens.
        Para documentos muito grandes, usa uma estratégia adaptativa de divisão.
        """
        try:
            # Extrai todo o texto do PDF preservando a ordem
            text_content = self._extract_text_with_context(input_path)
            if not text_content.strip():
                raise ValueError("Nenhum texto encontrado no documento")

            # Estima o tamanho total do documento
            total_tokens = self.estimate_tokens(text_content)
            logger.info(f"Documento tem aproximadamente {total_tokens} tokens")

            # Ajusta os limites baseado no tamanho do documento
            if total_tokens > 100000:  # Documento muito grande
                logger.info("Documento muito grande detectado. Usando estratégia adaptativa.")
                self.effective_token_limit = int(self.max_tokens_per_chunk * 0.25)  # 25% para mais margem
                self.force_split_limit = int(self.max_tokens_per_chunk * 0.15)  # 15% para chunks menores
            elif total_tokens > 50000:  # Documento grande
                logger.info("Documento grande detectado. Usando limites mais restritivos.")
                self.effective_token_limit = int(self.max_tokens_per_chunk * 0.3)  # 30% normal
                self.force_split_limit = int(self.max_tokens_per_chunk * 0.2)  # 20% normal
            else:  # Documento normal
                logger.info("Documento de tamanho normal detectado.")
                self.effective_token_limit = int(self.max_tokens_per_chunk * 0.4)  # 40% para docs normais
                self.force_split_limit = int(self.max_tokens_per_chunk * 0.25)  # 25% para docs normais

            # Primeira divisão em chunks grandes
            initial_chunks = self._create_text_chunks(text_content)
            if not initial_chunks:
                raise ValueError("Não foi possível criar chunks válidos do documento")

            # Segunda divisão para garantir tamanho máximo
            medium_chunks = []
            for chunk in initial_chunks:
                if self.estimate_tokens(chunk) > self.effective_token_limit:
                    medium_chunks.extend(self._force_split_chunk(chunk))
                else:
                    medium_chunks.append(chunk)

            # Terceira divisão para garantir tamanho máximo absoluto
            final_chunks = []
            for chunk in medium_chunks:
                chunk_tokens = self.estimate_tokens(chunk)
                if chunk_tokens > self.force_split_limit:
                    # Divide em partes ainda menores
                    sub_chunks = self._split_to_minimal_chunks(chunk)
                    final_chunks.extend(sub_chunks)
                else:
                    final_chunks.append(chunk)

            # Combina chunks muito pequenos
            optimized_chunks = self._optimize_chunks(final_chunks)

            # Salva os chunks em arquivos de texto
            chunk_paths = []
            for i, chunk in enumerate(optimized_chunks, 1):
                chunk_tokens = self.estimate_tokens(chunk)
                logger.info(f"Chunk {i} tem {chunk_tokens} tokens")
                
                chunk_path = os.path.join(self.temp_dir, f"chunk_{i}.txt")
                with open(chunk_path, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                chunk_paths.append(chunk_path)
                logger.info(f"Chunk {i} salvo em: {chunk_path}")

            logger.info(f"Documento dividido em {len(chunk_paths)} partes")
            return chunk_paths

        except Exception as e:
            logger.error(f"Erro ao dividir PDF: {str(e)}")
            raise

    def _extract_text_with_context(self, pdf_path: str) -> str:
        """
        Extrai texto do PDF mantendo o contexto e a ordem.
        Inclui informações de página para melhor rastreamento.
        """
        doc = None
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            total_pages = len(doc)
            logger.info(f"Iniciando extração de {total_pages} páginas do PDF")
            
            for page_num in range(total_pages):
                try:
                    page = doc[page_num]
                    # Extrai texto com informações de layout
                    blocks = page.get_text("blocks")
                    if not blocks:
                        # Tenta outros métodos de extração
                        text = page.get_text("text")
                        if text.strip():
                            # Tenta extrair o número real da página
                            real_page = self._extract_page_number(text.strip()) or (page_num + 1)
                            logger.info(f"Página {page_num + 1} (FL. {real_page}): Usando método alternativo de extração")
                            text_parts.append(f"\n[PÁGINA {real_page}]\n{text.strip()}\n")
                            continue
                        else:
                            logger.warning(f"Página {page_num + 1}: Nenhum texto encontrado")
                            continue
                    
                    # Ordena blocos por posição vertical (y0) e horizontal (x0)
                    blocks.sort(key=lambda b: (b[1], b[0]))
                    
                    # Junta todo o texto da página para procurar o número real
                    full_text = "\n".join(block[4].strip() for block in blocks if block[4].strip())
                    real_page = self._extract_page_number(full_text) or (page_num + 1)
                    
                    # Adiciona número da página e texto
                    page_text = [f"\n[PÁGINA {real_page}]\n"]
                    for block in blocks:
                        text = block[4].strip()
                        if text:  # Só adiciona se tiver conteúdo
                            page_text.append(text)
                    
                    # Verifica se extraiu algum texto da página
                    if len(page_text) > 1:  # Mais que só o cabeçalho
                        text_parts.append("\n".join(page_text))
                        logger.info(f"Página {page_num + 1} (FL. {real_page}): {len(blocks)} blocos extraídos")
                    else:
                        logger.warning(f"Página {page_num + 1}: Nenhum texto extraído dos blocos")
                
                except Exception as e:
                    logger.error(f"Erro ao processar página {page_num + 1}: {str(e)}")
                    # Tenta método alternativo de extração
                    try:
                        text = page.get_text("text")
                        if text.strip():
                            # Tenta extrair o número real da página
                            real_page = self._extract_page_number(text.strip()) or (page_num + 1)
                            logger.info(f"Página {page_num + 1} (FL. {real_page}): Recuperada com método alternativo")
                            text_parts.append(f"\n[PÁGINA {real_page}]\n{text.strip()}\n")
                    except:
                        logger.error(f"Falha total na extração da página {page_num + 1}")
            
            # Verifica se extraiu texto de todas as páginas
            pages_with_text = len([p for p in text_parts if p.strip()])
            logger.info(f"Extração concluída: {pages_with_text} de {total_pages} páginas com texto")
            
            if pages_with_text == 0:
                raise ValueError("Nenhum texto extraído do documento")
            elif pages_with_text < total_pages:
                logger.warning(f"Algumas páginas ({total_pages - pages_with_text}) não retornaram texto")
            
            return "\n".join(text_parts)
            
        finally:
            if doc:
                doc.close()

    def _extract_page_number(self, page_text: str) -> int:
        """
        Extrai o número real da página do texto do PDF.
        Procura por padrões comuns de numeração.
        """
        patterns = [
            r'FL\.\s*(\d+)',      # FL. XXX
            r'FLS\.\s*(\d+)',     # FLS. XXX
            r'FOLHA\s*(\d+)',     # FOLHA XXX
            r'PÁGINA\s*(\d+)',    # PÁGINA XXX
            r'PAG\.\s*(\d+)',     # PAG. XXX
            r'P\.\s*(\d+)',       # P. XXX
            r'(\d+)/\d+',         # XXX/YYY
            r'\b(\d+)\b'          # XXX (número solto)
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None

    def _force_split_chunk(self, text: str) -> List[str]:
        """
        Força a divisão de um chunk em partes menores, garantindo que cada parte
        não exceda o limite de tokens efetivo.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        # Divide o texto em linhas
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_tokens = self.estimate_tokens(line)
            
            # Se a linha for muito grande, divide em palavras
            if line_tokens > self.force_split_limit:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Divide a linha em palavras
                words = line.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self.estimate_tokens(word)
                    if temp_tokens + word_tokens > self.force_split_limit:
                        if temp_chunk:
                            chunks.append(' '.join(temp_chunk))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    chunks.append(' '.join(temp_chunk))
            
            # Se adicionar a linha exceder o limite, cria novo chunk
            elif current_tokens + line_tokens > self.force_split_limit:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_tokens = line_tokens
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        # Adiciona o último chunk se houver
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def _create_text_chunks(self, text: str) -> List[str]:
        """
        Divide o texto em chunks iniciais, que podem ser posteriormente subdivididos
        se necessário.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        # Divide por páginas primeiro
        pages = text.split('[PÁGINA')
        
        for page in pages:
            if not page.strip():
                continue
                
            # Restaura o marcador de página se não for a primeira
            if pages.index(page) > 0:
                page = '[PÁGINA' + page
            
            page_tokens = self.estimate_tokens(page)
            
            # Se a página for muito grande, divide-a
            if page_tokens > self.force_split_limit:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Divide a página em parágrafos
                sub_chunks = self._force_split_chunk(page)
                chunks.extend(sub_chunks)
            
            # Se adicionar a página exceder o limite, cria novo chunk
            elif current_tokens + page_tokens > self.force_split_limit:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [page]
                current_tokens = page_tokens
            else:
                current_chunk.append(page)
                current_tokens += page_tokens
        
        # Adiciona o último chunk se houver
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    def _split_to_minimal_chunks(self, text: str) -> List[str]:
        """
        Divide o texto em chunks muito pequenos, garantindo que nenhum exceda o limite.
        """
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        # Divide por caracteres se necessário
        chars = list(text)
        temp_text = ""
        
        for char in chars:
            temp_text += char
            if self.estimate_tokens(temp_text) >= self.force_split_limit:
                chunks.append(temp_text[:-1])  # Remove o último char que causou o excesso
                temp_text = char  # Começa novo chunk com o char que excedeu
        
        if temp_text:
            chunks.append(temp_text)
        
        return chunks

    def _optimize_chunks(self, chunks: List[str]) -> List[str]:
        """
        Otimiza os chunks combinando os muito pequenos e dividindo os muito grandes.
        Garante que nenhum chunk exceda 6000 tokens (40% de 15000).
        """
        optimized = []
        current_chunk = ""
        current_tokens = 0
        target_size = self.effective_token_limit  # 6000 tokens
        
        for chunk in chunks:
            chunk_tokens = self.estimate_tokens(chunk)
            
            # Se o chunk for muito grande, divide
            if chunk_tokens > target_size:
                if current_chunk:
                    optimized.append(current_chunk)
                    current_chunk = ""
                    current_tokens = 0
                optimized.extend(self._split_to_minimal_chunks(chunk))
                
            # Se combinar os chunks não exceder o limite alvo
            elif current_tokens + chunk_tokens <= target_size:
                if current_chunk:
                    current_chunk += "\n"
                current_chunk += chunk
                current_tokens += chunk_tokens
                
            # Se exceder o limite, salva o atual e começa novo
            else:
                if current_chunk:
                    optimized.append(current_chunk)
                current_chunk = chunk
                current_tokens = chunk_tokens
        
        # Adiciona o último chunk
        if current_chunk:
            optimized.append(current_chunk)
        
        # Verifica novamente se algum chunk está muito grande
        final_chunks = []
        for chunk in optimized:
            chunk_tokens = self.estimate_tokens(chunk)
            if chunk_tokens > target_size:
                final_chunks.extend(self._force_split_chunk(chunk))
            else:
                final_chunks.append(chunk)
        
        return final_chunks

    def block_cleanup(self):
        """Bloqueia a limpeza dos arquivos temporários."""
        self.cleanup_blocked = True
        logger.info("Limpeza de arquivos temporários bloqueada")
    
    def unblock_cleanup(self):
        """Desbloqueia a limpeza dos arquivos temporários."""
        self.cleanup_blocked = False
        logger.info("Limpeza de arquivos temporários desbloqueada")

    def cleanup(self):
        """Remove os arquivos temporários."""
        if self.cleaned_up or self.cleanup_blocked:
            return
            
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo {file_path}: {str(e)}")
                    # Se falhar na primeira tentativa, tenta novamente após um breve delay
                    time.sleep(0.1)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e2:
                        logger.error(f"Segunda tentativa falhou ao remover arquivo {file_path}: {str(e2)}")
            
            # Tenta remover o diretório algumas vezes
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    os.rmdir(self.temp_dir)
                    logger.info("Arquivos temporários removidos com sucesso")
                    self.cleaned_up = True
                    break
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")
                    else:
                        time.sleep(0.1)
                        
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos temporários: {str(e)}")

    def __del__(self):
        """Garante que os arquivos temporários sejam removidos quando o objeto for destruído."""
        if not self.cleaned_up:
            self.cleanup()
