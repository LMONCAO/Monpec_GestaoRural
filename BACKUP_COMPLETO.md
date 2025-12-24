# BACKUP COMPLETO DO SISTEMA MONPEC

## Data do Backup: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Estrutura do Backup

### 1. Código Fonte
- Todo o código Python (Django)
- Templates HTML
- Arquivos estáticos (CSS, JS, imagens)
- Configurações

### 2. Banco de Dados
- SQLite: `db.sqlite3`
- Bancos de tenant: `tenants/*.sqlite3`

### 3. Arquivos de Mídia
- Uploads de usuários: `media/`

### 4. Configurações
- `.env` (variáveis de ambiente)
- `settings.py`
- `requirements.txt`

## URLs Principais do Sistema

### Landing Page e Autenticação
- `/` - Landing page
- `/login/` - Login
- `/logout/` - Logout
- `/contato/` - Formulário de contato
- `/recuperar-senha/` - Recuperação de senha

### Dashboard e Módulos
- `/dashboard/` - Dashboard principal
- `/propriedade/<id>/modulos/` - Módulos da propriedade

### Módulo Pecuária
- `/propriedade/<id>/pecuaria/dashboard/` - Dashboard pecuária
- `/propriedade/<id>/pecuaria/inventario/` - Inventário
- `/propriedade/<id>/pecuaria/projecao/` - Projeções
- `/propriedade/<id>/pecuaria/planejamento/` - Planejamento
- `/propriedade/<id>/pecuaria/cenarios/` - Análise de cenários

### Módulo Curral
- `/propriedade/<id>/curral/` - Dashboard curral
- `/propriedade/<id>/curral/demo/` - Informações demo
- `/propriedade/<id>/curral/v3/` - Versão 3
- `/propriedade/<id>/curral/v4/` - Versão 4

### Módulo Rastreabilidade
- `/propriedade/<id>/rastreabilidade/` - Dashboard
- `/propriedade/<id>/rastreabilidade/importar-bnd/` - Importar BND/SISBOV
- `/propriedade/<id>/rastreabilidade/animais/` - Animais individuais

### Módulo Compras
- `/propriedade/<id>/compras/` - Dashboard (HABILITADO)
- `/propriedade/<id>/compras/requisicoes/` - Requisições (BLOQUEADO)
- `/propriedade/<id>/compras/fornecedores/` - Fornecedores (BLOQUEADO)
- `/propriedade/<id>/compras/notas-fiscais/` - Notas Fiscais (BLOQUEADO)

### Módulo Financeiro
- `/propriedade/<id>/financeiro/` - Financeiro Completo (HABILITADO)
- `/propriedade/<id>/financeiro/fluxo-caixa/` - Fluxo de Caixa (BLOQUEADO)
- `/propriedade/<id>/financeiro/contas-pagar/` - Contas a Pagar (BLOQUEADO)
- `/propriedade/<id>/financeiro/contas-receber/` - Contas a Receber (BLOQUEADO)

### Módulo Operações
- `/propriedade/<id>/operacoes/` - Dashboard (HABILITADO)
- `/propriedade/<id>/operacoes/combustivel/` - Combustível (BLOQUEADO)
- `/propriedade/<id>/operacoes/equipamentos/` - Equipamentos (BLOQUEADO)
- `/propriedade/<id>/operacoes/manutencao/` - Manutenção (BLOQUEADO)
- `/propriedade/<id>/operacoes/funcionarios/` - Funcionários (BLOQUEADO)

### Módulo Nutrição
- `/propriedade/<id>/nutricao/` - Dashboard (ABRE MODAL DE COMPRA)

### Módulo Bens e Patrimônio
- `/propriedade/<id>/imobilizado/` - Dashboard
- `/propriedade/<id>/bens/` - Lista de bens

### Assinaturas e Stripe
- `/assinaturas/` - Dashboard de assinaturas
- `/assinaturas/plano/<slug>/checkout/` - Checkout Stripe
- `/assinaturas/sucesso/` - Sucesso no pagamento
- `/assinaturas/webhook/` - Webhook Stripe

### Relatórios
- `/propriedade/<id>/relatorio-final/` - Relatório final
- `/propriedade/<id>/relatorios-customizados/` - Relatórios customizados

### Outros
- `/categorias/` - Categorias de animais
- `/transferencias/` - Transferências entre propriedades

## Configurações Importantes

### Variáveis de Ambiente (.env)
```
DEBUG=False
SECRET_KEY=<chave_secreta>
ALLOWED_HOSTS=<hosts_permitidos>
DATABASE_URL=<url_banco_dados>
STRIPE_SECRET_KEY=<chave_stripe>
STRIPE_PUBLISHABLE_KEY=<chave_publica_stripe>
STRIPE_WEBHOOK_SECRET=<webhook_secret>
EMAIL_HOST=<servidor_email>
EMAIL_PORT=<porta_email>
EMAIL_HOST_USER=<usuario_email>
EMAIL_HOST_PASSWORD=<senha_email>
```

### Banco de Dados
- SQLite em desenvolvimento
- PostgreSQL recomendado para produção

### Arquivos Estáticos
- Coletar com: `python manage.py collectstatic`
- Servir via Cloud Storage ou CDN em produção

## Comandos Importantes

### Backup do Banco de Dados
```bash
python manage.py dumpdata > backup_data.json
```

### Restaurar Banco de Dados
```bash
python manage.py loaddata backup_data.json
```

### Migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### Coletar Arquivos Estáticos
```bash
python manage.py collectstatic --noinput
```

### Criar Superusuário
```bash
python manage.py createsuperuser
```

## Versão de Demonstração

### Usuário Demo
- Username: `demo_monpec`
- Password: `demo123`

### Funcionalidades Bloqueadas para Demo
- Cadastros no módulo Cadastro
- Submenus de Compras (exceto Dashboard)
- Submenus de Financeiro (exceto Financeiro Completo)
- Submenus de Operações (exceto Dashboard)
- Nutrição (abre modal de compra)
- Projetos Bancários (abre modal de compra)
- Relatórios (abre modal de compra)

### Funcionalidades Habilitadas para Demo
- Visualização de dashboards
- Visualização de dados de exemplo
- Navegação pelos módulos principais
- Formulário de contato na landing page

## Deploy no Google Cloud

### Opção 1: Google App Engine
- Arquivo: `deploy/config/app.yaml`
- Runtime: Python 3.9

### Opção 2: Cloud Run
- Arquivo: `Dockerfile`
- Containerizado

### Variáveis de Ambiente no GCP
Configurar no Cloud Console:
- SECRET_KEY
- DEBUG=False
- DATABASE_URL
- STRIPE_* (todas as chaves)
- EMAIL_* (configurações de email)

## Notas Importantes

1. **Segurança**: Nunca commitar arquivos `.env` ou `db.sqlite3` no Git
2. **Backup**: Fazer backup regular do banco de dados
3. **Migrações**: Sempre testar migrações em ambiente de desenvolvimento primeiro
4. **Estáticos**: Coletar arquivos estáticos antes de cada deploy
5. **Logs**: Monitorar logs no Google Cloud Console






