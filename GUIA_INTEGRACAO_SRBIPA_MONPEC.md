# 🔗 Guia de Integração: Monpec com SRBIPA (Sistema de Rastreabilidade Bovídea Individual do Pará)

**Data:** Dezembro 2025  
**Versão:** 1.0  
**Sistema:** Monpec - Gestão Rural  
**Integração:** SRBIPA - ADEPARÁ

---

## 📋 SUMÁRIO EXECUTIVO

Este guia apresenta o processo completo para integrar o sistema Monpec com o **SRBIPA** (Sistema de Rastreabilidade Bovídea Individual do Pará), permitindo sincronização automática de dados de identificação e movimentação de animais entre os sistemas.

### **O que é o SRBIPA?**

O **SRBIPA** é o sistema oficial da **ADEPARÁ** (Agência de Defesa Agropecuária do Estado do Pará) para rastreabilidade individual de bovinos e búfalos no estado do Pará, instituído pelo **Decreto Estadual nº 3.533/2023**.

### **Benefícios da Integração:**

✅ **Sincronização Automática** - Dados atualizados em tempo real  
✅ **Conformidade Legal** - Atendimento automático às obrigações  
✅ **Redução de Trabalho Manual** - Eliminação de dupla digitação  
✅ **Validação Automática** - Verificação de dados antes do envio  
✅ **Relatórios Automáticos** - Geração de relatórios obrigatórios  
✅ **Rastreabilidade Completa** - Histórico completo de cada animal

---

## 🎯 1. REQUISITOS E PREPARAÇÃO

### 1.1. Requisitos Legais

#### **Cadastro na ADEPARÁ:**
- ✅ Propriedade cadastrada na ADEPARÁ
- ✅ Cadastro agropecuário atualizado
- ✅ Documentação em dia (prazo: 16 de julho de 2025)

#### **Identificação dos Animais:**
- ✅ Animais identificados com **dois brincos**:
  - Brinco visual (padrão ISO 076)
  - Brinco eletrônico (RFID)
- ✅ Números de brincos registrados no Monpec

### 1.2. Requisitos Técnicos

#### **Sistema Monpec:**
- ✅ Versão atualizada do sistema
- ✅ Módulo de rastreabilidade ativo
- ✅ Animais cadastrados individualmente
- ✅ Dados completos (brincos, raça, sexo, data de nascimento)

#### **Acesso ao SRBIPA:**
- ⚠️ **Credenciais de acesso** ao sistema SRBIPA
- ⚠️ **Solicitar acesso** na ADEPARÁ se ainda não tiver

### 1.3. Documentação Necessária

#### **Base Legal:**
- **Decreto Estadual nº 3.533/2023** - Institui o SRBIPA
- **Portaria ADEPARÁ nº 3879/2024** - Padronização de brincos
- **Instrução Normativa MAPA nº 62/2018** - Movimentação de animais

#### **Especificações Técnicas:**
- Padrão de identificação (ISO 076)
- Formato de dados para integração
- Protocolo de comunicação
- Validações obrigatórias

---

## 📞 2. COMO OBTER ACESSO AO SRBIPA

### 2.1. Contato com ADEPARÁ

#### **Informações de Contato:**

**ADEPARÁ - Agência de Defesa Agropecuária do Pará**
- **Site:** www.adepara.pa.gov.br
- **Telefone:** (91) 3210-5000
- **E-mail:** adepara@adepara.pa.gov.br
- **Endereço:** Av. Augusto Montenegro, 3150 - Icoaraci, Belém - PA

#### **Unidades Regionais:**
Consulte o site da ADEPARÁ para encontrar a unidade mais próxima da sua propriedade.

#### **📖 Guia de Credenciais SISBOV:**

Se você também precisa de credenciais para o SISBOV (Sistema Nacional), consulte:
- **`GUIA_CREDENCIAIS_SISBOV.md`** - Guia completo sobre como obter credenciais do SISBOV

**Nota:** O SRBIPA (Pará) e o SISBOV (Nacional) são sistemas complementares. Você pode precisar de credenciais para ambos.

### 2.2. Processo de Solicitação de Acesso

#### **Passo 1: Cadastro na ADEPARÁ**
1. Comparecer a uma unidade da ADEPARÁ
2. Apresentar documentos:
   - RG ou CNH
   - Comprovante de propriedade
   - Lista de animais da propriedade
