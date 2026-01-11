#!/usr/bin/env python
"""
SCRIPT PARA EXECUTAR MIGRAÇÕES NO CLOUD RUN
"""
import os
import sys
import subprocess

def executar_migracao():
    """Executa migrações via Cloud Run"""

    # Comando para executar migrações
    cmd = [
        "gcloud", "run", "jobs", "create", "migracao-monpec",
        "--source", ".",
        "--platform", "managed",
        "--region", "us-central1",
        "--set-env-vars",
        "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,SECRET_KEY=django-insecure-monpec-gcp-2025-secret-key-production",
        "--add-cloudsql-instances", "monpec-sistema-rural:us-central1:monpec-db",
        "--command", "python,manage.py,migrate,--noinput",
        "--wait"
    ]

    print("Executando migrações no Cloud SQL...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Migrações executadas com sucesso!")
        return True
    else:
        print(f"❌ Erro ao executar migrações: {result.stderr}")
        return False

if __name__ == '__main__':
    executar_migracao()




