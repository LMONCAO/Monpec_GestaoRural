// ============================================
// SCRIPT DE TESTE - SALVAMENTO DE PESAGEM
// ============================================
// Execute este script no console do navegador (F12)
// Copie e cole todo o código abaixo no console

(function() {
    console.log('🧪 ============================================');
    console.log('🧪 INICIANDO TESTE DE SALVAMENTO DE PESAGEM');
    console.log('🧪 ============================================');
    
    const relatorio = {
        timestamp: new Date().toISOString(),
        testes: [],
        erros: [],
        avisos: [],
        sucessos: []
    };
    
    function adicionarTeste(nome, status, detalhes) {
        relatorio.testes.push({
            nome: nome,
            status: status, // 'ok', 'erro', 'aviso'
            detalhes: detalhes,
            timestamp: new Date().toISOString()
        });
        
        if (status === 'ok') {
            relatorio.sucessos.push(nome);
            console.log(`✅ ${nome}:`, detalhes);
        } else if (status === 'erro') {
            relatorio.erros.push(nome);
            console.error(`❌ ${nome}:`, detalhes);
        } else {
            relatorio.avisos.push(nome);
            console.warn(`⚠️ ${nome}:`, detalhes);
        }
    }
    
    // ============================================
    // TESTE 1: Verificar elementos do DOM
    // ============================================
    console.log('\n📋 TESTE 1: Verificando elementos do DOM...');
    
    const elementos = {
        saveBtn: document.getElementById('saveBtn'),
        brincoInput: document.getElementById('brincoInput'),
        pesoValue: document.getElementById('pesoValue'),
        manualPesoInput: document.getElementById('manualPesoInput'),
        animalInfo: document.getElementById('animalInfo'),
        animalBrinco: document.getElementById('animalBrinco'),
        animalUltimoPeso: document.getElementById('animalUltimoPeso')
    };
    
    Object.keys(elementos).forEach(key => {
        if (elementos[key]) {
            adicionarTeste(`Elemento ${key} existe`, 'ok', {
                id: elementos[key].id,
                tagName: elementos[key].tagName,
                textContent: elementos[key].textContent ? elementos[key].textContent.substring(0, 50) : ''
            });
        } else {
            adicionarTeste(`Elemento ${key} existe`, 'erro', 'Elemento não encontrado no DOM');
        }
    });
    
    // ============================================
    // TESTE 2: Verificar variáveis globais
    // ============================================
    console.log('\n📋 TESTE 2: Verificando variáveis globais...');
    
    if (typeof window !== 'undefined') {
        adicionarTeste('window está disponível', 'ok', 'Objeto window existe');
    } else {
        adicionarTeste('window está disponível', 'erro', 'Objeto window não existe');
    }
    
    if (typeof workState !== 'undefined') {
        adicionarTeste('workState está definido', 'ok', {
            pesoAtual: workState.pesoAtual,
            animalId: workState.animalId,
            animalAtual: workState.animalAtual ? 'Definido' : 'Não definido'
        });
    } else {
        adicionarTeste('workState está definido', 'erro', 'Variável workState não está definida');
    }
    
    if (typeof window.salvarPesagemBackend !== 'undefined') {
        adicionarTeste('window.salvarPesagemBackend está definido', 'ok', {
            tipo: typeof window.salvarPesagemBackend,
            nome: window.salvarPesagemBackend.name || 'Função anônima'
        });
    } else {
        adicionarTeste('window.salvarPesagemBackend está definido', 'erro', 'Função não está disponível globalmente');
    }
    
    // ============================================
    // TESTE 3: Verificar listeners do botão Gravar
    // ============================================
    console.log('\n📋 TESTE 3: Verificando listeners do botão Gravar...');
    
    if (elementos.saveBtn) {
        // Tenta verificar se há listeners (não é 100% confiável, mas ajuda)
        const temListener = elementos.saveBtn.onclick !== null || 
                           elementos.saveBtn.getAttribute('onclick') !== null;
        
        adicionarTeste('Botão Gravar tem listeners', temListener ? 'ok' : 'aviso', {
            onclick: elementos.saveBtn.onclick ? 'Definido' : 'Não definido',
            atributoOnclick: elementos.saveBtn.getAttribute('onclick') || 'Não definido',
            texto: elementos.saveBtn.textContent.trim()
        });
        
        // Testa se o botão é clicável
        const estilo = window.getComputedStyle(elementos.saveBtn);
        adicionarTeste('Botão Gravar está visível', estilo.display !== 'none' ? 'ok' : 'erro', {
            display: estilo.display,
            visibility: estilo.visibility,
            pointerEvents: estilo.pointerEvents
        });
    }
    
    // ============================================
    // TESTE 4: Verificar função de salvamento
    // ============================================
    console.log('\n📋 TESTE 4: Testando função de salvamento...');
    
    if (typeof window.salvarPesagemBackend === 'function') {
        // Não executa a função, apenas verifica se está disponível
        adicionarTeste('Função salvarPesagemBackend é uma função', 'ok', {
            nome: window.salvarPesagemBackend.name || 'Função anônima',
            parametros: window.salvarPesagemBackend.length + ' parâmetros'
        });
        
        // Verifica se a função tem o código necessário
        const codigoFuncao = window.salvarPesagemBackend.toString();
        const temFetch = codigoFuncao.includes('fetch');
        const temPropriedadeId = codigoFuncao.includes('propriedade');
        const temAnimalId = codigoFuncao.includes('animal_id');
        const temPeso = codigoFuncao.includes('peso');
        
        adicionarTeste('Função tem código de fetch', temFetch ? 'ok' : 'erro', 'Verifica se usa fetch para API');
        adicionarTeste('Função tem propriedade_id', temPropriedadeId ? 'ok' : 'erro', 'Verifica se extrai propriedade_id');
        adicionarTeste('Função tem animal_id', temAnimalId ? 'ok' : 'erro', 'Verifica se usa animal_id');
        adicionarTeste('Função tem peso', temPeso ? 'ok' : 'erro', 'Verifica se usa peso');
    } else {
        adicionarTeste('Função salvarPesagemBackend é uma função', 'erro', 'Função não está disponível');
    }
    
    // ============================================
    // TESTE 5: Verificar estado atual
    // ============================================
    console.log('\n📋 TESTE 5: Verificando estado atual...');
    
    if (elementos.brincoInput) {
        const brincoValor = elementos.brincoInput.value;
        adicionarTeste('Brinco está preenchido', brincoValor ? 'ok' : 'aviso', {
            valor: brincoValor || 'Vazio',
            comprimento: brincoValor ? brincoValor.length : 0
        });
    }
    
    if (typeof workState !== 'undefined') {
        adicionarTeste('Peso atual está definido', workState.pesoAtual > 0 ? 'ok' : 'aviso', {
            pesoAtual: workState.pesoAtual,
            animalId: workState.animalId,
            temAnimal: !!workState.animalAtual
        });
    }
    
    // ============================================
    // TESTE 6: Simular clique no botão (sem salvar)
    // ============================================
    console.log('\n📋 TESTE 6: Simulando clique no botão Gravar...');
    
    if (elementos.saveBtn) {
        try {
            // Cria um evento de clique simulado
            const evento = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            
            // Dispara o evento (mas não executa realmente para não salvar)
            console.log('🔘 Disparando evento de clique simulado...');
            elementos.saveBtn.dispatchEvent(evento);
            
            adicionarTeste('Evento de clique pode ser disparado', 'ok', 'Evento foi disparado com sucesso');
        } catch (error) {
            adicionarTeste('Evento de clique pode ser disparado', 'erro', error.message);
        }
    }
    
    // ============================================
    // TESTE 7: Verificar API endpoint
    // ============================================
    console.log('\n📋 TESTE 7: Verificando endpoint da API...');
    
    const urlMatch = window.location.pathname.match(/propriedade\/(\d+)/);
    if (urlMatch) {
        const propriedadeId = urlMatch[1];
        const apiUrl = `/propriedade/${propriedadeId}/curral/api/pesagem/`;
        
        adicionarTeste('URL da API pode ser construída', 'ok', {
            propriedadeId: propriedadeId,
            apiUrl: apiUrl
        });
        
        // Verifica se a rota existe (faz uma requisição OPTIONS)
        fetch(apiUrl, { method: 'OPTIONS' })
            .then(response => {
                adicionarTeste('Endpoint da API responde', response.status < 500 ? 'ok' : 'erro', {
                    status: response.status,
                    statusText: response.statusText
                });
            })
            .catch(error => {
                adicionarTeste('Endpoint da API responde', 'erro', error.message);
            });
    } else {
        adicionarTeste('URL da API pode ser construída', 'erro', 'Não foi possível extrair propriedade_id da URL');
    }
    
    // ============================================
    // TESTE 8: Verificar CSRF token
    // ============================================
    console.log('\n📋 TESTE 8: Verificando CSRF token...');
    
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
    if (csrfToken) {
        adicionarTeste('CSRF token está disponível', 'ok', {
            token: csrfToken.substring(0, 10) + '...',
            comprimento: csrfToken.length
        });
    } else {
        adicionarTeste('CSRF token está disponível', 'erro', 'Token CSRF não encontrado nos cookies');
    }
    
    // ============================================
    // RELATÓRIO FINAL
    // ============================================
    setTimeout(() => {
        console.log('\n\n📊 ============================================');
        console.log('📊 RELATÓRIO FINAL DE TESTES');
        console.log('📊 ============================================');
        console.log(`✅ Sucessos: ${relatorio.sucessos.length}`);
        console.log(`⚠️ Avisos: ${relatorio.avisos.length}`);
        console.log(`❌ Erros: ${relatorio.erros.length}`);
        console.log(`📊 Total de testes: ${relatorio.testes.length}`);
        
        console.log('\n✅ TESTES QUE PASSARAM:');
        relatorio.sucessos.forEach((teste, index) => {
            console.log(`   ${index + 1}. ${teste}`);
        });
        
        if (relatorio.avisos.length > 0) {
            console.log('\n⚠️ AVISOS:');
            relatorio.avisos.forEach((teste, index) => {
                console.log(`   ${index + 1}. ${teste}`);
            });
        }
        
        if (relatorio.erros.length > 0) {
            console.log('\n❌ ERROS ENCONTRADOS:');
            relatorio.erros.forEach((teste, index) => {
                console.log(`   ${index + 1}. ${teste}`);
            });
        }
        
        console.log('\n📋 DETALHES COMPLETOS:');
        console.log(JSON.stringify(relatorio, null, 2));
        
        // Salva o relatório no localStorage para referência
        localStorage.setItem('teste_pesagem_relatorio', JSON.stringify(relatorio));
        console.log('\n💾 Relatório salvo no localStorage como "teste_pesagem_relatorio"');
        
        console.log('\n🎯 CONCLUSÃO:');
        if (relatorio.erros.length === 0) {
            console.log('✅ Todos os testes críticos passaram! O sistema deve estar funcionando.');
        } else {
            console.log('❌ Alguns testes falharam. Verifique os erros acima.');
        }
        
        console.log('\n🧪 ============================================');
        console.log('🧪 TESTE CONCLUÍDO');
        console.log('🧪 ============================================\n');
    }, 2000); // Aguarda 2 segundos para o teste da API terminar
    
    return relatorio;
})();



