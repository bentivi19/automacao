@echo off
REM Script para criar tarefa automática no Windows Task Scheduler
REM Execute como ADMINISTRADOR!

setlocal enabledelayedexpansion

echo.
echo ======================================================================
echo CONFIGURADOR DE TAREFA AUTOMATICA DO WINDOWS
echo ======================================================================
echo.

cd /d C:\AssistentePessoal

REM Encontrar o caminho completo do Python
for /f "delims=" %%i in ('where python.exe') do set PYTHON_PATH=%%i

if "%PYTHON_PATH%"=="" (
    echo ERRO: Python nao encontrado no PATH!
    echo Certifique-se que Python esta instalado e acessivel.
    pause
    exit /b 1
)

echo Encontrado Python em: %PYTHON_PATH%

REM Caminhos
set SCRIPT=alert_scheduler.py
set TASK_NAME=AssistenteBot-AlertScheduler
set TASK_DIR=C:\AssistentePessoal

echo [1/2] Removendo tarefa anterior...
schtasks /delete /tn "%TASK_NAME%" /f 2>nul
if %ERRORLEVEL% equ 0 (
    echo OK - Tarefa anterior removida
) else (
    echo INFO - Nenhuma tarefa anterior encontrada
)

echo [2/2] Criando nova tarefa...
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" -u \"%TASK_DIR%\%SCRIPT%\"" ^
    /sc minute ^
    /mo 1 ^
    /rl highest ^
    /f

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo SUCCESS! TAREFA CRIADA COM SUCESSO!
    echo ======================================================================
    echo.
    echo Sua tarefa ALERTSCHEDULE agora va:
    echo  - Executar AUTOMATICAMENTE a cada 1 minuto
    echo  - Iniciar quando o Windows inicia
    echo  - Enviar alertas Telegram mesmo com PC desligado
    echo.
    echo VOCE NAO PRECISA MAIS rodar python alert_scheduler.py manualmente!
    echo.
    echo Para verificar se esta funcionando:
    echo  1. Crie uma tarefa com horario daqui a 2 minutos
    echo  2. Aguarde - voce receberaacesso no Telegram mesmo com terminal fechado!
    echo.
    echo Para gerenciar a tarefa (pausar/deletar):
    echo  1. Pressione: Win + R
    echo  2. Digite: taskschd.msc
    echo  3. Procure: AssistenteBot-AlertScheduler
    echo.
) else (
    echo.
    echo ERRO! Nao foi possivel criar a tarefa.
    echo Certifique-se que VOCE ESTA EXECUTANDO COMO ADMINISTRADOR!
    echo.
    echo Para executar como administrador:
    echo  1. Clique com botao direito neste arquivo
    echo  2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

pause
