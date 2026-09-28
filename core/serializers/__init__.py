from .autor import AutorSerializer
from .categoria import CategoriaSerializer
from .editora import EditoraSerializer
from .livro import (
	LivroAlterarPrecoSerializer,
	LivroListRetrieveSerializer,
	LivroMaisVendidoSerializer,
	LivroSerializer,
)
from .user import UserRegistrationSerializer, UserSerializer
from .compra import CompraSerializer, CompraListSerializer, CompraCreateUpdateSerializer, ItensCompraSerializer, ItensCompraListSerializer, ItensCompraCreateUpdateSerializer
