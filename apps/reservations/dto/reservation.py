"""
DTO compatibility layer for reservation serializers.
"""

from apps.reservations.serializers.reservation_serializers import (
                                    ReservationSerializer,
                                    ReservationUpdateSerializer,)

__all__ = ["ReservationSerializer",
            "ReservationUpdateSerializer",]