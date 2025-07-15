from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from books.models import BookModel
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive

class CartAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    CART_EXPIRATION_MINUTES = 60

    def get(self, request, *args, **kwargs ):
        cart_expiration_str = request.session.get('cart_expiration')
        if cart_expiration_str:
            cart_expiration = datetime.fromisoformat(cart_expiration_str)

            if is_naive(cart_expiration):
                cart_expiration = make_aware(cart_expiration)

            if timezone.now() > cart_expiration:
                request.session['cart'] = {'items': {}}
                request.session.pop('cart_expiration', None)

        cart  = request.session.get('cart', {'items': {}})
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
        if 'items' not in cart:
            cart['items'] = {}

        cart['items'][book_id] = {
            'quantity': quantity,
            'title': book.title,
            'price': str(book.price),
            'thumbnail_url': book.thumbnail_url or ''
        }
        request.session['cart'] = cart
        expiration_time = timezone.now() + timedelta(minutes=self.CART_EXPIRATION_MINUTES)
        request.session['cart_expiration'] = expiration_time.isoformat()

        return Response(cart, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        book_id = str(request.data.get('book_id'))

        if not book_id:
            return Response({
                'book_id': 'O ID do livro deve ser informado.'
            }, status=status.HTTP_400_BAD_REQUEST
            )
        
        cart = request.session.get('cart', {})

        if book_id in cart.get('items', {}):
            del cart['items'][book_id]
            request.session['cart'] = cart
            if not cart:
                request.session.pop('cart_expiration', None)
            else:
                expiration_time = timezone.now() + timedelta(minutes=self.CART_EXPIRATION_MINUTES)
                request.session['cart_expiration'] = expiration_time.isoformat()
            return Response(cart, status=status.HTTP_200_OK)
        
        return Response({
            'detail': 'Livro não encontrado.'
        },status=status.HTTP_404_NOT_FOUND 
        )
    

class CartShippingSelectionAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})

        shipping_option = request.data.get('shipping_option')

        if not shipping_option or 'name' not in shipping_option or 'price' not in shipping_option:
            return Response(
                {"detail": "Uma opção de frete válida (com 'name' e 'cost') é obrigatória."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart['shipping_option'] = shipping_option
        request.session['cart'] = cart

        return Response(cart, status=status.HTTP_200_OK)


