"""
Script para listar todas as tabelas criadas no PostgreSQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def listar_tabelas():
    """Lista todas as tabelas criadas no banco de dados"""
    with connection.cursor() as cursor:
        # Obter todas as tabelas do schema público
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tabelas = cursor.fetchall()
        
        print("\n" + "="*70)
        print("TABELAS CRIADAS NO BANCO DE DADOS POSTGRESQL")
        print("="*70)
        print(f"\nTotal de tabelas: {len(tabelas)}\n")
        
        tabelas_django = []
        tabelas_app = []
        outras = []
        
        for nome_tabela, in tabelas:
            if nome_tabela.startswith('django_'):
                tabelas_django.append(nome_tabela)
            elif nome_tabela.startswith('gestao_rural_'):
                tabelas_app.append(nome_tabela)
            else:
                outras.append(nome_tabela)
        
        print(f"📦 Tabelas do Django ({len(tabelas_django)}):")
        for i, nome in enumerate(tabelas_django, 1):
            print(f"   {i:3d}. {nome}")
        
        print(f"\n📊 Tabelas do App gestao_rural ({len(tabelas_app)}):")
        for i, nome in enumerate(tabelas_app, 1):
            # Contar registros
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{nome}";')
                count = cursor.fetchone()[0]
                print(f"   {i:3d}. {nome:50s} ({count:6d} registros)")
            except Exception:
                print(f"   {i:3d}. {nome}")
        
        if outras:
            print(f"\n📋 Outras tabelas ({len(outras)}):")
            for i, nome in enumerate(outras, 1):
                print(f"   {i:3d}. {nome}")
        
        print("\n" + "="*70)
        print(f"✅ Total: {len(tabelas)} tabelas criadas com sucesso!")
        print("="*70 + "\n")

if __name__ == '__main__':
    try:
        # Verificar conexão
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Conectado ao PostgreSQL: {version.split(',')[0]}\n")
        
        listar_tabelas()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()







