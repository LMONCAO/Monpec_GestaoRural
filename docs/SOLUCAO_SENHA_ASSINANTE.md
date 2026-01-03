# 🔐 Solução: Senha de Assinante Não Reconhecida Após Deploy

## 📋 Problema

Após fazer o deploy, quando você tenta acessar como assinante, a senha não é reconhecida pelo sistema.

## 🔍 Causas Possíveis

1. **Hash de senha diferente**: A senha foi criada em desenvolvimento e o hash não funciona em produção
2. **Usuário não existe em produção**: O usuário pode não ter sido migrado para o banco de produção
3. **Senha nunca foi definida corretamente**: O usuário pode ter sido criado sem senha ou com hash incorreto
4. **Diferenças nas configurações**: Algoritmo de hash diferente entre ambientes

## ✅ Soluções

### Solução 1: Corrigir via Cloud Shell (Mais Rápido)

Execute este comando no **Cloud Shell** do Google Cloud:

```bash
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();username='admin';user=User.objects.filter(username=username).first();user.set_password('L6171r12@@') if user else None;user.save() if user else None;auth_test=authenticate(username=user.username,password='L6171r12@@') if user else None;print('✅ Senha corrigida!' if auth_test else '❌ Usuário não encontrado ou falha na autenticação')"
```

**Para outro usuário**, substitua `'admin'` pelo username ou email:

```bash
# Para username
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();username='SEU_USERNAME';senha='SUA_SENHA';user=User.objects.filter(username=username).first();user.set_password(senha) if user else None;user.save() if user else None;auth_test=authenticate(username=user.username,password=senha) if user else None;print('✅ Senha corrigida!' if auth_test else '❌ Falha')"

# Para email
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();email='SEU_EMAIL@exemplo.com';senha='SUA_SENHA';user=User.objects.filter(email__iexact=email).first();user.set_password(senha) if user else None;user.save() if user else None;auth_test=authenticate(username=user.username,password=senha) if user else None;print('✅ Senha corrigida!' if auth_test else '❌ Falha')"
```

### Solução 2: Verificar se o Usuário Existe

Antes de corrigir, verifique se o usuário existe no banco de produção:

```bash
gcloud run jobs execute verificar-usuario \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();users=User.objects.all();print('=== USUÁRIOS NO BANCO ===');[print(f'Username: {u.username} | Email: {u.email} | Ativo: {u.is_active} | Superuser: {u.is_superuser}') for u in users]"
```

### Solução 3: Criar Job Temporário no Cloud Run

Se o job `corrigir-senha-assinante` não existir, crie-o primeiro:

```bash
# Substitua SEU_PROJECT_ID pelo ID do seu projeto
PROJECT_ID="SEU_PROJECT_ID"
REGION="us-central1"

gcloud run jobs create corrigir-senha-assinante \
  --image gcr.io/${PROJECT_ID}/monpec:latest \
  --region=${REGION} \
  --add-cloudsql-instances=${PROJECT_ID}:${REGION}:monpec-db \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA_DB"
```

Depois execute o comando da Solução 1.

### Solução 4: Usar Script Python Local

Se você tem acesso ao código localmente:

1. **Edite o arquivo `corrigir_senha_assinante_rapido.py`** se necessário
2. **Configure as variáveis de ambiente:**
```bash
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
export CLOUD_SQL_CONNECTION_NAME=SEU_PROJECT_ID:us-central1:monpec-db
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=SUA_SENHA_DB
```

3. **Execute o script:**
```bash
python corrigir_senha_assinante_rapido.py admin L6171r12@@
```

## 🎯 Passo a Passo Recomendado

1. **Verifique se o usuário existe** (Solução 2)
2. **Se existir, corrija a senha** (Solução 1)
3. **Teste o login** no sistema
4. **Se ainda não funcionar**, verifique os logs do Cloud Run

## 📝 Notas Importantes

- ⚠️ **Sempre use `set_password()`** ao criar/atualizar senhas em produção
- ✅ O método `set_password()` gera o hash correto automaticamente
- 🔒 A senha deve ter no mínimo 12 caracteres (conforme configuração do Django)
- 📌 Após corrigir, teste o login imediatamente

## 🐛 Troubleshooting

### Erro: "Job não encontrado"
Crie o job primeiro usando a Solução 3.

### Erro: "Usuário não encontrado"
1. Verifique se o username/email está correto (Solução 2)
2. Se não existir, crie o usuário primeiro:
```bash
gcloud run jobs execute criar-usuario \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();user,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_staff':True,'is_superuser':True,'is_active':True});user.set_password('L6171r12@@');user.save();print('✅ Usuário criado!' if created else '✅ Usuário atualizado!')"
```

### Erro: "Autenticação falhou"
1. Verifique se a senha tem no mínimo 12 caracteres
2. Verifique se o usuário está ativo (`is_active=True`)
3. Verifique os logs do Cloud Run para mais detalhes

## 📞 Suporte

Se nenhuma das soluções funcionar, verifique:
- Logs do Cloud Run
- Configurações do banco de dados
- Variáveis de ambiente do Cloud Run


