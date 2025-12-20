# -*- coding: utf-8 -*-
"""
Views Completas para IATF
Sistema profissional de gestão de IATF
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, datetime, timedelta

from .models import Propriedade, AnimalIndividual, CategoriaAnimal
from .decorators import obter_propriedade_com_permissao
try:
    from .models_reproducao import EstacaoMonta
except ImportError:
    EstacaoMonta = None

try:
    from .models_iatf_completo import (
        ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF, EtapaLoteIATF,
        IATFIndividual, AplicacaoMedicamentoIATF, CalendarioIATF
    )
except ImportError:
    # Se não existir, criar classes vazias para não quebrar
    ProtocoloIATF = None
    TouroSemen = None
    LoteSemen = None
    LoteIATF = None
    IATFIndividual = None
    AplicacaoMedicamentoIATF = None
    CalendarioIATF = None


User = get_user_model()


@login_required
def iatf_dashboard(request, propriedade_id):
    """Dashboard completo de IATF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not IATFIndividual:
        messages.warning(request, 'Módulo IATF completo não está disponível. Execute as migrations primeiro.')
        return redirect('reproducao_dashboard', propriedade_id=propriedade.id)
    
    # Estatísticas Gerais
    total_iatfs = IATFIndividual.objects.filter(propriedade=propriedade).count()
    iatfs_pendentes = IATFIndividual.objects.filter(
        propriedade=propriedade,
        status__in=['PROGRAMADA', 'PROTOCOLO_INICIADO']
    ).count()
    
    iatfs_realizadas = IATFIndividual.objects.filter(
        propriedade=propriedade,
        status='REALIZADA'
    ).count()
    
    # Resultados
    prenhezes = IATFIndividual.objects.filter(
        propriedade=propriedade,
        resultado='PREMIDA'
    ).count()
    
    vazias = IATFIndividual.objects.filter(
        propriedade=propriedade,
        resultado='VAZIA'
    ).count()
    
    taxa_prenhez_geral = Decimal('0.00')
    if iatfs_realizadas > 0:
        taxa_prenhez_geral = (Decimal(str(prenhezes)) / Decimal(str(iatfs_realizadas))) * 100
    
    # Lotes
    lotes_ativos = LoteIATF.objects.filter(
        propriedade=propriedade,
        status__in=['PLANEJADO', 'EM_ANDAMENTO']
    ).count()
    
    # Protocolos mais usados
    protocolos_mais_usados = ProtocoloIATF.objects.filter(
        iatfs__propriedade=propriedade
    ).annotate(
        total_uso=Count('iatfs')
    ).order_by('-total_uso')[:5] if ProtocoloIATF else []
    
    # Sêmen
    lotes_semen_estoque = LoteSemen.objects.filter(
        propriedade=propriedade,
        status='ESTOQUE',
        doses_disponiveis__gt=0
    ) if LoteSemen else []
    total_doses_disponiveis = sum(l.doses_disponiveis for l in lotes_semen_estoque)
    
    # IATFs do mês
    taxa_prenhez_mes = Decimal('0.00')
    prenhezes_mes = 0
    iatfs_realizadas_mes = 0
    
    if IATFIndividual:
        mes_atual = date.today().replace(day=1)
        iatfs_mes = IATFIndividual.objects.filter(
            propriedade=propriedade,
            data_iatf__gte=mes_atual
        )
        prenhezes_mes = iatfs_mes.filter(resultado='PREMIDA').count()
        iatfs_realizadas_mes = iatfs_mes.filter(status='REALIZADA').count()
        if iatfs_realizadas_mes > 0:
            taxa_prenhez_mes = (Decimal(str(prenhezes_mes)) / Decimal(str(iatfs_realizadas_mes))) * 100
    
    # Próximas IATFs
    proximas_iatfs = []
    if IATFIndividual:
        proximas_iatfs = IATFIndividual.objects.filter(
            propriedade=propriedade,
            data_iatf__gte=date.today(),
            status__in=['PROGRAMADA', 'PROTOCOLO_INICIADO', 'DIA_0_GNRH', 'DIA_7_PGF2A', 'DIA_9_GNRH']
        ).select_related('animal_individual', 'protocolo').order_by('data_iatf')[:10]
    
    # Lotes em andamento
    lotes_andamento = []
    if LoteIATF:
        lotes_andamento = LoteIATF.objects.filter(
            propriedade=propriedade,
            status='EM_ANDAMENTO'
        ).select_related('protocolo', 'touro_semen').order_by('-data_inicio')[:5]
    
    context = {
        'propriedade': propriedade,
        'total_iatfs': total_iatfs,
        'iatfs_pendentes': iatfs_pendentes,
        'iatfs_realizadas': iatfs_realizadas,
        'prenhezes': prenhezes,
        'vazias': vazias,
        'taxa_prenhez_geral': taxa_prenhez_geral,
        'lotes_ativos': lotes_ativos,
        'protocolos_mais_usados': protocolos_mais_usados,
        'total_doses_disponiveis': total_doses_disponiveis,
        'taxa_prenhez_mes': taxa_prenhez_mes,
        'prenhezes_mes': prenhezes_mes,
        'iatfs_realizadas_mes': iatfs_realizadas_mes,
        'proximas_iatfs': proximas_iatfs,
        'lotes_andamento': lotes_andamento,
    }
    
    return render(request, 'gestao_rural/iatf_dashboard.html', context)


