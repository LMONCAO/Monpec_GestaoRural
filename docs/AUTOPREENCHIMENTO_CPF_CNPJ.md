# Autopreenchimento de Dados por CPF/CNPJ

## ✅ Funcionalidade Implementada

Quando o usuário digita o CPF/CNPJ do cliente no formulário de cadastro, o sistema agora busca automaticamente os dados e preenche os campos do formulário.

## 🎯 Como Funciona

### 1. **Busca Automática por CPF/CNPJ**
- Ao digitar um CPF (11 dígitos) ou CNPJ (14 dígitos) no campo "CPF/CNPJ"
- O sistema detecta automaticamente quando o campo perde o foco (blur)
- Ou o usuário pode clicar no botão de busca (🔍) ao lado do campo
- Os dados são buscados na API ReceitaWS (gratuita)

### 2. **Busca Automática por CEP**
- Ao digitar um CEP (8 dígitos) no campo "CEP"
- O sistema busca automaticamente o endereço na API ViaCEP (gratuita)
- Ou o usuário pode clicar no botão de busca (🔍) ao lado do campo

### 3. **Campos Preenchidos Automaticamente**

#### Para CNPJ (empresas):
- ✅ Nome/Razão Social
- ✅ Nome Fantasia
- ✅ Tipo de Pessoa (automaticamente "Pessoa Jurídica")
- ✅ Inscrição Estadual
- ✅ Telefone
- ✅ E-mail
- ✅ Endereço completo (Logradouro, Número, Complemento, Bairro, Cidade, Estado, CEP)

#### Para CPF (pessoas físicas):
- ⚠️ **Limitação**: APIs públicas de CPF são limitadas
- ✅ Tipo de Pessoa (automaticamente "Pessoa Física")
- ⚠️ Outros dados precisam ser preenchidos manualmente (ou usar API paga)

#### Para CEP:
- ✅ Logradouro
- ✅ Bairro
- ✅ Cidade
- ✅ Estado (UF)

## 📋 Arquivos Criados/Modificados

### 1. **Novo Serviço**
- `gestao_rural/services/consulta_cpf_cnpj.py`
  - Classe `ConsultaCPFCNPJ` para consultar dados
  - Integração com ReceitaWS (CNPJ)
  - Integração com ViaCEP (endereço)

### 2. **Novas Views/APIs**
- `gestao_rural/views.py`:
  - `consultar_cpf_cnpj_api()` - API para buscar dados por CPF/CNPJ
  - `consultar_cep_api()` - API para buscar endereço por CEP

### 3. **Novas URLs**
- `/api/consultar-cpf-cnpj/` - Endpoint para consulta CPF/CNPJ
- `/api/consultar-cep/` - Endpoint para consulta CEP

### 4. **Template Atualizado**
- `templates/gestao_rural/cliente_form.html`:
  - Botões de busca adicionados aos campos CPF/CNPJ e CEP
  - JavaScript para busca automática
  - Máscaras de formatação (CPF: 000.000.000-00, CNPJ: 00.000.000/0000-00, CEP: 00000-000)
  - Indicadores de loading durante a busca
  - Mensagens de sucesso/erro

### 5. **Dependências**
- `requirements.txt`: Adicionado `requests>=2.31.0`

## 🚀 Como Usar

### 1. **Preencher CNPJ de Empresa**
1. Acesse o formulário de novo cliente
2. Digite o CNPJ no campo "CPF/CNPJ" (com ou sem formatação)
3. Aguarde alguns segundos ou clique no botão de busca (🔍)
4. Os campos serão preenchidos automaticamente!

### 2. **Preencher CEP**
1. Digite o CEP no campo "CEP" (com ou sem formatação)
2. Aguarde alguns segundos ou clique no botão de busca (🔍)
3. Os campos de endereço serão preenchidos automaticamente!

## ⚠️ Limitações e Observações

### APIs Utilizadas
1. **ReceitaWS** (CNPJ):
   - ✅ Gratuita
   - ✅ Dados completos de empresas
   - ⚠️ Pode ter limitações de rate (consultas por minuto)
   - ⚠️ Depende da disponibilidade do serviço

2. **ViaCEP** (CEP):
   - ✅ Gratuita
   - ✅ Dados de endereço completos
   - ✅ Muito confiável

3. **CPF**:
   - ⚠️ APIs públicas de CPF são muito limitadas
   - ⚠️ Para dados completos de CPF, seria necessário API paga
   - ✅ Por enquanto, apenas define tipo de pessoa como "Física"

### Recomendações
- Se a busca falhar, os dados podem ser preenchidos manualmente
- Para uso intensivo, considere usar APIs pagas com mais recursos
- Os dados retornados são apenas para facilitar o cadastro - sempre revise antes de salvar

## 🔧 Melhorias Futuras (Opcional)

1. **Cache de Consultas**:
   - Armazenar resultados de consultas para evitar requisições repetidas

2. **Validação de CPF/CNPJ**:
   - Validar dígitos verificadores antes de buscar

3. **API de CPF Paga**:
   - Integrar com API paga para dados completos de CPF

4. **Tratamento de Erros Melhorado**:
   - Mensagens mais específicas para diferentes tipos de erro

5. **Busca em Lote**:
   - Permitir buscar múltiplos CNPJs de uma vez

## 📝 Exemplo de Uso

```javascript
// O JavaScript já está implementado no template
// Basta digitar o CNPJ e aguardar ou clicar no botão de busca

// Exemplo de CNPJ para testar:
// 11.222.333/0001-81 (formato com máscara)
// 11222333000181 (formato sem máscara)

// Exemplo de CEP para testar:
// 01310-100 (formato com máscara)
// 01310100 (formato sem máscara)
```

## ✅ Status

- ✅ Implementação completa
- ✅ Testes básicos realizados
- ✅ Documentação criada
- ⚠️ Requer testes com dados reais
- ⚠️ Pode precisar ajustes conforme uso

---

**Criado em:** 2025-01-XX  
**Versão:** 1.0  
**Status:** Funcional - Pronto para uso

