# Script PowerShell para configurar ambiente Poetry

Write-Host "Configurando ambiente Poetry..." -ForegroundColor Green

# Definir o diretório do projeto
$projectDir = "C:\Users\Julio Soama\CascadeProjects\web-automation"

# Navegar para o diretório do projeto
Write-Host "`nNavegando para $projectDir..." -ForegroundColor Cyan
Set-Location -Path $projectDir

# Forçar desativação de qualquer ambiente virtual
if ($env:VIRTUAL_ENV) {
    Write-Host "`nDesativando ambiente virtual atual: $env:VIRTUAL_ENV" -ForegroundColor Yellow
    deactivate
    Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
}

# Remover todos os ambientes virtuais do Poetry
Write-Host "`nRemovendo todos os ambientes virtuais Poetry..." -ForegroundColor Cyan
poetry env list | ForEach-Object {
    if ($_ -match '\S+') {
        poetry env remove $matches[0]
    }
}

# Limpar cache do Poetry
Write-Host "`nLimpando cache do Poetry..." -ForegroundColor Cyan
poetry cache clear . --all --no-interaction

# Limpar cache do pip
Write-Host "`nLimpando cache do pip..." -ForegroundColor Cyan
pip cache purge

# Remover poetry.lock se existir
$lockFile = Join-Path $projectDir "poetry.lock"
if (Test-Path $lockFile) {
    Write-Host "`nRemovendo poetry.lock..." -ForegroundColor Cyan
    Remove-Item $lockFile
}

# Instalar dependências com um novo ambiente virtual
Write-Host "`nInstalando dependências com Poetry..." -ForegroundColor Cyan
poetry install --no-cache --remove-untracked

# Obter o caminho do novo ambiente virtual
$envPath = poetry env info --path

Write-Host "`nAmbiente configurado com sucesso!" -ForegroundColor Green
Write-Host "`nPara ativar o novo ambiente, execute os seguintes comandos:" -ForegroundColor Yellow
Write-Host "1. exit" -ForegroundColor White
Write-Host "2. poetry shell" -ForegroundColor White
Write-Host "3. python -m web_automation.main" -ForegroundColor White

Write-Host "`nCaminho do novo ambiente virtual: $envPath" -ForegroundColor Cyan

# Manter a janela aberta
Write-Host "`nPressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
