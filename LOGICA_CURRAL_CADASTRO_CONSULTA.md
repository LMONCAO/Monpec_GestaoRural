# 📋 LÓGICA COMPLETA - CURRAL: CADASTRO E CONSULTA DE ANIMAIS

## 🎯 VISÃO GERAL

O sistema do Curral Inteligente 3.0 permite:
1. **Buscar/Identificar** animais por código (SISBOV, número de manejo ou RFID)
2. **Cadastrar** novos animais a partir de brincos do estoque
3. **Consultar** animais já cadastrados
4. **Registrar pesagens** e outros manejos

---

## 🔑 CONCEITOS IMPORTANTES

### **Brinco = SISBOV Completo**
- O **brinco** é o **SISBOV completo** (15 dígitos)
- Exemplo: `105500376195129`
- Este é o código principal de identificação

### **Número de Manejo**
- Extraído do SISBOV nas **posições 8-13** (6 dígitos)
- Exemplo: `105500376195129` → número de manejo = `619512`
- Usado para busca rápida e sequenciamento

### **RFID/Código Eletrônico**
- Código do chip eletrônico do brinco (opcional)
- Pode ser usado para busca alternativa

---

## 🔄 FLUXO COMPLETO DO SISTEMA

### **1. BUSCA/IDENTIFICAÇÃO DO ANIMAL**

#### **Frontend (JavaScript) - `buscarBrincoV3()`**

**Localização:** `templates/gestao_rural/curral_dashboard_v3.html` (linha ~2058)

```javascript
window.buscarBrincoV3 = async function(brincoParam) {
  // 1. Obtém o código do input ou do parâmetro
  let brinco = brincoParam || document.getElementById('brincoInputV3').value.trim();
  
  // 2. Valida se tem código
  if (!brinco) {
    mostrarToast('Digite o número de manejo, SISBOV ou RFID', 'warning');
    return;
  }
  
  // 3. Faz requisição para o backend
  const response = await fetch(identificarUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify({ codigo: brinco })
  });
  
  // 4. Processa a resposta
  const data = await response.json();
  
  // 5. Trata diferentes cenários:
  //    - status: 'duplicidade' → Múltiplos animais encontrados
  //    - status: 'animal' → Animal já cadastrado
  //    - status: 'estoque' → Brinco livre no estoque
  //    - status: 'nao_encontrado' → Não encontrado
}
```

#### **Backend (Python) - `curral_identificar_codigo()`**

**Localização:** `gestao_rural/views_curral.py` (linha ~870)

**Fluxo de Busca:**

1. **Normaliza o código** (remove caracteres não numéricos)
   ```python
   codigo = _normalizar_codigo(codigo_bruto)
   ```

2. **Busca ANIMAL já cadastrado** (prioridade)
   - Busca por: SISBOV, número de brinco, código eletrônico, número de manejo
   - Para códigos de 6 dígitos: busca exata no número de manejo
   - Para códigos de 15 dígitos: busca exata no SISBOV
   
3. **Se encontrou ANIMAL:**
   ```python
   if animal:
       # ANIMAL JÁ CADASTRADO: Retornar dados do animal normalmente
       # Preenche o card e vai direto para pesagem
       numero_manejo = animal.numero_manejo or _extrair_numero_manejo(animal.codigo_sisbov)
       
       # Retorna dados completos do animal
       return JsonResponse({
           'status': 'animal',
           'dados': {
               'id': animal.id,
               'numero_brinco': animal.numero_brinco,
               'codigo_sisbov': animal.codigo_sisbov,
               'numero_manejo': numero_manejo,
               'raca': animal.raca,
               'sexo': animal.sexo,
               'peso_atual': animal.peso_atual_kg,
               # ... outros dados
           },
           'mensagem': 'Animal localizado no rebanho.'
       })
   ```

4. **Se NÃO encontrou animal, busca BRINCO no ESTOQUE:**
   - Busca brincos com `status != 'EM_USO'`
   - Compara por: SISBOV completo, RFID, número de manejo
   - Se encontrou: retorna `status: 'estoque'`
   - Se encontrou múltiplos: retorna `status: 'estoque_multiplos'`

