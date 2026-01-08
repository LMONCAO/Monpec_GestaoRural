#!/usr/bin/env python
"""
Script para mostrar resumo completo da Fazenda Demonstração
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, CategoriaAnimal, AnimalIndividual
from gestao_rural.models_funcionarios import Funcionario
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_operacional import Equipamento
from gestao_rural.models_compras_financeiro import Fornecedor

def main():
    print("="*80)
    print("RESUMO COMPLETO - FAZENDA DEMONSTRACAO")
    print("="*80)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"PROPRIEDADE: {propriedade.nome_propriedade}")
    print(f"   Localizacao: {propriedade.municipio}/{propriedade.uf}")
    print(f"   Area: {propriedade.area_total_ha} hectares")
    print()

    # Pecuária
    print("MODULO PECUARIA:")
    print(f"   - Categorias de Animais: {CategoriaAnimal.objects.count()}")
    print(f"   - Animais Individuais: {AnimalIndividual.objects.filter(propriedade=propriedade).count()}")

    # Detalhes dos animais
    animais = AnimalIndividual.objects.filter(propriedade=propriedade)
    if animais.exists():
        from collections import Counter
        categorias = Counter()
        sexos = Counter()

        for animal in animais:
            categorias[animal.categoria.nome] += 1
            sexos[animal.sexo] += 1

        print("   - Por categoria:")
        for cat, count in sorted(categorias.items()):
            print(f"     * {cat}: {count}")

        print(f"   - Por sexo: {dict(sexos)}")
    print()

    # Recursos Humanos
    print("RECURSOS HUMANOS:")
    funcionarios = Funcionario.objects.filter(propriedade=propriedade)
    print(f"   - Funcionarios: {funcionarios.count()}")

    if funcionarios.exists():
        salarios = [f.salario_base for f in funcionarios if f.salario_base]
        if salarios:
            total_salarios = sum(salarios)
            media_salarios = total_salarios / len(salarios)
            print(f"     * Total salarios: R$ {total_salarios:.2f}")
            print(f"     * Media salarial: R$ {media_salarios:.2f}")
        # Listar funcionários
        print("   - Equipe:")
        for func in funcionarios.order_by('cargo'):
            print(f"     * {func.nome} - {func.cargo} (R$ {func.salario_base:.2f})")
    print()

    # Infraestrutura
    print("INFRAESTRUTURA:")
    pastagens = Pastagem.objects.filter(propriedade=propriedade)
    cochos = Cocho.objects.filter(propriedade=propriedade)
    equipamentos = Equipamento.objects.filter(propriedade=propriedade)

    print(f"   - Pastagens: {pastagens.count()}")
    if pastagens.exists():
        area_total = sum(p.area_ha for p in pastagens)
        print(f"     * Area total pastagens: {area_total:.2f} ha")
        print("   - Pastagens:")
        for past in pastagens:
            print(f"     * {past.nome} - {past.area_ha} ha ({past.tipo_pastagem})")

    print(f"   - Cochos: {cochos.count()}")
    if cochos.exists():
        tipos_cochos = {}
        for cocho in cochos:
            tipo = cocho.tipo_cocho
            tipos_cochos[tipo] = tipos_cochos.get(tipo, 0) + 1
        print(f"   - Por tipo: {tipos_cochos}")

    print(f"   - Equipamentos: {equipamentos.count()}")
    if equipamentos.exists():
        print("   - Equipamentos:")
        for equip in equipamentos:
            print(f"     * {equip.nome} ({equip.marca} {equip.ano})")
    print()

    # Fornecedores
    print("FORNECEDORES:")
    fornecedores = Fornecedor.objects.filter(propriedade=propriedade)
    print(f"   - Total: {fornecedores.count()}")

    if fornecedores.exists():
        tipos_fornec = {}
        for fornec in fornecedores:
            tipo = fornec.tipo
            tipos_fornec[tipo] = tipos_fornec.get(tipo, 0) + 1

        print(f"   - Por tipo: {tipos_fornec}")
        print("   - Lista:")
        for fornec in fornecedores.order_by('tipo'):
            print(f"     * {fornec.nome_fantasia} - {fornec.tipo}")
    print()

    # Estatísticas gerais
    print("ESTATISTICAS GERAIS:")
    print(f"   - Area total: {propriedade.area_total_ha} hectares")
    print(f"   - Rebanho: {animais.count()} animais")
    print(f"   - Equipe: {funcionarios.count()} funcionarios")
    print(f"   - Infraestrutura: {pastagens.count()} pastagens + {cochos.count()} cochos")
    print(f"   - Equipamentos: {equipamentos.count()}")
    print(f"   - Rede de fornecedores: {fornecedores.count()}")
    print()

    # Próximos passos
    print("PROXIMOS PASSOS PARA COMPLETAR:")
    print("   - Modulo Financeiro (contas, lancamentos)")
    print("   - Modulo de Compras (ordens, notas fiscais)")
    print("   - Modulo de Vendas (receitas)")
    print("   - Modulo Nutricional (suplementacao, distribuicao)")
    print("   - Modulo Operacional (combustivel, manutencao)")
    print("   - Historico de 24 meses + projecoes 6 meses")
    print()

    print("="*80)
    print("FAZENDA DEMONSTRACAO PRONTA PARA DEMONSTRACOES!")
    print("Sistema com dados realistas para apresentacoes")
    print("="*80)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