3. Atualizar cadastro agropecuário

#### **Passo 2: Solicitar Credenciais SRBIPA**
1. Solicitar acesso ao sistema SRBIPA
2. Informar que deseja integrar com sistema de gestão (Monpec)
3. Obter:
   - Login de acesso
   - Senha inicial
   - Token de API (se disponível)
   - Documentação técnica

#### **Passo 3: Verificar Formato de Integração**
1. Consultar se há API disponível
2. Verificar formato de exportação/importação
3. Obter especificações técnicas
4. Solicitar documentação de integração

### 2.3. Alternativas de Integração

#### **Opção 1: API REST (Ideal)**
- Integração em tempo real
- Sincronização automática
- Validação imediata
- **Status:** Verificar disponibilidade com ADEPARÁ

#### **Opção 2: Importação/Exportação de Arquivos**
- Exportação de dados do Monpec
- Importação no SRBIPA
- Sincronização periódica
- **Status:** Mais comum atualmente

#### **Opção 3: Integração via SISBOV Nacional**
- Integração com SISBOV do MAPA
- SRBIPA sincroniza com SISBOV
- **Status:** Verificar se SRBIPA está integrado ao SISBOV

---

## 🔧 3. IMPLEMENTAÇÃO TÉCNICA

### 3.1. Estrutura de Dados Necessária

#### **Dados de Identificação do Animal:**

```python
{
    "numero_brinco_visual": "BR123456789012",      # Brinco visual (15 dígitos)
    "numero_brinco_eletronico": "EID123456789",     # Brinco RFID
    "codigo_sisbov": "BR123456789012",              # Código SISBOV (se disponível)
    "numero_manejo": "123456",                      # Número de manejo (6 dígitos)
    "data_nascimento": "2020-05-15",                # Data de nascimento
    "raca": "Nelore",                               # Raça
    "sexo": "F",                                    # F (Fêmea) ou M (Macho)
    "categoria": "Novilha",                         # Categoria atual
    "propriedade_origem": "12345678901234",         # CPF/CNPJ da propriedade
    "data_identificacao": "2024-01-10",             # Data de aplicação dos brincos
    "tipo_origem": "NASCIMENTO"                     # NASCIMENTO, COMPRA, TRANSFERENCIA
}
```

#### **Dados de Movimentação:**

```python
{
    "numero_brinco": "BR123456789012",
    "tipo_movimentacao": "VENDA",                   # VENDA, COMPRA, TRANSFERENCIA, MORTE
    "data_movimentacao": "2025-01-15",
    "propriedade_origem": "12345678901234",
    "propriedade_destino": "98765432109876",
    "numero_gta": "GTA-2025-001234",                # Número da GTA
    "numero_nota_fiscal": "NF-123456",              # Número da nota fiscal (se houver)
    "peso": 450.5,                                  # Peso do animal (kg)
    "valor": 2500.00,                               # Valor da transação (R$)
    "observacoes": "Venda para frigorífico"
}
```

#### **Dados Sanitários:**

```python
{
    "numero_brinco": "BR123456789012",
    "tipo_registro": "VACINACAO",                  # VACINACAO, TRATAMENTO, EXAME
    "data": "2025-01-10",
    "descricao": "Vacinação contra brucelose",
    "produto": "Brucelose B19",
    "lote": "LOT-2024-001",
    "responsavel": "Dr. João Silva - CRMV-PA 1234"
}
```

### 3.2. Módulo de Integração SRBIPA

#### **Estrutura de Arquivos:**

```
gestao_rural/
├── apis_integracao/
│   ├── __init__.py
│   ├── api_srbipa.py              # Classe principal de integração
│   ├── exportadores_srbipa.py     # Exportação de dados
│   ├── importadores_srbipa.py     # Importação de dados
│   └── validadores_srbipa.py      # Validação de dados
├── views_rastreabilidade.py        # Views existentes
└── models.py                       # Modelos existentes
```

### 3.3. Código de Exemplo - API SRBIPA

#### **Classe Principal de Integração:**

