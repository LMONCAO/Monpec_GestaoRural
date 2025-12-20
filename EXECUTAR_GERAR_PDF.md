# ⚡ Executar gerar_pdf_teste_realista_bnd_sisbov.py - Guia Rápido

## 📝 Comandos Prontos para Copiar e Colar

### Passo 1: Descobrir ID da Propriedade

```bash
python manage.py shell
```

No shell Python que abrir, cole:
```python
from gestao_rural.models import Propriedade
for p in Propriedade.objects.all():
    animais = p.animais_individuais.filter(status='ATIVO').count()
    print(f"ID: {p.id} | {p.nome_propriedade} | {animais} animais ativos")
```

Anote o ID da propriedade que você quer usar.

### Passo 2: Executar o Script

**Windows PowerShell:**
```powershell
cd c:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural
python gerar_pdf_teste_realista_bnd_sisbov.py 1
```

**Substitua `1` pelo ID da sua propriedade!**

**Com nome personalizado:**
```powershell
python gerar_pdf_teste_realista_bnd_sisbov.py 1 minha_fazenda_teste.pdf
```

**Se o Python não estiver no PATH:**
```powershell
python311\python.exe gerar_pdf_teste_realista_bnd_sisbov.py 1
```

## ✅ O que Acontece

1. Script conecta ao banco de dados Django
2. Busca animais ativos da propriedade
3. Cria divergências intencionais:
   - 94% corretos
   - 5% com dados faltantes
   - 1% não conformes
4. Gera PDF: `teste_realista_bnd_sisbov.pdf`
5. Gera relatório: `teste_realista_bnd_sisbov_divergencias.txt`

## 📄 Arquivos Gerados

- ✅ `teste_realista_bnd_sisbov.pdf` - PDF para importação
- ✅ `teste_realista_bnd_sisbov_divergencias.txt` - Relatório das divergências

## 🎯 Exemplo Completo

```powershell
# 1. Ir para a pasta do projeto
cd c:\Users\joaoz\Documents\GitHub\Monpec_GestaoRural

# 2. Executar (substitua 1 pelo ID real)
python gerar_pdf_teste_realista_bnd_sisbov.py 1

# 3. Saída esperada:
# [INFO] Django configurado com: sistema_rural.settings
# [INFO] Propriedade: Nome da Fazenda
# [INFO] Total de animais encontrados: 50
# [INFO] Distribuicao de divergencias:
#   - Animais corretos: 47 (94%)
#   - Com dados faltantes: 2 (5%)
#   - Nao conformes: 1 (1%)
# [OK] PDF de teste realista criado: teste_realista_bnd_sisbov.pdf
```

## 🚨 Problemas Comuns

**"Propriedade não encontrada"**
→ Verifique o ID com o comando do Passo 1

**"Nenhum animal ativo encontrado"**
→ A propriedade precisa ter animais com status ATIVO

**"ModuleNotFoundError: reportlab"**
→ Execute: `pip install reportlab`

**"Django não configurado"**
→ O script tenta automaticamente, mas se falhar, verifique o settings.py

## 📚 Mais Informações

Veja `COMO_EXECUTAR_GERAR_PDF_TESTE.md` para guia completo.

---

**Comando Final:**
```bash
python gerar_pdf_teste_realista_bnd_sisbov.py <ID_PROPRIEDADE>
```


