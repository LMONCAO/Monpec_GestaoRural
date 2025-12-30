#!/bin/bash
# Comando que garante executar no diretório correto
# Execute: bash COMANDO_COM_DIRETORIO_CORRETO.sh

echo "=== COMANDO COM DIREÓRIO CORRETO GARANTIDO ==="
echo ""
echo "Este comando garante que os comandos executem no diretório /app"
echo "onde o manage.py está localizado no container"
echo ""
echo "Copie e cole este comando COMPLETO no Cloud Shell:"
echo ""
echo "---"
echo ""

cat <<'COMMAND'
gcloud builds submit --config <(cat <<'EOF'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    cd /app && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
EOF
) .
COMMAND

echo ""
echo "---"
echo ""
echo "✅ A diferença é que adicionei 'cd /app &&' no início"
echo "   Isso garante que estamos no diretório correto onde o manage.py está"
echo ""
echo "💡 IMPORTANTE: Antes de executar, certifique-se de estar no diretório"
echo "   do projeto no Cloud Shell. Execute:"
echo "   cd ~/Monpec_GestaoRural"
echo "   (ou o caminho onde está seu projeto)"

