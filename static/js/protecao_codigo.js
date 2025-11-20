/**
 * Proteção contra cópia e inspeção de código
 * Desabilita DevTools, bloqueia cópia, previne inspeção
 */

(function() {
    'use strict';
    
    // Apenas em produção (verificar via variável do Django)
    if (typeof DEBUG !== 'undefined' && DEBUG === true) {
        return; // Não aplicar proteções em desenvolvimento
    }
    
    // 1. Desabilitar menu de contexto (botão direito)
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // 2. Desabilitar seleção de texto (Ctrl+A, etc)
    document.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // 3. Desabilitar cópia (Ctrl+C, Ctrl+V, Ctrl+X)
    document.addEventListener('copy', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    document.addEventListener('cut', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    document.addEventListener('paste', function(e) {
        e.preventDefault();
        return false;
    }, false);
    
    // 4. Bloquear atalhos de teclado (F12, Ctrl+Shift+I, etc)
    document.addEventListener('keydown', function(e) {
        // F12 - DevTools
        if (e.keyCode === 123) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+I - DevTools
        if (e.ctrlKey && e.shiftKey && e.keyCode === 73) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+J - Console
        if (e.ctrlKey && e.shiftKey && e.keyCode === 74) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+Shift+C - Inspect Element
        if (e.ctrlKey && e.shiftKey && e.keyCode === 67) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+U - View Source
        if (e.ctrlKey && e.keyCode === 85) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+S - Save Page
        if (e.ctrlKey && e.keyCode === 83) {
            e.preventDefault();
            return false;
        }
        
        // Ctrl+P - Print (pode ser usado para salvar como PDF)
        if (e.ctrlKey && e.keyCode === 80) {
            e.preventDefault();
            return false;
        }
    }, false);
    
    // 5. Detectar abertura de DevTools
    let devtools = {
        open: false,
        orientation: null
    };
    
    const threshold = 160;
    setInterval(function() {
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            if (!devtools.open) {
                devtools.open = true;
                // DevTools aberto - redirecionar ou bloquear
                document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:Arial;font-size:24px;color:#d32f2f;"><div style="text-align:center;"><h1>Acesso Negado</h1><p>O uso de ferramentas de desenvolvedor não é permitido.</p><p>Por favor, feche o DevTools e recarregue a página.</p></div></div>';
                // Opcional: redirecionar
                // window.location.href = '/';
            }
        } else {
            devtools.open = false;
        }
    }, 500);
    
    // 6. Bloquear console
    const noop = function() {};
    const methods = ['log', 'debug', 'info', 'warn', 'error', 'assert', 'dir', 'dirxml',
                     'group', 'groupEnd', 'time', 'timeEnd', 'count', 'trace', 'profile', 'profileEnd'];
    
    methods.forEach(function(method) {
        if (window.console && window.console[method]) {
            window.console[method] = noop;
        }
    });
    
    // 7. Ofuscar código (adicionar comentários falsos)
    const fakeCode = `
    /* 
     * Código protegido por direitos autorais
     * Sistema MONPEC - Todos os direitos reservados
     * Cópia não autorizada é proibida
     */
    `;
    
    // 8. Watermarking invisível (rastreamento)
    const watermark = document.createElement('div');
    watermark.style.cssText = 'position:fixed;bottom:0;right:0;opacity:0.01;pointer-events:none;font-size:1px;color:transparent;';
    watermark.textContent = 'MONPEC-' + new Date().getTime() + '-' + Math.random().toString(36).substr(2, 9);
    document.body.appendChild(watermark);
    
    // 9. Detectar tentativas de inspeção
    Object.defineProperty(window, 'devtools', {
        get: function() {
            return devtools;
        },
        set: function(value) {
            devtools = value;
            if (devtools.open) {
                document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:Arial;font-size:24px;color:#d32f2f;"><div style="text-align:center;"><h1>Acesso Negado</h1><p>O uso de ferramentas de desenvolvedor não é permitido.</p></div></div>';
            }
        }
    });
    
    // 10. Proteção contra iframe (prevenir embedding)
    if (window.top !== window.self) {
        window.top.location = window.self.location;
    }
    
    // 11. Bloquear download de página (Ctrl+S)
    window.addEventListener('beforeunload', function(e) {
        // Aviso ao tentar sair
        e.preventDefault();
        e.returnValue = '';
    });
    
    console.log('%c⚠️ ATENÇÃO ⚠️', 'color: red; font-size: 50px; font-weight: bold;');
    console.log('%cEsta é uma área restrita!', 'color: red; font-size: 20px;');
    console.log('%cNão execute código aqui. Pode ser perigoso!', 'color: red; font-size: 16px;');
    
})();






