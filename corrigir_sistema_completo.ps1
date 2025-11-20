# Script para corrigir o sistema Monpec Projetista
Write-Host "🚀 CORRIGINDO SISTEMA MONPEC PROJETISTA" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Yellow

# Comandos para executar no servidor via SSH
$comandos = @"
# 1. Parar todos os processos Python
pkill -9 python

# 2. Navegar para o diretório correto
cd /var/www/monpec.com.br

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Criar estrutura de diretórios
mkdir -p gestao_rural
mkdir -p templates/gestao_rural

# 5. Criar __init__.py
touch gestao_rural/__init__.py

# 6. Criar apps.py
cat > gestao_rural/apps.py << 'EOF'
from django.apps import AppConfig

class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
EOF

# 7. Criar models.py
cat > gestao_rural/models.py << 'EOF'
from django.db import models
from django.contrib.auth.models import User

class Proprietario(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nome
    
    @property
    def area_total(self):
        return sum(prop.area for prop in self.propriedades.all())

class Propriedade(models.Model):
    nome = models.CharField(max_length=200)
    proprietario = models.ForeignKey(Proprietario, on_delete=models.CASCADE, related_name='propriedades')
    area = models.DecimalField(max_digits=10, decimal_places=2)
    municipio = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    endereco = models.TextField(blank=True, null=True)
    matricula = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nome} - {self.proprietario.nome}"
EOF

# 8. Criar views.py
cat > gestao_rural/views.py << 'EOF'
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Proprietario, Propriedade

def landing_page(request):
    return render(request, 'gestao_rural/landing.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos')
    return render(request, 'gestao_rural/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing_page')

@login_required
def dashboard(request):
    proprietarios = Proprietario.objects.all()
    propriedades = Propriedade.objects.all()
    return render(request, 'gestao_rural/dashboard.html', {
        'proprietarios': proprietarios,
        'propriedades': propriedades
    })

@login_required
def produtor_rural(request):
    proprietarios = Proprietario.objects.all()
    return render(request, 'gestao_rural/produtor_rural.html', {
        'proprietarios': proprietarios
    })

@login_required
def produtor_novo(request):
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            telefone = request.POST.get('telefone', '')
            email = request.POST.get('email', '')
            endereco = request.POST.get('endereco', '')
            cidade = request.POST.get('cidade', '')
            estado = request.POST.get('estado', '')
            observacoes = request.POST.get('observacoes', '')
            
            if not nome or not cpf:
                messages.error(request, 'Nome e CPF são obrigatórios!')
                return render(request, 'gestao_rural/produtor_novo.html')
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'CPF já cadastrado!')
                return render(request, 'gestao_rural/produtor_novo.html')
            
            proprietario = Proprietario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                observacoes=observacoes
            )
            
            messages.success(request, f'Proprietário {nome} cadastrado com sucesso!')
            return redirect('produtor_rural')
            
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {str(e)}')
    
    return render(request, 'gestao_rural/produtor_novo.html')

@login_required
def produtor_editar(request, produtor_id):
    proprietario = get_object_or_404(Proprietario, id=produtor_id)
    return render(request, 'gestao_rural/produtor_editar.html', {'proprietario': proprietario})

@login_required
def propriedades_lista(request, produtor_id=None):
    if produtor_id:
        proprietario = get_object_or_404(Proprietario, id=produtor_id)
        propriedades = Propriedade.objects.filter(proprietario=proprietario)
        return render(request, 'gestao_rural/propriedades_lista.html', {
            'proprietario': proprietario,
            'propriedades': propriedades
        })
    else:
        propriedades = Propriedade.objects.all()
        return render(request, 'gestao_rural/propriedades_lista.html', {
            'propriedades': propriedades
        })

@login_required
def propriedade_nova(request, produtor_id):
    proprietario = get_object_or_404(Proprietario, id=produtor_id)
    return render(request, 'gestao_rural/propriedade_nova.html', {'proprietario': proprietario})

