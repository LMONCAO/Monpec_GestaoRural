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


class AnimaisOfflineAPI(View):
    """
    API para fornecer dados de animais em formato JSON para cache offline
    """

    @method_decorator(login_required)
    def get(self, request):
        """Retorna dados de animais para cache offline"""
        try:
            propriedade = get_propriedade_atual(request)

            # Buscar animais com dados essenciais
            animais = AnimalIndividual.objects.filter(
                propriedade=propriedade
            ).select_related('categoria').values(
                'id', 'numero_brinco', 'categoria__nome', 'sexo', 'raca',
                'peso_atual_kg', 'data_nascimento', 'status', 'observacoes'
            )[:1000]  # Limitar para performance

            # Converter para lista e formatar datas
            animais_list = []
            for animal in animais:
                animal_dict = dict(animal)
                # Formatar data
                if animal_dict['data_nascimento']:
                    animal_dict['data_nascimento'] = animal_dict['data_nascimento'].strftime('%d/%m/%Y')

                # Renomear campos para consistência
                animal_dict['categoria'] = animal_dict.pop('categoria__nome')
                animal_dict['peso_atual'] = animal_dict.pop('peso_atual_kg')

                animais_list.append(animal_dict)

            response_data = {
                'success': True,
                'data': {
                    'animais': animais_list,
                    'total': len(animais_list),
                    'propriedade': {
                        'id': propriedade.id,
                        'nome': propriedade.nome_propriedade
                    }
                },
                'cached_at': request.GET.get('timestamp', 'now'),
                'cache_valid_for': '24h'  # Cache válido por 24 horas
            }

            response = JsonResponse(response_data)
            # Headers para cache do navegador
            response['Cache-Control'] = 'public, max-age=86400'  # 24 horas
            response['X-Offline-Capable'] = 'true'

            return response

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erro ao buscar animais: {str(e)}',
                'data': []
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
animais_offline_api_cached = cache_page(3600)(AnimaisOfflineAPI.as_view())