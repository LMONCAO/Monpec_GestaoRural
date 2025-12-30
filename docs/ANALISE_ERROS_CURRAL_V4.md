# Análise de Erros e Funcionalidades Não Implementadas - Curral V4

**Data da Análise:** 2025-01-XX  
**Sistema:** Curral Inteligente (V4)  
**Arquivo Principal:** `gestao_rural/views_curral.py` (função `curral_dashboard_v4`)  
**Template:** `templates/gestao_rural/curral_dashboard_v2.html`

---

## 🔴 PROBLEMAS CRÍTICOS ENCONTRADOS

### 1. **Cálculo de Desempenho de Peso NÃO Implementado no Backend**

**Localização:** `gestao_rural/views_curral.py` - função `curral_identificar_codigo` (linhas 1277-1424)

**Problema:**
A API retorna `pesagem_atual` e `pesagem_anterior`, mas **NÃO calcula**:
- `periodo_dias` (diferença em dias entre as pesagens)
- `ganho_peso` (diferença de peso entre as duas pesagens)
- `ganho_peso_diario` (ganho médio diário)

**Código Atual:**
```python
# Linha 1410-1411 - Apenas serializa as pesagens, não calcula métricas
'pesagem_atual': serializar_pesagem(pesagem_atual),
'pesagem_anterior': serializar_pesagem(pesagem_anterior),
```

**Impacto:**
- Campos "Períodos em Dias", "Ganho Diário" e "Ganho Total de Peso" sempre mostram "—"
- Mensagem "Desempenho de peso não disponível" aparece mesmo quando há dados suficientes
- O JavaScript tenta calcular no frontend (linhas 1582-1629 do template), mas falha se não houver datas corretas

**Solução Necessária:**
Adicionar cálculo no backend após obter as pesagens:
```python
# Calcular métricas de desempenho
periodo_dias = None
ganho_peso = None
ganho_peso_diario = None

if pesagem_atual and pesagem_anterior:
    if pesagem_atual.peso_kg is not None and pesagem_anterior.peso_kg is not None:
        ganho_peso = float(pesagem_atual.peso_kg) - float(pesagem_anterior.peso_kg)
        periodo_dias = (pesagem_atual.data_evento.date() - pesagem_anterior.data_evento.date()).days
        if periodo_dias > 0:
            ganho_peso_diario = ganho_peso / periodo_dias
```

E incluir no JSON de resposta:
```python
'periodo_dias': periodo_dias,
'ganho_peso': ganho_peso,
'ganho_peso_diario': ganho_peso_diario,
```

---

### 2. **Desconexão entre "Animais Trabalhados" e Tabela de Animais na Sessão**

**Localização:** 
- Backend: `gestao_rural/views_curral.py` - função `curral_dashboard_v4` (linha 820)
- Frontend: `templates/gestao_rural/curral_dashboard_v2.html` (linhas 20745-20844)

**Problema:**
- O contador "ANIMAIS TRABALHADOS: 129" vem de `stats_sessao.animais_processados` que conta eventos da sessão no banco
- A tabela "ANIMAIS NA SESSÃO" usa `window.animaisRegistradosTabela` que é populada apenas quando animais são processados **na sessão atual** via JavaScript
- Se a página for recarregada, `window.animaisRegistradosTabela` fica vazia, mas o contador do backend ainda mostra 129

**Código Problemático:**
```python
# Backend - linha 820
'animais_processados': animais_unicos,  # Conta eventos no banco
```

```javascript
// Frontend - linha 20760
if (window.animaisRegistradosTabela.length === 0) {
  // Mostra mensagem "Nenhum animal registrado ainda"
  // Mas o contador mostra 129!
}
```

**Impacto:**
- Usuário vê "129 animais trabalhados" mas a tabela está vazia
- Animais processados em sessões anteriores não aparecem na tabela após recarregar a página
- Inconsistência visual confunde o usuário

**Solução Necessária:**
1. **Opção A:** Carregar animais da sessão do banco ao inicializar a página
   - Buscar eventos da sessão ativa via API
   - Popular `window.animaisRegistradosTabela` com dados do backend
   
2. **Opção B:** Sincronizar o contador com a tabela
   - O contador deve mostrar apenas animais na tabela atual
   - Ou a tabela deve carregar animais do banco ao inicializar

---

### 3. **Discrepância entre "Peso Total" e "Peso Atual" na Balança**

**Localização:** `templates/gestao_rural/curral_dashboard_v2.html` (linhas 304-313, 7391-7392)

**Problema:**
- "PESO TOTAL: 389,0 kg" é a **soma de todos os pesos das pesagens da sessão** (linha 304)
- "PESO ATUAL: 305,2 kg" é o **peso do animal atual** sendo visualizado
- A discrepância é **normal** se houver múltiplos animais pesados na sessão

**Análise:**
O código está correto:
- `balancaPesoTotal` (linha 304): Soma de todas as pesagens da sessão
- `pesoAtualValorV2` (linha 1576): Peso do animal atual

**Observação:**
A diferença entre os valores é esperada quando há múltiplos animais pesados. Se o usuário espera que "Peso Total" seja o peso do animal atual, então há uma confusão de nomenclatura. Considerar renomear para "Peso Total da Sessão" ou "Soma dos Pesos".

---

### 4. **Campos da Ficha Cadastral Não Preenchidos**

**Localização:** 
- `templates/gestao_rural/curral_dashboard_v2.html` (linha 16691 - função `atualizarFichaCadastralV4`)
- Função `processarAnimalIdentificado` (linha 12310) chama outras funções mas não chama diretamente `atualizarFichaCadastralV4`

