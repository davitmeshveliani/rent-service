from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class JWTAuthTestCase(APITestCase):

    def setUp(self):
        self.username = "jwtuser"
        self.email = "jwtuser@example.com"
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(username=self.username,email=self.email,password=self.password,)
        self.token_url = reverse("users:login")
        self.refresh_url = reverse("users:token-refresh")

    def test_obtain_token_success_and_sets_cookies(self):
        """
        Verify that successful login sets both access and refresh
        JWT tokens in HttpOnly cookies.
        """

        response = self.client.post(self.token_url,{"email": self.email,"password": self.password,},
                                                                                format="json",)
        self.assertEqual(response.status_code,status.HTTP_200_OK,)


        # The login endpoint must set both JWT cookies.
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        # Both authentication cookies must be HttpOnly.
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_obtain_token_fail_with_wrong_password(self):
        """
        Verify that login is rejected when the password is incorrect.
        """

        response = self.client.post(self.token_url,{"email": self.email,
                                "password": "WrongPassword!",},format="json",)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)

    def test_refresh_token_success(self):
        """
        Verify that a valid refresh token stored in the cookie
        can be used to obtain a new access token.
        """

        login_response = self.client.post(
            self.token_url,{"email": self.email,"password": self.password,},
                                                        format="json",)

        self.assertEqual(login_response.status_code,status.HTTP_200_OK,)

        # Make sure login created the refresh token cookie.
        self.assertIn("refresh_token",login_response.cookies,)

        refresh_token = login_response.cookies["refresh_token"].value

        # Clear the client cookies so the refresh request is controlled explicitly.
        self.client.cookies.clear()

        # Send the refresh token through the cookie-based authentication flow.
        self.client.cookies["refresh_token"] = refresh_token

        refresh_response = self.client.post(self.refresh_url,format="json",)

        self.assertEqual(refresh_response.status_code,status.HTTP_200_OK,)

        # A successful refresh must issue a new access token cookie.
        self.assertIn("access_token",refresh_response.cookies,)

        self.assertTrue(refresh_response.cookies["access_token"]["httponly"])

    def test_refresh_token_fail_with_invalid_token(self):
        """
        Verify that refresh is rejected when the refresh token is invalid.
        """

        # Put an invalid token into the refresh cookie.
        self.client.cookies["refresh_token"] = ("invalid_fake_refresh_token_string")

        refresh_response = self.client.post(self.refresh_url,format="json",)

        self.assertEqual(refresh_response.status_code,status.HTTP_401_UNAUTHORIZED,)