```python
# gestao_rural/apis_integracao/api_srbipa.py

import requests
import json
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from datetime import datetime


class SRBIPAAPI:
    """Classe para integração com SRBIPA - ADEPARÁ"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa a API SRBIPA
        
        Args:
            api_key: Chave de API (se None, tenta obter de settings)
            base_url: URL base da API (se None, usa padrão)
        """
        self.api_key = api_key or getattr(settings, 'SRBIPA_API_KEY', '')
        self.base_url = base_url or getattr(
            settings, 
            'SRBIPA_BASE_URL', 
            'https://srbipa.adepara.pa.gov.br/api'  # URL a confirmar com ADEPARÁ
        )
        self.timeout = getattr(settings, 'SRBIPA_TIMEOUT', 30)
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
        }
    
    def enviar_animal(self, animal_data: Dict) -> Dict:
        """
        Envia dados de um animal para o SRBIPA
        
        Args:
            animal_data: Dicionário com dados do animal
            
        Returns:
            Resposta da API com status e dados
        """
        url = f"{self.base_url}/animais"
        
        # Validar dados antes de enviar
        if not self._validar_dados_animal(animal_data):
            return {
                'sucesso': False,
                'erro': 'Dados do animal inválidos'
            }
        
        try:
            response = requests.post(
                url,
                json=animal_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return {
                    'sucesso': True,
                    'dados': response.json(),
                    'mensagem': 'Animal cadastrado com sucesso no SRBIPA'
                }
            else:
                return {
                    'sucesso': False,
                    'erro': response.text,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'sucesso': False,
                'erro': f'Erro na comunicação com SRBIPA: {str(e)}'
            }
    
    def atualizar_animal(self, numero_brinco: str, animal_data: Dict) -> Dict:
        """
        Atualiza dados de um animal no SRBIPA
        
        Args:
            numero_brinco: Número do brinco do animal
            animal_data: Dados atualizados
            
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/animais/{numero_brinco}"
        
        try:
            response = requests.put(
                url,
                json=animal_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'dados': response.json(),
                    'mensagem': 'Animal atualizado com sucesso'
                }
            else:
                return {
                    'sucesso': False,
                    'erro': response.text,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'sucesso': False,
                'erro': f'Erro na comunicação: {str(e)}'
            }
    
    def registrar_movimentacao(self, movimentacao_data: Dict) -> Dict:
        """
        Registra uma movimentação de animal no SRBIPA
        
        Args:
            movimentacao_data: Dados da movimentação
            
        Returns:
            Resposta da API
        """
        url = f"{self.base_url}/movimentacoes"
        
        # Validar dados
        if not self._validar_dados_movimentacao(movimentacao_data):
            return {
                'sucesso': False,
                'erro': 'Dados da movimentação inválidos'
            }
        
        try:
            response = requests.post(
                url,
                json=movimentacao_data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                return {
                    'sucesso': True,
                    'dados': response.json(),
                    'mensagem': 'Movimentação registrada com sucesso'
                }
            else:
                return {
                    'sucesso': False,
                    'erro': response.text,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'sucesso': False,
                'erro': f'Erro na comunicação: {str(e)}'
            }
    
    def consultar_animal(self, numero_brinco: str) -> Dict:
        """
        Consulta dados de um animal no SRBIPA
        
        Args:
            numero_brinco: Número do brinco
            
        Returns:
            Dados do animal
        """
        url = f"{self.base_url}/animais/{numero_brinco}"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    'sucesso': True,
                    'dados': response.json()
                }
            else:
                return {
                    'sucesso': False,
                    'erro': response.text,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'sucesso': False,
                'erro': f'Erro na comunicação: {str(e)}'
            }
    
    def _validar_dados_animal(self, dados: Dict) -> bool:
        """Valida dados do animal antes de enviar"""
        campos_obrigatorios = [
            'numero_brinco_visual',
            'numero_brinco_eletronico',
            'data_nascimento',
            'raca',
            'sexo',
            'categoria'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return False
        
        return True
    
    def _validar_dados_movimentacao(self, dados: Dict) -> bool:
        """Valida dados da movimentação antes de enviar"""
        campos_obrigatorios = [
            'numero_brinco',
            'tipo_movimentacao',
            'data_movimentacao',
            'propriedade_origem'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in dados or not dados[campo]:
                return False
        
        return True
```

### 3.4. Exportador de Dados para SRBIPA

#### **Exportação em Lote:**

