Write-Host "Limpando ambiente anterior..."
poetry env remove python3.12
Remove-Item -Path "$env:APPDATA\pypoetry\Cache\virtualenvs" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\pip\Cache" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Criando novo ambiente virtual..."
poetry env use python3.12

Write-Host "Removendo poetry.lock e recriando..."
Remove-Item -Path "poetry.lock" -Force -ErrorAction SilentlyContinue

Write-Host "Configurando pyproject.toml..."
@"
[tool.poetry]
name = "web-automation"
version = "0.1.0"
description = "Web automation project for data extraction"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
numpy = "1.26.2"
pandas = "2.1.4"
openpyxl = "3.1.2"
pyautogui = "0.9.54"
Pillow = "10.1.0"
pytesseract = "0.3.10"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
"@ | Set-Content -Path "pyproject.toml" -Encoding UTF8

Write-Host "Instalando dependencias..."
poetry install

Write-Host "Ativando o ambiente virtual..."
poetry shell

Write-Host "Setup concluido! Execute 'python ocr_extract.py' para iniciar o programa."
