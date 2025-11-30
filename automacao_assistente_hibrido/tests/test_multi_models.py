#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script para verificar multi-provider model support
"""

from model_handlers import model_manager

print("=" * 60)
print("🧪 TESTE DE MÚLTIPLOS MODELOS")
print("=" * 60)

# Testar importação
print("\n✅ Importação OK\n")

# Listar provedores
providers = model_manager.get_providers()
print(f"Provedores disponíveis: {providers}")

# Listar modelos por provedor
print("\n" + "-" * 60)
print("MODELOS POR PROVEDOR:")
print("-" * 60)

for provider in providers:
    models = model_manager.get_models(provider)
    print(f"\n{provider}:")
    for model in models:
        print(f"  • {model}")

# Testar dicionário completo
print("\n" + "=" * 60)
print("RESUMO:")
print("=" * 60)
all_models = model_manager.get_all_models_dict()
for provider, models in all_models.items():
    print(f"✅ {provider}: {len(models)} modelo(s) disponível(is)")

print("\n" + "=" * 60)
print("🎉 TUDO OK! Sistema multi-provedor funcionando!")
print("=" * 60)
