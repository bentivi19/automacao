# Extrator de NFs e Promotorias

Este projeto automatiza a extração de números de NF e suas respectivas promotorias de uma página web, salvando os resultados em uma planilha Excel.

## Funcionalidades

- Captura de tela automática
- OCR para reconhecimento de texto
- Extração de NFs no formato XXXX.XXXXXXX/XXXX
- Identificação automática das promotorias
- Exportação para Excel com formatação
- Interface gráfica simples

## Requisitos

- Python 3.12
- Tesseract OCR
- Dependências Python listadas em `requirements.txt`

## Instalação

1. Instale o Tesseract OCR:
```powershell
.\install_tesseract.ps1
```

2. Instale as dependências Python:
```powershell
poetry install
```

## Uso

1. Execute o script:
```powershell
poetry run python ocr_extract.py
```

2. Navegue até a página que contém as NFs
3. Clique no botão "Extrair NFs"
4. Os resultados serão salvos em `atribuicoes_do_dia.xlsx`

## Estrutura do Projeto

- `ocr_extract.py`: Script principal
- `install_tesseract.ps1`: Script de instalação do Tesseract
- `requirements.txt`: Dependências Python
- `pyproject.toml`: Configuração do Poetry
