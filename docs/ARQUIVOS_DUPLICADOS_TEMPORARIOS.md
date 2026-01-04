# Arquivos Duplicados e Temporários para Revisão

## 📋 Arquivos Identificados para Revisão

### Scripts Temporários
Os seguintes arquivos parecem ser temporários ou versões antigas e podem ser removidos após revisão:

#### Scripts de Organização (podem ser removidos após uso)
- `_organizar_agora.py` - Script temporário de organização
- `organizar_projeto_completo.py` - Pode ser mantido como referência ou removido
- `organizar_projeto.ps1` - Versão alternativa, manter apenas `EXECUTAR_ORGANIZACAO.ps1`

#### Pasta scripts/temp_para_revisao/
Esta pasta contém scripts que foram temporariamente movidos para revisão. Após revisar e organizar:
1. Mover scripts úteis para as pastas apropriadas em `scripts/`
2. Remover scripts obsoletos ou duplicados
3. Remover a pasta `scripts/temp_para_revisao/` após limpeza

### Arquivos com Sufixos Temporários
Procure por arquivos com os seguintes padrões que podem ser removidos:
- `*_temp.*`
- `*_old.*`
- `*_copy.*`
- `*_backup.*`
- `*_v2.*`, `*_v3.*` (verificar se versões antigas)

## 🔍 Verificação de Duplicados

### Scripts com Nomes Similares
Após organizar, verifique por duplicados:
- Scripts com nomes muito similares (ex: `deploy.sh`, `DEPLOY.sh`, `deploy_agora.sh`)
- Scripts com versões (ex: `script_v1.py`, `script_v2.py`)
- Scripts em diferentes formatos do mesmo propósito (ex: `deploy.sh`, `deploy.ps1`, `deploy.bat`)

### Recomendações
1. **Manter apenas uma versão** de cada script funcional
2. **Consolidar funcionalidades** similares em um único script
3. **Remover versões antigas** após confirmar que versões novas funcionam
4. **Documentar** scripts mantidos em `docs/`

## 🗑️ Limpeza Sugerida

### Após Executar a Organização:
1. Revisar `scripts/temp_para_revisao/`
2. Identificar scripts duplicados ou obsoletos
3. Mover scripts úteis para pastas apropriadas
4. Remover scripts não utilizados
5. Atualizar documentação se necessário

## 📝 Nota
**NÃO remova arquivos sem revisar primeiro!** Alguns podem conter lógica importante ou serem referenciados em outros lugares.