@login_required
def lote_iatf_novo(request, propriedade_id):
    """Criar novo lote de IATF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    protocolos = ProtocoloIATF.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True),
        ativo=True
    )
    touros = TouroSemen.objects.filter(ativo=True)
    lotes_semen = LoteSemen.objects.filter(
        propriedade=propriedade,
        status='ESTOQUE',
        doses_disponiveis__gt=0
    )
    estacoes = EstacaoMonta.objects.filter(propriedade=propriedade, ativa=True)
    categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('nome')
    inseminadores = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    if request.method == 'POST':
        if not LoteIATF:
            messages.error(request, 'Módulo IATF completo não está disponível.')
            return redirect('reproducao_dashboard', propriedade_id=propriedade.id)
        
        lote = LoteIATF(propriedade=propriedade)
        lote.nome_lote = request.POST.get('nome_lote')
        lote.protocolo_id = request.POST.get('protocolo')
        lote.data_inicio = datetime.strptime(
            request.POST.get('data_inicio'), '%Y-%m-%d'
        ).date()
        
        if request.POST.get('estacao_monta'):
            lote.estacao_monta_id = request.POST.get('estacao_monta')
        if request.POST.get('touro_semen'):
            lote.touro_semen_id = request.POST.get('touro_semen')
        if request.POST.get('lote_semen'):
            lote.lote_semen_id = request.POST.get('lote_semen')
        if request.POST.get('score_reprodutivo'):
            try:
                lote.score_reprodutivo = Decimal(str(request.POST.get('score_reprodutivo')).replace(',', '.'))
            except Exception:
                lote.score_reprodutivo = None
        if request.POST.get('inseminador_padrao'):
            lote.inseminador_padrao_id = request.POST.get('inseminador_padrao')
        
        lote.custo_medicamentos = Decimal(request.POST.get('custo_medicamentos', 0))
        lote.custo_mao_obra = Decimal(request.POST.get('custo_mao_obra', 0))
        lote.observacoes = request.POST.get('observacoes', '')
        lote.responsavel = request.user
        
        try:
            lote.save()
            
            categorias_ids = request.POST.getlist('categoria_animais')
            if categorias_ids:
                lote.categoria_animais.set(categorias_ids)

            # Registrar etapas informadas (D0, D8, D10)
            usuarios_map = {str(user.id): user for user in inseminadores}
            usuarios_map[str(request.user.id)] = request.user

            etapas_form = [
                ('d0', 'D0', 0),
                ('d8', 'D8', lote.protocolo.dia_pgf2a if lote.protocolo else 8),
                ('d10', 'D10', lote.protocolo.dia_iatf if lote.protocolo else 10),
            ]
            etapas_criadas = 0
            for prefixo, codigo, dia_rel in etapas_form:
                nome = request.POST.get(f'{prefixo}_nome') or (
                    'Dia 0 - Início do Protocolo' if codigo == 'D0' else
                    'Dia 8 - Procedimentos' if codigo == 'D8' else
                    'Dia 10 - Inseminação'
                )
                data_prevista_str = request.POST.get(f'{prefixo}_data', '')
                hora_prevista_str = request.POST.get(f'{prefixo}_hora', '')
                medicamento = request.POST.get(f'{prefixo}_medicamento', '')
                descricao = request.POST.get(f'{prefixo}_descricao', '')
                responsavel_id = request.POST.get(f'{prefixo}_responsavel')
                status_etapa = request.POST.get(f'{prefixo}_status', 'AGENDADA')

                if data_prevista_str:
                    data_prevista = datetime.strptime(data_prevista_str, '%Y-%m-%d').date()
                else:
                    data_prevista = lote.data_inicio + timedelta(days=dia_rel)

                hora_prevista = None
                if hora_prevista_str:
                    try:
                        hora_prevista = datetime.strptime(hora_prevista_str, '%H:%M').time()
                    except ValueError:
                        hora_prevista = None

                responsavel_planejado = usuarios_map.get(responsavel_id) if responsavel_id else None

                etapa_kwargs = {
                    'lote': lote,
                    'nome_etapa': nome,
                    'codigo_etapa': codigo,
                    'dia_relativo': dia_rel,
                    'data_prevista': data_prevista,
                    'hora_prevista': hora_prevista,
                    'medicamento_planejado': medicamento or None,
                    'descricao_planejada': descricao or None,
                    'responsavel_planejado': responsavel_planejado or lote.inseminador_padrao or request.user,
                    'status': status_etapa if status_etapa in dict(EtapaLoteIATF.STATUS_CHOICES) else 'AGENDADA',
                }

                if codigo == 'D10':
                    etapa_kwargs['inseminador'] = responsavel_planejado or lote.inseminador_padrao
                    etapa_kwargs['touro_semen'] = lote.touro_semen

                EtapaLoteIATF.objects.create(**etapa_kwargs)
                etapas_criadas += 1

            if etapas_criadas == 0:
                lote.gerar_etapas_padrao(request.user)
            
            messages.success(request, 'Lote de IATF criado com sucesso!')
            return redirect('lote_iatf_detalhes', propriedade_id=propriedade.id, lote_id=lote.id)
        except Exception as e:
            messages.error(request, f'Erro ao criar lote: {str(e)}')
    
    # Etapas padrão do protocolo IATF
    etapas_protocolo = [
        ('d0', 'Dia 0 - Início do Protocolo'),
        ('d8', 'Dia 8 - Procedimentos'),
        ('d10', 'Dia 10 - Inseminação')
    ]
    
    return render(request, 'gestao_rural/lote_iatf_form.html', {
        'propriedade': propriedade,
        'protocolos': protocolos,
        'touros': touros,
        'lotes_semen': lotes_semen,
        'estacoes': estacoes,
        'categorias': categorias,
        'inseminadores': inseminadores,
        'status_etapas': EtapaLoteIATF.STATUS_CHOICES,
        'etapas_protocolo': etapas_protocolo
    })


@login_required
def lote_iatf_detalhes(request, propriedade_id, lote_id):
    """Detalhes do lote de IATF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not LoteIATF or not IATFIndividual:
        messages.error(request, 'Módulo IATF completo não está disponível.')
        return redirect('reproducao_dashboard', propriedade_id=propriedade.id)
    
    lote = get_object_or_404(LoteIATF, id=lote_id, propriedade=propriedade)
    
    # IATFs do lote
    iatfs = IATFIndividual.objects.filter(
        lote_iatf=lote
    ).select_related('animal_individual', 'protocolo').order_by('animal_individual__numero_brinco')
    
    etapas = lote.etapas.select_related(
        'responsavel_planejado', 'responsavel_execucao',
        'inseminador', 'touro_semen'
    ).order_by('dia_relativo', 'data_prevista')
    
    # Estatísticas do lote
    total_iatfs = iatfs.count()
    iatfs_realizadas = iatfs.filter(status='REALIZADA').count()
    prenhezes = iatfs.filter(resultado='PREMIDA').count()
    taxa_prenhez = Decimal('0.00')
    if iatfs_realizadas > 0:
        taxa_prenhez = (Decimal(str(prenhezes)) / Decimal(str(iatfs_realizadas))) * 100
    
    # Adicionar animais ao lote (AJAX)
    if request.method == 'POST' and request.POST.get('acao') == 'adicionar_animais':
        animais_ids = request.POST.getlist('animais')
        for animal_id in animais_ids:
            animal = get_object_or_404(AnimalIndividual, id=animal_id, propriedade=propriedade)
            iatf = IATFIndividual(
                propriedade=propriedade,
                lote_iatf=lote,
                animal_individual=animal,
                protocolo=lote.protocolo,
                data_inicio_protocolo=lote.data_inicio,
                touro_semen=lote.touro_semen,
                lote_semen=lote.lote_semen,
                status='PROTOCOLO_INICIADO',
                custo_protocolo=lote.custo_medicamentos / max(1, lote.numero_animais),
                custo_semen=lote.touro_semen.preco_dose if lote.touro_semen else Decimal('0'),
                custo_inseminacao=lote.custo_mao_obra / max(1, lote.numero_animais)
            )
            if lote.inseminador_padrao:
                iatf.inseminador = lote.inseminador_padrao
            if lote.estacao_monta:
                iatf.estacao_monta = lote.estacao_monta
            iatf.save()
        
        # Atualizar número de animais do lote
        lote.numero_animais = IATFIndividual.objects.filter(lote_iatf=lote).count()
        lote.save()
        
        messages.success(request, f'{len(animais_ids)} animal(is) adicionado(s) ao lote!')
        return redirect('lote_iatf_detalhes', propriedade_id=propriedade.id, lote_id=lote.id)
    
    # Animais disponíveis para adicionar
    animais_disponiveis = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO',
        sexo='F'
    ).exclude(
        id__in=iatfs.values_list('animal_individual_id', flat=True)
    ).order_by('numero_brinco')
    
    context = {
        'propriedade': propriedade,
        'lote': lote,
        'iatfs': iatfs,
        'total_iatfs': total_iatfs,
        'iatfs_realizadas': iatfs_realizadas,
        'prenhezes': prenhezes,
        'taxa_prenhez': taxa_prenhez,
        'animais_disponiveis': animais_disponiveis,
        'etapas': etapas,
    }
    
    return render(request, 'gestao_rural/lote_iatf_detalhes.html', context)


