# Analisador de Documentos Jurídicos

Sistema para análise automatizada de documentos jurídicos usando Mistral AI.

## Instalação e Configuração

1. **Requisitos do Sistema**:
   - Python 3.8 ou superior
   - Tesseract OCR ([Download Windows](https://github.com/UB-Mannheim/tesseract/wiki))
   - Poetry para gerenciamento de dependências

2. **Instalação**:
   ```bash
   # Clone o repositório ou baixe o ZIP
   cd web-automation

   # Instale as dependências usando Poetry
   poetry install

   # Ative o ambiente virtual
   poetry shell
   ```

3. **Configuração** (`.env`):
   ```env
   MISTRAL_API_KEY=sua_chave_aqui  # Principal modelo
   ANTHROPIC_API_KEY=sua_chave_aqui  # Backup (opcional)
   OPENAI_API_KEY=sua_chave_aqui     # Backup (opcional)
   ```

## Formas de Executar o Programa

1. **Da pasta raiz (web-automation)**:
   ```bash
   # Usando módulo Python
   python -m doc_analyzer.src.main

   # OU usando path direto
   cd doc_analyzer
   python src/main.py
   ```

2. **Da pasta doc_analyzer**:
   ```bash
   python src/main.py
   ```

## Uso do Sistema

1. **Interface Gráfica**:
   - Use o botão "Selecionar PDF" para escolher o documento
   - Clique em "Analisar" para iniciar o processamento
   - Os resultados aparecerão na área de texto
   - Use "Salvar Análise" para exportar o relatório

2. **Processamento de Documentos**:
   - O sistema extrai texto via OCR (para documentos digitalizados)
   - Analisa o conteúdo usando Mistral AI
   - Aplica regras de encaminhamento
   - Gera recomendações automáticas

## Modelos de IA

O sistema usa o Mistral AI como modelo principal devido à:
- Excelente performance
- Suporte nativo ao português
- Sem custos ou custos muito baixos
- Respostas rápidas e precisas

Modelos de backup (opcionais):
- Anthropic Claude
- OpenAI GPT-4

## Sistema de Regras

1. **Configuração** (`config/rules/dispatch_rules.yaml`):
   ```yaml
   # Exemplo de regra
   specialized_departments:
     - name: "DEIC"
       conditions:
         - "Lei 12.850"
       email: "deic@policiacivil.sp.gov.br"
   ```

2. **Templates de Email** (`config/templates/`):
   ```text
   Exmo(a). Sr(a). Delegado(a),
   
   Ref: ${numero_nf}
   ...
   ```

## Logs e Diagnóstico

- **Arquivos de Log**:
  ```
  logs/
  ├── main.log          # Log principal
  ├── pdf_processor.log # Processamento de PDF
  ├── ai_analyzer.log   # Análise com IA
  └── rules_engine.log  # Motor de regras
  ```

## Solução de Problemas

1. **Erro no OCR**:
   - Verifique instalação do Tesseract
   - Confirme qualidade do PDF
   - Consulte `logs/pdf_processor.log`

2. **Erro na Análise**:
   - Verifique chave Mistral API no `.env`
   - Confirme conexão com internet
   - Consulte `logs/ai_analyzer.log`

3. **Erro nas Regras**:
   - Valide sintaxe YAML
   - Verifique condições
   - Consulte `logs/rules_engine.log`

## Manutenção

1. **Atualizar Dependências**:
   ```bash
   poetry update
   ```

2. **Limpar Logs**:
   ```bash
   python cleanup.py --logs
   ```

3. **Backup**:
   - Templates: `config/templates/`
   - Regras: `config/rules/`
   - Análises: `output/`

## Suporte

- Consulte os logs em `logs/`
- Verifique a documentação
- Reporte problemas no GitHub
