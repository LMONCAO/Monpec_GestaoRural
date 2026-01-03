"""
Comando Django para fazer backup completo do sistema
Inclui: banco principal, tenants, arquivos media e static

Uso: 
    python manage.py backup_completo
    python manage.py backup_completo --compress
    python manage.py backup_completo --output-dir /caminho/backup
"""
from __future__ import annotations

import logging
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from gestao_rural.utils.backup_utils import (
    calcular_checksum,
    validar_integridade_backup,
    notificar_backup_falha,
    notificar_backup_sucesso,
    fazer_backup_remoto
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Faz backup completo do sistema (banco principal, tenants, media, static)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default=None,
            help='Diretório onde salvar os backups (padrão: BACKUP_DIR do settings)',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Comprimir backup completo em arquivo ZIP',
        )
        parser.add_argument(
            '--only-db',
            action='store_true',
            help='Fazer backup apenas dos bancos de dados (sem media/static)',
        )
        parser.add_argument(
            '--only-media',
            action='store_true',
            help='Fazer backup apenas dos arquivos media',
        )
        parser.add_argument(
            '--keep-days',
            type=int,
            default=30,
            help='Manter backups dos últimos X dias (padrão: 30)',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validar integridade do backup após criação (recomendado)',
        )
        parser.add_argument(
            '--remote',
            action='store_true',
            help='Enviar backup para Google Cloud Storage (requer BACKUP_GCS_BUCKET configurado)',
        )
        parser.add_argument(
            '--no-notify',
            action='store_true',
            help='Não enviar notificações por email (mesmo em caso de falha)',
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir'] or getattr(settings, 'BACKUP_DIR', None)
        if not output_dir:
            output_dir = Path(settings.BASE_DIR) / 'backups'
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        compress = options.get('compress', False)
        only_db = options.get('only_db', False)
        only_media = options.get('only_media', False)
        keep_days = options.get('keep_days', 30)
        validate = options.get('validate', True)  # Por padrão, validar
        remote = options.get('remote', False)
        no_notify = options.get('no_notify', False)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_completo_{timestamp}"
        backup_dir = output_dir / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando backup completo...'))
        self.stdout.write(f'Diretório de backup: {backup_dir}')
        
        resultados = {
            'banco_principal': False,
            'tenants': 0,
            'media': False,
            'static': False,
            'erros': []
        }
        
        try:
            # 1. Backup do banco principal
            if not only_media:
                self.stdout.write('\n[1/4] Fazendo backup do banco principal...')
                resultados['banco_principal'] = self._backup_banco_principal(backup_dir, timestamp)
            
            # 2. Backup dos tenants
            if not only_media:
                self.stdout.write('\n[2/4] Fazendo backup dos tenants...')
                resultados['tenants'] = self._backup_tenants(backup_dir, timestamp)
            
            # 3. Backup de arquivos media
            if not only_db:
                self.stdout.write('\n[3/4] Fazendo backup dos arquivos media...')
                resultados['media'] = self._backup_media(backup_dir)
            
            # 4. Backup de arquivos static (opcional, geralmente não muda)
            if not only_db and not only_media:
                self.stdout.write('\n[4/4] Fazendo backup dos arquivos static...')
                resultados['static'] = self._backup_static(backup_dir)
            
            # Criar arquivo de metadados
            self._criar_metadata(backup_dir, timestamp, resultados)
            
            # Comprimir se solicitado
            if compress:
                self.stdout.write('\n[5/5] Comprimindo backup...')
                arquivo_zip = self._comprimir_backup(backup_dir, output_dir, backup_name)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Backup comprimido: {arquivo_zip.name} '
                        f'({self._format_size(arquivo_zip.stat().st_size)})'
                    )
                )
                # Remover diretório não comprimido
                shutil.rmtree(backup_dir)
                caminho_final = arquivo_zip
            else:
                caminho_final = backup_dir
            
            # Validação de integridade
            checksum = None
            if validate and caminho_final.is_file():
                self.stdout.write('\n[6/6] Validando integridade do backup...')
                validacao = validar_integridade_backup(caminho_final)
                if validacao['valido']:
                    checksum = validacao['checksum']
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Backup íntegro (SHA256: {checksum[:16]}...)'
                        )
                    )
                else:
                    erros_validacao = '\n'.join(validacao['erros'])
                    self.stdout.write(
                        self.style.ERROR(f'✗ Backup pode estar corrompido!\n{erros_validacao}')
                    )
                    resultados['erros'].extend(validacao['erros'])
            
            # Backup remoto (Google Cloud Storage)
            backup_remoto_sucesso = False
            if remote:
                self.stdout.write('\n[7/7] Enviando backup para Google Cloud Storage...')
                resultado_remoto = fazer_backup_remoto(caminho_final)
                if resultado_remoto['sucesso']:
                    backup_remoto_sucesso = True
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Backup enviado: {resultado_remoto["url"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Falha ao enviar backup remoto: {", ".join(resultado_remoto["erros"])}'
                        )
                    )
                    resultados['erros'].extend(resultado_remoto['erros'])
            
            # Resumo
            self._mostrar_resumo(resultados, caminho_final, checksum, backup_remoto_sucesso)
            
            # Limpar backups antigos
            self._limpar_backups_antigos(output_dir, keep_days)
            
            # Notificações
            if not no_notify:
                tamanho_str = self._format_size(
                    caminho_final.stat().st_size if caminho_final.is_file() 
                    else sum(f.stat().st_size for f in caminho_final.rglob('*') if f.is_file())
                )
                notificar_backup_sucesso(tamanho_str, str(caminho_final), checksum)
            
        except Exception as e:
            erro_msg = f'Erro ao fazer backup: {e}'
            logger.exception('Erro ao fazer backup completo')
            
            # Notificar falha
            if not no_notify:
                notificar_backup_falha(erro_msg, {'tipo': 'exceção', 'traceback': str(e)})
            
            raise CommandError(erro_msg)
    
    def _backup_banco_principal(self, backup_dir: Path, timestamp: str) -> bool:
        """Faz backup do banco de dados principal"""
        try:
            db_path = Path(settings.DATABASES['default']['NAME'])
            
            if not db_path.exists():
                self.stdout.write(
                    self.style.WARNING(f'Banco principal não encontrado: {db_path}')
                )
                return False
            
            backup_db_path = backup_dir / f"db_principal_{timestamp}.sqlite3"
            shutil.copy2(db_path, backup_db_path)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Banco principal: {self._format_size(backup_db_path.stat().st_size)}'
                )
            )
            return True
            
        except Exception as e:
            erro = f'Erro ao fazer backup do banco principal: {e}'
            self.stdout.write(self.style.ERROR(erro))
            logger.exception(erro)
            return False
    
    def _backup_tenants(self, backup_dir: Path, timestamp: str) -> int:
        """Faz backup dos bancos de dados dos tenants"""
        try:
            from gestao_rural.models import TenantWorkspace
            
            tenants = TenantWorkspace.objects.filter(
                status=TenantWorkspace.Status.ATIVO
            )
            
            if not tenants.exists():
                self.stdout.write(self.style.WARNING('Nenhum tenant ativo encontrado.'))
                return 0
            
            tenants_dir = backup_dir / 'tenants'
            tenants_dir.mkdir(exist_ok=True)
            
            backups_criados = 0
            
            for tenant in tenants:
                try:
                    caminho_banco = Path(tenant.caminho_banco)
                    
                    if not caminho_banco.exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Tenant {tenant.id} ({tenant.alias}): banco não encontrado'
                            )
                        )
                        continue
                    
                    nome_backup = f"tenant_{tenant.id}_{tenant.alias}_{timestamp}.sqlite3"
                    caminho_backup = tenants_dir / nome_backup
                    
                    shutil.copy2(caminho_banco, caminho_backup)
                    
                    # Criar metadata do tenant
                    metadata = {
                        'tenant_id': tenant.id,
                        'alias': tenant.alias,
                        'assinatura_id': tenant.assinatura_id,
                        'usuario': tenant.assinatura.usuario.username if tenant.assinatura else None,
                        'data_backup': timestamp,
                        'tamanho_bytes': caminho_backup.stat().st_size,
                    }
                    
                    metadata_file = tenants_dir / f"{nome_backup}.metadata.json"
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                    self.stdout.write(
                        f'  ✓ Tenant {tenant.id} ({tenant.alias}): '
                        f'{self._format_size(caminho_backup.stat().st_size)}'
                    )
                    backups_criados += 1
                    
                except Exception as e:
                    erro = f'Erro ao fazer backup do tenant {tenant.id}: {e}'
                    self.stdout.write(self.style.ERROR(f'  ✗ {erro}'))
                    logger.exception(erro)
            
            return backups_criados
            
        except ImportError:
            self.stdout.write(
                self.style.WARNING('Modelo TenantWorkspace não encontrado. Pulando backup de tenants.')
            )
            return 0
        except Exception as e:
            erro = f'Erro ao fazer backup dos tenants: {e}'
            self.stdout.write(self.style.ERROR(erro))
            logger.exception(erro)
            return 0
    
    def _backup_media(self, backup_dir: Path) -> bool:
        """Faz backup dos arquivos media"""
        try:
            media_root = Path(settings.MEDIA_ROOT)
            
            if not media_root.exists():
                self.stdout.write(
                    self.style.WARNING(f'Diretório media não encontrado: {media_root}')
                )
                return False
            
            media_backup = backup_dir / 'media'
            
            # Copiar apenas se houver arquivos
            arquivos_media = list(media_root.rglob('*'))
            arquivos_media = [f for f in arquivos_media if f.is_file()]
            
            if not arquivos_media:
                self.stdout.write(self.style.WARNING('Nenhum arquivo media encontrado.'))
                return False
            
            self.stdout.write(f'  Copiando {len(arquivos_media)} arquivos...')
            shutil.copytree(media_root, media_backup, dirs_exist_ok=True)
            
            tamanho_total = sum(f.stat().st_size for f in media_backup.rglob('*') if f.is_file())
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Media: {len(arquivos_media)} arquivos '
                    f'({self._format_size(tamanho_total)})'
                )
            )
            return True
            
        except Exception as e:
            erro = f'Erro ao fazer backup dos arquivos media: {e}'
            self.stdout.write(self.style.ERROR(erro))
            logger.exception(erro)
            return False
    
    def _backup_static(self, backup_dir: Path) -> bool:
        """Faz backup dos arquivos static coletados"""
        try:
            static_root = Path(settings.STATIC_ROOT)
            
            if not static_root.exists():
                self.stdout.write(
                    self.style.WARNING(f'Diretório static não encontrado: {static_root}')
                )
                return False
            
            static_backup = backup_dir / 'staticfiles'
            
            arquivos_static = list(static_root.rglob('*'))
            arquivos_static = [f for f in arquivos_static if f.is_file()]
            
            if not arquivos_static:
                self.stdout.write(self.style.WARNING('Nenhum arquivo static encontrado.'))
                return False
            
            self.stdout.write(f'  Copiando {len(arquivos_static)} arquivos...')
            shutil.copytree(static_root, static_backup, dirs_exist_ok=True)
            
            tamanho_total = sum(f.stat().st_size for f in static_backup.rglob('*') if f.is_file())
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Static: {len(arquivos_static)} arquivos '
                    f'({self._format_size(tamanho_total)})'
                )
            )
            return True
            
        except Exception as e:
            erro = f'Erro ao fazer backup dos arquivos static: {e}'
            self.stdout.write(self.style.ERROR(erro))
            logger.exception(erro)
            return False
    
    def _criar_metadata(self, backup_dir: Path, timestamp: str, resultados: Dict):
        """Cria arquivo de metadados do backup"""
        metadata = {
            'data_backup': timestamp,
            'data_backup_iso': datetime.now().isoformat(),
            'versao_django': self._get_django_version(),
            'resultados': resultados,
            'configuracoes': {
                'base_dir': str(settings.BASE_DIR),
                'media_root': str(settings.MEDIA_ROOT),
                'static_root': str(settings.STATIC_ROOT),
            }
        }
        
        metadata_file = backup_dir / 'backup_metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _comprimir_backup(self, backup_dir: Path, output_dir: Path, backup_name: str) -> Path:
        """Comprime o diretório de backup em ZIP"""
        arquivo_zip = output_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(arquivo_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for arquivo in backup_dir.rglob('*'):
                if arquivo.is_file():
                    # Manter estrutura de diretórios relativa ao backup_dir
                    arcname = arquivo.relative_to(backup_dir)
                    zipf.write(arquivo, arcname)
        
        return arquivo_zip
    
    def _mostrar_resumo(self, resultados: Dict, caminho_final: Path, 
                        checksum: Optional[str] = None, backup_remoto: bool = False):
        """Mostra resumo do backup"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('BACKUP CONCLUÍDO COM SUCESSO!'))
        self.stdout.write('='*60)
        
        if resultados['banco_principal']:
            self.stdout.write('✓ Banco principal: OK')
        else:
            self.stdout.write(self.style.ERROR('✗ Banco principal: FALHOU'))
        
        if resultados['tenants'] > 0:
            self.stdout.write(f'✓ Tenants: {resultados["tenants"]} backups criados')
        else:
            self.stdout.write(self.style.WARNING('⚠ Tenants: Nenhum backup criado'))
        
        if resultados['media']:
            self.stdout.write('✓ Arquivos media: OK')
        else:
            self.stdout.write(self.style.WARNING('⚠ Arquivos media: Não incluídos'))
        
        if resultados['static']:
            self.stdout.write('✓ Arquivos static: OK')
        else:
            self.stdout.write(self.style.WARNING('⚠ Arquivos static: Não incluídos'))
        
        if resultados['erros']:
            self.stdout.write(self.style.ERROR(f'\n✗ Erros encontrados: {len(resultados["erros"])}'))
            for erro in resultados['erros']:
                self.stdout.write(self.style.ERROR(f'  - {erro}'))
        
        self.stdout.write(f'\nLocalização: {caminho_final}')
        
        if caminho_final.is_file():
            tamanho = caminho_final.stat().st_size
        else:
            tamanho = sum(f.stat().st_size for f in caminho_final.rglob('*') if f.is_file())
        
        self.stdout.write(f'Tamanho total: {self._format_size(tamanho)}')
        
        if checksum:
            self.stdout.write(f'Checksum (SHA256): {checksum}')
        
        if backup_remoto:
            self.stdout.write(self.style.SUCCESS('✓ Backup remoto: Enviado com sucesso'))
        
        self.stdout.write('='*60 + '\n')
    
    def _limpar_backups_antigos(self, backup_dir: Path, keep_days: int):
        """Remove backups mais antigos que X dias"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removidos = 0
        
        # Limpar diretórios de backup
        for item in backup_dir.iterdir():
            if item.is_dir() and item.name.startswith('backup_completo_'):
                try:
                    # Tentar extrair data do nome
                    data_str = item.name.replace('backup_completo_', '')
                    data_backup = datetime.strptime(data_str[:15], '%Y%m%d_%H%M%S')
                    
                    if data_backup < cutoff_date:
                        shutil.rmtree(item)
                        removidos += 1
                except (ValueError, OSError) as e:
                    logger.warning(f'Erro ao remover backup antigo {item}: {e}')
        
        # Limpar arquivos ZIP
        for arquivo in backup_dir.glob('backup_completo_*.zip'):
            try:
                if arquivo.stat().st_mtime < cutoff_date.timestamp():
                    arquivo.unlink()
                    removidos += 1
            except Exception as e:
                logger.warning(f'Erro ao remover backup ZIP antigo {arquivo}: {e}')
        
        if removidos > 0:
            self.stdout.write(
                self.style.WARNING(f'\nBackups antigos removidos: {removidos}')
            )
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def _get_django_version(self) -> str:
        """Retorna versão do Django"""
        try:
            import django
            return django.get_version()
        except:
            return 'desconhecida'

