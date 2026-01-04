# 🚀 Exemplo Rápido: Carregar Dados do Banco

## Cenário 1: Importar de Backup SQLite

Se você tem um backup SQLite do banco de dados:

```bash
# Windows (PowerShell)
.\scripts\carregar_dados_banco.ps1 -Fonte sqlite -Caminho "backup/db_backup.sqlite3" -UsuarioId 1

# Linux/Mac
./scripts/carregar_dados_banco.sh sqlite backup/db_backup.sqlite3 1

# Ou diretamente
python manage.py carregar_dados_banco --fonte sqlite --caminho "backup/db_backup.sqlite3" --usuario-id 1
```

## Cenário 2: Importar de PostgreSQL

Se seus dados estão em um banco PostgreSQL:

```bash
# Windows (PowerShell)
.\scripts\carregar_dados_banco.ps1 `
    -Fonte postgresql `
    -Host "localhost" `
    -Port 5432 `
    -Database "meu_banco" `
    -User "meu_user" `
    -Password "minha_senha" `
    -UsuarioId 1

# Ou diretamente
python manage.py carregar_dados_banco \
    --fonte postgresql \
    --host localhost \
    --port 5432 \
    --database meu_banco \
    --user meu_user \
    --password minha_senha \
    --usuario-id 1
```

## Cenário 3: Importar de Arquivo JSON

Crie um arquivo `dados.json`:

```json
{
    "gestao_rural_produtorrural": [
        {
            "nome": "João Silva",
            "cpf_cnpj": "12345678901",
            "telefone": "(11) 99999-9999",
            "email": "joao@fazenda.com",
            "endereco": "Fazenda São José, Zona Rural"
        }
    ],
    "gestao_rural_propriedade": [
        {
            "nome": "Fazenda São José",
            "area_total": 1000.50,
            "produtor_id": 1
        }
    ]
}
```

Depois importe:

```bash
python manage.py carregar_dados_banco --fonte json --caminho "dados.json" --usuario-id 1
```

## Cenário 4: Testar Antes de Importar (Dry-Run)

Sempre teste primeiro com `--dry-run`:

```bash
python manage.py carregar_dados_banco \
    --fonte sqlite \
    --caminho "backup/db_backup.sqlite3" \
    --usuario-id 1 \
    --dry-run
```

Isso mostrará o que seria importado sem salvar no banco.

## Cenário 5: Sincronizar Dados Existentes

Se você já tem dados no banco e quer sincronizá-los:

```bash
python manage.py carregar_dados_banco --fonte sincronizar --usuario-id 1
```

## 📝 Dicas Importantes

1. **Sempre faça backup antes de importar:**
   ```bash
   python manage.py backup_tenants
   ```

2. **Use --dry-run primeiro para testar**

3. **Verifique o usuário ID:**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.all().values('id', 'username')
   ```

4. **Para grandes volumes, seja paciente - a importação pode demorar**

## 🔍 Verificar Dados Importados

Depois de importar, verifique se os dados foram carregados:

```bash
python manage.py shell
>>> from gestao_rural.models import ProdutorRural, Propriedade
>>> ProdutorRural.objects.count()
>>> Propriedade.objects.count()
```

## ❓ Precisa de Ajuda?

Consulte a documentação completa em: `docs/CARREGAR_DADOS_BANCO.md`


