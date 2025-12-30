@echo off
chcp 65001 >nul
echo ========================================================================
echo INTEGRAR VENDAS DO PLANEJAMENTO COM O FINANCEIRO
echo ========================================================================
echo.
echo Este comando cria lancamentos financeiros baseados nas vendas projetadas
echo do planejamento/cenario, usando as datas e valores reais.
echo.
echo Caracteristicas:
echo - Data de recebimento = data_recebimento ou data_venda
echo - Data de competencia = data de recebimento
echo - Valor = valor_total da venda
echo - Descricao inclui: categoria, quantidade, cliente, peso, valor/kg
echo.
pause

echo.
echo Executando integracao...
python manage.py integrar_vendas_planejamento_financeiro --ano 2022

echo.
echo ========================================================================
echo CONCLUIDO!
echo ========================================================================
echo.
pause



























