# -*- coding: utf-8 -*-
"""
URLs para Relatórios Oficiais SISBOV - Anexos IV a XIX
Conforme Instrução Normativa MAPA nº 17/2006
"""

from django.urls import path
from . import views_relatorios_sisbov

urlpatterns = [
    # Menu principal de relatórios SISBOV
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/menu/', 
         views_relatorios_sisbov.relatorios_sisbov_menu, 
         name='relatorios_sisbov_menu'),
    
    # Anexo IV - Cadastro de Produtor Rural
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-iv/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_iv, 
         name='relatorio_sisbov_anexo_iv'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-iv/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_iv_pdf, 
         name='relatorio_sisbov_anexo_iv_pdf'),
    
    # Anexo V - Cadastro de Estabelecimento Rural
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-v/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_v, 
         name='relatorio_sisbov_anexo_v'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-v/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_v_pdf, 
         name='relatorio_sisbov_anexo_v_pdf'),
    
    # Anexo VI - Inventário de Animais
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-vi/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_vi, 
         name='relatorio_sisbov_anexo_vi'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-vi/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_vi_pdf, 
         name='relatorio_sisbov_anexo_vi_pdf'),
    
    # Anexo VII - Termo de Adesão
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-vii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_vii, 
         name='relatorio_sisbov_anexo_vii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-vii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_vii_pdf, 
         name='relatorio_sisbov_anexo_vii_pdf'),
    
    # Anexo VIII - Protocolo Declaratório de Produção
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-viii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_viii, 
         name='relatorio_sisbov_anexo_viii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-viii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_viii_pdf, 
         name='relatorio_sisbov_anexo_viii_pdf'),
    
    # Anexo IX - Comunicado de Entrada de Animais
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-ix/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_ix, 
         name='relatorio_sisbov_anexo_ix'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-ix/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_ix_pdf, 
         name='relatorio_sisbov_anexo_ix_pdf'),
    
    # Anexo X - Comunicado de Saída de Animais
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-x/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_x, 
         name='relatorio_sisbov_anexo_x'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-x/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_x_pdf, 
         name='relatorio_sisbov_anexo_x_pdf'),
    
    # Anexo XI - Declaração de Nascimento
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xi/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xi, 
         name='relatorio_sisbov_anexo_xi'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xi/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xi_pdf, 
         name='relatorio_sisbov_anexo_xi_pdf'),
    
    # Anexo XII - Declaração de Morte
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xii, 
         name='relatorio_sisbov_anexo_xii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xii_pdf, 
         name='relatorio_sisbov_anexo_xii_pdf'),
    
    # Anexo XIII - Declaração de Perda de Brinco
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xiii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xiii, 
         name='relatorio_sisbov_anexo_xiii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xiii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xiii_pdf, 
         name='relatorio_sisbov_anexo_xiii_pdf'),
    
    # Anexo XIV - Declaração de Mudança de Categoria
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xiv/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xiv, 
         name='relatorio_sisbov_anexo_xiv'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xiv/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xiv_pdf, 
         name='relatorio_sisbov_anexo_xiv_pdf'),
    
    # Anexo XV - Declaração de Mudança de Propriedade
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xv/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xv, 
         name='relatorio_sisbov_anexo_xv'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xv/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xv_pdf, 
         name='relatorio_sisbov_anexo_xv_pdf'),
    
    # Anexo XVI - Declaração de Abate
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xvi/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xvi, 
         name='relatorio_sisbov_anexo_xvi'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xvi/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xvi_pdf, 
         name='relatorio_sisbov_anexo_xvi_pdf'),
    
    # Anexo XVII - Declaração de Exportação
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xvii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xvii, 
         name='relatorio_sisbov_anexo_xvii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xvii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xvii_pdf, 
         name='relatorio_sisbov_anexo_xvii_pdf'),
    
    # Anexo XVIII - Declaração de Importação
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xviii/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xviii, 
         name='relatorio_sisbov_anexo_xviii'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xviii/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xviii_pdf, 
         name='relatorio_sisbov_anexo_xviii_pdf'),
    
    # Anexo XIX - Declaração de Movimentação
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xix/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xix, 
         name='relatorio_sisbov_anexo_xix'),
    path('propriedade/<int:propriedade_id>/rastreabilidade/relatorios-sisbov/anexo-xix/pdf/', 
         views_relatorios_sisbov.relatorio_sisbov_anexo_xix_pdf, 
         name='relatorio_sisbov_anexo_xix_pdf'),
]


