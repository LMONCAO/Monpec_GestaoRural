# 🔍 Verificar Logs - Novo Erro Após Correção

## ⚠️ Situação Atual

- ✅ Deploy concluído com sucesso
- ✅ `openpyxl` foi adicionado ao `requirements_producao.txt`
- ❌ Site ainda mostra "Internal Server Error"

Isso significa que há **outro erro** além do `openpyxl`.

---

## 📋 Verificar Logs do Cloud Run

Execute no Cloud Shell para ver o erro específico:

```bash
gcloud run services logs read monpec --region us-central1 --limit 100
```

**Procure por:**
- `Traceback` (erro completo do Python)
- `Exception` (exceções)
- `Error` (erros gerais)
- `ModuleNotFoundError` (outro módulo faltando)
- `ImportError` (erro de importação)
- `OperationalError` (erro de banco de dados)
- `KeyError` (variável de ambiente faltando)

---

## 🔍 Possíveis Problemas

### Problema 1: Outro Módulo Faltando

**Sintoma nos logs:**
```
ModuleNotFoundError: No module named 'X'
```

**Solução:**
- Verificar se o módulo está em `requirements_producao.txt`
- Adicionar se não estiver

---

### Problema 2: Erro de Banco de Dados

**Sintoma nos logs:**
```
OperationalError: could not connect to server
```

**Solução:**
- Verificar se o Cloud SQL está acessível
- Verificar se o `CLOUD_SQL_CONNECTION_NAME` está correto
- Verificar se o Cloud Run tem permissão para acessar o Cloud SQL

---

### Problema 3: Erro de Migração

**Sintoma nos logs:**
```
django.db.utils.OperationalError: relation "X" does not exist
```

**Solução:**
- Executar migrações manualmente
- Verificar se o banco está acessível

---

### Problema 4: Erro de Configuração

**Sintoma nos logs:**
```
KeyError: 'X'
```

**Solução:**
- Verificar se todas as variáveis de ambiente estão configuradas
- Re-executar o deploy com todas as variáveis

---

## 🚀 Ver Logs em Tempo Real

Para ver logs enquanto acessa o site:

```bash
gcloud run services logs tail monpec --region us-central1
```

Depois, acesse o site em outra aba e veja os logs aparecerem.

---

## 📝 Próximos Passos

1. **Execute o comando de logs** acima
2. **Copie o erro completo** (especialmente o Traceback)
3. **Me envie o erro** para eu ajudar a corrigir especificamente

---

**Última atualização:** Novembro 2025













