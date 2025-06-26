from rest_framework import viewsets
from .models import AddressModel
from .serializer import AddressSerializer
from common.permissions import IsOwenerAuth
from rest_framework import permissions

class AddressViewset(viewsets.ModelViewSet):
    queryset = AddressModel.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwenerAuth
    ]

    def get_queryset(self):
        qs = AddressModel.objects.select_related('user')
        return qs.filter(user=self.request.user).order_by('-id')


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)