# 🚀 TESTANDO SCHEDULER - PASSO A PASSO

## ✅ Verificação Inicial

Primeiro, rode o debug para confirmar tudo está OK:

```powershell
cd c:\AssistentePessoal
python debug_scheduler.py
```

Deve aparecer:
- ✅ Tarefas encontradas
- ✅ Telegram configurado
- ✅ Teste de envio bem-sucedido

---

## 📋 Para Testar o Scheduler

### **Opção 1: Teste com Tarefa Imediata**

1. **Abra o Streamlit** (http://localhost:8501)
2. **Vá para aba "Tarefas"**
3. **Crie uma nova tarefa:**
   - Descrição: "Teste Scheduler - Alerta em 2 minutos"
   - Marque: ✅ Telegram
   - Hora: **[HORA ATUAL] + 2 MINUTOS**
   - Exemplo: Se são 14:32, coloque 14:34
4. **Clique "Adicionar Tarefa"**
5. **Em um NOVO terminal, rode:**
   ```powershell
   cd c:\AssistentePessoal
   python alert_scheduler.py
   ```
6. **Aguarde 2 minutos** - você verá no terminal:
   ```
   ├─ Tarefa: Teste Scheduler - Alerta em 2 minutos...
   │  Agendado: 14:34 | Atual: 14:34 | Tipo: telegram
   └─ ⏰ ENVIANDO ALERTA! (diferença: 0.0 min)
      ✅ Telegram enviado!
   ```
7. **Receba no Telegram!** 📱

---

### **Opção 2: Teste com Tarefa Atrasada**

Para testar se o scheduler **recupera alertas que deveriam ter sido enviados antes**:

1. **Crie uma tarefa com horário do PASSADO:**
   - Descrição: "Teste Alerta Atrasado"
   - Marque: ✅ Telegram
   - Hora: **[HORA ATUAL] - 2 MINUTOS**
   - Exemplo: Se são 14:32, coloque 14:30
2. **Clique "Adicionar Tarefa"**
3. **Em um novo terminal, rode:**
   ```powershell
   cd c:\AssistentePessoal
   python alert_scheduler.py
   ```
4. **Na próxima verificação (em 10 segundos), verá:**
   ```
   └─ ⏰ ENVIANDO ALERTA! (diferença: 2.0 min)
      ✅ Telegram enviado!
   ```
5. **O alerta será enviado mesmo estando atrasado!** 🎯

---

## 🔧 Troubleshooting

### **Problema: "Telegram não configurado"**
- Verifique `.env` tem `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`
- Execute: `python debug_scheduler.py`

### **Problema: "Tarefa criada mas nenhum alerta foi enviado"**
1. Rode `python debug_scheduler.py`
2. Veja se a tarefa aparece em "Tarefas encontradas"
3. Confirme o horário está correto (HH:MM)
4. Verifique se "Alerta ativo: True"
5. Verifique se "Concluída: False"

### **Problema: Terminal não mostra output**
- Adicione `-u` ao comando:
  ```powershell
  python -u alert_scheduler.py
  ```

---

## 📊 Interpretando o Output

```
[14:34:23] Verificando tarefas...
  ├─ Tarefa: Teste Scheduler...          ← Encontrou a tarefa
  │  Agendado: 14:34 | Atual: 14:34 | Tipo: telegram
  └─ ⏰ ENVIANDO ALERTA!                 ← Vai enviar
     ✅ Telegram enviado!                ← Enviou com sucesso
```

---

## 🎯 Ciclo de Vida

1. **Primeira execução:** Scheduler busca tarefas não enviadas (até 5 min atrasadas)
2. **Minuto 1-10:** Verifica a cada 10 segundos
3. **Próximo minuto + 5 minutos:** Envia alarmes agendados e atrasados
4. **Marca como enviado:** Não duplica mesmo que rode scheduler 2x
5. **Continua até:** Você pressionar Ctrl+C

---

## ✨ Dicas

✅ Deixe o scheduler rodando 24/7 em background
✅ Use horários no futuro para testes
✅ Verifique Telegram está recebendo
✅ Veja o output do terminal para debugar
✅ Se parou, reinicie: `python alert_scheduler.py`

---

**Tudo pronto para testar?** 🚀
