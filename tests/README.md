# 🧪 Testes Automatizados - Monpec Gestão Rural

## Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py              # Configuração e fixtures
├── test_services.py         # Testes básicos de serviços
├── test_services_completo.py # Testes completos de serviços
├── test_views_produtores.py  # Testes de views de produtores
├── test_views_propriedades.py # Testes de views de propriedades
├── test_views_pecuaria.py    # Testes de views de pecuária
├── test_autenticacao.py      # Testes de autenticação/autorização
├── test_integracao.py        # Testes de integração (fluxos completos)
└── README.md                 # Este arquivo
```

## Como Executar

### Executar todos os testes
```bash
pytest
```

### Executar testes específicos
```bash
# Apenas testes de serviços
pytest tests/test_services.py

# Apenas testes de views
pytest tests/test_views_produtores.py

# Apenas testes de integração
pytest tests/test_integracao.py -m integration
```

### Executar com cobertura
```bash
pytest --cov=gestao_rural --cov-report=html
```

### Executar testes em paralelo (mais rápido)
```bash
pytest -n auto
```

## Fixtures Disponíveis

### Fixtures de Usuários
- `user`: Usuário comum de teste
- `admin_user`: Usuário administrador
- `client_logged_in`: Cliente Django autenticado

### Fixtures de Dados
- `produtor`: Produtor rural de teste
- `propriedade`: Propriedade rural de teste

## Cobertura de Testes

### Funcionalidades Testadas

#### ✅ Serviços
- ProdutorService (obter, permissões, criação)
- PropriedadeService (obter, permissões, criação)
- DashboardService (dados do dashboard)

#### ✅ Views
- CRUD de Produtores (criar, editar, excluir, listar)
- CRUD de Propriedades (criar, editar, excluir, listar)
- Views de Pecuária (dashboard, inventário, parâmetros)

#### ✅ Autenticação e Autorização
- Login/Logout
- Permissões de acesso
- Isolamento de dados por usuário

#### ✅ Integração
- Fluxos completos (criar produtor → propriedade)
- Fluxos de pecuária (parâmetros → inventário)
- Fluxos de edição

## Adicionar Novos Testes

### Exemplo: Teste de View
```python
@pytest.mark.django_db
def test_minha_view(client_logged_in):
    response = client_logged_in.get(reverse('minha_view'))
    assert response.status_code == 200
```

### Exemplo: Teste de Serviço
```python
@pytest.mark.django_db
def test_meu_servico(user):
    resultado = MeuService.fazer_algo(user)
    assert resultado is not None
```

## Boas Práticas

1. **Usar fixtures**: Reutilizar fixtures ao invés de criar dados em cada teste
2. **Isolamento**: Cada teste deve ser independente
3. **Nomes descritivos**: Nomes de testes devem descrever o que testam
4. **Arrange-Act-Assert**: Estruturar testes em 3 partes claras
5. **Marcadores**: Usar marcadores para categorizar testes

## Próximos Passos

- [ ] Adicionar testes para views financeiras
- [ ] Adicionar testes para views de compras
- [ ] Adicionar testes para views de vendas
- [ ] Adicionar testes de performance
- [ ] Aumentar cobertura para 80%+


