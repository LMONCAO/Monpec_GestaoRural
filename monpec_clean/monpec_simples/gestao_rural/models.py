from django.db import models

class Proprietario(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Proprietário"
        verbose_name_plural = "Proprietários"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Propriedade(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Propriedade")
    proprietario = models.ForeignKey(Proprietario, on_delete=models.CASCADE, related_name='propriedades', verbose_name="Proprietário")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área (hectares)")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.proprietario.nome}"
