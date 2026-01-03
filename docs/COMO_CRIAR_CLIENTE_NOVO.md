# Como Criar um Cliente Novo com Banco de Dados Vazio

Este guia explica como criar um novo cliente no sistema MONPEC com um banco de dados completamente vazio, como se fosse um cliente novo começando a usar o sistema.

## Scripts Disponíveis

Existem dois scripts para criar novos clientes:

### 1. Script Interativo (`criar_cliente_novo.py`)

Este script solicita todas as informações interativamente durante a execução.

**Uso:**
```bash
python311\python.exe criar_cliente_novo.py
```

O script irá solicitar:
- Nome completo do cliente
- E-mail
- Username (opcional, usa o e-mail se não informado)
- Senha
- CPF/CNPJ do produtor
- Telefone (opcional)
- Endereço do produtor (opcional)
- Nome da propriedade
- Município
- UF (2 letras)
- Área total (hectares)
- Tipo de ciclo pecuário (CRIA/RECRIA/ENGORDA/CICLO_COMPLETO)
- Tipo de propriedade (PROPRIA/ARRENDAMENTO)

### 2. Script com Parâmetros (`criar_cliente_novo_simples.py`)

Este script aceita todos os parâmetros via linha de comando, útil para automação.

**Uso:**
```bash
python311\python.exe criar_cliente_novo_simples.py nome email senha cpf_cnpj propriedade municipio uf area
```

**Parâmetros obrigatórios:**
1. `nome` - Nome completo do cliente
2. `email` - E-mail do cliente
3. `senha` - Senha do usuário
4. `cpf_cnpj` - CPF ou CNPJ do produtor
5. `propriedade` - Nome da propriedade
6. `municipio` - Município da propriedade
7. `uf` - UF (2 letras)
8. `area` - Área total em hectares

**Parâmetros opcionais (após os obrigatórios):**
9. `username` - Username (padrão: parte antes do @ do e-mail)
10. `telefone` - Telefone do produtor
11. `endereco` - Endereço do produtor
12. `tipo_ciclo` - Tipo de ciclo (CRIA/RECRIA/ENGORDA/CICLO_COMPLETO) [padrão: CICLO_COMPLETO]
13. `tipo_propriedade` - Tipo de propriedade (PROPRIA/ARRENDAMENTO) [padrão: PROPRIA]

**Exemplo:**
```bash
python311\python.exe criar_cliente_novo_simples.py "João Silva" joao@email.com senha123 12345678900 "Fazenda Teste" "São Paulo" SP 1000
```

**Exemplo completo com todos os parâmetros:**
```bash
python311\python.exe criar_cliente_novo_simples.py "João Silva" joao@email.com senha123 12345678900 "Fazenda Teste" "São Paulo" SP 1000 joao_silva "(11) 99999-9999" "Rua Exemplo, 123" CICLO_COMPLETO PROPRIA
```

## O que é Criado

Quando você executa um dos scripts, o sistema cria:

1. **Usuário (User)**
   - Username e e-mail únicos
   - Senha configurada
   - Usuário ativo

2. **Plano de Assinatura**
   - Se não existir, cria um plano básico padrão
   - Com todos os módulos disponíveis

3. **Assinatura do Cliente (AssinaturaCliente)**
   - Vinculada ao usuário
   - Status: ATIVA
   - Vinculada ao plano

4. **Produtor Rural (ProdutorRural)**
   - Dados do produtor
   - Vinculado ao usuário responsável

5. **Propriedade (Propriedade)**
   - Dados da propriedade
   - Vinculada ao produtor
   - Tipo de operação: Pecuária
   - Ciclo pecuário configurado

6. **Perfil de Tenant (TenantUsuario)**
   - Perfil ADMIN
   - Acesso a todos os módulos do plano

## Estado do Banco de Dados

Após a criação, o cliente terá:
- ✅ Usuário criado e ativo
- ✅ Estrutura básica (produtor, propriedade)
- ✅ Acesso ao sistema
- ✅ **Banco de dados vazio** (sem animais, movimentações, vendas, etc.)

O cliente pode começar a usar o sistema normalmente, cadastrando seus primeiros animais, movimentações, etc.

## Validações Realizadas

Os scripts validam:
- E-mail único (não pode estar cadastrado)
- Username único (gera automaticamente se já existir)
- CPF/CNPJ único (não pode estar cadastrado)
- Senha forte (conforme regras de segurança)
- UF com 2 letras
- Área maior que zero
- Todos os campos obrigatórios preenchidos

## Tratamento de Erros

Se ocorrer algum erro durante a criação:
- A transação é revertida (nada é criado)
- Uma mensagem de erro é exibida
- O sistema permanece no estado anterior

## Exemplo de Saída

```
======================================================================
✓ CLIENTE CRIADO COM SUCESSO!
======================================================================

DADOS DE ACESSO:
  Username: joao_silva
  E-mail: joao@email.com
  Senha: senha123

ESTRUTURA CRIADA:
  • Usuário: João Silva
  • Assinatura: 1 (Ativa)
  • Produtor: João Silva
  • Propriedade: Fazenda Teste

O banco de dados está vazio (sem animais, movimentações, etc.)
O cliente pode começar a usar o sistema normalmente.
======================================================================
```

## Notas Importantes

1. **Senha**: A senha deve atender aos requisitos de segurança do sistema (mínimo de caracteres, letras, números, etc.)

2. **E-mail e CPF/CNPJ**: Devem ser únicos no sistema

3. **Plano Padrão**: Se não existir um plano básico, um será criado automaticamente com:
   - Nome: "Plano Básico"
   - Máximo de 5 usuários
   - Todos os módulos padrão disponíveis

4. **Propriedade**: Uma propriedade é criada automaticamente. O cliente pode criar mais propriedades depois pelo sistema.

5. **Dados Vazios**: O sistema garante que não há dados de animais, movimentações, vendas, etc. O cliente começa do zero.

## Solução de Problemas

### Erro: "E-mail já está cadastrado"
- Use um e-mail diferente ou verifique se o cliente já existe

### Erro: "CPF/CNPJ já está cadastrado"
- Verifique se o produtor já está cadastrado no sistema

### Erro: "Senha inválida"
- A senha deve atender aos requisitos de segurança (mínimo de caracteres, letras, números, etc.)

### Erro: "UF deve ter 2 letras"
- Use apenas 2 letras para o estado (ex: SP, MG, RJ)

## Suporte

Em caso de dúvidas ou problemas, verifique:
1. Se o Django está configurado corretamente
2. Se o banco de dados está acessível
3. Se todas as migrações foram executadas
4. Os logs de erro exibidos no terminal


