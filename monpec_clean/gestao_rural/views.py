from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from .models import Proprietario, Propriedade, ProjetoCredito
import json
from datetime import datetime, date
import csv

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
    total_proprietarios = Proprietario.objects.count()
    total_propriedades = Propriedade.objects.count()
    total_projetos = ProjetoCredito.objects.count()
    projetos_aprovados = ProjetoCredito.objects.filter(status='aprovado').count()
    
    projetos_recentes = ProjetoCredito.objects.select_related('propriedade__proprietario').order_by('-created_at')[:5]
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
