#!/usr/bin/env python3
"""
SCRIPT COMPLETO DE DEPLOY MONPEC 2026
Inclui todos os dados criados: 1300 animais, planejamento, filtros funcionais

Este script executa todo o processo de deploy:
1. Build da imagem Docker
2. Push para Google Container Registry
3. Deploy no Cloud Run
4. Configuração das variáveis de ambiente
5. Verificações finais

Uso: python DEPLOY_MONPEC_COMPLETO_2026.py
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime


class DeployMonpec2026:
    """Deploy completo do Monpec com dados de 2026"""

    def __init__(self):
        # Configurações do Google Cloud
        self.project_id = "monpec-sistema-rural"  # Ajuste se necessário
        self.service_name = "monpec"
        self.region = "us-central1"
        self.db_password = "L6171r12@@jjms"  # Ajuste se necessário
        self.secret_key = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

        # Gera tag baseada na data/hora
        self.image_tag = datetime.now().strftime("v%Y%m%d_%H%M%S")
        self.image_name = f"gcr.io/{self.project_id}/{self.service_name}:{self.image_tag}"

    def run_command(self, command, description, critical=True):
        """Executa comando e retorna resultado"""
        print(f"🔄 {description}...")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                cwd=os.getcwd()
            )
            print(f"✅ {description} - OK")
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            if critical:
                print(f"❌ {description} - FALHOU")
                print(f"Erro: {e}")
                print(f"Output: {e.stdout}")
                print(f"Error: {e.stderr}")
                return False, e.stdout, e.stderr
            else:
                print(f"⚠️ {description} - Aviso (não crítico)")
                return True, e.stdout, e.stderr

    def check_prerequisites(self):
        """Verifica pré-requisitos"""
        print("🔍 Verificando pré-requisitos...")

        # Verificar se gcloud está instalado e configurado
        success, _, _ = self.run_command("gcloud --version", "Verificando gcloud CLI")
        if not success:
            print("❌ gcloud CLI não encontrado. Instale o Google Cloud SDK.")
            return False

        # Verificar se Docker está instalado
        success, _, _ = self.run_command("docker --version", "Verificando Docker")
        if not success:
            print("❌ Docker não encontrado.")
            return False

        # Verificar autenticação gcloud
        success, _, _ = self.run_command("gcloud auth list", "Verificando autenticação gcloud", critical=False)
        if not success:
            print("⚠️ Você pode precisar executar: gcloud auth login")

        # Configurar projeto
        success, _, _ = self.run_command(
            f"gcloud config set project {self.project_id}",
            "Configurando projeto gcloud"
        )
        if not success:
            return False

        print("✅ Pré-requisitos OK")
        return True

    def build_docker_image(self):
        """Build da imagem Docker"""
        print("🔨 Fazendo build da imagem Docker...")

        # Verificar se requirements_producao.txt existe
        if not Path("requirements_producao.txt").exists():
            print("📦 Criando requirements_producao.txt...")
            try:
                # Copiar requirements.txt para requirements_producao.txt se não existir
                if Path("requirements.txt").exists():
                    import shutil
                    shutil.copy("requirements.txt", "requirements_producao.txt")
                    print("✅ requirements_producao.txt criado")
                else:
                    print("❌ requirements.txt não encontrado")
                    return False
            except Exception as e:
                print(f"❌ Erro ao criar requirements_producao.txt: {e}")
                return False

        # Build da imagem
        command = f"docker build -t {self.image_name} ."
        success, _, _ = self.run_command(command, f"Build Docker (imagem: {self.image_name})")

        if success:
            print(f"✅ Imagem Docker criada: {self.image_name}")
        return success

    def push_to_gcr(self):
        """Push para Google Container Registry"""
        print("📤 Enviando imagem para GCR...")

        # Fazer login no GCR
        success, _, _ = self.run_command(
            f"gcloud auth configure-docker --quiet",
            "Configurando Docker para GCR"
        )
        if not success:
            return False

        # Push da imagem
        success, _, _ = self.run_command(
            f"docker push {self.image_name}",
            f"Push imagem para GCR ({self.image_name})"
        )

        if success:
            print(f"✅ Imagem enviada para GCR: {self.image_name}")
        return success

    def deploy_to_cloud_run(self):
        """Deploy no Cloud Run"""
        print("🚀 Fazendo deploy no Cloud Run...")

        # Comando completo de deploy
        deploy_command = (
            f"gcloud run deploy {self.service_name} "
            f"--image {self.image_name} "
            f"--region {self.region} "
            f"--platform managed "
            f"--allow-unauthenticated "
            f"--add-cloudsql-instances {self.project_id}:{self.region}:monpec-db "
            f"--set-env-vars "
            f"\"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,"
            f"DEBUG=False,"
            f"SECRET_KEY={self.secret_key},"
            f"CLOUD_SQL_CONNECTION_NAME={self.project_id}:{self.region}:monpec-db,"
            f"DB_NAME=monpec_db,"
            f"DB_USER=monpec_user,"
            f"DB_PASSWORD={self.db_password}\" "
            f"--memory 2Gi "
            f"--cpu 2 "
            f"--timeout 600"
        )

        success, _, _ = self.run_command(deploy_command, "Deploy Cloud Run")

        if success:
            print(f"✅ Deploy realizado com sucesso!")
            return True
        return False

    def get_service_url(self):
        """Obtém URL do serviço implantado"""
        print("🔗 Obtendo URL do serviço...")

        command = (
            f"gcloud run services describe {self.service_name} "
            f"--region {self.region} "
            f"--format=\"value(status.url)\""
        )

        success, stdout, _ = self.run_command(command, "Obter URL do serviço", critical=False)

        if success and stdout.strip():
            service_url = stdout.strip()
            print(f"✅ Serviço disponível em: {service_url}")
            print(f"📋 Login admin: admin / L6171r12@@")
            print(f"🎯 Propriedade principal: {service_url}/propriedade/5/pecuaria/")
            return service_url

        print("⚠️ Não foi possível obter a URL do serviço")
        return None

    def verify_deployment(self, service_url):
        """Verifica se o deploy funcionou"""
        if not service_url:
            return False

        print("🔍 Verificando deployment...")

        try:
            # Tentar acessar a home page
            response = requests.get(service_url, timeout=30)
            if response.status_code == 200:
                print("✅ Homepage acessível")

                # Verificar se landing page está correta
                if "MONPEC" in response.text.upper():
                    print("✅ Landing page MONPEC detectada")
                else:
                    print("⚠️ Landing page pode precisar ajustes")

                return True
            else:
                print(f"⚠️ Homepage retornou status {response.status_code}")
                return False

        except Exception as e:
            print(f"⚠️ Erro ao verificar deployment: {e}")
            return False

    def run_full_deploy(self):
        """Executa deploy completo"""
        print("🚀 DEPLOY MONPEC COMPLETO 2026")
        print("=" * 50)
        print("📊 Inclui: 1300 animais, planejamento estratégico, filtros funcionais")
        print("=" * 50)

        # Etapa 1: Verificar pré-requisitos
        if not self.check_prerequisites():
            print("❌ Falha nos pré-requisitos")
            return False

        # Etapa 2: Build da imagem
        if not self.build_docker_image():
            print("❌ Falha no build da imagem")
            return False

        # Etapa 3: Push para GCR
        if not self.push_to_gcr():
            print("❌ Falha no push para GCR")
            return False

        # Etapa 4: Deploy no Cloud Run
        if not self.deploy_to_cloud_run():
            print("❌ Falha no deploy")
            return False

        # Etapa 5: Obter URL e verificar
        service_url = self.get_service_url()

        if service_url and self.verify_deployment(service_url):
            print("\n" + "=" * 50)
            print("✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅")
            print("=" * 50)
            print(f"🔗 URL: {service_url}")
            print(f"👤 Login: admin / L6171r12@@")
            print(f"🏭 Demo: {service_url}/propriedade/5/pecuaria/")
            print(f"📊 Planejamento: {service_url}/propriedade/5/pecuaria/planejamento/")
            print("=" * 50)
            return True
        else:
            print("❌ Deploy concluído mas verificação falhou")
            return False


def main():
    """Função principal"""
    deploy = DeployMonpec2026()

    try:
        success = deploy.run_full_deploy()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Deploy interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()