```python
# gestao_rural/apis_integracao/exportadores_srbipa.py

from gestao_rural.models import AnimalIndividual, MovimentacaoIndividual
from .api_srbipa import SRBIPAAPI
from typing import List, Dict


class ExportadorSRBIPA:
    """Classe para exportar dados do Monpec para SRBIPA"""
    
    def __init__(self):
        self.api = SRBIPAAPI()
    
    def exportar_animal(self, animal: AnimalIndividual) -> Dict:
        """
        Exporta um animal do Monpec para SRBIPA
        
        Args:
            animal: Instância de AnimalIndividual
            
        Returns:
            Resultado da exportação
        """
        dados = {
            'numero_brinco_visual': animal.numero_brinco,
            'numero_brinco_eletronico': animal.codigo_eletronico or '',
            'codigo_sisbov': animal.codigo_sisbov or animal.numero_brinco,
            'numero_manejo': animal.numero_manejo or '',
            'data_nascimento': animal.data_nascimento.strftime('%Y-%m-%d') if animal.data_nascimento else '',
            'raca': animal.raca.nome if animal.raca else '',
            'sexo': 'F' if animal.sexo == 'FEMEA' else 'M',
            'categoria': animal.categoria.nome if animal.categoria else '',
            'propriedade_origem': animal.propriedade.cpf_cnpj or '',
            'data_identificacao': animal.data_identificacao.strftime('%Y-%m-%d') if animal.data_identificacao else '',
            'tipo_origem': animal.tipo_origem or 'NASCIMENTO'
        }
        
        # Se já existe no SRBIPA, atualizar; senão, criar
        resultado_consulta = self.api.consultar_animal(animal.numero_brinco)
        
        if resultado_consulta.get('sucesso'):
            return self.api.atualizar_animal(animal.numero_brinco, dados)
        else:
            return self.api.enviar_animal(dados)
    
    def exportar_movimentacao(self, movimentacao: MovimentacaoIndividual) -> Dict:
        """
        Exporta uma movimentação para SRBIPA
        
        Args:
            movimentacao: Instância de MovimentacaoIndividual
            
        Returns:
            Resultado da exportação
        """
        dados = {
            'numero_brinco': movimentacao.animal.numero_brinco,
            'tipo_movimentacao': movimentacao.tipo_movimentacao,
            'data_movimentacao': movimentacao.data_movimentacao.strftime('%Y-%m-%d'),
            'propriedade_origem': movimentacao.propriedade_origem.cpf_cnpj if movimentacao.propriedade_origem else '',
            'propriedade_destino': movimentacao.propriedade_destino.cpf_cnpj if movimentacao.propriedade_destino else '',
            'numero_gta': movimentacao.numero_gta or '',
            'numero_nota_fiscal': movimentacao.numero_nota_fiscal or '',
            'peso': float(movimentacao.peso) if movimentacao.peso else None,
            'valor': float(movimentacao.valor) if movimentacao.valor else None,
            'observacoes': movimentacao.observacoes or ''
        }
        
        return self.api.registrar_movimentacao(dados)
    
    def exportar_lote_animais(self, propriedade_id: int) -> Dict:
        """
        Exporta todos os animais de uma propriedade
        
        Args:
            propriedade_id: ID da propriedade
            
        Returns:
            Resumo da exportação
        """
        animais = AnimalIndividual.objects.filter(propriedade_id=propriedade_id)
        
        resultados = {
            'sucesso': 0,
            'erro': 0,
            'detalhes': []
        }
        
        for animal in animais:
            resultado = self.exportar_animal(animal)
            
            if resultado.get('sucesso'):
                resultados['sucesso'] += 1
            else:
                resultados['erro'] += 1
            
            resultados['detalhes'].append({
                'animal': animal.numero_brinco,
                'sucesso': resultado.get('sucesso'),
                'mensagem': resultado.get('mensagem') or resultado.get('erro')
            })
        
        return resultados
```

### 3.5. View de Integração

#### **View para Sincronização:**

