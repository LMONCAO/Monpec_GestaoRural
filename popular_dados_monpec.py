#!/usr/bin/env python
"""
Script para popular dados de pecuária realistas para Monpec Agropecuaria Ltda
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from gestao_rural.models import (
    ProdutorRural, Propriedade,
    CategoriaAnimal, AnimalIndividual, AnimalPesagem, AnimalVacinaAplicada,
    AnimalTratamento, AnimalReproducaoEvento, InventarioRebanho, CurralLote, CurralSessao
)

User = get_user_model()

def main():
    print("="*70)
    print("POPULANDO DADOS DE PECUARIA - MONPEC AGROPECUARIA LTDA")
    print("="*70)

    # Criar usuário se não existir
    usuario, created = User.objects.get_or_create(
        username='monpec',
        defaults={
            'email': 'admin@monpec.com.br',
            'first_name': 'Monpec',
            'last_name': 'Agropecuária',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        usuario.set_password('monpec2024')
        usuario.save()
        print("[OK] Usuario 'monpec' criado")
    else:
        print("[OK] Usuario 'monpec' ja existe")

    # Criar produtor se não existir
    produtor, created = ProdutorRural.objects.get_or_create(
        cpf_cnpj='12.345.678/0001-90',
        defaults={
            'nome': 'Monpec Agropecuaria Ltda',
            'email': 'contato@monpec.com.br',
            'telefone': '(11) 99999-9999',
            'endereco': 'Rua Principal, 123',
            'usuario_responsavel': usuario,
            'vai_emitir_nfe': True
        }
    )
    if created:
        print("[OK] Produtor 'Monpec Agropecuaria Ltda' criado")
    else:
        print("[OK] Produtor 'Monpec Agropecuaria Ltda' ja existe")

    # Verificar se propriedade já existe
    propriedade = Propriedade.objects.filter(nome_propriedade='Monpec', produtor=produtor).first()
    if propriedade:
        print("[OK] Propriedade 'Monpec' ja existe")
    else:
        # Se não existir, tentar criar com campos mínimos
        try:
            propriedade = Propriedade.objects.create(
                nome_propriedade='Monpec',
                produtor=produtor,
                municipio='Sao Paulo',
                uf='SP',
                area_total_ha=500.00
            )
            print("[OK] Propriedade 'Monpec' criada")
        except Exception as e:
            print(f"Erro ao criar propriedade: {e}")
            # Buscar qualquer propriedade do produtor
            propriedade = Propriedade.objects.filter(produtor=produtor).first()
            if propriedade:
                print(f"[OK] Usando propriedade existente: {propriedade.nome_propriedade}")
            else:
                print("ERRO: Nenhuma propriedade encontrada!")
                return
    
    print(f"\nProdutor: {produtor.nome}")
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Usuario: {usuario.username}\n")
    
    # 1. Criar categorias
    print("[1/7] Criando categorias de animais...")
    categorias = criar_categorias()
    print(f"OK: {len(categorias)} categorias criadas/verificadas\n")
    
    # 2. Criar animais
    print("[2/7] Criando animais individuais...")
    animais = criar_animais(propriedade, categorias, usuario)
    animais_femeas = [a for a in animais if a.sexo == 'F']
    animais_machos = [a for a in animais if a.sexo == 'M']
    print(f"OK: {len(animais)} animais criados ({len(animais_femeas)} femeas, {len(animais_machos)} machos)\n")
    
    # 3. Criar pesagens
    print("[3/7] Criando historico de pesagens...")
    pesagens_criadas = criar_pesagens(animais, usuario)
    print(f"OK: {pesagens_criadas} pesagens criadas\n")
    
    # 4. Criar reprodução
    print("[4/7] Criando eventos de reproducao...")
    eventos_reproducao = criar_reproducao(animais_femeas, animais_machos, usuario)
    print(f"OK: {eventos_reproducao} eventos de reproducao criados\n")
    
    # 5. Criar vacinas e tratamentos
    print("[5/7] Criando vacinas e tratamentos...")
    vacinas_criadas, tratamentos_criados = criar_vacinas_tratamentos(animais, usuario)
    print(f"OK: {vacinas_criadas} vacinas criadas")
    print(f"OK: {tratamentos_criados} tratamentos criados\n")
    
    # 6. Criar lotes
    print("[6/7] Criando lotes de curral...")
    lotes_criados = criar_lotes(propriedade, animais)
    print(f"OK: {lotes_criados} lotes criados\n")
    
    # 7. Criar inventário
    print("[7/7] Criando inventario do rebanho...")
    inventario_criado = criar_inventario(propriedade, categorias)
    print(f"OK: {inventario_criado} itens de inventario criados\n")
    
    # Resumo final
    print("="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Total de Animais: {len(animais)}")
    print(f"  - Fêmeas: {len(animais_femeas)}")
    print(f"  - Machos: {len(animais_machos)}")
    print(f"Total de Pesagens: {AnimalPesagem.objects.filter(animal__propriedade=propriedade).count()}")
    print(f"Total de Eventos Reprodutivos: {AnimalReproducaoEvento.objects.filter(animal__propriedade=propriedade).count()}")
    print(f"Total de Vacinas: {AnimalVacinaAplicada.objects.filter(animal__propriedade=propriedade).count()}")
    print(f"Total de Tratamentos: {AnimalTratamento.objects.filter(animal__propriedade=propriedade).count()}")
    print(f"Total de Lotes: {CurralLote.objects.filter(sessao__propriedade=propriedade).count()}")
    print(f"Total de Itens de Inventário: {InventarioRebanho.objects.filter(propriedade=propriedade).count()}")
    print("="*70)
    print("\nOK: DADOS POPULADOS COM SUCESSO!")

def criar_categorias():
    """Cria categorias de animais"""
    categorias_data = [
        {'nome': 'Vaca em Lactação', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('450.00')},
        {'nome': 'Vaca Seca', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('480.00')},
        {'nome': 'Vaca Prenhe', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('500.00')},
        {'nome': 'Novilha', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 18, 'idade_maxima_meses': 35, 'peso_medio_kg': Decimal('320.00')},
        {'nome': 'Bezerra', 'sexo': 'F', 'raca': 'NELORE', 'idade_maxima_meses': 17, 'peso_medio_kg': Decimal('150.00')},
        {'nome': 'Touro Reprodutor', 'sexo': 'M', 'raca': 'NELORE', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('650.00')},
        {'nome': 'Touro Jovem', 'sexo': 'M', 'raca': 'NELORE', 'idade_minima_meses': 12, 'idade_maxima_meses': 23, 'peso_medio_kg': Decimal('380.00')},
        {'nome': 'Bezerro', 'sexo': 'M', 'raca': 'NELORE', 'idade_maxima_meses': 11, 'peso_medio_kg': Decimal('160.00')},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria, created = CategoriaAnimal.objects.get_or_create(
            nome=cat_data['nome'],
            defaults=cat_data
        )
        categorias[cat_data['nome']] = categoria
        if created:
            print(f"  - {categoria.nome}")
    
    return categorias

def criar_animais(propriedade, categorias, usuario):
    """Cria animais individuais"""
    animais_data = []
    
    # Vacas em lactação (15)
    for i in range(1, 16):
        data_nasc = date.today() - timedelta(days=random.randint(1095, 2555))
        peso = Decimal(str(random.randint(420, 480)))
        animais_data.append({
            'numero_brinco': f'BR{1000+i:06d}',
            'categoria': categorias['Vaca em Lactação'],
            'sexo': 'F',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'LACTACAO'
        })
    
    # Vacas secas (8)
    for i in range(16, 24):
        data_nasc = date.today() - timedelta(days=random.randint(1095, 2555))
        peso = Decimal(str(random.randint(460, 500)))
        animais_data.append({
            'numero_brinco': f'BR{1000+i:06d}',
            'categoria': categorias['Vaca Seca'],
            'sexo': 'F',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'SECAGEM'
        })
    
    # Vacas prenhes (12)
    for i in range(24, 36):
        data_nasc = date.today() - timedelta(days=random.randint(1095, 2555))
        peso = Decimal(str(random.randint(480, 520)))
        animais_data.append({
            'numero_brinco': f'BR{1000+i:06d}',
            'categoria': categorias['Vaca Prenhe'],
            'sexo': 'F',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'PRENHE'
        })
    
    # Novilhas (10)
    for i in range(36, 46):
        data_nasc = date.today() - timedelta(days=random.randint(540, 1095))
        peso = Decimal(str(random.randint(280, 360)))
        animais_data.append({
            'numero_brinco': f'BR{1000+i:06d}',
            'categoria': categorias['Novilha'],
            'sexo': 'F',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'VAZIA'
        })
    
    # Bezerras (8)
    for i in range(46, 54):
        data_nasc = date.today() - timedelta(days=random.randint(60, 510))
        peso = Decimal(str(random.randint(120, 180)))
        animais_data.append({
            'numero_brinco': f'BR{1000+i:06d}',
            'categoria': categorias['Bezerra'],
            'sexo': 'F',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'INDEFINIDO'
        })
    
    # Touros reprodutores (3)
    for i in range(54, 57):
        data_nasc = date.today() - timedelta(days=random.randint(730, 1825))
        peso = Decimal(str(random.randint(600, 700)))
        animais_data.append({
            'numero_brinco': f'BR{2000+i:06d}',
            'categoria': categorias['Touro Reprodutor'],
            'sexo': 'M',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'INDEFINIDO'
        })
    
    # Bezerros (6)
    for i in range(57, 63):
        data_nasc = date.today() - timedelta(days=random.randint(30, 330))
        peso = Decimal(str(random.randint(130, 190)))
        animais_data.append({
            'numero_brinco': f'BR{3000+i:06d}',
            'categoria': categorias['Bezerro'],
            'sexo': 'M',
            'raca': 'NELORE',
            'data_nascimento': data_nasc,
            'peso_atual_kg': peso,
            'status': 'ATIVO',
            'status_reprodutivo': 'INDEFINIDO'
        })
    
    animais_criados = []
    for animal_data in animais_data:
        animal, created = AnimalIndividual.objects.get_or_create(
            numero_brinco=animal_data['numero_brinco'],
            defaults={
                **animal_data,
                'propriedade': propriedade,
                'propriedade_origem': propriedade,
                'data_identificacao': animal_data['data_nascimento'] + timedelta(days=30),
                'tipo_brinco': 'VISUAL',
                'tipo_origem': 'NASCIMENTO' if random.random() > 0.3 else 'COMPRA',
                'status_sanitario': 'APTO',
                'sistema_criacao': 'PASTO'
            }
        )
        if created:
            animais_criados.append(animal)
    
    return animais_criados

def criar_pesagens(animais, usuario):
    """Cria histórico de pesagens"""
    pesagens_criadas = 0
    for animal in animais:
        num_pesagens = random.randint(3, 6)
        peso_base = animal.peso_atual_kg or Decimal('300')
        
        for i in range(num_pesagens):
            dias_atras = random.randint(30, 180)
            data_pesagem = date.today() - timedelta(days=dias_atras)
            variacao = Decimal(str(random.randint(-20, 30)))
            peso = max(Decimal('50'), peso_base - variacao - Decimal(str(dias_atras // 30 * 5)))
            
            pesagem, created = AnimalPesagem.objects.get_or_create(
                animal=animal,
                data_pesagem=data_pesagem,
                defaults={
                    'peso_kg': peso,
                    'local': 'Balança Principal',
                    'responsavel': usuario,
                    'tipo_racao': random.choice(['Pastagem', 'Suplementação', None]),
                    'consumo_racao_kg_dia': Decimal(str(random.randint(8, 15))) if random.random() > 0.5 else None
                }
            )
            if created:
                pesagens_criadas += 1
    
    return pesagens_criadas

def criar_reproducao(animais_femeas, animais_machos, usuario):
    """Cria eventos de reprodução"""
    eventos_criados = 0
    vacas_reprodutivas = [a for a in animais_femeas if a.categoria.nome in ['Vaca em Lactação', 'Vaca Seca', 'Novilha']]
    touros = [a for a in animais_machos if a.categoria.nome == 'Touro Reprodutor']
    
    for vaca in vacas_reprodutivas[:25]:
        dias_atras = random.randint(60, 365)
        data_cobertura = date.today() - timedelta(days=dias_atras)
        touro_escolhido = random.choice(touros) if touros else None
        
        evento, created = AnimalReproducaoEvento.objects.get_or_create(
            animal=vaca,
            tipo_evento=random.choice(['COBERTURA', 'INSEMINACAO']),
            data_evento=data_cobertura,
            defaults={
                'resultado': 'Realizada',
                'touro_reprodutor': touro_escolhido.numero_brinco if touro_escolhido else 'Sêmen comercial',
                'responsavel': usuario
            }
        )
        if created:
            eventos_criados += 1
        
        if dias_atras > 45:
            data_diag = data_cobertura + timedelta(days=random.randint(30, 45))
            if data_diag < date.today():
                evento_diag, created = AnimalReproducaoEvento.objects.get_or_create(
                    animal=vaca,
                    tipo_evento='DIAGNOSTICO',
                    data_evento=data_diag,
                    defaults={
                        'resultado': 'Prenhez confirmada' if random.random() > 0.2 else 'Vazia',
                        'responsavel': usuario
                    }
                )
                if created:
                    eventos_criados += 1
        
        if dias_atras > 280 and random.random() > 0.3:
            data_parto = data_cobertura + timedelta(days=random.randint(280, 290))
            if data_parto < date.today():
                evento_parto, created = AnimalReproducaoEvento.objects.get_or_create(
                    animal=vaca,
                    tipo_evento='PARTO',
                    data_evento=data_parto,
                    defaults={
                        'resultado': random.choice(['Bezerro macho', 'Bezerra fêmea']),
                        'responsavel': usuario
                    }
                )
                if created:
                    eventos_criados += 1
    
    return eventos_criados

def criar_vacinas_tratamentos(animais, usuario):
    """Cria vacinas e tratamentos"""
    vacinas_comuns = ['Febre Aftosa', 'Brucelose', 'Raiva', 'Clostridioses', 'IBR/BVD', 'Leptospirose']
    vacinas_criadas = 0
    tratamentos_criados = 0
    
    for animal in animais:
        num_vacinas = random.randint(2, 4)
        for _ in range(num_vacinas):
            dias_atras = random.randint(30, 180)
            data_vacina = date.today() - timedelta(days=dias_atras)
            
            vacina, created = AnimalVacinaAplicada.objects.get_or_create(
                animal=animal,
                vacina=random.choice(vacinas_comuns),
                data_aplicacao=data_vacina,
                defaults={
                    'dose': '1 dose',
                    'lote_produto': f'LOTE-{random.randint(1000, 9999)}',
                    'proxima_dose': data_vacina + timedelta(days=random.randint(180, 365)),
                    'carencia_ate': data_vacina + timedelta(days=random.randint(21, 30)),
                    'responsavel': usuario
                }
            )
            if created:
                vacinas_criadas += 1
        
        if random.random() < 0.1:
            dias_atras = random.randint(10, 90)
            tratamento, created = AnimalTratamento.objects.get_or_create(
                animal=animal,
                produto=random.choice(['Ivermectina', 'Albendazol', 'Oxitetraciclina', 'Penicilina']),
                data_inicio=date.today() - timedelta(days=dias_atras),
                defaults={
                    'dosagem': random.choice(['5ml', '10ml', '1 dose']),
                    'data_fim': date.today() - timedelta(days=dias_atras - random.randint(3, 7)),
                    'carencia_ate': date.today() - timedelta(days=dias_atras - random.randint(15, 30)),
                    'motivo': random.choice(['Verminose', 'Infecção', 'Preventivo']),
                    'responsavel': usuario
                }
            )
            if created:
                tratamentos_criados += 1
    
    return vacinas_criadas, tratamentos_criados

def criar_lotes(propriedade, animais):
    """Cria lotes de curral"""
    # Criar sessão de curral primeiro
    sessao, created = CurralSessao.objects.get_or_create(
        propriedade=propriedade,
        nome='Sessão Principal - Manejo de Rotina',
        defaults={
            'tipo_trabalho': 'COLETA_DADOS',
            'status': 'ENCERRADA',
            'data_inicio': timezone.now() - timedelta(days=30),
            'data_fim': timezone.now() - timedelta(days=1)
        }
    )
    
    lotes_data = [
        {'nome': 'Lote Vacas Lactação', 'finalidade': 'REPRODUCAO', 'observacoes': 'Vacas em produção'},
        {'nome': 'Lote Vacas Secas', 'finalidade': 'PASTO', 'observacoes': 'Vacas em secagem'},
        {'nome': 'Lote Vacas Prenhes', 'finalidade': 'REPRODUCAO', 'observacoes': 'Vacas gestantes'},
        {'nome': 'Lote Novilhas', 'finalidade': 'ENGORDA', 'observacoes': 'Novilhas'},
        {'nome': 'Lote Bezerros', 'finalidade': 'ENGORDA', 'observacoes': 'Bezerros'},
        {'nome': 'Lote Touros', 'finalidade': 'REPRODUCAO', 'observacoes': 'Touros'},
    ]
    
    lotes_criados = 0
    for idx, lote_data in enumerate(lotes_data):
        lote, created = CurralLote.objects.get_or_create(
            sessao=sessao,
            nome=lote_data['nome'],
            defaults={
                'finalidade': lote_data['finalidade'],
                'observacoes': lote_data['observacoes'],
                'ordem_exibicao': idx + 1
            }
        )
        if created:
            lotes_criados += 1
        
        # Atribuir animais aos lotes
        if 'Lactação' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome == 'Vaca em Lactação'][:15]
        elif 'Secas' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome == 'Vaca Seca'][:8]
        elif 'Prenhes' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome == 'Vaca Prenhe'][:12]
        elif 'Novilhas' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome == 'Novilha'][:10]
        elif 'Bezerros' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome in ['Bezerro', 'Bezerra']][:14]
        elif 'Touros' in lote_data['nome']:
            animais_lote = [a for a in animais if a.categoria.nome == 'Touro Reprodutor'][:3]
        else:
            animais_lote = []
        
        for animal in animais_lote:
            animal.lote_atual = lote
            animal.save(update_fields=['lote_atual'])
    
    return lotes_criados

def criar_inventario(propriedade, categorias):
    """Cria inventário do rebanho"""
    inventario_criado = 0
    for categoria in categorias.values():
        quantidade = AnimalIndividual.objects.filter(
            propriedade=propriedade,
            categoria=categoria,
            status='ATIVO'
        ).count()
        
        if quantidade > 0:
            valor_por_cabeca = categoria.peso_medio_kg * Decimal('8.50')
            inventario, created = InventarioRebanho.objects.get_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=date.today(),
                defaults={
                    'quantidade': quantidade,
                    'valor_por_cabeca': valor_por_cabeca
                }
            )
            if created:
                inventario_criado += 1
    
    return inventario_criado

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

