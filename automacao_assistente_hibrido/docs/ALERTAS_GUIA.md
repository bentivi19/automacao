# GUIA DE CONFIGURAÇÃO - ALERTAS POR EMAIL E WHATSAPP

## ⚡ Configuração Rápida

### 📱 Resumo Visual
```
┌─────────────────────────────────────┐
│  ASSISTENTE PESSOAL - ALERTAS       │
├─────────────────────────────────────┤
│ 📧 Email      → Gmail (Gratuito)    │
│ 💬 WhatsApp   → Twilio (Gratuito)   │
│ 🔔 Tarefas    → Salve com alertas   │
└─────────────────────────────────────┘
```

**Tempo de configuração:** ~10 minutos

### Arquivo .env
Crie um arquivo `.env` em `C:\AssistentePessoal` com:

```
# Gmail (opcional)
GMAIL_USER=seu_email@gmail.com
GMAIL_PASSWORD=sua_senha_de_app_google
ALERT_EMAIL=seu_email@gmail.com

# Twilio WhatsApp (opcional)
TWILIO_ACCOUNT_SID=seu_account_sid
TWILIO_AUTH_TOKEN=seu_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+1400000000
TWILIO_WHATSAPP_TO=whatsapp:+5511983418704
```

---

## 📧 ALERTAS POR EMAIL (Gmail)

### Como Configurar:

1. **Acesse:** https://myaccount.google.com/apppasswords
2. **Selecione:** 
   - App: "Mail"
   - Device: "Windows Computer"
3. **Copie** a senha gerada (16 caracteres)
4. **Cole** no arquivo `.env` como `GMAIL_PASSWORD`
5. **Recarregue** a página
6. **Teste** clicando em "📧 Enviar Email de Teste" nas Configurações

### Usar Alertas por Email:
- Ao criar tarefa: marque "📧 Email"
- Selecione a hora
- Clique no botão 📧 para enviar agora ou aguarde a hora

---

## 💬 ALERTAS POR WHATSAPP (Twilio)

### Como Configurar:

#### Passo 1: Criar Conta Twilio
1. Acesse: https://www.twilio.com/try-twilio
2. Crie uma conta gratuita
3. Confirme seu email e número de telefone

#### Passo 2: Obter Credenciais
1. Vá para Console: https://console.twilio.com/
2. No menu lateral esquerdo, procure por **"Account"** ou clique no seu perfil (canto superior direito)
3. Você verá a página com **Account SID** e **Auth Token**
4. **Account SID**: Copie o valor exibido (tipo: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
5. **Auth Token**: Clique em "Show" para revelar, depois copie (tipo: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
6. Cole no arquivo `.env`:
   - `TWILIO_ACCOUNT_SID=YOUR_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN=YOUR_AUTH_TOKEN`

**Dica:** Se não encontrar, procure por "Settings" ou "Account Settings" no menu da esquerda.

#### Passo 3: Configurar WhatsApp Sandbox
1. No menu lateral, vá para: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. **IMPORTANTE:** Se você vir "Connect to sandbox", faça o seguinte:
   - Você receberá um número Twilio como **+1 415 523 8886**
   - NO SEU WHATSAPP PESSOAL, envie uma mensagem para esse número com o código (ex: "join wrong-today")
   - Aguarde a confirmação no console
3. Quando a sandbox estiver ativa, você verá:
   - **From:** whatsapp:+14155238886 (número Twilio)
   - **To:** whatsapp:+5511983418704 (seu número)
4. Pronto! Você já pode usar.

#### Passo 4: Configurar seu Número no .env
Na página que você está (Send a business-initiated message), você pode ver:
- **To:** whatsapp:+5511983418704 (seu número - PERFEITO!)
- **From:** whatsapp:+14155238886 (número Twilio - PERFEITO!)

Cole exatamente no arquivo `.env`:
```
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+5511983418704
```

**Importante:** Use os MESMOS números que aparecem na tela do Twilio!

#### Passo 5: Testar
1. Salve o arquivo `.env`
2. Recarregue a página do Streamlit (F5)
3. Vá para a aba "Configurações"
4. Clique em "💬 Enviar WhatsApp de Teste"
5. Verifique se recebeu a mensagem no seu WhatsApp (+55 11 98341-8704)

---

## 🎯 Como Usar

### Ao Criar uma Tarefa:
```
Tarefa: "Tomar remédio pela manhã"
Tipo de Alerta: ✅ Email  ✅ WhatsApp
Hora: 08:00
```

### Resultado:
- Receberá mensagem no WhatsApp às 08:00
- Também receberá email
- Poderá enviar manualmente clicando nos botões 📧 💬

### Visualização de Tarefas:
- 📧 = Alerta por Email
- 💬 = Alerta por WhatsApp
- 📧💬 = Ambos
- (08:00) = Hora do alerta

---

## ⚠️ Troubleshooting

### Email não chega:
1. Verifique pasta de SPAM
2. Regenere a Senha de Aplicativo Google
3. Verifique o arquivo `.env`
4. Clique em "📧 Enviar Email de Teste" para ver mensagem de erro

### WhatsApp não chega:
1. Verifique se confirmou a sandbox do Twilio
2. Seu número está adicionado nos Recipients?
3. Créditos Twilio disponíveis? (uso é gratuito mas limitado)
4. Clique em "� Enviar WhatsApp de Teste" para diagnosticar

### Arquivo .env não é lido:
1. Salve o arquivo sem extensão .txt (use editor de código)
2. Verifique que está na pasta `C:\AssistentePessoal`
3. Recarregue a página Streamlit

---

## 💡 Dicas

✅ Twilio gratuito com limite de mensagens/mês
✅ Gmail gratuito e ilimitado
✅ Use ambos para máxima flexibilidade
✅ Testes de email/WhatsApp nas Configurações
✅ Lembretes persistem entre sessões
