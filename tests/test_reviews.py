from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.listings.models.apartment import Apartment
from apps.reservations.models import Reservation
from apps.reviews.models import Review
from apps.users.choices.choices import RoleChoices

User = get_user_model()


class ReviewCRUDTests(APITestCase):

    def setUp(self):
        self.host = User.objects.create_user(
                                            email="host@example.com",
                                            username="host",
                                            password="Password123!",
                                            role=RoleChoices.HOST,)

        self.user = User.objects.create_user(
                                                email="reviewer@example.com",
                                                username="reviewer",
                                                password="Password123!",
                                                role=RoleChoices.GUEST,)

        self.apartment = Apartment.objects.create(
                                                title="Stuttgart Flat",
                                                price=Decimal("120.00"),
                                                address_city="Stuttgart",
                                                rooms=2,
                                                user=self.host,)

        now = timezone.now()

        self.reservation = Reservation.objects.create(
                                                user=self.user,
                                                listing=self.apartment,
                                                start_date=now - timedelta(days=10),
                                                end_date=now - timedelta(days=5),
                                                status=Reservation.StatusChoice.CONFIRMED,)

        self.review = Review.objects.create(
                                            user=self.user,
                                            listing=self.apartment,
                                            rating=4,
                                            comment="Great location and clean environment!",)

        self.list_url = reverse("review-list")
        self.detail_url = reverse("review-detail",
                                            kwargs={"pk": self.review.pk},)

    def test_create_review_with_valid_comment(self):
        """A guest can create a review after completing a confirmed stay."""
        apt2 = Apartment.objects.create(
                                        title="Düsseldorf Apartment",
                                        price=Decimal("150.00"),
                                        address_city="Düsseldorf",
                                        rooms=3,
                                        user=self.host,)

        now = timezone.now()

        Reservation.objects.create(
                                    user=self.user,
                                    listing=apt2,
                                    start_date=now - timedelta(days=10),
                                    end_date=now - timedelta(days=5),
                                    status=Reservation.StatusChoice.CONFIRMED,)

        self.client.force_authenticate(user=self.user)

        data = {
                    "listing": apt2.pk,
                    "rating": 5,
                    "comment": "Wonderful apartment, highly recommended!",}

        response = self.client.post(self.list_url,data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(Review.objects.count(), 2)

    def test_update_review(self):
        """A review owner can update their review."""
        self.client.force_authenticate(user=self.user)

        data = {"rating": 3,"comment": "Average experience after checking again.",}

        response = self.client.patch(self.detail_url,
            data,format="json",)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)

    def test_delete_review(self):
        """A review owner can delete their review."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT,)
        self.assertEqual(Review.objects.count(), 0)

