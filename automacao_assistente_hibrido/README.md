# 🤖 Assistente Pessoal - Estrutura do Projeto

## 📁 Organização de Pastas

```
AssistentePessoal/
│
├── 📄 ARQUIVOS PRINCIPAIS (Aplicação)
│   ├── assistant.py           ← 🚀 EXECUTE ISTO (Streamlit app)
│   ├── model_handlers.py       ← Sistema de múltiplos modelos IA
│   ├── memorystore.py          ← Gerenciamento de memória persistente
│   ├── notifications.py        ← Alertas (Email, Telegram)
│   ├── alert_scheduler.py      ← Agendador de tarefas
│   └── memory.py               ← Utilitários auxiliares
│
├── 📂 tests/                   ← Testes e Debug
│   ├── test_*.py               ← Scripts de teste
│   ├── debug_*.py              ← Scripts de debug
│   └── test_streamlit_integration.py
│
├── 📂 setup/                   ← Configuração e Setup
│   ├── setup_windows_task.py   ← Agendar com Windows Task Scheduler
│   ├── setup_telegram.py       ← Configurar Telegram Bot
│   ├── recover_alerts.py       ← Recuperar alertas perdidos
│   └── *.ps1 / *.bat           ← Scripts PowerShell/Batch
│
├── 📂 docs/                    ← Documentação
│   ├── GUIA_COMPLETO.md        ← 📖 Guia principal
│   ├── GUIA_MULTIPLOS_MODELOS.md ← Como usar múltiplos modelos IA
│   ├── GUIA_MODELOS_HIBRIDO.md    ← Sistema hybrid (Local + Cloud)
│   ├── ALERTAS_GUIA.md            ← Como configurar alertas
│   ├── TESTE_SCHEDULER.md         ← Testes do agendador
│   ├── .env.template              ← Template de configuração
│   └── .env.example               ← Exemplo de .env
│
├── 📂 data/                    ← Dados Persistentes
│   └── memory.json             ← Base de dados de memória
│
├── 📂 .venv/                   ← Ambiente virtual Python
│
├── 📄 .env                     ← ⚙️ Configurações (IMPORTANTE!)
├── 📄 .gitignore               ← Arquivos ignorados pelo Git
└── 📄 README.md                ← Este arquivo

```

---

## 🚀 Como Usar

### 1️⃣ Iniciar o Assistente (STREAMLIT)
```powershell
cd c:\AssistentePessoal
.\.venv\Scripts\activate
streamlit run assistant.py
```

### 2️⃣ Configurar API Keys
Copie o template e configure:
```powershell
copy docs\.env.template .env
# Edite .env com suas chaves de API
```

### 3️⃣ Rodar Testes
```powershell
.\.venv\Scripts\activate
python tests\test_multi_models.py
python tests\test_openai_key.py
```

### 4️⃣ Configurar Alertas 24/7
```powershell
.\.venv\Scripts\activate
python setup\setup_windows_task.py
```

---

## 📋 Arquivos Principais

### `assistant.py` - 🎯 Aplicação Principal
- Interface Streamlit
- Seleção de modelos IA
- Gerenciamento de tarefas e notas
- Análise de PDFs e imagens

### `model_handlers.py` - 🧠 Motor de IA Multi-Provedor
- **Local:** Ollama (LLaVA)
- **OpenAI:** GPT-4o, GPT-4o-mini, GPT-4-Turbo, GPT-3.5-Turbo
- **Google:** Gemini (pronto, sem chave)
- **Anthropic:** Claude (pronto, sem chave)

### `memorystore.py` - 💾 Memória Persistente
- Salva notas com tags
- Armazena tarefas agendadas
- Histórico de interações
- Busca semântica

### `notifications.py` - 📬 Sistema de Alertas
- Email via Gmail
- Telegram
- SMS (preparado)

### `alert_scheduler.py` - ⏰ Agendador
- Verifica tarefas a cada 10 segundos
- Envia alertas na hora certa
- Previne duplicatas

---

## 🧪 Scripts de Teste

```powershell
# Verificar múltiplos modelos disponíveis
python tests\test_multi_models.py

# Testar geração com todos os provedores
python tests\test_generation_multi.py

# Verificar API OpenAI
python tests\test_openai_key.py

# Simular integração Streamlit
python tests\test_streamlit_integration.py

# Testar sistema completo
python tests\test_complete_system.py
```

---

## ⚙️ Configuração (.env)

```
# OpenAI (NECESSÁRIO para GPT)
OPENAI_API_KEY=sk-proj-...

# Telegram (NECESSÁRIO para alertas Telegram)
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Gmail (Opcional - para alertas por email)
GMAIL_USER=...
GMAIL_PASSWORD=...

# Google Gemini (Opcional)
GOOGLE_API_KEY=...

# Anthropic Claude (Opcional)
ANTHROPIC_API_KEY=...
```

---

## 📊 Estrutura de Dados

### memory.json
```json
{
  "user_profile": { "nome": "...", "preferências": "..." },
  "tasks": [
    {
      "task": "Descrição",
      "alert_time": "14:30",
      "done": false,
      "alert_type": "telegram"
    }
  ],
  "notes": [
    {
      "text": "Nota salva",
      "tags": ["importante", "python"],
      "question": "Como fazer X?",
      "answer": "Resposta completa...",
      "source": "assistente"
    }
  ]
}
```

---

## 🔗 Recursos Úteis

- **Documentação Completa:** `docs/GUIA_COMPLETO.md`
- **Múltiplos Modelos IA:** `docs/GUIA_MULTIPLOS_MODELOS.md`
- **Alertas:** `docs/ALERTAS_GUIA.md`
- **OpenAI Docs:** https://platform.openai.com/docs
- **Streamlit Docs:** https://docs.streamlit.io
- **Ollama:** https://ollama.ai

---

## 🐛 Troubleshooting

### Erro: "memory.json não encontrado"
- ✅ Execute: `mkdir data`
- ✅ Verificar se `memorystore.py` está atualizado

### Erro: "Modelo não aparece"
- ✅ Reinicie Streamlit
- ✅ Verifique API key no `.env`
- ✅ Rode: `python tests\test_multi_models.py`

### Ollama offline
```powershell
ollama serve  # Em outro PowerShell
```

---

## 📈 Próximos Passos

- [ ] Adicionar interface de busca de notas
- [ ] Melhorar análise de imagens
- [ ] Suporte a mais idiomas
- [ ] Dashboard de estatísticas
- [ ] Backup automático

---

**Versão:** 2.0 (Reorganizado)  
**Última atualização:** Nov 2025  
**Status:** ✅ Funcionando
