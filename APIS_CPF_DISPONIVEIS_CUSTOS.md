# APIs de CPF Disponíveis no Brasil - Custos e Comparação

## ⚠️ Resumo Executivo

**Não existem APIs públicas gratuitas** para consulta completa de dados de CPF no Brasil. Todas as soluções disponíveis são pagas, devido a questões de privacidade e LGPD.

---

## 📊 Comparação de APIs Disponíveis

### 1. **Serpro (Governo Federal)** ⭐ Recomendado para Volume Alto

#### **Características:**
- ✅ **Fonte oficial**: Dados diretos da Receita Federal
- ✅ **Mais confiável**: Fonte governamental
- ✅ **Dados completos**: Nome, data de nascimento, situação cadastral, etc.
- ✅ **Inclui nome social** (versão atualizada)
- ⚠️ **Requisitos**: Certificado digital e-CNPJ obrigatório
- ⚠️ **Processo**: Contratação via Loja Serpro (pode ser burocrático)

#### **Tabela de Preços (2024):**

| Faixa | Consultas Mensais | Preço por Consulta (R$) |
|-------|-------------------|-------------------------|
| 1 | 0 a 999 | **R$ 0,6591** |
| 2 | 1.000 a 9.999 | **R$ 0,5649** |
| 3 | 10.000 a 49.999 | **R$ 0,3557** |
| 4 | 50.000 a 99.999 | **R$ 0,2616** |
| 5 | 100.000 a 249.999 | **R$ 0,1779** |
| 6 | 250.000 a 499.999 | **R$ 0,1569** |
| 7 | 500.000 a 999.999 | **R$ 0,1465** |
| 8 | 1.000.000 a 1.499.999 | **R$ 0,1360** |
| 9 | 1.500.000 a 2.999.999 | **R$ 0,1151** |
| 10 | 3.000.000 a 4.499.999 | **R$ 0,0732** |
| 11 | 4.500.000 a 9.999.999 | **R$ 0,0523** |
| 12 | 10.000.000 a 16.999.999 | **R$ 0,0314** |
| 13 | 17.000.000 a 19.999.999 | **R$ 0,025** |
| 14 | 20.000.000 a 24.999.999 | **R$ 0,023** |
| 15 | 25.000.000 a 29.999.999 | **R$ 0,020** |
| 16 | Acima de 30.000.000 | **R$ 0,017** |

#### **Exemplo de Custo:**
- **100 consultas/mês**: R$ 65,91
- **1.000 consultas/mês**: R$ 564,90
- **10.000 consultas/mês**: R$ 3.557,00

#### **Links:**
- **Loja Serpro**: https://loja.serpro.gov.br/en/consultacpf
- **Documentação**: https://www.gov.br/pt-br/servicos/obter-solucao-de-consulta-de-dados-de-cadastro-de-pessoa-fisica-cpf

---

### 2. **Brasil API Fácil** ⭐ Recomendado para Volume Baixo/Médio

#### **Características:**
- ✅ **Fácil integração**: API REST simples
- ✅ **Pay-per-use**: Paga apenas pelo que usar
- ✅ **Sem mensalidade**: Sem custos fixos
- ✅ **Crédito grátis**: R$ 1,00 para novos usuários
- ✅ **Reembolso automático**: Em caso de erro
- ⚠️ **Dados limitados**: Não retorna todos os dados completos

#### **Preços (2025):**

| Serviço | Preço por Consulta |
|---------|---------------------|
| **Validação de Maioridade** | **R$ 0,10** |
| **Consulta de Gênero** | **R$ 0,05** |
| **Consulta Completa CPF** | *Consultar site* |

#### **Exemplo de Custo:**
- **100 consultas/mês**: R$ 10,00 (maioridade) ou R$ 5,00 (gênero)
- **1.000 consultas/mês**: R$ 100,00 (maioridade) ou R$ 50,00 (gênero)

#### **Links:**
- **Site**: https://brasilapifacil.com.br/apis/cpf
- **Documentação**: https://brasilapifacil.com.br/docs/cpf

---

### 3. **SimpleData** ⭐ Recomendado para Múltiplas Consultas

#### **Características:**
- ✅ **API unificada**: CPF, CNPJ, CEP, Detran, ANVISA em uma única API
- ✅ **Pay-per-use**: Sem mensalidades fixas
- ✅ **Múltiplas fontes**: Integra várias bases de dados
- ⚠️ **Preços variáveis**: Dependem do tipo de consulta

#### **Preços:**
- **Modelo**: Pay-per-use (consultar site para valores atualizados)
- **Vantagem**: Pode ser mais barato se usar múltiplos serviços

#### **Links:**
- **Site**: https://simpledata.com.br/
- **Documentação**: Consultar site

---

### 4. **DataBrasil**

#### **Características:**
- ✅ **Planos mensais**: Com volume fixo de consultas
- ✅ **Múltiplos serviços**: CPF, CNPJ, CEP
- ⚠️ **Mensalidade fixa**: Mesmo sem usar todas as consultas

#### **Preços (Exemplo):**
- **Plano Básico**: R$ 99,00/mês para 1.000 consultas de CPF
- **Outros planos**: Consultar site

#### **Links:**
- **Site**: https://databrasil.net/

---

### 5. **API CPF/CNPJ (cpf.com.br)**

#### **Características:**
- ✅ **Consultas em tempo real**
- ✅ **Planos variados**: Conforme volume
- ⚠️ **Preços**: Consultar site

