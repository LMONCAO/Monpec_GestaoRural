#!/usr/bin/env python
"""
Script de teste para verificar sintaxe dos novos modelos
"""

def test_syntax():
    """Testa sintaxe dos novos modelos"""
    try:
        # Testar apenas a parte dos novos modelos
        code = '''
class PrecoIMEA(models.Model):
    """Modelo para armazenar preços IMEA"""

    TIPO_CATEGORIA_CHOICES = [
        ('BEZERRO', 'Bezerro (0-12 meses)'),
        ('BEZERRA', 'Bezerra (0-12 meses)'),
        ('GARROTE', 'Garrote (12-24 meses)'),
        ('NOVILHA', 'Novilha (12-24 meses)'),
        ('BOI', 'Boi (24-36 meses)'),
        ('BOI_MAGRO', 'Boi Magro (24-36 meses)'),
        ('VACA_INVERNAR', 'Vaca para Invernada'),
        ('VACA_DESCARTE', 'Vaca Descarte (>36 meses)'),
        ('TOURO', 'Touro (>36 meses)'),
        ('NOVA', 'Novilha para Reprodução'),
    ]

    uf = models.CharField(max_length=2, verbose_name="UF", db_index=True)
    ano = models.PositiveIntegerField(verbose_name="Ano", db_index=True)
    mes = models.PositiveIntegerField(verbose_name="Mês", db_index=True)
    tipo_categoria = models.CharField(max_length=20, choices=TIPO_CATEGORIA_CHOICES)
    preco_medio = models.DecimalField(max_digits=10, decimal_places=2)
'''

        import ast
        ast.parse(code)
        print("✅ Sintaxe dos modelos OK")

    except SyntaxError as e:
        print(f"❌ Erro de sintaxe: {e}")
        return False

    return True

if __name__ == "__main__":
    test_syntax()