5. **Se não encontrou nada:**
   - Retorna `status: 'nao_encontrado'`

---

### **2. CADASTRO DE NOVO ANIMAL DO ESTOQUE**

#### **Frontend - `abrirModalCadastroEstoque()`**

**Localização:** `templates/gestao_rural/curral_dashboard_v3.html` (linha ~3125)

```javascript
window.abrirModalCadastroEstoque = function(brinco, dadosEstoque) {
  // 1. Preenche informações do brinco no modal
  //    - BRINCO NO ESTOQUE (SISBOV completo)
  //    - SISBOV
  //    - NÚMERO DE MANEJO (extraído do SISBOV)
  
  // 2. Preenche campos com dados do último cadastro (se houver)
  //    - Raça, Sexo, Idade, Data de Nascimento, RFID
  
  // 3. Valida e habilita/desabilita botão "Confirmar Cadastro"
  validarBotaoConfirmarCadastro();
  
  // 4. Abre o modal
  document.getElementById('modalCadastroEstoque').classList.add('show');
}
```

#### **Frontend - `confirmarCadastroEstoqueV3()`**

**Localização:** `templates/gestao_rural/curral_dashboard_v3.html` (linha ~3492)

```javascript
window.confirmarCadastroEstoqueV3 = async function() {
  // 1. Obtém dados do formulário
  const brinco = brincoAtualV3 || // Tenta variável global
                 document.getElementById('cadastroBrincoV3').textContent || // Tenta elemento do modal
                 document.getElementById('cadastroSisbovV3').textContent; // Fallback
  
  const raca = document.getElementById('cadastroRacaV3').value.trim();
  const sexo = document.getElementById('cadastroSexoV3').value;
  const idade = document.getElementById('cadastroIdadeV3').value.trim();
  const dataNasc = document.getElementById('cadastroDataNascV3').value;
  const rfid = document.getElementById('cadastroRfidV3').value.trim();
  
  // 2. Valida campos obrigatórios
  if (!raca || !sexo || (!idade && !dataNasc)) {
    mostrarToast('Preencha todos os campos obrigatórios...', 'warning');
    return;
  }
  
  // 3. Prepara payload
  const payload = {
    tipo_fluxo: 'estoque',
    manejo: 'CADASTRO_INICIAL',
    codigo: brinco,                    // SISBOV completo
    numero_sisbov: numeroSisbov || brinco,
    rfid: rfid || '',
    sexo: sexo,                        // 'F' ou 'M'
    raca: raca || '',
    idade: idade || '',
    data_nascimento: dataNasc || '',
    origem_cadastro: 'NASCIMENTO'
  };
  
  // 4. Envia para o backend
  const response = await fetch(registrarUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify(payload)
  });
  
  // 5. Se sucesso:
  if (data.status === 'ok') {
    // Fecha modal
    fecharModal('modalCadastroEstoque');
    
    // Busca o animal recém-cadastrado para preencher o card
    if (data.animal_id) {
      await buscarAnimalPorId(data.animal_id, brinco);
    } else {
      await buscarBrincoV3(brinco);
    }
    
    // Foca no campo de pesagem
    document.getElementById('pesoValorV3').focus();
  }
}
```

#### **Backend - `curral_registrar_manejo()`**

**Localização:** `gestao_rural/views_curral.py` (linha ~1628)

**Fluxo de Cadastro:**

1. **Valida dados recebidos**
   ```python
   tipo_fluxo = payload.get('tipo_fluxo')  # 'estoque'
   codigo = payload.get('codigo')          # SISBOV completo
   sexo = payload.get('sexo')              # 'F' ou 'M'
   raca = payload.get('raca')
   idade = payload.get('idade')
   data_nascimento = payload.get('data_nascimento')
   ```

2. **Busca o brinco no estoque**
   ```python
   brinco = BrincoAnimal.objects.filter(
       propriedade=propriedade,
       numero_brinco=codigo,  # SISBOV completo
       status__in=['DISPONIVEL', 'RESERVADO']
   ).first()
   ```

