# 📋 Guia de Refatoração - Views.py

## Objetivo
Refatorar o arquivo `views.py` principal (5276 linhas) em módulos menores e mais organizados.

## Estrutura Proposta

### Arquivos a Criar
1. `views_produtores.py` - Views de CRUD de produtores
2. `views_propriedades.py` - Views de CRUD de propriedades  
3. `views_pecuaria_basica.py` - Views básicas de pecuária (inventário, parâmetros)

### Views a Mover

#### views_produtores.py
- `produtor_novo()` - linha 1379
- `produtor_editar()` - linha 1590
- `produtor_excluir()` - linha 1616

#### views_propriedades.py
- `propriedades_lista()` - linha 1633
- `propriedade_nova()` - linha 1651
- `propriedade_editar()` - linha 1685
- `propriedade_excluir()` - linha 1707

#### views_pecuaria_basica.py
- `pecuaria_dashboard()` - linha 1721
- `pecuaria_inventario()` - linha 1744
- `pecuaria_parametros()` - linha 2004
- `pecuaria_parametros_avancados()` - linha 1925
- `pecuaria_projecao()` - linha 2106
- `pecuaria_projecao_planilha()` - linha 2338
- `pecuaria_inventario_dados()` - linha 2465
- `pecuaria_projecao_demo_planilha()` - linha 2536

## Passos de Implementação

### Fase 1: Criar Arquivos e Mover Views
1. Criar `views_produtores.py` com imports necessários
2. Mover views de produtores
3. Atualizar `urls.py` para importar do novo arquivo
4. Testar funcionalidades
5. Repetir para propriedades e pecuária

### Fase 2: Usar Serviços
1. Refatorar views para usar `ProdutorService` e `PropriedadeService`
2. Remover lógica de negócio das views
3. Views ficam apenas com HTTP request/response

### Fase 3: Limpeza
1. Remover código duplicado
2. Remover imports não utilizados
3. Atualizar documentação

## Importante ⚠️
- Fazer mudanças incrementais
- Testar cada mudança antes de continuar
- Manter compatibilidade com código existente
- Não quebrar funcionalidades em produção

