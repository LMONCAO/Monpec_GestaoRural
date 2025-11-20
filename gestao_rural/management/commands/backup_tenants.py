"""
Comando Django para fazer backup dos bancos de dados dos tenants
Uso: python manage.py backup_tenants [--output-dir DIR] [--tenant-id ID]
"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gestao_rural.models import TenantWorkspace

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Faz backup dos bancos de dados dos tenants ativos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Diretório onde salvar os backups (padrão: BACKUP_DIR do settings)',
        )
        parser.add_argument(
            '--tenant-id',
            type=int,
            default=None,
            help='ID do tenant específico para backup (opcional)',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Comprimir backups em arquivo ZIP',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir'] or getattr(settings, 'BACKUP_DIR', None)
        if not output_dir:
            output_dir = Path(settings.BASE_DIR) / 'backups'
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tenant_id = options.get('tenant_id')
        compress = options.get('compress', False)
        
        # Buscar tenants
        if tenant_id:
            tenants = TenantWorkspace.objects.filter(id=tenant_id, status=TenantWorkspace.Status.ATIVO)
        else:
            tenants = TenantWorkspace.objects.filter(status=TenantWorkspace.Status.ATIVO)
        
        if not tenants.exists():
            self.stdout.write(self.style.WARNING('Nenhum tenant ativo encontrado.'))
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backups_criados = 0
        erros = []
        
        for tenant in tenants:
            try:
                caminho_banco = Path(tenant.caminho_banco)
                
                if not caminho_banco.exists():
                    self.stdout.write(
                        self.style.WARNING(
                            f'Banco de dados não encontrado para tenant {tenant.id}: {caminho_banco}'
                        )
                    )
                    continue
                
                # Nome do arquivo de backup
                nome_backup = f"tenant_{tenant.id}_{tenant.alias}_{timestamp}.sqlite3"
                caminho_backup = output_dir / nome_backup
                
                # Copiar arquivo
                shutil.copy2(caminho_banco, caminho_backup)
                
                # Comprimir se solicitado
                if compress:
                    import zipfile
                    caminho_zip = output_dir / f"{nome_backup}.zip"
                    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(caminho_backup, nome_backup)
                    caminho_backup.unlink()  # Remove arquivo não comprimido
                    caminho_final = caminho_zip
                else:
                    caminho_final = caminho_backup
                
                # Criar arquivo de metadados
                metadata = {
                    'tenant_id': tenant.id,
                    'alias': tenant.alias,
                    'assinatura_id': tenant.assinatura_id,
                    'usuario': tenant.assinatura.usuario.username,
                    'data_backup': timestamp,
                    'tamanho_bytes': caminho_final.stat().st_size,
                    'comprimido': compress,
                }
                
                import json
                metadata_file = output_dir / f"{nome_backup}.metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Backup criado: {caminho_final.name} '
                        f'({self._format_size(caminho_final.stat().st_size)})'
                    )
                )
                backups_criados += 1
                
            except Exception as e:
                erro_msg = f'Erro ao fazer backup do tenant {tenant.id}: {e}'
                self.stdout.write(self.style.ERROR(erro_msg))
                logger.exception(erro_msg)
                erros.append((tenant.id, str(e)))
        
        # Resumo
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total de backups criados: {backups_criados}'))
        if erros:
            self.stdout.write(self.style.ERROR(f'Erros: {len(erros)}'))
            for tenant_id, erro in erros:
                self.stdout.write(self.style.ERROR(f'  Tenant {tenant_id}: {erro}'))
        
        # Limpar backups antigos (manter últimos 30 dias)
        self._limpar_backups_antigos(output_dir, dias=30)
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _limpar_backups_antigos(self, backup_dir: Path, dias: int = 30):
        """Remove backups mais antigos que X dias"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=dias)
        removidos = 0
        
        for arquivo in backup_dir.glob('tenant_*.sqlite3*'):
            try:
                if arquivo.stat().st_mtime < cutoff_date.timestamp():
                    arquivo.unlink()
                    # Remover metadata se existir
                    metadata_file = backup_dir / f"{arquivo.stem}.metadata.json"
                    if metadata_file.exists():
                        metadata_file.unlink()
                    removidos += 1
            except Exception as e:
                logger.warning(f'Erro ao remover backup antigo {arquivo}: {e}')
        
        if removidos > 0:
            self.stdout.write(
                self.style.WARNING(f'Backups antigos removidos: {removidos}')
            )






