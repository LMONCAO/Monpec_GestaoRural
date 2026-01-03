# -*- coding: utf-8 -*-
"""
Serviço para cálculo automático do DRE baseado em lançamentos financeiros
e legislação contábil para produtor rural pessoa física
"""

from decimal import Decimal
from datetime import date
from django.db.models import Sum, Q
from django.utils import timezone

from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira


def calcular_dre_automatico(propriedade, ano):
    """
    Calcula automaticamente os valores do DRE baseado nos lançamentos financeiros
    e na legislação contábil para produtor rural pessoa física.
    
    Retorna um dicionário com todos os valores calculados.
    """
    from .models_financeiro import ReceitaAnual
    
    data_inicio = date(ano, 1, 1)
    data_fim = date(ano, 12, 31)
    
    # Buscar todos os lançamentos quitados do ano
    lancamentos = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        data_competencia__year=ano,
        status=LancamentoFinanceiro.STATUS_QUITADO
    ).select_related('categoria')
    
    # Contar lançamentos para debug
    total_lancamentos = lancamentos.count()
    total_despesas_lanc = lancamentos.filter(tipo=CategoriaFinanceira.TIPO_DESPESA).count()
    total_receitas_lanc = lancamentos.filter(tipo=CategoriaFinanceira.TIPO_RECEITA).count()
    
    # Receita bruta: soma de todas as receitas
    receita_bruta_calculada = lancamentos.filter(
        tipo=CategoriaFinanceira.TIPO_RECEITA
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    # Buscar receita anual existente para usar como base
    receita_anual = ReceitaAnual.objects.filter(
        propriedade=propriedade,
        ano=ano
    ).first()
    
    if receita_anual and receita_anual.valor_receita > 0:
        receita_bruta = receita_anual.valor_receita
    else:
        # Se não há receita anual cadastrada, usar a soma dos lançamentos
        receita_bruta = receita_bruta_calculada
    
    # Mapeamento de categorias para deduções e custos
    # Palavras-chave para identificar categorias
    palavras_icms = ['icms', 'imposto', 'tributo', 'taxa']
    palavras_funviral = ['funviral', 'funrural']
    palavras_outros_impostos = ['pis', 'cofins', 'ipi', 'iss']
    palavras_devolucoes = ['devolução', 'devolucao', 'retorno']
    palavras_abatimentos = ['abatimento', 'desconto', 'bonificação']
    
    # Custos de produção (CPV)
    palavras_cpv = [
        'compra', 'aquisição', 'aquisiçao', 'custo', 'gasto',
        'ração', 'racao', 'suplemento', 'medicamento', 'vacina',
        'mão de obra', 'mao de obra', 'salário', 'salario',
        'combustível', 'combustivel', 'energia', 'água', 'agua',
        'manutenção', 'manutencao', 'reparo', 'conserto',
        'insumo', 'fertilizante', 'calcário', 'calcareo',
        'semente', 'pastagem', 'cerca', 'bebedouro', 'cocho'
    ]
    
    # Depreciação
    palavras_depreciacao = ['depreciação', 'depreciacao', 'amortização', 'amortizacao']
    
    # Despesas financeiras
    palavras_despesas_financeiras = [
        'juro', 'taxa bancária', 'taxa bancaria', 'tarifa',
        'empréstimo', 'emprestimo', 'financiamento', 'cheque especial',
        'cartão de crédito', 'cartao de credito', 'multa', 'atraso'
    ]
    
    # Receitas financeiras
    palavras_receitas_financeiras = [
        'rendimento', 'aplicação', 'aplicacao', 'investimento',
        'poupança', 'poupanca', 'cdb', 'tesouro', 'dividendo'
    ]
    
    # Impostos sobre o lucro
    palavras_ir = ['imposto de renda', 'irpj', 'ir pf']
    palavras_csll = ['csll', 'contribuição social', 'contribuicao social']
    
    # Inicializar valores
    icms_vendas = Decimal('0.00')
    funviral_vendas = Decimal('0.00')
    outros_impostos_vendas = Decimal('0.00')
    devolucoes_vendas = Decimal('0.00')
    abatimentos_vendas = Decimal('0.00')
    custo_produtos_vendidos = Decimal('0.00')
    depreciacao_amortizacao = Decimal('0.00')
    despesas_financeiras = Decimal('0.00')
    receitas_financeiras = Decimal('0.00')
    csll = Decimal('0.00')
    irpj = Decimal('0.00')
    
    # Processar lançamentos de despesas
    despesas = lancamentos.filter(tipo=CategoriaFinanceira.TIPO_DESPESA)
    
    # Categorias administrativas que NÃO entram no CPV
    palavras_administrativas = [
        'administrativo', 'escritório', 'escritorio', 'contábil', 'contabil',
        'advogado', 'advocacia', 'jurídico', 'juridico', 'consultoria',
        'marketing', 'publicidade', 'propaganda', 'comercial', 'vendas'
    ]
    
    # Contador para debug
    despesas_processadas = 0
    despesas_cpv = 0
    
    for lancamento in despesas:
        categoria_nome = lancamento.categoria.nome.lower()
        descricao = lancamento.descricao.lower() if lancamento.descricao else ''
        texto_busca = f"{categoria_nome} {descricao}".lower()
        valor = lancamento.valor
        despesas_processadas += 1
        
        # Verificar primeiro por impostos específicos
        if 'funviral' in texto_busca or 'funrural' in texto_busca:
            funviral_vendas += valor
        elif 'icms' in texto_busca and ('venda' in texto_busca or 'sobre' in texto_busca):
            icms_vendas += valor
        elif any(palavra in texto_busca for palavra in palavras_outros_impostos):
            outros_impostos_vendas += valor
        # Devoluções e abatimentos
        elif any(palavra in texto_busca for palavra in palavras_devolucoes):
            devolucoes_vendas += valor
        elif any(palavra in texto_busca for palavra in palavras_abatimentos):
            abatimentos_vendas += valor
        # Depreciação
        elif any(palavra in texto_busca for palavra in palavras_depreciacao):
            depreciacao_amortizacao += valor
        # Despesas financeiras
        elif any(palavra in texto_busca for palavra in palavras_despesas_financeiras):
            despesas_financeiras += valor
        # Impostos sobre o lucro
        elif any(palavra in texto_busca for palavra in palavras_csll):
            csll += valor
        elif any(palavra in texto_busca for palavra in palavras_ir):
            irpj += valor
        # CPV - TODAS as outras despesas são custos de produção
        # Exceto despesas administrativas e financeiras
        else:
            # Se não for administrativa ou financeira, é custo de produção
            is_administrativa = any(palavra in texto_busca for palavra in palavras_administrativas)
            is_financeira = any(palavra in texto_busca for palavra in palavras_despesas_financeiras)
            
            if not is_administrativa and not is_financeira:
                # Todas as despesas operacionais são custos de produção
                custo_produtos_vendidos += valor
                despesas_cpv += 1
    
    # Processar lançamentos de receitas
    receitas = lancamentos.filter(tipo=CategoriaFinanceira.TIPO_RECEITA)
    
    for lancamento in receitas:
        categoria_nome = lancamento.categoria.nome.lower()
        descricao = lancamento.descricao.lower() if lancamento.descricao else ''
        texto_busca = f"{categoria_nome} {descricao}".lower()
        valor = lancamento.valor
        
        # Receitas financeiras
        if any(palavra in texto_busca for palavra in palavras_receitas_financeiras):
            receitas_financeiras += valor
    
    # Calcular impostos sobre vendas baseado na receita bruta
    # Para produtor rural pessoa física, geralmente:
    # - ICMS: 0% ou reduzido (depende do estado e produto)
    # - Funviral: 0,5% a 1,5% sobre receitas (depende do estado)
    # - PIS/COFINS: geralmente isento para pessoa física
    
    # Se não houver lançamentos específicos, calcular percentuais padrão
    if icms_vendas == 0 and receita_bruta > 0:
        # ICMS geralmente 0% para produtos rurais, mas pode variar
        # Vamos deixar 0% por padrão
        icms_vendas = Decimal('0.00')
    
    if funviral_vendas == 0 and receita_bruta > 0:
        # Funviral: 1% sobre receitas brutas (Lei 8.212/91, art. 22, § 3º)
        # Aplicável para produtor rural pessoa física
        funviral_vendas = (receita_bruta * Decimal('0.01')).quantize(Decimal('0.01'))  # 1% com 2 casas decimais
    
    if outros_impostos_vendas == 0 and receita_bruta > 0:
        # PIS/COFINS: geralmente isento para pessoa física
        outros_impostos_vendas = Decimal('0.00')
    
    # Calcular impostos sobre o lucro (se não houver lançamentos específicos)
    # Para pessoa física, o cálculo é diferente, mas vamos estimar
    receita_liquida_estimada = receita_bruta - icms_vendas - funviral_vendas - outros_impostos_vendas
    cpv_total = custo_produtos_vendidos
    lucro_bruto_estimado = receita_liquida_estimada - cpv_total
    
    # Buscar despesas operacionais configuradas
    from .models_financeiro import DespesaConfigurada
    despesas_configuradas = DespesaConfigurada.objects.filter(
        propriedade=propriedade,
        ativo=True
    )
    
    total_despesas_operacionais = Decimal('0.00')
    for despesa_config in despesas_configuradas:
        total_despesas_operacionais += despesa_config.calcular_valor_anual(receita_bruta)
    
    resultado_antes_ir_estimado = lucro_bruto_estimado - total_despesas_operacionais + (receitas_financeiras - despesas_financeiras)
    
    # Calcular IR e CSLL se não houver lançamentos específicos
    # Para pessoa física (produtor rural), o IR é calculado na declaração anual (DIRPF)
    # CSLL não se aplica a pessoa física (apenas para pessoa jurídica)
    # Os valores devem ser preenchidos manualmente após a declaração de imposto de renda
    if csll == 0:
        # CSLL não se aplica a pessoa física
        csll = Decimal('0.00')
    
    if irpj == 0:
        # IR: para pessoa física, calculado na DIRPF
        # Deixar 0 para preenchimento manual após declaração
        irpj = Decimal('0.00')
    
    # Garantir que todos os valores tenham apenas 2 casas decimais
    return {
        'receita_bruta': receita_bruta.quantize(Decimal('0.01')),
        'icms_vendas': icms_vendas.quantize(Decimal('0.01')),
        'funviral_vendas': funviral_vendas.quantize(Decimal('0.01')),
        'outros_impostos_vendas': outros_impostos_vendas.quantize(Decimal('0.01')),
        'devolucoes_vendas': devolucoes_vendas.quantize(Decimal('0.01')),
        'abatimentos_vendas': abatimentos_vendas.quantize(Decimal('0.01')),
        'custo_produtos_vendidos': custo_produtos_vendidos.quantize(Decimal('0.01')),
        'depreciacao_amortizacao': depreciacao_amortizacao.quantize(Decimal('0.01')),
        'despesas_financeiras': despesas_financeiras.quantize(Decimal('0.01')),
        'receitas_financeiras': receitas_financeiras.quantize(Decimal('0.01')),
        'csll': csll.quantize(Decimal('0.01')),
        'irpj': irpj.quantize(Decimal('0.01')),
    }


def preencher_receita_anual_automatico(propriedade, ano):
    """
    Preenche automaticamente uma ReceitaAnual com valores calculados
    baseado nos lançamentos financeiros.
    """
    from .models_financeiro import ReceitaAnual
    
    valores = calcular_dre_automatico(propriedade, ano)
    
    receita_anual, created = ReceitaAnual.objects.get_or_create(
        propriedade=propriedade,
        ano=ano,
        defaults={
            'valor_receita': valores['receita_bruta'],
            'icms_vendas': valores['icms_vendas'],
            'funviral_vendas': valores['funviral_vendas'],
            'outros_impostos_vendas': valores['outros_impostos_vendas'],
            'devolucoes_vendas': valores['devolucoes_vendas'],
            'abatimentos_vendas': valores['abatimentos_vendas'],
            'custo_produtos_vendidos': valores['custo_produtos_vendidos'],
            'depreciacao_amortizacao': valores['depreciacao_amortizacao'],
            'despesas_financeiras': valores['despesas_financeiras'],
            'receitas_financeiras': valores['receitas_financeiras'],
            'csll': valores['csll'],
            'irpj': valores['irpj'],
        }
    )
    
    if not created:
        # Atualizar valores existentes (mas preservar se já foram preenchidos manualmente)
        # Só atualiza se o valor atual for 0
        if receita_anual.icms_vendas == 0:
            receita_anual.icms_vendas = valores['icms_vendas']
        if receita_anual.funviral_vendas == 0:
            receita_anual.funviral_vendas = valores['funviral_vendas']
        if receita_anual.outros_impostos_vendas == 0:
            receita_anual.outros_impostos_vendas = valores['outros_impostos_vendas']
        if receita_anual.devolucoes_vendas == 0:
            receita_anual.devolucoes_vendas = valores['devolucoes_vendas']
        if receita_anual.abatimentos_vendas == 0:
            receita_anual.abatimentos_vendas = valores['abatimentos_vendas']
        if receita_anual.custo_produtos_vendidos == 0:
            receita_anual.custo_produtos_vendidos = valores['custo_produtos_vendidos']
        if receita_anual.depreciacao_amortizacao == 0:
            receita_anual.depreciacao_amortizacao = valores['depreciacao_amortizacao']
        if receita_anual.despesas_financeiras == 0:
            receita_anual.despesas_financeiras = valores['despesas_financeiras']
        if receita_anual.receitas_financeiras == 0:
            receita_anual.receitas_financeiras = valores['receitas_financeiras']
        if receita_anual.csll == 0:
            receita_anual.csll = valores['csll']
        if receita_anual.irpj == 0:
            receita_anual.irpj = valores['irpj']
        
        receita_anual.save()
    
    return receita_anual

