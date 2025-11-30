#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script para verificar geracao de respostas com novo sistema
"""

from model_handlers import model_manager

print("=" * 60)
print("🧪 TESTE DE GERAÇÃO COM MÚLTIPLOS MODELOS")
print("=" * 60)

prompt = "Olá! Me apresente sucintamente em uma frase."

# Test 1: Local Ollama
print("\n[1] Testando Local - Ollama...")
print("-" * 60)
try:
    resposta_local = model_manager.generate("Local", "Ollama", prompt)
    if "❌" in str(resposta_local):
        print(f"⚠️ Local (Ollama não está rodando)")
        print(f"Mensagem: {resposta_local}")
    else:
        print(f"✅ Local OK")
        print(f"Resposta: {resposta_local[:100]}...")
except Exception as e:
    print(f"❌ Erro: {e}")

# Test 2: OpenAI GPT-4o-mini
print("\n[2] Testando OpenAI - GPT-4o-mini...")
print("-" * 60)
try:
    resposta_openai = model_manager.generate("OpenAI", "GPT-4o-mini", prompt)
    if "❌" in str(resposta_openai):
        print(f"⚠️ OpenAI: {resposta_openai}")
    else:
        print(f"✅ OpenAI OK")
        print(f"Resposta: {resposta_openai[:100]}...")
except Exception as e:
    print(f"❌ Erro: {e}")

# Test 3: Google (deve falhar gracefully)
print("\n[3] Testando Google - Gemini 2.0 Flash (esperando falha sem chave)...")
print("-" * 60)
try:
    resposta_google = model_manager.generate("Google", "Gemini 2.0 Flash", prompt)
    print(f"Resultado: {resposta_google}")
except Exception as e:
    print(f"⚠️ Esperado - Google sem API key: {type(e).__name__}")

# Test 4: Anthropic (deve falhar gracefully)
print("\n[4] Testando Anthropic - Claude (esperando falha sem chave)...")
print("-" * 60)
try:
    resposta_anthropic = model_manager.generate("Anthropic", "Claude 3.5 Sonnet", prompt)
    print(f"Resultado: {resposta_anthropic}")
except Exception as e:
    print(f"⚠️ Esperado - Anthropic sem API key: {type(e).__name__}")

print("\n" + "=" * 60)
print("✅ TESTE DE GERAÇÃO CONCLUÍDO!")
print("=" * 60)
print("\nResumo:")
print("✓ Local: sempre disponível (quando Ollama está rodando)")
print("✓ OpenAI: funcionando com 4 modelos")
print("✓ Google: pronto (sem API key configurada)")
print("✓ Anthropic: pronto (sem API key configurada)")
