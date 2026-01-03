"""
Views básicas do módulo Pecuária
Refatorado do views.py principal para melhor organização
Inclui: dashboard, inventário, parâmetros e projeções básicas
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging

from .models import (
    Propriedade, InventarioRebanho, ParametrosProjecaoRebanho,
    MovimentacaoProjetada, CategoriaAnimal, ConfiguracaoVenda
)
from .services.propriedade_service import PropriedadeService

logger = logging.getLogger(__name__)


@login_required
def pecuaria_dashboard(request, propriedade_id):
    """Dashboard do módulo pecuária"""
    # Verificar permissão usando o serviço
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return redirect('dashboard')
    
    # Verificar se tem inventário inicial (otimizado)
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').first()
    
    # Verificar se tem parâmetros configurados (otimizado)
    parametros = ParametrosProjecaoRebanho.objects.filter(
        propriedade=propriedade
    ).only('id', 'taxa_natalidade_anual', 'periodicidade').first()
    
    # Contar movimentações projetadas (otimizado - apenas count, sem carregar dados)
    movimentacoes_count = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade
    ).count()
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'parametros': parametros,
        'movimentacoes_count': movimentacoes_count,
    }
    return render(request, 'gestao_rural/pecuaria_dashboard.html', context)


@login_required
def pecuaria_inventario(request, propriedade_id):
    """Gerenciamento do inventário inicial do rebanho"""
    # Verificar permissão
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return redirect('dashboard')
    
    # Buscar categorias ativas com sexo e raça definidos (otimizado)
    categorias = CategoriaAnimal.objects.filter(
        ativo=True,
        sexo__in=['F', 'M'],
        raca__isnull=False
    ).exclude(raca='').only(
        'id', 'nome', 'sexo', 'raca', 'idade_minima_meses'
    ).order_by('sexo', 'raca', 'idade_minima_meses')
    
    if request.method == 'POST':
        try:
            # Excluir inventário se solicitado
            if 'excluir_todos' in request.POST:
                InventarioRebanho.objects.filter(propriedade=propriedade).delete()
                messages.success(request, 'Inventário excluído com sucesso!')
                return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
            
            # Processar salvamento
            data_inventario_str = request.POST.get('data_inventario') or request.POST.get('data_inventario_hidden')
            
            if not data_inventario_str:
                data_inventario = timezone.now().date()
                messages.warning(request, 'Data não informada. Usando data atual.')
            else:
                try:
                    data_inventario = datetime.strptime(data_inventario_str, '%Y-%m-%d').date()
                except ValueError:
                    data_inventario = timezone.now().date()
                    messages.warning(request, 'Data inválida. Usando data atual.')
            
            # Processar cada categoria
            itens_salvos = 0
            erros = []
            
            with transaction.atomic():
                # Excluir todos os inventários anteriores desta propriedade
                InventarioRebanho.objects.filter(propriedade=propriedade).delete()
                
                for categoria in categorias:
                    quantidade_str = request.POST.get(f'quantidade_{categoria.id}', '').strip()
                    valor_str = request.POST.get(f'valor_por_cabeca_{categoria.id}', '').strip()
                    
                    # Pular se não há dados
                    if not quantidade_str and not valor_str:
                        continue
                    
                    try:
                        quantidade = int(quantidade_str) if quantidade_str else 0
                        valor_por_cabeca = Decimal(valor_str.replace(',', '.')) if valor_str else Decimal('0.00')
                        
                        # Validações
                        if quantidade < 0:
                            erros.append(f'{categoria.nome}: Quantidade não pode ser negativa')
                            continue
                        
                        if valor_por_cabeca < 0:
                            erros.append(f'{categoria.nome}: Valor não pode ser negativo')
                            continue
                        
                        # Criar novo registro
                        InventarioRebanho.objects.create(
                            propriedade=propriedade,
                            categoria=categoria,
                            data_inventario=data_inventario,
                            quantidade=quantidade,
                            valor_por_cabeca=valor_por_cabeca
                        )
                        itens_salvos += 1
                        
                    except (ValueError, InvalidOperation) as e:
                        erros.append(f'{categoria.nome}: {str(e)}')
            
            # Mensagens de feedback
            if erros:
                for erro in erros:
                    messages.error(request, erro)
            
            if itens_salvos > 0:
                messages.success(request, f'{itens_salvos} categoria(s) salva(s) com sucesso!')
            
            return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
            
        except Exception as e:
            logger.error(f'Erro ao processar inventário: {e}', exc_info=True)
            messages.error(request, f'Erro ao processar inventário: {str(e)}')
            return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    # Preparar dados para exibição
    categorias_com_inventario = []
    total_quantidade = 0
    total_valor = Decimal('0.00')
    
    # Verificar se há uma data específica na URL
    data_inventario_filtro = request.GET.get('data_inventario')
    if data_inventario_filtro:
        try:
            data_filtro = datetime.strptime(data_inventario_filtro, '%Y-%m-%d').date()
        except ValueError:
            data_filtro = None
    else:
        data_filtro = None
    
    # Buscar inventário (otimizado com select_related e only)
    inventario_dict = {}
    if data_filtro:
        inventarios_recentes = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria__in=categorias,
            data_inventario=data_filtro
        ).select_related('categoria').only(
            'id', 'categoria_id', 'quantidade', 'valor_por_cabeca', 
            'data_inventario', 'categoria__nome'
        ).order_by('categoria')
    else:
        inventarios_recentes = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria__in=categorias
        ).select_related('categoria').only(
            'id', 'categoria_id', 'quantidade', 'valor_por_cabeca', 
            'data_inventario', 'categoria__nome'
        ).order_by('categoria', '-data_inventario')
    
    # Agrupar por categoria
    for inv in inventarios_recentes:
        if data_filtro:
            inventario_dict[inv.categoria_id] = inv
        else:
            if inv.categoria_id not in inventario_dict:
                inventario_dict[inv.categoria_id] = inv
    
    for categoria in categorias:
        inventario = inventario_dict.get(categoria.id)
        
        quantidade = inventario.quantidade if inventario else 0
        valor_por_cabeca = inventario.valor_por_cabeca if inventario else Decimal('0.00')
        valor_total = inventario.valor_total if inventario else Decimal('0.00')
        
        total_quantidade += quantidade
        total_valor += valor_total
        
        categorias_com_inventario.append({
            'categoria': categoria,
            'quantidade': quantidade,
            'valor_por_cabeca': valor_por_cabeca,
            'valor_total': valor_total,
            'data_inventario': inventario.data_inventario if inventario else None
        })
    
    # Calcular valor médio por cabeça
    valor_medio = total_valor / total_quantidade if total_quantidade > 0 else Decimal('0.00')
    
    # Determinar a data do inventário a ser exibida
    data_inventario_atual = data_filtro
    
    if not data_inventario_atual:
        # Otimizado: apenas buscar a data, sem carregar o objeto completo
        inventario_mais_recente = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).only('data_inventario').order_by('-data_inventario').first()
        
        data_inventario_atual = inventario_mais_recente.data_inventario if inventario_mais_recente else None
    
    context = {
        'propriedade': propriedade,
        'categorias_com_inventario': categorias_com_inventario,
        'total_quantidade': total_quantidade,
        'total_valor': total_valor,
        'valor_medio': valor_medio,
        'tem_inventario': any(item['quantidade'] > 0 for item in categorias_com_inventario),
        'data_inventario_atual': data_inventario_atual,
    }
    
    return render(request, 'gestao_rural/pecuaria_inventario.html', context)


@login_required
def pecuaria_parametros(request, propriedade_id):
    """Configuração dos parâmetros de projeção do rebanho"""
    # Verificar permissão
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return redirect('dashboard')
    
    # Buscar ou criar parâmetros
    parametros, created = ParametrosProjecaoRebanho.objects.get_or_create(
        propriedade=propriedade,
        defaults={
            'taxa_natalidade_anual': Decimal('85.00'),
            'taxa_mortalidade_bezerros_anual': Decimal('5.00'),
            'taxa_mortalidade_adultos_anual': Decimal('2.00'),
            'percentual_venda_machos_anual': Decimal('90.00'),
            'percentual_venda_femeas_anual': Decimal('10.00'),
            'periodicidade': 'MENSAL',
        }
    )
    
    if request.method == 'POST':
        try:
            # Atualizar parâmetros
            parametros.taxa_natalidade_anual = Decimal(request.POST.get('taxa_natalidade_anual', '85.00'))
            parametros.taxa_mortalidade_bezerros_anual = Decimal(request.POST.get('taxa_mortalidade_bezerros_anual', '5.00'))
            parametros.taxa_mortalidade_adultos_anual = Decimal(request.POST.get('taxa_mortalidade_adultos_anual', '2.00'))
            parametros.percentual_venda_machos_anual = Decimal(request.POST.get('percentual_venda_machos_anual', '90.00'))
            parametros.percentual_venda_femeas_anual = Decimal(request.POST.get('percentual_venda_femeas_anual', '10.00'))
            parametros.periodicidade = request.POST.get('periodicidade', 'MENSAL')
            parametros.save()
            
            messages.success(request, 'Parâmetros salvos com sucesso!')
            return redirect('pecuaria_parametros', propriedade_id=propriedade.id)
        except Exception as e:
            logger.error(f'Erro ao salvar parâmetros: {e}', exc_info=True)
            messages.error(request, f'Erro ao salvar parâmetros: {str(e)}')
    
    context = {
        'propriedade': propriedade,
        'parametros': parametros,
    }
    return render(request, 'gestao_rural/pecuaria_parametros.html', context)


@login_required
def pecuaria_parametros_avancados(request, propriedade_id):
    """Configurações avançadas de vendas e reposição"""
    # Verificar permissão
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        messages.error(request, 'Você não tem permissão para acessar esta propriedade.')
        return redirect('dashboard')
    
    # Obter categorias e outras propriedades
    categorias = CategoriaAnimal.objects.all().order_by('sexo', 'idade_minima_meses')
    outras_fazendas = PropriedadeService.obter_propriedades_do_usuario(request.user).exclude(id=propriedade_id)
    
    if request.method == 'POST':
        if 'salvar_configuracoes' in request.POST:
            # Processar configurações de venda
            categoria_venda_id = request.POST.get('categoria_venda')
            frequencia_venda = request.POST.get('frequencia_venda')
            quantidade_venda = request.POST.get('quantidade_venda')
            tipo_reposicao = request.POST.get('tipo_reposicao')
            
            if categoria_venda_id and frequencia_venda and quantidade_venda and tipo_reposicao:
                categoria_venda = get_object_or_404(CategoriaAnimal, id=categoria_venda_id)
                
                # Criar configuração de venda
                configuracao = ConfiguracaoVenda.objects.create(
                    propriedade=propriedade,
                    categoria_venda=categoria_venda,
                    frequencia_venda=frequencia_venda,
                    quantidade_venda=int(quantidade_venda),
                    tipo_reposicao=tipo_reposicao
                )
                
                # Configurações de transferência
                if tipo_reposicao == 'TRANSFERENCIA':
                    fazenda_origem_id = request.POST.get('fazenda_origem')
                    quantidade_transferencia = request.POST.get('quantidade_transferencia')
                    
                    if fazenda_origem_id and quantidade_transferencia:
                        fazenda_origem = get_object_or_404(Propriedade, id=fazenda_origem_id)
                        configuracao.fazenda_origem = fazenda_origem
                        configuracao.quantidade_transferencia = int(quantidade_transferencia)
                        configuracao.save()
                
                # Configurações de compra
                elif tipo_reposicao == 'COMPRA':
                    categoria_compra_id = request.POST.get('categoria_compra')
                    quantidade_compra = request.POST.get('quantidade_compra')
                    valor_animal_venda = request.POST.get('valor_animal_venda')
                    percentual_desconto = request.POST.get('percentual_desconto')
                    
                    if categoria_compra_id and quantidade_compra:
                        categoria_compra = get_object_or_404(CategoriaAnimal, id=categoria_compra_id)
                        configuracao.categoria_compra = categoria_compra
                        configuracao.quantidade_compra = int(quantidade_compra)
                        
                        if valor_animal_venda:
                            configuracao.valor_animal_venda = Decimal(valor_animal_venda)
                        
                        if percentual_desconto:
                            configuracao.percentual_desconto = Decimal(percentual_desconto)
                            if configuracao.valor_animal_venda and configuracao.percentual_desconto:
                                configuracao.valor_animal_compra = configuracao.calcular_valor_compra()
                        
                        configuracao.save()
                
                messages.success(request, 'Configuração de venda salva com sucesso!')
                return redirect('pecuaria_parametros_avancados', propriedade_id=propriedade_id)
    
    # Obter configurações existentes
    configuracoes = ConfiguracaoVenda.objects.filter(propriedade=propriedade, ativo=True).order_by('-data_criacao')
    
    context = {
        'propriedade': propriedade,
        'categorias': categorias,
        'outras_fazendas': outras_fazendas,
        'configuracoes': configuracoes,
    }
    
    return render(request, 'gestao_rural/pecuaria_parametros_avancados.html', context)


@login_required
def pecuaria_inventario_dados(request, propriedade_id, categoria_id):
    """API para obter dados do inventário de uma categoria"""
    # Verificar permissão
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if not PropriedadeService.pode_acessar_propriedade(request.user, propriedade):
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    try:
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria
        ).order_by('-data_inventario').first()
        
        if inventario:
            return JsonResponse({
                'quantidade': inventario.quantidade,
                'valor_por_cabeca': str(inventario.valor_por_cabeca),
                'valor_total': str(inventario.valor_total),
                'data_inventario': inventario.data_inventario.strftime('%Y-%m-%d'),
            })
        else:
            return JsonResponse({
                'quantidade': 0,
                'valor_por_cabeca': '0.00',
                'valor_total': '0.00',
                'data_inventario': None,
            })
    except Exception as e:
        logger.error(f'Erro ao buscar dados do inventário: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

