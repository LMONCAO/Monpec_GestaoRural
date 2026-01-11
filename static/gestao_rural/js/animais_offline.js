// JavaScript para funcionalidade offline de animais - VERSÃO OTIMIZADA
// Cache inteligente: dados básicos sempre disponíveis, detalhes sob demanda

// Configurações de cache otimizado
const CACHE_CONFIG = {
    MAX_ANIMAIS_CACHE: 5000,        // Até 5000 animais básicos em cache
    CACHE_DURATION: 24 * 60 * 60 * 1000, // 24 horas
    DETALHES_CACHE_DURATION: 6 * 60 * 60 * 1000, // 6 horas para detalhes
    AUTO_LOAD_DETALHES: false,      // Não carregar detalhes automaticamente
    COMPRESSION_ENABLED: true       // Usar compressão quando disponível
};

// Cache local em memória para performance
let animaisBasicosCache = [];
let animaisDetalhesCache = new Map(); // Cache de detalhes por animal_id
let cacheMetadata = {
    lastLoad: null,
    totalAnimais: 0,
    tamanhoEstimado: 0
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Animais Offline Otimizado - Inicializando...');

    // Verificar se estamos offline
    if (!navigator.onLine) {
        mostrarNotificacao('Modo offline ativado - usando cache otimizado', 'warning');
    }

    // Inicializar aplicação
    inicializarAplicacao();

    // Configurar event listeners
    configurarEventListeners();

    // Carregar dados básicos primeiro (leve)
    carregarDadosBasicos();

    console.log('✅ Animais Offline Otimizado - Inicializado com sucesso!');
});

// Inicializar aplicação
function inicializarAplicacao() {
    // Esconder spinner de loading
    document.getElementById('loading-spinner').style.display = 'none';

    // Mostrar container de resultados
    document.getElementById('results-container').style.display = 'block';

    // Popular filtros de categoria
    popularFiltrosCategoria();

    // Renderizar tabela inicial
    renderizarTabela();
}

// Configurar event listeners
function configurarEventListeners() {
    // Busca em tempo real
    const searchInput = document.getElementById('search-input');
    searchInput.addEventListener('input', debounce(filtrarAnimais, 300));

    // Filtros
    document.getElementById('categoria-filter').addEventListener('change', filtrarAnimais);
    document.getElementById('sexo-filter').addEventListener('change', filtrarAnimais);

    // Status da rede
    window.addEventListener('online', () => {
        mostrarNotificacao('Conexão restaurada! Dados serão sincronizados.', 'success');
        setTimeout(() => location.reload(), 2000);
    });

    window.addEventListener('offline', () => {
        mostrarNotificacao('Conexão perdida. Trabalhando offline.', 'warning');
    });
}

// Carregar dados básicos otimizados (sempre disponível offline)
async function carregarDadosBasicos() {
    try {
        console.log('📊 Carregando dados básicos otimizados...');

        // Tentar carregar da API online primeiro
        if (navigator.onLine) {
            await carregarDaAPI();
        } else {
            // Se offline, tentar usar dados do service worker cache
            await carregarDoCacheLocal();
        }

        // Atualizar interface
        atualizarInterfaceComDados();

    } catch (error) {
        console.error('❌ Erro ao carregar dados básicos:', error);
        mostrarMensagemVazia('Erro ao carregar dados. Verifique sua conexão.');
    }
}

// Carregar dados da API online
async function carregarDaAPI() {
    try {
        const response = await fetch('/api/animais/offline/basico/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();

            if (data.success && data.data.animais) {
                animaisBasicosCache = data.data.animais;
                cacheMetadata = {
                    lastLoad: new Date().toISOString(),
                    totalAnimais: data.data.total,
                    tamanhoEstimado: data.data.tamanho_estimado_kb || 0,
                    tipo: 'basico'
                };

                // Salvar no localStorage para uso offline futuro
                salvarCacheLocalStorage();

                console.log(`✅ Carregados ${animaisBasicosCache.length} animais básicos (${cacheMetadata.tamanhoEstimado.toFixed(1)}KB)`);
                mostrarNotificacao(`${animaisBasicosCache.length} animais básicos carregados`, 'success');
            } else {
                throw new Error(data.error || 'Erro na resposta da API');
            }
        } else {
            throw new Error(`HTTP ${response.status}`);
        }

    } catch (error) {
        console.error('❌ Erro ao carregar da API:', error);
        // Fallback para cache local
        await carregarDoCacheLocal();
    }
}

