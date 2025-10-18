from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, F
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    ParametrosProjecaoRebanho, MovimentacaoProjetada, Cultura, CicloProducaoAgricola,
    ConfiguracaoVenda
)
from .forms import (
    ProdutorRuralForm, PropriedadeForm, InventarioRebanhoForm,
    ParametrosProjecaoForm, MovimentacaoProjetadaForm, CicloProducaoForm, CategoriaAnimalForm
)


def login_view(request):
    """View para login do usuário"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'gestao_rural/login.html')


@login_required
def logout_view(request):
    """View para logout do usuário"""
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal - lista de produtores"""
    produtores = ProdutorRural.objects.filter(usuario_responsavel=request.user)
    context = {
        'produtores': produtores,
    }
    return render(request, 'gestao_rural/dashboard.html', context)


@login_required
def produtor_novo(request):
    """Cadastro de novo produtor rural"""
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST)
        if form.is_valid():
            produtor = form.save(commit=False)
            produtor.usuario_responsavel = request.user
            produtor.save()
            messages.success(request, 'Produtor cadastrado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm()
    
    return render(request, 'gestao_rural/produtor_novo.html', {'form': form})


@login_required
def produtor_editar(request, produtor_id):
    """Edição de produtor rural"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST, instance=produtor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produtor atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm(instance=produtor)
    
    return render(request, 'gestao_rural/produtor_editar.html', {'form': form, 'produtor': produtor})


@login_required
def produtor_excluir(request, produtor_id):
    """Exclusão de produtor rural"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        produtor.delete()
        messages.success(request, 'Produtor excluído com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'gestao_rural/produtor_excluir.html', {'produtor': produtor})


@login_required
def propriedades_lista(request, produtor_id):
    """Lista de propriedades de um produtor"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
    }
    return render(request, 'gestao_rural/propriedades_lista.html', context)


@login_required
def propriedade_nova(request, produtor_id):
    """Cadastro de nova propriedade"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST)
        if form.is_valid():
            propriedade = form.save(commit=False)
            propriedade.produtor = produtor
            propriedade.save()
            messages.success(request, 'Propriedade cadastrada com sucesso!')
            return redirect('propriedades_lista', produtor_id=produtor.id)
    else:
        form = PropriedadeForm()
    
    context = {
        'form': form,
        'produtor': produtor,
    }
    return render(request, 'gestao_rural/propriedade_nova.html', context)


@login_required
def propriedade_editar(request, propriedade_id):
    """Edição de propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, instance=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriedade atualizada com sucesso!')
            return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
    else:
        form = PropriedadeForm(instance=propriedade)
    
    context = {
        'form': form,
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/propriedade_editar.html', context)


@login_required
def propriedade_excluir(request, propriedade_id):
    """Exclusão de propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        produtor_id = propriedade.produtor.id
        propriedade.delete()
        messages.success(request, 'Propriedade excluída com sucesso!')
        return redirect('propriedades_lista', produtor_id=produtor_id)
    
    return render(request, 'gestao_rural/propriedade_excluir.html', {'propriedade': propriedade})


@login_required
def pecuaria_dashboard(request, propriedade_id):
    """Dashboard do módulo pecuária"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Verificar se tem inventário inicial
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade).first()
    
    # Verificar se tem parâmetros configurados
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    # Contar movimentações projetadas
    movimentacoes_count = MovimentacaoProjetada.objects.filter(propriedade=propriedade).count()
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'parametros': parametros,
        'movimentacoes_count': movimentacoes_count,
    }
    return render(request, 'gestao_rural/pecuaria_dashboard.html', context)


@login_required
def pecuaria_inventario(request, propriedade_id):
    """Gerenciamento do inventário inicial"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    # Ordenar categorias: primeiro fêmeas por idade, depois machos por idade
    categorias = CategoriaAnimal.objects.filter(ativo=True).order_by(
        'sexo',  # F primeiro, depois M
        'idade_minima_meses'  # Por idade dentro de cada sexo
    )
    
    # Verificar se já existe inventário
    inventario_existente = InventarioRebanho.objects.filter(propriedade=propriedade).exists()
    
    # Debug: verificar dados
    print(f"Inventário existe: {inventario_existente}")
    inventarios = InventarioRebanho.objects.filter(propriedade=propriedade)
    for inv in inventarios:
        print(f"Inventário encontrado: Categoria {inv.categoria.nome}, Qtd: {inv.quantidade}, Valor: {inv.valor_por_cabeca}")
    
    if request.method == 'POST':
        # Verificar se é uma ação de exclusão
        if 'excluir_inventario' in request.POST:
            InventarioRebanho.objects.filter(propriedade=propriedade).delete()
            messages.success(request, 'Inventário excluído com sucesso!')
            return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
        
        # Processar inventário
        data_inventario = request.POST.get('data_inventario')
        
        # Validar data do inventário
        if not data_inventario:
            data_inventario = timezone.now().date()
            messages.warning(request, 'Data do inventário não informada. Usando data atual.')
        
        print(f"Data do inventário: {data_inventario}")
        
        # Usar transação para evitar problemas de concorrência
        with transaction.atomic():
            for categoria in categorias:
                quantidade = request.POST.get(f'quantidade_{categoria.id}')
                valor_por_cabeca = request.POST.get(f'valor_por_cabeca_{categoria.id}')
                
                if quantidade is not None:
                    quantidade_int = int(quantidade) if quantidade else 0
                    valor_por_cabeca_decimal = Decimal(valor_por_cabeca) if valor_por_cabeca else Decimal('0.00')
                    
                    print(f"Salvando categoria {categoria.nome}: qtd={quantidade_int}, valor={valor_por_cabeca_decimal}, data={data_inventario}")
                    
                    InventarioRebanho.objects.update_or_create(
                        propriedade=propriedade,
                        categoria=categoria,
                        data_inventario=data_inventario,
                        defaults={
                            'quantidade': quantidade_int,
                            'valor_por_cabeca': valor_por_cabeca_decimal
                        }
                    )
        
        if inventario_existente:
            messages.success(request, 'Saldo alterado com sucesso!')
        else:
            messages.success(request, 'Saldo inicial cadastrado com sucesso!')
        return redirect('pecuaria_dashboard', propriedade_id=propriedade.id)
    
    # Buscar inventário existente e anexar diretamente às categorias
    categorias_com_inventario = []
    for categoria in categorias:
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade, 
            categoria=categoria
        ).first()
        
        # Debug: verificar cada categoria
        print(f"Categoria: {categoria.nome}")
        print(f"   Inventário encontrado: {inventario}")
        
        if inventario:
            print(f"   Quantidade: {inventario.quantidade}")
            print(f"   Valor por cabeça: {inventario.valor_por_cabeca}")
            print(f"   Valor total: {inventario.valor_total}")
        
        # Criar um objeto temporário com categoria e inventário
        quantidade = inventario.quantidade if inventario else 0
        valor_por_cabeca = float(inventario.valor_por_cabeca) if inventario and inventario.valor_por_cabeca else 0.0
        # Calcular valor total usando a propriedade do modelo
        valor_total = float(inventario.valor_total) if inventario else 0.0
        
        print(f"   📊 Valores extraídos:")
        print(f"      Quantidade: {quantidade}")
        print(f"      Valor por cabeça: {valor_por_cabeca}")
        print(f"      Valor total: {valor_total}")
        
        categoria_data = {
            'categoria': categoria,
            'quantidade': quantidade,
            'valor_por_cabeca': valor_por_cabeca,
            'valor_total': valor_total
        }
        categorias_com_inventario.append(categoria_data)
        
        # Debug: verificar dados processados
        print(f"✅ Dados processados: {categoria_data}")
        print("=" * 50)
    
    context = {
        'propriedade': propriedade,
        'categorias_com_inventario': categorias_com_inventario,
        'inventario_ja_existe': inventario_existente,
    }
    return render(request, 'gestao_rural/pecuaria_inventario_tabela_nova.html', context)


@login_required
def pecuaria_parametros_avancados(request, propriedade_id):
    """Configurações avançadas de vendas e reposição"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Obter categorias e outras propriedades
    categorias = CategoriaAnimal.objects.all().order_by('sexo', 'idade_minima_meses')
    outras_fazendas = Propriedade.objects.filter(produtor__usuario_responsavel=request.user).exclude(id=propriedade_id)
    
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
                            # Calcular valor da compra
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
def pecuaria_parametros(request, propriedade_id):
    """Configuração dos parâmetros de projeção com IA Avançada"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Tentar buscar parâmetros existentes
    try:
        parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    except ParametrosProjecaoRebanho.DoesNotExist:
        # Criar novos parâmetros com valores padrão
        parametros = ParametrosProjecaoRebanho.objects.create(propriedade=propriedade)
    
    if request.method == 'POST':
        # Processar parâmetros normais
        form = ParametrosProjecaoForm(request.POST, instance=parametros)
        if form.is_valid():
            parametros = form.save()
            # Aplicar parâmetros específicos do tipo de ciclo
            parametros = aplicar_parametros_ciclo(propriedade, parametros)
            messages.success(request, 'Parâmetros salvos com sucesso!')
            return redirect('pecuaria_dashboard', propriedade_id=propriedade.id)
    else:
        form = ParametrosProjecaoForm(instance=parametros)
        # Aplicar parâmetros padrão do tipo de ciclo se não existirem
        if parametros:
            parametros = aplicar_parametros_ciclo(propriedade, parametros)
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'parametros': parametros,
    }
    return render(request, 'gestao_rural/pecuaria_parametros_ia_avancada.html', context)


