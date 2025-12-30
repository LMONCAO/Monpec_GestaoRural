#!/usr/bin/env python
"""
Script de Setup Completo do Sistema
Executa todas as configurações e melhorias automaticamente
"""
import os
import shutil
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
SCRIPTS_DIR.mkdir(exist_ok=True)

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

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

# Padrões de arquivos temporários
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
    r'^create_superuser\.py$',
]

ARQUIVOS_ESSENCIAIS = {
    'manage.py', 'requirements.txt', 'README.md', '.gitignore',
    'Dockerfile', 'docker-compose.yml', 'Procfile',
    'app.yaml', 'runtime.txt', 'wsgi.py', 'asgi.py',
    'auditoria_sistema.py', 'limpar_arquivos_temporarios.py',
    'RELATORIO_AUDITORIA.md', 'GUIA_REFATORACAO.md',
    'APLICAR_MELHORIAS.py', 'corrigir_problemas_seguranca.py',
    'SETUP_COMPLETO.py'
}

def passo1_criar_env():
    """Criar arquivo .env se não existir"""
    print_header("PASSO 1: Configurando Variáveis de Ambiente")
    
    env_file = BASE_DIR / '.env'
    env_example = BASE_DIR / '.env.example'
    
    if env_file.exists():
        print_warning("Arquivo .env já existe. Pulando criação.")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Arquivo .env criado a partir do .env.example")
        print_warning("⚠️  IMPORTANTE: Edite o arquivo .env com seus valores reais!")
        return True
    else:
        print_error("Arquivo .env.example não encontrado. Criando .env básico...")
        # Criar .env básico
        env_content = """# Configurações do Sistema MonPEC
# ⚠️ NUNCA commite este arquivo com valores reais!

DEBUG=True
SECRET_KEY=sua-secret-key-aqui

# Banco de Dados
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=sua-senha-aqui
DB_HOST=localhost
DB_PORT=5432

# Administrador
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@monpec.com.br
ADMIN_PASSWORD=sua-senha-admin-aqui

# Demo
DEMO_USER_PASSWORD=monpec

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=seu-token-aqui
MERCADOPAGO_PUBLIC_KEY=sua-public-key-aqui
"""
        env_file.write_text(env_content, encoding='utf-8')
        print_success("Arquivo .env básico criado")
        print_warning("⚠️  Edite o arquivo .env com seus valores reais!")
        return True

def passo2_organizar_arquivos():
    """Organizar arquivos temporários"""
    print_header("PASSO 2: Organizando Arquivos Temporários")
    
    arquivos_temp = []
    arquivos_raiz = [f for f in BASE_DIR.iterdir() if f.is_file() and f.suffix == '.py']
    
    for arquivo in arquivos_raiz:
        nome = arquivo.name
        if nome in ARQUIVOS_ESSENCIAIS:
            continue
        
        for padrao in PADROES_TEMPORARIOS:
            if re.match(padrao, nome, re.IGNORECASE):
                arquivos_temp.append(arquivo)
                break
    
    if not arquivos_temp:
        print_success("Nenhum arquivo temporário encontrado na raiz")
        return True
    
    print_info(f"Encontrados {len(arquivos_temp)} arquivos temporários")
    movidos = 0
    
    for arquivo in arquivos_temp:
        try:
            destino = SCRIPTS_DIR / arquivo.name
            if destino.exists():
                base = arquivo.stem
                extensao = arquivo.suffix
                contador = 1
                while destino.exists():
                    destino = SCRIPTS_DIR / f"{base}_{contador}{extensao}"
                    contador += 1
            
            shutil.move(str(arquivo), str(destino))
            print_success(f"Movido: {arquivo.name} -> scripts/{destino.name}")
            movidos += 1
        except Exception as e:
            print_error(f"Erro ao mover {arquivo.name}: {e}")
    
    print_success(f"{movidos} arquivo(s) movido(s) para scripts/")
    return True

