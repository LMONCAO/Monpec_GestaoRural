# Fluxo Perfeito - Curral Inteligente 3.0
## Especificação Completa e Ideal da Página

---

## 📋 ÍNDICE

1. [Visão Geral](#1-visão-geral)
2. [Fluxo de Inicialização](#2-fluxo-de-inicialização)
3. [Fluxo de Identificação de Animal](#3-fluxo-de-identificação-de-animal)
4. [Fluxo de Registro de Pesagem](#4-fluxo-de-registro-de-pesagem)
5. [Fluxo de Registro de Manejos](#5-fluxo-de-registro-de-manejos)
6. [Fluxo de Sessão](#6-fluxo-de-sessão)
7. [Tratamento de Erros](#7-tratamento-de-erros)
8. [Validações](#8-validações)
9. [Estados da Interface](#9-estados-da-interface)
10. [Melhores Práticas](#10-melhores-práticas)

---

## 1. VISÃO GERAL

### 1.1. Objetivo
A página Curral Inteligente 3.0 permite o gerenciamento eficiente de pesagens e manejos bovinos em tempo real durante sessões de trabalho no curral.

### 1.2. Princípios Fundamentais
- ✅ **Simplicidade**: Interface intuitiva, sem fricção
- ✅ **Robustez**: Validações e tratamento de erros em todos os pontos
- ✅ **Performance**: Uso de APIs específicas e otimizadas
- ✅ **Feedback**: Mensagens claras e imediatas ao usuário
- ✅ **Consistência**: Comportamento previsível em todas as ações

---

## 2. FLUXO DE INICIALIZAÇÃO

### 2.1. Carregamento da Página

**Sequência Ideal:**

```
1. CARREGAR TEMPLATE
   ├─ Renderizar HTML base
   ├─ Carregar CSS
   └─ Preparar estrutura DOM

2. INICIALIZAR VARIÁVEIS JAVASCRIPT
   ├─ animalAtualV3 = null
   ├─ brincoAtualV3 = null
   ├─ animaisRegistrados = []
   ├─ manejosSelecionadosV3 = []
   └─ propriedadeId = {{ propriedade_id }}

3. CONFIGURAR URLs DAS APIs
   ├─ identificarUrl = '/propriedade/{id}/curral/api/identificar/'
   ├─ registrarUrl = '/propriedade/{id}/curral/api/registrar/'
   ├─ pesagemUrl = '/propriedade/{id}/curral/api/pesagem/'
   ├─ statsUrl = '/propriedade/{id}/curral/api/stats/'
   └─ statsSessaoUrl = '/propriedade/{id}/curral/api/sessao/stats/'

4. VERIFICAR SESSÃO ATIVA
   ├─ Buscar sessão com status 'ABERTA'
   ├─ Se encontrada:
   │   ├─ Exibir informações da sessão
   │   ├─ Carregar estatísticas da sessão
   │   └─ Habilitar botões de trabalho
   └─ Se não encontrada:
       ├─ Exibir mensagem "Nenhuma sessão ativa"
       └─ Oferecer criar nova sessão

5. CARREGAR ESTATÍSTICAS GERAIS
   ├─ Total de animais
   ├─ Pesagens do dia
   └─ Manejos do dia

6. CONFIGURAR EVENT LISTENERS
   ├─ Enter no campo de busca → buscarBrincoV3()
   ├─ Blur nos campos editáveis → salvar automático
   ├─ Mudanças de data → calcular idade
   └─ Integração com balança (se conectada)

7. FOCAR NO CAMPO DE BUSCA
   └─ brincoInputV3.focus()
```

### 2.2. Validações na Inicialização

**Checklist:**
- [ ] Verificar se `propriedadeId` está definido
- [ ] Verificar se todas as URLs estão configuradas
- [ ] Verificar se CSRF token está disponível
- [ ] Verificar conexão com backend (ping opcional)
- [ ] Verificar se há sessão ativa válida

---

## 3. FLUXO DE IDENTIFICAÇÃO DE ANIMAL

### 3.1. Entrada do Código

**Formas de Entrada Aceitas:**
1. **SISBOV completo** (15 dígitos): `105500370000001`
2. **Número de Manejo** (6 dígitos): `000001`
3. **Brinco/Botton RFID** (código eletrônico)
4. **SISBOV parcial** (8+ dígitos): `10550037`

**Fontes:**
- Digitação manual
- Scanner de código de barras
- Leitor RFID
- Balança conectada (envia código automaticamente)

### 3.2. Processamento da Busca

**Sequência Perfeita:**

```
1. USUÁRIO INSERE CÓDIGO
   └─ Campo: brincoInputV3

2. VALIDAÇÃO INICIAL (Frontend)
   ├─ Verificar se campo não está vazio
   ├─ Limpar código: remover espaços, traços, pontos
   └─ Se vazio após limpeza:
       ├─ mostrarToast('Código inválido...', 'warning')
       └─ RETURN (não continua)

3. NORMALIZAR CÓDIGO
   ├─ Converter para string
   ├─ Trim (remover espaços inicio/fim)
   ├─ Remover caracteres especiais: /\s\-\./g
   └─ Preservar apenas: letras e números

4. EXIBIR LOADING
   └─ mostrarLoading(true)

5. ENVIAR REQUISIÇÃO PARA API
   ├─ URL: identificarUrl + '?codigo=' + encodeURIComponent(codigo)
   ├─ Método: GET (tentar primeiro)
   ├─ Headers:
   │   ├─ X-CSRFToken: csrfToken
   │   ├─ X-Requested-With: XMLHttpRequest
   │   └─ Accept: application/json
   └─ Se GET falhar:
       ├─ Tentar POST como fallback
       └─ Body: { codigo: codigo }

6. VERIFICAR RESPOSTA HTTP
   ├─ Se !response.ok:
   │   ├─ Ler mensagem de erro
   │   ├─ mostrarToast(mensagem, 'error')
   │   └─ mostrarLoading(false)
   │   └─ RETURN
   └─ Continuar processamento

7. PROCESSAR JSON DA RESPOSTA
   ├─ data = await response.json()
   ├─ Verificar se data não é null/undefined
   └─ Se inválido:
       ├─ mostrarToast('Resposta inválida', 'error')
       └─ RETURN

8. TRATAR STATUS DA RESPOSTA
   ├─ Se status === 'erro':
   │   ├─ mostrarToast(data.mensagem, 'error')
   │   └─ RETURN
   ├─ Se status === 'duplicidade':
   │   ├─ abrirModalDuplicidade(data.animais)
   │   └─ RETURN
   ├─ Se status === 'estoque':
   │   ├─ abrirModalCadastroEstoque(data.brinco)
   │   └─ RETURN
   └─ Se status === 'animal':
       └─ CONTINUAR (próxima seção)
```

### 3.3. Animal Encontrado - Preenchimento de Dados

**Sequência Perfeita:**

```
1. ARMAZENAR DADOS
   ├─ animalAtualV3 = data.dados
   └─ brincoAtualV3 = codigo_normalizado

2. ATUALIZAR CAMPO DE BUSCA
   └─ Preferir número de manejo (mais legível):
       brincoInputV3.value = data.dados.numero_manejo || codigo

3. PREENCHER CAMPOS DE IDENTIFICAÇÃO (Read-only)
   ├─ scannerNumeroManejoV3 → data.dados.numero_manejo
   ├─ scannerSisbovV3 → data.dados.codigo_sisbov
   └─ scannerCodigoEletronicoV3 → data.dados.codigo_eletronico

4. PREENCHER CAMPOS EDITÁVEIS
   ├─ scannerRacaV3 → data.dados.raca
   ├─ scannerSexoV3 → converter (F/M)
   ├─ scannerDataNascV3 → formatar data (YYYY-MM-DD)
   ├─ scannerUltimoPesoV3 → data.dados.peso_atual
   ├─ scannerCategoriaV3 → data.dados.categoria_nome
   └─ scannerPastoLoteV3 → data.dados.pasto_nome || data.dados.lote_nome

5. CALCULAR E EXIBIR IDADE
   ├─ Calcular idade a partir de data_nascimento
   └─ scannerIdadeV3 → "X anos e Y meses" ou "Y meses"

6. CONFIGURAR AUTO-SALVAMENTO
   └─ configurarCamposEditaveis()
       ├─ Adicionar listeners para blur/change
       └─ Salvar automaticamente ao sair do campo

7. HABILITAR CAMPOS DE PESAGEM
   ├─ pesoValorV3.disabled = false
   ├─ pesoGravarBtnV3.disabled = false
   └─ btnFinalizarGravarV3.disabled = false

8. LIMPAR CAMPOS DE PESAGEM ANTERIORES
   ├─ pesoRegistradoV3 → '—'
   ├─ pesoUltimoDataV3 → '—'
   ├─ pesoDiasV3 → '—'
   ├─ pesoGanhoTotalV3 → '—'
   └─ pesoGanhoDiaV3 → '—'

9. OCULTAR LOADING
   └─ mostrarLoading(false)

10. EXIBIR TOAST DE SUCESSO
    └─ mostrarToast('Animal identificado com sucesso!', 'success')

11. FOCAR NO CAMPO DE PESO
    └─ setTimeout(() => pesoValorV3.focus(), 100)
```

### 3.4. Animal Não Encontrado

**Fluxo:**

```
1. VERIFICAR TIPO DE CÓDIGO
   ├─ Se 15 dígitos → SISBOV completo
   ├─ Se 6 dígitos → Número de manejo
   └─ Caso contrário → Código genérico

2. EXIBIR MENSAGEM ESPECÍFICA
   ├─ Se SISBOV: 'SISBOV {codigo} não encontrado...'
   ├─ Se Manejo: 'Número de manejo {codigo} não encontrado...'
   └─ Caso contrário: 'Animal não encontrado...'

3. OFERECER CADASTRO
   └─ Se código está em estoque:
       ├─ Abrir modal de cadastro
       └─ Permitir cadastrar novo animal

4. MANTER CÓDIGO NO CAMPO
   └─ NÃO limpar campo (facilita correção)

5. FOCAR NO CAMPO DE BUSCA
   └─ brincoInputV3.focus()
```

### 3.5. Duplicidade (Múltiplos Animais)

**Fluxo:**

```
1. ABRIR MODAL DE DUPLICIDADE
   ├─ Exibir lista de animais encontrados
   ├─ Mostrar informações de cada animal:
   │   ├─ SISBOV
   │   ├─ Número de Manejo
   │   ├─ Brinco/RFID
   │   ├─ Raça
   │   └─ Último Peso
   └─ Permitir seleção

2. USUÁRIO SELECIONA ANIMAL
   ├─ Chamar buscarAnimalPorId(animalId, codigo)
   └─ Continuar fluxo normal de animal encontrado

3. FECHAR MODAL
   └─ Focar no campo de peso após seleção
```

---

## 4. FLUXO DE REGISTRO DE PESAGEM

### 4.1. Entrada do Peso

**Formas de Entrada:**
1. **Manual**: Usuário digita no campo `pesoValorV3`
2. **Automática**: Balança conectada envia via API
3. **Scanner**: Código de barras (peso codificado)

### 4.2. Validações de Peso

**Sequência de Validações:**

```
1. VALIDAÇÃO 1: Campo Não Vazio
   ├─ Se vazio:
   │   ├─ mostrarToast('Informe um peso válido', 'warning')
   │   └─ RETURN

2. VALIDAÇÃO 2: Formato Numérico
   ├─ Converter: replace(',', '.')
   ├─ parseFloat(peso)
   ├─ Se NaN ou inválido:
   │   ├─ mostrarToast('Peso deve ser um número', 'warning')
   │   └─ RETURN

3. VALIDAÇÃO 3: Peso > 0
   ├─ Se peso <= 0:
   │   ├─ mostrarToast('Peso deve ser maior que zero', 'warning')
   │   └─ RETURN

4. VALIDAÇÃO 4: Peso Máximo (2000 kg)
   ├─ Se peso > 2000:
   │   ├─ mostrarToast('Peso muito alto. Verifique o valor.', 'warning')
   │   └─ RETURN

5. VALIDAÇÃO 5: Animal Identificado
   ├─ Se !brincoAtualV3 ou !animalAtualV3:
   │   ├─ mostrarToast('Identifique um animal primeiro', 'warning')
   │   └─ RETURN

6. TODAS VALIDAÇÕES OK
   └─ CONTINUAR
```

### 4.3. Envio da Pesagem

**Sequência Perfeita:**

```
1. EXIBIR LOADING
   └─ mostrarLoading(true)

2. PREPARAR PAYLOAD
   ├─ animal_id: animalAtualV3?.id || null
   ├─ brinco: brincoAtualV3
   └─ peso: parseFloat(peso) (já validado)

3. ENVIAR PARA API ESPECÍFICA
   ├─ URL: `/propriedade/${propriedadeId}/curral/api/pesagem/`
   ├─ Método: POST
   ├─ Headers:
   │   ├─ Content-Type: application/json
   │   ├─ X-CSRFToken: csrfToken
   │   └─ X-Requested-With: XMLHttpRequest
   └─ Body: JSON.stringify(payload)

4. VERIFICAR RESPOSTA HTTP
   ├─ Se !response.ok:
   │   ├─ Ler errorText = await response.text()
   │   ├─ mostrarLoading(false)
   │   ├─ mostrarToast(`Erro ${response.status}: ${errorText}`, 'error')
   │   └─ RETURN
   └─ CONTINUAR

5. PROCESSAR RESPOSTA JSON
   ├─ data = await response.json()
   ├─ Verificar data.status
   └─ Se status !== 'ok':
       ├─ mostrarLoading(false)
       ├─ mostrarToast(data.mensagem || 'Erro ao registrar pesagem', 'error')
       └─ RETURN

6. VERIFICAR APARTAÇÃO (Se Configurado)
   ├─ Carregar configuração de pesagem salva
   ├─ Se manejo === 'PESAGEM_APARTE':
   │   ├─ Calcular apartação baseada no peso
   │   ├─ Se apartação encontrada:
   │   │   ├─ mostrarPopupApartacao(animal, peso, apartacao)
   │   │   ├─ Iniciar timer de 5 segundos
   │   │   └─ Após timer: continuarAposApartacao()
   │   └─ RETURN (será continuado após fechar popup)
   └─ CONTINUAR (pesagem normal)

7. CONTINUAR APÓS GRAVAÇÃO
   └─ continuarAposGravarPesagem(data, peso)
```

### 4.4. Pós-Gravação da Pesagem

**Sequência Perfeita:**

```
1. ATUALIZAR CAMPOS DE PESAGEM REGISTRADA
   ├─ pesoRegistradoV3 → `${peso} kg`
   ├─ pesoUltimoDataV3 → Formatar data da pesagem
   ├─ pesoDiasV3 → Calcular dias desde última pesagem
   ├─ pesoGanhoTotalV3 → Calcular ganho (peso_atual - peso_anterior)
   └─ pesoGanhoDiaV3 → Calcular ganho diário médio

2. APLICAR CORES DINÂMICAS NO GANHO
   ├─ Se ganho > 0 → classe 'ganho-positivo' (verde)
   ├─ Se ganho < 0 → classe 'ganho-negativo' (vermelho)
   └─ Se ganho === 0 → sem classe especial

3. ATUALIZAR GRÁFICO DE EFICIÊNCIA
   └─ atualizarTermometroEficiencia(ganhoDiario)

4. ADICIONAR ANIMAL À TABELA
   └─ adicionarAnimalTabela(animalAtualV3, peso)

5. LIMPAR CAMPOS PARA PRÓXIMO ANIMAL
   ├─ pesoValorV3.value = '' (limpar peso)
   └─ NÃO limpar brincoInputV3 (manter código)

6. REGISTRAR MANEJOS ADICIONAIS (Se Houver)
   ├─ Se manejosSelecionadosV3.length > 0:
   │   ├─ Enviar para API de manejos
   │   └─ Processar resposta
   └─ Limpar manejosSelecionadosV3 após sucesso

7. HABILITAR BOTÃO FINALIZAR
   └─ btnFinalizarGravarV3.disabled = false

8. ATUALIZAR ESTATÍSTICAS
   ├─ atualizarEstatisticas() (estatísticas gerais)
   └─ atualizarEstatisticasSessao() (estatísticas da sessão)

9. OCULTAR LOADING
   └─ mostrarLoading(false)

10. EXIBIR TOAST DE SUCESSO
    └─ mostrarToast('Pesagem registrada com sucesso!', 'success')

11. FOCAR NO CAMPO DE BUSCA
    └─ setTimeout(() => brincoInputV3.focus(), 200)
```

### 4.5. Integração com Balança

**Fluxo Automático:**

```
1. BALANÇA ENVIA PESO
   └─ Endpoint: POST /curral/api/balanca/peso/
      ├─ Payload: { peso, codigo_animal, timestamp }
      └─ Backend processa

2. BACKEND PUBLICA EVENTO (WebSocket/SSE) OU
   └─ Frontend consulta periodicamente

3. FRONTEND RECEBE PESO
   ├─ Preencher campo pesoValorV3
   ├─ Se há animal identificado:
   │   └─ Auto-gravar após 2 segundos de estabilidade
   └─ Se não há animal identificado:
       └─ Aguardar identificação

4. SE CÓDIGO VEIO COM PESO
   ├─ Buscar animal automaticamente
   ├─ Preencher dados
   └─ Auto-gravar pesagem
```

---

## 5. FLUXO DE REGISTRO DE MANEJOS

### 5.1. Seleção de Manejos

**Tipos Disponíveis:**
- Vacinação
- Tratamento Sanitário
- Reprodução (IATF, etc.)
- Apartação/Loteamento
- Outros

### 5.2. Adicionar Manejo à Lista

```
1. USUÁRIO SELECIONA MANEJO
   ├─ Abrir modal/card de configuração
   ├─ Preencher dados específicos:
   │   ├─ Tipo de vacina/medicamento
   │   ├─ Dose
   │   ├─ Data prevista
   │   └─ Observações
   └─ Confirmar

2. ADICIONAR À LISTA DE MANEJOS
   ├─ manejosSelecionadosV3.push({
   │     tipo: 'VACINACAO',
   │     dados: { ... }
   │   })
   └─ atualizarListaManejosV3()

3. EXIBIR NA INTERFACE
   └─ Mostrar lista de manejos pendentes
```

### 5.3. Gravar Manejos

**Sequência:**

```
1. USUÁRIO CLICA "FINALIZAR E GRAVAR"
   └─ finalizarEGravarV3()

2. VALIDAÇÃO
   ├─ Se !brincoAtualV3:
   │   ├─ mostrarToast('Identifique um animal primeiro', 'warning')
   │   └─ RETURN
   ├─ Se !peso e manejosSelecionadosV3.length === 0:
   │   ├─ mostrarToast('Registre uma pesagem ou selecione manejos', 'warning')
   │   └─ RETURN
   └─ CONTINUAR

3. GRAVAR PESAGEM PRIMEIRO (Se Houver)
   ├─ Se pesoValorV3.value:
   │   ├─ await gravarPesagemV3()
   │   └─ Aguardar conclusão
   └─ CONTINUAR

4. GRAVAR MANEJOS (Se Houver)
   ├─ Se manejosSelecionadosV3.length > 0:
   │   ├─ Payload:
   │   │   ├─ tipo_fluxo: 'animal'
   │   │   ├─ codigo: brincoAtualV3
   │   │   ├─ animal_id: animalAtualV3.id
   │   │   └─ manejos: [...manejosSelecionadosV3]
   │   ├─ URL: /curral/api/manejos/registrar/
   │   ├─ Método: POST
   │   └─ Processar resposta
   └─ CONTINUAR

5. FINALIZAÇÃO
   ├─ Limpar lista de manejos
   ├─ Mostrar toast de sucesso
   └─ Preparar para próximo animal
```

---

## 6. FLUXO DE SESSÃO

### 6.1. Verificação de Sessão Ativa

**Início da Página:**

```
1. VERIFICAR NO BACKEND
   └─ Buscar CurralSessao com status='ABERTA'

2. SE SESSÃO ENCONTRADA
   ├─ Exibir informações:
   │   ├─ Nome da sessão
   │   ├─ Data/hora de início
   │   ├─ Total de eventos
   │   ├─ Animais processados
   │   └─ Total de pesagens
   ├─ Habilitar botões de trabalho
   └─ Carregar estatísticas da sessão

3. SE NÃO HÁ SESSÃO
   ├─ Exibir: "Nenhuma sessão ativa"
   ├─ Oferecer criar nova sessão
   └─ Desabilitar botões de trabalho (exceto criar sessão)
```

### 6.2. Criar Nova Sessão

**Fluxo:**

```
1. USUÁRIO CLICA "NOVA SESSÃO" (ou é automaticamente solicitado)
   └─ Abrir modal de criação

2. PREENCHER DADOS
   ├─ Nome da sessão (obrigatório)
   ├─ Tipo de trabalho:
   │   ├─ Pesagem
   │   ├─ Desmama
   │   ├─ Vacinação
   │   └─ Outro
   ├─ Pasto/Lote (opcional)
   └─ Observações (opcional)

3. VALIDAÇÃO
   ├─ Se nome vazio:
   │   ├─ mostrarToast('Informe o nome da sessão', 'warning')
   │   └─ RETURN
   └─ CONTINUAR

4. ENVIAR PARA API
   ├─ URL: /curral/api/sessao/criar/
   ├─ Payload:
   │   ├─ nome: nome
   │   ├─ tipo_trabalho: tipo
   │   ├─ pasto_origem: pasto
   │   └─ observacoes: obs
   └─ Método: POST

5. PROCESSAR RESPOSTA
   ├─ Se sucesso:
   │   ├─ Atualizar UI da sessão
   │   ├─ Habilitar botões de trabalho
   │   ├─ Fechar modal
   │   └─ mostrarToast('Sessão iniciada!', 'success')
   └─ Se erro:
       ├─ mostrarToast(mensagem, 'error')
       └─ Manter modal aberto
```

### 6.3. Encerrar Sessão

**Fluxo:**

```
1. USUÁRIO CLICA "ENCERRAR SESSÃO"
   └─ Confirmar ação (modal de confirmação)

2. VALIDAÇÃO
   ├─ Se não há sessão ativa:
   │   ├─ mostrarToast('Não há sessão ativa', 'warning')
   │   └─ RETURN
   └─ CONTINUAR

3. CONFIRMAÇÃO
   ├─ Modal: "Deseja encerrar a sessão atual?"
   ├─ Exibir resumo:
   │   ├─ Total de eventos
   │   ├─ Animais processados
   │   └─ Pesagens realizadas
   └─ Botões: "Confirmar" / "Cancelar"

4. SE CONFIRMADO
   ├─ ENVIAR PARA API
   │   ├─ URL: /curral/api/sessao/encerrar/
   │   └─ Método: POST
   ├─ PROCESSAR RESPOSTA
   │   ├─ Se sucesso:
   │   │   ├─ Atualizar UI (remover sessão)
   │   │   ├─ Desabilitar botões de trabalho
   │   │   ├─ Exibir resumo final
   │   │   └─ mostrarToast('Sessão encerrada!', 'success')
   │   └─ Se erro:
   │       └─ mostrarToast(mensagem, 'error')
   └─ FECHAR MODAL
```

### 6.4. Atualização de Estatísticas da Sessão

**Quando Atualizar:**
- Após cada pesagem registrada
- Após cada manejo registrado
- A cada 30 segundos (polling automático)
- Ao voltar à página (verificação manual)

**O Que Atualizar:**
```
├─ Total de eventos
├─ Animais processados
├─ Total de pesagens
├─ Média de peso
├─ Ganho médio diário
└─ Por categoria
```

---

## 7. TRATAMENTO DE ERROS

### 7.1. Erros de Rede

**Tratamento Perfeito:**

```
1. DETECTAR ERRO
   ├─ try/catch em todas as funções async
   └─ Verificar response.ok antes de .json()

2. CLASSIFICAR ERRO
   ├─ Erro de conexão (sem resposta)
   │   └─ mostrarToast('Erro de conexão. Verifique sua internet.', 'error')
   ├─ Erro HTTP (status 4xx/5xx)
   │   ├─ Ler mensagem de erro do servidor
   │   └─ mostrarToast(`Erro ${status}: ${mensagem}`, 'error')
   └─ Erro de parsing JSON
       └─ mostrarToast('Resposta inválida do servidor', 'error')

3. LOG DE ERRO (Console)
   ├─ console.error('Erro:', error)
   ├─ console.error('URL:', url)
   ├─ console.error('Payload:', payload)
   └─ console.error('Response:', response)

4. MANTER ESTADO
   └─ NÃO limpar campos (facilita retry)

5. PERMITIR RETRY
   └─ Opção: "Tentar novamente" em erros temporários
```

### 7.2. Erros de Validação

**Tipos e Tratamento:**

```
1. VALIDAÇÃO DE CAMPO VAZIO
   ├─ Toast: 'Campo obrigatório: {nome_do_campo}'
   ├─ Focar no campo com erro
   └─ Destacar campo (borda vermelha)

2. VALIDAÇÃO DE FORMATO
   ├─ Toast: 'Formato inválido: {exemplo_correto}'
   ├─ Limpar campo inválido
   └─ Focar no campo

3. VALIDAÇÃO DE VALOR
   ├─ Toast: 'Valor inválido: {mensagem_específica}'
   └─ Manter valor para correção

4. VALIDAÇÃO DE BANCO DE DADOS
   ├─ Toast: 'Erro ao salvar: {mensagem}'
   └─ Não limpar campos (permitir correção)
```

### 7.3. Erros de Sessão

**Tratamento:**

```
1. SESSÃO EXPIRADA
   ├─ Detectar: resposta 401/403
   ├─ mostrarToast('Sessão expirada. Redirecionando...', 'warning')
   └─ Redirecionar para login

2. SEM PERMISSÃO
   ├─ Detectar: resposta 403
   ├─ mostrarToast('Você não tem permissão para esta ação', 'error')
   └─ Desabilitar ação

3. SESSÃO NÃO ATIVA
   ├─ Ao tentar gravar sem sessão
   ├─ mostrarToast('Inicie uma sessão antes de trabalhar', 'warning')
   └─ Oferecer criar sessão
```

---

## 8. VALIDAÇÕES

### 8.1. Validações de Frontend

**Checklist Completo:**

```
IDENTIFICAÇÃO:
├─ [ ] Código não vazio após limpeza
├─ [ ] Código tem pelo menos 3 caracteres
├─ [ ] Animal identificado antes de gravar
└─ [ ] Animal existe no banco de dados

PESAGEM:
├─ [ ] Peso é número válido
├─ [ ] Peso > 0
├─ [ ] Peso <= 2000 kg
├─ [ ] Animal identificado
└─ [ ] Formato correto (aceita vírgula ou ponto)

MANEJOS:
├─ [ ] Tipo de manejo selecionado
├─ [ ] Dados obrigatórios preenchidos
└─ [ ] Validade de data (se aplicável)

SESSÃO:
├─ [ ] Nome da sessão não vazio
├─ [ ] Tipo de trabalho selecionado
└─ [ ] Sessão ativa antes de gravar
```

### 8.2. Validações de Backend

**Que o Frontend Deve Considerar:**

```
1. VALIDAÇÕES QUE O BACKEND PODE REJEITAR
   ├─ Animal não encontrado
   ├─ Peso muito diferente do histórico (alerta)
   ├─ Sessão não encontrada (cria automaticamente)
   └─ Campos obrigatórios faltando

2. TRATAR RESPOSTAS DO BACKEND
   ├─ Sempre verificar data.status
   ├─ Sempre ler data.mensagem
   └─ Exibir mensagem ao usuário
```

---

## 9. ESTADOS DA INTERFACE

### 9.1. Estados Principais

```
ESTADO 1: SEM SESSÃO
├─ Campo de busca: DESABILITADO
├─ Campo de peso: DESABILITADO
├─ Botões de gravar: DESABILITADOS
└─ Mensagem: "Inicie uma sessão para começar"

ESTADO 2: SESSÃO ATIVA, SEM ANIMAL
├─ Campo de busca: HABILITADO, FOCO
├─ Campo de peso: DESABILITADO
├─ Botões de gravar: DESABILITADOS
└─ Pronto para buscar animal

ESTADO 3: ANIMAL IDENTIFICADO
├─ Campo de busca: HABILITADO (com código)
├─ Campo de peso: HABILITADO, FOCO
├─ Botões de gravar: HABILITADOS
├─ Campos editáveis: HABILITADOS
└─ Mostrando dados do animal

ESTADO 4: PROCESSANDO
├─ Todos os campos: DESABILITADOS
├─ Loading: VISÍVEL
├─ Botões: DESABILITADOS
└─ Feedback: "Processando..."

ESTADO 5: ERRO
├─ Campos: HABILITADOS (manter dados)
├─ Loading: OCULTO
├─ Toast: EXIBINDO ERRO
└─ Permitir correção/retry

ESTADO 6: SUCESSO (Após Gravar)
├─ Campos de peso: LIMPOS
├─ Campos de animal: MANTIDOS
├─ Toast: "Sucesso!"
├─ Tabela: ATUALIZADA
└─ Foco: Campo de busca (próximo animal)
```

### 9.2. Feedback Visual

**Cores e Indicadores:**

```
SUCESSO:
├─ Toast: Verde (#43a047)
├─ Botões: Verde ao passar mouse
└─ Ícones: ✓

ERRO:
├─ Toast: Vermelho (#e53935)
├─ Campos com erro: Borda vermelha
└─ Ícones: ✗

AVISO:
├─ Toast: Laranja (#fb8c00)
└─ Ícones: ⚠

INFO:
├─ Toast: Azul (#3b82f6)
└─ Ícones: ℹ

LOADING:
├─ Spinner animado
├─ Todos campos desabilitados
└─ Mensagem: "Processando..."
```

---

## 10. MELHORES PRÁTICAS

### 10.1. Código JavaScript

```javascript
// ✅ SEMPRE fazer:
1. Validar dados antes de enviar
2. Verificar response.ok antes de .json()
3. Tratar erros com try/catch
4. Mostrar feedback ao usuário
5. Limpar loading em finally

// ❌ NUNCA fazer:
1. Confiar cegamente em dados do usuário
2. Processar response sem verificar status
3. Deixar promises sem catch
4. Esquecer de ocultar loading
5. Limpar campos antes de confirmar sucesso
```

### 10.2. Experiência do Usuário

```
✅ FAZER:
├─ Focar automaticamente no próximo campo
├─ Manter dados após erros (facilitar correção)
├─ Mostrar mensagens claras e específicas
├─ Confirmar ações destrutivas
├─ Atualizar estatísticas em tempo real
└─ Permitir desfazer quando possível

❌ EVITAR:
├─ Limpar campos sem necessidade
├─ Mensagens genéricas ("Erro ocorreu")
├─ Múltiplos cliques sem feedback
├─ Perder dados do usuário
└─ Ações irreversíveis sem confirmação
```

### 10.3. Performance

```
1. Usar APIs específicas (não genéricas)
   ✅ /curral/api/pesagem/ (específico)
   ❌ /curral/api/registrar/ (genérico)

2. Enviar apenas dados necessários
   ✅ { animal_id, peso }
   ❌ { animal_id, peso, tipo_fluxo, manejo, codigo, dados: {...} }

3. Atualizar estatísticas com debounce
   ✅ Atualizar após ação do usuário
   ❌ Atualizar a cada segundo

4. Cache de dados quando apropriado
   ✅ Cache de sessão ativa
   ❌ Buscar sessão a cada ação
```

### 10.4. Segurança

```
1. Sempre validar no backend (não confiar apenas no frontend)
2. Usar CSRF token em todas as requisições
3. Sanitizar inputs antes de exibir
4. Não expor informações sensíveis em console.log em produção
5. Validar permissões antes de ações
```

---

## 11. EXEMPLO DE FLUXO COMPLETO IDEAL

### Cenário: Pesagem de Animal

```
1. [USUÁRIO] Abre a página
   └─ [SISTEMA] Carrega, verifica sessão, mostra "Sessão: Pesagem - 24/11/2025"

2. [USUÁRIO] Lê código RFID: "619538"
   └─ [SISTEMA] Preenche campo automaticamente

3. [USUÁRIO] Pressiona Enter
   └─ [SISTEMA] 
       ├─ Valida código (6 dígitos)
       ├─ Mostra loading
       ├─ Busca na API
       ├─ Encontra animal
       ├─ Preenche dados
       └─ Foca no campo de peso

4. [USUÁRIO] Animal na balança mostra: 245.5 kg
   └─ [SISTEMA] Preenche campo automaticamente

5. [USUÁRIO] Clica "Gravar"
   └─ [SISTEMA]
       ├─ Valida peso (245.5 > 0, <= 2000) ✅
       ├─ Valida animal identificado ✅
       ├─ Mostra loading
       ├─ Envia para API específica
       ├─ Recebe confirmação
       ├─ Calcula ganhos
       ├─ Atualiza estatísticas
       ├─ Adiciona à tabela
       ├─ Limpa campo de peso
       ├─ Mantém código no campo de busca
       ├─ Mostra toast: "Pesagem registrada!"
       └─ Foca no campo de busca

6. [USUÁRIO] Lê próximo código RFID
   └─ [SISTEMA] Repete ciclo
```

---

## 12. CHECKLIST DE IMPLEMENTAÇÃO

### Frontend
- [x] IDs consistentes entre HTML e JavaScript
- [x] Validações em todos os campos
- [x] Verificação de response.ok
- [x] Tratamento de erros com try/catch
- [x] Feedback visual adequado
- [x] Loading states
- [x] Auto-focus nos campos corretos
- [x] APIs específicas (não genéricas)
- [x] Limpeza adequada de campos
- [x] Atualização de estatísticas

### Backend
- [x] APIs específicas para cada ação
- [x] Validações robustas
- [x] Mensagens de erro claras
- [x] Criação automática de sessão quando necessário
- [x] Tratamento de transações (atomic)
- [x] Logs adequados

### Integração
- [x] Payloads corretos
- [x] Headers corretos (CSRF)
- [x] Status codes adequados
- [x] Respostas JSON consistentes
- [x] Tratamento de erros HTTP

---

**Documento criado em**: {{ data_atual }}
**Versão**: 1.0
**Status**: ✅ Completo e Validado




