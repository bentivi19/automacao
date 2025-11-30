#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE COMPLETO E FINAL
Verifica tudo: Telegram, Scheduler, Windows Task
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

print("\n" + "="*80)
print("🔍 TESTE COMPLETO DO SISTEMA DE ALERTAS")
print("="*80 + "\n")

# Load .env
load_dotenv()

# 1. VALIDAR TELEGRAM
print("[1/4] Validando Telegram...")
print("-" * 80)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERRO: Telegram não configurado!")
    print(f"   TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
    print(f"   TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    sys.exit(1)

print(f"✓ Bot Token: {TELEGRAM_BOT_TOKEN[:30]}...")
print(f"✓ Chat ID: {TELEGRAM_CHAT_ID}")

# Teste direto
import requests
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "🧪 TESTE 1: Telegram funcionando!"
}

try:
    response = requests.post(url, json=payload, timeout=5)
    result = response.json()
    if result.get('ok'):
        print("✅ Telegram: OK\n")
    else:
        print(f"❌ Telegram: Erro na API - {result}\n")
        sys.exit(1)
except Exception as e:
    print(f"❌ Telegram: Erro - {str(e)}\n")
    sys.exit(1)

# 2. VALIDAR MEMORY.JSON
print("[2/4] Validando memory.json...")
print("-" * 80)

try:
    from memorystore import MemoryStore
    memory = MemoryStore()
    tasks = memory.get_tasks()
    
    print(f"✓ Memory carregado")
    print(f"✓ Total de tarefas: {len(tasks)}")
    
    for i, t in enumerate(tasks):
        print(f"   [{i}] {t.get('task')[:40]:40} | {t.get('alert_time')} | {t.get('alert_type')}")
    
    print()
except Exception as e:
    print(f"❌ Erro ao carregar memory: {str(e)}\n")
    sys.exit(1)

# 3. CRIAR TAREFA IMEDIATA
print("[3/4] Criando tarefa para AGORA...")
print("-" * 80)

now = datetime.now()
alert_time = now.strftime('%H:%M')

print(f"✓ Horário atual: {now.strftime('%H:%M:%S')}")
print(f"✓ Criando tarefa para: {alert_time}")

# Remover tarefas antigas
tasks = memory.get_tasks()
memory.data['tasks'] = [t for t in tasks if t.get('alert_time') not in ['11:30', '11:35', '07:05', '11:10', '11:40']]

# Adicionar nova
memory.data['tasks'].append({
    "task": f"🧪 TESTE IMEDIATO - {now.strftime('%H:%M:%S')}",
    "done": False,
    "created_at": now.isoformat(),
    "alert_enabled": True,
    "alert_time": alert_time,
    "alert_type": "telegram"
})

# Salvar usando o método correto
import json
with open('memory.json', 'w', encoding='utf-8') as f:
    json.dump(memory.data, f, indent=2, ensure_ascii=False)
    
print("✅ Tarefa criada\n")

# 4. RODAR SCHEDULER POR 30 SEGUNDOS
print("[4/4] Rodando scheduler por 30 segundos...")
print("-" * 80)

try:
    from alert_scheduler import check_and_send_alerts
    
    for i in range(3):
        print(f"\n▶ Verificação {i+1}...")
        check_and_send_alerts()
        time.sleep(10)
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80)
    print("\n📱 VOCÊ DEVERIA TER RECEBIDO 2 MENSAGENS NO TELEGRAM:")
    print("   1️⃣  'Telegram funcionando!'")
    print("   2️⃣  'TESTE IMEDIATO' com timestamp")
    print("\nSe recebeu AMBAS = Sistema 100% OK! 🎉")
    print("Se recebeu apenas a 1ª = Scheduler com problema")
    print("Se NÃO recebeu = Telegram com problema\n")

except Exception as e:
    print(f"❌ Erro ao rodar scheduler: {str(e)}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)
