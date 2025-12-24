# Resumo: Impostos de Renda e Exportação para Excel

## ✅ Impostos de Renda Calculados e Preenchidos

### Tabela Progressiva de IR (Pessoa Física)
- **Faixa 1**: R$ 0,00 a R$ 22.847,76 → **0%** (Isento)
- **Faixa 2**: R$ 22.847,77 a R$ 33.919,80 → **7,5%** (Dedução: R$ 1.713,58)
- **Faixa 3**: R$ 33.919,81 a R$ 45.012,60 → **15%** (Dedução: R$ 4.257,57)
- **Faixa 4**: R$ 45.012,61 a R$ 55.976,16 → **22,5%** (Dedução: R$ 7.633,51)
- **Faixa 5**: Acima de R$ 55.976,16 → **27,5%** (Dedução: R$ 10.432,32)

### Impostos Calculados por Ano

#### 2022
- Lucro Líquido Total: R$ 7.699.997,38
- IR Total: R$ 2.107.066,96
- Distribuído proporcionalmente entre as 4 propriedades

#### 2023
- Lucro Líquido Total: R$ 7.100.004,96
- IR Total: R$ 1.942.069,04

#### 2024
- Lucro Líquido Total: R$ 9.877.991,63
- IR Total: R$ 2.706.015,38

#### 2025
- Lucro Líquido Total: R$ 6.200.008,30
- IR Total: R$ 1.694.569,96

### Como o IR é Calculado
1. **Lucro Líquido** = Receitas - Despesas Operacionais
2. **IR** = (Lucro Líquido × Alíquota da Faixa) - Dedução da Faixa
3. O IR é distribuído proporcionalmente entre as propriedades baseado no lucro de cada uma

## ✅ Exportação para Excel

### Funcionalidades Implementadas

1. **Planilha DRE (Demonstração do Resultado do Exercício)**
   - Receita Bruta
   - Deduções (ICMS, Funrural, Outros Impostos)
   - Receita Líquida
   - Custo dos Produtos Vendidos (CPV)
   - Lucro Bruto
   - Despesas Operacionais
   - Resultado Operacional
   - Resultado Não Operacional
   - Resultado Antes do IR (LAIR)
   - Provisão de Impostos (IRPJ)
   - Resultado Líquido do Exercício

2. **Planilha Balanço Patrimonial**
   - Ativo Total (Imobilizado + Rebanho)
   - Passivo (Dívidas)
   - Patrimônio Líquido

3. **Planilha Faturamento Contábil**
   - Faturamento mensal por propriedade
   - Total por mês
   - Total anual por propriedade
   - Total geral consolidado

### Como Usar

1. Acesse o relatório DRE consolidado
2. Clique no botão **"Exportar para Excel"**
3. O arquivo será baixado com 3 planilhas:
   - **DRE**: Demonstração do Resultado do Exercício
   - **Balanço Patrimonial**: Ativo, Passivo e Patrimônio Líquido
   - **Faturamento Contábil**: Receitas mensais detalhadas

### Formato do Arquivo
- Nome: `DRE_Balanco_[Nome_Produtor]_[Ano].xlsx`
- Formato: Excel (.xlsx)
- Compatível com Microsoft Excel, LibreOffice Calc, Google Sheets

## 📋 Dados Incluídos

### DRE
- Todos os valores com centavos (não redondos)
- Códigos contábeis conforme padrão brasileiro
- Valores negativos entre parênteses
- Totais destacados em negrito

### Balanço Patrimonial
- Ativo: Bens Imobilizados + Rebanho
- Passivo: Dívidas (SCR)
- Patrimônio Líquido: Ativo - Passivo

### Faturamento Contábil
- Receitas mensais de cada propriedade
- Total por mês (soma de todas as propriedades)
- Total anual por propriedade
- Total geral consolidado

## ✅ Status

- [x] Cálculo de Impostos de Renda implementado
- [x] Preenchimento automático de IR nas Receitas Anuais
- [x] Exportação DRE para Excel
- [x] Exportação Balanço Patrimonial para Excel
- [x] Exportação Faturamento Contábil para Excel
- [x] Botão de exportação no relatório DRE
- [x] Formatação profissional das planilhas

