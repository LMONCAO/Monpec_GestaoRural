# Estratégia de Refatoração - Fase 1

## Análise do Template

**Template atual:** `templates/gestao_rural/curral_dashboard_v2.html`
- **Total de linhas:** 17.385 linhas
- **CSS block:** linhas 6-4848 (4.842 linhas)
- **Content block:** linha 4852 em diante

## Estratégia de Extração

### Passo 1: Criar Template Principal Simplificado
Criar um novo template que usa includes mas mantém todo o código original temporariamente.

### Passo 2: Extração Gradual
Para cada seção, vamos:
1. Identificar o código da seção no template original
2. Criar um arquivo include separado
3. Substituir no template principal por `{% include %}`
4. Testar para garantir que funciona
5. Continuar com próxima seção

### Seções Identificadas:

1. **CSS Styles** (linhas 6-4848)
   - Inclui: CSS inline + JavaScript inline inicial
   - Arquivo: `curral/includes/css.html`

2. **Header** (aproximadamente linhas 4859-5006)
   - Inclui: Cabeçalho da página, menu, status conexão, sessão ativa
   - Arquivo: `curral/includes/header.html`

3. **Scanner/Brinco** (aproximadamente linhas 5022-5091)
   - Inclui: Input de brinco, resumo do animal identificado
   - Arquivo: `curral/includes/scanner.html`

4. **Pesagem** (aproximadamente linhas 5092-5200)
   - Inclui: Input de peso, botões, informações de pesagem
   - Arquivo: `curral/includes/pesagem.html`

5. **Estatísticas** (aproximadamente linhas 5202-5270)
   - Inclui: Cards de estatísticas, manejos selecionados
   - Arquivo: `curral/includes/estatisticas.html`

6. **Tabela de Animais** (aproximadamente linhas 5274-5320)
   - Inclui: Tabela de animais registrados
   - Arquivo: `curral/includes/tabela_animais.html`

7. **Modais** (aproximadamente linhas 5324+)
   - Inclui: Todos os modais (confirmação, diagnóstico, cadastro estoque, IATF, etc)
   - Arquivo: `curral/includes/modals.html`

8. **Scripts JavaScript** (linhas finais)
   - Inclui: Todo JavaScript inline restante
   - Arquivo: `curral/includes/scripts.html` (temporário, será removido na Fase 2)

## Ordem de Extração (por complexidade crescente):

1. ✅ Estrutura de pastas
2. ⏳ Header (mais simples, isolado)
3. ⏳ Scanner (relativamente independente)
4. ⏳ Pesagem (depende de scanner)
5. ⏳ Estatísticas (independente)
6. ⏳ Tabela de Animais (independente)
7. ⏳ Modais (independentes mas muitos)
8. ⏳ CSS (muito grande, deixar por último)
9. ⏳ Scripts (temporário, será removido na Fase 2)

## Estratégia de Teste

Após cada extração:
1. Verificar se a página carrega sem erros
2. Testar funcionalidade básica (identificar brinco, pesar, gravar)
3. Verificar se não quebrou nada

## Próximos Passos Imediatos:

1. Criar template principal que usa includes
2. Extrair Header primeiro (mais simples)
3. Testar
4. Continuar com as demais seções