// Carregar dados do cache local (localStorage)
async function carregarDoCacheLocal() {
    try {
        const cacheLocal = localStorage.getItem('monpec_animais_basicos_cache');

        if (cacheLocal) {
            const parsedCache = JSON.parse(cacheLocal);

            // Verificar se cache não está muito velho
            const cacheAge = Date.now() - new Date(parsedCache.metadata.lastLoad).getTime();

            if (cacheAge < CACHE_CONFIG.CACHE_DURATION) {
                animaisBasicosCache = parsedCache.animais;
                cacheMetadata = parsedCache.metadata;

                console.log(`📱 Carregados ${animaisBasicosCache.length} animais do cache local (${cacheAge / 1000 / 60}min atrás)`);
                mostrarNotificacao(`${animaisBasicosCache.length} animais carregados do cache local`, 'info');
                return;
            } else {
                console.log('⏰ Cache local expirado, será atualizado quando online');
            }
        }

        if (animaisBasicosCache.length === 0) {
            mostrarMensagemVazia('Nenhum dado disponível offline. Conecte-se à internet para carregar.');
        }

    } catch (error) {
        console.error('❌ Erro ao carregar cache local:', error);
        mostrarMensagemVazia('Erro ao carregar dados offline.');
    }
}

// Salvar cache no localStorage
function salvarCacheLocalStorage() {
    try {
        const cacheData = {
            animais: animaisBasicosCache,
            metadata: cacheMetadata
        };

        localStorage.setItem('monpec_animais_basicos_cache', JSON.stringify(cacheData));
        console.log('💾 Cache salvo no localStorage');
    } catch (error) {
        console.error('❌ Erro ao salvar cache:', error);
        // Se localStorage estiver cheio, tentar limpar outros dados
        if (error.name === 'QuotaExceededError') {
            console.warn('⚠️ localStorage cheio, limpando dados antigos...');
            limparCacheLocalStorage();
        }
    }
}

// Limpar cache antigo do localStorage
function limparCacheLocalStorage() {
    try {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('monpec_') && key !== 'monpec_animais_basicos_cache') {
                keysToRemove.push(key);
            }
        }

        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log(`🗑️ Removidos ${keysToRemove.length} itens antigos do cache`);
    } catch (error) {
        console.error('❌ Erro ao limpar cache:', error);
    }
}

// Atualizar interface com dados carregados
function atualizarInterfaceComDados() {
    // Esconder loading
    document.getElementById('loading-spinner').style.display = 'none';
    document.getElementById('results-container').style.display = 'block';

    // Popular filtros
    popularFiltrosCategoria();

    // Renderizar tabela
    renderizarTabela();

    // Atualizar estatísticas
    atualizarEstatisticasCache();
}

// Atualizar estatísticas do cache
function atualizarEstatisticasCache() {
    const statsElement = document.getElementById('cache-stats');
    if (statsElement && cacheMetadata.totalAnimais > 0) {
        statsElement.innerHTML = `
            <small class="text-muted">
                <i class="fas fa-database me-1"></i>
                ${cacheMetadata.totalAnimais} animais
                (${cacheMetadata.tamanhoEstimado.toFixed(1)}KB)
                ${navigator.onLine ? '• Online' : '• Offline'}
            </small>
        `;
    }
}

// Popular filtros de categoria
function popularFiltrosCategoria() {
    const categorias = [...new Set(animaisData.map(a => a.categoria).filter(c => c))];
    const select = document.getElementById('categoria-filter');

    categorias.sort().forEach(categoria => {
        const option = document.createElement('option');
        option.value = categoria;
        option.textContent = categoria;
        select.appendChild(option);
    });
}

