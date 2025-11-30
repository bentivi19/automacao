# 🤖 Sistema de Múltiplos Modelos de IA

## 📋 Resumo

O **Assistente Pessoal** agora suporta modelos de IA de **4 provedores diferentes**:

| Provedor | Status | Modelos | Custo |
|----------|--------|---------|-------|
| **Local (Ollama)** | ✅ Funcionando | LLaVA | 📍 Gratuito |
| **OpenAI (GPT)** | ✅ Funcionando | GPT-4o, 4o-mini, 4-Turbo, 3.5-Turbo | 💰 Pago |
| **Google (Gemini)** | 🔔 Pronto | 2.0 Flash, 1.5 Pro, 1.5 Flash | 💰 Pago |
| **Anthropic (Claude)** | 🔔 Pronto | 3.5 Sonnet, 3 Opus, 3 Sonnet, 3 Haiku | 💰 Pago |

---

## 🚀 Como Usar

### 1. Interface no Streamlit

Após reiniciar o Streamlit, a barra lateral terá **dois seletores**:

```
⚙️ Configurações

🌐 Provedor:    [Local ▼]
🤖 Modelo:      [Ollama ▼]
```

**Fluxo:**
1. Escolha o **Provedor** (Local, OpenAI, Google, Anthropic)
2. O seletor de **Modelo** atualiza automaticamente
3. Escreva sua pergunta e clique "Enviar"

---

## 📦 Modelos Disponíveis

### 🏠 Local - Ollama (Gratuito)
- **Modelo:** LLaVA
- **Requer:** Ollama rodando (`ollama serve`)
- **Vantagens:** Rápido, offline, sem custos
- **Limitações:** Menos poderoso que nuvem
- **Status:** ✅ Pronto

**Para iniciar Ollama:**
```powershell
ollama serve
```

---

### ☁️ OpenAI - GPT (Pago)
- **Modelos disponíveis:**
  - **GPT-4o** - Mais novo e capaz (recomendado)
  - **GPT-4o-mini** - Equilibrado (custo/performance)
  - **GPT-4-Turbo** - Contexto grande
  - **GPT-3.5-Turbo** - Rápido e barato

- **Preços (aproximados):**
  - GPT-4o: ~$0.015 por 1K tokens
  - GPT-4o-mini: ~$0.0015 por 1K tokens
  - GPT-3.5-Turbo: ~$0.0005 por 1K tokens

- **Saldo Atual:** $10 de crédito
- **Status:** ✅ Funcionando e testado

**Verificar Saldo:**
```powershell
cd c:\AssistentePessoal
.\.venv\Scripts\activate
python test_openai_key.py
```

---

### 🔵 Google - Gemini (Pago, Opcional)
- **Modelos disponíveis:**
  - **Gemini 2.0 Flash** - Novo e rápido
  - **Gemini 1.5 Pro** - Mais avançado
  - **Gemini 1.5 Flash** - Equilibrado

- **Status:** 🔔 Pronto (faltando chave)
- **Preço:** Free tier disponível (~1000 requisições/mês)

**Para adicionar suporte:**

1. Obtenha chave em: https://ai.google.dev/api-keys
2. Adicione ao `.env`:
   ```
   GOOGLE_API_KEY=sua_chave_aqui
   ```
3. Reinicie Streamlit - Google aparecerá nos provedores

---

### 🔴 Anthropic - Claude (Pago, Opcional)
- **Modelos disponíveis:**
  - **Claude 3.5 Sonnet** - Novo e poderoso
  - **Claude 3 Opus** - Mais avançado
  - **Claude 3 Sonnet** - Equilibrado
  - **Claude 3 Haiku** - Rápido e barato

- **Status:** 🔔 Pronto (faltando chave)
- **Preço:** Comece com free trial

**Para adicionar suporte:**

1. Obtenha chave em: https://console.anthropic.com/keys
2. Adicione ao `.env`:
   ```
   ANTHROPIC_API_KEY=sua_chave_aqui
   ```
3. Reinicie Streamlit - Anthropic aparecerá nos provedores

---

## ⚙️ Configuração de API Keys

### Arquivo `.env`

Localização: `c:\AssistentePessoal\.env`

```
# Já configurado ✓
OPENAI_API_KEY=sk-proj-...

# Opcional - adicione se tiver:
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=

# Telegram (já configurado ✓)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Como Adicionar uma Chave

**Opção 1: PowerShell (Rápido)**
```powershell
# Google
Add-Content C:\AssistentePessoal\.env "GOOGLE_API_KEY=sua_chave_aqui"

