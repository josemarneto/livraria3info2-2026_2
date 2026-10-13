from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core.models import Compra, ItensCompra, Livro, User
from core.serializers.compra import CompraCreateUpdateSerializer

QUANTIDADE_FINAL_ESPERADA = 5
TOTAL_COMPRA_ESPERADO = Decimal('225.00')
TOTAL_COMPRA_ATUALIZADO_ESPERADO = Decimal('180.00')


class CompraCreateUpdateSerializerTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(email='cliente@example.com', password='senha-segura')
        self.livro = Livro.objects.create(
            titulo='Django REST',
            quantidade=10,
            preco=Decimal('45.00'),
        )
        self.request_factory = APIRequestFactory()

    def criar_compra(self, quantidade):
        request = self.request_factory.post('/api/compras/')
        request.user = self.usuario
        serializer = CompraCreateUpdateSerializer(
            data={'itens': [{'livro': self.livro.pk, 'quantidade': quantidade}]},
            context={'request': request},
        )
        assert serializer.is_valid(), serializer.errors
        return serializer.save()

    def test_reuses_cart_and_increments_existing_book_quantity(self):
        primeira_compra = self.criar_compra(2)
        segunda_compra = self.criar_compra(3)

        assert primeira_compra.pk == segunda_compra.pk
        assert Compra.objects.filter(usuario=self.usuario, status=Compra.StatusCompra.CARRINHO).count() == 1
        item = ItensCompra.objects.get(compra=primeira_compra, livro=self.livro)
        assert item.quantidade == QUANTIDADE_FINAL_ESPERADA
        assert item.preco == self.livro.preco
        primeira_compra.refresh_from_db()
        assert primeira_compra.total == TOTAL_COMPRA_ESPERADO

    def test_updates_total_when_cart_items_are_replaced(self):
        compra = self.criar_compra(2)
        request = self.request_factory.put('/api/compras/')
        request.user = self.usuario
        serializer = CompraCreateUpdateSerializer(
            instance=compra,
            data={'itens': [{'livro': self.livro.pk, 'quantidade': 4}]},
            context={'request': request},
        )
        assert serializer.is_valid(), serializer.errors
        compra_atualizada = serializer.save()
        compra_atualizada.refresh_from_db()

        assert compra_atualizada.total == TOTAL_COMPRA_ATUALIZADO_ESPERADO
