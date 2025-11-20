# 📋 Instruções para Popular Dados em Todos os Módulos - Simulação 2025

## 🎯 Objetivo

Este comando popula dados de exemplo em **TODOS os módulos** do sistema para **TODAS as fazendas** cadastradas, simulando o **ano completo de 2025** desde janeiro, com **fazendas de grande porte** e **muitas movimentações e lançamentos mensais**.

## 🚀 Como Usar

### **Opção 1: Popular TODAS as Fazendas (Simulação 2025)**

```bash
python manage.py popular_todos_modulos_todas_fazendas
```

Este comando irá:
- ✅ Processar todas as propriedades cadastradas
- ✅ **Criar dados desde janeiro de 2025 até dezembro de 2025**
- ✅ **Fazendas de grande porte** com muitos animais e movimentações
- ✅ **Movimentações mensais** (vendas, nascimentos, compras)
- ✅ **Lançamentos financeiros mensais** (fluxo de caixa, custos, receitas)
- ✅ Popular dados em todos os módulos disponíveis
- ✅ Criar categorias padrão se não existirem
- ✅ Criar uma propriedade de exemplo se não houver nenhuma

### **Opção 2: Popular uma Fazenda Específica**

```bash
python manage.py popular_todos_modulos_todas_fazendas --propriedade-id 1
```

Substitua `1` pelo ID da propriedade desejada.

### **Opção 3: Pular Dados Existentes**

```bash
python manage.py popular_todos_modulos_todas_fazendas --skip-existing
```

Este comando não sobrescreverá dados que já existem.

### **Opção 4: Simular Outro Ano**

```bash
python manage.py popular_todos_modulos_todas_fazendas --ano 2024
```

Simula um ano diferente (padrão: 2025).

## 📊 Módulos Populados - Simulação Completa 2025

O comando popula dados nos seguintes módulos com **dados mensais ao longo de todo o ano**:

### ✅ **1. Módulo Pecuária**
- **Inventário inicial em janeiro 2025** (fazenda grande: 100-500 bezerros, 200-800 vacas, etc.)
- Parâmetros de Projeção
- Categorias de Animais (se não existirem)

### ✅ **2. Módulo Rastreabilidade (PNIB)**
- **Muitos animais individuais** (até 200 por categoria em fazendas grandes)
- Brincos de identificação
- Histórico de movimentações

### ✅ **3. Módulo Reprodução**
- **15 touros** (fazendas grandes) ou 3 (pequenas)
- Estações de Monta (janeiro a abril 2025)
- **IATFs mensais** (janeiro a abril, 10 por mês)
- Monta Natural (se disponível)

### ✅ **4. Módulo Operacional**
- Tanques de Combustível
- **12 abastecimentos mensais** (um por mês em 2025)
- Estoque de Suplementação
- Equipamentos (Trator, Pulverizador, Caminhão)

### ✅ **5. Módulo Funcionários**
- **6 funcionários** (fazendas grandes) ou 3 (pequenas)
- **12 folhas de pagamento mensais** (uma por mês em 2025)

### ✅ **6. Módulo Compras**
- Fornecedores (Ração, Medicamentos, Combustível)
- **12 ordens de compra mensais** (uma por mês em 2025)

### ✅ **7. Módulo Pastagens**
- Pastagens cadastradas (Brachiaria, Panicum, Mombaça)
- Rotação de pastagens (se disponível)

### ✅ **8. Módulo Financeiro**
- Custos Fixos (Mão de Obra, Energia, Combustível, Manutenção)
- Custos Variáveis (Ração, Medicamentos)
- Financiamentos
- Bens Imobilizados (Trator, Galpão, Caminhão)

### ✅ **9. Movimentações Anuais (NOVO!)**
- **Vendas mensais** (março, junho, setembro, dezembro - 20-100 animais por venda)
- **Nascimentos mensais** (setembro a dezembro - 30-150 bezerros por mês)
- **Compras esporádicas** (fevereiro, maio, agosto - 10-50 matrizes)
- **12 lançamentos de fluxo de caixa mensais** (receitas, custos, lucro)

## 📝 Exemplo de Saída

```
🚀 Iniciando população de dados em TODOS os módulos...
📋 Verificando categorias padrão...
  ✅ Categoria Bezerro(a) criada
  ✅ Categoria Novilho(a) criada
  ...

📊 Processando 3 propriedade(s)...

============================================================
🏠 Propriedade 1/3: Fazenda São José
============================================================
  🐄 Módulo Pecuária...
    ✅ Inventário e parâmetros criados
  🏷️ Módulo Rastreabilidade (PNIB)...
    ✅ 50 animais individuais criados
  👶 Módulo Reprodução...
    ✅ Touros e estações de monta criados
  ⚙️ Módulo Operacional...
    ✅ Dados operacionais criados
  👥 Módulo Funcionários...
    ✅ Funcionários criados
  🛒 Módulo Compras...
    ✅ Fornecedores criados
  🌿 Módulo Pastagens...
    ✅ Pastagens criadas
  💰 Módulo Financeiro...
    ✅ Dados financeiros criados
✅ Propriedade Fazenda São José concluída!

🎉 Processamento concluído para 3 propriedade(s)!
```

## ⚠️ Observações Importantes

1. **Dados de Exemplo**: Os dados criados são apenas para teste e demonstração
2. **Não Sobrescreve**: Por padrão, o comando atualiza dados existentes. Use `--skip-existing` para evitar isso
3. **Módulos Opcionais**: Se algum módulo não estiver disponível, o comando continuará com os outros
4. **Transações**: O comando usa transações do banco de dados para garantir consistência

## 🔧 Solução de Problemas

### **Erro: "Nenhuma propriedade encontrada"**
- O comando criará automaticamente uma propriedade de exemplo
- Ou cadastre uma propriedade manualmente antes de executar

### **Erro: "Modelo não disponível"**
- Alguns módulos podem não estar instalados
- O comando continuará com os módulos disponíveis

### **Dados não aparecem**
- Verifique se a propriedade foi processada corretamente
- Verifique os logs de erro no console
- Execute novamente com `--skip-existing` para evitar duplicatas

## 📞 Suporte

Se encontrar problemas, verifique:
1. Logs do comando no console
2. Se todas as migrações foram aplicadas: `python manage.py migrate`
3. Se as propriedades estão cadastradas corretamente

---

**Última atualização:** Dezembro 2024

