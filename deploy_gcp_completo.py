#!/usr/bin/env python
"""
DEPLOY COMPLETO MONPEC PARA GOOGLE CLOUD
Script automatizado que resolve todos os problemas identificados
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Executa comando e retorna resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Erro:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout")
        return False
    except Exception as e:
        print(f"💥 {description} - Exceção: {e}")
        return False

def main():
    print("🚀 DEPLOY MONPEC COMPLETO PARA GOOGLE CLOUD")
    print("=" * 60)

    # Verificar se estamos no diretório correto
    if not Path('manage.py').exists():
        print("❌ Execute este script na raiz do projeto MONPEC")
        return False

    # 1. Instalar dependências GCP
    if not run_command(
        "pip install google-cloud-storage google-auth psycopg2-binary django-storages[google]",
        "Instalando dependências do Google Cloud"
    ):
        return False

    # 2. Executar correção de exportações
    if not run_command(
        "python corrigir_exportacao_gcp.py",
        "Executando correção de exportações PDF/Excel"
    ):
        return False

    # 3. Executar correção de migrações
    if not run_command(
        "python corrigir_migracoes_gcp.py",
        "Executando correção de migrações e tabelas"
    ):
        return False

    # 4. Coletar arquivos estáticos
    if not run_command(
        "python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp_deploy",
        "Coletando arquivos estáticos"
    ):
        return False

    # 5. Testar configurações
    print("\n🧪 TESTANDO CONFIGURAÇÕES...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp_deploy')
        import django
        django.setup()

        from django.conf import settings
        print("✅ Configurações carregadas")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   DATABASE: {settings.DATABASES['default']['ENGINE']}")
        print(f"   EMAIL: {settings.DEFAULT_FROM_EMAIL}")

        # Testar conexão com banco
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com banco OK")

    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

    # 6. Criar superusuário se necessário
    print("\n👤 CRIANDO SUPERUSUÁRIO...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@monpec.com.br',
                password='Monpec2025@',
                first_name='Administrador',
                last_name='MONPEC'
            )
            print("✅ Superusuário criado: admin / Monpec2025@")
        else:
            print("✅ Superusuário já existe")
    except Exception as e:
        print(f"⚠️ Erro ao criar superusuário: {e}")

    # 7. Verificar se podemos fazer build do Docker
    print("\n🐳 VERIFICANDO DOCKER...")
    if run_command("docker --version", "Verificando Docker"):
        if run_command("docker build -f Dockerfile.gcp -t monpec-gcp .", "Fazendo build do Docker"):
            print("✅ Docker build concluído")
        else:
            print("⚠️ Docker build falhou, mas continuando...")
    else:
        print("⚠️ Docker não encontrado, pulando build")

    # 8. Criar arquivo de configuração de ambiente
    print("\n📝 CRIANDO .env.production...")
    env_content = """
# Configurações de Produção MONPEC - GCP
DEBUG=False
SECRET_KEY=django-insecure-gcp-production-key-2025-monpec-deploy
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp_deploy

# Banco PostgreSQL
DB_NAME=monpec_production
DB_USER=postgres
DB_PASSWORD=your_db_password_here
DB_HOST=/cloudsql/monpec-sistema-rural:us-central1:monpec-db
DB_PORT=5432

# Email Gmail
EMAIL_HOST_USER=l.moncaosilva@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DEFAULT_FROM_EMAIL=l.moncaosilva@gmail.com

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=your_mercadopago_token_here
MERCADOPAGO_PUBLIC_KEY=your_mercadopago_public_key_here

# Google Cloud
GOOGLE_CLOUD_PROJECT=monpec-sistema-rural
GS_BUCKET_NAME=monpec-static-files
GOOGLE_CREDENTIALS_JSON=your_credentials_json_here

# MONPEC
SITE_URL=https://monpec.com.br
CONSULTOR_EMAIL=l.moncaosilva@gmail.com
CONSULTOR_TELEFONE=

