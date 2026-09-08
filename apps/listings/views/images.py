"""
Compatibility exports for image controllers.
"""

from apps.listings.controllers.image_controller import (
    ApartmentImageDeleteController,
    ApartmentImageUploadController,)

ApartmentImageUploadView = ApartmentImageUploadController
ApartmentImageDeleteView = ApartmentImageDeleteController

__all__ = [
    "ApartmentImageUploadView",
    "ApartmentImageDeleteView",]