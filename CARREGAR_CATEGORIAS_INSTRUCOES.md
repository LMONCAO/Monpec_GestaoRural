# Como Carregar Categorias Padrão - Sistema MonPec

## 📋 **COMANDO PARA CARREGAR CATEGORIAS**

### **Executar o Comando:**
```bash
python manage.py carregar_categorias_completo
```

---

## ✅ **CATEGORIAS QUE SERÃO CARREGADAS**

### **Categorias Indefinidas (Gerais - 3):**
1. **Bezerro(a)** - 0-12 meses, 50kg
2. **Novilho(a)** - 12-24 meses, 250kg
3. **Garrotes** - 24-36 meses, 350kg

### **Categorias Fêmeas (5):**
1. **Bezerra** - 0-6 meses, 50kg
2. **Novilha** - 6-24 meses, 250kg
3. **Novilha Primípara** - 24-36 meses, 350kg
4. **Vaca Primípara** - 36-48 meses, 450kg
5. **Vaca Multípara** - 48+ meses, 500kg

### **Categorias Machos (4):**
1. **Bezerro** - 0-6 meses, 55kg
2. **Novilho** - 6-24 meses, 280kg
3. **Touro** - 36+ meses, 800kg
4. **Boi de Corte** - 24+ meses, 400kg

**Total: 12 categorias padrão**

---

## 🚀 **INSTRUÇÕES PARA CARREGAR**

### **Opção 1: Via Terminal**
```bash
cd C:\Monpec_projetista
python manage.py carregar_categorias_completo
```

### **Opção 2: Via PowerShell**
```powershell
cd C:\Monpec_projetista
python manage.py carregar_categorias_completo
```

---

## 📊 **O QUE O COMANDO FAZ**

### **1. Verifica se categoria já existe:**
- Se não existe: **CRIA**
- Se já existe: **ATUALIZA** com novos dados

### **2. Atualiza informações:**
- Idade mínima e máxima
- Sexo (Macho, Fêmea, Indefinido)
- Raça (padrão: Nelore)
- Peso médio
- Descrição

### **3. Resultado:**
```
✅ Categoria criada: Bezerro(a)
✅ Categoria criada: Novilho(a)
⚠️ Categoria atualizada: Bezerra
...
📊 Resumo: 8 categorias criadas, 4 atualizadas
```

---

## 🎯 **DEPOIS DE CARREGAR**

### **Categorias disponíveis:**
- ✅ Aparecem no cadastro de inventário
- ✅ Disponíveis para projeções
- ✅ Configuradas com pesos e idades padrão

### **Como usar:**
1. Acesse "Cadastrar Inventário"
2. Selecione uma categoria na lista
3. Informe a quantidade
4. O peso e idade já estarão configurados

---

## 🎉 **SISTEMA COMPLETO**

**Após executar o comando:**
- ✅ 12 categorias padrão carregadas
- ✅ Pesos médios configurados
- ✅ Idades configuradas
- ✅ Pronto para usar em inventários e projeções

**Execute o comando agora para carregar as categorias!** 🚀

