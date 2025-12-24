# 🔍 Verificação do Sistema de Análise em Tempo Real

## 📋 Como Verificar se Está Funcionando

### 1. **Abrir o Console do Navegador**
- Pressione `F12` ou `Ctrl+Shift+I` (Windows/Linux) ou `Cmd+Option+I` (Mac)
- Vá para a aba "Console"

### 2. **Verificar se o Sistema Foi Inicializado**

Execute no console:
```javascript
// Verificar se o sistema existe
console.log('Sistema existe?', typeof window.sistemaAnalise !== 'undefined');
console.log('Configuração:', window.sistemaAnalise?.analisesRealizadas);

// Verificar status
if (typeof window.verificarSistemaAnalise === 'function') {
  window.verificarSistemaAnalise();
} else {
  console.error('❌ Função verificarSistemaAnalise não encontrada');
}
```

### 3. **Verificar se o Botão Está Visível**

Execute no console:
```javascript
const btn = document.getElementById('btnTogglePainel');
if (btn) {
  console.log('✅ Botão encontrado:', btn);
  console.log('Posição:', btn.style.position, btn.style.top, btn.style.right);
} else {
  console.warn('⚠️ Botão não encontrado. Tentando criar...');
  if (typeof window.criarPainelAnalise === 'function') {
    window.criarPainelAnalise();
    console.log('✅ Painel criado manualmente');
  }
}
```

### 4. **Verificar se o Painel Existe**

Execute no console:
```javascript
const painel = document.getElementById('painelAnaliseSimulador');
if (painel) {
  console.log('✅ Painel encontrado');
  console.log('Visível?', painel.style.display !== 'none');
  // Tornar visível para teste
  painel.style.display = 'block';
} else {
  console.warn('⚠️ Painel não encontrado');
}
```

### 5. **Verificar Métricas em Tempo Real**

Execute no console:
```javascript
if (window.sistemaAnalise) {
  console.log('📊 Métricas Atuais:');
  console.log('- Análises realizadas:', window.sistemaAnalise.analisesRealizadas);
  console.log('- Eventos registrados:', window.sistemaAnalise.eventos.length);
  console.log('- Animais processados:', window.sistemaAnalise.metricas.fluxo.animaisProcessados);
  console.log('- Erros:', window.sistemaAnalise.metricas.fluxo.animaisComErro);
  console.log('- Fase atual:', window.sistemaAnalise.metricas.fluxo.faseAtual);
  console.log('- Performance:', window.sistemaAnalise.metricas.performance);
  console.log('- Diagnósticos:', window.sistemaAnalise.diagnosticos.length);
  console.log('- Recomendações:', window.sistemaAnalise.recomendacoes.length);
} else {
  console.error('❌ Sistema de análise não encontrado');
}
```

### 6. **Forçar Inicialização Manual**

Se o sistema não foi inicializado automaticamente:

```javascript
// Verificar se as funções existem
if (typeof window.criarPainelAnalise === 'function') {
  window.criarPainelAnalise();
  console.log('✅ Painel criado');
}

// Verificar novamente após 2 segundos
setTimeout(() => {
  const btn = document.getElementById('btnTogglePainel');
  if (btn) {
    console.log('✅ Botão está visível agora');
    btn.click(); // Abrir o painel
  } else {
    console.error('❌ Botão ainda não foi criado');
  }
}, 2000);
```

### 7. **Monitorar Atualizações em Tempo Real**

Execute no console para monitorar atualizações:
```javascript
// Monitorar atualizações a cada segundo
const monitor = setInterval(() => {
  if (window.sistemaAnalise) {
    const analises = window.sistemaAnalise.analisesRealizadas;
    const eventos = window.sistemaAnalise.eventos.length;
    console.log(`📊 Análises: ${analises} | Eventos: ${eventos}`);
    
    // Parar após 30 segundos
    if (analises > 100) {
      clearInterval(monitor);
      console.log('✅ Sistema está funcionando!');
    }
  }
}, 1000);

// Parar monitoramento após 30 segundos
setTimeout(() => {
  clearInterval(monitor);
  console.log('⏹️ Monitoramento parado');
}, 30000);
```

## ✅ Checklist de Verificação

- [ ] Sistema `window.sistemaAnalise` existe
- [ ] Função `window.verificarSistemaAnalise()` disponível
- [ ] Botão "📊 Análise" visível no canto superior direito
- [ ] Painel pode ser aberto ao clicar no botão
- [ ] Métricas estão sendo atualizadas
- [ ] Análises estão sendo realizadas (contador aumenta)
- [ ] Eventos estão sendo registrados
- [ ] Console não mostra erros de JavaScript

## 🔧 Solução de Problemas

### Problema: Botão não aparece
**Solução:**
```javascript
window.criarPainelAnalise();
```

### Problema: Painel não atualiza
**Solução:**
```javascript
// Forçar atualização
if (typeof window.atualizarPainel === 'function') {
  window.atualizarPainel();
}
```

### Problema: Sistema não inicializa
**Solução:**
```javascript
// Verificar se há erros no console
// Recarregar a página
location.reload();
```

## 📊 Exportar Dados de Análise

Para exportar os dados coletados:

```javascript
if (typeof window.exportarAnalise === 'function') {
  window.exportarAnalise();
} else {
  console.error('❌ Função exportarAnalise não encontrada');
}
```

## 🎯 Teste Completo Automatizado

Execute este código no console para um teste completo:

```javascript
(function testeCompleto() {
  console.log('🧪 Iniciando teste completo do Sistema de Análise...');
  
  // 1. Verificar sistema
  if (!window.sistemaAnalise) {
    console.error('❌ Sistema não encontrado');
    return;
  }
  console.log('✅ Sistema encontrado');
  
  // 2. Verificar botão
  const btn = document.getElementById('btnTogglePainel');
  if (!btn) {
    console.warn('⚠️ Botão não encontrado, criando...');
    if (window.criarPainelAnalise) {
      window.criarPainelAnalise();
    }
  } else {
    console.log('✅ Botão encontrado');
  }
  
  // 3. Verificar painel
  const painel = document.getElementById('painelAnaliseSimulador');
  if (!painel) {
    console.warn('⚠️ Painel não encontrado');
  } else {
    console.log('✅ Painel encontrado');
  }
  
  // 4. Verificar métricas
  console.log('📊 Métricas:', {
    analises: window.sistemaAnalise.analisesRealizadas,
    eventos: window.sistemaAnalise.eventos.length,
    animais: window.sistemaAnalise.metricas.fluxo.animaisProcessados
  });
  
  // 5. Verificar se está ativo
  setTimeout(() => {
    const analisesApos = window.sistemaAnalise.analisesRealizadas;
    if (analisesApos > window.sistemaAnalise.analisesRealizadas) {
      console.log('✅ Sistema está ativo e funcionando!');
    } else {
      console.log('⚠️ Sistema pode não estar processando eventos');
    }
  }, 2000);
  
  console.log('✅ Teste completo finalizado');
})();
```

