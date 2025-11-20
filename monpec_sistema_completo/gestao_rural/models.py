from django.db import models
from django.contrib.auth.models import User

class ProdutorRural(models.Model):
    nome_completo = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = "Produtor Rural"
        verbose_name_plural = "Produtores Rurais"

class Propriedade(models.Model):
    produtor = models.ForeignKey(ProdutorRural, on_delete=models.CASCADE)
    nome_propriedade = models.CharField(max_length=200)
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    area_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=[('propria', 'Própria'), ('arrendada', 'Arrendada')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome_propriedade} - {self.municipio}/{self.uf}"

class CategoriaAnimal(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class InventarioRebanho(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaAnimal, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    data_inventario = models.DateField()
    
    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.categoria.nome} - {self.quantidade} cabeças"

class CicloProducaoAgricola(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    cultura = models.CharField(max_length=100)
    safra = models.CharField(max_length=20)
    area_plantada = models.DecimalField(max_digits=10, decimal_places=2)
    produtividade = models.DecimalField(max_digits=10, decimal_places=2)
    custo_ha = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    receita_esperada_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    def save(self, *args, **kwargs):
        producao = self.area_plantada * self.produtividade
        self.receita_esperada_total = producao * self.preco_venda
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cultura} {self.safra}"

class BemImobilizado(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200)
    valor_aquisicao = models.DecimalField(max_digits=12, decimal_places=2)
    data_aquisicao = models.DateField()
    deprec_anual = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.descricao} ({self.tipo})"

class CustoFixo(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    custo_anual = models.DecimalField(max_digits=12, decimal_places=2)
    ativo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.custo_anual = self.valor_mensal * 12
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor_mensal}/mês"

class CustoVariavel(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    custo_anual = models.DecimalField(max_digits=12, decimal_places=2)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.custo_anual}/ano"

class Financiamento(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    banco = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    qt_parcelas = models.IntegerField()
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.banco} - {self.tipo}"
