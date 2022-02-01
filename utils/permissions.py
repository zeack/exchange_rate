from rest_framework import permissions
from core.models import User

class SuperOnly(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.is_superuser
        else:
            return False


class CurrentUserObj(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_authenticated:
            if getattr(obj, 'username', 'o') == getattr(user, 'username', 'u') \
                and obj.pk == user.pk:
                return True
            elif getattr(obj, 'user_id', 0) == user.id:
                return True
            return False
        else:
            return False
