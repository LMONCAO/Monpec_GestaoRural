#!/usr/bin/env python
"""
Script de Auditoria Completa do Sistema
Identifica erros, arquivos desnecessários e problemas de código
"""
import os
import sys
import re
from pathlib import Path
from collections import defaultdict

# Cores para output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

# Diretório raiz do projeto
BASE_DIR = Path(__file__).parent

# Arquivos que devem estar na raiz (não remover)
ARQUIVOS_ESSENCIAIS = {
    'manage.py', 'requirements.txt', 'README.md', '.gitignore',
    '.env.example', 'Dockerfile', 'docker-compose.yml', 'Procfile',
    'app.yaml', 'runtime.txt', 'wsgi.py', 'asgi.py'
}

# Padrões de arquivos temporários/teste
PADROES_TEMPORARIOS = [
    r'^testar_.*\.py$',
    r'^verificar_.*\.py$',
    r'^corrigir_.*\.py$',
    r'^criar_admin.*\.py$',
    r'^atualizar_.*\.py$',
    r'^aplicar_.*\.py$',
    r'^executar_.*\.py$',
    r'^fix_.*\.py$',
    r'^redefinir_.*\.py$',
    r'^diagnosticar_.*\.py$',
    r'^configurar_.*\.py$',
    r'^autenticar_.*\.py$',
    r'^fazer_.*\.py$',
    r'^listar_.*\.py$',
]

