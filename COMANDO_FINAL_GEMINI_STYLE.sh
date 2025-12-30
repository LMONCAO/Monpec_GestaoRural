#!/bin/bash
# Comando final estilo Gemini - Tudo de uma vez
# Execute: bash COMANDO_FINAL_GEMINI_STYLE.sh
# OU copie e cole o comando gcloud builds submit diretamente no terminal

echo "=== COMANDO FINAL: MIGRATE + COLLECTSTATIC + CRIAR ADMIN ==="
echo ""
echo "Agora que você está autenticado, este comando deve funcionar!"
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
echo "✅ Este comando vai:"
echo "   1. Executar migrate (criar tabelas do banco)"
echo "   2. Executar collectstatic (organizar arquivos JavaScript dos slides)"
echo "   3. Criar usuário admin (usuário: admin, senha: L6171r12@@)"
echo ""
echo "⏱️ Aguarde 3-5 minutos até ver STATUS: SUCCESS"
echo ""
echo "💡 DICA: Se este comando falhar, use a solução alternativa com Cloud Run Jobs"
echo "   (veja o arquivo COMANDOS_PARA_GOOGLE_CLOUD_SHELL.md)"

