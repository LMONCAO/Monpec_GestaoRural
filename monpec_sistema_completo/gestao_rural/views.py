from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .consolidacao_financeira import consolidar_dados_propriedade

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'gestao_rural/login.html')

@login_required
def dashboard(request):
    produtores = ProdutorRural.objects.count()
    propriedades = Propriedade.objects.count()
    return render(request, 'gestao_rural/dashboard.html', {
        'produtores': produtores,
        'propriedades': propriedades
    })

@login_required
def listar_propriedades(request):
    propriedades = Propriedade.objects.all()
    return render(request, 'gestao_rural/listar_propriedades.html', {'propriedades': propriedades})

@login_required
def detalhes_propriedade(request, pk):
    prop = get_object_or_404(Propriedade, pk=pk)
    dados = consolidar_dados_propriedade(prop)
    return render(request, 'gestao_rural/detalhes_propriedade.html', {
        'propriedade': prop,
        'dados': dados
    })
