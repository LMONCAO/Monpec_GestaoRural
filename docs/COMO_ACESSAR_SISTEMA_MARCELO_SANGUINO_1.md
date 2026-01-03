# COMO ACESSAR O SISTEMA MARCELO SANGUINO

## 🚀 ACESSO RÁPIDO

### 1. Iniciar o Sistema

Execute um dos seguintes arquivos:

**Opção 1 - Windows (Recomendado):**
```
MONPEC DESENVOLVIMENTO.bat
```

**Opção 2 - PowerShell:**
```
INICIAR_SISTEMA_MARCELO_SANGUINO.bat
```

### 2. Acessar no Navegador

Após iniciar o sistema, acesse:

```
http://localhost:8000
```

## 📋 MÓDULOS DISPONÍVEIS

### Dashboard Consolidado (Principal)
```
http://localhost:8000/relatorios-consolidados/
```

**Funcionalidades:**
- Selecionar propriedades (uma ou todas)
- Filtrar por ano
- Ver resumo consolidado:
  - Rebanho (total de cabeças e valor)
  - Bens imobilizados
  - Receitas do ano
  - Saldo líquido

### Relatórios Específicos

1. **Relatório de Rebanho:**
   ```
   http://localhost:8000/relatorios-consolidados/rebanho/
   ```

2. **Relatório de Bens:**
   ```
   http://localhost:8000/relatorios-consolidados/bens/
   ```

3. **DRE Consolidado:**
   ```
   http://localhost:8000/relatorios-consolidados/dre/
   ```

4. **Fluxo de Caixa:**
   ```
   http://localhost:8000/relatorios-consolidados/fluxo-caixa/
   ```

5. **Relatório Completo para Empréstimo:**
   ```
   http://localhost:8000/relatorios-consolidados/completo-emprestimo/
   ```

### Justificativa de Endividamento

**Página Principal:**
```
http://localhost:8000/justificativa-endividamento/
```

**Relatório Completo:**
```
http://localhost:8000/justificativa-endividamento/relatorio-completo/
```

## 🔐 LOGIN

**Usuário padrão:**
- Username: `admin`
- Senha: (a senha configurada no sistema)

Se não conseguir fazer login, execute:
```
python alterar_senha_admin.py
```

## 📊 FLUXO DE TRABALHO RECOMENDADO

### Para Comprovação de Empréstimo:

1. **Acesse o Dashboard Consolidado:**
   - `/relatorios-consolidados/`
   - Selecione todas as propriedades
   - Escolha o ano (ex: 2024)

2. **Gere o Relatório Completo:**
   - Clique em "Gerar Relatório Completo para Empréstimo"
   - Inclui: Rebanho + Bens + DRE + Fluxo de Caixa

3. **Gere a Justificativa de Endividamento:**
   - Acesse `/justificativa-endividamento/`
   - Importe o SCR do Banco Central (PDF)
   - Gere o relatório completo de justificativa

### Para Análise Financeira:

1. Acesse o Dashboard Consolidado
2. Visualize os cards de resumo
3. Acesse os relatórios específicos conforme necessário
4. Exporte ou imprima os relatórios

## 🛠️ TROUBLESHOOTING

### Sistema não inicia:
1. Verifique se o Python está instalado
2. Verifique se as dependências estão instaladas: `pip install -r requirements.txt`
3. Execute as migrações: `python manage.py migrate`

### Erro de login:
1. Execute: `python alterar_senha_admin.py`
2. Ou crie novo usuário: `python criar_superusuario.py`

### Dados não aparecem:
1. Verifique se há dados cadastrados no sistema
2. Verifique o filtro de ano selecionado
3. Verifique se as propriedades estão selecionadas

## 📞 SUPORTE

Para mais informações, consulte:
- `RESUMO_SISTEMA_MARCELO_SANGUINO.md`
- `DOCUMENTACAO_JUSTIFICATIVA_ENDIVIDAMENTO.md`
- `PLANO_SISTEMA_MARCELO_SANGUINO.md`



























