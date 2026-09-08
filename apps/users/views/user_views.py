"""
Compatibility views for user API endpoints.

The actual API logic is implemented in controllers.
"""

from apps.users.controllers.user_controller import (
                        ChangePasswordController,
                        CookieTokenObtainPairController,
                        CookieTokenRefreshController,
                        LogoutController,
                        UserProfileController,
                        UserRegistrationController,
                    )


UserRegistrationView = UserRegistrationController

CookieTokenObtainPairView = CookieTokenObtainPairController

CookieTokenRefreshView = CookieTokenRefreshController

LogoutView = LogoutController

UserProfileView = UserProfileController

ChangePasswordView = ChangePasswordController