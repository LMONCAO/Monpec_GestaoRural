# Como Testar a Refatoração - Curral Dashboard V2

## ✅ Status da Refatoração

### Includes Criados:
1. ✅ `curral/includes/header.html` - Cabeçalho completo
2. ✅ `curral/includes/scanner.html` - Seção de identificação do brinco
3. ✅ `curral/includes/pesagem.html` - Seção de pesagem
4. ✅ `curral/includes/estatisticas.html` - Cards de estatísticas e manejos
5. ✅ `curral/includes/tabela_animais.html` - Tabela de animais registrados
6. ✅ `curral/includes/modals.html` - Modais principais (confirmação, edição pesagem, toast, loading)

### Template Refatorado:
- ✅ `curral_dashboard_v2_refatorado.html` - Template principal que usa includes

### Template Original:
- ✅ `curral_dashboard_v2.html` - **Ainda está intacto e funcionando normalmente**

---

## 📝 Nota Importante

O template refatorado (`curral_dashboard_v2_refatorado.html`) foi criado, mas **ainda não está completo**. Ele precisa:

1. **CSS completo** - O CSS ainda está no template original (4.800+ linhas)
2. **JavaScript completo** - Os scripts ainda estão no template original (12.000+ linhas)

Por enquanto, o template refatorado serve como **prova de conceito** de como ficará a estrutura.

---

## 🧪 Como Testar os Includes

### Opção 1: Testar Individualmente (Recomendado)

Você pode incluir os includes no template original para testar gradualmente:

1. Abra `templates/gestao_rural/curral_dashboard_v2.html`
2. Localize a seção do Header (linha ~4858)
3. Substitua temporariamente por:
   ```django
   {% include "gestao_rural/curral/includes/header.html" %}
   ```
4. Teste se funciona
5. Reverta se houver problemas

### Opção 2: Testar o Template Refatorado

**ATENÇÃO**: O template refatorado ainda não está completo. Para testá-lo:

1. Copie o bloco `{% block extra_css %}` completo do template original
2. Copie o bloco `{% block extra_js %}` completo do template original
3. Cole no template refatorado
4. Modifique a view temporariamente para usar o template refatorado:
   ```python
   # Em gestao_rural/views_curral.py, linha ~566
   return render(request, 'gestao_rural/curral_dashboard_v2_refatorado.html', context)
   ```
5. Teste e reverta se necessário

---

## ✅ O Que Já Funciona

Os includes criados são **funcionais e prontos para uso**, mas dependem:
- Do CSS do template original (ainda não extraído)
- Do JavaScript do template original (ainda não extraído)
- Do contexto Django (variáveis como `propriedade`, `sessao_ativa`, etc.)

---

## 🔄 Próximos Passos

### Fase 1 Continuação:
1. ⏳ Extrair CSS completo para `includes/css.html`
2. ⏳ Testar template refatorado completo
3. ⏳ Substituir template original gradualmente

### Fase 2:
- Extrair JavaScript para arquivos externos
- Organizar em módulos

---

## 🚨 Se Algo Der Errado

**O template original está intacto e funcionando normalmente!**

Para restaurar completamente:
```powershell
.\backup_curral_refactor\RESTAURAR_BACKUP.ps1
```

Ou manualmente:
```powershell
Copy-Item -Path "backup_curral_refactor\20251120_132137\curral_dashboard_v2.html" -Destination "templates\gestao_rural\curral_dashboard_v2.html" -Force
```

---

**Data da Refatoração**: 2025-11-20
**Status**: ✅ Fase 1 em progresso - 60% completo
