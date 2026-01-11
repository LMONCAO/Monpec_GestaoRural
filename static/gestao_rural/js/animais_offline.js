// JavaScript para funcionalidade offline de animais
// Gerencia busca, filtros e visualização de dados cacheados

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Animais Offline - Inicializando...');

    // Verificar se estamos offline
    if (!navigator.onLine) {
        mostrarNotificacao('Modo offline ativado', 'warning');
    }

    // Inicializar aplicação
    inicializarAplicacao();

    // Configurar event listeners
    configurarEventListeners();

    // Carregar dados iniciais
    carregarDadosIniciais();

    console.log('✅ Animais Offline - Inicializado com sucesso!');
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

// Carregar dados iniciais
function carregarDadosIniciais() {
    if (!animaisData || animaisData.length === 0) {
        mostrarMensagemVazia('Nenhum animal encontrado no cache offline.');
        return;
    }

    console.log(`📊 Carregados ${animaisData.length} animais do cache`);
    mostrarNotificacao(`${animaisData.length} animais carregados do cache offline`, 'info');
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

// Ver detalhes do animal
function verDetalhesAnimal(animalId) {
    const animal = animaisData.find(a => a.id === animalId);
    if (!animal) {
        mostrarNotificacao('Animal não encontrado', 'error');
        return;
    }

    const modal = new bootstrap.Modal(document.getElementById('animalModal'));
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
                            <dd class="col-sm-7"><strong>${animal.numero_brinco}</strong></dd>

                            <dt class="col-sm-5">Categoria:</dt>
                            <dd class="col-sm-7">${animal.categoria}</dd>

                            <dt class="col-sm-5">Sexo:</dt>
                            <dd class="col-sm-7">${animal.sexo === 'F' ? 'Fêmea' : 'Macho'}</dd>

                            <dt class="col-sm-5">Raça:</dt>
                            <dd class="col-sm-7">${animal.raca || 'N/A'}</dd>

                            <dt class="col-sm-5">Status:</dt>
                            <dd class="col-sm-7">
                                <span class="badge ${animal.status === 'ATIVO' ? 'bg-success' : 'bg-secondary'}">
                                    ${animal.status}
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
                            <i class="fas fa-chart-line me-2"></i>
                            Dados Físicos
                        </h6>
                    </div>
                    <div class="card-body">
                        <dl class="row">
                            <dt class="col-sm-5">Peso Atual:</dt>
                            <dd class="col-sm-7">
                                <strong class="text-success">
                                    ${animal.peso_atual || 'N/A'} kg
                                </strong>
                            </dd>

                            <dt class="col-sm-5">Nascimento:</dt>
                            <dd class="col-sm-7">${animal.data_nascimento}</dd>
                        </dl>

                        ${animal.observacoes ? `
                            <div class="mt-3">
                                <h6><i class="fas fa-sticky-note me-2"></i>Observações:</h6>
                                <p class="text-muted small">${animal.observacoes}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>

        <div class="alert alert-info mt-3">
            <i class="fas fa-info-circle me-2"></i>
            <strong>Modo Offline:</strong> Estes dados foram carregados do cache local.
            Para dados atualizados, conecte-se à internet.
        </div>
    `;

    modal.show();
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