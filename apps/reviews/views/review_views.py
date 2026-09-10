from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema_view
from apps.reviews.models import Review
from apps.reviews.schemas.review_schema import (
                                                my_reviews_schema,
                                                review_detail_schema,
                                                review_list_create_schema,)

from apps.reviews.serializers import ReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


@review_list_create_schema
class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rating", "listing"]

    def get_queryset(self):
        return Review.objects.select_related("listing", "user", "listing__user").all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(get=my_reviews_schema)
class MyReviewsAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()
        return (Review.objects.filter(user=self.request.user).select_related
                    ("listing", "user", "listing__user").order_by("-created_at"))


@review_detail_schema
class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        return Review.objects.select_related("listing", "user", "listing__user").all()