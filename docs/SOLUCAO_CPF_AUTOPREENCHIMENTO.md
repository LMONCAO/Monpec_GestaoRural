# Solução para Autopreenchimento de CPF

## ⚠️ Situação Atual

**Problema:** O sistema não consegue buscar dados completos de CPF automaticamente porque:

1. **Não existem APIs públicas gratuitas** para consulta de dados de CPF no Brasil
2. **Questões de privacidade e LGPD** impedem o acesso público a dados de pessoas físicas
3. **APIs governamentais** (como Serpro) requerem certificado digital e-CNPJ e são pagas

## ✅ O que foi implementado

### 1. **Validação de CPF/CNPJ**
- ✅ Validação de dígitos verificadores
- ✅ Verificação se CPF/CNPJ é válido antes de buscar
- ✅ Mensagens de erro claras para CPF/CNPJ inválidos

### 2. **Mensagens Melhoradas**
- ✅ Mensagem informativa para CPF válido (explicando limitação)
- ✅ Mensagem de erro para CPF inválido
- ✅ Mensagem de sucesso apenas quando dados são realmente preenchidos

### 3. **Funcionalidade para CNPJ**
- ✅ Busca completa de dados de empresas via ReceitaWS
- ✅ Preenchimento automático de todos os campos

## 🔧 Soluções Possíveis para CPF

### Opção 1: Integração com API Paga (Recomendada para Produção)

#### **Serpro (Governo)**
- **URL**: https://www.gov.br/pt-br/servicos/obter-solucao-de-consulta-de-dados-de-cadastro-de-pessoa-fisica-cpf
- **Requisitos**: Certificado digital e-CNPJ
- **Custo**: Variável conforme volume
- **Vantagens**: Oficial, confiável
- **Desvantagens**: Requer certificado digital, processo burocrático

#### **Brasil API Fácil**
- **URL**: https://brasilapifacil.com.br/docs/cpf
- **Custo**: A partir de R$ 0,02 por consulta
- **Vantagens**: Fácil integração, pay-per-use
- **Desvantagens**: Custo por consulta

#### **SimpleData**
- **URL**: https://simpledata.com.br/
- **Custo**: Pay-per-use
- **Vantagens**: Integra múltiplas consultas (Receita Federal, Detran, ANVISA)
- **Desvantagens**: Custo por consulta

### Opção 2: Manter Preenchimento Manual (Atual)

**Vantagens:**
- ✅ Sem custos
- ✅ Sem dependência de APIs externas
- ✅ Conformidade com LGPD (dados não saem do sistema)

**Desvantagens:**
- ❌ Usuário precisa preencher manualmente
- ❌ Mais tempo para cadastrar clientes

### Opção 3: Cache Local (Híbrida)

Armazenar dados de CPFs já cadastrados no sistema para reutilização:

```python
# Exemplo de implementação
def buscar_cpf_cache(cpf):
    # Buscar no banco de dados se já foi cadastrado antes
    cliente_existente = Cliente.objects.filter(cpf_cnpj=cpf).first()
    if cliente_existente:
        return {
            'nome': cliente_existente.nome,
            'email': cliente_existente.email,
            # ... outros campos
        }
    return None
```

**Vantagens:**
- ✅ Reutiliza dados já cadastrados
- ✅ Sem custos adicionais
- ✅ Melhora experiência do usuário

**Desvantagens:**
- ❌ Só funciona para CPFs já cadastrados
- ❌ Não busca dados novos

## 📋 Como Implementar API Paga (Exemplo com Brasil API Fácil)

### 1. Adicionar Configuração

```python
# settings.py
BRASIL_API_FACIL_TOKEN = os.getenv('BRASIL_API_FACIL_TOKEN', '')
```

### 2. Atualizar Serviço

```python
# gestao_rural/services/consulta_cpf_cnpj.py

def consultar_cpf_com_api_paga(self, cpf: str) -> Optional[Dict]:
    """
    Consulta CPF usando API paga (Brasil API Fácil)
    """
    from django.conf import settings
    
    token = settings.BRASIL_API_FACIL_TOKEN
    if not token:
        return None  # API não configurada
    
    try:
        url = "https://brasilapifacil.com.br/api/cpf"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {'cpf': cpf}
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            return {
                'nome': dados.get('nome', ''),
                'data_nascimento': dados.get('data_nascimento', ''),
                'situacao_cadastral': dados.get('situacao', ''),
                # ... outros campos
            }
    except Exception as e:
        logger.error(f"Erro ao consultar CPF via API paga: {e}")
    
    return None
```

### 3. Atualizar View

```python
# Verificar se API paga está configurada
if settings.BRASIL_API_FACIL_TOKEN:
    dados = service.consultar_cpf_com_api_paga(cpf)
    if dados:
        return JsonResponse({'success': True, 'dados': dados})
```

## 💡 Recomendação

### Para Uso Imediato:
- ✅ **Manter preenchimento manual** (situação atual)
- ✅ **Melhorar validação** (já implementado)
- ✅ **Adicionar cache local** (reutilizar dados já cadastrados)

### Para Produção/Volume Alto:
- 💰 **Integrar API paga** (Brasil API Fácil ou similar)
- 📊 **Analisar custo-benefício** (quantos CPFs serão consultados por mês)
- 🔒 **Garantir segurança** (tokens, rate limiting)

## 📝 Status Atual

- ✅ Validação de CPF/CNPJ implementada
- ✅ Mensagens claras para o usuário
- ✅ Busca completa para CNPJ funcionando
- ⚠️ CPF requer preenchimento manual (limitação das APIs públicas)
- 💡 Pronto para integrar API paga quando necessário

---

**Última atualização:** 2025-01-XX  
**Versão:** 1.1  
**Status:** Funcional - Pronto para uso, com opção de melhorias futuras

