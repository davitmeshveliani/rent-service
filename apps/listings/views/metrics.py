"""
Compatibility exports for listing metrics controllers.

The actual API logic lives in:
apps.listings.controllers.metrics_controller
"""

from apps.listings.controllers.metrics_controller import (
    PopularListingsController,
    PopularSearchQueriesController,
    UserViewHistoryController,)

UserViewHistoryAPIView = UserViewHistoryController
PopularSearchQueriesAPIView = PopularSearchQueriesController
PopularListingsAPIView = PopularListingsController

__all__ = [
    "UserViewHistoryAPIView",
    "PopularSearchQueriesAPIView",
    "PopularListingsAPIView",]