"""
Custom REST framework permissions for listing ownership and host authorization.
"""

from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission allowing read-only access to any user,
    but restricting write operations exclusively to the apartment owner.
    """

    def has_object_permission(self,request: Request,view: APIView,obj: Any,) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsHostUser(permissions.BasePermission):
    """
    Permission allowing authenticated HOST and BOTH users.
    """

    def has_permission(
        self,
        request: Request,
        view: APIView,
    ) -> bool:
        user = request.user

        if not user.is_authenticated:
            return False

        return user.groups.filter(
            name__in=["HOST", "BOTH"]
        ).exists()