#### **Links:**
- **Site**: https://www.cpf.com.br/precos/

---

## 💰 Comparação de Custos (Exemplo: 1.000 consultas/mês)

| API | Custo Mensal (1.000 consultas) | Observações |
|-----|--------------------------------|-------------|
| **Serpro** | **R$ 564,90** | Mais caro, mas mais confiável |
| **Brasil API Fácil** | **R$ 100,00** (maioridade) | Mais barato, dados limitados |
| **DataBrasil** | **R$ 99,00** | Plano mensal fixo |
| **SimpleData** | *Consultar* | Varia conforme serviço |

---

## 🎯 Recomendações por Perfil

### **Volume Baixo (< 100 consultas/mês)**
- **Recomendação**: **Brasil API Fácil** ou **DataBrasil**
- **Motivo**: Custo mais baixo, fácil integração

### **Volume Médio (100 a 10.000 consultas/mês)**
- **Recomendação**: **Brasil API Fácil** ou **SimpleData**
- **Motivo**: Pay-per-use, sem mensalidade fixa

### **Volume Alto (> 10.000 consultas/mês)**
- **Recomendação**: **Serpro**
- **Motivo**: Melhor custo por consulta em volume alto, fonte oficial

### **Necessidade de Dados Oficiais**
- **Recomendação**: **Serpro**
- **Motivo**: Única fonte oficial (Receita Federal)

---

## 🔧 Como Integrar (Exemplo: Brasil API Fácil)

### 1. **Cadastro e Obtenção de Token**

1. Acesse: https://brasilapifacil.com.br/
2. Crie uma conta
3. Obtenha seu token de API
4. Receba R$ 1,00 de crédito grátis para testar

### 2. **Adicionar Configuração no Django**

```python
# settings.py
BRASIL_API_FACIL_TOKEN = os.getenv('BRASIL_API_FACIL_TOKEN', '')
```

### 3. **Atualizar Serviço de Consulta**

```python
# gestao_rural/services/consulta_cpf_cnpj.py

def consultar_cpf_com_api_paga(self, cpf: str) -> Optional[Dict]:
    """
    Consulta CPF usando Brasil API Fácil
    """
    from django.conf import settings
    
    token = settings.BRASIL_API_FACIL_TOKEN
    if not token:
        return None  # API não configurada
    
    cpf_limpo = self.limpar_cpf_cnpj(cpf)
    
    try:
        # Exemplo: Validação de maioridade
        url = "https://brasilapifacil.com.br/api/cpf/maioridade"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {'cpf': cpf_limpo}
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            return {
                'cpf_valido': True,
                'maior_idade': dados.get('maior_idade', False),
                # Adicionar outros campos conforme API disponibilizar
            }
    except Exception as e:
        logger.error(f"Erro ao consultar CPF via Brasil API Fácil: {e}")
    
    return None
```

### 4. **Atualizar View**

```python
# gestao_rural/views.py

@login_required
def consultar_cpf_cnpj_api(request):
    from django.conf import settings
    from .services.consulta_cpf_cnpj import ConsultaCPFCNPJ
    
    cpf_cnpj = request.GET.get('cpf_cnpj', '').strip()
    
    service = ConsultaCPFCNPJ()
    
    # Verificar se é CPF e se API paga está configurada
    valido, tipo = service.validar_cpf_cnpj(cpf_cnpj)
    
    if tipo == 'CPF' and settings.BRASIL_API_FACIL_TOKEN:
        # Tentar API paga primeiro
        dados = service.consultar_cpf_com_api_paga(cpf_cnpj)
        if dados:
            return JsonResponse({
                'success': True,
                'dados': dados,
                'fonte': 'brasil_api_facil'
            })
    
    # Fallback para consulta normal
    dados = consultar_dados_cpf_cnpj(cpf_cnpj)
    # ... resto do código
```

---

## 📝 Considerações Importantes

### **1. LGPD e Privacidade**
- ✅ Todas as APIs respeitam LGPD
- ✅ Dados são consultados apenas quando necessário
- ✅ Não armazenar dados de CPF sem consentimento

### **2. Custos Ocultos**
- ⚠️ Verificar se há taxas de setup
- ⚠️ Verificar limites de rate (consultas por minuto)
- ⚠️ Verificar se há custos de suporte

### **3. Confiabilidade**
- ✅ Serpro: Mais confiável (fonte oficial)
- ⚠️ APIs privadas: Verificar SLA e disponibilidade

### **4. Testes**
- ✅ Sempre testar com créditos grátis antes de contratar
- ✅ Validar se os dados retornados atendem suas necessidades

---

## 🚀 Próximos Passos

1. **Avaliar volume de consultas** necessário por mês
2. **Comparar custos** conforme tabela acima
3. **Testar APIs** com créditos grátis
4. **Escolher fornecedor** que melhor atende suas necessidades
5. **Implementar integração** seguindo exemplos acima

---

## 📚 Links Úteis

- **Serpro**: https://loja.serpro.gov.br/en/consultacpf
- **Brasil API Fácil**: https://brasilapifacil.com.br/apis/cpf
- **SimpleData**: https://simpledata.com.br/
- **DataBrasil**: https://databrasil.net/
- **API CPF/CNPJ**: https://www.cpf.com.br/precos/

---

**Última atualização:** 2025-01-XX  
**Fonte:** Pesquisa web e sites oficiais das APIs  
**Nota:** Preços podem variar - sempre consultar sites oficiais para valores atualizados

