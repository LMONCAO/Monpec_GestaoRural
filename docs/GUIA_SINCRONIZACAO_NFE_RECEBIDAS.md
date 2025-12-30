# Guia de Sincronização Automática de NFe Recebidas

## 📋 Visão Geral

Este sistema permite **sincronizar automaticamente** as Notas Fiscais Eletrônicas (NF-e) que foram **emitidas para o CPF/CNPJ** da sua propriedade, importando-as automaticamente no módulo de compras e integrando com o financeiro.

## ✨ Funcionalidades

- ✅ **Consulta automática** de NFe emitidas para seu CPF/CNPJ
- ✅ **Download automático** de XML e PDF (DANFE)
- ✅ **Importação automática** no sistema
- ✅ **Vinculação automática** com ordens de compra existentes
- ✅ **Geração automática** de contas a pagar
- ✅ **Integração completa** com módulos de compras e financeiro

## 🔧 Configuração Inicial

### 1. Configurar API de NF-e

Adicione a configuração da API nas `settings.py`:

```python
# settings.py
API_NFE = {
    'TIPO': 'TECNOSPEED',  # ou 'FOCUS_NFE', 'NFE_IO'
    'TOKEN': 'seu_token_aqui',
    'AMBIENTE': 'producao',  # ou 'homologacao'
    'COMPANY_ID': 'seu_company_id',  # apenas para NFe.io
}
```

### 2. Verificar CPF/CNPJ Cadastrado

Certifique-se de que o CPF/CNPJ está cadastrado no **Produtor Rural** vinculado à propriedade:

1. Acesse o cadastro do Produtor Rural
2. Verifique se o campo CPF/CNPJ está preenchido corretamente
3. Este será o documento usado para buscar as NFe recebidas

## 🚀 Como Usar

### Sincronização Manual (Interface Web)

1. Acesse: **Compras → Notas Fiscais**
2. Clique no botão **"Sincronizar NFe Recebidas"**
3. Configure os parâmetros:
   - **Período de busca**: Quantos dias atrás buscar (padrão: 30 dias)
   - **Limite de notas**: Máximo de notas por sincronização (padrão: 100)
   - **Baixar PDF**: Marque se deseja baixar também o PDF (DANFE)
4. Clique em **"Iniciar Sincronização"**
5. Aguarde o processamento (pode levar alguns minutos)
6. As notas importadas aparecerão na lista de notas fiscais

### Sincronização Automática (Comando)

Execute o comando de gerenciamento para sincronizar todas as propriedades:

```bash
# Sincronizar todas as propriedades (últimos 30 dias)
python manage.py sincronizar_nfe_recebidas

# Sincronizar propriedade específica
python manage.py sincronizar_nfe_recebidas --propriedade-id 1

# Personalizar período e limite
python manage.py sincronizar_nfe_recebidas --dias 60 --limite 200

# Incluir download de PDF
python manage.py sincronizar_nfe_recebidas --baixar-pdf
```

### Agendamento Automático (Cron/Tarefa Agendada)

Para sincronizar automaticamente todos os dias, configure uma tarefa agendada:

**Linux/Mac (Cron):**
```bash
# Editar crontab
crontab -e

# Adicionar linha (executa diariamente às 2h da manhã)
0 2 * * * cd /caminho/do/projeto && python manage.py sincronizar_nfe_recebidas >> /var/log/nfe_sync.log 2>&1
```

**Windows (Agendador de Tarefas):**
1. Abra o Agendador de Tarefas
2. Crie uma nova tarefa
3. Configure para executar diariamente
4. Ação: Executar programa
5. Programa: `python`
6. Argumentos: `manage.py sincronizar_nfe_recebidas`
7. Diretório inicial: Caminho do projeto

## 📊 O que Acontece na Sincronização

1. **Consulta**: O sistema consulta a API para buscar NFe emitidas para o CPF/CNPJ
2. **Download XML**: Baixa o XML de cada nota encontrada
3. **Importação**: Importa automaticamente no sistema
4. **Vinculação**: Tenta vincular a ordens de compra existentes (por fornecedor e valor)
5. **Conta a Pagar**: Gera automaticamente contas a pagar quando aplicável
6. **Download PDF**: Baixa o PDF (DANFE) se solicitado

## 🔗 Integrações

### Com Módulo de Compras

- Notas fiscais são vinculadas automaticamente a ordens de compra quando:
  - O fornecedor é o mesmo
  - O valor está dentro de uma tolerância de 5% ou R$ 1,00
  - A ordem de compra não possui nota fiscal vinculada

### Com Módulo Financeiro

- **Contas a Pagar** são geradas automaticamente quando:
  - A nota fiscal é vinculada a uma ordem de compra
  - A ordem de compra está autorizada

### Com Estoque

- Os itens da nota fiscal são importados e podem ser vinculados a insumos/estoque

## ⚠️ Limitações e Observações

### APIs Suportadas

Atualmente, a consulta automática de NFe recebidas está disponível para:

- ✅ **TecnoSpeed**: Suporta consulta de NFe destinadas (recebidas)
- ⚠️ **Focus NFe**: Não possui endpoint direto (use webhook ou sincronização manual)
- ⚠️ **NFe.io**: Não possui endpoint direto (use webhook ou sincronização manual)

### Alternativas para APIs sem Suporte

Se sua API não suporta consulta automática:

1. **Webhook**: Configure webhook na API para receber notificações quando NFe forem emitidas
2. **Sincronização Manual**: Use o upload de XML manualmente
3. **Integração com Receita Federal**: Use certificado digital e-CNPJ para consulta direta na Receita Federal

## 🐛 Solução de Problemas

### Erro: "API de NF-e não configurada"

**Solução**: Configure a variável `API_NFE` nas settings do Django.

### Erro: "CPF/CNPJ da propriedade não cadastrado"

**Solução**: Cadastre o CPF/CNPJ no cadastro do Produtor Rural vinculado à propriedade.

### Erro: "Tipo de API não suportado para consulta"

**Solução**: Use uma API que suporte consulta de NFe recebidas (TecnoSpeed) ou configure webhook.

### Notas não estão sendo encontradas

**Verificações**:
1. Confirme que o CPF/CNPJ está correto
2. Verifique se há notas fiscais no período informado
3. Confirme que a API está configurada corretamente
4. Verifique os logs do sistema para mais detalhes

## 📝 Logs e Monitoramento

O sistema registra todas as operações de sincronização:

- Notas encontradas
- Notas importadas
- Notas já existentes (duplicadas)
- Erros durante o processo

Consulte os logs do Django para detalhes:

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'nfe_sync.log',
        },
    },
    'loggers': {
        'gestao_rural.services_nfe_consulta': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## 🔒 Segurança

- As credenciais da API devem ser armazenadas de forma segura (variáveis de ambiente)
- O acesso à sincronização requer permissões de compras
- As notas importadas são vinculadas ao usuário que executou a sincronização

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte os logs do sistema
2. Verifique a documentação da API utilizada
3. Entre em contato com o suporte técnico

---

**Última atualização**: Dezembro 2024

