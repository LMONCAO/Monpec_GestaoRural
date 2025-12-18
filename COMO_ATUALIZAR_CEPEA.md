# 📊 Como Atualizar Preços CEPEA

Este documento explica como atualizar os preços CEPEA no sistema MONPEC.

## 🎯 O que são Preços CEPEA?

Os preços CEPEA (Centro de Estudos Avançados em Economia Aplicada) são valores médios de mercado de gado por estado, ano e categoria de animal. O sistema usa esses preços para calcular automaticamente os valores unitários dos animais nas projeções.

## 📝 Métodos de Atualização

### 1. **Atualização Manual Individual**

Atualiza um preço específico:

```bash
python manage.py atualizar_precos_cepea \
    --uf SP \
    --ano 2024 \
    --categoria BOI \
    --preco-medio 3200.00 \
    --preco-minimo 3000.00 \
    --preco-maximo 3400.00 \
    --fonte CEPEA
```

**Parâmetros:**
- `--uf`: Sigla do estado (SP, MG, MT, etc.)
- `--ano`: Ano de referência
- `--categoria`: Tipo de categoria (BEZERRO, BEZERRA, GARROTE, NOVILHA, BOI, BOI_MAGRO, PRIMIPARA, MULTIPARA, VACA_DESCARTE, TOURO)
- `--preco-medio`: Preço médio em R$/cabeça (obrigatório)
- `--preco-minimo`: Preço mínimo (opcional)
- `--preco-maximo`: Preço máximo (opcional)
- `--fonte`: Fonte dos dados (padrão: CEPEA)

### 2. **Cálculo Automático**

Calcula preços automaticamente usando fatores de correção por estado:

```bash
# Para um estado específico e intervalo de anos
python manage.py atualizar_precos_cepea \
    --calcular-automatico \
    --uf SP \
    --anos 2022-2026

# Para todos os estados e anos específicos
python manage.py atualizar_precos_cepea \
    --calcular-automatico \
    --anos 2024,2025,2026

# Para um estado, ano e categoria específicos
python manage.py atualizar_precos_cepea \
    --calcular-automatico \
    --uf MG \
    --ano 2024 \
    --categoria BOI
```

**Como funciona:**
- Usa valores base por categoria
- Aplica fatores de correção por estado
- Ajusta por inflação (5% ao ano a partir de 2023)

### 3. **Importação via CSV**

Importa preços de um arquivo CSV:

```bash
python manage.py atualizar_precos_cepea --csv precos_cepea.csv
```

**Formato do CSV:**
```csv
UF,Ano,Categoria,PrecoMedio,PrecoMinimo,PrecoMaximo
SP,2024,BOI,3200.00,3000.00,3400.00
SP,2024,BEZERRO,850.00,800.00,900.00
MG,2024,BOI,3100.00,2900.00,3300.00
MT,2024,BOI,2900.00,2700.00,3100.00
```

**Exemplo de arquivo completo:**
```csv
UF,Ano,Categoria,PrecoMedio,PrecoMinimo,PrecoMaximo
SP,2022,BEZERRO,800.00,750.00,850.00
SP,2022,BEZERRA,1200.00,1100.00,1300.00
SP,2022,GARROTE,1800.00,1700.00,1900.00
SP,2022,NOVILHA,2200.00,2100.00,2300.00
SP,2022,BOI,2800.00,2700.00,2900.00
SP,2023,BEZERRO,840.00,790.00,890.00
SP,2023,BEZERRA,1260.00,1160.00,1360.00
...
```

### 4. **Listar Preços Cadastrados**

Visualiza todos os preços cadastrados:

```bash
python manage.py atualizar_precos_cepea --listar
```

