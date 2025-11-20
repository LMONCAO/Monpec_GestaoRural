from django.shortcuts import render

def landing_page(request):
    """Página de landing do sistema Monpec"""
    return render(request, 'gestao_rural/landing.html')

