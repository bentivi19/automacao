# 🤖 Assistente Pessoal - Guia Completo

## 📋 Funcionalidades

### 1️⃣ **Chat Inteligente com Contexto**
- Faz perguntas ao modelo Ollama/LLava
- **Busca automaticamente em notas salvas** antes de responder
- Nunca alucina sobre arquivos deletados (usa contexto)
- Suporta:
  - 💬 Perguntas de texto
  - 📄 Análise de PDFs (extrai texto automaticamente)
  - 🖼️ Análise de Imagens

### 2️⃣ **Sistema de Notas com Q&A**
**Salvar Notas:**
- Faça uma pergunta → Receba resposta → Vá para aba "Notas"
- Adicione tags (ex: "python, código, dica")
- Defina a fonte (padrão: "assistente")
- Clique "Salvar Nota"

**Visualizar Notas:**
- Todas as notas aparecem em abas expansíveis
- Clique em uma nota para ver: Pergunta, Resposta, Tags, Fonte
- Use 🗑️ para deletar notas individuais

**Buscar Notas:**
- Vá para aba "Config" → "Buscar Notas"
- Digite palavras-chave
- Veja todas as notas relacionadas

### 3️⃣ **PDFs e Imagens com Contexto Inteligente**
Quando você envia um PDF ou Imagem:
1. O modelo analisa o arquivo e responde
2. **VOCÊ DECIDE se quer salvar como nota** (botões: "💾 Salvar" ou "❌ Não salvar")
3. Se salvar, define as tags personalizadas
4. Mesmo que delete o arquivo depois:
   - O modelo LEMBRA do conteúdo (via notas)
   - Pode responder perguntas sobre ele
   - Não inventa respostas

**Fluxo:**
```
1. Upload PDF "relatorio_vendas_2024.pdf"
2. Pergunta: "Qual foi o crescimento em %?"
3. Modelo responde corretamente
4. Sistema oferece: "💾 Salvar como Nota?" com tags
5. Você salva a nota
6. Você deleta o PDF
7. Pergunta novamente: "Qual foi o crescimento em %?"
8. Modelo responde corretamente (via nota salva, sem alucinar)
```

**Vantagens:**
✅ Controle total sobre o quê salvar
✅ Evita encher storage com notas desnecessárias
✅ Tags personalizadas para cada conteúdo
✅ Modelo nunca alucina sobre arquivos deletados

### 4️⃣ **Gerenciamento de Tarefas com Alertas**
**Criar Tarefa:**
- Digite a descrição (ex: "Tomar remédio")
- Escolha se quer alerta por Email ou Telegram
- Defina a hora (HH:MM)
- Clique "Adicionar Tarefa"

**Visualizar Tarefas:**
- **Tarefas Pendentes**: mostra hora do alerta
- **Clique OK** para marcar como concluída
- **Concluídas**: lista tarefas finalizadas
- **Botão "Limpar Concluídas"**: deleta finalizadas

### 5️⃣ **Alertas Automáticos**

#### **Opção 1: Email (Gmail)**
Configure no `.env`:
```
GMAIL_USER=seu_email@gmail.com
GMAIL_PASSWORD=sua_senha_de_app_google
ALERT_EMAIL=seu_email@gmail.com
```

#### **Opção 2: Telegram (Recomendado!)**
Configure no `.env`:
```
TELEGRAM_BOT_TOKEN=8312137837:AAFTM_8L...
TELEGRAM_CHAT_ID=1098844555
```

**Como configurar Telegram:**
1. Abra Telegram → busque @BotFather
2. Envie `/newbot`
3. Siga as instruções e copie o TOKEN
4. Coloque no `.env` como `TELEGRAM_BOT_TOKEN=seu_token`
5. Inicie seu bot com `/start`
6. Visite: `https://api.telegram.org/bot[TOKEN]/getUpdates`
7. Copie seu `chat_id` e coloque no `.env`
8. Pronto!

**Teste antes de usar:**
- Vá para Config → "Teste Telegram"
- Se receber mensagem = funcionando ✅

#### **Opção 3: Scheduler Automático**
Em um terminal separado, rode:
```powershell
cd c:\AssistentePessoal
python alert_scheduler.py
```

Isso vai:
- Rodar 24/7 em background
- Verificar tarefas a cada minuto
- Enviar alerta no horário exato
- Pode manter aberto sempre

**Usar com Streamlit:**
```powershell
# Terminal 1
streamlit run assistant.py

# Terminal 2 (separado)
python alert_scheduler.py
```

---

## 🎯 Fluxo de Uso Recomendado

### **Para Pesquisa/Estudo:**
1. Upload PDF/Imagem
2. Faça perguntas sobre o conteúdo
3. **Modelo responde normalmente**
4. **Você ESCOLHE se quer salvar como nota** (com tags personalizadas)
5. Delete o arquivo (você tem as notas salvas!)
6. Faça novas perguntas depois - o modelo lembra das notas

### **Para Lembretes Diários:**
1. Crie tarefas com horários
2. Configure alerta Telegram
3. Rode o scheduler: `python alert_scheduler.py`
4. Receba notificações na hora exata

### **Para Memória Pessoal:**
1. Converse com o modelo
2. Salve as melhores dicas/respostas
3. Use a busca para encontrar informações antigas
4. Construa sua base de conhecimento

---

## 🔧 Arquivos Importantes

- `assistant.py` - Interface Streamlit
- `memorystore.py` - Sistema de armazenamento de notas/tarefas
- `notifications.py` - Gerenciador de alertas
- `alert_scheduler.py` - Scheduler automático
- `.env` - Credenciais (Email, Telegram)
- `memory.json` - Banco de dados local (notas e tarefas)

---

## 📱 Requisitos

- Python 3.11+
- Ollama rodando (`http://localhost:11434`)
- Streamlit
- Telegram Bot Token (se usar Telegram)
- Gmail App Password (se usar Email)

---

## 🚀 Iniciar

### **Opção 1: Apenas Streamlit**
```powershell
cd c:\AssistentePessoal
streamlit run assistant.py
```

### **Opção 2: Streamlit + Alertas Automáticos (Recomendado)**
```powershell
# Terminal 1
cd c:\AssistentePessoal
streamlit run assistant.py

# Terminal 2 (abra outro)
cd c:\AssistentePessoal
python alert_scheduler.py
```

---

## 💡 Dicas

✅ Sempre salve notas de PDFs/Imagens importantes antes de deletar
✅ Use tags relevantes para achar notas depois
✅ Configure Telegram - é mais rápido que email
✅ Rode o scheduler se quer alertas automáticos
✅ Busque notas regularmente para usar como contexto

---

**Desenvolvido com ❤️ para você!**
