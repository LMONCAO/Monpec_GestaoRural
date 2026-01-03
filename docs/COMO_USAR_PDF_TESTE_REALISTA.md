# Como Usar o PDF de Teste Realista BND SISBOV

## 📋 Descrição

Este script gera um PDF de teste **realista** usando os animais **reais** cadastrados no sistema, introduzindo divergências intencionais para simular cenários reais de importação.

## 🎯 Divergências Introduzidas

### Distribuição:
- **94% dos animais**: Corretos (dados idênticos ao sistema)
- **5% dos animais**: Com dados faltantes (sexo, raça ou data de nascimento não identificados)
- **1% dos animais**: Não conformes
  - Metade: Animais que estão no sistema mas **NÃO** estão no PDF
  - Metade: Animais que estão no PDF mas **NÃO** estão no sistema (fakes)

### Dados da Propriedade:
- **100% idênticos** ao sistema (CNPJ/CPF, nome, etc.) para evitar erros de validação

## 🚀 Como Usar

### 1. Identificar o ID da Propriedade

Primeiro, você precisa saber o ID da propriedade que deseja usar para o teste.

**Opção A - Via Django Shell:**
```bash
python manage.py shell
```

```python
from gestao_rural.models import Propriedade
propriedades = Propriedade.objects.all()
for p in propriedades:
    print(f"ID: {p.id} - {p.nome_propriedade}")
```

**Opção B - Via Interface Web:**
- Acesse o sistema
- Vá até a propriedade desejada
- O ID estará na URL: `/propriedade/<id>/...`

### 2. Gerar o PDF de Teste

```bash
python gerar_pdf_teste_realista_bnd_sisbov.py <propriedade_id>
```

**Exemplo:**
```bash
python gerar_pdf_teste_realista_bnd_sisbov.py 1
```

**Com nome personalizado:**
```bash
python gerar_pdf_teste_realista_bnd_sisbov.py 1 meu_teste.pdf
```

### 3. Arquivos Gerados

O script gera dois arquivos:

1. **PDF de teste**: `teste_realista_bnd_sisbov.pdf` (ou nome personalizado)
   - Contém os animais com as divergências intencionais
   - Pronto para importação no sistema

2. **Relatório de divergências**: `teste_realista_bnd_sisbov_divergencias.txt`
   - Lista todas as divergências introduzidas
   - Útil para validar se o parser identificou corretamente

## 📊 O que Testar

Após importar o PDF, verifique:

### ✅ Animais Corretos (94%)
- Devem ser importados/atualizados sem problemas
- Dados devem estar idênticos ao sistema

### ⚠️ Animais com Dados Faltantes (5%)
- Devem ser importados mesmo com dados faltantes
- Campos faltantes devem permanecer vazios ou usar valores padrão
- Sistema deve lidar graciosamente com dados incompletos

### ❌ Animais Não Conformes (1%)

**Animais no sistema mas NÃO no PDF:**
- Devem permanecer no sistema (não devem ser removidos)
- Sistema deve identificar que estão faltando no PDF

**Animais só no PDF (fakes):**
- Devem ser criados como novos animais
- Ou devem ser identificados como divergências (dependendo da lógica)

## 🔍 Validação do Teste

### Checklist:

- [ ] PDF foi gerado com sucesso
- [ ] Relatório de divergências foi criado
- [ ] Total de animais no PDF corresponde ao esperado
- [ ] Dados da propriedade estão corretos
- [ ] Importação no sistema funcionou
- [ ] Animais corretos foram atualizados
- [ ] Animais com dados faltantes foram tratados corretamente
- [ ] Divergências foram identificadas (se aplicável)

## 📝 Exemplo de Saída

```
[INFO] Propriedade: Fazenda Teste
[INFO] Total de animais encontrados: 100
[INFO] Distribuicao de divergencias:
  - Animais corretos: 94 (94%)
  - Com dados faltantes: 5 (5%)
  - Nao conformes: 1 (1%)

[OK] PDF de teste realista criado: teste_realista_bnd_sisbov.pdf
   Total de animais no PDF: 95
   Animais corretos: 94
   Animais com dados faltantes: 5
   Animais nao conformes: 1
   Animais no sistema mas NAO no PDF: 1
   Animais so no PDF (fakes): 1
   Relatorio de divergencias salvo: teste_realista_bnd_sisbov_divergencias.txt
```

## 🐛 Solução de Problemas

### Erro: "Propriedade não encontrada"
- Verifique se o ID da propriedade está correto
- Use o Django shell para listar propriedades disponíveis

### Erro: "Nenhum animal ativo encontrado"
- A propriedade precisa ter animais com status 'ATIVO'
- Cadastre alguns animais antes de gerar o PDF

### Erro: "Django não configurado"
- Verifique se o settings.py está correto
- O script tenta diferentes configurações automaticamente

## 💡 Dicas

1. **Use uma propriedade de teste** com poucos animais primeiro
2. **Revise o relatório de divergências** antes de importar
3. **Compare os resultados** após a importação com o relatório
4. **Teste diferentes cenários** variando a quantidade de animais

## 📚 Arquivos Relacionados

- `gerar_pdf_teste_realista_bnd_sisbov.py` - Script principal
- `gestao_rural/bnd_sisbov_parser.py` - Parser que processará o PDF
- `gestao_rural/views_rastreabilidade.py` - View de importação
- `COMO_TESTAR_IMPORTACAO_PDF_BND_SISBOV.md` - Guia geral de testes

---

**Status**: ✅ Pronto para uso
**Data**: Dezembro 2024


