from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for the Users application.
    Manages application-specific settings, signals, and administrative metadata.
    """
    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "apps.users"
    verbose_name: str = "User Management"

    def ready(self) -> None:
        import apps.users.authentication  # noqa: F401