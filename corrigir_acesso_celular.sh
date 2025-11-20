#!/bin/bash

echo "📱 CORRIGINDO ACESSO PELO CELULAR"
echo "=================================="
echo ""

# Verificar IP do servidor
echo "1️⃣ Verificando IP do servidor..."
IP_LOCAL=$(hostname -I | awk '{print $1}')
IP_PUBLICO=$(curl -s ifconfig.me 2>/dev/null || echo "Não disponível")

echo "   IP Local: $IP_LOCAL"
echo "   IP Público: $IP_PUBLICO"
echo ""

# Verificar se está no diretório correto
if [ ! -f "sistema_rural/settings_producao.py" ]; then
    echo "❌ Erro: Arquivo settings_producao.py não encontrado!"
    echo "   Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Fazer backup
echo "2️⃣ Fazendo backup do settings_producao.py..."
cp sistema_rural/settings_producao.py sistema_rural/settings_producao.py.backup
echo "   ✅ Backup criado: settings_producao.py.backup"
echo ""

# Corrigir settings_producao.py
echo "3️⃣ Corrigindo settings_producao.py..."

# Criar arquivo temporário com as correções
cat > /tmp/settings_correcoes.py << 'PYTHON_EOF'
# Correções para acesso pelo celular:
# 1. Desabilitar SSL redirect temporariamente
# 2. Adicionar 0.0.0.0 ao ALLOWED_HOSTS
# 3. Adicionar IP ao CSRF_TRUSTED_ORIGINS
# 4. Desabilitar cookies seguros temporariamente
PYTHON_EOF

# Usar Python para fazer as correções
python3 << 'PYTHON_SCRIPT'
import re
import sys

# Ler arquivo
with open('sistema_rural/settings_producao.py', 'r') as f:
    content = f.read()

# Obter IP local
import subprocess
try:
    ip_local = subprocess.check_output(['hostname', '-I']).decode().strip().split()[0]
except:
    ip_local = None

# 1. Desabilitar SECURE_SSL_REDIRECT
content = re.sub(
    r'SECURE_SSL_REDIRECT = True',
    r'SECURE_SSL_REDIRECT = False  # Desabilitado para acesso pelo celular',
    content
)

# 2. Adicionar 0.0.0.0 ao ALLOWED_HOSTS se não existir
if "'0.0.0.0'" not in content and '"0.0.0.0"' not in content:
    # Encontrar ALLOWED_HOSTS e adicionar
    content = re.sub(
        r'(ALLOWED_HOSTS = \[)',
        r'\1\n    \'0.0.0.0\',  # Permite acesso de qualquer IP',
        content
    )

# 3. Adicionar IP local ao ALLOWED_HOSTS se disponível
if ip_local and ip_local not in content:
    content = re.sub(
        r'(ALLOWED_HOSTS = \[)',
        f'\\1\n    \'{ip_local}\',  # IP local do servidor',
        content
    )

# 4. Adicionar IP ao CSRF_TRUSTED_ORIGINS
if ip_local:
    csrf_line = f"    'http://{ip_local}:8000',  # IP local para acesso pelo celular"
    if csrf_line not in content:
        content = re.sub(
            r'(CSRF_TRUSTED_ORIGINS = \[)',
            f'\\1\n{csrf_line}',
            content
        )

# 5. Desabilitar cookies seguros
content = re.sub(
    r'SESSION_COOKIE_SECURE = True',
    r'SESSION_COOKIE_SECURE = False  # Desabilitado para acesso HTTP',
    content
)

content = re.sub(
    r'CSRF_COOKIE_SECURE = True',
    r'CSRF_COOKIE_SECURE = False  # Desabilitado para acesso HTTP',
    content
)

# Salvar arquivo
with open('sistema_rural/settings_producao.py', 'w') as f:
    f.write(content)

print("✅ Arquivo settings_producao.py corrigido!")
if ip_local:
    print(f"✅ IP local adicionado: {ip_local}")
PYTHON_SCRIPT

echo "   ✅ Correções aplicadas!"
echo ""

# Verificar firewall
echo "4️⃣ Verificando firewall..."
if command -v ufw &> /dev/null; then
    echo "   Verificando regras do UFW..."
    if ! ufw status | grep -q "8000/tcp"; then
        echo "   ⚠️  Porta 8000 não está permitida no firewall"
        echo "   Executando: sudo ufw allow 8000/tcp"
        sudo ufw allow 8000/tcp 2>/dev/null || echo "   ⚠️  Execute manualmente: sudo ufw allow 8000/tcp"
    else
        echo "   ✅ Porta 8000 já está permitida"
    fi
else
    echo "   ⚠️  UFW não encontrado. Verifique o firewall manualmente."
fi
echo ""

# Verificar se há servidor rodando
echo "5️⃣ Verificando servidor Django..."
if pgrep -f "python.*manage.py runserver" > /dev/null; then
    echo "   ⚠️  Servidor Django já está rodando"
    echo "   Verifique se está escutando em 0.0.0.0:8000"
    netstat -tlnp 2>/dev/null | grep :8000 || ss -tlnp 2>/dev/null | grep :8000 || echo "   Não foi possível verificar portas"
else
    echo "   ℹ️  Servidor Django não está rodando"
    echo "   Para iniciar, execute:"
    echo "   python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao"
fi
echo ""

# Resumo
echo "✅ CORREÇÕES APLICADAS!"
echo "======================"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. Reinicie o servidor Django:"
echo "   python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao"
echo ""
if [ -n "$IP_LOCAL" ]; then
    echo "2. No celular, acesse:"
    echo "   http://$IP_LOCAL:8000"
    echo ""
fi
if [ -n "$IP_PUBLICO" ] && [ "$IP_PUBLICO" != "Não disponível" ]; then
    echo "   Ou pelo IP público:"
    echo "   http://$IP_PUBLICO:8000"
    echo ""
fi
echo "3. Se não funcionar, verifique:"
echo "   - Firewall do servidor"
echo "   - Firewall do roteador (se na mesma rede)"
echo "   - Se o celular está na mesma rede Wi-Fi"
echo ""
echo "📄 Backup salvo em: sistema_rural/settings_producao.py.backup"
echo ""







