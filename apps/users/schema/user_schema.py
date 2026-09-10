"""
Swagger schemas for user API endpoints.
"""

from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.serializers import (ChangePasswordSerializer,
                                    UserProfileSerializer,
                                    UserRegistrationSerializer,)

# GENERIC ERROR RESPONSE

GenericErrorResponse = inline_serializer(
    name="UserErrorResponse",
    fields={
        "detail": serializers.CharField(
            help_text="Detailed error description.")},)

# MULTI-MEDIA TYPE REQUEST DICTIONARIES

registration_request_types = {
                            "application/json": UserRegistrationSerializer,
                            "multipart/form-data": UserRegistrationSerializer,
                            "application/x-www-form-urlencoded": UserRegistrationSerializer,}

profile_update_request_types = {
                        "application/json": UserProfileSerializer,
                        "multipart/form-data": UserProfileSerializer,
                        "application/x-www-form-urlencoded": UserProfileSerializer,}

change_password_request_types = {
                                "application/json": ChangePasswordSerializer,
                                "multipart/form-data": ChangePasswordSerializer,
                                "application/x-www-form-urlencoded": ChangePasswordSerializer,}


# 1. REGISTRATION

registration_schema = extend_schema(
    summary="Register a new user",
    description="API endpoint for registering a new user.",
    auth=[],
    request=registration_request_types,
    responses={
                201: OpenApiResponse(description="User successfully registered."),
                400: OpenApiResponse(
                    response=GenericErrorResponse, description="Validation Error"),},)


# 2. LOGIN

login_schema = extend_schema(
    summary="User Login",
    description=(
        "Authenticates a user and sets access and refresh tokens as HttpOnly cookies."),
    auth=[],
    request=TokenObtainPairSerializer,
    responses={
                200: OpenApiResponse(description="Successfully authenticated."),
                401: OpenApiResponse(
                    response=GenericErrorResponse, description="Invalid credentials."),},)


# 3. REFRESH TOKEN

refresh_schema = extend_schema(
    summary="Refresh Access Token",
    description=(
        "Extends SimpleJWT's TokenRefreshView to update access token in HttpOnly cookie."),
    auth=[],
    responses={200: OpenApiResponse(
                    description="Access token successfully refreshed in cookie."),
                401: OpenApiResponse(response=GenericErrorResponse,
                                    description="Invalid or expired refresh token.",),},)


# 4. LOGOUT

logout_schema = extend_schema(
    summary="Logout user",
    description=("Logs out the authenticated user by blacklisting the refresh token stored "
                "in the HttpOnly cookie and deleting authentication cookies."),
    request=None,
    responses={200: OpenApiResponse(description="Successfully logged out."),
                400: OpenApiResponse(
                    response=GenericErrorResponse, description="Invalid refresh token"),
                 401: OpenApiResponse(response=GenericErrorResponse, description="Unauthorized"),},)


# 5. USER PROFILE

profile_schema = extend_schema_view(
    get=extend_schema(
        summary="Retrieve user profile",
        operation_id="users_profile_retrieve",
        responses={200: UserProfileSerializer,
                    401: OpenApiResponse(
                        response=GenericErrorResponse, description="Unauthorized"),},),
    put=extend_schema(
        summary="Update user profile",
        operation_id="users_profile_update",
        request=profile_update_request_types,
        responses={200: UserProfileSerializer,
                    400: OpenApiResponse(response=GenericErrorResponse, description="Validation Error"),
                    401: OpenApiResponse(response=GenericErrorResponse, description="Unauthorized"),},),
    patch=extend_schema(
        summary="Partial update user profile",
        operation_id="users_profile_partial_update",
        request=profile_update_request_types,
        responses={200: UserProfileSerializer,
                    400: OpenApiResponse(response=GenericErrorResponse, description="Validation Error"),
                    401: OpenApiResponse(response=GenericErrorResponse, description="Unauthorized"),},),)


# 6. CHANGE PASSWORD

change_password_schema = extend_schema(
    summary="Change user password",
    operation_id="users_change_password",
    request=change_password_request_types,
    responses={200: OpenApiResponse(description="Password updated successfully."),
                400: OpenApiResponse(response=GenericErrorResponse, description="Validation Error"),
                401: OpenApiResponse(response=GenericErrorResponse, description="Unauthorized"),},)