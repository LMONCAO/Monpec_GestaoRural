# -*- coding: utf-8 -*-
"""
Backend de email customizado para usar OAuth2 do Google via Gmail API
Usa a API Gmail diretamente em vez de SMTP para maior confiabilidade
"""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage, EmailMultiAlternatives
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# Escopos necessários para envio de email
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailOAuth2Backend(BaseEmailBackend):
    """
    Backend de email que usa OAuth2 do Google via Gmail API
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.credentials = None
        self.service = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Carrega credenciais OAuth2 do token armazenado"""
        try:
            from decouple import config
            import os
            from pathlib import Path
            
            token_path = Path(settings.BASE_DIR) / 'gmail_token.json'
            credentials_path = Path(settings.BASE_DIR) / 'gmail_credentials.json'
            
            # Verificar se temos credenciais salvas
            if token_path.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(token_path), SCOPES
                )
                
                # Se as credenciais expiraram, atualizar
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials(token_path)
            else:
                logger.warning(
                    f"Token OAuth2 não encontrado em {token_path}. "
                    "Execute o script autenticar_gmail.py para obter credenciais."
                )
                
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais OAuth2: {e}")
            self.credentials = None
    
    def _save_credentials(self, token_path):
        """Salva as credenciais OAuth2 no arquivo"""
        try:
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'w') as token:
                token.write(self.credentials.to_json())
        except Exception as e:
            logger.error(f"Erro ao salvar credenciais: {e}")
    
    def _get_service(self):
        """Obtém o serviço Gmail API"""
        if self.service:
            return self.service
        
        if not self.credentials:
            if not self.fail_silently:
                raise ValueError(
                    "Credenciais OAuth2 não disponíveis. "
                    "Execute o script autenticar_gmail.py para obter credenciais."
                )
            return None
        
        try:
            # Renovar token se necessário
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_credentials(Path(settings.BASE_DIR) / 'gmail_token.json')
            
            # Construir serviço Gmail
            self.service = build('gmail', 'v1', credentials=self.credentials)
            return self.service
            
        except Exception as e:
            logger.error(f"Erro ao construir serviço Gmail: {e}")
            if not self.fail_silently:
                raise
            return None
    
    def send_messages(self, email_messages: List[EmailMessage]) -> int:
        """
        Envia mensagens usando Gmail API
        """
        if not email_messages:
            return 0
        
        service = self._get_service()
        if not service:
            if not self.fail_silently:
                raise ValueError("Serviço Gmail não disponível")
            return 0
        
        sent_count = 0
        
        for message in email_messages:
            try:
                # Criar mensagem MIME
                if isinstance(message, EmailMultiAlternatives):
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = message.subject
                    msg['From'] = message.from_email
                    msg['To'] = ', '.join(message.to)
                    
                    # Adicionar texto plano
                    if message.body:
                        part1 = MIMEText(message.body, 'plain', 'utf-8')
                        msg.attach(part1)
                    
                    # Adicionar HTML se houver
                    for alt in message.alternatives:
                        if alt[1] == 'text/html':
                            part2 = MIMEText(alt[0], 'html', 'utf-8')
                            msg.attach(part2)
                else:
                    msg = MIMEText(message.body, 'plain', 'utf-8')
                    msg['Subject'] = message.subject
                    msg['From'] = message.from_email
                    msg['To'] = ', '.join(message.to)
                
                # Adicionar cópias e cópias ocultas
                if message.cc:
                    msg['Cc'] = ', '.join(message.cc)
                if message.bcc:
                    msg['Bcc'] = ', '.join(message.bcc)
                
                # Codificar mensagem em base64url
                raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
                
                # Enviar via Gmail API
                send_message = service.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()
                
                logger.info(f"Email enviado via Gmail API. Message ID: {send_message.get('id')}")
                sent_count += 1
                
            except Exception as e:
                logger.exception(f"Erro ao enviar email: {e}")
                if not self.fail_silently:
                    raise
        
        return sent_count

