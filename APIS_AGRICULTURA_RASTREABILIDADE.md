# 🌾 APIs Disponíveis - MAPA, CNA e Embrapa

## 📋 **APIS DISPONÍVEIS PARA INTEGRAÇÃO**

### 🏛️ **1. MINISTÉRIO DA AGRICULTURA E PECUÁRIA (MAPA)**

#### **a) API Agrofit**
- **Descrição**: Dados sobre produtos fitossanitários registrados
- **Fonte**: [agroapi.cnptia.embrapa.br](https://www.agroapi.cnptia.embrapa.br/)
- **Dados disponíveis**:
  - Produtos fitossanitários
  - Pragas e culturas
  - Ingredientes ativos
  - Marcas comerciais
  - Titulares de registro
- **Uso no sistema**: Consulta de produtos permitidos para uso na propriedade

#### **b) API InfoDAP**
- **Descrição**: Informações da Declaração de Aptidão ao Pronaf (DAP)
- **Fonte**: [gov.br/conecta/catalogo/apis/infodap](https://www.gov.br/conecta/catalogo/apis/infodap)
- **Dados disponíveis**:
  - Identificação de unidades familiares de produção
  - Qualificação da propriedade
  - Aptidão ao Pronaf
- **Uso no sistema**: Validação de propriedades familiares e acesso a linhas de crédito

#### **c) SISBOV (Sistema Brasileiro de Rastreabilidade)**
- **Descrição**: Sistema oficial do MAPA para rastreabilidade de bovinos e bubalinos
- **Fonte**: [sisbov.agricultura.gov.br](https://sisbov.agricultura.gov.br/)
- **Status**: Sistema web, não possui API pública documentada
- **Observação**: Pode ser necessário solicitar acesso especial via SDA (Secretaria de Defesa Agropecuária)

#### **d) API SDA (Secretaria de Defesa Agropecuária)**
- **Descrição**: API para laboratórios integrar LIMS com serviços do MAPA
- **Fonte**: [gov.br/agricultura/.../solicitacao-de-acesso-a-api-externa](https://www.gov.br/agricultura/pt-br/assuntos/defesa-agropecuaria/plataforma-sda/mapa-labs/solicitacao-de-acesso-a-api-externa)
- **Acesso**: Requer solicitação formal e credenciais
- **Uso no sistema**: Integração com dados sanitários oficiais

---

### 🌱 **2. EMBRAPA (AgroAPI)**

#### **a) API BovTrace**
- **Descrição**: API para inserção padronizada de dados de rastreabilidade animal
- **Fonte**: [AgroAPI - Embrapa](https://www.agroapi.cnptia.embrapa.br/)
- **Documentação**: [infoteca.cnptia.embrapa.br](https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1160077/1/Comunicado136-2023.pdf)
- **Recursos**:
  - Inserção padronizada de dados
  - Verificação de dados sensíveis
  - Base de dados unificada
  - Interoperabilidade entre sistemas
- **Uso no sistema**: Integração direta com sistema de rastreabilidade bovina

#### **b) Outras APIs da AgroAPI**
- Índices vegetativos
- Termos técnicos agropecuários
- Modelos agropecuários

---

### 🏢 **3. CNA (Confederação da Agricultura e Pecuária do Brasil)**

#### **a) AgriTrace Animal**
- **Descrição**: Plataforma de gestão de protocolos de rastreabilidade animal
- **Fonte**: [cnabrasil.org.br](https://www.cnabrasil.org.br/)
- **Recursos**:
  - Certificação da cadeia produtiva
  - Rastreabilidade de origem ao consumidor
  - Protocolos de adesão voluntária
- **Status**: Não há documentação pública de API
- **Observação**: Contatar CNA diretamente para integração

---

## 🔧 **IMPLEMENTAÇÃO NO SISTEMA**

### **Estrutura de Integração Sugerida:**

```python
# gestao_rural/apis_integracao/
├── __init__.py
├── api_agrofit.py          # API de produtos fitossanitários
├── api_infodap.py          # API de DAP
├── api_bovtrace.py         # API de rastreabilidade bovina
├── api_sisbov.py           # Integração com SISBOV (se disponível)
└── utils.py                # Utilitários comuns
```

### **Funcionalidades a Implementar:**

1. **Sincronização de Dados de Rastreabilidade**
   - Enviar dados de animais para BovTrace
   - Validar números de brinco
   - Consultar histórico de animais

2. **Consulta de Produtos Fitossanitários**
   - Buscar produtos permitidos por cultura
   - Validar uso de defensivos

3. **Validação de Propriedades**
   - Consultar DAP via InfoDAP
   - Verificar elegibilidade para crédito

---

## 📝 **PRÓXIMOS PASSOS**

### **1. Solicitar Acessos:**

#### **Para API BovTrace (Embrapa):**
- Acessar: [agroapi.cnptia.embrapa.br](https://www.agroapi.cnptia.embrapa.br/)
- Registrar-se na plataforma
- Obter credenciais (API key)

#### **Para API SDA (MAPA):**
- Preencher solicitação em: [gov.br/agricultura/.../solicitacao-de-acesso-a-api-externa](https://www.gov.br/agricultura/pt-br/assuntos/defesa-agropecuaria/plataforma-sda/mapa-labs/solicitacao-de-acesso-a-api-externa)
- Aguardar aprovação
- Receber credenciais

#### **Para AgriTrace (CNA):**
- Contatar CNA diretamente
- Solicitar informações sobre integração
- Verificar disponibilidade de API

### **2. Implementar Integração:**

```python
# Exemplo de estrutura para API BovTrace
class BovTraceAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.agroapi.cnptia.embrapa.br/bovtrace"
    
    def enviar_animal(self, animal_data):
        """Envia dados de animal para BovTrace"""
        pass
    
    def consultar_animal(self, numero_brinco):
        """Consulta histórico de animal no BovTrace"""
        pass
    
    def validar_brinco(self, numero_brinco):
        """Valida se brinco existe no sistema"""
        pass
```

### **3. Configurar no Django:**

```python
# settings.py
AGRICULTURA_APIS = {
    'BOVTRACE_API_KEY': os.getenv('BOVTRACE_API_KEY', ''),
    'AGROFIT_ENABLED': True,
    'INFODAP_ENABLED': True,
    'SISBOV_ENABLED': False,  # Ativar quando tiver acesso
}
```

---

## ⚠️ **OBSERVAÇÕES IMPORTANTES**

1. **SISBOV**: Não possui API pública documentada. Pode ser necessário:
   - Solicitar acesso especial via SDA
   - Usar web scraping (não recomendado)
   - Integração manual via exportação/importação

2. **AgriTrace (CNA)**: Não há documentação pública de API. Contatar CNA diretamente.

3. **API BovTrace (Embrapa)**: É a mais acessível e documentada para rastreabilidade bovina.

4. **Autenticação**: Todas as APIs requerem credenciais e podem ter limites de requisições.

---

## 🎯 **RECOMENDAÇÃO**

### **Prioridade de Implementação:**

1. **API BovTrace (Embrapa)** - ✅ **MAIS ACESSÍVEL**
   - Melhor documentada
   - Focada em rastreabilidade bovina
   - Integração direta com nosso sistema

2. **API InfoDAP (MAPA)** - ✅ **ÚTIL PARA CRÉDITO**
   - Validação de propriedades familiares
   - Acesso a linhas de crédito específicas

3. **API Agrofit (Embrapa)** - ✅ **COMPLEMENTAR**
   - Útil para gestão de defensivos
   - Não é crítica para rastreabilidade

4. **SISBOV** - ⚠️ **AGUARDAR ACESSO**
   - Sistema oficial, mas sem API pública
   - Requer solicitação especial

5. **AgriTrace (CNA)** - ⚠️ **AGUARDAR INFORMAÇÕES**
   - Contatar CNA para detalhes

---

## 📚 **LINKS ÚTEIS**

- **AgroAPI (Embrapa)**: https://www.agroapi.cnptia.embrapa.br/
- **SISBOV**: https://sisbov.agricultura.gov.br/
- **InfoDAP API**: https://www.gov.br/conecta/catalogo/apis/infodap
- **MAPA - Plataforma SDA**: https://www.gov.br/agricultura/pt-br/assuntos/defesa-agropecuaria/plataforma-sda
- **CNA**: https://www.cnabrasil.org.br/

---

## 💡 **CONCLUSÃO**

O sistema pode ser integrado com:
- ✅ **API BovTrace** (Embrapa) - Para rastreabilidade bovina
- ✅ **API InfoDAP** (MAPA) - Para validação de propriedades
- ✅ **API Agrofit** (Embrapa) - Para produtos fitossanitários

As outras APIs (SISBOV, AgriTrace) requerem solicitação de acesso ou contato direto com os órgãos responsáveis.


