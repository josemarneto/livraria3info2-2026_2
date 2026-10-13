from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Autor
from core.serializers.autor import AutorSerializer


class AutorViewSet(ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['nome', 'email']
    ordering_fields = ['nome', 'email']
    ordering = ['nome']
