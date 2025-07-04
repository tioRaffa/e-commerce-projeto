from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from books.models import BookModel

class CartAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs ):
        cart  = request.session.get('cart', {})
        return Response(cart, status=status.HTTP_200_OK)
    
    def post(self, request, *arg, **kwargs):
        book_id = str(request.data.get('book_id'))
        if not book_id:
            return Response({
                "book_id": "ID do livro é obrigatorio"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({
                "quantity": "Quantidade é obrigatoria e deve ser mais que zero"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        
        book = get_object_or_404(BookModel, pk=book_id, is_active=True)
        if book.stock < quantity:
            return Response({
                'detail': f'Estoque insuficiente, {book.stock} unidades disponíveis.'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        cart = request.session.get('cart', {})

        cart[book_id] = {
            'quantity': quantity,
            'title': book.title,
            'price': str(book.price),
            'thumbnail_url': book.thumbnail_url or ''
        }
        request.session['cart'] = cart

        return Response(cart, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        book_id = str(request.data.get('book_id'))

        if not book_id:
            return Response({
                'book_id': 'O ID do livro deve ser informado.'
            }, status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = request.session.get('cart', {})

        if book_id in cart:
            del cart[book_id]
            request.session['cart'] = cart
            return Response(cart, status=status.HTTP_200_OK)
        
        return Response({
            'detail': 'Livro não encontrado.'
        },status=status.HTTP_404_NOT_FOUND 
        )