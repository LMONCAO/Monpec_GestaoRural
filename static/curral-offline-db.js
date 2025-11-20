// Sistema de armazenamento offline usando IndexedDB
class CurralOfflineDB {
  constructor() {
    this.dbName = 'CurralInteligenteDB';
    this.dbVersion = 1;
    this.db = null;
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('[DB] Erro ao abrir IndexedDB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('[DB] IndexedDB aberto com sucesso');
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // Store para fila de sincronização
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', {
            keyPath: 'id',
            autoIncrement: true,
          });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('status', 'status', { unique: false });
          syncStore.createIndex('type', 'type', { unique: false });
        }

        // Store para cache de animais
        if (!db.objectStoreNames.contains('animaisCache')) {
          const animaisStore = db.createObjectStore('animaisCache', {
            keyPath: 'id',
          });
          animaisStore.createIndex('codigo', 'codigo', { unique: true });
          animaisStore.createIndex('numero_brinco', 'numero_brinco', {
            unique: false,
          });
        }

        // Store para sessões offline
        if (!db.objectStoreNames.contains('sessoesOffline')) {
          const sessoesStore = db.createObjectStore('sessoesOffline', {
            keyPath: 'id',
            autoIncrement: true,
          });
          sessoesStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Store para eventos offline
        if (!db.objectStoreNames.contains('eventosOffline')) {
          const eventosStore = db.createObjectStore('eventosOffline', {
            keyPath: 'id',
            autoIncrement: true,
          });
          eventosStore.createIndex('sessao_id', 'sessao_id', {
            unique: false,
          });
          eventosStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        console.log('[DB] Estrutura do banco criada');
      };
    });
  }

  // ========== FILA DE SINCRONIZAÇÃO ==========
  async adicionarSyncItem(item) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');

      const syncItem = {
        ...item,
        timestamp: new Date().toISOString(),
        status: 'pending',
        tentativas: 0,
      };

      const request = store.add(syncItem);

      request.onsuccess = () => {
        console.log('[DB] Item adicionado à fila de sincronização:', syncItem);
        resolve(request.result);
      };

      request.onerror = () => {
        console.error('[DB] Erro ao adicionar item à fila:', request.error);
        reject(request.error);
      };
    });
  }

  async obterItensPendentes() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readonly');
      const store = transaction.objectStore('syncQueue');
      const index = store.index('status');
      const request = index.getAll('pending');

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async marcarItemSincronizado(id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.get(id);

      request.onsuccess = () => {
        const item = request.result;
        if (item) {
          item.status = 'synced';
          item.synced_at = new Date().toISOString();
          store.put(item);
          resolve(item);
        } else {
          reject(new Error('Item não encontrado'));
        }
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async incrementarTentativas(id) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readwrite');
      const store = transaction.objectStore('syncQueue');
      const request = store.get(id);

      request.onsuccess = () => {
        const item = request.result;
        if (item) {
          item.tentativas = (item.tentativas || 0) + 1;
          if (item.tentativas >= 5) {
            item.status = 'failed';
          }
          store.put(item);
          resolve(item);
        } else {
          reject(new Error('Item não encontrado'));
        }
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async contarItensPendentes() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['syncQueue'], 'readonly');
      const store = transaction.objectStore('syncQueue');
      const index = store.index('status');
      const request = index.count('pending');

      request.onsuccess = () => {
        resolve(request.result || 0);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  // ========== CACHE DE ANIMAIS ==========
  async salvarAnimalCache(animal) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['animaisCache'], 'readwrite');
      const store = transaction.objectStore('animaisCache');
      const request = store.put({
        ...animal,
        cached_at: new Date().toISOString(),
      });

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async buscarAnimalCache(codigo) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['animaisCache'], 'readonly');
      const store = transaction.objectStore('animaisCache');
      const index = store.index('codigo');
      const request = index.get(codigo);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  // ========== SESSÕES OFFLINE ==========
  async criarSessaoOffline(sessao) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['sessoesOffline'], 'readwrite');
      const store = transaction.objectStore('sessoesOffline');

      const sessaoOffline = {
        ...sessao,
        timestamp: new Date().toISOString(),
        status: 'offline',
        sincronizado: false,
      };

      const request = store.add(sessaoOffline);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async obterSessoesOffline() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['sessoesOffline'], 'readonly');
      const store = transaction.objectStore('sessoesOffline');
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  // ========== EVENTOS OFFLINE ==========
  async salvarEventoOffline(evento) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['eventosOffline'], 'readwrite');
      const store = transaction.objectStore('eventosOffline');

      const eventoOffline = {
        ...evento,
        timestamp: new Date().toISOString(),
        sincronizado: false,
      };

      const request = store.add(eventoOffline);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }

  async obterEventosOffline(sessaoId) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['eventosOffline'], 'readonly');
      const store = transaction.objectStore('eventosOffline');
      const index = store.index('sessao_id');
      const request = index.getAll(sessaoId);

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(request.error);
      };
    });
  }
}

// Instância global
const curralDB = new CurralOfflineDB();



