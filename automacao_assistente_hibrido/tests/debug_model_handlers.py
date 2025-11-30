#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de debug para verificar por que GPT não aparece
"""

import os
from dotenv import load_dotenv

print("\n" + "="*80)
print("DEBUG: Verificando configuração do GPT")
print("="*80 + "\n")

# Carregar .env
load_dotenv()

# Verificar se a chave foi carregada
api_key = os.getenv("OPENAI_API_KEY")

print(f"OPENAI_API_KEY carregada: {bool(api_key)}")
if api_key:
    print(f"Primeiros 30 caracteres: {api_key[:30]}...")
    print(f"Comprimento: {len(api_key)}")
else:
    print("❌ ERRO: Chave não encontrada!")

print("\n" + "="*80)
print("Tentando instanciar HybridModelManager...")
print("="*80 + "\n")

try:
    from model_handlers import HybridModelManager
    
    manager = HybridModelManager()
    
    print(f"✅ HybridModelManager criado")
    print(f"GPT disponível: {manager.gpt_available}")
    
    if not manager.gpt_available:
        print(f"Erro do GPT: {manager.gpt_error}")
    
    print(f"\nModelos disponíveis:")
    for modelo in manager.get_model_options():
        print(f"  - {modelo}")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("Fim do debug")
print("="*80 + "\n")
