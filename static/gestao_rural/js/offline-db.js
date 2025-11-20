/**
 * IndexedDB - Armazenamento Offline
 * MONPEC Curral Inteligente
 */

class OfflineDatabase {
    constructor() {
        this.dbName = 'monpec_curral_db';
        this.dbVersion = 1;
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Store: animais
                if (!db.objectStoreNames.contains('animais')) {
                    const animaisStore = db.createObjectStore('animais', { keyPath: 'id', autoIncrement: true });
                    animaisStore.createIndex('brinco', 'brinco', { unique: true });
                    animaisStore.createIndex('sisbov', 'sisbov', { unique: false });
                }

                // Store: pesagens
                if (!db.objectStoreNames.contains('pesagens')) {
                    const pesagensStore = db.createObjectStore('pesagens', { keyPath: 'id', autoIncrement: true });
                    pesagensStore.createIndex('animal_id', 'animal_id', { unique: false });
                    pesagensStore.createIndex('data', 'data', { unique: false });
                    pesagensStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                // Store: sanidade
                if (!db.objectStoreNames.contains('sanidade')) {
                    const sanidadeStore = db.createObjectStore('sanidade', { keyPath: 'id', autoIncrement: true });
                    sanidadeStore.createIndex('animal_id', 'animal_id', { unique: false });
                    sanidadeStore.createIndex('tipo', 'tipo', { unique: false });
                    sanidadeStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                // Store: reprodutivo
                if (!db.objectStoreNames.contains('reprodutivo')) {
                    const reprodutivoStore = db.createObjectStore('reprodutivo', { keyPath: 'id', autoIncrement: true });
                    reprodutivoStore.createIndex('animal_id', 'animal_id', { unique: false });
                    reprodutivoStore.createIndex('tipo', 'tipo', { unique: false });
                    reprodutivoStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                // Store: movimentacoes
                if (!db.objectStoreNames.contains('movimentacoes')) {
                    const movimentacoesStore = db.createObjectStore('movimentacoes', { keyPath: 'id', autoIncrement: true });
                    movimentacoesStore.createIndex('animal_id', 'animal_id', { unique: false });
                    movimentacoesStore.createIndex('data', 'data', { unique: false });
                    movimentacoesStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                // Store: pendentes_sync
                if (!db.objectStoreNames.contains('pendentes_sync')) {
                    const pendentesStore = db.createObjectStore('pendentes_sync', { keyPath: 'id', autoIncrement: true });
                    pendentesStore.createIndex('tipo', 'tipo', { unique: false });
                    pendentesStore.createIndex('sync_status', 'sync_status', { unique: false });
                    pendentesStore.createIndex('data_criacao', 'data_criacao', { unique: false });
                }
            };
        });
    }

    // ==================== ANIMAIS ====================
    async salvarAnimal(animal) {
        const transaction = this.db.transaction(['animais'], 'readwrite');
        const store = transaction.objectStore('animais');
        
        animal.data_criacao = new Date().toISOString();
        animal.sync_status = 'pending';
        
        return store.add(animal);
    }

    async buscarAnimal(brinco) {
        const transaction = this.db.transaction(['animais'], 'readonly');
        const store = transaction.objectStore('animais');
        const index = store.index('brinco');
        
        return new Promise((resolve, reject) => {
            const request = index.get(brinco);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async listarAnimais() {
        const transaction = this.db.transaction(['animais'], 'readonly');
        const store = transaction.objectStore('animais');
        
        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // ==================== PESAGENS ====================
    async salvarPesagem(pesagem) {
        const transaction = this.db.transaction(['pesagens', 'pendentes_sync'], 'readwrite');
        const pesagensStore = transaction.objectStore('pesagens');
        const pendentesStore = transaction.objectStore('pendentes_sync');
        
        pesagem.data = pesagem.data || new Date().toISOString();
        pesagem.sync_status = 'pending';
        
        const pesagemId = await new Promise((resolve, reject) => {
            const request = pesagensStore.add(pesagem);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });

        // Adiciona à fila de sincronização
        await new Promise((resolve, reject) => {
            const request = pendentesStore.add({
                tipo: 'pesagem',
                registro_id: pesagemId,
                url: '/api/curral/pesagem/',
                method: 'POST',
                payload: pesagem,
                data_criacao: new Date().toISOString(),
                sync_status: 'pending'
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        return pesagemId;
    }

    async buscarPesagens(animalId) {
        const transaction = this.db.transaction(['pesagens'], 'readonly');
        const store = transaction.objectStore('pesagens');
        const index = store.index('animal_id');
        
        return new Promise((resolve, reject) => {
            const request = index.getAll(animalId);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // ==================== SANIDADE ====================
    async salvarSanidade(sanidade) {
        const transaction = this.db.transaction(['sanidade', 'pendentes_sync'], 'readwrite');
        const sanidadeStore = transaction.objectStore('sanidade');
        const pendentesStore = transaction.objectStore('pendentes_sync');
        
        sanidade.data = sanidade.data || new Date().toISOString();
        sanidade.sync_status = 'pending';
        
        const sanidadeId = await new Promise((resolve, reject) => {
            const request = sanidadeStore.add(sanidade);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });

        await new Promise((resolve, reject) => {
            const request = pendentesStore.add({
                tipo: 'sanidade',
                registro_id: sanidadeId,
                url: '/api/curral/sanidade/',
                method: 'POST',
                payload: sanidade,
                data_criacao: new Date().toISOString(),
                sync_status: 'pending'
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        return sanidadeId;
    }

    // ==================== REPRODUTIVO ====================
    async salvarReprodutivo(reprodutivo) {
        const transaction = this.db.transaction(['reprodutivo', 'pendentes_sync'], 'readwrite');
        const reprodutivoStore = transaction.objectStore('reprodutivo');
        const pendentesStore = transaction.objectStore('pendentes_sync');
        
        reprodutivo.data = reprodutivo.data || new Date().toISOString();
        reprodutivo.sync_status = 'pending';
        
        const reprodutivoId = await new Promise((resolve, reject) => {
            const request = reprodutivoStore.add(reprodutivo);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });

        await new Promise((resolve, reject) => {
            const request = pendentesStore.add({
                tipo: 'reprodutivo',
                registro_id: reprodutivoId,
                url: '/api/curral/reprodutivo/',
                method: 'POST',
                payload: reprodutivo,
                data_criacao: new Date().toISOString(),
                sync_status: 'pending'
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        return reprodutivoId;
    }

    // ==================== MOVIMENTAÇÕES ====================
    async salvarMovimentacao(movimentacao) {
        const transaction = this.db.transaction(['movimentacoes', 'pendentes_sync'], 'readwrite');
        const movimentacoesStore = transaction.objectStore('movimentacoes');
        const pendentesStore = transaction.objectStore('pendentes_sync');
        
        movimentacao.data = movimentacao.data || new Date().toISOString();
        movimentacao.sync_status = 'pending';
        
        const movimentacaoId = await new Promise((resolve, reject) => {
            const request = movimentacoesStore.add(movimentacao);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });

        await new Promise((resolve, reject) => {
            const request = pendentesStore.add({
                tipo: 'movimentacao',
                registro_id: movimentacaoId,
                url: '/api/curral/movimentacao/',
                method: 'POST',
                payload: movimentacao,
                data_criacao: new Date().toISOString(),
                sync_status: 'pending'
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        return movimentacaoId;
    }

    // ==================== SINCRONIZAÇÃO ====================
    async getPendentesSync() {
        const transaction = this.db.transaction(['pendentes_sync'], 'readonly');
        const store = transaction.objectStore('pendentes_sync');
        const index = store.index('sync_status');
        
        return new Promise((resolve, reject) => {
            const request = index.getAll('pending');
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async marcarComoSincronizado(id) {
        const transaction = this.db.transaction(['pendentes_sync'], 'readwrite');
        const store = transaction.objectStore('pendentes_sync');
        
        return new Promise((resolve, reject) => {
            const request = store.get(id);
            request.onsuccess = () => {
                const data = request.result;
                if (data) {
                    data.sync_status = 'synced';
                    data.data_sync = new Date().toISOString();
                    const updateRequest = store.put(data);
                    updateRequest.onsuccess = () => resolve();
                    updateRequest.onerror = () => reject(updateRequest.error);
                } else {
                    resolve();
                }
            };
            request.onerror = () => reject(request.error);
        });
    }

    async removerPendente(id) {
        const transaction = this.db.transaction(['pendentes_sync'], 'readwrite');
        const store = transaction.objectStore('pendentes_sync');
        
        return store.delete(id);
    }

    // ==================== ESTATÍSTICAS ====================
    async getEstatisticas() {
        const [animais, pesagens, sanidade, reprodutivo, movimentacoes, pendentes] = await Promise.all([
            this.listarAnimais(),
            this.db.transaction(['pesagens'], 'readonly').objectStore('pesagens').getAll(),
            this.db.transaction(['sanidade'], 'readonly').objectStore('sanidade').getAll(),
            this.db.transaction(['reprodutivo'], 'readonly').objectStore('reprodutivo').getAll(),
            this.db.transaction(['movimentacoes'], 'readonly').objectStore('movimentacoes').getAll(),
            this.getPendentesSync()
        ]);

        return {
            total_animais: animais.length,
            total_pesagens: pesagens.result?.length || 0,
            total_sanidade: sanidade.result?.length || 0,
            total_reprodutivo: reprodutivo.result?.length || 0,
            total_movimentacoes: movimentacoes.result?.length || 0,
            pendentes_sync: pendentes.length
        };
    }
}

// Instância global
window.offlineDB = new OfflineDatabase();

// Inicializa quando disponível
if ('indexedDB' in window) {
    window.offlineDB.init().then(() => {
        console.log('[OfflineDB] Banco de dados inicializado');
    }).catch((error) => {
        console.error('[OfflineDB] Erro ao inicializar:', error);
    });
}






