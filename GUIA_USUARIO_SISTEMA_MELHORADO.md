# 📘 GUIA DO USUÁRIO - SISTEMA MONPEC 2.0

## 🎯 GUIA COMPLETO PARA USO DO SISTEMA MELHORADO

---

## 🚀 INÍCIO RÁPIDO

### **1. Primeiro Acesso**

1. **Acesse:** `http://191.252.225.106`
2. **Login:** Use suas credenciais
3. **Tela inicial:** Você verá o Dashboard Principal

### **2. Configuração Inicial**

#### **Carregar Categorias Pré-cadastradas (Apenas 1 vez):**

**No servidor (console web ou SSH):**
```bash
cd /var/www/monpec.com.br
source venv/bin/activate
python manage.py carregar_categorias
```

**Isso cria automaticamente:**
- ✅ 10 categorias de animais
- ✅ Com idades e pesos médios
- ✅ Valores de mercado
- ✅ Pronto para usar!

---

## 🏠 CADASTRO DE PROPRIEDADES

### **Como Cadastrar:**

1. **Ir para:** Menu → **Propriedades**
2. **Clicar em:** "Adicionar Nova Propriedade"
3. **Preencher:**
   - Nome da fazenda
   - Município e Estado
   - Área total (hectares)
   - Perfil (Cria/Recria/Engorda/Ciclo Completo)

**O card agora é MODERNO e ELEGANTE:**
- 🎨 Sem cores excessivas
- 📊 Estatísticas visíveis
- ⚡ Ações rápidas
- 🖼️ Visual clean

---

## 📊 INVENTÁRIO DE REBANHO

### **Nova Página Melhorada:**

#### **Como Cadastrar Inventário:**

1. **Ir para:** Gestão Pecuária → **Inventário de Rebanho**
2. **Selecionar:** Propriedade
3. **Preencher:** Quantidade e valor por categoria
4. **Cálculo Automático:** Sistema soma tudo
5. **Salvar:** Botão verde

**Categorias Pré-cadastradas:**
- ✅ Bezerros e Bezerras (0-12m)
- ✅ Garrotes e Novilhas (12-24m)
- ✅ Bois Magros (24-36m)
- ✅ Primíparas e Multíparas
- ✅ Touros
- ✅ Vacas de Descarte
- ✅ Bois Gordos

**Recursos:**
- 💰 Cálculo automático de valores
- 📊 Resumo instantâneo
- 🎨 Interface intuitiva
- ✏️ Edição fácil

---

## 📈 PROJEÇÕES E CENÁRIOS

### **Nova Página Ultra-Moderna:**

#### **Como Usar:**

1. **Ir para:** Gestão Pecuária → **Projeções e Cenários**
2. **Selecionar Cenário:**
   - 📉 Conservador (8% ao ano)
   - 📊 Moderado (12% ao ano)
   - 🚀 Agressivo (18% ao ano)
3. **Visualizar:**
   - Timeline 5 anos
   - Tabela comparativa
   - Gráficos interativos

**Recursos Novos:**
- 📅 Timeline visual linda
- 📊 Gráfico dual-axis (rebanho + receita)
- 📑 Tabela comparativa completa
- 📥 Exportar PDF/Excel (em 1 clique!)

---

## 🤖 INTELIGÊNCIA ARTIFICIAL

### **5 IAs Disponíveis:**

#### **1. IA de Nascimentos**
- 🐮 Previsão com sazonalidade
- ♂️♀️ Proporção realista M/F
- 👶 Mortalidade neonatal
- 📊 Capacidade reprodutiva

**Como usar:**
- Sistema calcula automaticamente
- Veja em: Dashboard IA → Nascimentos

#### **2. IA de Compras**
- 💰 Detecta estoque baixo
- 📅 Melhor época para comprar
- 🔥 Oportunidades de mercado
- 💡 ROI calculado

**Como usar:**
- Dashboard IA → Compras
- Veja sugestões e oportunidades

#### **3. IA de Vendas**
- 🎯 Ponto ideal de venda
- 💹 Previsão de preços
- 📈 Sazonalidade
- 🎲 Simulação de cenários

**Como usar:**
- Dashboard IA → Vendas
- Veja quando vender cada categoria

#### **4. IA de Transferências**
- 🔄 Balanceamento automático
- 📊 Análise de capacidade
- 💵 Custos calculados
- ✅ Sugestões otimizadas

**Como usar:**
- Dashboard IA → Transferências
- Veja recomendações entre fazendas

#### **5. IA de Evolução**
- 📊 Projeções 5 anos
- 🏆 Benchmarking
- 🎯 Metas inteligentes
- 📈 Análise de GAP

**Como usar:**
- Dashboard IA → Projeções
- Compare com mercado

---

## 📱 NOVA INTERFACE

