#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para recuperar alertas que foram perdidos
Envia AGORA qualquer alerta que deveria ter sido enviado
"""
from datetime import datetime, timedelta
from memorystore import MemoryStore
from notifications import NotificationManager

memory_store = MemoryStore()
notifier = NotificationManager()

print("\n" + "="*70)
print("RECUPERADOR DE ALERTAS PERDIDOS")
print("="*70)

tarefas = memory_store.get_tasks()
agora = datetime.now()
print(f"\nHora atual: {agora.strftime('%H:%M:%S')}")
print("Procurando alertas que deveriam ter sido enviados...\n")

alertas_recuperados = 0

for i, t in enumerate(tarefas):
    if t.get('alert_enabled') and not t.get('done'):
        descricao = t.get('task', '')
        hora_agendada = t.get('alert_time', '')
        alert_type = t.get('alert_type', '')
        
        if not hora_agendada:
            continue
        
        try:
            h, m = map(int, hora_agendada.split(':'))
            agendado = agora.replace(hour=h, minute=m, second=0)
            diferenca_minutos = (agora - agendado).total_seconds() / 60
            
            # Se passou da hora MAS ainda está dentro de 24 horas (mesmo dia)
            if 10 < diferenca_minutos <= 1440:  # 1440 = 24 horas
                print(f"⚠️  ALERTA PERDIDO encontrado:")
                print(f"   Tarefa: {descricao[:50]}...")
                print(f"   Deveria ter sido enviado em: {hora_agendada}")
                print(f"   Atraso: {diferenca_minutos:.0f} minutos")
                print(f"   Tipo: {alert_type}")
                
                # Enviar agora
                print(f"   └─ Enviando AGORA...")
                
                if alert_type == 'telegram':
                    resultado = notifier.send_telegram_alert(
                        f"[ALERTA RECUPERADO] {descricao}\n⏰ Deveria ter sido enviado às {hora_agendada}",
                        'ALERTA ATRASADO'
                    )
                elif alert_type == 'email':
                    resultado = notifier.send_email_alert(
                        f"[ALERTA RECUPERADO] {descricao}\nDeveria ter sido enviado às {hora_agendada}",
                        'ALERTA ATRASADO'
                    )
                
                if resultado.get('success'):
                    print(f"   ✅ Enviado com sucesso!\n")
                    alertas_recuperados += 1
                else:
                    print(f"   ❌ Erro: {resultado.get('message')}\n")
        
        except Exception as e:
            print(f"❌ Erro ao processar: {e}\n")

print("="*70)
if alertas_recuperados > 0:
    print(f"✅ {alertas_recuperados} alerta(s) recuperado(s) e enviado(s)!")
else:
    print("ℹ️  Nenhum alerta perdido encontrado")
print("="*70 + "\n")