# Problemas de segurança
PADROES_SEGURANCA = [
    (r'password\s*=\s*["\'][^"\']+["\']', 'Senha hardcoded'),
    (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', 'SECRET_KEY hardcoded'),
    (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API Key hardcoded'),
    (r'token\s*=\s*["\'][^"\']+["\']', 'Token hardcoded'),
]

def encontrar_arquivos_temporarios():
    """Encontra arquivos temporários na raiz do projeto"""
    print_header("1. ARQUIVOS TEMPORÁRIOS NA RAIZ")
    
    arquivos_temporarios = []
    arquivos_raiz = [f for f in BASE_DIR.iterdir() if f.is_file() and f.suffix == '.py']
    
    for arquivo in arquivos_raiz:
        nome = arquivo.name
        if nome in ARQUIVOS_ESSENCIAIS:
            continue
        
        # Verificar se corresponde a algum padrão temporário
        for padrao in PADROES_TEMPORARIOS:
            if re.match(padrao, nome, re.IGNORECASE):
                arquivos_temporarios.append(arquivo)
                break
    
    if arquivos_temporarios:
        print_warning(f"Encontrados {len(arquivos_temporarios)} arquivos temporários:")
        for arquivo in sorted(arquivos_temporarios):
            print(f"   - {arquivo.name}")
        return arquivos_temporarios
    else:
        print_success("Nenhum arquivo temporário encontrado na raiz")
        return []

def verificar_problemas_seguranca():
    """Verifica problemas de segurança no código"""
    print_header("2. PROBLEMAS DE SEGURANÇA")
    
    problemas = []
    arquivos_py = list(BASE_DIR.rglob('*.py'))
    
    # Excluir arquivos de migração e __pycache__
    arquivos_py = [f for f in arquivos_py 
                   if '__pycache__' not in str(f) 
                   and 'migrations' not in str(f)]
    
    for arquivo in arquivos_py:
        try:
            conteudo = arquivo.read_text(encoding='utf-8', errors='ignore')
            linhas = conteudo.split('\n')
            
            for num_linha, linha in enumerate(linhas, 1):
                for padrao, descricao in PADROES_SEGURANCA:
                    if re.search(padrao, linha, re.IGNORECASE):
                        # Ignorar comentários e variáveis de ambiente
                        if not linha.strip().startswith('#') and 'os.getenv' not in linha and 'config(' not in linha:
                            problemas.append({
                                'arquivo': arquivo.relative_to(BASE_DIR),
                                'linha': num_linha,
                                'problema': descricao,
                                'codigo': linha.strip()[:80]
                            })
        except Exception as e:
            print_warning(f"Erro ao ler {arquivo}: {e}")
    
    if problemas:
        print_warning(f"Encontrados {len(problemas)} problemas de segurança:")
        for prob in problemas[:20]:  # Limitar a 20 primeiros
            print(f"   {prob['arquivo']}:{prob['linha']} - {prob['problema']}")
            print(f"      {prob['codigo']}")
        if len(problemas) > 20:
            print(f"   ... e mais {len(problemas) - 20} problemas")
        return problemas
    else:
        print_success("Nenhum problema de segurança encontrado")
        return []

def verificar_imports_nao_utilizados():
    """Verifica imports não utilizados (análise básica)"""
    print_header("3. IMPORTS POTENCIALMENTE NÃO UTILIZADOS")
    
    # Esta é uma análise básica - para análise completa seria necessário AST
    print_info("Análise básica de imports (análise completa requer ferramentas especializadas)")
    print_info("Recomendado: usar pylint, flake8 ou autoflake para análise completa")
    
    return []

def verificar_arquivos_duplicados():
    """Verifica arquivos com nomes similares que podem ser duplicados"""
    print_header("4. ARQUIVOS POTENCIALMENTE DUPLICADOS")
    
    arquivos_py = list(BASE_DIR.rglob('*.py'))
    nomes_base = defaultdict(list)
    
    for arquivo in arquivos_py:
        if '__pycache__' not in str(arquivo):
            nome_base = arquivo.stem.lower()
            nomes_base[nome_base].append(arquivo)
    
    duplicados = {k: v for k, v in nomes_base.items() if len(v) > 1}
    
    if duplicados:
        print_warning(f"Encontrados {len(duplicados)} grupos de arquivos com nomes similares:")
        for nome, arquivos in list(duplicados.items())[:10]:
            print(f"   '{nome}':")
            for arquivo in arquivos:
                print(f"      - {arquivo.relative_to(BASE_DIR)}")
        return duplicados
    else:
        print_success("Nenhum arquivo duplicado encontrado")
        return {}

def verificar_todos_fixme():
    """Verifica comentários TODO, FIXME, etc."""
    print_header("5. COMENTÁRIOS TODO/FIXME/XXX")
    
    padroes = [
        (r'TODO', 'TODO'),
        (r'FIXME', 'FIXME'),
        (r'XXX', 'XXX'),
        (r'HACK', 'HACK'),
        (r'BUG', 'BUG'),
    ]
    
    problemas = []
    arquivos_py = list(BASE_DIR.rglob('*.py'))
    arquivos_py = [f for f in arquivos_py if '__pycache__' not in str(f)]
    
    for arquivo in arquivos_py:
        try:
            conteudo = arquivo.read_text(encoding='utf-8', errors='ignore')
            linhas = conteudo.split('\n')
            
            for num_linha, linha in enumerate(linhas, 1):
                for padrao, tipo in padroes:
                    if re.search(padrao, linha, re.IGNORECASE):
                        problemas.append({
                            'arquivo': arquivo.relative_to(BASE_DIR),
                            'linha': num_linha,
                            'tipo': tipo,
                            'codigo': linha.strip()[:80]
                        })
        except Exception as e:
            pass
    
    if problemas:
        print_warning(f"Encontrados {len(problemas)} comentários TODO/FIXME:")
        for prob in problemas[:15]:
            print(f"   {prob['arquivo']}:{prob['linha']} - {prob['tipo']}")
            print(f"      {prob['codigo']}")
        if len(problemas) > 15:
            print(f"   ... e mais {len(problemas) - 15} comentários")
        return problemas
    else:
        print_success("Nenhum comentário TODO/FIXME encontrado")
        return []

def verificar_arquivos_grandes():
    """Verifica arquivos muito grandes que podem precisar de refatoração"""
    print_header("6. ARQUIVOS MUITO GRANDES (>1000 linhas)")
    
    arquivos_grandes = []
    arquivos_py = list(BASE_DIR.rglob('*.py'))
    arquivos_html = list(BASE_DIR.rglob('*.html'))
    
    for arquivo in arquivos_py + arquivos_html:
        if '__pycache__' not in str(arquivo):
            try:
                num_linhas = len(arquivo.read_text(encoding='utf-8', errors='ignore').split('\n'))
                if num_linhas > 1000:
                    arquivos_grandes.append({
                        'arquivo': arquivo.relative_to(BASE_DIR),
                        'linhas': num_linhas
                    })
            except Exception as e:
                pass
    
    if arquivos_grandes:
        print_warning(f"Encontrados {len(arquivos_grandes)} arquivos muito grandes:")
        for item in sorted(arquivos_grandes, key=lambda x: x['linhas'], reverse=True):
            print(f"   {item['arquivo']}: {item['linhas']} linhas")
        return arquivos_grandes
    else:
        print_success("Nenhum arquivo muito grande encontrado")
        return []

def gerar_relatorio(arquivos_temp, problemas_seg, duplicados, todos, arquivos_grandes):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL DE AUDITORIA")
    
    total_problemas = (
        len(arquivos_temp) + 
        len(problemas_seg) + 
        len(duplicados) + 
        len(todos) + 
        len(arquivos_grandes)
    )
    
    print(f"\n📊 RESUMO:")
    print(f"   - Arquivos temporários: {len(arquivos_temp)}")
    print(f"   - Problemas de segurança: {len(problemas_seg)}")
    print(f"   - Arquivos duplicados: {len(duplicados)}")
    print(f"   - Comentários TODO/FIXME: {len(todos)}")
    print(f"   - Arquivos muito grandes: {len(arquivos_grandes)}")
    print(f"\n   TOTAL DE PROBLEMAS: {total_problemas}")
    
    print(f"\n📝 RECOMENDAÇÕES:")
    
    if arquivos_temp:
        print(f"   1. Mover {len(arquivos_temp)} arquivos temporários para pasta 'scripts/' ou removê-los")
    
    if problemas_seg:
        print(f"   2. Corrigir {len(problemas_seg)} problemas de segurança (senhas/tokens hardcoded)")
    
    if duplicados:
        print(f"   3. Revisar {len(duplicados)} grupos de arquivos duplicados")
    
    if todos:
        print(f"   4. Resolver {len(todos)} comentários TODO/FIXME pendentes")
    
    if arquivos_grandes:
        print(f"   5. Refatorar {len(arquivos_grandes)} arquivos muito grandes")
    
    print(f"\n💡 PRÓXIMOS PASSOS:")
    print(f"   1. Revisar o relatório acima")
    print(f"   2. Executar: python limpar_arquivos_temporarios.py (após revisão)")
    print(f"   3. Executar: pylint ou flake8 para análise completa de código")
    print(f"   4. Executar: black ou autopep8 para formatação de código")
    
    # Salvar relatório em arquivo
    relatorio_path = BASE_DIR / 'relatorio_auditoria.txt'
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE AUDITORIA DO SISTEMA\n")
        f.write("="*80 + "\n\n")
        f.write(f"Arquivos temporários encontrados: {len(arquivos_temp)}\n")
        for arquivo in arquivos_temp:
            f.write(f"  - {arquivo.name}\n")
        f.write(f"\nProblemas de segurança: {len(problemas_seg)}\n")
        for prob in problemas_seg[:20]:
            f.write(f"  - {prob['arquivo']}:{prob['linha']} - {prob['problema']}\n")
        f.write(f"\nArquivos duplicados: {len(duplicados)}\n")
        f.write(f"\nComentários TODO/FIXME: {len(todos)}\n")
        f.write(f"\nArquivos muito grandes: {len(arquivos_grandes)}\n")
    
    print_success(f"Relatório salvo em: {relatorio_path}")

def main():
    print_header("AUDITORIA COMPLETA DO SISTEMA")
    print_info("Iniciando análise...\n")
    
    # Executar todas as verificações
    arquivos_temp = encontrar_arquivos_temporarios()
    problemas_seg = verificar_problemas_seguranca()
    duplicados = verificar_arquivos_duplicados()
    todos = verificar_todos_fixme()
    arquivos_grandes = verificar_arquivos_grandes()
    
    # Gerar relatório
    gerar_relatorio(arquivos_temp, problemas_seg, duplicados, todos, arquivos_grandes)
    
    print_header("AUDITORIA CONCLUÍDA")

if __name__ == '__main__':
    main()






