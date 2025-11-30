#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples: Criar tarefa com Python e verificar se scheduler envia
"""

from datetime import datetime, timedelta
from memorystore import MemoryStore
import time

print("\n" + "="*80)
print("TESTE: Criar tarefa com Python e scheduler enviar")
print("="*80 + "\n")

now = datetime.now()
future = now + timedelta(minutes=2)  # 2 minutos no futuro
time_str = future.strftime('%H:%M')

print(f"Horário agora: {now.strftime('%H:%M:%S')}")
print(f"Criando tarefa para: {time_str}")
print()

# Carregar memory
memory = MemoryStore()

# Adicionar nova tarefa
resultado = memory.add_task(
    '🧪 TESTE PYTHON - Verificar Telegram', 
    alert_enabled=True, 
    alert_time=time_str, 
    alert_type='telegram'
)

if resultado:
    print("✅ Tarefa adicionada com sucesso")
else:
    print("❌ Erro ao adicionar tarefa")

# Mostrar todas as tarefas
tasks = memory.get_tasks()
print(f"\nTotal de tarefas salvas: {len(tasks)}\n")
print("Tarefas:")

for i, t in enumerate(tasks):
    desc = t.get('task', '')[:40]
    hora = t.get('alert_time', '--:--')
    ativa = t.get('alert_enabled', False)
    tipo = t.get('alert_type', 'nenhum')
    print(f"  [{i}] {desc:40} | {hora} | Ativa: {ativa} | {tipo}")

print("\n" + "="*80)
print("Agora vamos rodar o scheduler por 2 minutos...")
print("Você deve receber um alerta no Telegram!")
print("="*80 + "\n")

# Rodar scheduler
try:
    from alert_scheduler import check_and_send_alerts
    import schedule
    
    for i in range(12):  # 12 × 10 segundos = 120 segundos = 2 minutos
        print(f"\n[Verificação {i+1}/12]")
        check_and_send_alerts()
        time.sleep(10)
    
    print("\n" + "="*80)
    print("✅ Teste finalizado!")
    print("Se você recebeu o alerta = Sistema OK!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()
