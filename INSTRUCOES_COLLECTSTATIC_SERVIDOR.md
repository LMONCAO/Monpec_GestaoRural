# Instruções para Executar Collectstatic no Servidor

## Problema
As imagens não estão aparecendo no site monpec.com.br porque os arquivos estáticos não foram coletados no servidor de produção.

## Solução

### Opção 1: Executar via Script (Recomendado)

Execute o script PowerShell que foi criado:

```powershell
.\executar_collectstatic_servidor.ps1
```

Se você tiver uma chave SSH configurada:

```powershell
.\executar_collectstatic_servidor.ps1 -ChaveSSH "caminho\para\sua\chave.pem"
```

### Opção 2: Executar Manualmente via SSH

1. **Conecte-se ao servidor:**
   ```bash
   ssh ubuntu@10.1.1.234
   ```
   (ou use o usuário e IP correto do seu servidor)

2. **Navegue até o diretório do projeto:**
   ```bash
   cd /var/www/monpec.com.br
   ```
   (ou o caminho onde está o projeto Django)

3. **Execute o collectstatic:**
   ```bash
   python3 manage.py collectstatic --noinput --clear --settings=sistema_rural.settings_producao
   ```

4. **Reinicie os serviços:**
   ```bash
   # Reiniciar gunicorn (se estiver usando)
   sudo systemctl restart gunicorn
   
   # Reiniciar nginx (se estiver usando)
   sudo systemctl restart nginx
   
   # Ou reiniciar o serviço monpec (se existir)
   sudo systemctl restart monpec
   ```

5. **Verifique se as imagens foram coletadas:**
   ```bash
   ls -lh /var/www/monpec.com.br/static/site/*.jpeg
   ```

### Opção 3: Se o projeto estiver em outro diretório

Se o projeto não estiver em `/var/www/monpec.com.br`, verifique onde está:

```bash
# Procurar o diretório do projeto
find /home -name "manage.py" 2>/dev/null
find /var -name "manage.py" 2>/dev/null

# Ou verificar processos Django
ps aux | grep manage.py
```

Depois navegue até o diretório encontrado e execute o collectstatic.

## Verificação

Após executar o collectstatic, verifique se as imagens estão acessíveis:

- https://monpec.com.br/static/site/foto1.jpeg
- https://monpec.com.br/static/site/foto2.jpeg
- https://monpec.com.br/static/site/foto3.jpeg
- https://monpec.com.br/static/site/foto4.jpeg
- https://monpec.com.br/static/site/foto5.jpeg
- https://monpec.com.br/static/site/foto6.jpeg

Se as imagens aparecerem, o problema está resolvido!

## Problemas Comuns

### Erro: "Permission denied"
```bash
# Dar permissões ao diretório static
sudo chown -R www-data:www-data /var/www/monpec.com.br/static
sudo chmod -R 755 /var/www/monpec.com.br/static
```

### Erro: "No module named django"
```bash
# Ativar o ambiente virtual (se houver)
source venv/bin/activate
# ou
source env/bin/activate
```

### Erro: "STATIC_ROOT não encontrado"
Verifique se o diretório existe e tem permissões:
```bash
sudo mkdir -p /var/www/monpec.com.br/static
sudo chown -R $USER:$USER /var/www/monpec.com.br/static
```

## Nota Importante

A correção na view `gestao_rural/views_static.py` já foi aplicada. Ela agora verifica primeiro em `STATIC_ROOT` (onde os arquivos coletados ficam em produção) e depois em `STATICFILES_DIRS` (desenvolvimento).

Após executar o collectstatic no servidor, as imagens devem aparecer corretamente no site.

