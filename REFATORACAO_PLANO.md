# Plano de Refatoração - Curral Dashboard V2

## ✅ Backup Concluído
Backup salvo em: `backup_curral_refactor/20251120_132137/`

## 📋 Estrutura de Refatoração Planejada

### Estrutura de Pastas:

```
templates/gestao_rural/
├── curral/
│   ├── includes/
│   │   ├── css.html           # Estilos CSS
│   │   ├── header.html        # Cabeçalho da página
│   │   ├── scanner.html       # Seção de identificação do brinco
│   │   ├── pesagem.html       # Seção de pesagem
│   │   ├── estatisticas.html  # Estatísticas e resumo
│   │   ├── modals.html        # Todos os modais (confirmação, diagnóstico, etc)
│   │   └── scripts.html       # Scripts JavaScript inline (temporário)
│   └── curral_dashboard_v2.html  # Template principal (simplificado)

static/gestao_rural/
└── curral/
    ├── components/
    │   ├── Scanner.js         # Componente de identificação
    │   ├── Pesagem.js         # Componente de pesagem
    │   ├── AnimalCard.js      # Card de informações do animal
    │   └── Estatisticas.js    # Componente de estatísticas
    ├── services/
    │   ├── api.js             # Chamadas à API
    │   └── cache.js           # Sistema de cache
    ├── utils/
    │   ├── formatters.js      # Formatação de dados
    │   └── validators.js      # Validações
    └── main.js                # Arquivo principal
```

## 🎯 Fases de Implementação

### ✅ Fase 0: Backup - CONCLUÍDA
- [x] Backup de todos os arquivos críticos
- [x] Script de restauração criado

### 🔄 Fase 1: Dividir Template em Includes (EM ANDAMENTO)
- [ ] Criar estrutura de pastas
- [ ] Extrair CSS para includes/css.html
- [ ] Extrair Header para includes/header.html
- [ ] Extrair Scanner para includes/scanner.html
- [ ] Extrair Pesagem para includes/pesagem.html
- [ ] Extrair Estatísticas para includes/estatisticas.html
- [ ] Extrair Modais para includes/modals.html
- [ ] Refatorar template principal para usar includes

### ⏳ Fase 2: Extrair JavaScript para Arquivos Externos
- [ ] Criar estrutura de pastas em static/
- [ ] Extrair funções principais para components/
- [ ] Mover código de API para services/api.js
- [ ] Criar utilitários em utils/
- [ ] Criar arquivo main.js principal
- [ ] Remover JavaScript inline do template

### ⏳ Fase 3: Organizar em Módulos Reutilizáveis
- [ ] Organizar components em módulos ES6
- [ ] Criar sistema de eventos
- [ ] Implementar padrão de observadores
- [ ] Criar módulos reutilizáveis

### ⏳ Fase 4: Otimizar Backend
- [ ] Separar view curral_painel em múltiplas views menores
- [ ] Criar serializers para dados
- [ ] Implementar cache de dados frequentes
- [ ] Otimizar queries do banco

### ⏳ Fase 5: Implementar Testes
- [ ] Testes unitários backend
- [ ] Testes de componentes frontend
- [ ] Testes de integração

---

## 📝 Notas Importantes

1. **Mantendo Compatibilidade**: Todas as mudanças serão feitas mantendo a funcionalidade existente
2. **Testes Incrementais**: Cada fase será testada antes de prosseguir
3. **Rollback Disponível**: Backup completo permite restaurar a qualquer momento

## 🚨 Se Algo Der Errado

Execute o script de restauração:
```powershell
.\backup_curral_refactor\RESTAURAR_BACKUP.ps1
```

Ou manualmente:
```powershell
Copy-Item -Path "backup_curral_refactor\20251120_132137\curral_dashboard_v2.html" -Destination "templates\gestao_rural\curral_dashboard_v2.html" -Force
```

---

**Início da Refatoração**: 2025-11-20 13:21
