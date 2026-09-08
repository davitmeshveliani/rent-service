
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.listings.models.apartment import Apartment, PropertyTypeChoices
from apps.users.choices.choices import RoleChoices


User = get_user_model()


class APISecurityTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
                                email="user1@example.com",
                                username="user1",
                                password="Password123!",
                                role=RoleChoices.HOST,)

        self.user2 = User.objects.create_user(
                                email="user2@example.com",
                                username="user2",
                                password="Password123!",
                                role=RoleChoices.GUEST,)

        self.apartment = Apartment.objects.create(
                                title="Hamburg Apartment",
                                description="Nice view near harbor",
                                price=Decimal("100.00"),
                                address_city="Hamburg",
                                rooms=2,
                                property_type=PropertyTypeChoices.APARTMENT,
                                user=self.user1,)

        self.list_url = reverse("listing-list-create")
        self.detail_url = reverse("listing-detail",kwargs={"pk": self.apartment.pk},)

    def test_anonymous_user_can_read(self):
        """
        Verify that an anonymous user can access the public listings endpoint.
        """

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK,)

    def test_anonymous_user_cannot_create(self):
        """
        Verify that an anonymous user cannot create a listing.
        """

        data = {
                    "title": "New Frankfurt Flat",
                    "description": "A comfortable apartment",
                    "price": "120.00",
                    "address_city": "Frankfurt",
                    "rooms": 1,
                    "property_type": PropertyTypeChoices.APARTMENT,}

        response = self.client.post(self.list_url,data,format="json",)

        self.assertIn(response.status_code,
            [status.HTTP_401_UNAUTHORIZED,status.HTTP_403_FORBIDDEN,],)

    def test_other_user_cannot_update_listing(self):
        """
        Verify that another user cannot modify someone else's listing.
        """

        self.client.force_authenticate(user=self.user2)

        response = self.client.patch(
            self.detail_url,{"title": "Unauthorized Update"},format="json",)

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN,)
        self.apartment.refresh_from_db()
        self.assertEqual(self.apartment.title,"Hamburg Apartment",)

    def test_other_user_cannot_delete_listing(self):
        """
        Verify that another user cannot delete someone else's listing.
        """

        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN,)
        self.apartment.refresh_from_db()
        self.assertTrue(
            self.apartment.is_active,)

    def test_owner_can_delete_listing(self):
        """
        Verify that the listing owner can delete their listing
        through the API and that it becomes inactive.
        """

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT,)
        self.apartment.refresh_from_db()
        self.assertFalse(
            self.apartment.is_active,)

