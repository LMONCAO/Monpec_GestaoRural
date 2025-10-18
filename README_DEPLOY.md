# Sistema de Gestão Rural - Deploy

## 🚀 Deploy no Vercel (Recomendado)

### Passo 1: Conectar ao Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Faça login com sua conta GitHub
3. Clique em "New Project"
4. Selecione o repositório `LMONCAO/Monpec_projetista`

### Passo 2: Configurações do Deploy
- **Framework Preset**: Django
- **Root Directory**: `/`
- **Build Command**: `pip install -r requirements_vercel.txt`
- **Output Directory**: `/`
- **Install Command**: `pip install -r requirements_vercel.txt`

### Passo 3: Variáveis de Ambiente
Adicione estas variáveis no painel do Vercel:
```
DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.vercel.app
```

### Passo 4: Deploy
- Clique em "Deploy"
- Aguarde o processo de build
- Acesse o link fornecido pelo Vercel

## 🌐 Deploy no Seu Domínio (monpec.com.br)

### Opção 1: Vercel Custom Domain
1. No painel do Vercel, vá em "Domains"
2. Adicione `monpec.com.br`
3. Configure os DNS no seu provedor de domínio
4. Aponte para o Vercel

### Opção 2: Deploy Manual no Servidor
1. Clone o repositório no seu servidor
2. Configure o ambiente virtual
3. Execute os comandos de setup
4. Configure o Nginx/Apache

## 📱 Funcionalidades do Sistema

### ✅ Implementadas
- Dashboard principal
- Gestão de propriedades
- Inventário pecuário
- Projeções e análises
- Sistema de categorias
- Relatórios consolidados
- Interface responsiva

### 🔧 Configurações
- Django 4.2.7
- SQLite (desenvolvimento)
- PostgreSQL (produção)
- Bootstrap 5
- Charts.js para gráficos

## 🎯 Próximos Passos

1. **Deploy no Vercel**: Mais fácil e rápido
2. **Configurar domínio personalizado**: monpec.com.br
3. **Configurar banco de dados**: PostgreSQL para produção
4. **Configurar SSL**: HTTPS automático no Vercel
5. **Monitoramento**: Logs e métricas

## 📞 Suporte
Para dúvidas ou problemas, consulte a documentação ou entre em contato.