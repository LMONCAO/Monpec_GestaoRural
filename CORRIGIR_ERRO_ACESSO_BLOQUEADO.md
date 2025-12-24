# 🔧 Corrigir Erro: "Acesso bloqueado"

## ❌ Erro Atual:

O Google está bloqueando porque o app está em "fase de testes" e seu email não está como testador aprovado.

## ✅ Solução:

Você precisa adicionar seu email como "Usuário de teste" no Google Cloud Console.

### Passo a Passo:

1. **Acesse o Google Cloud Console:**
   - https://console.cloud.google.com/
   - Certifique-se que o projeto "monpec-sistema-rural" está selecionado

2. **Vá para OAuth Consent Screen:**
   - Menu lateral: "APIs e serviços" > "Tela de consentimento OAuth"
   - (Ou acesse diretamente: https://console.cloud.google.com/apis/credentials/consent)

3. **Adicione seu email como Test User:**
   - Role a página até a seção **"Usuários de teste"** (Test users)
   - Clique no botão **"+ ADICIONAR USUÁRIOS"** (ou "ADD USERS")
   - Digite: `l.moncaosilva@gmail.com`
   - Clique em **"ADICIONAR"** (ou "ADD")
   - Clique em **"SALVAR"** (ou "SAVE")

4. **Execute novamente o script:**
   ```bash
   python autenticar_gmail.py
   ```

## 📋 Verificação:

Após adicionar seu email como test user, você deve ver:
- Seu email listado na seção "Usuários de teste"
- Status do app: "Em teste" (Testing)

## ⚠️ Importante:

- O app precisa estar em modo "Testing" para funcionar sem verificação completa
- Apenas emails adicionados como "Test users" podem usar o app
- Se quiser usar em produção depois, precisará submeter para verificação do Google

---

## 🚀 Depois de adicionar:

Execute novamente:
```bash
python autenticar_gmail.py
```

Agora deve funcionar!
