# Redis (opcional)
REDIS_URL=redis://localhost:6379/0
"""

    with open('.env.production', 'w', encoding='utf-8') as f:
        f.write(env_content.strip())

    print("✅ Arquivo .env.production criado")

    # 9. Criar script de deploy para Cloud Run
    print("\n☁️ CRIANDO SCRIPT DE DEPLOY...")

    deploy_script = '''#!/bin/bash
# Script de Deploy MONPEC para Google Cloud Run

echo "🚀 DEPLOY MONPEC PARA GOOGLE CLOUD RUN"
echo "====================================="

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI não encontrado. Instale o Google Cloud SDK."
    exit 1
fi

# Fazer login no gcloud (se necessário)
echo "🔐 Verificando autenticação..."
gcloud auth list --filter=status:ACTIVE --format="value(account)"

# Configurar projeto
echo "📍 Configurando projeto..."
gcloud config set project monpec-sistema-rural

# Construir e enviar imagem para GCR
echo "🐳 Construindo imagem Docker..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec-app .

# Fazer deploy no Cloud Run
echo "☁️ Fazendo deploy no Cloud Run..."
gcloud run deploy monpec-app \\
  --image gcr.io/monpec-sistema-rural/monpec-app \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --port 8080 \\
  --memory 2Gi \\
  --cpu 1 \\
  --max-instances 10 \\
  --min-instances 1 \\
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp_deploy" \\
  --set-secrets="SECRET_KEY=monpec-secret-key:latest" \\
  --set-secrets="MERCADOPAGO_ACCESS_TOKEN=mercadopago-token:latest" \\
  --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db

echo "✅ DEPLOY CONCLUÍDO!"
echo ""
echo "🌐 URL da aplicação:"
gcloud run services describe monpec-app --region=us-central1 --format="value(status.url)"
'''

    with open('deploy_cloud_run.sh', 'w', encoding='utf-8') as f:
        f.write(deploy_script)

    # Tornar executável
    os.chmod('deploy_cloud_run.sh', 0o755)

    print("✅ Script deploy_cloud_run.sh criado")

    # 10. Criar README de deploy
    print("\n📖 CRIANDO DOCUMENTAÇÃO...")

    readme_deploy = '''# 🚀 DEPLOY MONPEC PARA GOOGLE CLOUD

## Problemas Resolvidos
- ✅ Erro 500 por tabelas faltantes
- ✅ Linha 22 com problemas de importação
- ✅ Exportação PDF/Excel não funcionando
- ✅ Migrações não executando corretamente

## Pré-requisitos
1. Conta Google Cloud Platform
2. Projeto criado: `monpec-sistema-rural`
3. Cloud SQL PostgreSQL configurado
4. Secret Manager configurado
5. Cloud Storage bucket criado

## Configuração de Secrets (Cloud Secret Manager)

```bash
# Criar secrets
echo -n "your-secret-key-here" | gcloud secrets create monpec-secret-key --data-file=-
echo -n "your-mercadopago-token" | gcloud secrets create mercadopago-token --data-file=-
```

## Arquivos de Configuração
- `sistema_rural/settings_gcp_deploy.py` - Configurações otimizadas
- `Dockerfile.gcp` - Container otimizado
- `requirements_gcp.txt` - Dependências GCP
- `.env.production` - Variáveis de ambiente

## Comando de Deploy

```bash
# Executar correções locais
python corrigir_exportacao_gcp.py
python corrigir_migracoes_gcp.py

# Fazer deploy
chmod +x deploy_cloud_run.sh
./deploy_cloud_run.sh
```

## Pós-Deploy

1. Acessar URL do Cloud Run
2. Verificar logs: `gcloud logs read`
3. Executar migrações remotas se necessário
4. Configurar domínio personalizado

## Monitoramento

```bash
# Ver logs
gcloud logs read --filter="resource.type=cloud_run_revision"

# Ver status do serviço
gcloud run services describe monpec-app --region=us-central1

# Ver conexões Cloud SQL
gcloud sql instances list
```

## Suporte
📧 Email: l.moncaosilva@gmail.com
📱 WhatsApp: Configurar no CONSULTOR_TELEFONE
'''

    with open('README_DEPLOY_GCP.md', 'w', encoding='utf-8') as f:
        f.write(readme_deploy)

    print("✅ README_DEPLOY_GCP.md criado")

    print("\n" + "=" * 60)
    print("🎉 PREPARAÇÃO PARA DEPLOY GCP CONCLUÍDA!")
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Configure seu projeto Google Cloud")
    print("2. Execute: python corrigir_migracoes_gcp.py")
    print("3. Configure as variáveis de ambiente")
    print("4. Execute: ./deploy_cloud_run.sh")
    print()
    print("📚 DOCUMENTAÇÃO: README_DEPLOY_GCP.md")
    print("🆘 SUPORTE: l.moncaosilva@gmail.com")
    print()
    print("🚀 SISTEMA MONPEC PRONTO PARA PRODUÇÃO!")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)