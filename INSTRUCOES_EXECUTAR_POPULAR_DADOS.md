# 🚀 Como Executar o Comando para Popular Dados

## ⚡ Método Rápido (Recomendado)

### **Para Popular TODAS as Fazendas:**

1. **Clique duas vezes** no arquivo:
   ```
   POPULAR_DADOS_2025.bat
   ```

2. Aguarde o processo concluir (pode levar alguns minutos)

3. Recarregue a página do dashboard no navegador

---

### **Para Popular APENAS a Fazenda Monpec 2 (ID 2):**

1. **Clique duas vezes** no arquivo:
   ```
   POPULAR_DADOS_FAZENDA_2.bat
   ```

2. Aguarde o processo concluir

3. Recarregue a página do dashboard no navegador

---

## 🔧 Método Manual (Terminal)

### **Opção 1: Via Terminal/PowerShell**

```bash
# Navegar até a pasta do projeto
cd C:\Monpec_projetista

# Executar para TODAS as fazendas
python manage.py popular_todos_modulos_todas_fazendas

# OU executar para uma fazenda específica (ID 2)
python manage.py popular_todos_modulos_todas_fazendas --propriedade-id 2
```

### **Opção 2: Se Python não estiver no PATH**

```bash
# Se tiver Python local em python311\
python311\python.exe manage.py popular_todos_modulos_todas_fazendas --propriedade-id 2

# OU se tiver em python\
python\python.exe manage.py popular_todos_modulos_todas_fazendas --propriedade-id 2

# OU usar py launcher
py manage.py popular_todos_modulos_todas_fazendas --propriedade-id 2
```

---

## 📊 O que será criado:

- ✅ **Inventário inicial** em janeiro 2025 (muitos animais)
- ✅ **Movimentações mensais** (vendas, nascimentos, compras)
- ✅ **Lançamentos financeiros** mensais (12 meses)
- ✅ **Abastecimentos** mensais (12 registros)
- ✅ **Folhas de pagamento** mensais (12 registros)
- ✅ **Compras** mensais (12 ordens)
- ✅ **IATFs** e eventos de reprodução
- ✅ **Animais individuais** rastreados (muitos)

---

## ⚠️ Importante:

1. **O processo pode levar alguns minutos** dependendo da quantidade de dados
2. **Recarregue a página** do dashboard após a execução
3. **Se der erro**, verifique se o servidor Django está rodando
4. **Os dados são criados desde janeiro 2025** até dezembro 2025

---

## 🔍 Verificar se funcionou:

Após executar, o dashboard deve mostrar:
- ✅ Muitos animais no inventário (não zero)
- ✅ Valores financeiros (não R$ 0,00)
- ✅ Touros cadastrados
- ✅ Funcionários ativos
- ✅ Movimentações registradas

---

**Última atualização:** Novembro 2025








