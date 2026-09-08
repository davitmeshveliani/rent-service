
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class JWTAdvancedAuthTestCase(APITestCase):

    def setUp(self):
        self.username = "advanced_jwt_user"
        self.email = "adv_jwt@example.com"
        self.password = "StrongPassword123!"

        self.user = User.objects.create_user(username=self.username,email=self.email,password=self.password,)
        self.token_url = reverse("users:login")
        self.profile_url = reverse("users:profile")

    def test_access_token_with_invalid_signature_fails(self):
        """
        Verify that access is denied when the JWT stored
        in the authentication cookie has been tampered with.
        """

        # Authenticate the user and receive the JWT in the HttpOnly cookie.
        login_response = self.client.post(
            self.token_url,{"email": self.email,"password": self.password,},format="json",)

        self.assertEqual(login_response.status_code,status.HTTP_200_OK,)

        # Make sure the login response contains the access token cookie.
        self.assertIn("access_token", login_response.cookies)

        access_token = login_response.cookies["access_token"].value

        # Remove the valid authentication cookie before sending the tampered token.
        self.client.cookies.clear()

        # Modify the original JWT so that its signature becomes invalid.
        tampered_token = access_token[:-5] + "XXXXX"

        # Put the invalid token into the authentication cookie.
        self.client.cookies["access_token"] = tampered_token

        # The protected endpoint must reject the invalid JWT.
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)

    def test_unauthenticated_request_to_protected_endpoint(self):
        """
        Verify that a protected endpoint cannot be accessed
        without authentication.
        """

        # Remove all authentication cookies from the test client.
        self.client.cookies.clear()

        # Request the protected profile endpoint without authentication.
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)
