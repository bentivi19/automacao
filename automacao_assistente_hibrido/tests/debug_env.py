#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug detalhado do carregamento do .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

print("\n" + "="*80)
print("DEBUG DETALHADO DO .ENV")
print("="*80 + "\n")

# Verificar arquivo
print("1. Localizando arquivo .env...")
dotenv_path = find_dotenv()
print(f"   Caminho encontrado: {dotenv_path}")

if not dotenv_path:
    dotenv_path = r"C:\AssistentePessoal\.env"
    print(f"   Usando caminho manual: {dotenv_path}")

print(f"   Existe: {os.path.exists(dotenv_path)}")

# Ler arquivo diretamente
print("\n2. Conteúdo do arquivo:")
try:
    with open(dotenv_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'OPENAI' in line:
                print(f"   Linha {i}: {line[:80]}...")
                if len(line) > 80:
                    print(f"            {line[80:]}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Carregar com dotenv
print("\n3. Carregando com load_dotenv()...")
result = load_dotenv(dotenv_path, override=True)
print(f"   Sucesso: {result}")

# Verificar variável
print("\n4. Variável após load_dotenv():")
api_key = os.getenv("OPENAI_API_KEY")
print(f"   OPENAI_API_KEY: {bool(api_key)}")

if api_key:
    print(f"   Valor: {api_key[:50]}...")
else:
    print("   ❌ Não foi carregada")

# Listar todas as variáveis do .env
print("\n5. Todas as variáveis carregadas:")
for key, value in os.environ.items():
    if 'OPENAI' in key or 'TELEGRAM' in key or 'API' in key:
        print(f"   {key}={value[:50] if len(str(value)) > 50 else value}...")

print("\n" + "="*80 + "\n")
