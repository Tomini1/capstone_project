from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """
    Allow owners to read/write their own objects; admins can access all; others denied.
    Assumes the object has a 'user' attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return getattr(obj, "user_id", None) == request.user.id
