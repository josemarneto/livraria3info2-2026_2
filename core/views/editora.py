from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Editora
from core.serializers import EditoraSerializer


class EditoraViewSet(ModelViewSet):
    queryset = Editora.objects.all()
    serializer_class = EditoraSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nome', 'cidade', 'email']
    ordering_fields = ['nome', 'cidade', 'email']
    ordering = ['nome']
