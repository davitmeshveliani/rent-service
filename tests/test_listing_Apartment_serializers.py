from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.listings.models.apartment import Apartment, PropertyTypeChoices
from apps.listings.serializers.apartments import ApartmentSerializer

User = get_user_model()


class ApartmentSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
                                        email="test@example.com",
                                        username="testuser",
                                        password="Password123!",)

        self.apartment = Apartment.objects.create(
                                        title="Berlin Apartment",
                                        description="Comfortable apartment in Berlin.",
                                        price=Decimal("150.00"),
                                        address_city="Berlin",
                                        address_district="Mitte",
                                        rooms=2,
                                        property_type=PropertyTypeChoices.APARTMENT,
                                        is_active=True,
                                        user=self.user,)

    def test_apartment_serializer_fields(self):
        """Verify that the serializer returns all expected apartment fields."""
        serializer = ApartmentSerializer(instance=self.apartment)
        data = serializer.data

        expected_fields = [
                            "id","title",
                            "description","price","address_city","address_district",#
                                "rooms","property_type",
                            "is_active","views_count","user", "images","created_at",]

        for field in expected_fields:
            self.assertIn(field, data)

        self.assertEqual(data["title"], self.apartment.title)
        self.assertEqual(data["description"], self.apartment.description)
        self.assertEqual(Decimal(str(data["price"])), self.apartment.price.amount, )

        self.assertEqual(data["address_city"],
            self.apartment.address_city,)
        self.assertEqual(data["address_district"],
            self.apartment.address_district,)
        self.assertEqual(data["rooms"], self.apartment.rooms)
        self.assertEqual(
            data["property_type"],
            self.apartment.property_type,)
        self.assertEqual(data["is_active"],
            self.apartment.is_active,)
        self.assertEqual(data["views_count"],
            self.apartment.views_count,)
        self.assertEqual(data["images"], [])

