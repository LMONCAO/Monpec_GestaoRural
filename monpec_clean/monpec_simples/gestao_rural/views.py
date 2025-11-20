from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Proprietario, Propriedade
import json

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
    
    context = {
        'total_proprietarios': total_proprietarios,
        'total_propriedades': total_propriedades,
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
    
    return render(request, 'gestao_rural/proprietarios_lista.html', {
        'proprietarios': proprietarios,
        'search': search
    })

@login_required
@csrf_exempt
def proprietario_novo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            cpf = data.get('cpf')
            telefone = data.get('telefone', '')
            email = data.get('email', '')
            cidade = data.get('cidade', '')
            estado = data.get('estado', '')
            
            if not nome or not cpf:
                return JsonResponse({'success': False, 'message': 'Nome e CPF são obrigatórios!'})
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                return JsonResponse({'success': False, 'message': 'CPF já cadastrado!'})
            
            proprietario = Proprietario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                cidade=cidade,
                estado=estado
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'Proprietário {nome} cadastrado com sucesso!',
                'proprietario': {
                    'id': proprietario.id,
                    'nome': proprietario.nome,
                    'cpf': proprietario.cpf,
                    'telefone': proprietario.telefone or '',
                    'email': proprietario.email or '',
                    'cidade': proprietario.cidade or '',
                    'estado': proprietario.estado or '',
                    'created_at': proprietario.created_at.strftime('%d/%m/%Y')
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao cadastrar: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def propriedades_lista(request):
    search = request.GET.get('search', '')
    propriedades = Propriedade.objects.select_related('proprietario')
    
    if search:
        propriedades = propriedades.filter(
            Q(nome__icontains=search) | 
            Q(proprietario__nome__icontains=search) |
            Q(municipio__icontains=search)
        )
    
    return render(request, 'gestao_rural/propriedades_lista.html', {
        'propriedades': propriedades,
        'search': search
    })
