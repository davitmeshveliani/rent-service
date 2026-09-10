from rest_framework.permissions import BasePermission


class IsHostUser(BasePermission):
    """
    Allows access only to authenticated users
    who belong to the HOST or BOTH group.
    """

    message = "Only host users are allowed to perform this action."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.groups.filter(
            name__in=["HOST", "BOTH"]
        ).exists()


class IsOwnerOrReadOnly(BasePermission):
    """
    Allows read access to everyone.
    Write access is allowed only to the owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return obj.user == request.user