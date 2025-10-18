from django.urls import path
from . import views_projetos_bancarios

urlpatterns = [
    # URLs para projetos bancários
    path('propriedade/<int:propriedade_id>/projetos-bancarios/', 
         views_projetos_bancarios.projetos_bancarios_dashboard, 
         name='projetos_bancarios_dashboard'),
]

