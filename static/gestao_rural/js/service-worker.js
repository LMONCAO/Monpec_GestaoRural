/**
 * Service Worker - MONPEC Curral Inteligente
 * Funciona offline e sincroniza quando online
 */

const CACHE_NAME = 'monpec-curral-v1.0.0';
const OFFLINE_CACHE = 'monpec-offline-v1.0.0';
const API_CACHE = 'monpec-api-v1.0.0';

// Arquivos estáticos para cache
const STATIC_ASSETS = [
    '/static/gestao_rural/css/curral_enhanced.css',
    '/static/gestao_rural/js/curral_super_tela_enhanced.js',
    '/static/gestao_rural/manifest.json',
    '/static/gestao_rural/icons/icon-192x192.png',
    '/static/gestao_rural/icons/icon-512x512.png'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Cacheando arquivos estáticos');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Ativando...');
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE && cacheName !== API_CACHE) {
                        console.log('[Service Worker] Removendo cache antigo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Estratégia: Network First, fallback para Cache, depois Offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Ignora requisições não-GET
    if (request.method !== 'GET') {
        return;
    }

    // API requests - Network First com cache
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/curral/api/')) {
        event.respondWith(networkFirstStrategy(request));
        return;
    }

    // HTML pages - Network First, fallback para cache
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(networkFirstWithOfflineFallback(request));
        return;
    }

    // Static assets - Cache First
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirstStrategy(request));
        return;
    }

    // Default: Network First
    event.respondWith(networkFirstStrategy(request));
});

// Estratégia: Network First
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cachea resposta bem-sucedida
        if (networkResponse.ok) {
            const cache = await caches.open(API_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Network falhou, tentando cache:', request.url);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Retorna resposta offline se disponível
        return new Response(
            JSON.stringify({ 
                error: 'Offline', 
                message: 'Você está offline. Os dados serão sincronizados quando a conexão voltar.',
                offline: true 
            }),
            {
                headers: { 'Content-Type': 'application/json' },
                status: 503
            }
        );
    }
}

// Estratégia: Network First com fallback offline
async function networkFirstWithOfflineFallback(request) {
    try {
        const networkResponse = await fetch(request);
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Página offline genérica
        return caches.match('/offline.html') || new Response(
            '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>Você está offline</h1><p>Algumas funcionalidades podem estar limitadas.</p></body></html>',
            { headers: { 'Content-Type': 'text/html' } }
        );
    }
}

// Estratégia: Cache First
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Erro ao buscar:', request.url);
        throw error;
    }
}

// Sincronização em background quando online
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Sincronização em background:', event.tag);
    
    if (event.tag === 'sync-offline-data') {
        event.waitUntil(syncOfflineData());
    }
});

// Sincroniza dados offline quando conexão volta
async function syncOfflineData() {
    try {
        // Busca dados pendentes do IndexedDB
        const pendingData = await getPendingDataFromIndexedDB();
        
        if (pendingData.length === 0) {
            console.log('[Service Worker] Nenhum dado pendente para sincronizar');
            return;
        }
        
        console.log(`[Service Worker] Sincronizando ${pendingData.length} registros...`);
        
        // Envia cada registro
        for (const data of pendingData) {
            try {
                const response = await fetch(data.url, {
                    method: data.method || 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': data.csrfToken || ''
                    },
                    body: JSON.stringify(data.payload)
                });
                
                if (response.ok) {
                    // Remove do IndexedDB após sucesso
                    await removePendingDataFromIndexedDB(data.id);
                    console.log('[Service Worker] Registro sincronizado:', data.id);
                }
            } catch (error) {
                console.error('[Service Worker] Erro ao sincronizar registro:', error);
            }
        }
        
        // Notifica que sincronização foi concluída
        self.clients.matchAll().then((clients) => {
            clients.forEach((client) => {
                client.postMessage({
                    type: 'SYNC_COMPLETE',
                    count: pendingData.length
                });
            });
        });
    } catch (error) {
        console.error('[Service Worker] Erro na sincronização:', error);
    }
}

// Helper functions para IndexedDB (serão implementadas no cliente)
function getPendingDataFromIndexedDB() {
    return new Promise((resolve) => {
        // Implementação será feita no cliente
        resolve([]);
    });
}

function removePendingDataFromIndexedDB(id) {
    return Promise.resolve();
}

// Notificações push (para futuras implementações)
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push notification recebida');
    
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'MONPEC Curral';
    const options = {
        body: data.body || 'Nova notificação',
        icon: '/static/gestao_rural/icons/icon-192x192.png',
        badge: '/static/gestao_rural/icons/icon-96x96.png',
        data: data.url || '/',
        vibrate: [200, 100, 200],
        tag: data.tag || 'default'
    };
    
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow(event.notification.data || '/')
    );
});






