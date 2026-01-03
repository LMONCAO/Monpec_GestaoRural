# Como Aplicar a Migração de NF-e

A migração `0070_adicionar_cliente_nota_fiscal` adiciona o campo `cliente` à tabela `NotaFiscal` para permitir a emissão de NF-e de saída.

## Opção 1: Usar o Script PowerShell (Recomendado)

Execute no PowerShell na raiz do projeto:

```powershell
.\APLICAR_MIGRACAO_NFE.ps1
```

## Opção 2: Executar Manualmente

### No PowerShell ou CMD:

1. Navegue até a raiz do projeto:
   ```powershell
   cd c:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural
   ```

2. Execute a migração:
   ```powershell
   python manage.py migrate gestao_rural
   ```

   Ou especificamente a migração 0070:
   ```powershell
   python manage.py migrate gestao_rural 0070_adicionar_cliente_nota_fiscal
   ```

### Se o Python não estiver no PATH:

1. Encontre o caminho do Python no seu sistema (geralmente em `C:\Python311\` ou similar)

2. Use o caminho completo:
   ```powershell
   C:\Python311\python.exe manage.py migrate gestao_rural
   ```

## Opção 3: Usar o Script Python

Execute o script Python criado:

```powershell
python executar_migracao_nfe.py
```

## Verificar se a Migração foi Aplicada

Após executar a migração, verifique com:

```powershell
python manage.py showmigrations gestao_rural
```

Você deve ver `[X] 0070_adicionar_cliente_nota_fiscal` marcado como aplicado.

## O que a Migração Faz

1. ✅ Adiciona o campo `cliente` (ForeignKey) à tabela `NotaFiscal`
2. ✅ Torna o campo `fornecedor` opcional (null=True, blank=True)
3. ✅ Remove a restrição `unique_together` que impedia múltiplas notas com o mesmo número

## Após a Migração

Após aplicar a migração com sucesso:

1. ✅ O erro `no such column: gestao_rural_notafiscal.cliente_id` será resolvido
2. ✅ Você poderá acessar o dashboard de compras sem erros
3. ✅ Você poderá emitir NF-e de saída vinculadas a clientes
4. ✅ Você poderá importar NF-e de entrada vinculadas a fornecedores

## Problemas Comuns

### Erro: "Python não foi encontrado"
- Certifique-se de que o Python está instalado
- Adicione o Python ao PATH do sistema
- Ou use o caminho completo do executável Python

### Erro: "no such module named django"
- Ative o ambiente virtual do projeto
- Ou instale o Django: `pip install django`

### Erro: "Migration already applied"
- A migração já foi aplicada anteriormente
- Isso é normal e não é um problema

