from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsModerator(BasePermission):
    """Права для группы модераторов"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """Права для владельца объекта"""

    def has_object_permission(self, request, view, obj):
        # if not request.user.is_authenticated:
        #     return False
        return obj.owner == request.user


class IsOwnerOrReadOnly(BasePermission):
    """Права: чтение для всех, изменение только для владельца"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user