// Filtrar animais baseado nos critérios
function filtrarAnimais() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const categoriaFilter = document.getElementById('categoria-filter').value;
    const sexoFilter = document.getElementById('sexo-filter').value;

    // Atualizar filtros atuais
    currentFilters = {
        search: searchTerm,
        categoria: categoriaFilter,
        sexo: sexoFilter
    };

    // Aplicar filtros
    filteredAnimais = animaisData.filter(animal => {
        // Filtro de busca
        const matchesSearch = !searchTerm ||
            animal.numero_brinco.toLowerCase().includes(searchTerm) ||
            (animal.observacoes && animal.observacoes.toLowerCase().includes(searchTerm));

        // Filtro de categoria
        const matchesCategoria = !categoriaFilter || animal.categoria === categoriaFilter;

        // Filtro de sexo
        const matchesSexo = !sexoFilter || animal.sexo === sexoFilter;

        return matchesSearch && matchesCategoria && matchesSexo;
    });

    // Renderizar resultados
    renderizarTabela();
}

// Renderizar tabela de animais
function renderizarTabela() {
    const tbody = document.getElementById('animais-tbody');
    const countElement = document.getElementById('resultado-count');
    const noResultsElement = document.getElementById('no-results');

    // Limpar tabela
    tbody.innerHTML = '';

    // Atualizar contador
    countElement.textContent = filteredAnimais.length;

    if (filteredAnimais.length === 0) {
        noResultsElement.style.display = 'block';
        return;
    }

    noResultsElement.style.display = 'none';

    // Renderizar linhas
    filteredAnimais.forEach(animal => {
        const row = criarLinhaAnimal(animal);
        tbody.appendChild(row);
    });
}

// Criar linha da tabela para um animal
function criarLinhaAnimal(animal) {
    const tr = document.createElement('tr');

    // Status badge
    const statusBadge = animal.status === 'ATIVO'
        ? '<span class="badge bg-success">Ativo</span>'
        : '<span class="badge bg-secondary">' + animal.status + '</span>';

    // Sexo icon
    const sexoIcon = animal.sexo === 'F'
        ? '<i class="fas fa-venus text-danger"></i>'
        : '<i class="fas fa-mars text-primary"></i>';

    tr.innerHTML = `
        <td>
            <strong class="text-primary">${animal.numero_brinco}</strong>
        </td>
        <td>${animal.categoria}</td>
        <td>${sexoIcon} ${animal.sexo}</td>
        <td>${animal.raca || 'N/A'}</td>
        <td>${animal.peso_atual || 'N/A'}</td>
        <td>${animal.data_nascimento}</td>
        <td>${statusBadge}</td>
        <td>
            <button class="btn btn-sm btn-outline-primary" onclick="verDetalhesAnimal(${animal.id})">
                <i class="fas fa-eye me-1"></i>
                Ver
            </button>
        </td>
    `;

    return tr;
}

// Ver detalhes do animal - CARREGAMENTO SOB DEMANDA
async function verDetalhesAnimal(animalId) {
    const animalBasico = animaisBasicosCache.find(a => a.id === animalId);
    if (!animalBasico) {
        mostrarNotificacao('Animal não encontrado', 'error');
        return;
    }

    const modal = new bootstrap.Modal(document.getElementById('animalModal'));
    const detailsContainer = document.getElementById('animal-details');

    // Mostrar loading enquanto carrega detalhes
    detailsContainer.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando detalhes do animal...</p>
        </div>
    `;

    modal.show();

    try {
        // Verificar se já temos detalhes em cache
        let animalDetalhado = animaisDetalhesCache.get(animalId);

        if (!animalDetalhado) {
            // Carregar detalhes sob demanda
            animalDetalhado = await carregarDetalhesAnimal(animalId);
        }

        // Renderizar detalhes completos
        renderizarDetalhesAnimal(animalDetalhado, animalBasico);

    } catch (error) {
        console.error('❌ Erro ao carregar detalhes:', error);

        // Mostrar detalhes básicos se falhar carregamento detalhado
        renderizarDetalhesBasicos(animalBasico);
    }
}

// Carregar detalhes do animal sob demanda
async function carregarDetalhesAnimal(animalId) {
    try {
        const response = await fetch(`/api/animais/offline/detalhes/${animalId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();

            if (data.success && data.data.animal) {
                // Salvar no cache detalhado
                animaisDetalhesCache.set(animalId, data.data.animal);

                // Limitar cache detalhado para não crescer demais
                if (animaisDetalhesCache.size > 100) {
                    // Remover entrada mais antiga (simples FIFO)
                    const firstKey = animaisDetalhesCache.keys().next().value;
                    animaisDetalhesCache.delete(firstKey);
                }

                console.log(`📋 Detalhes carregados para animal ${animalId}`);
                return data.data.animal;
            } else {
                throw new Error(data.error || 'Erro na resposta da API');
            }
        } else if (response.status === 503) {
            // Offline - tentar usar dados básicos apenas
            throw new Error('offline');
        } else {
            throw new Error(`HTTP ${response.status}`);
        }

    } catch (error) {
        if (error.message === 'offline') {
            console.log('🌐 Offline: mostrando apenas dados básicos');
            throw new Error('offline');
        }
        console.error('❌ Erro ao carregar detalhes:', error);
        throw error;
    }
}

