# 📱 COMO USAR O MÓDULO DE MARKETING - MONPEC

## 🎯 VISÃO GERAL

O módulo de Marketing foi criado para ajudar você a:
1. **Gerar posts automaticamente** para redes sociais usando templates
2. **Capturar leads** através de uma landing page com acesso gratuito
3. **Gerenciar sua lista de interessados** e acompanhar conversões
4. **Configurar estratégias** para atingir seu público-alvo

---

## 🚀 PRIMEIROS PASSOS

### 1. Criar Migrações e Aplicar

Primeiro, você precisa criar as migrações para os novos modelos:

```bash
python manage.py makemigrations gestao_rural
python manage.py migrate
```

### 2. Popular Templates Iniciais

Acesse o admin ou use o comando:

```bash
python manage.py shell
```

No shell:

```python
from gestao_rural.gerador_posts import popular_templates_iniciais
popular_templates_iniciais()
```

Ou acesse: `/marketing/templates/` e clique em "Popular Templates Iniciais"

### 3. Configurar

Acesse: `/marketing/configuracao/` e configure:
- URL do site (ex: https://monpec.com.br)
- WhatsApp para contato
- Email de contato
- Mensagens padrão
- Ativar/desativar acesso gratuito

---

## 📝 GERANDO POSTS AUTOMATICAMENTE

### Gerar um Post Individual

1. Acesse: `/marketing/posts/gerar/`
2. Escolha um template OU um tipo de post
3. Selecione a rede social
4. (Opcional) Adicione variáveis extras em JSON
5. Clique em "Gerar Post"
6. Revise e edite se necessário
7. Publique nas redes sociais

### Gerar Posts para a Semana

1. Acesse: `/marketing/posts/gerar-semana/`
2. Clique em "Gerar Posts da Semana"
3. O sistema criará 7 posts diferentes (um para cada dia)
4. Revise e ajuste conforme necessário

### Variáveis Disponíveis nos Templates

Você pode usar essas variáveis nos seus templates (entre chaves `{}`):

- `{nome_produto}` - MONPEC
- `{nome_produto_completo}` - MONPEC - Gestão Rural Inteligente
- `{url_site}` - URL do site configurada
- `{beneficio_1}` até `{beneficio_5}` - Benefícios principais
- `{problema_1}` até `{problema_4}` - Problemas comuns
- `{cta_padrao}` - Call-to-action padrão

---

## 🎯 CAPTURA DE LEADS

### Landing Page de Acesso Gratuito

A landing page está disponível em: `/acesso-gratuito/`

**O que acontece quando alguém se cadastra:**

1. Lead é salvo no banco de dados
2. (Se ativado) Um usuário é criado automaticamente
3. Email com credenciais é enviado
4. Lead fica disponível em `/marketing/leads/`

### Gerenciar Leads

1. Acesse: `/marketing/leads/`
2. Veja todos os leads capturados
3. Filtre por status, origem, ou busque
4. Clique em um lead para ver detalhes e editar

### Status dos Leads

- **Novo**: Lead recém-cadastrado
- **Contatado**: Já foi contactado
- **Qualificado**: Lead interessado e qualificado
- **Convertido**: Convertido em cliente
- **Descartado**: Não qualificado

---

## 🛠️ CRIANDO SEUS PRÓPRIOS TEMPLATES

### Criar Template

1. Acesse: `/marketing/templates/`
2. Clique em "Novo Template"
3. Preencha:
   - **Nome**: Nome identificador (ex: "Post de Apresentação")
   - **Tipo**: Tipo de post (Apresentação, Vendas, etc.)
   - **Rede Social**: Instagram, Facebook, LinkedIn, etc.
   - **Conteúdo**: Use variáveis `{variavel}` que serão substituídas
   - **Hashtags**: Separe por vírgula
4. Salve

### Exemplo de Template

```
🐄💼 {nome_produto_completo}

✅ {beneficio_1}
✅ {beneficio_2}
✅ {beneficio_3}

{cta_padrao}

Acesse: {url_site}
```

---

## 📊 DASHBOARD DE MARKETING

Acesse: `/marketing/` para ver:

- Total de leads
- Leads novos
- Total de posts
- Posts pendentes
- Posts recentes
- Leads recentes

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### Configurar Email

Para enviar emails automaticamente com credenciais, configure no `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu@email.com'
EMAIL_HOST_PASSWORD = 'sua_senha'
DEFAULT_FROM_EMAIL = 'contato@monpec.com.br'
```

Ou use as configurações já existentes do projeto.

### Configurar URLs Públicas

A landing page precisa estar acessível publicamente. Certifique-se de que:

1. A URL `/acesso-gratuito/` está acessível
2. Não requer login
3. Está configurada no seu domínio (monpec.com.br)

---

## 🔗 INTEGRANDO COM REDES SOCIAIS

### Instagram/Facebook

1. Gere o post no sistema
2. Copie o conteúdo e hashtags
3. Publique manualmente ou use ferramentas como:
   - Meta Business Suite
   - Later
   - Hootsuite

### LinkedIn

1. Gere o post no sistema
2. Copie e adapte se necessário (formato mais profissional)
3. Publique no LinkedIn

### WhatsApp

1. Gere o post no sistema
2. Use o conteúdo para criar mensagens
3. Envie via WhatsApp Business

---

## 📈 ESTRATÉGIA RECOMENDADA

### Semana 1: Setup

1. ✅ Popular templates iniciais
2. ✅ Configurar sistema
3. ✅ Testar geração de posts
4. ✅ Publicar landing page

### Semana 2-4: Gerar Tráfego

1. Gerar posts para semana
2. Publicar nas redes sociais
3. Direcionar para landing page
4. Capturar leads

### Semana 5+: Otimizar

1. Analisar quais posts funcionam melhor
2. Criar novos templates baseados em resultados
3. Ajustar estratégia
4. Converter leads em clientes

---

## 🎨 PERSONALIZAÇÃO

### Criar Templates Personalizados

Você pode criar templates específicos para:
- Diferentes tipos de conteúdo
- Diferentes redes sociais
- Diferentes campanhas
- Diferentes públicos-alvo

### Variáveis Personalizadas

Você pode adicionar variáveis personalizadas em:
- Configurações → Variáveis Padrão (JSON)
- Ao gerar post → Variáveis Extras (JSON)

Exemplo:

```json
{
  "desconto": "50%",
  "prazo": "até 31/12/2024",
  "telefone": "(11) 99999-9999"
}
```

---

## ❓ TROUBLESHOOTING

### Posts não estão sendo gerados

- Verifique se há templates ativos
- Verifique se o template escolhido existe
- Veja os logs de erro

### Emails não estão sendo enviados

- Verifique configurações de email no settings.py
- Verifique se DEFAULT_FROM_EMAIL está configurado
- Teste enviando email manualmente

### Landing page não está acessível

- Verifique se a URL está correta
- Verifique permissões de acesso
- Verifique se não há middleware bloqueando

---

## 📞 PRÓXIMOS PASSOS

1. **Criar mais templates** baseados nos exemplos do guia de marketing
2. **Configurar landing page** no domínio monpec.com.br
3. **Integrar com ferramentas** de agendamento de posts
4. **Criar campanhas** específicas
5. **Acompanhar métricas** de conversão

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- `docs/GUIA_MARKETING_REDES_SOCIAIS.md` - Guia completo de marketing
- `docs/TEMPLATES_RAPIDOS_REDES_SOCIAIS.md` - Templates prontos para usar
- `docs/PLANO_ACAO_MARKETING.md` - Plano de ação detalhado

---

**Boa sorte com suas vendas! 🚀**





















