#!/usr/bin/env python3
"""
DEPLOY DIRETO NO GOOGLE CLOUD - MONPEC
Script simples e direto para fazer deploy usando suas configurações existentes
"""
import os
import sys
import subprocess
import time


def run_command(cmd, description):
    """Executa comando e mostra resultado"""
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
    """Deploy direto"""
    print("🚀 DEPLOY DIRETO MONPEC NO GOOGLE CLOUD")
    print("=" * 50)

    # Verificar se tem configurações
    if not os.path.exists('.env_gcp'):
        print("❌ Arquivo .env_gcp não encontrado!")
        print("Configure suas credenciais primeiro.")
        return

    # 1. Configurar projeto
    print("1. Configurando projeto...")
    success, _ = run_command(
        "gcloud config set project monpec-29862706245",
        "Configurando projeto monpec-29862706245"
    )
    if not success:
        return

    # 2. Configurar região
    success, _ = run_command(
        "gcloud config set compute/region us-central1",
        "Configurando região us-central1"
    )
    if not success:
        return

    # 3. Build da imagem
    print("2. Fazendo build da imagem...")
    success, _ = run_command(
        "docker build -t gcr.io/monpec-29862706245/monpec:latest .",
        "Build da imagem Docker"
    )
    if not success:
        return

    # 4. Push para GCR
    print("3. Enviando imagem para Google Container Registry...")
    success, _ = run_command(
        "docker push gcr.io/monpec-29862706245/monpec:latest",
        "Push da imagem para GCR"
    )
    if not success:
        return

    # 5. Deploy no Cloud Run
    print("4. Fazendo deploy no Cloud Run...")
    deploy_cmd = """
    gcloud run deploy monpec \
      --image gcr.io/monpec-29862706245/monpec:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
      --memory 1Gi \
      --cpu 1 \
      --max-instances 10 \
      --timeout 300 \
      --concurrency 80
    """

    success, output = run_command(deploy_cmd, "Deploy no Cloud Run")

    if success:
        # Extrair URL
        for line in output.split('\n'):
            if 'https://' in line and 'monpec' in line:
                url = line.strip()
                break
        else:
            url = "Verifique no Google Cloud Console"

        print("\n" + "=" * 50)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        print(f"🌐 URL do serviço: {url}")
        print("🔍 Health Check: [URL]/health/")
        print("👤 Admin: admin@monpec.com.br / L6171r12@@jjms")
        print("\n📊 Para monitorar:")
        print("gcloud run services describe monpec --region=us-central1")
        print("gcloud logging read --filter='resource.labels.service_name=monpec' --limit=5")
    else:
        print("\n❌ DEPLOY FALHOU!")
        print("Verifique os logs acima para detalhes.")


if __name__ == "__main__":
    main()