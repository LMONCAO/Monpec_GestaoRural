"""
Script para adicionar a coluna tipo_trabalho na tabela CurralSessao
Uso: python311\python.exe adicionar_coluna_tipo_trabalho.py
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("ADICIONANDO COLUNA TIPO_TRABALHO")
print("=" * 60)
print()

# Verificar se a coluna já existe
try:
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(gestao_rural_curralsessao);")
        colunas = cursor.fetchall()
        colunas_existentes = [col[1] for col in colunas]
        
        # Lista de colunas que devem existir (da migração 0048)
        colunas_necessarias = {
            'tipo_trabalho': "VARCHAR(20) DEFAULT 'COLETA_DADOS'",
            'nome_lote': "VARCHAR(100) NULL",
            'pasto_origem': "VARCHAR(200) NULL",
            'quantidade_esperada': "INTEGER NULL",
        }
        
        colunas_adicionadas = []
        
        for coluna, definicao in colunas_necessarias.items():
            if coluna in colunas_existentes:
                print(f"[OK] A coluna {coluna} ja existe!")
            else:
                print(f"[AVISO] A coluna {coluna} nao existe. Adicionando...")
                
                # Adicionar a coluna
                sql = f"""
                ALTER TABLE gestao_rural_curralsessao 
                ADD COLUMN {coluna} {definicao};
                """
                
                cursor.execute(sql)
                print(f"[OK] Coluna {coluna} adicionada com sucesso!")
                colunas_adicionadas.append(coluna)
        
        # Atualizar registros existentes com valor padrão para tipo_trabalho
        if 'tipo_trabalho' in colunas_adicionadas or 'tipo_trabalho' not in colunas_existentes:
            cursor.execute("""
                UPDATE gestao_rural_curralsessao 
                SET tipo_trabalho = 'COLETA_DADOS' 
                WHERE tipo_trabalho IS NULL;
            """)
            print("[OK] Registros existentes atualizados com valor padrao para tipo_trabalho!")
            
except Exception as e:
    print(f"[ERRO] Nao foi possivel adicionar a coluna: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("[SUCESSO] Operacao concluida!")
print("=" * 60)

