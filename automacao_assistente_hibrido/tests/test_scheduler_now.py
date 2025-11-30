#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simulado do scheduler - mostra exatamente o que vai acontecer
"""
from datetime import datetime, timedelta
from memorystore import MemoryStore
from notifications import NotificationManager

memory_store = MemoryStore()
notifier = NotificationManager()

print("\n" + "="*70)
print("SIMULACAO - TESTE DO SCHEDULER")
print("="*70)

tarefas = memory_store.get_tasks()
agora = datetime.now()

print(f"\nHora atual: {agora.strftime('%H:%M:%S')}")
print("\nAnalisando cada tarefa:")
print("-"*70)

for i, t in enumerate(tarefas):
    if t.get('alert_enabled') and not t.get('done'):
        descricao = t.get('task', '')
        hora_agendada = t.get('alert_time', '')
        alert_type = t.get('alert_type', '')
        
        if not hora_agendada:
            print(f"\n❌ Tarefa {i+1}: {descricao[:40]}...")
            print(f"   └─ ERRO: Sem horário definido!")
            continue
        
        print(f"\n✓ Tarefa {i+1}: {descricao[:40]}...")
        print(f"  ├─ Agendada: {hora_agendada}")
        print(f"  ├─ Tipo: {alert_type}")
        
        try:
            # Converter hora agendada
            h, m = map(int, hora_agendada.split(':'))
            agendado = agora.replace(hour=h, minute=m, second=0)
            
            # Calcular diferença
            diferenca_minutos = (agora - agendado).total_seconds() / 60
            diferenca_segundos = (agora - agendado).total_seconds() % 60
            
            print(f"  └─ Diferença: {diferenca_minutos:.1f} min ({diferenca_segundos:.0f} seg)")
            
            # Verificar se deve enviar
            if -1 <= diferenca_minutos <= 5:  # Entre 1 min antes até 5 min depois
                print(f"\n  ⚠️  SERIA ENVIADO AGORA!")
                print(f"     └─ Testando envio...")
                
                if alert_type == 'telegram':
                    resultado = notifier.send_telegram_alert(f"[TESTE] {descricao}", 'TESTE')
                    if resultado.get('success'):
                        print(f"     └─ ✅ Telegram enviado com sucesso!")
                    else:
                        print(f"     └─ ❌ Erro: {resultado.get('message')}")
            else:
                if diferenca_minutos > 5:
                    print(f"  └─ ❌ JÁ PASSOU! (há {diferenca_minutos:.1f} min)")
                else:
                    tempo_falta = -diferenca_minutos
                    print(f"  └─ ⏳ Falta {tempo_falta:.1f} min")
        
        except Exception as e:
            print(f"  └─ ❌ Erro ao processar: {e}")

print("\n" + "="*70)
print("PARA ENVIAR AGORA:")
print("="*70)
print("\n1. Crie uma nova tarefa com horário de AGORA + 1 MINUTO")
print("2. Execute: python alert_scheduler.py")
print("3. Aguarde o horário chegar")
print("4. Verá a mensagem no terminal")
print("5. Receberá no Telegram")
print("\n" + "="*70 + "\n")
