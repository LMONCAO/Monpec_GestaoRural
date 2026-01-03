"""
Comando Django para verificar status dos backups
Mostra informações sobre últimos backups, tamanhos, próximos agendamentos, etc.

Uso: 
    python manage.py backup_status
    python manage.py backup_status --detailed
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Mostra status dos backups do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostrar informações detalhadas',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Saída em formato JSON',
        )

    def handle(self, *args, **options):
        backup_dir = Path(getattr(settings, 'BACKUP_DIR', None) or (settings.BASE_DIR / 'backups'))
        
        if not backup_dir.exists():
            if options['json']:
                self.stdout.write(json.dumps({
                    'status': 'error',
                    'message': 'Diretório de backups não existe',
                    'backup_dir': str(backup_dir)
                }))
            else:
                self.stdout.write(self.style.ERROR('❌ Diretório de backups não existe!'))
                self.stdout.write(f'   Caminho: {backup_dir}')
            return
        
        # Coletar informações
        info = self._coletar_informacoes(backup_dir)
        
        if options['json']:
            self.stdout.write(json.dumps(info, indent=2, default=str))
        else:
            self._mostrar_status(info, options.get('detailed', False))

    def _coletar_informacoes(self, backup_dir: Path) -> Dict:
        """Coleta informações sobre os backups"""
        backups = []
        total_size = 0
        
        # Procurar backups (diretórios e arquivos ZIP)
        for item in backup_dir.iterdir():
            if item.is_dir() and item.name.startswith('backup_completo_'):
                try:
                    # Tentar extrair data do nome
                    data_str = item.name.replace('backup_completo_', '')
                    data_backup = datetime.strptime(data_str[:15], '%Y%m%d_%H%M%S')
                    
                    tamanho = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                    total_size += tamanho
                    
                    backups.append({
                        'tipo': 'diretorio',
                        'nome': item.name,
                        'data': data_backup,
                        'tamanho': tamanho,
                        'caminho': str(item)
                    })
                except (ValueError, OSError):
                    pass
            
            elif item.is_file() and item.suffix == '.zip' and item.name.startswith('backup_completo_'):
                try:
                    data_str = item.name.replace('backup_completo_', '').replace('.zip', '')
                    data_backup = datetime.strptime(data_str[:15], '%Y%m%d_%H%M%S')
                    
                    tamanho = item.stat().st_size
                    total_size += tamanho
                    
                    backups.append({
                        'tipo': 'zip',
                        'nome': item.name,
                        'data': data_backup,
                        'tamanho': tamanho,
                        'caminho': str(item)
                    })
                except (ValueError, OSError):
                    pass
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['data'], reverse=True)
        
        # Calcular estatísticas
        ultimo_backup = backups[0] if backups else None
        total_backups = len(backups)
        
        # Verificar espaço em disco
        import shutil
        statvfs = shutil.disk_usage(backup_dir)
        espaco_total = statvfs.total
        espaco_usado = statvfs.used
        espaco_livre = statvfs.free
        percentual_usado = (espaco_usado / espaco_total) * 100 if espaco_total > 0 else 0
        
        return {
            'status': 'ok',
            'backup_dir': str(backup_dir),
            'total_backups': total_backups,
            'ultimo_backup': {
                'data': ultimo_backup['data'].isoformat() if ultimo_backup else None,
                'tipo': ultimo_backup['tipo'] if ultimo_backup else None,
                'tamanho': ultimo_backup['tamanho'] if ultimo_backup else 0,
                'idade_horas': (datetime.now() - ultimo_backup['data']).total_seconds() / 3600 if ultimo_backup else None
            },
            'tamanho_total': total_size,
            'espaco_disco': {
                'total': espaco_total,
                'usado': espaco_usado,
                'livre': espaco_livre,
                'percentual_usado': round(percentual_usado, 2)
            },
            'backups_recentes': [
                {
                    'nome': b['nome'],
                    'data': b['data'].isoformat(),
                    'tipo': b['tipo'],
                    'tamanho': b['tamanho']
                }
                for b in backups[:5]
            ]
        }

    def _mostrar_status(self, info: Dict, detailed: bool):
        """Mostra status formatado"""
        self.stdout.write(self.style.SUCCESS('📊 STATUS DOS BACKUPS'))
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # Informações gerais
        self.stdout.write(f'📁 Diretório: {info["backup_dir"]}')
        self.stdout.write(f'📦 Total de backups: {info["total_backups"]}')
        self.stdout.write('')
        
        # Último backup
        if info['ultimo_backup']['data']:
            ultimo = info['ultimo_backup']
            idade_horas = ultimo['idade_horas']
            
            self.stdout.write(self.style.SUCCESS('✅ Último backup:'))
            self.stdout.write(f'   Data: {ultimo["data"]}')
            self.stdout.write(f'   Tipo: {ultimo["tipo"]}')
            self.stdout.write(f'   Tamanho: {self._format_size(ultimo["tamanho"])}')
            
            if idade_horas < 24:
                self.stdout.write(self.style.SUCCESS(f'   Idade: {idade_horas:.1f} horas (OK)'))
            elif idade_horas < 48:
                self.stdout.write(self.style.WARNING(f'   Idade: {idade_horas:.1f} horas (Atenção)'))
            else:
                self.stdout.write(self.style.ERROR(f'   Idade: {idade_horas:.1f} horas (CRÍTICO)'))
        else:
            self.stdout.write(self.style.ERROR('❌ Nenhum backup encontrado!'))
        
        self.stdout.write('')
        
        # Espaço em disco
        espaco = info['espaco_disco']
        self.stdout.write('💾 Espaço em disco:')
        self.stdout.write(f'   Total: {self._format_size(espaco["total"])}')
        self.stdout.write(f'   Usado: {self._format_size(espaco["usado"])} ({espaco["percentual_usado"]}%)')
        self.stdout.write(f'   Livre: {self._format_size(espaco["livre"])}')
        
        if espaco['percentual_usado'] > 90:
            self.stdout.write(self.style.ERROR('   ⚠️  Espaço crítico!'))
        elif espaco['percentual_usado'] > 80:
            self.stdout.write(self.style.WARNING('   ⚠️  Espaço baixo'))
        
        self.stdout.write('')
        
        # Backups recentes
        if detailed and info['backups_recentes']:
            self.stdout.write('📋 Últimos 5 backups:')
            for backup in info['backups_recentes']:
                data_obj = datetime.fromisoformat(backup['data'])
                self.stdout.write(f'   • {backup["nome"]}')
                self.stdout.write(f'     {data_obj.strftime("%Y-%m-%d %H:%M:%S")} - {self._format_size(backup["tamanho"])}')
            self.stdout.write('')
        
        # Tamanho total
        self.stdout.write(f'📊 Tamanho total dos backups: {self._format_size(info["tamanho_total"])}')
        self.stdout.write('')
        
        # Recomendações
        self._mostrar_recomendacoes(info)

    def _mostrar_recomendacoes(self, info: Dict):
        """Mostra recomendações baseadas no status"""
        recomendacoes = []
        
        if not info['ultimo_backup']['data']:
            recomendacoes.append('⚠️  Nenhum backup encontrado! Execute: python manage.py backup_completo')
        
        if info['ultimo_backup']['data']:
            idade_horas = info['ultimo_backup']['idade_horas']
            if idade_horas > 48:
                recomendacoes.append('⚠️  Último backup tem mais de 48 horas! Considere fazer backup agora.')
        
        if info['espaco_disco']['percentual_usado'] > 90:
            recomendacoes.append('⚠️  Espaço em disco crítico! Limpe backups antigos ou aumente espaço.')
        elif info['espaco_disco']['percentual_usado'] > 80:
            recomendacoes.append('⚠️  Espaço em disco baixo. Considere limpar backups antigos.')
        
        if recomendacoes:
            self.stdout.write(self.style.WARNING('💡 Recomendações:'))
            for rec in recomendacoes:
                self.stdout.write(f'   {rec}')
            self.stdout.write('')

    def _format_size(self, size_bytes: int) -> str:
        """Formata tamanho em bytes para formato legível"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"








