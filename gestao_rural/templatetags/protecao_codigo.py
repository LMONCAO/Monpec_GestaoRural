"""
Template tags para proteção de código
"""
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def protecao_codigo_js():
    """Inclui script de proteção de código"""
    if settings.DEBUG:
        return mark_safe('')
    
    return mark_safe('''
    <script>
    // Proteção contra cópia e inspeção
    (function() {
        // Desabilitar menu de contexto
        document.addEventListener('contextmenu', e => e.preventDefault());
        
        // Desabilitar seleção
        document.addEventListener('selectstart', e => e.preventDefault());
        
        // Desabilitar cópia
        document.addEventListener('copy', e => e.preventDefault());
        document.addEventListener('cut', e => e.preventDefault());
        document.addEventListener('paste', e => e.preventDefault());
        
        // Bloquear atalhos
        document.addEventListener('keydown', function(e) {
            if (e.keyCode === 123 || // F12
                (e.ctrlKey && e.shiftKey && [73, 74, 67].includes(e.keyCode)) || // Ctrl+Shift+I/J/C
                (e.ctrlKey && [85, 83, 80].includes(e.keyCode))) { // Ctrl+U/S/P
                e.preventDefault();
                return false;
            }
        });
        
        // Detectar DevTools
        let devtools = false;
        setInterval(() => {
            if (window.outerHeight - window.innerHeight > 160 || 
                window.outerWidth - window.innerWidth > 160) {
                if (!devtools) {
                    devtools = true;
                    document.body.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100vh;font-family:Arial;"><h1 style="color:#d32f2f;">Acesso Negado</h1></div>';
                }
            } else {
                devtools = false;
            }
        }, 500);
        
        // Bloquear console
        const noop = () => {};
        ['log', 'debug', 'info', 'warn', 'error'].forEach(m => {
            if (window.console && window.console[m]) {
                window.console[m] = noop;
            }
        });
    })();
    </script>
    ''')


@register.simple_tag
def watermark_codigo():
    """Adiciona watermark invisível para rastreamento"""
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    
    timestamp = int(timezone.now().timestamp())
    session_id = ''
    
    # Tentar obter session ID se disponível
    try:
        # Isso será preenchido no template
        pass
    except:
        pass
    
    watermark_text = f'MONPEC-{timestamp}-{hash(str(timestamp)) % 1000000}'
    
    return mark_safe(f'''
    <div style="position:fixed;bottom:0;right:0;opacity:0.01;pointer-events:none;font-size:1px;color:transparent;z-index:9999;">
        {watermark_text}
    </div>
    ''')


@register.filter
def ofuscar_texto(texto):
    """Ofusca texto sensível (parcialmente)"""
    if not texto:
        return ''
    
    # Ofuscar apenas parte do texto
    if len(texto) > 10:
        return texto[:3] + '*' * (len(texto) - 6) + texto[-3:]
    return '*' * len(texto)