@login_required
def pecuaria_projecao(request, propriedade_id):
    """Visualização e geração da projeção"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Verificar se tem inventário e parâmetros
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    if not inventario.exists():
        messages.error(request, 'É necessário cadastrar o inventário inicial primeiro.')
        return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    if not parametros:
        messages.error(request, 'É necessário configurar os parâmetros de projeção primeiro.')
        return redirect('pecuaria_parametros', propriedade_id=propriedade.id)
    
    if request.method == 'POST':
        anos_projecao = int(request.POST.get('anos_projecao', 5))
        
        print(f"🚀 Iniciando geração de projeção INTELIGENTE para {propriedade.nome_propriedade}")
        
        # Gerar projeção com IA
        gerar_projecao(propriedade, anos_projecao)
        
        messages.success(request, f'Projeção INTELIGENTE gerada para {anos_projecao} anos!')
        return redirect('pecuaria_projecao', propriedade_id=propriedade.id)
    
    # Buscar movimentações projetadas
    movimentacoes = MovimentacaoProjetada.objects.filter(propriedade=propriedade).order_by('data_movimentacao')
    
    # Gerar resumo em formato de tabela por ano
    resumo_projecao_por_ano = gerar_resumo_projecao_por_ano(movimentacoes, inventario)
    evolucao_categorias, periodos_ordenados = gerar_evolucao_categorias_tabela(movimentacoes, inventario)
    evolucao_detalhada = gerar_evolucao_detalhada_rebanho(movimentacoes, inventario)
    
    # Calcular totais do inventário
    total_femeas = 0
    total_machos = 0
    total_geral = 0
    
    for item in inventario:
        total_geral += item.quantidade
        if any(termo in item.categoria.nome.lower() for termo in ['fêmea', 'femea', 'bezerra', 'novilha', 'primípara', 'multípara', 'vaca']):
            total_femeas += item.quantidade
        elif any(termo in item.categoria.nome.lower() for termo in ['macho', 'bezerro', 'garrote', 'boi', 'touro']):
            total_machos += item.quantidade
    
    # IDENTIFICAÇÃO AUTOMÁTICA DA FAZENDA
    identificacao_fazenda = None
    if inventario.exists() and parametros:
        try:
            from .ia_identificacao_fazendas import sistema_identificacao
            identificacao_fazenda = sistema_identificacao.identificar_perfil_fazenda(
                list(inventario), parametros
            )
            print(f"🏭 Fazenda identificada como: {identificacao_fazenda['nome_perfil']}")
        except Exception as e:
            print(f"⚠️ Erro na identificação da fazenda: {e}")
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'parametros': parametros,
        'movimentacoes': movimentacoes,
        'resumo_projecao_por_ano': resumo_projecao_por_ano,
        'evolucao_categorias': evolucao_categorias,
        'evolucao_detalhada': evolucao_detalhada,
        'periodos': periodos_ordenados,
        'total_femeas': total_femeas,
        'identificacao_fazenda': identificacao_fazenda,
        'total_machos': total_machos,
        'total_geral': total_geral,
    }
    return render(request, 'gestao_rural/pecuaria_projecao.html', context)


def pecuaria_inventario_dados(request, propriedade_id):
    """View para retornar dados do inventário em JSON para a IA"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Obter inventário mais recente
    inventario_data = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).order_by('-data_inventario').first()
    
    if not inventario_data:
        # Se não há inventário, retornar dados vazios
        return JsonResponse({
            'success': False,
            'message': 'Nenhum inventário encontrado',
            'inventario': {}
        })
    
    # Obter todas as categorias e seus valores
    inventario = {}
    categorias = CategoriaAnimal.objects.all()
    
    for categoria in categorias:
        item = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria,
            data_inventario=inventario_data.data_inventario
        ).first()
        
        if item:
            inventario[categoria.nome] = {
                'quantidade': item.quantidade,
                'valor_por_cabeca': float(item.valor_por_cabeca),
                'valor_total': float(item.valor_total)
            }
        else:
            inventario[categoria.nome] = {
                'quantidade': 0,
                'valor_por_cabeca': 0.0,
                'valor_total': 0.0
            }
    
    return JsonResponse({
        'success': True,
        'inventario': inventario,
        'data_inventario': inventario_data.data_inventario.strftime('%d/%m/%Y')
    })


