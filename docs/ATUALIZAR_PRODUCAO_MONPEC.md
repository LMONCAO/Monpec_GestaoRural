# Atualização do Site MONPEC em Produção (monpec.com.br)

## Problemas Corrigidos

### 1. ✅ Menu Mobile (Estilo Gerbov)
- Menu hambúrguer funcional
- Menu em tela cheia no mobile
- Botão X para fechar
- Fecha ao clicar em links ou fora do menu

### 2. ✅ Carregamento de Imagens
- Caminhos das imagens verificados
- JavaScript do slideshow ajustado
- Tratamento de erros melhorado

### 3. ✅ Formulário de Demonstração
- Mensagens de erro mais específicas
- Tratamento de exceções melhorado

### 4. ✅ Usuário Admin
- Script criado para criar/corrigir usuário admin

## Passos para Atualizar em Produção

### 1. Fazer Upload dos Arquivos Atualizados

```bash
# Arquivos que foram modificados:
# - templates/site/landing_page.html
# - gestao_rural/views.py
# - criar_admin_fix.py (novo arquivo)
```

### 2. Coletar Arquivos Estáticos

```bash
# No servidor de produção
cd /var/www/monpec.com.br  # ou caminho do seu projeto
source venv/bin/activate  # se usar virtualenv
python manage.py collectstatic --noinput
```

### 3. Criar/Corrigir Usuário Admin

```bash
# No servidor de produção
python criar_admin_fix.py
```

Isso criará o usuário `admin` com:
- Usuário: `admin`
- Senha: `L6171r12@@`
- Email: `admin@monpec.com.br`

### 4. Reiniciar o Servidor

```bash
# Se usar systemd
sudo systemctl restart gunicorn
# ou
sudo systemctl restart monpec

# Se usar supervisor
sudo supervisorctl restart monpec

# Se usar manualmente
# Parar o processo atual e iniciar novamente
```

### 5. Verificar Permissões dos Arquivos Estáticos

```bash
# Garantir que o servidor web tem acesso aos arquivos estáticos
sudo chown -R www-data:www-data /var/www/monpec.com.br/static
sudo chmod -R 755 /var/www/monpec.com.br/static

# Verificar se as imagens existem
ls -la /var/www/monpec.com.br/static/site/foto*.jpeg
```

### 6. Verificar Configuração do Nginx/Apache

Se usar Nginx, verificar se está servindo arquivos estáticos:

```nginx
location /static/ {
    alias /var/www/monpec.com.br/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

Se usar Apache, verificar se está servindo arquivos estáticos:

```apache
Alias /static /var/www/monpec.com.br/static
<Directory /var/www/monpec.com.br/static>
    Require all granted
</Directory>
```

### 7. Testar no Site

1. Acessar https://monpec.com.br (ou http://monpec.com.br)
2. Testar menu mobile (abrir no celular)
3. Verificar se as imagens aparecem no slideshow
4. Testar formulário de demonstração
5. Testar login com usuário admin

## Troubleshooting

### Se as imagens não aparecerem:

1. Verificar se os arquivos existem:
```bash
ls -la static/site/foto*.jpeg
```

2. Verificar permissões:
```bash
chmod 644 static/site/foto*.jpeg
```

3. Verificar se o collectstatic foi executado:
```bash
ls -la /var/www/monpec.com.br/static/site/
```

4. Verificar logs do servidor web:
```bash
sudo tail -f /var/log/nginx/error.log
# ou
sudo tail -f /var/log/apache2/error.log
```

### Se o menu mobile não funcionar:

1. Limpar cache do navegador (Ctrl+Shift+Delete)
2. Verificar console do navegador (F12) para erros JavaScript
3. Verificar se o Font Awesome está carregando

### Se o formulário de demonstração der erro:

1. Verificar logs do Django:
```bash
tail -f /var/log/monpec/django.log
```

2. Verificar se o banco de dados está acessível
3. Verificar se as migrações estão aplicadas:
```bash
python manage.py migrate
```

## Comandos Rápidos

```bash
# Atualizar tudo de uma vez
cd /var/www/monpec.com.br
source venv/bin/activate
git pull  # se usar git
python manage.py collectstatic --noinput
python criar_admin_fix.py
sudo systemctl restart gunicorn
```

## Verificação Final

Após atualizar, verificar:

- [ ] Menu mobile funciona no celular
- [ ] Imagens aparecem no slideshow
- [ ] Formulário de demonstração funciona
- [ ] Login com admin funciona
- [ ] Site carrega sem erros no console










