# Organização do Projeto

## Estrutura de Pastas

### 📁 docs/
Documentação do projeto (.md files)

### 📁 scripts/
Scripts organizados por categoria:
- **scripts/admin/** - Scripts para criação/gerenciamento de administradores
- **scripts/backup/** - Scripts de backup e exportação/importação
- **scripts/configuracao/** - Scripts de configuração do sistema
- **scripts/correcoes/** - Scripts de correção de problemas
- **scripts/deploy/** - Scripts de deploy e atualização
- **scripts/utilitarios/** - Scripts Python utilitários (não parte do Django)
- **scripts/emergencia/** - Scripts de emergência e rollback
- **scripts/manutencao/** - Scripts de manutenção do sistema
- **scripts/melhorias/** - Scripts de melhorias

### 📁 deploy/
Arquivos e configurações relacionadas ao deploy:
- **deploy/config/** - Arquivos de configuração (app.yaml, etc)
- **deploy/scripts/** - Scripts específicos de deploy

### 📁 temp/
Arquivos temporários (não versionados)

## Arquivos que Permanecem na Raiz

- `manage.py` - Django management script
- `requirements.txt` - Dependências Python
- `Dockerfile`, `Dockerfile.prod` - Configurações Docker
- `.gitignore` - Configuração Git
- `app.yaml`, `build-config.yaml`, `cloudbuild-config.yaml` - Configurações de deploy
- `entrypoint.sh` - Entrypoint do container

## Como Organizar Novos Arquivos

1. **Documentação (.md)**: Mover para `docs/`
2. **Scripts de deploy**: Mover para `scripts/deploy/`
3. **Scripts de admin**: Mover para `scripts/admin/`
4. **Scripts de correção**: Mover para `scripts/correcoes/`
5. **Scripts de configuração**: Mover para `scripts/configuracao/`
6. **Scripts de backup**: Mover para `scripts/backup/`
7. **Scripts Python utilitários**: Mover para `scripts/utilitarios/`
8. **Arquivos temporários**: Mover para `temp/` ou remover

## Notas

- Scripts organizados em `scripts/` não são ignorados pelo `.gitignore`
- Apenas arquivos temporários e na pasta `temp/` são ignorados
- Scripts duplicados devem ser consolidados ou removidos

