# Como Testar a Importação de PDF BND SISBOV

## 📄 PDF de Teste Gerado

Foi criado um arquivo PDF de teste: **`teste_bnd_sisbov.pdf`** com 15 animais simulados.

Este PDF contém a estrutura esperada de um arquivo BND SISBOV exportado do Portal SISBOV, incluindo:
- Cabeçalho com informações do sistema
- Dados da propriedade (CNPJ, data de emissão)
- Tabela com animais contendo:
  - Código SISBOV (formato BR + 13 dígitos)
  - Número de Manejo (6 dígitos)
  - Número do Brinco (15 dígitos)
  - Raça
  - Sexo (Macho/Fêmea)
  - Data de Nascimento
  - Peso (kg)

## 🧪 Como Testar

### Opção 1: Testar no Sistema Django (Recomendado)

1. **Instalar dependências** (se ainda não instalou):
   ```bash
   pip install PyPDF2 pdfplumber
   ```

2. **Iniciar o servidor Django**:
   ```bash
   python manage.py runserver
   ```

3. **Acessar o sistema**:
   - Faça login no sistema
   - Navegue até: **Pecuária → Rastreabilidade**
   - Clique em **"Importar BND/SISBOV"**

4. **Fazer upload do PDF**:
   - Clique em "Selecionar arquivo"
   - Escolha o arquivo: `teste_bnd_sisbov.pdf`
   - Clique em **"Importar arquivo SISBOV"**

5. **Verificar resultados**:
   - O sistema deve exibir mensagens de sucesso
   - Verifique quantos animais foram criados/atualizados
   - Acesse a lista de animais individuais para verificar os dados importados

### Opção 2: Gerar Novo PDF de Teste

Se quiser gerar um PDF com mais ou menos animais:

```bash
python gerar_pdf_teste_bnd_sisbov.py [quantidade]
```

Exemplos:
- `python gerar_pdf_teste_bnd_sisbov.py 20` - Gera PDF com 20 animais
- `python gerar_pdf_teste_bnd_sisbov.py 5` - Gera PDF com 5 animais
- `python gerar_pdf_teste_bnd_sisbov.py` - Gera PDF com 10 animais (padrão)

### Opção 3: Testar com PDF Real do Portal SISBOV

1. **Exportar PDF do Portal SISBOV**:
   - Acesse o Portal SISBOV oficial
   - Exporte o inventário de animais em formato PDF
   - Salve o arquivo

2. **Importar no sistema**:
   - Siga os passos da Opção 1
   - Use o PDF real exportado do Portal

## 📊 Estrutura do PDF de Teste

O PDF gerado contém:

### Cabeçalho
- Título: "BASE NACIONAL DE DADOS - SISBOV"
- Subtítulo: "Sistema Brasileiro de Identificação e Certificação de Origem Bovina e Bubalina"

### Dados da Propriedade
- Nome: "Fazenda Teste SISBOV"
- CNPJ/CPF: "12.345.678/0001-90"
- Inscrição Estadual: "123.456.789.012"
- Data de Emissão: Data atual

### Tabela de Animais
Colunas:
1. Código SISBOV
2. Nº Manejo
3. Nº Brinco
4. Raça
5. Sexo
6. Data Nasc.
7. Peso (kg)

## ✅ O que Verificar Após a Importação

1. **Animais Criados**:
   - Verifique se todos os animais do PDF foram importados
   - Confirme que os códigos SISBOV estão corretos

2. **Dados Preenchidos**:
   - Código SISBOV: ✅ Deve estar preenchido
   - Número de Brinco: ✅ Deve estar preenchido
   - Raça: ✅ Deve estar preenchido (se presente no PDF)
   - Sexo: ✅ Deve estar preenchido (se presente no PDF)
   - Data de Nascimento: ✅ Deve estar preenchido (se presente no PDF)
   - Peso: ✅ Deve estar preenchido (se presente no PDF)

3. **Validações**:
   - Códigos SISBOV devem estar no formato correto (BR + 13 dígitos)
   - Números de brinco devem ter 15 dígitos
   - Datas devem estar no formato correto

## 🔧 Solução de Problemas

### Erro: "Bibliotecas necessárias não estão instaladas"
**Solução**: Instale as dependências:
```bash
pip install PyPDF2 pdfplumber
```

### Erro: "Nenhum animal foi encontrado no PDF"
**Possíveis causas**:
- PDF não contém códigos SISBOV no formato esperado
- PDF está corrompido ou em formato não suportado
- PDF é uma imagem escaneada (requer OCR)

**Solução**:
- Verifique se o PDF foi exportado diretamente do Portal SISBOV
- Tente exportar novamente do Portal
- Use PDFs com texto selecionável (não imagens escaneadas)

### Erro: "Código SISBOV não encontrado"
**Solução**:
- Verifique se o PDF contém códigos no formato BR + 13 dígitos
- Confirme que o PDF não está protegido ou criptografado

## 📝 Notas Importantes

1. **PDFs Escaneados**: PDFs que são imagens escaneadas podem ter menor precisão na extração. O parser funciona melhor com PDFs com texto selecionável.

2. **Formatos Suportados**: 
   - ✅ PDF com texto selecionável (melhor resultado)
   - ✅ PDF gerado diretamente do Portal SISBOV
   - ⚠️ PDF escaneado (pode ter menor precisão)

3. **Dados Opcionais**: Nem todos os campos são obrigatórios. O sistema importará o que conseguir extrair do PDF.

## 🎯 Próximos Passos

Após testar com sucesso:

1. **Testar com PDF real** do Portal SISBOV
2. **Ajustar padrões de extração** se necessário (em `bnd_sisbov_parser.py`)
3. **Adicionar suporte a XML** BND SISBOV (formato mais estruturado)
4. **Melhorar tratamento de erros** baseado em feedback

## 📚 Arquivos Relacionados

- `gestao_rural/bnd_sisbov_parser.py` - Parser principal
- `gestao_rural/views_rastreabilidade.py` - View de importação
- `templates/gestao_rural/importar_bnd_sisbov.html` - Interface
- `gerar_pdf_teste_bnd_sisbov.py` - Gerador de PDF de teste
- `teste_bnd_sisbov.pdf` - PDF de teste gerado

---

**Status**: ✅ PDF de teste criado e pronto para uso
**Data**: Dezembro 2024


