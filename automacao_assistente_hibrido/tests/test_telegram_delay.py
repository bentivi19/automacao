#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste com DELAY - Enviar alertas espaçados para ver se chegam
"""

import time
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

print("\n" + "="*80)
print("TESTE DE TELEGRAM COM DELAY")
print("="*80 + "\n")

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Enviar 3 mensagens com delay
mensagens = [
    "📬 ALERTA 1: Teste chegando agora",
    "📬 ALERTA 2: Teste após 5 segundos",
    "📬 ALERTA 3: Teste após mais 5 segundos"
]

for i, msg in enumerate(mensagens):
    timestamp = datetime.now().strftime('%H:%M:%S')
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{msg}\n\nHora: {timestamp}"
    }
    
    print(f"Enviando mensagem {i+1}/3...")
    try:
        response = requests.post(url, json=payload, timeout=5)
        result = response.json()
        
        if result.get('ok'):
            print(f"  ✅ Enviada com sucesso (ID: {result.get('result', {}).get('message_id')})")
        else:
            print(f"  ❌ Erro: {result}")
    except Exception as e:
        print(f"  ❌ Erro: {str(e)}")
    
    if i < len(mensagens) - 1:
        print(f"  Aguardando 5 segundos...\n")
        time.sleep(5)

print("\n" + "="*80)
print("Você deveria ter recebido 3 mensagens no Telegram")
print("Verifique se todas chegaram!")
print("="*80 + "\n")
