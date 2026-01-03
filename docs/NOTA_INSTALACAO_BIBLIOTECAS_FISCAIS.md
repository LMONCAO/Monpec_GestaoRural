# Nota: Instalação de Bibliotecas Fiscais

## ✅ Bibliotecas Instaladas com Sucesso

As seguintes bibliotecas foram instaladas para trabalhar com arquivos SPED e análise fiscal:

### 1. **spedpytools** (v0.1.1)
- **Função**: Visualização e análise de arquivos SPED em estruturas de tabelas (Pandas)
- **Uso**: Ler arquivos SPED (EFD, ECD, etc.) e exportar para Excel
- **Exemplo**:
  ```python
  from spedpytools import spedpytools
  arq = spedpytools.EFDFile()
  arq.readfile("efd.txt")
  arq.to_excel("output.xlsx")
  ```

### 2. **sped-extractor** (v1.0.5)
- **Função**: Extrai informações dos manuais SPED (registros, campos, blocos)
- **Uso**: Obter estrutura de campos e registros dos módulos SPED
- **Exemplo**:
  ```python
  from spedextractor import get_fields, get_registers, get_blocks
  efd_fields = get_fields("efd_icms_ipi")
  efd_registers = get_registers("efd_icms_ipi")
  ```

### 3. **python-sped** (v1.1.4)
- **Função**: Biblioteca base para trabalhar com SPED
- **Uso**: Processamento básico de arquivos SPED

### 4. **spedpy** (v1.2.3)
- **Função**: Processamento de arquivos SPED
- **Uso**: Análise e manipulação de dados SPED

---

## ⚠️ Bibliotecas Não Encontradas

As seguintes bibliotecas mencionadas no guia **não estão disponíveis** no PyPI:

### ❌ **pysintegra**
- **Status**: Não encontrado no PyPI
- **Alternativa**: 
  - Usar a estrutura base implementada em `gestao_rural/services/sintegra_service.py`
  - Ou desenvolver gerador customizado baseado no manual oficial do Sintegra

### ❌ **erpbrasil.sped**
- **Status**: Repositório GitHub não encontrado ou não disponível publicamente
- **Alternativa**: 
  - Usar a estrutura base implementada em `gestao_rural/services/sped_service.py`
  - Ou usar as bibliotecas instaladas (`spedpytools`, `sped-extractor`) para análise

---

## 📋 Situação Atual

### ✅ O que temos:
1. **Estrutura base implementada** nos serviços:
   - `gestao_rural/services/sintegra_service.py` - Geração de arquivos Sintegra
   - `gestao_rural/services/sped_service.py` - Geração de arquivos SPED Fiscal

2. **Bibliotecas para análise**:
   - `spedpytools` - Para ler e analisar arquivos SPED existentes
   - `sped-extractor` - Para obter estrutura dos manuais SPED

### ⚠️ O que falta:
1. **Bibliotecas especializadas para geração**:
   - As bibliotecas `pysintegra` e `erpbrasil.sped` não estão disponíveis
   - A estrutura base implementada precisa ser ajustada para produção

2. **Validação e testes**:
   - Arquivos gerados precisam ser validados com ferramentas oficiais
   - Consultar contador/tributarista para validação

---

## 🚀 Próximos Passos Recomendados

### Opção 1: Usar Estrutura Base (Atual)
- ✅ Já implementada e funcional
- ⚠️ Requer ajustes para cálculos fiscais reais
- ⚠️ Requer validação com ferramentas oficiais

### Opção 2: Integração com APIs de Terceiros
- **Focus NFe**: API completa para documentos fiscais
- **NFe.io**: API para NF-e e outros documentos
- **Vantagens**: Validação automática, layouts atualizados
- **Desvantagem**: Custo mensal

### Opção 3: Desenvolvimento Customizado
- Desenvolver geradores baseados nos manuais oficiais
- Manter atualizações conforme mudanças regulatórias
- **Vantagem**: Controle total
- **Desvantagem**: Requer manutenção constante

---

## 📚 Recursos Úteis

### Documentação Oficial
- [Manual Sintegra](http://www.sintegra.gov.br/)
- [SPED - Receita Federal](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/sped)
- [Guia Prático EFD ICMS/IPI](https://www.gov.br/receitafederal/pt-br/assuntos/orientacao-tributaria/sped)

### Bibliotecas Instaladas
- [spedpytools no PyPI](https://pypi.org/project/spedpytools/)
- [sped-extractor no PyPI](https://pypi.org/project/sped-extractor/)

### APIs de Terceiros
- [Focus NFe](https://doc.focusnfe.com.br/)
- [NFe.io](https://nfe.io/)

---

## 💡 Recomendação

Para uso em **produção**, recomenda-se:

1. **Testar a estrutura base** implementada com dados reais
2. **Validar arquivos gerados** com ferramentas oficiais
3. **Consultar contador/tributarista** para validação fiscal
4. **Considerar integração com API de terceiros** se necessário validação automática e layouts sempre atualizados

A estrutura base implementada é um bom ponto de partida e pode ser ajustada conforme necessário.

---

**Data da instalação**: 2025-01-XX  
**Status**: Bibliotecas de análise instaladas - Estrutura base pronta para ajustes

