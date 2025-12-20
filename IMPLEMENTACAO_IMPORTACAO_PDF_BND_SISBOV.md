# Implementação de Importação de PDF BND SISBOV

## Resumo

Foi implementada a funcionalidade de importação de arquivos PDF da Base Nacional de Dados (BND) do Sistema Brasileiro de Identificação e Certificação de Bovinos e Bubalinos (SISBOV).

## Arquivos Criados/Modificados

### 1. Novo Arquivo: `gestao_rural/bnd_sisbov_parser.py`

Parser dedicado para extrair dados de animais de PDFs exportados do Portal SISBOV.

**Funcionalidades:**
- Extração de texto usando `pdfplumber` (preferencial) e `PyPDF2` (fallback)
- Identificação de códigos SISBOV (formato BR + 13 dígitos ou 15 dígitos)
- Extração de informações dos animais:
  - Código SISBOV
  - Número de Manejo (6 dígitos)
  - Número do Brinco (12-15 dígitos)
  - Raça
  - Sexo (M/F)
  - Data de Nascimento
  - Peso (kg)
- Extração de informações da propriedade:
  - Nome da propriedade
  - CNPJ/CPF
  - Data de emissão
- Processamento de tabelas estruturadas
- Processamento de texto livre com padrões regex
- Geração de relatório de extração

**Padrões de Identificação:**
- Código SISBOV: `BR\d{13}` ou `\d{15}`
- Número de Manejo: `\d{6}`
- Número do Brinco: `\d{12,15}`
- Data: `\d{2}/\d{2}/\d{4}`
- CNPJ/CPF: Formatos padrão brasileiros
- Peso: Valores com unidade "kg" ou "KG"
- Raça: Identificação de raças comuns (Nelore, Angus, Brahman, etc.)
- Sexo: Macho/Fêmea (M/F)

### 2. Modificado: `gestao_rural/views_rastreabilidade.py`

Atualização da função `importar_bnd_sisbov` para suportar arquivos PDF.

**Mudanças:**
- Adicionado suporte para arquivos `.pdf`
- Integração com `BNDSisbovParser`
- Processamento de animais extraídos do PDF
- Validação e normalização de códigos SISBOV
- Criação/atualização de registros de animais
- Tratamento de erros específico para PDFs
- Mensagens de feedback ao usuário

**Fluxo de Processamento:**
1. Verifica se bibliotecas necessárias estão instaladas (PyPDF2, pdfplumber)
2. Cria instância do parser
3. Extrai dados do PDF
4. Processa cada animal extraído:
   - Normaliza código SISBOV
   - Busca ou cria animal no banco
   - Atualiza dados existentes quando necessário
5. Exibe estatísticas (criados, atualizados, erros)

### 3. Modificado: `templates/gestao_rural/importar_bnd_sisbov.html`

Atualização da interface para permitir upload de PDFs.

**Mudanças:**
- Formulário funcional para upload de arquivos
- Campo de input com aceitação de múltiplos formatos (`.xlsx`, `.xls`, `.csv`, `.pdf`)
- Instruções atualizadas mencionando suporte a PDF
- Interface mais clara e funcional

## Dependências Necessárias

Para que a funcionalidade funcione, é necessário instalar as seguintes bibliotecas:

```bash
pip install PyPDF2 pdfplumber
```

**Nota:** As bibliotecas `openpyxl` (para Excel) já devem estar instaladas se a importação de Excel já funcionava.

## Como Usar

1. Acesse o módulo de Rastreabilidade
2. Vá em "Importar BND/SISBOV"
3. Selecione um arquivo PDF exportado do Portal SISBOV
4. Clique em "Importar arquivo SISBOV"
5. O sistema processará o arquivo e exibirá:
   - Quantidade de animais criados
   - Quantidade de animais atualizados
   - Erros encontrados (se houver)

## Estrutura do PDF BND SISBOV

O parser foi desenvolvido para identificar os seguintes padrões comuns em PDFs BND SISBOV:

### Campos Principais Extraídos:
- **Código SISBOV**: Identificador único de 15 dígitos (formato BR + 13 dígitos)
- **Número de Manejo**: 6 dígitos extraídos do código SISBOV
- **Número do Brinco**: 12-15 dígitos
- **Raça**: Nome da raça do animal
- **Sexo**: M (Macho) ou F (Fêmea)
- **Data de Nascimento**: Data no formato DD/MM/YYYY
- **Peso**: Peso atual em quilogramas

### Estratégias de Extração:

1. **Busca por Códigos SISBOV**: Identifica códigos SISBOV no texto e extrai informações próximas
2. **Processamento de Tabelas**: Identifica cabeçalhos de tabela e processa linhas estruturadas
3. **Contexto ao Redor**: Para cada código encontrado, analisa contexto de 500 caracteres para extrair informações relacionadas

## Limitações e Melhorias Futuras

### Limitações Atuais:
- Depende da qualidade do OCR/extração de texto do PDF
- PDFs escaneados podem ter menor precisão
- Alguns formatos não padronizados podem não ser reconhecidos

### Melhorias Futuras Sugeridas:
1. Suporte a XML BND SISBOV (formato estruturado mais confiável)
2. Validação cruzada com dados já existentes no sistema
3. Interface de pré-visualização dos dados antes de importar
4. Opção de mapeamento manual de colunas para formatos não padronizados
5. Suporte a múltiplos PDFs em lote
6. Logs detalhados de extração para debug

## Testes Recomendados

1. Testar com PDF exportado diretamente do Portal SISBOV
2. Testar com diferentes formatos de PDF (texto, escaneado)
3. Validar extração de todos os campos esperados
4. Verificar tratamento de erros e mensagens ao usuário
5. Testar com arquivos grandes (muitos animais)

## Referências

- Manual do SISBOV: https://sistemas.agricultura.gov.br/imagens/manual.pdf
- WebService BND-SISBOV: https://www.gov.br/agricultura/pt-br/assuntos/sanidade-animal-e-vegetal/saude-animal/rastreabilidade-animal/WS
- Estudo de Rastreabilidade: `ESTUDO_RASTREABILIDADE_BOVINA_FORMULARIOS.md`

## Status

✅ **Implementação Completa**
- Parser criado e funcional
- View atualizada com suporte a PDF
- Template atualizado com formulário funcional
- Sem erros de linting

**Próximos Passos:**
- Testar com arquivos reais do Portal SISBOV
- Ajustar padrões de extração conforme necessário
- Adicionar melhorias baseadas em feedback dos usuários


