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

// URLs de API que devem ser cacheadas para offline (OTIMIZADO)
const API_CACHE_PATTERNS = [
  /\/api\/animais\/offline\/basico\//,    // Cache básico (leve - até 5000 animais)
  /\/api\/animais\/offline\/detalhes\//,  // Cache detalhado (sob demanda - até 100 animais)
  /\/api\/propriedade\/\d+\/animais\/offline\//,
  /\/api\/animal\/\d+\/offline\//,
  /\/api\/rebanho\//
];

// Configurações de cache otimizado para reduzir volume de dados
const CACHE_CONFIG = {
  MAX_ANIMAIS_BASICOS: 5000,    // Até 5000 animais básicos (muito leve)
  MAX_ANIMAIS_DETALHADOS: 100,  // Até 100 animais detalhados (mais pesado)
  CACHE_DURATION: 24 * 60 * 60 * 1000, // 24 horas em ms
  COMPRESSION_LEVEL: 6,         // Nível de compressão LZ
  AUTO_CLEANUP: true,           // Limpeza automática de dados velhos
  MAX_CACHE_SIZE: 50 * 1024 * 1024  // 50MB máximo por cache
};

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

// Estratégia especial para APIs - Cache Inteligente + Compressão
async function apiCacheStrategy(request) {
  const url = new URL(request.url);

  try {
    // Tenta buscar da rede primeiro
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // Estratégia baseada no tipo de dados
      if (url.pathname.includes('/basico/')) {
        // Dados básicos: sempre cachear (leve)
        await cacheBasicData(request, networkResponse.clone());
      } else if (url.pathname.includes('/detalhes/')) {
        // Dados detalhados: cachear com limite e compressão
        await cacheDetailedData(request, networkResponse.clone());
      }

      return networkResponse;
    }
  } catch (error) {
    console.log('🌐 API offline, usando cache inteligente...');
  }

  // Fallback para cache inteligente
  return await getIntelligentCache(request);
}

// Cache de dados básicos (sempre cachear - muito leve)
async function cacheBasicData(request, response) {
  try {
    const data = await response.json();

    // Verificar limite de animais básicos
    if (data.animais && data.animais.length > CACHE_CONFIG.MAX_ANIMAIS_BASICOS) {
      console.warn(`⚠️ Muitos animais básicos (${data.animais.length}), truncando para ${CACHE_CONFIG.MAX_ANIMAIS_BASICOS}`);
      data.animais = data.animais.slice(0, CACHE_CONFIG.MAX_ANIMAIS_BASICOS);
      data.total = data.animais.length;
    }

    // Criar resposta comprimida
    const compressedData = await compressData(data);
    const compressedResponse = new Response(compressedData, {
      headers: {
        'Content-Type': 'application/json',
        'X-Cache-Type': 'basic',
        'X-Cache-Time': Date.now(),
        'X-Compressed': 'true'
      }
    });

    const cache = await caches.open(CACHE_NAME);
    await cache.put(request, compressedResponse);

    // Limpeza automática se necessário
    if (CACHE_CONFIG.AUTO_CLEANUP) {
      await cleanupOldCache();
    }

  } catch (error) {
    console.error('❌ Erro ao cachear dados básicos:', error);
  }
}

// Cache de dados detalhados (sob demanda - mais pesado)
async function cacheDetailedData(request, response) {
  try {
    const data = await response.json();

    // Verificar se já temos muitos dados detalhados
    const cache = await caches.open(CACHE_NAME);
    const detailedKeys = await cache.keys().then(requests =>
      requests.filter(req => req.url.includes('/detalhes/'))
    );

    // Se atingiu limite, remover o mais antigo
    if (detailedKeys.length >= CACHE_CONFIG.MAX_ANIMAIS_DETALHADOS) {
      console.log('🗑️ Removendo cache detalhado antigo para liberar espaço...');
      await cache.delete(detailedKeys[0]);
    }

    // Comprimir e cachear
    const compressedData = await compressData(data);
    const compressedResponse = new Response(compressedData, {
      headers: {
        'Content-Type': 'application/json',
        'X-Cache-Type': 'detailed',
        'X-Cache-Time': Date.now(),
        'X-Compressed': 'true'
      }
    });

    await cache.put(request, compressedResponse);

  } catch (error) {
    console.error('❌ Erro ao cachear dados detalhados:', error);
  }
}

