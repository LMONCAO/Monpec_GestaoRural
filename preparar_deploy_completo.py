#!/usr/bin/env python
"""
SCRIPT PARA PREPARAR DEPLOY COMPLETO NO GOOGLE CLOUD
- Faz backup dos dados atuais
- Prepara dados para producao
- Configura URLs corretas
- Verifica landing page
"""
import os
import sys
import django
import json
from datetime import datetime
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import call_command
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from gestao_rural.models import Propriedade, PlanejamentoAnual, CenarioPlanejamento
from gestao_rural.models_funcionarios import Funcionario
from gestao_rural.models_compras_financeiro import Fornecedor

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def backup_dados_atuais():
    """Faz backup dos dados atuais"""
    print("[BACKUP] Fazendo backup dos dados atuais...")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backup_deploy_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)

    # Backup do banco SQLite
    import shutil
    shutil.copy('db.sqlite3', f'{backup_dir}/db.sqlite3')

    # Dados em JSON
    dados = {
        'timestamp': timestamp,
        'propriedades': list(Propriedade.objects.values()),
        'planejamentos': list(PlanejamentoAnual.objects.values()),
        'cenarios': list(CenarioPlanejamento.objects.values()),
        'funcionarios': list(Funcionario.objects.values()) if Funcionario.objects.exists() else [],
        'fornecedores': list(Fornecedor.objects.values()) if Fornecedor.objects.exists() else [],
        'usuarios': list(User.objects.values('id', 'username', 'email', 'is_superuser', 'date_joined')),
    }

    with open(f'{backup_dir}/dados_backup.json', 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)

    print(f"[OK] Backup criado em: {backup_dir}/")
    return backup_dir

def preparar_dados_producao():
    """Prepara dados específicos para produção"""
    print("[PRODUCAO] Preparando dados para producao...")

    # 1. Garantir que a propriedade admin tem dados completos
    try:
        propriedade_admin = Propriedade.objects.filter(
            produtor__usuario_responsavel__username='admin',
            nome_propriedade__icontains='Grande'
        ).first()

        if propriedade_admin:
            print(f"[OK] Propriedade admin encontrada: {propriedade_admin.nome_propriedade} (ID: {propriedade_admin.id})")

            # Executar comandos de popular dados
            print("[EXEC] Executando popular_fazenda_grande_demo...")
            call_command('popular_fazenda_grande_demo', propriedade_id=propriedade_admin.id, force=True, verbosity=1)

            print("[EXEC] Executando criar_planejamento_2026...")
            call_command('criar_planejamento_2026', propriedade_id=propriedade_admin.id, verbosity=1)

        else:
            print("[ERRO] Propriedade admin nao encontrada, criando uma...")
            admin_user = User.objects.get(username='admin')

            # Criar propriedade grande para admin
            propriedade_admin = Propriedade.objects.create(
                produtor=admin_user.produtor_rural if hasattr(admin_user, 'produtor_rural') else None,
                nome_propriedade='Fazenda Grande Demonstracao Producao',
                municipio='Campo Grande',
                uf='MS',
                area_total_ha=5000.00,
                tipo_operacao='PECUARIA',
                tipo_ciclo_pecuario=['CICLO_COMPLETO'],
                tipo_propriedade='PROPRIA',
                valor_hectare_proprio=12000.00
            )

            print(f"[OK] Propriedade criada: {propriedade_admin.nome_propriedade} (ID: {propriedade_admin.id})")

            # Popular com dados
            call_command('popular_fazenda_grande_demo', propriedade_id=propriedade_admin.id, force=True, verbosity=1)
            call_command('criar_planejamento_2026', propriedade_id=propriedade_admin.id, verbosity=1)

    except Exception as e:
        print(f"[ERRO] Erro ao preparar dados: {e}")
        return False

    return True

