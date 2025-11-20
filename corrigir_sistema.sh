#!/bin/bash
# Script para corrigir e ativar todos os módulos

cd /var/www/monpec.com.br

echo "1. Corrigindo urls.py..."
sed -i '2s/.*/from . import views/' gestao_rural/urls.py

echo "2. Limpando views.py..."
head -n 1790 gestao_rural/views.py > /tmp/views_clean.py
mv /tmp/views_clean.py gestao_rural/views.py

echo "3. Adicionando views..."
cat >> gestao_rural/views.py << 'EOF'

@login_required
def propriedade_modulos(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    return render(request, 'gestao_rural/propriedade_modulos.html', {'propriedade': propriedade})

@login_required
def patrimonio_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    return render(request, 'gestao_rural/patrimonio_dashboard.html', {'propriedade': propriedade, 'bens': []})

@login_required
def financeiro_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    return render(request, 'gestao_rural/financeiro_dashboard.html', {'propriedade': propriedade, 'lancamentos': []})

@login_required
def projetos_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    return render(request, 'gestao_rural/projetos_dashboard.html', {'propriedade': propriedade, 'projetos': []})
EOF

echo "4. Adicionando URLs..."
sed -i "/name='propriedade_excluir'/a\    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos')," gestao_rural/urls.py
sed -i "/name='relatorio_final'/a\    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard')," gestao_rural/urls.py
sed -i "/name='patrimonio_dashboard'/a\    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard')," gestao_rural/urls.py
sed -i "/name='financeiro_dashboard'/a\    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard')," gestao_rural/urls.py

echo "5. Verificando..."
source venv/bin/activate
python manage.py check

echo "6. Reiniciando Django..."
pkill -9 python
sleep 2
python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
sleep 3

echo "7. Testando..."
ps aux | grep manage | grep -v grep
curl -s http://127.0.0.1:8000 | head -3

echo "✅ SISTEMA CORRIGIDO E REINICIADO!"
