# -*- coding: utf-8 -*-
"""
Services para Sistema de Configurações por Módulo
Lógica de negócio centralizada
"""

import logging
from typing import Dict, List, Optional, Any, Type
from django.core.cache import cache
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Model, QuerySet

from .constants_configuracoes import (
    MODELO_MAP, 
    ALLOWED_MODEL_MODULES,
    CACHE_TIMEOUT_TOTAL,
    CACHE_PREFIX
)

logger = logging.getLogger(__name__)


class ConfiguracoesService:
    """Service class para gerenciar configurações de módulos"""
    
    @staticmethod
    def carregar_modelo_classe(nome_modelo: str) -> Type[Model]:
        """
        Carrega a classe do modelo dinamicamente com validação de segurança.
        
        Args:
            nome_modelo: Nome do modelo (chave do MODELO_MAP)
        
        Returns:
            Classe do modelo Django
        
        Raises:
            ValueError: Se modelo não for encontrado ou não permitido
        """
        if nome_modelo not in MODELO_MAP:
            raise ValueError(f'Modelo "{nome_modelo}" não encontrado no mapa')
        
        module_path, class_name = MODELO_MAP[nome_modelo].rsplit('.', 1)
        
        # Validação de segurança: verificar se módulo está na whitelist
        if module_path not in ALLOWED_MODEL_MODULES:
            raise ValueError(f'Módulo "{module_path}" não está na lista de permitidos')
        
        try:
            module = __import__(module_path, fromlist=[class_name])
            modelo_class = getattr(module, class_name)
            return modelo_class
        except (ImportError, AttributeError) as e:
            logger.error(f'Erro ao carregar modelo {nome_modelo}: {str(e)}')
            raise ValueError(f'Erro ao carregar modelo {nome_modelo}: {str(e)}')
    
    @staticmethod
    def obter_total_registros(modelo_class: Type[Model], propriedade=None) -> int:
        """
        Obtém total de registros com cache.
        
        Args:
            modelo_class: Classe do modelo Django
            propriedade: Objeto Propriedade (opcional)
        
        Returns:
            Total de registros
        """
        # Gerar chave de cache
        if propriedade:
            cache_key = f'{CACHE_PREFIX}_total_{modelo_class.__name__}_{propriedade.id}'
        else:
            cache_key = f'{CACHE_PREFIX}_total_{modelo_class.__name__}_global'
        
        # Tentar obter do cache
        total = cache.get(cache_key)
        
        if total is None:
            try:
                if hasattr(modelo_class, 'propriedade'):
                    # Modelo tem relação com propriedade
                    if propriedade:
                        total = modelo_class.objects.filter(propriedade=propriedade).count()
                    else:
                        total = modelo_class.objects.count()
                else:
                    # Modelo global (sem propriedade)
                    total = modelo_class.objects.count()
                
                # Armazenar no cache
                cache.set(cache_key, total, CACHE_TIMEOUT_TOTAL)
            except Exception as e:
                logger.error(f'Erro ao contar registros de {modelo_class.__name__}: {str(e)}')
                total = 0
        
        return total
    
    @staticmethod
    def obter_queryset(modelo_class: Type[Model], propriedade=None) -> QuerySet:
        """
        Obtém queryset otimizado do modelo.
        
        Args:
            modelo_class: Classe do modelo Django
            propriedade: Objeto Propriedade (opcional)
        
        Returns:
            QuerySet otimizado
        """
        if hasattr(modelo_class, 'propriedade'):
            queryset = modelo_class.objects.filter(propriedade=propriedade)
            # Otimizar com select_related se houver relacionamentos
            if hasattr(modelo_class, '_meta'):
                related_fields = [f.name for f in modelo_class._meta.get_fields() 
                                if f.many_to_one and f.related_model]
                if related_fields:
                    queryset = queryset.select_related(*related_fields[:3])  # Limitar a 3 para performance
        else:
            queryset = modelo_class.objects.all()
        
        return queryset
    
    @staticmethod
    def serializar_registro(registro: Model) -> Dict[str, Any]:
        """
        Serializa um registro para formato JSON.
        
        Args:
            registro: Instância do modelo Django
        
        Returns:
            Dicionário com dados serializados
        """
        return {
            'id': registro.id,
            'nome': str(registro),
            'ativo': getattr(registro, 'ativo', True),
            'criado_em': registro.criado_em.isoformat() if hasattr(registro, 'criado_em') else None,
        }
    
    @staticmethod
    def validar_permissao_edicao(user, propriedade, modelo_class: Type[Model]) -> bool:
        """
        Valida se usuário tem permissão para editar registros do modelo.
        
        Args:
            user: Usuário Django
            propriedade: Objeto Propriedade
            modelo_class: Classe do modelo
        
        Returns:
            True se tiver permissão, False caso contrário
        """
        # Verificar se propriedade pertence ao usuário
        if hasattr(propriedade, 'produtor'):
            if hasattr(propriedade.produtor, 'usuario'):
                if propriedade.produtor.usuario != user:
                    return False
        
        # Verificar permissões Django (se implementado)
        model_name = modelo_class.__name__.lower()
        if user.has_perm(f'gestao_rural.change_{model_name}'):
            return True
        
        # Por padrão, permitir se for dono da propriedade
        return True
    
    @staticmethod
    def invalidar_cache_total(modelo_class: Type[Model], propriedade=None):
        """
        Invalida cache de contagem de registros.
        
        Args:
            modelo_class: Classe do modelo Django
            propriedade: Objeto Propriedade (opcional)
        """
        if propriedade:
            cache_key = f'{CACHE_PREFIX}_total_{modelo_class.__name__}_{propriedade.id}'
        else:
            cache_key = f'{CACHE_PREFIX}_total_{modelo_class.__name__}_global'
        
        cache.delete(cache_key)








