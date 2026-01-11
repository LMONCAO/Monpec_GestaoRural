# Ícones da PWA Monpec

Este diretório deve conter os ícones da Progressive Web App (PWA) do Monpec.

## Ícones Necessários

Para que a PWA funcione corretamente, você precisa gerar os seguintes ícones em formato PNG:

### Tamanhos Padrão (obrigatórios):
- `icon-72.png` - 72x72 pixels
- `icon-96.png` - 96x96 pixels
- `icon-128.png` - 128x128 pixels
- `icon-144.png` - 144x144 pixels
- `icon-152.png` - 152x152 pixels
- `icon-192.png` - 192x192 pixels
- `icon-384.png` - 384x384 pixels
- `icon-512.png` - 512x512 pixels

## Como Gerar os Ícones

### Opção 1: Usar Ferramenta Online (Recomendado)
1. Acesse: https://favicon.io/favicon-converter/
2. Faça upload de uma imagem do logo Monpec (PNG, JPG, SVG)
3. Selecione os tamanhos: 72, 96, 128, 144, 152, 192, 384, 512
4. Baixe o ZIP e extraia os arquivos neste diretório

### Opção 2: Usar Ferramenta Desktop
1. Instale o ImageMagick ou similar
2. Use comandos como:
```bash
convert logo_monpec.png -resize 192x192 icon-192.png
convert logo_monpec.png -resize 512x512 icon-512.png
# ... para todos os tamanhos
```

### Opção 3: Usar Canva ou Figma
1. Crie um design com fundo verde (#2d6a4f) e o texto "MONPEC"
2. Exporte em múltiplas resoluções

## Design Sugerido

- **Fundo**: Verde escuro (#2d6a4f ou similar)
- **Texto**: "MONPEC" em branco
- **Formato**: Circular ou quadrado com cantos arredondados
- **Estilo**: Moderno, profissional, rural

## Verificação

Após adicionar os ícones:
1. Limpe o cache do navegador (Ctrl+F5)
2. Visite o site
3. Abra as ferramentas de desenvolvedor (F12)
4. Vá em Application > Manifest
5. Verifique se os ícones estão carregando corretamente

## Teste da PWA

Para testar se a PWA está funcionando:
1. Abra o site no Chrome
2. Clique nos 3 pontos (⋮) > "Instalar Monpec"
3. Ou procure o botão "Instalar" na barra de endereço
4. Teste offline: desconecte a internet e use o app instalado