from django.db.models import Q, Sum
from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, Livro
from core.serializers import (
    LivroAjustarEstoqueSerializer,
    LivroAlterarPrecoSerializer,
    LivroListRetrieveSerializer,
    LivroMaisVendidoSerializer,
    LivroSerializer,
)


class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve'}:
            return LivroListRetrieveSerializer
        return LivroSerializer

    @extend_schema(
        request=LivroAlterarPrecoSerializer,
        responses={200: None},
        description='Altera o preço de um livro específico.',
        summary='Alterar preço do livro',
    )
    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()
        serializer = LivroAlterarPrecoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        livro.preco = serializer.validated_data['preco']
        livro.save()

        return Response(
            {'detail': f'Preço do livro "{livro.titulo}" atualizado para {livro.preco}.'},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary='Lista os livros mais vendidos',
        description='Retorna os livros que venderam mais de 10 unidades.',
        responses={200: LivroMaisVendidoSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        livros = (
            Livro.objects.annotate(
                total_vendidos=Sum(
                    'itens_compra__quantidade',
                    filter=Q(itens_compra__compra__status=Compra.StatusCompra.FINALIZADO),
                )
            )
            .filter(total_vendidos__gt=10)
            .order_by('-total_vendidos')
        )
        serializer = LivroMaisVendidoSerializer(livros, many=True)
        if not serializer.data:
            return Response(
                {'detail': 'Nenhum livro excedeu 10 vendas.'},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Ajusta o estoque de um livro',
        description='Aumenta ou diminui o estoque; impede resultado negativo.',
        request=LivroAjustarEstoqueSerializer,
        responses={
            200: OpenApiResponse(
                description='Estoque ajustado com sucesso.',
                examples=[
                    OpenApiExample(
                        'Ajuste concluído',
                        value={'status': 'Quantidade ajustada com sucesso', 'novo_estoque': 30},
                    )
                ],
            ),
            400: OpenApiResponse(
                description='Erro de validação.',
                examples=[
                    OpenApiExample(
                        'Estoque negativo',
                        value={'quantidade': ['A quantidade em estoque não pode ser negativa.']},
                    )
                ],
            ),
        },
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def ajustar_estoque(self, request, pk=None):
        livro = self.get_object()
        livro = Livro.objects.select_for_update().get(pk=livro.pk)
        serializer = LivroAjustarEstoqueSerializer(
            data=request.data,
            context={'livro': livro},
        )
        serializer.is_valid(raise_exception=True)

        livro.quantidade = (livro.quantidade or 0) + serializer.validated_data['quantidade']
        livro.save(update_fields=('quantidade',))
        return Response(
            {
                'status': 'Quantidade ajustada com sucesso',
                'novo_estoque': livro.quantidade,
            },
            status=status.HTTP_200_OK,
        )
