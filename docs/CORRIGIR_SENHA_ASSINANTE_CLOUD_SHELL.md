# Corrigir Senha de Assinante em Produção

## Problema
Após o deploy, a senha do assinante não está sendo reconhecida no login.

## Solução Rápida (Cloud Shell)

Execute este comando no Cloud Shell do Google Cloud:

```bash
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();username='admin';user=User.objects.filter(username=username).first();user.set_password('L6171r12@@') if user else None;user.save() if user else None;print('✅ Senha corrigida!' if user else '❌ Usuário não encontrado')"
```

**OU** para um usuário específico (substitua `admin` pelo username ou email):

```bash
# Para username
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();username='SEU_USERNAME_AQUI';user=User.objects.filter(username=username).first();user.set_password('SUA_SENHA_AQUI') if user else None;user.save() if user else None;print('✅ Senha corrigida!' if user else '❌ Usuário não encontrado')"

# Para email
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();email='SEU_EMAIL_AQUI';user=User.objects.filter(email__iexact=email).first();user.set_password('SUA_SENHA_AQUI') if user else None;user.save() if user else None;print('✅ Senha corrigida!' if user else '❌ Usuário não encontrado')"
```

## Solução via Cloud SQL (Acesso Direto)

Se você tem acesso direto ao Cloud SQL, pode executar o script Python localmente:

1. **Conectar ao Cloud SQL:**
```bash
gcloud sql connect monpec-db --user=monpec_user --database=monpec_db
```

2. **Ou executar via Cloud Run Jobs:**

Primeiro, crie um job temporário:

```bash
gcloud run jobs create corrigir-senha-assinante \
  --image gcr.io/SEU_PROJECT_ID/monpec:latest \
  --region=us-central1 \
  --add-cloudsql-instances=SEU_PROJECT_ID:us-central1:monpec-db \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=SEU_PROJECT_ID:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA_DB"
```

Depois execute:

```bash
gcloud run jobs execute corrigir-senha-assinante \
  --region=us-central1 \
  --args python,corrigir_senha_assinante.py
```

## Solução via Script Python Local

Se você tem o script `corrigir_senha_assinante.py` localmente:

1. **Configurar variáveis de ambiente:**
```bash
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
export CLOUD_SQL_CONNECTION_NAME=SEU_PROJECT_ID:us-central1:monpec-db
export DB_NAME=monpec_db
export DB_USER=monpec_user
export DB_PASSWORD=SUA_SENHA_DB
```

2. **Executar o script:**
```bash
python corrigir_senha_assinante.py
```

## Verificar Usuário Existe

Para verificar se o usuário existe no banco:

```bash
gcloud run jobs execute verificar-usuario \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();users=User.objects.all();print('Usuários encontrados:');[print(f'  - {u.username} ({u.email}) - Ativo: {u.is_active}') for u in users]"
```

## Causas Comuns

1. **Hash de senha diferente entre ambientes**: O hash da senha pode ter sido gerado em desenvolvimento e não funciona em produção
2. **Usuário não existe em produção**: O usuário pode não ter sido migrado para o banco de produção
3. **Senha nunca foi definida**: O usuário pode ter sido criado sem senha
4. **Problema com algoritmo de hash**: Diferenças nas configurações do Django entre ambientes

## Prevenção

Para evitar este problema no futuro:

1. **Sempre use `set_password()`** ao criar usuários em produção
2. **Teste o login após criar usuários** em produção
3. **Use migrações do Django** para criar usuários iniciais
4. **Documente as senhas iniciais** em local seguro


