#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar se o Windows Task Scheduler está rodando corretamente
Cria um arquivo LOG toda vez que é executado
"""

import os
import sys
from datetime import datetime

# Arquivo de log
LOG_FILE = r"C:\AssistentePessoal\scheduler_log.txt"

def log_msg(msg):
    """Escreve mensagem no arquivo de log"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {msg}\n")

# Registrar que o script foi executado
log_msg("✓ TESTE: alert_scheduler.py foi EXECUTADO pelo Windows Task Scheduler!")

# Agora rodar o scheduler normal
try:
    from alert_scheduler import start_scheduler
    
    log_msg("✓ Módulo alert_scheduler carregado com sucesso")
    
    # Rodar por 70 segundos e depois sair (para não travar)
    import time
    start_scheduler()
    
    # Rodar por 1 minuto
    for _ in range(6):
        time.sleep(10)
    
    log_msg("✓ Scheduler completou ciclo de 60 segundos")
    
except Exception as e:
    log_msg(f"✗ ERRO: {str(e)}")
    log_msg(f"  Tipo: {type(e).__name__}")
    import traceback
    log_msg(f"  Traceback: {traceback.format_exc()}")
