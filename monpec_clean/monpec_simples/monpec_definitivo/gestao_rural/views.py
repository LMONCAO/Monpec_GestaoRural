from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Count
from .models import Proprietario, Propriedade, Categoria, ItemInventario
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
    total_categorias = Categoria.objects.count()
    total_itens = ItemInventario.objects.count()
    
    # Estatísticas por propriedade
    propriedades_stats = Propriedade.objects.annotate(
        total_itens=Count('itens_inventario'),
        valor_total=Sum('itens_inventario__valor_total')
    ).order_by('-created_at')[:5]
    
    context = {
        'total_proprietarios': total_proprietarios,
        'total_propriedades': total_propriedades,
        'total_categorias': total_categorias,
        'total_itens': total_itens,
        'propriedades_stats': propriedades_stats,
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
            endereco = data.get('endereco', '')
            cidade = data.get('cidade', '')
            estado = data.get('estado', '')
            observacoes = data.get('observacoes', '')
            
            if not nome or not cpf:
                return JsonResponse({'success': False, 'message': 'Nome e CPF são obrigatórios!'})
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                return JsonResponse({'success': False, 'message': 'CPF já cadastrado!'})
            
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
    propriedades = Propriedade.objects.select_related('proprietario').annotate(
        total_itens=Count('itens_inventario'),
        valor_total=Sum('itens_inventario__valor_total')
    )
    
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
    return render(request, 'gestao_rural/projetos_dashboard.html', {'propriedade': propriedade})

@login_required
def categorias_lista(request):
    categorias = Categoria.objects.all()
    return render(request, 'gestao_rural/categorias_lista.html', {'categorias': categorias})

@login_required
def inventario_lista(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    itens = ItemInventario.objects.filter(propriedade=propriedade).select_related('categoria')
    return render(request, 'gestao_rural/inventario_lista.html', {
        'propriedade': propriedade,
        'itens': itens
    })
