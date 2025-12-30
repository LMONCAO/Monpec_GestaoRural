# Dados Realistas do Setor Pecuário - Base de Cálculo

## Pesquisa de Mercado 2024-2025

### Preços e Valores

- **Preço da Arroba**: R$ 280-320 (média: R$ 300/arroba)
- **Peso Médio de Abate**: 450-500 kg (15-16 arrobas)
- **Valor Médio por Cabeça**: R$ 4.800 (16 arrobas × R$ 300)
- **Custo por Cabeça/Ano**: R$ 2.000-2.500 (média: R$ 2.200)

### Margens e Taxas

- **Margem de Lucro**: 15-25% (média: 20%)
- **Taxa de Natalidade**: 70-85% (média: 75%)
- **Taxa de Mortalidade**: 2-4% (média: 3%)
- **Taxa de Venda de Machos**: 80-90% ao ano
- **Taxa de Venda de Fêmeas**: 10-20% ao ano

### Estrutura de Rebanho Típica

Para uma propriedade com ~341 cabeças:

- **Bezerros (0-12 meses)**: 45 cabeças (13%)
- **Bezerras (0-12 meses)**: 42 cabeças (12%)
- **Garrotes (12-24 meses)**: 38 cabeças (11%)
- **Novilhas (12-24 meses)**: 35 cabeças (10%)
- **Bois (24-36 meses)**: 28 cabeças (8%)
- **Vacas Primíparas**: 25 cabeças (7%)
- **Vacas Multíparas**: 120 cabeças (35%)
- **Touros**: 8 cabeças (2%)

### Custos Mensais por Categoria

- **Alimentação**: R$ 15.000/mês
- **Sanidade**: R$ 5.000/mês
- **Mão de Obra**: R$ 12.000/mês
- **Energia e Combustível**: R$ 3.000/mês
- **Manutenção**: R$ 4.000/mês
- **Impostos e Taxas**: R$ 2.000/mês

**Total Despesas Mensais**: ~R$ 41.000/mês

### Receitas Mensais

- **Vendas de Animais**: 15-20 cabeças/mês × R$ 4.800 = R$ 72.000 - R$ 96.000/mês
- **Margem Líquida Mensal**: R$ 31.000 - R$ 55.000/mês

### Suplementação

- **Sal Mineral**: R$ 3,50/kg
- **Ração Concentrada**: R$ 2,80/kg
- **Silagem**: R$ 180,00/tonelada
- **Feno**: R$ 25,00/fardo

### Bens Patrimoniais Típicos

- **Trator**: R$ 300.000 - R$ 400.000 (depreciação: 10%/ano)
- **Caminhão**: R$ 150.000 - R$ 200.000 (depreciação: 12%/ano)
- **Pulverizador**: R$ 40.000 - R$ 50.000 (depreciação: 15%/ano)
- **Balança**: R$ 20.000 - R$ 30.000 (depreciação: 10%/ano)
- **Bebedouros**: R$ 10.000 - R$ 20.000 (depreciação: 8%/ano)

### Funcionários

- **Gerente de Fazenda**: R$ 7.000 - R$ 9.000/mês
- **Vaqueiro**: R$ 3.000 - R$ 4.000/mês
- **Tratorista**: R$ 4.000 - R$ 5.000/mês
- **Auxiliar de Campo**: R$ 2.000 - R$ 3.000/mês

### Pastagens

- **Área Total**: 135 hectares (3 pastagens)
- **Capim Braquiária**: 50 ha
- **Capim Panicum**: 45 ha
- **Capim Tifton**: 40 ha

### Cochos

- **Cochos de Sal**: 3 unidades
- **Cochos de Ração**: 3 unidades
- **Bebedouros**: 3 unidades
- **Cochos Mistos**: 3 unidades

## Resultados Esperados nos Gráficos

Com esses dados, os gráficos devem mostrar:

1. **Evolução do Rebanho**: Crescimento de ~5-8% ao ano
2. **Receitas vs Despesas**: Margem positiva de 20-30%
3. **Vendas Mensais**: R$ 70.000 - R$ 100.000/mês
4. **Custos por Categoria**: Distribuição equilibrada
5. **Projeções**: Tendência de crescimento sustentável

## Como Usar

Execute o comando:

```bash
python manage.py popular_dados_pecuaria_realista
```

Ou use o arquivo batch:

```bash
POPULAR_DADOS_SISTEMA.bat
```

Os dados serão criados para a primeira propriedade do primeiro produtor encontrado, ou você pode especificar:

```bash
python manage.py popular_dados_pecuaria_realista --propriedade-id 1
```





























