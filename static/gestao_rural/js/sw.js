// Service Worker para Monpec PWA
// Gerencia cache offline e sincronização de dados

const CACHE_NAME = 'monpec-v1.0.0';
const OFFLINE_URL = '/offline/';

// Recursos críticos que sempre ficam em cache
const CRITICAL_RESOURCES = [
  '/',
  '/static/gestao_rural/css/estilo.css',
  '/static/gestao_rural/js/jquery.min.js',
  '/static/gestao_rural/js/bootstrap.min.js',
  '/static/gestao_rural/js/main.js',
  '/static/gestao_rural/images/logo.png',
  '/offline/',
  '/manifest.json'
];

// URLs de API que devem ser cacheadas para offline
const API_CACHE_PATTERNS = [
  /\/api\/animais\//,
  /\/api\/propriedade\/\d+\/animais\//,
  /\/api\/animal\/\d+\//,
  /\/api\/rebanho\//
];

// Install Event - Cache inicial
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Cacheando recursos críticos...');
        return cache.addAll(CRITICAL_RESOURCES);
      })
      .then(() => {
        console.log('✅ Service Worker instalado com sucesso!');
        return self.skipWaiting();
      })
  );
});

// Activate Event - Limpeza de caches antigos
self.addEventListener('activate', (event) => {
  console.log('🎯 Service Worker ativando...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('✅ Service Worker ativado!');
      return self.clients.claim();
    })
  );
});

// Fetch Event - Estratégia de cache
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Estratégia 1: Cache First para recursos estáticos
  if (event.request.destination === 'style' ||
      event.request.destination === 'script' ||
      event.request.destination === 'image' ||
      event.request.destination === 'font') {
    event.respondWith(cacheFirstStrategy(event.request));
    return;
  }

  // Estratégia 2: Network First para páginas HTML
  if (event.request.destination === 'document') {
    event.respondWith(networkFirstStrategy(event.request));
    return;
  }

  // Estratégia 3: Cache para APIs importantes
  if (API_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname))) {
    event.respondWith(apiCacheStrategy(event.request));
    return;
  }

  // Estratégia padrão: Network First
  event.respondWith(networkFirstStrategy(event.request));
});

// Estratégia Cache First - Para recursos estáticos
async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('❌ Erro na estratégia Cache First:', error);
    return new Response('Recurso não disponível offline', { status: 503 });
  }
}

// Estratégia Network First - Para páginas dinâmicas
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('🌐 Rede indisponível, tentando cache...');
  }

  // Fallback para cache
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  // Último fallback - página offline
  if (request.destination === 'document') {
    const offlineResponse = await caches.match(OFFLINE_URL);
    if (offlineResponse) {
      return offlineResponse;
    }
  }

  return new Response('Serviço indisponível', { status: 503 });
}

// Estratégia especial para APIs - Cache + Background Sync
async function apiCacheStrategy(request) {
  try {
    // Tenta buscar da rede primeiro
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
  } catch (error) {
    console.log('🌐 API offline, usando cache...');
  }

  // Fallback para cache
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    // Adiciona header indicando que é do cache
    const response = new Response(cachedResponse.body, {
      status: cachedResponse.status,
      statusText: cachedResponse.statusText,
      headers: {
        ...cachedResponse.headers,
        'X-Cache-Status': 'offline'
      }
    });
    return response;
  }

  return new Response(JSON.stringify({
    error: 'Dados não disponíveis offline',
    message: 'Esta informação não foi carregada anteriormente'
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Background Sync para sincronizar dados quando voltar online
self.addEventListener('sync', (event) => {
  console.log('🔄 Background Sync:', event.tag);

  if (event.tag === 'sync-pending-data') {
    event.waitUntil(syncPendingData());
  }
});

// Função para sincronizar dados pendentes
async function syncPendingData() {
  console.log('🔄 Sincronizando dados pendentes...');

  try {
    // Aqui você implementaria a lógica para enviar dados pendentes
    // Por exemplo: mudanças em animais, manejos, etc.

    const pendingData = await getPendingDataFromIndexedDB();

    for (const data of pendingData) {
      await sendDataToServer(data);
    }

    console.log('✅ Dados sincronizados com sucesso!');
  } catch (error) {
    console.log('❌ Erro na sincronização:', error);
  }
}

// Placeholder functions - implemente conforme sua necessidade
async function getPendingDataFromIndexedDB() {
  // Implementar busca de dados pendentes no IndexedDB
  return [];
}

async function sendDataToServer(data) {
  // Implementar envio de dados para o servidor
  return fetch('/api/sync/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

// Message Event - Comunicação com a página principal
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'GET_CACHE_STATUS') {
    caches.keys().then((cacheNames) => {
      event.ports[0].postMessage({
        cacheNames: cacheNames,
        currentCache: CACHE_NAME
      });
    });
  }
});

console.log('🚀 Service Worker Monpec carregado!');