import requests
import json
import time
from datetime import datetime

print("\n" + "="*70)
print("🤖 CONFIGURADOR TELEGRAM - ASSISTENTE PESSOAL")
print("="*70)

token = input("\n📌 Cole seu TOKEN do Telegram (obtido do @BotFather):\n> ").strip()

if not token or ':' not in token:
    print("❌ Token inválido! Deve ter formato: 123456:ABC-DEF...")
    exit(1)

print(f"\n✅ Token recebido: {token[:20]}...")
print("\n" + "-"*70)
print("PRÓXIMAS ETAPAS:")
print("-"*70)
print("1. Abra o Telegram no seu celular/PC")
print("2. Procure pelo seu bot (nome que colocou no @BotFather)")
print("3. CLIQUE PARA INICIAR uma conversa com o bot")
print("4. ENVIE UMA MENSAGEM QUALQUER (pode ser só 'oi' ou '/start')")
print("5. VOLTE AQUI E PRESSIONE ENTER")
print("-"*70)

input("\n⏳ Pressione ENTER quando tiver enviado a mensagem para o bot... ")

print("\n🔍 Buscando seu ID...")
time.sleep(1)

try:
    url = f'https://api.telegram.org/bot{token}/getUpdates'
    response = requests.get(url, timeout=5)
    data = response.json()
    
    if not data.get('ok'):
        print(f"\n❌ Erro na resposta: {data}")
        exit(1)
    
    if not data.get('result'):
        print("\n❌ Ainda nenhuma mensagem recebida!")
        print("   - Tem certeza que clicou em 'INICIAR' no bot?")
        print("   - Tentou enviar uma mensagem?")
        print("   - Espere 5 segundos e tente novamente")
        exit(1)
    
    # Pega o primeiro update (mensagem mais recente)
    update = data['result'][-1]
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    user_id = message.get('from', {}).get('id')
    text = message.get('text', '')
    
    if not chat_id:
        print("❌ Não consegui encontrar o chat ID")
        print(f"Resposta: {json.dumps(data, indent=2)}")
        exit(1)
    
    print("\n" + "="*70)
    print("✅ SUCESSO! IDS ENCONTRADOS:")
    print("="*70)
    print(f"\n📱 CHAT ID:    {chat_id}")
    print(f"👤 USER ID:    {user_id}")
    print(f"💬 Mensagem:   {text}")
    print(f"🔑 Token:      {token[:30]}...")
    print("\n" + "="*70)
    
    print("\nAGORA FAÇA ISSO:")
    print("-"*70)
    print(f"\n1. Abra o arquivo: c:\\AssistentePessoal\\.env")
    print(f"\n2. Procure por essas linhas:")
    print(f"""
# Telegram Bot (GRATUITO e SIMPLES!)
TELEGRAM_BOT_TOKEN=seu_bot_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
""")
    print(f"\n3. Substitua por:")
    print(f"""
# Telegram Bot (GRATUITO e SIMPLES!)
TELEGRAM_BOT_TOKEN={token}
TELEGRAM_CHAT_ID={chat_id}
""")
    print(f"\n4. SALVE o arquivo (Ctrl+S)")
    print(f"\n5. REINICIE o Streamlit (F5 no navegador)")
    print("\n" + "="*70)
    
    # Oferece salvar automaticamente
    salvar = input("\n💾 Quer que eu salve automaticamente? (S/N): ").strip().upper()
    if salvar == 'S':
        # Lê o arquivo atual
        with open('c:\\AssistentePessoal\\.env', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Substitui ou adiciona Telegram
        if 'TELEGRAM_BOT_TOKEN' in conteudo:
            conteudo = conteudo.replace(
                f"TELEGRAM_BOT_TOKEN=seu_bot_token_aqui",
                f"TELEGRAM_BOT_TOKEN={token}"
            )
            conteudo = conteudo.replace(
                f"TELEGRAM_CHAT_ID=seu_chat_id_aqui",
                f"TELEGRAM_CHAT_ID={chat_id}"
            )
        else:
            conteudo += f"\n\n# Telegram Bot (GRATUITO e SIMPLES!)\nTELEGRAM_BOT_TOKEN={token}\nTELEGRAM_CHAT_ID={chat_id}\n"
        
        # Salva
        with open('c:\\AssistentePessoal\\.env', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print("\n✅ Arquivo .env atualizado com sucesso!")
        print("   Você já pode usar o Streamlit agora!")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")
    exit(1)
