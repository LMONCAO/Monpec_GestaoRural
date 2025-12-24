# Guia de Cadastros Financeiros - Sistema Monpec

Este guia explica como fazer o cadastro de **Plano de Contas**, **Centro de Custo** e **Contas de Lançamento** no sistema.

## 📋 Índice

1. [Plano de Contas](#plano-de-contas)
2. [Centro de Custo](#centro-de-custo)
3. [Contas de Lançamento](#contas-de-lançamento)
4. [Como Usar nos Módulos](#como-usar-nos-módulos)

---

## 📊 Plano de Contas

O **Plano de Contas** é a estrutura contábil que organiza as receitas e despesas da propriedade.

### Como Acessar

1. Acesse o módulo **Financeiro** da propriedade
2. No menu lateral, procure por **"Planos de Contas"** ou acesse diretamente:
   ```
   /propriedade/{id}/financeiro/planos-conta/
   ```

### Como Cadastrar

**Nota:** Atualmente, o sistema não possui uma interface específica para cadastro de Planos de Contas. Você pode:

#### Opção 1: Via Django Admin (Recomendado)

1. Acesse o Django Admin: `http://localhost:8000/admin/`
2. Faça login com usuário administrador
3. Navegue até: **Gestão Rural > Planos de Contas**
4. Clique em **"Adicionar Plano de Conta"**
5. Preencha os campos:
   - **Propriedade:** Selecione a propriedade (ou deixe vazio para disponibilizar para todas)
   - **Código:** Código único do plano (ex: "1.1.01", "2.3.05")
   - **Nome:** Nome descritivo (ex: "Ração para Gado", "Medicamentos")
   - **Tipo:** 
     - `RECEITA` - Para receitas
     - `DESPESA` - Para despesas
     - `TRANSFERENCIA` - Para transferências
   - **Descrição:** Descrição detalhada (opcional)
   - **Categoria Financeira:** Categoria relacionada (opcional)
   - **Ativo:** Marque se estiver ativo

6. Clique em **"Salvar"**

#### Opção 2: Via Python Shell

```python
from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import PlanoConta

# Obter a propriedade
propriedade = Propriedade.objects.get(id=1)

# Criar plano de conta
plano = PlanoConta.objects.create(
    propriedade=propriedade,
    codigo="1.1.01",
    nome="Ração para Gado",
    tipo=PlanoConta.TIPO_DESPESA,
    descricao="Despesas com ração para gado de corte",
    ativo=True
)
```

### Exemplos de Planos de Contas

#### Despesas Operacionais
- **Código:** `1.1.01` - **Nome:** Ração para Gado
- **Código:** `1.1.02` - **Nome:** Medicamentos Veterinários
- **Código:** `1.1.03` - **Nome:** Combustível
- **Código:** `1.1.04` - **Nome:** Manutenção de Equipamentos
- **Código:** `1.1.05` - **Nome:** Salários

#### Receitas
- **Código:** `2.1.01` - **Nome:** Venda de Gado
- **Código:** `2.1.02` - **Nome:** Venda de Leite
- **Código:** `2.1.03` - **Nome:** Outras Receitas

---

## 🎯 Centro de Custo

O **Centro de Custo** permite segmentar os custos por área/departamento da propriedade.

### Como Acessar

1. Acesse o módulo **Financeiro** da propriedade
2. No menu lateral, clique em **"Centros de Custo"** ou acesse:
   ```
   /propriedade/{id}/financeiro/centros-custo/
   ```

### Como Cadastrar

1. Na lista de Centros de Custo, clique no botão **"Novo Centro de Custo"**
2. Preencha o formulário:
   - **Nome:** Nome do centro de custo (ex: "Pecuária", "Agricultura", "Administração")
   - **Tipo:**
     - `OPERACIONAL` - Para atividades operacionais
     - `ADMINISTRATIVO` - Para atividades administrativas
     - `INVESTIMENTO` - Para investimentos
   - **Descrição:** Descrição detalhada (opcional)
   - **Ativo:** Marque se estiver ativo

3. Clique em **"Salvar"**

### Exemplos de Centros de Custo

- **Nome:** Pecuária - **Tipo:** Operacional
- **Nome:** Agricultura - **Tipo:** Operacional
- **Nome:** Infraestrutura - **Tipo:** Operacional
- **Nome:** Administração - **Tipo:** Administrativo
- **Nome:** Investimentos - **Tipo:** Investimento

---

## 💰 Contas de Lançamento

As **Contas de Lançamento** são as contas financeiras (caixa, bancos, investimentos) onde os valores são registrados.

### Como Acessar

1. Acesse o módulo **Financeiro** da propriedade
2. No menu lateral, clique em **"Contas"** ou acesse:
   ```
   /propriedade/{id}/financeiro/contas/
   ```

### Como Cadastrar

1. Na lista de Contas, clique no botão **"Nova Conta"**
2. Preencha o formulário:
   - **Nome:** Nome da conta (ex: "Caixa", "Banco do Brasil", "Conta Corrente")
   - **Tipo:**
     - `CAIXA` - Para caixa físico
     - `BANCO` - Para contas bancárias
     - `INVESTIMENTO` - Para investimentos
   - **Saldo Inicial:** Saldo inicial da conta (opcional)
   - **Descrição:** Descrição detalhada (opcional)
   - **Ativo:** Marque se estiver ativa

3. Clique em **"Salvar"**

### Exemplos de Contas

- **Nome:** Caixa Principal - **Tipo:** Caixa
- **Nome:** Banco do Brasil - Conta Corrente - **Tipo:** Banco
- **Nome:** Banco do Brasil - Poupança - **Tipo:** Banco
- **Nome:** Investimentos - **Tipo:** Investimento

---

## 🔗 Como Usar nos Módulos

### Em Ordens de Compra

Ao criar uma **Ordem de Compra**, você pode selecionar:
- **Plano de Conta:** Para classificar a despesa
- **Centro de Custo:** Para identificar a área responsável

### Em Requisições de Compra

Ao criar uma **Requisição de Compra**, você pode informar:
- **Plano de Conta:** Para classificar a despesa
- **Centro de Custo:** Para identificar a área responsável

### Em Lançamentos Financeiros

Ao criar um **Lançamento Financeiro**, você deve informar:
- **Conta:** Conta onde o valor será registrado
- **Plano de Conta:** Para classificar a receita/despesa
- **Centro de Custo:** Para identificar a área responsável

---

## 📝 Dicas Importantes

1. **Organização:** Mantenha uma estrutura hierárquica nos códigos do Plano de Contas
   - Exemplo: `1.1.01`, `1.1.02`, `1.2.01`, etc.

2. **Nomenclatura:** Use nomes claros e descritivos para facilitar a busca

3. **Ativação:** Mantenha apenas os cadastros ativos que estão em uso

4. **Consistência:** Use a mesma nomenclatura em todas as propriedades para facilitar relatórios consolidados

5. **Centro de Custo:** Crie centros de custo que reflitam a estrutura organizacional da propriedade

---

## 🆘 Suporte

Se tiver dúvidas ou precisar de ajuda:
1. Consulte a documentação do sistema
2. Entre em contato com o suporte técnico
3. Verifique os exemplos de cadastros já existentes no sistema

---

**Última atualização:** Dezembro 2025











