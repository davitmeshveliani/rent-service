from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions

from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


@extend_schema_view(
    get=extend_schema(
        summary="List or filter reviews",
        description="Public endpoint to list reviews. Can be filtered by rating or listing ID.",
        auth=[],),

    post=extend_schema(
        summary="Create a new review",
        description="Requires authentication. User is automatically set from token.",),)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rating", "listing"]

    def get_queryset(self):
        return (Review.objects.select_related
                ("listing", "user", "listing__user").all())

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
                summary="Get authenticated user's reviews",
                description="Retrieve all reviews created by the currently logged-in user.",)


class MyReviewsAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Review.objects.none()

        return (Review.objects.filter(user=self.request.user).select_related
                        ("listing", "user", "listing__user").order_by("-created_at"))


@extend_schema_view(
    get=extend_schema(
        summary="Retrieve review details",
        auth=[],),  # GET

    put=extend_schema(
        operation_id="reviews_update",
        summary="Update a review",),

    patch=extend_schema(
        operation_id="reviews_partial_update",
        summary="Partially update a review",),

    delete=extend_schema(
        summary="Delete a review",),)


class ReviewRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        return (Review.objects.select_related
                ("listing", "user", "listing__user").all())