def gerar_projecao(propriedade, anos):
    """Função para gerar a projeção do rebanho com IA Inteligente"""
    from .ia_movimentacoes_automaticas import sistema_movimentacoes
    
    # Limpar projeções anteriores
    MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
    
    # Buscar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(propriedade=propriedade)
    parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    
    print(f"🚀 Iniciando geração de projeção INTELIGENTE para {propriedade.nome_propriedade}")
    print(f"📊 Parâmetros: Natalidade={parametros.taxa_natalidade_anual}%, Mortalidade Bezerros={parametros.taxa_mortalidade_bezerros_anual}%, Mortalidade Adultos={parametros.taxa_mortalidade_adultos_anual}%")
    print(f"📅 Anos de projeção: {anos}")
    
    # Usar sistema inteligente para gerar todas as movimentações
    movimentacoes = sistema_movimentacoes.gerar_movimentacoes_completas(
        propriedade, parametros, inventario_inicial, anos
    )
    
    print(f"\n✅ Total de movimentações INTELIGENTES geradas: {len(movimentacoes)}")
    return movimentacoes


@login_required
def agricultura_dashboard(request, propriedade_id):
    """Dashboard do módulo agricultura"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    ciclos = CicloProducaoAgricola.objects.filter(propriedade=propriedade).order_by('-data_inicio_plantio')
    
    context = {
        'propriedade': propriedade,
        'ciclos': ciclos,
    }
    return render(request, 'gestao_rural/agricultura_dashboard.html', context)


@login_required
def agricultura_ciclo_novo(request, propriedade_id):
    """Cadastro de novo ciclo de produção agrícola"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = CicloProducaoForm(request.POST)
        if form.is_valid():
            ciclo = form.save(commit=False)
            ciclo.propriedade = propriedade
            ciclo.save()
            messages.success(request, 'Ciclo de produção cadastrado com sucesso!')
            return redirect('agricultura_dashboard', propriedade_id=propriedade.id)
    else:
        form = CicloProducaoForm()
    
    context = {
        'form': form,
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/agricultura_ciclo_novo.html', context)


@login_required
def relatorio_final(request, propriedade_id):
    """Relatório final para análise bancária"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Dados da pecuária
    inventario_pecuaria = InventarioRebanho.objects.filter(propriedade=propriedade)
    parametros_pecuaria = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    movimentacoes_pecuaria = MovimentacaoProjetada.objects.filter(propriedade=propriedade)
    
    # Dados da agricultura
    ciclos_agricultura = CicloProducaoAgricola.objects.filter(propriedade=propriedade)
    
    # Cálculos de resumo
    total_rebanho_atual = inventario_pecuaria.aggregate(total=Sum('quantidade'))['total'] or 0
    
    # Projeção de receita agrícola
    receita_agricola_total = sum(ciclo.receita_esperada_total for ciclo in ciclos_agricultura)
    custo_agricola_total = sum(ciclo.custo_total_producao for ciclo in ciclos_agricultura)
    lucro_agricola_total = receita_agricola_total - custo_agricola_total
    
    context = {
        'propriedade': propriedade,
        'inventario_pecuaria': inventario_pecuaria,
        'parametros_pecuaria': parametros_pecuaria,
        'movimentacoes_pecuaria': movimentacoes_pecuaria,
        'ciclos_agricultura': ciclos_agricultura,
        'total_rebanho_atual': total_rebanho_atual,
        'receita_agricola_total': receita_agricola_total,
        'custo_agricola_total': custo_agricola_total,
        'lucro_agricola_total': lucro_agricola_total,
    }
    return render(request, 'gestao_rural/relatorio_final.html', context)


def gerar_resumo_projecao_tabela(movimentacoes, periodicidade):
    """Gera resumo da projeção em formato de tabela por período"""
    from collections import defaultdict
    from datetime import datetime
    
    resumo = defaultdict(lambda: {
        'nascimentos_femeas': 0,
        'nascimentos_machos': 0,
        'vendas_femeas': 0,
        'vendas_machos': 0,
        'mortes_femeas': 0,
        'mortes_machos': 0,
        'total_rebanho': 0
    })
    
    # Agrupar movimentações por período
    for mov in movimentacoes:
        data = mov.data_movimentacao
        if periodicidade == 'MENSAL':
            periodo = f"{data.month:02d}/{data.year}"
        elif periodicidade == 'TRIMESTRAL':
            trimestre = ((data.month - 1) // 3) + 1
            periodo = f"T{trimestre}/{data.year}"
        elif periodicidade == 'SEMESTRAL':
            semestre = 1 if data.month <= 6 else 2
            periodo = f"S{semestre}/{data.year}"
        else:  # ANUAL
            periodo = str(data.year)
        
        # Categorizar por tipo e sexo
        if mov.tipo_movimentacao == 'NASCIMENTO':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['nascimentos_femeas'] += mov.quantidade
            else:
                resumo[periodo]['nascimentos_machos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'VENDA':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['vendas_femeas'] += mov.quantidade
            else:
                resumo[periodo]['vendas_machos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'MORTE':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['mortes_femeas'] += mov.quantidade
            else:
                resumo[periodo]['mortes_machos'] += mov.quantidade
    
    # Calcular total do rebanho por período
    total_inicial = 0
    for periodo in sorted(resumo.keys()):
        resumo[periodo]['total_rebanho'] = (
            total_inicial + 
            resumo[periodo]['nascimentos_femeas'] + 
            resumo[periodo]['nascimentos_machos'] - 
            resumo[periodo]['vendas_femeas'] - 
            resumo[periodo]['vendas_machos'] - 
            resumo[periodo]['mortes_femeas'] - 
            resumo[periodo]['mortes_machos']
        )
        total_inicial = resumo[periodo]['total_rebanho']
    
    return dict(resumo)


def gerar_evolucao_categorias_tabela(movimentacoes, inventario_inicial):
    """Gera evolução das categorias em formato de tabela"""
    from collections import defaultdict
    from datetime import datetime
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Agrupar movimentações por período e categoria
    evolucao = defaultdict(lambda: defaultdict(int))
    periodos = set()
    
    for mov in movimentacoes:
        data = mov.data_movimentacao
        periodo = f"{data.month:02d}/{data.year}"
        periodos.add(periodo)
        
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'TRANSFERENCIA_ENTRADA']:
            evolucao[categoria][periodo] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA']:
            evolucao[categoria][periodo] -= mov.quantidade
    
    # Ordenar períodos cronologicamente
    periodos_ordenados = sorted(periodos, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
    
    # Calcular saldo acumulado por categoria
    resultado = {}
    for categoria, movimentacoes_cat in evolucao.items():
        saldo_anterior = categorias_inicial.get(categoria, 0)
        resultado[categoria] = [saldo_anterior]  # Saldo inicial
        
        for periodo in periodos_ordenados:
            saldo_anterior += movimentacoes_cat.get(periodo, 0)
            resultado[categoria].append(saldo_anterior)
    
    return resultado, periodos_ordenados


def gerar_evolucao_detalhada_rebanho(movimentacoes, inventario_inicial):
    """Gera evolução detalhada do rebanho com todas as movimentações do período completo"""
    from collections import defaultdict
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Agrupar movimentações por categoria
    movimentacoes_por_categoria = defaultdict(lambda: {
        'nascimentos': 0,
        'compras': 0,
        'vendas': 0,
        'transferencias_entrada': 0,
        'transferencias_saida': 0,
        'promocao_entrada': 0,  # Promoção de categoria (envelhecimento)
        'promocao_saida': 0,    # Promoção de categoria (envelhecimento)
        'mortes': 0,
        'evolucao_categoria': None
    })
    
    # Processar TODAS as movimentações do período completo
    print(f"Processando {len(movimentacoes)} movimentações para evolução detalhada")
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao == 'NASCIMENTO':
            movimentacoes_por_categoria[categoria]['nascimentos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'COMPRA':
            movimentacoes_por_categoria[categoria]['compras'] += mov.quantidade
        elif mov.tipo_movimentacao == 'VENDA':
            movimentacoes_por_categoria[categoria]['vendas'] += mov.quantidade
        elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
            # Distinguir entre transferência entre fazendas e promoção de categoria
            if 'Promoção' in mov.observacao:
                movimentacoes_por_categoria[categoria]['promocao_entrada'] += mov.quantidade
            else:
                movimentacoes_por_categoria[categoria]['transferencias_entrada'] += mov.quantidade
        elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
            # Distinguir entre transferência entre fazendas e promoção de categoria
            if 'Promoção' in mov.observacao:
                movimentacoes_por_categoria[categoria]['promocao_saida'] += mov.quantidade
            else:
                movimentacoes_por_categoria[categoria]['transferencias_saida'] += mov.quantidade
        elif mov.tipo_movimentacao == 'MORTE':
            movimentacoes_por_categoria[categoria]['mortes'] += mov.quantidade
    
    # Calcular saldo final e evolução de categoria
    resultado = {}
    for categoria, movs in movimentacoes_por_categoria.items():
        saldo_inicial = categorias_inicial.get(categoria, 0)
        
        # Calcular saldo final
        saldo_final = (saldo_inicial + 
                      movs['nascimentos'] + 
                      movs['compras'] + 
                      movs['transferencias_entrada'] + 
                      movs['promocao_entrada'] - 
                      movs['vendas'] - 
                      movs['transferencias_saida'] - 
                      movs['promocao_saida'] - 
                      movs['mortes'])
        
        # Calcular evolução de categoria baseada na promoção (envelhecimento)
        evolucao_categoria = None
        if movs['promocao_entrada'] > 0 or movs['promocao_saida'] > 0:
            # Se houve promoção, mostrar o saldo líquido da promoção
            saldo_promocao = movs['promocao_entrada'] - movs['promocao_saida']
            if saldo_promocao > 0:
                evolucao_categoria = f"+{saldo_promocao}"
            elif saldo_promocao < 0:
                evolucao_categoria = f"{saldo_promocao}"
            else:
                evolucao_categoria = "0"
        else:
            # Se não houve promoção, mostrar "-" para indicar que não evoluiu
            evolucao_categoria = "-"
        
        # Mostrar nascimentos apenas para categorias de 0-12 meses
        nascimentos_display = movs['nascimentos'] if any(termo in categoria.lower() for termo in ['bezerro', 'bezerra', '0-12']) else 0
        
        # Obter peso médio da categoria
        try:
            categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
            peso_medio_kg = categoria_obj.peso_medio_kg or Decimal('0.00')
        except CategoriaAnimal.DoesNotExist:
            peso_medio_kg = Decimal('0.00')
        
        # Calcular valor unitário baseado no inventário inicial
        valor_unitario = Decimal('0.00')
        try:
            print(f"Buscando inventário para categoria: '{categoria}'")
            print(f"Inventário disponível:")
            for item in inventario_inicial:
                print(f"   - {item.categoria.nome}: R$ {item.valor_por_cabeca}")
            
            item_inventario = next((item for item in inventario_inicial if item.categoria.nome == categoria), None)
            if item_inventario and item_inventario.valor_por_cabeca:
                valor_unitario = item_inventario.valor_por_cabeca
                print(f"💰 {categoria}: Valor unitário encontrado = R$ {valor_unitario}")
            else:
                print(f"⚠️ {categoria}: Valor unitário não encontrado no inventário")
                if item_inventario:
                    print(f"   Item encontrado mas sem valor: {item_inventario.valor_por_cabeca}")
                else:
                    print(f"   Nenhum item encontrado para esta categoria")
                
                # Usar valor padrão se não encontrar no inventário
                try:
                    categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                    valor_unitario = obter_valor_padrao_por_categoria(categoria_obj)
                    print(f"🔧 {categoria}: Usando valor padrão = R$ {valor_unitario}")
                except CategoriaAnimal.DoesNotExist:
                    valor_unitario = Decimal('2000.00')  # Valor padrão genérico
                    print(f"🔧 {categoria}: Usando valor genérico = R$ {valor_unitario}")
        except Exception as e:
            print(f"ERRO {categoria}: Erro ao buscar valor unitário: {e}")
            valor_unitario = Decimal('0.00')
        
        # Calcular valor total
        valor_total = valor_unitario * Decimal(str(saldo_final))
        
        resultado[categoria] = {
            'saldo_inicial': saldo_inicial,
            'nascimentos': nascimentos_display,
            'compras': movs['compras'],
            'vendas': movs['vendas'],
            'transferencias_entrada': movs['transferencias_entrada'],
            'transferencias_saida': movs['transferencias_saida'],
            'mortes': movs['mortes'],
            'evolucao_categoria': evolucao_categoria,
            'saldo_final': saldo_final,
            'peso_medio_kg': peso_medio_kg,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        }
    
    print(f"Evolução detalhada processada para {len(resultado)} categorias")
    return resultado


def obter_parametros_padrao_ciclo(tipo_ciclo):
    """Retorna parâmetros padrão baseados no tipo de ciclo pecuário"""
    parametros_padrao = {
        'CRIA': {
            'taxa_natalidade_anual': 85.0,
            'taxa_mortalidade_bezerros_anual': 5.0,
            'taxa_mortalidade_adultos_anual': 2.0,
            'percentual_venda_machos_anual': 0.0,  # Não vende machos na cria
            'percentual_venda_femeas_anual': 0.0,  # Não vende fêmeas na cria
            'descricao': 'Foco na reprodução e criação de bezerros'
        },
        'RECRIA': {
            'taxa_natalidade_anual': 0.0,  # Não há reprodução na recria
            'taxa_mortalidade_bezerros_anual': 3.0,
            'taxa_mortalidade_adultos_anual': 1.5,
            'percentual_venda_machos_anual': 0.0,  # Não vende na recria
            'percentual_venda_femeas_anual': 0.0,  # Não vende na recria
            'descricao': 'Foco no desenvolvimento de animais jovens'
        },
        'ENGORDA': {
            'taxa_natalidade_anual': 0.0,  # Não há reprodução na engorda
            'taxa_mortalidade_bezerros_anual': 2.0,
            'taxa_mortalidade_adultos_anual': 1.0,
            'percentual_venda_machos_anual': 100.0,  # Vende todos os machos
            'percentual_venda_femeas_anual': 100.0,  # Vende todas as fêmeas
            'descricao': 'Foco na terminação e venda de animais'
        },
        'CICLO_COMPLETO': {
            'taxa_natalidade_anual': 85.0,
            'taxa_mortalidade_bezerros_anual': 5.0,
            'taxa_mortalidade_adultos_anual': 2.0,
            'percentual_venda_machos_anual': 80.0,  # Vende a maioria dos machos
            'percentual_venda_femeas_anual': 10.0,  # Vende algumas fêmeas
            'descricao': 'Sistema completo: cria, recria e engorda'
        }
    }
    
    return parametros_padrao.get(tipo_ciclo, parametros_padrao['CICLO_COMPLETO'])


def aplicar_parametros_ciclo(propriedade, parametros):
    """Aplica parâmetros específicos baseados no tipo de ciclo da propriedade"""
    if propriedade.tipo_ciclo_pecuario:
        parametros_ciclo = obter_parametros_padrao_ciclo(propriedade.tipo_ciclo_pecuario)
        
        # Atualizar parâmetros se não foram definidos pelo usuário
        if not parametros.taxa_natalidade_anual:
            parametros.taxa_natalidade_anual = parametros_ciclo['taxa_natalidade_anual']
        if not parametros.taxa_mortalidade_bezerros_anual:
            parametros.taxa_mortalidade_bezerros_anual = parametros_ciclo['taxa_mortalidade_bezerros_anual']
        if not parametros.taxa_mortalidade_adultos_anual:
            parametros.taxa_mortalidade_adultos_anual = parametros_ciclo['taxa_mortalidade_adultos_anual']
        if not parametros.percentual_venda_machos_anual:
            parametros.percentual_venda_machos_anual = parametros_ciclo['percentual_venda_machos_anual']
        if not parametros.percentual_venda_femeas_anual:
            parametros.percentual_venda_femeas_anual = parametros_ciclo['percentual_venda_femeas_anual']
        
        parametros.save()
    
    return parametros


# Views para Transferências entre Propriedades
@login_required
def transferencias_lista(request):
    """Lista todas as transferências do usuário"""
    transferencias = TransferenciaPropriedade.objects.filter(
        Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
        Q(propriedade_destino__produtor__usuario_responsavel=request.user)
    ).order_by('-data_transferencia')
    
    context = {
        'transferencias': transferencias,
    }
    return render(request, 'gestao_rural/transferencias_lista.html', context)


@login_required
def transferencia_nova(request):
    """Criar nova transferência entre propriedades"""
    if request.method == 'POST':
        form = TransferenciaPropriedadeForm(request.POST, user=request.user)
        if form.is_valid():
            transferencia = form.save()
            messages.success(request, 'Transferência cadastrada com sucesso!')
            return redirect('transferencias_lista')
    else:
        form = TransferenciaPropriedadeForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'gestao_rural/transferencia_nova.html', context)


@login_required
def transferencia_editar(request, transferencia_id):
    """Editar transferência existente"""
    transferencia = get_object_or_404(
        TransferenciaPropriedade.objects.filter(
            Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
            Q(propriedade_destino__produtor__usuario_responsavel=request.user)
        ),
        id=transferencia_id
    )
    
    if request.method == 'POST':
        form = TransferenciaPropriedadeForm(request.POST, instance=transferencia, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transferência atualizada com sucesso!')
            return redirect('transferencias_lista')
    else:
        form = TransferenciaPropriedadeForm(instance=transferencia, user=request.user)
    
    context = {
        'form': form,
        'transferencia': transferencia,
    }
    return render(request, 'gestao_rural/transferencia_editar.html', context)


@login_required
def transferencia_excluir(request, transferencia_id):
    """Excluir transferência"""
    transferencia = get_object_or_404(
        TransferenciaPropriedade.objects.filter(
            Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
            Q(propriedade_destino__produtor__usuario_responsavel=request.user)
        ),
        id=transferencia_id
    )
    
    if request.method == 'POST':
        transferencia.delete()
        messages.success(request, 'Transferência excluída com sucesso!')
        return redirect('transferencias_lista')
    
    context = {
        'transferencia': transferencia,
    }
    return render(request, 'gestao_rural/transferencia_excluir.html', context)


def gerar_resumo_projecao_por_ano(movimentacoes, inventario_inicial):
    """Gera resumo da projeção organizado por ano no mesmo formato da Evolução Detalhada"""
    from collections import defaultdict
    from datetime import datetime
    from .models import CategoriaAnimal
    
    # Buscar todas as categorias ativas
    todas_categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('sexo', 'idade_minima_meses')
    nomes_categorias = [cat.nome for cat in todas_categorias]
    
    # Agrupar movimentações por ano
    movimentacoes_por_ano = defaultdict(list)
    for mov in movimentacoes:
        ano = mov.data_movimentacao.year
        movimentacoes_por_ano[ano].append(mov)
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Gerar resumo detalhado para cada ano
    resumo_por_ano = {}
    saldos_finais_ano_anterior = {}  # Armazenar saldos finais do ano anterior
    
    for ano in sorted(movimentacoes_por_ano.keys()):
        movimentacoes_ano = movimentacoes_por_ano[ano]
        
        # Agrupar movimentações por categoria para o ano
        movimentacoes_por_categoria = defaultdict(lambda: {
            'nascimentos': 0,
            'compras': 0,
            'vendas': 0,
            'transferencias_entrada': 0,
            'transferencias_saida': 0,
            'promocao_entrada': 0,
            'promocao_saida': 0,
            'mortes': 0,
            'evolucao_categoria': None
        })
        
        for mov in movimentacoes_ano:
            categoria = mov.categoria.nome
            
            if mov.tipo_movimentacao == 'NASCIMENTO':
                movimentacoes_por_categoria[categoria]['nascimentos'] += mov.quantidade
            elif mov.tipo_movimentacao == 'COMPRA':
                movimentacoes_por_categoria[categoria]['compras'] += mov.quantidade
            elif mov.tipo_movimentacao == 'VENDA':
                movimentacoes_por_categoria[categoria]['vendas'] += mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                if 'Promoção' in mov.observacao:
                    movimentacoes_por_categoria[categoria]['promocao_entrada'] += mov.quantidade
                else:
                    movimentacoes_por_categoria[categoria]['transferencias_entrada'] += mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                if 'Promoção' in mov.observacao:
                    movimentacoes_por_categoria[categoria]['promocao_saida'] += mov.quantidade
                else:
                    movimentacoes_por_categoria[categoria]['transferencias_saida'] += mov.quantidade
            elif mov.tipo_movimentacao == 'MORTE':
                movimentacoes_por_categoria[categoria]['mortes'] += mov.quantidade
        
        # Calcular resultado para cada categoria do ano
        resultado_ano = {}
        
        # Processar todas as categorias ativas, não apenas as que têm movimentações
        for categoria_nome in nomes_categorias:
            # Obter movimentações para esta categoria (pode estar vazio)
            movs = movimentacoes_por_categoria.get(categoria_nome, {
                'nascimentos': 0,
                'compras': 0,
                'vendas': 0,
                'transferencias_entrada': 0,
                'transferencias_saida': 0,
                'promocao_entrada': 0,
                'promocao_saida': 0,
                'mortes': 0,
                'evolucao_categoria': None
            })
            # Para o primeiro ano, usar inventário inicial
            # Para anos seguintes, usar saldo final do ano anterior
            if ano == min(movimentacoes_por_ano.keys()):
                saldo_inicial = categorias_inicial.get(categoria_nome, 0)
            else:
                saldo_inicial = saldos_finais_ano_anterior.get(categoria_nome, 0)
            
            # Calcular saldo final
            saldo_final = (saldo_inicial + 
                          movs['nascimentos'] + 
                          movs['compras'] + 
                          movs['transferencias_entrada'] + 
                          movs['promocao_entrada'] - 
                          movs['vendas'] - 
                          movs['transferencias_saida'] - 
                          movs['promocao_saida'] - 
                          movs['mortes'])
            
            # Calcular evolução de categoria
            evolucao_categoria = None
            if movs['promocao_entrada'] > 0 or movs['promocao_saida'] > 0:
                saldo_promocao = movs['promocao_entrada'] - movs['promocao_saida']
                if saldo_promocao > 0:
                    evolucao_categoria = f"+{saldo_promocao}"
                elif saldo_promocao < 0:
                    evolucao_categoria = f"{saldo_promocao}"
                else:
                    evolucao_categoria = "0"
            else:
                evolucao_categoria = "-"
            
            # Mostrar nascimentos apenas para categorias de 0-12 meses
            nascimentos_display = movs['nascimentos'] if any(termo in categoria_nome.lower() for termo in ['bezerro', 'bezerra', '0-12']) else 0
            
            # Obter peso médio da categoria
            try:
                categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                peso_medio_kg = categoria_obj.peso_medio_kg or Decimal('0.00')
            except CategoriaAnimal.DoesNotExist:
                peso_medio_kg = Decimal('0.00')
            
            # Calcular valor unitário baseado no inventário inicial
            valor_unitario = Decimal('0.00')
            try:
                item_inventario = next((item for item in inventario_inicial if item.categoria.nome == categoria_nome), None)
                if item_inventario and item_inventario.valor_por_cabeca:
                    valor_unitario = item_inventario.valor_por_cabeca
                else:
                    # Usar valor padrão se não encontrar no inventário
                    try:
                        categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                        valor_unitario = obter_valor_padrao_por_categoria(categoria_obj)
                    except CategoriaAnimal.DoesNotExist:
                        valor_unitario = Decimal('2000.00')  # Valor padrão genérico
            except:
                valor_unitario = Decimal('2000.00')  # Valor padrão genérico em caso de erro
            
            # Calcular valor total
            valor_total = valor_unitario * Decimal(str(saldo_final))
            
            resultado_ano[categoria_nome] = {
                'saldo_inicial': saldo_inicial,
                'nascimentos': nascimentos_display,
                'compras': movs['compras'],
                'vendas': movs['vendas'],
                'transferencias_entrada': movs['transferencias_entrada'],
                'transferencias_saida': movs['transferencias_saida'],
                'mortes': movs['mortes'],
                'evolucao_categoria': evolucao_categoria,
                'saldo_final': saldo_final,
                'peso_medio_kg': peso_medio_kg,
                'valor_unitario': valor_unitario,
                'valor_total': valor_total
            }
            
            # Armazenar saldo final para usar como saldo inicial do próximo ano
            saldos_finais_ano_anterior[categoria_nome] = saldo_final
        
        # Calcular totais do ano
        totais_ano = {
            'saldo_inicial_total': 0,
            'nascimentos_total': 0,
            'compras_total': 0,
            'vendas_total': 0,
            'transferencias_entrada_total': 0,
            'transferencias_saida_total': 0,
            'mortes_total': 0,
            'saldo_final_total': 0,
            'valor_total_geral': Decimal('0.00')
        }
        
        for categoria_nome, dados in resultado_ano.items():
            totais_ano['saldo_inicial_total'] += dados['saldo_inicial']
            totais_ano['nascimentos_total'] += dados['nascimentos']
            totais_ano['compras_total'] += dados['compras']
            totais_ano['vendas_total'] += dados['vendas']
            totais_ano['transferencias_entrada_total'] += dados['transferencias_entrada']
            totais_ano['transferencias_saida_total'] += dados['transferencias_saida']
            totais_ano['mortes_total'] += dados['mortes']
            totais_ano['saldo_final_total'] += dados['saldo_final']
            totais_ano['valor_total_geral'] += dados['valor_total']
        
        # Adicionar linha de totais
        resultado_ano['TOTAIS'] = {
            'saldo_inicial': totais_ano['saldo_inicial_total'],
            'nascimentos': totais_ano['nascimentos_total'],
            'compras': totais_ano['compras_total'],
            'vendas': totais_ano['vendas_total'],
            'transferencias_entrada': totais_ano['transferencias_entrada_total'],
            'transferencias_saida': totais_ano['transferencias_saida_total'],
            'mortes': totais_ano['mortes_total'],
            'evolucao_categoria': '-',
            'saldo_final': totais_ano['saldo_final_total'],
            'peso_medio_kg': Decimal('0.00'),
            'valor_unitario': Decimal('0.00'),
            'valor_total': totais_ano['valor_total_geral']
        }
        
        resumo_por_ano[ano] = resultado_ano
    
    print(f"Resumo por ano processado para {len(resumo_por_ano)} anos")
    return resumo_por_ano


# ==================== GESTÃO DE CATEGORIAS ====================

@login_required
def categorias_lista(request):
    """Lista todas as categorias de animais"""
    categorias = CategoriaAnimal.objects.all().order_by('nome')
    return render(request, 'gestao_rural/categorias_lista.html', {'categorias': categorias})


@login_required
def categoria_nova(request):
    """Cria uma nova categoria de animal"""
    if request.method == 'POST':
        form = CategoriaAnimalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('categorias_lista')
    else:
        form = CategoriaAnimalForm()
    
    return render(request, 'gestao_rural/categoria_nova.html', {'form': form})


@login_required
def categoria_editar(request, categoria_id):
    """Edita uma categoria existente"""
    categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaAnimalForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('categorias_lista')
    else:
        form = CategoriaAnimalForm(instance=categoria)
    
    return render(request, 'gestao_rural/categoria_editar.html', {'form': form, 'categoria': categoria})


@login_required
def categoria_excluir(request, categoria_id):
    """Exclui uma categoria"""
    categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
    
    if request.method == 'POST':
        # Verificar se a categoria está sendo usada em algum inventário
        inventarios = InventarioRebanho.objects.filter(categoria=categoria)
        if inventarios.exists():
            messages.error(request, f'Não é possível excluir a categoria "{categoria.nome}" pois ela está sendo usada em {inventarios.count()} inventário(s).')
            return redirect('categorias_lista')
        
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('categorias_lista')
    
    return render(request, 'gestao_rural/categoria_excluir.html', {'categoria': categoria})


def obter_saldo_atual_propriedade(propriedade, data_referencia):
    """Obtém o saldo atual de uma propriedade em uma data específica"""
    from decimal import Decimal
    
    saldo_por_categoria = {}
    
    # Obter inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    if inventario_inicial:
        # Saldo inicial
        saldo_por_categoria[inventario_inicial.categoria] = inventario_inicial.quantidade
        
        # Calcular movimentações desde o inventário inicial
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            data_movimentacao__gt=inventario_inicial.data_inventario,
            data_movimentacao__lte=data_referencia
        )
        
        for movimentacao in movimentacoes:
            categoria = movimentacao.categoria
            
            if categoria not in saldo_por_categoria:
                saldo_por_categoria[categoria] = 0
            
            if movimentacao.tipo_movimentacao == 'NASCIMENTO':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'COMPRA':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'VENDA':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'MORTE':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
    
    return saldo_por_categoria


def obter_valor_padrao_por_categoria(categoria):
    """Retorna valores padrão por categoria de animal"""
    from decimal import Decimal
    
    # Valores padrão baseados no mercado brasileiro (R$ por cabeça)
    valores_padrao = {
        'bezerro': Decimal('800.00'),      # 0-12 meses
        'bezerra': Decimal('1200.00'),     # 0-12 meses
        'garrote': Decimal('1800.00'),     # 12-24 meses
        'novilha': Decimal('2200.00'),     # 12-24 meses
        'boi': Decimal('2800.00'),         # 24-36 meses
        'boi_magro': Decimal('2500.00'),   # 24-36 meses (magro)
        'primipara': Decimal('3000.00'),   # 24-36 meses
        'multipara': Decimal('3500.00'),   # >36 meses
        'vaca_descarte': Decimal('2000.00'), # vacas de descarte
        'touro': Decimal('4000.00')        # reprodutores
    }
    
    nome_categoria = categoria.nome.lower()
    
    # Identificar o tipo de animal baseado no nome da categoria
    if 'bezerro' in nome_categoria and 'bezerra' not in nome_categoria:
        return valores_padrao['bezerro']
    elif 'bezerra' in nome_categoria:
        return valores_padrao['bezerra']
    elif 'garrote' in nome_categoria:
        return valores_padrao['garrote']
    elif 'novilha' in nome_categoria:
        return valores_padrao['novilha']
    elif 'boi' in nome_categoria and 'magro' in nome_categoria:
        return valores_padrao['boi_magro']
    elif 'boi' in nome_categoria:
        return valores_padrao['boi']
    elif 'primípara' in nome_categoria or 'primipara' in nome_categoria:
        return valores_padrao['primipara']
    elif 'multípara' in nome_categoria or 'multipara' in nome_categoria:
        return valores_padrao['multipara']
    elif 'descarte' in nome_categoria:
        return valores_padrao['vaca_descarte']
    elif 'touro' in nome_categoria:
        return valores_padrao['touro']
    else:
        # Valor padrão genérico
        return Decimal('2000.00')


def processar_compras_configuradas(propriedade, data_referencia, fator_inflacao=1.0):
    """Processa compras configuradas para uma propriedade com inflação"""
    from decimal import Decimal
    
    print(f"Processando compras para {propriedade.nome_propriedade} em {data_referencia} (inflação: {fator_inflacao:.2%})")
    
    # Buscar configurações de venda que geram compras
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade,
        tipo_reposicao='COMPRA',
        ativo=True
    )
    
    print(f"Configurações de compra encontradas: {configuracoes.count()}")
    for config in configuracoes:
        print(f"   - {config.categoria_compra.nome} (Qtd: {config.quantidade_compra})")
    
    compras_processadas = []
    
    for config in configuracoes:
        print(f"Processando compra: {config.categoria_compra.nome}")
        
        # Verificar se é o momento da compra baseado na frequência
        momento_correto = verificar_momento_compra(config, data_referencia)
        print(f"   Momento correto: {momento_correto}")
        
        if momento_correto and config.quantidade_compra > 0:
            # Calcular valor com inflação
            valor_original = config.valor_animal_compra or Decimal('0')
            
            # Se não há valor configurado, usar valor padrão
            if valor_original == 0:
                valor_original = obter_valor_padrao_por_categoria(config.categoria_compra)
            
            valor_com_inflacao = valor_original * Decimal(str(fator_inflacao))
            
            # Registrar a compra com valor inflacionado
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                data_movimentacao=data_referencia,
                tipo_movimentacao='COMPRA',
                categoria=config.categoria_compra,
                quantidade=config.quantidade_compra,
                observacao=f'Compra configurada - {config.categoria_compra.nome} - R$ {valor_com_inflacao}/cabeça (Inflação: {fator_inflacao:.1%})'
            )
            
            compras_processadas.append({
                'categoria': config.categoria_compra,
                'quantidade': config.quantidade_compra,
                'valor_unitario': valor_com_inflacao,
                'valor_total': valor_com_inflacao * config.quantidade_compra
            })
            
            print(f"Compra aplicada: {config.categoria_compra.nome} +{config.quantidade_compra} (R$ {valor_com_inflacao:.2f} cada)")
        else:
            print(f"AVISO: Não é o momento da compra ou quantidade zero")
    
    print(f"Total de compras processadas: {len(compras_processadas)}")
    return compras_processadas


def verificar_momento_compra(config, data_referencia):
    """Verifica se é o momento correto para realizar uma compra baseado na frequência"""
    from datetime import datetime, timedelta
    
    print(f"Verificando momento da compra:")
    print(f"   Frequência: {config.frequencia_venda}")
    print(f"   Data referência: {data_referencia}")
    print(f"   Data criação: {config.data_criacao}")
    
    # Converter data_referencia para datetime se necessário
    if isinstance(data_referencia, str):
        data_referencia = datetime.strptime(data_referencia, '%Y-%m-%d').date()
    elif hasattr(data_referencia, 'date'):
        data_referencia = data_referencia.date()
    
    # Calcular dias baseado na frequência
    frequencia_dias = {
        'MENSAL': 30,
        'BIMESTRAL': 60,
        'TRIMESTRAL': 90,
        'SEMESTRAL': 180,
        'ANUAL': 365
    }
    
    dias_frequencia = frequencia_dias.get(config.frequencia_venda, 30)
    print(f"   Dias necessários: {dias_frequencia}")
    
    # Verificar se já passou o tempo suficiente desde a última compra
    ultima_compra = MovimentacaoProjetada.objects.filter(
        propriedade=config.propriedade,
        tipo_movimentacao='COMPRA',
        categoria=config.categoria_compra
    ).order_by('-data_movimentacao').first()
    
    if ultima_compra:
        dias_desde_ultima = (data_referencia - ultima_compra.data_movimentacao).days
        print(f"   Última compra: {ultima_compra.data_movimentacao}")
        print(f"   Dias desde última: {dias_desde_ultima}")
        resultado = dias_desde_ultima >= dias_frequencia
    else:
        # Primeira compra - verificar se passou o tempo mínimo
        dias_desde_inicio = (data_referencia - config.data_criacao.date()).days
        print(f"   Primeira compra - dias desde criação: {dias_desde_inicio}")
        resultado = dias_desde_inicio >= dias_frequencia
    
    print(f"   Resultado: {resultado}")
    return resultado


def processar_transferencias_configuradas(propriedade_destino, data_referencia):
    """Processa transferências configuradas para uma propriedade de destino"""
    from decimal import Decimal
    
    print(f"Processando transferências para {propriedade_destino.nome_propriedade} em {data_referencia}")
    
    # Buscar configurações de venda que geram transferências
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade_destino,
        tipo_reposicao='TRANSFERENCIA',
        ativo=True
    )
    
    print(f"Configurações encontradas: {configuracoes.count()}")
    for config in configuracoes:
        print(f"   - {config.categoria_venda.nome} de {config.fazenda_origem.nome_propriedade} (Qtd: {config.quantidade_transferencia})")
    
    transferencias_processadas = []
    
    for config in configuracoes:
        print(f"Verificando configuração: {config.categoria_venda.nome}")
        
        # Verificar se é o momento da transferência baseado na frequência
        momento_correto = verificar_momento_transferencia(config, data_referencia)
        print(f"   Momento correto: {momento_correto}")
        
        if momento_correto:
            # Obter saldo da propriedade de origem
            saldo_origem = obter_saldo_atual_propriedade(config.fazenda_origem, data_referencia)
            print(f"   Saldo origem: {saldo_origem}")
            
            # Verificar se há saldo suficiente na categoria de origem
            categoria_origem = config.categoria_venda
            saldo_disponivel = saldo_origem.get(categoria_origem, 0)
            print(f"   Saldo disponível: {saldo_disponivel}, Quantidade necessária: {config.quantidade_transferencia}")
            
            if saldo_disponivel >= config.quantidade_transferencia:
                # Criar transferência de saída na origem
                movimentacao_saida = MovimentacaoProjetada.objects.create(
                    propriedade=config.fazenda_origem,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    categoria=categoria_origem,
                    quantidade=config.quantidade_transferencia,
                    observacao=f'Transferência para {propriedade_destino.nome_propriedade}'
                )
                
                # Criar transferência de entrada no destino
                movimentacao_entrada = MovimentacaoProjetada.objects.create(
                    propriedade=propriedade_destino,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    categoria=categoria_origem,
                    quantidade=config.quantidade_transferencia,
                    observacao=f'Transferência de {config.fazenda_origem.nome_propriedade}'
                )
                
                transferencias_processadas.append({
                    'origem': config.fazenda_origem,
                    'destino': propriedade_destino,
                    'categoria': categoria_origem,
                    'quantidade': config.quantidade_transferencia,
                    'data': data_referencia
                })
                
                print(f"Transferência processada: {config.fazenda_origem.nome_propriedade} → {propriedade_destino.nome_propriedade}")
                print(f"   Categoria: {categoria_origem.nome}")
                print(f"   Quantidade: {config.quantidade_transferencia}")
                print(f"   Data: {data_referencia}")
            else:
                print(f"ERRO: Saldo insuficiente: {saldo_disponivel} < {config.quantidade_transferencia}")
        else:
            print(f"AVISO: Não é o momento da transferência")
    
    print(f"Total de transferências processadas: {len(transferencias_processadas)}")
    return transferencias_processadas


def verificar_momento_transferencia(config, data_referencia):
    """Verifica se é o momento de processar uma transferência baseado na frequência"""
    from datetime import datetime, timedelta
    
    print(f"Verificando momento da transferência:")
    print(f"   Frequência: {config.frequencia_venda}")
    print(f"   Data referência: {data_referencia}")
    print(f"   Data criação: {config.data_criacao}")
    
    # Converter data_referencia para datetime se necessário
    if isinstance(data_referencia, str):
        data_referencia = datetime.strptime(data_referencia, '%Y-%m-%d').date()
    elif hasattr(data_referencia, 'date'):
        data_referencia = data_referencia.date()
    
    # Calcular dias baseado na frequência
    frequencia_dias = {
        'MENSAL': 30,
        'BIMESTRAL': 60,
        'TRIMESTRAL': 90,
        'SEMESTRAL': 180,
        'ANUAL': 365
    }
    
    dias_frequencia = frequencia_dias.get(config.frequencia_venda, 30)
    print(f"   Dias necessários: {dias_frequencia}")
    
    # Verificar se já passou o tempo suficiente desde a última transferência
    ultima_transferencia = MovimentacaoProjetada.objects.filter(
        propriedade=config.propriedade,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=config.categoria_venda
    ).order_by('-data_movimentacao').first()
    
    if ultima_transferencia:
        dias_desde_ultima = (data_referencia - ultima_transferencia.data_movimentacao).days
        print(f"   Última transferência: {ultima_transferencia.data_movimentacao}")
        print(f"   Dias desde última: {dias_desde_ultima}")
        resultado = dias_desde_ultima >= dias_frequencia
    else:
        # Primeira transferência - verificar se passou o tempo mínimo
        dias_desde_inicio = (data_referencia - config.data_criacao.date()).days
        print(f"   Primeira transferência - dias desde criação: {dias_desde_inicio}")
        resultado = dias_desde_inicio >= dias_frequencia
    
    print(f"   Resultado: {resultado}")
    return resultado


@login_required
def testar_transferencias(request, propriedade_id):
    """View para testar o sistema de transferências"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar configurações de transferência
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade,
        tipo_reposicao='TRANSFERENCIA',
        ativo=True
    )
    
    # Simular data atual
    from datetime import date
    data_atual = date.today()
    
    # Processar transferências
    transferencias_processadas = processar_transferencias_configuradas(propriedade, data_atual)
    
    context = {
        'propriedade': propriedade,
        'configuracoes': configuracoes,
        'transferencias_processadas': transferencias_processadas,
        'data_teste': data_atual,
    }
    
    return render(request, 'gestao_rural/testar_transferencias.html', context)


