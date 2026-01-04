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
    """Cadastro de novo produtor rural ou edição via query string"""
    is_demo_user = is_usuario_demo(request.user)
    
    # Se for usuário demo, redirecionar para setup automático
    if is_demo_user:
        logger.info(f'Usuário demo tentou acessar cadastro de produtor. Redirecionando para demo_setup.')
        return redirect('demo_setup')
    
    # Verificar se há um ID de produtor para editar via query string
    produtor_para_editar = None
    editar_id = request.GET.get('editar')
    if editar_id:
        try:
            produtor_id = int(editar_id)
            # Verificar permissão
            if is_usuario_assinante(request.user):
                produtor_para_editar = get_object_or_404(ProdutorRural, id=produtor_id)
            else:
                produtor_para_editar = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
            
            # Verificar se tem permissão
            if not ProdutorService.pode_acessar_produtor(request.user, produtor_para_editar):
                messages.error(request, 'Você não tem permissão para editar este produtor.')
                return redirect('produtor_novo')
        except (ValueError, TypeError):
            pass  # ID inválido, continuar como novo produtor
    
    if request.method == 'POST':
        # Se estiver editando, usar a instância do produtor
        if produtor_para_editar:
            form = ProdutorRuralForm(request.POST, request.FILES, instance=produtor_para_editar)
        else:
            form = ProdutorRuralForm(request.POST)
        
        if form.is_valid():
            try:
                produtor = form.save(commit=False)
                # Se for novo produtor, definir o usuário responsável
                if not produtor_para_editar:
                    produtor.usuario_responsavel = request.user
                produtor.save()
                
                # Se for usuário demo, criar propriedade automaticamente
                if is_demo_user and not produtor_para_editar:
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
                
                if produtor_para_editar:
                    messages.success(request, 'Produtor atualizado com sucesso!')
                else:
                    messages.success(request, 'Produtor cadastrado com sucesso!')
                return redirect('produtor_novo')
            except Exception as e:
                logger.error(f'Erro ao salvar produtor: {e}', exc_info=True)
                messages.error(request, 'Erro ao salvar produtor. Por favor, tente novamente.')
    else:
        # Pré-preencher formulário
        if produtor_para_editar:
            # Carregar dados do produtor para edição
            form = ProdutorRuralForm(instance=produtor_para_editar)
        else:
            # Pré-preencher formulário com dados do usuário de demonstração
            initial_data = ProdutorService.obter_dados_iniciais_demo(request.user) if is_demo_user else {}
            form = ProdutorRuralForm(initial=initial_data)
    
    # Buscar lista de produtores usando o serviço
    produtores_com_tipo = []
    filtro_tipo = request.GET.get('tipo', 'todos')
    
    try:
        produtores_queryset = ProdutorService.obter_produtores_do_usuario(request.user)
        if produtores_queryset:
            # Converter para lista e garantir que usuario_responsavel está carregado
            from .models import ProdutorRural
            produtores_ids = [p.id for p in produtores_queryset if hasattr(p, 'id')]
            
            if produtores_ids:
                # Recarregar com select_related e annotate para garantir que usuario_responsavel e propriedades_count estão disponíveis
                from django.db.models import Count
                try:
                    produtores = list(ProdutorRural.objects.filter(
                        id__in=produtores_ids
                    ).select_related('usuario_responsavel').annotate(
                        propriedades_count=Count('propriedade')
                    ).order_by('nome'))
                except Exception as e:
                    logger.warning(f'Erro ao usar annotate: {e}. Usando query simplificada.')
                    # Se annotate falhar, usar sem ele
                    produtores = list(ProdutorRural.objects.filter(
                        id__in=produtores_ids
                    ).select_related('usuario_responsavel').order_by('nome'))
                    # Adicionar propriedades_count manualmente
                    for p in produtores:
                        try:
                            p.propriedades_count = p.propriedade.count()
                        except:
                            p.propriedades_count = 0
            else:
                produtores = []
        else:
            produtores = []
        
        # Adicionar informação de tipo (demo/assinante) para cada produtor
        # Nota: is_usuario_demo e is_usuario_assinante já estão importados no topo do arquivo
        
        for produtor in produtores:
            tipo_usuario = 'usuario'  # padrão
            try:
                usuario_resp = getattr(produtor, 'usuario_responsavel', None)
                
                if usuario_resp:
                    # Verificar tipo do usuário
                    try:
                        is_demo = is_usuario_demo(usuario_resp)
                        is_assinante = is_usuario_assinante(usuario_resp) if not is_demo else False
                        tipo_usuario = 'demo' if is_demo else ('assinante' if is_assinante else 'usuario')
                    except Exception as e:
                        logger.warning(f'Erro ao verificar tipo do usuário: {e}')
                        tipo_usuario = 'usuario'
                
                # Adicionar atributo ao produtor
                produtor.tipo_usuario = tipo_usuario
                
                # Garantir que propriedades_count existe
                if not hasattr(produtor, 'propriedades_count'):
                    try:
                        produtor.propriedades_count = produtor.propriedade.count()
                    except:
                        produtor.propriedades_count = 0
                
                # Aplicar filtro
                if filtro_tipo == 'todos':
                    produtores_com_tipo.append(produtor)
                elif filtro_tipo == 'demo' and tipo_usuario == 'demo':
                    produtores_com_tipo.append(produtor)
                elif filtro_tipo == 'assinante' and tipo_usuario == 'assinante':
                    produtores_com_tipo.append(produtor)
                    
            except Exception as e:
                logger.warning(f'Erro ao processar produtor: {e}')
                # Em caso de erro, marcar como usuário comum
                try:
                    produtor.tipo_usuario = 'usuario'
                    # Garantir que propriedades_count existe
                    if not hasattr(produtor, 'propriedades_count'):
                        try:
                            produtor.propriedades_count = produtor.propriedade.count()
                        except:
                            produtor.propriedades_count = 0
                    if filtro_tipo == 'todos':
                        produtores_com_tipo.append(produtor)
                except:
                    pass
                    
    except Exception as e:
        logger.error(f'Erro ao buscar produtores: {e}', exc_info=True)
        produtores_com_tipo = []
    
    # Garantir que todas as variáveis do contexto estão definidas
    context = {
        'form': form,
        'is_demo_user': is_demo_user,
        'produtores': produtores_com_tipo if produtores_com_tipo else [],
        'produtor_editando': produtor_para_editar,
        'filtro_tipo': filtro_tipo if filtro_tipo else 'todos',
    }
    
    try:
        return render(request, 'gestao_rural/produtor_novo.html', context)
    except Exception as e:
        logger.error(f'Erro ao renderizar template produtor_novo: {e}', exc_info=True)
        # Em caso de erro no template, retornar uma resposta simples
        messages.error(request, f'Erro ao carregar página: {str(e)}')
        return redirect('dashboard')


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