// Renderizar detalhes completos do animal
function renderizarDetalhesAnimal(animalDetalhado, animalBasico) {
    const detailsContainer = document.getElementById('animal-details');

    detailsContainer.innerHTML = `
        <div class="row g-3">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-id-card me-2"></i>
                            Identificação
                        </h6>
                    </div>
                    <div class="card-body">
                        <dl class="row">
                            <dt class="col-sm-5">Brinco:</dt>
                            <dd class="col-sm-7"><strong>${animalDetalhado.numero_brinco}</strong></dd>

                            <dt class="col-sm-5">Categoria:</dt>
                            <dd class="col-sm-7">${animalDetalhado.categoria}</dd>

                            <dt class="col-sm-5">Sexo:</dt>
                            <dd class="col-sm-7">${animalDetalhado.sexo === 'F' ? 'Fêmea' : 'Macho'}</dd>

                            <dt class="col-sm-5">Raça:</dt>
                            <dd class="col-sm-7">${animalDetalhado.raca || 'N/A'}</dd>

                            <dt class="col-sm-5">Status:</dt>
                            <dd class="col-sm-7">
                                <span class="badge ${animalDetalhado.status === 'ATIVO' ? 'bg-success' : 'bg-secondary'}">
                                    ${animalDetalhado.status}
                                </span>
                            </dd>

                            ${animalDetalhado.lote ? `
                                <dt class="col-sm-5">Lote:</dt>
                                <dd class="col-sm-7">${animalDetalhado.lote}</dd>
                            ` : ''}

                            ${animalDetalhado.localizacao ? `
                                <dt class="col-sm-5">Localização:</dt>
                                <dd class="col-sm-7">${animalDetalhado.localizacao}</dd>
                            ` : ''}
                        </dl>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>
                            Dados Físicos
                        </h6>
                    </div>
                    <div class="card-body">
                        <dl class="row">
                            <dt class="col-sm-5">Peso Atual:</dt>
                            <dd class="col-sm-7">
                                <strong class="text-success">
                                    ${animalDetalhado.peso_atual || 'N/A'} kg
                                </strong>
                            </dd>

                            <dt class="col-sm-5">Nascimento:</dt>
                            <dd class="col-sm-7">${animalDetalhado.data_nascimento}</dd>

                            ${animalDetalhado.data_aquisicao ? `
                                <dt class="col-sm-5">Aquisição:</dt>
                                <dd class="col-sm-7">${animalDetalhado.data_aquisicao}</dd>
                            ` : ''}
                        </dl>

                        ${animalDetalhado.observacoes ? `
                            <div class="mt-3">
                                <h6><i class="fas fa-sticky-note me-2"></i>Observações:</h6>
                                <p class="text-muted small">${animalDetalhado.observacoes}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>

        <div class="alert alert-success mt-3">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Dados Completos:</strong> Informações detalhadas carregadas com sucesso.
        </div>
    `;
}

// Renderizar detalhes básicos quando offline
function renderizarDetalhesBasicos(animalBasico) {
    const detailsContainer = document.getElementById('animal-details');

    detailsContainer.innerHTML = `
        <div class="row g-3">
            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-id-card me-2"></i>
                            Identificação (Dados Básicos)
                        </h6>
                    </div>
                    <div class="card-body">
                        <dl class="row">
                            <dt class="col-sm-5">Brinco:</dt>
                            <dd class="col-sm-7"><strong>${animalBasico.numero_brinco}</strong></dd>

                            <dt class="col-sm-5">Categoria:</dt>
                            <dd class="col-sm-7">${animalBasico.categoria}</dd>

                            <dt class="col-sm-5">Sexo:</dt>
                            <dd class="col-sm-7">${animalBasico.sexo === 'F' ? 'Fêmea' : 'Macho'}</dd>

                            <dt class="col-sm-5">Raça:</dt>
                            <dd class="col-sm-7">${animalBasico.raca || 'N/A'}</dd>

                            <dt class="col-sm-5">Status:</dt>
                            <dd class="col-sm-7">
                                <span class="badge ${animalBasico.status === 'ATIVO' ? 'bg-success' : 'bg-secondary'}">
                                    ${animalBasico.status}
                                </span>
                            </dd>
                        </dl>
                    </div>
                </div>
            </div>

            <div class="col-md-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-info-circle me-2"></i>
                            Status Offline
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Dados Limitados:</strong> Informações detalhadas
                            (peso, nascimento, observações) não estão disponíveis offline.
                        </div>

                        <div class="mt-3">
                            <h6>Para ver dados completos:</h6>
                            <ul class="small">
                                <li>Conecte-se à internet</li>
                                <li>Atualize a página</li>
                                <li>Clique novamente no animal</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="alert alert-info mt-3">
            <i class="fas fa-wifi-slash me-2"></i>
            <strong>Modo Offline:</strong> Mostrando apenas dados básicos do cache.
            Conecte-se para ver informações completas.
        </div>
    `;
}

// Limpar filtros
function limparFiltros() {
    document.getElementById('search-input').value = '';
    document.getElementById('categoria-filter').value = '';
    document.getElementById('sexo-filter').value = '';

    currentFilters = { search: '', categoria: '', sexo: '' };
    filteredAnimais = [...animaisData];

    renderizarTabela();
    mostrarNotificacao('Filtros limpos', 'info');
}

// Exportar para CSV
function exportToCSV() {
    if (filteredAnimais.length === 0) {
        mostrarNotificacao('Nenhum dado para exportar', 'warning');
        return;
    }

    const headers = ['Brinco', 'Categoria', 'Sexo', 'Raça', 'Peso (kg)', 'Data Nascimento', 'Status', 'Observações'];
    const rows = filteredAnimais.map(animal => [
        animal.numero_brinco,
        animal.categoria,
        animal.sexo,
        animal.raca || '',
        animal.peso_atual || '',
        animal.data_nascimento,
        animal.status,
        animal.observacoes || ''
    ]);

    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');

    downloadFile(csvContent, 'animais_offline.csv', 'text/csv');
}

// Exportar para JSON
function exportToJSON() {
    if (filteredAnimais.length === 0) {
        mostrarNotificacao('Nenhum dado para exportar', 'warning');
        return;
    }

    const jsonContent = JSON.stringify({
        exportado_em: new Date().toISOString(),
        filtros_aplicados: currentFilters,
        total_animais: filteredAnimais.length,
        animais: filteredAnimais
    }, null, 2);

    downloadFile(jsonContent, 'animais_offline.json', 'application/json');
}

// Função auxiliar para download de arquivos
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
    mostrarNotificacao(`Arquivo ${filename} baixado com sucesso!`, 'success');
}

// Mostrar mensagem quando não há resultados
function mostrarMensagemVazia(mensagem) {
    const container = document.getElementById('results-container');
    const noResults = document.getElementById('no-results');

    container.style.display = 'none';
    noResults.style.display = 'block';
    noResults.querySelector('h5').textContent = mensagem;
}

// Mostrar notificações
function mostrarNotificacao(mensagem, tipo = 'info') {
    // Implementar sistema de notificações
    console.log(`[${tipo.toUpperCase()}] ${mensagem}`);

    // Se tiver um sistema de notificações, usar aqui
    // Por exemplo: toastr, bootstrap toast, etc.
}

// Função debounce para busca em tempo real
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Função para tentar sincronizar quando volta online
function tentarSincronizar() {
    if (navigator.onLine && 'serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(registration => {
            registration.sync.register('sync-pending-data')
                .then(() => console.log('🔄 Sincronização solicitada'))
                .catch(err => console.log('❌ Erro na sync:', err));
        });
    }
}

// Tentar sincronizar quando volta online
window.addEventListener('online', () => {
    setTimeout(tentarSincronizar, 1000);
});

console.log('🐄 Sistema de Animais Offline carregado!');