### **Melhorias Visuais:**

✅ **Login Profissional:**
- Design moderno com gradientes
- Animações suaves
- Toggle mostrar/ocultar senha
- Lembrar-me neste dispositivo

✅ **Dashboard Reorganizado:**
- Cards com ícones coloridos
- Estatísticas em destaque
- Atividade recente
- Ações rápidas

✅ **Cards de Propriedade:**
- Visual elegante
- Sem cores excessivas
- Informações claras
- Ações visíveis

✅ **Formulários Modernos:**
- Inputs com bordas arredondadas
- Labels flutuantes
- Cálculos automáticos
- Validação visual

---

## 🎨 CORES DO SISTEMA

**Nova Paleta Elegante:**
- 🔵 Primary: #667eea (Azul suave)
- 🟣 Secondary: #764ba2 (Roxo elegante)
- 🟢 Success: #28a745 (Verde confirmação)
- 🔴 Danger: #dc3545 (Vermelho alerta)
- 🟡 Warning: #ffc107 (Amarelo atenção)
- ⚫ Dark: #2c3e50 (Cinza escuro)

**Gradientes:**
- Todos os gradientes usam combinações suaves
- Nunca mais que 2 cores por elemento
- Visual limpo e profissional

---

## 📊 RELATÓRIOS

### **Tipos Disponíveis:**

#### **1. Relatório Mensal (PDF)**
- 📋 Resumo executivo
- 🔄 Movimentações do mês
- 🤖 Insights da IA
- 💡 Recomendações

**Gerar:** Dashboard → Relatórios → Mensal

#### **2. Relatório Anual (Excel)**
- 📊 Múltiplas abas
- 📈 Gráficos integrados
- 💰 Análise financeira
- 📉 Evolução mensal

**Gerar:** Dashboard → Relatórios → Anual

#### **3. Relatório de Projeções (PDF/Excel)**
- 📅 5 anos de projeção
- 🎯 Cenários comparativos
- 💹 Análise de investimento
- 🏆 Metas e objetivos

**Gerar:** Projeções → Exportar

---

## 🔐 SEGURANÇA E PERFORMANCE

### **SSL/HTTPS (Quando Configurado):**
- 🔒 Conexão segura
- 🛡️ Proteção de dados
- ✅ Certificado válido
- 🔄 Renovação automática

### **Performance:**
- ⚡ Tempo de resposta < 1s
- 🚀 Cache Redis ativo
- 📦 Compressão GZIP
- 💾 Queries otimizadas

---

## 📱 USO MOBILE

### **O Sistema é 100% Responsivo:**

✅ **Celular:**
- Menu hamburger
- Cards adaptados
- Formulários touch-friendly
- Gráficos responsivos

✅ **Tablet:**
- Layout otimizado
- Grids ajustados
- Navegação fácil

---

## 💡 DICAS PRÁTICAS

### **1. Atalhos do Teclado:**
- `Ctrl + K`: Busca rápida
- `Ctrl + S`: Salvar formulário
- `Esc`: Fechar modais

### **2. Filtros Rápidos:**
- Use os filtros no topo das tabelas
- Ordene clicando nos cabeçalhos
- Busque por texto

### **3. Exportações:**
- PDF: Relatórios impressos
- Excel: Análises detalhadas
- CSV: Integração com outros sistemas

---

## 🆘 PROBLEMAS COMUNS

### **"Não consigo fazer login"**
✅ Verifique usuário e senha
✅ Limpe cache do navegador
✅ Tente em modo anônimo

### **"Categorias não aparecem"**
✅ Execute: `python manage.py carregar_categorias`
✅ Verifique se o servidor está rodando

### **"Página demora a carregar"**
✅ Verifique conexão com internet
✅ Limpe cache do navegador
✅ Contacte administrador

---

## 📞 SUPORTE

**Problemas técnicos:**
- 📧 Email: suporte@monpec.com.br
- 📱 WhatsApp: (XX) XXXXX-XXXX

**Documentação:**
- 📖 README_SISTEMA_MELHORADO.md
- 📋 RESUMO_MELHORIAS_IMPLEMENTADAS.md
- 🔧 COMO_ATUALIZAR_SERVIDOR.md

---

## 🎉 APROVEITE O SISTEMA!

Agora você tem um sistema **profissional**, **moderno** e **inteligente** para gerir seu rebanho!

**Principais benefícios:**
- 🤖 5 IAs trabalhando por você
- 📊 Dashboards lindos e informativos
- 📱 Acesso de qualquer lugar
- ⚡ Rápido e eficiente
- 🎨 Interface profissional

---

**Sistema Monpec 2.0 - Gestão Rural do Futuro! 🚀🐮**

---

*Versão: 2.0 | Data: 23/10/2025 | Status: ✅ Produção*

