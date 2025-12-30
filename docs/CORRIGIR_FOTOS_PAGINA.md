# Como Corrigir Fotos que Não Aparecem na Página

## ✅ Status Atual

- ✓ Todas as 6 fotos existem em `static/site/` (foto1.jpeg até foto6.jpeg)
- ✓ Template está correto usando `{% static 'site/fotoX.jpeg' %}`
- ✓ Django configurado para servir arquivos estáticos quando DEBUG=True
- ✓ URLs configuradas corretamente

## 🔧 Solução

### Passo 1: Reiniciar o Servidor Django

**IMPORTANTE:** O servidor precisa ser reiniciado para reconhecer os arquivos estáticos.

1. Pare o servidor Django (pressione `Ctrl+C` no terminal onde está rodando)
2. Inicie novamente:

```bash
python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings
```

### Passo 2: Limpar Cache do Navegador

1. Pressione `Ctrl+Shift+R` (ou `Ctrl+F5`) para forçar o recarregamento
2. Ou limpe o cache do navegador completamente:
   - Chrome/Edge: `Ctrl+Shift+Delete` → Limpar dados de navegação
   - Firefox: `Ctrl+Shift+Delete` → Limpar dados

### Passo 3: Verificar se DEBUG=True

O servidor deve estar rodando em modo desenvolvimento (DEBUG=True) para servir arquivos estáticos automaticamente.

Se estiver usando `--settings=sistema_rural.settings`, o DEBUG deve estar True por padrão.

### Passo 4: Se DEBUG=False (Produção)

Se o servidor estiver em modo produção (DEBUG=False), execute:

```bash
python manage.py collectstatic --noinput
```

Isso copiará os arquivos de `static/` para `staticfiles/` onde o servidor de produção os servirá.

## 📁 Estrutura de Arquivos

Os arquivos devem estar em:
```
Monpec_GestaoRural/
  static/
    site/
      foto1.jpeg
      foto2.jpeg
      foto3.jpeg
      foto4.jpeg
      foto5.jpeg
      foto6.jpeg
```

## 🔍 Verificação

Após reiniciar o servidor e limpar o cache, verifique:

1. Abra o navegador em `http://localhost:8000/`
2. Abra o Console do Desenvolvedor (F12)
3. Verifique se há erros de carregamento de imagens
4. As fotos devem aparecer no slideshow da página inicial

## ⚠️ Problemas Comuns

1. **Servidor não reiniciado**: O mais comum - sempre reinicie após mudanças
2. **Cache do navegador**: Use Ctrl+Shift+R para forçar recarregamento
3. **DEBUG=False**: Execute collectstatic se estiver em produção
4. **Caminho incorreto**: Verifique se os arquivos estão em `static/site/`

## ✅ Solução Rápida (Resumo)

```bash
# 1. Parar servidor (Ctrl+C)
# 2. Reiniciar servidor
python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings

# 3. No navegador: Ctrl+Shift+R para limpar cache
```



