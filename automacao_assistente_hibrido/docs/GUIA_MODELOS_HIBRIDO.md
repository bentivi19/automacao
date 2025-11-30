# 🤖 Assistente Híbrido - Local + GPT-4o

## 📋 Visão Geral

O assistente agora suporta **2 modelos de IA**:

1. **Local - LLaVA (Ollama)** 📍
   - Roda no seu computador
   - Sem custos
   - Mais rápido
   - Suporta imagens e PDFs nativamente

2. **Nuvem - GPT-4o-mini** ☁️
   - Roda na nuvem OpenAI
   - Requer API key (pago, mas com plano gratuito)
   - Mais poderoso e criativo
   - Melhor para texto e análise

---

## ⚙️ Configuração

### **Opção 1: Usar Apenas Local (Padrão)**

1. Certifique-se que **Ollama está rodando**:
   ```powershell
   ollama serve
   ```

2. **Abra o Streamlit** (sem fazer mais nada):
   ```powershell
   streamlit run assistant.py
   ```

3. **Na sidebar**, você verá apenas:
   - "Local - LLaVA (Ollama)"

✅ **Pronto! Tudo funcionando.**

---

### **Opção 2: Usar Local + GPT-4o**

1. **Obtenha a chave OpenAI**:
   - Vá para: https://platform.openai.com/api-keys
   - Clique "Create new secret key"
   - Copie a chave (tipo: `sk-proj-...`)

2. **Configure no `.env`**:
   ```
   OPENAI_API_KEY=sk-proj-sua-chave-aqui
   ```

3. **Reinicie o Streamlit**:
   ```powershell
   streamlit run assistant.py
   ```

4. **Na sidebar**, você verá agora:
   - "Local - LLaVA (Ollama)"
   - "Nuvem - GPT-4o-mini" ← novo!

✅ **Pronto! Ambos disponíveis.**

---

## 🎯 Como Usar

### **Seletor de Modelo**

Na **aba Config** da sidebar:

```
⚙️ Configurações
  🤖 Modelo de IA
  [ Escolha o modelo ▼ ]
  - Local - LLaVA (Ollama)
  - Nuvem - GPT-4o-mini
```

Clique para alternar entre modelos. Sua escolha é **salva na sessão**.

### **Diferenças Práticas**

**Local (LLaVA):**
```
Você: "Analise esta imagem"
Modelo: Processa localmente, responde em 5-10 segundos
Custo: R$ 0,00
```

**Nuvem (GPT):**
```
Você: "Escreva um artigo sobre Python"
Modelo: Resposta mais criativa e detalhada
Custo: ~R$ 0,01-0,05 por pergunta (muito barato)
```

---

## 💻 Arquitetura Modular

### **model_handlers.py** - O coração do sistema

```python
# Interface unificada
class ModelHandler:
    def generate(prompt: str, img_data: bytes) -> str:
        raise NotImplementedError

# Implementações
class OllamaLocalHandler(ModelHandler):
    # Chama Ollama via HTTP
    
class GPTHandler(ModelHandler):
    # Chama OpenAI via SDK

# Gerenciador
class HybridModelManager:
    def generate(model_choice, prompt, img_data):
        # Roteia para o modelo certo
```

### **assistant.py** - Integração simples

```python
from model_handlers import model_manager

# Na sidebar
model_choice = st.selectbox("Escolha:", 
    options=model_manager.get_model_options()
)

# Na pergunta
resultado = model_manager.generate(
    model_choice, 
    prompt, 
    img_data
)
```

---

## 📊 Comparação de Modelos

| Aspecto | LLaVA Local | GPT-4o-mini |
|---------|-------------|------------|
| **Custo** | Grátis | ~$0.15/1K tokens |
| **Velocidade** | 5-10s | 2-5s |
| **Criatividade** | Boa | Excelente |
| **Análise de Imagens** | ✅ Sim | ✅ Sim |
| **Offline** | ✅ Sim | ❌ Não |
| **Qualidade Texto** | Boa | Excelente |
| **Requer API Key** | ❌ Não | ✅ Sim |

---

## 🔧 Troubleshooting

### **"Modelo não reconhecido"**
- Verifique se o modelo selecionado é exato
- Reinicie o Streamlit

### **"Ollama não está rodando"**
```powershell
# Terminal 1
ollama serve

# Terminal 2 (Streamlit)
streamlit run assistant.py
```

### **"OPENAI_API_KEY não configurada"**
- Verifique que copiou certo no `.env`
- A chave deve começar com `sk-proj-`
- Reinicie o Streamlit após editar `.env`

### **GPT retorna erro de quota**
- Você pode ter ultrapassado o free tier
- Verifique seu usage em: https://platform.openai.com/account/usage/overview
- Consideramos usar apenas Local para economizar

---

## 💡 Dicas de Uso

✅ **Combine os modelos:**
- Use **Local** para tarefas rápidas (resumos, lembretes)
- Use **GPT** para tarefas criativas (artigos, brainstorm)

✅ **Economize crédito GPT:**
- Deixe Local como padrão
- Use GPT apenas quando precisar

✅ **Aproveite o contexto de notas:**
- Ambos os modelos usam o histórico automaticamente
- Quanto melhor as notas, melhor a resposta

---

## 📝 Exemplo Real

**Cenário:** Pesquisa sobre Python

```
1. Local (LLaVA):
   "O que é Python?"
   → Resposta rápida e básica

2. Nuvem (GPT):
   "Escreva um guia completo sobre Python"
   → Resposta detalhada, artigo pronto

3. Local (LLaVA):
   "Resuma o artigo acima"
   → Resume em segundos (usa contexto de notas)
```

---

## 🚀 Próximas Melhorias (Futuro)

- [ ] Suporte a Claude (Anthropic)
- [ ] Suporte a Gemini (Google)
- [ ] Cache de respostas para economizar
- [ ] Histórico de qual modelo foi usado em cada nota
- [ ] Comparar respostas dos 2 modelos lado a lado

---

**Desenvolvido para máxima flexibilidade e modularidade!** 🎉
