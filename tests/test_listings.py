from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.listings.models.apartment import Apartment, PropertyTypeChoices
from apps.users.choices.choices import RoleChoices


User = get_user_model()


class ListingCRUDTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
                                email="owner@example.com",
                                username="owner",
                                password="Password123!",
                                role=RoleChoices.HOST,)

        self.other_user = User.objects.create_user(
                                    email="client@example.com",
                                    username="client",
                                    password="Password123!",
                                    role=RoleChoices.GUEST,)

        self.listing = Apartment.objects.create(
                                        title="Berlin Center Flat",
                                        description="Comfortable living space in Mitte",
                                        price=Decimal("100.00"),
                                        address_city="Berlin",
                                        rooms=2,
                                        property_type=PropertyTypeChoices.APARTMENT,
                                        user=self.user,)

        self.list_url = reverse("listing-list-create")
        self.detail_url = reverse("listing-detail",kwargs={"pk": self.listing.pk},)

    def test_list_listings(self):
        """
        Verify that listings can be retrieved successfully.
        """

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)

    def test_create_listing_as_host(self):
        """
        Verify that a HOST can create a new listing.
        """

        self.client.force_authenticate(user=self.user)

        data = {
                    "title": "Munich Studio",
                    "description": "Cozy studio near Marienplatz",
                    "price": "250.00","address_city": "Munich","rooms": 1,
                    "property_type": PropertyTypeChoices.STUDIO,}

        response = self.client.post(self.list_url,data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)

        self.assertEqual(Apartment.objects.filter(user=self.user).count(),2,)

    def test_update_listing_owner(self):
        """
        Verify that the listing owner can update their listing.
        """

        self.client.force_authenticate(user=self.user)

        data = {"title": "Updated Berlin Flat",}

        response = self.client.patch(self.detail_url,
            data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.listing.refresh_from_db()
        self.assertEqual(
            self.listing.title,"Updated Berlin Flat",)

    def test_update_listing_forbidden_for_other(self):
        """
        Verify that another user cannot modify someone else's listing.
        """

        self.client.force_authenticate(user=self.other_user)

        data = {"title": "Hacked Title",}

        response = self.client.patch(self.detail_url,
            data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN,)
        self.listing.refresh_from_db()
        self.assertEqual(
            self.listing.title,"Berlin Center Flat",)

    def test_delete_listing(self):
        """
        Verify that the owner can delete a listing through
        the API and that the listing is soft-deleted.
        """

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT,)
        self.listing.refresh_from_db()

        # The listing remains in the database but becomes inactive.
        self.assertFalse(
            self.listing.is_active,)

