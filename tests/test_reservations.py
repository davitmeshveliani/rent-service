from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from dateutil.relativedelta import relativedelta
from apps.listings.models.apartment import (
                                        Apartment,
                                        PropertyTypeChoices,)
from apps.reservations.models import Reservation


User = get_user_model()


class ReservationCRUDTests(APITestCase):

    def setUp(self):
        now = timezone.now()

        host_group = Group.objects.create(name="HOST")
        guest_group = Group.objects.create(name="GUEST")

        self.host = User.objects.create_user(
                                    email="host@example.com",
                                    username="hostuser",
                                    password="Password123!",)

        self.guest = User.objects.create_user(
                            email="guest@example.com",
                            username="guestuser",
                            password="Password123!",)

        self.other_user = User.objects.create_user(
                                    email="other@example.com",
                                    username="otheruser",
                                    password="Password123!",)

        self.host.groups.add(host_group)
        self.guest.groups.add(guest_group)
        self.other_user.groups.add(guest_group)

        self.listing = Apartment.objects.create(
            title="Modern Flat",
                        description="Nice place to stay",
                        price=Decimal("120.00"),
                        address_city="Berlin",
                        rooms=2,
                        property_type=PropertyTypeChoices.APARTMENT,
                        user=self.host,)

        self.reservation = Reservation.objects.create(
                                listing=self.listing,
                                user=self.guest,
                                start_date=now + timedelta(days=1),
                                end_date=now + timedelta(days=5),)

        self.list_url = "/api/reservations/"
        self.detail_url = (f"/api/reservations/"
                           f"{self.reservation.pk}/")

        self.cancel_url = (f"/api/reservations/"
                           f"{self.reservation.pk}/cancel/")

    def test_create_reservation(self):
        """
        Verify that a guest can create a reservation
        for an available future date range.
        """

        self.client.force_authenticate(user=self.guest)
        now = timezone.now()
        start_date = (now + timedelta(days=10)).replace(hour=12,minute=0,second=0,microsecond=0,)
        end_date = (now + timedelta(days=15)).replace(hour=12,minute=0,second=0,microsecond=0,)

        data = {
                    "listing": str(self.listing.pk),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),}

        response = self.client.post(self.list_url,data,format="json",)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED,)
        self.assertEqual(
            Reservation.objects.filter(listing=self.listing,user=self.guest,).count(),2,)

    def test_get_reservation_forbidden_for_other(self):
        """
        Verify that another user cannot access
        someone else's reservation.
        """

        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.detail_url)

        self.assertIn(
            response.status_code,[status.HTTP_403_FORBIDDEN,status.HTTP_404_NOT_FOUND,],)

    def test_cancel_reservation(self):
        """
        Verify that the reservation owner can cancel
        their reservation before the check-in time.
        """

        self.client.force_authenticate(user=self.guest)

        response = self.client.post(self.cancel_url,format="json",)

        self.assertEqual(response.status_code,status.HTTP_200_OK,)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status,Reservation.StatusChoice.CANCELLED,)

    def test_reservation_cannot_be_more_than_one_year_in_advance(self):
        self.client.force_authenticate(user=self.guest)

        start_date = timezone.now() + relativedelta(years=1, days=1)
        start_date = start_date.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

        end_date = start_date + timedelta(days=1)

        response = self.client.post(
            self.list_url,
            {
                "listing": str(self.listing.pk),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )