from django.urls import path

from apps.listings.controllers import (
                        ApartmentImageDeleteController,
                        ApartmentImageUploadController,
                        ListingDetailController,
                        ListingListCreateController,
                        MyListingsController,
                        PopularListingsController,
                        PopularSearchQueriesController,
                        UserViewHistoryController,)

urlpatterns = [
    path("",ListingListCreateController.as_view(),name="listing-list-create",),
    path("my/",MyListingsController.as_view(),name="my-listings",),
    path("history/",UserViewHistoryController.as_view(),name="view-history",),
    path("popular/",PopularListingsController.as_view(),name="popular-listings",),
    path("popular-searches/",PopularSearchQueriesController.as_view(),name="popular-searches",),
    path("images/upload/",ApartmentImageUploadController.as_view(),name="image-upload",),
    path("images/<uuid:pk>/",ApartmentImageDeleteController.as_view(),name="image-delete",),
    path("<uuid:pk>/",ListingDetailController.as_view(),name="listing-detail",),]