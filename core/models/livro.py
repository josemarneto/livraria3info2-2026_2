from django.db import models

from uploader.models import Image

from .autor import Autor
from .categoria import Categoria


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, null=True, blank=True)
    editora = models.ForeignKey('Editora', on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='livros', null=True, blank=True)
    data_publicacao = models.DateField()
    preco = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    autores = models.ManyToManyField(Autor, related_name='livros')
    capa = models.ForeignKey(
        Image,
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f"{self.titulo} - {', '.join([autor.nome for autor in self.autores.all()])}"
