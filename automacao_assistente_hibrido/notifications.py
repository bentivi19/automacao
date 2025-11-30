# -*- coding: utf-8 -*-
# notifications.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class NotificationManager:
    """Gerencia notificações por email para tarefas e lembretes."""
    
    def __init__(self):
        self.gmail_user = os.getenv("GMAIL_USER")
        self.gmail_password = os.getenv("GMAIL_PASSWORD")
        self.alert_email = os.getenv("ALERT_EMAIL", self.gmail_user)
        
        # Telegram Bot
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
    def send_email_alert(self, task: str, task_type: str = "lembrete"):
        """Envia alerta por email para uma tarefa/lembrete."""
        
        if not self.gmail_user or not self.gmail_password:
            return {
                "success": False,
                "message": "Configuração de email não encontrada. Configure .env com GMAIL_USER e GMAIL_PASSWORD"
            }
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg["From"] = self.gmail_user
            msg["To"] = self.alert_email
            msg["Subject"] = f"🔔 Alerta: {task_type.upper()} - {datetime.now().strftime('%H:%M')}"
            
            # Corpo do email
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #2c3e50; margin-bottom: 15px;">🔔 Alerta de {task_type.upper()}</h2>
                        
                        <p style="font-size: 16px; color: #34495e; margin: 10px 0;">
                            <strong>Tarefa/Lembrete:</strong> {task}
                        </p>
                        
                        <p style="font-size: 14px; color: #7f8c8d; margin: 15px 0;">
                            <strong>Data e Hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 15px 0;">
                        
                        <p style="font-size: 12px; color: #95a5a6;">
                            Este é um alerta automático do seu Assistente Pessoal.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, "html"))
            
            # Conectar ao Gmail e enviar
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            return {
                "success": True,
                "message": f"✅ Alerta enviado para {self.alert_email}"
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "❌ Erro de autenticação. Verifique GMAIL_USER e GMAIL_PASSWORD no arquivo .env"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erro ao enviar email: {str(e)}"
            }
    
    def send_telegram_alert(self, task: str, task_type: str = "lembrete"):
        """Envia alerta por Telegram - SUPER SIMPLES E GRATUITO!"""
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return {
                "success": False,
                "message": "❌ Telegram não configurado. Adicione TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no arquivo .env"
            }
        
        try:
            # Formatar mensagem
            hora = datetime.now().strftime('%H:%M')
            mensagem = f"""🔔 *{task_type.upper()} - {hora}*

*Tarefa:* {task}

_Assistente Pessoal_"""
            
            # Enviar via Telegram
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            dados = {
                "chat_id": self.telegram_chat_id,
                "text": mensagem,
                "parse_mode": "Markdown"
            }
            
            resposta = requests.post(url, json=dados, timeout=10)
            resultado = resposta.json()
            
            if resultado.get("ok"):
                return {
                    "success": True,
                    "message": f"✅ Alerta enviado para Telegram!"
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Erro Telegram: {resultado.get('description', 'Desconhecido')}"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Erro ao enviar Telegram: {str(e)}"
            }

# Instância global
notifier = NotificationManager()
