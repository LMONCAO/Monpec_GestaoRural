"""
Utilitários para sistema de backup
Inclui: notificações, validação de integridade, backup remoto
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def calcular_checksum(arquivo: Path, algoritmo: str = 'sha256') -> Optional[str]:
    """
    Calcula checksum de um arquivo
    
    Args:
        arquivo: Caminho do arquivo
        algoritmo: 'sha256', 'md5', etc.
    
    Returns:
        String com hash hexadecimal ou None em caso de erro
    """
    try:
        hash_obj = hashlib.new(algoritmo)
        
        with open(arquivo, 'rb') as f:
            # Ler em chunks para arquivos grandes
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f'Erro ao calcular checksum de {arquivo}: {e}')
        return None


def validar_integridade_backup(arquivo: Path, checksum_esperado: Optional[str] = None) -> Dict:
    """
    Valida integridade de um backup
    
    Args:
        arquivo: Caminho do arquivo de backup
        checksum_esperado: Checksum esperado (se fornecido)
    
    Returns:
        Dict com status e informações
    """
    resultado = {
        'valido': False,
        'erros': [],
        'checksum': None
    }
    
    # Verificar se arquivo existe
    if not arquivo.exists():
        resultado['erros'].append(f'Arquivo não encontrado: {arquivo}')
        return resultado
    
    # Verificar se é arquivo (não diretório)
    if not arquivo.is_file():
        resultado['erros'].append(f'Não é um arquivo: {arquivo}')
        return resultado
    
    # Calcular checksum
    checksum = calcular_checksum(arquivo)
    if not checksum:
        resultado['erros'].append('Erro ao calcular checksum')
        return resultado
    
    resultado['checksum'] = checksum
    
    # Validar checksum se fornecido
    if checksum_esperado:
        if checksum != checksum_esperado:
            resultado['erros'].append('Checksum não confere! Arquivo pode estar corrompido.')
            return resultado
    
    # Validar se arquivo pode ser aberto (para ZIP)
    if arquivo.suffix == '.zip':
        import zipfile
        try:
            with zipfile.ZipFile(arquivo, 'r') as zipf:
                # Tentar ler lista de arquivos
                zipf.namelist()
        except zipfile.BadZipFile:
            resultado['erros'].append('Arquivo ZIP corrompido ou inválido')
            return resultado
        except Exception as e:
            resultado['erros'].append(f'Erro ao validar ZIP: {e}')
            return resultado
    
    # Validação de arquivos de banco removida - sistema usa apenas PostgreSQL
    # Arquivos .sqlite3 não são mais suportados
    
    resultado['valido'] = True
    return resultado


def notificar_backup_falha(erro: str, detalhes: Optional[Dict] = None):
    """
    Envia notificação quando backup falha
    
    Args:
        erro: Mensagem de erro
        detalhes: Dicionário com detalhes adicionais
    """
    try:
        # Obter email de destino
        email_destino = getattr(settings, 'BACKUP_NOTIFICATION_EMAIL', None)
        
        if not email_destino:
            # Tentar obter de ADMINS
            admins = getattr(settings, 'ADMINS', [])
            if admins:
                if isinstance(admins[0], tuple):
                    email_destino = admins[0][1]
                else:
                    email_destino = admins[0]
        
        if not email_destino:
            logger.warning('BACKUP_NOTIFICATION_EMAIL não configurado. Notificação não enviada.')
            return False
        
        # Preparar mensagem
        assunto = "[MONPEC] ⚠️ Falha no Backup Automático"
        
        detalhes_str = ""
        if detalhes:
            detalhes_str = "\n".join([f"  - {k}: {v}" for k, v in detalhes.items()])
        
        mensagem = f"""
O backup automático do sistema MonPEC falhou!

Erro: {erro}

Detalhes:
{detalhes_str or 'Nenhum detalhe adicional'}

Ação recomendada:
1. Verificar logs: logs/backup_automatico.log
2. Verificar espaço em disco
3. Executar backup manual: python manage.py backup_completo
4. Verificar status: python manage.py backup_status

Sistema: MonPEC Gestão Rural
"""
        
        # Enviar email
        send_mail(
            assunto,
            mensagem,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br'),
            [email_destino],
            fail_silently=False,
        )
        
        logger.info(f'Notificação de falha de backup enviada para {email_destino}')
        return True
        
    except Exception as e:
        logger.error(f'Erro ao enviar notificação de backup: {e}')
        return False


def notificar_backup_sucesso(tamanho: str, localizacao: str, checksum: Optional[str] = None):
    """
    Envia notificação quando backup é bem-sucedido (opcional)
    
    Args:
        tamanho: Tamanho do backup formatado
        localizacao: Caminho do backup
        checksum: Checksum do backup (opcional)
    """
    # Por padrão, não notificar sucesso (apenas falhas)
    notificar_sucesso = getattr(settings, 'BACKUP_NOTIFY_ON_SUCCESS', False)
    
    if not notificar_sucesso:
        return
    
    try:
        email_destino = getattr(settings, 'BACKUP_NOTIFICATION_EMAIL', None)
        if not email_destino:
            return
        
        assunto = "[MONPEC] ✅ Backup Automático Concluído"
        
        checksum_str = f"\nChecksum: {checksum}" if checksum else ""
        
        mensagem = f"""
O backup automático do sistema MonPEC foi concluído com sucesso!

Tamanho: {tamanho}
Localização: {localizacao}
{checksum_str}

Sistema: MonPEC Gestão Rural
"""
        
        send_mail(
            assunto,
            mensagem,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br'),
            [email_destino],
            fail_silently=True,
        )
    except Exception:
        pass


def fazer_backup_remoto(arquivo_local: Path, bucket_name: Optional[str] = None, 
                        caminho_remoto: Optional[str] = None) -> Dict:
    """
    Faz upload do backup para Google Cloud Storage
    
    Args:
        arquivo_local: Caminho do arquivo local
        bucket_name: Nome do bucket GCS (ou de BACKUP_GCS_BUCKET)
        caminho_remoto: Caminho no bucket (ou gerado automaticamente)
    
    Returns:
        Dict com status e informações
    """
    resultado = {
        'sucesso': False,
        'url': None,
        'erros': []
    }
    
    try:
        # Verificar se google-cloud-storage está instalado
        try:
            from google.cloud import storage
        except ImportError:
            resultado['erros'].append('google-cloud-storage não instalado. Instale com: pip install google-cloud-storage')
            return resultado
        
        # Obter configurações
        if not bucket_name:
            bucket_name = getattr(settings, 'BACKUP_GCS_BUCKET', None)
        
        if not bucket_name:
            resultado['erros'].append('BACKUP_GCS_BUCKET não configurado')
            return resultado
        
        # Gerar caminho remoto se não fornecido
        if not caminho_remoto:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            caminho_remoto = f"backups/{arquivo_local.name}"
        
        # Inicializar cliente GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(caminho_remoto)
        
        # Fazer upload
        blob.upload_from_filename(str(arquivo_local))
        
        # Tornar público (opcional) ou configurar permissões
        # blob.make_public()  # Descomente se quiser público
        
        resultado['sucesso'] = True
        resultado['url'] = f"gs://{bucket_name}/{caminho_remoto}"
        resultado['caminho_remoto'] = caminho_remoto
        
        logger.info(f'Backup enviado para GCS: {resultado["url"]}')
        return resultado
        
    except Exception as e:
        erro_msg = f'Erro ao fazer backup remoto: {e}'
        resultado['erros'].append(erro_msg)
        logger.exception(erro_msg)
        return resultado

