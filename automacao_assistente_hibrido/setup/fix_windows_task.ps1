# Script PowerShell para CORRIGIR a tarefa do Windows Task Scheduler
# com o caminho correto do Python

Write-Host ""
Write-Host "======================================================================"
Write-Host "CORRIGIR TAREFA DO WINDOWS TASK SCHEDULER"
Write-Host "======================================================================"
Write-Host ""

# Verificar admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERRO: Precisa rodar como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clique direito no arquivo -> Executar com PowerShell -> SIM"
    Write-Host ""
    pause
    exit 1
}

Write-Host "OK - Rodando como Admin" -ForegroundColor Green
Write-Host ""

# Encontrar Python
Write-Host "Procurando Python..."
$pythonPath = (python -c "import sys; print(sys.executable)" 2>$null).Trim()

if (-not $pythonPath -or -not (Test-Path $pythonPath)) {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python encontrado: $pythonPath" -ForegroundColor Green
Write-Host ""

$taskName = "AssistenteBot-AlertScheduler"
$scriptPath = "C:\AssistentePessoal\alert_scheduler.py"
$taskDir = "C:\AssistentePessoal"

Write-Host "[1/2] Deletando tarefa antiga..."
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue 2>$null
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[2/2] Criando nova tarefa com caminho CORRETO..."

try {
    # Acao: executar Python com o script
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "-u `"$scriptPath`"" -WorkingDirectory $taskDir
    
    # Trigger: a cada 1 minuto, começando agora
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 1000)
    
    # Configuracoes
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
    
    # Registrar tarefa
    Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description "Alert Scheduler para Assistente Pessoal" -Settings $settings -RunLevel Highest -Force -ErrorAction Stop | Out-Null
    
    Write-Host "OK - Tarefa criada!" -ForegroundColor Green
    Write-Host ""
    
    # Verificar
    $task = Get-ScheduledTask -TaskName $taskName
    Write-Host "Status: $($task.State)" -ForegroundColor Green
    
    # Forcar execucao imediata
    Write-Host ""
    Write-Host "Forcando primeira execucao..."
    Start-ScheduledTask -TaskName $taskName
    
    Write-Host ""
    Write-Host "======================================================================"
    Write-Host "SUCESSO!" -ForegroundColor Green
    Write-Host "======================================================================"
    Write-Host ""
    Write-Host "Sua tarefa agora:"
    Write-Host "  - Executa AUTOMATICAMENTE a cada 1 minuto"
    Write-Host "  - Rodara com Python CORRETO"
    Write-Host "  - Inicia quando Windows inicia"
    Write-Host "  - Aguarde 30 segundos e verifique o Telegram"
    Write-Host ""
    
}
catch {
    Write-Host "ERRO: $_" -ForegroundColor Red
    pause
    exit 1
}

pause
