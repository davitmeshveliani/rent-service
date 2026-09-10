"""
API controllers for listing metrics and user history.
"""

from django.db.models import Count, QuerySet
from drf_spectacular.utils import (
                                OpenApiResponse,
                                extend_schema,
                                extend_schema_view,
                                inline_serializer,)
from rest_framework import generics, permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.listings.services import ListingService
from apps.listings.models import (
                                Apartment,
                                ListingViewHistory,
                                SearchHistory,)
from apps.listings.serializers import (
                                        ApartmentSerializer,
                                        ListingViewHistorySerializer,
                                        PopularSearchSerializer,)


ErrorSchema = inline_serializer(
    name="MetricsControllerErrorResponse",
    fields={"detail": serializers.CharField(default="Error detail message.")},)


@extend_schema(
    summary="Get user's view history",
    description=("Retrieves the last 20 viewed apartments "
                        "for the authenticated user."),
    responses={
                200: ListingViewHistorySerializer(many=True),
                401: OpenApiResponse(response=ErrorSchema,description="Authentication required",),},)

class UserViewHistoryController(generics.ListAPIView):
    serializer_class = ListingViewHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[ListingViewHistory]:
        if getattr(self, "swagger_fake_view", False):
            return ListingViewHistory.objects.none()

        return (ListingViewHistory.objects.filter
                                    (user=self.request.user).select_related
                                    ("listing", "listing__user").prefetch_related
                                    ("listing__images").order_by("-created_at")[:20])


@extend_schema_view(
    get=extend_schema(
        request=None,
        responses={
                    200: PopularSearchSerializer(many=True),},
        summary="Fetch top 10 popular searches",
        operation_id="listings_popular_searches",
        auth=[],
                ),)


class PopularSearchQueriesController(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self,request: Request,*args,**kwargs,) -> Response:
        popular_searches = (SearchHistory.objects.values("query").annotate(
                count=Count("query")).order_by("-count","query",)[:10])
        return Response(popular_searches,status=status.HTTP_200_OK,)


@extend_schema(
    summary="Get popular listings",
    description=("Retrieves active listings ranked by views and "
                            "review activity."),
    responses={
        200: ApartmentSerializer(many=True),},
    auth=[],)

class PopularListingsController(generics.ListAPIView):
    serializer_class = ApartmentSerializer
    permission_classes = [permissions.AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = ListingService()

    def get_queryset(self) -> QuerySet[Apartment]:
        if getattr(self,"swagger_fake_view",False,):
            return Apartment.objects.none()
        return self.service.get_popular_listings()