@login_required
def iatf_individual_novo(request, propriedade_id):
    """Registrar nova IATF individual"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not IATFIndividual or not ProtocoloIATF:
        messages.error(request, 'Módulo IATF completo não está disponível.')
        return redirect('reproducao_dashboard', propriedade_id=propriedade.id)
    
    animais = AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO',
        sexo='F'
    ).order_by('numero_brinco')
    protocolos = []
    if ProtocoloIATF:
        protocolos = ProtocoloIATF.objects.filter(
            Q(propriedade=propriedade) | Q(propriedade__isnull=True),
            ativo=True
        )
    touros = []
    if TouroSemen:
        touros = TouroSemen.objects.filter(ativo=True)
    lotes_semen = []
    if LoteSemen:
        lotes_semen = LoteSemen.objects.filter(
            propriedade=propriedade,
            status='ESTOQUE',
            doses_disponiveis__gt=0
        )
    estacoes = []
    if EstacaoMonta:
        estacoes = EstacaoMonta.objects.filter(propriedade=propriedade, ativa=True)
    lotes_iatf = []
    if LoteIATF:
        lotes_iatf = LoteIATF.objects.filter(propriedade=propriedade, status__in=['PLANEJADO', 'EM_ANDAMENTO'])
    
    if request.method == 'POST':
        iatf = IATFIndividual(propriedade=propriedade)
        iatf.animal_individual_id = request.POST.get('animal_individual')
        iatf.protocolo_id = request.POST.get('protocolo')
        iatf.data_inicio_protocolo = datetime.strptime(
            request.POST.get('data_inicio_protocolo'), '%Y-%m-%d'
        ).date()
        
        if request.POST.get('lote_iatf'):
            iatf.lote_iatf_id = request.POST.get('lote_iatf')
        if request.POST.get('estacao_monta'):
            iatf.estacao_monta_id = request.POST.get('estacao_monta')
        if request.POST.get('touro_semen'):
            iatf.touro_semen_id = request.POST.get('touro_semen')
        if request.POST.get('lote_semen'):
            iatf.lote_semen_id = request.POST.get('lote_semen')
            # Atualizar doses utilizadas do lote
            lote_semen = LoteSemen.objects.get(id=request.POST.get('lote_semen'))
            lote_semen.doses_utilizadas += 1
            lote_semen.save()
        
        iatf.numero_dose = request.POST.get('numero_dose', '')
        iatf.status = request.POST.get('status', 'PROTOCOLO_INICIADO')
        iatf.condicao_corporal = request.POST.get('condicao_corporal', '')
        if request.POST.get('peso_kg'):
            iatf.peso_kg = Decimal(request.POST.get('peso_kg'))
        if request.POST.get('dias_vazia'):
            iatf.dias_vazia = int(request.POST.get('dias_vazia'))
        
        iatf.custo_protocolo = Decimal(request.POST.get('custo_protocolo', 0))
        iatf.custo_semen = Decimal(request.POST.get('custo_semen', 0))
        iatf.custo_inseminacao = Decimal(request.POST.get('custo_inseminacao', 0))
        
        if request.POST.get('inseminador'):
            iatf.inseminador_id = request.POST.get('inseminador')
        if request.POST.get('veterinario'):
            iatf.veterinario_id = request.POST.get('veterinario')
        
        iatf.observacoes = request.POST.get('observacoes', '')
        
        try:
            iatf.save()
            messages.success(request, 'IATF registrada com sucesso!')
            return redirect('iatf_individual_detalhes', propriedade_id=propriedade.id, iatf_id=iatf.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar IATF: {str(e)}')
    
    return render(request, 'gestao_rural/iatf_individual_form.html', {
        'propriedade': propriedade,
        'animais': animais,
        'protocolos': protocolos,
        'touros': touros,
        'lotes_semen': lotes_semen,
        'estacoes': estacoes,
        'lotes_iatf': lotes_iatf
    })


@login_required
def iatf_individual_detalhes(request, propriedade_id, iatf_id):
    """Detalhes da IATF individual"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not IATFIndividual:
        messages.error(request, 'Módulo IATF completo não está disponível.')
        return redirect('reproducao_dashboard', propriedade_id=propriedade.id)
    
    iatf = get_object_or_404(IATFIndividual, id=iatf_id, propriedade=propriedade)
    
    # Aplicações de medicamentos
    aplicacoes = []
    if AplicacaoMedicamentoIATF:
        aplicacoes = AplicacaoMedicamentoIATF.objects.filter(
            iatf=iatf
        ).order_by('dia_protocolo', 'data_aplicacao')
    
    # Calcular próximas etapas
    proxima_etapa = None
    if iatf.status == 'PROGRAMADA':
        proxima_etapa = 'Dia 0 - Aplicar GnRH'
        proxima_data = iatf.data_dia_0_gnrh
    elif iatf.status == 'DIA_0_GNRH':
        proxima_etapa = 'Dia 7 - Aplicar PGF2α'
        proxima_data = iatf.data_dia_7_pgf2a
    elif iatf.status == 'DIA_7_PGF2A':
        proxima_etapa = 'Dia 9 - Aplicar GnRH Final'
        proxima_data = iatf.data_dia_9_gnrh
    elif iatf.status == 'DIA_9_GNRH':
        proxima_etapa = 'Dia 10 - Realizar IATF'
        proxima_data = iatf.data_iatf
    else:
        proxima_etapa = None
        proxima_data = None
    
    context = {
        'propriedade': propriedade,
        'iatf': iatf,
        'aplicacoes': aplicacoes,
        'proxima_etapa': proxima_etapa,
        'proxima_data': proxima_data,
    }
    
    return render(request, 'gestao_rural/iatf_individual_detalhes.html', context)


