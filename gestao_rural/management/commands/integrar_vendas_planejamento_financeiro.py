# -*- coding: utf-8 -*-
"""
Comando para integrar vendas do planejamento/cenário com o módulo financeiro.
Cria lançamentos financeiros baseados nas vendas projetadas, usando datas e valores reais.
"""
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count

from gestao_rural.models import VendaProjetada, Propriedade
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira
)


class Command(BaseCommand):
    help = 'Integra vendas do planejamento/cenário com o módulo financeiro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID da propriedade (se não informado, usa a primeira)',
        )
        parser.add_argument(
            '--ano',
            type=int,
            help='Ano específico para integrar (se não informado, integra todos)',
        )
        parser.add_argument(
            '--excluir-existentes',
            action='store_true',
            help='Excluir lançamentos existentes antes de criar novos',
        )

    def handle(self, *args, **options):
        propriedade_id = options.get('propriedade_id')
        ano = options.get('ano')
        excluir_existentes = options.get('excluir_existentes', False)

        # Buscar propriedade
        if propriedade_id:
            try:
                propriedade = Propriedade.objects.get(id=propriedade_id)
            except Propriedade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Propriedade com ID {propriedade_id} não encontrada.'))
                return
        else:
            propriedade = Propriedade.objects.first()
            if not propriedade:
                self.stdout.write(self.style.ERROR('Nenhuma propriedade encontrada.'))
                return

        self.stdout.write(self.style.SUCCESS(f'Propriedade: {propriedade.nome_propriedade}'))

        # Buscar conta destino padrão
        conta_destino = ContaFinanceira.objects.filter(
            propriedade=propriedade,
            ativa=True
        ).first()

        if not conta_destino:
            self.stdout.write(self.style.ERROR('Nenhuma conta financeira ativa encontrada. Crie uma conta primeiro.'))
            return

        self.stdout.write(f'Conta destino: {conta_destino.nome}')

        # Buscar categoria de receita padrão
        categoria_receita = CategoriaFinanceira.objects.filter(
            propriedade=propriedade,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            ativa=True
        ).first()

        if not categoria_receita:
            # Criar categoria padrão se não existir
            categoria_receita = CategoriaFinanceira.objects.create(
                propriedade=propriedade,
                nome='Vendas de Animais',
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao='Receitas provenientes de vendas de animais do planejamento',
                ativa=True
            )
            self.stdout.write(f'Categoria criada: {categoria_receita.nome}')
        else:
            self.stdout.write(f'Categoria: {categoria_receita.nome}')

        # Buscar vendas projetadas
        vendas = VendaProjetada.objects.filter(propriedade=propriedade)
        
        if ano:
            vendas = vendas.filter(data_venda__year=ano)
            self.stdout.write(f'\nFiltrando vendas do ano {ano}...')
        else:
            self.stdout.write('\nBuscando todas as vendas projetadas...')

        total_vendas = vendas.count()
        self.stdout.write(f'Total de vendas encontradas: {total_vendas}')

        if total_vendas == 0:
            self.stdout.write(self.style.WARNING('Nenhuma venda projetada encontrada.'))
            return

        # Excluir lançamentos existentes se solicitado
        if excluir_existentes:
            lancamentos_existentes = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao__icontains='Venda'
            )
            if ano:
                lancamentos_existentes = lancamentos_existentes.filter(data_competencia__year=ano)
            
            total_excluidos = lancamentos_existentes.count()
            if total_excluidos > 0:
                lancamentos_existentes.delete()
                self.stdout.write(f'[OK] {total_excluidos} lançamentos existentes excluídos.')

        # Criar lançamentos financeiros
        lancamentos_criados = 0
        lancamentos_duplicados = 0
        total_receitas = Decimal('0.00')
        hoje = timezone.localdate()

        with transaction.atomic():
            for venda in vendas:
                # Data de recebimento = data_recebimento ou data_venda
                data_recebimento = venda.data_recebimento or venda.data_venda
                
                # Verificar se já existe lançamento para esta venda
                lancamento_existente = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    descricao__icontains=f"Venda {venda.data_venda.strftime('%d/%m/%Y')}",
                    valor=venda.valor_total,
                    data_competencia=data_recebimento
                ).first()
                
                if lancamento_existente:
                    lancamentos_duplicados += 1
                    continue

                # Montar descrição detalhada
                descricao_parts = [
                    f"Venda {venda.data_venda.strftime('%d/%m/%Y')}",
                    f"{venda.quantidade} {venda.categoria.nome}",
                ]
                
                if venda.cliente_nome:
                    descricao_parts.append(f"Cliente: {venda.cliente_nome}")
                
                if venda.peso_total_kg:
                    descricao_parts.append(f"Peso: {venda.peso_total_kg:,.2f} kg")
                
                if venda.valor_por_kg:
                    descricao_parts.append(f"R$ {venda.valor_por_kg:,.2f}/kg")
                
                descricao = " - ".join(descricao_parts)

                # Criar lançamento financeiro
                # Data de competência = data de recebimento (quando o dinheiro entra)
                # Data de vencimento = data de recebimento (recebimento à vista)
                # Data de quitação = data de recebimento se já passou, senão None
                data_quitacao = data_recebimento if data_recebimento <= hoje else None
                status = LancamentoFinanceiro.STATUS_QUITADO if data_quitacao else LancamentoFinanceiro.STATUS_PENDENTE

                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_receita,
                    conta_destino=conta_destino,
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao=descricao,
                    valor=venda.valor_total,
                    data_competencia=data_recebimento,  # Data quando o dinheiro entra
                    data_vencimento=data_recebimento,  # Recebimento à vista
                    data_quitacao=data_quitacao,
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=status,
                    documento_referencia=f"Venda Projetada ID: {venda.id}",
                    observacoes=(
                        f"Gerado automaticamente da venda projetada. "
                        f"Data venda: {venda.data_venda.strftime('%d/%m/%Y')}. "
                        f"Cliente: {venda.cliente_nome or 'Não definido'}"
                    )
                )
                lancamentos_criados += 1
                total_receitas += venda.valor_total

        # Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('RESUMO DA INTEGRAÇÃO'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Lançamentos criados: {lancamentos_criados}')
        self.stdout.write(f'Lançamentos duplicados (ignorados): {lancamentos_duplicados}')
        self.stdout.write(f'Total de receitas: R$ {total_receitas:,.2f}')
        
        if lancamentos_criados > 0:
            self.stdout.write(self.style.SUCCESS(f'\n[OK] Integração concluída com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('\nNenhum lançamento novo foi criado.'))


