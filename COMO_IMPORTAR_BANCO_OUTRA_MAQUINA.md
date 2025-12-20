# Como Importar Banco de Dados de Outra Máquina

Este guia explica como importar o banco de dados da outra máquina para esta.

## 📋 Pré-requisitos

- Acesso ao arquivo `db.sqlite3` da outra máquina
- O arquivo deve estar completo e funcional

## 🚀 Método 1: Usando o Script Automático (Recomendado)

### Windows

1. Execute o script:
   ```batch
   IMPORTAR_BANCO_OUTRA_MAQUINA.bat
   ```

2. Escolha uma opção:
   - **Opção 1**: Copie o arquivo `db.sqlite3` da outra máquina para esta pasta e pressione qualquer tecla
   - **Opção 2**: Informe o caminho completo do arquivo

3. O script fará automaticamente:
   - Backup do banco atual
   - Cópia do novo banco
   - Verificação do banco
   - Aplicação de migrações

## 📁 Método 2: Cópia Manual

### Passo a Passo

1. **Localizar o banco na outra máquina:**
   - O arquivo está em: `[pasta_do_projeto]/db.sqlite3`

2. **Fazer backup do banco atual (IMPORTANTE!):**
   ```batch
   copy db.sqlite3 db.sqlite3.backup
   ```

3. **Copiar o banco da outra máquina:**
   - Via USB, rede, ou qualquer método de transferência
   - Copie o arquivo `db.sqlite3` da outra máquina
   - Cole na raiz deste projeto (substituindo o arquivo atual)

4. **Aplicar migrações:**
   ```batch
   python manage.py migrate
   ```

5. **Verificar o banco:**
   ```batch
   python verificar_banco_correto.py
   ```

## 🔄 Método 3: Via Rede (Se as máquinas estão na mesma rede)

### Na Máquina de Origem

1. Compartilhe a pasta do projeto ou o arquivo `db.sqlite3`

### Na Máquina Destino

1. Acesse o arquivo compartilhado
2. Copie o `db.sqlite3` para esta pasta
3. Execute as migrações:
   ```batch
   python manage.py migrate
   ```

## 📦 Método 4: Via Exportação/Importação JSON

### Na Máquina de Origem

1. Exporte os dados:
   ```batch
   python manage.py dumpdata --indent 2 --output dados_exportados.json
   ```

2. Copie o arquivo `dados_exportados.json` para esta máquina

### Na Máquina Destino

1. Importe os dados:
   ```batch
   python manage.py loaddata dados_exportados.json
   ```

## ✅ Verificação Após Importação

Após importar, verifique se os dados estão corretos:

```batch
python verificar_banco_correto.py
```

Este script verifica:
- Se o produtor Marcelo Sanguino existe
- Se a Fazenda Canta Galo existe
- Se há dados no banco

## 🐛 Solução de Problemas

### Erro: Banco corrompido

**Solução:**
- Verifique se o arquivo foi copiado completamente
- Tente copiar novamente
- Verifique o tamanho do arquivo (deve ser similar ao original)

### Erro: Migrações falhando

**Solução:**
```batch
python manage.py migrate --run-syncdb
```

### Erro: Dados não aparecem

**Solução:**
1. Verifique se o banco foi copiado corretamente
2. Verifique se as migrações foram aplicadas
3. Limpe o cache do navegador
4. Reinicie o servidor

## 📝 Notas Importantes

1. **Sempre faça backup** do banco atual antes de importar
2. **Pare o servidor** antes de copiar o banco
3. **Aplique as migrações** após copiar o banco
4. **Verifique os dados** após a importação

## 🔐 Segurança

- Não compartilhe o banco de dados em locais públicos
- Use métodos seguros de transferência
- Mantenha backups regulares