3. **Cria o animal**
   ```python
   animal = AnimalIndividual.objects.create(
       propriedade=propriedade,
       numero_brinco=brinco.numero_brinco,  # SISBOV completo
       codigo_sisbov=brinco.numero_brinco,  # SISBOV completo
       codigo_eletronico=rfid,
       numero_manejo=_extrair_numero_manejo(brinco.numero_brinco),
       sexo=sexo,
       raca=raca,
       data_nascimento=data_nascimento,
       # ... outros campos
   )
   ```

4. **Atualiza status do brinco**
   ```python
   brinco.status = 'EM_USO'
   brinco.save()
   ```

5. **Cria movimentação de nascimento**
   ```python
   MovimentacaoAnimal.objects.create(
       animal=animal,
       tipo_movimentacao='NASCIMENTO',
       propriedade_origem=propriedade,
       propriedade_destino=propriedade,
       data_movimentacao=timezone.now(),
       # ...
   )
   ```

6. **Retorna sucesso**
   ```python
   return JsonResponse({
       'status': 'ok',
       'animal_id': animal.id,
       'mensagem': 'Animal cadastrado com sucesso!'
   })
   ```

---

### **3. CONSULTA DE ANIMAL JÁ CADASTRADO**

Quando um animal já está cadastrado e você busca novamente:

#### **Lógica de Consulta**

**Localização:** `gestao_rural/views_curral.py` (linha ~1150)

```python
if animal:  # Animal já cadastrado encontrado
    # 1. Extrai número de manejo do animal
    numero_manejo = animal.numero_manejo or _extrair_numero_manejo(animal.codigo_sisbov)
    
    # 2. Prepara dados completos do animal
    #    - Histórico de pesagens
    #    - Dados de nascimento
    #    - Categoria, lote, etc.
    
    # 3. Retorna dados do animal
    return JsonResponse({
        'status': 'animal',
        'dados': {
            'id': animal.id,
            'numero_brinco': animal.numero_brinco,
            'codigo_sisbov': animal.codigo_sisbov,
            'numero_manejo': numero_manejo,
            'raca': animal.raca,
            'sexo': animal.sexo,
            'peso_atual': animal.peso_atual_kg,
            'data_nascimento': animal.data_nascimento,
            # ... outros dados
        },
        'mensagem': 'Animal localizado no rebanho.'
    })
```

**Resultado:** O sistema preenche o card com os dados do animal e vai direto para o campo de pesagem.

---

## 📊 DIAGRAMA DE FLUXO

```
┌─────────────────────────────────────────────────────────────┐
│  USUÁRIO DIGITA CÓDIGO (SISBOV/Manejo/RFID)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  buscarBrincoV3() - Frontend                                │
│  Envia: { codigo: "619512" }                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  curral_identificar_codigo() - Backend                      │
│  1. Normaliza código                                        │
│  2. Busca ANIMAL cadastrado                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────┐          ┌──────────────────────┐
│ ANIMAL        │          │ NÃO ENCONTROU ANIMAL  │
│ ENCONTRADO    │          │ Busca BRINCO ESTOQUE  │
└───────┬───────┘          └──────┬───────────────┘
        │                         │
        ▼                         │
┌─────────────────────────────┐  │
│ Retorna:                    │  │
│ status: 'animal'            │  │
│ dados: {animal completo...} │  │
└───────┬─────────────────────┘  │
        │                         │
        │                         ▼
        │              ┌──────────────────────┐
        │              │ BRINCO ENCONTRADO?    │
        │              └──────┬───────────────┘
        │                     │
        │              ┌───────┴───────────────┐
        │              │                       │
        │              ▼                       ▼
        │      ┌───────────────┐      ┌───────────────┐
        │      │ SIM           │      │ NÃO           │
        │      │ status:       │      │ status:       │
        │      │ 'estoque'     │      │ 'nao_         │
        │      │ dados:        │      │ encontrado'   │
        │      │ {brinco...}   │      └───────────────┘
        │      └───────┬───────┘
        │              │
        └──────────────┴──────────────┐
                       │              │
                       ▼              ▼
        ┌─────────────────────────────────────────────┐
        │ Frontend recebe resposta                     │
        │                                              │
        │ Se status === 'animal':                      │
        │   → Preenche card com dados do animal        │
        │   → Habilita campo de pesagem                │
        │   → Foca no campo de pesagem                 │
        │                                              │
        │ Se status === 'estoque':                     │
        │   → abrirModalCadastroEstoque(brinco, dados)│
        │   → Usuário preenche e confirma              │
        │   → Sistema cadastra animal                  │
        │   → Preenche card com dados                  │
        │   → Vai para pesagem                         │
        │                                              │
        │ Se status === 'nao_encontrado':              │
        │   → Mostra mensagem de erro                  │
        └─────────────────────────────────────────────┘
```

