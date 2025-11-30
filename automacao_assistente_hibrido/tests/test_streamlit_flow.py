#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simular EXATAMENTE o fluxo do Streamlit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_handlers import model_manager
from memorystore import MemoryStore
from PIL import Image
import io

print("=" * 70)
print("🔍 SIMULANDO FLUXO DO STREAMLIT")
print("=" * 70)

# Setup
memory_store = MemoryStore()

# 1. Simular upload de imagem
print("\n1️⃣ Simulando upload de imagem...")
img = Image.new('RGB', (200, 200), color='green')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)
img_data = img_bytes.getvalue()
print(f"   ✅ Imagem: {len(img_data)} bytes (verde)")

# 2. Simular input do usuário
user_input = "O que você vê nessa imagem?"
print(f"\n2️⃣ Input do usuário: '{user_input}'")

# 3. Simular seleção de modelo
provider = "OpenAI"
model = "📱 GPT-4o-mini (Visão)"
print(f"\n3️⃣ Modelo selecionado:")
print(f"   Provider: {provider}")
print(f"   Model: {model}")

# 4. Simular função call_model
def call_model(prompt, img_data=None):
    # Buscar notas relevantes ANTES de fazer a pergunta (apenas se não tiver imagem/vídeo/áudio)
    if not img_data:
        notas_relevantes = memory_store.search_notes(prompt, limit=3)
    else:
        notas_relevantes = []
    
    # Construir contexto com as notas
    contexto = ''
    if notas_relevantes:
        contexto = '\n\n[CONTEXTO DE NOTAS ANTERIORES]\n'
        for nota in notas_relevantes:
            if nota.get('question') and nota.get('answer'):
                contexto += f"\nPergunta: {nota.get('question')}\nResposta: {nota.get('answer')}\n"
            else:
                contexto += f"\nNota: {nota.get('text')}\n"
        contexto += '\n[FIM DO CONTEXTO]\n\n'
    
    # Montar prompt com contexto (simples, sem adicionar "Pergunta do usuario")
    prompt_final = contexto + prompt if contexto else prompt
    
    print(f"\n   🔹 Prompt final enviado ao modelo:")
    print(f"      '{prompt_final}'")
    print(f"   🔹 Tem img_data? {img_data is not None}")
    print(f"   🔹 Tamanho img_data: {len(img_data) if img_data else 0} bytes")
    
    # Chamar modelo selecionado
    resultado = model_manager.generate(provider, model, prompt_final, img_data)
    
    print(f"\n   📍 Resposta do modelo:")
    print(f"      {resultado}")
    
    return resultado

# 5. Processar imagem
print(f"\n4️⃣ Processando imagem com call_model...")
resultado = call_model(f'Imagem: {user_input}', img_data=img_data)

# 6. Validar resultado
print(f"\n5️⃣ Validação:")
if "verde" in resultado.lower() or "green" in resultado.lower():
    print(f"   ✅ SUCESSO! Modelo identificou a cor verde!")
else:
    print(f"   ❌ FALHA: Modelo não identificou a cor corretamente")
    print(f"   Resposta: {resultado}")

print("\n" + "=" * 70)
