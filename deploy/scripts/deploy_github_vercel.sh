#!/bin/bash

echo "🚀 CONFIGURANDO DEPLOY COM GITHUB + VERCEL"
echo "=========================================="

# Criar arquivo de configuração para Vercel
echo "📝 Criando vercel.json..."
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "sistema_rural.settings"
  }
}
EOF

# Criar arquivo requirements.txt para Vercel
echo "📝 Criando requirements.txt para Vercel..."
cat > requirements_vercel.txt << 'EOF'
Django==4.2.7
django-crispy-forms==2.0
crispy-bootstrap5==0.7
Pillow==10.1.0
python-decouple==3.8
gunicorn==21.2.0
EOF

# Criar arquivo .gitignore
echo "📝 Criando .gitignore..."
cat > .gitignore << 'EOF'
# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local
.env.production

# Vercel
.vercel
EOF

echo ""
echo "✅ ARQUIVOS DE CONFIGURAÇÃO CRIADOS!"
echo "===================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Fazer commit dos arquivos para o GitHub"
echo "2. Conectar o repositório ao Vercel"
echo "3. Configurar o domínio monpec.com.br"
echo "4. Fazer deploy automático"
echo ""
echo "🌐 O sistema será acessível em: https://monpec.com.br"


