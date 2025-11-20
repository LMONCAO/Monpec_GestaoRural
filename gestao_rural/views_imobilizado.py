from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Propriedade
from .models_patrimonio import TipoBem, BemPatrimonial
from .forms_imobilizado import BemPatrimonialForm, TipoBemForm

# Importar CategoriaImobilizadoForm com fallback
try:
    from .forms_imobilizado import CategoriaImobilizadoForm
except ImportError:
    # Fallback se o form não existir
    from django import forms
    from django.core.exceptions import ValidationError
    from .models import CategoriaImobilizado
    
    class CategoriaImobilizadoForm(forms.ModelForm):
        class Meta:
            model = CategoriaImobilizado
            fields = ['nome', 'vida_util_anos', 'taxa_depreciacao', 'descricao']
        
        def clean_taxa_depreciacao(self):
            from django.core.exceptions import ValidationError
            taxa = self.cleaned_data.get('taxa_depreciacao')
            if taxa and (taxa < 0 or taxa > 100):
                raise ValidationError('A taxa de depreciação deve estar entre 0 e 100%.')
            return taxa


@login_required
def imobilizado_dashboard(request, propriedade_id):
    """Dashboard do módulo de imobilizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Busca bens ativos
    bens = BemPatrimonial.objects.filter(
        propriedade=propriedade, 
        ativo=True
    ).order_by('-data_aquisicao')
    
    # Calcula totais
    valor_total_bens = bens.aggregate(
        total=Sum('valor_aquisicao')
    )['total'] or Decimal('0.00')
    
    # Calcular valor_depreciado manualmente (não é campo do banco)
    valor_depreciado = Decimal('0.00')
    for bem in bens:
        if hasattr(bem, 'valor_aquisicao') and bem.valor_aquisicao:
            # Calcular depreciação baseada na idade do bem
            try:
                anos_decorridos = (datetime.now().date() - bem.data_aquisicao).days / 365.25
                depreciacao_percentual = min(anos_decorridos * Decimal('0.10'), Decimal('1.0'))  # 10% ao ano
                valor_depreciado += Decimal(str(bem.valor_aquisicao)) * depreciacao_percentual
            except (ValueError, TypeError, AttributeError, KeyError) as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"Erro ao calcular depreciação do bem {bem.id}: {e}")
                pass
    
    valor_residual = valor_total_bens - valor_depreciado
    
    # Agrupa por categoria
    bens_por_categoria = {}
    for bem in bens:
        categoria_key = bem.tipo_bem.categoria
        categoria_nome = bem.tipo_bem.get_categoria_display()
        if categoria_key not in bens_por_categoria:
            bens_por_categoria[categoria_key] = {
                'nome': categoria_nome,
                'quantidade': 0,
                'valor_total': Decimal('0.00'),
                'valor_depreciado': Decimal('0.00'),
                'bens': []
            }
        
        # Calcular depreciação individual usando propriedade do modelo
        bem_valor_depreciado = bem.depreciacao_acumulada
        
        bens_por_categoria[categoria_key]['quantidade'] += 1
        bens_por_categoria[categoria_key]['valor_total'] += bem.valor_aquisicao
        bens_por_categoria[categoria_key]['valor_depreciado'] += bem_valor_depreciado
        bens_por_categoria[categoria_key]['bens'].append(bem)
    
    # Bens próximos ao fim da vida útil
    data_limite = datetime.now().date() + timedelta(days=365)
    bens_vencendo = 0
    for bem in bens:
        if bem.tipo_bem.vida_util_anos:
            data_fim_vida_util = bem.data_aquisicao + timedelta(days=bem.tipo_bem.vida_util_anos * 365)
            if data_fim_vida_util <= data_limite:
                bens_vencendo += 1
    
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


@login_required
def bens_lista(request, propriedade_id):
    """Lista todos os bens da propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Filtros
    categoria_filter = request.GET.get('categoria', '')
    status_filter = request.GET.get('status', '')
    
    bens = BemPatrimonial.objects.filter(propriedade=propriedade)
    
    if categoria_filter:
        bens = bens.filter(tipo_bem__categoria__id=categoria_filter)
    
    if status_filter == 'ativo':
        bens = bens.filter(ativo=True)
    elif status_filter == 'inativo':
        bens = bens.filter(ativo=False)
    
    bens = bens.order_by('-data_aquisicao')

    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(bens, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Busca categorias únicas para o filtro (via TipoBem)
    from .models_patrimonio import TipoBem
    categorias_choices = TipoBem.CATEGORIAS
    categorias = [{'id': cat[0], 'nome': cat[1]} for cat in categorias_choices]
    
    # Calcular totais
    valor_total = sum(b.valor_aquisicao for b in page_obj)
    valor_atual_total = sum(b.valor_atual for b in page_obj)
    depreciacao_total = sum(b.depreciacao_acumulada for b in page_obj)
    
    context = {
        'propriedade': propriedade,
        'bens': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_filter': categoria_filter,
        'status_filter': status_filter,
        'valor_total': valor_total,
        'valor_atual_total': valor_atual_total,
        'depreciacao_total': depreciacao_total,
    }
    
    return render(request, 'gestao_rural/bens_lista.html', context)


@login_required
def bem_novo(request, propriedade_id):
    """Adiciona novo bem"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = BemPatrimonialForm(request.POST)
        if form.is_valid():
            bem = form.save(commit=False)
            bem.propriedade = propriedade
            bem.save()
            
            messages.success(request, f'Bem "{bem.descricao}" cadastrado com sucesso!')
            return redirect('bens_lista', propriedade_id=propriedade_id)
    else:
        form = BemPatrimonialForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    return render(request, 'gestao_rural/bem_novo.html', context)


@login_required
def bem_editar(request, propriedade_id, bem_id):
    """Edita bem existente"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    bem = get_object_or_404(BemPatrimonial, id=bem_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = BemPatrimonialForm(request.POST, instance=bem)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bem "{bem.descricao}" atualizado com sucesso!')
            return redirect('bens_lista', propriedade_id=propriedade_id)
    else:
        form = BemPatrimonialForm(instance=bem)
    
    context = {
        'propriedade': propriedade,
        'bem': bem,
        'form': form,
    }
    
    return render(request, 'gestao_rural/bem_editar.html', context)


@login_required
def bem_excluir(request, propriedade_id, bem_id):
    """Exclui bem"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    bem = get_object_or_404(BemPatrimonial, id=bem_id, propriedade=propriedade)
    
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


@login_required
def categorias_lista(request):
    """Lista categorias de imobilizado"""
    from .models import CategoriaImobilizado
    categorias = CategoriaImobilizado.objects.all().order_by('nome')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/categorias_imobilizado_lista.html', context)


@login_required
def categoria_nova(request):
    """Adiciona nova categoria"""
    if request.method == 'POST':
        form = CategoriaImobilizadoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Categoria criada com sucesso!')
                return redirect('categorias_imobilizado_lista')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao criar categoria: {str(e)}', exc_info=True)
                messages.error(request, f'Erro ao criar categoria: {str(e)}')
        else:
            from .utils_forms import formatar_mensagem_erro_form
            erro_msg = formatar_mensagem_erro_form(form)
            messages.error(request, f'Erro no formulário: {erro_msg}')
    else:
        form = CategoriaImobilizadoForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'gestao_rural/categoria_imobilizado_nova.html', context)


@login_required
def categoria_editar(request, categoria_id):
    """Editar categoria de imobilizado"""
    from .models import CategoriaImobilizado
    categoria = get_object_or_404(CategoriaImobilizado, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaImobilizadoForm(request.POST, instance=categoria)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
                return redirect('categorias_imobilizado_lista')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Erro ao atualizar categoria: {str(e)}', exc_info=True)
                messages.error(request, f'Erro ao atualizar categoria: {str(e)}')
        else:
            from .utils_forms import formatar_mensagem_erro_form
            erro_msg = formatar_mensagem_erro_form(form)
            messages.error(request, f'Erro no formulário: {erro_msg}')
    else:
        form = CategoriaImobilizadoForm(instance=categoria)
    
    context = {
        'categoria': categoria,
        'form': form,
    }
    
    return render(request, 'gestao_rural/categoria_imobilizado_editar.html', context)


@login_required
def categoria_excluir(request, categoria_id):
    """Excluir categoria de imobilizado"""
    from .models import CategoriaImobilizado
    categoria = get_object_or_404(CategoriaImobilizado, id=categoria_id)
    
    # Verificar se há bens usando esta categoria
    from .models_patrimonio import TipoBem
    tipos_bens_vinculados = TipoBem.objects.filter(categoria=categoria).count()
    
    if request.method == 'POST':
        try:
            if tipos_bens_vinculados > 0:
                messages.error(request, f'Não é possível excluir esta categoria. Existem {tipos_bens_vinculados} tipo(s) de bem vinculado(s).')
                return redirect('categorias_imobilizado_lista')
            
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome_categoria}" excluída com sucesso!')
            return redirect('categorias_imobilizado_lista')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Erro ao excluir categoria: {str(e)}', exc_info=True)
            messages.error(request, f'Erro ao excluir categoria: {str(e)}')
            return redirect('categorias_imobilizado_lista')
    
    context = {
        'categoria': categoria,
        'tipos_bens_vinculados': tipos_bens_vinculados,
    }
    
    return render(request, 'gestao_rural/categoria_imobilizado_excluir.html', context)


@login_required
def calcular_depreciacao_automatica(request, propriedade_id):
    """Calcula depreciação automaticamente para todos os bens"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        bens = BemPatrimonial.objects.filter(propriedade=propriedade, ativo=True)
        bens_atualizados = 0
        
        for bem in bens:
            # Calcula depreciação baseada no tempo decorrido
            tempo_decorrido = datetime.now().date() - bem.data_aquisicao
            anos_decorridos = tempo_decorrido.days / 365.25
            
            if anos_decorridos > 0 and bem.tipo_bem.vida_util_anos:
                # Depreciação linear baseada na vida útil do tipo de bem
                depreciacao_anual = Decimal(str(bem.valor_aquisicao)) / Decimal(str(bem.tipo_bem.vida_util_anos))
                depreciacao_total = min(depreciacao_anual * Decimal(str(anos_decorridos)), Decimal(str(bem.valor_aquisicao)))
                # O modelo já calcula a depreciação via propriedades
                bem.save()
                bens_atualizados += 1
        
        messages.success(request, f'Depreciação calculada para {bens_atualizados} bens!')
        return redirect('imobilizado_dashboard', propriedade_id=propriedade_id)
    
    # GET - mostrar página de confirmação
    bens = BemPatrimonial.objects.filter(propriedade=propriedade, ativo=True)
    
    context = {
        'propriedade': propriedade,
        'total_bens': bens.count(),
    }
    
    return render(request, 'gestao_rural/calcular_depreciacao.html', context)


@login_required
def relatorio_imobilizado(request, propriedade_id):
    """Gera relatório de imobilizado"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Busca todos os bens
    bens = BemPatrimonial.objects.filter(propriedade=propriedade).order_by('tipo_bem__categoria', 'descricao')
    
    # Calcula totais
    valor_total = sum(bem.valor_aquisicao for bem in bens)
    valor_depreciado = sum(bem.depreciacao_acumulada for bem in bens)
    valor_residual = valor_total - valor_depreciado
    
    # Agrupa por categoria
    bens_por_categoria = {}
    for bem in bens:
        categoria_key = bem.tipo_bem.categoria
        categoria_nome = bem.tipo_bem.get_categoria_display()
        if categoria_key not in bens_por_categoria:
            bens_por_categoria[categoria_key] = {
                'nome': categoria_nome,
                'quantidade': 0,
                'valor_total': Decimal('0.00'),
                'valor_depreciado': Decimal('0.00'),
                'bens': []
            }
        bens_por_categoria[categoria_key]['quantidade'] += 1
        bens_por_categoria[categoria_key]['valor_total'] += bem.valor_aquisicao
        bens_por_categoria[categoria_key]['valor_depreciado'] += bem.depreciacao_acumulada
        bens_por_categoria[categoria_key]['bens'].append(bem)
    
    context = {
        'propriedade': propriedade,
        'bens': bens,
        'bens_por_categoria': bens_por_categoria,
        'valor_total': valor_total,
        'valor_depreciado': valor_depreciado,
        'valor_residual': valor_residual,
        'data_relatorio': datetime.now(),
    }
    
    return render(request, 'gestao_rural/relatorio_imobilizado.html', context)

