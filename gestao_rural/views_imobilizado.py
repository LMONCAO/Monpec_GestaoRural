from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Avg
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Propriedade, CategoriaImobilizado, BemImobilizado
from .forms_imobilizado import BemImobilizadoForm, CategoriaImobilizadoForm


def imobilizado_dashboard(request, propriedade_id):
    """Dashboard do módulo de imobilizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca bens ativos
    bens = BemImobilizado.objects.filter(
        propriedade=propriedade, 
        ativo=True
    ).order_by('-data_aquisicao')
    
    # Calcula totais
    valor_total_bens = bens.aggregate(
        total=Sum('valor_aquisicao')
    )['total'] or Decimal('0.00')
    
    valor_depreciado = bens.aggregate(
        total=Sum('valor_depreciado')
    )['total'] or Decimal('0.00')
    
    valor_residual = valor_total_bens - valor_depreciado
    
    # Agrupa por categoria
    bens_por_categoria = {}
    for bem in bens:
        categoria = bem.categoria.nome
        if categoria not in bens_por_categoria:
            bens_por_categoria[categoria] = {
                'quantidade': 0,
                'valor_total': Decimal('0.00'),
                'valor_depreciado': Decimal('0.00'),
                'bens': []
            }
        bens_por_categoria[categoria]['quantidade'] += 1
        bens_por_categoria[categoria]['valor_total'] += bem.valor_aquisicao
        bens_por_categoria[categoria]['valor_depreciado'] += bem.valor_depreciado
        bens_por_categoria[categoria]['bens'].append(bem)
    
    # Bens próximos ao fim da vida útil
    data_limite = datetime.now().date() + timedelta(days=365)
    bens_vencendo = bens.filter(
        data_fim_vida_util__lte=data_limite
    ).count()
    
    context = {
        'propriedade': propriedade,
        'bens': bens,
        'bens_por_categoria': bens_por_categoria,
        'valor_total_bens': valor_total_bens,
        'valor_depreciado': valor_depreciado,
        'valor_residual': valor_residual,
        'bens_vencendo': bens_vencendo,
    }
    
    return render(request, 'gestao_rural/imobilizado_dashboard.html', context)


def bens_lista(request, propriedade_id):
    """Lista todos os bens da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Filtros
    categoria_filter = request.GET.get('categoria', '')
    status_filter = request.GET.get('status', '')
    
    bens = BemImobilizado.objects.filter(propriedade=propriedade)
    
    if categoria_filter:
        bens = bens.filter(categoria__id=categoria_filter)
    
    if status_filter == 'ativo':
        bens = bens.filter(ativo=True)
    elif status_filter == 'inativo':
        bens = bens.filter(ativo=False)
    
    bens = bens.order_by('-data_aquisicao')
    
    # Busca categorias para o filtro
    categorias = CategoriaImobilizado.objects.all().order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'bens': bens,
        'categorias': categorias,
        'categoria_filter': categoria_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'gestao_rural/bens_lista.html', context)


def bem_novo(request, propriedade_id):
    """Adiciona novo bem"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        form = BemImobilizadoForm(request.POST)
        if form.is_valid():
            bem = form.save(commit=False)
            bem.propriedade = propriedade
            bem.save()
            
            messages.success(request, f'Bem "{bem.nome}" cadastrado com sucesso!')
            return redirect('bens_lista', propriedade_id=propriedade_id)
    else:
        form = BemImobilizadoForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/bem_novo.html', context)


def bem_editar(request, propriedade_id, bem_id):
    """Edita bem existente"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    bem = get_object_or_404(BemImobilizado, id=bem_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = BemImobilizadoForm(request.POST, instance=bem)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bem "{bem.nome}" atualizado com sucesso!')
            return redirect('bens_lista', propriedade_id=propriedade_id)
    else:
        form = BemImobilizadoForm(instance=bem)
    
    context = {
        'propriedade': propriedade,
        'bem': bem,
        'form': form,
    }
    
    return render(request, 'gestao_rural/bem_editar.html', context)


def bem_excluir(request, propriedade_id, bem_id):
    """Exclui bem"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    bem = get_object_or_404(BemImobilizado, id=bem_id, propriedade=propriedade)
    
    if request.method == 'POST':
        nome = bem.nome
        bem.delete()
        messages.success(request, f'Bem "{nome}" excluído com sucesso!')
        return redirect('bens_lista', propriedade_id=propriedade_id)
    
    context = {
        'propriedade': propriedade,
        'bem': bem,
    }
    
    return render(request, 'gestao_rural/bem_excluir.html', context)


def categorias_lista(request):
    """Lista categorias de imobilizado"""
    categorias = CategoriaImobilizado.objects.all().order_by('nome')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/categorias_imobilizado_lista.html', context)


def categoria_nova(request):
    """Adiciona nova categoria"""
    if request.method == 'POST':
        form = CategoriaImobilizadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('categorias_imobilizado_lista')
    else:
        form = CategoriaImobilizadoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'gestao_rural/categoria_imobilizado_nova.html', context)


def calcular_depreciacao_automatica(request, propriedade_id):
    """Calcula depreciação automaticamente para todos os bens"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    bens = BemImobilizado.objects.filter(propriedade=propriedade, ativo=True)
    bens_atualizados = 0
    
    for bem in bens:
        # Calcula depreciação baseada no tempo decorrido
        tempo_decorrido = datetime.now().date() - bem.data_aquisicao
        anos_decorridos = tempo_decorrido.days / 365.25
        
        if anos_decorridos > 0:
            # Depreciação linear
            depreciacao_anual = bem.valor_aquisicao / bem.vida_util_anos
            bem.valor_depreciado = min(depreciacao_anual * anos_decorridos, bem.valor_aquisicao)
            bem.save()
            bens_atualizados += 1
    
    messages.success(request, f'Depreciação calculada para {bens_atualizados} bens!')
    return redirect('imobilizado_dashboard', propriedade_id=propriedade_id)


def relatorio_imobilizado(request, propriedade_id):
    """Gera relatório de imobilizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Busca todos os bens
    bens = BemImobilizado.objects.filter(propriedade=propriedade).order_by('categoria__nome', 'nome')
    
    # Calcula totais
    valor_total = sum(bem.valor_aquisicao for bem in bens)
    valor_depreciado = sum(bem.valor_depreciado for bem in bens)
    valor_residual = valor_total - valor_depreciado
    
    # Agrupa por categoria
    bens_por_categoria = {}
    for bem in bens:
        categoria = bem.categoria.nome
        if categoria not in bens_por_categoria:
            bens_por_categoria[categoria] = {
                'quantidade': 0,
                'valor_total': Decimal('0.00'),
                'valor_depreciado': Decimal('0.00'),
                'bens': []
            }
        bens_por_categoria[categoria]['quantidade'] += 1
        bens_por_categoria[categoria]['valor_total'] += bem.valor_aquisicao
        bens_por_categoria[categoria]['valor_depreciado'] += bem.valor_depreciado
        bens_por_categoria[categoria]['bens'].append(bem)
    
    context = {
        'propriedade': propriedade,
        'bens': bens,
        'bens_por_categoria': bens_por_categoria,
        'valor_total': valor_total,
        'valor_depreciado': valor_depreciado,
        'valor_residual': valor_residual,
        'data_relatorio': datetime.now().date(),
    }
    
    return render(request, 'gestao_rural/relatorio_imobilizado.html', context)

