// Sistema de sincronização offline/online
class CurralOfflineSync {
  constructor() {
    this.isOnline = navigator.onLine;
    this.syncInterval = null;
    this.syncInProgress = false;
    this.db = curralDB;
    this.syncCallbacks = [];
  }

  async init() {
    await this.db.init();

    // Detectar mudanças de conexão
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.onConnectionRestored();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.onConnectionLost();
    });

    // Iniciar sincronização periódica se online
    if (this.isOnline) {
      this.iniciarSincronizacaoPeriodica();
    }

    // Sincronizar itens pendentes ao iniciar
    if (this.isOnline) {
      setTimeout(() => this.sincronizarPendentes(), 2000);
    }
  }

  onConnectionRestored() {
    console.log('[SYNC] Conexão restaurada!');
    this.mostrarNotificacao('Conexão restaurada. Sincronizando dados...', 'success');
    this.iniciarSincronizacaoPeriodica();
    this.sincronizarPendentes();
  }

  onConnectionLost() {
    console.log('[SYNC] Conexão perdida. Modo offline ativado.');
    this.mostrarNotificacao('Modo offline ativado. Dados serão salvos localmente.', 'warning');
    this.pararSincronizacaoPeriodica();
  }

  iniciarSincronizacaoPeriodica() {
    if (this.syncInterval) return;

    // Sincroniza a cada 30 segundos quando online
    this.syncInterval = setInterval(() => {
      if (this.isOnline && !this.syncInProgress) {
        this.sincronizarPendentes();
      }
    }, 30000);
  }

  pararSincronizacaoPeriodica() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
  }

  async sincronizarPendentes() {
    if (!this.isOnline || this.syncInProgress) {
      return;
    }

    this.syncInProgress = true;
    const pendentes = await this.db.obterItensPendentes();

    if (pendentes.length === 0) {
      this.syncInProgress = false;
      return;
    }

    console.log(`[SYNC] Sincronizando ${pendentes.length} itens pendentes...`);

    let sucessos = 0;
    let erros = 0;

    for (const item of pendentes) {
      try {
        await this.sincronizarItem(item);
        await this.db.marcarItemSincronizado(item.id);
        sucessos++;
      } catch (error) {
        console.error('[SYNC] Erro ao sincronizar item:', item, error);
        await this.db.incrementarTentativas(item.id);
        erros++;
      }
    }

    this.syncInProgress = false;

    if (sucessos > 0) {
      this.mostrarNotificacao(
        `${sucessos} item(ns) sincronizado(s) com sucesso!`,
        'success'
      );
    }

    if (erros > 0) {
      this.mostrarNotificacao(
        `${erros} item(ns) falharam na sincronização.`,
        'error'
      );
    }

    // Atualizar contador de pendentes
    this.atualizarContadorPendentes();
  }

  async sincronizarItem(item) {
    const { type, url, method, payload, headers } = item;

    try {
      // Se for um item da fila antiga, usa endpoint de sincronização
      let syncUrl = url;
      let syncPayload = payload;
      
      // Extrai propriedade_id da URL se possível
      const urlMatch = url.match(/propriedade\/(\d+)\//);
      if (urlMatch && type) {
        const propriedadeId = urlMatch[1];
        syncUrl = `/propriedade/${propriedadeId}/curral/api/sincronizar/`;
        syncPayload = {
          type: type,
          dados: payload
        };
      }

      const response = await fetch(syncUrl, {
        method: method || 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
        body: JSON.stringify(syncPayload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.status !== 'ok') {
        throw new Error(data.mensagem || 'Erro na sincronização');
      }

      // Executar callbacks de sincronização
      this.syncCallbacks.forEach((callback) => {
        try {
          callback(type, item, data);
        } catch (e) {
          console.error('[SYNC] Erro em callback:', e);
        }
      });

      return data;
    } catch (error) {
      console.error('[SYNC] Erro ao sincronizar:', error);
      throw error;
    }
  }

  async adicionarParaSincronizacao(type, url, method, payload, headers = {}) {
    const item = {
      type,
      url,
      method: method || 'POST',
      payload,
      headers,
    };

    if (this.isOnline) {
      // Tenta sincronizar imediatamente
      try {
        await this.sincronizarItem(item);
        return { success: true, synced: true };
      } catch (error) {
        // Se falhar, adiciona à fila
        console.log('[SYNC] Falha na sincronização imediata, adicionando à fila');
      }
    }

    // Adiciona à fila de sincronização
    await this.db.adicionarSyncItem(item);
    this.atualizarContadorPendentes();

    return { success: true, synced: false, queued: true };
  }

  async atualizarContadorPendentes() {
    const count = await this.db.contarItensPendentes();
    const evento = new CustomEvent('syncQueueUpdated', { detail: { count } });
    window.dispatchEvent(evento);
  }

  mostrarNotificacao(mensagem, tipo) {
    // Usa a função mostrarToast se disponível
    if (typeof mostrarToast === 'function') {
      mostrarToast(mensagem, tipo);
    } else {
      console.log(`[${tipo.toUpperCase()}] ${mensagem}`);
    }
  }

  onSync(callback) {
    this.syncCallbacks.push(callback);
  }

  isOnlineStatus() {
    return this.isOnline;
  }
}

// Instância global
const curralSync = new CurralOfflineSync();