// Busca inteligente no cache
async function getIntelligentCache(request) {
  const url = new URL(request.url);
  const cache = await caches.open(CACHE_NAME);

  // Tentar encontrar resposta comprimida
  let cachedResponse = await cache.match(request);

  if (cachedResponse && cachedResponse.headers.get('X-Compressed') === 'true') {
    try {
      // Descomprimir dados
      const compressedData = await cachedResponse.text();
      const decompressedData = await decompressData(compressedData);

      // Criar nova resposta com dados descomprimidos
      cachedResponse = new Response(JSON.stringify(decompressedData), {
        status: cachedResponse.status,
        statusText: cachedResponse.statusText,
        headers: {
          ...Object.fromEntries(cachedResponse.headers),
          'X-Cache-Status': 'offline',
          'X-Decompressed': 'true'
        }
      });
    } catch (error) {
      console.error('❌ Erro ao descomprimir cache:', error);
      return createOfflineErrorResponse(url);
    }
  }

  if (cachedResponse) {
    // Verificar se não está muito velho
    const cacheTime = parseInt(cachedResponse.headers.get('X-Cache-Time') || '0');
    const age = Date.now() - cacheTime;

    if (age < CACHE_CONFIG.CACHE_DURATION) {
      return cachedResponse;
    } else {
      console.log('⏰ Cache expirado, removendo...');
      await cache.delete(request);
    }
  }

  return createOfflineErrorResponse(url);
}

// Criar resposta de erro offline inteligente
function createOfflineErrorResponse(url) {
  let message = 'Dados não disponíveis offline';

  if (url.pathname.includes('/basico/')) {
    message = 'Dados básicos não foram carregados. Conecte-se à internet para carregar.';
  } else if (url.pathname.includes('/detalhes/')) {
    message = 'Detalhes não disponíveis offline. Carregue primeiro quando online.';
  }

  return new Response(JSON.stringify({
    error: 'Dados não disponíveis offline',
    message: message,
    suggestion: 'Conecte-se à internet para carregar estes dados.'
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Compressão simples de dados (base64 + deflate-like)
async function compressData(data) {
  const jsonString = JSON.stringify(data);
  // Compressão básica: apenas base64 por enquanto
  // Pode ser melhorado com bibliotecas como pako.js
  return btoa(jsonString);
}

// Descompressão de dados
async function decompressData(compressedData) {
  const jsonString = atob(compressedData);
  return JSON.parse(jsonString);
}

// Limpeza automática de cache antigo
async function cleanupOldCache() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const keys = await cache.keys();
    const now = Date.now();

    let totalSize = 0;
    const entriesToCheck = [];

    // Verificar tamanho e idade de cada entrada
    for (const request of keys) {
      const response = await cache.match(request);
      if (response) {
        const cacheTime = parseInt(response.headers.get('X-Cache-Time') || '0');
        const age = now - cacheTime;

        // Estimar tamanho (aproximado)
        const contentLength = response.headers.get('content-length');
        const size = contentLength ? parseInt(contentLength) : 1024; // estimativa
        totalSize += size;

        entriesToCheck.push({
          request,
          age,
          size,
          cacheTime
        });
      }
    }

    console.log(`📊 Cache status: ${totalSize / 1024}KB, ${entriesToCheck.length} entradas`);

    // Remover entradas antigas se cache estiver muito grande
    if (totalSize > CACHE_CONFIG.MAX_CACHE_SIZE) {
      console.log('🗑️ Cache muito grande, limpando entradas antigas...');

      // Ordenar por idade (mais antigos primeiro)
      entriesToCheck.sort((a, b) => b.age - a.age);

      // Remover 20% das entradas mais antigas
      const toRemove = Math.ceil(entriesToCheck.length * 0.2);
      for (let i = 0; i < toRemove; i++) {
        await cache.delete(entriesToCheck[i].request);
        console.log(`🗑️ Removido: ${entriesToCheck[i].request.url}`);
      }
    }

  } catch (error) {
    console.error('❌ Erro na limpeza de cache:', error);
  }
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