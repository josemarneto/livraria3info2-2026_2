from django.db import models

from .categoria import Categoria


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey('Autor', on_delete=models.CASCADE)
    editora = models.ForeignKey('Editora', on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)
    data_publicacao = models.DateField()
    preco = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.titulo} - {self.autor.nome}"
