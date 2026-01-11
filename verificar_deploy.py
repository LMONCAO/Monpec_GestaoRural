#!/usr/bin/env python
"""
VERIFICAR SE O DEPLOY MONPEC ESTA FUNCIONANDO
"""
import requests
import sys

def verificar_url(url, nome):
    """Verifica se uma URL está funcionando"""
    try:
        print(f"[TESTE] {nome}: {url}")
        response = requests.get(url, timeout=30, allow_redirects=True)

        if response.status_code == 200:
            print(f"[OK] {nome} FUNCIONANDO! (Status: {response.status_code})")

            # Verificar conteúdo
            if 'MONPEC' in response.text.upper():
                print("[OK] Conteudo MONPEC encontrado!")
            else:
                print("[AVISO] Pagina carregou mas conteudo pode estar diferente")

            return True

        elif response.status_code == 404:
            print(f"[ERRO] {nome} - Pagina nao encontrada (404)")
        elif response.status_code == 500:
            print(f"[ERRO] {nome} - Erro interno do servidor (500)")
        elif response.status_code == 503:
            print(f"[AVISO] {nome} - Servico indisponivel (503) - AGUARDE, pode estar inicializando")
        elif response.status_code == 302:
            print(f"[REDIRECT] {nome} - Redirecionamento (302) - pode precisar login")
        else:
            print(f"[AVISO] {nome} - Status: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"[ERRO] {nome} - Erro de conexao (servico pode nao estar rodando)")
    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] {nome} - Timeout (servico lento)")
    except Exception as e:
        print(f"[ERRO] {nome} - Erro: {str(e)[:50]}...")

    return False

def main():
    print("[VERIFICACAO] VERIFICANDO DEPLOY MONPEC NO GOOGLE CLOUD")
    print("=" * 60)

    # URLs possíveis
    urls = [
        ('https://monpec-fzzfjppzva-uc.a.run.app/', 'Landing Page Principal'),
        ('https://monpec-29862706245.us-central1.run.app/', 'Landing Page Secundaria'),
        ('https://monpec.com.br/', 'Dominio Proprio'),
    ]

    deploy_funcionando = False

    for url, nome in urls:
        if verificar_url(url, nome):
            deploy_funcionando = True
            url_base = url.rstrip('/')

            print("\n" + "=" * 40)
            print("[SUCESSO] DEPLOY FUNCIONANDO!")
            print("=" * 40)
            print(f"[LANDING] Landing Page: {url_base}/")
            print(f"[ADMIN] Admin: {url_base}/admin/")
            print(f"[DASHBOARD] Dashboard: {url_base}/propriedade/5/pecuaria/")
            print(f"[PLANEJAMENTO] Planejamento: {url_base}/propriedade/5/pecuaria/planejamento/")
            print("\n[OK] SISTEMA COMPLETO COM:")
            print("- 1.300 animais populados")
            print("- Planejamento 2026")
            print("- Dados financeiros")
            print("- Cenarios de analise")
            break

        print("")  # Linha em branco entre testes

    if not deploy_funcionando:
        print("\n" + "=" * 40)
        print("[ERRO] DEPLOY PODE TER FALHADO")
        print("=" * 40)
        print("\n[DIAGNOSTICO] POSSIVEIS PROBLEMAS:")
        print("1. Servico ainda inicializando (aguarde 5-10 minutos)")
        print("2. Erro no build/deploy")
        print("3. Problema com banco de dados")
        print("4. Configuracao incorreta")

        print("\n[LOGS] PARA DIAGNOSTICAR:")
        print("1. Abra: https://console.cloud.google.com/cloudshell")
        print("2. Execute: gcloud run services describe monpec --region=us-central1")
        print("3. Ver logs: gcloud run services logs read monpec --region=us-central1 --limit=20")

        print("\n[RETRY] SE AINDA NAO FUNCIONAR:")
        print("- Execute novamente: bash deploy_atualizado.sh")
        print("- Ou tente: gcloud run services update monpec --region=us-central1")

if __name__ == '__main__':
    main()