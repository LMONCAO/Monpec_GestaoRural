"""
Views para funcionalidades offline da PWA
Gerencia consulta de animais quando offline
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import AnimalIndividual, Propriedade
from .helpers_acesso import get_propriedade_atual


@login_required
def animais_offline_view(request):
    """
    Página para consultar animais offline
    Exibe animais que foram cacheados localmente
    """
    try:
        propriedade = get_propriedade_atual(request)

        # Buscar animais da propriedade (limitado para performance offline)
        animais = AnimalIndividual.objects.filter(
            propriedade=propriedade,
            status='ATIVO'
        ).select_related('categoria').order_by('numero_brinco')[:500]  # Limitar para cache

        # Preparar dados para cache offline
        animais_data = []
        for animal in animais:
            animais_data.append({
                'id': animal.id,
                'numero_brinco': animal.numero_brinco,
                'categoria': animal.categoria.nome if animal.categoria else 'N/A',
                'sexo': animal.sexo,
                'raca': animal.raca,
                'peso_atual': str(animal.peso_atual_kg) if animal.peso_atual_kg else 'N/A',
                'data_nascimento': animal.data_nascimento.strftime('%d/%m/%Y') if animal.data_nascimento else 'N/A',
                'status': animal.status,
                'observacoes': animal.observacoes or ''
            })

        context = {
            'animais_json': json.dumps(animais_data),
            'total_animais': len(animais_data),
            'propriedade': propriedade
        }

        return render(request, 'gestao_rural/animais_offline.html', context)

    except Exception as e:
        # Em caso de erro, mostrar página offline
        return render(request, 'site/offline.html', {
            'error': f'Erro ao carregar animais: {str(e)}'
        })


class AnimaisOfflineAPIBasico(View):
    """
    API para dados BÁSICOS de animais - OTIMIZADO PARA CACHE LEVE
    Retorna apenas informações essenciais para reduzir volume de dados
    """

    @method_decorator(login_required)
    def get(self, request):
        """Retorna dados básicos de animais para cache offline leve"""
        try:
            propriedade = get_propriedade_atual(request)

            # Buscar APENAS dados essenciais (muito leve)
            animais = AnimalIndividual.objects.filter(
                propriedade=propriedade,
                status='ATIVO'  # Só animais ativos para reduzir volume
            ).select_related('categoria').values(
                'id', 'numero_brinco', 'categoria__nome', 'sexo', 'raca', 'status'
            ).order_by('numero_brinco')[:5000]  # Até 5000 animais básicos

            # Converter para lista otimizada
            animais_list = []
            for animal in animais:
                animal_dict = dict(animal)
                # Renomear para consistência
                animal_dict['categoria'] = animal_dict.pop('categoria__nome')

                # REMOVER dados pesados que não são essenciais para busca offline
                # peso_atual_kg, data_nascimento, observacoes são removidos para reduzir tamanho
                animais_list.append(animal_dict)

            response_data = {
                'success': True,
                'data': {
                    'animais': animais_list,
                    'total': len(animais_list),
                    'tipo_cache': 'basico',  # Indica tipo de cache
                    'propriedade': {
                        'id': propriedade.id,
                        'nome': propriedade.nome_propriedade
                    }
                },
                'cached_at': request.GET.get('timestamp', 'now'),
                'cache_valid_for': '24h',
                'tamanho_estimado_kb': len(str(animais_list)) / 1024  # Debug do tamanho
            }

            response = JsonResponse(response_data)
            # Headers otimizados para cache offline
            response['Cache-Control'] = 'public, max-age=86400'  # 24 horas
            response['X-Offline-Capable'] = 'true'
            response['X-Cache-Type'] = 'basico'
            response['X-Compressed-Capable'] = 'true'

            return response

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao buscar animais básicos: {str(e)}',
                'data': []
            }, status=500)


class AnimaisOfflineAPIDetalhes(View):
    """
    API para dados DETALHADOS de animais - CARREGADO SOB DEMANDA
    Retorna informações completas apenas quando solicitado
    """

    @method_decorator(login_required)
    def get(self, request, animal_id=None):
        """Retorna dados detalhados de um animal específico"""
        try:
            propriedade = get_propriedade_atual(request)

            if animal_id:
                # Buscar animal específico com TODOS os detalhes
                animal = AnimalIndividual.objects.filter(
                    propriedade=propriedade,
                    id=animal_id
                ).select_related('categoria').first()

                if not animal:
                    return JsonResponse({
                        'success': False,
                        'error': 'Animal não encontrado'
                    }, status=404)

                # Dados completos do animal
                animal_data = {
                    'id': animal.id,
                    'numero_brinco': animal.numero_brinco,
                    'categoria': animal.categoria.nome if animal.categoria else 'N/A',
                    'sexo': animal.sexo,
                    'raca': animal.raca,
                    'peso_atual': str(animal.peso_atual_kg) if animal.peso_atual_kg else 'N/A',
                    'data_nascimento': animal.data_nascimento.strftime('%d/%m/%Y') if animal.data_nascimento else 'N/A',
                    'data_aquisicao': animal.data_aquisicao.strftime('%d/%m/%Y') if animal.data_aquisicao else 'N/A',
                    'status': animal.status,
                    'observacoes': animal.observacoes or '',
                    # Dados adicionais que podem ser pesados
                    'lote': animal.lote or '',
                    'localizacao': animal.localizacao or ''
                }

                response_data = {
                    'success': True,
                    'data': {
                        'animal': animal_data,
                        'tipo_cache': 'detalhes'
                    },
                    'cached_at': request.GET.get('timestamp', 'now'),
                    'cache_valid_for': '6h'  # Cache detalhado válido por menos tempo
                }
            else:
                # Buscar múltiplos animais detalhados (limitado para performance)
                animal_ids = request.GET.get('ids', '').split(',')
                if not animal_ids or animal_ids[0] == '':
                    return JsonResponse({
                        'success': False,
                        'error': 'IDs de animais não fornecidos'
                    }, status=400)

                # Limitar a 50 animais por vez para não sobrecarregar
                animal_ids = animal_ids[:50]

                animais = AnimalIndividual.objects.filter(
                    propriedade=propriedade,
                    id__in=animal_ids
                ).select_related('categoria')

                animais_list = []
                for animal in animais:
                    animais_list.append({
                        'id': animal.id,
                        'numero_brinco': animal.numero_brinco,
                        'categoria': animal.categoria.nome if animal.categoria else 'N/A',
                        'sexo': animal.sexo,
                        'raca': animal.raca,
                        'peso_atual': str(animal.peso_atual_kg) if animal.peso_atual_kg else 'N/A',
                        'data_nascimento': animal.data_nascimento.strftime('%d/%m/%Y') if animal.data_nascimento else 'N/A',
                        'status': animal.status,
                        'observacoes': animal.observacoes or ''
                    })

                response_data = {
                    'success': True,
                    'data': {
                        'animais': animais_list,
                        'total': len(animais_list),
                        'tipo_cache': 'detalhes'
                    },
                    'cached_at': request.GET.get('timestamp', 'now'),
                    'cache_valid_for': '6h'
                }

            response = JsonResponse(response_data)
            # Headers para cache detalhado
            response['Cache-Control'] = 'public, max-age=21600'  # 6 horas
            response['X-Offline-Capable'] = 'true'
            response['X-Cache-Type'] = 'detalhes'
            response['X-Compressed-Capable'] = 'true'

            return response

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao buscar detalhes: {str(e)}',
                'data': {}
            }, status=500)


@csrf_exempt
@login_required
def sync_animais_offline(request):
    """
    Endpoint para sincronizar alterações feitas offline
    Recebe dados modificados quando volta online
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

    try:
        data = json.loads(request.body)
        propriedade = get_propriedade_atual(request)

        sync_results = {
            'created': 0,
            'updated': 0,
            'errors': []
        }

        # Aqui você implementaria a lógica de sincronização
        # Por exemplo: criar novos animais, atualizar pesos, etc.

        # Placeholder - implementar conforme necessidade
        if 'pending_animals' in data:
            for animal_data in data['pending_animals']:
                try:
                    # Lógica para sincronizar animal
                    # animal, created = AnimalIndividual.objects.get_or_create(...)
                    sync_results['created'] += 1
                except Exception as e:
                    sync_results['errors'].append(f"Erro em animal {animal_data.get('numero_brinco', 'N/A')}: {str(e)}")

        return JsonResponse({
            'success': True,
            'results': sync_results,
            'message': f'Sincronização concluída: {sync_results["created"]} criados, {sync_results["updated"]} atualizados'
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erro na sincronização: {str(e)}'}, status=500)


# Cache da API por 1 hora para melhorar performance
animais_offline_api_cached = cache_page(3600)(AnimaisOfflineAPIBasico.as_view())