**Problema:**
Vários campos mostram "—" mesmo quando o animal está carregado:
- CÓDIGO ELETRÔNICO
- SISBOV
- RAÇA
- SEXO
- CATEGORIA
- PASTO/LOTE
- STATUS BND
- COTA HILTON
- Nº MANEJO
- NASCIMENTO
- ÚLTIMO PESO
- STATUS REPRODUTIVO

**Causa:**
A função `processarAnimalIdentificado` (linha 12310) chama:
- `atualizarScannerResumoV2` (atualiza card de identificação)
- `atualizarResumoPesagemV2` (atualiza balança)
- `abrirPopupBrinco` (abre popup)

Mas **NÃO chama** `atualizarFichaCadastralV4` que é a função responsável por preencher a ficha cadastral completa (linha 16691).

**Verificação:**
Busca por `atualizarFichaCadastralV4` no template retorna **ZERO resultados** de chamadas. A função existe mas **NUNCA é chamada**!

**Solução:**
Adicionar chamada para `atualizarFichaCadastralV4` na função `processarAnimalIdentificado`:
```javascript
// Na função processarAnimalIdentificado, após atualizarScannerResumoV2 (linha ~12364)
if (typeof window.atualizarFichaCadastralV4 === 'function') {
  console.log('📋 Atualizando ficha cadastral V4');
  window.atualizarFichaCadastralV4(dados);
  sucesso = true;
}
```

---

## 🟡 PROBLEMAS MENORES / MELHORIAS

### 5. **Campo "PESO (KG)" com Mensagem "Identifique o"**

**Problema:**
O campo de entrada de peso mostra "Identifique o" como placeholder/mensagem, o que não é claro para o usuário.

**Solução:**
Alterar para mensagem mais clara: "Digite o peso em kg" ou "Aguardando identificação do animal"

---

### 6. **Módulos de Configuração Sem Feedback Visual**

**Problema:**
Os módulos (Pesagem, Sanitário, Reprodução, Movimentação) são clicáveis mas não mostram se estão ativos/configurados.

**Solução:**
Adicionar estado visual (cor, ícone, badge) quando um módulo está ativo.

---

### 7. **Progresso da Sessão com Valores "—"**

**Localização:** 
- Backend: `gestao_rural/views_curral.py` - função `curral_stats_sessao_api` (linha 3677)
- Frontend: `templates/gestao_rural/curral_dashboard_v2.html` (linhas 1444-1482)

**Problema:**
- "ANIMAIS PLANEJADOS: —"
- "ANIMAIS RESTANTES: —"
- Barra de progresso em 0%

**Causa:**
A API `curral_stats_sessao_api` **NÃO retorna** `animais_planejados` (que deveria vir de `sessao_ativa.quantidade_esperada`). O modelo `CurralSessao` tem o campo `quantidade_esperada` (linha 3137 do models.py), mas ele não está sendo incluído na resposta da API.

**Código Atual:**
```python
# Linha 3702-3717 - API não inclui quantidade_esperada
stats = {
    'sessao_ativa': True,
    'animais_processados': animais_unicos,
    # FALTA: 'animais_planejados': sessao_ativa.quantidade_esperada,
}
```

**Solução:**
Adicionar `quantidade_esperada` na resposta da API:
```python
stats = {
    'sessao_ativa': True,
    'animais_processados': animais_unicos,
    'animais_planejados': sessao_ativa.quantidade_esperada,  # ADICIONAR
    # ... resto dos campos
}
```

---

## 📋 CHECKLIST DE VERIFICAÇÃO

### Backend (`gestao_rural/views_curral.py`)

- [ ] Função `curral_identificar_codigo` calcula `periodo_dias`, `ganho_peso` e `ganho_peso_diario`
- [ ] Função `curral_dashboard_v4` retorna lista de animais processados na sessão
- [ ] Função `curral_dashboard_v4` retorna `quantidade_planejada` da sessão
- [ ] API retorna todos os campos necessários para preencher a ficha cadastral

### Frontend (`templates/gestao_rural/curral_dashboard_v2.html`)

- [ ] Função `preencherFichaCadastralV2` preenche todos os campos corretamente
- [ ] Função `atualizarResumoPesagemV2` calcula desempenho quando dados estão disponíveis
- [ ] Função `atualizarTabelaAnimaisRegistrados` carrega animais do backend ao inicializar
- [ ] Função `atualizarProgressoSessao` calcula progresso corretamente
- [ ] Lógica de "Peso Total" vs "Peso Atual" está clara e correta
- [ ] Placeholder do campo de peso está claro

---

## 🔧 PRIORIDADES DE CORREÇÃO

1. **ALTA:** Calcular desempenho de peso no backend (#1)
2. **ALTA:** Sincronizar tabela de animais com contador (#2)
3. **MÉDIA:** Preencher campos da ficha cadastral (#4)
4. **MÉDIA:** Corrigir lógica de Peso Total vs Peso Atual (#3)
5. **BAIXA:** Melhorar feedback visual dos módulos (#6)
6. **BAIXA:** Corrigir progresso da sessão (#7)

---

## 📝 NOTAS ADICIONAIS

- O código JavaScript está bem estruturado, mas há dependência excessiva de cálculos no frontend
- Recomenda-se mover cálculos complexos para o backend para garantir consistência
- A API `curral_identificar_codigo` retorna dados suficientes, mas faltam métricas calculadas
- Há múltiplas funções JavaScript que fazem coisas similares (ex: `atualizarListaAnimaisTrabalhados` e `atualizarTabelaAnimaisRegistrados`), considerar unificação

---

**Fim da Análise**