**Saída:**
```
Total de preços cadastrados: 150

UF   Ano    Categoria            Preço Médio     Fonte           Atualizado          
----------------------------------------------------------------------------------------------------
SP   2024   Boi (24-36 meses)    R$     3.200,00 CEPEA           26/11/2025 17:30
SP   2024   Bezerro (0-12 meses) R$       850,00 CEPEA           26/11/2025 17:30
MG   2024   Boi (24-36 meses)    R$     3.100,00 CEPEA           26/11/2025 17:30
...
```

## 🔧 Atualização via Admin do Django

1. Acesse o admin do Django: `http://localhost:8000/admin/`
2. Navegue até **Gestão Rural > Preços CEPEA**
3. Clique em **Adicionar Preço CEPEA** ou edite um existente
4. Preencha os campos:
   - **UF**: Estado (ex: SP, MG, MT)
   - **Ano**: Ano de referência
   - **Tipo de Categoria**: Tipo de animal
   - **Preço Médio**: Valor médio em R$/cabeça
   - **Preço Mínimo**: Valor mínimo (opcional)
   - **Preço Máximo**: Valor máximo (opcional)
   - **Fonte**: Fonte dos dados (padrão: CEPEA)

## 📊 Categorias Disponíveis

- **BEZERRO**: Bezerro (0-12 meses) - Macho
- **BEZERRA**: Bezerra (0-12 meses) - Fêmea
- **GARROTE**: Garrote (12-24 meses) - Macho
- **NOVILHA**: Novilha (12-24 meses) - Fêmea
- **BOI**: Boi (24-36 meses)
- **BOI_MAGRO**: Boi Magro (24-36 meses)
- **PRIMIPARA**: Primípara (24-36 meses)
- **MULTIPARA**: Multípara (>36 meses)
- **VACA_DESCARTE**: Vaca Descarte (>36 meses)
- **TOURO**: Touro (>36 meses)

## 🎯 Exemplos Práticos

### Exemplo 1: Atualizar preço de Boi em SP para 2024
```bash
python manage.py atualizar_precos_cepea \
    --uf SP \
    --ano 2024 \
    --categoria BOI \
    --preco-medio 3200.00
```

### Exemplo 2: Calcular preços automaticamente para SP (2022-2026)
```bash
python manage.py atualizar_precos_cepea \
    --calcular-automatico \
    --uf SP \
    --anos 2022-2026
```

### Exemplo 3: Importar preços de arquivo CSV
```bash
python manage.py atualizar_precos_cepea --csv dados_cepea_2024.csv
```

### Exemplo 4: Listar todos os preços
```bash
python manage.py atualizar_precos_cepea --listar
```

## 📌 Fatores de Correção por Estado

O sistema aplica automaticamente fatores de correção baseados em dados históricos:

- **SP**: +10%
- **MG**: +5%
- **MT/MS**: -5%
- **PR**: +8%
- **SC**: +12%
- **RS**: +10%
- **BA**: -8%
- **PA**: -12%
- **RO/AC**: -10%
- **Outros**: Sem ajuste

## 🔄 Como o Sistema Usa os Preços

1. **Prioridade 1**: Preço CEPEA cadastrado no banco de dados
2. **Prioridade 2**: Cálculo automático usando fatores de correção
3. **Prioridade 3**: Valores padrão do sistema

Quando uma projeção é gerada:
- O sistema busca o preço CEPEA para o estado da propriedade
- Usa o ano da projeção
- Aplica o preço à categoria correspondente
- Se não encontrar, calcula automaticamente

## ⚠️ Observações Importantes

1. **Atualização Regular**: Recomenda-se atualizar os preços CEPEA periodicamente (trimestral ou semestralmente)
2. **Fonte dos Dados**: Sempre informe a fonte dos dados para rastreabilidade
3. **Validação**: Verifique os preços antes de salvar, especialmente em importações em massa
4. **Anos Futuros**: Para projeções futuras, o sistema calcula automaticamente com base na inflação estimada

## 📞 Suporte

Para dúvidas ou problemas, consulte a documentação do sistema ou entre em contato com o suporte técnico.

























