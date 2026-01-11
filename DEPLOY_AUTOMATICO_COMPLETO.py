#!/usr/bin/env python3
"""
DEPLOY AUTOMÁTICO COMPLETO MONPEC
Script que faz tudo automaticamente
"""

import subprocess
import sys
import time
import os

def executar_comando(cmd, descricao):
    """Executa comando e mostra resultado"""
    print(f"\n🔄 {descricao}...")
    print(f"📋 Comando: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print(f"✅ {descricao} - SUCESSO")
            if result.stdout.strip():
                print(f"📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {descricao} - FALHA")
            print(f"📄 STDOUT: {result.stdout}")
            print(f"📄 STDERR: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ {descricao} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {descricao} - ERRO: {e}")
        return False

def main():
    print("=" * 80)
    print("🚀 DEPLOY AUTOMÁTICO COMPLETO MONPEC")
    print("=" * 80)

    # Configurações
    image = "gcr.io/monpec-sistema-rural/monpec:latest"
    region = "us-central1"
    service = "monpec"

    env_vars = (
        "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,"
        "DB_HOST=34.9.51.178,"
        "DB_PORT=5432,"
        "DB_NAME=monpec-db,"
        "DB_USER=postgres,"
        "DB_PASSWORD=L6171r12@@jjms,"
        "DEBUG=False,"
        "SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
    )

    # Passo 1: Reset do banco
    print("\n" + "="*60)
    print("1️⃣ RESETANDO BANCO DE DADOS")
    print("="*60)

    reset_cmd = f"""
    gcloud run jobs create reset-db-final --image {image} --region {region} \
    --set-env-vars="{env_vars}" \
    --command="python" --args="manage.py,reset_db" \
    --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800
    """

    if executar_comando(reset_cmd, "Criando job de reset"):
        executar_comando("gcloud run jobs execute reset-db-final --region=us-central1 --wait", "Executando reset do banco")

    # Passo 2: Migrações
    print("\n" + "="*60)
    print("2️⃣ APLICANDO MIGRAÇÕES")
    print("="*60)

    migrate_cmd = f"""
    gcloud run jobs create migrate-final --image {image} --region {region} \
    --set-env-vars="{env_vars}" \
    --command="python" --args="manage.py,migrate,--noinput" \
    --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800
    """

    if executar_comando(migrate_cmd, "Criando job de migração"):
        executar_comando("gcloud run jobs execute migrate-final --region=us-central1 --wait", "Executando migrações")

    # Passo 3: Popular dados
    print("\n" + "="*60)
    print("3️⃣ POPULANDO DADOS")
    print("="*60)

    populate_cmd = f"""
    gcloud run jobs create populate-final --image {image} --region {region} \
    --set-env-vars="{env_vars}" \
    --command="python" --args="popular_dados_producao.py" \
    --memory=4Gi --cpu=2 --max-retries=3 --task-timeout=1800
    """

    if executar_comando(populate_cmd, "Criando job de população"):
        executar_comando("gcloud run jobs execute populate-final --region=us-central1 --wait", "Executando população de dados")

    # Passo 4: Atualizar serviço
    print("\n" + "="*60)
    print("4️⃣ ATUALIZANDO SERVIÇO")
    print("="*60)

    update_cmd = f"""
    gcloud run services update {service} --region={region} \
    --set-env-vars="{env_vars}" \
    --memory=4Gi --cpu=2 --timeout=300
    """

    executar_comando(update_cmd, "Atualizando serviço")

    # Passo 5: Testar sistema
    print("\n" + "="*60)
    print("5️⃣ TESTANDO SISTEMA")
    print("="*60)

    testar_cmd = """
    echo "=== VERIFICANDO SISTEMA ===" && \
    curl -I https://monpec-29862706245.us-central1.run.app/ && \
    echo "" && \
    echo "=== TESTANDO LANDING PAGE ===" && \
    curl -s https://monpec-29862706245.us-central1.run.app/ | head -10
    """

    executar_comando(testar_cmd, "Testando sistema final")

    # Resultado final
    print("\n" + "="*80)
    print("🎉 DEPLOY CONCLUÍDO!")
    print("="*80)
    print("🌐 Landing Page: https://monpec-29862706245.us-central1.run.app/")
    print("🔐 Admin: https://monpec-29862706245.us-central1.run.app/admin/")
    print("📊 Dashboard: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/")
    print("📅 Planejamento: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/planejamento/")
    print("\n👤 LOGIN ADMIN:")
    print("Usuário: admin")
    print("Senha: [sua senha atual]")
    print("="*80)

if __name__ == "__main__":
    main()