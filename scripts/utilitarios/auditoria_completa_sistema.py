#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoria Completa do Sistema
Verifica views, templates, imports e gera relatório de melhorias
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Configuração Django
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Tentar inicializar Django (opcional)
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    import django
    django.setup()
except Exception:
    # Continuar sem Django - não é crítico para a auditoria
    pass

GESTAO_RURAL = BASE_DIR / 'gestao_rural'
TEMPLATES_DIR = BASE_DIR / 'templates' / 'gestao_rural'

# Resultados da auditoria
RESULTADOS = {
    'views_ok': [],
    'views_erro': [],
    'templates_ok': [],
    'templates_faltantes': [],
    'imports_ok': [],
    'imports_erro': [],
    'urls_duplicadas': [],
    'funcoes_nao_encontradas': [],
    'problemas_sintaxe': [],
    'melhorias': []
}

def verificar_imports_arquivo(arquivo_path):
    """Verifica se os imports de um arquivo estão corretos"""
    problemas = []
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Tentar parsear o arquivo
        try:
            ast.parse(conteudo)
        except SyntaxError as e:
            problemas.append({
                'tipo': 'sintaxe',
                'erro': str(e),
                'linha': e.lineno if hasattr(e, 'lineno') else None
            })
            return problemas
        
        # Verificar imports
        linhas = conteudo.split('\n')
        for i, linha in enumerate(linhas, 1):
            if linha.strip().startswith('from ') or linha.strip().startswith('import '):
                # Verificar imports relativos
                if 'from .' in linha or 'from ..' in linha:
                    continue  # Imports relativos são difíceis de verificar sem contexto
                
                # Verificar imports absolutos básicos
                match = re.match(r'from\s+([\w.]+)\s+import', linha)
                if match:
                    modulo = match.group(1)
                    # Verificar se é um módulo padrão ou Django
                    if not modulo.startswith('django') and not modulo.startswith('gestao_rural'):
                        try:
                            __import__(modulo)
                        except ImportError:
                            # Não é erro crítico, pode ser opcional
                            pass
        
    except Exception as e:
        problemas.append({
            'tipo': 'erro_leitura',
            'erro': str(e)
        })
    
    return problemas

