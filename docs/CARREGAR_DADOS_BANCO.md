# Guia: Carregar Dados do Banco de Dados

Este guia explica como carregar seus dados do banco de dados para o sistema web.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Fontes de Dados Suportadas](#fontes-de-dados-suportadas)
3. [Exemplos de Uso](#exemplos-de-uso)
4. [Opções Disponíveis](#opções-disponíveis)
5. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O comando `carregar_dados_banco` permite importar dados de diferentes fontes para o sistema web:

- **SQLite**: Importar de um arquivo `.db` ou `.sqlite3`
- **PostgreSQL**: Importar de um banco PostgreSQL
- **JSON**: Importar de um arquivo JSON
- **CSV**: Importar de um arquivo CSV
- **Sincronizar**: Sincronizar dados já existentes no banco

## 📦 Fontes de Dados Suportadas

### 1. SQLite

Importa dados de um banco SQLite (arquivo `.db` ou `.sqlite3`).

**Exemplo:**
```bash
python manage.py carregar_dados_banco --fonte sqlite --caminho "backup/db_backup.sqlite3" --usuario-id 1
```

**Com PowerShell:**
```powershell
.\scripts\carregar_dados_banco.ps1 -Fonte sqlite -Caminho "backup/db_backup.sqlite3" -UsuarioId 1
```

### 2. PostgreSQL

Importa dados de um banco PostgreSQL.

**Exemplo:**
```bash
python manage.py carregar_dados_banco \
    --fonte postgresql \
    --host localhost \
    --port 5432 \
    --database meu_banco \
    --user meu_user \
    --password minha_senha \
    --usuario-id 1
```

**Com PowerShell:**
```powershell
.\scripts\carregar_dados_banco.ps1 `
    -Fonte postgresql `
    -Host "localhost" `
    -Port 5432 `
    -Database "meu_banco" `
    -User "meu_user" `
    -Password "minha_senha" `
    -UsuarioId 1
```

### 3. JSON

Importa dados de um arquivo JSON.

**Formato do JSON:**
```json
{
    "gestao_rural_produtorrural": [
        {
            "nome": "João Silva",
            "cpf_cnpj": "12345678901",
            "telefone": "(11) 99999-9999",
            "email": "joao@fazenda.com"
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

**Exemplo:**
```bash
python manage.py carregar_dados_banco --fonte json --caminho "dados.json" --usuario-id 1
```

### 4. CSV

Importa dados de um arquivo CSV. Requer especificar a tabela.

**Exemplo:**
```bash
python manage.py carregar_dados_banco \
    --fonte csv \
    --caminho "produtores.csv" \
    --tabela gestao_rural_produtorrural \
    --usuario-id 1
```

**Formato do CSV:**
```csv
nome,cpf_cnpj,telefone,email
João Silva,12345678901,(11) 99999-9999,joao@fazenda.com
Maria Santos,98765432100,(11) 88888-8888,maria@fazenda.com
```

### 5. Sincronizar

Sincroniza dados já existentes no banco atual para um usuário específico.

**Exemplo:**
```bash
python manage.py carregar_dados_banco --fonte sincronizar --usuario-id 1
```

## ⚙️ Opções Disponíveis

### Opções Gerais

- `--fonte`: Fonte dos dados (obrigatório)
  - Valores: `sqlite`, `postgresql`, `json`, `csv`, `sincronizar`

- `--caminho`: Caminho do arquivo (obrigatório para sqlite, json, csv)

- `--tabela`: Nome da tabela específica para importar (opcional)

- `--usuario-id`: ID do usuário para vincular os dados (recomendado)

- `--sobrescrever`: Sobrescrever dados existentes (padrão: False)

- `--dry-run`: Simular importação sem salvar no banco (útil para testar)

### Opções PostgreSQL

- `--host`: Host do banco PostgreSQL (padrão: localhost)

- `--port`: Porta do banco PostgreSQL (padrão: 5432)

- `--database`: Nome do banco de dados (obrigatório)

- `--user`: Usuário do banco (obrigatório)

- `--password`: Senha do banco (obrigatório)

## 🔍 Exemplos Práticos

### Exemplo 1: Importar backup SQLite

```bash
# Primeiro, fazer um teste (dry-run)
python manage.py carregar_dados_banco \
    --fonte sqlite \
    --caminho "backup/db_backup.sqlite3" \
    --usuario-id 1 \
    --dry-run

# Se estiver tudo ok, importar de verdade
python manage.py carregar_dados_banco \
    --fonte sqlite \
    --caminho "backup/db_backup.sqlite3" \
    --usuario-id 1
```

### Exemplo 2: Importar apenas uma tabela específica

```bash
python manage.py carregar_dados_banco \
    --fonte sqlite \
    --caminho "backup/db_backup.sqlite3" \
    --tabela gestao_rural_produtorrural \
    --usuario-id 1
```

### Exemplo 3: Importar e sobrescrever dados existentes

```bash
python manage.py carregar_dados_banco \
    --fonte json \
    --caminho "dados.json" \
    --usuario-id 1 \
    --sobrescrever
```

### Exemplo 4: Importar de PostgreSQL de produção

```bash
python manage.py carregar_dados_banco \
    --fonte postgresql \
    --host "meu-servidor.com" \
    --port 5432 \
    --database "monpec_db" \
    --user "monpec_user" \
    --password "senha_segura" \
    --usuario-id 1
```

## 🛠️ Troubleshooting

### Erro: "Arquivo não encontrado"

**Solução:** Verifique se o caminho do arquivo está correto e se o arquivo existe.

```bash
# Verificar se o arquivo existe
ls backup/db_backup.sqlite3  # Linux/Mac
dir backup\db_backup.sqlite3  # Windows
```

### Erro: "psycopg2 não está instalado"

**Solução:** Instale o psycopg2 para suportar PostgreSQL:

```bash
pip install psycopg2-binary
```

### Erro: "Usuário com ID X não encontrado"

**Solução:** Verifique se o usuário existe no banco:

```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()
```

### Erro: "Tabela não mapeada"

**Solução:** O comando suporta apenas tabelas mapeadas. Tabelas suportadas:
- `gestao_rural_produtorrural`
- `gestao_rural_propriedade`
- `gestao_rural_categoriaanimal`
- `gestao_rural_animalindividual`
- `gestao_rural_brincoanimal`

Para adicionar mais tabelas, edite o arquivo `gestao_rural/management/commands/carregar_dados_banco.py`.

### Dados não aparecem no sistema web

**Soluções:**
1. Verifique se os dados foram importados corretamente:
   ```bash
   python manage.py shell
   >>> from gestao_rural.models import ProdutorRural
   >>> ProdutorRural.objects.count()
   ```

2. Verifique se o `usuario_id` está correto e se os dados estão vinculados ao usuário correto.

3. Limpe o cache do navegador e recarregue a página.

## 📝 Notas Importantes

1. **Backup**: Sempre faça backup do banco antes de importar dados, especialmente com `--sobrescrever`.

2. **Dry-Run**: Use `--dry-run` primeiro para testar a importação sem modificar o banco.

3. **Usuário ID**: É recomendado sempre especificar `--usuario-id` para vincular os dados ao usuário correto.

4. **Transações**: A importação usa transações, então se houver erro, nenhum dado será salvo.

5. **Performance**: Para grandes volumes de dados, a importação pode demorar. Seja paciente.

## 🔗 Comandos Relacionados

- `python manage.py popular_monpec1_demo` - Popular dados de demonstração
- `python manage.py backup_tenants` - Fazer backup dos dados
- `python manage.py restaurar_backup` - Restaurar backup

## 📞 Suporte

Se encontrar problemas, verifique:
1. Os logs do Django
2. A documentação do Django
3. Os arquivos de exemplo em `docs/`

