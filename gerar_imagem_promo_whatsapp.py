"""
Script para gerar imagem promocional para WhatsApp
Usa Selenium para capturar a página HTML como imagem
"""
import os
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium não instalado. Instale com: pip install selenium")

def gerar_imagem_promocional():
    """Gera imagem promocional a partir do HTML"""
    
    if not SELENIUM_AVAILABLE:
        print("\n📝 Para usar este script, instale as dependências:")
        print("   pip install selenium")
        print("\n📋 Alternativa: Abra 'templates/gestao_rural/promo_whatsapp.html' no navegador")
        print("   e use a ferramenta de captura de tela.")
        return False
    
    # Caminho do arquivo HTML
    base_dir = Path(__file__).parent
    html_file = base_dir / 'templates' / 'gestao_rural' / 'promo_whatsapp.html'
    html_path = html_file.resolve().as_uri()
    
    if not html_file.exists():
        print(f"❌ Arquivo não encontrado: {html_file}")
        return False
    
    print(f"📄 Carregando: {html_file}")
    
    try:
        # Configurar Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=600,900')
        chrome_options.add_argument('--disable-gpu')
        
        # Inicializar driver
        print("🚀 Inicializando navegador...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Carregar página
        print(f"📥 Carregando página HTML...")
        driver.get(html_path)
        
        # Aguardar carregamento
        import time
        time.sleep(2)
        
        # Capturar screenshot
        output_file = base_dir / 'promo_monpec_whatsapp.png'
        print(f"📸 Capturando screenshot...")
        driver.save_screenshot(str(output_file))
        
        # Fechar navegador
        driver.quit()
        
        print(f"\n✅ Imagem gerada com sucesso!")
        print(f"📁 Localização: {output_file}")
        print(f"\n📱 Agora você pode compartilhar no WhatsApp!")
        print(f"🔗 Link para adicionar na descrição:")
        print(f"   https://pay.hotmart.com/O102944551F")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao gerar imagem: {e}")
        print(f"\n💡 Alternativa: Abra o arquivo HTML no navegador e capture manualmente:")
        print(f"   {html_file}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("📸 GERADOR DE IMAGEM PROMOCIONAL - MONPEC")
    print("=" * 60)
    print()
    
    gerar_imagem_promocional()
    
    print()
    print("=" * 60)


