"""
Script para backup automático dos tenants
Execute via agendador de tarefas (Windows Task Scheduler) ou cron (Linux)

Windows: Agendar para executar diariamente
Linux: Adicionar ao crontab: 0 2 * * * /caminho/para/python backup_automatico.py
"""
import os
import sys
import django
from pathlib import Path

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    try:
        # Executa o comando de backup
        call_command('backup_tenants', '--compress')
        print("Backup concluido com sucesso!")
    except Exception as e:
        print(f"ERRO ao executar backup: {e}")
        sys.exit(1)






