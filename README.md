# Analisador de Documentos

Sistema de análise de documentos jurídicos e policiais usando IA.

## Funcionalidades

- Extração automática de informações de documentos PDF
- Análise de conteúdo usando IA (Mistral)
- Interface gráfica interativa
- Capacidade de fazer perguntas sobre o documento

## Requisitos

- Python 3.12+
- Bibliotecas listadas em `requirements.txt`
- Chaves de API (configurar no arquivo `.env`):
  - `MISTRAL_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `OPENAI_API_KEY`

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv web-automation-py3.12
```

3. Ative o ambiente virtual:
```bash
# Windows
web-automation-py3.12\Scripts\activate

# Linux/Mac
source web-automation-py3.12/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as chaves de API no arquivo `.env`

## Execução

Para iniciar o programa, use:

```bash
python -m src.main
```

## Uso

1. Clique em "Selecionar Arquivo" para escolher um PDF
2. O sistema analisará o documento e mostrará as informações extraídas
3. Use o campo de pergunta para fazer consultas sobre o documento
4. O sistema responderá usando IA, baseado no conteúdo do documento

## Estrutura do Projeto

- `src/`: Código fonte
  - `ai_analyzer/`: Módulos de análise com IA
  - `pdf_processor/`: Processamento de PDFs
  - `knowledge_base/`: Base de conhecimento jurídico
  - `ui/`: Interface gráfica
- `config/`: Arquivos de configuração
  - `rules/`: Regras para análise de documentos
