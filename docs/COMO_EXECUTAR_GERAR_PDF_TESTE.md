# Como Executar o Script gerar_pdf_teste_realista_bnd_sisbov.py

## 🚀 Passo a Passo Rápido

### 1. Identificar o ID da Propriedade

**Opção A - Via Django Shell (Recomendado):**

```bash
python manage.py shell
```

Depois execute no shell:
```python
from gestao_rural.models import Propriedade
for p in Propriedade.objects.all():
    print(f"ID: {p.id} - {p.nome_propriedade} - Produtor: {p.produtor.nome if p.produtor else 'N/A'}")
```

**Opção B - Via Interface Web:**
- Acesse o sistema no navegador
- Vá até a propriedade desejada
- O ID estará na URL: `http://localhost:8000/propriedade/1/...` (onde `1` é o ID)

### 2. Executar o Script

**Comando básico:**
```bash
python gerar_pdf_teste_realista_bnd_sisbov.py <propriedade_id>
```

**Exemplos práticos:**

```bash
# Usando ID 1 (gerará teste_realista_bnd_sisbov.pdf)
python gerar_pdf_teste_realista_bnd_sisbov.py 1

# Usando ID 5 com nome personalizado
python gerar_pdf_teste_realista_bnd_sisbov.py 5 meu_teste_fazenda.pdf

# Usando caminho completo do Python (se necessário)
python311\python.exe gerar_pdf_teste_realista_bnd_sisbov.py 1
```

### 3. Verificar os Arquivos Gerados

Após executar, você terá:

1. **PDF de teste**: `teste_realista_bnd_sisbov.pdf` (ou nome personalizado)
   - Contém os animais com divergências intencionais
   - Pronto para importação

2. **Relatório de divergências**: `teste_realista_bnd_sisbov_divergencias.txt`
   - Lista todas as divergências criadas
   - Útil para validar os resultados

## 📋 Exemplo Completo

```bash
# 1. Abrir terminal/PowerShell na pasta do projeto
cd c:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural

# 2. Verificar propriedades disponíveis
python manage.py shell
# (executar código Python acima para listar)

# 3. Gerar PDF (exemplo com ID 1)
python gerar_pdf_teste_realista_bnd_sisbov.py 1

# 4. Saída esperada:
# [INFO] Django configurado com: sistema_rural.settings
# [INFO] Propriedade: Fazenda Teste
# [INFO] Total de animais encontrados: 100
# [INFO] Distribuicao de divergencias:
#   - Animais corretos: 94 (94%)
#   - Com dados faltantes: 5 (5%)
#   - Nao conformes: 1 (1%)
# [OK] PDF de teste realista criado: teste_realista_bnd_sisbov.pdf
#    Total de animais no PDF: 95
#    Animais corretos: 94
#    Animais com dados faltantes: 5
#    Animais nao conformes: 1
#    Animais no sistema mas NAO no PDF: 1
#    Animais so no PDF (fakes): 1
#    Relatorio de divergencias salvo: teste_realista_bnd_sisbov_divergencias.txt
```

## 🔧 Solução de Problemas

### Erro: "Propriedade não encontrada"
```bash
# Verifique o ID correto
python manage.py shell
# from gestao_rural.models import Propriedade
# Propriedade.objects.values_list('id', 'nome_propriedade')
```

### Erro: "Nenhum animal ativo encontrado"
- A propriedade precisa ter animais com `status='ATIVO'`
- Cadastre alguns animais antes de gerar o PDF

### Erro: "Django não configurado"
- O script tenta diferentes configurações automaticamente
- Se falhar, verifique qual `settings.py` está sendo usado
- Pode precisar ajustar o caminho do `DJANGO_SETTINGS_MODULE`

### Erro: "ModuleNotFoundError: No module named 'reportlab'"
```bash
# Instalar dependência
pip install reportlab
# ou
python311\python.exe -m pip install reportlab
```

## 📊 O que o Script Faz

1. **Busca animais reais** da propriedade especificada
2. **Calcula divergências**:
   - 94% corretos
   - 5% com dados faltantes
   - 1% não conformes
3. **Gera PDF** com estrutura BND SISBOV
4. **Cria relatório** detalhado das divergências

## ✅ Checklist de Validação

Após gerar o PDF, verifique:

- [ ] PDF foi criado com sucesso
- [ ] Relatório de divergências foi gerado
- [ ] Total de animais no PDF está correto
- [ ] Dados da propriedade estão idênticos ao sistema
- [ ] PDF pode ser aberto e visualizado
- [ ] Estrutura do PDF está correta (tabela, cabeçalho, etc.)

## 🎯 Próximos Passos

Após gerar o PDF:

1. **Importar no sistema**:
   - Acesse: Pecuária → Rastreabilidade → Importar BND/SISBOV
   - Faça upload do PDF gerado
   - Verifique os resultados

2. **Validar divergências**:
   - Compare o relatório de divergências com os resultados da importação
   - Verifique se animais com dados faltantes foram tratados corretamente
   - Confirme se divergências foram identificadas

## 💡 Dicas

- **Use propriedades de teste** com poucos animais primeiro
- **Revise o relatório** antes de importar para saber o que esperar
- **Teste diferentes cenários** variando a propriedade
- **Mantenha o relatório** para referência futura

---

**Comando Rápido:**
```bash
python gerar_pdf_teste_realista_bnd_sisbov.py <ID_PROPRIEDADE>
```


