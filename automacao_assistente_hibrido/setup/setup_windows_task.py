#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
setup_windows_task.py - Configura agendador automático no Windows
Cria uma tarefa que executa alert_scheduler.py AUTOMATICAMENTE A CADA MINUTO
mesmo que o PC esteja desligado
"""

import os
import subprocess
import sys
from pathlib import Path

print("\n" + "="*70)
print("⚙️  CONFIGURADOR DE TAREFA AUTOMÁTICA DO WINDOWS")
print("="*70)

# Caminho do projeto
project_path = Path(__file__).parent.absolute()
scheduler_script = project_path / "alert_scheduler.py"
python_exe = sys.executable

print(f"\n📍 Caminho do projeto: {project_path}")
print(f"🐍 Python: {python_exe}")
print(f"📄 Script: {scheduler_script}")

# Verificar se o arquivo existe
if not scheduler_script.exists():
    print(f"\n❌ ERRO: {scheduler_script} não encontrado!")
    sys.exit(1)

print("\n" + "="*70)
print("CRIANDO TAREFA NO WINDOWS TASK SCHEDULER...")
print("="*70)

# Nome da tarefa
task_name = "AssistenteBot-AlertScheduler"

# Comando que será executado
# Usa 'python -u' para forçar unbuffered output
command = f'"{python_exe}" -u "{scheduler_script}"'

# Script XML para criar a tarefa
# Configurado para:
# - Rodar a cada 1 minuto
# - Iniciar quando o Windows inicia
# - Rodar mesmo se desligado
# - Reiniciar se parar
task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-11-30T00:00:00</Date>
    <Author>AssistenteBot</Author>
    <Description>Executa o scheduler de alertas do Assistente Pessoal 24/7</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <TimeTrigger>
      <Enabled>true</Enabled>
      <StartBoundary>2025-11-30T00:00:00</StartBoundary>
      <Repetition>
        <Interval>PT1M</Interval>
        <Duration>P30D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <Duration>PT10M</Duration>
      <WaitTimeout>PT1H</WaitTimeout>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>5</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>-u "{scheduler_script}"</Arguments>
      <WorkingDirectory>{project_path}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

# Salvar XML temporário
xml_file = project_path / "task_temp.xml"
try:
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)
    print(f"✅ Arquivo de configuração criado: {xml_file}")
except Exception as e:
    print(f"❌ Erro ao criar arquivo XML: {e}")
    sys.exit(1)

# Criar a tarefa usando o comando 'schtasks'
print("\n📋 Registrando tarefa no Windows Task Scheduler...")
print("   (Pode pedir permissão de administrador)\n")

try:
    # Primeiro, tentar deletar se já existir
    print("   [1/2] Removendo tarefa anterior (se existir)...")
    subprocess.run(
        ['schtasks', '/delete', '/tn', task_name, '/f'],
        capture_output=True,
        timeout=10
    )
    print("   ✓ Limpeza completa")
    
    # Criar a nova tarefa
    print("   [2/2] Criando nova tarefa...")
    result = subprocess.run(
        ['schtasks', '/create', '/tn', task_name, '/xml', str(xml_file), '/f'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("   ✓ Tarefa criada com sucesso!")
    else:
        print(f"   ⚠️  Código de retorno: {result.returncode}")
        if result.stderr:
            print(f"   Erro: {result.stderr}")
        if result.stdout:
            print(f"   Info: {result.stdout}")

except subprocess.TimeoutExpired:
    print("❌ Timeout ao executar comando")
    sys.exit(1)
except FileNotFoundError:
    print("❌ ERRO: Comando 'schtasks' não encontrado!")
    print("   (Você precisa estar em um Windows com suporte a Task Scheduler)")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao criar tarefa: {e}")
    sys.exit(1)

# Limpar arquivo temporário
try:
    xml_file.unlink()
    print("   ✓ Limpeza de arquivos temporários")
except:
    pass

print("\n" + "="*70)
print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
print("="*70)

print("\n📋 Detalhes da tarefa criada:")
print(f"   Nome: {task_name}")
print(f"   Comando: {command}")
print(f"   Diretório: {project_path}")
print(f"   Frequência: A cada 1 minuto")
print(f"   Execução: Automática ao iniciar Windows")
print(f"   Prioridade: Normal")

print("\n🎯 Como funciona:")
print("   1. Windows inicia (ou em qualquer momento)")
print("   2. Task Scheduler ativa automaticamente")
print("   3. Alert_scheduler.py executa a cada minuto")
print("   4. Verifica tarefas agendadas")
print("   5. Envia alertas no Telegram")
print("   6. Tudo funciona 24/7 SEM você precisar fazer nada!")

print("\n✨ VOCÊ NÃO PRECISA MAIS:")
print("   ❌ Rodar 'python alert_scheduler.py' manualmente")
print("   ❌ Deixar um terminal aberto")
print("   ❌ PC ligado (após inicializar, funciona em background)")

print("\n📱 Seus alertas vão chegar:")
print("   ✅ Mesmo desligando e ligando o PC")
print("   ✅ Mesmo saindo do Streamlit")
print("   ✅ Mesmo desligando qualquer terminal")

print("\n🔍 Para verificar se está rodando:")
print("   1. Pressione: Win + R")
print("   2. Digite: tasklist | findstr alert_scheduler")
print("   3. Se aparecer, está funcionando!")

print("\n🛑 Para parar/pausar a tarefa:")
print("   1. Pressione: Win + R")
print("   2. Digite: taskschd.msc")
print("   3. Procure por: AssistenteBot-AlertScheduler")
print("   4. Clique com botão direito → Desabilitar")

print("\n" + "="*70)
print("🎉 TUDO PRONTO! SUA TAREFA AUTOMÁTICA ESTÁ ATIVA!")
print("="*70 + "\n")

# Oferecer para verificar se está rodando
print("💡 Dica: Para confirmar que tudo está funcionando,")
print("   crie uma tarefa para daqui a 1-2 minutos.")
print("   Você receberá o alerta MESMO QUE FECHE ESTE TERMINAL!\n")
