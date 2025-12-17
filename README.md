# 🚜 MONPEC Gestão Rural

Sistema completo de gestão rural para propriedades, incluindo pecuária, agricultura, financeiro, compras e relatórios consolidados.

## 🚀 Instalação Rápida

### Windows
```bash
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
cd Monpec_GestaoRural
INSTALAR.bat
INICIAR.bat
```

### Linux/Mac
```bash
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
cd Monpec_GestaoRural
chmod +x INSTALAR.sh INICIAR.sh
./INSTALAR.sh
./INICIAR.sh
```

**📖 Para instruções detalhadas, veja [README_INSTALACAO.md](README_INSTALACAO.md)**

## ✨ Funcionalidades

### 🐄 Pecuária
- Gestão completa de rebanho
- Inventário de animais
- Projeções e movimentações
- Planejamento anual
- Cenários de produção
- Vendas projetadas

### 💰 Financeiro
- Contas a pagar/receber
- Fluxo de caixa
- Receitas e despesas
- Categorias financeiras
- Centros de custo

### 📊 Relatórios Consolidados
- Dashboard multi-propriedade
- Relatório completo para empréstimo bancário
- Análise de rebanho consolidado
- DRE (Demonstração de Resultado do Exercício)
- Fluxo de caixa consolidado
- Justificativa de endividamento

### 🏗️ Bens e Patrimônio
- Controle de máquinas e veículos
- Instalações
- Depreciação

### 🛒 Compras
- Fornecedores
- Ordens de compra
- Notas fiscais

### 📁 Projetos Bancários
- Projetos de crédito rural
- Análise de viabilidade
- Documentação bancária

## 🗄️ Banco de Dados

O sistema suporta:
- **SQLite** (padrão - desenvolvimento local)
- **PostgreSQL** (recomendado para produção/múltiplas máquinas)
- **MySQL** (alternativa)

**📖 Para configurar banco de dados remoto, veja [CONFIGURACAO_BANCO_DADOS.md](CONFIGURACAO_BANCO_DADOS.md)**

## 📋 Requisitos

- Python 3.8 ou superior
- Django 4.2.7
- PostgreSQL (opcional - apenas se usar banco remoto)

## 🔧 Configuração

1. Clone o repositório
2. Execute `INSTALAR.bat` (Windows) ou `./INSTALAR.sh` (Linux/Mac)
3. Configure o arquivo `.env` se necessário
4. Execute `INICIAR.bat` (Windows) ou `./INICIAR.sh` (Linux/Mac)

## 📦 Estrutura do Projeto

```
Monpec_GestaoRural/
├── gestao_rural/          # Aplicação principal
├── monpec_sistema_completo/  # Configurações Django
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
├── media/                 # Uploads de arquivos
├── INSTALAR.bat          # Instalador Windows
├── INICIAR.bat            # Iniciar servidor Windows
├── INSTALAR.sh            # Instalador Linux/Mac
├── INICIAR.sh             # Iniciar servidor Linux/Mac
└── requirements.txt       # Dependências Python
```

## 🔐 Primeiro Acesso

Após a instalação, crie um superusuário:

```bash
python manage.py createsuperuser
```

Acesse: http://127.0.0.1:8000

## 📚 Documentação

- [Guia de Instalação](README_INSTALACAO.md)
- [Configuração de Banco de Dados](CONFIGURACAO_BANCO_DADOS.md)

## 🛠️ Comandos Úteis

```bash
# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Exportar dados
python manage.py dumpdata > backup.json

# Importar dados
python manage.py loaddata backup.json

# Gerar projeções (exemplo)
python manage.py gerar_projecao_completa_canta_galo --ano-inicio 2022 --ano-fim 2025
```

## 🆘 Suporte

Para problemas ou dúvidas:
1. Consulte a documentação
2. Verifique os logs de erro
3. Execute o instalador novamente

## 📄 Licença

Este projeto é propriedade da MONPEC.

---

**Desenvolvido por MONPEC** 🚜












