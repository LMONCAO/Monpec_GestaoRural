# 🚀 Como Acessar a Versão V3 Corretamente

## ⚠️ IMPORTANTE: Não abra o arquivo HTML diretamente!

**ERRADO:** `file:///C:/Users/joaoz/Documents/GitHub/Monpec_GestaoRural/templates/gestao_rural/curral_dashboard_v3.html`

**CORRETO:** Acesse via servidor Django

## ✅ Forma Correta de Acessar

### 1. Certifique-se de que o servidor está rodando:
```powershell
python manage.py runserver 0.0.0.0:8000
```

### 2. Acesse no navegador usando uma destas URLs:

**Para a propriedade ID 2:**
```
http://localhost:8000/propriedade/2/curral/v3/
```

**Para a propriedade ID 1:**
```
http://localhost:8000/propriedade/1/curral/v3/
```

### 3. Ou use o redirecionamento automático:
```
http://localhost:8000/propriedade/2/curral/painel/
```
(Será redirecionado automaticamente para `/curral/v3/`)

## 🔍 Por que não funciona abrir o arquivo diretamente?

- O arquivo HTML contém código Django (templates, variáveis `{{ }}`, tags `{% %}`)
- Esses códigos precisam ser processados pelo Django
- O servidor Django processa os templates e retorna HTML completo
- Abrir diretamente mostra o código bruto, não a página renderizada

## 📝 Passos para Acessar Corretamente:

1. **Feche todas as abas** que estão abrindo o arquivo diretamente
2. **Abra uma nova aba** no navegador
3. **Digite na barra de endereço:**
   ```
   http://localhost:8000/propriedade/2/curral/v3/
   ```
4. **Pressione Enter**

## 🎯 Verificação:

Se estiver funcionando corretamente, você verá:
- A URL no navegador será: `http://localhost:8000/propriedade/2/curral/v3/`
- A página será renderizada com todos os dados dinâmicos
- Os botões e formulários funcionarão corretamente
- Não haverá código Django visível (como `{{ sessao_ativa.nome }}`)

## 🛠️ Se o servidor não estiver rodando:

Execute no PowerShell:
```powershell
.\rodar_localhost.ps1
```

Ou manualmente:
```powershell
python manage.py runserver 0.0.0.0:8000
```

