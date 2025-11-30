#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testar se a chave OpenAI é válida e funciona
"""

import os
from dotenv import load_dotenv

print("\n" + "="*80)
print("TESTE DETALHADO DA CHAVE OPENAI")
print("="*80 + "\n")

# Carregar .env
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")

print(f"1. Chave carregada: {bool(api_key)}")
if api_key:
    print(f"   Primeiros 30 chars: {api_key[:30]}")
    print(f"   Comprimento: {len(api_key)}")
    print(f"   Válida (começa com sk-proj-): {api_key.startswith('sk-proj-')}")
else:
    print("   ❌ Nenhuma chave encontrada!")
    exit(1)

print("\n2. Tentando conectar à OpenAI...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    print("   ✅ Cliente criado com sucesso")
    
except Exception as e:
    print(f"   ❌ Erro ao criar cliente: {str(e)}")
    exit(1)

print("\n3. Testando acesso à API...")
try:
    # Tentar listar modelos (chamada simples)
    response = client.models.list()
    print(f"   ✅ Acesso à API bem-sucedido!")
    print(f"   Modelos disponíveis: {len(response.data)}")
    
except Exception as e:
    error_str = str(e)
    print(f"   ❌ Erro na API: {error_str[:150]}")
    
    # Analisar tipo de erro
    if "billing" in error_str.lower():
        print("\n   ⚠️  PROBLEMA DE BILLING DETECTADO")
        print("   - Acesse: https://platform.openai.com/account/billing/overview")
        print("   - Verifique se tem método de pagamento")
        print("   - Ative auto-recharge se necessário")
    elif "invalid" in error_str.lower() or "unauthorized" in error_str.lower():
        print("\n   ⚠️  PROBLEMA DE AUTENTICAÇÃO")
        print("   - A chave pode estar expirada ou inválida")
        print("   - Gere uma nova chave em: https://platform.openai.com/api-keys")
    
    exit(1)

print("\n4. Testando chamada real ao GPT...")
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente de teste."},
            {"role": "user", "content": "Teste: Responda com 'OK' apenas."}
        ],
        max_tokens=10
    )
    
    answer = response.choices[0].message.content
    print(f"   ✅ Resposta GPT: {answer}")
    print("   🎉 TUDO FUNCIONANDO!")
    
except Exception as e:
    error_str = str(e)
    print(f"   ❌ Erro: {error_str[:200]}")
    
    if "billing" in error_str.lower() or "not_active" in error_str.lower():
        print("\n   ⚠️  Seu crédito na OpenAI pode estar vencido ou desabilitado")
        print("   - Mesmo com saldo, a conta pode estar inativa")
        print("   - Acesse: https://platform.openai.com/account/billing/overview")
        print("   - Clique em 'Enable auto recharge' ou adicione novo método de pagamento")

print("\n" + "="*80 + "\n")
