from django.urls import path
from . import views_imobilizado

urlpatterns = [
    # URLs para imobilizado
    path('propriedade/<int:propriedade_id>/imobilizado/', 
         views_imobilizado.imobilizado_dashboard, 
         name='imobilizado_dashboard'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/bens/', 
         views_imobilizado.bens_lista, 
         name='bens_lista'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/bem/novo/', 
         views_imobilizado.bem_novo, 
         name='bem_novo'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/bem/<int:bem_id>/editar/', 
         views_imobilizado.bem_editar, 
         name='bem_editar'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/bem/<int:bem_id>/excluir/', 
         views_imobilizado.bem_excluir, 
         name='bem_excluir'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/calcular-depreciacao/', 
         views_imobilizado.calcular_depreciacao_automatica, 
         name='calcular_depreciacao_automatica'),
    
    path('propriedade/<int:propriedade_id>/imobilizado/relatorio/', 
         views_imobilizado.relatorio_imobilizado, 
         name='relatorio_imobilizado'),
    
    # URLs para categorias
    path('imobilizado/categorias/', 
         views_imobilizado.categorias_lista, 
         name='categorias_imobilizado_lista'),
    
    path('imobilizado/categoria/nova/', 
         views_imobilizado.categoria_nova, 
         name='categoria_imobilizado_nova'),
]

