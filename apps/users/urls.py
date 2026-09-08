"""
URL routing configuration for user authentication and profile management endpoints.
"""

from typing import Any

from django.urls import path

from apps.users.views.user_views import (
    ChangePasswordView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    UserProfileView,
    UserRegistrationView,
)

app_name: str = "users"

urlpatterns: list[Any] = [
    # Authentication Endpoints (HttpOnly Cookies)
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),


    # User Profile Endpoints
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),


]