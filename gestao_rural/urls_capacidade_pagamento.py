from django.urls import path
from . import views_capacidade_pagamento

urlpatterns = [
    # URLs para capacidade de pagamento
    path('propriedade/<int:propriedade_id>/capacidade-pagamento/', 
         views_capacidade_pagamento.capacidade_pagamento_dashboard, 
         name='capacidade_pagamento_dashboard'),
]

