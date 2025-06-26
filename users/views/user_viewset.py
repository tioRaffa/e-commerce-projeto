from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from users.serializer import UserUpdateSerializer, ProfileUpdateSerializer, UserReadSerializer
from models.profile import ProfileModel

class UserViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'me' and self.request.method in ['PATCH']:
            return UserUpdateSerializer
        return UserReadSerializer
    
    @action(detail=False, methods=['get', 'patch'], url_name='me')
    def me(self, request, *args, **kwargs):
        user = self.request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)   

        if request.method == 'PATCH':
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_execptions=True)
            validate_data = serializer.validated_data

            user.first_name = validate_data.get('fist_name', user.first_name)
            user.last_name = validate_data.get('last_name', user.last_name)
            user.save(update_files['first_name', 'last_name'])

            profile_data = validate_data.get('profile')
            if profile_data:
                profile, created = ProfileModel.objects.get_or_create(user=user)

                profile_serializer = ProfileUpdateSerializer(
                    isnstance=profile, data=profile_data, partial=True
                )
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()

            read_serializer = UserReadSerializer(user)
            return Response(read_serializer.data, status=status.HTTP_200_OK)