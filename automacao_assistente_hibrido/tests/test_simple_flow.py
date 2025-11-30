#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simples para validar fluxo de imagem
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_handlers import model_manager
from PIL import Image
import io

print("=" * 70)
print("🔍 VALIDAÇÃO SIMPLES - FLUXO DE IMAGEM")
print("=" * 70)

# 1. Criar imagem de teste
print("\n1️⃣ Criando imagem...")
img = Image.new('RGB', (200, 200), color='blue')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)
img_data = img_bytes.getvalue()
print(f"   ✅ Imagem: {len(img_data)} bytes")

# 2. Obter handlers
print("\n2️⃣ Carregando handler GPT-4o-mini...")
provider = "OpenAI"
model_name = "📱 GPT-4o-mini (Visão)"

print(f"   Provider: {provider}")
print(f"   Model: {model_name}")

# 3. Verificar se handler existe
if provider in model_manager.handlers and model_name in model_manager.handlers[provider]:
    handler = model_manager.handlers[provider][model_name]
    print(f"   ✅ Handler encontrado: {handler.model}")
else:
    print(f"   ❌ Handler não encontrado!")
    print(f"   Provedores: {list(model_manager.handlers.keys())}")
    print(f"   Modelos em OpenAI: {list(model_manager.handlers.get('OpenAI', {}).keys())}")
    sys.exit(1)

# 4. Testar chamada COM IMAGEM
print("\n3️⃣ Testando chamada com imagem...")
prompt = "Qual é a cor desta imagem? Responda apenas a cor."

try:
    response = handler.generate(prompt, img_data=img_data)
    print(f"\n   📍 RESPOSTA RECEBIDA:")
    print(f"   {response}")
    
    if "azul" in response.lower() or "blue" in response.lower():
        print(f"\n   ✅ SUCESSO! Modelo consegue ver a imagem!")
    else:
        print(f"\n   ⚠️ Resposta estranha - modelo não identificou a cor corretamente")
        
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
