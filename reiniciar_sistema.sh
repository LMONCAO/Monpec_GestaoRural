#!/bin/bash

echo "🔄 REINICIANDO SISTEMA RURAL"
echo "=============================="

# Parar serviços
echo "⏹️ Parando serviços..."
systemctl stop sistema-rural
systemctl stop nginx

# Aguardar um momento
sleep 2

# Remover socket antigo se existir
echo "🗑️ Removendo socket antigo..."
rm -f /home/django/sistema-rural/sistema_rural.sock

# Verificar permissões
echo "🔐 Verificando permissões..."
chown -R django:www-data /home/django/sistema-rural/
chmod -R 755 /home/django/sistema-rural/

# Iniciar Gunicorn
echo "🚀 Iniciando Gunicorn..."
systemctl start sistema-rural

# Aguardar inicialização
sleep 3

# Iniciar Nginx
echo "🌐 Iniciando Nginx..."
systemctl start nginx

# Verificar status
echo "📊 Verificando status dos serviços..."
systemctl status sistema-rural --no-pager -l
echo ""
systemctl status nginx --no-pager -l

# Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost

echo ""
echo "✅ REINICIALIZAÇÃO CONCLUÍDA!"
echo "=============================="
echo "Acesse: http://45.32.219.76"


