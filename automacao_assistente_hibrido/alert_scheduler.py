import time
import schedule
from datetime import datetime, timedelta
from memorystore import MemoryStore
from notifications import NotificationManager

memory_store = MemoryStore()
notifier = NotificationManager()

# Rastrear tarefas já enviadas para não duplicar
tarefas_enviadas = set()

def check_and_send_alerts():
    """Verifica tarefas e envia alertas no horário certo ou até 5 minutos atrasado"""
    global tarefas_enviadas
    
    tarefas = memory_store.get_tasks()
    agora = datetime.now()
    agora_formatada = agora.strftime('%H:%M')
    agora_segundos = agora.strftime('%H:%M:%S')
    
    print(f"\n[{agora_segundos}] Verificando tarefas...")
    
    for i, tarefa in enumerate(tarefas):
        if tarefa.get('alert_enabled') and not tarefa.get('done'):
            hora_agendada = tarefa.get('alert_time')
            descricao = tarefa.get('task', '')
            alert_type = tarefa.get('alert_type', 'email')
            
            # Criar ID único para a tarefa
            task_id = f"{i}_{descricao}_{hora_agendada}"
            
            print(f"  ├─ Tarefa: {descricao[:40]}...")
            print(f"  │  Agendado: {hora_agendada} | Atual: {agora_formatada} | Tipo: {alert_type}")
            
            # Verificar se é a hora EXATA ou até 5 minutos de atraso
            if hora_agendada and task_id not in tarefas_enviadas:
                try:
                    # Parse das horas
                    hora_parts = hora_agendada.split(':')
                    h_agendada = int(hora_parts[0])
                    m_agendada = int(hora_parts[1])
                    
                    agendado = datetime.now().replace(hour=h_agendada, minute=m_agendada, second=0)
                    diferenca = (agora - agendado).total_seconds() / 60
                    
                    # Se está entre -5 min (antes) até +10 min (depois)
                    if -5 <= diferenca <= 10:
                        print(f"  └─ ⏰ ENVIANDO ALERTA! (diferença: {diferenca:.1f} min)")
                        
                        if alert_type == 'telegram':
                            resultado = notifier.send_telegram_alert(descricao, 'ALERTA')
                            if resultado.get('success'):
                                print(f"     ✅ Telegram enviado!")
                                tarefas_enviadas.add(task_id)
                            else:
                                print(f"     ❌ Erro Telegram: {resultado.get('message')}")
                        elif alert_type == 'email':
                            resultado = notifier.send_email_alert(descricao, 'ALERTA')
                            if resultado.get('success'):
                                print(f"     ✅ Email enviado!")
                                tarefas_enviadas.add(task_id)
                            else:
                                print(f"     ❌ Erro Email: {resultado.get('message')}")
                except Exception as e:
                    print(f"     ❌ Erro ao processar: {str(e)}")

def start_scheduler():
    """Inicia o agendador de alertas"""
    print("\n" + "="*70)
    print("🤖 SCHEDULER DE ALERTAS INICIADO")
    print("="*70)
    print("Monitorando tarefas agendadas...")
    print("Faixa de tolerância: 5 minutos ANTES até 10 minutos DEPOIS")
    print("Verificação: A cada 10 segundos")
    print("Pressione Ctrl+C para parar\n")
    
    # Verificar a cada 10 segundos (mais frequente = menos chance de perder)
    schedule.every(10).seconds.do(check_and_send_alerts)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n❌ Scheduler parado pelo usuário")
        exit(0)

if __name__ == '__main__':
    start_scheduler()
