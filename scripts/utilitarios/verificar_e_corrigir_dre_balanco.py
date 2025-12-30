# -*- coding: utf-8 -*-
"""
Script para verificar, recalcular e corrigir DRE e Balanço Patrimonial
Garantindo dados corretos e realistas para apresentação ao banco
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date
from django.db.models import Sum, Q
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, InventarioRebanho, BemImobilizado,
    SCRBancoCentral, DividaBanco, MovimentacaoProjetada
)
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, ReceitaAnual, CategoriaFinanceira
)


def verificar_dre_por_ano(propriedades, ano):
    """Verifica e recalcula DRE para um ano específico"""
    print(f"\n{'='*80}")
    print(f"VERIFICANDO DRE - ANO {ano}")
    print(f"{'='*80}")
    
    # Buscar ReceitaAnual
    receitas_anuais = ReceitaAnual.objects.filter(
        propriedade__in=propriedades,
        ano=ano
    )
    
    if not receitas_anuais.exists():
        print(f"[ERRO] Não há ReceitaAnual cadastrada para {ano}")
        return None
    
    # Calcular totais
    receita_bruta = sum(r.valor_receita or Decimal('0.00') for r in receitas_anuais)
    icms_vendas = sum(r.icms_vendas or Decimal('0.00') for r in receitas_anuais)
    funrural_vendas = sum(r.funviral_vendas or Decimal('0.00') for r in receitas_anuais)
    outros_impostos_vendas = sum(r.outros_impostos_vendas or Decimal('0.00') for r in receitas_anuais)
    total_deducoes = icms_vendas + funrural_vendas + outros_impostos_vendas
    receita_liquida = receita_bruta - total_deducoes
    
    cpv = sum(r.custo_produtos_vendidos or Decimal('0.00') for r in receitas_anuais)
    lucro_bruto = receita_liquida - cpv
    
    # Despesas operacionais
    despesas_operacionais = (
        sum(r.retirada_labore or Decimal('0.00') for r in receitas_anuais) +
        sum(r.assistencia_contabil or Decimal('0.00') for r in receitas_anuais) +
        sum(r.encargos_inss or Decimal('0.00') for r in receitas_anuais) +
        sum(r.taxas_diversas or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_administrativas or Decimal('0.00') for r in receitas_anuais) +
        sum(r.material_uso_consumo or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_comunicacao or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_viagens or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_energia_eletrica or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_transportes or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_combustivel or Decimal('0.00') for r in receitas_anuais) +
        sum(r.despesas_manutencao or Decimal('0.00') for r in receitas_anuais) +
        sum(r.depreciacao_amortizacao or Decimal('0.00') for r in receitas_anuais)
    )
    
    resultado_operacional = lucro_bruto - despesas_operacionais
    
    # Resultado financeiro
    despesas_financeiras = sum(r.despesas_financeiras or Decimal('0.00') for r in receitas_anuais)
    receitas_financeiras = sum(r.receitas_financeiras or Decimal('0.00') for r in receitas_anuais)
    resultado_financeiro = receitas_financeiras - despesas_financeiras
    
    lair = resultado_operacional + resultado_financeiro
    
    # Impostos
    csll = sum(r.csll or Decimal('0.00') for r in receitas_anuais)
    irpj = sum(r.irpj or Decimal('0.00') for r in receitas_anuais)
    total_impostos = csll + irpj
    
    resultado_liquido = lair - total_impostos
    
    # Verificar se há lançamentos financeiros
    lancamentos_receita = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_lancamentos_receita = lancamentos_receita.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    lancamentos_despesa = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_lancamentos_despesa = lancamentos_despesa.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    # Exibir resultados
    print(f"\n[RECEITAS]")
    print(f"  Receita Bruta: R$ {receita_bruta:,.2f}")
    print(f"  ICMS: R$ {icms_vendas:,.2f}")
    print(f"  Funrural: R$ {funrural_vendas:,.2f}")
    print(f"  Outros Impostos: R$ {outros_impostos_vendas:,.2f}")
    print(f"  Total Deduções: R$ {total_deducoes:,.2f}")
    print(f"  Receita Líquida: R$ {receita_liquida:,.2f}")
    print(f"  (Lançamentos Receita: R$ {total_lancamentos_receita:,.2f})")
    
    print(f"\n[CUSTOS E DESPESAS]")
    print(f"  CPV: R$ {cpv:,.2f}")
    print(f"  Lucro Bruto: R$ {lucro_bruto:,.2f}")
    print(f"  Despesas Operacionais: R$ {despesas_operacionais:,.2f}")
    print(f"  Resultado Operacional: R$ {resultado_operacional:,.2f}")
    print(f"  Despesas Financeiras: R$ {despesas_financeiras:,.2f}")
    print(f"  Receitas Financeiras: R$ {receitas_financeiras:,.2f}")
    print(f"  Resultado Financeiro: R$ {resultado_financeiro:,.2f}")
    print(f"  (Lançamentos Despesa: R$ {total_lancamentos_despesa:,.2f})")
    
    print(f"\n[IMPOSTOS E RESULTADO]")
    print(f"  LAIR: R$ {lair:,.2f}")
    print(f"  CSLL: R$ {csll:,.2f}")
    print(f"  IRPJ: R$ {irpj:,.2f}")
    print(f"  Total Impostos: R$ {total_impostos:,.2f}")
    print(f"  RESULTADO LÍQUIDO: R$ {resultado_liquido:,.2f}")
    
    # Verificar consistência
    diferenca_receita = abs(receita_bruta - total_lancamentos_receita)
    if diferenca_receita > Decimal('1000.00'):
        print(f"\n[AVISO] Diferença entre ReceitaAnual e Lançamentos: R$ {diferenca_receita:,.2f}")
    
    # Verificar margem
    if receita_liquida > 0:
        margem_lucro = (resultado_liquido / receita_liquida) * 100
        print(f"\n[MARGEM] Margem de Lucro Líquido: {margem_lucro:.2f}%")
        if margem_lucro < 5 or margem_lucro > 20:
            print(f"[AVISO] Margem fora do esperado para pecuária (5-15%)")
    
    return {
        'receita_bruta': receita_bruta,
        'receita_liquida': receita_liquida,
        'lucro_bruto': lucro_bruto,
        'resultado_operacional': resultado_operacional,
        'lair': lair,
        'resultado_liquido': resultado_liquido,
        'margem_lucro': margem_lucro if receita_liquida > 0 else Decimal('0.00'),
    }


def verificar_balanco_patrimonial(propriedades, ano):
    """Verifica e calcula Balanço Patrimonial"""
    print(f"\n{'='*80}")
    print(f"VERIFICANDO BALANÇO PATRIMONIAL - ANO {ano}")
    print(f"{'='*80}")
    
    # ATIVO
    # Bens Imobilizados
    bens_imobilizados = BemImobilizado.objects.filter(
        propriedade__in=propriedades,
        ativo=True
    )
    valor_imobilizado = sum(b.valor_atual for b in bens_imobilizados)
    
    # Rebanho (Ativo Circulante)
    inventarios = InventarioRebanho.objects.filter(
        propriedade__in=propriedades,
        data_inventario__year=ano
    )
    valor_rebanho = Decimal('0.00')
    for inv in inventarios:
        try:
            valor_rebanho += inv.valor_total
        except:
            valor_rebanho += (inv.quantidade * inv.valor_por_cabeca)
    
    # Contas a Receber (estimativa)
    lancamentos_receber = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_PENDENTE
    )
    contas_receber = lancamentos_receber.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    ativo_total = valor_imobilizado + valor_rebanho + contas_receber
    
    # PASSIVO
    primeira_propriedade = propriedades.first()
    produtor = primeira_propriedade.produtor if primeira_propriedade else None
    
    scr = SCRBancoCentral.objects.filter(produtor=produtor).order_by('-data_referencia_scr').first()
    total_dividas = Decimal('0.00')
    if scr:
        dividas = DividaBanco.objects.filter(scr=scr)
        total_dividas = sum(d.valor_total for d in dividas)
    
    # Contas a Pagar (estimativa)
    lancamentos_pagar = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_PENDENTE
    )
    contas_pagar = lancamentos_pagar.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    passivo_total = total_dividas + contas_pagar
    
    # PATRIMÔNIO LÍQUIDO
    patrimonio_liquido = ativo_total - passivo_total
    
    # Exibir resultados
    print(f"\n[ATIVO]")
    print(f"  Bens Imobilizados: R$ {valor_imobilizado:,.2f}")
    print(f"  Rebanho (Ativo Circulante): R$ {valor_rebanho:,.2f}")
    print(f"  Contas a Receber: R$ {contas_receber:,.2f}")
    print(f"  TOTAL ATIVO: R$ {ativo_total:,.2f}")
    
    print(f"\n[PASSIVO]")
    print(f"  Dívidas Bancárias: R$ {total_dividas:,.2f}")
    print(f"  Contas a Pagar: R$ {contas_pagar:,.2f}")
    print(f"  TOTAL PASSIVO: R$ {passivo_total:,.2f}")
    
    print(f"\n[PATRIMÔNIO LÍQUIDO]")
    print(f"  PATRIMÔNIO LÍQUIDO: R$ {patrimonio_liquido:,.2f}")
    
    # Verificar consistência
    if patrimonio_liquido < 0:
        print(f"\n[ERRO CRÍTICO] Patrimônio Líquido negativo!")
    
    # Verificar cobertura
    if total_dividas > 0:
        cobertura_patrimonial = (ativo_total / total_dividas) * 100
        print(f"\n[COBERTURA] Cobertura Patrimonial: {cobertura_patrimonial:.2f}%")
        if cobertura_patrimonial < 100:
            print(f"[AVISO] Ativo não cobre totalmente as dívidas!")
    
    return {
        'ativo_total': ativo_total,
        'valor_imobilizado': valor_imobilizado,
        'valor_rebanho': valor_rebanho,
        'contas_receber': contas_receber,
        'passivo_total': passivo_total,
        'total_dividas': total_dividas,
        'contas_pagar': contas_pagar,
        'patrimonio_liquido': patrimonio_liquido,
    }


def verificar_consistencia_geral(propriedades, anos):
    """Verifica consistência geral dos dados"""
    print(f"\n{'='*80}")
    print(f"VERIFICAÇÃO DE CONSISTÊNCIA GERAL")
    print(f"{'='*80}")
    
    erros = []
    avisos = []
    
    for ano in anos:
        # Verificar ReceitaAnual
        receitas_anuais = ReceitaAnual.objects.filter(
            propriedade__in=propriedades,
            ano=ano
        )
        
        if not receitas_anuais.exists():
            erros.append(f"Ano {ano}: Não há ReceitaAnual cadastrada")
            continue
        
        # Verificar se há lançamentos financeiros
        lancamentos = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            data_competencia__year=ano
        )
        
        if not lancamentos.exists():
            avisos.append(f"Ano {ano}: Não há lançamentos financeiros")
        
        # Verificar inventários
        inventarios = InventarioRebanho.objects.filter(
            propriedade__in=propriedades,
            data_inventario__year=ano
        )
        
        if not inventarios.exists():
            avisos.append(f"Ano {ano}: Não há inventários de rebanho")
        
        # Verificar bens imobilizados
        bens = BemImobilizado.objects.filter(
            propriedade__in=propriedades,
            ativo=True
        )
        
        if not bens.exists():
            avisos.append(f"Nenhum bem imobilizado cadastrado")
    
    # Exibir resultados
    if erros:
        print(f"\n[ERROS ENCONTRADOS]")
        for erro in erros:
            print(f"  ❌ {erro}")
    
    if avisos:
        print(f"\n[AVISOS]")
        for aviso in avisos:
            print(f"  ⚠️  {aviso}")
    
    if not erros and not avisos:
        print(f"\n[OK] Nenhum erro ou aviso encontrado!")
    
    return len(erros) == 0


def main():
    """Função principal"""
    print("="*80)
    print("VERIFICAÇÃO E RECÁLCULO DE DRE E BALANÇO PATRIMONIAL")
    print("="*80)
    
    # Buscar produtor
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor 'Marcelo Sanguino' não encontrado!")
        return
    
    print(f"\n[PRODUTOR] {produtor.nome}")
    print(f"[CPF/CNPJ] {produtor.cpf_cnpj}")
    
    # Buscar propriedades
    propriedades = Propriedade.objects.filter(produtor=produtor)
    print(f"\n[PROPRIEDADES] {propriedades.count()} encontradas:")
    for prop in propriedades:
        print(f"  - {prop.nome_propriedade}")
    
    # Anos a verificar
    anos = [2022, 2023, 2024, 2025]
    
    # Verificar consistência geral
    consistencia_ok = verificar_consistencia_geral(propriedades, anos)
    
    # Verificar DRE e Balanço para cada ano
    resultados_dre = {}
    resultados_balanco = {}
    
    for ano in anos:
        dre = verificar_dre_por_ano(propriedades, ano)
        if dre:
            resultados_dre[ano] = dre
        
        balanco = verificar_balanco_patrimonial(propriedades, ano)
        if balanco:
            resultados_balanco[ano] = balanco
    
    # Resumo final
    print(f"\n{'='*80}")
    print(f"RESUMO FINAL")
    print(f"{'='*80}")
    
    print(f"\n[RESULTADO LÍQUIDO POR ANO]")
    for ano in anos:
        if ano in resultados_dre:
            rl = resultados_dre[ano]['resultado_liquido']
            margem = resultados_dre[ano]['margem_lucro']
            print(f"  {ano}: R$ {rl:,.2f} (Margem: {margem:.2f}%)")
    
    print(f"\n[PATRIMÔNIO LÍQUIDO POR ANO]")
    for ano in anos:
        if ano in resultados_balanco:
            pl = resultados_balanco[ano]['patrimonio_liquido']
            print(f"  {ano}: R$ {pl:,.2f}")
    
    print(f"\n{'='*80}")
    if consistencia_ok:
        print("✅ VERIFICAÇÃO CONCLUÍDA - DADOS CONSISTENTES")
    else:
        print("⚠️  VERIFICAÇÃO CONCLUÍDA - HÁ ERROS A CORRIGIR")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

