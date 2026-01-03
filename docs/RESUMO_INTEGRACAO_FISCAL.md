# Resumo: Integração com Sintegra e Receita Federal

## ✅ O que foi implementado

### 1. **Documentação Completa**
- **`GUIA_INTEGRACAO_SINTEGRA_RECEITA_FEDERAL.md`**: Guia completo com:
  - Explicação do que é Sintegra e Receita Federal
  - Dados necessários para integração
  - Bibliotecas Python recomendadas
  - Exemplos de código
  - Próximos passos de implementação

### 2. **Serviços de Geração de Arquivos**

#### **`gestao_rural/services/sintegra_service.py`**
- Classe `SintegraService` para geração de arquivos Sintegra
- Validação de dados obrigatórios
- Geração de registros tipo 0, 1, 3 (entrada/saída) e 5
- Função helper `gerar_arquivo_sintegra()`

#### **`gestao_rural/services/sped_service.py`**
- Classe `SPEDService` para geração de arquivos SPED Fiscal
- Geração de EFD-ICMS/IPI
- Registros 0000, 0001, 0005, C100, C170, 9999
- Função helper `gerar_arquivo_sped()`

### 3. **Views e Interface**

#### **`gestao_rural/views_fiscal.py`**
- `fiscal_dashboard()`: Dashboard principal
- `download_sintegra()`: Geração e download de arquivo Sintegra
- `download_sped()`: Geração e download de arquivo SPED
- `validar_dados_fiscais()`: API para validar dados cadastrais

#### **`templates/gestao_rural/fiscal_dashboard.html`**
- Interface web completa
- Formulários para geração de arquivos
- Validação de dados fiscais
- Informações e alertas importantes

### 4. **URLs Configuradas**
- `/propriedade/<id>/fiscal/` - Dashboard
- `/propriedade/<id>/fiscal/sintegra/download/` - Download Sintegra
- `/propriedade/<id>/fiscal/sped/download/` - Download SPED
- `/propriedade/<id>/fiscal/validar/` - API de validação

### 5. **Dependências**
- `requirements.txt` atualizado com bibliotecas recomendadas (comentadas)

---

## 🚀 Como Usar

### 1. Acessar o Dashboard Fiscal
```
http://seu-servidor/propriedade/<id>/fiscal/
```

### 2. Gerar Arquivo Sintegra
1. Acesse o dashboard fiscal
2. Preencha o período (início e fim)
3. Selecione a UF
4. Clique em "Gerar e Baixar Arquivo Sintegra"

### 3. Gerar Arquivo SPED
1. Acesse o dashboard fiscal
2. Preencha o período (início e fim)
3. Clique em "Gerar e Baixar Arquivo SPED"

### 4. Validar Dados
- Clique no botão "Validar Dados Fiscais" para verificar se todos os dados obrigatórios estão preenchidos

---

## ⚠️ Importante: Status Atual

### ✅ Funcionalidades Implementadas
- Estrutura base completa
- Geração de arquivos em formato texto
- Validação de dados cadastrais
- Interface web funcional

### ⚠️ Limitações Atuais
- **Cálculos de impostos são simplificados** - Em produção, é necessário:
  - Implementar cálculos reais de ICMS, IPI, PIS, COFINS
  - Considerar alíquotas por estado/produto
  - Aplicar CST (Código de Situação Tributária) corretamente
  
- **Layouts são genéricos** - Cada estado tem formato específico:
  - SP, MG, RS, etc. têm layouts diferentes
  - Recomenda-se usar bibliotecas especializadas (pysintegra, erpbrasil.sped)
  
- **Falta campo Cliente em NotaFiscal** - Para notas de saída, é necessário:
  - Adicionar campo `cliente` no modelo `NotaFiscal`
  - Criar migração

---

## 📋 Próximos Passos Recomendados

### Fase 1: Instalar Bibliotecas Especializadas (Recomendado)
```bash
# Opção 1: pysintegra (para Sintegra)
pip install pysintegra

# Opção 2: erpbrasil.edoc (biblioteca completa)
pip install erpbrasil.edoc erpbrasil.sped

# Opção 3: pysped (para SPED)
pip install pysped
```

### Fase 2: Ajustar Cálculos Fiscais
1. Implementar cálculo real de ICMS por estado
2. Implementar cálculo de IPI, PIS, COFINS
3. Adicionar CST (Código de Situação Tributária) nos itens
4. Considerar regime tributário (Simples, Presumido, Real)

### Fase 3: Adicionar Campos Faltantes
1. Adicionar campo `cliente` em `NotaFiscal` (para notas de saída)
2. Adicionar campos de impostos calculados em `NotaFiscal`
3. Adicionar `regime_tributario` em `Propriedade` ou `ProdutorRural`

### Fase 4: Validação e Testes
1. Testar com dados reais
2. Validar arquivos gerados com ferramentas oficiais
3. Consultar contador/tributarista
4. Ajustar conforme feedback

### Fase 5: Integração com APIs de Terceiros (Opcional)
- Considerar usar APIs como Focus NFe, NFe.io para:
  - Geração automática de arquivos
  - Validação automática
  - Transmissão direta

---

## 🔧 Ajustes Necessários para Produção

### 1. Modelo NotaFiscal
Adicionar campos para impostos calculados:
```python
# Em models_compras_financeiro.py
base_calculo_icms = models.DecimalField(...)
valor_icms = models.DecimalField(...)
base_calculo_ipi = models.DecimalField(...)
valor_ipi = models.DecimalField(...)
# ... outros impostos
cliente = models.ForeignKey(Cliente, ...)  # Para notas de saída
```

### 2. Cálculo de Impostos
Implementar serviço de cálculo fiscal:
```python
# gestao_rural/services/calculo_fiscal.py
def calcular_icms(nota, item, uf_origem, uf_destino):
    # Implementar cálculo real conforme legislação
    pass
```

### 3. Tabelas de Referência
- Tabela de municípios IBGE (para código IBGE)
- Tabela de CFOP
- Tabela de CST
- Tabela de NCM

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Manual Sintegra](http://www.sintegra.gov.br/)
- [SPED - Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/sped)
- [eSocial](https://www.gov.br/esocial/pt-br)

### Bibliotecas Python
- [pysintegra](https://github.com/akretion/pysintegra)
- [erpbrasil.edoc](https://github.com/erpbrasil/erpbrasil.edoc)
- [erpbrasil.sped](https://github.com/erpbrasil/erpbrasil.sped)

### APIs de Terceiros
- [Focus NFe](https://doc.focusnfe.com.br/)
- [NFe.io](https://nfe.io/)

---

## 💡 Dicas Importantes

1. **Sempre valide arquivos antes de transmitir** - Use ferramentas oficiais
2. **Consulte um contador** - Integrações fiscais são complexas e mudam frequentemente
3. **Mantenha bibliotecas atualizadas** - Layouts mudam anualmente
4. **Teste em ambiente de homologação primeiro** - Nunca transmita arquivos de produção sem testar
5. **Documente alterações** - Mantenha registro de mudanças nos layouts

---

**Criado em:** 2024-01-XX  
**Versão:** 1.0  
**Status:** Estrutura base implementada - Requer ajustes para produção