# Anthropic
Add-Content C:\AssistentePessoal\.env "ANTHROPIC_API_KEY=sua_chave_aqui"
```

**Opção 2: Editar no Bloco de Notas**
1. Abra: `C:\AssistentePessoal\.env`
2. Adicione as linhas com suas chaves
3. Salve e reinicie o Streamlit

---

## 🧪 Testes

### Verificar Todos os Modelos
```powershell
cd c:\AssistentePessoal
.\.venv\Scripts\activate
python test_multi_models.py
```

**Saída esperada:**
```
Provedores disponíveis: ['Local', 'OpenAI']
✅ Local: 1 modelo(s) disponível(is)
✅ OpenAI: 4 modelo(s) disponível(is)
```

### Testar Geração de Respostas
```powershell
cd c:\AssistentePessoal
.\.venv\Scripts\activate
python test_generation_multi.py
```

### Testar OpenAI Específico
```powershell
cd c:\AssistentePessoal
.\.venv\Scripts\activate
python test_openai_key.py
```

---

## 📊 Comparação de Modelos

| Recurso | Local LLaVA | GPT-4o | Gemini 2.0 | Claude 3.5 |
|---------|-------------|--------|-----------|-----------|
| Velocidade | ⚡ Rápido | ⚡⚡ Muito rápido | ⚡⚡⚡ Ultrarrápido | ⚡ Rápido |
| Qualidade | ✓ Boa | ✓✓✓ Excelente | ✓✓✓ Excelente | ✓✓✓ Excelente |
| Criatividade | ✓ Boa | ✓✓✓ Muito boa | ✓✓ Boa | ✓✓✓ Muito boa |
| Análise | ✓ Boa | ✓✓✓ Excelente | ✓✓✓ Excelente | ✓✓✓ Excelente |
| Offline | ✓ Sim | ✗ Não | ✗ Não | ✗ Não |
| Custo | 📍 Grátis | 💰 Baixo | 💰 Médio | 💰 Médio |
| Imagens | ✓ Sim | ✓ Sim | ✓ Sim | ~ Sim |

---

## 🎯 Recomendações

### Para Uso Diário
- **Melhor Qualidade:** GPT-4o (quando tiver credits)
- **Melhor Custo-Benefício:** GPT-4o-mini
- **Sem Internet:** Local Ollama
- **Rápido e Barato:** GPT-3.5-Turbo

### Para Diferentes Tarefas
- **Análise Técnica:** GPT-4o-mini ➜ GPT-4o
- **Criatividade:** Claude 3.5 Sonnet
- **Pesquisa:** Gemini 2.0 Flash
- **Tarefas Simples:** Local LLaVA (offline)

---

## 🛠️ Arquitetura Técnica

### Estrutura de `model_handlers.py`

```
HybridModelManager (Central)
├── OllamaLocalHandler (sempre disponível)
├── OpenAIHandler (4 modelos GPT)
├── GoogleGeminiHandler (pronto, sem chave)
└── AnthropicClaudeHandler (pronto, sem chave)
```

### Como Funciona

1. **HybridModelManager** tenta carregar cada provedor
2. Se API key ausente ➜ provedor desabilitado (silenciosamente)
3. Se API key presente ➜ todos os modelos carregados
4. Streamlit só mostra provedores disponíveis

**Graceful Degradation:** Sistema funciona sem todas as chaves, mostrando apenas o que está configurado.

---

## ❓ Troubleshooting

### "Modelo não aparece no dropdown"
- ✅ Reiniciou Streamlit?
- ✅ API key está no `.env`?
- ✅ Sintaxe correta no `.env`?
- ✅ `.env` foi salvo?

### "Erro ao chamar modelo"
- Verifique o console do Streamlit (`terminal.log`)
- Teste com `test_generation_multi.py`
- Verifique API key e saldo da conta

### "Ollama offline"
```powershell
ollama serve  # Em outro PowerShell
```

### "Não tenho API key do Google/Anthropic"
- É totalmente opcional!
- Use apenas OpenAI e Local Ollama por enquanto
- Sistema funciona perfeitamente sem eles

---

## 📝 Próximos Passos

### Já Implementado ✅
- [x] Suporte a múltiplos provedores
- [x] Interface de seleção dinâmica
- [x] Graceful degradation
- [x] 4 modelos diferentes

### Você Pode Fazer Agora
- [ ] Adicionar chave do Google Gemini (opcional)
- [ ] Adicionar chave do Anthropic Claude (opcional)
- [ ] Comparar qualidade de respostas
- [ ] Escolher modelo favorito para cada tarefa

---

## 📞 Suporte

Para dúvidas sobre:
- **OpenAI:** https://platform.openai.com/docs
- **Google:** https://ai.google.dev/docs
- **Anthropic:** https://docs.anthropic.com
- **Ollama:** https://github.com/ollama/ollama

---

**Versão:** 1.0 (Multi-Provider)  
**Última atualização:** 2024  
**Status:** ✅ Funcionando perfeitamente
