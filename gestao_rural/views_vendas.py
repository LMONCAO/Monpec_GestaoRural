from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import Propriedade, ParametrosVendaPorCategoria, CategoriaAnimal
from .forms_vendas import ParametrosVendaPorCategoriaForm, BulkVendaPorCategoriaForm


def vendas_por_categoria_lista(request, propriedade_id):
    """Lista os parâmetros de venda por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca parâmetros existentes
    parametros = ParametrosVendaPorCategoria.objects.filter(
        propriedade=propriedade
    ).order_by('categoria__nome')
    
    # Busca categorias sem parâmetro configurado
    categorias_sem_parametro = CategoriaAnimal.objects.exclude(
        parametrosvendaporcategoria__propriedade=propriedade
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'parametros': parametros,
        'categorias_sem_parametro': categorias_sem_parametro,
    }
    
    return render(request, 'gestao_rural/vendas_por_categoria_lista.html', context)


def vendas_por_categoria_novo(request, propriedade_id):
    """Adiciona novo parâmetro de venda por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = ParametrosVendaPorCategoriaForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            parametro = form.save(commit=False)
            parametro.propriedade = propriedade
            parametro.save()
            
            messages.success(request, f'Parâmetro de venda para {parametro.categoria.nome} configurado com sucesso!')
            return redirect('vendas_por_categoria_lista', propriedade_id=propriedade_id)
    else:
        form = ParametrosVendaPorCategoriaForm(propriedade=propriedade)
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/vendas_por_categoria_novo.html', context)


def vendas_por_categoria_editar(request, propriedade_id, parametro_id):
    """Edita parâmetro de venda por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    parametro = get_object_or_404(ParametrosVendaPorCategoria, id=parametro_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = ParametrosVendaPorCategoriaForm(request.POST, instance=parametro, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Parâmetro de venda para {parametro.categoria.nome} atualizado com sucesso!')
            return redirect('vendas_por_categoria_lista', propriedade_id=propriedade_id)
    else:
        form = ParametrosVendaPorCategoriaForm(instance=parametro, propriedade=propriedade)
    
    context = {
        'propriedade': propriedade,
        'parametro': parametro,
        'form': form,
    }
    
    return render(request, 'gestao_rural/vendas_por_categoria_editar.html', context)


def vendas_por_categoria_bulk(request, propriedade_id):
    """Configuração em massa de vendas por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = BulkVendaPorCategoriaForm(request.POST, propriedade=propriedade)
        if form.is_valid():
            with transaction.atomic():
                categorias_processadas = 0
                
                for field_name, percentual in form.cleaned_data.items():
                    if field_name.startswith('percentual_') and percentual and percentual > 0:
                        categoria_id = field_name.replace('percentual_', '')
                        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
                        
                        # Cria ou atualiza o parâmetro
                        parametro, created = ParametrosVendaPorCategoria.objects.get_or_create(
                            propriedade=propriedade,
                            categoria=categoria,
                            defaults={'percentual_venda_anual': percentual}
                        )
                        
                        if not created:
                            parametro.percentual_venda_anual = percentual
                            parametro.ativo = True
                            parametro.save()
                        
                        categorias_processadas += 1
                
                if categorias_processadas > 0:
                    messages.success(request, f'{categorias_processadas} parâmetros de venda configurados com sucesso!')
                else:
                    messages.warning(request, 'Nenhum parâmetro foi configurado. Verifique os valores informados.')
                
                return redirect('vendas_por_categoria_lista', propriedade_id=propriedade_id)
    else:
        form = BulkVendaPorCategoriaForm(propriedade=propriedade)
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/vendas_por_categoria_bulk.html', context)


@require_http_methods(["POST"])
def vendas_por_categoria_excluir(request, propriedade_id, parametro_id):
    """Exclui parâmetro de venda por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    parametro = get_object_or_404(ParametrosVendaPorCategoria, id=parametro_id, propriedade=propriedade)
    
    categoria_nome = parametro.categoria.nome
    parametro.delete()
    
    messages.success(request, f'Parâmetro de venda para {categoria_nome} excluído com sucesso!')
    return redirect('vendas_por_categoria_lista', propriedade_id=propriedade_id)


def vendas_por_categoria_toggle_status(request, propriedade_id, parametro_id):
    """Ativa/desativa parâmetro de venda por categoria"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    parametro = get_object_or_404(ParametrosVendaPorCategoria, id=parametro_id, propriedade=propriedade)
    
    parametro.ativo = not parametro.ativo
    parametro.save()
    
    status = "ativado" if parametro.ativo else "desativado"
    messages.success(request, f'Parâmetro de venda para {parametro.categoria.nome} {status} com sucesso!')
    
    return redirect('vendas_por_categoria_lista', propriedade_id=propriedade_id)

