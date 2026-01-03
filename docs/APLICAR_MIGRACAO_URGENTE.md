# ⚠️ URGENTE: Aplicar Migração de NF-e

O erro `no such column: gestao_rural_notafiscal.cliente_id` indica que a migração **0070_adicionar_cliente_nota_fiscal** ainda não foi aplicada ao banco de dados.

## 🚨 Solução Imediata

Execute **UM** dos comandos abaixo no terminal (PowerShell ou CMD) na **raiz do projeto**:

### Opção 1: Comando Direto (Recomendado)

```powershell
python manage.py migrate gestao_rural
```

### Opção 2: Aplicar Migração Específica

```powershell
python manage.py migrate gestao_rural 0070_adicionar_cliente_nota_fiscal
```

### Opção 3: Aplicar Todas as Migrações

```powershell
python manage.py migrate
```

## 📍 Onde Executar

1. Abra o **PowerShell** ou **CMD**
2. Navegue até a raiz do projeto:
   ```powershell
   cd c:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural
   ```
3. Execute o comando de migração

## ✅ Verificar se Funcionou

Após executar, você deve ver uma mensagem como:

```
Running migrations:
  Applying gestao_rural.0070_adicionar_cliente_nota_fiscal... OK
```

## 🔄 Após Aplicar a Migração

1. **Reinicie o servidor Django** (se estiver rodando)
2. Acesse novamente: `http://localhost:8000/propriedade/8/compras/`
3. O erro deve desaparecer

## ⚠️ Se o Python Não Estiver no PATH

Se aparecer "Python não foi encontrado", use o caminho completo:

```powershell
C:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural\python311\python.exe manage.py migrate gestao_rural
```

Ou encontre onde o Python está instalado e use o caminho completo.

## 📝 O que a Migração Faz

A migração `0070_adicionar_cliente_nota_fiscal`:
- ✅ Adiciona a coluna `cliente_id` à tabela `gestao_rural_notafiscal`
- ✅ Torna o campo `fornecedor_id` opcional
- ✅ Remove restrições que impediam múltiplas notas com mesmo número

## 🆘 Se Ainda Não Funcionar

1. Verifique se está na raiz do projeto (onde está o `manage.py`)
2. Verifique se o banco de dados está acessível
3. Tente executar: `python manage.py showmigrations gestao_rural` para ver o status
4. Se a migração aparecer como `[ ]` (não aplicada), execute novamente o migrate

