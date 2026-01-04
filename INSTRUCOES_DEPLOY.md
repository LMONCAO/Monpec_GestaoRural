# Instruções para Deploy das Alterações

As alterações para login automático após criar usuário demo foram realizadas com sucesso. Para fazer o deploy, siga os passos abaixo:

## Arquivos Modificados

1. `gestao_rural/views.py` - Adicionado login automático após criar/atualizar usuário demo
2. `templates/site/landing_page.html` - Adicionado `credentials: 'same-origin'` no fetch

## Passos para Deploy

### Opção 1: Via GitHub Actions (Recomendado)

1. **Abra o terminal no diretório do projeto:**
   ```
   cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
   ```

2. **Verifique os arquivos modificados:**
   ```powershell
   git status
   ```

3. **Adicione os arquivos modificados:**
   ```powershell
   git add gestao_rural/views.py templates/site/landing_page.html
   ```

4. **Faça o commit:**
   ```powershell
   git commit -m "Fix: Login automático após criar usuário demo - redireciona para demo_loading"
   ```

5. **Configure o remote (se ainda não estiver configurado):**
   ```powershell
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   ```
   *Substitua SEU_USUARIO e SEU_REPOSITORIO pelos valores corretos*

6. **Faça o push:**
   ```powershell
   git push -u origin master
   ```
   *ou se já tiver configurado:*
   ```powershell
   git push
   ```

7. **Acompanhe o deploy:**
   - Acesse: https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions
   - O GitHub Actions irá fazer o deploy automaticamente para o Google Cloud Run

### Opção 2: Usar o Script PowerShell

Execute o script `FAZER_DEPLOY_ALTERACOES.ps1` que foi criado:

```powershell
.\FAZER_DEPLOY_ALTERACOES.ps1
```

O script irá:
- Verificar se o Git está instalado
- Verificar se há remote configurado
- Adicionar os arquivos modificados
- Fazer commit
- Fazer push para o GitHub

## O que foi alterado?

### 1. Login Automático (`gestao_rural/views.py`)

**Antes:** Após criar o usuário, redirecionava para `/login/?demo=true&email=...`

**Agora:** Faz login automático do usuário e redireciona diretamente para `/demo/loading/`

Mudanças:
- Adicionado `login(request, user)` após criar/atualizar usuário
- Alterado `redirect_url` de `reverse('login') + '?demo=true&...'` para `reverse('demo_loading')`

### 2. Cookies no Fetch (`templates/site/landing_page.html`)

Adicionado `credentials: 'same-origin'` no fetch para garantir que os cookies de sessão sejam mantidos durante a requisição AJAX.

## Resultado Esperado

Após o deploy, quando um usuário criar uma conta demo:
1. ✅ O sistema cria/atualiza o usuário
2. ✅ O sistema faz login automático
3. ✅ O usuário é redirecionado diretamente para `demo_loading`
4. ✅ O usuário não precisa fazer login manual

## Verificação Pós-Deploy

Após o deploy, teste:
1. Acesse a landing page
2. Preencha o formulário de demonstração
3. Verifique se após criar a conta, o usuário é redirecionado diretamente para o sistema demo (sem passar pela página de login)

## Observações

- O deploy via GitHub Actions pode levar alguns minutos
- Verifique os logs em: https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions
- O serviço será atualizado em: https://monpec-29862706245.us-central1.run.app


