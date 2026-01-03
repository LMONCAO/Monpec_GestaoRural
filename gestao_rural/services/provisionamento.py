from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from django.utils import timezone

from gestao_rural.models import AssinaturaCliente, TenantWorkspace

logger = logging.getLogger(__name__)


@dataclass
class ProvisionamentoResultado:
    workspace: TenantWorkspace
    sucesso: bool
    mensagem: str = ""


def _registrar_database(alias: str, caminho: Path) -> None:
    settings.DATABASES[alias] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(caminho),
    }
    connections.databases[alias] = settings.DATABASES[alias]


def _obter_ou_criar_workspace(assinatura: AssinaturaCliente) -> TenantWorkspace:
    alias = assinatura.alias_tenant
    caminho = Path(settings.TENANT_DATABASE_DIR) / f"{alias}.sqlite3"

    workspace, _ = TenantWorkspace.objects.get_or_create(
        assinatura=assinatura,
        defaults={
            'alias': alias,
            'caminho_banco': str(caminho),
        },
    )

    if workspace.alias != alias or workspace.caminho_banco != str(caminho):
        workspace.alias = alias
        workspace.caminho_banco = str(caminho)
        workspace.save(update_fields=['alias', 'caminho_banco', 'atualizado_em'])

    return workspace


def provisionar_workspace(assinatura: AssinaturaCliente) -> ProvisionamentoResultado:
    workspace = _obter_ou_criar_workspace(assinatura)

    if workspace.status == TenantWorkspace.Status.ATIVO:
        return ProvisionamentoResultado(workspace=workspace, sucesso=True, mensagem="Workspace já provisionado.")

    workspace.status = TenantWorkspace.Status.PROVISIONANDO
    workspace.ultimo_erro = ""
    workspace.save(update_fields=['status', 'ultimo_erro', 'atualizado_em'])

    caminho = Path(workspace.caminho_banco)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    try:
        _registrar_database(workspace.alias, caminho)
        if caminho.exists():
            caminho.unlink()

        call_command(
            'migrate',
            database=workspace.alias,
            interactive=False,
            run_syncdb=True,
            verbosity=0,
        )

        workspace.status = TenantWorkspace.Status.ATIVO
        workspace.provisionado_em = timezone.now()
        workspace.save(update_fields=['status', 'provisionado_em', 'atualizado_em'])
        mensagem = "Banco provisionado com sucesso."
        logger.info("Workspace %s provisionado para assinatura %s", workspace.alias, assinatura.pk)
        return ProvisionamentoResultado(workspace=workspace, sucesso=True, mensagem=mensagem)
    except Exception as exc:  # pragma: no cover - log de erro
        mensagem = f"Falha ao provisionar workspace: {exc}"
        logger.exception(mensagem)
        workspace.marcar_erro(mensagem)
        return ProvisionamentoResultado(workspace=workspace, sucesso=False, mensagem=mensagem)


def registrar_workspaces_existentes() -> None:
    """Recarrega workspaces ativos na inicialização do Django."""
    try:
        ativos = TenantWorkspace.objects.filter(
            status__in=[
                TenantWorkspace.Status.ATIVO,
                TenantWorkspace.Status.PROVISIONANDO,
            ]
        )
    except Exception:
        return

    for workspace in ativos:
        caminho = Path(workspace.caminho_banco)
        if not caminho.exists():
            logger.warning("Arquivo de banco %s não encontrado para workspace %s.", caminho, workspace.alias)
            continue

        try:
            _registrar_database(workspace.alias, caminho)
        except Exception:  # pragma: no cover - log de erro
            logger.exception("Erro ao registrar workspace %s durante inicialização.", workspace.alias)