```python
# gestao_rural/views_rastreabilidade.py (adicionar)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from gestao_rural.models import Propriedade
from gestao_rural.apis_integracao.exportadores_srbipa import ExportadorSRBIPA
import json


@require_http_methods(["GET", "POST"])
def sincronizar_srbipa(request, propriedade_id):
    """
    View para sincronizar dados com SRBIPA
    """
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, usuario=request.user)
    
    if request.method == 'POST':
        exportador = ExportadorSRBIPA()
        
        # Exportar todos os animais
        resultado = exportador.exportar_lote_animais(propriedade_id)
        
        if resultado['sucesso'] > 0:
            messages.success(
                request, 
                f"Sincronização realizada com sucesso! {resultado['sucesso']} animais sincronizados."
            )
        
        if resultado['erro'] > 0:
            messages.warning(
                request,
                f"{resultado['erro']} animais apresentaram erro na sincronização."
            )
        
        context = {
            'propriedade': propriedade,
            'resultado': resultado
        }
        
        return render(request, 'gestao_rural/sincronizacao_srbipa.html', context)
    
    context = {
        'propriedade': propriedade
    }
    
    return render(request, 'gestao_rural/sincronizacao_srbipa.html', context)
```

---

## 📝 4. CONFIGURAÇÃO NO MONPEC

### 4.1. Configurações em settings.py

```python
# settings.py

# Configurações SRBIPA
SRBIPA_API_KEY = env('SRBIPA_API_KEY', default='')
SRBIPA_BASE_URL = env('SRBIPA_BASE_URL', default='https://srbipa.adepara.pa.gov.br/api')
SRBIPA_TIMEOUT = env('SRBIPA_TIMEOUT', default=30)
SRBIPA_SINCRONIZACAO_AUTOMATICA = env('SRBIPA_SINCRONIZACAO_AUTOMATICA', default=False)
```

### 4.2. Variáveis de Ambiente (.env)

```bash
# .env

# SRBIPA - ADEPARÁ
SRBIPA_API_KEY=sua_chave_api_aqui
SRBIPA_BASE_URL=https://srbipa.adepara.pa.gov.br/api
SRBIPA_TIMEOUT=30
SRBIPA_SINCRONIZACAO_AUTOMATICA=False
```

### 4.3. URLs

```python
# gestao_rural/urls.py

urlpatterns = [
    # ... outras URLs ...
    path('propriedade/<int:propriedade_id>/rastreabilidade/sincronizar-srbipa/', 
         views_rastreabilidade.sincronizar_srbipa, 
         name='sincronizar_srbipa'),
]
```

---

## 🔄 5. PROCESSO DE SINCRONIZAÇÃO

### 5.1. Sincronização Manual

#### **Passo a Passo:**

1. **Acessar o Sistema:**
   - Login no Monpec
   - Selecionar propriedade
   - Ir em "Rastreabilidade" → "Sincronizar com SRBIPA"

2. **Verificar Dados:**
   - Sistema mostra lista de animais a sincronizar
   - Verificar se dados estão completos
   - Corrigir dados faltantes se necessário

3. **Iniciar Sincronização:**
   - Clicar em "Sincronizar Agora"
   - Sistema envia dados para SRBIPA
   - Aguardar processamento

4. **Verificar Resultado:**
   - Visualizar relatório de sincronização
   - Verificar animais sincronizados
   - Corrigir erros se houver

### 5.2. Sincronização Automática

#### **Configuração:**

1. **Ativar Sincronização Automática:**
   - Configurações → Integrações → SRBIPA
   - Ativar "Sincronização Automática"
   - Definir frequência (diária, semanal)

2. **Eventos que Disparam Sincronização:**
   - Cadastro de novo animal
   - Atualização de dados do animal
   - Registro de movimentação
   - Mudança de status

3. **Logs de Sincronização:**
   - Sistema mantém log de todas as sincronizações
   - Visualizar histórico
   - Verificar erros

### 5.3. Sincronização em Lote

#### **Para Migração Inicial:**

1. **Preparar Dados:**
   - Exportar todos os animais
   - Validar dados
   - Corrigir inconsistências

2. **Executar Sincronização:**
   - Usar comando de sincronização em lote
   - Processar em lotes pequenos (100 animais)
   - Verificar resultado de cada lote

3. **Validar Resultado:**
   - Comparar dados no SRBIPA
   - Verificar se todos foram sincronizados
   - Corrigir erros

---

## ⚠️ 6. TROUBLESHOOTING

### 6.1. Problemas Comuns

