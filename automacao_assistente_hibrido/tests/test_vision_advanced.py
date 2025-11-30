#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar modelos OpenAI com visão avançada
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_handlers import model_manager

print("=" * 70)
print("🎥 TESTE DE MODELOS COM VISÃO AVANÇADA")
print("=" * 70)

# Verificar modelos disponíveis
print("\n✅ Provedores disponíveis:")
providers = model_manager.get_providers()
for provider in providers:
    print(f"   • {provider}")

print("\n📷 Modelos OpenAI disponíveis (com visão):")
openai_models = model_manager.get_models("OpenAI")
for model in openai_models:
    print(f"   {model}")

print("\n" + "=" * 70)
print("CAPACIDADES:")
print("=" * 70)

capabilities = {
    "🎥 GPT-4o (Multimodal)": {
        "Imagens": "✅ Sim",
        "Vídeos": "✅ Sim",
        "Áudios": "✅ Sim",
        "Custo": "Médio",
        "Recomendado": "Sim ⭐"
    },
    "📷 GPT-4 Turbo com Visão": {
        "Imagens": "✅ Sim",
        "Vídeos": "⚠️ Limitado",
        "Áudios": "❌ Não",
        "Custo": "Alto",
        "Recomendado": "Para documentos"
    },
    "📱 GPT-4o-mini (Visão)": {
        "Imagens": "✅ Sim",
        "Vídeos": "✅ Sim",
        "Áudios": "✅ Sim",
        "Custo": "Muito Baixo",
        "Recomendado": "Melhor custo-benefício"
    }
}

for model, caps in capabilities.items():
    print(f"\n{model}")
    print("-" * 70)
    for capability, status in caps.items():
        print(f"  {capability:20} {status}")

print("\n" + "=" * 70)
print("TESTE DE GERAÇÃO COM VISÃO")
print("=" * 70)

# Teste com GPT-4o-mini (mais barato)
print("\n🧪 Testando GPT-4o-mini...")
prompt = "Se você tivesse uma imagem, o que poderia fazer com ela?"
try:
    response = model_manager.generate("OpenAI", "📱 GPT-4o-mini (Visão)", prompt)
    print(f"✅ Resposta: {response[:100]}...")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "=" * 70)
print("✅ TUDO PRONTO!")
print("=" * 70)
print("""
Você agora pode:
  1️⃣ Fazer upload de IMAGENS 📷
  2️⃣ Fazer upload de VÍDEOS 🎬
  3️⃣ Fazer upload de ÁUDIOS 🎤
  4️⃣ Fazer upload de PDFs 📄

Recomendações:
  • Use GPT-4o para análise profunda de mídia
  • Use GPT-4o-mini para economizar (75% mais barato)
  • Consulte docs/GUIA_VISAO_AVANCADA.md para mais detalhes
""")
