# -*- coding: utf-8 -*-
"""
Comando utilitário para gerar dados completos do dashboard de planejamento.
Executa uma rotina única que cria usuário, produtor, propriedade, inventário,
parâmetros de projeção e todos os vínculos necessários (metas, atividades,
cenários, indicadores, fluxo de caixa etc).

Uso:
    python manage.py seed_planejamento --usuario admin --ano 2025
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
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
    ProdutorRural,
    Propriedade,
    TipoFinanciamento,
)


def _decimal(valor) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"))


class Command(BaseCommand):
    help = "Gera dados completos para o dashboard de planejamento pecuário."

    def add_arguments(self, parser):
        parser.add_argument(
            "--usuario",
            default="admin",
            help="Usuário que será vinculado ao produtor/propriedade (default: admin).",
        )
        parser.add_argument(
            "--ano",
            type=int,
            default=timezone.now().year,
            help="Ano que receberá o planejamento (default: ano atual).",
        )

    def handle(self, *args, **options):
        usuario_username = options["usuario"]
        ano_planejamento = options["ano"]

        usuario = self._garantir_usuario(usuario_username)
        produtor = self._garantir_produtor(usuario)
        propriedade = self._garantir_propriedade(produtor)

        categorias = self._garantir_categorias()
        self._garantir_inventario(propriedade, categorias, ano_planejamento)
        self._garantir_parametros_projecao(propriedade)

        planejamento = self._garantir_planejamento(propriedade, ano_planejamento)
        cenarios = self._garantir_cenarios(planejamento)
        self._garantir_atividades(planejamento, categorias, ano_planejamento)
        self._garantir_metas_comerciais(planejamento, categorias)
        self._garantir_metas_financeiras(planejamento)
        self._garantir_indicadores(planejamento)
        self._garantir_movimentacoes(propriedade, planejamento, cenarios["baseline"])
        self._garantir_financeiro(propriedade, ano_planejamento)

        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("Rotina concluída com sucesso!"))
        self.stdout.write(
            self.style.SUCCESS(
                f"Usuário: {usuario.username} | Propriedade: {propriedade.nome_propriedade}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Planejamento configurado para o ano de {planejamento.ano}."
            )
        )

    # ------------------------------------------------------------------ Helpers
    def _garantir_usuario(self, username):
        User = get_user_model()
        usuario, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": f"{username}@monpec.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            usuario.set_password("admin123")
            usuario.save()
            self.stdout.write(f"Usuário '{username}' criado com senha padrão 'admin123'.")
        else:
            self.stdout.write(f"Usuário '{username}' reaproveitado.")
        return usuario

    def _garantir_produtor(self, usuario):
        produtor, created = ProdutorRural.objects.get_or_create(
            cpf_cnpj="11122233344",
            defaults={
                "nome": "Produtor Demo Monpec",
                "usuario_responsavel": usuario,
                "telefone": "(67) 99999-1111",
                "email": "demo@monpec.com.br",
                "anos_experiencia": 18,
            },
        )
        if created:
            self.stdout.write("Produtor demo criado.")
        return produtor

    def _garantir_propriedade(self, produtor):
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade="Fazenda Monpec 2",
            produtor=produtor,
            defaults={
                "municipio": "Jaruqari",
                "uf": "MS",
                "area_total_ha": Decimal("3000"),
                "tipo_operacao": "PECUARIA",
                "tipo_ciclo_pecuario": ["CICLO_COMPLETO"],
                "valor_hectare_proprio": Decimal("18000"),
            },
        )
        if created:
            self.stdout.write("Propriedade demo criada.")
        return propriedade

    def _garantir_categorias(self):
        categorias_config = [
            ("Bezerras (0-12m)", "F", 0, 12, 180),
            ("Bezerros (0-12m)", "M", 0, 12, 185),
            ("Novilhas (12-24m)", "F", 12, 24, 320),
            ("Garrotes (12-24m)", "M", 12, 24, 330),
            ("Matrizes Ativas", "F", 24, 120, 420),
            ("Vacas de Descarte", "F", 36, 120, 430),
            ("Touros", "M", 36, 120, 450),
        ]
        categorias = {}
        for nome, sexo, idade_min, idade_max, peso in categorias_config:
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
        self.stdout.write("Categorias de animais garantidas.")
        return categorias

    def _garantir_inventario(self, propriedade, categorias, ano):
        data_ref = date(ano, 1, 31)
        inventario_config = [
            ("Bezerras (0-12m)", 320),
            ("Bezerros (0-12m)", 340),
            ("Novilhas (12-24m)", 520),
            ("Garrotes (12-24m)", 510),
            ("Matrizes Ativas", 1400),
            ("Vacas de Descarte", 180),
            ("Touros", 20),
        ]
        for nome, quantidade in inventario_config:
            categoria = categorias[nome]
            InventarioRebanho.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_ref,
                defaults={
                    "quantidade": quantidade,
                    "valor_por_cabeca": Decimal("3200.00")
                    if "Matrizes" in nome
                    else Decimal("2100.00"),
                },
            )
        self.stdout.write("Inventário do rebanho preenchido.")

    def _garantir_parametros_projecao(self, propriedade):
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
        self.stdout.write("Parâmetros de projeção atualizados.")

    def _garantir_planejamento(self, propriedade, ano):
        planejamento, _ = PlanejamentoAnual.objects.update_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                "descricao": "Planejamento integrado criado automaticamente.",
                "status": "EM_ANDAMENTO",
            },
        )
        self.stdout.write(f"Planejamento {ano} configurado.")
        return planejamento

    def _garantir_cenarios(self, planejamento):
        baseline, _ = CenarioPlanejamento.objects.update_or_create(
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
        otimista, _ = CenarioPlanejamento.objects.update_or_create(
            planejamento=planejamento,
            nome="Mercado Otimista",
            defaults={
                "descricao": "Simula preços +8% com custos -3%.",
                "ajuste_preco_percentual": Decimal("8.00"),
                "ajuste_custo_percentual": Decimal("-3.00"),
                "ajuste_producao_percentual": Decimal("4.00"),
            },
        )
        return {"baseline": baseline, "otimista": otimista}

    def _garantir_atividades(self, planejamento, categorias, ano):
        atividades = [
            {
                "tipo": "IATF - rodada 1",
                "categoria": categorias["Matrizes Ativas"],
                "inicio": date(ano, 2, 10),
                "fim": date(ano, 2, 28),
                "responsavel": "Equipe Reprodução",
                "custo": Decimal("85000.00"),
                "indicador": "Taxa prenhez",
            },
            {
                "tipo": "Reforma de pasto - módulo 3",
                "categoria": None,
                "inicio": date(ano, 3, 5),
                "fim": date(ano, 4, 15),
                "responsavel": "Gestor Operações",
                "custo": Decimal("45000.00"),
                "indicador": "UA/ha",
            },
            {
                "tipo": "Venda programada de garrotes",
                "categoria": categorias["Garrotes (12-24m)"],
                "inicio": date(ano, 6, 1),
                "fim": date(ano, 6, 30),
                "responsavel": "Time Comercial",
                "custo": Decimal("5000.00"),
                "indicador": "Receita mensal",
            },
        ]
        for dados in atividades:
            AtividadePlanejada.objects.update_or_create(
                planejamento=planejamento,
                tipo_atividade=dados["tipo"],
                defaults={
                    "categoria": dados["categoria"],
                    "descricao": f"Atividade gerada automaticamente ({dados['tipo']}).",
                    "data_inicio_prevista": dados["inicio"],
                    "data_fim_prevista": dados["fim"],
                    "responsavel": dados["responsavel"],
                    "custo_previsto": dados["custo"],
                    "indicador_alvo": dados["indicador"],
                    "status": "AGENDADA",
                },
            )
        self.stdout.write("Atividades planejadas atualizadas.")

    def _garantir_metas_comerciais(self, planejamento, categorias):
        metas = [
            {
                "categoria": categorias["Garrotes (12-24m)"],
                "quantidade": 420,
                "arrobas": Decimal("6300"),
                "preco": Decimal("285.00"),
                "canal": "Frigorífico Prime",
            },
            {
                "categoria": categorias["Novilhas (12-24m)"],
                "quantidade": 180,
                "arrobas": Decimal("2700"),
                "preco": Decimal("265.00"),
                "canal": "Reposição parceira",
            },
            {
                "categoria": None,
                "quantidade": 120,
                "arrobas": Decimal("1800"),
                "preco": Decimal("190.00"),
                "canal": "Leilões regionais",
            },
        ]
        for dados in metas:
            MetaComercialPlanejada.objects.update_or_create(
                planejamento=planejamento,
                categoria=dados["categoria"],
                canal_venda=dados["canal"],
                defaults={
                    "quantidade_animais": dados["quantidade"],
                    "arrobas_totais": dados["arrobas"],
                    "preco_medio_esperado": dados["preco"],
                    "percentual_impostos": Decimal("4.50"),
                    "observacoes": "Meta criada automaticamente pela rotina seed_planejamento.",
                },
            )
        self.stdout.write("Metas comerciais garantidas.")

    def _garantir_metas_financeiras(self, planejamento):
        metas = [
            {
                "descricao": "Custo mensal de suplementação",
                "tipo": "VARIAVEL",
                "valor": Decimal("185000.00"),
                "indice": "IGP-M",
                "percentual": Decimal("4.50"),
            },
            {
                "descricao": "Programa de genética e IATF",
                "tipo": "INVESTIMENTO",
                "valor": Decimal("320000.00"),
                "indice": "",
                "percentual": Decimal("0.00"),
            },
            {
                "descricao": "Folha operacional",
                "tipo": "FIXO",
                "valor": Decimal("980000.00"),
                "indice": "IPCA",
                "percentual": Decimal("4.00"),
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
                    "observacoes": "Gerado automaticamente para compor o dashboard.",
                },
            )
        self.stdout.write("Metas financeiras garantidas.")

    def _garantir_indicadores(self, planejamento):
        indicadores = [
            {
                "codigo": "TAXA_PRENHEZ",
                "nome": "Taxa de prenhez (IATF + monta)",
                "unidade": "%",
                "valor": Decimal("88.00"),
                "eixo": "REPRODUCAO",
                "direcao": "MAIOR",
            },
            {
                "codigo": "ARROBAS_VENDIDAS",
                "nome": "Produção anual de arrobas",
                "unidade": "@",
                "valor": Decimal("11200.00"),
                "eixo": "ENGORDA",
                "direcao": "MAIOR",
            },
            {
                "codigo": "CUSTO_ARROBA",
                "nome": "Custo operacional por arroba",
                "unidade": "R$",
                "valor": Decimal("248.00"),
                "eixo": "FINANCEIRO",
                "direcao": "MENOR",
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
                    "valor_base": dados["valor"] - Decimal("5.00"),
                    "eixo_estrategico": dados["eixo"],
                    "direcao_meta": dados["direcao"],
                    "prioridade": 2,
                },
            )
        self.stdout.write("Indicadores estratégicos configurados.")

    def _garantir_movimentacoes(self, propriedade, planejamento, cenario_baseline):
        inventario_base = (
            propriedade.inventariorebanho_set.order_by("data_inventario", "id").first()
        )
        if not inventario_base:
            raise ValueError(
                "Não há inventário cadastrado para a propriedade. "
                "Execute seed_planejamento novamente após garantir inventário."
            )

        inicio = date(planejamento.ano, 1, 1)
        movimentacoes = []
        for mes in range(0, 12):
            dia = inicio + timedelta(days=mes * 30)
            movimentacoes.extend(
                [
                    {
                        "tipo": "NASCIMENTO",
                        "categoria": None,
                        "quantidade": random.randint(90, 120),
                        "data": dia,
                    },
                    {
                        "tipo": "VENDA",
                        "categoria": inventario_base.categoria,
                        "quantidade": random.randint(50, 80),
                        "preco": Decimal("285.00"),
                        "data": dia,
                    },
                    {
                        "tipo": "COMPRA",
                        "categoria": inventario_base.categoria,
                        "quantidade": random.randint(10, 20),
                        "preco": Decimal("210.00"),
                        "data": dia,
                    },
                ]
            )

        MovimentacaoProjetada.objects.filter(
            propriedade=propriedade, planejamento=planejamento
        ).delete()

        for dados in movimentacoes:
            categoria = dados["categoria"] or inventario_base.categoria
            valor_por_cabeca = dados.get("preco", Decimal("0.00"))
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                planejamento=planejamento,
                cenario=cenario_baseline,
                data_movimentacao=dados["data"],
                tipo_movimentacao=dados["tipo"],
                categoria=categoria,
                quantidade=dados["quantidade"],
                valor_por_cabeca=valor_por_cabeca if valor_por_cabeca else None,
                valor_total=(
                    valor_por_cabeca * Decimal(dados["quantidade"])
                    if valor_por_cabeca
                    else None
                ),
            )
        self.stdout.write("Movimentações projetadas geradas.")

    def _garantir_financeiro(self, propriedade, ano):
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
            nome="BB Invest Pecuária 2025",
            defaults={
                "tipo": tipo_fin,
                "descricao": "Financiamento de longo prazo para intensificação.",
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
        self.stdout.write("Dados financeiros consolidados.")

