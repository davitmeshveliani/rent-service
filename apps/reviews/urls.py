from django.urls import path
from .views import (
    MyReviewsAPIView,
    ReviewListCreateAPIView,
    ReviewRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path('', ReviewListCreateAPIView.as_view(), name='review-list'),
    path('my/', MyReviewsAPIView.as_view(), name='my-reviews'),
    path('<uuid:pk>/', ReviewRetrieveUpdateDestroyAPIView.as_view(), name='review-detail'),
]