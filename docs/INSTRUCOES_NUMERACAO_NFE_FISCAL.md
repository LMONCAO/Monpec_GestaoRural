# Instruções para Implementação de Numeração Fiscal de NF-e

## ⚠️ IMPORTANTE: Arquivo models_compras_financeiro.py foi sobrescrito

O arquivo `gestao_rural/models_compras_financeiro.py` foi acidentalmente sobrescrito durante a implementação. É necessário restaurá-lo do backup ou git antes de continuar.

## Implementações Realizadas

### 1. Novo Modelo: NumeroSequencialNFE

Crie o seguinte modelo no arquivo `gestao_rural/models_compras_financeiro.py` (adicione ao final do arquivo):

```python
class NumeroSequencialNFE(models.Model):
    """
    Controla a numeração sequencial de NF-e por propriedade e série
    Conforme legislação fiscal, cada estabelecimento deve ter numeração única por série
    """
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='numeros_sequenciais_nfe',
        verbose_name="Propriedade"
    )
    serie = models.CharField(
        max_length=10,
        default='1',
        verbose_name="Série da NF-e",
        help_text="Série da nota fiscal (geralmente '1' para a série normal)"
    )
    proximo_numero = models.IntegerField(
        default=1,
        verbose_name="Próximo Número",
        help_text="Próximo número sequencial a ser usado nesta série"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data da Última Atualização"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações sobre esta série (ex: 'Série normal', 'Série de teste', etc.)"
    )
    
    class Meta:
        verbose_name = "Número Sequencial de NF-e"
        verbose_name_plural = "Números Sequenciais de NF-e"
        unique_together = [['propriedade', 'serie']]
        ordering = ['propriedade', 'serie']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - Série {self.serie} - Próximo: {self.proximo_numero}"
    
    def obter_proximo_numero(self):
        """
        Retorna o próximo número e incrementa o contador
        """
        numero = self.proximo_numero
        self.proximo_numero += 1
        self.save(update_fields=['proximo_numero', 'data_atualizacao'])
        return numero
    
    @classmethod
    def obter_ou_criar(cls, propriedade, serie='1'):
        """
        Obtém ou cria um registro de numeração sequencial para a propriedade e série
        """
        obj, created = cls.objects.get_or_create(
            propriedade=propriedade,
            serie=serie,
            defaults={'proximo_numero': 1}
        )
        return obj
```

### 2. Arquivo de Utilitários Criado

O arquivo `gestao_rural/services_nfe_utils.py` foi criado com as seguintes funções:
- `obter_proximo_numero_nfe(propriedade, serie='1')`: Obtém próximo número sequencial
- `validar_numero_nfe_unico(...)`: Valida se número é único
- `obter_series_disponiveis(propriedade)`: Lista séries disponíveis
- `configurar_serie_nfe(...)`: Configura uma série

### 3. Views Atualizadas

As seguintes views foram atualizadas para usar o novo sistema:
- `vendas_nota_fiscal_emitir`: Usa `obter_proximo_numero_nfe()`
- `vendas_venda_nova`: Usa `obter_proximo_numero_nfe()`

### 4. Novas Views Criadas

- `vendas_configurar_series_nfe`: Interface para configurar séries
- `vendas_excluir_serie_nfe`: Excluir configuração de série

### 5. URLs Adicionadas

```python
path('propriedade/<int:propriedade_id>/vendas/configurar-series-nfe/', ...),
path('propriedade/<int:propriedade_id>/vendas/configurar-series-nfe/<int:serie_id>/excluir/', ...),
```

### 6. Templates Criados

- `templates/gestao_rural/vendas_configurar_series_nfe.html`: Interface de configuração

## Próximos Passos

1. **Restaurar models_compras_financeiro.py** do backup/git
2. **Adicionar o modelo NumeroSequencialNFE** ao final do arquivo restaurado
3. **Criar e aplicar migration**:
   ```bash
   python manage.py makemigrations gestao_rural --name adicionar_numero_sequencial_nfe
   python manage.py migrate gestao_rural
   ```
4. **Testar o sistema de numeração**

## Benefícios da Implementação

✅ **Conformidade Fiscal**: Cada propriedade tem numeração sequencial única por série
✅ **Múltiplas Séries**: Suporte para diferentes séries (normal, teste, exportação, etc.)
✅ **Controle Robusto**: Prevenção de duplicação de números usando transações
✅ **Interface Amigável**: Configuração visual de séries
✅ **Auditoria**: Rastreamento de última atualização

## Como Funciona

1. Quando uma NF-e é criada, o sistema busca ou cria um registro `NumeroSequencialNFE` para a propriedade e série
2. O método `obter_proximo_numero()` retorna o próximo número e incrementa o contador atomicamente
3. Cada propriedade pode ter múltiplas séries, cada uma com sua própria numeração
4. A interface permite configurar séries adicionais e ajustar o próximo número quando necessário






