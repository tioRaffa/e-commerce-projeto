from rest_framework import viewsets, status, permissions
from .models import AddressModel
from .serializer import AddressSerializer
from common.permissions import IsOwenerAuth
from rest_framework.response import Response

class AddressViewset(viewsets.ModelViewSet):
    queryset = AddressModel.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        qs = AddressModel.objects.select_related('user')
        return qs.filter(user=self.request.user).order_by('-id')


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        address_count = self.get_queryset().count()
        if address_count >=3:
            return Response({
                "detail": "Limite de 3 endereços por Usuario atingidos!"
            },
            status=status.HTTP_400_BAD_REQUEST
            )


        return super().create(request, *args, **kwargs)