@login_required
def propriedade_editar(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/propriedade_editar.html', {'propriedade': propriedade})

@login_required
def propriedade_modulos(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/propriedade_modulos.html', {'propriedade': propriedade})

@login_required
def pecuaria_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/pecuaria_dashboard.html', {'propriedade': propriedade})

@login_required
def pecuaria_parametros(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/pecuaria_parametros.html', {'propriedade': propriedade})

@login_required
def agricultura_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/agricultura_dashboard.html', {'propriedade': propriedade})

@login_required
def financeiro_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/financeiro_dashboard.html', {'propriedade': propriedade})

@login_required
def patrimonio_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/patrimonio_dashboard.html', {'propriedade': propriedade})

@login_required
def projetos_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/projetos_dashboard.html', {'propriedade': propriedade})

@login_required
def relatorio_final(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/relatorio_final.html', {'propriedade': propriedade})

@login_required
def categorias_lista(request):
    return render(request, 'gestao_rural/categorias_lista.html')
EOF

# 9. Criar urls.py
cat > gestao_rural/urls.py << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('produtor-rural/', views.produtor_rural, name='produtor_rural'),
    path('produtor/novo/', views.produtor_novo, name='produtor_novo'),
    path('produtor/<int:produtor_id>/editar/', views.produtor_editar, name='produtor_editar'),
    path('produtor/<int:produtor_id>/propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('produtor/<int:produtor_id>/propriedade/nova/', views.propriedade_nova, name='propriedade_nova'),
    path('propriedade/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedades/', views.propriedades_lista, name='propriedades_lista_sem_id'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/pecuaria/parametros/', views.pecuaria_parametros, name='pecuaria_parametros'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/relatorio/final/', views.relatorio_final, name='relatorio_final'),
    path('categorias/', views.categorias_lista, name='categorias_lista'),
]
EOF

# 10. Criar admin.py
cat > gestao_rural/admin.py << 'EOF'
from django.contrib import admin
from .models import Proprietario, Propriedade

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado']
    search_fields = ['nome', 'cpf', 'cidade']
    list_filter = ['estado', 'cidade']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado']
    search_fields = ['nome', 'proprietario__nome', 'municipio']
    list_filter = ['estado', 'municipio']
EOF

# 11. Executar migrações
python manage.py makemigrations
python manage.py migrate

# 12. Criar superusuário
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com.br', 'admin123') if not User.objects.filter(username='admin').exists() else print('Superusuário já existe')" | python manage.py shell

# 13. Adicionar dados de exemplo
python manage.py shell << 'EOF'
from gestao_rural.models import Proprietario, Propriedade

if not Proprietario.objects.exists():
    p1 = Proprietario.objects.create(
        nome="João Silva",
        cpf="123.456.789-00",
        telefone="(67) 99999-9999",
        email="joao@email.com",
        cidade="Maracaju",
        estado="MS"
    )
    
    p2 = Proprietario.objects.create(
        nome="Maria Santos",
        cpf="987.654.321-00",
        telefone="(67) 88888-8888",
        email="maria@email.com",
        cidade="Dourados",
        estado="MS"
    )
    
    Propriedade.objects.create(
        nome="Fazenda São José",
        proprietario=p1,
        area=500.00,
        municipio="Maracaju",
        estado="MS"
    )
    
    Propriedade.objects.create(
        nome="Sítio Boa Vista",
        proprietario=p2,
        area=200.00,
        municipio="Dourados",
        estado="MS"
    )
    
    print("Dados de exemplo criados com sucesso!")
else:
    print("Dados já existem!")
EOF

# 14. Iniciar Django na porta 9000
nohup python manage.py runserver 0.0.0.0:9000 > /tmp/django_9000.log 2>&1 &

echo "SISTEMA MONPEC PROJETISTA CONCLUÍDO!"
echo "===================================="
echo "Tente acessar: http://45.32.219.76:9000"
echo "Login: admin / admin123"
"@

Write-Host "📋 COMANDOS PARA EXECUTAR NO SERVIDOR:" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host $comandos -ForegroundColor White
Write-Host ""
Write-Host "🔧 INSTRUÇÕES:" -ForegroundColor Green
Write-Host "1. Conecte-se ao servidor via SSH" -ForegroundColor White
Write-Host "2. Execute os comandos acima" -ForegroundColor White
Write-Host "3. Acesse: http://45.32.219.76:9000" -ForegroundColor White
Write-Host "4. Login: admin / admin123" -ForegroundColor White


