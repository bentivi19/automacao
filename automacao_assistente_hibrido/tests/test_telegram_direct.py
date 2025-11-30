#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar envio direto de mensagem Telegram
Valida que o bot e chat ID estão corretos
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print("\n" + "="*70)
print("TESTE DE TELEGRAM - VALIDAÇÃO DIRETA")
print("="*70 + "\n")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERRO: Variáveis de ambiente não configuradas!")
    print(f"   TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
    print(f"   TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    sys.exit(1)

print(f"✓ Bot Token encontrado: {TELEGRAM_BOT_TOKEN[:20]}...")
print(f"✓ Chat ID encontrado: {TELEGRAM_CHAT_ID}")
print()

import requests

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": f"🧪 TESTE DIRETO DE TELEGRAM\n\n✅ Mensagem enviada com sucesso!\n\n⏰ Hora: {datetime.now().strftime('%H:%M:%S')}\n\nSe você viu esta mensagem, o Telegram está funcionando corretamente!"
}

print("Enviando mensagem de teste...")
try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result.get('ok'):
        print("✅ SUCESSO! Mensagem enviada via Telegram!")
        print(f"   Message ID: {result.get('result', {}).get('message_id')}")
    else:
        print("❌ ERRO na API do Telegram!")
        print(f"   Resposta: {result}")
        
except Exception as e:
    print(f"❌ ERRO ao enviar: {str(e)}")
    sys.exit(1)

print("\n" + "="*70)
print("Se recebeu a mensagem no Telegram, o sistema está OK!")
print("="*70 + "\n")
