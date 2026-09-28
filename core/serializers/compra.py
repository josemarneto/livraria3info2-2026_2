from django.db import transaction
from rest_framework.serializers import (
    CharField,
    CurrentUserDefault,
    DateTimeField,
    HiddenField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
)

from core.models import Compra, ItensCompra


class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco')

    def validate_quantidade(self, quantidade):
        if quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior do que zero.')
        return quantidade

    def validate(self, item):
        estoque = item['livro'].quantidade
        if estoque is None or item['quantidade'] > estoque:
            raise ValidationError('Quantidade de itens maior do que a quantidade em estoque.')
        return item


class CompraCreateUpdateSerializer(ModelSerializer):
    usuario = HiddenField(default=CurrentUserDefault())
    itens = ItensCompraCreateUpdateSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens', [])
        compra = Compra.objects.create(**validated_data)
        for item in itens:
            item['preco'] = item['livro'].preco
            ItensCompra.objects.create(compra=compra, **item)
        return compra

    @transaction.atomic
    def update(self, compra, validated_data):
        itens = validated_data.pop('itens', [])
        if itens:
            compra.itens.all().delete()
            for item in itens:
                item['preco'] = item['livro'].preco
                ItensCompra.objects.create(compra=compra, **item)
        return super().update(compra, validated_data)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')


class ItensCompraSerializer(ModelSerializer):
    total = SerializerMethodField()

    def get_total(self, instance):
        return instance.preco * instance.quantidade

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'preco', 'total')
        depth = 1


class ItensCompraListSerializer(ModelSerializer):
    livro = CharField(source='livro.titulo', read_only=True)

    class Meta:
        model = ItensCompra
        fields = ('quantidade', 'preco', 'livro')
        depth = 1


class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    data_criacao = DateTimeField(read_only=True)
    data_atualizacao = DateTimeField(read_only=True)
    itens = ItensCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = (
            'id',
            'usuario',
            'status',
            'total',
            'data_criacao',
            'data_atualizacao',
            'itens',
        )


class CompraListSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    itens = ItensCompraListSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')
