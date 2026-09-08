"""
Custom authentication backends for REST framework, including HttpOnly Cookie JWT extraction.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token

User = get_user_model()


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class.

    First checks the HttpOnly cookie ('access_token') for web clients.
    If missing, falls back to checking the standard Authorization header (Authorization: Bearer <token>).
    Includes CSRF enforcement when cookie authentication is used.
    """

    def enforce_csrf(self, request: Request) -> None:
        """
        Enforces CSRF protection for cookie-based requests.
        """
        check = CSRFCheck(get_response=lambda req: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request: Request) -> tuple[AbstractBaseUser, Token] | None:

        """
        Authenticates the incoming request using cookie or header credentials.
        """
        # 1. First check the HttpOnly cookie (Web Clients Priority)
        cookie_raw_token: str | None = request.COOKIES.get("access_token")

        if cookie_raw_token:
            try:
                # Validate CSRF token when authentication is based on cookies
                self.enforce_csrf(request)

                raw_token_bytes: bytes = cookie_raw_token.encode("utf-8")
                validated_token: Token = self.get_validated_token(raw_token_bytes)
                user_from_cookie: AbstractBaseUser = self.get_user(validated_token)
                return user_from_cookie, validated_token

            except exceptions.AuthenticationFailed:
                # Ignore invalid/expired cookie and continue as anonymous.
                pass

        # 2. If no cookie is present, fall back to standard HTTP Authorization header
        header: bytes | None = self.get_header(request)
        if header is not None:
            raw_token: bytes | None = self.get_raw_token(header)
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                user: AbstractBaseUser = self.get_user(validated_token)
                return user, validated_token

        return None


class CookieAuthScheme(OpenApiAuthenticationExtension):
    target_class = "apps.users.authentication.CookieJWTAuthentication"
    name = "cookieAuth"

    def get_security_definition(self, auto_schema):
        return {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "HttpOnly JWT access token cookie (or standard Bearer token).",}