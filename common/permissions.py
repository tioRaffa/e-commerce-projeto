from rest_framework import permissions


class IsOwenerAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        return obj.user == self.request.user