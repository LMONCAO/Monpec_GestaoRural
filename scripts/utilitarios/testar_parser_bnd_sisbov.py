# -*- coding: utf-8 -*-
"""
Script para testar o parser BND SISBOV com o PDF de teste gerado
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_rural.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from gestao_rural.bnd_sisbov_parser import BNDSisbovParser

def testar_parser_pdf(pdf_path):
    """Testa o parser com um arquivo PDF"""
    
    if not os.path.exists(pdf_path):
        print(f"[ERRO] Arquivo nao encontrado: {pdf_path}")
        return False
    
    print(f"\n{'='*60}")
    print(f"TESTE DO PARSER BND SISBOV")
    print(f"{'='*60}")
    print(f"\nArquivo: {pdf_path}")
    print(f"Tamanho: {os.path.getsize(pdf_path)} bytes")
    
    try:
        # Ler arquivo PDF
        with open(pdf_path, 'rb') as f:
            conteudo = f.read()
        
        # Criar objeto UploadedFile simulado
        arquivo = SimpleUploadedFile(
            name=os.path.basename(pdf_path),
            content=conteudo,
            content_type='application/pdf'
        )
        
        # Criar parser e extrair dados
        print("\n[1/3] Criando parser...")
        parser = BNDSisbovParser()
        
        print("[2/3] Extraindo dados do PDF...")
        dados_extraidos = parser.extrair_dados_pdf(arquivo)
        
        print("[3/3] Processamento concluido!")
        
        # Exibir resultados
        print(f"\n{'='*60}")
        print("RESULTADOS DA EXTRACAO")
        print(f"{'='*60}")
        
        # Informações da propriedade
        info_prop = dados_extraidos.get('informacoes_propriedade', {})
        print(f"\n[PROPRIEDADE]")
        print(f"  Nome: {info_prop.get('nome_propriedade', 'N/A')}")
        print(f"  CNPJ/CPF: {info_prop.get('cnpj_cpf', 'N/A')}")
        print(f"  Data Emissao: {info_prop.get('data_emissao', 'N/A')}")
        
        # Animais extraídos
        animais = dados_extraidos.get('animais', [])
        total_animais = len(animais)
        
        print(f"\n[ANIMAIS]")
        print(f"  Total extraido: {total_animais}")
        
        if total_animais > 0:
            print(f"\n  Primeiros 5 animais:")
            for i, animal in enumerate(animais[:5], 1):
                print(f"    {i}. SISBOV: {animal.get('codigo_sisbov', 'N/A')}")
                print(f"       Brinco: {animal.get('numero_brinco', 'N/A')}")
                print(f"       Manejo: {animal.get('numero_manejo', 'N/A')}")
                print(f"       Raca: {animal.get('raca', 'N/A')}")
                print(f"       Sexo: {animal.get('sexo', 'N/A')}")
                print(f"       Nascimento: {animal.get('data_nascimento', 'N/A')}")
                print(f"       Peso: {animal.get('peso_kg', 'N/A')} kg")
                print()
            
            if total_animais > 5:
                print(f"  ... e mais {total_animais - 5} animais")
            
            # Estatísticas
            print(f"\n[ESTATISTICAS]")
            animais_com_brinco = sum(1 for a in animais if a.get('numero_brinco'))
            animais_com_raca = sum(1 for a in animais if a.get('raca'))
            animais_com_sexo = sum(1 for a in animais if a.get('sexo'))
            animais_com_data = sum(1 for a in animais if a.get('data_nascimento'))
            animais_com_peso = sum(1 for a in animais if a.get('peso_kg'))
            
            print(f"  Animais com brinco: {animais_com_brinco}/{total_animais}")
            print(f"  Animais com raca: {animais_com_raca}/{total_animais}")
            print(f"  Animais com sexo: {animais_com_sexo}/{total_animais}")
            print(f"  Animais com data nascimento: {animais_com_data}/{total_animais}")
            print(f"  Animais com peso: {animais_com_peso}/{total_animais}")
        else:
            print("  [AVISO] Nenhum animal foi extraido do PDF!")
            print("  Verifique se o formato do PDF esta correto.")
        
        # Relatório completo
        print(f"\n{'='*60}")
        print("RELATORIO COMPLETO")
        print(f"{'='*60}")
        relatorio = parser.gerar_relatorio_extracao()
        print(relatorio)
        
        print(f"\n{'='*60}")
        print("[SUCESSO] Teste concluido!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao processar PDF:")
        print(f"  {str(e)}")
        import traceback
        print(f"\nTraceback completo:")
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    # Caminho do PDF de teste
    pdf_teste = 'teste_bnd_sisbov.pdf'
    
    if len(sys.argv) > 1:
        pdf_teste = sys.argv[1]
    
    sucesso = testar_parser_pdf(pdf_teste)
    
    if sucesso:
        print("\n[DICA] Agora voce pode testar a importacao no sistema Django:")
        print("  1. Acesse o modulo de Rastreabilidade")
        print("  2. Vá em 'Importar BND/SISBOV'")
        print(f"  3. Selecione o arquivo: {pdf_teste}")
        print("  4. Clique em 'Importar arquivo SISBOV'")
    else:
        print("\n[ERRO] O teste falhou. Verifique o arquivo PDF e tente novamente.")
        sys.exit(1)


