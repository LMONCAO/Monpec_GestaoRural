# 🔧 Resumo das Correções Aplicadas - Sistema MONPEC

## Problema Identificado
O sistema estava retornando "Internal Server Error" no endereço `monpec.com.br`.

## Correções Aplicadas

### 1. ✅ Configuração do WSGI (`sistema_rural/wsgi.py`)
- **Problema**: O WSGI não estava detectando automaticamente o servidor de produção para usar `settings_producao`.
- **Solução**: Adicionada detecção automática baseada em:
  - Variável de ambiente `LOCAWEB_SERVER`
  - Hostname contendo `monpec.com.br`
  - Sistema operacional Linux (não Windows)

### 2. ✅ Configuração CSRF (`sistema_rural/settings_producao.py`)
- **Problema**: `CSRF_TRUSTED_ORIGINS` não incluía `http://monpec.com.br` (apenas HTTPS).
- **Solução**: Adicionados `http://monpec.com.br` e `http://www.monpec.com.br` para suportar acesso HTTP.

### 3. ✅ SECRET_KEY (`sistema_rural/settings_producao.py`)
- **Problema**: SECRET_KEY poderia não estar configurada, causando erro em produção.
- **Solução**: 
  - Adicionada leitura do arquivo `.env_producao`
  - Fallback para chave padrão se não encontrar (com aviso)
  - Verificação de SECRET_KEY válida antes de usar

## Arquivos Modificados

1. `sistema_rural/wsgi.py` - Detecção automática de ambiente de produção
2. `sistema_rural/settings_producao.py` - Correções de CSRF e SECRET_KEY

## Scripts Criados

1. `diagnosticar_erro_producao.py` - Script de diagnóstico completo
2. `CORRIGIR_SISTEMA_PRODUCAO.ps1` - Script PowerShell para correção automática

## Próximos Passos no Servidor

### 1. Executar Diagnóstico
```bash
python diagnosticar_erro_producao.py
```

### 2. Verificar Variáveis de Ambiente
Certifique-se de que as seguintes variáveis estão configuradas no servidor:
- `SECRET_KEY` - Chave secreta do Django
- `DB_NAME` - Nome do banco de dados
- `DB_USER` - Usuário do banco de dados
- `DB_PASSWORD` - Senha do banco de dados
- `DB_HOST` - Host do banco de dados
- `DB_PORT` - Porta do banco de dados

### 3. Aplicar Migrações
```bash
python manage.py migrate --settings=sistema_rural.settings_producao
```

### 4. Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
```

### 5. Verificar Configurações
```bash
python manage.py check --settings=sistema_rural.settings_producao --deploy
```

### 6. Reiniciar Servidor Web
Reinicie o servidor web (Apache/Nginx) ou o serviço Django:
```bash
# Exemplo para systemd
sudo systemctl restart gunicorn
# ou
sudo systemctl restart apache2
# ou
sudo systemctl restart nginx
```

## Verificação de Logs

Verifique os logs para identificar erros específicos:
- **Windows**: `logs/django.log`
- **Linux**: `/var/log/monpec/django.log`

## Configuração do Servidor Web

Certifique-se de que o servidor web está configurado para:
1. Usar `DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao`
2. Apontar para o arquivo `sistema_rural/wsgi.py`
3. Ter permissões corretas nos diretórios de static e media

## Exemplo de Configuração Apache (mod_wsgi)

```apache
<VirtualHost *:80>
    ServerName monpec.com.br
    ServerAlias www.monpec.com.br
    
    WSGIDaemonProcess monpec python-path=/caminho/para/projeto python-home=/caminho/para/venv
    WSGIProcessGroup monpec
    WSGIScriptAlias / /caminho/para/projeto/sistema_rural/wsgi.py
    
    <Directory /caminho/para/projeto/sistema_rural>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    
    Alias /static /var/www/monpec.com.br/static
    <Directory /var/www/monpec.com.br/static>
        Require all granted
    </Directory>
    
    Alias /media /var/www/monpec.com.br/media
    <Directory /var/www/monpec.com.br/media>
        Require all granted
    </Directory>
    
    # Definir variável de ambiente
    SetEnv DJANGO_SETTINGS_MODULE sistema_rural.settings_producao
</VirtualHost>
```

## Exemplo de Configuração Nginx + Gunicorn

### Gunicorn (systemd service)
```ini
[Unit]
Description=Gunicorn daemon for MONPEC
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/projeto
Environment="DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao"
ExecStart=/caminho/para/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock sistema_rural.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Nginx
```nginx
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br;
    
    location /static/ {
        alias /var/www/monpec.com.br/static/;
    }
    
    location /media/ {
        alias /var/www/monpec.com.br/media/;
    }
    
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Teste Final

Após aplicar todas as correções:
1. Acesse `http://monpec.com.br` no navegador
2. Verifique se a página carrega corretamente
3. Teste o login
4. Verifique os logs para garantir que não há erros

## Suporte

Se o problema persistir:
1. Execute `diagnosticar_erro_producao.py` e compartilhe a saída
2. Verifique os logs do servidor web e do Django
3. Verifique as permissões dos diretórios
4. Verifique a conexão com o banco de dados
