def verificar_landing_page():
    """Verifica se a landing page esta correta"""
    print("[VERIFICACAO] Verificando landing page...")

    try:
        from django.test import RequestFactory
        from django.urls import reverse
        from site.views import landing_page

        factory = RequestFactory()
        request = factory.get('/')
        response = landing_page(request)

        if response.status_code == 200:
            print("[OK] Landing page carregando corretamente")
            return True
        else:
            print(f"[ERRO] Erro na landing page: Status {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERRO] Erro ao verificar landing page: {e}")
        return False

def criar_script_deploy():
    """Cria script de deploy atualizado"""
    print("[SCRIPT] Criando script de deploy atualizado...")

    script_content = '''#!/bin/bash
# SCRIPT DE DEPLOY MONPEC - VERSÃO ATUALIZADA
# Execute no Google Cloud Shell

echo "🚀 Iniciando deploy MONPEC..."

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Build da imagem
echo "🔨 Fazendo build da imagem..."
gcloud builds submit . --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m

# Deploy do serviço
echo "🚀 Fazendo deploy..."
gcloud run deploy monpec \\
  --image gcr.io/monpec-sistema-rural/monpec:latest \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it,DEBUG=False" \\
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \\
  --memory=2Gi \\
  --cpu=2 \\
  --timeout=300 \\
  --max-instances=10 \\
  --min-instances=1 \\
  --port=8080

# Executar migrações
echo "🗄️ Executando migrações..."
gcloud run jobs create migrate-monpec-complete \\
  --image gcr.io/monpec-sistema-rural/monpec:latest \\
  --region us-central1 \\
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \\
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \\
  --command="python" \\
  --args="manage.py,migrate,--noinput" \\
  --memory=2Gi \\
  --cpu=1 \\
  --max-retries=3 \\
  --task-timeout=600

gcloud run jobs execute migrate-monpec-complete --region=us-central1 --wait

# Popular dados de produção
echo "📊 Populando dados de produção..."
gcloud run jobs create populate-monpec-data \\
  --image gcr.io/monpec-sistema-rural/monpec:latest \\
  --region us-central1 \\
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \\
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \\
  --command="python" \\
  --args="popular_dados_producao.py" \\
  --memory=2Gi \\
  --cpu=1 \\
  --max-retries=3 \\
  --task-timeout=600

gcloud run jobs execute populate-monpec-data --region=us-central1 --wait

# Verificar status
echo "✅ Verificando status..."
URL=$(gcloud run services describe monpec --region=us-central1 --format="value(status.url)")
echo "🌐 Serviço disponível em: $URL"

echo "🎉 Deploy concluído com sucesso!"
echo "📱 Landing page: $URL"
echo "🔐 Admin: $URL/admin/"
'''

    with open('deploy_atualizado.sh', 'w', encoding='utf-8') as f:
        f.write(script_content)

    print("[OK] Script de deploy criado: deploy_atualizado.sh")

def main():
    print("[DEPLOY] PREPARANDO DEPLOY COMPLETO MONPEC")
    print("=" * 50)

    # 1. Backup dos dados atuais
    backup_dir = backup_dados_atuais()

    # 2. Preparar dados para producao
    if preparar_dados_producao():
        print("[OK] Dados de producao preparados")
    else:
        print("[ERRO] Erro ao preparar dados de producao")
        return

    # 3. Verificar landing page
    if verificar_landing_page():
        print("[OK] Landing page verificada")
    else:
        print("[AVISO] Problema na landing page (continuando mesmo assim)")

    # 4. Criar script de deploy
    criar_script_deploy()

    print("\n" + "=" * 50)
    print("[SUCESSO] PREPARACAO CONCLUIDA!")
    print(f"[BACKUP] Backup salvo em: {backup_dir}/")
    print("[SCRIPT] Script de deploy: deploy_atualizado.sh")
    print("\n[PROXIMOS PASSOS]:")
    print("1. Faca upload do codigo para o Google Cloud")
    print("2. Execute: bash deploy_atualizado.sh")
    print("3. Verifique se a landing page esta correta")
    print("4. Teste o sistema com os dados populados")

if __name__ == '__main__':
    main()