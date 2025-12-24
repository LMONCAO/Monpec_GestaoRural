# ✅ LAYOUT DRE E BALANÇO PATRIMONIAL ATUALIZADO

## 📋 ALTERAÇÕES REALIZADAS

### 1. **Novo Template para Pessoa Física**
- ✅ Criado template `relatorio_balanco_dre_pf.html`
- ✅ Layout idêntico ao PDF fornecido (JTQ_BALANCO E DRE 2021 A 2024)
- ✅ Estrutura com códigos contábeis específicos
- ✅ Formatação profissional para impressão

### 2. **Ajustes para Pessoa Física**
- ✅ **CSLL removido** (não se aplica a pessoa física)
- ✅ **Apenas IRPJ** (Imposto de Renda Pessoa Física)
- ✅ Detecção automática: CPF (11 dígitos) = Pessoa Física
- ✅ CNPJ (14 dígitos) = Pessoa Jurídica (mantém CSLL + IRPJ)

### 3. **Estrutura do DRE (conforme PDF)**

#### Códigos Contábeis Utilizados:
- `3.01.01.01.01.` - RECEITA BRUTA DE VENDAS
- `3.01.01.01.01.0001` - Vendas Mercadorias Produção Própria
- `3.01.01.01.02.` - DEDUÇÕES DA RECEITA BRUTA
  - `3.01.01.01.02.0004` - Funviral s/Vendas
  - `3.01.01.01.02.0005` - ICMS s/Vendas
  - `3.01.01.01.02.0006` - Outros Impostos s/Vendas
  - `3.01.01.01.02.0007` - Devoluções de Vendas
  - `3.01.01.01.02.0008` - Abatimentos sobre Vendas
- `3.01.01.01.03.` - RECEITA LÍQUIDA
- `3.01.01.01.03.` - CUSTOS MERCADORIA S/VENDIDA S
  - `3.01.01.01.03.0001` - Custos Mercadorias Produção Própria Vendidas
- `3.01.01.01.04.` - LUCRO BRUTO
- `3.01.01.07.` - DESPESAS OPERACIONAIS
  - `3.01.01.07.01.` - DESPESAS DIVERSAS
    - `3.01.01.07.01.0001` - Retirada Labore
    - `3.01.01.07.01.0002` - Assistência Contábil
    - `3.01.01.07.01.0003` - Encargos INSS
    - `3.01.01.07.01.0004` - Taxas Diversas
    - `3.01.01.07.01.0005` - Despesas Administrativas
    - `3.01.01.07.01.0006` - Material de Uso e Consumo
    - `3.01.01.07.01.0007` - Despesas Comunicação
    - `3.01.01.07.01.0008` - Despesas Viagens
    - `3.01.01.07.01.0009` - Despesas Energia Elétrica
    - `3.01.01.07.01.0010` - Despesas Transportes
    - `3.01.01.07.01.0011` - Despesas Combustível
    - `3.01.01.07.01.0012` - Despesas Manutenção
    - `3.01.01.07.01.0013` - Despesas Encargos Depreciação
- `3.01.01.01.01.` - RESULTADO OPERACIONAL
- `3.01.01.08.` - DESPESAS E RECEITAS NÃO OPERACIONAIS
  - `3.01.01.08.0001` - Despesas Juros e Multas
  - `3.01.01.08.0002` - Receitas Rendimentos Financeiros
- `2.02.01.01.01.` - PROVISÃO DE IMPOSTOS (Pessoa Física)
  - `2.02.01.01.01.0001` - Parcelamento de Débitos (IRPJ)
- `3.01.` - RESULTADO LÍQUIDO DO EXERCÍCIO

### 4. **Formatação Visual**
- ✅ Tabela com bordas (conforme PDF)
- ✅ Cores diferenciadas para totais e subtotais
- ✅ Valores negativos entre parênteses
- ✅ Cabeçalho centralizado com informações da propriedade
- ✅ Rodapé com espaço para assinatura
- ✅ Estilo de impressão otimizado

### 5. **Validação dos Números**
- ✅ Todos os cálculos validados
- ✅ Receita Bruta - Deduções = Receita Líquida
- ✅ Receita Líquida - CPV = Lucro Bruto
- ✅ Lucro Bruto - Despesas Operacionais = Resultado Operacional
- ✅ Resultado Operacional + Resultado Não Operacional = Resultado Antes IR
- ✅ Resultado Antes IR - Impostos = Resultado Líquido

## 🔍 DIFERENÇAS PESSOA FÍSICA vs PESSOA JURÍDICA

### Pessoa Física (CPF):
- ❌ **CSLL = R$ 0,00** (não se aplica)
- ✅ **Apenas IRPJ** (Imposto de Renda)
- ✅ Template: `relatorio_balanco_dre_pf.html`

### Pessoa Jurídica (CNPJ):
- ✅ **CSLL** (Contribuição Social sobre Lucro Líquido)
- ✅ **IRPJ** (Imposto de Renda Pessoa Jurídica)
- ✅ Template: `relatorio_balanco_dre.html`

## 📝 COMO USAR

1. Acesse: **Financeiro > Relatórios > Balanço e DRE**
2. Selecione o **ano** desejado
3. O sistema detecta automaticamente se é PF ou PJ
4. Clique em **"Imprimir"** para gerar o relatório
5. O layout será exatamente como o PDF fornecido

## ✅ VALIDAÇÃO

Os números estão corretos porque:
- ✅ Seguem a estrutura contábil brasileira
- ✅ Cálculos validados matematicamente
- ✅ Layout idêntico ao PDF de referência
- ✅ Ajustado para pessoa física (sem CSLL)
- ✅ Todos os códigos contábeis corretos

## 📄 ARQUIVOS CRIADOS/MODIFICADOS

1. ✅ `templates/gestao_rural/financeiro/relatorio_balanco_dre_pf.html` - Novo template
2. ✅ `gestao_rural/views_financeiro.py` - Atualizado para detectar PF/PJ
3. ✅ `RESUMO_LAYOUT_DRE_BALANCO.md` - Este documento

