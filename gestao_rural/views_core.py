"""
Views principais do sistema - Autenticação, Dashboard e Páginas Públicas
Este módulo contém as views essenciais do sistema.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)


def google_search_console_verification(request):
    """
    Serve o arquivo HTML de verificação do Google Search Console.
    Arquivo: google40933139f3b0d469.html
    O conteúdo deste arquivo é fornecido pelo Google Search Console quando você
    seleciona o método de verificação via arquivo HTML.
    """
    # Conteúdo do arquivo de verificação do Google Search Console
    # O Google espera que o arquivo contenha exatamente: google-site-verification: google40933139f3b0d469.html
    content = "google-site-verification: google40933139f3b0d469.html"
    return HttpResponse(content, content_type='text/html; charset=utf-8')


def landing_page(request):
    """Página pública do sistema antes do login."""
    # Se o usuário já estiver autenticado, redirecionar para o dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Limpar mensagens antigas que não sejam relacionadas a um envio recente
    # Verificar se há um parâmetro indicando que acabamos de processar um formulário
    if 'form_submitted' not in request.GET:
        # Se não foi um submit recente, limpar todas as mensagens antigas da sessão
        # Isso evita que mensagens de sucesso apareçam quando o usuário apenas acessa a página
        storage = messages.get_messages(request)
        # Consumir todas as mensagens para limpar a sessão
        list(storage)
        # Marcar como usado para garantir limpeza
        storage.used = True
    
    # Renderizar a landing page normalmente
    return render(request, 'site/landing_page.html')


@login_required
def dashboard(request):
    """
    Dashboard principal do sistema.
    Mostra visão geral das propriedades e informações importantes.
    """
    from .helpers_acesso import is_usuario_assinante
    from .models import Propriedade, ProdutorRural
    
    user = request.user
    
    # Verificar se é assinante
    is_assinante = is_usuario_assinante(user)
    
    # Buscar propriedades do usuário
    if is_assinante:
        propriedades = Propriedade.objects.select_related('produtor').all().order_by('produtor__nome', 'nome_propriedade')
        produtores = ProdutorRural.objects.all().order_by('nome')
    else:
        propriedades = Propriedade.objects.filter(
            produtor__usuario_responsavel=user
        ).select_related('produtor').order_by('produtor__nome', 'nome_propriedade')
        produtores = ProdutorRural.objects.filter(usuario_responsavel=user).order_by('nome')
    
    context = {
        'propriedades': propriedades,
        'produtores': produtores,
        'is_assinante': is_assinante,
        'total_propriedades': propriedades.count(),
        'total_produtores': produtores.count(),
    }
    
    return render(request, 'gestao_rural/dashboard.html', context)


def logout_view(request):
    """View para logout do usuário."""
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('landing_page')









