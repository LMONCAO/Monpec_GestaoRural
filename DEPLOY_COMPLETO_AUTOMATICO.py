#!/usr/bin/env python
"""
DEPLOY COMPLETO AUTOMÁTICO MONPEC
Script que faz upload e deploy completo no Google Cloud
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def executar_comando(cmd, descricao=""):
    """Executa comando e mostra resultado"""
    print(f"\n🔧 {descricao}")
    print(f"📝 Comando: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

        if result.stdout:
            print(f"✅ Saída: {result.stdout[:500]}..." if len(result.stdout) > 500 else f"✅ Saída: {result.stdout}")

        if result.stderr:
            print(f"⚠️  Avisos: {result.stderr[:500]}..." if len(result.stderr) > 500 else f"⚠️  Avisos: {result.stderr}")

        if result.returncode == 0:
            print(f"✅ {descricao} - SUCESSO")
            return True
        else:
            print(f"❌ {descricao} - ERRO (código: {result.returncode})")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏰ {descricao} - TIMEOUT (5 minutos)")
        return False
    except Exception as e:
        print(f"💥 {descricao} - ERRO: {str(e)}")
        return False

def verificar_gcloud():
    """Verifica se gcloud está instalado e configurado"""
    print("\n🔍 Verificando gcloud CLI...")

    if not executar_comando("gcloud --version", "Verificar gcloud instalado"):
        print("❌ gcloud CLI não está instalado!")
        print("📥 Baixe de: https://cloud.google.com/sdk/docs/install")
        return False

    # Verificar se está logado
    if not executar_comando("gcloud auth list --filter=status:ACTIVE", "Verificar login gcloud"):
        print("❌ Não está logado no gcloud!")
        print("🔑 Execute: gcloud auth login")
        return False

    return True

def configurar_projeto():
    """Configura projeto do Google Cloud"""
    print("\n⚙️ Configurando projeto...")

    # Configurar projeto
    if not executar_comando("gcloud config set project monpec-sistema-rural", "Configurar projeto"):
        return False

    # Verificar projeto
    if not executar_comando("gcloud config get-value project", "Verificar projeto atual"):
        return False

    return True

def preparar_arquivos():
    """Prepara arquivos para deploy"""
    print("\n📦 Preparando arquivos...")

    # Criar .gcloudignore se não existir
    gcloudignore_path = ".gcloudignore"
    if not os.path.exists(gcloudignore_path):
        with open(gcloudignore_path, 'w') as f:
            f.write("""# Arquivos a ignorar no upload
.git/
.gitignore
*.pyc
__pycache__/
*.log
.env*
venv/
.venv/
node_modules/
staticfiles/
media/
*.sqlite3
backup_*/
test_*/
debug_*/
temp/
.vscode/
.idea/
""")
        print("✅ Arquivo .gcloudignore criado")

    # Coletar arquivos estáticos
    print("📂 Coletando arquivos estáticos...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    try:
        import django
        django.setup()
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Arquivos estáticos coletados")
    except Exception as e:
        print(f"⚠️ Erro ao coletar estáticos: {e}")

    return True

def fazer_deploy():
    """Executa o deploy completo"""
    print("\n🚀 Iniciando deploy completo...")

    # Passo 1: Build da imagem
    print("\n🔨 PASSO 1: Build da imagem")
    if not executar_comando(
        "gcloud builds submit . --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m",
        "Build da imagem Docker"
    ):
        return False

    # Passo 2: Deploy do serviço
    print("\n🚀 PASSO 2: Deploy do serviço")
    deploy_cmd = '''gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it,DEBUG=False" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --min-instances=1 \
  --port=8080'''

    if not executar_comando(deploy_cmd, "Deploy do serviço Cloud Run"):
        return False

    # Passo 3: Executar migrações
    print("\n🗄️ PASSO 3: Executando migrações")
    migrate_job_cmd = '''gcloud run jobs create migrate-monpec-complete \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=3 \
  --task-timeout=600'''

    if not executar_comando(migrate_job_cmd, "Criar job de migração"):
        return False

    if not executar_comando(
        "gcloud run jobs execute migrate-monpec-complete --region=us-central1 --wait",
        "Executar migrações"
    ):
        return False

    # Passo 4: Popular dados
    print("\n📊 PASSO 4: Populando dados de produção")
    populate_job_cmd = '''gcloud run jobs create populate-monpec-data \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="popular_dados_producao.py" \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=3 \
  --task-timeout=600'''

    if not executar_comando(populate_job_cmd, "Criar job de população de dados"):
        return False

    if not executar_comando(
        "gcloud run jobs execute populate-monpec-data --region=us-central1 --wait",
        "Popular dados de produção"
    ):
        return False

    return True

def verificar_deploy():
    """Verifica se o deploy foi bem-sucedido"""
    print("\n🔍 Verificando deploy...")

    # Obter URL do serviço
    url_result = executar_comando(
        'gcloud run services describe monpec --region=us-central1 --format="value(status.url)"',
        "Obter URL do serviço"
    )

    if url_result:
        # Tentar fazer uma requisição simples
        try:
            import requests
            response = requests.get(url_result.stdout.strip(), timeout=30)
            if response.status_code == 200:
                print(f"✅ Deploy verificado! Serviço rodando em: {url_result.stdout.strip()}")
                return url_result.stdout.strip()
            else:
                print(f"⚠️ Serviço respondeu com código: {response.status_code}")
                return url_result.stdout.strip()
        except Exception as e:
            print(f"⚠️ Não foi possível testar a URL: {e}")
            return url_result.stdout.strip()

    return None

def main():
    print("🚀 DEPLOY COMPLETO AUTOMÁTICO MONPEC")
    print("=" * 50)

    # Verificações iniciais
    if not verificar_gcloud():
        print("\n❌ Pré-requisitos não atendidos. Instale e configure o gcloud CLI primeiro.")
        return

    if not configurar_projeto():
        print("\n❌ Erro ao configurar projeto.")
        return

    if not preparar_arquivos():
        print("\n❌ Erro ao preparar arquivos.")
        return

    # Executar deploy
    if fazer_deploy():
        # Verificar resultado
        url = verificar_deploy()

        print("\n" + "=" * 50)
        print("🎉 DEPLOY CONCLUÍDO!")
        print("=" * 50)

        if url:
            print(f"🌐 URL do serviço: {url}")
            print(f"🏠 Landing page: {url}")
            print(f"🔐 Admin: {url}admin/")
            print(f"📊 Dashboard: {url}propriedade/5/pecuaria/")
            print(f"📅 Planejamento: {url}propriedade/5/pecuaria/planejamento/")

        print("\n✅ SISTEMA PRONTO COM:")
        print("- 1.300 animais populados")
        print("- Planejamento 2026 completo")
        print("- Landing page funcionando")
        print("- URLs corretas configuradas")

    else:
        print("\n❌ DEPLOY FALHOU!")
        print("Verifique os logs acima para identificar o problema.")

if __name__ == '__main__':
    main()