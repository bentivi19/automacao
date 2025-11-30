#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para limpar tarefas antigas e criar teste novo
"""

import json
from datetime import datetime, timedelta
from memorystore import MemoryStore

# Carregar memory
memory = MemoryStore()

print("\n" + "="*70)
print("LIMPEZA DE TAREFAS E TESTE NOVO")
print("="*70 + "\n")

# Obter tarefas
tasks = memory.get_tasks()

# Filtrar apenas tarefas NÃO realizadas
active_tasks = [t for t in tasks if not t.get('done')]

print(f"Total de tarefas: {len(active_tasks)}")

# Remover tarefas antigas
new_tasks = []
for t in active_tasks:
    alert_time = t.get('alert_time', '')
    if alert_time in ['07:05', '11:10', '11:30']:
        print(f"❌ Deletando: {t.get('task')[:40]}... (horário: {alert_time})")
    else:
        new_tasks.append(t)
        print(f"✓ Mantendo: {t.get('task')[:40]}...")

# Adicionar nova tarefa de teste
now = datetime.now()
future_time = now + timedelta(minutes=2)  # 2 minutos no futuro
time_str = future_time.strftime('%H:%M')

print(f"\n📝 Criando nova tarefa de teste...")
print(f"   Horário atual: {now.strftime('%H:%M:%S')}")
print(f"   Horário da tarefa: {time_str}")
print(f"   (Será enviada em ~2 minutos)\n")

new_tasks.append({
    "task": "🧪 TESTE AGORA - Verificar Telegram",
    "done": False,
    "created_at": now.isoformat(),
    "alert_enabled": True,
    "alert_time": time_str,
    "alert_type": "telegram"
})

# Salvar
memory.data['tasks'] = new_tasks
memory.save()

print("✅ Feito! Agora:")
print(f"   1. Execute: python alert_scheduler.py")
print(f"   2. Aguarde {future_time.strftime('%H:%M')} (aproximadamente 2 minutos)")
print(f"   3. Você receberá um alerta no Telegram")
print(f"\nSe receber = Tudo OK!")
print(f"Se NÃO receber = Problema no Telegram\n")