@login_required
def iatf_registrar_aplicacao(request, propriedade_id, iatf_id):
    """Registrar aplicação de medicamento"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    iatf = get_object_or_404(IATFIndividual, id=iatf_id, propriedade=propriedade)
    
    if request.method == 'POST':
        aplicacao = AplicacaoMedicamentoIATF(iatf=iatf)
        aplicacao.tipo_medicamento = request.POST.get('tipo_medicamento')
        aplicacao.nome_medicamento = request.POST.get('nome_medicamento')
        aplicacao.dosagem = request.POST.get('dosagem', '')
        aplicacao.data_aplicacao = datetime.strptime(
            request.POST.get('data_aplicacao'), '%Y-%m-%d'
        ).date()
        if request.POST.get('hora_aplicacao'):
            aplicacao.hora_aplicacao = datetime.strptime(
                request.POST.get('hora_aplicacao'), '%H:%M'
            ).time()
        aplicacao.dia_protocolo = int(request.POST.get('dia_protocolo', 0))
        aplicacao.aplicado_por = request.user
        aplicacao.aplicado_corretamente = request.POST.get('aplicado_corretamente') == 'on'
        aplicacao.observacoes = request.POST.get('observacoes', '')
        
        try:
            aplicacao.save()
            
            # Atualizar status da IATF baseado na aplicação
            if aplicacao.dia_protocolo == 0:
                iatf.status = 'DIA_0_GNRH'
                iatf.data_dia_0_gnrh = aplicacao.data_aplicacao
            elif aplicacao.dia_protocolo == 7:
                iatf.status = 'DIA_7_PGF2A'
                iatf.data_dia_7_pgf2a = aplicacao.data_aplicacao
            elif aplicacao.dia_protocolo == 9:
                iatf.status = 'DIA_9_GNRH'
                iatf.data_dia_9_gnrh = aplicacao.data_aplicacao
            
            iatf.save()
            
            messages.success(request, 'Aplicação registrada com sucesso!')
            return redirect('iatf_individual_detalhes', propriedade_id=propriedade.id, iatf_id=iatf.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar aplicação: {str(e)}')
    
    return render(request, 'gestao_rural/iatf_aplicacao_form.html', {
        'propriedade': propriedade,
        'iatf': iatf
    })


@login_required
def iatf_registrar_inseminacao(request, propriedade_id, iatf_id):
    """Registrar inseminação realizada"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    iatf = get_object_or_404(IATFIndividual, id=iatf_id, propriedade=propriedade)
    
    if request.method == 'POST':
        iatf.data_iatf_realizada = datetime.strptime(
            request.POST.get('data_iatf_realizada'), '%Y-%m-%d'
        ).date()
        if request.POST.get('hora_iatf'):
            iatf.hora_iatf = datetime.strptime(
                request.POST.get('hora_iatf'), '%H:%M'
            ).time()
        iatf.status = 'REALIZADA'
        if request.POST.get('inseminador'):
            iatf.inseminador_id = request.POST.get('inseminador')
        iatf.observacoes_protocolo = request.POST.get('observacoes', '')
        
        try:
            iatf.save()
            
            # Atualizar lote
            if iatf.lote_iatf:
                lote = iatf.lote_iatf
                lote.animais_inseminados = IATFIndividual.objects.filter(
                    lote_iatf=lote,
                    status='REALIZADA'
                ).count()
                if lote.animais_inseminados >= lote.numero_animais:
                    lote.status = 'CONCLUIDO'
                else:
                    lote.status = 'EM_ANDAMENTO'
                lote.save()
            
            messages.success(request, 'Inseminação registrada com sucesso!')
            return redirect('iatf_individual_detalhes', propriedade_id=propriedade.id, iatf_id=iatf.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar inseminação: {str(e)}')
    
    return render(request, 'gestao_rural/iatf_inseminacao_form.html', {
        'propriedade': propriedade,
        'iatf': iatf
    })


@login_required
def iatf_registrar_diagnostico(request, propriedade_id, iatf_id):
    """Registrar diagnóstico de prenhez"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    iatf = get_object_or_404(IATFIndividual, id=iatf_id, propriedade=propriedade)
    
    if request.method == 'POST':
        iatf.data_diagnostico = datetime.strptime(
            request.POST.get('data_diagnostico'), '%Y-%m-%d'
        ).date()
        iatf.resultado = request.POST.get('resultado')
        if request.POST.get('dias_gestacao_diagnostico'):
            iatf.dias_gestacao_diagnostico = int(request.POST.get('dias_gestacao_diagnostico'))
        iatf.metodo_diagnostico = request.POST.get('metodo_diagnostico', '')
        if request.POST.get('diagnostico_por'):
            iatf.diagnostico_por_id = request.POST.get('diagnostico_por')
        iatf.observacoes_diagnostico = request.POST.get('observacoes', '')
        
        try:
            iatf.save()
            
            # Atualizar lote
            if iatf.lote_iatf:
                lote = iatf.lote_iatf
                lote.numero_prenhezes = IATFIndividual.objects.filter(
                    lote_iatf=lote,
                    resultado='PREMIDA'
                ).count()
                lote.save()
            
            # Criar nascimento se prenha
            if iatf.resultado == 'PREMIDA':
                from .models_reproducao import Nascimento
                # Calcular data estimada de nascimento (280 dias)
                data_nascimento_estimada = iatf.data_iatf + timedelta(days=280)
                # O nascimento será criado quando o parto acontecer
            
            messages.success(request, 'Diagnóstico registrado com sucesso!')
            return redirect('iatf_individual_detalhes', propriedade_id=propriedade.id, iatf_id=iatf.id)
        except Exception as e:
            messages.error(request, f'Erro ao registrar diagnóstico: {str(e)}')
    
    return render(request, 'gestao_rural/iatf_diagnostico_form.html', {
        'propriedade': propriedade,
        'iatf': iatf
    })


@login_required
def lotes_iatf_lista(request, propriedade_id):
    """Lista de lotes de IATF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    lotes = LoteIATF.objects.filter(propriedade=propriedade)
    
    if status_filter:
        lotes = lotes.filter(status=status_filter)
    if search:
        lotes = lotes.filter(nome_lote__icontains=search)
    
    lotes = lotes.select_related('protocolo', 'touro_semen').order_by('-data_inicio')
    
    context = {
        'propriedade': propriedade,
        'lotes': lotes,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'gestao_rural/lotes_iatf_lista.html', context)


@login_required
def iatfs_lista(request, propriedade_id):
    """Lista de IATFs individuais"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    status_filter = request.GET.get('status', '')
    resultado_filter = request.GET.get('resultado', '')
    search = request.GET.get('search', '')
    
    iatfs = IATFIndividual.objects.filter(propriedade=propriedade)
    
    if status_filter:
        iatfs = iatfs.filter(status=status_filter)
    if resultado_filter:
        iatfs = iatfs.filter(resultado=resultado_filter)
    if search:
        iatfs = iatfs.filter(animal_individual__numero_brinco__icontains=search)
    
    iatfs = iatfs.select_related(
        'animal_individual', 'protocolo', 'touro_semen', 'lote_iatf'
    ).order_by('-data_inicio_protocolo')
    
    context = {
        'propriedade': propriedade,
        'iatfs': iatfs,
        'status_filter': status_filter,
        'resultado_filter': resultado_filter,
        'search': search,
    }
    
    return render(request, 'gestao_rural/iatfs_lista.html', context)


@login_required
def protocolos_iatf_lista(request, propriedade_id):
    """Lista de protocolos IATF"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    protocolos = ProtocoloIATF.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True),
        ativo=True
    ).annotate(
        total_uso=Count('iatfs')
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'protocolos': protocolos,
    }
    
    return render(request, 'gestao_rural/protocolos_iatf_lista.html', context)


