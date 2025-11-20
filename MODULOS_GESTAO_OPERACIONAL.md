# 🏭 Módulos de Gestão Operacional - Sistema Completo

## 📋 **MÓDULOS A IMPLEMENTAR**

### **1. CONTROLE DE ABASTECIMENTO** ⚠️
- Controle de combustível
- Abastecimento de veículos e máquinas
- Histórico de consumo
- Análise de custos

### **2. MANUTENÇÃO DE FROTA** ⚠️
- Gestão de veículos e máquinas
- Controle de manutenções
- Histórico de serviços
- Alertas de manutenção

### **3. FÁBRICA DE RAÇÃO** ⚠️
- Formulação de rações
- Controle de produção
- Gestão de estoque de ingredientes
- Cálculo de custos

### **4. CONTROLE DE EMPREITEIROS** ⚠️
- Cadastro de empreiteiros
- Contratos de serviços
- Controle de pagamentos
- Avaliação de serviços

### **5. GESTÃO DE FUNCIONÁRIOS** ⚠️
- Cadastro de funcionários
- Contratação e demissão
- Controle de ponto
- Folha de pagamento

---

## 🗄️ **MODELOS DE DADOS**

### **1. CONTROLE DE ABASTECIMENTO**

```python
class TipoCombustivel(models.Model):
    """Tipos de combustível"""
    nome = CharField()  # Diesel, Gasolina, Etanol, etc.
    unidade_medida = CharField()  # Litros
    preco_medio = DecimalField()

class VeiculoMaquina(models.Model):
    """Veículos e máquinas da propriedade"""
    propriedade = ForeignKey(Propriedade)
    tipo = CharField()  # Veículo, Máquina Agrícola, Implemento
    marca = CharField()
    modelo = CharField()
    placa = CharField(null=True)
    ano = IntegerField()
    capacidade_tanque = DecimalField()  # Litros
    consumo_medio = DecimalField()  # km/L ou horas/L
    ativo = BooleanField()

class Abastecimento(models.Model):
    """Registro de abastecimentos"""
    propriedade = ForeignKey(Propriedade)
    veiculo_maquina = ForeignKey(VeiculoMaquina)
    tipo_combustivel = ForeignKey(TipoCombustivel)
    data_abastecimento = DateField()
    quantidade_litros = DecimalField()
    valor_unitario = DecimalField()
    valor_total = DecimalField()
    quilometragem_horas = DecimalField()  # km ou horas
    fornecedor = CharField()
    nota_fiscal = CharField(null=True)
    observacoes = TextField()
```

### **2. MANUTENÇÃO DE FROTA**

```python
class TipoManutencao(models.Model):
    """Tipos de manutenção"""
    nome = CharField()  # Preventiva, Corretiva, Revisão
    descricao = TextField()

class Manutencao(models.Model):
    """Controle de manutenções"""
    propriedade = ForeignKey(Propriedade)
    veiculo_maquina = ForeignKey(VeiculoMaquina)
    tipo_manutencao = ForeignKey(TipoManutencao)
    data_agendamento = DateField()
    data_realizacao = DateField(null=True)
    quilometragem_horas = DecimalField()
    descricao_servico = TextField()
    valor_servico = DecimalField()
    fornecedor_servico = CharField()
    status = CharField()  # Agendada, Em Andamento, Concluída
    observacoes = TextField()

class ItemManutencao(models.Model):
    """Itens utilizados na manutenção"""
    manutencao = ForeignKey(Manutencao)
    peca_servico = CharField()
    quantidade = DecimalField()
    valor_unitario = DecimalField()
    valor_total = DecimalField()
```

### **3. FÁBRICA DE RAÇÃO**

```python
class IngredienteRacao(models.Model):
    """Ingredientes para produção de ração"""
    nome = CharField()  # Milho, Soja, Farelo, etc.
    tipo = CharField()  # Energético, Proteico, Mineral
    unidade_medida = CharField()  # kg
    preco_medio = DecimalField()

class FormulaRacao(models.Model):
    """Fórmulas de ração"""
    propriedade = ForeignKey(Propriedade)
    nome = CharField()  # Ração Engorda, Ração Recria, etc.
    categoria_animal = ForeignKey(CategoriaAnimal)
    ingredientes = JSONField()  # {ingrediente_id: quantidade_kg}
    proteina_bruta = DecimalField()  # %
    energia_metabolizavel = DecimalField()  # Mcal/kg
    custo_por_kg = DecimalField()
    ativo = BooleanField()

class ProducaoRacao(models.Model):
    """Produção de ração"""
    propriedade = ForeignKey(Propriedade)
    formula = ForeignKey(FormulaRacao)
    data_producao = DateField()
    quantidade_produzida = DecimalField()  # kg
    custo_total = DecimalField()
    custo_por_kg = DecimalField()
    lote = CharField()
    data_validade = DateField()
    observacoes = TextField()

class ItemProducaoRacao(models.Model):
    """Ingredientes utilizados na produção"""
    producao = ForeignKey(ProducaoRacao)
    ingrediente = ForeignKey(IngredienteRacao)
    quantidade_usada = DecimalField()  # kg
    valor_unitario = DecimalField()
    valor_total = DecimalField()
```

### **4. CONTROLE DE EMPREITEIROS**

