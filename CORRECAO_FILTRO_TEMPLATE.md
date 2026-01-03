# ✅ Correção do Filtro de Template

## 🔍 Problema Encontrado

O template `dashboard_navegacao.html` estava usando o filtro `formatar_numero` que não estava registrado nos template tags.

**Erro:**
```
TemplateSyntaxError: Invalid filter: 'formatar_numero'
```

## ✅ Solução Aplicada

Adicionei o filtro `formatar_numero` como alias para `numero_br` no arquivo `gestao_rural/templatetags/formatacao_br.py`:

```python
@register.filter(name='formatar_numero')
def formatar_numero(valor, casas_decimais=0):
    """
    Alias para numero_br - Formata número no padrão brasileiro: 1.000 ou 1.152,38
    Uso: {{ valor|formatar_numero }} ou {{ valor|formatar_numero:2 }}
    """
    return numero_br(valor, casas_decimais)
```

## 📋 Arquivos Modificados

- ✅ `gestao_rural/templatetags/formatacao_br.py` - Filtro `formatar_numero` adicionado

## 🔄 Próximo Passo

**Fazer novo deploy** para aplicar a correção:

```bash
# 1. Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest .

# 2. Deploy
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec:latest --region us-central1
```

Ou simplesmente atualizar o serviço (se a imagem já foi buildada):

```bash
gcloud run deploy monpec --region us-central1
```

## ✅ Status

- [x] Filtro `formatar_numero` adicionado
- [ ] Novo build feito (em progresso)
- [ ] Novo deploy feito
- [ ] Testar dashboard

