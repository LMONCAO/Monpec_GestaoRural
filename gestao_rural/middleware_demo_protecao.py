"""
Middleware para proteger propriedade Monpec1 de alterações por usuários de demonstração
Bloqueia operações de escrita (POST, PUT, DELETE) para usuários de demonstração
"""
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import resolve
import re
import logging

logger = logging.getLogger(__name__)


class DemoProtecaoMonpec1Middleware:
    """
    Middleware que bloqueia operações de escrita para usuários de demonstração
    na propriedade Monpec1
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Métodos HTTP que modificam dados (bloquear)
        self.metodos_bloqueados = ['POST', 'PUT', 'PATCH', 'DELETE']
        
        # Rotas que devem ser bloqueadas (padrões de URLs que modificam dados)
        self.rotas_bloqueadas = [
            r'/propriedade/\d+/.*/novo/',
            r'/propriedade/\d+/.*/criar/',
            r'/propriedade/\d+/.*/editar/',
            r'/propriedade/\d+/.*/atualizar/',
            r'/propriedade/\d+/.*/excluir/',
            r'/propriedade/\d+/.*/deletar/',
            r'/propriedade/\d+/.*/salvar/',
            r'/propriedade/\d+/.*/adicionar/',
            r'/propriedade/\d+/.*/remover/',
            r'/propriedade/\d+/.*/api/.*',  # APIs que modificam dados
        ]
        
        # Exceções: rotas que podem ser acessadas mesmo sendo POST
        self.rotas_permitidas = [
            r'/login/',
            r'/logout/',
            r'/criar-usuario-demonstracao/',
        ]
    
    def _is_usuario_demo(self, user):
        """Verifica se o usuário é de demonstração"""
        if not user.is_authenticated:
            return False
        
        # IMPORTANTE: Superusuários e staff nunca são demo
        if user.is_superuser or user.is_staff:
            return False
        
        # Verificar se é usuário demo padrão
        if user.username in ['demo', 'demo_monpec']:
            return True
        
        # Verificar se tem UsuarioAtivo (usuário criado pelo popup)
        try:
            from .models_auditoria import UsuarioAtivo
            UsuarioAtivo.objects.get(usuario=user)
            return True
        except:
            return False
    
    def _is_propriedade_monpec1(self, request):
        """Verifica se a requisição é para a propriedade Monpec1"""
        path = request.path
        
        # Extrair propriedade_id da URL
        match = re.search(r'/propriedade/(\d+)/', path)
        if not match:
            return False
        
        propriedade_id = match.group(1)
        
        try:
            from .models import Propriedade
            propriedade = Propriedade.objects.filter(id=propriedade_id).first()
            if propriedade and 'Monpec1' in propriedade.nome_propriedade:
                return True
        except Exception as e:
            logger.error(f'Erro ao verificar propriedade Monpec1: {e}')
        
        return False
    
    def _is_rota_bloqueada(self, path):
        """Verifica se a rota deve ser bloqueada"""
        # Verificar exceções primeiro
        for pattern in self.rotas_permitidas:
            if re.match(pattern, path):
                return False
        
        # Verificar se é uma rota bloqueada
        for pattern in self.rotas_bloqueadas:
            if re.search(pattern, path):
                return True
        
        return False
    
    def __call__(self, request):
        # Verificar se é usuário de demonstração
        if self._is_usuario_demo(request.user):
            # Verificar se é propriedade Monpec1
            if self._is_propriedade_monpec1(request):
                # Verificar se é método que modifica dados
                if request.method in self.metodos_bloqueados:
                    # Verificar se a rota deve ser bloqueada
                    if self._is_rota_bloqueada(request.path):
                        # Bloquear a requisição
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                            # Requisição AJAX/JSON
                            return JsonResponse({
                                'success': False,
                                'message': '⚠️ Modo de demonstração: Você não pode inserir, editar ou excluir dados na propriedade Monpec1. Apenas visualização permitida.'
                            }, status=403)
                        else:
                            # Requisição normal
                            messages.warning(
                                request,
                                '⚠️ <strong>Modo de demonstração:</strong> Você não pode inserir, editar ou excluir dados na propriedade Monpec1. Apenas visualização permitida.'
                            )
                            # Redirecionar de volta para a página anterior ou módulos
                            propriedade_id = re.search(r'/propriedade/(\d+)/', request.path)
                            if propriedade_id:
                                from django.shortcuts import redirect
                                from django.urls import reverse
                                return redirect('propriedade_modulos', propriedade_id=propriedade_id.group(1))
                            return HttpResponseForbidden('Modo de demonstração: Operação não permitida.')
        
        return self.get_response(request)



