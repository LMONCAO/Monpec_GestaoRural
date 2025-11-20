# 🔧 Instruções para Criar a Tabela do WhatsApp

## ⚠️ Erro Atual

O erro `no such table: gestao_rural_mensagemwhatsapp` ocorre porque a tabela ainda não foi criada no banco de dados.

## ✅ Solução

Execute a migração para criar a tabela:

### **Opção 1: Usando o Script (Windows)**

1. Execute o arquivo: `executar_migracao_whatsapp.bat`
2. Ou no terminal/PowerShell:
   ```bash
   python manage.py migrate gestao_rural 0046_add_whatsapp_mensagens
   ```

### **Opção 2: Migração Completa**

Execute todas as migrações pendentes:
```bash
python manage.py migrate
```

### **Opção 3: Se o Python não estiver no PATH**

Use o caminho completo do Python:
```bash
C:\Monpec_projetista\python311\python.exe manage.py migrate gestao_rural 0046_add_whatsapp_mensagens
```

## 📋 O Que a Migração Faz

A migração `0046_add_whatsapp_mensagens.py` cria a tabela `gestao_rural_mensagemwhatsapp` com os seguintes campos:

- `id` - Chave primária
- `numero_whatsapp` - Número do WhatsApp
- `tipo_mensagem` - Tipo (audio, texto)
- `conteudo_audio_url` - URL do áudio
- `conteudo_texto` - Texto transcrito
- `dados_extraidos` - Dados extraídos (JSON)
- `status` - Status do processamento
- `propriedade` - Propriedade relacionada
- `erro_processamento` - Erros (se houver)
- `observacoes` - Observações
- `data_recebimento` - Data de recebimento
- `data_processamento` - Data de processamento

## ✅ Após Executar

Depois de executar a migração:

1. Recarregue a página do sistema
2. Acesse: `/propriedade/{id}/whatsapp/mensagens/`
3. A página deve carregar sem erros

## 🔍 Verificar se Funcionou

Você pode verificar se a tabela foi criada:

```bash
python manage.py dbshell
```

Depois execute:
```sql
.tables
```

Você deve ver `gestao_rural_mensagemwhatsapp` na lista.

---

**Nota**: Se ainda houver erro, verifique se o servidor Django está rodando e se o banco de dados está acessível.





