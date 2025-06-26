from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from users.serializer import UserUpdateSerializer, ProfileUpdateSerializer, UserReadSerializer
from users.models import ProfileModel

class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'me' and self.request.method in ['PATCH']:
            return UserUpdateSerializer
        return UserReadSerializer
    
    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request, *args, **kwargs):
        user = self.request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)   

        elif request.method == 'PATCH':
            serializer = self.get_serializer(instance=user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            user.first_name = validated_data.get('first_name', user.first_name)
            user.last_name = validated_data.get('last_name', user.last_name)
            user.save(update_fields=['first_name', 'last_name'])

            profile_data = validated_data.get('profile')
            if profile_data:
                profile, created = ProfileModel.objects.get_or_create(user=user)

                profile_serializer = ProfileUpdateSerializer(
                    instance=profile, data=profile_data, partial=True
                )
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()

            read_serializer = UserReadSerializer(user)
            return Response(read_serializer.data, status=status.HTTP_200_OK)