#### **Erro: "Credenciais inválidas"**
- **Causa:** API key incorreta ou expirada
- **Solução:** Verificar credenciais na ADEPARÁ e atualizar no sistema

#### **Erro: "Animal já cadastrado"**
- **Causa:** Animal já existe no SRBIPA
- **Solução:** Sistema deve atualizar ao invés de criar novo

#### **Erro: "Dados incompletos"**
- **Causa:** Faltam campos obrigatórios
- **Solução:** Completar dados do animal antes de sincronizar

#### **Erro: "Timeout na comunicação"**
- **Causa:** Problema de conexão ou servidor lento
- **Solução:** Tentar novamente ou verificar conexão

### 6.2. Validações Importantes

#### **Antes de Sincronizar:**
- ✅ Todos os animais têm brinco visual cadastrado
- ✅ Todos os animais têm brinco eletrônico cadastrado
- ✅ Data de nascimento informada
- ✅ Raça informada
- ✅ Sexo informado
- ✅ Categoria informada
- ✅ Propriedade cadastrada na ADEPARÁ

---

## 📚 7. DOCUMENTAÇÃO ADICIONAL

### 7.1. Links Úteis

- **ADEPARÁ:** www.adepara.pa.gov.br
- **SRBIPA:** (URL a confirmar com ADEPARÁ)
- **Decreto 3.533/2023:** (consultar site ADEPARÁ)
- **Portaria 3879/2024:** (consultar site ADEPARÁ)

### 7.2. Contatos para Suporte

#### **ADEPARÁ - Suporte Técnico:**
- **Telefone:** (91) 3210-5000
- **E-mail:** adepara@adepara.pa.gov.br
- **Horário:** Segunda a Sexta, 8h às 17h

#### **Monpec - Suporte:**
- **Site:** https://monpec-29862706245.us-central1.run.app/
- **WhatsApp:** (consultar site)
- **E-mail:** contato@monpec.com.br

---

## 🎯 8. PRÓXIMOS PASSOS

### 8.1. Implementação Imediata

1. ⚠️ **Contatar ADEPARÁ** para obter:
   - Credenciais de acesso
   - Documentação técnica
   - Formato de integração disponível

2. ⚠️ **Desenvolver Módulo de Integração:**
   - Criar classe SRBIPAAPI
   - Implementar exportadores
   - Criar views de sincronização

3. ⚠️ **Testes:**
   - Testar com dados de exemplo
   - Validar formato de dados
   - Verificar sincronização

### 8.2. Melhorias Futuras

- ✅ Sincronização automática em tempo real
- ✅ Validação bidirecional (SRBIPA → Monpec)
- ✅ Dashboard de sincronização
- ✅ Relatórios de conformidade
- ✅ Alertas de erros

---

## ✅ 9. CHECKLIST DE IMPLEMENTAÇÃO

### **Fase 1: Preparação**
- [ ] Contatar ADEPARÁ para obter credenciais
- [ ] Obter documentação técnica do SRBIPA
- [ ] Verificar formato de integração disponível
- [ ] Validar dados dos animais no Monpec

### **Fase 2: Desenvolvimento**
- [ ] Criar classe SRBIPAAPI
- [ ] Implementar exportadores
- [ ] Criar views de sincronização
- [ ] Criar templates de interface

### **Fase 3: Testes**
- [ ] Testar com dados de exemplo
- [ ] Validar sincronização de animais
- [ ] Validar sincronização de movimentações
- [ ] Testar tratamento de erros

### **Fase 4: Produção**
- [ ] Configurar credenciais em produção
- [ ] Realizar sincronização inicial
- [ ] Validar dados no SRBIPA
- [ ] Treinar usuários

---

**Última atualização:** Dezembro 2025  
**Versão:** 1.0  
**Status:** Aguardando informações da ADEPARÁ sobre formato de integração

---

## 📝 NOTAS IMPORTANTES

⚠️ **ATENÇÃO:** Este guia foi criado com base nas informações disponíveis. O formato exato de integração com o SRBIPA pode variar e deve ser confirmado diretamente com a ADEPARÁ.

⚠️ **RECOMENDAÇÃO:** Entre em contato com a ADEPARÁ antes de iniciar a implementação para obter:
- Credenciais de acesso
- Documentação técnica atualizada
- Formato de dados exato
- Protocolo de comunicação

---

**FIM DO GUIA**

