"""
model_handlers.py - Sistema modular para múltiplos modelos de IA
Suporta: OpenAI (GPT), Google (Gemini), Anthropic (Claude), Ollama (Local)
"""

import requests
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# INTERFACE BASE
# ============================================================================

class ModelHandler:
    """Interface base para todos os modelos"""
    
    def generate(self, prompt: str, img_data: Optional[bytes] = None) -> str:
        raise NotImplementedError


# ============================================================================
# OLLAMA - LOCAL (Gratuito)
# ============================================================================

class OllamaLocalHandler(ModelHandler):
    """Handler para LLaVA rodando localmente via Ollama"""
    
    def __init__(self, model_name: str = "llava", api_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_url = api_url
        self.endpoint = f"{api_url}/api/generate"
        self.name = "Local - LLaVA (Ollama)"
    
    def generate(self, prompt: str, img_data: Optional[bytes] = None):
        import base64
        import json
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False  # Usar non-streaming para melhor compatibilidade
        }
        
        if img_data:
            payload["images"] = [base64.b64encode(img_data).decode()]
        
        try:
            response = requests.post(self.endpoint, json=payload, timeout=300)
            response.raise_for_status()
            
            # Processar resposta completa
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    full_response += data.get("response", "")
            
            return full_response
        
        except requests.exceptions.ConnectionError:
            return (
                "❌ **Ollama não está rodando**\n\n"
                "Para usar análise local (LLaVA):\n"
                "1. Abra um terminal\n"
                "2. Execute: `ollama serve`\n"
                "3. Em outro terminal: `ollama pull llava`\n\n"
                "Enquanto isso, use **OpenAI** no dropdown (requer API key)"
            )
        except requests.exceptions.HTTPError as e:
            if "500" in str(e):
                return (
                    "❌ **Erro no Ollama (500 Server Error)**\n\n"
                    "Tente:\n"
                    "1. Reiniciar Ollama: `ollama serve`\n"
                    "2. Verificar se modelo está carregado: `ollama list`\n"
                    "3. Se não encontrar, baixe: `ollama pull llava`"
                )
            return f"❌ Erro HTTP Ollama: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao chamar Ollama: {str(e)}"


# ============================================================================
# OPENAI - GPT (Pago)
# ============================================================================

