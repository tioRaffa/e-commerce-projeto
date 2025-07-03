import pytest

# Marcador para indicar que todos os testes neste arquivo precisam de acesso ao banco de dados
pytestmark = pytest.mark.django_db

# Testes do Modelo
def test_book_model_creation(book):
    """
    Testa a criação básica de um livro e verifica se os dados foram salvos corretamente.
    """
    assert book.title == 'Test Book'
    assert book.is_ready_for_shipping() is True
    assert str(book) == 'Test Book'

def test_is_ready_for_shipping_false(book):
    """
    Testa se 'is_ready_for_shipping' retorna False quando faltam dimensões.
    """
    book.weight_g = None
    book.save()
    assert book.is_ready_for_shipping() is False
