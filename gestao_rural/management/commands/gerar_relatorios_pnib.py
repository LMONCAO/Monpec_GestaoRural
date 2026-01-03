import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from gestao_rural.models import (
    Propriedade,
    AnimalIndividual,
    MovimentacaoIndividual,
)


class Command(BaseCommand):
    help = "Gera relatórios PNIB (Identificação, Movimentação e Sanitário) e armazena para auditoria."

    def add_arguments(self, parser):
        parser.add_argument(
            "--propriedade",
            type=int,
            help="ID da propriedade específica. Se omitido, gera para todas.",
        )

    def handle(self, *args, **options):
        target_id = options.get("propriedade")
        propriedades = (
            Propriedade.objects.filter(id=target_id)
            if target_id
            else Propriedade.objects.all()
        )

        if not propriedades.exists():
            self.stdout.write(self.style.WARNING("Nenhuma propriedade encontrada para gerar relatórios."))
            return

        exec_time = timezone.now()
        base_dir = Path(getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media"))
        relatorio_raiz = base_dir / "reports" / "pnib" / exec_time.strftime("%Y%m%d")
        relatorio_raiz.mkdir(parents=True, exist_ok=True)

        for propriedade in propriedades:
            slug = slugify(propriedade.nome_propriedade) or f"fazenda-{propriedade.id}"
            destino = relatorio_raiz / f"{propriedade.id}_{slug}"
            destino.mkdir(parents=True, exist_ok=True)

            self._gerar_identificacao(propriedade, destino, exec_time)
            self._gerar_movimentacao(propriedade, destino, exec_time)
            self._gerar_sanitario(propriedade, destino, exec_time)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Relatórios PNIB gerados para {propriedade.nome_propriedade} em {destino}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Geração de relatórios PNIB concluída."))

    def _gerar_identificacao(self, propriedade, destino, exec_time):
        arquivo = destino / "identificacao_individual.csv"
        campos = [
            "numero_brinco",
            "codigo_sisbov",
            "codigo_eletronico",
            "data_identificacao",
            "data_nascimento",
            "categoria",
            "sexo",
            "raca",
            "peso_atual_kg",
            "status",
            "status_sanitario",
            "lote_atual",
            "data_saida",
            "motivo_saida",
            "responsavel_tecnico",
        ]
        animais = (
            AnimalIndividual.objects.filter(propriedade=propriedade)
            .select_related("categoria", "lote_atual", "lote_atual__sessao", "responsavel_tecnico")
            .order_by("numero_brinco")
        )
        with arquivo.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["RELATÓRIO DE IDENTIFICAÇÃO INDIVIDUAL PNIB"])
            writer.writerow([f"Propriedade: {propriedade.nome_propriedade}"])
            writer.writerow([f"Gerado em: {exec_time.strftime('%d/%m/%Y %H:%M')}"])
            writer.writerow([])
            writer.writerow(campos)

            for animal in animais:
                writer.writerow(
                    [
                        animal.numero_brinco,
                        animal.codigo_sisbov or "",
                        animal.codigo_eletronico or "",
                        animal.data_identificacao.strftime("%Y-%m-%d") if animal.data_identificacao else "",
                        animal.data_nascimento.strftime("%Y-%m-%d") if animal.data_nascimento else "",
                        animal.categoria.nome if animal.categoria else "",
                        animal.get_sexo_display(),
                        animal.raca or "",
                        f"{animal.peso_atual_kg:.2f}" if animal.peso_atual_kg else "",
                        animal.get_status_display(),
                        animal.get_status_sanitario_display(),
                        animal.lote_atual.nome if animal.lote_atual else "",
                        animal.data_saida.strftime("%Y-%m-%d") if animal.data_saida else "",
                        animal.motivo_saida or "",
                        animal.responsavel_tecnico.get_full_name()
                        if animal.responsavel_tecnico
                        else "",
                    ]
                )

    def _gerar_movimentacao(self, propriedade, destino, exec_time):
        arquivo = destino / "movimentacoes.csv"
        campos = [
            "data_movimentacao",
            "numero_brinco",
            "codigo_sisbov",
            "tipo_movimentacao",
            "propriedade_origem",
            "propriedade_destino",
            "quantidade_animais",
            "peso_kg",
            "valor",
            # Campos de documento foram removidos na versão atual
            "numero_documento",
            "documento_emissor",
            "data_documento",
            "responsavel",
            "motivo_detalhado",
            "observacoes",
        ]
        movimentos = (
            MovimentacaoIndividual.objects.filter(animal__propriedade=propriedade)
            .select_related(
                "animal",
                "animal__categoria",
                "propriedade_origem",
                "propriedade_destino",
                "responsavel",
            )
            .order_by("-data_movimentacao", "animal__numero_brinco")
        )

        with arquivo.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["RELATÓRIO DE MOVIMENTAÇÃO PNIB"])
            writer.writerow([f"Propriedade: {propriedade.nome_propriedade}"])
            writer.writerow([f"Gerado em: {exec_time.strftime('%d/%m/%Y %H:%M')}"])
            writer.writerow([])
            writer.writerow(campos)

            for mov in movimentos:
                writer.writerow(
                    [
                        mov.data_movimentacao.strftime("%Y-%m-%d"),
                        mov.animal.numero_brinco,
                        mov.animal.codigo_sisbov or "",
                        mov.get_tipo_movimentacao_display(),
                        mov.propriedade_origem.nome_propriedade if mov.propriedade_origem else "",
                        mov.propriedade_destino.nome_propriedade if mov.propriedade_destino else "",
                        mov.quantidade_animais,
                        f"{mov.peso_kg:.2f}" if mov.peso_kg else "",
                        f"{mov.valor:.2f}" if mov.valor else "",
                        mov.numero_documento or "",
                        mov.documento_emissor or "",
                        mov.data_documento.strftime("%Y-%m-%d") if mov.data_documento else "",
                        mov.responsavel.get_full_name() if mov.responsavel else "",
                        mov.motivo_detalhado or "",
                        mov.observacoes or "",
                    ]
                )

    def _gerar_sanitario(self, propriedade, destino, exec_time):
        arquivo = destino / "status_sanitario.csv"
        campos = [
            "numero_brinco",
            "codigo_sisbov",
            "status_sanitario",
            "data_identificacao",
            "data_saida",
            "motivo_saida",
            "responsavel_tecnico",
        ]
        animais = (
            AnimalIndividual.objects.filter(propriedade=propriedade)
            .select_related("responsavel_tecnico")
            .order_by("numero_brinco")
        )

        with arquivo.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["RELATÓRIO SANITÁRIO PNIB"])
            writer.writerow([f"Propriedade: {propriedade.nome_propriedade}"])
            writer.writerow([f"Gerado em: {exec_time.strftime('%d/%m/%Y %H:%M')}"])
            writer.writerow([])
            writer.writerow(campos)

            for animal in animais:
                writer.writerow(
                    [
                        animal.numero_brinco,
                        animal.codigo_sisbov or "",
                        animal.get_status_sanitario_display(),
                        animal.data_identificacao.strftime("%Y-%m-%d") if animal.data_identificacao else "",
                        animal.data_saida.strftime("%Y-%m-%d") if animal.data_saida else "",
                        animal.motivo_saida or "",
                        animal.responsavel_tecnico.get_full_name()
                        if animal.responsavel_tecnico
                        else "",
                    ]
                )

