"""
Views relacionadas a Produtores Rurais
Refatorado do views.py principal para melhor organização
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
import logging

from .models import ProdutorRural
from .forms import ProdutorRuralForm
from .decorators import bloquear_demo_cadastro
from .helpers_acesso import is_usuario_demo, is_usuario_assinante
from .services.produtor_service import ProdutorService

logger = logging.getLogger(__name__)


@login_required
def produtor_novo(request):
    """Cadastro de novo produtor rural"""
    is_demo_user = is_usuario_demo(request.user)
    
    # Se for usuário demo, redirecionar para setup automático
    if is_demo_user:
        logger.info(f'Usuário demo tentou acessar cadastro de produtor. Redirecionando para demo_setup.')
        return redirect('demo_setup')
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST)
        if form.is_valid():
            try:
                produtor = form.save(commit=False)
                produtor.usuario_responsavel = request.user
                produtor.save()
                
                # Se for usuário demo, criar propriedade automaticamente
                if is_demo_user:
                    try:
                        dados_produtor = {
                            'nome': produtor.nome,
                            'cpf_cnpj': produtor.cpf_cnpj,
                            'email': produtor.email,
                            'telefone': produtor.telefone or '',
                        }
                        produtor, propriedade = ProdutorService.criar_produtor_com_propriedade_demo(
                            request.user,
                            dados_produtor
                        )
                        messages.success(
                            request, 
                            f'Produtor e propriedade {propriedade.nome_propriedade} cadastrados com sucesso! Bem-vindo à demonstração!'
                        )
                        return redirect('propriedade_modulos', propriedade_id=propriedade.id)
                    except Exception as e:
                        logger.error(f'Erro ao criar propriedade Monpec automaticamente: {e}')
                        messages.warning(
                            request, 
                            'Produtor cadastrado, mas houve um erro ao criar a propriedade. Por favor, crie manualmente.'
                        )
                
                messages.success(request, 'Produtor cadastrado com sucesso!')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f'Erro ao salvar produtor: {e}', exc_info=True)
                messages.error(request, 'Erro ao cadastrar produtor. Por favor, tente novamente.')
    else:
        # Pré-preencher formulário com dados do usuário de demonstração
        initial_data = ProdutorService.obter_dados_iniciais_demo(request.user) if is_demo_user else {}
        form = ProdutorRuralForm(initial=initial_data)
    
    # Buscar lista de produtores usando o serviço
    produtores = ProdutorService.obter_produtores_do_usuario(request.user)
    
    context = {
        'form': form,
        'is_demo_user': is_demo_user,
        'produtores': produtores,
    }
    return render(request, 'gestao_rural/produtor_novo.html', context)


@login_required
@bloquear_demo_cadastro
def produtor_editar(request, produtor_id):
    """Edição de produtor rural"""
    # Verificar permissão usando o serviço
    if is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    # Verificar se tem permissão
    if not ProdutorService.pode_acessar_produtor(request.user, produtor):
        messages.error(request, 'Você não tem permissão para editar este produtor.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST, request.FILES, instance=produtor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produtor atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm(instance=produtor)
    
    return render(request, 'gestao_rural/produtor_editar.html', {
        'form': form, 
        'produtor': produtor,
        'today': date.today()
    })


@login_required
@bloquear_demo_cadastro
def produtor_excluir(request, produtor_id):
    """Exclusão de produtor rural"""
    # Verificar permissão
    if is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    # Verificar se tem permissão
    if not ProdutorService.pode_acessar_produtor(request.user, produtor):
        messages.error(request, 'Você não tem permissão para excluir este produtor.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        produtor.delete()
        messages.success(request, 'Produtor excluído com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'gestao_rural/produtor_excluir.html', {'produtor': produtor})