def passo3_instalar_ferramentas():
    """Instalar ferramentas de qualidade"""
    print_header("PASSO 3: Instalando Ferramentas de Qualidade")
    
    requirements_dev = BASE_DIR / 'requirements-dev.txt'
    
    if not requirements_dev.exists():
        print_warning("requirements-dev.txt não encontrado. Pulando instalação.")
        return False
    
    print_info("Instalando ferramentas de desenvolvimento...")
    print_warning("Isso pode levar alguns minutos...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_dev)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print_success("Ferramentas de qualidade instaladas com sucesso!")
            return True
        else:
            print_warning("Alguns pacotes podem não ter sido instalados:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("Timeout ao instalar ferramentas. Tente manualmente: pip install -r requirements-dev.txt")
        return False
    except Exception as e:
        print_error(f"Erro ao instalar ferramentas: {e}")
        print_info("Tente manualmente: pip install -r requirements-dev.txt")
        return False

def passo4_formatar_codigo():
    """Formatar código com black e isort"""
    print_header("PASSO 4: Formatando Código")
    
    # Verificar se black está instalado
    try:
        subprocess.run([sys.executable, '-m', 'black', '--version'], 
                      capture_output=True, check=True)
        black_instalado = True
    except:
        black_instalado = False
        print_warning("Black não está instalado. Pulando formatação.")
    
    if black_instalado:
        print_info("Formatando código com Black...")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'black', '--check', 'gestao_rural/'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print_info("Aplicando formatação...")
                subprocess.run(
                    [sys.executable, '-m', 'black', 'gestao_rural/'],
                    timeout=120
                )
                print_success("Código formatado com Black")
            else:
                print_success("Código já está formatado")
        except Exception as e:
            print_warning(f"Erro ao formatar: {e}")
    
    # Verificar se isort está instalado
    try:
        subprocess.run([sys.executable, '-m', 'isort', '--version'], 
                      capture_output=True, check=True)
        isort_instalado = True
    except:
        isort_instalado = False
        print_warning("Isort não está instalado. Pulando organização de imports.")
    
    if isort_instalado:
        print_info("Organizando imports com Isort...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'isort', 'gestao_rural/'],
                timeout=60
            )
            print_success("Imports organizados com Isort")
        except Exception as e:
            print_warning(f"Erro ao organizar imports: {e}")
    
    return True

def passo5_verificar_configuracoes():
    """Verificar se todas as configurações estão corretas"""
    print_header("PASSO 5: Verificando Configurações")
    
    arquivos_config = {
        '.pylintrc': 'Pylint',
        '.flake8': 'Flake8',
        'pyproject.toml': 'Black/Isort',
        'requirements-dev.txt': 'Dependências de desenvolvimento',
    }
    
    todos_ok = True
    for arquivo, nome in arquivos_config.items():
        caminho = BASE_DIR / arquivo
        if caminho.exists():
            print_success(f"{nome} configurado")
        else:
            print_warning(f"{nome} não encontrado ({arquivo})")
            todos_ok = False
    
    return todos_ok

def main():
    print_header("SETUP COMPLETO DO SISTEMA MONPEC")
    print_info("Este script irá configurar tudo automaticamente...")
    print()
    
    resultados = {
        'env': passo1_criar_env(),
        'arquivos': passo2_organizar_arquivos(),
        'ferramentas': passo3_instalar_ferramentas(),
        'formatação': passo4_formatar_codigo(),
        'configurações': passo5_verificar_configuracoes(),
    }
    
    print_header("RESUMO DO SETUP")
    
    for passo, sucesso in resultados.items():
        if sucesso:
            print_success(f"PASSO '{passo}': Concluído")
        else:
            print_warning(f"PASSO '{passo}': Concluído com avisos")
    
    print()
    print_header("PRÓXIMOS PASSOS MANUAIS")
    print()
    print("1. Edite o arquivo .env com seus valores reais:")
    print("   - SECRET_KEY (gere uma nova)")
    print("   - ADMIN_PASSWORD")
    print("   - Configurações do banco de dados")
    print("   - Tokens do Mercado Pago")
    print()
    print("2. Execute análise de código:")
    print("   pylint gestao_rural/")
    print("   flake8 gestao_rural/")
    print()
    print("3. Revise os arquivos em scripts/ e remova os desnecessários")
    print()
    print("4. Teste o sistema:")
    print("   python manage.py runserver")
    print()
    print_header("SETUP CONCLUÍDO!")
    print()
    print_success("Sistema configurado e pronto para uso!")

if __name__ == '__main__':
    main()






