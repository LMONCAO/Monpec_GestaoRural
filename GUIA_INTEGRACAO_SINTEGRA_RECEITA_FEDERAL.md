# Guia de Integração: Sintegra e Receita Federal

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Integração com Sintegra](#integração-com-sintegra)
3. [Integração com Receita Federal](#integração-com-receita-federal)
4. [Implementação Técnica](#implementação-técnica)
5. [Bibliotecas e Ferramentas](#bibliotecas-e-ferramentas)
6. [Estrutura de Dados Necessária](#estrutura-de-dados-necessária)
7. [Exemplos de Código](#exemplos-de-código)

---

## 🎯 Visão Geral

Este guia apresenta como integrar o sistema de gestão rural com:
- **Sintegra**: Sistema Integrado de Informações sobre Operações Interestaduais com Mercadorias e Serviços
- **Receita Federal**: Para declarações fiscais e tributárias

### O que já temos no sistema:
✅ Modelo de Nota Fiscal (NF-e) com upload de XML  
✅ Cadastro de Clientes e Fornecedores com CPF/CNPJ e Inscrição Estadual  
✅ Estrutura de webhooks e APIs REST  
✅ Dados cadastrais completos (Propriedade, Produtor Rural)

### O que precisamos implementar:
🔨 Geração de arquivos para transmissão ao Sintegra  
🔨 Integração com APIs da Receita Federal (SPED, eSocial, etc.)  
🔨 Validação e validação de dados fiscais  
🔨 Geração de relatórios obrigatórios  

---

## 🔄 Integração com Sintegra

### O que é o Sintegra?
Sistema que consolida informações sobre operações interestaduais para apuração de ICMS. Cada estado tem suas próprias regras e formatos.

### Dados Necessários para Sintegra:

#### 1. **Dados do Contribuinte (Propriedade)**
- CNPJ/CPF
- Inscrição Estadual
- Razão Social
- Endereço completo
- CEP, Município, UF

#### 2. **Operações de Entrada (Compras)**
- Notas Fiscais de entrada
- Fornecedores (CNPJ, IE, UF)
- Valores (produtos, ICMS, IPI, etc.)
- CFOP (Código Fiscal de Operações)
- Data de entrada

#### 3. **Operações de Saída (Vendas)**
- Notas Fiscais de saída
- Clientes (CNPJ, IE, UF)
- Valores e impostos
- CFOP
- Data de saída

### Formato de Arquivo Sintegra

Cada estado tem seu formato específico. Exemplos:
- **SP**: Arquivo texto delimitado (.txt)
- **MG**: Arquivo texto com layout específico
- **RS**: Arquivo EDI (Electronic Data Interchange)

### Estrutura Básica do Arquivo Sintegra:

```
Tipo 0 - Registro de Identificação do Arquivo
Tipo 1 - Registro de Identificação da Empresa
Tipo 2 - Registro de Totalizadores
Tipo 3 - Registro de Entradas/Saídas
Tipo 4 - Registro de Informações Complementares
Tipo 5 - Registro de Encerramento
```

---

## 🏛️ Integração com Receita Federal

### Principais Obrigações:

#### 1. **SPED Fiscal (Sistema Público de Escrituração Digital)**
- **SPED ICMS/IPI**: Apuração de impostos
- **SPED Contribuições**: PIS/PASEP e COFINS
- **EFD-Contribuições**: Escrituração Fiscal Digital

#### 2. **eSocial**
- Eventos trabalhistas
- Folha de pagamento
- Funcionários

#### 3. **DCTF (Declaração de Débitos e Créditos Tributários Federais)**
- Apuração de impostos federais

#### 4. **DASN-SIMEI (Declaração Anual do Simples Nacional)**
- Para empresas optantes pelo Simples Nacional

### Dados Necessários:

#### Para SPED:
- Livros fiscais (entradas, saídas, apuração)
- Notas fiscais (todas as operações)
- Apuração de impostos (ICMS, IPI, PIS, COFINS)
- Inventário de estoque

#### Para eSocial:
- Dados dos funcionários
- Folha de pagamento
- Eventos trabalhistas (admissão, demissão, férias, etc.)

---

## 🛠️ Implementação Técnica

### Opções de Integração:

#### **Opção 1: Integração Direta (Complexa)**
- Desenvolvimento próprio de geradores de arquivo
- Conformidade com layouts específicos de cada estado/órgão
- Manutenção constante devido a mudanças regulatórias

#### **Opção 2: Uso de Bibliotecas Python (Recomendada)**
- Bibliotecas especializadas que já implementam os layouts
- Menos código para manter
- Atualizações regulares pela comunidade

#### **Opção 3: Integração via API de Terceiros (Mais Simples)**
- Serviços como Focus NFe, NFe.io, ou similares
- APIs prontas para geração e transmissão
- Custo mensal, mas reduz muito o trabalho

---

## 📚 Bibliotecas e Ferramentas

### Para Sintegra:

#### 1. **pysintegra** (Recomendado)
```bash
pip install pysintegra
```
- Gera arquivos Sintegra para vários estados
- Suporta múltiplos formatos
- Documentação: https://github.com/akretion/pysintegra

#### 2. **erpbrasil.edoc**
```bash
pip install erpbrasil.edoc
```
- Biblioteca completa para documentos fiscais eletrônicos
- Suporta Sintegra, SPED, NF-e, etc.

### Para Receita Federal:

#### 1. **erpbrasil.sped**
```bash
pip install erpbrasil.sped
```
- Geração de arquivos SPED (ICMS/IPI, Contribuições)
- Validação de dados
- Layouts atualizados

#### 2. **pysped**
```bash
pip install pysped
```
- Biblioteca para SPED Fiscal e Contribuições
- Geração de EFD (Escrituração Fiscal Digital)

#### 3. **python-esocial**
```bash
pip install python-esocial
```
- Integração com eSocial
- Geração de eventos trabalhistas

### Para APIs de Terceiros:

#### 1. **Focus NFe API**
- API REST para NF-e, NFS-e, MDF-e
- Geração automática de arquivos Sintegra
- Documentação: https://doc.focusnfe.com.br/

#### 2. **NFe.io**
- API completa para documentos fiscais
- Suporta múltiplos estados

---

## 📊 Estrutura de Dados Necessária

### Campos Adicionais Necessários nos Modelos:

#### Propriedade (já temos, mas verificar):
```python
- cpf_cnpj ✅ (já existe em ProdutorRural)
- inscricao_estadual ✅ (já existe)
- razao_social (adicionar se não tiver)
- regime_tributario (Simples, Lucro Presumido, Real)
- optante_simples (boolean)
```

#### NotaFiscal (já temos, mas verificar):
```python
- chave_acesso ✅
- cfop ✅ (já existe em ItemNotaFiscal)
- base_calculo_icms
- valor_icms
- base_calculo_ipi
- valor_ipi
- base_calculo_pis
- valor_pis
- base_calculo_cofins
- valor_cofins
- codigo_situacao_tributaria (CST)
```

#### Cliente/Fornecedor (já temos):
```python
- cpf_cnpj ✅
- inscricao_estadual ✅
- uf ✅
- tipo_pessoa ✅
```

---

## 💻 Exemplos de Código

### Exemplo 1: Gerar Arquivo Sintegra (usando pysintegra)

```python
# gestao_rural/services/sintegra_service.py

from pysintegra import Sintegra
from decimal import Decimal
from datetime import date
from gestao_rural.models import Propriedade
from gestao_rural.models_compras_financeiro import NotaFiscal

def gerar_arquivo_sintegra(propriedade_id, periodo_inicio, periodo_fim, uf):
    """
    Gera arquivo Sintegra para transmissão
    
    Args:
        propriedade_id: ID da propriedade
        periodo_inicio: Data inicial (date)
        periodo_fim: Data final (date)
        uf: UF do estado (ex: 'SP', 'MG', 'RS')
    """
    propriedade = Propriedade.objects.get(id=propriedade_id)
    produtor = propriedade.produtor
    
    # Buscar notas fiscais do período
    notas_entrada = NotaFiscal.objects.filter(
        propriedade=propriedade,
        tipo='ENTRADA',
        data_emissao__range=[periodo_inicio, periodo_fim]
    )
    
    notas_saida = NotaFiscal.objects.filter(
        propriedade=propriedade,
        tipo='SAIDA',
        data_emissao__range=[periodo_inicio, periodo_fim]
    )
    
    # Criar instância do Sintegra
    sintegra = Sintegra()
    
    # Configurar dados do contribuinte
    sintegra.set_contribuinte(
        cnpj=produtor.cpf_cnpj.replace('.', '').replace('/', '').replace('-', ''),
        inscricao_estadual=propriedade.inscricao_estadual or '',
        razao_social=produtor.nome,
        municipio=propriedade.municipio,
        uf=propriedade.uf,
        cep=propriedade.cep.replace('-', '') if propriedade.cep else '',
        endereco=propriedade.endereco or '',
    )
    
    # Adicionar notas de entrada
    for nota in notas_entrada:
        fornecedor = nota.fornecedor
        sintegra.add_entrada(
            data_entrada=nota.data_entrada or nota.data_emissao,
            uf_origem=fornecedor.estado or '',
            cnpj_fornecedor=fornecedor.cpf_cnpj.replace('.', '').replace('/', '').replace('-', ''),
            inscricao_estadual_fornecedor=fornecedor.inscricao_estadual or '',
            modelo='55',  # NF-e
            serie=nota.serie,
            numero=nota.numero,
            cfop=nota.itens.first().cfop if nota.itens.exists() else '',
            valor_total=float(nota.valor_total),
            base_calculo_icms=float(nota.valor_produtos),  # Ajustar conforme necessário
            valor_icms=0.0,  # Calcular baseado na alíquota
        )
    
    # Adicionar notas de saída
    for nota in notas_saida:
        # Buscar cliente da nota (precisa adicionar campo cliente em NotaFiscal)
        # cliente = nota.cliente
        sintegra.add_saida(
            data_saida=nota.data_entrada or nota.data_emissao,
            uf_destino='',  # Preencher quando tiver cliente
            cnpj_cliente='',  # Preencher quando tiver cliente
            inscricao_estadual_cliente='',
            modelo='55',
            serie=nota.serie,
            numero=nota.numero,
            cfop='',
            valor_total=float(nota.valor_total),
            base_calculo_icms=float(nota.valor_produtos),
            valor_icms=0.0,
        )
    
    # Gerar arquivo
    arquivo = sintegra.gerar_arquivo(uf=uf)
    
    return arquivo
```

### Exemplo 2: Gerar SPED Fiscal (usando erpbrasil.sped)

```python
# gestao_rural/services/sped_service.py

from erpbrasil.sped import SpedFiscal
from gestao_rural.models import Propriedade
from gestao_rural.models_compras_financeiro import NotaFiscal

def gerar_sped_fiscal(propriedade_id, periodo_inicio, periodo_fim):
    """
    Gera arquivo SPED Fiscal (EFD-ICMS/IPI)
    """
    propriedade = Propriedade.objects.get(id=propriedade_id)
    produtor = propriedade.produtor
    
    # Buscar todas as notas do período
    notas = NotaFiscal.objects.filter(
        propriedade=propriedade,
        data_emissao__range=[periodo_inicio, periodo_fim]
    )
    
    # Criar instância do SPED
    sped = SpedFiscal()
    
    # Configurar empresa
    sped.set_empresa(
        cnpj=produtor.cpf_cnpj.replace('.', '').replace('/', '').replace('-', ''),
        inscricao_estadual=propriedade.inscricao_estadual or '',
        razao_social=produtor.nome,
        codigo_municipio='',  # Buscar código IBGE do município
        uf=propriedade.uf,
    )
    
    # Adicionar notas fiscais
    for nota in notas:
        sped.add_nota_fiscal(
            chave_acesso=nota.chave_acesso,
            data_emissao=nota.data_emissao,
            tipo_operacao='0' if nota.tipo == 'ENTRADA' else '1',
            valor_total=float(nota.valor_total),
            # ... outros campos necessários
        )
    
    # Gerar arquivo
    arquivo = sped.gerar_arquivo()
    
    return arquivo
```

### Exemplo 3: View para Download de Arquivo Sintegra

```python
# gestao_rural/views_fiscal.py

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import Propriedade
from .services.sintegra_service import gerar_arquivo_sintegra

@login_required
def download_sintegra(request, propriedade_id):
    """
    Gera e faz download do arquivo Sintegra
    """
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Verificar permissão
    if not request.user.has_perm('gestao_rural.view_propriedade', propriedade):
        return HttpResponse('Sem permissão', status=403)
    
    # Obter parâmetros
    periodo_inicio = datetime.strptime(
        request.GET.get('inicio', f'{datetime.now().year}-01-01'),
        '%Y-%m-%d'
    ).date()
    
    periodo_fim = datetime.strptime(
        request.GET.get('fim', f'{datetime.now().year}-12-31'),
        '%Y-%m-%d'
    ).date()
    
    uf = request.GET.get('uf', propriedade.uf)
    
    # Gerar arquivo
    arquivo = gerar_arquivo_sintegra(
        propriedade_id=propriedade.id,
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        uf=uf
    )
    
    # Preparar resposta
    response = HttpResponse(arquivo, content_type='text/plain; charset=iso-8859-1')
    response['Content-Disposition'] = f'attachment; filename="sintegra_{propriedade.uf}_{periodo_inicio.year}{periodo_inicio.month:02d}.txt"'
    
    return response
```

### Exemplo 4: Integração com API Focus NFe (Alternativa Simples)

```python
# gestao_rural/services/focus_nfe_service.py

import requests
from django.conf import settings

class FocusNFEService:
    """
    Serviço para integração com Focus NFe API
    """
    
    def __init__(self):
        self.base_url = "https://api.focusnfe.com.br"
        self.token = settings.FOCUS_NFE_TOKEN  # Adicionar no settings.py
    
    def gerar_sintegra(self, propriedade_id, periodo_inicio, periodo_fim):
        """
        Solicita geração de arquivo Sintegra via API
        """
        url = f"{self.base_url}/sintegra"
        
        headers = {
            "Authorization": f"Token token={self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "cnpj": "",  # CNPJ da propriedade
            "periodo_inicio": periodo_inicio.strftime("%Y-%m-%d"),
            "periodo_fim": periodo_fim.strftime("%Y-%m-%d"),
            "uf": "",  # UF do estado
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def consultar_status(self, job_id):
        """
        Consulta status da geração do arquivo
        """
        url = f"{self.base_url}/sintegra/{job_id}"
        
        headers = {
            "Authorization": f"Token token={self.token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
```

---

## 📝 Próximos Passos de Implementação

### Fase 1: Preparação dos Dados
1. ✅ Verificar campos existentes nos modelos
2. ⬜ Adicionar campos faltantes (regime tributário, CST, etc.)
3. ⬜ Criar migrações para novos campos
4. ⬜ Validar dados cadastrais (CPF/CNPJ, IE)

### Fase 2: Instalação de Bibliotecas
1. ⬜ Adicionar bibliotecas ao `requirements.txt`
2. ⬜ Instalar dependências
3. ⬜ Testar bibliotecas escolhidas

### Fase 3: Implementação dos Serviços
1. ⬜ Criar `gestao_rural/services/sintegra_service.py`
2. ⬜ Criar `gestao_rural/services/sped_service.py`
3. ⬜ Criar views para geração de arquivos
4. ⬜ Adicionar URLs

### Fase 4: Interface do Usuário
1. ⬜ Criar página para geração de arquivos Sintegra
2. ⬜ Criar página para geração de SPED
3. ⬜ Adicionar histórico de arquivos gerados
4. ⬜ Adicionar validações e mensagens de erro

### Fase 5: Testes e Validação
1. ⬜ Testar com dados reais
2. ⬜ Validar arquivos gerados com ferramentas oficiais
3. ⬜ Corrigir problemas encontrados
4. ⬜ Documentar processo

---

## ⚠️ Considerações Importantes

### 1. **Conformidade Legal**
- Cada estado tem regras específicas para Sintegra
- Layouts podem mudar anualmente
- É recomendado validar arquivos antes de transmitir

### 2. **Segurança**
- Dados fiscais são sensíveis
- Implementar autenticação adequada
- Logs de auditoria para geração de arquivos
- Criptografia para dados em trânsito

### 3. **Performance**
- Arquivos podem ser grandes (milhares de notas)
- Considerar processamento assíncrono (Celery)
- Cache de dados frequentemente acessados

### 4. **Manutenção**
- Manter bibliotecas atualizadas
- Monitorar mudanças regulatórias
- Testar após atualizações

---

## 🔗 Links Úteis

- [Manual Sintegra](http://www.sintegra.gov.br/)
- [SPED - Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/sped)
- [eSocial - Portal](https://www.gov.br/esocial/pt-br)
- [pysintegra GitHub](https://github.com/akretion/pysintegra)
- [erpbrasil.edoc](https://github.com/erpbrasil/erpbrasil.edoc)

---

## 📞 Suporte

Para dúvidas sobre implementação:
1. Consultar documentação das bibliotecas
2. Verificar exemplos nos repositórios GitHub
3. Contatar suporte técnico das bibliotecas
4. Consultar contador/tributarista para validação

---

**Última atualização:** 2024-01-XX  
**Versão do documento:** 1.0

