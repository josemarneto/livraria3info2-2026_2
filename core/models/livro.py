from django.db import models


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey('Autor', on_delete=models.CASCADE)
    editora = models.ForeignKey('Editora', on_delete=models.CASCADE)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    data_publicacao = models.DateField()

    def __str__(self):
        return self.titulo
