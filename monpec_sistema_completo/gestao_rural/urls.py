from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('propriedades/', views.listar_propriedades, name='listar_propriedades'),
    path('propriedades/<int:pk>/', views.detalhes_propriedade, name='detalhes_propriedade'),
]
