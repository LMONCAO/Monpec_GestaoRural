# Cache Local: Busca de Clientes por CPF/CNPJ

## ✅ Funcionalidade Implementada

O sistema agora busca automaticamente **clientes já cadastrados** no banco de dados quando você digita o CPF/CNPJ no formulário. Se encontrar, preenche todos os campos automaticamente!

## 🎯 Como Funciona

### **Prioridade de Busca:**

1. **Primeiro**: Busca no banco de dados local (clientes já cadastrados)
   - ✅ Se encontrar → Preenche todos os campos automaticamente
   - ✅ Funciona para CPF e CNPJ
   - ✅ Reutiliza dados já cadastrados

2. **Segundo**: Para CNPJ, consulta ReceitaWS (se não encontrou no banco)
   - ✅ Busca dados públicos de empresas
   - ✅ Preenche automaticamente

3. **Terceiro**: Para CPF, apenas valida (se não encontrou no banco)
   - ⚠️ Não há APIs públicas para CPF
   - ✅ Mas se já foi cadastrado antes, reutiliza os dados!

## 📋 Campos Preenchidos Automaticamente

Quando encontra cliente no banco ou consulta CNPJ:

- ✅ Nome/Razão Social
- ✅ Nome Fantasia
- ✅ Tipo de Pessoa
- ✅ Inscrição Estadual
- ✅ Tipo de Cliente
- ✅ Telefone
- ✅ Celular
- ✅ E-mail
- ✅ Website
- ✅ Endereço completo (Logradouro, Número, Complemento, Bairro, Cidade, Estado, CEP)
- ✅ Dados Bancários (Banco, Agência, Conta, Tipo de Conta, PIX)

## 🚀 Vantagens

### **1. Reutilização de Dados**
- Se você já cadastrou um cliente antes, não precisa digitar tudo novamente
- Basta digitar o CPF/CNPJ e os dados são preenchidos automaticamente

### **2. Economia de Tempo**
- Não precisa consultar APIs externas para clientes já conhecidos
- Dados já estão no sistema

### **3. Sem Custos**
- Busca local é gratuita
- Não consome APIs pagas desnecessariamente

### **4. Funciona Offline**
- Busca no banco de dados local
- Não depende de conexão com internet (para clientes já cadastrados)

## 💡 Exemplo de Uso

### **Cenário 1: Cliente Já Cadastrado**
1. Você cadastrou "João Silva" com CPF "123.456.789-00" há 1 mês
2. Hoje precisa cadastrar novamente (outra propriedade ou edição)
3. Digite o CPF "123.456.789-00"
4. **Sistema encontra no banco e preenche tudo automaticamente!** ✅

### **Cenário 2: Cliente Novo (CNPJ)**
1. Digite um CNPJ que nunca foi cadastrado
2. Sistema busca no banco → não encontra
3. Sistema consulta ReceitaWS → encontra dados públicos
4. **Preenche automaticamente!** ✅

### **Cenário 3: Cliente Novo (CPF)**
1. Digite um CPF que nunca foi cadastrado
2. Sistema busca no banco → não encontra
3. Sistema valida CPF e define tipo como "Física"
4. **Você preenche os dados manualmente** (primeira vez)

## 🔧 Detalhes Técnicos

### **Busca no Banco de Dados**
- Busca por CPF/CNPJ exato (sem formatação)
- Não considera propriedade (busca em todas)
- Retorna o primeiro cliente encontrado

### **Campos Retornados**
Todos os campos do modelo `Cliente` são retornados:
- Dados principais
- Contato
- Endereço
- Dados bancários

## 📝 Mensagens do Sistema

### **Cliente Encontrado no Banco:**
- ✅ "Cliente encontrado no sistema! Dados preenchidos automaticamente. (X campos)"

### **CNPJ Consultado na ReceitaWS:**
- ✅ "Dados consultados na ReceitaWS e preenchidos automaticamente! (X campos)"

### **CPF Não Encontrado:**
- ℹ️ "CPF válido detectado. Cliente não encontrado no sistema. Por favor, preencha os dados."

## ✅ Status

- ✅ Implementação completa
- ✅ Busca local funcionando
- ✅ Preenchimento automático de todos os campos
- ✅ Funciona para CPF e CNPJ
- ✅ Integrado com busca ReceitaWS para CNPJ

---

**Criado em:** 2025-01-XX  
**Versão:** 1.0  
**Status:** Funcional - Pronto para uso

