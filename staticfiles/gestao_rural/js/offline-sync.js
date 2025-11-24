/**
 * Sincronização Offline/Online
 * MONPEC Curral Inteligente
 */

class OfflineSync {
    constructor() {
        this.isOnline = navigator.onLine;
        this.syncInProgress = false;
        this.syncInterval = null;
        this.init();
    }

    init() {
        // Detecta mudanças de conexão
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Inicia sincronização periódica se online
        if (this.isOnline) {
            this.startPeriodicSync();
        }

        // Registra service worker para sincronização em background
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            this.registerBackgroundSync();
        }
    }

    handleOnline() {
        console.log('[OfflineSync] Conexão restaurada');
        this.isOnline = true;
        this.showNotification('Conexão restaurada', 'Sincronizando dados...', 'success');
        this.syncAll();
        this.startPeriodicSync();
    }

    handleOffline() {
        console.log('[OfflineSync] Modo offline ativado');
        this.isOnline = false;
        this.showNotification('Modo offline', 'Você pode continuar trabalhando. Os dados serão sincronizados quando a conexão voltar.', 'info');
        this.stopPeriodicSync();
    }

    async syncAll() {
        if (this.syncInProgress || !this.isOnline) {
            return;
        }

        this.syncInProgress = true;

        try {
            const pendentes = await window.offlineDB.getPendentesSync();
            
            if (pendentes.length === 0) {
                console.log('[OfflineSync] Nenhum dado pendente');
                this.syncInProgress = false;
                return;
            }

            console.log(`[OfflineSync] Sincronizando ${pendentes.length} registros...`);

            let sucesso = 0;
            let erro = 0;

            for (const pendente of pendentes) {
                try {
                    const response = await fetch(pendente.url, {
                        method: pendente.method || 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify(pendente.payload)
                    });

                    if (response.ok) {
                        await window.offlineDB.marcarComoSincronizado(pendente.id);
                        sucesso++;
                    } else {
                        console.error('[OfflineSync] Erro ao sincronizar:', response.status);
                        erro++;
                    }
                } catch (error) {
                    console.error('[OfflineSync] Erro ao sincronizar registro:', error);
                    erro++;
                }
            }

            if (sucesso > 0) {
                this.showNotification(
                    'Sincronização concluída',
                    `${sucesso} registro(s) sincronizado(s) com sucesso.`,
                    'success'
                );
            }

            if (erro > 0) {
                this.showNotification(
                    'Erro na sincronização',
                    `${erro} registro(s) não puderam ser sincronizados.`,
                    'error'
                );
            }

        } catch (error) {
            console.error('[OfflineSync] Erro na sincronização:', error);
            this.showNotification('Erro', 'Ocorreu um erro ao sincronizar os dados.', 'error');
        } finally {
            this.syncInProgress = false;
        }
    }

    startPeriodicSync() {
        // Sincroniza a cada 5 minutos se online
        this.syncInterval = setInterval(() => {
            if (this.isOnline && !this.syncInProgress) {
                this.syncAll();
            }
        }, 5 * 60 * 1000); // 5 minutos
    }

    stopPeriodicSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }

    async registerBackgroundSync() {
        try {
            const registration = await navigator.serviceWorker.ready;
            
            if ('sync' in registration) {
                await registration.sync.register('sync-offline-data');
                console.log('[OfflineSync] Background sync registrado');
            }
        } catch (error) {
            console.error('[OfflineSync] Erro ao registrar background sync:', error);
        }
    }

    getCSRFToken() {
        const cookie = document.cookie.match(/csrftoken=([^;]+)/);
        return cookie ? cookie[1] : '';
    }

    showNotification(title, message, type = 'info') {
        // Cria notificação visual
        const notification = document.createElement('div');
        notification.className = `sync-notification sync-${type}`;
        notification.innerHTML = `
            <div class="sync-notification-icon">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            </div>
            <div class="sync-notification-content">
                <div class="sync-notification-title">${title}</div>
                <div class="sync-notification-message">${message}</div>
            </div>
            <button class="sync-notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        document.body.appendChild(notification);

        // Auto-remove após 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Força sincronização manual
    async forceSync() {
        if (!this.isOnline) {
            this.showNotification('Offline', 'Você está offline. Não é possível sincronizar.', 'error');
            return;
        }

        this.showNotification('Sincronizando', 'Aguarde...', 'info');
        await this.syncAll();
    }
}

// Inicializa quando disponível
if (window.offlineDB) {
    window.offlineSync = new OfflineSync();
} else {
    // Aguarda inicialização do IndexedDB
    setTimeout(() => {
        if (window.offlineDB) {
            window.offlineSync = new OfflineSync();
        }
    }, 1000);
}







