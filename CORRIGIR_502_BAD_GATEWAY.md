# Corrigir Erro 502 Bad Gateway no App Engine

## Problema

O App Engine está retornando erro **502 Bad Gateway**, indicando que o nginx (proxy) não consegue se comunicar com a aplicação Django.

## Causas Possíveis

1. **Aplicação não está iniciando corretamente**
2. **Erro no código que impede o startup**
3. **Variáveis de ambiente não configuradas**
4. **Banco de dados não acessível**
5. **Problemas com migrações**

## Soluções

### 1. Verificar Logs do App Engine

```bash
# Ver logs em tempo real
gcloud app logs tail -s default

# Ver últimos 100 logs
gcloud app logs read -s default --limit=100
```

### 2. Verificar Variáveis de Ambiente

Acesse: https://console.cloud.google.com/appengine/settings

Certifique-se de que as seguintes variáveis estão configuradas:

```
DEBUG=False
SECRET_KEY=[sua-chave-secreta]
DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp
PYTHONUNBUFFERED=1
ALLOWED_HOSTS=monpec-sistema-rural.rj.r.appspot.com,monpec.com.br,www.monpec.com.br
```

### 3. Verificar se o Banco de Dados Está Acessível

Se estiver usando Cloud SQL:

```bash
# Verificar conexão
gcloud sql instances list

# Verificar se a conexão está configurada
gcloud sql instances describe [INSTANCE_NAME]
```

### 4. Executar Migrações no App Engine

```bash
# Via Cloud Shell
gcloud app versions migrate [VERSION]

# Ou executar manualmente via Cloud Shell
gcloud app shell
python manage.py migrate
```

### 5. Verificar se a Aplicação Está Rodando

```bash
# Ver versões do App Engine
gcloud app versions list

# Ver detalhes de uma versão
gcloud app versions describe [VERSION]
```

### 6. Fazer Novo Deploy com Correções

Após corrigir os problemas:

```bash
# Fazer novo deploy
gcloud app deploy --version=[NOVA_VERSION]

# Promover a nova versão
gcloud app versions migrate [NOVA_VERSION]
```

## Correções Aplicadas

✅ **MessageMiddleware corrigido** - Ordem do middleware ajustada em `settings.py`
✅ **Migrações aplicadas** - Tabela `gestao_rural_cocho` criada

## Próximos Passos

1. Verificar logs do App Engine para identificar o erro específico
2. Configurar variáveis de ambiente no GCP Console
3. Executar migrações se necessário
4. Fazer novo deploy se houver mudanças no código

## Comandos Úteis

```bash
# Ver status do serviço
gcloud app describe

# Ver logs detalhados
gcloud app logs read -s default --limit=50

# Fazer deploy de uma nova versão
gcloud app deploy --version=$(date +%Y%m%d-%H%M%S)

# Verificar se há erros de sintaxe
python manage.py check --deploy
```

## Troubleshooting

### Se o erro persistir:

1. **Verificar se o requirements.txt está correto**
   - Todas as dependências estão listadas?
   - Versões compatíveis?

2. **Verificar se o app.yaml está correto**
   - Runtime correto (python311)?
   - Handlers configurados?

3. **Verificar se há erros de importação**
   - Todos os módulos estão disponíveis?
   - Não há imports circulares?

4. **Verificar se o banco de dados está acessível**
   - Cloud SQL está rodando?
   - Credenciais corretas?

## Suporte

Se o problema persistir após seguir todos os passos:
1. Verificar logs detalhados no Cloud Console
2. Verificar se há erros de sintaxe no código
3. Considerar usar Cloud Run como alternativa






