@login_required
def obter_saldo_fazenda_ajax(request, fazenda_id, categoria_id):
    """AJAX endpoint para obter saldo atual de uma fazenda"""
    from datetime import date
    import json
    
    try:
        fazenda = get_object_or_404(Propriedade, id=fazenda_id, produtor__usuario_responsavel=request.user)
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        
        # Obter saldo atual
        data_atual = date.today()
        saldo_por_categoria = obter_saldo_atual_propriedade(fazenda, data_atual)
        saldo_atual = saldo_por_categoria.get(categoria, 0)
        
        return JsonResponse({
            'success': True,
            'fazenda': fazenda.nome_propriedade,
            'categoria': categoria.nome,
            'saldo_atual': saldo_atual,
            'data_consulta': data_atual.strftime('%d/%m/%Y')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def buscar_saldo_inventario(request, propriedade_id, categoria_id):
    """View para buscar saldo do inventário de uma categoria específica"""
    try:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        
        # Buscar inventário da categoria
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria
        ).first()
        
        if inventario:
            quantidade = inventario.quantidade
            categoria_nome = categoria.nome
        else:
            quantidade = 0
            categoria_nome = categoria.nome
        
        return JsonResponse({
            'success': True,
            'quantidade': quantidade,
            'categoria_nome': categoria_nome,
            'propriedade_nome': propriedade.nome_propriedade
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar saldo: {str(e)}'
        })
