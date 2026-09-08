from django.apps import AppConfig


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reservations"

    def ready(self) -> None:
        import apps.reservations.signals.reservation_signals  # noqa: F401