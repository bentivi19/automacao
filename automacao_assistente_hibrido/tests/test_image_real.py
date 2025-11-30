#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar se imagem está sendo enviada corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_handlers import model_manager
import base64
from PIL import Image
import io

print("=" * 70)
print("🧪 TESTE COM IMAGEM REAL")
print("=" * 70)

# Criar uma imagem de teste (quadrado vermelho 100x100)
print("\n1️⃣ Criando imagem de teste...")
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)
img_data = img_bytes.getvalue()
print(f"   ✅ Imagem criada: {len(img_data)} bytes")

# Testar com GPT-4o-mini
print("\n2️⃣ Testando com GPT-4o-mini...")
model_name = '📱 GPT-4o-mini (Visão)'
prompt = "Descreva esta imagem em uma palavra"

print(f"   Modelo: {model_name}")
print(f"   Prompt: {prompt}")
print(f"   Imagem: {len(img_data)} bytes (quadrado vermelho)")

try:
    handler = model_manager.handlers["OpenAI"][model_name]
    print(f"   ✅ Handler encontrado (API: {handler.model})")
    
    # Chamar com imagem
    response = handler.generate(prompt, img_data)
    print(f"\n   📍 RESPOSTA: {response}")
    
    if "vermelho" in response.lower() or "red" in response.lower():
        print("   ✅ SUCESSO! O modelo conseguiu ver a imagem!")
    else:
        print("   ❌ PROBLEMA: Modelo não identificou a cor vermelha")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
