"""
Views para versão de demonstração
"""
from django.shortcuts import render
from django.conf import settings


def comprar_sistema(request):
    """
    Página de compra do sistema
    Mostra mensagem por 4 segundos e redireciona para link de pagamento
    """
    # Link de pagamento (pode ser configurado no settings)
    link_pagamento = getattr(settings, 'DEMO_LINK_PAGAMENTO', 'https://monpec.com.br/assinaturas/')
    
    context = {
        'link_pagamento': link_pagamento,
        'tempo_redirecionamento': 4,  # 4 segundos
    }
    
    return render(request, 'gestao_rural/demo/comprar_sistema.html', context)




