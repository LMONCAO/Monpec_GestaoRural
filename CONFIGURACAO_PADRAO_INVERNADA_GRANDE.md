# CONFIGURAÇÃO PADRÃO - FAZENDA INVERNADA GRANDE

## REGRAS PERMANENTES DE PROJEÇÃO

Este documento descreve as regras **PERMANENTES** e **PADRÃO** para geração de projeções da Fazenda Invernada Grande. Estas regras estão implementadas no script `garantir_configuracao_invernada_grande_apos_projecao.py` e **DEVEM SER APLICADAS** após cada nova geração de projeção.

---

## 1. INVENTÁRIO INICIAL

### Regra Principal
**SEM INVENTÁRIO INICIAL**

### Implementação
- O inventário inicial de "Vacas Descarte" deve ser **DELETADO** após cada nova projeção
- Não deve haver inventário inicial cadastrado para esta categoria

---

## 2. TRANSFERÊNCIAS DE ENTRADA

### Regra Principal
**Receber 512 vacas descarte da Canta Galo em 2022**

### Implementação
- Buscar transferências de saída (`TRANSFERENCIA_SAIDA`) da Canta Galo para 2022
- Criar transferências de entrada (`TRANSFERENCIA_ENTRADA`) correspondentes na Invernada Grande
- Data: 15/01/2022
- Quantidade: 512 vacas descarte

### Código
- Script: `garantir_configuracao_invernada_grande_apos_projecao.py`
- Método: PASSO 3

---

## 3. VENDAS MENSAIS

### Regra Principal
**Vender 80 cabeças mensais até zerar o saldo**

### Implementação
- Primeira venda: 1 mês após a transferência (15/02/2022)
- Vendas mensais de 80 cabeças cada
- Última venda: quantidade restante (pode ser menor que 80)
- Período: fevereiro a agosto de 2022
- Cliente: JBS
- Valores:
  - Peso médio: 450 kg
  - Valor por kg: R$ 6,50
  - Valor por animal: R$ 2.925,00

### Código
- Script: `garantir_configuracao_invernada_grande_apos_projecao.py`
- Método: PASSO 5

---

## 4. SALDO ZERADO

### Regra Principal
**Saldo deve ser ZERADO em 2023, 2024 e 2025**

### Implementação
- Todas as 512 vacas devem ser vendidas em 2022
- Saldo final de 2022: 0
- Saldo inicial de 2023: 0 (baseado no saldo final de 2022)
- Saldo final de 2023: 0
- Saldo inicial de 2024: 0
- Saldo final de 2024: 0
- Saldo inicial de 2025: 0
- Saldo final de 2025: 0

### Verificação
- Deletar qualquer movimentação incorreta de 2025
- Garantir que não há inventário inicial

---

## 5. EXECUÇÃO APÓS NOVA PROJEÇÃO

### Script Obrigatório
**`garantir_configuracao_invernada_grande_apos_projecao.py`**

### Quando Executar
**SEMPRE após gerar uma nova projeção para Invernada Grande**

### O que o Script Faz
1. Deleta inventário inicial
2. Busca transferências de saída da Canta Galo (2022)
3. Cria entradas correspondentes na Invernada Grande
4. Deleta vendas existentes para recriar
5. Cria vendas mensais de 80 cabeças
6. Deleta movimentações incorretas de 2025

---

## 6. INTEGRAÇÃO AUTOMÁTICA

### Opção 1: Executar Manualmente
Após cada nova projeção, execute:
```bash
python garantir_configuracao_invernada_grande_apos_projecao.py
```

### Opção 2: Integrar na View (Futuro)
Modificar `gestao_rural/views.py` para chamar automaticamente após gerar projeção.

---

## 7. RESUMO DAS MOVIMENTAÇÕES

### 2022
- **Entrada:** +512 vacas (15/01/2022) - Transferência da Canta Galo
- **Vendas:** 
  - 80 vacas (15/02/2022)
  - 80 vacas (15/03/2022)
  - 80 vacas (15/04/2022)
  - 80 vacas (15/05/2022)
  - 80 vacas (15/06/2022)
  - 80 vacas (15/07/2022)
  - 32 vacas (15/08/2022)
- **Total vendido:** 512 vacas
- **Saldo final:** 0

### 2023
- **Saldo inicial:** 0
- **Movimentações:** Nenhuma
- **Saldo final:** 0

### 2024
- **Saldo inicial:** 0
- **Movimentações:** Nenhuma
- **Saldo final:** 0

### 2025
- **Saldo inicial:** 0
- **Movimentações:** Nenhuma (outras categorias podem ter movimentações)
- **Saldo final:** 0 (para Vacas Descarte)

---

## 8. MANUTENÇÃO

### Ao Modificar o Código
1. **NUNCA** remover a lógica de deletar inventário inicial
2. **SEMPRE** verificar transferências da Canta Galo antes de criar entradas
3. **SEMPRE** criar vendas mensais de 80 cabeças
4. **SEMPRE** deletar movimentações incorretas de 2025

### Ao Gerar Nova Projeção
1. Gerar projeção normalmente pelo sistema
2. **OBRIGATÓRIO:** Executar `garantir_configuracao_invernada_grande_apos_projecao.py`
3. Verificar se as planilhas de 2022, 2023, 2024 e 2025 aparecem
4. Verificar se o saldo está zerado em todos os anos

---

## 9. HISTÓRICO DE ALTERAÇÕES

### 2025-01-XX
- **Implementada** configuração padrão permanente
- **Criado** script de garantia de configuração
- **Documentada** todas as regras e procedimentos

---

## 10. CONTATO

Em caso de dúvidas ou necessidade de alteração destas regras, consulte a documentação do código ou o desenvolvedor responsável.

---

**ÚLTIMA ATUALIZAÇÃO**: 2025-01-XX
**VERSÃO**: 1.0
**STATUS**: ATIVA E PERMANENTE

**SCRIPT OBRIGATÓRIO**: `garantir_configuracao_invernada_grande_apos_projecao.py`











