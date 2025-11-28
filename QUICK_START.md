# ⚡ Início Rápido

## Para Usuários Windows

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
   cd Monpec_GestaoRural
   ```

2. **Execute o instalador:**
   ```bash
   INSTALAR.bat
   ```

3. **Inicie o servidor:**
   ```bash
   INICIAR.bat
   ```

4. **Acesse:** http://127.0.0.1:8000

## Para Usuários Linux/Mac

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
   cd Monpec_GestaoRural
   ```

2. **Dê permissão de execução:**
   ```bash
   chmod +x INSTALAR.sh INICIAR.sh
   ```

3. **Execute o instalador:**
   ```bash
   ./INSTALAR.sh
   ```

4. **Inicie o servidor:**
   ```bash
   ./INICIAR.sh
   ```

5. **Acesse:** http://127.0.0.1:8000

## Migrar Dados de Outra Máquina

### Na máquina antiga:
```bash
EXPORTAR_DADOS.bat    # Windows
# ou
./EXPORTAR_DADOS.sh   # Linux/Mac
```

### Na máquina nova:
1. Copie o arquivo de backup para a pasta `backups/`
2. Execute:
```bash
IMPORTAR_DADOS.bat    # Windows
# ou
./IMPORTAR_DADOS.sh   # Linux/Mac
```

## Pronto! 🎉

O sistema está instalado e rodando. Para mais detalhes, consulte:
- [README_INSTALACAO.md](README_INSTALACAO.md) - Instalação detalhada
- [CONFIGURACAO_BANCO_DADOS.md](CONFIGURACAO_BANCO_DADOS.md) - Configuração de banco remoto