```python
class Empreiteiro(models.Model):
    """Cadastro de empreiteiros"""
    nome = CharField()
    cpf_cnpj = CharField(unique=True)
    telefone = CharField()
    email = EmailField()
    endereco = TextField()
    tipo_servico = CharField()  # Plantio, Colheita, Construção, etc.
    ativo = BooleanField()

class ContratoEmpreiteiro(models.Model):
    """Contratos com empreiteiros"""
    propriedade = ForeignKey(Propriedade)
    empreiteiro = ForeignKey(Empreiteiro)
    tipo_servico = CharField()
    descricao = TextField()
    data_inicio = DateField()
    data_fim = DateField()
    valor_total = DecimalField()
    forma_pagamento = CharField()
    status = CharField()  # Ativo, Concluído, Cancelado
    observacoes = TextField()

class PagamentoEmpreiteiro(models.Model):
    """Pagamentos a empreiteiros"""
    contrato = ForeignKey(ContratoEmpreiteiro)
    data_pagamento = DateField()
    valor = DecimalField()
    forma_pagamento = CharField()
    observacoes = TextField()
```

### **5. GESTÃO DE FUNCIONÁRIOS**

```python
class Cargo(models.Model):
    """Cargos dos funcionários"""
    nome = CharField()  # Gerente, Veterinário, Operador, etc.
    descricao = TextField()
    salario_base = DecimalField()

class Funcionario(models.Model):
    """Cadastro de funcionários"""
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('AFASTADO', 'Afastado'),
        ('DEMITIDO', 'Demitido'),
    ]
    
    propriedade = ForeignKey(Propriedade)
    nome = CharField()
    cpf = CharField(unique=True)
    rg = CharField()
    data_nascimento = DateField()
    telefone = CharField()
    email = EmailField()
    endereco = TextField()
    cargo = ForeignKey(Cargo)
    data_admissao = DateField()
    data_demissao = DateField(null=True)
    salario = DecimalField()
    status = CharField(choices=STATUS_CHOICES, default='ATIVO')
    observacoes = TextField()

class Contratacao(models.Model):
    """Registro de contratações"""
    funcionario = ForeignKey(Funcionario)
    propriedade = ForeignKey(Propriedade)
    cargo = ForeignKey(Cargo)
    data_admissao = DateField()
    salario_inicial = DecimalField()
    tipo_contrato = CharField()  # CLT, Temporário, PJ
    observacoes = TextField()

class Demissao(models.Model):
    """Registro de demissões"""
    funcionario = ForeignKey(Funcionario)
    data_demissao = DateField()
    motivo = TextField()
    tipo_demissao = CharField()  # Sem justa causa, Justa causa, Pedido
    valor_rescisao = DecimalField()
    observacoes = TextField()

class PontoFuncionario(models.Model):
    """Controle de ponto"""
    funcionario = ForeignKey(Funcionario)
    data = DateField()
    entrada = TimeField()
    saida = TimeField(null=True)
    horas_trabalhadas = DecimalField(null=True)
    tipo = CharField()  # Normal, Extra, Folga
    observacoes = TextField()
```

---

## 📊 **FUNCIONALIDADES POR MÓDULO**

### **1. CONTROLE DE ABASTECIMENTO**

#### **Funcionalidades:**
- Registro de abastecimentos
- Histórico de consumo
- Análise de custos por veículo
- Alertas de consumo alto
- Relatórios de abastecimento

#### **Relatórios:**
- Consumo mensal por veículo
- Custo de combustível
- Análise de eficiência
- Comparativo entre veículos

---

### **2. MANUTENÇÃO DE FROTA**

#### **Funcionalidades:**
- Cadastro de veículos e máquinas
- Agendamento de manutenções
- Controle de manutenções preventivas
- Histórico de serviços
- Alertas de manutenção

#### **Relatórios:**
- Histórico de manutenções
- Custos de manutenção
- Tempo de parada
- Análise de disponibilidade

---

### **3. FÁBRICA DE RAÇÃO**

#### **Funcionalidades:**
- Formulação de rações
- Controle de ingredientes
- Produção de ração
- Cálculo de custos
- Controle de lotes

#### **Relatórios:**
- Produção mensal
- Custos de produção
- Análise de fórmulas
- Comparativo de custos

---

### **4. CONTROLE DE EMPREITEIROS**

#### **Funcionalidades:**
- Cadastro de empreiteiros
- Contratos de serviços
- Controle de pagamentos
- Avaliação de serviços
- Histórico de contratos

#### **Relatórios:**
- Gastos com empreiteiros
- Histórico de contratos
- Análise de fornecedores
- Contratos ativos

---

### **5. GESTÃO DE FUNCIONÁRIOS**

#### **Funcionalidades:**
- Cadastro de funcionários
- Contratação
- Demissão
- Controle de ponto
- Folha de pagamento
- Avaliação de desempenho

#### **Relatórios:**
- Folha de pagamento
- Histórico de funcionários
- Análise de custos de pessoal
- Rotatividade

---

## 🎯 **INTEGRAÇÃO COM SISTEMA ATUAL**

### **Vantagens:**
- ✅ Integração com módulo de custos
- ✅ Integração com fluxo de caixa
- ✅ Integração financeira
- ✅ Multi-propriedade

### **Benefícios:**
- Controle completo operacional
- Análise de custos detalhada
- Planejamento financeiro
- Relatórios consolidados

---

## 📝 **PRÓXIMOS PASSOS**

1. Criar modelos de dados
2. Criar views e templates
3. Integrar com módulos existentes
4. Criar relatórios
5. Testar funcionalidades


