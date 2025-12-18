@echo off
chcp 65001 >nul
echo ========================================================================
echo REGERAR RECEITAS BASEADAS NAS VENDAS REAIS DO PLANEJAMENTO
echo ========================================================================
echo.
echo Este script vai:
echo 1. Excluir receitas financeiras de 2022 (geradas aleatoriamente)
echo 2. Criar receitas baseadas nas vendas projetadas do planejamento
echo 3. Usar datas e valores reais das vendas
echo.
echo Vendas encontradas em 2022:
echo   - 8 vendas projetadas
echo   - Valor total: R$ 6.967.047,72
echo.
pause

echo.
echo [1/3] Verificando vendas projetadas...
python verificar_vendas_projetadas.py

echo.
echo [2/3] Excluindo receitas antigas de 2022...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from gestao_rural.models_financeiro import LancamentoFinanceiro; from gestao_rural.models_financeiro import CategoriaFinanceira; receitas_2022 = LancamentoFinanceiro.objects.filter(data_competencia__year=2022, tipo=CategoriaFinanceira.TIPO_RECEITA); total = receitas_2022.count(); receitas_2022.delete(); print(f'[OK] {total} receitas excluidas')"

echo.
echo [3/3] Criando receitas baseadas nas vendas reais...
python manage.py integrar_vendas_planejamento_financeiro --ano 2022

echo.
echo ========================================================================
echo CONCLUIDO!
echo ========================================================================
echo.
echo Agora as receitas financeiras refletem as vendas reais do planejamento:
echo - Datas de recebimento = datas reais das vendas
echo - Valores = valores reais das vendas
echo - Descricoes = detalhes do que foi vendido (categoria, quantidade, cliente)
echo.
pause