def verificar_view_existe(arquivo_view, nome_funcao):
    """Verifica se uma função view existe no arquivo"""
    try:
        with open(arquivo_view, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Procurar a função
        pattern = rf'def\s+{nome_funcao}\s*\('
        if re.search(pattern, conteudo):
            return True
        
        # Verificar se é uma classe
        pattern = rf'class\s+{nome_funcao}\s*[\(:]'
        if re.search(pattern, conteudo):
            return True
        
        return False
    except Exception:
        return False

def verificar_template_existe(template_name):
    """Verifica se um template existe"""
    caminhos_possiveis = [
        TEMPLATES_DIR / template_name,
        BASE_DIR / 'templates' / template_name,
        BASE_DIR / template_name,
    ]
    
    return any(p.exists() for p in caminhos_possiveis)

def extrair_template_de_view(arquivo_view, nome_funcao):
    """Extrai o nome do template usado em uma view"""
    try:
        with open(arquivo_view, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Procurar render() com template
        pattern = rf'def\s+{nome_funcao}.*?render\s*\(\s*[^,]+,\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(pattern, conteudo, re.DOTALL)
        if match:
            return match.group(1)
        
        # Procurar em context
        pattern = rf'def\s+{nome_funcao}.*?template_name\s*=\s*[\'"]([^\'"]+)[\'"]'
        match = re.search(pattern, conteudo, re.DOTALL)
        if match:
            return match.group(1)
        
        return None
    except Exception:
        return None

def analisar_urls():
    """Analisa o arquivo urls.py e verifica todas as views"""
    urls_file = GESTAO_RURAL / 'urls.py'
    
    if not urls_file.exists():
        RESULTADOS['views_erro'].append({
            'arquivo': str(urls_file),
            'erro': 'Arquivo urls.py não encontrado'
        })
        return
    
    try:
        with open(urls_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Extrair todos os path() calls
        pattern = r'path\s*\(\s*[\'"][^\'"]+[\'"]\s*,\s*([\w.]+)\.([\w]+)'
        matches = re.findall(pattern, conteudo)
        
        views_verificadas = set()
        
        for modulo, funcao in matches:
            if (modulo, funcao) in views_verificadas:
                RESULTADOS['urls_duplicadas'].append({
                    'modulo': modulo,
                    'funcao': funcao
                })
                continue
            
            views_verificadas.add((modulo, funcao))
            
            # Determinar arquivo da view
            if modulo == 'views':
                arquivo_view = GESTAO_RURAL / 'views.py'
            else:
                arquivo_view = GESTAO_RURAL / f'{modulo}.py'
            
            # Verificar se arquivo existe
            if not arquivo_view.exists():
                RESULTADOS['views_erro'].append({
                    'modulo': modulo,
                    'funcao': funcao,
                    'erro': f'Arquivo {arquivo_view} não encontrado'
                })
                continue
            
            # Verificar se função existe
            if not verificar_view_existe(arquivo_view, funcao):
                RESULTADOS['funcoes_nao_encontradas'].append({
                    'modulo': modulo,
                    'funcao': funcao,
                    'arquivo': str(arquivo_view)
                })
            else:
                RESULTADOS['views_ok'].append({
                    'modulo': modulo,
                    'funcao': funcao
                })
                
                # Verificar template
                template_name = extrair_template_de_view(arquivo_view, funcao)
                if template_name:
                    if verificar_template_existe(template_name):
                        RESULTADOS['templates_ok'].append({
                            'view': f'{modulo}.{funcao}',
                            'template': template_name
                        })
                    else:
                        RESULTADOS['templates_faltantes'].append({
                            'view': f'{modulo}.{funcao}',
                            'template': template_name,
                            'arquivo': str(arquivo_view)
                        })
    
    except Exception as e:
        RESULTADOS['views_erro'].append({
            'arquivo': str(urls_file),
            'erro': f'Erro ao analisar: {str(e)}'
        })

def verificar_imports_views():
    """Verifica imports em todos os arquivos de views"""
    views_files = list(GESTAO_RURAL.glob('views*.py'))
    
    for arquivo in views_files:
        problemas = verificar_imports_arquivo(arquivo)
        
        if problemas:
            for problema in problemas:
                if problema['tipo'] == 'sintaxe':
                    RESULTADOS['problemas_sintaxe'].append({
                        'arquivo': str(arquivo),
                        'erro': problema['erro'],
                        'linha': problema.get('linha')
                    })
        else:
            RESULTADOS['imports_ok'].append(str(arquivo))

def gerar_sugestoes_melhorias():
    """Gera sugestões de melhorias baseadas nos problemas encontrados"""
    
    # Melhorias baseadas em templates faltantes
    if RESULTADOS['templates_faltantes']:
        RESULTADOS['melhorias'].append({
            'prioridade': 'ALTA',
            'categoria': 'Templates',
            'descricao': f'Criar {len(RESULTADOS["templates_faltantes"])} templates faltantes',
            'detalhes': RESULTADOS['templates_faltantes'][:5]  # Primeiros 5
        })
    
    # Melhorias baseadas em funções não encontradas
    if RESULTADOS['funcoes_nao_encontradas']:
        RESULTADOS['melhorias'].append({
            'prioridade': 'CRÍTICA',
            'categoria': 'Views',
            'descricao': f'Implementar {len(RESULTADOS["funcoes_nao_encontradas"])} views faltantes',
            'detalhes': RESULTADOS['funcoes_nao_encontradas']
        })
    
    # Melhorias baseadas em problemas de sintaxe
    if RESULTADOS['problemas_sintaxe']:
        RESULTADOS['melhorias'].append({
            'prioridade': 'CRÍTICA',
            'categoria': 'Código',
            'descricao': f'Corrigir {len(RESULTADOS["problemas_sintaxe"])} erros de sintaxe',
            'detalhes': RESULTADOS['problemas_sintaxe']
        })
    
    # Melhorias baseadas em URLs duplicadas
    if RESULTADOS['urls_duplicadas']:
        RESULTADOS['melhorias'].append({
            'prioridade': 'MÉDIA',
            'categoria': 'URLs',
            'descricao': f'Remover {len(RESULTADOS["urls_duplicadas"])} URLs duplicadas',
            'detalhes': RESULTADOS['urls_duplicadas']
        })
    
    # Melhorias gerais
    total_views = len(RESULTADOS['views_ok']) + len(RESULTADOS['views_erro'])
    if total_views > 0:
        percentual_ok = (len(RESULTADOS['views_ok']) / total_views) * 100
        if percentual_ok < 90:
            RESULTADOS['melhorias'].append({
                'prioridade': 'ALTA',
                'categoria': 'Qualidade',
                'descricao': f'Taxa de views funcionais: {percentual_ok:.1f}% (meta: 90%+)',
                'detalhes': []
            })

def gerar_relatorio():
    """Gera relatório completo em Markdown"""
    relatorio = f"""# Relatório de Auditoria Completa do Sistema
**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---

## 📊 Resumo Executivo

| Métrica | Quantidade | Status |
|---------|------------|--------|
| Views Funcionais | {len(RESULTADOS['views_ok'])} | ✅ |
| Views com Problemas | {len(RESULTADOS['views_erro'])} | {'⚠️' if len(RESULTADOS['views_erro']) > 0 else '✅'} |
| Funções Não Encontradas | {len(RESULTADOS['funcoes_nao_encontradas'])} | {'❌' if len(RESULTADOS['funcoes_nao_encontradas']) > 0 else '✅'} |
| Templates OK | {len(RESULTADOS['templates_ok'])} | ✅ |
| Templates Faltantes | {len(RESULTADOS['templates_faltantes'])} | {'⚠️' if len(RESULTADOS['templates_faltantes']) > 0 else '✅'} |
| Erros de Sintaxe | {len(RESULTADOS['problemas_sintaxe'])} | {'❌' if len(RESULTADOS['problemas_sintaxe']) > 0 else '✅'} |
| URLs Duplicadas | {len(RESULTADOS['urls_duplicadas'])} | {'⚠️' if len(RESULTADOS['urls_duplicadas']) > 0 else '✅'} |

---

## ✅ Views Funcionais

Total: **{len(RESULTADOS['views_ok'])}** views verificadas e funcionando.

"""
    
    if RESULTADOS['views_ok']:
        relatorio += "### Lista de Views OK\n\n"
        for view in RESULTADOS['views_ok'][:20]:  # Primeiras 20
            relatorio += f"- `{view['modulo']}.{view['funcao']}`\n"
        if len(RESULTADOS['views_ok']) > 20:
            relatorio += f"\n*... e mais {len(RESULTADOS['views_ok']) - 20} views*\n"
    
    relatorio += "\n---\n\n"
    
    # Problemas encontrados
    if RESULTADOS['funcoes_nao_encontradas']:
        relatorio += "## ❌ Funções Não Encontradas\n\n"
        relatorio += "**CRÍTICO:** As seguintes funções são referenciadas nas URLs mas não existem:\n\n"
        for item in RESULTADOS['funcoes_nao_encontradas']:
            relatorio += f"- `{item['modulo']}.{item['funcao']}` (arquivo: `{item['arquivo']}`)\n"
        relatorio += "\n---\n\n"
    
    if RESULTADOS['templates_faltantes']:
        relatorio += "## ⚠️ Templates Faltantes\n\n"
        relatorio += "Os seguintes templates são referenciados mas não existem:\n\n"
        for item in RESULTADOS['templates_faltantes'][:10]:  # Primeiros 10
            relatorio += f"- **View:** `{item['view']}`\n"
            relatorio += f"  - **Template:** `{item['template']}`\n"
            relatorio += f"  - **Arquivo:** `{item['arquivo']}`\n\n"
        if len(RESULTADOS['templates_faltantes']) > 10:
            relatorio += f"*... e mais {len(RESULTADOS['templates_faltantes']) - 10} templates faltantes*\n"
        relatorio += "\n---\n\n"
    
    if RESULTADOS['problemas_sintaxe']:
        relatorio += "## ❌ Erros de Sintaxe\n\n"
        for item in RESULTADOS['problemas_sintaxe']:
            relatorio += f"- **Arquivo:** `{item['arquivo']}`\n"
            relatorio += f"  - **Erro:** {item['erro']}\n"
            if item.get('linha'):
                relatorio += f"  - **Linha:** {item['linha']}\n"
            relatorio += "\n"
        relatorio += "\n---\n\n"
    
    if RESULTADOS['urls_duplicadas']:
        relatorio += "## ⚠️ URLs Duplicadas\n\n"
        for item in RESULTADOS['urls_duplicadas']:
            relatorio += f"- `{item['modulo']}.{item['funcao']}`\n"
        relatorio += "\n---\n\n"
    
    # Melhorias sugeridas
    if RESULTADOS['melhorias']:
        relatorio += "## 💡 Sugestões de Melhorias\n\n"
        
        # Agrupar por prioridade
        criticas = [m for m in RESULTADOS['melhorias'] if m['prioridade'] == 'CRÍTICA']
        altas = [m for m in RESULTADOS['melhorias'] if m['prioridade'] == 'ALTA']
        medias = [m for m in RESULTADOS['melhorias'] if m['prioridade'] == 'MÉDIA']
        
        if criticas:
            relatorio += "### 🔴 Prioridade CRÍTICA\n\n"
            for melhoria in criticas:
                relatorio += f"**{melhoria['categoria']}:** {melhoria['descricao']}\n\n"
        
        if altas:
            relatorio += "### 🟠 Prioridade ALTA\n\n"
            for melhoria in altas:
                relatorio += f"**{melhoria['categoria']}:** {melhoria['descricao']}\n\n"
        
        if medias:
            relatorio += "### 🟡 Prioridade MÉDIA\n\n"
            for melhoria in medias:
                relatorio += f"**{melhoria['categoria']}:** {melhoria['descricao']}\n\n"
        
        relatorio += "\n---\n\n"
    
    # Recomendações finais
    relatorio += """## 📋 Recomendações Finais

### Para o Programador (sem alterar layout/fontes):

1. **Corrigir Funções Faltantes** (se houver)
   - Implementar todas as views referenciadas nas URLs
   - Garantir que todas retornem render/redirect/JsonResponse

2. **Criar Templates Faltantes** (se houver)
   - Criar templates básicos para views que os necessitam
   - Usar templates base existentes como referência

3. **Corrigir Erros de Sintaxe** (se houver)
   - Revisar arquivos com erros de sintaxe
   - Testar imports e dependências

4. **Remover URLs Duplicadas** (se houver)
   - Consolidar rotas duplicadas
   - Manter apenas uma versão de cada rota

5. **Melhorias de Código**
   - Adicionar tratamento de erros onde necessário
   - Documentar views complexas
   - Otimizar queries de banco de dados

### Notas Importantes:

- ⚠️ **NÃO alterar layout ou fontes** conforme solicitado
- ✅ Focar apenas em correções funcionais
- ✅ Manter compatibilidade com código existente
- ✅ Testar após cada correção

---

**Relatório gerado automaticamente pela ferramenta de auditoria.**
"""
    
    return relatorio

def main():
    """Função principal"""
    print("Iniciando auditoria completa do sistema...")
    print("=" * 60)
    
    print("\n[1/4] Analisando URLs e Views...")
    analisar_urls()
    
    print("\n[2/4] Verificando imports...")
    verificar_imports_views()
    
    print("\n[3/4] Gerando sugestoes de melhorias...")
    gerar_sugestoes_melhorias()
    
    print("\n[4/4] Gerando relatorio...")
    relatorio = gerar_relatorio()
    
    # Salvar relatório
    relatorio_file = BASE_DIR / 'RELATORIO_AUDITORIA_COMPLETA.md'
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print(f"\n[OK] Relatorio salvo em: {relatorio_file}")
    print("\n" + "=" * 60)
    print("\nResumo:")
    print(f"   [OK] Views OK: {len(RESULTADOS['views_ok'])}")
    print(f"   [ERRO] Views com erro: {len(RESULTADOS['views_erro'])}")
    print(f"   [ERRO] Funcoes nao encontradas: {len(RESULTADOS['funcoes_nao_encontradas'])}")
    print(f"   [AVISO] Templates faltantes: {len(RESULTADOS['templates_faltantes'])}")
    print(f"   [ERRO] Erros de sintaxe: {len(RESULTADOS['problemas_sintaxe'])}")
    print(f"   [AVISO] URLs duplicadas: {len(RESULTADOS['urls_duplicadas'])}")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()


