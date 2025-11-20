# Rotinas Automáticas para desbloquear o dashboard de planejamento

Este guia descreve como popular rapidamente o ambiente com todos os dados
necessários (inventário, parâmetros, planejamento, metas, cenários e finanças)
usando o novo comando `seed_planejamento` e os scripts auxiliares.

## 1. Pré-requisitos

- Banco configurado (`python manage.py migrate` já executado).
- Ambiente virtual ativado e dependências instaladas (`pip install -r requirements.txt`).
- Usuário desejado criado (o comando cria um _admin_ padrão caso não exista).

## 2. Execução manual (recomendado em desenvolvimento)

```bash
python manage.py migrate
python manage.py carregar_categorias  # opcional, garante nomes base
python manage.py seed_planejamento --usuario admin --ano 2025
```

O comando cria/atualiza:

- Usuário (senha `admin123` quando recém-criado), produtor e propriedade
- Categorias, inventário e parâmetros de projeção
- Planejamento completo (atividades, metas comerciais/financeiras, indicadores, cenários)
- Movimentações projetadas para 12 meses
- Fluxo de caixa, indicadores financeiros e financiamento ativo

Após a execução, basta acessar:

- `http://localhost:8000/propriedade/2/pecuaria/planejamento/`
- `http://localhost:8000/propriedade/2/pecuaria/projecao/`

## 3. Scripts automatizados

Há dois _wrappers_ prontos no diretório `scripts/`:

### Windows PowerShell

```powershell
scripts\setup_planejamento_demo.ps1 -Python "python" -Usuario "admin" -Ano 2025
```

### Bash (Linux/Mac/WSL)

```bash
chmod +x scripts/setup_planejamento_demo.sh
./scripts/setup_planejamento_demo.sh --python python --usuario admin --ano 2025
```

Ambos executam:

1. `python manage.py migrate`
2. `python manage.py seed_planejamento ...`

## 4. Reexecutando / limpando dados

- O comando é idempotente: rodar novamente atualiza os registros do mesmo ano.
- Para iniciar do zero, execute `python manage.py flush` (cuidado: remove todos os dados) e depois rode os passos acima.

## 5. Checklist rápido pós-execução

- [ ] Login com usuário informado (`admin` / `admin123` quando criado pela rotina)
- [ ] Dashboard Planejamento exibe cards preenchidos
- [ ] Aba Projeções lista movimentações por ano/mês
- [ ] Cards financeiros (fluxo e indicadores) mostram valores reais

> Sempre que precisar demonstrar o módulo ou resetar o ambiente de homologação,
> rode os scripts desta rotina para garantir dados consistentes em menos de um minuto.










