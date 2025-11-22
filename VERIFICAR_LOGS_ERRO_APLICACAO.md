# 🔍 Verificar Logs - Internal Server Error

## ⚠️ Situação

- ✅ Deploy concluído com sucesso
- ❌ Site ainda mostra "Internal Server Error"

Isso significa que há um erro na aplicação Django, não no processo de deploy.

---

## 📋 Passo 1: Verificar Logs do Cloud Run

Execute no Cloud Shell para ver o erro específico:

```bash
gcloud run services logs read monpec --region us-central1 --limit 100
```

**Procure por:**
- `Traceback` (erro completo do Python)
- `Exception` (exceções)
- `Error` (erros gerais)
- `OperationalError` (erro de banco de dados)
- `ImportError` (erro de importação)
- `KeyError` (variável de ambiente faltando)

---

## 📋 Passo 2: Ver Logs em Tempo Real

Para ver logs enquanto acessa o site:

```bash
gcloud run services logs tail monpec --region us-central1
```

Depois, acesse o site em outra aba e veja os logs aparecerem.

---

## 🔍 Possíveis Problemas

### Problema 1: Erro de Banco de Dados

**Sintoma nos logs:**
```
OperationalError: could not connect to server
```

**Solução:**
- Verificar se o Cloud SQL está acessível
- Verificar se o `CLOUD_SQL_CONNECTION_NAME` está correto
- Verificar se o Cloud Run tem permissão para acessar o Cloud SQL

---

### Problema 2: Variável de Ambiente Faltando

**Sintoma nos logs:**
```
KeyError: 'SECRET_KEY'
```

**Solução:**
- Verificar se todas as variáveis de ambiente estão configuradas
- Re-executar o deploy com todas as variáveis

---

### Problema 3: Erro de Importação

**Sintoma nos logs:**
```
ImportError: No module named 'X'
```

**Solução:**
- Verificar se o módulo está em `requirements_producao.txt`
- Verificar se o build incluiu todas as dependências

---

### Problema 4: Erro de Migração

**Sintoma nos logs:**
```
django.db.utils.OperationalError: relation "X" does not exist
```

**Solução:**
- Executar migrações manualmente
- Verificar se o banco está acessível

---

## 🚀 Solução Rápida: Verificar Variáveis de Ambiente

Verifique se todas as variáveis estão configuradas:

```bash
gcloud run services describe monpec --region us-central1 --format="value(spec.template.spec.containers[0].env)"
```

**Deve mostrar:**
- `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- `DEBUG=False`
- `DB_NAME=monpec_db`
- `DB_USER=monpec_user`
- `DB_PASSWORD=Monpec2025!`
- `CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db`
- `SECRET_KEY=...`

---

## 📝 Próximos Passos

1. **Execute o comando de logs** (Passo 1)
2. **Copie o erro completo** (especialmente o Traceback)
3. **Me envie o erro** para eu ajudar a corrigir especificamente

---

**Última atualização:** Novembro 2025

