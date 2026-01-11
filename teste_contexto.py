#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import PlanejamentoAnual, CenarioPlanejamento
from gestao_rural.views_pecuaria_completa import _montar_contexto_planejamento

planejamento = PlanejamentoAnual.objects.filter(propriedade_id=5, ano=2026).first()
if planejamento:
    # Simular a lógica da view principal
    cenario = planejamento.cenarios.filter(is_baseline=True).first()
    print(f'Cenario baseline encontrado: {cenario is not None}')
    if cenario:
        print(f'Cenario: {cenario.nome}')

    from gestao_rural.models import Propriedade
    propriedade = Propriedade.objects.get(id=5)

    context = _montar_contexto_planejamento(propriedade, planejamento, cenario)

    # Simular o que a view principal faz
    context['cenario_atual'] = cenario

    print('Contexto criado:')
    print(f'planejamento existe: {context.get("planejamento") is not None}')
    print(f'cenario existe: {context.get("cenario") is not None}')
    print(f'cenario_atual existe: {context.get("cenario_atual") is not None}')
    print(f'total_animais: {context.get("total_animais", 0)}')
    print(f'total_vendas_qtd: {context.get("total_vendas_qtd", 0)}')
    print(f'metricas_cenario existe: {context.get("metricas_cenario") is not None}')

    if context.get('metricas_cenario'):
        metricas = context['metricas_cenario']
        print(f'receitas: {metricas.get("receitas_totais", 0)}')
        print(f'custos: {metricas.get("custos_totais", 0)}')
        print(f'lucro: {metricas.get("lucro", 0)}')
else:
    print('Planejamento não encontrado')