# ========================================
# COMPLETAR SISTEMA MONPEC - AUTOMÁTICO
# ========================================

Write-Host "🚀 COMPLETANDO SISTEMA MONPEC AUTOMATICAMENTE" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Yellow

Set-Location "monpec_local"

# 1. CRIAR VIEWS COMPLETAS
Write-Host "📝 Criando views completas..." -ForegroundColor Cyan

@"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from .models import Proprietario, Propriedade, ProjetoCredito, Documento
import json
from datetime import datetime, date
import csv
import io

# ========================================
# PÁGINAS PRINCIPAIS
# ========================================

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
    # Estatísticas
    total_proprietarios = Proprietario.objects.count()
    total_propriedades = Propriedade.objects.count()
    total_projetos = ProjetoCredito.objects.count()
    projetos_aprovados = ProjetoCredito.objects.filter(status='aprovado').count()
    
    # Projetos recentes
    projetos_recentes = ProjetoCredito.objects.select_related('propriedade__proprietario').order_by('-created_at')[:5]
    
    # Proprietários recentes
    proprietarios_recentes = Proprietario.objects.order_by('-created_at')[:5]
    
    context = {
        'total_proprietarios': total_proprietarios,
        'total_propriedades': total_propriedades,
        'total_projetos': total_projetos,
        'projetos_aprovados': projetos_aprovados,
        'projetos_recentes': projetos_recentes,
        'proprietarios_recentes': proprietarios_recentes,
    }
    return render(request, 'gestao_rural/dashboard.html', context)

# ========================================
# GESTÃO DE PROPRIETÁRIOS
# ========================================

@login_required
def proprietarios_lista(request):
    search = request.GET.get('search', '')
    proprietarios = Proprietario.objects.all()
    
    if search:
        proprietarios = proprietarios.filter(
            Q(nome__icontains=search) | 
            Q(cpf__icontains=search) | 
            Q(cidade__icontains=search)
        )
    
    paginator = Paginator(proprietarios, 10)
    page_number = request.GET.get('page')
    proprietarios = paginator.get_page(page_number)
    
    return render(request, 'gestao_rural/proprietarios_lista.html', {
        'proprietarios': proprietarios,
        'search': search
    })

@login_required
def proprietario_novo(request):
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
                return render(request, 'gestao_rural/proprietario_novo.html')
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'CPF já cadastrado!')
                return render(request, 'gestao_rural/proprietario_novo.html')
            
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
            return redirect('proprietarios_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {str(e)}')
    
    return render(request, 'gestao_rural/proprietario_novo.html')

