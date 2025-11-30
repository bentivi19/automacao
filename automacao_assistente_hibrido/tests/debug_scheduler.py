#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de DEBUG para verificar tarefas e alertas
"""
import json
from datetime import datetime
from memorystore import MemoryStore
from notifications import NotificationManager

print("\n" + "="*70)
print("DEBUG - VERIFICADOR DE TAREFAS E ALERTAS")
print("="*70)

memory_store = MemoryStore()
notifier = NotificationManager()

# 1. Verificar arquivo memory.json
print("\n[1] Verificando memory.json...")
try:
    with open('memory.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Arquivo encontrado")
    print(f"   Total de tarefas: {len(data.get('tasks', []))}")
except Exception as e:
    print(f"❌ Erro ao ler memory.json: {e}")
    exit(1)

# 2. Listar todas as tarefas
print("\n[2] Tarefas encontradas:")
tarefas = memory_store.get_tasks()
if not tarefas:
    print("❌ Nenhuma tarefa encontrada!")
else:
    for i, t in enumerate(tarefas):
        print(f"\n   Tarefa {i+1}:")
        print(f"   └─ Descrição: {t.get('task', 'N/A')}")
        print(f"   └─ Concluída: {t.get('done', False)}")
        print(f"   └─ Alerta ativo: {t.get('alert_enabled', False)}")
        print(f"   └─ Tipo alerta: {t.get('alert_type', 'nenhum')}")
        print(f"   └─ Horário: {t.get('alert_time', 'não definido')}")

# 3. Verificar credenciais Telegram
print("\n[3] Verificando configuração Telegram:")
print(f"   Token: {notifier.telegram_bot_token[:30] if notifier.telegram_bot_token else 'NÃO CONFIGURADO'}...")
print(f"   Chat ID: {notifier.telegram_chat_id if notifier.telegram_chat_id else 'NÃO CONFIGURADO'}")

if not notifier.telegram_bot_token or not notifier.telegram_chat_id:
    print("❌ Telegram não configurado no .env!")
    print("   Configure: TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
else:
    print("✅ Telegram configurado")

# 4. Testar envio Telegram
print("\n[4] Testando envio Telegram:")
resultado = notifier.send_telegram_alert("Teste de DEBUG do Scheduler", "TESTE")
if resultado.get('success'):
    print(f"✅ {resultado.get('message')}")
else:
    print(f"❌ {resultado.get('message')}")

# 5. Simular próximo alerta
print("\n[5] Simulando próximos alertas:")
agora = datetime.now()
print(f"   Hora atual: {agora.strftime('%H:%M:%S')}")

proximos = []
for i, t in enumerate(tarefas):
    if t.get('alert_enabled') and not t.get('done'):
        hora_agendada = t.get('alert_time', '')
        if hora_agendada:
            proximos.append({
                'tarefa': t.get('task', ''),
                'hora': hora_agendada,
                'tipo': t.get('alert_type', '')
            })

if proximos:
    print("\n   Próximos alertas agendados:")
    for p in proximos:
        print(f"   ├─ {p['hora']} - {p['tarefa'][:40]}... ({p['tipo']})")
else:
    print("   ❌ Nenhum alerta agendado!")

print("\n" + "="*70)
print("RESUMO:")
print("="*70)
print(f"✅ Tarefas totais: {len(tarefas)}")
print(f"✅ Tarefas com alerta: {len([t for t in tarefas if t.get('alert_enabled')])}")
print(f"✅ Tarefas pendentes: {len([t for t in tarefas if not t.get('done')])}")
print(f"✅ Telegram configurado: {'SIM' if notifier.telegram_bot_token else 'NÃO'}")
print("\nPara rodar o scheduler, execute:")
print("   python alert_scheduler.py")
print("="*70 + "\n")
