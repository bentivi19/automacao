# Verifica se está rodando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Por favor, execute como Administrador!"
    Break
}

# Instala o Chocolatey se não estiver instalado
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Output "Instalando Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Instala o Tesseract
Write-Output "Instalando Tesseract OCR..."
choco install tesseract -y

# Baixa e instala o pacote de idioma português
$tessdataPath = "C:\Program Files\Tesseract-OCR\tessdata"
$porTrainedData = "https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata"
$outputFile = Join-Path $tessdataPath "por.traineddata"

Write-Output "Baixando pacote de idioma português..."
Invoke-WebRequest -Uri $porTrainedData -OutFile $outputFile

# Adiciona o Tesseract ao PATH e configura TESSDATA_PREFIX
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
[Environment]::SetEnvironmentVariable("TESSDATA_PREFIX", $tessdataPath, "Machine")
$env:TESSDATA_PREFIX = $tessdataPath

Write-Output "Instalação concluída! O Tesseract foi instalado em C:\Program Files\Tesseract-OCR"
Write-Output "O pacote de idioma português foi instalado em $tessdataPath"
Write-Output "A variável TESSDATA_PREFIX foi configurada para $tessdataPath"
Write-Output "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