@login_required
def touros_semen_lista(request, propriedade_id):
    """Lista de touros para sêmen"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    touros = TouroSemen.objects.filter(ativo=True).annotate(
        total_uso=Count('iatfs')
    ).order_by('nome_touro')
    
    context = {
        'propriedade': propriedade,
        'touros': touros,
    }
    
    return render(request, 'gestao_rural/touros_semen_lista.html', context)


@login_required
def lotes_semen_lista(request, propriedade_id):
    """Lista de lotes de sêmen"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    status_filter = request.GET.get('status', '')
    
    lotes = LoteSemen.objects.filter(propriedade=propriedade)
    
    if status_filter:
        lotes = lotes.filter(status=status_filter)
    
    lotes = lotes.select_related('touro').order_by('-data_aquisicao')
    
    context = {
        'propriedade': propriedade,
        'lotes': lotes,
        'status_filter': status_filter,
    }
    
    return render(request, 'gestao_rural/lotes_semen_lista.html', context)


@login_required
def iatf_relatorio(request, propriedade_id):
    """Relatório completo de IATF com filtros e visualização"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not IATFIndividual:
        messages.warning(request, 'Módulo IATF completo não está disponível.')
        return redirect('iatf_dashboard', propriedade_id=propriedade.id)
    
    # Importar função de coleta de dados
    from .relatorios_iatf import coletar_dados_iatf, IATFModuloIndisponivel
    
    # Obter filtros da requisição
    filtros = {
        'data_inicio': request.GET.get('data_inicio'),
        'data_final': request.GET.get('data_final'),
        'diagnostico_ate': request.GET.get('diagnostico_ate'),
        'lote_id': request.GET.get('lote_id'),
        'resultado': request.GET.get('resultado'),
        'incluir_sem_diagnostico': request.GET.get('incluir_sem_diagnostico') == 'on',
    }
    
    # Coletar dados
    try:
        dados = coletar_dados_iatf(propriedade, filtros)
    except IATFModuloIndisponivel as e:
        messages.error(request, str(e))
        return redirect('iatf_dashboard', propriedade_id=propriedade.id)
    
    # Obter lotes para o filtro
    lotes = LoteIATF.objects.filter(propriedade=propriedade).order_by('-data_inicio')
    
    # Resultado choices para o filtro
    resultado_choices = dados.get('resultado_choices', [])
    
    context = {
        'propriedade': propriedade,
        'dados': dados,
        'lotes': lotes,
        'resultado_choices': resultado_choices,
        'filtros_aplicados': dados['filtros_aplicados'],
    }
    
    return render(request, 'gestao_rural/iatf_relatorio.html', context)


@login_required
def iatf_relatorio_etapas(request, propriedade_id):
    """Relatório de IATF por etapas - Cabeçalho com fazenda e lotes, tabela com colunas D0, D8, D10, Diagnóstico"""
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not LoteIATF:
        messages.warning(request, 'Módulo IATF completo não está disponível.')
        return redirect('iatf_dashboard', propriedade_id=propriedade.id)
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    lote_id = request.GET.get('lote_id')
    
    # Buscar lotes
    lotes_query = LoteIATF.objects.filter(propriedade=propriedade)
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            lotes_query = lotes_query.filter(data_inicio__gte=data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            lotes_query = lotes_query.filter(data_inicio__lte=data_fim_obj)
        except ValueError:
            pass
    
    if lote_id:
        try:
            lotes_query = lotes_query.filter(id=int(lote_id))
        except ValueError:
            pass
    
    lotes = lotes_query.select_related('protocolo', 'touro_semen', 'lote_semen', 'inseminador_padrao').prefetch_related('etapas').order_by('-data_inicio')
    
    # Preparar dados para a tabela
    dados_tabela = []
    for lote in lotes:
        # Buscar etapas do lote
        etapas = lote.etapas.all().order_by('dia_relativo')
        
        # Organizar etapas por código
        etapa_d0 = etapas.filter(dia_relativo=0).first()
        etapa_d8 = etapas.filter(dia_relativo__gte=7, dia_relativo__lte=9).first()  # Pode ser D7, D8 ou D9
        etapa_d10 = etapas.filter(dia_relativo__gte=9, dia_relativo__lte=11).first()  # Pode ser D9, D10 ou D11
        
        # Buscar diagnósticos (IATFs individuais com diagnóstico)
        if IATFIndividual:
            iatfs_lote = IATFIndividual.objects.filter(
                lote_iatf=lote,
                data_diagnostico__isnull=False
            ).order_by('-data_diagnostico')
            
            # Agrupar diagnósticos
            diagnosticos = []
            for iatf in iatfs_lote:
                diagnosticos.append({
                    'data': iatf.data_diagnostico,
                    'resultado': iatf.get_resultado_display(),
                    'dias_gestacao': iatf.dias_gestacao_diagnostico,
                    'veterinario': iatf.veterinario.get_full_name() if iatf.veterinario else iatf.veterinario.username if iatf.veterinario else '-'
                })
        else:
            diagnosticos = []
        
        # Buscar IATFs individuais para contar
        if IATFIndividual:
            total_iatfs = IATFIndividual.objects.filter(lote_iatf=lote).count()
            prenhezes = IATFIndividual.objects.filter(lote_iatf=lote, resultado='PREMIDA').count()
        else:
            total_iatfs = lote.numero_animais
            prenhezes = lote.numero_prenhezes
        
        dados_tabela.append({
            'lote': lote,
            'etapa_d0': etapa_d0,
            'etapa_d8': etapa_d8,
            'etapa_d10': etapa_d10,
            'diagnosticos': diagnosticos,
            'total_iatfs': total_iatfs,
            'prenhezes': prenhezes,
            'taxa_prenhez': (prenhezes / total_iatfs * 100) if total_iatfs > 0 else 0
        })
    
    # Estatísticas gerais
    total_lotes = lotes.count()
    total_animais = sum(l.numero_animais for l in lotes)
    total_prenhezes = sum(d['prenhezes'] for d in dados_tabela)
    taxa_prenhez_geral = (total_prenhezes / total_animais * 100) if total_animais > 0 else 0
    
    # Todos os lotes para o filtro
    todos_lotes = LoteIATF.objects.filter(propriedade=propriedade).order_by('-data_inicio')
    
    context = {
        'propriedade': propriedade,
        'lotes': lotes,
        'dados_tabela': dados_tabela,
        'todos_lotes': todos_lotes,
        'total_lotes': total_lotes,
        'total_animais': total_animais,
        'total_prenhezes': total_prenhezes,
        'taxa_prenhez_geral': taxa_prenhez_geral,
        'filtros': {
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'lote_id': lote_id
        }
    }
    
    return render(request, 'gestao_rural/iatf_relatorio_etapas.html', context)


@login_required
def iatf_relatorio_etapas_pdf(request, propriedade_id):
    """Gera relatório de IATF por etapas em PDF formato horizontal (planilha)"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from datetime import datetime
    
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    if not LoteIATF:
        messages.warning(request, 'Módulo IATF completo não está disponível.')
        return redirect('iatf_dashboard', propriedade_id=propriedade.id)
    
    # Filtros (mesmos da view HTML)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    lote_id = request.GET.get('lote_id')
    
    # Buscar lotes (mesma lógica da view HTML)
    lotes_query = LoteIATF.objects.filter(propriedade=propriedade)
    
    if data_inicio:
        try:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            lotes_query = lotes_query.filter(data_inicio__gte=data_inicio_obj)
        except ValueError:
            pass
    
    if data_fim:
        try:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            lotes_query = lotes_query.filter(data_inicio__lte=data_fim_obj)
        except ValueError:
            pass
    
    if lote_id:
        try:
            lotes_query = lotes_query.filter(id=int(lote_id))
        except ValueError:
            pass
    
    lotes = lotes_query.select_related('protocolo', 'touro_semen', 'lote_semen', 'inseminador_padrao').prefetch_related('etapas').order_by('-data_inicio')
    
    # Preparar dados para a tabela (mesma lógica da view HTML)
    dados_tabela = []
    for lote in lotes:
        etapas = lote.etapas.all().order_by('dia_relativo')
        etapa_d0 = etapas.filter(dia_relativo=0).first()
        etapa_d8 = etapas.filter(dia_relativo__gte=7, dia_relativo__lte=9).first()
        etapa_d10 = etapas.filter(dia_relativo__gte=9, dia_relativo__lte=11).first()
        
        if IATFIndividual:
            iatfs_lote = IATFIndividual.objects.filter(
                lote_iatf=lote,
                data_diagnostico__isnull=False
            ).order_by('-data_diagnostico')
            diagnosticos = []
            for iatf in iatfs_lote:
                diagnosticos.append({
                    'data': iatf.data_diagnostico,
                    'resultado': iatf.get_resultado_display(),
                    'dias_gestacao': iatf.dias_gestacao_diagnostico,
                    'veterinario': iatf.veterinario.get_full_name() if iatf.veterinario else (iatf.veterinario.username if iatf.veterinario else '-')
                })
            total_iatfs = IATFIndividual.objects.filter(lote_iatf=lote).count()
            prenhezes = IATFIndividual.objects.filter(lote_iatf=lote, resultado='PREMIDA').count()
        else:
            diagnosticos = []
            total_iatfs = lote.numero_animais
            prenhezes = lote.numero_prenhezes
        
        dados_tabela.append({
            'lote': lote,
            'etapa_d0': etapa_d0,
            'etapa_d8': etapa_d8,
            'etapa_d10': etapa_d10,
            'diagnosticos': diagnosticos,
            'total_iatfs': total_iatfs,
            'prenhezes': prenhezes,
            'taxa_prenhez': (prenhezes / total_iatfs * 100) if total_iatfs > 0 else 0
        })
    
    # Estatísticas gerais
    total_lotes = lotes.count()
    total_animais = sum(l.numero_animais for l in lotes)
    total_prenhezes = sum(d['prenhezes'] for d in dados_tabela)
    taxa_prenhez_geral = (total_prenhezes / total_animais * 100) if total_animais > 0 else 0
    
    # Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    data_atual = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="relatorio_iatf_etapas_{propriedade.id}_{data_atual}.pdf"'
    
    # Criar documento PDF em paisagem (horizontal)
    doc = SimpleDocTemplate(response, pagesize=landscape(A4), 
                           leftMargin=1*cm, rightMargin=1*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a5f'),
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666')
    )
    
    # Cabeçalho
    story.append(Paragraph("RELATÓRIO DE IATF POR ETAPAS", title_style))
    story.append(Paragraph(f"{propriedade.nome_propriedade}", subtitle_style))
    if propriedade.municipio:
        localizacao = f"{propriedade.municipio}"
        if propriedade.uf:
            localizacao += f", {propriedade.uf}"
        story.append(Paragraph(localizacao, styles['Normal']))
    story.append(Paragraph(f"Data do Relatório: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Resumo
    resumo_data = [
        ['Total de Lotes', 'Total de Animais', 'Total de Prenhezes', 'Taxa de Prenhez Geral'],
        [str(total_lotes), str(total_animais), str(total_prenhezes), f"{taxa_prenhez_geral:.1f}%"]
    ]
    resumo_table = Table(resumo_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#E7E6E6')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 11),
        ('TOPPADDING', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(resumo_table)
    story.append(Spacer(1, 20))
    
    # Preparar dados da tabela principal
    table_data = []
    
    # Cabeçalho da tabela
    header = [
        'Lote', 'Protocolo', 'Status', 'Data\nInício', 'Data\nIATF', 'Animais',
        'D0 - Data', 'D0 - Hora', 'D0 - Medic.', 'D0 - Resp.', 'D0 - Status',
        'D8 - Data', 'D8 - Hora', 'D8 - Medic.', 'D8 - Resp.', 'D8 - Status',
        'D10 - Data', 'D10 - Hora', 'D10 - Medic.', 'D10 - Insem.', 'D10 - Status',
        'Diag. - Data', 'Diag. - Result.', 'Diag. - Gest.', 'Diag. - Vet.',
        'Prenh.', 'Total', 'Taxa %'
    ]
    table_data.append(header)
    
    # Dados das linhas
    for item in dados_tabela:
        lote = item['lote']
        etapa_d0 = item['etapa_d0']
        etapa_d8 = item['etapa_d8']
        etapa_d10 = item['etapa_d10']
        diagnosticos = item['diagnosticos']
        
        # Formatar diagnósticos
        diag_data = '; '.join([d['data'].strftime('%d/%m/%Y') for d in diagnosticos]) if diagnosticos else '-'
        diag_result = '; '.join([d['resultado'] for d in diagnosticos]) if diagnosticos else '-'
        diag_gest = '; '.join([str(d['dias_gestacao']) if d['dias_gestacao'] else '-' for d in diagnosticos]) if diagnosticos else '-'
        diag_vet = '; '.join([d['veterinario'] for d in diagnosticos]) if diagnosticos else '-'
        
        # Formatar inseminador D10
        inseminador_d10 = '-'
        if etapa_d10:
            if etapa_d10.inseminador:
                inseminador_d10 = etapa_d10.inseminador.get_full_name()[:10] if etapa_d10.inseminador.get_full_name() else etapa_d10.inseminador.username[:10]
            elif etapa_d10.responsavel_planejado:
                inseminador_d10 = etapa_d10.responsavel_planejado.get_full_name()[:10] if etapa_d10.responsavel_planejado.get_full_name() else etapa_d10.responsavel_planejado.username[:10]
        
        row = [
            lote.nome_lote[:20] if len(lote.nome_lote) > 20 else lote.nome_lote,
            (lote.protocolo.nome[:15] if lote.protocolo else '-')[:15],
            lote.get_status_display()[:10],
            lote.data_inicio.strftime('%d/%m/%Y') if lote.data_inicio else '-',
            lote.data_iatf.strftime('%d/%m/%Y') if lote.data_iatf else '-',
            str(lote.numero_animais),
            etapa_d0.data_prevista.strftime('%d/%m/%Y') if etapa_d0 and etapa_d0.data_prevista else '-',
            etapa_d0.hora_prevista.strftime('%H:%M') if etapa_d0 and etapa_d0.hora_prevista else '-',
            (etapa_d0.medicamento_planejado[:12] if etapa_d0 and etapa_d0.medicamento_planejado else '-')[:12],
            (etapa_d0.responsavel_planejado.get_full_name()[:10] if etapa_d0 and etapa_d0.responsavel_planejado else '-')[:10],
            etapa_d0.get_status_display()[:8] if etapa_d0 else '-',
            etapa_d8.data_prevista.strftime('%d/%m/%Y') if etapa_d8 and etapa_d8.data_prevista else '-',
            etapa_d8.hora_prevista.strftime('%H:%M') if etapa_d8 and etapa_d8.hora_prevista else '-',
            (etapa_d8.medicamento_planejado[:12] if etapa_d8 and etapa_d8.medicamento_planejado else '-')[:12],
            (etapa_d8.responsavel_planejado.get_full_name()[:10] if etapa_d8 and etapa_d8.responsavel_planejado else '-')[:10],
            etapa_d8.get_status_display()[:8] if etapa_d8 else '-',
            etapa_d10.data_prevista.strftime('%d/%m/%Y') if etapa_d10 and etapa_d10.data_prevista else '-',
            etapa_d10.hora_prevista.strftime('%H:%M') if etapa_d10 and etapa_d10.hora_prevista else '-',
            (etapa_d10.medicamento_planejado[:12] if etapa_d10 and etapa_d10.medicamento_planejado else '-')[:12],
            inseminador_d10,
            etapa_d10.get_status_display()[:8] if etapa_d10 else '-',
            diag_data[:15],
            diag_result[:15],
            diag_gest[:10],
            diag_vet[:15],
            str(item['prenhezes']),
            str(item['total_iatfs']),
            f"{item['taxa_prenhez']:.1f}%"
        ]
        table_data.append(row)
    
    # Criar tabela
    # Calcular larguras das colunas (total ~27cm em landscape A4)
    col_widths = [
        2.5*cm, 2.0*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.0*cm,  # Lote, Protocolo, Status, Datas, Animais
        1.5*cm, 1.0*cm, 1.5*cm, 1.5*cm, 1.2*cm,  # D0 (5 colunas)
        1.5*cm, 1.0*cm, 1.5*cm, 1.5*cm, 1.2*cm,  # D8 (5 colunas)
        1.5*cm, 1.0*cm, 1.5*cm, 1.5*cm, 1.2*cm,  # D10 (5 colunas)
        1.5*cm, 1.5*cm, 1.2*cm, 1.5*cm,  # Diagnóstico (4 colunas)
        1.0*cm, 1.0*cm, 1.2*cm  # Resultados (3 colunas)
    ]
    
    main_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilo da tabela
    table_style = TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Destaque para taxa de prenhez
        ('TEXTCOLOR', (26, 1), (26, -1), colors.HexColor('#198754')),
        ('FONTNAME', (26, 1), (26, -1), 'Helvetica-Bold'),
    ])
    
    main_table.setStyle(table_style)
    story.append(main_table)
    
    # Rodapé
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<i>Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</i>", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                        alignment=TA_CENTER, textColor=colors.grey)))
    
    # Construir PDF
    doc.build(story)
    
    return response

