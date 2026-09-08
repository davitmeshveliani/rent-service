"""
Signals for reservation-related events.
"""

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.reservations.models import Reservation


@receiver(post_save,sender=Reservation,)
def reservation_created_email(sender,instance: Reservation,created: bool,**kwargs,) -> None:
    """
    Send a confirmation email when a new reservation is created.
    """

    if not created:
        return
    user_email = getattr(instance.user,"email",None,)
    if not user_email:
        return
    send_mail(subject="Rentify – Reservation Created",
        message=(
                    f"Hello {instance.user},\n\n"
                    "Your reservation has been created successfully.\n\n"
                    f"Listing: {instance.listing.title}\n"
                    f"Start date: {instance.start_date}\n"
                    f"End date: {instance.end_date}\n"
                    f"Status: {instance.status}\n\n"
                    "Thank you for using Rentify."),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,)