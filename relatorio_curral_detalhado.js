// ============================================
// RELATÓRIO DETALHADO - TELA CURRAL
// ============================================
// Execute este script no console do navegador (F12)
// Digite: allow pasting (se solicitado)
// Depois cole este código completo

(function() {
    console.clear();
    console.log('%c🧪 ============================================', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
    console.log('%c🧪 RELATÓRIO DETALHADO - TELA CURRAL', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
    console.log('%c🧪 ============================================', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
    
    const relatorio = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        informacoesGerais: {},
        elementosDOM: {},
        funcoesJavaScript: {},
        estadoAtual: {},
        configuracoes: {},
        apiEndpoints: {},
        problemas: [],
        sugestoes: []
    };
    
    // ============================================
    // 1. INFORMAÇÕES GERAIS
    // ============================================
    console.log('\n%c📋 1. INFORMAÇÕES GERAIS', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    relatorio.informacoesGerais = {
        url: window.location.href,
        titulo: document.title,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        propriedadeId: window.location.pathname.match(/propriedade\/(\d+)/)?.[1] || 'Não encontrado',
        estaNoCurral: window.location.href.includes('/curral/'),
        estaNoPainel: window.location.href.includes('/painel/')
    };
    
    console.table(relatorio.informacoesGerais);
    
    // ============================================
    // 2. ELEMENTOS DO DOM
    // ============================================
    console.log('\n%c📋 2. ELEMENTOS DO DOM', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    const elementosImportantes = {
        // Botões principais
        saveBtn: { nome: 'Botão Gravar Pesagem', id: 'saveBtn', tipo: 'button' },
        nextAnimalBtn: { nome: 'Botão Próximo Animal', id: 'nextAnimalBtn', tipo: 'button' },
        simularPesoBtn: { nome: 'Botão Simular Peso', id: 'simularPesoBtn', tipo: 'button' },
        limparPesoBtn: { nome: 'Botão Limpar Peso', id: 'limparPesoBtn', tipo: 'button' },
        confirmarPesoBtn: { nome: 'Botão Confirmar Peso', id: 'confirmarPesoBtn', tipo: 'button' },
        
        // Campos de entrada
        brincoInput: { nome: 'Campo Brinco', id: 'brincoInput', tipo: 'input' },
        manualPesoInput: { nome: 'Input Manual de Peso', id: 'manualPesoInput', tipo: 'input' },
        
        // Displays
        pesoValue: { nome: 'Display de Peso', id: 'pesoValue', tipo: 'display' },
        pesoDisplay: { nome: 'Container de Peso', id: 'pesoDisplay', tipo: 'container' },
        animalInfo: { nome: 'Card de Informações do Animal', id: 'animalInfo', tipo: 'card' },
        animalBrinco: { nome: 'Display Brinco do Animal', id: 'animalBrinco', tipo: 'display' },
        animalUltimoPeso: { nome: 'Display Último Peso', id: 'animalUltimoPeso', tipo: 'display' },
        animalRaca: { nome: 'Display Raça', id: 'animalRaca', tipo: 'display' },
        animalSexo: { nome: 'Display Sexo', id: 'animalSexo', tipo: 'display' },
        animalNascimento: { nome: 'Display Nascimento', id: 'animalNascimento', tipo: 'display' },
        
        // Outros elementos
        pesoDate: { nome: 'Data da Pesagem', id: 'pesoDate', tipo: 'display' },
        autoNextToggle: { nome: 'Toggle Auto-Próximo', id: 'autoNextToggle', tipo: 'toggle' }
    };
    
    relatorio.elementosDOM = {};
    
    for (const [key, info] of Object.entries(elementosImportantes)) {
        const elemento = document.getElementById(info.id);
        const status = elemento ? '✅ ENCONTRADO' : '❌ NÃO ENCONTRADO';
        
        if (elemento) {
            const estilo = window.getComputedStyle(elemento);
            relatorio.elementosDOM[key] = {
                status: 'ENCONTRADO',
                nome: info.nome,
                id: info.id,
                tipo: info.tipo,
                visivel: estilo.display !== 'none' && estilo.visibility !== 'hidden',
                texto: elemento.textContent ? elemento.textContent.trim().substring(0, 50) : '',
                valor: elemento.value || elemento.textContent || 'N/A',
                classes: elemento.className || 'N/A',
                disabled: elemento.disabled || false
            };
            
            console.log(`✅ ${info.nome} (${info.id}):`, {
                Visível: relatorio.elementosDOM[key].visivel ? 'Sim' : 'Não',
                Texto: relatorio.elementosDOM[key].texto,
                Valor: relatorio.elementosDOM[key].valor,
                Desabilitado: relatorio.elementosDOM[key].disabled
            });
        } else {
            relatorio.elementosDOM[key] = {
                status: 'NÃO ENCONTRADO',
                nome: info.nome,
                id: info.id,
                tipo: info.tipo
            };
            
            console.log(`❌ ${info.nome} (${info.id}): NÃO ENCONTRADO`);
        }
    }
    
    // ============================================
    // 3. FUNÇÕES JAVASCRIPT
    // ============================================
    console.log('\n%c📋 3. FUNÇÕES JAVASCRIPT', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    relatorio.funcoesJavaScript = {};
    
    // Verifica workState
    if (typeof workState !== 'undefined') {
        relatorio.funcoesJavaScript.workState = {
            status: '✅ DEFINIDO',
            tipo: typeof workState,
            propriedades: Object.keys(workState),
            valores: {
                pesoAtual: workState.pesoAtual,
                animalId: workState.animalId,
                animalAtual: workState.animalAtual ? 'Definido' : 'Não definido',
                autoNext: workState.autoNext,
                voicePrompts: workState.voicePrompts,
                activeTasks: workState.activeTasks || []
            }
        };
        console.log('✅ workState:', relatorio.funcoesJavaScript.workState.valores);
    } else {
        relatorio.funcoesJavaScript.workState = { status: '❌ NÃO DEFINIDO' };
        console.log('❌ workState: NÃO DEFINIDO');
    }
    
    // Verifica window.salvarPesagemBackend
    if (typeof window.salvarPesagemBackend !== 'undefined') {
        const codigo = window.salvarPesagemBackend.toString();
        relatorio.funcoesJavaScript.salvarPesagemBackend = {
            status: '✅ DEFINIDO',
            tipo: typeof window.salvarPesagemBackend,
            nome: window.salvarPesagemBackend.name || 'Função anônima',
            parametros: window.salvarPesagemBackend.length,
            temFetch: codigo.includes('fetch'),
            temPropriedadeId: codigo.includes('propriedade'),
            temAnimalId: codigo.includes('animal_id'),
            temPeso: codigo.includes('peso'),
            tamanhoCodigo: codigo.length + ' caracteres'
        };
        console.log('✅ window.salvarPesagemBackend:', {
            Tipo: relatorio.funcoesJavaScript.salvarPesagemBackend.tipo,
            Parâmetros: relatorio.funcoesJavaScript.salvarPesagemBackend.parametros,
            'Tem fetch': relatorio.funcoesJavaScript.salvarPesagemBackend.temFetch ? 'Sim' : 'Não',
            'Tem propriedade_id': relatorio.funcoesJavaScript.salvarPesagemBackend.temPropriedadeId ? 'Sim' : 'Não',
            'Tem animal_id': relatorio.funcoesJavaScript.salvarPesagemBackend.temAnimalId ? 'Sim' : 'Não',
            'Tem peso': relatorio.funcoesJavaScript.salvarPesagemBackend.temPeso ? 'Sim' : 'Não'
        });
    } else {
        relatorio.funcoesJavaScript.salvarPesagemBackend = { status: '❌ NÃO DEFINIDO' };
        console.log('❌ window.salvarPesagemBackend: NÃO DEFINIDO');
        relatorio.problemas.push('Função salvarPesagemBackend não está disponível globalmente');
    }
    
    // Verifica outras funções importantes
    const funcoesParaVerificar = [
        'atualizarPeso',
        'atualizarEstadoBrinco',
        'confirmarPesoManual',
        'registrarAnimalNaSessao',
        'irParaProximoAnimal',
        'getCookie'
    ];
    
    relatorio.funcoesJavaScript.outras = {};
    funcoesParaVerificar.forEach(nome => {
        try {
            const existe = typeof eval(nome) !== 'undefined';
            relatorio.funcoesJavaScript.outras[nome] = existe ? '✅ DEFINIDO' : '❌ NÃO DEFINIDO';
        } catch (e) {
            relatorio.funcoesJavaScript.outras[nome] = '❌ NÃO DEFINIDO';
        }
    });
    
    console.table(relatorio.funcoesJavaScript.outras);
    
    // ============================================
    // 4. ESTADO ATUAL
    // ============================================
    console.log('\n%c📋 4. ESTADO ATUAL DO SISTEMA', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    const brincoInput = document.getElementById('brincoInput');
    const pesoValue = document.getElementById('pesoValue');
    const animalInfo = document.getElementById('animalInfo');
    
    relatorio.estadoAtual = {
        brincoPreenchido: brincoInput ? (brincoInput.value || '') : 'Campo não encontrado',
        pesoAtual: typeof workState !== 'undefined' ? workState.pesoAtual : 'workState não definido',
        pesoDisplay: pesoValue ? pesoValue.textContent.trim() : 'Display não encontrado',
        animalIdentificado: typeof workState !== 'undefined' ? (workState.animalId ? 'Sim' : 'Não') : 'workState não definido',
        animalInfoVisivel: animalInfo ? (animalInfo.style.display !== 'none' ? 'Sim' : 'Não') : 'Elemento não encontrado',
        animalId: typeof workState !== 'undefined' ? workState.animalId : 'N/A',
        animalAtual: typeof workState !== 'undefined' ? (workState.animalAtual ? 'Definido' : 'Não definido') : 'N/A'
    };
    
    console.table(relatorio.estadoAtual);
    
    // ============================================
    // 5. CONFIGURAÇÕES
    // ============================================
    console.log('\n%c📋 5. CONFIGURAÇÕES', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    const autoNextToggle = document.getElementById('autoNextToggle');
    
    relatorio.configuracoes = {
        autoProximo: autoNextToggle ? (autoNextToggle.checked ? 'Ativado' : 'Desativado') : 'Toggle não encontrado',
        voicePrompts: typeof workState !== 'undefined' ? (workState.voicePrompts ? 'Ativado' : 'Desativado') : 'N/A',
        tarefasAtivas: typeof workState !== 'undefined' ? (workState.activeTasks || []) : []
    };
    
    console.table(relatorio.configuracoes);
    
    // ============================================
    // 6. API ENDPOINTS
    // ============================================
    console.log('\n%c📋 6. API ENDPOINTS', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    const propriedadeId = window.location.pathname.match(/propriedade\/(\d+)/)?.[1];
    
    if (propriedadeId) {
        const endpoints = {
            identificar: `/propriedade/${propriedadeId}/curral/api/identificar/`,
            pesagem: `/propriedade/${propriedadeId}/curral/api/pesagem/`,
            sessao: `/propriedade/${propriedadeId}/curral/api/sessao/`
        };
        
        relatorio.apiEndpoints = {
            propriedadeId: propriedadeId,
            endpoints: endpoints
        };
        
        console.log('Endpoints disponíveis:');
        Object.entries(endpoints).forEach(([nome, url]) => {
            console.log(`  ${nome}: ${url}`);
        });
        
        // Testa se o endpoint de pesagem responde
        console.log('\nTestando endpoint de pesagem...');
        fetch(endpoints.pesagem, { method: 'OPTIONS' })
            .then(response => {
                relatorio.apiEndpoints.pesagemStatus = response.status;
                relatorio.apiEndpoints.pesagemOk = response.status < 500;
                console.log(`✅ Endpoint de pesagem responde: Status ${response.status}`);
            })
            .catch(error => {
                relatorio.apiEndpoints.pesagemStatus = 'Erro';
                relatorio.apiEndpoints.pesagemOk = false;
                console.log(`❌ Endpoint de pesagem não responde: ${error.message}`);
            });
    } else {
        relatorio.apiEndpoints = { erro: 'Propriedade ID não encontrado na URL' };
        console.log('❌ Propriedade ID não encontrado na URL');
    }
    
    // ============================================
    // 7. CSRF TOKEN
    // ============================================
    console.log('\n%c📋 7. CSRF TOKEN', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    const csrfToken = getCookie('csrftoken');
    relatorio.csrfToken = {
        disponivel: csrfToken ? 'Sim' : 'Não',
        token: csrfToken ? csrfToken.substring(0, 10) + '...' : 'N/A',
        comprimento: csrfToken ? csrfToken.length : 0
    };
    
    console.table(relatorio.csrfToken);
    
    // ============================================
    // 8. LISTENERS DO BOTÃO GRAVAR
    // ============================================
    console.log('\n%c📋 8. LISTENERS DO BOTÃO GRAVAR', 'font-size: 14px; font-weight: bold; color: #1976d2;');
    
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        // Verifica se há listeners (método aproximado)
        const temOnclick = saveBtn.onclick !== null;
        const temAtributo = saveBtn.getAttribute('onclick') !== null;
        const estilo = window.getComputedStyle(saveBtn);
        
        relatorio.listenersGravar = {
            botaoEncontrado: 'Sim',
            visivel: estilo.display !== 'none',
            habilitado: !saveBtn.disabled,
            temOnclick: temOnclick,
            temAtributoOnclick: temAtributo,
            texto: saveBtn.textContent.trim(),
            classes: saveBtn.className
        };
        
        console.table(relatorio.listenersGravar);
    } else {
        relatorio.listenersGravar = { botaoEncontrado: 'Não' };
        console.log('❌ Botão Gravar não encontrado');
        relatorio.problemas.push('Botão Gravar (saveBtn) não encontrado no DOM');
    }
    
    // ============================================
    // 9. ANÁLISE DE PROBLEMAS
    // ============================================
    console.log('\n%c📋 9. ANÁLISE DE PROBLEMAS', 'font-size: 14px; font-weight: bold; color: #d32f2f;');
    
    // Verifica problemas comuns
    if (!document.getElementById('saveBtn')) {
        relatorio.problemas.push('Botão Gravar não encontrado - Recarregue a página (Ctrl+F5)');
    }
    
    if (typeof window.salvarPesagemBackend === 'undefined') {
        relatorio.problemas.push('Função salvarPesagemBackend não está disponível - Verifique se o código foi carregado');
    }
    
    if (typeof workState === 'undefined') {
        relatorio.problemas.push('Variável workState não está definida - Verifique se o JavaScript foi carregado');
    }
    
    if (!getCookie('csrftoken')) {
        relatorio.problemas.push('CSRF token não encontrado - Faça login novamente');
    }
    
    if (relatorio.problemas.length > 0) {
        console.log('❌ Problemas encontrados:');
        relatorio.problemas.forEach((problema, index) => {
            console.log(`  ${index + 1}. ${problema}`);
        });
    } else {
        console.log('✅ Nenhum problema crítico encontrado!');
    }
    
    // ============================================
    // 10. SUGESTÕES
    // ============================================
    console.log('\n%c📋 10. SUGESTÕES', 'font-size: 14px; font-weight: bold; color: #f57c00;');
    
    if (typeof workState !== 'undefined' && workState.pesoAtual <= 0) {
        relatorio.sugestoes.push('Digite um peso para testar o salvamento');
    }
    
    if (typeof workState !== 'undefined' && !workState.animalId) {
        relatorio.sugestoes.push('Identifique um animal (digite um brinco) para testar o salvamento');
    }
    
    if (relatorio.sugestoes.length > 0) {
        console.log('💡 Sugestões:');
        relatorio.sugestoes.forEach((sugestao, index) => {
            console.log(`  ${index + 1}. ${sugestao}`);
        });
    } else {
        console.log('✅ Sistema pronto para uso!');
    }
    
    // ============================================
    // RELATÓRIO FINAL
    // ============================================
    setTimeout(() => {
        console.log('\n\n%c📊 ============================================', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
        console.log('%c📊 RELATÓRIO FINAL', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
        console.log('%c📊 ============================================', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
        
        const elementosEncontrados = Object.values(relatorio.elementosDOM).filter(e => e.status === 'ENCONTRADO').length;
        const elementosTotal = Object.keys(relatorio.elementosDOM).length;
        
        console.log(`\n✅ Elementos encontrados: ${elementosEncontrados}/${elementosTotal}`);
        console.log(`✅ Funções disponíveis: ${Object.values(relatorio.funcoesJavaScript).filter(f => f.status && f.status.includes('✅')).length}`);
        console.log(`❌ Problemas encontrados: ${relatorio.problemas.length}`);
        console.log(`💡 Sugestões: ${relatorio.sugestoes.length}`);
        
        console.log('\n📋 RESUMO EXECUTIVO:');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        if (relatorio.problemas.length === 0) {
            console.log('%c✅ SISTEMA FUNCIONANDO CORRETAMENTE', 'font-size: 14px; font-weight: bold; color: #4caf50;');
            console.log('   Todos os componentes principais estão funcionando.');
            console.log('   Você pode testar o salvamento de pesagem normalmente.');
        } else {
            console.log('%c⚠️ ALGUNS PROBLEMAS FORAM ENCONTRADOS', 'font-size: 14px; font-weight: bold; color: #ff9800;');
            console.log('   Verifique os problemas listados acima.');
            console.log('   Siga as sugestões para resolver.');
        }
        
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        
        // Salva relatório completo
        localStorage.setItem('relatorio_curral_detalhado', JSON.stringify(relatorio, null, 2));
        console.log('💾 Relatório completo salvo no localStorage como "relatorio_curral_detalhado"');
        console.log('   Para ver novamente: JSON.parse(localStorage.getItem("relatorio_curral_detalhado"))');
        
        console.log('\n%c🧪 ============================================', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
        console.log('%c🧪 RELATÓRIO CONCLUÍDO', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
        console.log('%c🧪 ============================================\n', 'font-size: 16px; font-weight: bold; color: #2e7d32;');
    }, 2000);
    
    return relatorio;
})();



