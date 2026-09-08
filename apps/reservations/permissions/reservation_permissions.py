"""
Custom permission classes for reservation access control.
"""

from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsReservationParticipant(permissions.BasePermission):
    """
    Custom permission to allow access only to the reservation owner (Guest)
    or the property owner (Host).
    """

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return obj.user == user or getattr(obj.listing, "user", None) == user