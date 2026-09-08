"""
Seed the database with realistic fake Rentify data.
"""

import random
from datetime import timedelta
from decimal import Decimal

import requests
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from djmoney.money import Money

from apps.listings.models.apartment import (
    Apartment,
    PropertyTypeChoices,
)
from apps.listings.models.apartment_image import ApartmentImage
from apps.listings.models.history import (
    ListingViewHistory,
    SearchHistory,
)
from apps.reservations.models import Reservation
from apps.reviews.models import Review
from apps.users.choices.choices import GenderChoices, RoleChoices
from apps.users.models import User


class Command(BaseCommand):
    """Seed database with fake Rentify data."""

    help = "Seed database with Rentify fake data"

    @transaction.atomic
    def handle(self, *args, **options):
        # --------------------------------------------------
        # USERS
        # --------------------------------------------------
        self.stdout.write("Creating users...")

        users = []

        first_names = [
            "Alexander",
            "Dmitry",
            "Michael",
            "Ivan",
            "Artem",
            "Anna",
            "Maria",
            "Elena",
            "Olga",
            "Sofia",
        ]

        last_names = [
            "Müller",
            "Schmidt",
            "Schneider",
            "Fischer",
            "Weber",
            "Meyer",
            "Wagner",
            "Becker",
            "Schulz",
            "Hoffmann",
        ]

        roles = [
            RoleChoices.HOST,
            RoleChoices.GUEST,
            RoleChoices.BOTH,
        ]

        genders = [
            GenderChoices.MALE,
            GenderChoices.FEMALE,
            GenderChoices.OTHER,
        ]

        for i in range(1, 101):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                phone_number=f"+49150000{i:04d}",
                address=f"Street {i}",
                birthday=(
                    timezone.now().date()
                    - timedelta(days=random.randint(7000, 18000))
                ),
                bio=f"Test user {i}",
                gender=random.choice(genders),
                role=random.choice(roles),
                is_active=True,
            )

            user.set_password("Test12345!")
            users.append(user)

        User.objects.bulk_create(users)
        users = list(User.objects.all())

        # --------------------------------------------------
        # DJANGO GROUPS
        # --------------------------------------------------
        self.stdout.write("Assigning users to Django groups...")

        groups = {
            group_name: Group.objects.get_or_create(
                name=group_name
            )[0]
            for group_name in (
                "GUEST",
                "HOST",
                "BOTH",
            )
        }

        for user in users:
            group = groups.get(user.role)

            if group:
                user.groups.add(group)

        # --------------------------------------------------
        # APARTMENTS
        # --------------------------------------------------
        self.stdout.write("Creating apartments...")

        cities = [
            "Berlin",
            "Munich",
            "Hamburg",
            "Frankfurt",
            "Cologne",
            "Stuttgart",
            "Düsseldorf",
        ]

        hosts = [
            user
            for user in users
            if user.role in (
                RoleChoices.HOST,
                RoleChoices.BOTH,
            )
        ]

        apartments = []

        for i in range(1, 201):
            property_type = random.choice(
                list(PropertyTypeChoices)
            )

            if property_type == PropertyTypeChoices.STUDIO:
                rooms = 1
                price = Decimal(
                    str(random.randint(2000, 5000))
                )
                title_prefix = "Cozy Studio"

            elif property_type == PropertyTypeChoices.APARTMENT:
                rooms = random.randint(2, 3)
                price = Decimal(
                    str(random.randint(4000, 10000))
                )
                title_prefix = "Spacious Apartment"

            elif property_type == PropertyTypeChoices.HOUSE:
                rooms = random.randint(3, 5)
                price = Decimal(
                    str(random.randint(15000, 35000))
                )
                title_prefix = "Comfortable House"

            else:
                rooms = random.randint(4, 6)
                price = Decimal(
                    str(random.randint(30000, 70000))
                )
                title_prefix = "Luxury Villa"

            city = random.choice(cities)

            apartment = Apartment(
                title=f"{title_prefix} #{i}",
                description=(
                    "Beautiful living apartment with all amenities "
                    f"in the city center of {city}."
                ),
                price=Money(price, "EUR"),
                address_city=city,
                rooms=rooms,
                property_type=property_type,
                user=random.choice(hosts),
            )

            apartments.append(apartment)

        Apartment.objects.bulk_create(apartments)
        apartments = list(Apartment.objects.all())

        # --------------------------------------------------
        # IMAGES
        # --------------------------------------------------
        self.stdout.write("Downloading categorical images...")

        categorized_urls = {
            PropertyTypeChoices.STUDIO: [
                (
                    "https://images.unsplash.com/"
                    "photo-1522708323590-d24dbb6b0267?w=800"
                ),
                (
                    "https://images.unsplash.com/"
                    "photo-1536376072261-38c75010e6c9?w=800"
                ),
            ],
            PropertyTypeChoices.APARTMENT: [
                (
                    "https://images.unsplash.com/"
                    "photo-1502672260266-1c1ef2d93688?w=800"
                ),
                (
                    "https://images.unsplash.com/"
                    "photo-1560448204-e02f11c3d0e2?w=800"
                ),
            ],
            PropertyTypeChoices.HOUSE: [
                (
                    "https://images.unsplash.com/"
                    "photo-1616486338812-3dadae4b4ace?w=800"
                ),
                (
                    "https://images.unsplash.com/"
                    "photo-1505691938895-1758d7feb511?w=800"
                ),
            ],
            PropertyTypeChoices.VILLA: [
                (
                    "https://images.unsplash.com/"
                    "photo-1512917774080-9991f1c4c750?w=800"
                ),
                (
                    "https://images.unsplash.com/"
                    "photo-1600596542815-ffad4c1539a9?w=800"
                ),
            ],
        }

        downloaded_images = {}

        for property_type, urls in categorized_urls.items():
            downloaded_images[property_type] = []

            for url in urls:
                try:
                    response = requests.get(
                        url,
                        timeout=5,
                    )

                    if response.status_code == 200:
                        downloaded_images[property_type].append(
                            response.content
                        )

                except requests.RequestException:
                    pass

        for apartment in apartments:
            property_type = apartment.property_type
            images = downloaded_images.get(property_type, [])

            if images:
                image_bytes = random.choice(images)
            else:
                image_bytes = (
                    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"
                    b"\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
                )

            image = ApartmentImage(
                apartment=apartment,
                is_main=True,
            )

            image.image.save(
                f"apartment_{apartment.id}.jpg",
                ContentFile(image_bytes),
                save=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Images saved successfully."
            )
        )

        # --------------------------------------------------
        # RESERVATIONS
        # --------------------------------------------------
        self.stdout.write(
            "Creating reservations and reviews..."
        )

        reservations = []
        current_date = (
            timezone.now().date()
            + timedelta(days=1)
        )

        for apartment in apartments[:100]:
            guest_users = [
                user
                for user in users
                if user != apartment.user
            ]

            for step in range(2):
                guest = random.choice(guest_users)

                start_date = (
                    current_date
                    + timedelta(days=step * 20)
                )

                end_date = (
                    start_date
                    + timedelta(
                        days=random.randint(2, 7)
                    )
                )

                reservations.append(
                    Reservation(
                        listing=apartment,
                        user=guest,
                        status=random.choice(
                            [
                                Reservation.StatusChoice.PENDING,
                                Reservation.StatusChoice.CONFIRMED,
                            ]
                        ),
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

        Reservation.objects.bulk_create(reservations)
        reservations = list(
            Reservation.objects.all()
        )

        # --------------------------------------------------
        # REVIEWS
        # --------------------------------------------------
        confirmed_reservations = [
            reservation
            for reservation in reservations
            if (
                reservation.status
                == Reservation.StatusChoice.CONFIRMED
            )
        ]

        reviews = []
        used_reviews = set()

        comments = [
            "Great apartment! Very clean and cozy.",
            (
                "Excellent location, "
                "everything is close by."
            ),
            (
                "Hospitable host, "
                "really enjoyed our stay."
            ),
            (
                "Clean bed linen, "
                "wonderful view from the window."
            ),
            (
                "Everything matches the description. "
                "Will definitely return!"
            ),
            (
                "Comfortable furniture "
                "and fast Wi-Fi."
            ),
        ]

        for reservation in confirmed_reservations:
            key = (
                reservation.user_id,
                reservation.listing_id,
            )

            if key in used_reviews:
                continue

            used_reviews.add(key)

            reviews.append(
                Review(
                    listing=reservation.listing,
                    user=reservation.user,
                    rating=random.randint(3, 5),
                    comment=random.choice(comments),
                )
            )

        Review.objects.bulk_create(reviews)

        # --------------------------------------------------
        # SEARCH HISTORY
        # --------------------------------------------------
        self.stdout.write(
            "Creating search and view history..."
        )

        search_queries = [
            "Berlin",
            "Munich",
            "Studio",
            "Villa",
            "Center",
            "2 rooms",
            "Hamburg",
        ]

        search_histories = []

        for _ in range(100):
            search_histories.append(
                SearchHistory(
                    user=random.choice(users),
                    query=random.choice(search_queries),
                )
            )

        SearchHistory.objects.bulk_create(
            search_histories
        )

        # --------------------------------------------------
        # VIEW HISTORY
        # --------------------------------------------------
        view_histories = []

        for _ in range(200):
            view_histories.append(
                ListingViewHistory(
                    user=random.choice(users),
                    apartment=random.choice(apartments),
                )
            )

        ListingViewHistory.objects.bulk_create(
            view_histories
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Database seeded successfully!"
            )
        )