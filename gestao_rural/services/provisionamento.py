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


def _registrar_database(alias: str, nome_banco: str) -> None:
    """Registra um banco PostgreSQL para o tenant."""
    from django.conf import settings
    import os
    
    # Usar as mesmas credenciais do banco padrão, mas com nome de banco diferente
    default_db = settings.DATABASES['default']
    settings.DATABASES[alias] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': nome_banco,
        'USER': default_db.get('USER', os.getenv('DB_USER', '')),
        'PASSWORD': default_db.get('PASSWORD', os.getenv('DB_PASSWORD', '')),
        'HOST': default_db.get('HOST', os.getenv('DB_HOST', 'localhost')),
        'PORT': default_db.get('PORT', os.getenv('DB_PORT', '5432')),
        'OPTIONS': default_db.get('OPTIONS', {}),
        'CONN_MAX_AGE': default_db.get('CONN_MAX_AGE', 600),
    }
    connections.databases[alias] = settings.DATABASES[alias]


def _provisionar_workspace_postgres(assinatura: AssinaturaCliente) -> ProvisionamentoResultado:
    """Provisiona workspace usando PostgreSQL (produção)."""
    workspace = _obter_ou_criar_workspace(assinatura)
    if workspace.status == TenantWorkspace.Status.ATIVO:
        return ProvisionamentoResultado(
            workspace=workspace,
            sucesso=True,
            mensagem="Workspace já está ativo."
        )

    workspace.status = TenantWorkspace.Status.PROVISIONANDO
    workspace.save(update_fields=['status', 'atualizado_em'])

    nome_banco = workspace.caminho_banco  # Agora é o nome do banco PostgreSQL

    try:
        # Criar banco PostgreSQL se não existir
        # Nota: Precisa usar conexão ao banco 'postgres' para criar novos bancos
        from django.db import connection
        import psycopg2

        # Conectar ao banco 'postgres' para criar novos bancos
        default_db = settings.DATABASES['default']
        conn_admin = psycopg2.connect(
            host=default_db.get('HOST', 'localhost'),
            port=default_db.get('PORT', '5432'),
            database='postgres',  # Conectar ao banco padrão para criar novos
            user=default_db.get('USER', ''),
            password=default_db.get('PASSWORD', '')
        )
        conn_admin.autocommit = True  # Necessário para CREATE DATABASE

        try:
            with conn_admin.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [nome_banco])
                if not cursor.fetchone():
                    # Criar banco de dados
                    cursor.execute(f'CREATE DATABASE "{nome_banco}"')
                    logger.info(f"Banco de dados PostgreSQL '{nome_banco}' criado para tenant {workspace.alias}")
        finally:
            conn_admin.close()

        # Registrar conexão do banco
        _registrar_database(workspace.alias, nome_banco)

        # Aplicar migrations no banco do tenant
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
        mensagem = f"Falha ao provisionar workspace: {str(exc)}"
        workspace.status = TenantWorkspace.Status.ERRO
        workspace.ultimo_erro = mensagem
        workspace.save(update_fields=['status', 'ultimo_erro', 'atualizado_em'])
        logger.exception("Falha ao provisionar workspace %s para assinatura %s: %s",
                        workspace.alias, assinatura.pk, mensagem)
        return ProvisionamentoResultado(workspace=workspace, sucesso=False, mensagem=mensagem)


def _provisionar_workspace_sqlite(assinatura: AssinaturaCliente) -> ProvisionamentoResultado:
    """Provisiona workspace usando SQLite (desenvolvimento)."""
    workspace = _obter_ou_criar_workspace(assinatura)

    # Em desenvolvimento com SQLite, apenas marcar como ativo sem criar banco físico
    if workspace.status != TenantWorkspace.Status.ATIVO:
        workspace.status = TenantWorkspace.Status.ATIVO
        workspace.provisionado_em = timezone.now()
        workspace.save(update_fields=['status', 'provisionado_em', 'atualizado_em'])

    mensagem = "Workspace provisionado com sucesso (SQLite - desenvolvimento)."
    logger.info("Workspace %s provisionado para assinatura %s (modo desenvolvimento)",
               workspace.alias, assinatura.pk)

    return ProvisionamentoResultado(workspace=workspace, sucesso=True, mensagem=mensagem)


def _obter_ou_criar_workspace(assinatura: AssinaturaCliente) -> TenantWorkspace:
    """Obtém ou cria um workspace para o tenant usando PostgreSQL."""
    alias = assinatura.alias_tenant
    # Usar nome de banco PostgreSQL em vez de caminho de arquivo SQLite
    nome_banco = f"monpec_tenant_{alias}"

    workspace, _ = TenantWorkspace.objects.get_or_create(
        assinatura=assinatura,
        defaults={
            'alias': alias,
            'caminho_banco': nome_banco,  # Agora armazena nome do banco PostgreSQL
        },
    )

    if workspace.alias != alias or workspace.caminho_banco != nome_banco:
        workspace.alias = alias
        workspace.caminho_banco = nome_banco
        workspace.save(update_fields=['alias', 'caminho_banco', 'atualizado_em'])

    return workspace




def provisionar_workspace(assinatura: AssinaturaCliente) -> ProvisionamentoResultado:
    """
    Provisiona workspace para uma assinatura.
    Suporta tanto PostgreSQL (produção) quanto SQLite (desenvolvimento).
    """
    # Verificar se estamos em modo de desenvolvimento (SQLite)
    is_sqlite = settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'

    if is_sqlite:
        return _provisionar_workspace_sqlite(assinatura)
    else:
        return _provisionar_workspace_postgres(assinatura)


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
        nome_banco = workspace.caminho_banco  # Agora é o nome do banco PostgreSQL
        
        # Verificar se o banco existe usando conexão ao banco postgres
        try:
            import psycopg2
            default_db = settings.DATABASES['default']
            conn_check = psycopg2.connect(
                host=default_db.get('HOST', 'localhost'),
                port=default_db.get('PORT', '5432'),
                database='postgres',
                user=default_db.get('USER', ''),
                password=default_db.get('PASSWORD', '')
            )
            try:
                with conn_check.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [nome_banco])
                    if not cursor.fetchone():
                        logger.warning("Banco PostgreSQL '%s' não encontrado para workspace %s.", nome_banco, workspace.alias)
                        continue
            finally:
                conn_check.close()
        except Exception as e:
            logger.warning("Erro ao verificar banco '%s' para workspace %s: %s", nome_banco, workspace.alias, e)
            continue

        try:
            _registrar_database(workspace.alias, nome_banco)
        except Exception:  # pragma: no cover - log de erro
            logger.exception("Erro ao registrar workspace %s durante inicialização.", workspace.alias)