---

## 🔍 FUNÇÕES AUXILIARES IMPORTANTES

### **`_normalizar_codigo(codigo: str)`**
- Remove caracteres não numéricos
- Retorna código limpo (apenas números)

### **`_extrair_numero_manejo(codigo_sisbov: str)`**
- Para códigos de 15 dígitos: extrai posições 8-13 (6 dígitos)
- Exemplo: `105500376195129` → `619512`

### **`validarBotaoConfirmarCadastro()`**
- Valida se campos obrigatórios estão preenchidos:
  - ✅ Raça (obrigatório)
  - ✅ Sexo (obrigatório)
  - ✅ Idade OU Data de Nascimento (pelo menos um)
- Habilita/desabilita botão "Confirmar Cadastro"

---

## 📝 CAMPOS OBRIGATÓRIOS NO CADASTRO

1. **Raça** - Texto livre (ex: "NELORE")
2. **Sexo** - Dropdown: "Fêmea" (F) ou "Macho" (M)
3. **Idade OU Data de Nascimento** - Pelo menos um deve ser preenchido
   - Se informar idade → sistema calcula data de nascimento
   - Se informar data → sistema calcula idade

**Campos Opcionais:**
- RFID/Código Eletrônico
- Observações

---

## 🎯 RESUMO DA LÓGICA

### **CENÁRIO 1: Animal JÁ CADASTRADO**
1. **Busca:** Usuário digita código → Sistema busca animal → **Encontrou animal cadastrado**
2. **Resultado:** Sistema preenche o card com dados do animal → Vai direto para pesagem
3. **NÃO abre modal de cadastro** - Animal já existe no sistema

### **CENÁRIO 2: Animal NÃO CADASTRADO (Brinco no Estoque)**
1. **Busca:** Usuário digita código → Sistema busca animal → **NÃO encontrou animal**
2. **Busca Estoque:** Sistema busca brinco no estoque → **Encontrou brinco livre**
3. **Modal:** Sistema abre modal de cadastro com dados do brinco
4. **Cadastro:** Usuário preenche dados (Raça, Sexo, Idade/Data) → Confirma cadastro
5. **Resultado:** Sistema cadastra animal → Preenche card com dados → Vai para pesagem

### **CENÁRIO 3: Código NÃO ENCONTRADO**
1. **Busca:** Usuário digita código → Sistema busca animal → **NÃO encontrou**
2. **Busca Estoque:** Sistema busca brinco no estoque → **NÃO encontrou**
3. **Resultado:** Sistema mostra mensagem "Código não encontrado"

---

## 🔗 ARQUIVOS PRINCIPAIS

- **Frontend:** `templates/gestao_rural/curral_dashboard_v3.html`
  - Função `buscarBrincoV3()` - linha ~2058
  - Função `abrirModalCadastroEstoque()` - linha ~3125
  - Função `confirmarCadastroEstoqueV3()` - linha ~3492

- **Backend:** `gestao_rural/views_curral.py`
  - Função `curral_identificar_codigo()` - linha ~870
  - Função `curral_registrar_manejo()` - linha ~1628
  - Função `_extrair_numero_manejo()` - linha ~794

---

**Última atualização:** 23/11/2025

