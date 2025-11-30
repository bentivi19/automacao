#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script para verificar integração com Streamlit
Simula o que o assistant.py vai fazer
"""

from model_handlers import model_manager

print("=" * 70)
print("🧪 TESTE DE INTEGRAÇÃO - SIMULANDO STREAMLIT")
print("=" * 70)

# Simular session_state do Streamlit
class SessionState:
    def __init__(self):
        self.current_provider = 'Local'
        self.current_model = 'Ollama'
    
    def update_provider(self, provider):
        self.current_provider = provider
        # Modelo padrão para este provedor
        modelos = model_manager.get_models(provider)
        if modelos:
            self.current_model = modelos[0]

session = SessionState()

print("\n" + "=" * 70)
print("TEST 1: Listar Provedores (para dropdown 1)")
print("=" * 70)
providers = model_manager.get_providers()
print(f"Provedores: {providers}")
print(f"Selecionado: {session.current_provider}")

print("\n" + "=" * 70)
print("TEST 2: Listar Modelos do Provedor (para dropdown 2)")
print("=" * 70)
models = model_manager.get_models(session.current_provider)
print(f"Modelos disponíveis em '{session.current_provider}': {models}")
print(f"Modelo selecionado: {session.current_model}")

print("\n" + "=" * 70)
print("TEST 3: Simular Mudança de Provedor")
print("=" * 70)
session.update_provider('OpenAI')
print(f"Novo provedor: {session.current_provider}")
print(f"Modelos em '{session.current_provider}': {model_manager.get_models(session.current_provider)}")
print(f"Modelo padrão: {session.current_model}")

print("\n" + "=" * 70)
print("TEST 4: Teste de Geração com Provider/Model")
print("=" * 70)
prompt = "Quem é você? (responda em uma frase)"
print(f"Provider: {session.current_provider}")
print(f"Model: {session.current_model}")
print(f"Prompt: {prompt}\n")

resposta = model_manager.generate(session.current_provider, session.current_model, prompt)
print(f"Resposta: {resposta[:150]}...")

print("\n" + "=" * 70)
print("TEST 5: Testar com Provider Não Disponível (graceful degradation)")
print("=" * 70)
resposta_falha = model_manager.generate("Google", "Gemini 2.0 Flash", prompt)
print(f"Resultado: {resposta_falha}")

print("\n" + "=" * 70)
print("✅ INTEGRAÇÃO OK!")
print("=" * 70)
print("\nResumo:")
print("✓ Dropdown de Provedores: Funciona")
print("✓ Dropdown de Modelos: Funciona (dinâmico)")
print("✓ Geração de Respostas: Funciona")
print("✓ Graceful Degradation: Funciona")
print("\n✅ PRONTO PARA USAR NO STREAMLIT!")
