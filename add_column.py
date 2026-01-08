import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(gestao_rural_produtorrural);")
    columns = [col[1] for col in cursor.fetchall()]

    print(f"Colunas existentes: {columns}")

    # Colunas que podem estar faltando
    colunas_para_adicionar = [
        ('vai_emitir_nfe', 'BOOLEAN DEFAULT 0'),
        ('certificado_digital', 'TEXT'),
        ('senha_certificado', 'TEXT'),
        ('certificado_valido_ate', 'DATE'),
        ('certificado_tipo', 'TEXT'),
        ('inscricao_estadual', 'TEXT'),
        ('documento', 'TEXT'),
        ('bairro', 'TEXT'),
        ('cep', 'TEXT'),
        ('cidade', 'TEXT'),
        ('estado', 'TEXT'),
        ('pais', 'TEXT DEFAULT \'Brasil\''),
        ('complemento', 'TEXT'),
        ('numero', 'TEXT'),
        ('logradouro', 'TEXT'),
        ('tipo_pessoa', 'TEXT DEFAULT \'PJ\''),
        ('razao_social', 'TEXT'),
        ('nome_fantasia', 'TEXT'),
        ('data_fundacao', 'DATE'),
        ('capital_social', 'DECIMAL(15,2) DEFAULT 0'),
        ('cnae_principal', 'TEXT'),
        ('cnae_secundario', 'TEXT'),
        ('porte_empresa', 'TEXT'),
        ('situacao_cadastral', 'TEXT'),
        ('data_situacao_cadastral', 'DATE'),
        ('motivo_situacao_cadastral', 'TEXT'),
        ('situacao_especial', 'TEXT'),
        ('data_situacao_especial', 'DATE'),
    ]

    for coluna, tipo in colunas_para_adicionar:
        if coluna not in columns:
            try:
                cursor.execute(f"ALTER TABLE gestao_rural_produtorrural ADD COLUMN {coluna} {tipo};")
                print(f"Coluna '{coluna}' adicionada com sucesso!")
            except Exception as e:
                print(f"Erro ao adicionar coluna '{coluna}': {e}")
        else:
            print(f"Coluna '{coluna}' já existe.")

    conn.commit()
    conn.close()
except Exception as e:
    print(f'Erro geral: {e}')
