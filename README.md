# MONPEC - Sistema de Gestão Rural

Sistema completo de gestão para propriedades rurais, desenvolvido em Django.

## 🚀 Características Principais

- **Gestão de Propriedades**: Cadastro completo de propriedades rurais
- **Pecuária**: Inventário, projeções, planejamento e rastreabilidade
- **Financeiro**: Controle de receitas, despesas, DRE e fluxo de caixa
- **Relatórios Consolidados**: Relatórios completos para comprovação bancária
- **Multi-propriedade**: Gerenciamento de múltiplas propriedades
- **Rastreabilidade**: Sistema completo de rastreabilidade bovina (PNIB)

## 📋 Requisitos

- Python 3.11 ou superior
- Git (para atualizações do GitHub)
- SQLite3 (banco de dados padrão)

## 🛠️ Instalação Rápida

### Windows

1. Execute o instalador:
   ```batch
   INSTALAR.bat
   ```

2. Inicie o servidor:
   ```batch
   INICIAR.bat
   ```

3. Acesse no navegador:
   ```
   http://localhost:8000
   ```

### Linux/Mac

1. Execute o instalador:
   ```bash
   chmod +x INSTALAR.sh
   ./INSTALAR.sh
   ```

2. Inicie o servidor:
   ```bash
   chmod +x INICIAR.sh
   ./INICIAR.sh
   ```

3. Acesse no navegador:
   ```
   http://localhost:8000
   ```

## 📖 Documentação

- [Guia de Instalação](README_INSTALACAO.md) - Instruções detalhadas de instalação
- [Início Rápido](QUICK_START.md) - Comece a usar o sistema rapidamente
- [Configuração de Banco de Dados](CONFIGURACAO_BANCO_DADOS.md) - Configuração de banco remoto

## 🔄 Atualização do GitHub

### Windows

Para atualizar o sistema do GitHub e iniciar:

```batch
ATUALIZAR_E_INICIAR.bat
```

Ou apenas atualizar:

```batch
ATUALIZAR_GITHUB.bat
```

### Linux/Mac

```bash
chmod +x ATUALIZAR_GITHUB.sh
./ATUALIZAR_GITHUB.sh
```

## 💾 Backup e Restauração

### Exportar Dados

**Windows:**
```batch
EXPORTAR_DADOS.bat
```

**Linux/Mac:**
```bash
chmod +x EXPORTAR_DADOS.sh
./EXPORTAR_DADOS.sh
```

### Importar Dados

**Windows:**
```batch
IMPORTAR_DADOS.bat
```

**Linux/Mac:**
```bash
chmod +x IMPORTAR_DADOS.sh
./IMPORTAR_DADOS.sh
```

## 🔐 Acesso Padrão

- **URL**: http://localhost:8000
- **Usuário**: `admin`
- **Senha**: `admin`

⚠️ **IMPORTANTE**: Altere a senha após o primeiro acesso!

## 📁 Estrutura do Projeto

```
Monpec_GestaoRural/
├── gestao_rural/          # Aplicação principal
├── templates/             # Templates HTML
├── static/                # Arquivos estáticos
├── sistema_rural/         # Configurações do Django
├── manage.py              # Script de gerenciamento Django
├── db.sqlite3            # Banco de dados (SQLite)
└── requirements.txt      # Dependências Python
```

## 🎯 Funcionalidades Principais

### Módulos Disponíveis

1. **Dashboard**: Visão geral do sistema
2. **Pecuária**: Gestão completa do rebanho
3. **Financeiro**: Controle financeiro completo
4. **Relatórios**: Relatórios consolidados e customizados
5. **Rastreabilidade**: Sistema PNIB completo
6. **Compras**: Gestão de compras e fornecedores
7. **Nutrição**: Gestão nutricional
8. **Operações**: Operações diversas

### Relatórios Consolidados

- Dashboard Consolidado
- Relatório de Rebanho
- Relatório de Bens
- DRE Consolidado
- Fluxo de Caixa
- Relatório Completo para Empréstimo
- Justificativa de Endividamento

## 🔧 Configuração

### Configurar Banco Marcelo Sanguino

O sistema pode ser configurado para usar o banco do Marcelo Sanguino:

```batch
python configurar_banco_marcelo_sanguino.py
```

### Verificar Banco

```batch
python verificar_banco_correto.py
```

## 📞 Suporte

Para mais informações, consulte a documentação completa ou entre em contato com o suporte.

## 📝 Licença

Sistema proprietário - Todos os direitos reservados.















<<<<<<< HEAD











=======
>>>>>>> 82f662d03a852eab216d20cd9d12193f5dbd2881





































