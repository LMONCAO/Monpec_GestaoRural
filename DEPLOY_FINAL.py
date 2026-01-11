#!/usr/bin/env python3
"""
DEPLOY FINAL MONPEC - COM CREDENCIAIS CORRETAS
"""
import os
import sys
import subprocess


def run_command(cmd, description):
    """Executa comando"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - OK")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FALHOU")
        print(f"Erro: {e.stderr}")
        return False, e.stderr


def main():
    """Deploy final com credenciais corretas"""
    print("🚀 DEPLOY FINAL MONPEC NO GOOGLE CLOUD")
    print("=" * 50)
    print("Credenciais confirmadas:")
    print("- Banco: monpec-db")
    print("- Senha: L6171r12@@jjms")
    print()

    # Configurar projeto
    success, _ = run_command(
        "gcloud config set project monpec-sistema-rural",
        "Configurando projeto monpec-sistema-rural"
    )
    if not success:
        return

    # Build da imagem
    success, _ = run_command(
        "docker build -t gcr.io/monpec-sistema-rural/monpec:latest .",
        "Build da imagem Docker"
    )
    if not success:
        return

    # Push para registry
    success, _ = run_command(
        "docker push gcr.io/monpec-sistema-rural/monpec:latest",
        "Push da imagem para GCR"
    )
    if not success:
        return

    # Deploy com credenciais corretas
    deploy_cmd = '''
    gcloud run deploy monpec \
      --image gcr.io/monpec-sistema-rural/monpec:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
      --set-env-vars "DB_NAME=monpec-db" \
      --set-env-vars "DB_USER=postgres" \
      --set-env-vars "DB_PASSWORD=L6171r12@@jjms" \
      --set-env-vars "DB_HOST=/cloudsql/monpec-sistema-rural:us-central1:monpec-db" \
      --memory 1Gi \
      --cpu 1 \
      --max-instances 10 \
      --timeout 300 \
      --concurrency 80
    '''

    success, output = run_command(deploy_cmd, "Deploy final no Cloud Run")

    if success:
        print("\n" + "=" * 50)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("=" * 50)

        # Extrair URL
        for line in output.split('\n'):
            if 'https://' in line and 'monpec' in line:
                url = line.strip()
                print(f"🌐 URL do serviço: {url}")
                print(f"🔍 Health Check: {url}/health/")
                break
        else:
            print("🌐 Verifique a URL no Google Cloud Console")

        print("👤 Login admin: admin@monpec.com.br / L6171r12@@jjms")
        print("\n📊 Monitoramento:")
        print("gcloud run services describe monpec --region=us-central1")
        print("gcloud logging read --filter='resource.labels.service_name=monpec' --limit=5")
    else:
        print("\n❌ DEPLOY FALHOU!")
        print("Verifique os logs e credenciais.")


if __name__ == "__main__":
    main()