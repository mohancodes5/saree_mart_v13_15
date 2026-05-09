from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.email_utils import send_order_placed_email, send_order_status_email

from .models import Order


@receiver(pre_save, sender=Order)
def order_store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Order.objects.only("status").get(pk=instance.pk)
            instance._previous_order_status = previous.status
        except Order.DoesNotExist:
            instance._previous_order_status = None
    else:
        instance._previous_order_status = None


@receiver(post_save, sender=Order)
def order_email_notifications(sender, instance, created, **kwargs):
    if created:
        send_order_placed_email(instance)
        return
    prev = getattr(instance, "_previous_order_status", None)
    if prev is not None and prev != instance.status:
        send_order_status_email(instance, prev)
