"""
Views relacionadas a Propriedades Rurais
Refatorado do views.py principal para melhor organização
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

from .models import Propriedade, ProdutorRural
from .forms import PropriedadeForm
from .decorators import bloquear_demo_cadastro
from .helpers_acesso import is_usuario_assinante
from .services.propriedade_service import PropriedadeService
from .services.produtor_service import ProdutorService

logger = logging.getLogger(__name__)


@login_required
def propriedades_lista(request, produtor_id):
    """Lista de propriedades de um produtor"""
    # Verificar permissão usando o serviço
    if is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    # Verificar se tem permissão
    if not ProdutorService.pode_acessar_produtor(request.user, produtor):
        messages.error(request, 'Você não tem permissão para acessar este produtor.')
        return redirect('dashboard')
    
    # Buscar propriedades usando o serviço
    propriedades = PropriedadeService.obter_propriedades_do_produtor(request.user, produtor)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
    }
    return render(request, 'gestao_rural/propriedades_lista.html', context)


@login_required
def propriedade_nova(request, produtor_id=None):
    """Cadastro de nova propriedade - sempre permite seleção de produtor"""
    produtor = None
    
    # Se produtor_id foi fornecido na URL, buscar o produtor (apenas para pré-selecionar)
    # Mas o campo sempre será exibido para permitir alteração
    if produtor_id:
        # Verificar permissão
        if request.user.is_superuser or request.user.is_staff:
            produtor = get_object_or_404(ProdutorRural, id=produtor_id)
        elif is_usuario_assinante(request.user):
            produtor = get_object_or_404(ProdutorRural, id=produtor_id)
        else:
            produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
        
        # Verificar se tem permissão
        if not ProdutorService.pode_acessar_produtor(request.user, produtor):
            messages.error(request, 'Você não tem permissão para criar propriedade para este produtor.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, user=request.user, produtor_initial=produtor)
        if form.is_valid():
            try:
                propriedade = form.save()
                messages.success(request, 'Propriedade cadastrada com sucesso!')
                return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
            except Exception as e:
                logger.error(f'Erro ao salvar propriedade: {e}', exc_info=True)
                messages.error(request, 'Erro ao cadastrar propriedade. Por favor, tente novamente.')
    else:
        form = PropriedadeForm(user=request.user, produtor_initial=produtor)
    
    context = {
        'form': form,
        'produtor': produtor,
    }
    return render(request, 'gestao_rural/propriedade_nova.html', context)


@login_required
@bloquear_demo_cadastro
def propriedade_editar(request, propriedade_id):
    """Edição de propriedade"""
    # Buscar propriedade
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Verificar permissão usando o serviço
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para editar esta propriedade.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, instance=propriedade, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Propriedade atualizada com sucesso!')
                return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
            except Exception as e:
                logger.error(f'Erro ao atualizar propriedade: {e}', exc_info=True)
                messages.error(request, 'Erro ao atualizar propriedade. Por favor, tente novamente.')
    else:
        form = PropriedadeForm(instance=propriedade, user=request.user)
    
    context = {
        'form': form,
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/propriedade_editar.html', context)


@login_required
@bloquear_demo_cadastro
def propriedade_excluir(request, propriedade_id):
    """Exclusão de propriedade"""
    # Buscar propriedade
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Verificar permissão usando o serviço
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para excluir esta propriedade.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        produtor_id = propriedade.produtor.id
        try:
            propriedade.delete()
            messages.success(request, 'Propriedade excluída com sucesso!')
            return redirect('propriedades_lista', produtor_id=produtor_id)
        except Exception as e:
            logger.error(f'Erro ao excluir propriedade: {e}', exc_info=True)
            messages.error(request, 'Erro ao excluir propriedade. Por favor, tente novamente.')
            return redirect('propriedades_lista', produtor_id=produtor_id)
    
    return render(request, 'gestao_rural/propriedade_excluir.html', {'propriedade': propriedade})


