from django.apps import AppConfig


class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
    
    def ready(self):
        """Executado quando a aplicação está pronta"""
            # Importar aqui para evitar importações circulares
        try:
            from django.db import transaction
            from .models import CategoriaAnimal
            # Garantir que todos os modelos especializados sejam registrados
            from . import models_reproducao  # noqa: F401
            from . import models_compras_financeiro  # noqa: F401
            from . import models_iatf_completo  # noqa: F401
            # Importar models_cadastros para garantir que Cliente seja carregado
            from . import models_cadastros  # noqa: F401
            from .services.provisionamento import registrar_workspaces_existentes
            
            # Criar categorias padrão se não existirem
            self.criar_categorias_padrao()
            registrar_workspaces_existentes()
        except Exception as e:
            # Em caso de erro (por exemplo, durante migrações), apenas logar
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f'Erro ao criar categorias padrão na inicialização: {e}')
    
    def criar_categorias_padrao(self):
        """Cria as categorias padrão do sistema se não existirem"""
        from django.db import transaction
        from .models import CategoriaAnimal
        
        categorias_padrao = [
            # FÊMEAS (5 categorias)
            {
                'nome': 'Bezerro(a) 0-12 F',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 0 a 12 Meses'
            },
            {
                'nome': 'Novilha 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 12 a 24 Meses'
            },
            {
                'nome': 'Primíparas 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas Primíparas de 24 a 36 Meses'
            },
            {
                'nome': 'Vacas Descarte +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas de Descarte acima de 36 Meses'
            },
            {
                'nome': 'Vacas em Reprodução +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas em Reprodução acima de 36 Meses'
            },
            
            # MACHOS (4 categorias) - APENAS "Garrote 12-24 M" (não criar "Garrote 12-4 M")
            {
                'nome': 'Bezerro(o) 0-12 M',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Machos de 0 a 12 Meses'
            },
            {
                'nome': 'Garrote 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Garrotes de 12 a 24 Meses'
            },
            {
                'nome': 'Boi 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Bois de 24 a 36 Meses'
            },
            {
                'nome': 'Touro +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Touros acima de 36 Meses'
            },
        ]
        
        try:
            with transaction.atomic():
                for cat_data in categorias_padrao:
                    CategoriaAnimal.objects.get_or_create(
                        nome=cat_data['nome'],
                        defaults={
                            'idade_minima_meses': cat_data.get('idade_minima_meses'),
                            'idade_maxima_meses': cat_data.get('idade_maxima_meses'),
                            'sexo': cat_data.get('sexo', 'I'),
                            'raca': cat_data.get('raca', 'NELORE'),
                            'descricao': cat_data.get('descricao', ''),
                            'ativo': True
                        }
                    )
        except Exception:
            # Se der erro (tabela não existe ainda, por exemplo), ignorar
            pass