@login_required
def proprietario_editar(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    
    if request.method == 'POST':
        try:
            proprietario.nome = request.POST.get('nome')
            proprietario.cpf = request.POST.get('cpf')
            proprietario.telefone = request.POST.get('telefone', '')
            proprietario.email = request.POST.get('email', '')
            proprietario.endereco = request.POST.get('endereco', '')
            proprietario.cidade = request.POST.get('cidade', '')
            proprietario.estado = request.POST.get('estado', '')
            proprietario.observacoes = request.POST.get('observacoes', '')
            proprietario.save()
            
            messages.success(request, 'Proprietário atualizado com sucesso!')
            return redirect('proprietarios_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    return render(request, 'gestao_rural/proprietario_editar.html', {'proprietario': proprietario})

@login_required
def proprietario_detalhes(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    propriedades = proprietario.propriedades.all()
    projetos = ProjetoCredito.objects.filter(propriedade__proprietario=proprietario)
    
    return render(request, 'gestao_rural/proprietario_detalhes.html', {
        'proprietario': proprietario,
        'propriedades': propriedades,
        'projetos': projetos
    })

# ========================================
# GESTÃO DE PROPRIEDADES
# ========================================

@login_required
def propriedades_lista(request):
    search = request.GET.get('search', '')
    proprietario_id = request.GET.get('proprietario', '')
    
    propriedades = Propriedade.objects.select_related('proprietario')
    
    if search:
        propriedades = propriedades.filter(
            Q(nome__icontains=search) | 
            Q(proprietario__nome__icontains=search) |
            Q(municipio__icontains=search)
        )
    
    if proprietario_id:
        propriedades = propriedades.filter(proprietario_id=proprietario_id)
    
    paginator = Paginator(propriedades, 10)
    page_number = request.GET.get('page')
    propriedades = paginator.get_page(page_number)
    
    proprietarios = Proprietario.objects.all()
    
    return render(request, 'gestao_rural/propriedades_lista.html', {
        'propriedades': propriedades,
        'proprietarios': proprietarios,
        'search': search,
        'proprietario_id': proprietario_id
    })

@login_required
def propriedade_nova(request, proprietario_id):
    proprietario = get_object_or_404(Proprietario, id=proprietario_id)
    
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            area = request.POST.get('area')
            municipio = request.POST.get('municipio')
            estado = request.POST.get('estado')
            endereco = request.POST.get('endereco', '')
            matricula = request.POST.get('matricula', '')
            observacoes = request.POST.get('observacoes', '')
            
            if not nome or not area or not municipio or not estado:
                messages.error(request, 'Campos obrigatórios não preenchidos!')
                return render(request, 'gestao_rural/propriedade_nova.html', {'proprietario': proprietario})
            
            propriedade = Propriedade.objects.create(
                nome=nome,
                proprietario=proprietario,
                area=area,
                municipio=municipio,
                estado=estado,
                endereco=endereco,
                matricula=matricula,
                observacoes=observacoes
            )
            
            messages.success(request, f'Propriedade {nome} cadastrada com sucesso!')
            return redirect('propriedades_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {str(e)}')
    
    return render(request, 'gestao_rural/propriedade_nova.html', {'proprietario': proprietario})

@login_required
def propriedade_editar(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        try:
            propriedade.nome = request.POST.get('nome')
            propriedade.area = request.POST.get('area')
            propriedade.municipio = request.POST.get('municipio')
            propriedade.estado = request.POST.get('estado')
            propriedade.endereco = request.POST.get('endereco', '')
            propriedade.matricula = request.POST.get('matricula', '')
            propriedade.observacoes = request.POST.get('observacoes', '')
            propriedade.save()
            
            messages.success(request, 'Propriedade atualizada com sucesso!')
            return redirect('propriedades_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar: {str(e)}')
    
    return render(request, 'gestao_rural/propriedade_editar.html', {'propriedade': propriedade})

@login_required
def propriedade_detalhes(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    projetos = propriedade.projetos.all()
    
    return render(request, 'gestao_rural/propriedade_detalhes.html', {
        'propriedade': propriedade,
        'projetos': projetos
    })

# ========================================
# MÓDULOS DA PROPRIEDADE
# ========================================

@login_required
def propriedade_modulos(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/propriedade_modulos.html', {'propriedade': propriedade})

@login_required
def pecuaria_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/pecuaria_dashboard.html', {'propriedade': propriedade})

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
    projetos = propriedade.projetos.all()
    return render(request, 'gestao_rural/projetos_dashboard.html', {
        'propriedade': propriedade,
        'projetos': projetos
    })

@login_required
def relatorio_final(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/relatorio_final.html', {'propriedade': propriedade})

# ========================================
# GESTÃO DE PROJETOS
# ========================================

@login_required
def projetos_lista(request):
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    
    projetos = ProjetoCredito.objects.select_related('propriedade__proprietario')
    
    if search:
        projetos = projetos.filter(
            Q(titulo__icontains=search) | 
            Q(propriedade__nome__icontains=search) |
            Q(propriedade__proprietario__nome__icontains=search)
        )
    
    if status:
        projetos = projetos.filter(status=status)
    
    paginator = Paginator(projetos, 10)
    page_number = request.GET.get('page')
    projetos = paginator.get_page(page_number)
    
    return render(request, 'gestao_rural/projetos_lista.html', {
        'projetos': projetos,
        'search': search,
        'status': status
    })

@login_required
def projeto_novo(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo')
            tipo = request.POST.get('tipo')
            valor_solicitado = request.POST.get('valor_solicitado')
            prazo_pagamento = request.POST.get('prazo_pagamento')
            data_inicio = request.POST.get('data_inicio')
            observacoes = request.POST.get('observacoes', '')
            
            if not all([titulo, tipo, valor_solicitado, prazo_pagamento, data_inicio]):
                messages.error(request, 'Campos obrigatórios não preenchidos!')
                return render(request, 'gestao_rural/projeto_novo.html', {'propriedade': propriedade})
            
            projeto = ProjetoCredito.objects.create(
                propriedade=propriedade,
                titulo=titulo,
                tipo=tipo,
                valor_solicitado=valor_solicitado,
                prazo_pagamento=prazo_pagamento,
                data_inicio=data_inicio,
                observacoes=observacoes
            )
            
            messages.success(request, f'Projeto {titulo} criado com sucesso!')
            return redirect('projetos_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao criar projeto: {str(e)}')
    
    return render(request, 'gestao_rural/projeto_novo.html', {'propriedade': propriedade})

# ========================================
# RELATÓRIOS E EXPORTAÇÃO
# ========================================

@login_required
def relatorios_dashboard(request):
    # Estatísticas para relatórios
    stats = {
        'total_proprietarios': Proprietario.objects.count(),
        'total_propriedades': Propriedade.objects.count(),
        'total_projetos': ProjetoCredito.objects.count(),
        'projetos_por_status': ProjetoCredito.objects.values('status').annotate(count=Count('id')),
        'projetos_por_tipo': ProjetoCredito.objects.values('tipo').annotate(count=Count('id')),
        'valor_total_solicitado': ProjetoCredito.objects.aggregate(total=Sum('valor_solicitado'))['total'] or 0,
    }
    
    return render(request, 'gestao_rural/relatorios_dashboard.html', {'stats': stats})

@login_required
def exportar_csv(request):
    tipo = request.GET.get('tipo', 'proprietarios')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{tipo}.csv"'
    
    writer = csv.writer(response)
    
    if tipo == 'proprietarios':
        writer.writerow(['Nome', 'CPF', 'Telefone', 'Email', 'Cidade', 'Estado', 'Data Criação'])
        for prop in Proprietario.objects.all():
            writer.writerow([
                prop.nome, prop.cpf, prop.telefone, prop.email, 
                prop.cidade, prop.estado, prop.created_at.strftime('%d/%m/%Y')
            ])
    
    elif tipo == 'propriedades':
        writer.writerow(['Nome', 'Proprietário', 'Área', 'Município', 'Estado', 'Data Criação'])
        for prop in Propriedade.objects.select_related('proprietario'):
            writer.writerow([
                prop.nome, prop.proprietario.nome, prop.area, 
                prop.municipio, prop.estado, prop.created_at.strftime('%d/%m/%Y')
            ])
    
    elif tipo == 'projetos':
        writer.writerow(['Título', 'Propriedade', 'Proprietário', 'Tipo', 'Valor', 'Status', 'Data Criação'])
        for proj in ProjetoCredito.objects.select_related('propriedade__proprietario'):
            writer.writerow([
                proj.titulo, proj.propriedade.nome, proj.propriedade.proprietario.nome,
                proj.get_tipo_display(), proj.valor_solicitado, proj.get_status_display(),
                proj.created_at.strftime('%d/%m/%Y')
            ])
    
    return response

# ========================================
# API ENDPOINTS
# ========================================

@csrf_exempt
def api_proprietarios(request):
    if request.method == 'GET':
        proprietarios = Proprietario.objects.all()
        data = []
        for prop in proprietarios:
            data.append({
                'id': prop.id,
                'nome': prop.nome,
                'cpf': prop.cpf,
                'cidade': prop.cidade,
                'estado': prop.estado,
                'propriedades_count': prop.propriedades.count()
            })
        return JsonResponse({'proprietarios': data})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_propriedades(request):
    if request.method == 'GET':
        proprietario_id = request.GET.get('proprietario_id')
        propriedades = Propriedade.objects.all()
        
        if proprietario_id:
            propriedades = propriedades.filter(proprietario_id=proprietario_id)
        
        data = []
        for prop in propriedades:
            data.append({
                'id': prop.id,
                'nome': prop.nome,
                'proprietario': prop.proprietario.nome,
                'area': float(prop.area),
                'municipio': prop.municipio,
                'estado': prop.estado
            })
        return JsonResponse({'propriedades': data})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
"@ | Out-File -FilePath "gestao_rural/views.py" -Encoding UTF8

Write-Host "✅ Views criadas!" -ForegroundColor Green

# 2. CRIAR URLS
Write-Host "🔗 Criando URLs..." -ForegroundColor Cyan

@"
from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestão de Proprietários
    path('proprietarios/', views.proprietarios_lista, name='proprietarios_lista'),
    path('proprietarios/novo/', views.proprietario_novo, name='proprietario_novo'),
    path('proprietarios/<int:proprietario_id>/editar/', views.proprietario_editar, name='proprietario_editar'),
    path('proprietarios/<int:proprietario_id>/detalhes/', views.proprietario_detalhes, name='proprietario_detalhes'),
    
    # Gestão de Propriedades
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedades/<int:propriedade_id>/editar/', views.propriedade_editar, name='propriedade_editar'),
    path('propriedades/<int:propriedade_id>/detalhes/', views.propriedade_detalhes, name='propriedade_detalhes'),
    path('propriedades/<int:propriedade_id>/nova/', views.propriedade_nova, name='propriedade_nova'),
    
    # Módulos da Propriedade
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    path('propriedade/<int:propriedade_id>/relatorio/', views.relatorio_final, name='relatorio_final'),
    
    # Gestão de Projetos
    path('projetos/', views.projetos_lista, name='projetos_lista'),
    path('projetos/<int:propriedade_id>/novo/', views.projeto_novo, name='projeto_novo'),
    
    # Relatórios
    path('relatorios/', views.relatorios_dashboard, name='relatorios_dashboard'),
    path('exportar/csv/', views.exportar_csv, name='exportar_csv'),
    
    # API
    path('api/proprietarios/', views.api_proprietarios, name='api_proprietarios'),
    path('api/propriedades/', views.api_propriedades, name='api_propriedades'),
]
"@ | Out-File -FilePath "gestao_rural/urls.py" -Encoding UTF8

Write-Host "✅ URLs criadas!" -ForegroundColor Green

# 3. CRIAR ADMIN
Write-Host "👨‍💼 Criando admin..." -ForegroundColor Cyan

@"
from django.contrib import admin
from .models import Proprietario, Propriedade, ProjetoCredito, Documento

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado', 'created_at']
    search_fields = ['nome', 'cpf', 'cidade', 'email']
    list_filter = ['estado', 'cidade', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado', 'created_at']
    search_fields = ['nome', 'proprietario__nome', 'municipio', 'matricula']
    list_filter = ['estado', 'municipio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(ProjetoCredito)
class ProjetoCreditoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'propriedade', 'tipo', 'valor_solicitado', 'status', 'data_inicio']
    search_fields = ['titulo', 'propriedade__nome', 'propriedade__proprietario__nome']
    list_filter = ['tipo', 'status', 'data_inicio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'projeto', 'tipo', 'data_upload']
    search_fields = ['nome', 'projeto__titulo']
    list_filter = ['tipo', 'data_upload']
    readonly_fields = ['data_upload']
    ordering = ['-data_upload']
"@ | Out-File -FilePath "gestao_rural/admin.py" -Encoding UTF8

Write-Host "✅ Admin criado!" -ForegroundColor Green

Write-Host "🎉 SISTEMA COMPLETO CRIADO!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. python manage.py makemigrations" -ForegroundColor White
Write-Host "2. python manage.py migrate" -ForegroundColor White
Write-Host "3. python manage.py createsuperuser" -ForegroundColor White
Write-Host "4. python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Acesse: http://127.0.0.1:8000" -ForegroundColor Green


