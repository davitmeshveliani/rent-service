"""
API controllers for user authentication, registration,
and profile management.
"""

from typing import Any

from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema_view
from apps.users.schema.user_schema import (
                                            registration_schema,
                                            login_schema,
                                            refresh_schema,
                                            logout_schema,
                                            profile_schema,
                                            change_password_schema,)

from apps.users.serializers.user_serializers import (
                                                    ChangePasswordSerializer,
                                                    LogoutSerializer,
                                                    UserProfileSerializer,
                                                    UserRegistrationSerializer,)


User = get_user_model()


# 1. REGISTRATION

@registration_schema
class UserRegistrationController(CreateAPIView):
    """API endpoint for registering a new user."""

    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        response_serializer = UserProfileSerializer(user,
                                 context=self.get_serializer_context(),)
        headers = self.get_success_headers(serializer.data)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,)


# 2. LOGIN

@login_schema
class CookieTokenObtainPairController(TokenObtainPairView):
    """
    Extends SimpleJWT's TokenObtainPairView to set access and refresh
    tokens as HttpOnly cookies upon successful login.
    """

    permission_classes = (AllowAny,)

    def post(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            access_token: str | None = response.data.get("access")
            refresh_token: str | None = response.data.get("refresh")

            if access_token:
                response.set_cookie(key="access_token",value=access_token,
                                httponly=True,secure=False,samesite="Lax",)
            if refresh_token:
                response.set_cookie(key="refresh_token",value=refresh_token,
                                    httponly=True,secure=False,samesite="Lax",)
            response.data = {"detail": "Login successful."}
        return response


# 3. REFRESH TOKEN

@refresh_schema
class CookieTokenRefreshController(TokenRefreshView):
    """
    Extends SimpleJWT's TokenRefreshView to update access token
    in HttpOnly cookie.
    """

    def post(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        data = (request.data.copy()
                    if hasattr(request.data, "copy")
                    else dict(request.data))

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token and "refresh" not in data:
            data["refresh"] = refresh_token
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                        {"detail": (
                                "Invalid or expired refresh token.")},
                        status=status.HTTP_401_UNAUTHORIZED,)

        response = Response(
                        serializer.validated_data,
                        status=status.HTTP_200_OK,)

        access_token: str | None = response.data.get("access")

        if access_token:
            response.set_cookie(key="access_token",value=access_token,
                                httponly=True,secure=False,samesite="Lax",)

        response.data = {
            "detail": "Token refreshed successfully."}

        return response


# 4. LOGOUT

@logout_schema
class LogoutController(generics.GenericAPIView):
    """
    API endpoint to log out users by blacklisting the refresh token
    and deleting authentication cookies.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self,request: Request,*args: Any,**kwargs: Any,) -> Response:
        data = (
                request.data.copy()
                if hasattr(request.data, "copy")
                else dict(request.data))

        if ("refresh" not in data
            and "refresh_token" in request.COOKIES):
            data["refresh"] = request.COOKIES.get("refresh_token")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,)

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


# 5. USER PROFILE

@profile_schema
class UserProfileController(RetrieveUpdateAPIView):
    """API endpoint to retrieve and update authenticated user's profile."""

    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self) -> Any:
        return self.request.user


# 6. CHANGE PASSWORD

@extend_schema_view(post=change_password_schema)
class ChangePasswordController(generics.GenericAPIView):
    """API endpoint to update user password."""

    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self) -> Any:
        return self.request.user

    def post(self,request: Request,*args: Any,**kwargs: Any,) -> Response:

        user = self.get_object()
        serializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])

        user.save()

        return Response(
                    {"detail": (
                            "Password updated successfully.")},
                    status=status.HTTP_200_OK,)