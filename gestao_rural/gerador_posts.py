"""
Gerador automático de posts para redes sociais
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .models_marketing import TemplatePost, PostGerado, ConfiguracaoMarketing


class GeradorPosts:
    """Classe para gerar posts automaticamente a partir de templates"""
    
    # Variáveis padrão que podem ser substituídas
    VARIAVEIS_PADRAO = {
        'nome_produto': 'MONPEC',
        'nome_produto_completo': 'MONPEC - Gestão Rural Inteligente',
        'url_site': 'https://monpec.com.br',
        'beneficio_1': 'Gestão completa do rebanho',
        'beneficio_2': 'Controle financeiro (DRE, Fluxo de Caixa)',
        'beneficio_3': 'Projeções inteligentes com IA',
        'beneficio_4': 'Relatórios profissionais para empréstimos',
        'beneficio_5': 'Rastreabilidade completa (PNIB)',
        'problema_1': 'Planilhas confusas e desorganizadas',
        'problema_2': 'Falta de controle sobre o rebanho',
        'problema_3': 'Dificuldade em comprovar situação para bancos',
        'problema_4': 'Projeções feitas no "feeling"',
        'cta_padrao': '👉 Entre em contato e descubra como o MONPEC pode transformar sua gestão!',
    }
    
    HASHTAGS_PADRAO = [
        '#MONPEC', '#GestãoRural', '#Agronegócio', '#TecnologiaAgrícola',
        '#Pecuária', '#GestãoPecuária', '#FazendaDigital', '#AgTech',
        '#InovaçãoNoCampo', '#ProdutorRural', '#GestãoDeFazenda'
    ]
    
    def __init__(self):
        self.config = ConfiguracaoMarketing.get_config()
        self.variaveis = {**self.VARIAVEIS_PADRAO}
        
        # Atualizar com variáveis da configuração
        if self.config.variaveis_padrao:
            self.variaveis.update(self.config.variaveis_padrao)
        
        # Adicionar variáveis da config
        if self.config.url_site:
            self.variaveis['url_site'] = self.config.url_site
        if self.config.mensagem_cta_padrao:
            self.variaveis['cta_padrao'] = self.config.mensagem_cta_padrao
    
    def substituir_variaveis(self, texto: str, variaveis_extras: Optional[Dict] = None) -> str:
        """
        Substitui variáveis no template pelo valor correspondente
        
        Exemplo: "Olá, bem-vindo ao {nome_produto}!" -> "Olá, bem-vindo ao MONPEC!"
        """
        variaveis = {**self.variaveis}
        if variaveis_extras:
            variaveis.update(variaveis_extras)
        
        resultado = texto
        for chave, valor in variaveis.items():
            resultado = resultado.replace(f'{{{chave}}}', str(valor))
        
        return resultado
    
    def gerar_post(self, template_id: int, variaveis_extras: Optional[Dict] = None, 
                   rede_social: str = 'geral', usuario=None) -> PostGerado:
        """
        Gera um post a partir de um template
        
        Args:
            template_id: ID do template a usar
            variaveis_extras: Dicionário com variáveis extras para substituição
            rede_social: Rede social destino ('instagram', 'facebook', etc.)
            usuario: Usuário que está gerando o post
        
        Returns:
            PostGerado: Instância do post gerado
        """
        try:
            template = TemplatePost.objects.get(id=template_id, ativo=True)
        except TemplatePost.DoesNotExist:
            raise ValueError(f"Template {template_id} não encontrado ou inativo")
        
        # Processar conteúdo
        conteudo_final = self.substituir_variaveis(template.conteudo, variaveis_extras)
        
        # Processar hashtags
        hashtags_lista = []
        if template.hashtags:
            hashtags_lista.extend([h.strip() for h in template.hashtags.split(',')])
        
        # Adicionar hashtags padrão se necessário
        if len(hashtags_lista) < 5:
            hashtags_lista.extend(random.sample(self.HASHTAGS_PADRAO, 
                                              min(5, len(self.HASHTAGS_PADRAO))))
        
        hashtags_final = ' '.join(hashtags_lista[:10])  # Limitar a 10 hashtags
        
        # Determinar rede social
        if rede_social == 'geral' or template.rede_social != 'geral':
            rede_social = template.rede_social
        
        # Criar post
        variaveis_usadas = {**self.variaveis}
        if variaveis_extras:
            variaveis_usadas.update(variaveis_extras)
        
        post = PostGerado.objects.create(
            template=template,
            titulo=f"{template.nome} - {datetime.now().strftime('%d/%m/%Y')}",
            conteudo_final=conteudo_final,
            hashtags_final=hashtags_final,
            rede_social=rede_social,
            tipo_post=template.tipo_post,
            variaveis_usadas=variaveis_usadas,
            status='rascunho',
            criado_por=usuario,
        )
        
        return post
    
    def gerar_post_aleatorio(self, tipo_post: Optional[str] = None, 
                            rede_social: str = 'geral', usuario=None) -> PostGerado:
        """
        Gera um post aleatório de um tipo específico
        
        Args:
            tipo_post: Tipo de post (opcional). Se None, escolhe aleatório
            rede_social: Rede social destino
            usuario: Usuário que está gerando o post
        """
        filtros = {'ativo': True}
        
        if rede_social != 'geral':
            filtros['rede_social__in'] = [rede_social, 'geral']
        
        if tipo_post:
            filtros['tipo_post'] = tipo_post
        
        templates = TemplatePost.objects.filter(**filtros)
        
        if not templates.exists():
            raise ValueError("Nenhum template disponível com os filtros especificados")
        
        template = random.choice(list(templates))
        return self.gerar_post(template.id, rede_social=rede_social, usuario=usuario)
    
    def gerar_posts_semana(self, usuario=None) -> List[PostGerado]:
        """
        Gera posts para uma semana completa (7 posts)
        """
        tipos_semana = [
            'apresentacao',
            'funcionalidade',
            'educacao',
            'prova_social',
            'vendas',
            'engajamento',
            'tendencias'
        ]
        
        posts = []
        for tipo in tipos_semana:
            try:
                post = self.gerar_post_aleatorio(tipo_post=tipo, usuario=usuario)
                posts.append(post)
            except ValueError:
                # Se não houver template do tipo, continua
                continue
        
        return posts


def popular_templates_iniciais():
    """Popula o banco com templates iniciais"""
    
    templates_data = [
        {
            'nome': 'Apresentação Básica',
            'tipo_post': 'apresentacao',
            'rede_social': 'geral',
            'conteudo': '''🐄💼 {nome_produto_completo}

✅ {beneficio_1}
✅ {beneficio_2}
✅ {beneficio_3}
✅ {beneficio_4}
✅ {beneficio_5}

🏆 Sistema completo desenvolvido especialmente para quem leva o agronegócio a sério.

{cta_padrao}

Acesse: {url_site}''',
            'hashtags': '#MONPEC, #GestãoRural, #Agronegócio, #TecnologiaAgrícola, #Pecuária',
        },
        {
            'nome': 'Problema x Solução',
            'tipo_post': 'problema_solucao',
            'rede_social': 'geral',
            'conteudo': '''❌ PROBLEMAS QUE VOCÊ NÃO PRECISA MAIS ENFRENTAR:

🔴 {problema_1}
🔴 {problema_2}
🔴 {problema_3}
🔴 {problema_4}

✅ COM O {nome_produto} VOCÊ TERÁ:

✅ Sistema completo em uma única plataforma
✅ Controle total do inventário e movimentações
✅ Relatórios profissionais para comprovação bancária
✅ Projeções inteligentes baseadas em IA
✅ Tudo organizado e acessível de qualquer lugar

💡 Pare de perder dinheiro por falta de gestão eficiente!

{cta_padrao}''',
            'hashtags': '#GestãoRural, #MONPEC, #Agronegócio, #Eficiência, #Tecnologia',
        },
        {
            'nome': 'Funcionalidade - Projeções',
            'tipo_post': 'funcionalidade',
            'rede_social': 'geral',
            'conteudo': '''🔮 PROJEÇÕES INTELIGENTES - O Futuro do Seu Rebanho

Imagine poder simular o crescimento do seu rebanho pelos próximos 20 anos com um clique?

Com o módulo de Projeções Inteligentes do {nome_produto}:

🎯 Análise automática do perfil da sua fazenda
🤖 IA identifica automaticamente o melhor padrão
📊 Projeções detalhadas de nascimentos, movimentações e receitas

💼 Tome decisões baseadas em dados, não em "achismos"!

{cta_padrao}''',
            'hashtags': '#ProjeçõesPecuárias, #IA, #MONPEC, #GestãoInteligente, #Agronegócio',
        },
        {
            'nome': 'Funcionalidade - Relatórios',
            'tipo_post': 'funcionalidade',
            'rede_social': 'geral',
            'conteudo': '''💰 PRECISA DE EMPRÉSTIMO? O {nome_produto} GERA TUDO!

Conseguir financiamento rural nunca foi tão fácil!

📋 RELATÓRIOS PROFISSIONAIS AUTOMÁTICOS:

✅ Rebanho Consolidado
✅ Bens Imobilizados
✅ DRE Consolidado
✅ Fluxo de Caixa
✅ Relatório Completo para Empréstimo

🏦 Documentação completa que os bancos exigem, gerada automaticamente!

👉 Pare de perder oportunidades por falta de documentação!

Acesse: {url_site}''',
            'hashtags': '#EmpréstimoRural, #Financiamento, #MONPEC, #Relatórios, #Agronegócio',
        },
        {
            'nome': 'Dica Rápida',
            'tipo_post': 'educacao',
            'rede_social': 'geral',
            'conteudo': '''💡 DICA {nome_produto}: Controle de Inventário Eficiente

Um bom inventário é a base de uma gestão rural eficiente!

✅ O que fazer:
1️⃣ Registre TODAS as categorias do rebanho
2️⃣ Atualize mensalmente
3️⃣ Use o sistema para não perder informações

❌ O que evitar:
• Inventários feitos de memória
• Atualizações esporádicas
• Informações desorganizadas

🎯 COM O {nome_produto}:
• Registre tudo em um só lugar
• Receba alertas para atualizações
• Gere relatórios automáticos

💼 A diferença entre sucesso e fracasso está nos detalhes!

👉 Comece agora mesmo! {url_site}''',
            'hashtags': '#DicaGestãoRural, #Inventário, #MONPEC, #Pecuária, #Dicas',
        },
        {
            'nome': 'Pré-Lançamento',
            'tipo_post': 'vendas',
            'rede_social': 'geral',
            'conteudo': '''🚀 PRÉ-LANÇAMENTO {nome_produto} - Garanta Sua Vaga!

O futuro da gestão rural está chegando!

📅 Acesse gratuitamente agora!

🎁 CONDIÇÕES ESPECIAIS:

✅ Acesso gratuito ao sistema
✅ Consultoria personalizada incluída
✅ Treinamento completo
✅ Suporte especializado

💰 ACESSE GRATUITAMENTE e descubra como transformar sua gestão rural!

⏰ Não perca esta oportunidade única.

👉 Cadastre-se agora: {url_site}

💬 Dúvidas? Fale conosco pelo WhatsApp!''',
            'hashtags': '#PréLançamento, #MONPEC, #OfertaEspecial, #GestãoRural, #Agronegócio',
        },
        {
            'nome': 'Pergunta Engajamento',
            'tipo_post': 'engajamento',
            'rede_social': 'instagram',
            'conteudo': '''❓ PERGUNTA DO DIA

Qual é o maior desafio na gestão da sua propriedade rural?

A) 📊 Falta de controle financeiro
B) 🐄 Dificuldade em gerenciar o rebanho
C) 📄 Problemas para obter empréstimos
D) ⏰ Perda de tempo com burocracias
E) 📈 Falta de projeções e planejamento

👉 Comente abaixo com a letra correspondente!

💡 Qualquer que seja seu desafio, o {nome_produto} pode ajudar você a resolver!

🎯 Sistema completo desenvolvido para facilitar a vida do produtor rural.

👉 Quer saber como? Entre em contato!

{url_site}''',
            'hashtags': '#PerguntaDoDia, #GestãoRural, #MONPEC, #Agronegócio, #Engajamento',
        },
    ]
    
    criados = 0
    for template_data in templates_data:
        template, created = TemplatePost.objects.get_or_create(
            nome=template_data['nome'],
            defaults=template_data
        )
        if created:
            criados += 1
    
    return criados


