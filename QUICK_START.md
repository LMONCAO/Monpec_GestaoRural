# Início Rápido - MONPEC Gestão Rural

Guia rápido para começar a usar o sistema em poucos minutos.

## ⚡ Início Rápido (5 minutos)

### 1. Instalar o Sistema

**Windows:**
```batch
INSTALAR.bat
```

**Linux/Mac:**
```bash
chmod +x INSTALAR.sh && ./INSTALAR.sh
```

### 2. Iniciar o Servidor

**Windows:**
```batch
INICIAR.bat
```

**Linux/Mac:**
```bash
chmod +x INICIAR.sh && ./INICIAR.sh
```

### 3. Acessar o Sistema

1. Abra o navegador
2. Acesse: `http://localhost:8000`
3. Login: `admin` / Senha: `admin`

## 🎯 Primeiras Ações

### 1. Cadastrar Produtor

1. Vá em **Produtores** > **Novo Produtor**
2. Preencha os dados
3. Salve

### 2. Cadastrar Propriedade

1. Vá em **Propriedades** > **Nova Propriedade**
2. Selecione o produtor
3. Preencha os dados da propriedade
4. Salve

### 3. Configurar Inventário

1. Acesse a propriedade
2. Vá em **Pecuária** > **Inventário**
3. Adicione categorias de animais
4. Configure quantidades e valores

### 4. Visualizar Relatórios

1. Acesse **Relatórios** no menu
2. Selecione o tipo de relatório
3. Configure filtros
4. Visualize ou exporte

## 📊 Funcionalidades Principais

### Dashboard
- Visão geral do sistema
- Estatísticas principais
- Acesso rápido aos módulos

### Pecuária
- **Inventário**: Cadastro de animais por categoria
- **Projeções**: Projeções de vendas e crescimento
- **Planejamento**: Planejamento estratégico
- **Rastreabilidade**: Sistema PNIB completo

### Financeiro
- **Receitas**: Controle de receitas
- **Despesas**: Controle de despesas
- **DRE**: Demonstração de Resultado
- **Fluxo de Caixa**: Controle de fluxo mensal

### Relatórios
- **Consolidados**: Relatórios multi-propriedade
- **Customizados**: Crie seus próprios relatórios
- **Exportação**: PDF e Excel

## 🔄 Atualizar do GitHub

Para manter o sistema atualizado:

**Windows:**
```batch
ATUALIZAR_GITHUB.bat
```

**Linux/Mac:**
```bash
./ATUALIZAR_GITHUB.sh
```

## 💾 Backup

Sempre faça backup antes de atualizações:

**Windows:**
```batch
EXPORTAR_DADOS.bat
```

**Linux/Mac:**
```bash
./EXPORTAR_DADOS.sh
```

## 🆘 Precisa de Ajuda?

- Consulte a [Documentação Completa](README.md)
- Veja o [Guia de Instalação](README_INSTALACAO.md)
- Verifique a [Configuração de Banco](CONFIGURACAO_BANCO_DADOS.md)

## 🎓 Dicas Rápidas

1. **Use o Dashboard**: Comece sempre pelo dashboard para ter uma visão geral
2. **Configure Propriedades**: Configure todas as propriedades antes de adicionar dados
3. **Faça Backups**: Sempre faça backup antes de grandes mudanças
4. **Atualize Regularmente**: Mantenha o sistema atualizado do GitHub
5. **Use Relatórios**: Os relatórios consolidados são poderosos para análise

## 📱 Acesso Remoto

Para acessar de outros dispositivos na mesma rede:

1. Inicie o servidor com: `python manage.py runserver 0.0.0.0:8000`
2. Acesse usando o IP da máquina: `http://[IP-DA-MAQUINA]:8000`















