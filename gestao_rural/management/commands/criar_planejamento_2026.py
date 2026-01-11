# -*- coding: utf-8 -*-
"""
Comando para criar um planejamento completo e detalhado para o ano de 2026.
Preenche todos os cards, planilhas, metas, indicadores e atividades.

Uso:
    python manage.py criar_planejamento_2026 --propriedade_id 1
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from gestao_rural.models import (
    AtividadePlanejada,
    CategoriaAnimal,
    CenarioPlanejamento,
    Financiamento,
    FluxoCaixa,
    IndicadorFinanceiro,
    IndicadorPlanejado,
    InventarioRebanho,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada,
    MovimentacaoProjetada,
    ParametrosProjecaoRebanho,
    PlanejamentoAnual,
    Propriedade,
    TipoFinanciamento,
)
from gestao_rural.services.planejamento_helper import criar_planejamento_automatico


def _decimal(valor) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"))


class Command(BaseCommand):
    help = "Cria um planejamento completo e detalhado para 2026."

    def add_arguments(self, parser):
        parser.add_argument(
            "--propriedade_id",
            type=int,
            required=True,
            help="ID da propriedade para criar o planejamento.",
        )

    def handle(self, *args, **options):
        propriedade_id = options["propriedade_id"]
        ano = 2026

        try:
            propriedade = Propriedade.objects.get(id=propriedade_id)
        except Propriedade.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Propriedade com ID {propriedade_id} não encontrada.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Criando planejamento completo para {ano}...")
        )
        self.stdout.write(f"Propriedade: {propriedade.nome_propriedade}")

        with transaction.atomic():
            # 1. Garantir inventário
            self._garantir_inventario_completo(propriedade, ano)

            # 2. Garantir parâmetros de projeção
            self._garantir_parametros_projecao(propriedade)

            # 3. Criar ou obter planejamento
            planejamento = self._criar_planejamento(propriedade, ano)

            # 4. Criar cenários
            cenarios = self._criar_cenarios(planejamento)

            # 5. Criar atividades planejadas (12 meses)
            self._criar_atividades_completas(planejamento, ano)

            # 6. Criar metas comerciais detalhadas
            self._criar_metas_comerciais_completas(planejamento)

            # 7. Criar metas financeiras completas
            self._criar_metas_financeiras_completas(planejamento)

            # 8. Criar indicadores estratégicos
            self._criar_indicadores_completos(planejamento)

            # 9. Criar movimentações projetadas mensais
            self._criar_movimentacoes_projetadas(propriedade, planejamento, cenarios["baseline"], ano)

            # 10. Criar dados financeiros
            self._criar_dados_financeiros(propriedade, ano)

        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("[SUCESSO] Planejamento 2026 criado com sucesso!"))
        self.stdout.write(
            self.style.SUCCESS(
                f"   Propriedade: {propriedade.nome_propriedade} | Ano: {ano}"
            )
        )

    def _garantir_inventario_completo(self, propriedade, ano):
        """Cria inventário completo se não existir"""
        data_ref = date(ano, 1, 1)

        # Verificar se já existe inventário
        if InventarioRebanho.objects.filter(
            propriedade=propriedade, data_inventario__year=ano
        ).exists():
            self.stdout.write("   Inventário já existe, mantendo dados existentes.")
            return

        # Buscar categorias existentes ou criar padrões
        categorias = {}
        categorias_config = [
            ("Bezerras (0-12m)", "F", 0, 12, 180, 350),
            ("Bezerros (0-12m)", "M", 0, 12, 185, 360),
            ("Novilhas (12-24m)", "F", 12, 24, 320, 520),
            ("Garrotes (12-24m)", "M", 12, 24, 330, 510),
            ("Matrizes Ativas", "F", 24, 120, 420, 1400),
            ("Vacas de Descarte", "F", 36, 120, 430, 180),
            ("Touros", "M", 36, 120, 450, 20),
        ]

        for nome, sexo, idade_min, idade_max, peso, quantidade in categorias_config:
            categoria, _ = CategoriaAnimal.objects.get_or_create(
                nome=nome,
                defaults={
                    "sexo": sexo,
                    "idade_minima_meses": idade_min,
                    "idade_maxima_meses": idade_max,
                    "peso_medio_kg": Decimal(str(peso)),
                },
            )
            categorias[nome] = categoria

            # Criar inventário
            valor_por_cabeca = Decimal("3200.00") if "Matrizes" in nome else Decimal("2100.00")
            InventarioRebanho.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_ref,
                defaults={
                    "quantidade": quantidade,
                    "valor_por_cabeca": valor_por_cabeca,
                },
            )

        self.stdout.write("   [OK] Inventario completo criado.")

    def _garantir_parametros_projecao(self, propriedade):
        """Garante parâmetros de projeção"""
        ParametrosProjecaoRebanho.objects.update_or_create(
            propriedade=propriedade,
            defaults={
                "taxa_natalidade_anual": Decimal("85.00"),
                "taxa_mortalidade_bezerros_anual": Decimal("6.00"),
                "taxa_mortalidade_adultos_anual": Decimal("2.20"),
                "percentual_venda_machos_anual": Decimal("92.00"),
                "percentual_venda_femeas_anual": Decimal("12.00"),
                "periodicidade": "MENSAL",
            },
        )

    def _criar_planejamento(self, propriedade, ano):
        """Cria ou obtém planejamento"""
        planejamento, created = PlanejamentoAnual.objects.get_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                "descricao": f"Planejamento estratégico completo para {ano}",
                "status": "EM_ANDAMENTO",
            },
        )
        if created:
            self.stdout.write(f"   [OK] Planejamento {ano} criado.")
        else:
            self.stdout.write(f"   [INFO] Planejamento {ano} ja existia, atualizando...")
        return planejamento

    def _criar_cenarios(self, planejamento):
        """Cria cenários de planejamento"""
        baseline, _ = CenarioPlanejamento.objects.get_or_create(
            planejamento=planejamento,
            nome="Baseline / Geral",
            defaults={
                "descricao": "Cenário oficial aprovado pelo comitê.",
                "is_baseline": True,
                "ajuste_preco_percentual": Decimal("0.00"),
                "ajuste_custo_percentual": Decimal("0.00"),
                "ajuste_producao_percentual": Decimal("0.00"),
            },
        )

        otimista, _ = CenarioPlanejamento.objects.get_or_create(
            planejamento=planejamento,
            nome="Mercado Otimista",
            defaults={
                "descricao": "Simula preços +8% com custos -3%.",
                "ajuste_preco_percentual": Decimal("8.00"),
                "ajuste_custo_percentual": Decimal("-3.00"),
                "ajuste_producao_percentual": Decimal("4.00"),
            },
        )

        conservador, _ = CenarioPlanejamento.objects.get_or_create(
            planejamento=planejamento,
            nome="Mercado Conservador",
            defaults={
                "descricao": "Simula preços -5% com custos +4%.",
                "ajuste_preco_percentual": Decimal("-5.00"),
                "ajuste_custo_percentual": Decimal("4.00"),
                "ajuste_producao_percentual": Decimal("-2.00"),
            },
        )

        return {"baseline": baseline, "otimista": otimista, "conservador": conservador}

    def _criar_atividades_completas(self, planejamento, ano):
        """Cria atividades planejadas para todo o ano"""
        atividades = [
            # Q1
            {
                "tipo": "IATF - Rodada 1",
                "categoria": None,
                "inicio": date(ano, 1, 15),
                "fim": date(ano, 2, 15),
                "responsavel": "Equipe Reprodução",
                "custo": Decimal("85000.00"),
                "indicador": "Taxa de prenhez",
            },
            {
                "tipo": "Vacinação de Rebanho",
                "categoria": None,
                "inicio": date(ano, 1, 20),
                "fim": date(ano, 1, 25),
                "responsavel": "Veterinário Responsável",
                "custo": Decimal("25000.00"),
                "indicador": "Cobertura vacinal",
            },
            {
                "tipo": "IATF - Rodada 2",
                "categoria": None,
                "inicio": date(ano, 3, 10),
                "fim": date(ano, 4, 10),
                "responsavel": "Equipe Reprodução",
                "custo": Decimal("85000.00"),
                "indicador": "Taxa de prenhez",
            },
            # Q2
            {
                "tipo": "Reforma de Pasto - Módulo 1",
                "categoria": None,
                "inicio": date(ano, 4, 1),
                "fim": date(ano, 5, 15),
                "responsavel": "Gestor Operações",
                "custo": Decimal("45000.00"),
                "indicador": "UA/ha",
            },
            {
                "tipo": "Venda Programada - Garrotes",
                "categoria": None,
                "inicio": date(ano, 5, 1),
                "fim": date(ano, 5, 31),
                "responsavel": "Time Comercial",
                "custo": Decimal("5000.00"),
                "indicador": "Receita mensal",
            },
            {
                "tipo": "Suplementação Estratégica",
                "categoria": None,
                "inicio": date(ano, 6, 1),
                "fim": date(ano, 6, 30),
                "responsavel": "Zootecnista",
                "custo": Decimal("120000.00"),
                "indicador": "Ganho de peso",
            },
            # Q3
            {
                "tipo": "IATF - Rodada 3",
                "categoria": None,
                "inicio": date(ano, 7, 15),
                "fim": date(ano, 8, 15),
                "responsavel": "Equipe Reprodução",
                "custo": Decimal("85000.00"),
                "indicador": "Taxa de prenhez",
            },
            {
                "tipo": "Venda Programada - Novilhas",
                "categoria": None,
                "inicio": date(ano, 8, 1),
                "fim": date(ano, 8, 31),
                "responsavel": "Time Comercial",
                "custo": Decimal("8000.00"),
                "indicador": "Receita mensal",
            },
            {
                "tipo": "Reforma de Pasto - Módulo 2",
                "categoria": None,
                "inicio": date(ano, 9, 1),
                "fim": date(ano, 10, 15),
                "responsavel": "Gestor Operações",
                "custo": Decimal("45000.00"),
                "indicador": "UA/ha",
            },
            # Q4
            {
                "tipo": "Venda Programada - Terminados",
                "categoria": None,
                "inicio": date(ano, 10, 1),
                "fim": date(ano, 10, 31),
                "responsavel": "Time Comercial",
                "custo": Decimal("10000.00"),
                "indicador": "Receita mensal",
            },
            {
                "tipo": "Avaliação de Desempenho",
                "categoria": None,
                "inicio": date(ano, 11, 1),
                "fim": date(ano, 11, 30),
                "responsavel": "Equipe Técnica",
                "custo": Decimal("15000.00"),
                "indicador": "KPIs gerais",
            },
            {
                "tipo": "Planejamento 2027",
                "categoria": None,
                "inicio": date(ano, 12, 1),
                "fim": date(ano, 12, 31),
                "responsavel": "Gestão",
                "custo": Decimal("20000.00"),
                "indicador": "Estratégia",
            },
        ]

        for dados in atividades:
            AtividadePlanejada.objects.update_or_create(
                planejamento=planejamento,
                tipo_atividade=dados["tipo"],
                data_inicio_prevista=dados["inicio"],
                defaults={
                    "categoria": dados["categoria"],
                    "descricao": f"{dados['tipo']} - Planejado para {ano}",
                    "data_fim_prevista": dados["fim"],
                    "responsavel": dados["responsavel"],
                    "custo_previsto": dados["custo"],
                    "indicador_alvo": dados["indicador"],
                    "status": "AGENDADA",
                },
            )

        self.stdout.write(f"   [OK] {len(atividades)} atividades planejadas criadas.")

    def _criar_metas_comerciais_completas(self, planejamento):
        """Cria metas comerciais detalhadas"""
        # Buscar categorias
        categorias = {}
        for nome in [
            "Garrotes (12-24m)",
            "Novilhas (12-24m)",
            "Vacas de Descarte",
            "Touros",
        ]:
            try:
                categorias[nome] = CategoriaAnimal.objects.get(nome=nome)
            except CategoriaAnimal.DoesNotExist:
                continue

        metas = [
            {
                "categoria": categorias.get("Garrotes (12-24m)"),
                "quantidade": 420,
                "arrobas": Decimal("6300.00"),
                "preco": Decimal("285.00"),
                "canal": "Frigorífico Prime",
            },
            {
                "categoria": categorias.get("Novilhas (12-24m)"),
                "quantidade": 180,
                "arrobas": Decimal("2700.00"),
                "preco": Decimal("265.00"),
                "canal": "Reposição Parceira",
            },
            {
                "categoria": categorias.get("Vacas de Descarte"),
                "quantidade": 150,
                "arrobas": Decimal("2250.00"),
                "preco": Decimal("190.00"),
                "canal": "Leilões Regionais",
            },
            {
                "categoria": categorias.get("Touros"),
                "quantidade": 8,
                "arrobas": Decimal("120.00"),
                "preco": Decimal("320.00"),
                "canal": "Mercado Especializado",
            },
        ]

        for dados in metas:
            if dados["categoria"]:
                MetaComercialPlanejada.objects.update_or_create(
                    planejamento=planejamento,
                    categoria=dados["categoria"],
                    defaults={
                        "quantidade_animais": dados["quantidade"],
                        "arrobas_totais": dados["arrobas"],
                        "preco_medio_esperado": dados["preco"],
                        "canal_venda": dados["canal"],
                        "percentual_impostos": Decimal("4.50"),
                        "observacoes": f"Meta comercial para {planejamento.ano}",
                    },
                )

        self.stdout.write(f"   [OK] {len(metas)} metas comerciais criadas.")

    def _criar_metas_financeiras_completas(self, planejamento):
        """Cria metas financeiras completas"""
        metas = [
            {
                "descricao": "Custo Mensal de Suplementação",
                "tipo": "VARIAVEL",
                "valor": Decimal("185000.00"),
                "indice": "IGP-M",
                "percentual": Decimal("4.50"),
            },
            {
                "descricao": "Programa de Genética e IATF",
                "tipo": "INVESTIMENTO",
                "valor": Decimal("320000.00"),
                "indice": "",
                "percentual": Decimal("0.00"),
            },
            {
                "descricao": "Folha Operacional",
                "tipo": "FIXO",
                "valor": Decimal("980000.00"),
                "indice": "IPCA",
                "percentual": Decimal("4.00"),
            },
            {
                "descricao": "Manutenção de Equipamentos",
                "tipo": "VARIAVEL",
                "valor": Decimal("85000.00"),
                "indice": "IPCA",
                "percentual": Decimal("4.00"),
            },
            {
                "descricao": "Combustível e Lubrificantes",
                "tipo": "VARIAVEL",
                "valor": Decimal("120000.00"),
                "indice": "IPCA",
                "percentual": Decimal("4.00"),
            },
            {
                "descricao": "Medicamentos e Veterinária",
                "tipo": "VARIAVEL",
                "valor": Decimal("95000.00"),
                "indice": "IPCA",
                "percentual": Decimal("4.00"),
            },
            {
                "descricao": "Infraestrutura e Melhorias",
                "tipo": "INVESTIMENTO",
                "valor": Decimal("180000.00"),
                "indice": "",
                "percentual": Decimal("0.00"),
            },
        ]

        for dados in metas:
            MetaFinanceiraPlanejada.objects.update_or_create(
                planejamento=planejamento,
                descricao=dados["descricao"],
                defaults={
                    "tipo_custo": dados["tipo"],
                    "valor_anual_previsto": dados["valor"],
                    "indice_correcao": dados["indice"],
                    "percentual_correcao": dados["percentual"],
                    "observacoes": f"Meta financeira para {planejamento.ano}",
                },
            )

        self.stdout.write(f"   [OK] {len(metas)} metas financeiras criadas.")

    def _criar_indicadores_completos(self, planejamento):
        """Cria indicadores estratégicos completos"""
        indicadores = [
            {
                "codigo": "TAXA_PRENHEZ",
                "nome": "Taxa de Prenhez (IATF + Monta)",
                "unidade": "%",
                "valor": Decimal("88.00"),
                "eixo": "REPRODUCAO",
                "direcao": "MAIOR",
                "prioridade": 1,
            },
            {
                "codigo": "TAXA_NASCIMENTO",
                "nome": "Taxa de Natalidade",
                "unidade": "%",
                "valor": Decimal("85.00"),
                "eixo": "REPRODUCAO",
                "direcao": "MAIOR",
                "prioridade": 1,
            },
            {
                "codigo": "ARROBAS_VENDIDAS",
                "nome": "Produção Anual de Arrobas",
                "unidade": "@",
                "valor": Decimal("11200.00"),
                "eixo": "ENGORDA",
                "direcao": "MAIOR",
                "prioridade": 1,
            },
            {
                "codigo": "CUSTO_ARROBA",
                "nome": "Custo Operacional por Arroba",
                "unidade": "R$",
                "valor": Decimal("248.00"),
                "eixo": "FINANCEIRO",
                "direcao": "MENOR",
                "prioridade": 1,
            },
            {
                "codigo": "LOTACAO_UA",
                "nome": "Lotação (UA/ha)",
                "unidade": "UA/ha",
                "valor": Decimal("1.15"),
                "eixo": "OPERACIONAL",
                "direcao": "MAIOR",
                "prioridade": 2,
            },
            {
                "codigo": "ANIMAIS_POR_HECTARE",
                "nome": "Animais por Hectare",
                "unidade": "cab/ha",
                "valor": Decimal("0.85"),
                "eixo": "OPERACIONAL",
                "direcao": "MAIOR",
                "prioridade": 2,
            },
            {
                "codigo": "MARGEM_OPERACIONAL",
                "nome": "Margem Operacional",
                "unidade": "R$",
                "valor": Decimal("2830000.00"),
                "eixo": "FINANCEIRO",
                "direcao": "MAIOR",
                "prioridade": 1,
            },
            {
                "codigo": "LUCRO_POR_HECTARE",
                "nome": "Lucro por Hectare",
                "unidade": "R$",
                "valor": Decimal("943.33"),
                "eixo": "FINANCEIRO",
                "direcao": "MAIOR",
                "prioridade": 1,
            },
        ]

        for dados in indicadores:
            IndicadorPlanejado.objects.update_or_create(
                planejamento=planejamento,
                codigo=dados["codigo"],
                defaults={
                    "nome": dados["nome"],
                    "unidade": dados["unidade"],
                    "valor_meta": dados["valor"],
                    "valor_base": dados["valor"] - (dados["valor"] * Decimal("0.05")),
                    "eixo_estrategico": dados["eixo"],
                    "direcao_meta": dados["direcao"],
                    "prioridade": dados["prioridade"],
                    "observacoes": f"Meta estratégica para {planejamento.ano}",
                },
            )

        self.stdout.write(f"   [OK] {len(indicadores)} indicadores criados.")

    def _criar_movimentacoes_projetadas(self, propriedade, planejamento, cenario, ano):
        """Cria movimentações projetadas mensais"""
        # Limpar movimentações antigas do planejamento
        MovimentacaoProjetada.objects.filter(
            propriedade=propriedade, planejamento=planejamento
        ).delete()

        # Buscar categorias
        try:
            categoria_garrote = CategoriaAnimal.objects.get(nome="Garrotes (12-24m)")
            categoria_novilha = CategoriaAnimal.objects.get(nome="Novilhas (12-24m)")
            categoria_vaca = CategoriaAnimal.objects.get(nome="Vacas de Descarte")
        except CategoriaAnimal.DoesNotExist:
            # Usar categorias que existem
            categoria_garrote = CategoriaAnimal.objects.filter(nome__icontains="Garrote").first()
            categoria_novilha = CategoriaAnimal.objects.filter(nome__icontains="Novilha").first()
            categoria_vaca = CategoriaAnimal.objects.filter(nome__icontains="Vaca").first()

        movimentacoes = []
        for mes in range(1, 13):
            data_base = date(ano, mes, 15)

            # Nascimentos (mais concentrados em alguns meses)
            if mes in [2, 3, 4, 8, 9, 10]:
                movimentacoes.append(
                    {
                        "tipo": "NASCIMENTO",
                        "categoria": categoria_garrote if categoria_garrote else None,
                        "quantidade": random.randint(90, 120),
                        "data": data_base,
                    }
                )

            # Vendas (concentradas em trimestres)
            if mes in [5, 6, 8, 10, 11]:
                movimentacoes.append(
                    {
                        "tipo": "VENDA",
                        "categoria": categoria_garrote if categoria_garrote else None,
                        "quantidade": random.randint(50, 80),
                        "preco": Decimal("285.00"),
                        "data": data_base,
                    }
                )

            # Compras (esporádicas)
            if mes in [1, 4, 7]:
                movimentacoes.append(
                    {
                        "tipo": "COMPRA",
                        "categoria": categoria_novilha if categoria_novilha else None,
                        "quantidade": random.randint(10, 20),
                        "preco": Decimal("2100.00"),
                        "data": data_base,
                    }
                )

        for dados in movimentacoes:
            categoria = dados.get("categoria")
            valor_por_cabeca = dados.get("preco", Decimal("0.00"))
            quantidade = dados["quantidade"]

            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                planejamento=planejamento,
                cenario=cenario,
                data_movimentacao=dados["data"],
                tipo_movimentacao=dados["tipo"],
                categoria=categoria,
                quantidade=quantidade,
                valor_por_cabeca=valor_por_cabeca if valor_por_cabeca else None,
                valor_total=(
                    valor_por_cabeca * Decimal(quantidade) if valor_por_cabeca else None
                ),
            )

        self.stdout.write(f"   [OK] {len(movimentacoes)} movimentacoes projetadas criadas.")

    def _criar_dados_financeiros(self, propriedade, ano):
        """Cria dados financeiros"""
        referencia = date(ano, 1, 31)

        FluxoCaixa.objects.update_or_create(
            propriedade=propriedade,
            data_referencia=referencia,
            defaults={
                "receita_total": Decimal("9250000.00"),
                "custo_fixo_total": Decimal("3880000.00"),
                "custo_variavel_total": Decimal("2540000.00"),
                "lucro_bruto": Decimal("2830000.00"),
                "margem_lucro": Decimal("30.60"),
            },
        )

        indicadores = [
            ("Margem Operacional", "RENTABILIDADE", Decimal("32.50"), "%"),
            ("Liquidez Corrente", "LIQUIDEZ", Decimal("1.82"), "x"),
            ("Endividamento sobre Receita", "ENDIVIDAMENTO", Decimal("28.00"), "%"),
        ]

        for nome, tipo, valor, unidade in indicadores:
            IndicadorFinanceiro.objects.update_or_create(
                propriedade=propriedade,
                nome=nome,
                data_referencia=referencia,
                defaults={
                    "tipo": tipo,
                    "valor": valor,
                    "unidade": unidade,
                },
            )

        tipo_fin, _ = TipoFinanciamento.objects.get_or_create(
            nome="Investimento Pecuário",
            defaults={"descricao": "Linha de crédito para expansão de rebanho."},
        )

        Financiamento.objects.update_or_create(
            propriedade=propriedade,
            nome=f"BB Invest Pecuária {ano}",
            defaults={
                "tipo": tipo_fin,
                "descricao": f"Financiamento de longo prazo para intensificação - {ano}",
                "valor_principal": Decimal("1500000.00"),
                "taxa_juros_anual": Decimal("8.20"),
                "tipo_taxa": "FIXA",
                "data_contratacao": referencia,
                "data_primeiro_vencimento": referencia + timedelta(days=30),
                "data_ultimo_vencimento": referencia + timedelta(days=30 * 60),
                "numero_parcelas": 60,
                "valor_parcela": Decimal("31250.00"),
                "ativo": True,
            },
        )

        self.stdout.write("   [OK] Dados financeiros criados.")


















