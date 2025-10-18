# Sistema de Gestão Rural - Projeções para Análise Bancária

Sistema completo para gestão de propriedades rurais com projeções de rebanho e produção agrícola, desenvolvido para análise de capacidade de pagamento bancária.

## 🚀 Funcionalidades

### Módulo de Gestão
- **Cadastro de Produtores Rurais**: Gestão completa de produtores
- **Gestão de Propriedades**: Cadastro de propriedades com tipos de operação
- **Sistema de Usuários**: Autenticação e controle de acesso

### Módulo Pecuária (Rebanho)
- **Inventário Inicial**: Cadastro do rebanho por categoria
- **Parâmetros de Projeção**: Configuração de taxas de natalidade, mortalidade e vendas
- **Projeção Inteligente**: Simulação com promoção automática de categorias
- **Categorias Automáticas**: Sistema completo de categorias para gado de corte

### Módulo Agricultura
- **Ciclos de Produção**: Gestão de safras e culturas
- **Projeção de Receitas**: Cálculo automático de receitas e custos
- **Análise de Lucratividade**: Comparação entre receitas e custos

### Relatórios Bancários
- **Relatório Final**: Consolidação de todas as projeções
- **Análise de Capacidade de Pagamento**: Dados para análise bancária
- **Exportação**: Geração de relatórios em PDF

## 🏗️ Arquitetura do Sistema

### Modelos Principais
- `ProdutorRural`: Cadastro de produtores
- `Propriedade`: Propriedades rurais
- `CategoriaAnimal`: Categorias do rebanho
- `InventarioRebanho`: Inventário inicial
- `ParametrosProjecaoRebanho`: Parâmetros para simulação
- `MovimentacaoProjetada`: Movimentações da projeção
- `RegraPromocaoCategoria`: Regras de promoção de categoria
- `CicloProducaoAgricola`: Ciclos agrícolas

### Lógica de Projeção Pecuária

O sistema implementa uma simulação completa do ciclo de vida do rebanho:

1. **Nascimentos**: Calculados baseados em fêmeas reprodutivas
2. **Mortalidade**: Aplicada por categoria (bezerros vs adultos)
3. **Vendas**: Percentuais configuráveis por tipo de animal
4. **Promoção de Categoria**: Envelhecimento automático dos animais

#### Fluxo de Promoção (A Virada de Ano)
```
Bezerras (0-12m) → Novilhas (12-24m) → Primíparas (24-36m) → Multíparas (>36m)
Bezerros (0-12m) → Garrotes (12-24m) → Bois Magros (24-36m)
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Django 4.2+

### Instalação Rápida

1. **Clone o repositório**
```bash
git clone <repository-url>
cd sistema_rural
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o sistema**
```bash
python setup_sistema.py
```

4. **Execute o servidor**
```bash
python manage.py runserver
```

### Acesso ao Sistema
- **Sistema**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Usuário**: admin | **Senha**: admin123

## 📋 Como Usar

### 1. Cadastro Inicial
1. Acesse o sistema e faça login
2. Cadastre um novo produtor rural
3. Adicione propriedades ao produtor
4. Configure o tipo de operação (Pecuária/Agricultura/Mista)

### 2. Módulo Pecuária
1. **Inventário Inicial**: Cadastre a quantidade de animais por categoria
2. **Parâmetros**: Configure as taxas de natalidade, mortalidade e vendas
3. **Projeção**: Gere a simulação para os próximos anos
4. **Análise**: Visualize a evolução do rebanho

### 3. Módulo Agricultura
1. **Ciclos de Produção**: Cadastre as safras planejadas
2. **Custos e Receitas**: Configure preços e produtividades
3. **Projeção**: Visualize a evolução da produção

### 4. Relatório Final
1. Acesse o relatório final da propriedade
2. Visualize todas as projeções consolidadas
3. Gere o relatório para análise bancária

## 🎯 Categorias de Animais (Gado de Corte)

### Fêmeas
- **Bezerras (0-12m)**: Fêmeas jovens
- **Novilhas (12-24m)**: Prontas para primeiro entoure
- **Primíparas (24-36m)**: Vacas de primeira cria
- **Multíparas (>36m)**: Vacas experientes
- **Vacas de Descarte**: Selecionadas para descarte

### Machos
- **Bezerros (0-12m)**: Machos jovens
- **Garrotes (12-24m)**: Machos em crescimento
- **Bois Magros (24-36m)**: Prontos para venda
- **Touros**: Reprodutores

## 🔧 Configuração Avançada

### Personalizar Categorias
```python
# Acesse o admin Django
# Vá em Gestão Rural > Categorias de Animais
# Adicione ou modifique categorias conforme necessário
```

### Configurar Regras de Promoção
```python
# Acesse o admin Django
# Vá em Gestão Rural > Regras de Promoção de Categoria
# Configure as regras de envelhecimento dos animais
```

### Parâmetros de Projeção
- **Natalidade**: Taxa anual de nascimentos
- **Mortalidade**: Taxas diferenciadas por idade
- **Vendas**: Percentuais de venda por categoria
- **Periodicidade**: Frequência de cálculo (Mensal/Trimestral/Semestral/Anual)

## 📊 Exemplo de Uso

### Cenário: Fazenda de Gado de Corte
1. **Inventário Inicial**: 100 vacas, 50 novilhas, 30 bezerros
2. **Parâmetros**: 85% natalidade, 5% mortalidade bezerros, 2% mortalidade adultos
3. **Projeção 5 anos**: Sistema calcula crescimento do rebanho
4. **Resultado**: Relatório com evolução do rebanho e capacidade de pagamento

### Benefícios para Análise Bancária
- **Projeção Realista**: Baseada no ciclo de vida real dos animais
- **Crescimento Exponencial**: Mostra o potencial de crescimento do rebanho
- **Capacidade de Pagamento**: Dados concretos para análise de crédito
- **Relatórios Profissionais**: Documentos prontos para análise bancária

## 🚀 Tecnologias Utilizadas

- **Backend**: Django 4.2
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Banco de Dados**: SQLite (desenvolvimento)
- **Gráficos**: Chart.js
- **Relatórios**: ReportLab (PDF)

## 📈 Próximas Funcionalidades

- [ ] Dashboard com gráficos interativos
- [ ] Exportação de relatórios em PDF
- [ ] Integração com APIs de preços
- [ ] Sistema de alertas e notificações
- [ ] Módulo de gestão financeira
- [ ] Relatórios comparativos entre propriedades

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para dúvidas ou suporte, entre em contato através dos issues do GitHub.

---

**Sistema de Gestão Rural** - Desenvolvido para análise de capacidade de pagamento bancária