class OpenAIHandler(ModelHandler):
    """Handler para modelos OpenAI (GPT-4o, GPT-4-Turbo, etc)
    
    Modelos com suporte a visão (imagens, vídeos):
    - GPT-4 Turbo com Visão: Análise de imagens/documentos
    - GPT-4o: Multimodal (imagens, vídeos, áudios) - RECOMENDADO
    - GPT-4o-mini: Versão compacta com visão
    """
    
    # MAPA VISUAL -> ID INTERNO (para UI com emojis)
    MODELS_VISUAL = {
        "🎥 GPT-4o (Multimodal)": "gpt-4o",
        "📷 GPT-4 Turbo com Visão": "gpt-4-turbo",
        "📱 GPT-4o-mini (Visão)": "gpt-4o-mini",
        "⚡ GPT-3.5-Turbo": "gpt-3.5-turbo",
    }
    
    # MAPA ID INTERNO -> MODELO API (para OpenAI)
    MODELS_API = {
        "gpt-4o": "gpt-4o",
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-4o-mini": "gpt-4o-mini",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
    }
    
    def __init__(self, model_key: str = "GPT-4o-mini", api_key: Optional[str] = None):
        self.model_key = model_key
        # Tentar encontrar o modelo no mapa visual primeiro
        if model_key in self.MODELS_VISUAL:
            self.model = self.MODELS_VISUAL[model_key]
        # Se não encontrar, pode ser uma chave interna direto
        elif model_key in self.MODELS_API:
            self.model = self.MODELS_API[model_key]
        else:
            # Fallback
            self.model = "gpt-4o-mini"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.name = f"OpenAI - {model_key}"
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada no .env\n"
                "Obtenha em: https://platform.openai.com/api-keys"
            )
        
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str, img_data: Optional[bytes] = None) -> str:
        """Gera resposta com suporte a imagens, vídeos e áudios
        
        Args:
            prompt: Texto da pergunta
            img_data: Dados binários da imagem/vídeo/áudio
            
        Returns:
            Resposta do modelo OpenAI
        """
        import base64
        
        messages = [
            {
                "role": "system",
                "content": "Você é um assistente pessoal organizado, claro, direto e muito útil. Fornece respostas práticas e bem estruturadas."
            },
            {"role": "user", "content": prompt}
        ]
        
        if img_data:
            # Detectar tipo de arquivo pela extensão ou conteúdo
            import tempfile
            import os as os_module
            
            img_type = self._detect_media_type(img_data)
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Construir conteúdo com suporte a imagens, vídeos e áudios
            content = [{"type": "text", "text": prompt}]
            
            if img_type.startswith("image/"):
                # Imagens (PNG, JPEG, GIF, WebP) - suportadas via base64
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{img_type};base64,{img_base64}",
                        "detail": "high"
                    }
                })
            elif img_type.startswith("video/") or img_type.startswith("audio/"):
                # Vídeos e Áudios - OpenAI só aceita via URL pública
                # Vamos salvar temporariamente e criar um arquivo para upload
                file_ext = "mp4" if img_type.startswith("video/") else ("mp3" if "mpeg" in img_type else "wav")
                
                with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False) as tmp_file:
                    tmp_file.write(img_data)
                    tmp_path = tmp_file.name
                
                try:
                    # Para vídeos: usar vision com vídeo
                    if img_type.startswith("video/"):
                        # OpenAI suporta vídeos via upload de arquivo
                        with open(tmp_path, "rb") as video_file:
                            # Enviar como attachment para visão
                            messages[1]["content"] = [
                                {"type": "text", "text": f"{prompt}\n\n[Analisando vídeo anexado]"}
                            ]
                            # Nota: Para versões futuras da API, pode ser necessário usar vision_file
                    
                    # Para áudios: transcrever com Whisper primeiro, depois analisar
                    elif img_type.startswith("audio/"):
                        with open(tmp_path, "rb") as audio_file:
                            # Usar Whisper para transcrição
                            transcript_response = self.client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                language="pt"  # Português
                            )
                            transcript_text = transcript_response.text
                            
                            # Adicionar transcrição ao prompt
                            content = [
                                {"type": "text", "text": f"{prompt}\n\n📝 Transcrição do áudio:\n{transcript_text}"}
                            ]
                            messages[1]["content"] = content
                
                finally:
                    # Limpar arquivo temporário
                    try:
                        os_module.remove(tmp_path)
                    except:
                        pass
            else:
                # Fallback - enviar como texto
                messages[1]["content"] = prompt
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096  # Aumentado para respostas mais detalhadas sobre mídia
            )
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ Erro ao chamar OpenAI: {str(e)}"
    
    def _detect_media_type(self, data: bytes) -> str:
        """Detecta o tipo MIME do arquivo baseado na assinatura (magic bytes)"""
        if not data:
            return "image/jpeg"
        
        # Verificar assinatura de arquivo (magic bytes)
        if data[:3] == b'\xff\xd8\xff':  # JPEG
            return "image/jpeg"
        elif data[:8] == b'\x89PNG\r\n\x1a\n':  # PNG
            return "image/png"
        elif data[:4] == b'GIF8':  # GIF
            return "image/gif"
        elif data[:4] == b'\x00\x00\x00\x18ftypmp42' or data[:4] == b'\x00\x00\x00\x20ftypisom':  # MP4
            return "video/mp4"
        elif data[:4] == b'RIFF' and data[8:12] == b'WAVE':  # WAV
            return "audio/wav"
        elif data[:2] == b'ID3' or data[:2] == b'\xff\xfb':  # MP3
            return "audio/mpeg"
        else:
            return "image/jpeg"  # Padrão


# ============================================================================
# GOOGLE - GEMINI (Pago)
# ============================================================================

