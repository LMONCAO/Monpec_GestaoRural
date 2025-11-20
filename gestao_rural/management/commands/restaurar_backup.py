"""
Comando Django para restaurar backup de um tenant
Uso: python manage.py restaurar_backup --backup-file ARQUIVO [--tenant-id ID]
"""
from __future__ import annotations

import logging
import shutil
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gestao_rural.models import TenantWorkspace

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Restaura backup de um tenant'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-file',
            type=str,
            required=True,
            help='Caminho do arquivo de backup (.sqlite3 ou .zip)',
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='ID do tenant para restaurar (opcional, tenta detectar do backup)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força restauração mesmo se tenant já tiver banco ativo',
        )

    def handle(self, *args, **options):
        backup_file = Path(options['backup_file'])
        tenant_id = options.get('tenant_id')
        force = options.get('force', False)
        
        if not backup_file.exists():
            raise CommandError(f'Arquivo de backup não encontrado: {backup_file}')
        
        # Descomprimir se necessário
        if backup_file.suffix == '.zip':
            import zipfile
            import tempfile
            
            temp_dir = Path(tempfile.mkdtemp())
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_dir)
                    # Procurar arquivo .sqlite3
                    sqlite_files = list(temp_dir.glob('*.sqlite3'))
                    if not sqlite_files:
                        raise CommandError('Nenhum arquivo .sqlite3 encontrado no ZIP')
                    backup_file = sqlite_files[0]
            except Exception as e:
                raise CommandError(f'Erro ao descomprimir backup: {e}')
        
        # Tentar detectar tenant_id do metadata ou nome do arquivo
        if not tenant_id:
            # Procurar arquivo de metadata
            metadata_file = backup_file.parent / f"{backup_file.stem}.metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    tenant_id = metadata.get('tenant_id')
            
            # Se ainda não encontrou, tentar do nome do arquivo
            if not tenant_id:
                partes = backup_file.stem.split('_')
                if len(partes) >= 2 and partes[0] == 'tenant':
                    try:
                        tenant_id = int(partes[1])
                    except ValueError:
                        pass
        
        if not tenant_id:
            raise CommandError(
                'Não foi possível detectar o tenant_id. '
                'Use --tenant-id para especificar.'
            )
        
        # Buscar tenant
        try:
            tenant = TenantWorkspace.objects.get(id=tenant_id)
        except TenantWorkspace.DoesNotExist:
            raise CommandError(f'Tenant {tenant_id} não encontrado.')
        
        # Verificar se já existe banco
        caminho_banco = Path(tenant.caminho_banco)
        if caminho_banco.exists() and not force:
            raise CommandError(
                f'Banco de dados já existe para tenant {tenant_id}. '
                'Use --force para sobrescrever.'
            )
        
        # Fazer backup do banco atual se existir
        if caminho_banco.exists():
            backup_antigo = caminho_banco.parent / f"{caminho_banco.name}.backup_antes_restauracao"
            shutil.copy2(caminho_banco, backup_antigo)
            self.stdout.write(
                self.style.WARNING(
                    f'Backup do banco atual criado: {backup_antigo.name}'
                )
            )
        
        # Restaurar
        try:
            caminho_banco.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, caminho_banco)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Backup restaurado com sucesso para tenant {tenant_id}!\n'
                    f'Banco: {caminho_banco}'
                )
            )
        except Exception as e:
            raise CommandError(f'Erro ao restaurar backup: {e}')







