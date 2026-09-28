from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, Livro
from core.serializers import CompraCreateUpdateSerializer, CompraListSerializer, CompraSerializer


class CompraViewSet(ModelViewSet):
    queryset = Compra.objects.all()
    serializer_class = CompraSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return CompraListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return CompraCreateUpdateSerializer
        return CompraSerializer

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
            return Compra.objects.all()
        if usuario.groups.filter(name='administradores'):
            return Compra.objects.all()
        return Compra.objects.filter(usuario=usuario)

    @extend_schema(
        request=None,
        responses={200: None},
        description='Gera um relatório de vendas do mês atual.',
        summary='Relatório de vendas do mês',
    )
    @action(detail=False, methods=['get'])
    def relatorio_vendas_mes(self, request):
        agora = timezone.now()
        inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        compras = Compra.objects.filter(
            status=Compra.StatusCompra.FINALIZADO,
            data_criacao__gte=inicio_mes,
        )

        total_vendas = sum((compra.total for compra in compras), Decimal('0.00'))
        return Response(
            {
                'status': 'Relatório de vendas deste mês',
                'total_vendas': total_vendas,
                'quantidade_vendas': compras.count(),
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=None,
        responses={200: None, 400: None},
        description='Finaliza a compra, atualizando o estoque dos livros.',
        summary='Finalizar compra',
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def finalizar(self, request, pk=None):
        compra = self.get_object()
        compra = Compra.objects.select_for_update().get(pk=compra.pk)

        if compra.status == Compra.StatusCompra.FINALIZADO:
            return Response(
                {'status': 'Compra já finalizada'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantidades = defaultdict(int)
        for item in compra.itens.all():
            quantidades[item.livro_id] += item.quantidade

        livros = {
            livro.pk: livro
            for livro in Livro.objects.select_for_update().filter(pk__in=quantidades).order_by('pk')
        }
        for livro_id, quantidade in quantidades.items():
            livro = livros[livro_id]
            estoque = livro.quantidade or 0
            if quantidade > estoque:
                return Response(
                    {
                        'status': 'Quantidade insuficiente',
                        'livro': livro.titulo,
                        'quantidade_disponivel': livro.quantidade,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for livro_id, quantidade in quantidades.items():
            livro = livros[livro_id]
            livro.quantidade = (livro.quantidade or 0) - quantidade
            livro.save(update_fields=('quantidade',))

        compra.status = Compra.StatusCompra.FINALIZADO
        compra.save()
        return Response({'status': 'Compra finalizada'}, status=status.HTTP_200_OK)
