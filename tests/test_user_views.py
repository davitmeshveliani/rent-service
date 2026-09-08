from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.choices.choices import RoleChoices


User = get_user_model()


class UserAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
                                        username="testuser",
                                        email="test@example.com",
                                        password="testpassword123",
                                        role=RoleChoices.GUEST,)

        self.register_url = reverse("users:register")
        self.profile_url = reverse("users:profile")
        self.change_password_url = reverse("users:change-password")

    def test_user_registration(self):
        """Test successful user registration."""
        data = {
                    "username": "newuser",
                    "password": "newpassword123",
                    "email": "new@example.com",
                    "role": RoleChoices.GUEST,
                }

        response = self.client.post(self.register_url,data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(User.objects.count(), 2)
        self.assertNotIn("password", response.data)

    def test_get_user_profile_authenticated(self):
        """Test that an authenticated user can retrieve their profile."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.assertEqual(response.data["email"],self.user.email,)

    def test_get_user_profile_unauthenticated(self):
        """Test that unauthenticated access to the profile is rejected."""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,)

    def test_update_user_profile(self):
        """Test that an authenticated user can update their profile."""
        self.client.force_authenticate(user=self.user)

        update_data = {"first_name": "UpdatedName",}
        response = self.client.patch(self.profile_url,update_data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name,"UpdatedName",)

    def test_change_password(self):
        """Test successful password change."""
        self.client.force_authenticate(user=self.user)

        data = {
                    "old_password": "testpassword123",
                    "new_password": "newsecurepassword123",
                }

        response = self.client.post(self.change_password_url,data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password("newsecurepassword123"))

    def test_change_password_with_wrong_old_password(self):
        """Test that an incorrect old password is rejected."""
        self.client.force_authenticate(user=self.user)

        data = { "old_password": "wrongpassword123",
                "new_password": "newsecurepassword123",
                }

        response = self.client.post(self.change_password_url,data,format="json",)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,)



    def test_user_login(self):
            """Test successful user login and authentication cookies."""
            login_url = reverse("users:login")

            data = {
                        "email": "test@example.com",
                        "password": "testpassword123",}

            response = self.client.post(login_url,data,format="json",)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                            response.data["detail"],
                            "Login successful.",)

            self.assertIn("access_token", response.cookies)
            self.assertIn("refresh_token", response.cookies)

            self.assertTrue(response.cookies["access_token"]["httponly"])
            self.assertTrue(response.cookies["refresh_token"]["httponly"])

