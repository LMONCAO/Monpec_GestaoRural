# 📸 Gerar Imagem Promocional para WhatsApp

## 📋 Como Usar

### Opção 1: Captura de Tela Manual
1. Abra o arquivo `templates/gestao_rural/promo_whatsapp.html` no navegador
2. Ajuste o zoom do navegador para visualizar bem o card
3. Use a ferramenta de captura de tela do Windows ou uma extensão do navegador
4. Capture apenas o card promocional
5. Salve como imagem PNG ou JPG

### Opção 2: Usar Ferramenta Online
1. Acesse: https://htmlcsstoimage.com/ ou https://www.bannerbear.com/
2. Cole o código HTML do arquivo `promo_whatsapp.html`
3. Configure as dimensões: 600x800px (recomendado para WhatsApp)
4. Gere e baixe a imagem

### Opção 3: Usar Python (Puppeteer/Playwright)
```python
# Instalar: pip install playwright selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--window-size=600,800')

driver = webdriver.Chrome(options=chrome_options)
driver.get('file:///caminho/para/promo_whatsapp.html')

driver.save_screenshot('promo_monpec.png')
driver.quit()
```

### Opção 4: Usar Node.js (Puppeteer)
```javascript
const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 600, height: 800 });
  await page.goto('file:///caminho/para/promo_whatsapp.html');
  await page.screenshot({ path: 'promo_monpec.png', fullPage: true });
  await browser.close();
})();
```

## 📱 Dicas para WhatsApp

- **Tamanho recomendado**: 600x800px ou 1080x1350px (formato vertical/retrato)
- **Formato**: PNG ou JPG
- **Tamanho do arquivo**: Máximo 16MB (WhatsApp permite até 16MB)
- **Qualidade**: Use alta qualidade (PNG) para texto nítido

## 🔗 Link na Descrição

Quando compartilhar a imagem no WhatsApp, adicione este texto na descrição:

```
🎯 PROMOÇÃO ESPECIAL DE LANÇAMENTO 🎯

OS 100 PRIMEIROS que adquirir o sistema MONPEC pagando apenas 1 MENSALIDADE DE R$ 99,00 vão ganhar o ACESSO ANUAL COMPLETO! 🚀

🔥 Lançamento: 05/12/2025
⏰ Oferta Limitada - Não perca!

💳 Garanta sua vaga agora:
https://pay.hotmart.com/O102944551F

Monpec. - Monitor da Pecuária
```

## 🎨 Personalização

Para personalizar o card, edite o arquivo `templates/gestao_rural/promo_whatsapp.html`:
- Cores: Edite as cores CSS no `<style>`
- Textos: Edite o conteúdo HTML
- Link: Altere a URL do botão CTA


