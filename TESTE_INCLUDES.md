# Guia de Teste dos Includes

## ✅ Includes Criados e Prontos para Teste

### 1. Header (`curral/includes/header.html`)
- **Linhas no original**: ~153 linhas (4853-5006)
- **Status**: ✅ Pronto para teste

### 2. Scanner (`curral/includes/scanner.html`)
- **Linhas no original**: ~70 linhas (5021-5091)
- **Status**: ✅ Pronto para teste

### 3. Pesagem (`curral/includes/pesagem.html`)
- **Linhas no original**: ~109 linhas (5092-5200)
- **Status**: ✅ Pronto para teste

### 4. Estatísticas (`curral/includes/estatisticas.html`)
- **Linhas no original**: ~70 linhas (5202-5271)
- **Status**: ✅ Pronto para teste

### 5. Tabela de Animais (`curral/includes/tabela_animais.html`)
- **Linhas no original**: ~50 linhas (5273-5322)
- **Status**: ✅ Pronto para teste

### 6. Modais (`curral/includes/modals.html`)
- **Linhas no original**: ~160+ linhas (5324+)
- **Status**: ✅ Pronto para teste

---

## 🧪 Como Testar

### Opção 1: Testar Individualmente (Recomendado)

Você pode testar cada include substituindo a seção correspondente no template original:

#### Teste 1: Header

1. Abra `templates/gestao_rural/curral_dashboard_v2.html`
2. Localize a linha 4853 (`<!-- Contador de itens pendentes de sincronização -->`)
3. Substitua até a linha 5006 por:
   ```django
   {% include "gestao_rural/curral/includes/header.html" %}
   ```
4. Salve e teste no navegador
5. Se funcionar, continue; se não, restaure do backup

#### Teste 2: Scanner e Pesagem (dentro do card)

1. No template original, localize linha 5021 (`<div class="col-lg-5 col-md-6">`)
2. Substitua as seções de Scanner (até linha 5091) por:
   ```django
   {% include "gestao_rural/curral/includes/scanner.html" %}
   ```
3. Substitua a seção de Pesagem (linhas 5092-5200) por:
   ```django
   {% include "gestao_rural/curral/includes/pesagem.html" %}
   ```

#### Teste 3: Estatísticas

1. Localize linha 5202 (`<div class="col-lg-4 col-md-12">`)
2. Substitua até linha 5271 por:
   ```django
   {% include "gestao_rural/curral/includes/estatisticas.html" %}
   ```

### Opção 2: Testar Template Refatorado

**⚠️ ATENÇÃO**: O template refatorado ainda precisa do CSS e JavaScript do original.

Para usar o template refatorado completamente:

1. Copie o bloco `{% block extra_css %}` do template original (linhas 6-4848)
2. Copie o bloco `{% block extra_js %}` do template original (linhas 6163+)
3. Cole no template refatorado
4. Ou simplesmente inclua o template original dentro do refatorado temporariamente

---

## ✅ Checklist de Teste

- [ ] Header carrega corretamente
- [ ] Menu de Relatórios funciona
- [ ] Status de conexão aparece
- [ ] Sessão ativa mostra dados
- [ ] Scanner identifica animais
- [ ] Pesagem registra peso
- [ ] Estatísticas atualizam
- [ ] Tabela mostra animais
- [ ] Modais abrem e fecham

---

## 🔄 Se Algo Der Errado

**Restaure do backup:**
```powershell
.\backup_curral_refactor\RESTAURAR_BACKUP.ps1
```

Ou manualmente:
```powershell
Copy-Item -Path "backup_curral_refactor\20251120_132137\curral_dashboard_v2.html" -Destination "templates\gestao_rural\curral_dashboard_v2.html" -Force
```
