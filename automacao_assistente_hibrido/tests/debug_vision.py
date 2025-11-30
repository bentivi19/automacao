#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script para verificar o problema de imagem
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_handlers import model_manager

print("=" * 70)
print("🔍 DEBUG - PROBLEMA DE IMAGEM")
print("=" * 70)

# Verificar modelos
print("\n1️⃣ Modelos disponíveis:")
models = model_manager.get_models("OpenAI")
for i, model in enumerate(models):
    print(f"   [{i}] '{model}' (len={len(model)})")

# Verificar handlers
print("\n2️⃣ Handlers registrados em model_manager.handlers['OpenAI']:")
for key in model_manager.handlers["OpenAI"]:
    print(f"   '{key}'")

# Testar com modelo específico
print("\n3️⃣ Testando geração com cada modelo:")
test_prompt = "Você consegue ver imagens? Responda apenas 'SIM' ou 'NÃO'"

for model_name in models:
    print(f"\n   Testando: '{model_name}'")
    try:
        # Tentar com handler direto
        if model_name in model_manager.handlers["OpenAI"]:
            handler = model_manager.handlers["OpenAI"][model_name]
            print(f"      ✅ Handler encontrado")
            print(f"      Model API: {handler.model}")
            
            # Fazer chamada sem imagem
            response = handler.generate(test_prompt)
            print(f"      Resposta: {response[:50]}...")
        else:
            print(f"      ❌ Handler NÃO encontrado no dicionário")
            print(f"         Chaves disponíveis: {list(model_manager.handlers['OpenAI'].keys())}")
    except Exception as e:
        print(f"      ❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ DEBUG CONCLUÍDO")
print("=" * 70)