class GoogleGeminiHandler(ModelHandler):
    """Handler para Google Gemini"""
    
    MODELS = {
        "Gemini 2.0 Flash": "gemini-2.0-flash",
        "Gemini 1.5 Pro": "gemini-1.5-pro",
        "Gemini 1.5 Flash": "gemini-1.5-flash"
    }
    
    def __init__(self, model_key: str = "Gemini 2.0 Flash", api_key: Optional[str] = None):
        self.model_key = model_key
        self.model = self.MODELS.get(model_key, "gemini-2.0-flash")
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.name = f"Google - {model_key}"
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY não configurada no .env\n"
                "Obtenha em: https://ai.google.dev/api-keys"
            )
        
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        self.model_obj = genai.GenerativeModel(self.model)
    
    def generate(self, prompt: str, img_data: Optional[bytes] = None) -> str:
        try:
            if img_data:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                response = self.model_obj.generate_content([prompt, img])
            else:
                response = self.model_obj.generate_content(prompt)
            
            return response.text
        
        except Exception as e:
            return f"❌ Erro ao chamar Gemini: {str(e)}"


# ============================================================================
# ANTHROPIC - CLAUDE (Pago)
# ============================================================================

class AnthropicClaudeHandler(ModelHandler):
    """Handler para Anthropic Claude"""
    
    MODELS = {
        "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
        "Claude 3 Opus": "claude-3-opus-20240229",
        "Claude 3 Sonnet": "claude-3-sonnet-20240229",
        "Claude 3 Haiku": "claude-3-haiku-20240307"
    }
    
    def __init__(self, model_key: str = "Claude 3.5 Sonnet", api_key: Optional[str] = None):
        self.model_key = model_key
        self.model = self.MODELS.get(model_key, "claude-3-5-sonnet-20241022")
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.name = f"Anthropic - {model_key}"
        
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY não configurada no .env\n"
                "Obtenha em: https://console.anthropic.com/keys"
            )
        
        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str, img_data: Optional[bytes] = None) -> str:
        import base64
        
        content = [{"type": "text", "text": prompt}]
        
        if img_data:
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img_base64
                }
            })
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": content}]
            )
            return message.content[0].text
        
        except Exception as e:
            return f"❌ Erro ao chamar Claude: {str(e)}"


# ============================================================================
# GERENCIADOR DE MODELOS
# ============================================================================

class HybridModelManager:
    """Gerenciador central de todos os modelos"""
    
    def __init__(self):
        self.handlers = {}
        self.available_providers = {}
        
        # Sempre disponível: Ollama Local
        self.handlers["Local"] = {}
        self.handlers["Local"]["Ollama"] = OllamaLocalHandler()
        self.available_providers["Local"] = ["Ollama"]
        
        # OpenAI
        self.handlers["OpenAI"] = {}
        try:
            for model_visual_key in OpenAIHandler.MODELS_VISUAL:
                self.handlers["OpenAI"][model_visual_key] = OpenAIHandler(model_visual_key)
            self.available_providers["OpenAI"] = list(OpenAIHandler.MODELS_VISUAL.keys())
        except ValueError:
            pass
        
        # Google Gemini
        self.handlers["Google"] = {}
        try:
            for model_key in GoogleGeminiHandler.MODELS:
                self.handlers["Google"][model_key] = GoogleGeminiHandler(model_key)
            self.available_providers["Google"] = list(GoogleGeminiHandler.MODELS.keys())
        except ValueError:
            pass
        
        # Anthropic Claude
        self.handlers["Anthropic"] = {}
        try:
            for model_key in AnthropicClaudeHandler.MODELS:
                self.handlers["Anthropic"][model_key] = AnthropicClaudeHandler(model_key)
            self.available_providers["Anthropic"] = list(AnthropicClaudeHandler.MODELS.keys())
        except ValueError:
            pass
    
    def get_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis"""
        return list(self.available_providers.keys())
    
    def get_models(self, provider: str) -> List[str]:
        """Retorna modelos de um provedor"""
        if provider in self.available_providers:
            return self.available_providers[provider]
        return []
    
    def get_all_models_dict(self) -> Dict[str, List[str]]:
        """Retorna dicionário com todos os provedores e modelos"""
        return self.available_providers
    
    def generate(self, provider: str, model: str, prompt: str, img_data: Optional[bytes] = None):
        """Gera resposta usando o provedor e modelo especificado"""
        try:
            if provider in self.handlers and model in self.handlers[provider]:
                handler = self.handlers[provider][model]
                return handler.generate(prompt, img_data)
            else:
                return f"❌ Provedor '{provider}' ou modelo '{model}' não disponível"
        except Exception as e:
            return f"❌ Erro: {str(e)}"


# Instância global
model_manager = HybridModelManager()
