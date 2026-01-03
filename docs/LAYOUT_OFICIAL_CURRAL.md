# Layout Oficial do Curral Inteligente

## Status: DEFINITIVO E OFICIAL

**Data de Definição:** 19/12/2025

## Arquivo Oficial

O layout oficial está definido no arquivo:
- `templates/gestao_rural/curral_dashboard_v2.html`

Este é o **ÚNICO** layout que deve ser usado para o Curral Inteligente.

## Views que Usam Este Layout

Todas as seguintes views usam o mesmo template oficial:
- `curral_dashboard_v3` → usa `curral_dashboard_v2.html`
- `curral_dashboard_v4` → usa `curral_dashboard_v2.html`
- `curral_painel` → usa `curral_dashboard_v2.html` (verificar)

## Regras de Modificação

### ✅ PERMITIDO

Melhorias futuras podem ser feitas APENAS em:

1. **Modais Adicionais**
   - JavaScript dos modais
   - CSS específico dos modais
   - Funcionalidades dentro dos modais

2. **Programação/Backend**
   - Lógica de negócio
   - APIs e endpoints
   - Processamento de dados
   - Funcionalidades JavaScript (exceto alterações estruturais no layout)

3. **Conteúdo Dinâmico**
   - Dados exibidos nos cards (via JavaScript)
   - Valores preenchidos dinamicamente
   - Listas e tabelas populadas por JavaScript

### ❌ NÃO PERMITIDO

**NÃO ALTERAR:**

1. **Estrutura HTML dos Cards Principais**
   - Não mudar a estrutura dos cards
   - Não alterar classes principais
   - Não modificar o layout grid (42% 58%)

2. **CSS Estrutural**
   - Não alterar tamanhos dos cards
   - Não mudar posicionamento
   - Não modificar cores principais
   - Não alterar proporções do layout

3. **Classes Principais**
   - `.card-curral`
   - `.curral-v2-wrapper`
   - `.curral-main-container`
   - `.configuracao-sessao-wrapper`
   - Estrutura de grid principal

## Estrutura do Layout

O layout oficial possui:
- **Layout de duas colunas:** 42% esquerda / 58% direita
- **Cards principais:** Configuração, Identificação, Ficha Cadastral, Balança
- **Estilo limpo e profissional:** Sem poluição visual
- **Cores originais:** Sem gradientes excessivos

## Backup

O backup original está em:
- `templates/gestao_rural/curral_dashboard_v2_backup_20251219_125718.html`

Em caso de problemas, este backup pode ser usado para restaurar o layout oficial.

## Manutenção

- Qualquer dúvida sobre alterações, consultar este documento
- Alterações estruturais devem ser discutidas antes de implementar
- Este layout é o padrão para todas as propriedades



