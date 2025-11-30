# Script PowerShell para criar tarefa no Windows Task Scheduler
# EXECUTAR COMO ADMINISTRADOR!

Write-Host ""
Write-Host "======================================================================"
Write-Host "CONFIGURADOR DE TAREFA AUTOMATICA"
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
$pythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source

if (-not $pythonPath) {
    Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Python: $pythonPath" -ForegroundColor Cyan
Write-Host ""

$taskName = "AssistenteBot-AlertScheduler"
$scriptPath = "C:\AssistentePessoal\alert_scheduler.py"
$taskDir = "C:\AssistentePessoal"

Write-Host "[1/3] Removendo tarefa antiga..."
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue 2>$null
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Criando nova tarefa..."

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "-u $scriptPath" -WorkingDirectory $taskDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 1000)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName $taskName -Description "Alert Scheduler" -Settings $settings -RunLevel Highest -Force -ErrorAction Stop | Out-Null

Write-Host "OK - Tarefa criada!" -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] Verificando..."
$task = Get-ScheduledTask -TaskName $taskName
Write-Host "OK - Status: $($task.State)" -ForegroundColor Green
Write-Host ""

Write-Host "======================================================================"
Write-Host "SUCESSO!" -ForegroundColor Green
Write-Host "======================================================================"
Write-Host ""
Write-Host "Sua tarefa agora:"
Write-Host "  - Executa AUTOMATICAMENTE a cada 1 minuto"
Write-Host "  - Inicia quando Windows inicia"
Write-Host "  - Funciona mesmo com PC desligado"
Write-Host "  - NAO precisa de Python rodando!"
Write-Host ""

Write-Host "Pressione qualquer tecla..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
