@echo off
chcp 65001 >nul
echo ========================================================================
echo REGERAR DADOS FINANCEIROS 2022 COM VALORES REAIS
echo ========================================================================
echo.
echo Este script vai:
echo 1. Excluir TODOS os lancamentos financeiros de 2022 (receitas e despesas)
echo 2. Criar receitas baseadas nas vendas REAIS do planejamento
echo 3. Criar despesas proporcionais e realistas
echo.
echo IMPORTANTE: Os valores serao baseados nas vendas reais do planejamento!
echo.
pause

echo.
echo [1/4] Verificando vendas projetadas...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from gestao_rural.models import VendaProjetada; from django.db.models import Sum; vendas = VendaProjetada.objects.filter(data_venda__year=2022); total = vendas.count(); valor = vendas.aggregate(total=Sum('valor_total'))['total'] or 0; print(f'Vendas encontradas: {total}'); print(f'Valor total: R$ {valor:,.2f}')"

echo.
echo [2/4] Excluindo TODOS os lancamentos financeiros de 2022...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings'); django.setup(); from gestao_rural.models_financeiro import LancamentoFinanceiro; from gestao_rural.models_compras_financeiro import NotaFiscal; lancamentos = LancamentoFinanceiro.objects.filter(data_competencia__year=2022); notas = NotaFiscal.objects.filter(data_emissao__year=2022); total_lanc = lancamentos.count(); total_notas = notas.count(); lancamentos.delete(); notas.delete(); print(f'[OK] {total_lanc} lancamentos e {total_notas} notas excluidos')"

echo.
echo [3/4] Criando receitas baseadas nas vendas REAIS do planejamento...
python manage.py integrar_vendas_planejamento_financeiro --ano 2022

echo.
echo [4/4] Criando despesas proporcionais e realistas...
echo (Baseadas nas receitas reais, sem gerar receitas aleatorias)
python gerar_despesas_proporcionais.py

echo.
echo ========================================================================
echo CONCLUIDO!
echo ========================================================================
echo.
echo Agora os dados financeiros refletem:
echo - Receitas: Baseadas nas vendas REAIS do planejamento
echo - Despesas: Proporcionais e realistas (aproximadamente 90%% das receitas)
echo.
pause

