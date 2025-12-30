#!/usr/bin/env python
"""
Script para limpar e organizar arquivos temporários do projeto
Move arquivos temporários para pasta scripts/ ou remove (com confirmação)
"""
import os
import shutil
from pathlib import Path

# Diretório raiz do projeto
BASE_DIR = Path(__file__).parent

# Arquivos que devem estar na raiz (não remover)
ARQUIVOS_ESSENCIAIS = {
    'manage.py', 'requirements.txt', 'README.md', '.gitignore',
    '.env.example', 'Dockerfile', 'docker-compose.yml', 'Procfile',
    'app.yaml', 'runtime.txt', 'wsgi.py', 'asgi.py', 'auditoria_sistema.py',
    'limpar_arquivos_temporarios.py', 'RELATORIO_AUDITORIA.md'
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
    r'^create_superuser\.py$',
]

def encontrar_arquivos_temporarios():
    """Encontra arquivos temporários na raiz"""
    import re
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
    
    return arquivos_temporarios

def main():
    print("="*80)
    print("LIMPEZA DE ARQUIVOS TEMPORÁRIOS")
    print("="*80)
    print()
    
    arquivos_temp = encontrar_arquivos_temporarios()
    
    if not arquivos_temp:
        print("✅ Nenhum arquivo temporário encontrado!")
        return
    
    print(f"⚠️  Encontrados {len(arquivos_temp)} arquivos temporários:")
    print()
    for i, arquivo in enumerate(arquivos_temp, 1):
        print(f"  {i}. {arquivo.name}")
    print()
    
    # Criar pasta scripts/ se não existir
    scripts_dir = BASE_DIR / 'scripts'
    scripts_dir.mkdir(exist_ok=True)
    
    print(f"📁 Os arquivos serão movidos para: {scripts_dir}")
    print()
    resposta = input("Deseja continuar? (s/n): ").strip().lower()
    
    if resposta != 's':
        print("❌ Operação cancelada.")
        return
    
    # Mover arquivos
    movidos = 0
    erros = 0
    
    for arquivo in arquivos_temp:
        try:
            destino = scripts_dir / arquivo.name
            # Se já existir, adicionar sufixo
            if destino.exists():
                base = arquivo.stem
                extensao = arquivo.suffix
                contador = 1
                while destino.exists():
                    destino = scripts_dir / f"{base}_{contador}{extensao}"
                    contador += 1
            
            shutil.move(str(arquivo), str(destino))
            print(f"✅ Movido: {arquivo.name} -> scripts/{destino.name}")
            movidos += 1
        except Exception as e:
            print(f"❌ Erro ao mover {arquivo.name}: {e}")
            erros += 1
    
    print()
    print("="*80)
    print(f"✅ Concluído! {movidos} arquivo(s) movido(s), {erros} erro(s)")
    print("="*80)
    print()
    print("💡 Dica: Revise os arquivos em scripts/ e remova os que não são mais necessários")

if __name__ == '__main__':
    main()






