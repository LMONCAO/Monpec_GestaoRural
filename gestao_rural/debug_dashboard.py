# -*- coding: utf-8 -*-
"""
Script de Auditoria do Dashboard de Pecuária
Verifica se todos os dados estão sendo buscados e passados corretamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_gestao_rural.settings')
django.setup()

from django.contrib.auth.models import User
from gestao_rural.models import Propriedade
from gestao_rural.views_pecuaria_completa import pecuaria_completa_dashboard
from django.test import RequestFactory
from datetime import date, timedelta

def auditar_dashboard():
    """Audita o dashboard completo"""
    print("=" * 80)
    print("AUDITORIA DO DASHBOARD DE PECUÁRIA")
    print("=" * 80)
    
    # 1. Verificar se há propriedades
    print("\n1. VERIFICANDO PROPRIEDADES...")
    propriedades = Propriedade.objects.all()
    print(f"   Total de propriedades: {propriedades.count()}")
    
    if propriedades.count() == 0:
        print("   ❌ ERRO: Nenhuma propriedade encontrada!")
        return
    
    propriedade = propriedades.first()
    print(f"   ✓ Propriedade selecionada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
    
    # 2. Verificar usuário
    print("\n2. VERIFICANDO USUÁRIO...")
    usuarios = User.objects.all()
    if usuarios.count() == 0:
        print("   ❌ ERRO: Nenhum usuário encontrado!")
        return
    
    usuario = usuarios.first()
    print(f"   ✓ Usuário selecionado: {usuario.username}")
    
    # 3. Criar request simulado
    print("\n3. CRIANDO REQUEST SIMULADO...")
    factory = RequestFactory()
    request = factory.get(f'/propriedade/{propriedade.id}/pecuaria/dashboard/')
    request.user = usuario
    
    # 4. Verificar dados do banco antes de chamar a view
    print("\n4. VERIFICANDO DADOS NO BANCO...")
    
    # Inventário
    from gestao_rural.models import InventarioRebanho
    inventarios = InventarioRebanho.objects.filter(propriedade=propriedade)
    print(f"   Inventários: {inventarios.count()}")
    if inventarios.exists():
        total_animais = sum(i.quantidade or 0 for i in inventarios)
        print(f"   Total de animais no inventário: {total_animais}")
    
    # Animais Individuais
    try:
        from gestao_rural.models_pecuaria import AnimalIndividual
        animais = AnimalIndividual.objects.filter(propriedade=propriedade, status='ATIVO')
        print(f"   Animais Individuais Ativos: {animais.count()}")
    except Exception as e:
        print(f"   ⚠ Não foi possível buscar AnimalIndividual: {e}")
    
    # Lançamentos Financeiros
    try:
        from gestao_rural.models_financeiro import LancamentoFinanceiro
        lancamentos = LancamentoFinanceiro.objects.filter(propriedade=propriedade)
        print(f"   Lançamentos Financeiros: {lancamentos.count()}")
        if lancamentos.exists():
            receitas = lancamentos.filter(tipo='RECEITA')
            despesas = lancamentos.filter(tipo='DESPESA')
            print(f"   - Receitas: {receitas.count()}")
            print(f"   - Despesas: {despesas.count()}")
    except Exception as e:
        print(f"   ⚠ Não foi possível buscar LancamentoFinanceiro: {e}")
    
    # 5. Chamar a view e verificar o contexto
    print("\n5. CHAMANDO A VIEW...")
    try:
        response = pecuaria_completa_dashboard(request, propriedade.id)
        
        if hasattr(response, 'context_data'):
            context = response.context_data
        elif hasattr(response, 'context'):
            context = response.context
        else:
            print("   ❌ ERRO: Não foi possível obter o contexto da resposta")
            print(f"   Tipo de resposta: {type(response)}")
            return
        
        print("\n6. VERIFICANDO CONTEXTO RETORNADO...")
        
        # Verificar variáveis principais
        variaveis_principais = [
            'total_animais_inventario',
            'valor_total_rebanho',
            'receitas_mes',
            'despesas_mes',
            'saldo_mes',
            'total_custos_operacionais',
            'margem_lucro',
        ]
        
        for var in variaveis_principais:
            valor = context.get(var, 'NÃO ENCONTRADO')
            print(f"   {var}: {valor} (tipo: {type(valor).__name__})")
        
        # Verificar se há dados
        print("\n7. RESUMO DOS DADOS...")
        total_animais = context.get('total_animais_inventario', 0)
        receitas = context.get('receitas_mes', 0)
        despesas = context.get('despesas_mes', 0)
        
        if total_animais == 0 and receitas == 0 and despesas == 0:
            print("   ⚠ ATENÇÃO: Todos os valores estão zerados!")
            print("   Isso pode indicar:")
            print("   - Não há dados cadastrados")
            print("   - Os dados não estão sendo buscados corretamente")
            print("   - Há um problema com os filtros de data")
        else:
            print("   ✓ Dados encontrados no contexto")
        
        print("\n8. VERIFICANDO TEMPLATE...")
        if hasattr(response, 'template_name'):
            print(f"   Template: {response.template_name}")
        elif hasattr(response, 'rendered_content'):
            print("   ✓ Template renderizado com sucesso")
            # Verificar se há conteúdo renderizado
            if len(response.rendered_content) < 100:
                print("   ⚠ ATENÇÃO: Template renderizado mas conteúdo muito pequeno!")
        else:
            print("   ⚠ Não foi possível verificar o template")
        
        print("\n" + "=" * 80)
        print("AUDITORIA CONCLUÍDA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO ao chamar a view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    auditar_dashboard()





