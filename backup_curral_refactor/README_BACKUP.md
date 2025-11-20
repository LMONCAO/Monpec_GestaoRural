# Backup do Curral Dashboard - Refatoração

## Data do Backup
Gerado automaticamente antes da refatoração completa do sistema de Curral Dashboard.

## Arquivos no Backup

### Templates
- `curral_dashboard_v2.html` - Template principal (17.385 linhas)
- `curral_dashboard.html` - Template alternativo

### Backend
- `views_curral.py` - Views do curral (função `curral_painel` e relacionadas)

### Frontend
- `curral_dashboard_v2_simulacao_novo.js` - Sistema de simulação (1.005 linhas)

### CSS
- `curral_animations.css`
- `curral_enhanced.css`
- `curral_tela_unica.css`
- `curral.css`

## Como Restaurar

### Restaurar arquivos individuais:
```powershell
# Exemplo: restaurar o template principal
Copy-Item -Path "backup_curral_refactor\[DATA_BACKUP]\curral_dashboard_v2.html" -Destination "templates\gestao_rural\curral_dashboard_v2.html" -Force
```

### Restaurar tudo:
```powershell
$backupDir = "backup_curral_refactor\[DATA_BACKUP]"
Copy-Item -Path "$backupDir\curral_dashboard_v2.html" -Destination "templates\gestao_rural\" -Force
Copy-Item -Path "$backupDir\views_curral.py" -Destination "gestao_rural\" -Force
Copy-Item -Path "$backupDir\curral_dashboard_v2_simulacao_novo.js" -Destination "static\gestao_rural\" -Force
```

## Motivo do Backup
Refatoração completa do sistema de Curral Dashboard para:
1. Dividir template em includes menores
2. Extrair JavaScript para arquivos externos
3. Organizar em módulos reutilizáveis
4. Otimizar backend (separar views)
5. Implementar testes

## Status
✅ Backup concluído antes da refatoração
